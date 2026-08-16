"""Page: every attested sign in id order, with merge and composite status.

Replaces the earlier hand-built allsigns.html, which rendered each sign from a
single codepoint and therefore showed "none" for the 44 signs whose glyphs.json
entry is a *sequence* of codepoints (20-composites.md).
"""
import base64
import json
import re
import sys
from collections import Counter

sys.path.insert(0, "src")
from gallery import FONT  # noqa: E402

b64 = base64.b64encode(FONT.read_bytes()).decode()
RAW = {g["glyph_id"]: str(g["unicode"])
       for g in json.load(open("data/parsed/glyphs.json"))}
lines = json.loads(open("data/parsed/lines.json").read())
freq = Counter(g for l in lines for g in l["signs"] if g)
am = json.load(open("data/parsed/allograph_map.json"))
MAP = {int(k): v for k, v in am["map"].items()}
merged = json.loads(open("data/parsed/lines_merged.json").read())
mfreq = Counter(g for l in merged for g in l["signs"] if g)


def cps(i):
    return [c.upper() for c in re.findall(r"&#x([0-9A-Fa-f]+);", RAW.get(i, ""))]


SINGLE = {}
for i in RAW:
    c = cps(i)
    if len(c) == 1:
        SINGLE.setdefault(c[0], i)

signs = sorted(freq)
composite = {i: [SINGLE.get(x) for x in cps(i)] for i in signs if len(cps(i)) > 1}
missing = [i for i in signs if not cps(i) or cps(i) == ["2047"]]
canon = [i for i in signs if i not in MAP]

# groups sharing an identical codepoint sequence
groups = {}
for i in signs:
    c = tuple(cps(i))
    if c and c != ("2047",):
        groups.setdefault(c, []).append(i)
ident = {i: sorted(v, key=lambda x: -freq[x])
         for c, v in groups.items() if len(v) > 1 for i in v}


def gl(i):
    c = cps(i)
    if not c or c == ["2047"]:
        return '<span class="none">none</span>'
    return '<span class="g">' + "".join(f"&#x{x};" for x in c) + "</span>"


def card(i):
    cls = ["card"]
    tags = []
    if i in MAP:
        cls.append("gone")
        tags.append(f'<span class="t merged">&rarr; {MAP[i]}</span>')
    elif i in ident:
        tags.append('<span class="t kept">canonical</span>')
    if i in composite:
        parts = " + ".join(str(p) if p else "?" for p in composite[i])
        tags.append(f'<span class="t comp">{parts}</span>')
    if i in missing:
        tags.append('<span class="t miss">unidentified</span>')
    n = freq[i]
    after = mfreq.get(i, 0)
    nn = (f'<span class="n">{n}</span>' if i in MAP or after == n
          else f'<span class="n">{n} &rarr; <b>{after}</b></span>')
    return (f'<div class="{" ".join(cls)}" id="s{i}">{gl(i)}'
            f'<span class="id">{i}</span>{nn}'
            f'<div class="tags">{"".join(tags)}</div></div>')


html = f"""<title>Indus Sign Index</title>
<style>
:root {{
  --ground:#e8ebe6; --panel:#f5f7f3; --sunk:#dfe4dc;
  --ink:#191f1b; --muted:#69726b; --line:#d2d8d0;
  --accent:#2e5c76; --merged:#2f6b52; --comp:#96682c; --miss:#a8443a;
  --serif:"Iowan Old Style","Palatino Linotype",Palatino,Georgia,serif;
  --sans:ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif;
  --mono:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
}}
@media (prefers-color-scheme: dark) {{
  :root:not([data-theme="light"]) {{
    --ground:#131813; --panel:#1b211c; --sunk:#10150f;
    --ink:#e5eae3; --muted:#8f988f; --line:#2a312b;
    --accent:#7fb2ce; --merged:#69b691; --comp:#d6a45e; --miss:#e0796d;
  }}
}}
:root[data-theme="dark"] {{
  --ground:#131813; --panel:#1b211c; --sunk:#10150f;
  --ink:#e5eae3; --muted:#8f988f; --line:#2a312b;
  --accent:#7fb2ce; --merged:#69b691; --comp:#d6a45e; --miss:#e0796d;
}}
@font-face {{ font-family:"Indus";
  src:url(data:font/ttf;base64,{b64}) format("truetype"); font-display:block; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; background:var(--ground); color:var(--ink);
  font:16px/1.6 var(--sans); -webkit-font-smoothing:antialiased; }}
.wrap {{ max-width:1240px; margin:0 auto; padding:0 24px 70px; }}
header {{ padding:64px 0 6px; }}
.eyebrow {{ font:600 11px/1 var(--sans); letter-spacing:.17em;
  text-transform:uppercase; color:var(--accent); margin-bottom:18px; }}
h1 {{ font:400 clamp(30px,4.6vw,42px)/1.08 var(--serif); margin:0 0 16px;
  letter-spacing:-.017em; }}
.lede {{ font:400 18px/1.55 var(--serif); color:var(--muted); max-width:64ch;
  margin:0; }}
.stats {{ display:grid; gap:1px; background:var(--line);
  grid-template-columns:repeat(auto-fit,minmax(140px,1fr));
  border:1px solid var(--line); border-radius:3px; overflow:hidden;
  margin:32px 0 24px; }}
.stat {{ background:var(--panel); padding:15px 17px; }}
.stat b {{ display:block; font:600 25px/1 var(--mono);
  font-variant-numeric:tabular-nums; }}
.stat span {{ display:block; font-size:12.5px; color:var(--muted);
  margin-top:5px; }}
.bar {{ display:flex; gap:8px; flex-wrap:wrap; align-items:center;
  padding:14px 0 22px; border-bottom:1px solid var(--line); margin-bottom:22px;
  position:sticky; top:0; background:var(--ground); z-index:2; }}
button {{ font:500 13px var(--sans); padding:7px 14px; cursor:pointer;
  border:1px solid var(--line); background:var(--panel); color:var(--ink);
  border-radius:2px; }}
button[aria-pressed="true"] {{ background:var(--ink); color:var(--ground);
  border-color:var(--ink); }}
button:focus-visible {{ outline:2px solid var(--accent); outline-offset:2px; }}
.grid {{ display:grid; gap:8px;
  grid-template-columns:repeat(auto-fill,minmax(112px,1fr)); }}
.card {{ background:var(--panel); border:1px solid var(--line);
  border-radius:3px; padding:12px 6px 8px; text-align:center;
  display:flex; flex-direction:column; align-items:center; gap:3px;
  min-height:132px; }}
.card.gone {{ opacity:.5; }}
.g {{ font-family:"Indus"; font-size:34px; line-height:1.15; min-height:42px; }}
.none {{ font:600 10px var(--mono); color:var(--miss); min-height:42px;
  display:flex; align-items:center; }}
.id {{ font:600 12px var(--mono); }}
.n {{ font:400 10.5px var(--mono); color:var(--muted); }}
.n b {{ color:var(--merged); }}
.tags {{ display:flex; flex-direction:column; gap:2px; margin-top:2px; }}
.t {{ font:600 8.5px var(--sans); letter-spacing:.07em; text-transform:uppercase;
  padding:2px 5px; border-radius:2px; border:1px solid currentColor; }}
.t.merged {{ color:var(--merged); }}
.t.kept {{ color:var(--accent); }}
.t.comp {{ color:var(--comp); text-transform:none; letter-spacing:0;
  font-family:var(--mono); font-size:9px; }}
.t.miss {{ color:var(--miss); }}
footer {{ margin-top:44px; padding-top:26px; border-top:1px solid var(--line);
  color:var(--muted); font-size:13.5px; }}
footer p {{ max-width:74ch; margin:0 0 9px; }}
</style>

<div class="wrap">
<header>
  <div class="eyebrow">Indus script &middot; sign index</div>
  <h1>Every attested sign, in id order</h1>
  <p class="lede">All {len(signs)} signs that occur at least once in the corpus.
  Ids are the source database&rsquo;s own numbering, not Mahadevan&rsquo;s or
  Parpola&rsquo;s. Faded cards are ids that have been merged into another;
  the arrow gives the surviving number.</p>
  <div class="stats">
    <div class="stat"><b>{len(signs)}</b><span>attested ids</span></div>
    <div class="stat"><b>{len(canon)}</b><span>after merging</span></div>
    <div class="stat"><b>{len(composite)}</b><span>written twice</span></div>
    <div class="stat"><b>{len(missing)}</b><span>unidentified in source</span></div>
    <div class="stat"><b>{sum(freq.values())}</b><span>tokens</span></div>
  </div>
</header>

<div class="bar">
  <button data-f="all" aria-pressed="true">All</button>
  <button data-f="canon" aria-pressed="false">Surviving only</button>
  <button data-f="gone" aria-pressed="false">Merged away</button>
  <button data-f="comp" aria-pressed="false">Composites</button>
  <button data-f="miss" aria-pressed="false">Unidentified</button>
</div>

<div class="grid" id="grid">{"".join(card(i) for i in signs)}</div>

<footer>
  <p><b>Composites.</b> {len(composite)} of these ids are not single glyphs. The
  database stores them as a sequence of codepoints, and each is another sign
  written two or three times &mdash; sign 56 is sign 55 twice, sign 617 is 615
  twice. The tag gives the parts.</p>
  <p><b>Merging.</b> 41 groups of ids share an identical codepoint sequence, so
  the font draws them as literally the same glyph; those are merged
  automatically. Three further merges were made by eye and are documented in
  <span class="t comp">src/apply_merges.py</span>.</p>
  <p><b>Unidentified.</b> {len(missing)} signs carry U+2047, the digitizer&rsquo;s
  own marker for a sign they could not identify. There is no image for these;
  the source never had one.</p>
</footer>
</div>
<script>
const g = document.getElementById('grid');
document.querySelectorAll('.bar button').forEach(b => b.onclick = () => {{
  document.querySelectorAll('.bar button').forEach(x =>
    x.setAttribute('aria-pressed', x === b));
  const f = b.dataset.f;
  g.querySelectorAll('.card').forEach(c => {{
    const gone = c.classList.contains('gone');
    const has = s => !!c.querySelector('.t.' + s);
    let show = true;
    if (f === 'canon') show = !gone;
    else if (f === 'gone') show = gone;
    else if (f === 'comp') show = has('comp');
    else if (f === 'miss') show = has('miss');
    c.style.display = show ? '' : 'none';
  }});
}});
</script>
"""

open("allsigns.html", "w").write(
    html.encode("ascii", "xmlcharrefreplace").decode())
print(f"wrote allsigns.html  {len(html)//1024} KB")
print(f"  attested {len(signs)}  surviving {len(canon)}  "
      f"composites {len(composite)}  unidentified {len(missing)}")
