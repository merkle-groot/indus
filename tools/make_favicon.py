"""Favicon from the Indus fish sign (220, U+E10A).

Pulls the glyph outline straight out of the site's font, so the icon is the
same shape the page renders. Writes an SVG (theme-aware) plus PNG fallbacks.

    python3 tools/make_favicon.py
"""
import pathlib

from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parents[1]
FONT = ROOT / "site" / "fonts" / "indus.ttf"
OUT = ROOT / "site"

FISH = 0xE10A          # sign 220, the plain fish
BOX = 64               # svg viewBox
PAD = 7                # breathing room inside the box
INK = "#15171b"
PAPER = "#ffffff"
INK_DARK = "#e8eae2"   # the fish on a dark tab strip


def glyph_path():
    font = TTFont(FONT)
    name = font.getBestCmap()[FISH]
    glyphs = font.getGlyphSet()

    bounds = BoundsPen(glyphs)
    glyphs[name].draw(bounds)
    x0, y0, x1, y1 = bounds.bounds

    pen = SVGPathPen(glyphs)
    glyphs[name].draw(pen)
    d = pen.getCommands()

    scale = (BOX - 2 * PAD) / max(x1 - x0, y1 - y0)
    tx = PAD + ((BOX - 2 * PAD) - (x1 - x0) * scale) / 2 - x0 * scale
    ty = PAD + ((BOX - 2 * PAD) - (y1 - y0) * scale) / 2 + y1 * scale
    return d, f"translate({tx:.2f} {ty:.2f}) scale({scale:.5f} -{scale:.5f})"


def write_svg(d, transform):
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {BOX} {BOX}">
<style>
  path{{fill:{INK}}}
  @media (prefers-color-scheme:dark){{path{{fill:{INK_DARK}}}}}
</style>
<path transform="{transform}" d="{d}"/>
</svg>
'''
    (OUT / "favicon.svg").write_text(svg)


def write_png(name, size, bg, fg, pad_ratio=0.16):
    img = Image.new("RGBA", (size, size), bg)
    draw = ImageDraw.Draw(img)
    pt = size
    while pt > 4:
        font = ImageFont.truetype(str(FONT), pt)
        x0, y0, x1, y1 = draw.textbbox((0, 0), chr(FISH), font=font)
        if max(x1 - x0, y1 - y0) <= size * (1 - 2 * pad_ratio):
            break
        pt -= 1
    draw.text(((size - (x1 - x0)) / 2 - x0, (size - (y1 - y0)) / 2 - y0),
              chr(FISH), font=font, fill=fg)
    img.save(OUT / name)


if __name__ == "__main__":
    d, transform = glyph_path()
    write_svg(d, transform)
    write_png("favicon-32.png", 32, (0, 0, 0, 0), INK)
    write_png("apple-touch-icon.png", 180, PAPER, INK, pad_ratio=0.20)
    for f in ("favicon.svg", "favicon-32.png", "apple-touch-icon.png"):
        print(f"{f:24} {(OUT / f).stat().st_size:>7,} bytes")
