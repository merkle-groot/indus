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

# canonical id = the most frequent member, so the common sign keeps its number
MAP = {}
for s in A_SETS:
    keep = max(s, key=lambda i: freq[i])
    for i in s:
        if i != keep:
            MAP[i] = keep

merged = [{**l, "signs": [MAP.get(g, g) for g in l["signs"]]} for l in lines]
json.dump(merged, open("data/parsed/lines_merged.json", "w"), indent=1)

after = Counter(g for l in merged for g in l["signs"] if g)
inA = {i for s in A_SETS for i in s}
inB = {i for s in B_FAMS for i in s}
attested = set(freq)

json.dump({
    "applied": "allograph_sets (A) only",
    "not_applied": "derivational_families (B)",
    "map": {str(k): v for k, v in sorted(MAP.items())},
    "sets": [sorted(s, key=lambda i: -freq[i]) for s in A_SETS],
    "kept_apart": [sorted(s, key=lambda i: -freq[i]) for s in B_FAMS],
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
