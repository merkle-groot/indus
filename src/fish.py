"""Is the fish family a modifier system, and is the modifier numeric?

Rendered forms (ids 215-260):
  220 plain fish            284
  240 fish + X cross        256
  235 fish + roof/chevron   186
  233 fish + top cross      140
  231 fish + internal line   60
  226 fish + flanking marks  26
  236 roof-fish + flanking   21
  222 (fish) + raised hook   16
  241 X-fish  + flanking     10
  243 fish in a frame        10
  232 line-fish + flanking    8
  234 fish + flanking         6

So it decomposes two ways: a body modifier (X / roof / cross / line / none)
and an optional pair of flanking strokes. The question is whether either
dimension is numeric -- i.e. graded and countable -- or merely categorical.

Tests:
  1. paradigm  -- do fish variants substitute for one another in minimal pairs
                  the way numerals do?
  2. quantified -- is a fish variant preceded by a numeral, and does the
                  variant choice depend on the numeral's value? If the
                  modifier encoded a quantity, an explicit numeral in front
                  would be redundant and should be suppressed.
  3. flanking  -- do flanked and unflanked forms of the same body appear in
                  the same contexts (allographs) or different ones (distinct
                  signs)?
"""
import json
from collections import Counter, defaultdict
from itertools import combinations

from scipy import stats

FISH = {220: "plain", 240: "X", 235: "roof", 233: "topcross", 231: "line",
        226: "plain+flank", 236: "roof+flank", 222: "(plain)+hook",
        241: "X+flank", 243: "framed", 232: "line+flank", 234: "plain+flank2"}
BODY = {220: "plain", 226: "plain", 234: "plain", 222: "plain",
        240: "X", 241: "X", 235: "roof", 236: "roof",
        233: "topcross", 231: "line", 232: "line", 243: "plain"}
FLANK = {226, 232, 234, 236, 241}

NUMS = {}
for i in range(1, 8):
    NUMS[i] = i
for i in range(31, 36):
    NUMS[i] = i - 30
for i in range(12, 20):
    NUMS[i] = i - 10

lines = json.loads(open("data/parsed/lines.json").read())
texts = [tuple(l["signs"]) for l in lines if l["signs"]]
tok = [g for t in texts for g in t]
N = len(tok)
cnt = Counter(tok)
pfish = sum(g in FISH for g in tok) / N
print(f"fish-family tokens: {sum(g in FISH for g in tok)} ({pfish:.1%} of corpus)")

# ---------------------------------------------------------------- 1. paradigm
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

both = sum(a[i] in FISH and b[i] in FISH for a, b, i in pairs)
one = sum((a[i] in FISH) ^ (b[i] in FISH) for a, b, i in pairs)
pv = (sum(a[i] in FISH for a, b, i in pairs)
      + sum(b[i] in FISH for a, b, i in pairs)) / (2 * len(pairs))
print(f"\n=== 1. substitution paradigm ({len(pairs)} minimal pairs) ===")
print(f"  P(a variant is fish-family)         = {pv:.3f}")
print(f"  pairs with >=1 fish variant         = {both + one}")
print(f"  P(both fish | at least one)         = {both/(both+one):.3f}")
print(f"  expected if independent             = {pv:.3f}")
print(f"  enrichment                          = {both/(both+one)/pv:.2f}x")
r = stats.binomtest(both, both + one, pv, alternative="greater")
print(f"  binomial p                          = {r.pvalue:.3g}")
print("\n  fish-for-fish substitutions observed:")
sub = Counter()
for a, b, i in pairs:
    if a[i] in FISH and b[i] in FISH:
        sub[tuple(sorted((FISH[a[i]], FISH[b[i]])))] += 1
for k, c in sub.most_common(12):
    print(f"    {k[0]:<14} <-> {k[1]:<14} {c}")

# ------------------------------------------------------------- 2. quantified?
print("\n=== 2. are fish variants quantified by a preceding numeral? ===")
print(f"  {'sign':>5} {'form':<15} {'n':>5} {'prevIsNum':>10} {'rate':>7}")
base_prev = sum(1 for t in texts for j in range(1, len(t)) if t[j - 1] in NUMS) / \
    max(sum(len(t) - 1 for t in texts), 1)
for g in sorted(FISH, key=lambda g: -cnt.get(g, 0)):
    tot = prev = 0
    for t in texts:
        for j, s in enumerate(t):
            if s == g and j > 0:
                tot += 1
                prev += t[j - 1] in NUMS
    if tot >= 5:
        print(f"  {g:>5} {FISH[g]:<15} {tot:>5} {prev:>10} {prev/tot:>6.1%}")
print(f"  corpus baseline P(previous token is a numeral) = {base_prev:.1%}")

print("\n  value of the numeral immediately preceding a fish variant:")
vals = Counter()
for t in texts:
    for j, s in enumerate(t):
        if s in FISH and j > 0 and t[j - 1] in NUMS:
            vals[NUMS[t[j - 1]]] += 1
print("   ", dict(sorted(vals.items())))
allv = Counter(NUMS[g] for g in tok if g in NUMS)
print("    all numerals:", dict(sorted(allv.items())))

# ------------------------------------------------------------- 3. flanking
print("\n=== 3. is flanking an allograph or a distinct sign? ===")
print("  If flanked/unflanked were the same sign written two ways, they should")
print("  share contexts. Comparing the multiset of neighbouring signs:\n")
ctx = defaultdict(Counter)
for t in texts:
    for j, s in enumerate(t):
        if s in FISH:
            if j:
                ctx[s][("L", t[j - 1])] += 1
            if j + 1 < len(t):
                ctx[s][("R", t[j + 1])] += 1


def cosine(a, b):
    keys = set(a) | set(b)
    num = sum(a[k] * b[k] for k in keys)
    da = sum(v * v for v in a.values()) ** .5
    db = sum(v * v for v in b.values()) ** .5
    return num / (da * db) if da and db else 0.0


for base, pair in [("plain", (220, 226)), ("roof", (235, 236)),
                   ("X", (240, 241)), ("line", (231, 232))]:
    u, f = pair
    if cnt.get(u, 0) and cnt.get(f, 0):
        print(f"  {base:<9} {u} (n={cnt[u]:>3}) vs {f} (n={cnt[f]:>3})  "
              f"context cosine = {cosine(ctx[u], ctx[f]):.3f}")
print("\n  for reference, cosine between two unrelated frequent fish forms:")
print(f"    220 vs 240  = {cosine(ctx[220], ctx[240]):.3f}")
print(f"    220 vs 235  = {cosine(ctx[220], ctx[235]):.3f}")
print(f"    235 vs 240  = {cosine(ctx[235], ctx[240]):.3f}")
