"""Page: the whole investigation -- what was tried, what survived, what broke."""
import base64
import json
import re
import sys

sys.path.insert(0, "src")
from gallery import FONT  # noqa: E402

b64 = base64.b64encode(FONT.read_bytes()).decode()
CP = {g["glyph_id"]: int(re.sub(r"[^0-9A-Fa-f]", "", g["unicode"]), 16)
      for g in json.load(open("data/parsed/glyphs.json"))
      if str(g["unicode"]).startswith("&#x")}


def gl(i):
    return (f'<span class="gl">&#x{CP[i]:X};</span>' if i in CP
            else '<span class="miss">no glyph</span>')


# ---------------------------------------------------------------- the ledger
# verdict: broke | held | part
LEDGER = [
    (1, "Is the corpus trustworthy?", "part",
     "Sourced 2543 artefacts from the yajnadevam SQL, taking only the epigraphic "
     "layer and none of its decipherment claims. Validated against a fact we did "
     "not supply: sign 740 came out as both the most frequent sign and hard "
     "against the text end — the known signature of the jar sign.",
     "740 = 11.4% of tokens, mean position .109", "01-corpus"),
    (2, "Do the signs depend on the picture on the seal?", "broke",
     "First pass found 25 significant sign–motif associations. Then we "
     "deduplicated: one 11-sign text stamped eleven times, all rhinoceros. Every "
     "one of the 25 vanished. This set the rule for everything after it.",
     "p = .069, R² ≈ 1% after dedup", "03-sign-motif"),
    (3, "Are the stroke signs numbers?", "held",
     "Yes. Three parallel series — short strokes, long strokes, stacked rows "
     "— encode the same values with different graphics. The stacked form "
     "takes over exactly where a single row stops being legible.",
     "1788 numeral tokens identified", "04-numerals"),
    (4, "Is the counting base 10?", "broke",
     "Concluded base 8, on a hard cliff after value 7. Withdrawn at step 16 "
     "— the cliff was an artefact of excluding the bracketed and three-row "
     "stroke signs.",
     "conclusion retracted", "05-radix"),
    (5, "Is the fish sign a number being operated on?", "part",
     "The fish family takes numeric coefficients, and a marked fish behaves "
     "differently from a plain one: it never takes a coefficient above 3. "
     "Independently, Parpola reads his numerals as compounds with the fish "
     "— arrived at here from co-occurrence counts alone.",
     "p = 1.3e-07", "07-fish-as-operand"),
    (6, "Are the never-counted signs a household roster?", "broke",
     "They do cluster and they do hold fixed positions. But in any census you "
     "count the members, and these are never counted — sign 400 takes one "
     "numeral in 308 opportunities. A roster whose entries cannot be enumerated "
     "is not a roster. Sign 740 also appears in 48% of all texts, which no "
     "person is.",
     "23 of 30 orderings → 8 after control", "08-hierarchy"),
    (7, "Are these musical notes?", "broke",
     "A melody reuses its pitches. These texts avoid reusing a sign eleven times "
     "below chance. The inventory is wrong too: 591 signs, 34% of them appearing "
     "exactly once.",
     "z = −19.1", "09-music"),
    (8, "Could the numerals be repeat counts, hiding the repetition?", "broke",
     "Compression only removes repeats that sit next to each other. Returning to "
     "a pitch later — which is what melody is — cannot be compressed "
     "away, and it is just as depleted.",
     "74 observed vs 271 expected, z = −13.5", "09-music"),
    (9, "Can we simply get more data?", "part",
     "No. Every free corpus on GitHub traces back to the same two digitizations. "
     "ICIT is 1.6× larger and gated behind an email. What we did get: a "
     "validated Parpola sign-number crosswalk, and the first error bar this field "
     "has had — two people digitizing the same 161 seals agree on 93% of "
     "signs.",
     "93.2% inter-transcriber agreement", "10-more-data"),
    (10, "Is “1” rare because nobody writes it?", "held",
     "Probably. It is droppable in a way 2 and 3 are not, it counts the same "
     "nouns, it sits in the numeral slot — and whether it gets written "
     "depends on the medium, not the message. Seals write it twice as often as "
     "tablets. That is a convention, not information.",
     "3 of 4 tests pass", "11-unmarked-one"),
    (11, "Does “never together” carve the script into fields?", "part",
     "Globally, no — only 35 of 77 testable signs avoid anything at all. But "
     "one field falls out cleanly and it is the strongest effect in the project: "
     "a terminal slot that holds exactly one sign. And two signs that habitually "
     "end texts turn out to sit <em>behind</em> it, so there are two positions at "
     "the end, not one.",
     "740 / 520 together 6 times, 90 expected", "12-slots"),
    (12, "Do long texts contain short ones?", "part",
     "Twice as often as chance. But the corpus has no damage flags, and a broken "
     "seal is trivially a fragment of a longer text. Counting only texts with a "
     "hole in the middle — which breakage cannot produce — most of the "
     "effect goes away, though not all of it.",
     "22.4% → 5.8% vs 4.1% once breakage is excluded", "13-growth"),
    (13, "Do seals and tablets fill out different forms?", "held",
     "Same signs, same layout, different value in the last field. Tablets append "
     "sign 400 behind the ending that seals leave off. The frozen opening formula "
     "is three times commoner on seals. And, against expectation, the "
     "mass-produced tablets are the ones that <em>don’t</em> count.",
     "p = 1.1e-14", "14-object-forms"),
    (14, "Does the form vary by city?", "held",
     "Almost not at all — and the absence is the finding. Two capitals 600 km "
     "apart produce statistically indistinguishable seal texts. The only regional "
     "practice in the corpus is Harappa’s tablets. What you write on matters "
     "about twice as much as where you are.",
     "seal endings, MD vs Harappa: p = 0.98", "15-city-forms"),
    (15, "Read every stroke sign as a number with a modifier.", "held",
     "Rendered all of them at 380px and counted instead of guessing from the id. "
     "Sign 55 is twelve strokes with 37 tokens, and it passes every numeral test. "
     "Values 1–9 fade out normally; 12 stands alone at forty times its "
     "extrapolation. Base 8 could not survive that. The bracket half of the idea "
     "failed — sign 48 is its own sign, followed by the jar in all 14 cases.",
     "12 observed 37, expected 0.9, p = 1.4e-45", "16-twelve"),
]

HOLDS = [
    ("The terminal slot", 740, 520,
     "Two of the commonest signs share a text six times where chance predicts "
     "ninety. They compete for the last position, and it holds exactly one "
     "filler. Survives every control available.", "z = −14.1"),
    ("A second position behind it", 400, 90,
     "Both habitually end texts, yet neither avoids the jar sign. When they "
     "co-occur with it they sit after it — 400 in 91 of 109 cases. Counting "
     "which sign comes last would have missed this.", "91 of 109"),
    ("One form, held across a civilisation", 740, None,
     "Mohenjo-daro and Harappa produce seal texts whose endings are "
     "indistinguishable. The minor towns follow. This matches the "
     "standardisation already known from Indus weights and brick ratios.",
     "p = 0.98"),
    ("Texts do not reuse a sign", None, None,
     "Far below chance, and not only for adjacent repeats. An inscription "
     "behaves less like a sequence and more like a set of distinct values.",
     "z = −19.1"),
    ("A quantity at twelve", 55, None,
     "Values 1–9 decay smoothly and 10 and 11 are absent exactly as that "
     "decay predicts. Then twelve, forty times over its extrapolation. A unit, "
     "not a digit — though nothing visibly multiplies it.",
     "p = 1.4e-45"),
    ("A frozen two-sign unit", 817, 2,
     "One sign that drags a specific numeral behind it in three-quarters of "
     "cases, and it is a seal convention: 18.5% of seal texts against 5.7% of "
     "tablet texts.", "246 of 327"),
]

CORRECTIONS = [
    ("Two-row numerals were read as their raw id.",
     "Caught by zooming in on the rendered chart: sign 16 is six strokes, not "
     "sixteen. Every value in the numeral work shifted."),
    ("Twenty-five sign–motif associations were duplicates.",
     "One text stamped eleven times, all on rhinoceros seals. Deduplication "
     "became mandatory for everything afterwards."),
    ("Base 8 was wrong.",
     "It depended on excluding stroke signs we had filed as unclassifiable. One "
     "of them is a twelve with 37 tokens."),
    ("A numeral appeared to precede sign 55 significantly.",
     "Six copies of one text were doing the work. After dedup, p = 0.23 and the "
     "multiplied-base reading fails."),
    ("Modifier examples in an earlier page were the wrong family.",
     "Caught by rendering the candidates and looking at them rather than "
     "trusting adjacent id numbers."),
]

OPEN = [
    ("Sign 56 cannot be read.", "Ten tokens, and no glyph for it in this font. "
     "It sits in the stroke range, so it could move the numeral picture again."),
    ("Twelve, or “many”?", "Three rows of four could be a conventional "
     "plural rather than a literal count. Every test run here would look "
     "identical either way."),
    ("The middle of a text is untested.", "Positional grammar is recoverable at "
     "the end. Whether the middle is unstructured or merely too sparse to "
     "measure cannot be settled at this corpus size."),
    ("ICIT.", "4660 artefacts, 17957 signs — 1.6× what we have. Access "
     "is by writing to the administrator. It is the only thing that would move "
     "the ceiling."),
]

VERD = {"held": ("holds", "held"), "broke": ("ruled out", "broke"),
        "part": ("partly", "part")}


def ledger_html():
    out = []
    for n, q, v, body, stat, note in LEDGER:
        out.append(
            f'<article class="row {v}">'
            f'<div class="rail"><span class="seq">{n:02d}</span>'
            f'<span class="chip">{VERD[v][0]}</span></div>'
            f'<div class="body"><h3>{q}</h3><p>{body}</p>'
            f'<div class="meta"><span class="fig">{stat}</span>'
            f'<span class="src">{note}.md</span></div></div></article>')
    return "\n".join(out)


def holds_html():
    out = []
    for title, a, b, body, stat in HOLDS:
        glyphs = "".join(gl(x) for x in (a, b) if x is not None)
        out.append(
            f'<div class="hold"><div class="hg">{glyphs or "&nbsp;"}</div>'
            f'<h3>{title}</h3><p>{body}</p>'
            f'<span class="fig">{stat}</span></div>')
    return "\n".join(out)


html = f"""<title>The Indus Ledger</title>
<style>
:root {{
  --ground:#e8ebe6; --panel:#f5f7f3; --sunk:#dfe4dc;
  --ink:#191f1b; --muted:#69726b; --line:#d2d8d0;
  --accent:#2e5c76; --held:#2f6b52; --part:#96682c; --broke:#8a8f88;
  --serif:"Iowan Old Style","Palatino Linotype",Palatino,Georgia,serif;
  --sans:ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif;
  --mono:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
}}
@media (prefers-color-scheme: dark) {{
  :root:not([data-theme="light"]) {{
    --ground:#131813; --panel:#1b211c; --sunk:#10150f;
    --ink:#e5eae3; --muted:#8f988f; --line:#2a312b;
    --accent:#7fb2ce; --held:#69b691; --part:#d6a45e; --broke:#767d76;
  }}
}}
:root[data-theme="dark"] {{
  --ground:#131813; --panel:#1b211c; --sunk:#10150f;
  --ink:#e5eae3; --muted:#8f988f; --line:#2a312b;
  --accent:#7fb2ce; --held:#69b691; --part:#d6a45e; --broke:#767d76;
}}
@font-face {{ font-family:"Indus";
  src:url(data:font/ttf;base64,{b64}) format("truetype"); font-display:block; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; background:var(--ground); color:var(--ink);
  font:16px/1.62 var(--sans); -webkit-font-smoothing:antialiased; }}
.wrap {{ max-width:1010px; margin:0 auto; padding:0 26px; }}
.gl {{ font-family:"Indus"; line-height:1; }}
.miss {{ font-family:var(--mono); font-size:10px; color:var(--part);
  border:1px dashed currentColor; border-radius:3px; padding:0 3px; }}

header {{ padding:70px 0 8px; }}
.eyebrow {{ font:600 11px/1 var(--sans); letter-spacing:.17em;
  text-transform:uppercase; color:var(--accent); margin-bottom:20px; }}
h1 {{ font:400 clamp(34px,5.4vw,50px)/1.06 var(--serif); margin:0 0 18px;
  letter-spacing:-.017em; text-wrap:balance; }}
.lede {{ font:400 19.5px/1.55 var(--serif); color:var(--muted);
  max-width:64ch; margin:0; }}
.stats {{ display:grid; gap:1px; background:var(--line);
  grid-template-columns:repeat(auto-fit,minmax(150px,1fr));
  border:1px solid var(--line); border-radius:3px; overflow:hidden;
  margin:38px 0 0; }}
.stat {{ background:var(--panel); padding:16px 18px; }}
.stat b {{ display:block; font:600 27px/1 var(--mono);
  font-variant-numeric:tabular-nums; }}
.stat span {{ display:block; font-size:12.5px; color:var(--muted);
  margin-top:6px; }}

section {{ padding:52px 0; border-top:1px solid var(--line); margin-top:52px; }}
section:first-of-type {{ border-top:0; }}
h2 {{ font:400 28px/1.18 var(--serif); margin:0 0 10px; letter-spacing:-.01em; }}
.sub {{ color:var(--muted); max-width:70ch; margin:0 0 30px; font-size:15.5px; }}

.rules {{ display:grid; gap:14px;
  grid-template-columns:repeat(auto-fit,minmax(226px,1fr)); }}
.rule {{ background:var(--panel); border:1px solid var(--line);
  border-radius:3px; padding:16px 18px; }}
.rule b {{ display:block; font:600 12.5px/1.4 var(--sans); margin-bottom:6px;
  letter-spacing:.01em; }}
.rule span {{ font-size:13.5px; color:var(--muted); line-height:1.5; }}

.row {{ display:grid; grid-template-columns:104px 1fr; gap:22px;
  padding:22px 0; border-bottom:1px solid var(--line); }}
.row:last-child {{ border-bottom:0; }}
.rail {{ display:flex; flex-direction:column; gap:9px; align-items:flex-start; }}
.seq {{ font:600 12px/1 var(--mono); color:var(--muted);
  font-variant-numeric:tabular-nums; }}
.chip {{ font:600 9.5px/1 var(--sans); letter-spacing:.11em;
  text-transform:uppercase; padding:5px 8px; border-radius:2px;
  border:1px solid currentColor; }}
.held .chip {{ color:var(--held); }}
.part .chip {{ color:var(--part); }}
.broke .chip {{ color:var(--broke); }}
.held .body {{ border-left:2px solid var(--held); }}
.part .body {{ border-left:2px solid var(--part); }}
.broke .body {{ border-left:2px solid var(--line); }}
.body {{ padding-left:20px; }}
.body h3 {{ font:400 20.5px/1.3 var(--serif); margin:0 0 8px;
  text-wrap:balance; }}
.body p {{ margin:0 0 12px; font-size:15px; color:var(--ink);
  max-width:68ch; }}
.meta {{ display:flex; gap:14px; flex-wrap:wrap; align-items:baseline; }}
.fig {{ font:600 12px var(--mono); font-variant-numeric:tabular-nums;
  color:var(--accent); }}
.src {{ font:400 11.5px var(--mono); color:var(--muted); }}

.holds {{ display:grid; gap:16px;
  grid-template-columns:repeat(auto-fit,minmax(272px,1fr)); }}
.hold {{ background:var(--panel); border:1px solid var(--line);
  border-radius:3px; padding:20px 20px 18px; display:flex;
  flex-direction:column; }}
.hg {{ font-size:30px; min-height:38px; letter-spacing:6px;
  color:var(--ink); margin-bottom:10px; }}
.hold h3 {{ font:400 18px/1.28 var(--serif); margin:0 0 8px; }}
.hold p {{ margin:0 0 14px; font-size:14px; color:var(--muted);
  line-height:1.55; flex:1; }}

.list {{ border:1px solid var(--line); border-radius:3px; overflow:hidden; }}
.item {{ background:var(--panel); padding:15px 19px;
  border-bottom:1px solid var(--line); }}
.item:last-child {{ border-bottom:0; }}
.item b {{ display:block; font:600 14.5px/1.4 var(--sans); margin-bottom:4px; }}
.item span {{ font-size:14px; color:var(--muted); line-height:1.55; }}

.wall {{ background:var(--sunk); border:1px solid var(--line);
  border-radius:3px; padding:26px 28px; }}
.wall p {{ margin:0 0 12px; font-size:15.5px; max-width:68ch; }}
.wall p:last-child {{ margin-bottom:0; }}
.wall b {{ font-family:var(--mono); font-size:14px; }}

footer {{ padding:44px 0 70px; border-top:1px solid var(--line);
  margin-top:52px; color:var(--muted); font-size:13.5px; }}
footer p {{ max-width:70ch; margin:0 0 9px; }}
@media (max-width:640px) {{
  .row {{ grid-template-columns:1fr; gap:12px; }}
  .rail {{ flex-direction:row; align-items:center; gap:11px; }}
  .body {{ padding-left:14px; }}
}}
</style>

<div class="wrap">
<header>
  <div class="eyebrow">Indus script &middot; investigation record</div>
  <h1>Fifteen ideas, tested against 11,135 signs</h1>
  <p class="lede">A running account of what we tried on the undeciphered Indus
  script, what the data refused, and the handful of structures that held up
  under every control we could think of. Nothing here is a decipherment. Several
  entries are us correcting ourselves.</p>
  <div class="stats">
    <div class="stat"><b>2,543</b><span>inscribed artefacts</span></div>
    <div class="stat"><b>11,135</b><span>sign tokens</span></div>
    <div class="stat"><b>591</b><span>distinct signs</span></div>
    <div class="stat"><b>4.26</b><span>mean signs per line</span></div>
    <div class="stat"><b>34%</b><span>signs seen exactly once</span></div>
  </div>
</header>

<section>
  <h2>The rules we worked under</h2>
  <p class="sub">Most of these were adopted after something went wrong. The
  second one cost us twenty-five findings on the day we introduced it.</p>
  <div class="rules">
    <div class="rule"><b>Epigraphy only</b><span>The source database ships a
      decipherment its field rejects. We took which signs, in what order, on
      which object &mdash; and nothing else.</span></div>
    <div class="rule"><b>Deduplicate first</b><span>Mass-produced tablets repeat
      the same text dozens of times. Left in, they manufacture significance out
      of nothing.</span></div>
    <div class="rule"><b>Control for position</b><span>If one sign likes the
      start and another the end, order follows for free. Every sequence claim is
      tested against a null that keeps those habits.</span></div>
    <div class="rule"><b>Control for site and medium</b><span>Two signs from
      different cities never meet for reasons that have nothing to do with
      grammar.</span></div>
    <div class="rule"><b>Report the failures</b><span>Most of this page is
      negative results. A hypothesis that dies cleanly is worth more than one
      that survives on a technicality.</span></div>
  </div>
</section>

<section>
  <h2>The ledger</h2>
  <p class="sub">In order. Each idea came out of the one before it, which is why
  the sequence matters &mdash; and why one entry retracts an earlier one.</p>
  {ledger_html()}
</section>

<section>
  <h2>What held up</h2>
  <p class="sub">Findings that survived deduplication, positional controls, and
  stratification by site and object class.</p>
  <div class="holds">{holds_html()}</div>
</section>

<section>
  <h2>Where we were wrong</h2>
  <p class="sub">Kept deliberately. Each of these was caught by a later check,
  and the checks are more transferable than the findings.</p>
  <div class="list">
  {"".join(f'<div class="item"><b>{a}</b><span>{b}</span></div>'
           for a, b in CORRECTIONS)}
  </div>
</section>

<section>
  <h2>The wall</h2>
  <div class="wall">
    <p>Every analysis here ends the same way. The corpus has 591 distinct signs
    and <b>the median one appears two or three times</b>. Roughly 495 of the 571
    non-numeral signs are too rare to test at all.</p>
    <p>Collapsing look-alike signs seemed like the obvious escape. It is not
    &mdash; merging mostly combines signs that were <em>already</em> common, and
    the count of testable signs falls from <b>87 to 80</b> rather than rising.</p>
    <p>There is also a floor under the data itself. Two people digitizing the
    same 161 seals from the same photographs agree on <b>93.2%</b> of signs, and
    on one seal in eleven they do not agree how many signs are present. Effects
    smaller than that are noise.</p>
  </div>
</section>

<section>
  <h2>Still open</h2>
  <div class="list">
  {"".join(f'<div class="item"><b>{a}</b><span>{b}</span></div>'
           for a, b in OPEN)}
  </div>
</section>

<footer>
  <p><b>What this is not.</b> No reading, no phonetic values, no language
  assignment. Everything above is distributional: where signs sit, what they
  avoid, and how those patterns change with the object and the city.</p>
  <p>Corpus: 2543 artefacts from the yajnadevam digitization of CISI, epigraphic
  layer only, cross-checked against the mayig / Parpola-numbered corpus. Working
  notes in <span class="src">notes/01&ndash;16</span>.</p>
</footer>
</div>
"""

open("dossier.html", "w").write(
    html.encode("ascii", "xmlcharrefreplace").decode())
print("wrote dossier.html", len(html) // 1024, "KB")
