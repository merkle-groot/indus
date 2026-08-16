"""Run established Indus statistics on corpora with known status.

External source files are downloaded to gitignored data/external/.  Only the
derived JSON is committed.  The ordered comparison is ORACC's CC0 ED IIIa
administrative corpus.  Kansas cattle brands supply a real non-linguistic
comparison, but their four catalogue fields describe a two-dimensional emblem,
not a reading order; only order-invariant statistics are run on them.

All corpora are deduplicated before analysis.  The main comparison uses 1,000
records containing only the 100 commonest types in each corpus.  This fixes both
sample size and observed inventory.  Ordered nulls shuffle each absolute
position within exact length x site x object strata.  The cattle-brand repeat
null instead reallocates the unordered components conditional on length.
"""
import csv
import hashlib
import io
import json
import math
import shutil
import subprocess
import urllib.request
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

SEED = 34
RUNS = 500
MATCH_N = 1000
MATCH_K = 100
MIN_EVENTS = 15
EXTERNAL = Path("data/external")
OUT = Path("data/parsed/known_corpora.json")

ORACC_URL = "https://oracc.museum.upenn.edu/json/epsd2-admin-ed3a.zip"
ORACC_SHA256 = "8d4b7bfb6cba7190c2c150ca8b24860c25a430e6ffd0f18ce03ff49092a0a645"
CATTLE_COMMIT = "01e05a546f0d30a4c6c2c35f57fae0e6633a6c5e"
CATTLE_URL = ("https://raw.githubusercontent.com/masonyoungblood/"
              f"cattle_brand_data/{CATTLE_COMMIT}/brand_data.csv")
CATTLE_SHA256 = "a263a35f5efcfe69f7a134171646626403fcdd53306a7196b68101d01539036e"

INDUS_NUMERALS = ({1, 2, 3, 4, 5, 6, 7, 13, 14, 15, 16, 17, 18, 19,
                   27, 28, 29, 31, 32, 33, 34, 35, 36, 48, 49, 50,
                   51, 55, 56, 57})


def download(url, path, sha256):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        try:
            with urllib.request.urlopen(url, timeout=120) as response, open(path, "wb") as out:
                shutil.copyfileobj(response, out)
        except Exception:
            path.unlink(missing_ok=True)
            subprocess.run(["curl", "-fL", url, "-o", str(path)], check=True)
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != sha256:
        raise RuntimeError(f"checksum mismatch for {path}: {digest}")


def load_indus():
    lines = json.load(open("data/parsed/lines_merged.json"))
    inscriptions = json.load(open("data/parsed/inscriptions.json"))
    by_artifact = {i["cisi"] or f"#{i['seal_id']}": i for i in inscriptions}
    records, seen = [], set()
    for line in lines:
        text = tuple(g for g in line["signs"] if g)
        meta = by_artifact.get(line.get("artifact"), {})
        obj = meta.get("obj_class") or "unknown"
        site = line.get("site") or "unknown"
        key = (text, site, obj)
        if text and key not in seen:
            seen.add(key)
            records.append({"text": text, "numeric": tuple(g in INDUS_NUMERALS for g in text),
                            "site": site, "object": obj})
    return records


def gdl_identity(g):
    """One identity for one top-level ORACC grapheme description."""
    if not isinstance(g, dict):
        return None
    if g.get("n") == "n":
        return "N:" + str(g.get("form", "n"))
    for key, prefix in (("v", "V:"), ("s", "S:"), ("c", "C:"), ("q", "Q:")):
        if key in g:
            value = str(g[key])
            return None if value == "x" else prefix + value
    if "det" in g:
        values = [gdl_identity(x) for x in g.get("seq", [])]
        values = [x for x in values if x]
        return values[0] if len(values) == 1 else None
    return None


def oracc_lines(document):
    lines, current, bad = [], None, False

    def walk(value):
        nonlocal current, bad
        if isinstance(value, dict):
            if value.get("node") == "d" and value.get("type") == "line-start":
                if current is not None:
                    lines.append((current, bad))
                current, bad = [], False
                return
            if value.get("node") == "l" and current is not None:
                form = value.get("f", {})
                gdl = form.get("gdl", [])
                if not isinstance(gdl, list):
                    bad = True
                    return
                for item in gdl:
                    sign = gdl_identity(item)
                    if sign is None:
                        bad = True
                    else:
                        current.append((sign, form.get("pos") == "n"))
                return
            for child in value.values():
                walk(child)
        elif isinstance(value, list):
            for child in value:
                walk(child)

    walk(document.get("cdl", []))
    if current is not None:
        lines.append((current, bad))
    return lines


def load_oracc():
    archive = EXTERNAL / "epsd2-admin-ed3a.zip"
    root = EXTERNAL / "epsd2-admin-ed3a"
    download(ORACC_URL, archive, ORACC_SHA256)
    if not (root / "epsd2/admin/ed3a/catalogue.json").exists():
        root.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(archive) as zf:
            zf.extractall(root)
    corpus = root / "epsd2/admin/ed3a"
    catalogue_doc = json.load(open(corpus / "catalogue.json"))
    if "CC0" not in catalogue_doc.get("license", ""):
        raise RuntimeError("ORACC archive no longer reports the expected CC0 licence")
    catalogue = catalogue_doc["members"]
    records, seen = [], set()
    exclusions = Counter()
    for path in sorted((corpus / "corpusjson").glob("*.json")):
        document = json.load(open(path))
        textid = document["textid"]
        meta = catalogue.get(textid, {})
        site = meta.get("provenience") or "unknown"
        obj = (meta.get("object_type") or "unknown").lower()
        for signs, bad in oracc_lines(document):
            if bad:
                exclusions["unreadable_line"] += 1
                continue
            if not signs:
                exclusions["empty_line"] += 1
                continue
            text = tuple(x for x, _ in signs)
            numeric = tuple(flag for _, flag in signs)
            key = (text, site, obj)
            if key in seen:
                exclusions["duplicate"] += 1
                continue
            seen.add(key)
            records.append({"text": text, "numeric": numeric,
                            "site": site, "object": obj})
    # The comparison needs identities, not transliteration values.  Opaque IDs
    # also keep third-party textual labels out of the committed derived file.
    inventory = sorted({g for record in records for g in record["text"]})
    opaque = {g: f"E{i:04d}" for i, g in enumerate(inventory, 1)}
    for record in records:
        record["text"] = tuple(opaque[g] for g in record["text"])
    return records, dict(exclusions), catalogue_doc


def load_cattle():
    path = EXTERNAL / "cattle_brand_data.csv"
    download(CATTLE_URL, path, CATTLE_SHA256)
    records, seen = [], set()
    exclusions = Counter()
    with open(path, newline="") as handle:
        for row in csv.DictReader(handle):
            code = row["brand"]
            if len(code) != 13:
                exclusions["malformed_code"] += 1
                continue
            fields = tuple(code[i:i + 3].replace(",", "") for i in range(0, 12, 3))
            components = tuple(x for x in fields if x)
            if not components:
                exclusions["empty_design"] += 1
                continue
            # Same design at the same registry location in multiple books is a copy.
            site = row.get("location") or "unknown"
            key = (code[:12], site)
            if key in seen:
                exclusions["duplicate_design_site"] += 1
                continue
            seen.add(key)
            records.append({"text": components, "numeric": None,
                            "site": site, "object": "registered cattle brand"})
    return records, dict(exclusions)


def summary(records):
    freq = Counter(g for r in records for g in r["text"])
    lengths = np.asarray([len(r["text"]) for r in records])
    repeated = sum(len(set(r["text"])) < len(r["text"]) for r in records)
    return {"records": len(records), "tokens": int(lengths.sum()), "inventory": len(freq),
            "mean_length": float(lengths.mean()), "median_length": float(np.median(lengths)),
            "hapax": sum(n == 1 for n in freq.values()),
            "hapax_inventory_rate": sum(n == 1 for n in freq.values()) / len(freq),
            "repeat_records": repeated, "repeat_rate": repeated / len(records)}


def matched(records, rng):
    freq = Counter(g for r in records for g in r["text"])
    top = {g for g, _ in freq.most_common(MATCH_K)}
    eligible = [r for r in records if set(r["text"]) <= top]
    if len(eligible) < MATCH_N:
        raise RuntimeError(f"only {len(eligible)} records on top-{MATCH_K} inventory")
    for _ in range(10000):
        take = rng.choice(len(eligible), MATCH_N, replace=False)
        sample = [eligible[i] for i in take]
        if len({g for r in sample for g in r["text"]}) == MATCH_K:
            return sample, len(eligible)
    raise RuntimeError("could not draw a matched sample containing every type")


def positional_shuffle(records, rng):
    out = [list(r["text"]) for r in records]
    groups = defaultdict(list)
    for ri, record in enumerate(records):
        for i in range(len(record["text"])):
            groups[(len(record["text"]), i, record["site"], record["object"])].append((ri, i))
    for cells in groups.values():
        values = [out[ri][i] for ri, i in cells]
        rng.shuffle(values)
        for (ri, i), value in zip(cells, values):
            out[ri][i] = value
    return out


def unordered_shuffle(records, rng):
    """Length-conditioned component reallocation; there is no physical position."""
    out = [list(r["text"]) for r in records]
    by_length = defaultdict(list)
    for ri, text in enumerate(out):
        for i in range(len(text)):
            by_length[len(text)].append((ri, i))
    for cells in by_length.values():
        values = [out[ri][i] for ri, i in cells]
        rng.shuffle(values)
        for (ri, i), value in zip(cells, values):
            out[ri][i] = value
    return out


def interval(values):
    values = np.asarray(values, float)
    return {"mean": float(values.mean()), "lo": float(np.quantile(values, .025)),
            "hi": float(np.quantile(values, .975)), "sd": float(values.std(ddof=1))}


def no_repeat(records, ordered, rng):
    observed = sum(len(set(r["text"])) < len(r["text"]) for r in records)
    null = []
    for _ in range(RUNS):
        shuffled = positional_shuffle(records, rng) if ordered else unordered_shuffle(records, rng)
        null.append(sum(len(set(t)) < len(t) for t in shuffled))
    stats = interval(null)
    stats.update({"observed": observed, "observed_rate": observed / len(records),
                  "z": (observed - stats["mean"]) / stats["sd"] if stats["sd"] else None,
                  "lower_p": (1 + sum(x <= observed for x in null)) / (RUNS + 1)})
    return stats


def exclusion_scan(records, rng):
    signs = sorted({g for r in records for g in r["text"]}, key=str)
    index = {g: i for i, g in enumerate(signs)}
    observed_presence = np.zeros((len(records), len(signs)), dtype=np.uint8)
    for i, record in enumerate(records):
        observed_presence[i, [index[g] for g in set(record["text"])]] = 1
    frequency = observed_presence.sum(axis=0)
    eligible = np.flatnonzero(frequency >= 20)
    pairs = [(a, b) for ii, a in enumerate(eligible) for b in eligible[ii + 1:]]
    observed_co = observed_presence.T.astype(np.int32) @ observed_presence.astype(np.int32)
    null = np.empty((RUNS, len(pairs)), dtype=np.int16)
    for run in range(RUNS):
        shuffled = positional_shuffle(records, rng)
        matrix = np.zeros_like(observed_presence)
        for i, text in enumerate(shuffled):
            matrix[i, [index[g] for g in set(text)]] = 1
        co = matrix.T.astype(np.int32) @ matrix.astype(np.int32)
        null[run] = [co[a, b] for a, b in pairs]
    rows = []
    for j, (a, b) in enumerate(pairs):
        values = null[:, j].astype(float)
        obs = int(observed_co[a, b])
        sd = values.std(ddof=1)
        p = (1 + int(np.sum(values <= obs))) / (RUNS + 1)
        rows.append({"a": signs[a], "b": signs[b], "observed": obs,
                     "null_mean": float(values.mean()), "null_lo": float(np.quantile(values, .025)),
                     "null_hi": float(np.quantile(values, .975)),
                     "z": (obs - values.mean()) / sd if sd else None, "p": p})
        rows[-1]["normal_p"] = (math.erfc(-rows[-1]["z"] / math.sqrt(2)) / 2
                                  if rows[-1]["z"] is not None else 1.0)
    rows.sort(key=lambda x: (x["normal_p"], x["z"] if x["z"] is not None else 0))
    discoveries = []
    for rank, row in enumerate(rows, 1):
        if row["normal_p"] <= .05 * rank / len(rows):
            discoveries = rows[:rank]
    fixed = next((x for x in rows if {x["a"], x["b"]} == {740, 520}), None)
    return {"eligible_signs": len(eligible), "testable_pairs": len(rows),
            "bh_discoveries": len(discoveries), "strongest": rows[:10],
            "indus_740_520": fixed}


def q_stat(left, totals, p):
    valid = totals * p * (1 - p) > 0
    return float(np.sum((left[valid] - totals[valid] * p) ** 2 /
                        (totals[valid] * p * (1 - p))))


def numeral_side(records, rng):
    events = []
    for record in records:
        flags = record["numeric"]
        for i, (a, b) in enumerate(zip(flags, flags[1:])):
            if a and not b:
                events.append((record["text"][i + 1], 1, len(flags), i + 1,
                               record["site"], record["object"]))
            elif not a and b:
                events.append((record["text"][i], 0, len(flags), i,
                               record["site"], record["object"]))
    freq = Counter(e[0] for e in events)
    signs = sorted((g for g, n in freq.items() if n >= MIN_EVENTS), key=str)
    idx = {g: i for i, g in enumerate(signs)}
    selected = [e for e in events if e[0] in idx]
    totals = np.bincount([idx[e[0]] for e in selected], minlength=len(signs))
    sides = np.asarray([e[1] for e in selected], dtype=np.int8)
    event_sign = np.asarray([idx[e[0]] for e in selected], dtype=int)
    left = np.bincount(event_sign, weights=sides, minlength=len(signs))
    base = float(sides.mean())
    observed = q_stat(left, totals, base)
    groups = defaultdict(list)
    for i, event in enumerate(selected):
        groups[event[2:]].append(i)
    q_null = []
    for _ in range(RUNS):
        perm = sides.copy()
        for cells in groups.values():
            perm[cells] = rng.permutation(perm[cells])
        counts = np.bincount(event_sign, weights=perm, minlength=len(signs))
        q_null.append(q_stat(counts, totals, base))
    stats = interval(q_null)
    stats.update({"events": len(events), "eligible_signs": len(signs),
                  "numeral_left_rate": base, "observed_q": observed,
                  "upper_p": (1 + sum(x >= observed for x in q_null)) / (RUNS + 1),
                  "extreme_signs": int(np.sum((left / totals <= .1) | (left / totals >= .9)))})
    return stats


def main():
    rng = np.random.default_rng(SEED)
    indus = load_indus()
    oracc, oracc_exclusions, oracc_meta = load_oracc()
    cattle, cattle_exclusions = load_cattle()
    corpora = {"indus": indus, "ed3a": oracc, "cattle_brands": cattle}
    result = {
        "method": {"seed": SEED, "runs": RUNS, "match_n": MATCH_N, "match_inventory": MATCH_K},
        "sources": {
            "ed3a": {"url": ORACC_URL, "sha256": ORACC_SHA256,
                      "license": oracc_meta["license"], "license_url": oracc_meta["license-url"],
                      "timestamp": oracc_meta["UTC-timestamp"], "exclusions": oracc_exclusions},
            "cattle_brands": {"url": CATTLE_URL, "commit": CATTLE_COMMIT,
                              "sha256": CATTLE_SHA256, "license": "not stated in repository",
                              "exclusions": cattle_exclusions}
        }, "full": {}, "matched": {}}
    samples = {}
    for name, records in corpora.items():
        result["full"][name] = summary(records)
        samples[name], eligible = matched(records, rng)
        result["matched"][name] = {"eligible_top100_records": eligible,
                                    "summary": summary(samples[name])}
    for name in ("indus", "ed3a"):
        result["matched"][name]["no_repeat"] = no_repeat(samples[name], True, rng)
        result["matched"][name]["terminal_exclusion"] = exclusion_scan(samples[name], rng)
        result["matched"][name]["numeral_side"] = numeral_side(samples[name], rng)
    result["matched"]["cattle_brands"]["no_repeat"] = no_repeat(samples["cattle_brands"], False, rng)
    result["matched"]["cattle_brands"]["terminal_exclusion"] = {
        "status": "infeasible", "reason": "catalogue component fields do not encode physical order"}
    result["matched"]["cattle_brands"]["numeral_side"] = {
        "status": "infeasible", "reason": "emblems have neither reading order nor numeral annotation"}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
