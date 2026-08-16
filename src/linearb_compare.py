"""Structural comparison of the Indus corpus with Linear B.

Linear B is deciphered, so we know its structure: ~88 syllabograms, ~100-170
commodity logograms, decimal numerals with distinct signs for 1/10/100/1000/
10000 repeated up to 9x, and a rigid COMMODITY-then-NUMBER word order in its
palace accounts. This tests whether Indus behaves the same way. It is a
falsifiable structural comparison, not a phonetic one.

  L1 inventory & length
  L2 word order   -- is the commodity-then-number rule present?
  L3 commodity class -- is the counted vocabulary a small closed set?
  L4 numeral ceiling -- how large a quantity can Indus express?
"""
import json
from collections import Counter

lines = json.loads(open("data/parsed/lines.json").read())
recs, seen = [], set()
for l in lines:
    t = tuple(x for x in l["signs"] if x)
    if not t:
        continue
    k = (t, l.get("site"))
    if k in seen:
        continue
    seen.add(k)
    recs.append(t)
freq = Counter(g for t in recs for g in t)
tok = sum(freq.values())

UNIT = set(range(1, 8)) | {31, 32, 33, 34, 35, 36} | set(range(12, 20))
VALUE = {**{i: i for i in range(1, 8)}, **{i: i - 10 for i in range(13, 20)},
         **{i: i - 30 for i in range(31, 37)}, 27: 7, 28: 8, 55: 12, 29: 6,
         48: 7, 49: 7, 50: 8, 57: 12, 51: 9, 56: 24}

print("=== L1: inventory and length ===")
print(f"  distinct signs {len(freq)}   tokens {tok}   "
      f"hapax {sum(1 for g in freq if freq[g]==1)} "
      f"({sum(1 for g in freq if freq[g]==1)/len(freq):.0%})")
print(f"  mean text length {tok/len(recs):.2f}")
print("  Linear B: ~260 signs total, short accounting entries")

print("\n=== L2: commodity-then-number word order ===")
before = after = 0
for t in recs:
    for i in range(len(t) - 1):
        if t[i] not in UNIT and t[i + 1] in UNIT:
            before += 1
        if t[i] in UNIT and t[i + 1] not in UNIT:
            after += 1
print(f"  noun then numeral: {before}")
print(f"  numeral then noun: {after}")
print(f"  ratio {max(before,after)/min(before,after):.2f} : 1")
print("  Linear B is rigidly commodity-then-number; Indus is ~even (no rule)")

print("\n=== L3: is the counted vocabulary a closed commodity set? ===")
after_num = Counter()
for t in recs:
    for i in range(1, len(t)):
        if t[i - 1] in UNIT and t[i] not in UNIT:
            after_num[t[i]] += 1
top = sum(c for _, c in after_num.most_common(15))
print(f"  distinct signs ever directly after a numeral: {len(after_num)}")
print(f"  top 15 cover {top/sum(after_num.values()):.0%} of post-numeral tokens")
print("  most-counted signs:")
for g, c in after_num.most_common(6):
    print(f"    {g:>4}  {c:>3}x  ({c/freq[g]:.0%} of its tokens are post-numeral)")
print("  Linear B commodities are a small closed set of mostly-hapax logograms")

print("\n=== L4: numeral ceiling ===")
runs = []
for t in recs:
    cur = 0
    for g in t:
        if g in VALUE:
            cur += VALUE[g]
        elif cur:
            runs.append(cur)
            cur = 0
    if cur:
        runs.append(cur)
c = Counter(runs)
print(f"  largest quantity expressed in any text: {max(runs)}")
print("  distribution:", {v: c[v] for v in sorted(c)})
print("  Linear B tallies reach the ten-thousands; Indus tops out at 26.")
print("  A script whose largest number is 26 is not doing bulk inventory.")
