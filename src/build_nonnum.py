"""Page: the 571 signs that are not numerals, split by whether they get counted."""
import base64
import json
import re
import sys
from collections import Counter

from scipy import stats

sys.path.insert(0, "src")
from gallery import FONT, font_codepoints

have = font_codepoints(FONT)
cp = {g["glyph_id"]: int(re.sub(r"[^0-9A-Fa-f]", "", g["unicode"]), 16)
      for g in json.load(open("data/parsed/glyphs.json"))
      if str(g["unicode"]).startswith("&#x")}
b64 = base64.b64encode(FONT.read_bytes()).decode()

NUM = set(range(1, 8)) | set(range(12, 20)) | set(range(31, 36))
EXCLUDED = [25, 27, 28, 29, 36, 41, 42, 45, 46, 48, 49, 50, 51, 55, 56, 57, 58, 59]

lines = json.load(open("data/parsed/lines.json"))
texts = [tuple(l["signs"]) for l in lines if l["signs"]]
freq = Counter(g for t in texts for g in t)
nonnum = sorted((g for g in freq if g not in NUM), key=lambda g: -freq[g])

tot = prev = 0
for t in texts:
    for j in range(1, len(t)):
        tot += 1
        prev += t[j - 1] in NUM
BASE = prev / tot

stat = {}
for g in freq:
    n = p = 0
    for t in texts:
        for j, s in enumerate(t):
            if s == g and j > 0:
                n += 1
                p += t[j - 1] in NUM
    pv = stats.binomtest(p, n, BASE).pvalue if n >= 15 else None
    stat[g] = {"n": n, "p": p, "rate": (p / n) if n else None, "pv": pv}

counted = [g for g in nonnum if stat[g]["pv"] is not None
           and stat[g]["pv"] < .05 and stat[g]["rate"] > BASE]
never = [g for g in nonnum if stat[g]["pv"] is not None
         and stat[g]["pv"] < .05 and stat[g]["rate"] < BASE]
neutral = [g for g in nonnum if stat[g]["pv"] is not None and g not in counted
           and g not in never]
untested = [g for g in nonnum if stat[g]["pv"] is None]
counted.sort(key=lambda g: -stat[g]["rate"])
never.sort(key=lambda g: stat[g]["rate"])


def gl(g, cls=""):
    c = f"gl {cls}".strip()
    if cp.get(g) in have:
        return f'<span class="{c}">&#x{cp[g]:X};</span>'
    return f'<span class="{c} miss">{g}</span>'


def card(g, show_rate=True):
    s = stat[g]
    r = ""
    if show_rate and s["rate"] is not None and s["pv"] is not None:
        pct = f'{s["rate"]:.0%}'
        cls = "up" if g in counted else ("down" if g in never else "flat")
        r = (f'<span class="rate {cls}">{pct}</span>'
             f'<span class="rn">{s["p"]}/{s["n"]}</span>')
    return (f'<div class="sc"><div class="scg">{gl(g)}</div>'
            f'<div class="sci">{g}</div><div class="scn">{freq[g]}</div>{r}</div>')


def grid(ids, show_rate=True):
    return f'<div class="sgrid">{"".join(card(g, show_rate) for g in ids)}</div>'


exrows = []
for g in EXCLUDED:
    if not freq.get(g):
        continue
    s = stat[g]
    rate = "&mdash;" if not s["n"] else f'{s["rate"]:.0%}'
    exrows.append(f'<tr><td class="tg">{gl(g)}</td><td>{g}</td><td>{freq[g]}</td>'
                  f'<td>{s["p"]}/{s["n"]}</td><td>{rate}</td></tr>')

html = f"""<title>Signs That Are Not Numbers</title>
<style>
:root {{
  --ground:#e8ebe6; --panel:#f5f7f3; --sunk:#dfe4dc;
  --ink:#191f1b; --muted:#69726b; --line:#d2d8d0;
  --accent:#2e5c76; --flag:#96682c; --down:#4a6f52;
  --serif:"Iowan Old Style","Palatino Linotype",Palatino,Georgia,serif;
  --sans:ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif;
  --mono:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
}}
@media (prefers-color-scheme: dark) {{
  :root:not([data-theme="light"]) {{
    --ground:#131813; --panel:#1b211c; --sunk:#10150f;
    --ink:#e5eae3; --muted:#8f988f; --line:#2a312b;
    --accent:#7fb2ce; --flag:#d6a45e; --down:#8fc19c;
  }}
}}
:root[data-theme="dark"] {{
  --ground:#131813; --panel:#1b211c; --sunk:#10150f;
  --ink:#e5eae3; --muted:#8f988f; --line:#2a312b;
  --accent:#7fb2ce; --flag:#d6a45e; --down:#8fc19c;
}}
@font-face {{ font-family:"Indus";
  src:url(data:font/ttf;base64,{b64}) format("truetype"); font-display:block; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; background:var(--ground); color:var(--ink); font:16px/1.6 var(--sans); }}
.wrap {{ max-width:1120px; margin:0 auto; padding:0 28px; }}
.gl {{ font-family:"Indus"; }}
.miss {{ font-family:var(--mono); font-size:.55em; color:var(--flag);
  border:1px dashed currentColor; border-radius:3px; padding:0 3px; }}
header {{ padding:64px 0 30px; }}
.eyebrow {{ font:600 11px/1 var(--sans); letter-spacing:.16em; text-transform:uppercase;
  color:var(--accent); margin-bottom:18px; }}
h1 {{ font:400 46px/1.08 var(--serif); margin:0 0 16px; letter-spacing:-.015em;
  text-wrap:balance; }}
.lede {{ font:400 19px/1.55 var(--serif); color:var(--muted); max-width:62ch; margin:0; }}
.stats {{ display:grid; gap:1px; background:var(--line);
  grid-template-columns:repeat(auto-fit,minmax(150px,1fr));
  border:1px solid var(--line); border-radius:3px; overflow:hidden; margin:36px 0 0; }}
.stat {{ background:var(--panel); padding:17px 19px; }}
.stat b {{ display:block; font:600 29px/1 var(--mono); font-variant-numeric:tabular-nums; }}
.stat span {{ display:block; font-size:12.5px; color:var(--muted); margin-top:6px; }}
section {{ padding:44px 0; border-top:1px solid var(--line); }}
h2 {{ font:400 27px/1.2 var(--serif); margin:0 0 10px; }}
h3 {{ font:600 12px/1 var(--sans); letter-spacing:.11em; text-transform:uppercase;
  margin:26px 0 12px; }}
h3.up {{ color:var(--flag); }} h3.down {{ color:var(--down); }} h3.flat {{ color:var(--muted); }}
.sub {{ color:var(--muted); max-width:68ch; margin:0 0 8px; font-size:15px; }}
.sgrid {{ display:grid; gap:5px; grid-template-columns:repeat(auto-fill,minmax(66px,1fr)); }}
.sc {{ background:var(--panel); border:1px solid var(--line); border-radius:3px;
  padding:7px 3px 5px; text-align:center; }}
.scg {{ font-size:27px; line-height:1.15; height:34px; }}
.sci {{ font:600 10px/1.3 var(--mono); }}
.scn {{ font:400 9px/1.2 var(--mono); color:var(--muted); }}
.rate {{ display:block; font:600 10px/1.4 var(--mono); margin-top:3px; }}
.rate.up {{ color:var(--flag); }} .rate.down {{ color:var(--down); }}
.rate.flat {{ color:var(--muted); }}
.rn {{ display:block; font:400 8.5px/1.2 var(--mono); color:var(--muted); }}
table {{ border-collapse:collapse; width:100%; max-width:620px; font-size:14px; }}
th,td {{ text-align:left; padding:7px 12px 7px 0; border-bottom:1px solid var(--line);
  font-variant-numeric:tabular-nums; }}
th {{ font:600 10.5px/1 var(--sans); letter-spacing:.09em; text-transform:uppercase;
  color:var(--muted); }}
td.tg {{ font-family:"Indus"; font-size:25px; width:44px; }}
.caveats li {{ margin-bottom:9px; color:var(--muted); font-size:14.5px; }}
.caveats strong {{ color:var(--ink); font-weight:600; }}
footer {{ padding:32px 0 70px; color:var(--muted); font-size:13px; }}
@media (max-width:700px) {{ h1 {{ font-size:33px; }} }}
</style>

<div class="wrap">
<header>
  <div class="eyebrow">Indus corpus &middot; the non-numeral inventory</div>
  <h1>Signs that are not numbers</h1>
  <p class="lede">Twenty of the 591 signs are stroke-group numerals. These are the
  other {len(nonnum)}. Rather than list them flat, they are split by a question
  the corpus can answer: does anyone ever put a number in front of this sign?
  That separates the things Indus scribes counted from the things they never
  did.</p>
  <div class="stats">
    <div class="stat"><b>{len(nonnum)}</b><span>non-numeral signs</span></div>
    <div class="stat"><b>{sum(freq[g] for g in nonnum):,}</b><span>tokens</span></div>
    <div class="stat"><b>{BASE:.0%}</b><span>baseline chance of a numeral before any sign</span></div>
    <div class="stat"><b>{len(counted)}</b><span>counted more than chance</span></div>
    <div class="stat"><b>{len(never)}</b><span>counted less than chance</span></div>
    <div class="stat"><b>{len(untested)}</b><span>too rare to test</span></div>
  </div>
</header>

<section>
  <h2>Counted, and never counted</h2>
  <p class="sub">A numeral sits immediately before the sign it counts, which
  happens {BASE:.0%} of the time across the corpus. Each sign below shows the
  share of its own occurrences that are preceded by a numeral. Only signs with
  at least 15 positioned occurrences are tested; significance is a binomial test
  against the {BASE:.0%} baseline.</p>

  <h3 class="up">{len(counted)} signs are counted far more than chance</h3>
  {grid(counted)}

  <h3 class="down">{len(never)} signs are almost never counted</h3>
  {grid(never)}

  <h3 class="flat">{len(neutral)} signs sit at the baseline</h3>
  {grid(neutral)}
</section>

<section>
  <h2>The stroke-like signs I set aside</h2>
  <p class="sub">These carry strokes but were kept out of the numeral set
  because they add brackets, bars or hooks. I tried to settle it by asking
  whether they get preceded by numerals &mdash; on the theory that a numeral
  would not be. <strong>The test fails.</strong> Genuine numerals are themselves
  preceded by numerals often (sign 3 at 41%, sign 31 at 30%), because numerals
  cluster. So this stays an open judgment call, shown here with its data rather
  than resolved.</p>
  <table>
    <tr><th></th><th>id</th><th>tokens</th><th>preceded by numeral</th><th>rate</th></tr>
    {''.join(exrows)}
  </table>
</section>

<section>
  <h2>The full inventory</h2>
  <p class="sub">All {len(nonnum)} non-numeral signs by frequency. The long tail
  is the story: most signs in this script appear a handful of times, which is
  the ceiling on every analysis in this project.</p>
  {grid(nonnum, show_rate=False)}
</section>

<section>
  <h2>Reading it</h2>
  <ul class="caveats">
    <li><strong>The split is functional, not semantic.</strong> Sign 700 is
    preceded by a numeral 80% of the time; sign 400 &mdash; the second most
    frequent sign in the corpus &mdash; once in 308 opportunities. Whatever 400
    is, it is not a commodity.</li>
    <li><strong>Never-counted does not mean unimportant.</strong> The
    never-counted group contains some of the most common signs in the script.
    They are doing a different job.</li>
    <li><strong>Most signs cannot be tested.</strong> {len(untested)} of
    {len(nonnum)} appear too rarely to say anything about.</li>
    <li><strong>Adjacency is not grammar.</strong> "Preceded by a numeral" is a
    positional fact. It is consistent with counting, but this corpus cannot show
    that the numeral modifies the sign rather than merely sitting before it.</li>
  </ul>
</section>

<footer>
  Corpus: epigraphic layer of the CISI digitisation in yajnadevam/indus-website
  &mdash; 2,543 objects, 11,135 sign tokens. Glyphs drawn with sk_indus_script;
  signs the font lacks appear as their numeric id. Decipherment claims from that
  source are not used.
</footer>
</div>
"""

open("nonnumerals.html", "w").write(html.encode("ascii", "xmlcharrefreplace").decode())
print(f"wrote nonnumerals.html")
print(f"  {len(nonnum)} non-numeral, counted {len(counted)}, never {len(never)}, "
      f"neutral {len(neutral)}, untested {len(untested)}")
