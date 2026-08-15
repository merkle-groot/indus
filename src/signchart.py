"""Render a sign chart: every sign id with its glyph and corpus frequency.

Needed because sign *identity* is only recoverable by eye -- the database gives
numeric ids, not descriptions, so we cannot tell which ids are stroke groups
(the usual numeral candidates) without actually looking at them.
"""
import base64
import json
import re
from collections import Counter

from gallery import font_codepoints, FONT  # reuse cmap parsing

have = font_codepoints(FONT)
glyphs = json.loads(open("data/parsed/glyphs.json").read())
cp = {g["glyph_id"]: int(re.sub(r"[^0-9A-Fa-f]", "", g["unicode"]), 16)
      for g in glyphs if str(g["unicode"]).startswith("&#x")}

lines = json.loads(open("data/parsed/lines.json").read())
freq = Counter(g for l in lines for g in l["signs"])

b64 = base64.b64encode(FONT.read_bytes()).decode()
cells = []
for g, c in freq.most_common():
    code = cp.get(g)
    glyph = (f"&#x{code:X};" if code in have
             else '<span class="x">no glyph</span>')
    cells.append(f'<div class=c><div class=g>{glyph}</div>'
                 f'<div class=i>{g}</div><div class=f>{c}</div></div>')

html = f"""<title>Indus Sign Chart</title>
<style>
@font-face {{ font-family:Indus; src:url(data:font/ttf;base64,{b64}) format("truetype"); }}
body {{ background:#fff; color:#111; margin:0; padding:16px;
  font:12px ui-sans-serif,system-ui,sans-serif; }}
h1 {{ font-size:15px; margin:0 0 12px; }}
.grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(74px,1fr)); gap:6px; }}
.c {{ border:1px solid #ddd; border-radius:6px; padding:6px 2px; text-align:center; }}
.g {{ font-family:Indus; font-size:30px; line-height:1.25; height:40px; }}
.i {{ font-weight:700; font-size:11px; }}
.f {{ color:#888; font-size:10px; }}
.x {{ font-family:sans-serif; font-size:9px; color:#c00; }}
</style>
<h1>Indus signs by corpus frequency &mdash; id (bold) and token count</h1>
<div class=grid>{''.join(cells)}</div>
"""
open("signchart.html", "w").write(html.encode("ascii", "xmlcharrefreplace").decode())
print(f"wrote signchart.html  ({len(freq)} signs)")
