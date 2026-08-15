"""Are the stroke signs numerals, and do texts vary like denominations?

Sign ids encode stroke count, so the numeral candidates are identifiable:
  short strokes  1-7    (single row, small)
  long strokes   31-35  (single row, full height)
  two-row groups 12-19  (strokes stacked in two rows)

The denomination hypothesis makes a testable prediction. If inscriptions are
like coins -- fixed legend, variable value -- then among pairs of texts that
differ in exactly one position, that position should be a numeral far more
often than chance.

The within-pair design controls for everything about the text: we compare the
one varying slot against the shared slots of the very same pair.
"""
import json
from collections import Counter, defaultdict
from itertools import combinations

import numpy as np
from scipy import stats

SHORT = set(range(1, 8))
LONG = {31, 32, 33, 34, 35}
TWOROW = set(range(12, 20))
NUM = SHORT | LONG | TWOROW
VALUE = {**{i: i for i in SHORT}, **{i: i - 30 for i in LONG},
         **{i: i for i in TWOROW}}
SERIES = {**{i: "short" for i in SHORT}, **{i: "long" for i in LONG},
          **{i: "tworow" for i in TWOROW}}

lines = json.loads(open("data/parsed/lines.json").read())
texts = [tuple(l["signs"]) for l in lines if l["signs"]]
uniq = sorted(set(texts))
tokens = [g for t in texts for g in t]

print(f"lines {len(texts)}   distinct texts {len(uniq)}   tokens {len(tokens)}")
nrate = sum(g in NUM for g in tokens) / len(tokens)
print(f"numeral tokens: {sum(g in NUM for g in tokens)} ({nrate:.1%} of corpus)")
for s in ("short", "long", "tworow"):
    ids = [i for i in NUM if SERIES[i] == s]
    c = Counter(g for g in tokens if g in ids)
    print(f"  {s:<7} " + "  ".join(f"{VALUE[i]}:{c.get(i,0)}" for i in sorted(ids, key=lambda i: VALUE[i])))

# ---------------------------------------------------------------- minimal pairs
by_len = defaultdict(list)
for t in uniq:
    by_len[len(t)].append(t)

pairs = []
for L, ts in by_len.items():
    if L < 2:
        continue
    for a, b in combinations(ts, 2):
        diff = [i for i in range(L) if a[i] != b[i]]
        if len(diff) == 1:
            pairs.append((a, b, diff[0]))

print(f"\nminimal pairs (same length, differ at exactly one slot): {len(pairs)}")

var_signs, shared_signs = [], []
for a, b, i in pairs:
    var_signs += [a[i], b[i]]
    shared_signs += [a[j] for j in range(len(a)) if j != i]

v_num = sum(g in NUM for g in var_signs)
s_num = sum(g in NUM for g in shared_signs)
print(f"  varying slots : {v_num}/{len(var_signs)} numerals  ({v_num/len(var_signs):.1%})")
print(f"  shared slots  : {s_num}/{len(shared_signs)} numerals  ({s_num/len(shared_signs):.1%})")
tab = [[v_num, len(var_signs) - v_num], [s_num, len(shared_signs) - s_num]]
chi2, p, *_ = stats.chi2_contingency(tab)
odds = (tab[0][0] * tab[1][1]) / max(tab[0][1] * tab[1][0], 1)
print(f"  odds ratio {odds:.2f}   chi2 p = {p:.3g}")

both = sum(a[i] in NUM and b[i] in NUM for a, b, i in pairs)
same_series = sum(a[i] in NUM and b[i] in NUM and SERIES[a[i]] == SERIES[b[i]]
                  for a, b, i in pairs)
print(f"  pairs where BOTH variants are numerals: {both}/{len(pairs)} ({both/len(pairs):.1%})")
print(f"    ...and from the same stroke series  : {same_series}")

exp = nrate ** 2
print(f"  expected 'both numerals' if slots were random: {exp:.1%} "
      f"-> {exp*len(pairs):.1f} pairs")

print("\n  the same-series minimal pairs (denomination-style variation):")
for a, b, i in pairs:
    if a[i] in NUM and b[i] in NUM and SERIES[a[i]] == SERIES[b[i]]:
        ctx = " ".join("_" if j == i else str(a[j]) for j in range(len(a)))
        print(f"    [{ctx}]   {VALUE[a[i]]} vs {VALUE[b[i]]}  ({SERIES[a[i]]})")

# ------------------------------------------------------------------- position
print("\n=== where do numerals sit? (relative position, 0=text-initial) ===")
for s in ("short", "long", "tworow"):
    pos = [j / (len(t) - 1) for t in texts if len(t) > 1
           for j, g in enumerate(t) if g in NUM and SERIES[g] == s]
    if pos:
        print(f"  {s:<7} n={len(pos):<5} mean {np.mean(pos):.3f}  median {np.median(pos):.2f}")
allpos = [j / (len(t) - 1) for t in texts if len(t) > 1 for j in range(len(t))]
print(f"  {'baseline':<7} n={len(allpos):<5} mean {np.mean(allpos):.3f}")

# --------------------------------------------------------------- what follows
print("\n=== sign immediately AFTER a numeral (reading order) ===")
after = Counter()
for t in texts:
    for j, g in enumerate(t[:-1]):
        if g in NUM:
            after[t[j + 1]] += 1
tot = sum(after.values())
base = Counter(tokens)
btot = len(tokens)
rows = [(s, c, c / tot, base[s] / btot) for s, c in after.most_common(12)]
print(f"  {'sign':>6} {'count':>6} {'after%':>8} {'corpus%':>8} {'lift':>6}")
for s, c, f, b in rows:
    print(f"  {s:>6} {c:>6} {f:>7.1%} {b:>8.1%} {f/b:>6.2f}")
