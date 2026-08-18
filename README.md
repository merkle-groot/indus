# Indus script — a distributional investigation

Forty core rounds of hypothesis-testing against the corpus of Indus inscriptions,
plus provenance follow-ups.
**This is not a decipherment.** There are no phonetic values here and no language
assignment. Everything is distributional: where signs sit, what they avoid, and
how those patterns shift with the object and the city.

Most of it is negative results. That is the point.

Start with **[notes/](notes/)**, in order — each round came out of the one
before it, and one of them retracts an earlier conclusion.

## What survived

| finding | |
|---|---|
| A **terminal cohort**, with one transcription-robust exclusion anchor. The seven fixed signs end 1,179/2,086 texts against 400 expected by within-text position shuffle; 740/520 occur together 6 times against 27.7 under the exact-position/site/object null. | finality z = +47.5; pair z = −5.45 |
| The terminal construction can **float left when 400 or 90 follows it**. There is no general absolute −2 slot and no dense, fully robust exclusion clique. | −2 cohort: 0/33 BH exclusions |
| **Texts do not reuse a sign**, far below the exact-position/site/object control. The effect survives every transcription-noise draw. | z = −14.85; noise 95% −14.17 to −10.03 |
| **Seals and tablets** share a layout and fill the last field differently. | p = 1e-14 |
| **One form across the civilisation** — Mohenjo-daro and Harappa seal endings are indistinguishable. | p = 0.98 |
| Stroke signs are numerals: values 1–9, then a **spike at twelve**. | p = 1.4e-45 |
| **Numeral side is sign-specific**, not universally fixed. Global overdispersion survives exact position/site/object control and transcription noise. | controlled z = +16.09; noise 95% +10.62 to +15.82 |
| Dependency is mostly local but **MI remains above an exact-bigram surrogate at distances 2–4**. Distances 5–6 do not survive the controlled reading. | excess 0.052–0.078 bits, BH |
| The merged inventory is **not saturated**: 515 identifiable observed types after removing database unknown markers, with Chao1 ≈715 and ACE ≈695. | centered bootstrap 95%: 683–756 / 668–727 |
| The public megalithic-graffiti API is a **sign inventory, not a text corpus**. Its shapes are closer to Indus signs than an unrelated Moravian pottery-mark control, but sequence tests are impossible. | base/variant vs control AUC = .739 |
| The four fixed headlines replicate in random halves and disjoint site halves and sit outside pairing-destroyed pipeline nulls. Exploratory seven-sign paradigms have a measurable false-positive cost. | empirical exploratory FPR 7.1% |
| Duplicate texts are mainly **local production data**, but 35% of repeated types reach multiple sites. Copied units remain shorter and vocabulary-poorer after site/object/length controls. | 84.4% of surplus attestations local |

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

`data/parsed/` is committed, so most analysis scripts run without the clones.
The corpus itself needs `data/yaj` for the font. Round 34 downloads pinned
comparison files into gitignored `data/external/`; round 38 needs the independent
`data/cisi` transcription to rebuild its confusion model. Round 40 harvests its
public API, glyphs, and CC-BY control into gitignored `data/graffiti/` with
`python src/scrape_graffiti.py full`.

## Layout

```
notes/     the investigation, 01-40 in order, plus provenance follow-ups
src/       one script per question, named after it
data/parsed/   derived JSON: lines, controls, posteriors, merges, crosswalks
site/      the public write-up: all 41 rounds, one static page
*.html     generated report pages
```

The site in `site/` is self-contained (no build step, no dependencies) and
deploys to Vercel as-is; `vercel.json` points at it. Preview it with
`cd site && python3 -m http.server 8712`.

## The wall

The corrected merged corpus has 527 recorded sign IDs, but twelve are database
markers for “unidentified”; the main identifiable inventory is **515 observed
types**. Of these, roughly **416 identifiable non-numeral signs still have fewer
than 20 tokens**. Partial pooling can assign them shrunken estimates, but it does
not create observations: only three rare signs have finality intervals above the
base rate, two are probably post-terminal additions, and the model fails global
posterior-predictive checks.

Nor is 515 a ceiling. Singleton-sensitive estimators put the merged total near
**695–715**, and the accumulation curve has not plateaued. That makes the wall
larger, not smaller: future data will probably add types as well as tokens.

Two independent digitizers agree on **93.2%** of aligned signs. Propagating that
disagreement leaves the no-repeat effect, terminal cohort, 740/520 anchor, and
global numeral-side result intact, while erasing most marginal pairwise edges.
The wall is now explicit uncertainty rather than a blanket objection: strong
effects clear it; z around −2 to −3 generally does not.

[ICIT](https://www.epigraphica.de/) (4,660 artefacts, 17,957 signs) remains the
only corpus large enough to move the wall materially, but it is request-gated.
The public examples and numbering are not an independent corpus; see
[note 41](notes/41-icit-and-public-data.md).

## Provenance and licence

The primary epigraphic data derives from
[yajnadevam/indus-website](https://github.com/yajnadevam/indus-website)
(GPL-3.0); `data/parsed/` is a transformation of it and inherits that licence.
Its numbering follows the ICIT/Wells-style enumeration rather than Mahadevan's
or Parpola's; see [note 41](notes/41-icit-and-public-data.md) for provenance and
[note 10](notes/10-more-data.md) for the Parpola crosswalk.

Round 34's comparison JSON contains only derived aggregates. The ORACC source
archive declares CC0. The cattle-brand repository states no licence, so its raw
CSV remains gitignored and is not redistributed; full provenance and checksums
are in [note 34](notes/34-known-corpora.md).
