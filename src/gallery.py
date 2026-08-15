"""Build a self-contained HTML gallery of the corpus, rendering real Indus glyphs.

The font maps each sign to a Private Use Area codepoint. We embed it as a
data: URI so the page works offline and with no external requests.
"""
import base64
import json
import re
import struct
from collections import Counter
from pathlib import Path

FONT = Path("data/yaj/src/assets/fonts/sk_indus_script-webfont.ttf")
OUT = Path("gallery.html")


def font_codepoints(path):
    """Codepoints present in the font's (3,1) cmap subtable."""
    d = path.read_bytes()
    tabs = {}
    for i in range(struct.unpack(">H", d[4:6])[0]):
        o = 12 + 16 * i
        tabs[d[o:o + 4].decode("latin1")] = struct.unpack(">II", d[o + 8:o + 16])
    off = tabs["cmap"][0]
    sub = None
    for i in range(struct.unpack(">H", d[off + 2:off + 4])[0]):
        pid, eid, so = struct.unpack(">HHI", d[off + 4 + 8 * i:off + 12 + 8 * i])
        if (pid, eid) == (3, 1):
            sub = off + so
    seg2 = struct.unpack(">H", d[sub + 6:sub + 8])[0]
    seg = seg2 // 2
    ends = [struct.unpack(">H", d[sub + 14 + 2 * i:sub + 16 + 2 * i])[0] for i in range(seg)]
    starts = [struct.unpack(">H", d[sub + 16 + seg2 + 2 * i:sub + 18 + seg2 + 2 * i])[0]
              for i in range(seg)]
    return {c for s, e in zip(starts, ends) if e != 0xFFFF for c in range(s, e + 1)}


have = font_codepoints(FONT)
glyphs = json.loads(Path("data/parsed/glyphs.json").read_text())
cp = {g["glyph_id"]: int(re.sub(r"[^0-9A-Fa-f]", "", g["unicode"]), 16)
      for g in glyphs if str(g["unicode"]).startswith("&#x")}

seals = json.loads(Path("data/parsed/inscriptions.json").read_text())
sites = json.loads(Path("data/parsed/sites.json").read_text())

tokens = renderable = 0
for s in seals:
    for g in s["glyphs"]:
        if g == 0:
            continue
        tokens += 1
        renderable += cp.get(g) in have
print(f"token coverage by font: {renderable}/{tokens} = {renderable/tokens:.1%}")

b64 = base64.b64encode(FONT.read_bytes()).decode()

records = []
for s in seals:
    # stored left-to-right on the object; render in reading order (right-to-left)
    signs = [g for g in s["glyphs"] if g != 0]
    if s.get("direction") != "L/R":
        signs = signs[::-1]
    records.append({
        # 168 artifacts carry no CISI id; fall back to the database key
        "id": s["cisi"] or f"#{s['seal_id']}", "site": sites.get(s.get("site"), "?"),
        "cls": s.get("obj_class") or "?", "code": s.get("obj_code") or "?",
        "mat": s.get("material") or "?", "motif": s.get("motif") or "unrecorded",
        "n": len(signs),
        "g": [[g, cp.get(g, 0) if cp.get(g) in have else 0] for g in signs],
    })

facets = {
    "cls": Counter(r["cls"] for r in records),
    "site": Counter(r["site"] for r in records),
    "motif": Counter(r["motif"] for r in records),
}


def opts(key, label):
    o = "".join(f'<option value="{k}">{k} ({v})</option>'
                for k, v in facets[key].most_common())
    return f'<label>{label}<select data-k="{key}"><option value="">all</option>{o}</select></label>'


html = f"""<title>Indus Corpus Browser</title>
<style>
:root {{
  --bg:#faf8f5; --panel:#fff; --ink:#1c1917; --dim:#78716c; --line:#e7e2da;
  --accent:#9a6a3c;
}}
:root:not([data-theme="light"]) {{ }}
@media (prefers-color-scheme: dark) {{
  :root:not([data-theme="light"]) {{
    --bg:#17150f; --panel:#211e17; --ink:#f0ebe2; --dim:#a8a096; --line:#332f26;
    --accent:#d3a06a;
  }}
}}
:root[data-theme="dark"] {{
  --bg:#17150f; --panel:#211e17; --ink:#f0ebe2; --dim:#a8a096; --line:#332f26;
  --accent:#d3a06a;
}}
@font-face {{
  font-family:"Indus"; src:url(data:font/ttf;base64,{b64}) format("truetype");
  font-display:block;
}}
* {{ box-sizing:border-box; }}
body {{
  margin:0; background:var(--bg); color:var(--ink);
  font:15px/1.5 ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif;
}}
header {{ padding:28px 24px 16px; max-width:1200px; margin:0 auto; }}
h1 {{ font-size:22px; margin:0 0 4px; letter-spacing:-.01em; }}
.sub {{ color:var(--dim); font-size:14px; }}
.bar {{
  position:sticky; top:0; z-index:5; background:var(--bg);
  border-bottom:1px solid var(--line); padding:12px 24px;
}}
.bar-in {{ max-width:1200px; margin:0 auto; display:flex; gap:14px;
  flex-wrap:wrap; align-items:center; }}
label {{ font-size:12px; color:var(--dim); display:flex; gap:6px; align-items:center; }}
select,input {{
  font:inherit; font-size:13px; padding:5px 8px; border:1px solid var(--line);
  border-radius:6px; background:var(--panel); color:var(--ink); max-width:230px;
}}
#count {{ margin-left:auto; font-size:13px; color:var(--dim); }}
main {{ max-width:1200px; margin:0 auto; padding:20px 24px 60px;
  display:grid; gap:12px; grid-template-columns:repeat(auto-fill,minmax(310px,1fr)); }}
.card {{
  background:var(--panel); border:1px solid var(--line); border-radius:10px;
  padding:14px 16px; display:flex; flex-direction:column; gap:10px;
}}
.txt {{
  font-family:"Indus"; font-size:38px; line-height:1.35; direction:rtl;
  overflow-x:auto; white-space:nowrap; padding-bottom:2px;
}}
.txt .miss {{
  font-family:ui-monospace,monospace; font-size:11px; color:var(--accent);
  border:1px dashed var(--accent); border-radius:4px; padding:1px 3px;
  vertical-align:middle;
}}
.meta {{ font-size:12px; color:var(--dim); display:flex; flex-wrap:wrap; gap:4px 10px; }}
.meta b {{ color:var(--ink); font-weight:600; }}
.tag {{ font-size:11px; border:1px solid var(--line); border-radius:99px;
  padding:1px 8px; color:var(--dim); }}
.note {{ max-width:1200px; margin:0 auto; padding:0 24px 40px;
  color:var(--dim); font-size:13px; line-height:1.6; }}
.note code {{ font-size:12px; }}
</style>

<header>
  <h1>Indus Corpus Browser</h1>
  <div class="sub">{len(records)} inscribed objects &middot; rendered right-to-left in reading order</div>
</header>

<div class="bar"><div class="bar-in">
  {opts("cls", "object")}
  {opts("site", "site")}
  {opts("motif", "motif")}
  <label>id <input id="q" placeholder="e.g. M-178" size="10"></label>
  <label>min signs <input id="minn" type="number" value="0" min="0" max="20" size="3" style="width:60px"></label>
  <span id="count"></span>
</div></div>

<main id="grid"></main>

<div class="note">
Glyphs are drawn with the <code>sk_indus_script</code> font, which covers
{renderable/tokens:.0%} of sign tokens. Signs the font has no glyph for appear as
their numeric id in a dashed box. Sign order is reading order (right-to-left);
line breaks within an object are not shown. Motif "unrecorded" means the source
database has no row — for pottery that is usually genuine, for seals it is
usually a gap.
</div>

<script>
const DATA = {json.dumps(records, separators=(",", ":"))};
const grid = document.getElementById('grid'), count = document.getElementById('count');
const sels = [...document.querySelectorAll('select')];
const q = document.getElementById('q'), minn = document.getElementById('minn');

function render() {{
  const f = {{}};
  sels.forEach(s => {{ if (s.value) f[s.dataset.k] = s.value; }});
  const needle = q.value.trim().toLowerCase(), mn = +minn.value || 0;
  const rows = DATA.filter(r =>
    Object.entries(f).every(([k, v]) => r[k] === v) &&
    r.n >= mn &&
    (!needle || r.id.toLowerCase().includes(needle)));
  count.textContent = rows.length + ' of ' + DATA.length;
  grid.innerHTML = rows.slice(0, 400).map(r => {{
    const txt = r.g.map(([id, c]) =>
      c ? '&#x' + c.toString(16).toUpperCase() + ';'
        : '<span class="miss">' + id + '</span>').join('');
    return `<div class="card">
      <div class="txt">${{txt}}</div>
      <div class="meta">
        <b>${{r.id}}</b><span class="tag">${{r.code}}</span>
        <span>${{r.site}}</span><span>${{r.mat}}</span>
        <span>${{r.motif}}</span><span>${{r.n}} signs</span>
      </div></div>`;
  }}).join('') + (rows.length > 400
    ? '<div class="note">showing first 400 of ' + rows.length + '</div>' : '');
}}
[...sels, q, minn].forEach(e => e.addEventListener('input', render));
render();
</script>
"""

OUT.write_text(html.encode("ascii", "xmlcharrefreplace").decode())
print(f"wrote {OUT}  ({OUT.stat().st_size/1_000_000:.1f} MB)")
