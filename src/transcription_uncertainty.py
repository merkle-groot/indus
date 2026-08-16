"""Propagate observed inter-digitizer sign-identity disagreement.

The 146 shared, equal-length artefacts from note 10 provide 778 aligned mapped
positions and 53 disagreements.  A sign-specific empirical-Bayes confusion
model shrinks each source sign's error rate toward the global 53/778 rate and
backs sparse alternative identities toward the global observed confusion
distribution.  Treating pairwise disagreement as our transcription's error
probability is deliberately conservative.

Each noisy draw perturbs token identities, rededuplicates text x site x object,
and reruns positional controls for the fixed headline statistics.
"""
import glob
import json
import math
import re
from collections import Counter, defaultdict

import numpy as np

SEED = 38
DRAWS = 300
NULL_RUNS = 60
BASE_NULL_RUNS = 1000
SHRINKAGE = 20.0
TARGET_BACKOFF = 5.0
OUT = "data/parsed/transcription_uncertainty.json"

TERMINAL = {740, 520, 390, 151, 527, 617, 156}
NUMERALS = ({1, 2, 3, 4, 5, 6, 7, 13, 14, 15, 16, 17, 18, 19,
             27, 28, 29, 31, 32, 33, 34, 35, 36, 48, 49, 50, 51,
             55, 56, 57})
PAIRS = [(740, 520), (740, 390), (740, 527), (740, 617),
         (740, 151), (740, 156), (520, 390),
         (817, 861), (817, 820), (861, 820)]


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


def build_noise_model(records):
    crosswalk = {int(k): v for k, v in json.load(open("data/parsed/crosswalk.json"))["y2p"].items()}
    merge = {int(k): v for k, v in json.load(open("data/parsed/allograph_map.json"))["map"].items()}
    frequency = Counter(g for r in records for g in r["text"])
    reverse = defaultdict(set)
    for y, p in crosswalk.items():
        reverse[p].add(merge.get(y, y))

    inscriptions = json.load(open("data/parsed/inscriptions.json"))
    ours = {}
    for item in inscriptions:
        if item.get("cisi"):
            ours.setdefault(item["cisi"], item)
    theirs = {}
    for path in glob.glob("data/cisi/corpus/*/*.json"):
        for side in json.load(open(path)):
            theirs[side["id"]] = [g["id"] for g in side["graphemes"]]

    comparisons, mismatches = Counter(), Counter()
    confusion = defaultdict(Counter)
    comparable = equal_length = agreements = 0
    opaque = {}
    unrepresented_disagreements = 0
    for key, external in sorted(theirs.items()):
        base = re.sub(r"[A-Za-z]$", "", key)
        if base not in ours:
            continue
        comparable += 1
        source_raw = [g for g in ours[base]["glyphs"] if g]
        if len(source_raw) != len(external):
            continue
        equal_length += 1
        for raw, target_p in zip(source_raw, external):
            if raw not in crosswalk:
                continue
            source = merge.get(raw, raw)
            comparisons[source] += 1
            if crosswalk[raw] == target_p:
                agreements += 1
                continue
            mismatches[source] += 1
            candidates = sorted(reverse.get(target_p, ()))
            if candidates:
                weights = np.asarray([frequency[g] for g in candidates], float)
                weights /= weights.sum()
                for target, weight in zip(candidates, weights):
                    confusion[source][target] += float(weight)
            else:
                # An opaque negative ID means “alternative identity absent from
                # our sign list”; different external IDs remain different.
                if target_p not in opaque:
                    opaque[target_p] = -1000 - len(opaque)
                confusion[source][opaque[target_p]] += 1.0
                unrepresented_disagreements += 1

    total = sum(comparisons.values())
    total_mismatch = sum(mismatches.values())
    global_rate = total_mismatch / total
    global_targets = Counter()
    for counts in confusion.values():
        global_targets.update(counts)
    global_total = sum(global_targets.values())
    global_prob = {target: count / global_total for target, count in global_targets.items()}

    error_probability, alternatives = {}, {}
    inventory = sorted({g for r in records for g in r["text"]})
    for source in inventory:
        error_probability[source] = ((mismatches[source] + SHRINKAGE * global_rate) /
                                     (comparisons[source] + SHRINKAGE))
        weights = Counter(confusion[source])
        for target, p in global_prob.items():
            if target != source:
                weights[target] += TARGET_BACKOFF * p
        weights.pop(source, None)
        targets = np.asarray(list(weights), dtype=int)
        probability = np.asarray([weights[t] for t in targets], float)
        probability /= probability.sum()
        alternatives[source] = (targets, probability)

    rows = []
    for source in sorted(comparisons, key=lambda g: (-comparisons[g], g)):
        rows.append({"sign": source, "comparisons": comparisons[source],
                     "disagreements": mismatches[source],
                     "raw_rate": mismatches[source] / comparisons[source],
                     "shrunken_rate": error_probability[source]})
    return {"comparable_artifacts": comparable, "equal_length_artifacts": equal_length,
            "unequal_length_artifacts": comparable - equal_length,
            "aligned_positions": total, "agreements": agreements,
            "disagreements": total_mismatch, "global_rate": global_rate,
            "mapped_alternative_disagreements": total_mismatch - unrepresented_disagreements,
            "unrepresented_alternative_disagreements": unrepresented_disagreements,
            "sign_rates": rows}, error_probability, alternatives


def noisy_records(records, error_probability, alternatives, rng):
    out, seen, changed = [], set(), 0
    for record in records:
        text = []
        for sign in record["text"]:
            if rng.random() < error_probability[sign]:
                targets, p = alternatives[sign]
                sign = int(rng.choice(targets, p=p))
                changed += 1
            text.append(sign)
        text = tuple(text)
        key = (text, record["site"], record["object"])
        if key not in seen:
            seen.add(key)
            out.append({"text": text, "site": record["site"], "object": record["object"]})
    return out, changed


def column_shuffle(records, rng):
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
    return [tuple(x) for x in out]


def repeat_count(texts):
    return sum(len(set(t)) < len(t) for t in texts)


def pair_counts(texts):
    sets = [set(t) for t in texts]
    return np.asarray([sum(a in s and b in s for s in sets) for a, b in PAIRS], float)


def positional_metrics(records, rng, runs):
    texts = [r["text"] for r in records]
    observed_repeat = repeat_count(texts)
    observed_pairs = pair_counts(texts)
    repeat_null = np.empty(runs)
    pair_null = np.empty((runs, len(PAIRS)))
    for run in range(runs):
        shuffled = column_shuffle(records, rng)
        repeat_null[run] = repeat_count(shuffled)
        pair_null[run] = pair_counts(shuffled)
    repeat_sd = repeat_null.std(ddof=1)
    pair_sd = pair_null.std(axis=0, ddof=1)
    return {"repeat_observed": observed_repeat,
            "repeat_null_mean": float(repeat_null.mean()),
            "repeat_z": float((observed_repeat-repeat_null.mean())/repeat_sd),
            "pair_observed": observed_pairs.tolist(),
            "pair_null_mean": pair_null.mean(axis=0).tolist(),
            "pair_z": np.divide(observed_pairs-pair_null.mean(axis=0), pair_sd,
                                out=np.full(len(PAIRS), np.nan), where=pair_sd>0).tolist()}


def terminal_finality(records):
    observed = expected = variance = 0.0
    for record in records:
        text = record["text"]
        p = sum(g in TERMINAL for g in text) / len(text)
        observed += text[-1] in TERMINAL
        expected += p
        variance += p * (1 - p)
    return {"observed": int(observed), "rate": observed / len(records),
            "expected": expected, "z": (observed-expected)/math.sqrt(variance)}


def side_test(records, rng, runs):
    events = []
    for record in records:
        text = record["text"]
        for i, (a, b) in enumerate(zip(text, text[1:])):
            if a in NUMERALS and b not in NUMERALS:
                events.append((b, 1, len(text), i+1, record["site"], record["object"]))
            elif a not in NUMERALS and b in NUMERALS:
                events.append((a, 0, len(text), i, record["site"], record["object"]))
    frequency = Counter(e[0] for e in events)
    signs = sorted(g for g, n in frequency.items() if n >= 15)
    idx = {g: i for i, g in enumerate(signs)}
    selected = [e for e in events if e[0] in idx]
    sign_index = np.asarray([idx[e[0]] for e in selected], int)
    sides = np.asarray([e[1] for e in selected], np.int8)
    totals = np.bincount(sign_index, minlength=len(signs))
    p = sides.mean()
    left = np.bincount(sign_index, weights=sides, minlength=len(signs))
    q = float(np.sum((left-totals*p)**2/(totals*p*(1-p))))
    groups = defaultdict(list)
    for i, event in enumerate(selected):
        groups[event[2:]].append(i)
    null = np.empty(runs)
    for run in range(runs):
        perm = sides.copy()
        for cells in groups.values():
            perm[cells] = rng.permutation(perm[cells])
        counts = np.bincount(sign_index, weights=perm, minlength=len(signs))
        null[run] = np.sum((counts-totals*p)**2/(totals*p*(1-p)))
    sd = null.std(ddof=1)
    return {"events": len(events), "eligible_signs": len(signs), "q": q,
            "null_mean": float(null.mean()), "excess_q": float(q-null.mean()),
            "z": float((q-null.mean())/sd) if sd else float("nan")}


def full_metrics(records, rng, runs):
    result = positional_metrics(records, rng, runs)
    result["terminal"] = terminal_finality(records)
    result["numeral_side"] = side_test(records, rng, runs)
    result["records"] = len(records)
    return result


def distribution(values, direction):
    values = np.asarray(values, float)
    threshold = -1.96 if direction == "lower" else 1.96
    survives = values <= threshold if direction == "lower" else values >= threshold
    return {"median": float(np.median(values)),
            "lo": float(np.quantile(values, .025)),
            "hi": float(np.quantile(values, .975)),
            "survival_rate": float(np.mean(survives))}


def summary(values):
    values = np.asarray(values, float)
    return {"median": float(np.median(values)),
            "lo": float(np.quantile(values, .025)),
            "hi": float(np.quantile(values, .975))}


def main():
    rng = np.random.default_rng(SEED)
    records = load_records()
    model, error_probability, alternatives = build_noise_model(records)
    baseline = full_metrics(records, rng, BASE_NULL_RUNS)

    samples = defaultdict(list)
    changed, record_counts = [], []
    for _ in range(DRAWS):
        noisy, n_changed = noisy_records(records, error_probability, alternatives, rng)
        metric = full_metrics(noisy, rng, NULL_RUNS)
        changed.append(n_changed)
        record_counts.append(len(noisy))
        samples["no_repeat_z"].append(metric["repeat_z"])
        samples["terminal_final_z"].append(metric["terminal"]["z"])
        samples["terminal_final_rate"].append(metric["terminal"]["rate"])
        samples["side_z"].append(metric["numeral_side"]["z"])
        samples["side_excess_q"].append(metric["numeral_side"]["excess_q"])
        samples["side_eligible"].append(metric["numeral_side"]["eligible_signs"])
        for i, pair in enumerate(PAIRS):
            samples[f"pair_{pair[0]}_{pair[1]}_z"].append(metric["pair_z"][i])

    result = {"method": {"seed": SEED, "draws": DRAWS,
                         "null_runs_per_draw": NULL_RUNS,
                         "baseline_null_runs": BASE_NULL_RUNS,
                         "error_rate_shrinkage_equivalent_positions": SHRINKAGE,
                         "alternative_backoff_equivalent_disagreements": TARGET_BACKOFF,
                         "deduplication": "text x site x object after every perturbation"},
              "noise_model": model,
              "draw_diagnostics": {"changed_tokens": summary(changed),
                                   "record_count": summary(record_counts)},
              "baseline": baseline,
              "uncertainty": {
                  "no_repeat_z": distribution(samples["no_repeat_z"], "lower"),
                  "terminal_final_z": distribution(samples["terminal_final_z"], "upper"),
                  "terminal_final_rate": summary(samples["terminal_final_rate"]),
                  "numeral_side_z": distribution(samples["side_z"], "upper"),
                  "numeral_side_excess_q": summary(samples["side_excess_q"]),
                  "numeral_side_eligible_signs": summary(samples["side_eligible"]),
                  "pairs": {f"{a}/{b}": distribution(samples[f"pair_{a}_{b}_z"], "lower")
                            for a, b in PAIRS}}}
    with open(OUT, "w") as handle:
        json.dump(result, handle, indent=2)
        handle.write("\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
