"""Page: what got grouped, what was deliberately kept apart, what was left alone."""
import base64
import json
import re
import sys
from collections import Counter

sys.path.insert(0, "src")
from gallery import FONT  # noqa: E402

b64 = base64.b64encode(FONT.read_bytes()).decode()
CP = {g["glyph_id"]: int(re.sub(r"[^0-9A-Fa-f]", "", g["unicode"]), 16)
      for g in json.load(open("data/parsed/glyphs.json"))
      if str(g["unicode"]).startswith("&#x")}

sf = json.load(open("data/parsed/shape_families.json"))
am = json.load(open("data/parsed/allograph_map.json"))
A_SETS = am["sets"]
B_FAMS = am["kept_apart"]
EXCL = {e["id"]: e for e in sf["excluded"]}

lines = json.loads(open("data/parsed/lines.json").read())
freq = Counter(g for l in lines for g in l["signs"] if g)
attested = set(freq)
inA = {i for s in A_SETS for i in s}
inB = {i for s in B_FAMS for i in s}
alone = sorted(attested - inA - inB, key=lambda i: -freq[i])

only_a = len(inA - inB)
both = len(inA & inB)
only_b = len(inB - inA)
n_alone = len(alone)
TOT = len(attested)


def gl(i, cls="g"):
    if i not in CP:
        return f'<span class="nog" title="no glyph in the font">{i}</span>'
    return f'<span class="{cls}">&#x{CP[i]:X};</span>'


def cell(i, star=False):
    return (f'<div class="cell{" base" if star else ""}">{gl(i)}'
            f'<span class="id">{i}</span>'
            f'<span class="n">{freq[i]}</span></div>')


def sets_html(groups, star_first=False):
    out = []
    for s in sorted(groups, key=lambda s: -sum(freq[i] for i in s)):
        cells = "".join(cell(i, star_first and k == 0) for k, i in enumerate(s))
        out.append(f'<div class="set"><div class="cells">{cells}</div></div>')
    return "".join(out)


# frequency profile of the ungrouped
buckets = [("1 token", lambda n: n == 1), ("2-4", lambda n: 2 <= n <= 4),
           ("5-19", lambda n: 5 <= n <= 19), ("20+", lambda n: n >= 20)]
prof = [(lab, sum(1 for i in alone if f(freq[i]))) for lab, f in buckets]
big_alone = [i for i in alone if freq[i] >= 20][:24]

FISH = next((s for s in B_FAMS if 220 in s), None)

html = f"""<title>The Allograph Plate</title>
<style>
:root {{
  --ground:#e8ebe6; --panel:#f5f7f3; --sunk:#dfe4dc;
  --ink:#191f1b; --muted:#69726b; --line:#d2d8d0;
  --accent:#2e5c76; --merged:#2f6b52; --apart:#96682c; --alone:#8a8f88;
  --serif:"Iowan Old Style","Palatino Linotype",Palatino,Georgia,serif;
  --sans:ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif;
  --mono:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
}}
@media (prefers-color-scheme: dark) {{
  :root:not([data-theme="light"]) {{
    --ground:#131813; --panel:#1b211c; --sunk:#10150f;
    --ink:#e5eae3; --muted:#8f988f; --line:#2a312b;
    --accent:#7fb2ce; --merged:#69b691; --apart:#d6a45e; --alone:#767d76;
  }}
}}
:root[data-theme="dark"] {{
  --ground:#131813; --panel:#1b211c; --sunk:#10150f;
  --ink:#e5eae3; --muted:#8f988f; --line:#2a312b;
  --accent:#7fb2ce; --merged:#69b691; --apart:#d6a45e; --alone:#767d76;
}}
@font-face {{ font-family:"Indus";
  src:url(data:font/ttf;base64,{b64}) format("truetype"); font-display:block; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; background:var(--ground); color:var(--ink);
  font:16px/1.62 var(--sans); -webkit-font-smoothing:antialiased; }}
.wrap {{ max-width:1060px; margin:0 auto; padding:0 26px; }}

header {{ padding:70px 0 10px; }}
.eyebrow {{ font:600 11px/1 var(--sans); letter-spacing:.17em;
  text-transform:uppercase; color:var(--accent); margin-bottom:20px; }}
h1 {{ font:400 clamp(32px,5vw,46px)/1.07 var(--serif); margin:0 0 18px;
  letter-spacing:-.017em; text-wrap:balance; }}
.lede {{ font:400 19px/1.55 var(--serif); color:var(--muted);
  max-width:64ch; margin:0; }}

.bar {{ display:flex; height:16px; border-radius:3px; overflow:hidden;
  margin:38px 0 12px; border:1px solid var(--line); }}
.bar i {{ display:block; }}
.key {{ display:flex; gap:22px; flex-wrap:wrap; font-size:13px;
  color:var(--muted); }}
.key b {{ font:600 13px var(--mono); color:var(--ink); margin-right:5px; }}
.key s {{ display:inline-block; width:9px; height:9px; border-radius:2px;
  text-decoration:none; margin-right:7px; }}

section {{ padding:50px 0; border-top:1px solid var(--line); margin-top:50px; }}
h2 {{ font:400 27px/1.18 var(--serif); margin:0 0 8px; letter-spacing:-.01em; }}
h2 em {{ font-style:normal; font:600 12px var(--mono); color:var(--muted);
  margin-left:10px; vertical-align:3px; }}
.sub {{ color:var(--muted); max-width:72ch; margin:0 0 26px; font-size:15.5px; }}

.grid {{ display:grid; gap:10px;
  grid-template-columns:repeat(auto-fill,minmax(160px,1fr)); }}
.set {{ background:var(--panel); border:1px solid var(--line);
  border-radius:3px; padding:12px 10px; }}
.cells {{ display:flex; flex-wrap:wrap; gap:8px; justify-content:center; }}
.cell {{ display:flex; flex-direction:column; align-items:center; gap:2px;
  min-width:44px; }}
.g {{ font-family:"Indus"; font-size:34px; line-height:1.1; }}
.id {{ font:600 10px var(--mono); color:var(--muted); }}
.n {{ font:400 9.5px var(--mono); color:var(--muted); opacity:.75; }}
.cell.base .id {{ color:var(--apart); }}
.cell.base .g {{ text-shadow:0 0 0 currentColor; }}
.cell.base::after {{ content:"base"; font:600 8px var(--sans);
  letter-spacing:.09em; text-transform:uppercase; color:var(--apart); }}
.nog {{ font:600 10px var(--mono); color:var(--apart);
  border:1px dashed currentColor; border-radius:3px; padding:2px 4px; }}

#merged .set {{ border-left:2px solid var(--merged); }}
#apart .set {{ border-left:2px solid var(--apart); }}

.call {{ background:var(--sunk); border:1px solid var(--line);
  border-radius:3px; padding:22px 24px; margin:0 0 26px;
  display:flex; gap:24px; align-items:center; flex-wrap:wrap; }}
.call .cells {{ justify-content:flex-start; }}
.call p {{ margin:0; font-size:15px; max-width:52ch; flex:1; min-width:260px; }}
.call b {{ font-family:var(--mono); font-size:14px; }}

.prof {{ display:grid; gap:1px; background:var(--line);
  grid-template-columns:repeat(auto-fit,minmax(130px,1fr));
  border:1px solid var(--line); border-radius:3px; overflow:hidden;
  margin-bottom:26px; }}
.prof div {{ background:var(--panel); padding:15px 17px; }}
.prof b {{ display:block; font:600 25px/1 var(--mono);
  font-variant-numeric:tabular-nums; }}
.prof span {{ display:block; font-size:12.5px; color:var(--muted);
  margin-top:5px; }}

footer {{ padding:42px 0 70px; border-top:1px solid var(--line);
  margin-top:50px; color:var(--muted); font-size:13.5px; }}
footer p {{ max-width:72ch; margin:0 0 9px; }}
</style>

<div class="wrap">
<header>
  <div class="eyebrow">Indus script &middot; sign inventory</div>
  <h1>What counts as one sign, and what does not</h1>
  <p class="lede">The most disputed question in Indus epigraphy is how many
  signs there are. Every glyph in the corpus was rendered and compared pixel by
  pixel. Shapes that are the same drawing were merged. Shapes that are a base
  plus something added were deliberately left apart &mdash; because that
  something carries behaviour.</p>

  <div class="bar">
    <i style="background:var(--merged);width:{100*only_a/TOT:.2f}%"></i>
    <i style="background:var(--accent);width:{100*both/TOT:.2f}%"></i>
    <i style="background:var(--apart);width:{100*only_b/TOT:.2f}%"></i>
    <i style="background:var(--alone);width:{100*n_alone/TOT:.2f}%"></i>
  </div>
  <div class="key">
    <span><s style="background:var(--merged)"></s><b>{only_a}</b>merged</span>
    <span><s style="background:var(--accent)"></s><b>{both}</b>both</span>
    <span><s style="background:var(--apart)"></s><b>{only_b}</b>kept apart</span>
    <span><s style="background:var(--alone)"></s><b>{n_alone}</b>left alone</span>
  </div>
</header>

<section id="merged">
  <h2>Merged<em>{len(A_SETS)} sets &middot; {len(inA)} signs &rarr;
    {len(A_SETS)}</em></h2>
  <p class="sub">Same drawing, drawn twice. Within each set the glyphs are
  pixel-identical or near enough that no scribe was distinguishing them. The
  whole set now carries the number of its commonest member. Applying these took
  the inventory from <b>591 to 529</b> and the hapax count from 199 to 165
  &mdash; and moved not one headline result: the terminal slot stayed at
  z&nbsp;=&nbsp;&minus;14.2, the no-repeat rule at z&nbsp;=&nbsp;&minus;17.5,
  seals-versus-tablets at p&nbsp;&asymp;&nbsp;1e&minus;18.</p>
  <div class="grid">{sets_html(A_SETS)}</div>
</section>

<section id="apart">
  <h2>Kept apart<em>{len(B_FAMS)} families &middot; {len(inB)} signs</em></h2>
  <p class="sub">A base plus a stroke, a bar, a bracket. These look like
  candidates for merging and they are not, because the added mark predicts how
  the sign behaves. Merging them buys nothing statistically &mdash; the testable
  sign count actually falls back &mdash; and it erases a real finding.</p>

  <div class="call">
    <div class="cells">{"".join(cell(i, k == 0)
                                for k, i in enumerate(FISH or []))}</div>
    <p>The clearest case. A plain fish takes a coefficient above three sixteen
    times in ninety-three; a marked fish never does, in fifty-one chances
    &mdash; <b>p&nbsp;=&nbsp;6.5e&minus;04</b>. Declare them one character and
    the test collapses to <b>p&nbsp;=&nbsp;0.37</b>, not because the pattern
    went away but because the merge assumed it away.</p>
  </div>

  <div class="grid">{sets_html(B_FAMS, star_first=True)}</div>
</section>

<section id="alone">
  <h2>Left alone<em>{n_alone} signs</em></h2>
  <p class="sub">Most of the inventory resembles nothing else closely enough to
  group. This is not a failure of the method &mdash; it is the shape of the
  problem.</p>

  <div class="prof">
    {"".join(f'<div><b>{n}</b><span>seen {lab}</span></div>' for lab, n in prof)}
  </div>

  <p class="sub">Note the two ends. The <b>{prof[0][1]}</b> singletons cannot be
  grouped because there is nothing to compare them against, and they are the
  reason a third of the inventory stays untestable. But the commonest signs in
  the corpus are also ungrouped &mdash; they are distinctive enough that nothing
  else looks like them. The workhorses of the script are unambiguous; the
  ambiguity lives entirely in the tail.</p>

  <div class="grid"><div class="set" style="grid-column:1/-1">
    <div class="cells">{"".join(cell(i) for i in big_alone)}</div>
  </div></div>

  <p class="sub" style="margin-top:24px">A further <b>{len(EXCL)}</b> signs
  could not be compared at all &mdash; their codepoint has no glyph in this
  font, so there is nothing to render. Sign 56, with ten tokens and sitting in
  the numeral range, is the one that matters.</p>
  <div class="grid"><div class="set" style="grid-column:1/-1">
    <div class="cells">{"".join(
        f'<div class="cell"><span class="nog">{i}</span>'
        f'<span class="n">{e["tokens"]}</span></div>'
        for i, e in sorted(EXCL.items(), key=lambda kv: -kv[1]["tokens"]))}</div>
  </div></div>
</section>

<footer>
  <p><b>Method.</b> Every mapped glyph rendered at 256px, binarised, cropped to
  its ink, scaled to a 52px box and compared under a small search over scale and
  offset. Sets were cut where a two-component mixture separated the
  nearest-neighbour distances. Groups were then checked three ways: against
  Parpola's sign numbers, against fifteen groups picked independently by eye
  (<b>15 of 15 recovered</b>), and against corpus behaviour.</p>
  <p>Applied map in <span class="nog">data/parsed/allograph_map.json</span>;
  merged corpus in <span class="nog">lines_merged.json</span>. The original
  <span class="nog">lines.json</span> is untouched, so every figure in notes
  01&ndash;19 remains reproducible as written.</p>
</footer>
</div>
"""

open("plate.html", "w").write(
    html.encode("ascii", "xmlcharrefreplace").decode())
print("wrote plate.html", len(html) // 1024, "KB")
print(f"A sets {len(A_SETS)}  B families {len(B_FAMS)}  alone {n_alone}  "
      f"excluded {len(EXCL)}")
