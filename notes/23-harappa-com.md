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
