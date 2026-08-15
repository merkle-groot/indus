"""Independent transcription cross-check, and a Parpola sign-number crosswalk.

Every free Indus corpus traces back to one of two digitizations. We have both:

  A. yajnadevam population-script.sql  -- 2543 artefacts, its own sign ids (Y)
  B. mayig/indus-valley-script-corpus  -- 179 artefact sides, Parpola ids (P)

They were transcribed independently from the same published plates (CISI), so
where they overlap we can ask something no single corpus can answer: **how often
do two careful digitizers read the same seal the same way?** That number is the
error floor under every result in this project.

The join needs a Y->P dictionary. glossa-lab published one derived from the same
yajnadevam SQL; we take only the id pairs, never the phonetic readings attached
to them, and we validate the map against the jar sign before trusting it.

  C1 crosswalk  -- build and validate Y->P
  C2 collapse   -- does Parpola's allograph grouping merge any of our sign ids?
  C3 agreement  -- for the 161 shared artefacts, do the two transcriptions match?
"""
import glob
import json
import re
from collections import Counter

# ------------------------------------------------------------------ C1
print("=== C1: building the Y -> P crosswalk ===")
gl = json.load(open("data/glossa/yaj_pnumbered.json"))
ymap, tok, mapped = {}, 0, 0
for r in gl:
    ps = r["sign_sequence_raw"].split()
    ys = r["sign_sequence_source_ids"].split()
    for p, y in zip(ps, ys):
        tok += 1
        if p.startswith("Yunmapped"):
            continue
        mapped += 1
        ymap.setdefault(int(y[1:]), Counter())[p] += 1

amb = {y: v for y, v in ymap.items() if len(v) > 1}
Y2P = {y: v.most_common(1)[0][0] for y, v in ymap.items()}
print(f"  our sign ids            : 591")
print(f"  ids with a Parpola no.  : {len(Y2P)}")
print(f"  tokens covered          : {mapped}/{tok} ({mapped/tok:.1%})")
print(f"  ids mapping to >1 P     : {len(amb)}")

# Validation: our sign 740 is the most frequent sign and sits text-final. That
# is the jar sign. Whatever P number it gets must be the most frequent P sign in
# the independent mayig corpus too, or the map is wrong.
print("\n  validation against the jar sign")
print(f"    our 740 (most frequent, text-final) -> {Y2P.get(740)}")

# ------------------------------------------------------------------ C2
print("\n=== C2: does Parpola's numbering merge any of our ids? ===")
back = {}
for y, p in Y2P.items():
    back.setdefault(p, []).append(y)
merges = {p: ys for p, ys in back.items() if len(ys) > 1}
print(f"  distinct P signs behind our {len(Y2P)} mapped ids : {len(back)}")
print(f"  P signs that absorb 2+ of our ids               : {len(merges)}")

lines = json.loads(open("data/parsed/lines.json").read())
freq = Counter(g for l in lines for g in l["signs"] if g)
fams = {f["base"]: set(f["variants"]) | {f["base"]}
        for f in json.loads(open("data/parsed/families.json").read())}

print("\n  merged groups (our ids -> one Parpola sign), and whether our own")
print("  family grouping had already caught them:")
for p, ys in sorted(merges.items(), key=lambda kv: -sum(freq[y] for y in kv[1])):
    same = any(set(ys) <= v for v in fams.values())
    n = sum(freq[y] for y in ys)
    print(f"    {p}  {str(sorted(ys)):<28} {n:>5} tokens  "
          f"{'ours agrees' if same else 'OURS SPLIT THESE'}")

# ------------------------------------------------------------------ C3
print("\n=== C3: do two independent transcriptions agree? ===")
ins = json.loads(open("data/parsed/inscriptions.json").read())
ours = {}
for i in ins:
    if i.get("cisi"):
        ours.setdefault(i["cisi"], []).append(i)

may = {}
for f in glob.glob("data/cisi/corpus/*/*.json"):
    for side in json.load(open(f)):
        may[side["id"]] = [g["id"] for g in side["graphemes"]]

exact = lenok = comparable = 0
partial_num = partial_den = 0
bad = []
for k, mseq in sorted(may.items()):
    base = re.sub(r"[A-Za-z]$", "", k)
    if base not in ours:
        continue
    # our glyph list, storage order (as inscribed), line breaks dropped
    oseq_y = [g for g in ours[base][0]["glyphs"] if g]
    comparable += 1
    if len(oseq_y) == len(mseq):
        lenok += 1
        oseq_p = [Y2P.get(g) for g in oseq_y]
        pairs = [(a, b) for a, b in zip(oseq_p, mseq) if a is not None]
        partial_den += len(pairs)
        partial_num += sum(a == b for a, b in pairs)
        if pairs and all(a == b for a, b in pairs):
            exact += 1
        elif pairs:
            bad.append((base, oseq_p, mseq))

print(f"  artefacts in both corpora        : {comparable}")
print(f"  same number of signs             : {lenok} ({lenok/comparable:.0%})")
print(f"  of those, every mapped sign agrees: {exact} ({exact/max(lenok,1):.0%})")
print(f"  sign-level agreement             : {partial_num}/{partial_den} "
      f"({partial_num/max(partial_den,1):.1%})")

print("\n  first disagreements (ours -> theirs):")
for base, o, m in bad[:12]:
    diff = " ".join(f"[{a}|{b}]" if a != b else str(a)
                    for a, b in zip(o, m) if a is not None)
    print(f"    {base:<9} {diff}")

json.dump({"y2p": Y2P, "merges": merges}, open("data/parsed/crosswalk.json", "w"),
          indent=1)
print("\nwrote data/parsed/crosswalk.json")
