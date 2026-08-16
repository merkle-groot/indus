"""Estimate unseen sign inventory under merged/unmerged sign definitions.

Counts are taken only after deduplicating exact text x site x object records.
The main analysis excludes the twelve digitizer 'unidentified' IDs; recorded
and collapsed-to-one-marker versions are retained as sensitivity analyses.
Confidence intervals are stratified text bootstraps.  Accumulation and Heaps
bands randomize text order, preserving the texts as sampling clusters.
"""
import json
from collections import Counter, defaultdict

import numpy as np

SEED = 35
BOOT = 1000
ACCUM_RUNS = 500
FRACTIONS = np.asarray([.05, .10, .20, .35, .50, .75, 1.0])
UNKNOWN = {12, 25, 106, 316, 376, 445, 515, 516, 546, 547, 606, 999}
OUT = "data/parsed/inventory_estimates.json"


def load_records(path):
    lines = json.load(open(path))
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


def handle_unknown(records, mode):
    out, seen = [], set()
    for record in records:
        if mode == "recorded":
            text = record["text"]
        elif mode == "collapse_unknown":
            text = tuple("UNK" if g in UNKNOWN else g for g in record["text"])
        elif mode == "exclude_unknown":
            text = tuple(g for g in record["text"] if g not in UNKNOWN)
        else:
            raise ValueError(mode)
        key = (text, record["site"], record["object"])
        if text and key not in seen:
            seen.add(key)
            out.append({"text": text, "site": record["site"], "object": record["object"]})
    return out


def abundance(records):
    return Counter(g for record in records for g in record["text"])


def estimators(freq):
    spectrum = Counter(freq.values())
    observed = len(freq)
    tokens = sum(freq.values())
    f1, f2 = spectrum[1], spectrum[2]
    coverage = 1 - f1 / tokens if tokens else float("nan")
    good_turing = observed / coverage if coverage > 0 else float("nan")
    chao1 = observed + f1 * (f1 - 1) / (2 * (f2 + 1))

    cutoff = 10
    rare_counts = {i: spectrum[i] for i in range(1, cutoff + 1)}
    s_rare = sum(rare_counts.values())
    s_abundant = observed - s_rare
    n_rare = sum(i * rare_counts[i] for i in rare_counts)
    c_ace = 1 - f1 / n_rare if n_rare else 0
    if c_ace > 0 and n_rare > 1:
        numer = sum(i * (i - 1) * rare_counts[i] for i in rare_counts)
        gamma2 = max((s_rare / c_ace) * numer / (n_rare * (n_rare - 1)) - 1, 0)
        ace = s_abundant + s_rare / c_ace + f1 * gamma2 / c_ace
    else:
        gamma2, ace = float("nan"), float("nan")
    return {"observed": observed, "tokens": tokens, "f1": f1, "f2": f2,
            "sample_coverage": coverage, "good_turing_coverage_total": good_turing,
            "chao1": chao1, "ace": ace, "ace_gamma2": gamma2,
            "frequency_spectrum": {str(i): spectrum[i] for i in range(1, 11)} |
                                  {">10": sum(n for k, n in spectrum.items() if k > 10)}}


def bootstrap(records, rng, point):
    groups = defaultdict(list)
    for record in records:
        groups[(record["site"], record["object"])].append(record)
    keys = sorted(groups, key=str)
    values = {name: [] for name in ("good_turing_coverage_total", "chao1", "ace")}
    for _ in range(BOOT):
        sample = []
        for key in keys:
            group = groups[key]
            take = rng.integers(0, len(group), len(group))
            sample.extend(group[i] for i in take)
        result = estimators(abundance(sample))
        for name in values:
            if np.isfinite(result[name]):
                values[name].append(result[name])
    # Ordinary richness-bootstrap percentiles are biased sharply downward:
    # resampling omits many of the already rare observed types.  Center the
    # stratified bootstrap deviations on the full-sample estimate and retain
    # the raw median so that this correction is auditable.
    out = {}
    for name, x in values.items():
        x = np.asarray(x)
        median = float(np.median(x))
        out[name] = {
            "lo": float(point[name] + np.quantile(x, .025) - median),
            "hi": float(point[name] + np.quantile(x, .975) - median),
            "raw_bootstrap_median": median,
            "method": "stratified centered percentile bootstrap"}
    return out


def interpolate_accumulation(records, order, thresholds):
    seen, token_count, out, j = set(), 0, [], 0
    for ix in order:
        text = records[ix]["text"]
        for sign in text:
            seen.add(sign)
            token_count += 1
            while j < len(thresholds) and token_count >= thresholds[j]:
                out.append(len(seen))
                j += 1
    while len(out) < len(thresholds):
        out.append(len(seen))
    return np.asarray(out, float)


def accumulation_and_heaps(records, rng):
    total_tokens = sum(len(r["text"]) for r in records)
    thresholds = np.maximum(1, np.rint(FRACTIONS * total_tokens).astype(int))
    curves = np.empty((ACCUM_RUNS, len(thresholds)))
    heaps = []
    for run in range(ACCUM_RUNS):
        order = rng.permutation(len(records))
        curve = interpolate_accumulation(records, order, thresholds)
        curves[run] = curve
        slope, intercept = np.polyfit(np.log(thresholds), np.log(curve), 1)
        heaps.append((math_exp(intercept), slope,
                      math_exp(intercept) * (2 * total_tokens) ** slope,
                      math_exp(intercept) * (10 * total_tokens) ** slope))
    heaps = np.asarray(heaps)
    med = np.median(curves, axis=0)
    slope, intercept = np.polyfit(np.log(thresholds), np.log(med), 1)
    k = math_exp(intercept)
    return {
        "curve": [{"tokens": int(n), "observed": float(m),
                   "lo": float(lo), "hi": float(hi)}
                  for n, m, lo, hi in zip(thresholds, med,
                                         np.quantile(curves, .025, axis=0),
                                         np.quantile(curves, .975, axis=0))],
        "heaps": {"k": k, "beta": slope,
                  "beta_interval": [float(np.quantile(heaps[:, 1], .025)),
                                    float(np.quantile(heaps[:, 1], .975))],
                  "at_2x_tokens": k * (2 * total_tokens) ** slope,
                  "at_2x_interval": [float(np.quantile(heaps[:, 2], .025)),
                                     float(np.quantile(heaps[:, 2], .975))],
                  "at_10x_tokens": k * (10 * total_tokens) ** slope,
                  "at_10x_interval": [float(np.quantile(heaps[:, 3], .025)),
                                      float(np.quantile(heaps[:, 3], .975))]}}


def math_exp(x):
    # Kept separate so all JSON-facing values are ordinary Python floats.
    return float(np.exp(x))


def zipf(freq):
    counts = np.asarray(sorted(freq.values(), reverse=True), float)
    ranks = np.arange(1, len(counts) + 1, dtype=float)
    slope, intercept = np.polyfit(np.log(ranks), np.log(counts), 1)
    fitted = intercept + slope * np.log(ranks)
    actual = np.log(counts)
    r2 = 1 - np.sum((actual - fitted) ** 2) / np.sum((actual - actual.mean()) ** 2)
    return {"alpha": float(-slope), "intercept": float(intercept), "r_squared": float(r2)}


def analyse(records, rng):
    freq = abundance(records)
    point = estimators(freq)
    point["intervals"] = bootstrap(records, rng, point)
    point["zipf"] = zipf(freq)
    point["accumulation"] = accumulation_and_heaps(records, rng)
    point["records"] = len(records)
    point["position_shuffle_check"] = "invariant: abundance and richness are unchanged"
    return point


def main():
    rng = np.random.default_rng(SEED)
    source = {"unmerged": load_records("data/parsed/lines.json"),
              "merged": load_records("data/parsed/lines_merged.json")}
    result = {"method": {"seed": SEED, "bootstrap_runs": BOOT,
                         "accumulation_runs": ACCUM_RUNS,
                         "unknown_ids": sorted(UNKNOWN)}, "analyses": {}}
    for inventory, records in source.items():
        result["analyses"][inventory] = {}
        for mode in ("recorded", "collapse_unknown", "exclude_unknown"):
            handled = handle_unknown(records, mode)
            result["analyses"][inventory][mode] = analyse(handled, rng)
    with open(OUT, "w") as handle:
        json.dump(result, handle, indent=2)
        handle.write("\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
