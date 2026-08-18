# site/

The public write-up: all 41 rounds, what each one asked, and what came through
the controls. One self-contained static page.

```
site/
  index.html      the whole site: markup, styles, and the round data inline
  fonts/indus.ttf the Indus Script Font (PUA E0xx-E7xx), used to render real signs
```

Round summaries live in the `ROUNDS` array near the bottom of `index.html`.
Each entry is `{n, t, tag, q, a, stat?, signs?, file}`; `tag` drives the rail
colour, the outcome map in the hero, and the filter chips, whose counts
recompute themselves. `signs` holds HTML entities for PUA codepoints, which come
from `data/parsed/glyphs.json` (`glyph_id` to `unicode`).

## Local preview

```bash
cd site && python3 -m http.server 8712    # http://localhost:8712
```

## Deploy

`vercel.json` at the repo root points Vercel at this directory, so a plain
`vercel --prod` from the repo root ships it. No build step, no dependencies.

To deploy this folder on its own instead, run `vercel --prod` from inside
`site/` and delete the `outputDirectory` line from the root config.

## Font

`fonts/indus.ttf` is `sk_indus_script-webfont.ttf` from
[yajnadevam/indus-website](https://github.com/yajnadevam/indus-website), the
Indus Script Font the National Fund for Mohenjo-daro built from Parpola's sign
forms. It's copied here so the page stays self-contained.
