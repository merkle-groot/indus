# Indus script — a distributional investigation

Twenty rounds of hypothesis-testing against the corpus of Indus inscriptions.
**This is not a decipherment.** There are no phonetic values here and no language
assignment. Everything is distributional: where signs sit, what they avoid, and
how those patterns shift with the object and the city.

Most of it is negative results. That is the point.

Start with **[notes/](notes/)**, in order — each round came out of the one
before it, and one of them retracts an earlier conclusion.

## What survived

| finding | |
|---|---|
| A **terminal slot** holding exactly one sign. 740 and 520 share a text 6 times where chance predicts 90. | z = −14.2 |
| A **second position behind it** — 400 follows 740 in 91 of 109 co-occurrences, so "ends the text" and "fills the last slot" are different things. | |
| **Texts do not reuse a sign**, far below chance, adjacent or not. | z = −19.1 |
| **Seals and tablets** share a layout and fill the last field differently. | p = 1e-14 |
| **One form across the civilisation** — Mohenjo-daro and Harappa seal endings are indistinguishable. | p = 0.98 |
| Stroke signs are numerals: values 1–9, then a **spike at twelve**. | p = 1.4e-45 |

## Method

Five rules, most adopted after something went wrong:

1. **Epigraphy only.** The source database ships a decipherment its field
   rejects. Only which signs, in what order, on which object were taken.
2. **Deduplicate first.** Mass-produced tablets repeat the same text dozens of
   times. Left in, they manufacture significance — this cost 25 findings the
   day it went in.
3. **Control for position.** If one sign prefers the start and another the end,
   ordering follows for free.
4. **Control for site and object class.** Two signs from different cities never
   meet for reasons that have nothing to do with grammar.
5. **Report the failures.**

## Setup

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt

# source corpora (gitignored — clone them yourself)
git clone https://github.com/yajnadevam/indus-website           data/yaj
git clone https://github.com/mayig/indus-valley-script-corpus   data/cisi

.venv/bin/python3 src/parse_yaj.py     # -> data/parsed/
.venv/bin/python3 src/eda.py
```

Two further corpora were evaluated and rejected (see
[notes/01-corpus.md](notes/01-corpus.md)); clone them only to reproduce that
assessment:

```bash
git clone https://github.com/ramnerd/IVC_script_decoded                    data/IVC_script_decoded
git clone https://github.com/Kee2u/Deciphering_the_Indus_Valley_Script     data/Deciphering_the_Indus_Valley_Script
```

`data/parsed/` is committed, so the analysis scripts run without the clones.
The corpus itself needs `data/yaj` for the font.

## Layout

```
notes/     the investigation, 01-20, in order
src/       one script per question, named after it
data/parsed/   derived JSON: lines, glyphs, sites, merges, crosswalks
*.html     generated report pages
```

## The wall

591 distinct signs, and **the median one appears two or three times**. Roughly
495 of the 571 non-numeral signs are too rare to test. Collapsing look-alikes
does not fix it. And two people digitizing the same 161 seals agree on only
**93.2%** of signs — effects smaller than that are noise.

The one thing that would help is [ICIT](https://www.epigraphica.de/) (4660
artefacts, 17957 signs), which is not downloadable.

## Provenance and licence

The epigraphic data derives from
[yajnadevam/indus-website](https://github.com/yajnadevam/indus-website)
(GPL-3.0); `data/parsed/` is a transformation of it and inherits that licence.
Sign numbering is that database's own, not Mahadevan's or Parpola's — see
[notes/10-more-data.md](notes/10-more-data.md) for the crosswalk.
