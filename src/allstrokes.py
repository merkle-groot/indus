"""Treat every stroke sign as a number carrying a modifier.

05-radix.md excluded the bracketed and barred stroke signs (ids 41-51, 55) and
flagged it as the analysis's biggest open caveat: "if any of those encode higher
values, the cliff could move." This is that test.

Stroke counts were read off the glyphs rendered at 380px (`scratchpad/big.png`),
not guessed from the id:

  plain, one row      1..7        = 1..7
  two rows            12..19      = id - 10          (2..9)
  long strokes        31..36      = id - 30          (1..6)
  three rows          27 = 2+3+2  = 7
                      28 = 3+3+2  = 8   (slanted)
                      55 = 4+4+4  = 12
  round brackets      48 = 4+3    = 7
                      49 = 7 in a row = 7
                      50 = 8 long = 8
                      57 = 4+4+4  = 12  (reversed brackets)
  bar/roof above      51 = 5+4    = 9

Per the brief, the four bracket shapes -- ( ), ) (, ) ), ( ( -- are treated as
ONE modifier. Ids 34, 36, 41, 56 and 58 have no glyph in this font; 34 and 36
are read from their series (long strokes), the rest are left out.

The headline consequence is that **55 is twelve strokes and has 42 tokens**,
which would put a well-attested value above the base-8 boundary. So the whole
weight of the analysis falls on one question: does 55 behave like a numeral?

  S1 the new distribution
  S2 does 55 act like a numeral? (position, what it precedes, who it counts)
  S3 do bracketed forms behave like their plain counterparts?
"""
import json
from collections import Counter, defaultdict

from scipy import stats

# value, modifier
STROKE = {
    1: (1, "plain"), 2: (2, "plain"), 3: (3, "plain"), 4: (4, "plain"),
    5: (5, "plain"), 6: (6, "plain"), 7: (7, "plain"),
    13: (3, "tworow"), 14: (4, "tworow"), 15: (5, "tworow"), 16: (6, "tworow"),
    17: (7, "tworow"), 18: (8, "tworow"), 19: (9, "tworow"),
    31: (1, "long"), 32: (2, "long"), 33: (3, "long"), 34: (4, "long"),
    35: (5, "long"), 36: (6, "long"),
    27: (7, "threerow"), 28: (8, "threerow"), 55: (12, "threerow"),
    29: (6, "slant"),
    48: (7, "bracket"), 49: (7, "bracket"), 50: (8, "bracket"),
    57: (12, "bracket"),
    51: (9, "roof"),
}
OLD = set(range(1, 8)) | {31, 32, 33, 34, 35} | set(range(12, 20))
TRIO = {817, 820, 861}

lines = json.loads(open("data/parsed/lines.json").read())
ins = {}
for i in json.loads(open("data/parsed/inscriptions.json").read()):
    ins[i["cisi"] or f"#{i['seal_id']}"] = i
texts = [[g for g in l["signs"] if g] for l in lines]
freq = Counter(g for t in texts for g in t)

# ------------------------------------------------------------------ S1
print("=== S1: the value distribution, before and after ===")
old = Counter()
new = Counter()
for g, n in freq.items():
    if g in OLD:
        v = g if g < 8 else g - 30 if g > 30 else g - 10
        old[v] += n
    if g in STROKE:
        new[STROKE[g][0]] += n
print("  value   old   new   added by")
for v in sorted(set(old) | set(new)):
    who = ", ".join(f"{g}({freq[g]})" for g, (vv, m) in sorted(STROKE.items())
                    if vv == v and g not in OLD)
    print(f"  {v:>5} {old[v]:>5} {new[v]:>5}   {who}")
print(f"\n  tokens: {sum(old.values())} -> {sum(new.values())}")
print(f"  highest value with >=10 tokens: old "
      f"{max(v for v in old if old[v]>=10)}, new {max(v for v in new if new[v]>=10)}")

# ------------------------------------------------------------------ S2
print("\n=== S2: does 55 behave like a numeral? ===")
NUMS = [g for g in OLD if freq[g] >= 20]


def profile(gs, label):
    pos, foll, texts_with = [], Counter(), 0
    for t in texts:
        if not any(g in gs for g in t):
            continue
        texts_with += 1
        for i, g in enumerate(t):
            if g not in gs:
                continue
            if len(t) > 1:
                pos.append(i / (len(t) - 1))
            if i + 1 < len(t):
                foll[t[i + 1]] += 1
    print(f"  {label:<22} n_texts {texts_with:>4}  mean pos "
          f"{sum(pos)/max(len(pos),1):.3f}  followed-by top: "
          f"{', '.join(f'{g}({n})' for g,n in foll.most_common(5))}")
    return pos, foll


pn, fn = profile(set(NUMS), "known numerals")
p55, f55 = profile({55}, "sign 55")
p48, f48 = profile({48}, "sign 48")
print(f"\n  position, 55 vs numerals: Mann-Whitney p = "
      f"{stats.mannwhitneyu(p55, pn).pvalue:.3f}")
print(f"  position, 48 vs numerals: Mann-Whitney p = "
      f"{stats.mannwhitneyu(p48, pn).pvalue:.3f}")

# do they count the same things? cosine over the followed-by profile
def cos(a, b):
    k = set(a) | set(b)
    return (sum(a[x] * b[x] for x in k) /
            ((sum(v*v for v in a.values()) ** .5) *
             (sum(v*v for v in b.values()) ** .5) or 1))


print(f"\n  overlap of what they precede (cosine, 1.0 = identical targets)")
print(f"    55 vs numerals : {cos(f55, fn):.3f}")
print(f"    48 vs numerals : {cos(f48, fn):.3f}")
half1 = Counter()
half2 = Counter()
for i, g in enumerate(NUMS):
    (half1 if i % 2 == 0 else half2).update(profile.__defaults__ or {})
for t in texts:
    for i, g in enumerate(t):
        if g in NUMS and i + 1 < len(t):
            (half1 if NUMS.index(g) % 2 == 0 else half2)[t[i + 1]] += 1
print(f"    numerals vs themselves (split-half baseline): {cos(half1, half2):.3f}")

# is 55 ever preceded/followed by a numeral, as a numeral would not be?
adj = Counter()
for t in texts:
    for i, g in enumerate(t):
        if g != 55:
            continue
        if i and t[i-1] in OLD:
            adj["numeral before"] += 1
        if i + 1 < len(t) and t[i+1] in OLD:
            adj["numeral after"] += 1
n55 = freq[55]
base_b = sum(1 for t in texts for i, g in enumerate(t)
             if i and t[i-1] in OLD) / sum(len(t) for t in texts)
print(f"\n  55 preceded by a numeral: {adj['numeral before']}/{n55} "
      f"({adj['numeral before']/n55:.0%}) vs corpus base rate {base_b:.0%}")

# where does 55 live?
oc = Counter()
site = Counter()
for l in lines:
    if 55 in l["signs"]:
        site[l.get("site")] += 1
        oc[(ins.get(l.get("artifact")) or {}).get("obj_class")] += 1
print(f"  55 by site   : {site.most_common(4)}")
print(f"  55 by object : {oc.most_common(4)}")

# ------------------------------------------------------------------ S3
print("\n=== S3: do bracketed forms behave like their plain counterparts? ===")
BR = {g for g, (v, m) in STROKE.items() if m == "bracket"}
print(f"  bracketed signs: {sorted(BR)}  total tokens "
      f"{sum(freq[g] for g in BR)}")
for g in sorted(BR):
    v = STROKE[g][0]
    same = {h for h, (vv, m) in STROKE.items() if vv == v and m != "bracket"}
    fb = Counter()
    fp = Counter()
    for t in texts:
        for i, x in enumerate(t):
            if i + 1 < len(t):
                if x == g:
                    fb[t[i + 1]] += 1
                elif x in same:
                    fp[t[i + 1]] += 1
    print(f"    {g} (={v}, n={freq[g]}) vs plain {sorted(same)}: "
          f"target overlap {cos(fb, fp):.3f}   "
          f"top: {', '.join(str(k) for k,_ in fb.most_common(3))}")
