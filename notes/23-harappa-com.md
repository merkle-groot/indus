# harappa.com, and independent confirmation of the terminal slot

## Access

The site is behind Cloudflare and returns **403** to both `curl` and ordinary
programmatic fetching. I did not drive a browser at it to get around that.

The Internet Archive mirrors it publicly, which is a legitimate route, so the
survey below is from there: **27,069 archived URLs, ~6,300 unique after
stripping query strings.**

## What is actually there

Almost nothing structured. The archive breaks down as ~4,600 article pages,
~3,100 category listings, several hundred blog posts, and large photo-essay
collections. There is:

- **no sign list**
- **no machine-readable corpus**
- **no catalogue of artefact images indexed by CISI id** — the handful of URLs
  that look like `M-xxxx` are malformed crawler artefacts, concatenated URLs

So it does not help with the eleven missing CISI plates from
[20-composites.md](20-composites.md), which was the main hope.

Two content pages are directly relevant: `/content/fish-sign` and
`/content/arrow-sign`, both interview material with **Iravatham Mahadevan**.
Text saved locally to `data/harappa/` and **gitignored** — it is someone else's
copyrighted writing and does not belong in this repo.

## The arrow-sign page confirms our strongest result

[12-slots.md](12-slots.md) found, from co-occurrence statistics alone:

> Signs **740** and **520** appear together 6 times where chance predicts 90.
> **z = −14.19**, and −12.4 / −12.6 after controlling for site and object class.

Mahadevan, discussing the same two signs qualitatively, says the jar sign and
the arrow sign are *"generally mutually exclusive"*.

The identification is secure on the glyphs. Rendered at 300px, **740 is a
vessel with two handles** — the jar sign, already the corpus's validation anchor
([01-corpus.md](01-corpus.md)) — and **520 is a shaft with a triangular head**,
an arrow or lance. Both are text-final: 740 ends 72% of the texts it appears in,
520 ends 84%.

This is the first time anything in this project has been independently
corroborated by the literature. It was derived here from a different corpus,
with deduplication and stratified controls, by a route that had no knowledge of
the claim.

### What we add to it

Mahadevan states the exclusivity as an observation and says plainly that no one
has hard evidence about what these signs mean. The contribution here is that the
exclusivity itself is now **measured**: 6 observed against 90 expected, holding
after controlling for text length, site and object class.

And the project's framing differs. Mahadevan reads the pair as two grammatical
suffixes that are "integrally connected". [12-slots.md](12-slots.md) reads them
as two fillers of one **terminal slot** — which is the same observation with a
different emphasis, and it generalises: 390, 151, 527, 617 and 156 also exclude
740 significantly. It is a paradigm with at least seven members, not a pair.

### Two smaller points

- He reasons *from* the exclusivity **against** Parpola's genitive/dative
  reading: if they were case endings, the same name should sometimes take
  either. That is the same logic as a slot holding one value, arrived at from
  grammar rather than statistics.
- He suggests a sign depicting a plain standing man may denote a servant. Sign
  **90** is a standing human figure, and it is one of the two signs
  [12-slots.md](12-slots.md) found sitting *behind* the jar rather than
  competing with it (after 740 in 62 of 69 co-occurrences). Nothing here tests
  his reading; the positional fact is just worth recording next to it.

## The fish page

Historical background on the Dravidian *meen* = fish = star rebus, from Heras
through Parpola. It is decipherment argument, which this project excludes by
rule ([01-corpus.md](01-corpus.md)), and it adds no counts or distributional
claims. Noted and not imported.

It does not bear on [06-fish.md](06-fish.md) or
[07-fish-as-operand.md](07-fish-as-operand.md), whose findings — that the fish
family takes numeric coefficients and that a *marked* fish never takes one above
3 — are distributional and independent of what the sign depicts.

## Verdict

As a data source, **nothing**. As corroboration, one genuinely valuable hit: the
strongest statistical result in this project restates, in measured form, an
exclusivity that the field's leading epigrapher had already noticed and could
not quantify.

## The bulk harvest: one substantive lead, which then failed

`src/scrape_harappa.py` pulled ~340 pages via the archive. The naive keyword
ranking is dominated by boilerplate — every `/articles/NNNN` URL returns the
same listing template, and `CHANGELOG.txt` tops the list because Drupal's
changelog says "script" 56 times. After dropping repeated templates, 115 pages
remain and only a handful are substantive. They are Q&A pages, mostly with
Mahadevan.

One is directly on our subject. Asked about Brian Wells's volumetric reading of
certain signs, Mahadevan rejects it, and adds the detail that matters here:
groups of vertical strokes stand for ones — *but not all of them* — and groups
of **semicircles probably stand for tens**.

### The semicircle series exists

Rendering the 900 block turns up exactly that series:

| sign | shape | tokens (dedup) |
|---|---|---|
| 900 | one arc | 60 |
| 904 | two arcs | 30 |
| 918 | three arcs | 1 |
| 914 | four arcs | 1 |
| 908 | five arcs | 2 |

The "but not all of them" caveat also matches
[16-twelve.md](16-twelve.md), where several stroke signs turned out not to
behave as numerals.

### And they take what looks like a multiplier

| | preceded by a unit numeral | p vs base |
|---|---|---|
| base rate, any sign | 1426/7028 = **20.3%** | — |
| **sign 900** | **27/50 = 54%** | **1.5e-07** |
| **sign 904** | **11/25 = 44%** | **6.2e-03** |

And the preceding value *varies* — for 900 it runs 1, 2, 3, 4, 5, with no single
value dominating. That is unlike the frozen pairs in
[22-two-forms-of-two.md](22-two-forms-of-two.md), where 817 takes the value two
102 times out of 120. A variable small multiplier before a unit is what a tens
sign should look like, and `[3][900]` occurs 12 times.

This looked like the higher-unit symbol that [05-radix.md](05-radix.md) went
looking for and failed to find — because it only searched among stroke signs.

### The control refutes it

A counted **noun** also sits after a numeral. So: how does 54% compare with
other signs?

| sign | preceded by a numeral |
|---|---|
| 585 | 64% |
| 700 | 63% |
| 4 | 57% |
| **900** | **54%** |
| 61 | 51% |
| 803 | 50% |
| **904** | **44%** |
| 220 (a fish) | 44% |

**900 is unremarkable.** Three signs beat it, and the fish sign 220 — a thing
that is plainly counted rather than a unit of measure — sits at the same rate on
four times the data. The variability of the multiplier is not distinctive
either: sign 405 is more evenly spread (top value only 33%) than 900 (44%).

Two further checks go the wrong way as well. A tens-unit should be followed by
the thing being counted; sign 900 is followed by **740, the terminal jar sign,
21 times of 60**, and sits in the last two slots of its text 47% of the time.
That is the position of a counted item inside the formula, not of a modifier
attached to one.

**Verdict: not supported.** The distribution cannot separate "three tens" from
"three of some thing", and on every discriminating check 900 patterns with the
things rather than with the numbers. Mahadevan's reading may still be right —
it rests on shape and on comparative argument, neither of which this corpus can
test — but nothing here supports it, and the apparent multiplier signal is an
artefact of not having run the control.

Noting for the record that the 54%-versus-20% comparison looked convincing
until the right baseline was applied. That is the same error as
[21-frame-family.md](21-frame-family.md), caught earlier this time.

## Incidental: the font's provenance

The search also settled where our glyphs come from. The Indus Script Font is a
Private Use Area font built by the **National Fund for Mohenjo-daro** from
**Parpola's** corpus, released February 2017, ~1,800 signs. Our
`sk_indus_script-webfont.ttf` has 2,003 glyphs in the PUA range E0xx–E7xx.

So the shapes this project has been rendering, counting strokes on, and
comparing pixel-by-pixel are Parpola's sign forms. That is worth knowing: it
means the glyph evidence and the Parpola crosswalk in
[10-more-data.md](10-more-data.md) are **not independent sources**. Where they
agree, that agreement is weaker than it looked.
