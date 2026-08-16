"""Does each sign prefer its numeral on a particular side?

24-linear-b.md pooled every adjacency and found almost equal totals.  A pooled
average can hide sign-specific rules, so this script measures the numeral-left
share for every non-numeral sign with at least 15 numeral adjacencies.

The requested null is independent binomial draws at the corpus base rate.  The
house-rule controls are stricter permutations of the side labels among events:

  position       within exact (text length, focal-sign index)
  site/object    within (site, object class)
  combined       within (length, index, site, object class)

These keep each sign's number of adjacency events fixed and, for the combined
null, preserve all available positional and contextual confounds.  The test
statistic is Pearson overdispersion across sign-specific left/right splits.
"""
import json
import math
from collections import Counter, defaultdict

import numpy as np
from scipy import stats

MIN_ADJ = 15
N_PERM = 5000
RNG = np.random.default_rng(28)

NUMERALS = (set(range(1, 8)) | {31, 32, 33, 34, 35, 36} |
            set(range(12, 20)))
FISH = {220, 240, 235, 233, 231, 226, 236, 222, 241, 243, 232, 234}
FROZEN = {(817, 2), (861, 2), (820, 2), (840, 32)}

inscriptions = json.load(open("data/parsed/inscriptions.json"))
allograph = json.load(open("data/parsed/allograph_map.json"))["map"]
merge = {int(k): v for k, v in allograph.items()}


def inscription_lines(ins):
    out, current = [], []
    for g in ins["glyphs"] + [0]:
        if g == 0:
            if current:
                # Round 27: every raw GLYPHSEQUENCE line needs reversal.
                out.append(tuple(merge.get(x, x) for x in current[::-1]))
                current = []
        else:
            current.append(g)
    return out


recs, seen = [], set()
for ins in inscriptions:
    for text in inscription_lines(ins):
        key = (text, ins.get("site"))
        if key in seen:
            continue
        seen.add(key)
        recs.append({"text": text, "site": ins.get("site"),
                     "object": ins.get("obj_class")})

# y=1 means the numeral is on the left: [numeral, focal sign].
events = []
for rec in recs:
    text = rec["text"]
    for i, (a, b) in enumerate(zip(text, text[1:])):
        if a in NUMERALS and b not in NUMERALS:
            events.append({"sign": b, "side": 1, "length": len(text),
                           "index": i + 1, "site": rec["site"],
                           "object": rec["object"], "pair": (a, b)})
        if a not in NUMERALS and b in NUMERALS:
            events.append({"sign": a, "side": 0, "length": len(text),
                           "index": i, "site": rec["site"],
                           "object": rec["object"], "pair": (a, b)})

adj_freq = Counter(e["sign"] for e in events)
signs = sorted(g for g, n in adj_freq.items() if n >= MIN_ADJ)
sign_index = {g: i for i, g in enumerate(signs)}
n = np.asarray([adj_freq[g] for g in signs], dtype=int)
observed_left = np.zeros(len(signs), dtype=int)
for event in events:
    if event["sign"] in sign_index:
        observed_left[sign_index[event["sign"]]] += event["side"]
base_p = sum(e["side"] for e in events) / len(events)

print("=== corpus and pooled result ===")
print(f"  deduplicated sequence x site records: {len(recs)}")
print(f"  numeral-left adjacencies: {sum(e['side'] for e in events)}")
print(f"  numeral-right adjacencies: {sum(not e['side'] for e in events)}")
print(f"  pooled numeral-left rate: {base_p:.3%}")
print(f"  signs with >= {MIN_ADJ} adjacencies: {len(signs)}")


def q_stat(left, totals, p):
    return float(np.sum((left - totals * p) ** 2 / (totals * p * (1 - p))))


observed_q = q_stat(observed_left, n, base_p)


def event_arrays(source_events, selected_signs):
    idx = {g: i for i, g in enumerate(selected_signs)}
    sign_idx = np.asarray([idx.get(e["sign"], -1) for e in source_events], dtype=int)
    sides = np.asarray([e["side"] for e in source_events], dtype=np.int8)
    totals = np.asarray([sum(e["sign"] == g for e in source_events)
                         for g in selected_signs], dtype=int)
    return idx, sign_idx, sides, totals


def grouped_indices(source_events, fields):
    groups = defaultdict(list)
    for i, event in enumerate(source_events):
        groups[tuple(event[f] for f in fields)].append(i)
    return [np.asarray(v, dtype=int) for v in groups.values() if len(v) > 1]


def permutation_counts(source_events, selected_signs, fields, runs=N_PERM):
    _, event_sign, sides, totals = event_arrays(source_events, selected_signs)
    groups = grouped_indices(source_events, fields)
    valid = event_sign >= 0
    out = np.empty((runs, len(selected_signs)), dtype=np.int16)
    for run in range(runs):
        perm = sides.copy()
        for group in groups:
            perm[group] = RNG.permutation(perm[group])
        out[run] = np.bincount(event_sign[valid], weights=perm[valid],
                               minlength=len(selected_signs)).astype(np.int16)
    return out, totals


# Requested independent-token mixture.
coin_counts = RNG.binomial(n, base_p, size=(N_PERM, len(signs)))
coin_q = np.asarray([q_stat(row, n, base_p) for row in coin_counts])

null_specs = {
    "coin flips": None,
    "position": ("length", "index"),
    "site + object": ("site", "object"),
    "position + site + object": ("length", "index", "site", "object"),
}
null_q = {"coin flips": coin_q}
combined_counts = None
for label, fields in null_specs.items():
    if fields is None:
        continue
    counts, totals = permutation_counts(events, signs, fields)
    assert np.array_equal(totals, n)
    q = np.asarray([q_stat(row, n, base_p) for row in counts])
    null_q[label] = q
    if label == "position + site + object":
        combined_counts = counts

print("\n=== overdispersion of sign-specific side splits ===")
print(f"  observed Pearson Q = {observed_q:.1f} on {len(signs)-1} df; "
      f"dispersion = {observed_q/(len(signs)-1):.1f}x")
print("  null                         mean Q     null 95%       upper p")
for label in null_specs:
    values = null_q[label]
    lo, hi = np.quantile(values, [.025, .975])
    p = (1 + np.sum(values >= observed_q)) / (len(values) + 1)
    print(f"  {label:<28} {values.mean():>7.1f}  {lo:>7.1f}-{hi:<7.1f} {p:>9.5f}")

shares = observed_left / n
bins = [(0, .1), (.1, .3), (.3, .7), (.7, .9), (.9, 1.000001)]
print("\n  observed split histogram (numeral-left share)")
for lo, hi in bins:
    print(f"    {lo:.1f} <= p < {min(hi,1):.1f}: "
          f"{sum((shares >= lo) & (shares < hi))} signs")
extreme_obs = int(np.sum((shares <= .1) | (shares >= .9)))
extreme_coin = np.sum(((coin_counts / n) <= .1) | ((coin_counts / n) >= .9), axis=1)
print(f"  signs at <=10% or >=90%: observed {extreme_obs}; "
      f"coin-null mean {extreme_coin.mean():.2f}, max {extreme_coin.max()}")


# Per-sign empirical p under the combined control.  BH is applied over all 37.
individual = []
for i, g in enumerate(signs):
    lower = (1 + np.sum(combined_counts[:, i] <= observed_left[i])) / (N_PERM + 1)
    upper = (1 + np.sum(combined_counts[:, i] >= observed_left[i])) / (N_PERM + 1)
    p = min(1, 2 * min(lower, upper))
    individual.append({"sign": g, "n": n[i], "left": observed_left[i],
                       "share": shares[i], "null_left": combined_counts[:, i].mean(),
                       "p": p})
ordered = sorted(individual, key=lambda r: r["p"])
discoveries = []
for rank, row in enumerate(ordered, 1):
    if row["p"] <= .05 * rank / len(ordered):
        discoveries = ordered[:rank]
surviving = {r["sign"] for r in discoveries}

print("\n=== every sign with >=15 numeral adjacencies ===")
print("  sign    n  numeral-left numeral-right  left share  controlled E(left)  "
      "controlled p  BH")
for row in sorted(individual, key=lambda r: (r["share"], r["sign"])):
    print(f"  {row['sign']:>4} {row['n']:>4} {row['left']:>13} "
          f"{row['n']-row['left']:>13} {row['share']:>10.1%} "
          f"{row['null_left']:>18.1f} {row['p']:>13.5f}  "
          f"{'yes' if row['sign'] in surviving else 'no'}")
print(f"  combined-control BH discoveries: {len(discoveries)} / {len(signs)}")


# Frozen-pair robustness: remove the known 817/861/820+2 and 840+32 edges,
# then rerun the most conservative global null.
unfrozen = [e for e in events if e["pair"] not in FROZEN]
unfrozen_freq = Counter(e["sign"] for e in unfrozen)
unfrozen_signs = sorted(g for g, count in unfrozen_freq.items() if count >= MIN_ADJ)
_, unfrozen_idx, unfrozen_side, unfrozen_n = event_arrays(unfrozen, unfrozen_signs)
unfrozen_left = np.bincount(unfrozen_idx[unfrozen_idx >= 0],
                            weights=unfrozen_side[unfrozen_idx >= 0],
                            minlength=len(unfrozen_signs))
unfrozen_p = unfrozen_side.mean()
unfrozen_q_obs = q_stat(unfrozen_left, unfrozen_n, unfrozen_p)
unfrozen_counts, _ = permutation_counts(
    unfrozen, unfrozen_signs, ("length", "index", "site", "object"))
unfrozen_q = np.asarray([q_stat(row, unfrozen_n, unfrozen_p)
                         for row in unfrozen_counts])
print("\n=== robustness: remove the four known frozen pairs ===")
print(f"  events {len(events)} -> {len(unfrozen)}; eligible signs "
      f"{len(signs)} -> {len(unfrozen_signs)}")
print(f"  observed Q {unfrozen_q_obs:.1f}; combined-control mean "
      f"{unfrozen_q.mean():.1f}, 95% "
      f"{np.quantile(unfrozen_q,.025):.1f}-{np.quantile(unfrozen_q,.975):.1f}; "
      f"p = {(1+np.sum(unfrozen_q>=unfrozen_q_obs))/(N_PERM+1):.5f}")


# ---------------------------------------------------------------- correlates
all_positions = defaultdict(list)
for rec in recs:
    text = rec["text"]
    for i, g in enumerate(text):
        all_positions[g].append(i / (len(text) - 1) if len(text) > 1 else .5)
mean_position = [np.mean(all_positions[g]) for g in signs]
rho, p_rho = stats.spearmanr(shares, mean_position)


def cmh_binary(source_events, exposure, stratum):
    groups = defaultdict(list)
    for event in source_events:
        x = exposure(event)
        if x is not None:
            groups[stratum(event)].append((int(x), event["side"]))
    num = den = ad = bc = 0.0
    used = 0
    for rows in groups.values():
        total = len(rows)
        nx = sum(x for x, y in rows)
        ny = sum(y for x, y in rows)
        a = sum(x and y for x, y in rows)
        if total < 2 or nx in (0, total) or ny in (0, total):
            continue
        expected = nx * ny / total
        variance = nx * (total - nx) * ny * (total - ny) / (total * total * (total - 1))
        num += a - expected
        den += variance
        b, c = nx - a, ny - a
        d = total - a - b - c
        ad += a * d / total
        bc += b * c / total
        used += 1
    z = num / math.sqrt(den) if den else float("nan")
    return {"strata": used, "z": z, "p": 2 * stats.norm.sf(abs(z)),
            "or": ad / bc if bc else float("inf")}


object_test = cmh_binary(
    events,
    lambda e: True if e["object"] == "seal" else False if e["object"] == "tablet" else None,
    lambda e: (e["sign"], e["length"], e["index"], e["site"]))
site_test = cmh_binary(
    events,
    lambda e: True if e["site"] == "SI1" else False if e["site"] == "SI2" else None,
    lambda e: (e["sign"], e["length"], e["index"], e["object"]))
fish_test = cmh_binary(
    events, lambda e: e["sign"] in FISH,
    lambda e: (e["length"], e["index"], e["site"], e["object"]))

fish_counts = Counter((e["sign"] in FISH, e["side"]) for e in events)
print("\n=== available correlates of side ===")
print(f"  sign split vs mean text position: Spearman rho {rho:.3f}, p={p_rho:.4g}")
print("  contrast (outcome=numeral left)         CMH strata    OR       z        p")
print(f"  seal vs tablet, controlling sign/position/site "
      f"{object_test['strata']:>5} {object_test['or']:>8.3f} "
      f"{object_test['z']:>8.2f} {object_test['p']:>9.4g}")
print(f"  Mohenjo-daro vs Harappa, control sign/position/object "
      f"{site_test['strata']:>3} {site_test['or']:>8.3f} "
      f"{site_test['z']:>8.2f} {site_test['p']:>9.4g}")
print(f"  fish vs other, controlling position/site/object "
      f"{fish_test['strata']:>11} {fish_test['or']:>8.3f} "
      f"{fish_test['z']:>8.2f} {fish_test['p']:>9.4g}")
fish_left, fish_right = fish_counts[(True, 1)], fish_counts[(True, 0)]
other_left, other_right = fish_counts[(False, 1)], fish_counts[(False, 0)]
print(f"  raw fish split: {fish_left}/{fish_left+fish_right} numeral-left "
      f"({fish_left/(fish_left+fish_right):.1%}); other signs "
      f"{other_left}/{other_left+other_right} "
      f"({other_left/(other_left+other_right):.1%})")
