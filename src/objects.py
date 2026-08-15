"""What kinds of physical objects is this script written on, and what's pictured on them?"""
import json
from collections import Counter, defaultdict
from pathlib import Path

import parse_yaj as P  # reuse the SQL row parser

text = Path("data/yaj/population-script.sql").read_text(encoding="utf-8", errors="replace")
seals = json.loads(Path("data/parsed/inscriptions.json").read_text())
sites = json.loads(Path("data/parsed/sites.json").read_text())

# --- object type -----------------------------------------------------------
# Codes are CISI-style. The repo's own qualityMap collapses them to coarse
# classes but has at least one clear error (TAB:C -> "Tag"; TAB = tablet), so
# we group by the prefix before the first colon instead.
feat = {r[0]: r[1] for r in P.rows("FEATURE", text)}
obj_type = {}
for sid, qid in ((r[0], r[1]) for r in P.rows("ICONOGRAPHYFEATURES", text)):
    obj_type[sid] = feat.get(qid, f"?{qid}")

CLASS = {"SEAL": "seal", "TAB": "tablet", "TAG": "sealing/tag", "POT": "pottery",
         "ROD": "rod", "BNGL": "bangle", "IMPL": "implement",
         "MISC": "misc", "Oth": "misc"}

# --- iconography -----------------------------------------------------------
# symbolMap from the repo's frontend, normalised to the depicted subject.
MOTIF = {
    "Bull1": "one-horned bull ('unicorn')", "Bull2": "two-horned bull",
    "Bull3": "three-horned bull", "Bult": "humped bull", "Bull": "bull",
    "Zebu": "zebu", "Buff": "water buffalo", "Gaur": "gaur",
    "Elep": "elephant", "Rhin": "rhinoceros", "Gavi": "rhinoceros",
    "Tigr": "tiger", "Htgr": "hunting tiger", "T-A-T": "tiger-attacking-tiger",
    "Goat": "goat", "Hare": "hare", "Ass": "ass", "Turt": "turtle",
    "Fish": "fish", "Tri4": "three-fish motif", "Bird": "bird",
    "Comp": "composite animal", "CompBull": "composite animal (bull)",
    "Anth": "anthropomorphic figure", "T-M-T": "three-headed deity",
    "Pipal": "pipal tree", "Phyt": "tree",
    "Crs": "cross", "Cros": "cross", "Xcrs": "crossed rods",
    "Xhch": "crosshatched square", "Maze": "maze pattern",
    "Box": "box", "Loop": "looped object", "Gavi+Bult": "rhinoceros and bull",
    "Scene": "unknown", "Mult": "unknown", "S590": "unknown",
    "Othr": "unknown", "Misc": "unknown", "None": "none", "nan": "unknown",
}


def motif(code):
    """'Bull1:W' and 'Goat:4' are sub-variants; strip to the depicted subject."""
    if code is None:
        return None
    return MOTIF.get(code.split(":")[0], MOTIF.get(code, code))


for s in seals:
    code = obj_type.get(s["seal_id"])
    s["obj_code"] = code
    s["obj_class"] = CLASS.get(code.split(":")[0], "misc") if code else None
    s["motif"] = motif(s.get("iconography"))

json.dump(seals, open("data/parsed/inscriptions.json", "w"), indent=1, ensure_ascii=False)


def table(title, counter, total=None, width=34):
    total = total or sum(counter.values())
    print(f"\n=== {title} (n={total}) ===")
    for k, c in counter.most_common():
        bar = "#" * round(40 * c / max(counter.values()))
        print(f"  {str(k):<{width}} {c:>5}  {c/total:5.1%} {bar}")


table("object class", Counter(s["obj_class"] for s in seals))
table("object code, full granularity", Counter(s["obj_code"] for s in seals))
table("material", Counter(s.get("material") or "unrecorded" for s in seals))
table("motif / field symbol", Counter(s["motif"] or "UNRECORDED" for s in seals))

print("\n=== object class x motif ===")
cx = defaultdict(Counter)
for s in seals:
    cx[s["obj_class"]][s["motif"] or "UNRECORDED"] += 1
for cls, cnt in sorted(cx.items(), key=lambda kv: -sum(kv[1].values())):
    tot = sum(cnt.values())
    top = ", ".join(f"{m} {c}" for m, c in cnt.most_common(5))
    print(f"  {str(cls):<14} n={tot:<5} {top}")

print("\n=== object class x site (top 2 sites) ===")
for cls in cx:
    cnt = Counter(sites.get(s.get("site"), "?") for s in seals if s["obj_class"] == cls)
    print(f"  {str(cls):<14} " + ", ".join(f"{k} {v}" for k, v in cnt.most_common(3)))

print("\n=== text length by object class ===")
for cls in sorted(cx, key=lambda c: -sum(cx[c].values())):
    ls = [len([g for g in s["glyphs"] if g != 0]) for s in seals if s["obj_class"] == cls]
    print(f"  {str(cls):<14} n={len(ls):<5} mean {sum(ls)/len(ls):.2f}  max {max(ls)}")
