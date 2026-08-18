"""Draw site/og.jpg, the 1200x630 link-preview card for the write-up.

Run from the repo root: python3 tools/make_og.py
System serif faces plus site/fonts/indus.ttf for the signs; Pillow only.
"""
from PIL import Image, ImageDraw, ImageFont

S = "/System/Library/Fonts/Supplemental/"
W, H = 1200, 630
PAPER = (255, 255, 255)
INK = (21, 23, 27)
INK2 = (84, 86, 92)
RULE = (220, 218, 211)
SPOT = (43, 76, 140)

f_disp   = ImageFont.truetype(S + "Georgia.ttf", 82)
f_lede   = ImageFont.truetype(S + "Times New Roman.ttf", 30)
f_util   = ImageFont.truetype(S + "Arial Narrow.ttf", 22)
f_util_b = ImageFont.truetype(S + "Arial Narrow Bold.ttf", 22)
f_num    = ImageFont.truetype(S + "Georgia.ttf", 40)
f_lbl    = ImageFont.truetype(S + "Arial Narrow.ttf", 20)
f_indus  = ImageFont.truetype("site/fonts/indus.ttf", 74)

img = Image.new("RGB", (W, H), PAPER)
d = ImageDraw.Draw(img)

# faint newsprint ruling
for y in range(0, H, 3):
    d.line([(0, y), (W, y)], fill=(250, 250, 248))

M = 64
def track(draw, xy, text, font, fill, sp=3.2):
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=font, fill=fill)
        x += draw.textlength(ch, font=font) + sp
    return x

# masthead strip
top = 46
track(d, (M, top), "A DISTRIBUTIONAL BROADSHEET", f_util, INK2)
r = "INDUS VALLEY CIVILISATION"
wr = sum(d.textlength(c, font=f_util) + 3.2 for c in r) - 3.2
track(d, (W - M - wr, top), r, f_util, INK2)
d.rectangle([M, top + 38, W - M, top + 41], fill=INK)

# headline
y = top + 84
d.text((M, y), "Indus Valley", font=f_disp, fill=INK)
d.text((M, y + 92), "script analysis", font=f_disp, fill=INK)

# lede
y2 = y + 198
for line in ["Forty-one hypotheses about the Indus script, tested",
             "against the corpus itself. The controls killed most of",
             "them; what’s left is small, and it holds."]:
    d.text((M, y2), line, font=f_lede, fill=INK2)
    y2 += 40

# not-a-decipherment mark
y3 = y2 + 6
d.rectangle([M, y3 + 4, M + 3, y3 + 30], fill=SPOT)
track(d, (M + 16, y3 + 7), "THIS IS NOT A DECIPHERMENT", f_util_b, SPOT, 2.6)

# glyph column, right side
gx = W - M - 300
d.line([(gx - 46, top + 84), (gx - 46, y3 + 32)], fill=RULE)
gy = top + 92
for row in ["", "", ""]:
    d.text((gx, gy), row, font=f_indus, fill=INK)
    gy += 100

# footer stat strip
fy = H - 132
d.line([(M, fy), (W - M, fy)], fill=INK, width=2)
cells = [("2,543", "ARTEFACTS"), ("11,135", "SIGN TOKENS"),
         ("515", "IDENTIFIABLE SIGNS"), ("41", "ROUNDS OF TESTING")]
cw = (W - 2 * M) / 4
for i, (n, lab) in enumerate(cells):
    x = M + i * cw
    if i:
        d.line([(x - 20, fy + 20), (x - 20, fy + 74)], fill=RULE)
    d.text((x, fy + 20), n, font=f_num, fill=INK)
    track(d, (x + 2, fy + 70), lab, f_lbl, INK2, 2.2)

img.convert("RGB").save("site/og.jpg", quality=88, optimize=True, progressive=False)
