"""First look at the parsed corpus: size, shape, Zipf, positional structure."""
import json
from collections import Counter
from pathlib import Path

D = Path("data/parsed")
texts = json.loads((D / "inscriptions.json").read_text())
sites = json.loads((D / "sites.json").read_text())

BR = 0  # glyph id 0 is the line-break marker, not a sign

lines = []           # every physical line of text, as a list of sign ids
for t in texts:
    cur = []
    for g in t["glyphs"]:
        if g == BR:
            if cur:
                lines.append((t, cur))
            cur = []
        else:
            cur.append(g)
    if cur:
        lines.append((t, cur))

signs = Counter(g for _, l in lines for g in l)
tokens = sum(signs.values())

print(f"artifacts            : {len(texts)}")
print(f"lines of text        : {len(lines)}")
print(f"sign tokens          : {tokens}")
print(f"distinct signs       : {len(signs)}")
print(f"mean line length     : {tokens / len(lines):.2f}")
print(f"median line length   : {sorted(len(l) for _, l in lines)[len(lines) // 2]}")
print(f"longest line         : {max(len(l) for _, l in lines)}")

print("\nline-length distribution")
ld = Counter(len(l) for _, l in lines)
for n in sorted(ld):
    bar = "#" * round(60 * ld[n] / max(ld.values()))
    print(f"  {n:>3} | {ld[n]:>4} {bar}")

print("\nhapax / frequency profile")
f = Counter(signs.values())
hapax = f[1]
print(f"  signs seen once    : {hapax}  ({hapax / len(signs):.0%} of inventory)")
print(f"  signs seen  <5     : {sum(v for k, v in f.items() if k < 5)}")
print(f"  top 20 signs cover : {sum(c for _, c in signs.most_common(20)) / tokens:.0%} of tokens")
print(f"  top 100 cover      : {sum(c for _, c in signs.most_common(100)) / tokens:.0%} of tokens")

print("\nmost frequent signs (id, count, %)")
for g, c in signs.most_common(15):
    print(f"  {g:>4}  {c:>5}  {c / tokens:5.1%}")

print("\npositional bias (top 10 initial vs final)")
init = Counter(l[0] for _, l in lines if l)
fin = Counter(l[-1] for _, l in lines if l)
print("  initial:", ", ".join(f"{g}({c})" for g, c in init.most_common(10)))
print("  final  :", ", ".join(f"{g}({c})" for g, c in fin.most_common(10)))

print("\nartifacts per site (top 12)")
bysite = Counter(t.get("site") for t in texts)
for s, c in bysite.most_common(12):
    print(f"  {str(sites.get(s, s)):<28} {c:>5}")

# Stored order is left-to-right on the artifact; the script reads right-to-left.
# lines.json is written in READING order.
json.dump([{"artifact": t["cisi"], "site": t.get("site"),
            "signs": l[::-1] if t.get("direction") != "L/R" else l}
           for t, l in lines],
          open(D / "lines.json", "w"), indent=1)
print(f"\nwrote {D / 'lines.json'}")
