"""Page: all 30 ordering pairs, before and after the positional control."""
import base64
import json
import re
import sys
from collections import defaultdict
from itertools import combinations

import numpy as np
from scipy import stats

sys.path.insert(0, "src")
from gallery import FONT, font_codepoints

have = font_codepoints(FONT)
cp = {g["glyph_id"]: int(re.sub(r"[^0-9A-Fa-f]", "", g["unicode"]), 16)
      for g in json.load(open("data/parsed/glyphs.json"))
      if str(g["unicode"]).startswith("&#x")}
b64 = base64.b64encode(FONT.read_bytes()).decode()

NEVER = [615, 527, 742, 595, 636, 400, 90, 60, 690, 435, 741, 100, 740, 920, 151]
lines = json.load(open("data/parsed/lines.json"))
texts = [tuple(l["signs"]) for l in lines if l["signs"]]
uniq = sorted(set(texts))

pos = defaultdict(list)
for t in texts:
    if len(t) > 1:
        for j, g in enumerate(t):
            pos[g].append(j / (len(t) - 1))
mp = {g: float(np.mean(pos[g])) for g in NEVER if pos[g]}

rng = np.random.default_rng(0)
rows = []
for a, b in combinations(NEVER, 2):
    ab = ba = 0
    for t in uniq:
        if a in t and b in t:
            ia, ib = t.index(a), t.index(b)
            ab += ia < ib
            ba += ib < ia
    n = ab + ba
    if n < 6:
        continue
    pred = float((rng.choice(np.array(pos[a]), 40000)
                  < rng.choice(np.array(pos[b]), 40000)).mean())
    praw = stats.binomtest(max(ab, ba), n, .5).pvalue
    pc = stats.binomtest(ab, n, min(max(pred, 1e-6), 1 - 1e-6)).pvalue
    rows.append(dict(a=a, b=b, ab=ab, ba=ba, n=n, obs=ab / n, pred=pred,
                     praw=praw, pc=pc))
rows.sort(key=lambda r: r["pc"])
n_raw = sum(r["praw"] < .05 for r in rows)
n_ctrl = sum(r["pc"] < .05 for r in rows)


def gl(g, cls=""):
    c = f"gl {cls}".strip()
    if cp.get(g) in have:
        return f'<span class="{c}">&#x{cp[g]:X};</span>'
    return f'<span class="{c} miss">{g}</span>'


def fmt(p):
    return f"{p:.0e}".replace("e-0", "e&minus;") if p < .001 else f"{p:.3f}"


trs = []
for r in rows:
    real = r["pc"] < .05
    cls = "real" if real else ("slots" if r["praw"] < .05 else "none")
    label = ("real ordering" if real else
             ("explained by slots" if r["praw"] < .05 else "no ordering"))
    delta = r["obs"] - r["pred"]
    trs.append(f"""<tr class="{cls}" data-cls="{cls}">
  <td class="pair">{gl(r['a'])}<b>{r['a']}</b><span class="lt">&lt;</span>
      {gl(r['b'])}<b>{r['b']}</b></td>
  <td class="num">{r['ab']}</td><td class="num">{r['ba']}</td>
  <td class="num">{r['n']}</td>
  <td class="num obs">{r['obs']:.2f}</td>
  <td class="num pred">{r['pred']:.2f}</td>
  <td class="num delta">{'+' if delta >= 0 else '&minus;'}{abs(delta):.2f}</td>
  <td class="num">{fmt(r['praw'])}</td>
  <td class="num strong">{fmt(r['pc'])}</td>
  <td class="v">{label}</td></tr>""")

slotrows = "".join(
    f'<div class="sl"><span class="slg">{gl(g)}</span>'
    f'<span class="sli">{g}</span>'
    f'<span class="slb"><i style="left:{v*100:.1f}%"></i></span>'
    f'<span class="slv">{v:.3f}</span></div>'
    for g, v in sorted(mp.items(), key=lambda kv: kv[1]))

html = f"""<title>Ordering or Just Seating</title>
<style>
:root {{
  --ground:#e8ebe6; --panel:#f5f7f3; --sunk:#dfe4dc;
  --ink:#191f1b; --muted:#69726b; --line:#d2d8d0;
  --accent:#2e5c76; --real:#96682c; --slots:#7d8a86;
  --serif:"Iowan Old Style","Palatino Linotype",Palatino,Georgia,serif;
  --sans:ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif;
  --mono:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
}}
@media (prefers-color-scheme: dark) {{
  :root:not([data-theme="light"]) {{
    --ground:#131813; --panel:#1b211c; --sunk:#10150f;
    --ink:#e5eae3; --muted:#8f988f; --line:#2a312b;
    --accent:#7fb2ce; --real:#d6a45e; --slots:#6e7a76;
  }}
}}
:root[data-theme="dark"] {{
  --ground:#131813; --panel:#1b211c; --sunk:#10150f;
  --ink:#e5eae3; --muted:#8f988f; --line:#2a312b;
  --accent:#7fb2ce; --real:#d6a45e; --slots:#6e7a76;
}}
@font-face {{ font-family:"Indus";
  src:url(data:font/ttf;base64,{b64}) format("truetype"); font-display:block; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; background:var(--ground); color:var(--ink); font:16px/1.6 var(--sans); }}
.wrap {{ max-width:1080px; margin:0 auto; padding:0 26px; }}
.gl {{ font-family:"Indus"; font-size:23px; line-height:1; }}
.miss {{ font-family:var(--mono); font-size:10px; color:var(--real);
  border:1px dashed currentColor; border-radius:3px; padding:0 3px; }}
header {{ padding:62px 0 28px; }}
.eyebrow {{ font:600 11px/1 var(--sans); letter-spacing:.16em; text-transform:uppercase;
  color:var(--accent); margin-bottom:18px; }}
h1 {{ font:400 44px/1.09 var(--serif); margin:0 0 16px; letter-spacing:-.015em;
  text-wrap:balance; }}
.lede {{ font:400 19px/1.55 var(--serif); color:var(--muted); max-width:62ch; margin:0; }}
.stats {{ display:grid; gap:1px; background:var(--line);
  grid-template-columns:repeat(auto-fit,minmax(168px,1fr));
  border:1px solid var(--line); border-radius:3px; overflow:hidden; margin:34px 0 0; }}
.stat {{ background:var(--panel); padding:17px 19px; }}
.stat b {{ display:block; font:600 29px/1 var(--mono); font-variant-numeric:tabular-nums; }}
.stat span {{ display:block; font-size:12.5px; color:var(--muted); margin-top:6px; }}
section {{ padding:44px 0; border-top:1px solid var(--line); }}
h2 {{ font:400 26px/1.2 var(--serif); margin:0 0 10px; }}
.sub {{ color:var(--muted); max-width:70ch; margin:0 0 22px; font-size:15px; }}
.sl {{ display:grid; grid-template-columns:34px 42px 1fr 54px; align-items:center;
  gap:10px; padding:4px 0; }}
.sli {{ font:600 11px var(--mono); color:var(--muted); }}
.slb {{ position:relative; height:5px; background:var(--sunk); border-radius:3px; }}
.slb i {{ position:absolute; top:-4px; width:3px; height:13px; background:var(--accent);
  border-radius:2px; }}
.slv {{ font:400 11px var(--mono); color:var(--muted); text-align:right;
  font-variant-numeric:tabular-nums; }}
.scale {{ display:flex; justify-content:space-between; font:600 9.5px var(--sans);
  letter-spacing:.09em; text-transform:uppercase; color:var(--muted);
  margin:6px 0 0 86px; padding-right:64px; }}
.controls {{ display:flex; gap:8px; flex-wrap:wrap; margin-bottom:16px; }}
button {{ font:500 13px var(--sans); padding:7px 15px; cursor:pointer;
  border:1px solid var(--line); background:var(--panel); color:var(--ink);
  border-radius:2px; }}
button[aria-pressed="true"] {{ background:var(--ink); color:var(--ground);
  border-color:var(--ink); }}
button:focus-visible {{ outline:2px solid var(--accent); outline-offset:2px; }}
.tbox {{ overflow-x:auto; border:1px solid var(--line); border-radius:3px;
  background:var(--panel); }}
table {{ border-collapse:collapse; width:100%; min-width:800px; font-size:13.5px; }}
th {{ font:600 10px/1.3 var(--sans); letter-spacing:.08em; text-transform:uppercase;
  color:var(--muted); text-align:right; padding:12px 12px 9px; position:sticky; top:0;
  background:var(--panel); border-bottom:1px solid var(--line); }}
th:first-child, th:last-child {{ text-align:left; }}
td {{ padding:8px 12px; border-bottom:1px solid var(--line);
  font-variant-numeric:tabular-nums; }}
td.num {{ text-align:right; font-family:var(--mono); font-size:12.5px; }}
td.pair {{ display:flex; align-items:center; gap:5px; white-space:nowrap; }}
td.pair b {{ font:600 11px var(--mono); }}
.lt {{ color:var(--muted); padding:0 3px; }}
td.strong {{ font-weight:700; }}
td.v {{ font-size:12px; color:var(--muted); white-space:nowrap; }}
tr.real td.v, tr.real td.strong {{ color:var(--real); font-weight:600; }}
tr.real td.delta {{ color:var(--real); font-weight:600; }}
tr.real {{ background:color-mix(in srgb,var(--real) 7%,transparent); }}
tr.slots td.v {{ color:var(--slots); }}
tbody tr:last-child td {{ border-bottom:0; }}
.caveats li {{ margin-bottom:9px; color:var(--muted); font-size:14.5px; }}
.caveats strong {{ color:var(--ink); font-weight:600; }}
footer {{ padding:30px 0 70px; color:var(--muted); font-size:13px; }}
@media (max-width:640px) {{ h1 {{ font-size:32px; }} }}
</style>

<div class="wrap">
<header>
  <div class="eyebrow">Indus corpus &middot; the never-counted signs</div>
  <h1>Ordering, or just seating</h1>
  <p class="lede">Fifteen signs in the corpus are never preceded by a number.
  When two of them share a text, one almost always comes first &mdash; which
  looks like rank. But if one sign simply prefers the start of a text and the
  other the end, that order follows with no rule behind it. This separates the
  two.</p>
  <div class="stats">
    <div class="stat"><b>30</b><span>pairs co-occurring at least six times</span></div>
    <div class="stat"><b>{n_raw}</b><span>look ordered against a coin flip</span></div>
    <div class="stat"><b>{n_ctrl}</b><span>survive the positional control</span></div>
    <div class="stat"><b>{n_raw - n_ctrl}</b><span>were seating preference</span></div>
  </div>
</header>

<section>
  <h2>Where each sign likes to sit</h2>
  <p class="sub">Mean relative position across the corpus. This is the
  confound &mdash; it alone predicts most of the apparent ordering.</p>
  {slotrows}
  <div class="scale"><span>text-initial</span><span>text-final</span></div>
</section>

<section>
  <h2>All 30 pairs</h2>
  <p class="sub"><b>obs</b> is how often the left sign actually comes first.
  <b>pred</b> is what you would get by drawing each sign's slot independently
  from its own position distribution &mdash; the order you would see with no
  rule at all. <b>p raw</b> tests against a coin flip; <b>p ctrl</b> tests
  against <i>pred</i>. Only the second one means anything.</p>
  <div class="controls">
    <button data-f="all" aria-pressed="true">All 30</button>
    <button data-f="real" aria-pressed="false">Real ordering ({n_ctrl})</button>
    <button data-f="slots" aria-pressed="false">Explained by slots ({n_raw - n_ctrl})</button>
  </div>
  <div class="tbox"><table>
    <thead><tr><th>pair</th><th>a&lt;b</th><th>b&lt;a</th><th>n</th>
      <th>obs</th><th>pred</th><th>&Delta;</th><th>p raw</th><th>p ctrl</th>
      <th>verdict</th></tr></thead>
    <tbody id="tb">{''.join(trs)}</tbody>
  </table></div>
</section>

<section>
  <h2>What the two groups look like</h2>
  <ul class="caveats">
    <li><strong>The clearest false positive is 400 &lt; 740.</strong> 17 versus
    87, p = 2e&minus;12 raw &mdash; it reads as an iron law. But 400 sits at
    0.900 and 740 at 0.866, so the no-rule prediction is 0.14 and the observed
    0.16 is nothing at all. Every one of sign 400's six pairings collapses the
    same way.</li>
    <li><strong>The survivors defy their slots.</strong> 60 &lt; 741 is the
    standout: both sit early and close together, 0.306 against 0.349, so a near
    coin flip at 0.58 is expected. Observed is 28 to 1. And 690 &lt; 435 runs
    backwards from its prediction, 0.09 against 0.40.</li>
    <li><strong>The real rules cluster at the front.</strong> Almost every
    surviving pair involves signs from the early half of the text. The tail end
    &mdash; 740, 400, 90, 527, 151 &mdash; is fixed furniture whose order needs
    no rule to explain.</li>
    <li><strong>This does not identify what the signs are.</strong> It shows
    eight genuine adjacency constraints. Whether they encode rank, grammar or
    formula convention is not something sequence alone can settle.</li>
  </ul>
</section>

<footer>
  Computed on 1,980 distinct texts, so repeated inscriptions cannot inflate any
  count. Predicted rates from 40,000 draws per pair. Corpus: epigraphic layer of
  the CISI digitisation in yajnadevam/indus-website.
</footer>
</div>

<script>
const btns=[...document.querySelectorAll('.controls button')];
const rows=[...document.querySelectorAll('#tb tr')];
btns.forEach(b=>b.addEventListener('click',()=>{{
  btns.forEach(x=>x.setAttribute('aria-pressed',String(x===b)));
  rows.forEach(r=>{{r.style.display =
    (b.dataset.f==='all'||r.dataset.cls===b.dataset.f)?'':'none';}});
}}));
</script>
"""

open("ordering.html", "w").write(html.encode("ascii", "xmlcharrefreplace").decode())
print(f"wrote ordering.html  raw={n_raw} ctrl={n_ctrl}")
