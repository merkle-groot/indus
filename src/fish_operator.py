"""Hypothesis: the fish is a value, and its body-marks are operators applied to it.

This is not the hypothesis rejected in 06-fish.md. There the modifier was the
number; here the *fish* is the number and the modifier is a function on it.
Different predictions:

  P1  If the fish is a value, it should belong to the same distributional class
      as the stroke numerals -- i.e. substitute for them in minimal pairs.
  P2  A binary operation needs a second operand. Marked fish should therefore
      take a preceding numeral MORE often than plain fish, not less.
  P3  Different operators should select different operand ranges, so the value
      distribution of the preceding numeral should differ by fish variant.
  P4  Values sit where values sit. Fish should occupy the same positional zone
      as the stroke numerals.
  P5  Operators do not usually stack arbitrarily, while values recur freely.
"""
import json
from collections import Counter, defaultdict
from itertools import combinations

import numpy as np
from scipy import stats

NUMS = {}
for i in range(1, 8):
    NUMS[i] = i
for i in range(31, 36):
    NUMS[i] = i - 30
for i in range(12, 20):
    NUMS[i] = i - 10

PLAIN = {220}
MARKED = {240: "X", 235: "roof", 233: "topcross", 231: "line",
          226: "flank", 236: "roof+flank", 241: "X+flank", 232: "line+flank",
          222: "bracket+hook", 234: "flank2", 243: "framed"}
FISH = set(PLAIN) | set(MARKED)

lines = json.loads(open("data/parsed/lines.json").read())
texts = [tuple(l["signs"]) for l in lines if l["signs"]]
tok = [g for t in texts for g in t]

# ---------------------------------------------------- P1 cross-substitution
uniq = sorted(set(texts))
by_len = defaultdict(list)
for t in uniq:
    by_len[len(t)].append(t)
pairs = []
for L, ts in by_len.items():
    if L < 2:
        continue
    for a, b in combinations(ts, 2):
        d = [i for i in range(L) if a[i] != b[i]]
        if len(d) == 1:
            pairs.append((a, b, d[0]))

n_pairs = len(pairs)
p_num = (sum(a[i] in NUMS for a, b, i in pairs)
         + sum(b[i] in NUMS for a, b, i in pairs)) / (2 * n_pairs)
p_fish = (sum(a[i] in FISH for a, b, i in pairs)
          + sum(b[i] in FISH for a, b, i in pairs)) / (2 * n_pairs)

nn = sum(a[i] in NUMS and b[i] in NUMS for a, b, i in pairs)
ff = sum(a[i] in FISH and b[i] in FISH for a, b, i in pairs)
nf = sum((a[i] in NUMS and b[i] in FISH) or (a[i] in FISH and b[i] in NUMS)
         for a, b, i in pairs)

print("=== P1: do fish substitute for stroke numerals? ===")
print(f"  minimal pairs: {n_pairs}")
print(f"  numeral <-> numeral : {nn:>4}   expected {p_num**2*n_pairs:>6.1f}   "
      f"lift {nn/(p_num**2*n_pairs):.2f}")
print(f"  fish    <-> fish    : {ff:>4}   expected {p_fish**2*n_pairs:>6.1f}   "
      f"lift {ff/(p_fish**2*n_pairs):.2f}")
print(f"  numeral <-> fish    : {nf:>4}   expected {2*p_num*p_fish*n_pairs:>6.1f}   "
      f"lift {nf/(2*p_num*p_fish*n_pairs):.2f}")
r = stats.binomtest(nf, n_pairs, 2 * p_num * p_fish)
print(f"  binomial p for the cross term = {r.pvalue:.3g}")
print("  -> if the fish were a value it should swap with numerals freely")

# ---------------------------------------------------- P2 operand requirement
print("\n=== P2: do MARKED fish take a preceding numeral more than PLAIN? ===")
rows = []
for g in sorted(FISH, key=lambda g: -Counter(tok)[g]):
    tot = prev = 0
    for t in texts:
        for j, s in enumerate(t):
            if s == g and j > 0:
                tot += 1
                prev += t[j - 1] in NUMS
    if tot >= 10:
        rows.append((g, "plain" if g in PLAIN else MARKED.get(g, "?"), tot, prev))
for g, lab, tot, prev in rows:
    print(f"  {g:>5} {lab:<13} {prev:>4}/{tot:<4} {prev/tot:>6.1%}")
pl = [r for r in rows if r[0] in PLAIN]
mk = [r for r in rows if r[0] not in PLAIN]
if pl and mk:
    a, b = sum(r[3] for r in pl), sum(r[2] for r in pl)
    c, d = sum(r[3] for r in mk), sum(r[2] for r in mk)
    _, pv, *_ = stats.chi2_contingency([[a, b - a], [c, d - c]])
    print(f"  plain  {a}/{b} = {a/b:.1%}    marked {c}/{d} = {c/d:.1%}   p={pv:.3g}")
    print("  -> operator reading predicts marked > plain")

# ---------------------------------------------------- P3 operand selectivity
print("\n=== P3: do different marks select different operand values? ===")
dist = {}
for g in sorted(FISH):
    v = Counter()
    for t in texts:
        for j, s in enumerate(t):
            if s == g and j > 0 and t[j - 1] in NUMS:
                v[NUMS[t[j - 1]]] += 1
    if sum(v.values()) >= 15:
        dist[g] = v
labs = sorted(dist)
allv = sorted({k for v in dist.values() for k in v})
print(f"  {'sign':>5} {'form':<10} " + " ".join(f"{v:>4}" for v in allv))
for g in labs:
    print(f"  {g:>5} {('plain' if g in PLAIN else MARKED.get(g,'?')):<10} "
          + " ".join(f"{dist[g].get(v,0):>4}" for v in allv))
if len(labs) > 1:
    table = np.array([[dist[g].get(v, 0) for v in allv] for g in labs])
    keep = table.sum(0) > 0
    chi2, pv, *_ = stats.chi2_contingency(table[:, keep])
    print(f"  chi-square across variants: p = {pv:.3g}")
    print("  -> operator reading predicts different operand profiles")

# ---------------------------------------------------- P4 position
print("\n=== P4: do fish sit where numerals sit? ===")
def mpos(S):
    return [j / (len(t) - 1) for t in texts if len(t) > 1
            for j, g in enumerate(t) if g in S]
pn, pf = mpos(NUMS), mpos(FISH)
pb = [j / (len(t) - 1) for t in texts if len(t) > 1 for j in range(len(t))]
print(f"  numerals mean position {np.mean(pn):.3f}  (n={len(pn)})")
print(f"  fish     mean position {np.mean(pf):.3f}  (n={len(pf)})")
print(f"  baseline               {np.mean(pb):.3f}")
print(f"  numerals vs fish, Mann-Whitney p = {stats.mannwhitneyu(pn, pf).pvalue:.3g}")

# ---------------------------------------------------- P5 stacking
print("\n=== P5: how freely do fish and numerals repeat within one text? ===")
for name, S in (("numerals", set(NUMS)), ("fish", FISH)):
    per = [sum(g in S for g in t) for t in texts]
    c = Counter(per)
    tot = sum(1 for p in per if p)
    print(f"  {name:<9} texts with >=1: {tot:<5} "
          f">=2: {sum(v for k, v in c.items() if k >= 2):<5} "
          f">=3: {sum(v for k, v in c.items() if k >= 3)}")
adjacent = sum(1 for t in texts for x, y in zip(t, t[1:]) if x in FISH and y in FISH)
print(f"  adjacent fish-fish pairs: {adjacent}")
