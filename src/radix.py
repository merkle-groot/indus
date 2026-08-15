"""Is there a radix, and is it 10?

Two signatures of a base-B system:
  (a) truncation -- single-symbol stroke counts run 1..B-1 and stop, because B
      gets its own higher-order representation;
  (b) composition -- a higher-order symbol combines with a lower one, and the
      lower tier's maximum is B-1.

We have three stroke series whose ids encode stroke count. If they are tiers of
one system (rather than three unrelated notations) they should co-occur, in a
consistent order, with a bounded lower tier.
"""
import json
from collections import Counter, defaultdict
from itertools import combinations

import numpy as np
from scipy import stats

SERIES = {}
for i in range(1, 8):
    SERIES[i] = ("short", i)
for i in range(31, 36):
    SERIES[i] = ("long", i - 30)
for i in range(12, 20):
    # verified by eye on the rendered chart: id 16 is |||/||| = 6 strokes,
    # 17 is ||||/||| = 7, 18 is ||||/|||| = 8, 19 is |||||/|||| = 9.
    SERIES[i] = ("tworow", i - 10)
NUM = set(SERIES)

lines = json.loads(open("data/parsed/lines.json").read())
texts = [tuple(l["signs"]) for l in lines if l["signs"]]
tokens = [g for t in texts for g in t]
cnt = Counter(tokens)

# ------------------------------------------------------- (a) truncation
print("=== value distribution per series ===")
for s in ("short", "long", "tworow"):
    vals = sorted((v, cnt.get(i, 0)) for i, (ss, v) in SERIES.items() if ss == s)
    tot = sum(c for _, c in vals)
    print(f"\n  {s}  (n={tot})")
    mx = max(c for _, c in vals) or 1
    for v, c in vals:
        print(f"    {v:>2} | {c:>4} {'#' * round(46 * c / mx)}")
    present = [v for v, c in vals if c > 0]
    print(f"    values attested: {present}  max={max(present) if present else None}")

# ------------------------------------------------------- (b) composition
print("\n" + "=" * 66)
print("=== do the series co-occur in the same text? ===")
have = defaultdict(set)
for ti, t in enumerate(texts):
    for g in t:
        if g in NUM:
            have[ti].add(SERIES[g][0])
pat = Counter(frozenset(v) for v in have.values())
print(f"  texts containing at least one numeral: {len(have)} / {len(texts)}")
for k, c in pat.most_common():
    print(f"    {'+'.join(sorted(k)):<22} {c:>5}")

# expected co-occurrence if series were independent across texts
n = len(texts)
p = {s: sum(s in v for v in have.values()) / n for s in ("short", "long", "tworow")}
print("\n  pairwise co-occurrence, observed vs independent expectation:")
for a, b in combinations(("short", "long", "tworow"), 2):
    obs = sum(a in v and b in v for v in have.values())
    exp = p[a] * p[b] * n
    tab = [[obs, sum(a in v and b not in v for v in have.values())],
           [sum(b in v and a not in v for v in have.values()),
            sum(a not in v and b not in v for v in have.values())]]
    _, pv, *_ = stats.chi2_contingency(tab)
    print(f"    {a:>6} + {b:<7} obs {obs:>4}   exp {exp:>6.1f}   "
          f"ratio {obs/exp if exp else 0:>5.2f}   p={pv:.2g}")

# ------------------------------------------------------- adjacency & order
print("\n" + "=" * 66)
print("=== adjacent numeral pairs (reading order: left = earlier) ===")
adj = Counter()
for t in texts:
    for x, y in zip(t, t[1:]):
        if x in NUM and y in NUM:
            adj[(SERIES[x][0], SERIES[y][0])] += 1
tot_adj = sum(adj.values())
print(f"  total adjacent numeral-numeral pairs: {tot_adj}")
for (a, b), c in adj.most_common():
    print(f"    {a:>6} -> {b:<7} {c:>4}")

if tot_adj:
    print("\n  order asymmetry (is one series consistently first?)")
    for a, b in combinations(("short", "long", "tworow"), 2):
        ab, ba = adj.get((a, b), 0), adj.get((b, a), 0)
        if ab + ba:
            r = stats.binomtest(ab, ab + ba, 0.5)
            print(f"    {a}->{b} {ab:>3}   vs   {b}->{a} {ba:>3}   p={r.pvalue:.3g}")

    print("\n  values in adjacent pairs (are they additive-looking?)")
    pv = Counter()
    for t in texts:
        for x, y in zip(t, t[1:]):
            if x in NUM and y in NUM:
                pv[(SERIES[x], SERIES[y])] += 1
    for (sx, sy), c in pv.most_common(12):
        print(f"    {sx[0]}{sx[1]} + {sy[0]}{sy[1]}  ->  {c}")

# ------------------------------------------------------- radix scan
print("\n" + "=" * 66)
print("=== which radix is consistent with the attested maxima? ===")
for s in ("short", "long", "tworow"):
    present = sorted(v for i, (ss, v) in SERIES.items() if ss == s and cnt.get(i, 0) > 0)
    rare = [v for i, (ss, v) in SERIES.items()
            if ss == s and 0 < cnt.get(i, 0) <= 3]
    solid = [v for i, (ss, v) in SERIES.items() if ss == s and cnt.get(i, 0) > 3]
    print(f"  {s:<7} attested {present}")
    print(f"          well-attested (>3 tokens) {sorted(solid)}   "
          f"marginal (<=3) {sorted(rare)}")
    if solid:
        print(f"          -> truncation at {max(solid)} implies radix "
              f"{max(solid)+1}")
