"""Bias-corrected mutual information at separations 1..6.

Miller--Madow correction is applied to H(X)+H(Y)-H(X,Y), in bits.  Two
controls accompany every distance: an exact absolute-position shuffle within
length x site x object, and an exact-bigram surrogate made by exchanging
suffixes after shared pivots inside those same strata.  The latter preserves
the complete bigram multiset, not merely a fitted transition model.
"""
import json
import math
from collections import Counter, defaultdict

import numpy as np

SEED = 37
MAX_K = 6
POSITION_RUNS = 500
BIGRAM_RUNS = 300
BIGRAM_SWEEPS = 30
BOOT_RUNS = 1000
OUT = "data/parsed/mi_distance.json"


def load_records():
    lines = json.load(open("data/parsed/lines_merged.json"))
    inscriptions = json.load(open("data/parsed/inscriptions.json"))
    by_artifact = {i["cisi"] or f"#{i['seal_id']}": i for i in inscriptions}
    records, seen = [], set()
    for line in lines:
        text = tuple(g for g in line["signs"] if g)
        meta = by_artifact.get(line.get("artifact"), {})
        site = line.get("site") or "unknown"
        obj = meta.get("obj_class") or "unknown"
        key = (text, site, obj)
        if text and key not in seen:
            seen.add(key)
            records.append({"text": text, "site": site, "object": obj})
    return records


def mi_at_k(texts, k):
    pairs = [(text[i], text[i + k]) for text in texts for i in range(len(text) - k)]
    n = len(pairs)
    joint = Counter(pairs)
    left = Counter(a for a, _ in pairs)
    right = Counter(b for _, b in pairs)
    plugin = sum(count / n * math.log2(count * n / (left[a] * right[b]))
                 for (a, b), count in joint.items())
    # Hx_MM + Hy_MM - Hxy_MM.  Equivalent to subtracting the leading
    # finite-sample MI bias based on the occupied cells.
    correction = (len(joint) - len(left) - len(right) + 1) / (2 * n * math.log(2))
    return {"pairs": n, "left_types": len(left), "right_types": len(right),
            "joint_types": len(joint), "plugin_bits": plugin,
            "mm_correction_bits": correction, "mm_bits": plugin - correction}


def curve(texts):
    return [mi_at_k(texts, k) for k in range(1, MAX_K + 1)]


def column_shuffle(records, rng):
    out = [list(record["text"]) for record in records]
    groups = defaultdict(list)
    for ri, record in enumerate(records):
        for i in range(len(record["text"])):
            groups[(len(record["text"]), i, record["site"], record["object"])].append((ri, i))
    for cells in groups.values():
        values = [out[ri][i] for ri, i in cells]
        rng.shuffle(values)
        for (ri, i), value in zip(cells, values):
            out[ri][i] = value
    return [tuple(x) for x in out]


def bigram_counts(texts):
    return Counter((a, b) for text in texts for a, b in zip(text, text[1:]))


def bigram_surrogate(records, rng):
    """Recombine equal-length texts after shared signs; preserve all bigrams."""
    original = [tuple(record["text"]) for record in records]
    out = [list(text) for text in original]
    strata = defaultdict(list)
    for i, record in enumerate(records):
        strata[(len(record["text"]), record["site"], record["object"])].append(i)
    effective = 0
    for _ in range(BIGRAM_SWEEPS):
        keys = list(strata)
        rng.shuffle(keys)
        for key in keys:
            length = key[0]
            if length < 3 or len(strata[key]) < 2:
                continue
            cuts = rng.permutation(length - 1)
            for cut in cuts:
                buckets = defaultdict(list)
                for ri in strata[key]:
                    buckets[out[ri][cut]].append(ri)
                for bucket in buckets.values():
                    if len(bucket) < 2:
                        continue
                    tails = [tuple(out[ri][cut + 1:]) for ri in bucket]
                    order = rng.permutation(len(bucket))
                    if np.any(order != np.arange(len(bucket))):
                        effective += 1
                    for ri, tail_index in zip(bucket, order):
                        out[ri][cut + 1:] = tails[tail_index]
    result = [tuple(x) for x in out]
    if bigram_counts(result) != bigram_counts(original):
        raise RuntimeError("bigram surrogate failed exact preservation check")
    changed = sum(a != b for a, b in zip(original, result))
    return result, {"changed_records": changed,
                    "changed_fraction": changed / len(records),
                    "effective_tail_permutations": effective}


def centered_interval(values, point):
    values = np.asarray(values, float)
    median = np.median(values)
    return [float(point + np.quantile(values, .025) - median),
            float(point + np.quantile(values, .975) - median)]


def main():
    rng = np.random.default_rng(SEED)
    records = load_records()
    texts = [record["text"] for record in records]
    observed = curve(texts)

    position = np.empty((POSITION_RUNS, MAX_K))
    for run in range(POSITION_RUNS):
        position[run] = [row["mm_bits"] for row in curve(column_shuffle(records, rng))]

    bigram = np.empty((BIGRAM_RUNS, MAX_K))
    diagnostics = []
    for run in range(BIGRAM_RUNS):
        surrogate, diagnostic = bigram_surrogate(records, rng)
        bigram[run] = [row["mm_bits"] for row in curve(surrogate)]
        diagnostics.append(diagnostic)

    groups = defaultdict(list)
    for record in records:
        groups[(record["site"], record["object"])].append(record)
    bootstrap = np.empty((BOOT_RUNS, MAX_K))
    for run in range(BOOT_RUNS):
        sample = []
        for group in groups.values():
            take = rng.integers(0, len(group), len(group))
            sample.extend(group[i] for i in take)
        bootstrap[run] = [row["mm_bits"] for row in curve([r["text"] for r in sample])]

    rows = []
    for k in range(MAX_K):
        real = observed[k]["mm_bits"]
        ppos = position[:, k]
        pbig = bigram[:, k]
        row = observed[k] | {
            "k": k + 1,
            "bootstrap_interval": centered_interval(bootstrap[:, k], real),
            "bootstrap_raw_median": float(np.median(bootstrap[:, k])),
            "position_null_mean": float(ppos.mean()),
            "position_null_interval": [float(np.quantile(ppos, .025)), float(np.quantile(ppos, .975))],
            "position_excess": float(real - ppos.mean()),
            "position_upper_p": float((1 + np.sum(ppos >= real)) / (POSITION_RUNS + 1)),
            "bigram_null_mean": float(pbig.mean()),
            "bigram_null_interval": [float(np.quantile(pbig, .025)), float(np.quantile(pbig, .975))],
            "bigram_excess": float(real - pbig.mean()),
            "bigram_upper_p": float((1 + np.sum(pbig >= real)) / (BIGRAM_RUNS + 1))}
        rows.append(row)

    result = {"method": {"seed": SEED, "records": len(records),
                         "position_runs": POSITION_RUNS, "bigram_runs": BIGRAM_RUNS,
                         "bigram_sweeps": BIGRAM_SWEEPS, "bootstrap_runs": BOOT_RUNS,
                         "bias_correction": "Miller-Madow entropy correction"},
              "bigram_surrogate_diagnostics": {
                  "exact_bigram_preservation": True,
                  "mean_changed_fraction": float(np.mean([x["changed_fraction"] for x in diagnostics])),
                  "min_changed_fraction": float(np.min([x["changed_fraction"] for x in diagnostics])),
                  "mean_effective_tail_permutations": float(np.mean([x["effective_tail_permutations"] for x in diagnostics]))},
              "curve": rows}
    with open(OUT, "w") as handle:
        json.dump(result, handle, indent=2)
        handle.write("\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
