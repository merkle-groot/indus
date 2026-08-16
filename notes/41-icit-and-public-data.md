# The ICIT corpus, our numbering, and two external checks

Script: `src/icit_align.py`. This note does three things: it records what of the
larger Indus corpus is actually obtainable, it shows that **our sign numbering
is ICIT's** (which resolves an open question from [10-more-data.md](10-more-data.md)
and extends the non-independence warning of [23-harappa-com.md](23-harappa-com.md)),
and it ingests two external sources that bear directly on this project's
findings. No new decipherment content; the house rules ([01-corpus.md](01-corpus.md))
still hold.

## The data-access map

The recurring hope in these notes has been more data — the wall is 11135 tokens
([10-more-data.md](10-more-data.md)). The honest state of what is reachable:

| source | size | status |
|---|---|---|
| **our corpus** (Yajnadevam) | 2376 artefacts | in hand |
| **ICIT** (Wells/Fuls) | 4660 artefacts, 5644 texts, 17957 signs | **request-gated**; live DB returns 401 |
| ICIT documentation (Fuls 2010) | 16 pp methodology | **public**, retrieved |
| Nair 2026 scorecard (arXiv 2604.17828) | analysis of our corpus | **public**, retrieved |
| Mahadevan 1977 concordance + CISI vols 1–2 | ~3700 artefacts | on archive.org, but **OCR of a custom sign font is unusable** for sequences |
| CISI vol 3; Kanmer material | recent finds | academia.edu, **login-walled (403)** |
| Fuls books | — | for sale only |

The live ICIT database at `indus.epigraphica.de` is behind HTTP auth and was not
touched. Access is by request to the administrator; that request is the only
legitimate route and it is outstanding. Retrieved files are gitignored under
`data/external/icit/` with provenance, per the [23-harappa-com.md](23-harappa-com.md)
convention for third-party copyrighted material.

The blunt finding: **every openly downloadable "Indus corpus" resolves to the one
we already have.** The Mahadevan and CISI plates are public but image-based, and
their OCR renders the Indus sign font as garbage — extracting texts from them is a
vision task, not a download. The genuinely new material (ICIT proper, CISI vol 3,
recent excavations) is either gated or unscanned.

## Our numbering is ICIT's — the decisive test

[10-more-data.md](10-more-data.md) left the provenance of the Yajnadevam sign
numbering partly open, crosswalking it to Parpola. The ICIT documentation prints
worked examples in Bryan Wells's 3-digit codes, including one testable quantitative
claim: the sign cluster **400-740-176 "occurs 36 times on TAB:B, TAB:C and TAB:I
from Harappa."**

If our numbering is the same enumeration, that cluster should appear about 36 times
in our corpus, concentrated on Harappa tablets — but **mirror-reversed**, because
ICIT prints texts with the initial sign on the left while our `lines.json` stores
the opposite orientation (the direction question of [27-direction.md](27-direction.md)).

| | ICIT (Fuls doc) | ours, reversed as `176-740-400` |
|---|---|---|
| occurrences | 36 | **37** |
| dominant site | Harappa | **Harappa (35 of 37)** |
| dominant object | tablets (TAB) | **tablets (32 of 37)** |

The match is exact within transcription noise, and it only works after reversal.
A second documented cluster, `033-705`, appears **72 times** in our corpus as
`705-033`. Two independent facts follow:

1. **The sign identities are shared, not independent.** Yajnadevam's numbers are
   Wells's ICIT glyph codes. Nair 2026 states this directly — the corpus "uses the
   ICIT glyph numbering system (G### prefix)". So `740` is ICIT's jar and `520` is
   ICIT's arrow *by construction*, not by convergence.
2. **Our corpus is a mirror-stored subset of the ICIT/CISI corpus.** The same
   physical Harappa tablets are in both.

This is the same category of catch as [23-harappa-com.md](23-harappa-com.md), where
the glyphs turned out to be Parpola's forms: where our sign evidence agrees with
ICIT's, that agreement is **weaker than it looks**, because it is not a second
source. Two of the doc's individual multi-sign seal texts do not appear in our
corpus even reversed — expected, since we hold roughly half of ICIT's artefacts.

## What the ICIT documentation independently corroborates

Sign *identity* is shared, so it cannot corroborate anything. Sign *method* and
*distributional structure* can, and here the convergence is real because Wells and
Fuls arrived at it separately and earlier.

- **A terminal-position sign class.** ICIT assigns signs to functions including
  **TMK (Terminal Marker)** and **ITM (Initial Cluster Terminal Marker)**, and its
  structure-analysis tool searches "before or after one or more Terminal Marker(s)".
  This is the terminal slot of [12-slots.md](12-slots.md), reached from the other
  direction. Their worked examples use 520 and 740 as the terminal markers — the
  exact pair this project found excluding each other at z = −14.
- **Deduplication.** ICIT has a switch to "remove identical texts, thereby
  eliminating the so-called TAB-effect." That is rule 2 of this project
  ([01-corpus.md](01-corpus.md)) under a different name — mass-produced tablets
  manufacturing significance — independently recognised as a thing you must control.
- **Frozen sign clusters.** ICIT's "sign cluster analysis" counts repeating
  sequences as candidate words; `400-740-176` at 36× is exactly the kind of frozen
  collocation this project found in [22-two-forms-of-two.md](22-two-forms-of-two.md).

Three of this project's core moves — a terminal slot, dedup-before-analysis, and
frozen collocations — were already present in a 2006–2010 database built by other
people. That is corroboration of *method*, and it is worth more than the numeric
agreement, which is circular.

## Nair 2026: the emblem hypothesis, tested on our corpus

The arXiv scorecard (Nair, April 2026) runs on the same 1916-text corpus and asks
the exact skeptical question — is this a non-linguistic emblem or administrative
system? — by scoring the four Farmer–Sproat–Witzel properties against two synthetic
non-linguistic generators. Its own key table:

| FSW property | Indus | heraldic gen. | admin gen. | vs heraldic | vs admin |
|---|---:|---:|---:|:--:|:--:|
| mean length | 4.42 | 4.01 | 4.02 | discriminates | not |
| repeated phrases ≥3 | 565 | 310 | 339 | discriminates | not |
| repeated phrases ≥6 | 11 | 2.3 | 0.18 | discriminates | discriminates |
| hapax rate | 0.33 | 0.10 | 0.44 | discriminates | discriminates |
| positional rigidity (V) | 0.15 | 0.08 | 0.23 | discriminates | discriminates |

The Indus corpus sits **between** the two baselines and matches neither cleanly:
the heraldic model fails on formulaic repetition, the administrative model fails on
hapax rate (33% vs ~44%) and positional rigidity (0.15 vs ~0.23). Their conditional
entropy result — observed 3.232 bits against a within-inscription shuffle null of
4.613, below all 1000 shuffles — is our no-repeat / positional-structure result
([09-music.md](09-music.md), [12-slots.md](12-slots.md)) in another currency.

Two things to hold onto. First, this is a genuinely external test of the "fancy
random stamps / emblems" reading: a heraldic generator tuned to match Indus
frequency and positional structure still cannot reproduce its repetition profile.
Second, Nair repeats the caveat this project also lives by, citing Sproat: a
corpus more ordered than chance proves structure, **not language**. Their scorecard
narrows what the system is *not* — not cleanly heraldic, not cleanly administrative,
not random — without reaching what it *is*.

## What this changes for getting ICIT

Because ICIT shares our numbering, integrating it would need **no crosswalk** — the
worry in [10-more-data.md](10-more-data.md) about merging transcription traditions
is smaller than feared for this particular source. The gain from the full 4660
artefacts is not primarily statistical power (doubling N buys ~√2 on a z-score and
does not move the wall, since the median sign stays rare) but **stratification**:
[14-object-forms.md](14-object-forms.md) and [15-city-forms.md](15-city-forms.md)
could only test two cities. ICIT's Dholavira, Lothal and Kalibangan material in
quantity would let "is the form uniform across the civilisation?" be asked properly
instead of as a two-city comparison.

## What this does not license

The numbering identity means our glyph evidence is not independent of ICIT or, one
step back, of Parpola. Nothing here reads a sign. The ICIT terminal-marker labels
(TMK, ITM, LOG) are *their* preliminary functional guesses and were not imported;
only the distributional fact of a terminal position, which this project measured on
its own, is claimed. Nair's scorecard is external corroboration of structure, not of
meaning, and its synthetic generators are its authors' own stress-test baselines,
not attested systems — as they themselves flag. The comparison rules out two
non-linguistic models; it does not establish a linguistic one.
