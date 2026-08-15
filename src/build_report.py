"""Build the modifier catalogue as a self-contained HTML page."""
import base64
import json
import re
import statistics
import sys
from collections import Counter

sys.path.insert(0, "src")
from gallery import FONT, font_codepoints

have = font_codepoints(FONT)
cp = {g["glyph_id"]: int(re.sub(r"[^0-9A-Fa-f]", "", g["unicode"]), 16)
      for g in json.load(open("data/parsed/glyphs.json"))
      if str(g["unicode"]).startswith("&#x")}
b64 = base64.b64encode(FONT.read_bytes()).decode()

lines = json.load(open("data/parsed/lines.json"))
freq = Counter(g for l in lines for g in l["signs"])
fams = json.load(open("data/parsed/modifiers.json"))


def gl(g, cls=""):
    """Always keep the .gl class -- it carries font-family:Indus."""
    c = f"gl {cls}".strip()
    if cp.get(g) in have:
        return f'<span class="{c}">&#x{cp[g]:X};</span>'
    return f'<span class="{c} miss">{g}</span>'


def chip(g):
    return (f'<span class="chip">{gl(g)}'
            f'<span class="cid">{g}</span><span class="cn">{freq.get(g,0)}</span></span>')


# ---------------------------------------------------------------- summary
n_signs = len(freq)
n_fam = len(fams)
n_var = sum(len(f["variants"]) for f in fams)
var_counts = [v["n"] for f in fams for v in f["variants"]]
med_var = statistics.median(var_counts)
rare = sum(1 for c in var_counts if c <= 5)
testable = [f for f in fams if f["p"] is not None]
sig = [f for f in testable if f["p"] < .05]

# ------------------------------------------------- modifier type exemplars
TYPES = [
    ("Overlay", "A cross or bar struck through the body of the sign.",
     220, [240, 241], [690, 647, 811], "Sign 692 (a plain cross) takes the same "
     "treatment at 690; 811 is a circle with a cross set through it."),
    ("Infix", "A stroke, dot or lens placed inside the sign.",
     220, [231, 232], [808, 812, 813, 814], "All four are the plain circle or "
     "oval, sign 790, with something enclosed."),
    ("Flanking", "Short strokes standing to the left and right, not touching.",
     220, [226, 234], [910, 912, 592, 689], "The most widely borrowed modifier "
     "after the fish, appearing on crescents, boxes and crosses alike."),
    ("Enclosure", "The sign bracketed or framed by an outer form.",
     220, [222, 243], [267, 269, 940], "Sign 266 bracketed becomes 267; sign "
     "268 becomes 269. The clearest base-to-variant pairs outside the fish."),
    ("Superscript", "A chevron or roof set above the sign.",
     220, [235, 236], [729, 731], "Almost exclusive to the fish. Only two other "
     "signs take it, once each — modifiers are not equally productive."),
]


def dist_bar(d, hi_from=4):
    if not d:
        return '<div class="nodata">no data</div>'
    tot = sum(d.values())
    out = []
    for v in range(1, 10):
        c = d.get(str(v), d.get(v, 0))
        if not c:
            continue
        w = 100 * c / tot
        out.append(f'<span class="seg {"hi" if v >= hi_from else "lo"}" '
                   f'style="width:{w:.2f}%" title="value {v}: {c}">'
                   f'<i>{v}</i></span>')
    return f'<div class="bar">{"".join(out)}</div>'


rows = []
order = sorted(fams, key=lambda f: (f["p"] is None, f["p"] if f["p"] is not None else 0,
                                    -f["n_base"]))
for f in order:
    b = f["base"]
    verdict, vcls = "", "none"
    if f["p"] is not None:
        rb = f["hi_base"] / f["obs_base"]
        rv = f["hi_var"] / f["obs_var"]
        if f["p"] < .05:
            verdict = ("base takes larger numbers" if rb > rv
                       else "variants take larger numbers")
            vcls = "up" if rb > rv else "down"
        else:
            verdict = "no difference"
            vcls = "flat"
    stat = ""
    if f["p"] is not None:
        stat = f"""
      <div class="test">
        <div class="trow"><span class="tl">base</span>{dist_bar(f['vb'])}
          <span class="tn">{f['hi_base']}/{f['obs_base']} &ge;4</span></div>
        <div class="trow"><span class="tl">variants</span>{dist_bar(f['vv'])}
          <span class="tn">{f['hi_var']}/{f['obs_var']} &ge;4</span></div>
        <div class="verdict {vcls}">{verdict}<span class="pv">p = {f['p']:.2g}</span></div>
      </div>"""
    else:
        stat = ('<div class="test"><div class="nodata">too few numeral-preceded '
                'occurrences to test</div></div>')
    rows.append(f"""
  <article class="fam" data-testable="{1 if f['p'] is not None else 0}"
           data-sig="{1 if (f['p'] is not None and f['p'] < .05) else 0}">
    <div class="base">{gl(b, 'glbig')}
      <div class="bid">{b}</div><div class="bn">{f['n_base']} tokens</div></div>
    <div class="vars">
      <div class="vlab">{len(f['variants'])} variants &middot; {f['n_var']} tokens</div>
      <div class="chips">{''.join(chip(v['id']) for v in f['variants'])}</div>
    </div>
    {stat}
  </article>""")

type_cards = []
for name, desc, exb, exv, others, note in TYPES:
    type_cards.append(f"""
    <div class="tcard">
      <h3>{name}</h3>
      <p>{desc}</p>
      <div class="tex">
        <span class="tbase">{gl(exb, 'glmid')}<i>{exb}</i></span>
        <span class="arrow">&rarr;</span>
        {''.join(f'<span class="tvar">{gl(v, "glmid")}<i>{v}</i></span>' for v in exv)}
      </div>
      <div class="tother"><span class="olab">same modifier, other bases</span>
        {''.join(f'<span class="tvar sm">{gl(v)}<i>{v}</i><u>{freq.get(v,0)}</u></span>' for v in others)}</div>
      <p class="tnote">{note}</p>
    </div>""")

html = f"""<title>Indus Sign Modifiers</title>
<style>
:root {{
  --ground:#e8ebe6; --panel:#f5f7f3; --sunk:#dfe4dc;
  --ink:#191f1b; --muted:#69726b; --line:#d2d8d0;
  --accent:#2e5c76; --flag:#96682c; --down:#6b4a7a;
  --serif: "Iowan Old Style","Palatino Linotype",Palatino,Georgia,serif;
  --sans: ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif;
  --mono: ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
}}
@media (prefers-color-scheme: dark) {{
  :root:not([data-theme="light"]) {{
    --ground:#131813; --panel:#1b211c; --sunk:#10150f;
    --ink:#e5eae3; --muted:#8f988f; --line:#2a312b;
    --accent:#7fb2ce; --flag:#d6a45e; --down:#b795c6;
  }}
}}
:root[data-theme="dark"] {{
  --ground:#131813; --panel:#1b211c; --sunk:#10150f;
  --ink:#e5eae3; --muted:#8f988f; --line:#2a312b;
  --accent:#7fb2ce; --flag:#d6a45e; --down:#b795c6;
}}
@font-face {{ font-family:"Indus";
  src:url(data:font/ttf;base64,{b64}) format("truetype"); font-display:block; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; background:var(--ground); color:var(--ink);
  font:16px/1.6 var(--sans); }}
.wrap {{ max-width:1120px; margin:0 auto; padding:0 28px; }}
.gl {{ font-family:"Indus"; }}
.miss {{ font-family:var(--mono); font-size:.62em; color:var(--flag);
  border:1px dashed currentColor; border-radius:3px; padding:0 3px; }}

header {{ padding:64px 0 34px; }}
.eyebrow {{ font:600 11px/1 var(--sans); letter-spacing:.16em;
  text-transform:uppercase; color:var(--accent); margin-bottom:18px; }}
h1 {{ font:400 46px/1.08 var(--serif); margin:0 0 16px;
  letter-spacing:-.015em; text-wrap:balance; }}
.lede {{ font:400 19px/1.55 var(--serif); color:var(--muted);
  max-width:60ch; margin:0; }}

.stats {{ display:grid; gap:1px; background:var(--line);
  grid-template-columns:repeat(auto-fit,minmax(158px,1fr));
  border:1px solid var(--line); border-radius:3px; overflow:hidden;
  margin:38px 0 8px; }}
.stat {{ background:var(--panel); padding:18px 20px; }}
.stat b {{ display:block; font:600 30px/1 var(--mono);
  font-variant-numeric:tabular-nums; letter-spacing:-.02em; }}
.stat span {{ display:block; font-size:12.5px; color:var(--muted); margin-top:7px; }}

h2 {{ font:400 27px/1.2 var(--serif); margin:0 0 10px; letter-spacing:-.01em; }}
section {{ padding:46px 0; border-top:1px solid var(--line); }}
.sub {{ color:var(--muted); max-width:66ch; margin:0 0 26px; font-size:15px; }}

.types {{ display:grid; gap:14px;
  grid-template-columns:repeat(auto-fit,minmax(300px,1fr)); }}
.tcard {{ background:var(--panel); border:1px solid var(--line);
  border-radius:3px; padding:18px 20px 16px;
  display:flex; flex-direction:column; gap:10px; }}
.tcard h3 {{ font:600 13px/1 var(--sans); letter-spacing:.1em;
  text-transform:uppercase; color:var(--accent); margin:0; }}
.tcard p {{ margin:0; font-size:14px; color:var(--muted); }}
.tex {{ display:flex; align-items:flex-end; gap:12px; flex-wrap:wrap;
  padding:10px 0 4px; border-top:1px solid var(--line); }}
.glmid {{ font-size:40px; line-height:1; }}
.tbase,.tvar {{ display:flex; flex-direction:column; align-items:center; gap:5px; }}
.tbase i,.tvar i {{ font:400 10px/1 var(--mono); color:var(--muted);
  font-style:normal; }}
.arrow {{ color:var(--muted); padding-bottom:14px; }}
.tother {{ display:flex; align-items:flex-end; gap:10px; flex-wrap:wrap;
  border-top:1px solid var(--line); padding-top:10px; }}
.olab {{ font:600 10px/1.5 var(--sans); letter-spacing:.08em;
  text-transform:uppercase; color:var(--muted); align-self:center; }}
.tvar.sm .gl {{ font-size:25px; }}
.tvar u {{ font:400 9px/1 var(--mono); color:var(--muted); text-decoration:none; }}
.tnote {{ font-size:12.5px; color:var(--muted); margin:0; padding-top:2px; }}

.controls {{ display:flex; gap:8px; flex-wrap:wrap; align-items:center;
  margin-bottom:22px; }}
button {{ font:500 13px var(--sans); padding:7px 15px; cursor:pointer;
  border:1px solid var(--line); background:var(--panel); color:var(--ink);
  border-radius:2px; }}
button[aria-pressed="true"] {{ background:var(--ink); color:var(--ground);
  border-color:var(--ink); }}
button:focus-visible {{ outline:2px solid var(--accent); outline-offset:2px; }}
#shown {{ margin-left:auto; font:400 13px var(--mono); color:var(--muted); }}

.fam {{ display:grid; gap:20px; align-items:start;
  grid-template-columns:104px minmax(0,1fr) 290px;
  background:var(--panel); border:1px solid var(--line); border-radius:3px;
  padding:18px 20px; margin-bottom:10px; }}
.base {{ text-align:center; }}
.glbig {{ font-size:56px; line-height:1.05; display:block; }}
.bid {{ font:600 13px var(--mono); margin-top:8px; }}
.bn {{ font-size:11px; color:var(--muted); }}
.vlab {{ font:600 10px/1 var(--sans); letter-spacing:.1em; text-transform:uppercase;
  color:var(--muted); margin-bottom:12px; }}
.chips {{ display:flex; flex-wrap:wrap; gap:5px; }}
.chip {{ display:flex; flex-direction:column; align-items:center;
  min-width:42px; padding:5px 4px 4px; background:var(--sunk);
  border-radius:2px; }}
.chip .gl {{ font-size:23px; line-height:1.15; }}
.cid {{ font:600 9.5px/1.3 var(--mono); }}
.cn {{ font:400 9px/1.2 var(--mono); color:var(--muted); }}

.test {{ border-left:1px solid var(--line); padding-left:18px; }}
.trow {{ display:grid; grid-template-columns:52px 1fr; gap:7px;
  align-items:center; margin-bottom:7px; }}
.tl {{ font:600 9.5px/1 var(--sans); letter-spacing:.08em; text-transform:uppercase;
  color:var(--muted); }}
.bar {{ display:flex; height:19px; border-radius:2px; overflow:hidden;
  background:var(--sunk); }}
.seg {{ display:flex; align-items:center; justify-content:center;
  min-width:0; overflow:hidden; }}
.seg i {{ font:600 9.5px/1 var(--mono); font-style:normal; }}
.seg.lo {{ background:color-mix(in srgb,var(--accent) 26%,transparent); }}
.seg.lo i {{ color:var(--ink); }}
.seg.hi {{ background:var(--flag); }}
.seg.hi i {{ color:var(--panel); }}
.tn {{ grid-column:2; font:400 10.5px var(--mono); color:var(--muted);
  margin-top:-4px; }}
.verdict {{ font-size:12.5px; margin-top:10px; padding-top:9px;
  border-top:1px solid var(--line); display:flex; justify-content:space-between;
  gap:10px; }}
.verdict .pv {{ font:400 11px var(--mono); color:var(--muted); }}
.verdict.up {{ color:var(--flag); font-weight:600; }}
.verdict.down {{ color:var(--down); font-weight:600; }}
.verdict.flat,.nodata {{ color:var(--muted); }}
.nodata {{ font-size:12.5px; font-style:italic; }}

.caveats li {{ margin-bottom:9px; color:var(--muted); font-size:14.5px; }}
.caveats strong {{ color:var(--ink); font-weight:600; }}
footer {{ padding:34px 0 70px; color:var(--muted); font-size:13px; }}
@media (max-width:940px) {{
  .fam {{ grid-template-columns:82px minmax(0,1fr); }}
  .test {{ grid-column:1/-1; border-left:0; padding-left:0;
    border-top:1px solid var(--line); padding-top:14px; }}
  h1 {{ font-size:34px; }}
}}
</style>

<div class="wrap">
<header>
  <div class="eyebrow">Indus corpus &middot; 2,543 inscribed objects</div>
  <h1>Most Indus signs are other signs, marked</h1>
  <p class="lede">Of {n_signs} distinct signs in the corpus, only {n_fam} are
  independent shapes. The remaining {n_var} are those shapes carrying a
  modifier &mdash; a cross struck through, a chevron above, strokes to either
  side. This catalogues every family and asks whether the modifier changes how
  much of the thing you may count.</p>

  <div class="stats">
    <div class="stat"><b>{n_signs}</b><span>distinct signs attested</span></div>
    <div class="stat"><b>{n_fam}</b><span>base shapes</span></div>
    <div class="stat"><b>{n_var}</b><span>modified variants</span></div>
    <div class="stat"><b>{med_var:.0f}</b><span>median tokens per variant</span></div>
    <div class="stat"><b>{len(testable)}</b><span>families with data to test</span></div>
    <div class="stat"><b>{len(sig)}</b><span>showing a real difference</span></div>
  </div>
</header>

<section>
  <h2>Five recurring modifiers</h2>
  <p class="sub">The same handful of marks reappear across unrelated base
  shapes, which is what makes them look like a system rather than incidental
  variation. The fish (sign 220) is the clearest single demonstration &mdash; it
  takes all five.</p>
  <div class="types">{''.join(type_cards)}</div>
</section>

<section>
  <h2>Does the modifier cap the quantity?</h2>
  <p class="sub">Numerals sit immediately before the sign they count. For each
  family, the bars show which numeral values are found in front of the base
  versus in front of its variants. Ochre marks values of 4 or more. If a
  modifier turned a sign into a larger unit, you would expect it to take only
  small coefficients &mdash; and for two families that is exactly what happens.
  Computed on distinct texts only, so repeated inscriptions cannot inflate
  the counts.</p>

  <div class="controls">
    <button data-f="sig" aria-pressed="false">Significant only</button>
    <button data-f="testable" aria-pressed="true">Testable only</button>
    <button data-f="all" aria-pressed="false">All {n_fam} families</button>
    <span id="shown"></span>
  </div>
  <div id="list">{''.join(rows)}</div>
</section>

<section>
  <h2>What this does and does not show</h2>
  <ul class="caveats">
    <li><strong>The decomposition is solid.</strong> {n_var} of {n_signs} signs
    are variants of {n_fam} bases. Whatever the marks mean, Indus writing was
    built by modifying a small set of shapes.</li>
    <li><strong>The quantity effect is family-specific, not a law.</strong> Only
    {len(testable)} families have enough numeral-preceded occurrences to test at
    all, {len(sig)} show a real difference, and they do not agree in direction.
    Sign 220 and sign 390 accept larger numbers than their variants; sign 415 is
    the reverse.</li>
    <li><strong>Variants are rare.</strong> The median variant appears
    {med_var:.0f} times; {rare} of {n_var} appear five times or fewer. That
    scarcity, not the method, is what limits the analysis.</li>
    <li><strong>Families are grouped by sign id.</strong> The id numbering
    encodes shape, verified against the rendered chart, with families cut at id
    gaps greater than two and one manual merge for the fish. A mis-grouped
    family would produce a spurious comparison.</li>
    <li><strong>A cap on quantity is not proof of multiplication.</strong> It
    shows the mark constrains how much can be counted. A variant meaning a
    title, a rank or a named person would look the same.</li>
  </ul>
</section>

<footer>
  Corpus: epigraphic layer of the CISI digitisation in
  <span class="gl" style="font-family:var(--mono)">yajnadevam/indus-website</span>,
  2,543 objects, 11,135 sign tokens. Glyphs drawn with the sk_indus_script font,
  which covers 98.1% of tokens; signs it lacks appear as their numeric id.
  Decipherment claims from that source are not used.
</footer>
</div>

<script>
const list = document.getElementById('list');
const shown = document.getElementById('shown');
const btns = [...document.querySelectorAll('.controls button')];
function apply(mode) {{
  btns.forEach(b => b.setAttribute('aria-pressed', String(b.dataset.f === mode)));
  let n = 0;
  list.querySelectorAll('.fam').forEach(el => {{
    const ok = mode === 'all'
      || (mode === 'testable' && el.dataset.testable === '1')
      || (mode === 'sig' && el.dataset.sig === '1');
    el.style.display = ok ? '' : 'none';
    if (ok) n++;
  }});
  shown.textContent = n + ' of {n_fam} families';
}}
btns.forEach(b => b.addEventListener('click', () => apply(b.dataset.f)));
apply('testable');
</script>
"""

open("modifiers.html", "w").write(html.encode("ascii", "xmlcharrefreplace").decode())
print(f"wrote modifiers.html  ({len(html)/1e6:.1f} MB)")
print(f"  {n_signs} signs, {n_fam} bases, {n_var} variants, "
      f"{len(testable)} testable, {len(sig)} significant")
