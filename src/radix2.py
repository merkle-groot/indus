"""Is the cliff in the value distribution a radix boundary, or just decay?

Combined counts across all three stroke series:
  1:298  2:846  3:391  4:86  5:61  6:40  7:57  8:6  9:3   (nothing >=10)

Values 4-7 sit on a plateau (86, 61, 40, 57) and then collapse to 6 and 3.
If a base-B system writes 1..B-1 with strokes and switches representation at B,
we expect exactly that: a plateau then a cliff at B. The competing explanation
is that big numbers are simply rare, or that 8-9 strokes are hard to draw.

Test: fit the plateau on 4..7, extrapolate to 8 and 9, and ask how improbable
the observed counts are under Poisson. Then score every candidate radix.
"""
import json
from collections import Counter

import numpy as np
from scipy import stats

SER = {}
for i in range(1, 8):
    SER[i] = ("short", i)
for i in range(31, 36):
    SER[i] = ("long", i - 30)
for i in range(12, 20):
    SER[i] = ("tworow", i - 10)

lines = json.loads(open("data/parsed/lines.json").read())
tok = [g for l in lines for g in l["signs"]]
c = Counter(tok)
val = Counter()
for i, (s, v) in SER.items():
    val[v] += c.get(i, 0)
N = sum(val.values())

print("combined value counts:",
      "  ".join(f"{v}:{val[v]}" for v in sorted(val)))
print(f"total {N}\n")

# ---------------------------------------------------------------- the cliff
print("=== is the drop after 7 a cliff or ordinary decay? ===")
for lo, hi in [(4, 7), (5, 7), (3, 7)]:
    xs = np.arange(lo, hi + 1)
    ys = np.array([val[v] for v in xs], float)
    # log-linear (exponential) fit on the plateau
    b, a = np.polyfit(xs, np.log(np.maximum(ys, .5)), 1)
    for tgt in (8, 9):
        pred = np.exp(a + b * tgt)
        obs = val[tgt]
        p = stats.poisson.cdf(obs, pred)
        print(f"  fit on {lo}-{hi}: predict {tgt} = {pred:6.1f}, "
              f"observed {obs:>2}  Poisson P(<=obs) = {p:.2431g}"
              .replace(".2431g", ".3g"))
    print()

# ------------------------------------------------------------- radix scan
print("=== radix scan ===")
print("  For base B, strokes should cover 1..B-1 and stop.")
print("  'inside' = tokens with value < B, 'outside' = tokens with value >= B\n")
print(f"  {'B':>3} {'inside':>8} {'outside':>8} {'outside%':>9}  {'verdict'}")
for B in range(4, 13):
    inside = sum(n for v, n in val.items() if v < B)
    outside = sum(n for v, n in val.items() if v >= B)
    frac = outside / N
    if outside == 0:
        verdict = "no violations, but B unconstrained from above"
    elif frac < .01:
        verdict = "clean truncation"
    elif frac < .10:
        verdict = "leaky"
    else:
        verdict = "violated"
    print(f"  {B:>3} {inside:>8} {outside:>8} {frac:>8.2%}  {verdict}")

# ------------------------------------------ is the tworow split graphic?
print("\n=== is the single-row / two-row split about magnitude or graphics? ===")
for v in range(1, 10):
    sr = sum(c.get(i, 0) for i, (s, vv) in SER.items()
             if vv == v and s in ("short", "long"))
    tr = sum(c.get(i, 0) for i, (s, vv) in SER.items() if vv == v and s == "tworow")
    tot = sr + tr
    if tot:
        print(f"  value {v}:  single-row {sr:>4}  two-row {tr:>3}   "
              f"two-row share {tr/tot:5.1%}")
print("\n  If two-row were a distinct higher-order tier we would expect it to")
print("  carry its own value range. Instead it takes over exactly where a")
print("  single row of strokes stops being legible.")

# --------------------------------------- any candidate higher-order sign?
print("\n=== candidate 'higher unit' signs ===")
print("  A base-B system needs a symbol for B. It should behave like a numeral:")
print("  sit early, and substitute for numerals in minimal pairs.\n")
NUM = set(SER)
texts = [tuple(l["signs"]) for l in lines if l["signs"]]
pos, after_num = {}, Counter()
for t in texts:
    for j, g in enumerate(t):
        if len(t) > 1:
            pos.setdefault(g, []).append(j / (len(t) - 1))
        if j and t[j - 1] in NUM:
            after_num[g] += 1
numpos = np.mean([p for g in NUM for p in pos.get(g, [])])
base = np.mean([p for g in pos for p in pos[g]])
print(f"  numerals sit at {numpos:.3f}, corpus baseline {base:.3f}")
cand = [(g, np.mean(v), len(v)) for g, v in pos.items()
        if g not in NUM and len(v) >= 30]
cand.sort(key=lambda r: r[1])
print(f"  earliest-sitting non-numeral signs (n>=30):")
print(f"  {'sign':>6} {'meanpos':>8} {'n':>5}")
for g, m, n in cand[:10]:
    print(f"  {g:>6} {m:>8.3f} {n:>5}")
