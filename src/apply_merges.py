"""Apply the A allograph sets, leave the B derivational families split.

19-merge-impact.md settled where the line goes. Merging the A sets (same
drawing, drawn twice) cleans the inventory and costs nothing: every headline
result is unchanged to the second decimal. Merging the B families (a base plus
something added) buys nothing and erases the fish coefficient cap, because the
merge asserts precisely what that finding measures.

So: A in, B out.

`lines.json` is left untouched so every number in notes 01-19 stays reproducible
as written. This writes a parallel corpus and the map used to build it.
"""
import json
from collections import Counter

sf = json.load(open("data/parsed/shape_families.json"))
A_SETS = [s["members"] for s in sf["allograph_sets"]]
B_FAMS = [[f["base"]] + [m["id"] for m in f["members"]]
          for f in sf["derivational_families"]]

lines = json.loads(open("data/parsed/lines.json").read())
freq = Counter(g for l in lines for g in l["signs"] if g)

# One documented override. 154 + 156 fell to B because their Dice overlap is
# 0.776 rather than ~1.0 -- the bodies are identical and the top decoration
# differs. Everything else says one sign: their chamfer distance is 0.0041,
# *below* the 0.00433 cut for an A set; Parpola numbers both P004; and they pass
# the behavioural test (position p = .55, next-sign cosine 0.803 against a 0.604
# bar, object-class cosine 1.000). Merging them also sharpens the terminal slot
# from z = -4.73 / -4.33 separately to -6.40 together (18-allographs.md).
# Applying "A only" mechanically dropped a merge three sources agree on.
# 326 + 330 are the same glyph -- closed frame, two outer legs, two inner teeth,
# indistinguishable at 260px. The shape pipeline never paired them. 3 texts
# between them, so the merge is correct rather than consequential
# (21-frame-family.md).
#
# 318 + 323 is the weakest of the three and is flagged as such. The pixel test
# is AGAINST it: chamfer 0.0072, above the 0.00433 A-set cut, 226 px residual.
# The pipeline paired them as base+modifier. Applied anyway because the
# behaviour agrees -- both are followed by sign 920 (2/2 and 2/4), next-sign
# cosine 0.816, and they never share a text -- but on 2 and 4 tokens that is
# thin. Revisit if the corpus ever grows (21-frame-family.md).
OVERRIDE = [[156, 154], [326, 330], [318, 323]]

# Union-find, so overlapping sets and the override compose instead of the later
# one silently winning. A single-pass dict leaves any sign whose target was
# itself remapped stranded one hop short.
parent = {}


def find(x):
    parent.setdefault(x, x)
    while parent[x] != x:
        parent[x] = parent[parent[x]]
        x = parent[x]
    return x


for s in A_SETS + OVERRIDE:
    r = find(s[0])
    for i in s[1:]:
        parent[find(i)] = r

groups = {}
for i in parent:
    groups.setdefault(find(i), set()).add(i)

# canonical id = the most frequent member, so the common sign keeps its number
MAP = {}
for members in groups.values():
    keep = max(members, key=lambda i: freq[i])
    for i in members:
        if i != keep:
            MAP[i] = keep

merged = [{**l, "signs": [MAP.get(g, g) for g in l["signs"]]} for l in lines]
json.dump(merged, open("data/parsed/lines_merged.json", "w"), indent=1)

after = Counter(g for l in merged for g in l["signs"] if g)
inA = {i for s in A_SETS for i in s}
inB = {i for s in B_FAMS for i in s}
attested = set(freq)

json.dump({
    "applied": "allograph_sets (A) plus one documented override",
    "override": OVERRIDE,
    "not_applied": "derivational_families (B)",
    "map": {str(k): v for k, v in sorted(MAP.items())},
    "sets": [sorted(m, key=lambda i: -freq[i]) for m in groups.values()],
    "kept_apart": [sorted(s, key=lambda i: -freq[i]) for s in B_FAMS
                    if set(s) not in [set(o) for o in OVERRIDE]],
}, open("data/parsed/allograph_map.json", "w"), indent=1)

print(f"attested signs      {len(attested)}")
print(f"  in an A set       {len(inA & attested)}  across {len(A_SETS)} sets")
print(f"  in a B family     {len(inB & attested)}  across {len(B_FAMS)} families")
print(f"  in both           {len(inA & inB & attested)}")
print(f"  in neither        {len(attested - inA - inB)}")
print(f"  no glyph in font  {len(sf['excluded'])}")
print()
print(f"ids rewritten       {len(MAP)}")
print(f"inventory           {len(attested)} -> {len(after)}")
print(f"hapax               {sum(1 for v in freq.values() if v == 1)} -> "
      f"{sum(1 for v in after.values() if v == 1)}")
print(f"signs with n>=20    {sum(1 for v in freq.values() if v >= 20)} -> "
      f"{sum(1 for v in after.values() if v >= 20)}")
print("\nwrote data/parsed/lines_merged.json, data/parsed/allograph_map.json")
