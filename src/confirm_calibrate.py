"""Held-out confirmation and empirical false-positive calibration.

Four fixed findings are evaluated in a stratified random split and a disjoint
site split: repeat avoidance, 740/520 exclusion, terminal-set finality, and
numeral-side overdispersion.  Statistic-specific positional nulls are used.

Calibration then sends exact-position surrogate corpora, random pairs, and
frequency-matched random seven-sign sets through the same decisions.  The
surrogates preserve length, absolute position, site, object, and sign frequency
while destroying which signs share a text.
"""
import json
import math
from collections import Counter, defaultdict

import numpy as np

SEED = 36
CONFIRM_RUNS = 1000
CAL_RUNS = 300
SIDE_INNER = 199
RANDOM_HYPOTHESES = 5000
TERMINAL = {740, 520, 390, 151, 527, 617, 156}
NUMERALS = ({1, 2, 3, 4, 5, 6, 7, 13, 14, 15, 16, 17, 18, 19,
             27, 28, 29, 31, 32, 33, 34, 35, 36, 48, 49, 50, 51,
             55, 56, 57})
OUT = "data/parsed/confirmation_calibration.json"


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
    return out


def with_texts(records, texts):
    return [{"text": tuple(text), "site": r["site"], "object": r["object"]}
            for r, text in zip(records, texts)]


def interval(values):
    values = np.asarray(values, float)
    return {"mean": float(values.mean()), "lo": float(np.quantile(values, .025)),
            "hi": float(np.quantile(values, .975)), "sd": float(values.std(ddof=1))}


def wilson(k, n, z=1.96):
    p = k / n
    den = 1 + z * z / n
    center = (p + z * z / (2 * n)) / den
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return [center - half, center + half]


def repeat_count(records):
    return sum(len(set(r["text"])) < len(r["text"]) for r in records)


def cooccurrence(records, pair):
    return sum(set(pair) <= set(r["text"]) for r in records)


def terminal_count(records, signs=TERMINAL):
    return sum(r["text"][-1] in signs for r in records)


def terminal_null(records, signs, rng, runs):
    values = []
    for _ in range(runs):
        total = 0
        for record in records:
            text = record["text"]
            total += text[rng.integers(len(text))] in signs
        values.append(total)
    return values


def q_stat(left, totals, p):
    if not len(totals) or p in (0, 1):
        return float("nan")
    return float(np.sum((left - totals * p) ** 2 / (totals * p * (1 - p))))


def side_events(records, min_events):
    events = []
    for record in records:
        text = record["text"]
        for i, (a, b) in enumerate(zip(text, text[1:])):
            if a in NUMERALS and b not in NUMERALS:
                events.append((b, 1, len(text), i + 1, record["site"], record["object"]))
            elif a not in NUMERALS and b in NUMERALS:
                events.append((a, 0, len(text), i, record["site"], record["object"]))
    freq = Counter(e[0] for e in events)
    signs = sorted(g for g, n in freq.items() if n >= min_events)
    idx = {g: i for i, g in enumerate(signs)}
    selected = [e for e in events if e[0] in idx]
    if not selected:
        return None
    sign_index = np.asarray([idx[e[0]] for e in selected], int)
    side = np.asarray([e[1] for e in selected], np.int8)
    totals = np.bincount(sign_index, minlength=len(signs))
    groups = defaultdict(list)
    for i, event in enumerate(selected):
        groups[event[2:]].append(i)
    return events, signs, sign_index, side, totals, list(groups.values())


def side_test(records, rng, runs, min_events):
    prepared = side_events(records, min_events)
    if prepared is None:
        return None
    events, signs, sign_index, sides, totals, groups = prepared
    p = float(sides.mean())
    left = np.bincount(sign_index, weights=sides, minlength=len(signs))
    observed = q_stat(left, totals, p)
    null = []
    for _ in range(runs):
        perm = sides.copy()
        for cells in groups:
            perm[cells] = rng.permutation(perm[cells])
        counts = np.bincount(sign_index, weights=perm, minlength=len(signs))
        null.append(q_stat(counts, totals, p))
    stats = interval(null)
    stats.update({"events": len(events), "eligible_signs": len(signs),
                  "observed_q": observed, "excess_q": observed - stats["mean"],
                  "upper_p": (1 + sum(x >= observed for x in null)) / (runs + 1)})
    return stats


def confirm(records, rng, side_threshold):
    observed_repeat = repeat_count(records)
    observed_pair = cooccurrence(records, (740, 520))
    observed_terminal = terminal_count(records)
    repeat_null, pair_null = [], []
    for _ in range(CONFIRM_RUNS):
        shuffled = with_texts(records, column_shuffle(records, rng))
        repeat_null.append(repeat_count(shuffled))
        pair_null.append(cooccurrence(shuffled, (740, 520)))
    final_null = terminal_null(records, TERMINAL, rng, CONFIRM_RUNS)
    repeat_stats, pair_stats, final_stats = map(interval, (repeat_null, pair_null, final_null))
    repeat_stats.update({"observed": observed_repeat,
                         "rate": observed_repeat / len(records),
                         "rate_interval": wilson(observed_repeat, len(records)),
                         "z": (observed_repeat-repeat_stats["mean"]) / repeat_stats["sd"],
                         "lower_p": (1+sum(x <= observed_repeat for x in repeat_null))/(CONFIRM_RUNS+1)})
    pair_stats.update({"observed": observed_pair,
                       "z": (observed_pair-pair_stats["mean"]) / pair_stats["sd"],
                       "lower_p": (1+sum(x <= observed_pair for x in pair_null))/(CONFIRM_RUNS+1)})
    final_stats.update({"observed": observed_terminal,
                        "rate": observed_terminal / len(records),
                        "rate_interval": wilson(observed_terminal, len(records)),
                        "z": (observed_terminal-final_stats["mean"]) / final_stats["sd"],
                        "upper_p": (1+sum(x >= observed_terminal for x in final_null))/(CONFIRM_RUNS+1)})
    return {"records": len(records), "sites": sorted({r["site"] for r in records}),
            "no_repeat": repeat_stats, "exclusion_740_520": pair_stats,
            "terminal_set_finality": final_stats,
            "numeral_side": side_test(records, rng, CONFIRM_RUNS, side_threshold)}


def random_split(records, rng):
    groups = defaultdict(list)
    for i, record in enumerate(records):
        groups[(record["site"], record["object"])].append(i)
    halves = [[], []]
    for indices in groups.values():
        indices = np.asarray(indices)
        rng.shuffle(indices)
        cut = len(indices) // 2
        extra = int(len(indices) % 2 and rng.integers(2) == 0)
        halves[0].extend(records[i] for i in indices[:cut + extra])
        halves[1].extend(records[i] for i in indices[cut + extra:])
    return halves


def normal_cdf(z):
    return .5 * math.erfc(-z / math.sqrt(2))


def bh_any(pvalues, alpha=.05):
    pvalues = np.sort(np.asarray(pvalues))
    return bool(np.any(pvalues <= alpha * np.arange(1, len(pvalues) + 1) / len(pvalues)))


def pair_matrices(records, texts_runs, signs):
    idx = {g: i for i, g in enumerate(signs)}
    pairs = [(a, b) for i, a in enumerate(range(len(signs))) for b in range(i + 1, len(signs))]
    out = np.empty((len(texts_runs), len(pairs)), dtype=np.int16)
    for run, texts in enumerate(texts_runs):
        presence = np.zeros((len(records), len(signs)), dtype=np.uint8)
        for ri, text in enumerate(texts):
            cells = [idx[g] for g in set(text) if g in idx]
            presence[ri, cells] = 1
        co = presence.T.astype(np.int32) @ presence.astype(np.int32)
        out[run] = [co[a, b] for a, b in pairs]
    return pairs, out


def final_z(records, signs):
    observed = expected = variance = 0.0
    signs = set(signs)
    for record in records:
        text = record["text"]
        p = sum(g in signs for g in text) / len(text)
        observed += text[-1] in signs
        expected += p
        variance += p * (1 - p)
    return (observed - expected) / math.sqrt(variance), int(observed), expected


def calibration(records, rng):
    freq = Counter(g for r in records for g in set(r["text"]))
    signs = sorted(g for g, n in freq.items() if n >= 20)
    shuffled_texts = [column_shuffle(records, rng) for _ in range(CAL_RUNS)]

    repetitions = np.asarray([sum(len(set(t)) < len(t) for t in texts)
                              for texts in shuffled_texts], float)
    pair_fixed = np.asarray([sum({740, 520} <= set(t) for t in texts)
                             for texts in shuffled_texts], float)
    observed_repeat = repeat_count(records)
    observed_pair = cooccurrence(records, (740, 520))

    pairs, pair_null = pair_matrices(records, shuffled_texts, signs)
    pair_mean = pair_null.mean(axis=0)
    pair_sd = pair_null.std(axis=0, ddof=1)
    valid = pair_sd > 0
    surrogate_any = []
    for run in range(CAL_RUNS):
        z = np.zeros(len(pairs))
        z[valid] = (pair_null[run, valid] - pair_mean[valid]) / pair_sd[valid]
        surrogate_any.append(bh_any([normal_cdf(x) for x in z[valid]]))

    real_presence = np.zeros((len(records), len(signs)), dtype=np.uint8)
    index = {g: i for i, g in enumerate(signs)}
    for ri, record in enumerate(records):
        real_presence[ri, [index[g] for g in set(record["text"]) if g in index]] = 1
    real_co = real_presence.T.astype(np.int32) @ real_presence.astype(np.int32)
    real_pair_values = np.asarray([real_co[a, b] for a, b in pairs])
    real_z = np.zeros(len(pairs)); real_z[valid] = (real_pair_values[valid]-pair_mean[valid])/pair_sd[valid]

    pair_lookup = {(signs[a], signs[b]): j for j, (a, b) in enumerate(pairs)}
    eligible_pairs = list(pair_lookup)
    fabricated_p = []
    for _ in range(RANDOM_HYPOTHESES):
        pair = eligible_pairs[rng.integers(len(eligible_pairs))]
        fabricated_p.append(normal_cdf(real_z[pair_lookup[pair]]))

    # Frequency-rank-matched random seven-sign sets, excluding the known set.
    ranked = [g for g, _ in sorted(freq.items(), key=lambda x: (-x[1], x[0])) if g in index]
    ranks = {g: i for i, g in enumerate(ranked)}
    terminal_ranks = [ranks[g] for g in TERMINAL if g in ranks]
    random_sets, random_final_z, random_pair_min = [], [], []
    for _ in range(RANDOM_HYPOTHESES):
        chosen = set()
        for rank in terminal_ranks:
            candidates = [g for g in ranked[max(0, rank-5):rank+6]
                          if g not in TERMINAL and g not in chosen]
            if not candidates:
                candidates = [g for g in ranked if g not in TERMINAL and g not in chosen]
            chosen.add(candidates[rng.integers(len(candidates))])
        chosen = sorted(chosen)
        zf, _, _ = final_z(records, chosen)
        pvals = []
        for i, a in enumerate(chosen):
            for b in chosen[i+1:]:
                key = (a, b) if (a, b) in pair_lookup else (b, a)
                if key in pair_lookup:
                    pvals.append(normal_cdf(real_z[pair_lookup[key]]))
        random_sets.append(chosen)
        random_final_z.append(zf)
        random_pair_min.append(min(pvals) if pvals else 1.0)
    random_final_z = np.asarray(random_final_z)
    random_pair_min = np.asarray(random_pair_min)
    paradigm_calls = (random_final_z >= 1.645) & (random_pair_min <= .05 / 21)

    known_final_z, known_final_obs, known_final_expected = final_z(records, TERMINAL)
    known_pair_p = min(normal_cdf(real_z[j]) for pair, j in pair_lookup.items()
                       if pair[0] in TERMINAL and pair[1] in TERMINAL)

    # Full side-test pipeline on pairing-destroyed corpora.
    side_calls, side_excesses = [], []
    for texts in shuffled_texts:
        test = side_test(with_texts(records, texts), rng, SIDE_INNER, 15)
        side_calls.append(test is not None and test["upper_p"] <= .05)
        side_excesses.append(test["excess_q"] if test else float("nan"))
    real_side = side_test(records, rng, 999, 15)

    rep_mean, rep_sd = repetitions.mean(), repetitions.std(ddof=1)
    pair_mean_fixed, pair_sd_fixed = pair_fixed.mean(), pair_fixed.std(ddof=1)
    return {
        "surrogate_corpora": {"runs": CAL_RUNS,
            "no_repeat": {"observed": observed_repeat, "null": interval(repetitions),
                          "empirical_p": (1+sum(repetitions <= observed_repeat))/(CAL_RUNS+1),
                          "nominal_5pct_false_positive_rate": float(np.mean(repetitions <= np.quantile(repetitions, .05)))},
            "fixed_740_520": {"observed": observed_pair, "null": interval(pair_fixed),
                              "empirical_p": (1+sum(pair_fixed <= observed_pair))/(CAL_RUNS+1),
                              "nominal_5pct_false_positive_rate": float(np.mean(pair_fixed <= np.quantile(pair_fixed, .05)))},
            "pair_scan": {"pairs": len(pairs), "surrogates_with_any_bh_discovery": int(sum(surrogate_any)),
                          "familywise_false_positive_rate": float(np.mean(surrogate_any)),
                          "real_bh_any": bh_any([normal_cdf(x) for x in real_z[valid]]),
                          "real_min_z": float(real_z.min())},
            "numeral_side_pipeline": {"tested_surrogates": len(side_calls),
                                      "false_positive_rate": float(np.mean(side_calls)),
                                      "real": real_side,
                                      "surrogate_excess_q": interval(np.asarray(side_excesses)[np.isfinite(side_excesses)])}},
        "fabricated_hypotheses": {
            "random_pairs": {"draws": RANDOM_HYPOTHESES,
                             "nominal_p_below_05": float(np.mean(np.asarray(fabricated_p) < .05)),
                             "p_below_bonferroni": float(np.mean(np.asarray(fabricated_p) < .05/len(pairs)))},
            "frequency_matched_seven_sign_sets": {"draws": RANDOM_HYPOTHESES,
                "pipeline_false_positive_rate": float(np.mean(paradigm_calls)),
                "random_final_z_95": [float(np.quantile(random_final_z,.025)), float(np.quantile(random_final_z,.975))],
                "known_terminal": {"final_z": known_final_z, "final_observed": known_final_obs,
                                   "final_expected": known_final_expected,
                                   "best_pair_p": known_pair_p,
                                   "pipeline_pass": known_final_z >= 1.645 and known_pair_p <= .05/21}}}}


def main():
    rng = np.random.default_rng(SEED)
    records = load_records()
    halves = random_split(records, rng)
    site_halves = [[r for r in records if r["site"] == "SI1"],
                   [r for r in records if r["site"] != "SI1"]]
    result = {"method": {"seed": SEED, "confirm_runs": CONFIRM_RUNS,
                         "calibration_runs": CAL_RUNS, "side_inner_runs": SIDE_INNER,
                         "random_hypotheses": RANDOM_HYPOTHESES,
                         "random_split": "within site x object strata",
                         "site_split": "SI1 versus all other sites"},
              "confirmation": {"random": {}, "by_site": {}},
              "calibration": None}
    for i, half in enumerate(halves, 1):
        result["confirmation"]["random"][f"half_{i}"] = confirm(half, rng, 8)
    for name, half in zip(("SI1", "other_sites"), site_halves):
        result["confirmation"]["by_site"][name] = confirm(half, rng, 8)
    result["calibration"] = calibration(records, rng)
    with open(OUT, "w") as handle:
        json.dump(result, handle, indent=2)
        handle.write("\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
