# Can we get more data?

Script: `src/crosscheck.py`. The binding constraint on every analysis in this
project is that the median sign appears 2–3 times. This is the attempt to fix
that at the source rather than with cleverer statistics.

## What exists

An exhaustive sweep of GitHub and the published literature. Every freely
available Indus corpus traces back to one of two digitizations:

| corpus | size | numbering | status |
|---|---|---|---|
| yajnadevam `population-script.sql` | 2543 artefacts, 11135 tokens | its own (Y) | **in use** |
| mayig / CISI | 179 artefact sides | Parpola (P) | **now joined** |
| glossa-lab | *the same yajnadevam SQL*, re-exported | Y + partial P | crosswalk taken |
| ShaktiOSindia deposit | *the same yajnadevam SQL* | Y | nothing new |
| ramnerd, Kee2u | 556 seqs / no texts at all | — | rejected earlier |

There is exactly one substantially larger corpus, and it is not downloadable:

> **ICIT** (Fuls / Wells, epigraphica.de) — 4660 inscribed artefacts, 5644
> texts, **17957 legible signs**, sign list of 709. Access is by emailing the
> administrator (`fuls@epigraphica.de`).

That is ~1.6x our token count and would meaningfully widen what is testable.
Nothing else would.

## The crosswalk (C1)

glossa-lab published a Y→P mapping derived from the same SQL. We take **only the
id pairs**, never the phonetic readings attached to them.

- 185 of our 591 sign ids get a Parpola number
- those cover **9344 / 11280 tokens (82.8%)**
- **zero ambiguous mappings** — no Y id maps to two different P signs

Validated the same way as the corpus itself: our sign 740, the most frequent
sign and hard against the text end, maps to **P324**. That is Parpola's jar
sign. The map reproduces the anchor without being told to.

Written to `data/parsed/crosswalk.json`. This is what makes published results
citable against our numbering, which `01-corpus.md` listed as an open problem.

## Parpola's allographs vs ours (C2)

Our 185 mapped ids collapse to **153 Parpola signs** — 22 P signs absorb two or
more of our ids. Compared against the 71 families in `data/parsed/families.json`
that we derived ourselves from glyph-id adjacency:

| | |
|---|---|
| merges our grouping already caught | 6 |
| merges we had split apart | **16** |

Two of the misses matter:

- **P385 = our 817 + 861** (314 tokens, both strongly text-initial at .08 and
  .16). These are the signs behind the "2 outranks 1" collocation in
  [05-radix.md](05-radix.md). If they are one sign, that result simplifies.
- **P086 = our 390 + 405 + 406 + 407** (398 tokens). Mean positions .72 and .59
  differ enough to be worth a second look before accepting the merge.

One merge to *reject*: **P145 = our 32 + 600**. Sign 600 has 3 tokens total, so
it cannot disturb the numeral reading of 32.

## Collapsing does not fix scarcity (C2, continued)

The hope was that merging allographs would lift rare signs over the testability
threshold. It does the opposite.

| inventory | signs | hapax | **signs with n≥20** | median count |
|---|---|---|---|---|
| raw ids | 591 | 34% | **87** | 3 |
| + Parpola merges | 559 | 34% | **80** | 3 |
| + our own families | 336 | 32% | **51** | 2 |

Merging combines signs that were *already* frequent far more often than it
rescues rare ones, so the count of testable signs falls. The hapax rate does not
move at all. **Allograph consolidation is not a route around the data ceiling.**

## Two transcriptions of the same seals (C3)

The genuinely new thing available here. 161 artefacts appear in both corpora,
transcribed independently from the same CISI plates. Nobody can measure
digitizer disagreement from one corpus alone.

| | |
|---|---|
| artefacts in both | 161 |
| same number of signs | 146 (**91%**) |
| of those, every mapped sign agrees | 128 (**88%**) |
| sign-level agreement | 725/778 (**93.2%**) |

Reversal was tested and ruled out — 0 artefacts match better in reverse, so the
two corpora share a direction convention and the disagreements are real reading
disputes, not an alignment artefact.

**This is a noise floor for the whole project.** Roughly 1 sign in 14 is read
differently by two careful digitizers, and 1 artefact in 11 is not even assigned
the same number of signs. Some part of that 6.8% is crosswalk error rather than
transcription error, so it is an upper bound on disagreement — but it is the
first empirical error bar we have, and effects near it should be treated as
noise.

Sample disagreements (ours | theirs):

```
M-112  P324 P332 [P050|P056] P126 P111 P325 P285 P254
M-127  P238 P324 [P050|P060] [P325|P324] P194
M-140  P324 P309 [P122|P145] P050 P201 P283 P221
M-173  P324 P110 [P154|P160] P303 P364
```

The confusions cluster: P050/P056/P060 (fish variants), P122/P145, P324/P325.
Digitizers disagree precisely about **which variant of a sign** they are looking
at — the same allograph question that C2 is about, and the same one that makes
34% of the inventory hapax.

## Where this leaves it

- The corpus cannot be grown from public sources. ICIT is the only real option
  and it needs a human to ask for it.
- We gained a validated Parpola crosswalk covering 83% of tokens, which we did
  not have.
- We gained an error bar: **~93% sign-level agreement** between independent
  readings.
- We learned that allograph collapsing, the obvious statistical workaround, does
  not buy testable signs.

## Aside: external corroboration of the fish result

The Parpola material bundled with the crosswalk notes that his numeral signs
(strokes 1–N) are read as compounds *with the fish sign* — 6+fish, 7+fish. We
arrived at numerals attaching to the fish family purely from co-occurrence
statistics ([06-fish.md](06-fish.md), [07-fish-as-operand.md](07-fish-as-operand.md)),
with no knowledge of that reading. The structural claim is independently
attested; his phonetic interpretation of it remains out of scope here.
