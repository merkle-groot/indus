# Is a doubled sign one sign or two?

> **Uncertainty update — see
> [38-transcription-uncertainty.md](38-transcription-uncertainty.md).** The
> 617/740 exact-position exclusion below is marginal: after propagating observed
> sign-identity disagreement its z interval is −2.94 to −0.83 and only 50% of
> draws remain below −1.96. The strong final-position difference between 617
> and 615 remains descriptive; this pairwise exclusion should be labelled
> fragile.

Script: `src/doubled_signs.py`. [20-composites.md](20-composites.md) found that
the font literally encodes 617 as `615 + 615`, 34 as `32 + 32`, and so on. It
did not ask whether the corpus treats those entries as repetitions of the base,
as independent signs, or as derived forms.

The three accounts make different predictions.

| account | same text as base | position and neighbours |
|---|---|---|
| repetition device | depleted by the no-repeat rule | like the base |
| independent sign | no special depletion | unrelated to the base |
| derivational doubling | not necessarily depleted | same broad class, but a changed slot or context |

## Setup and controls

The analysis starts from `lines_merged.json`. Its 2613 lines reduce to **1929
distinct sign sequences**. Site and object tests retain one copy of a sequence
per site or object class, so a text attested in two strata can inform the
control while mass-produced copies inside one stratum cannot.

Four baselines are reported together below:

- Mantel-Haenszel co-occurrence tests stratified separately by text length,
  site, and object class, as in [12-slots.md](12-slots.md)
- an exact-position shuffle: within every text length, each absolute slot is
  shuffled independently; this keeps every sign's observed length-by-position
  profile and destroys only which signs share a text
- position and left/right-neighbour cosines
- 200 unrelated sign pairs matched on the two endpoint frequencies, so a rare
  doubled sign is not compared with a well-measured common-sign baseline

## The no-repeat prediction fails

If `D = S + S` were just an economical way to write two adjacent S tokens,
then D and S together would amount to reusing S and should be depleted. None of
the seven pairs is.

| D / S | texts with D / S | together | expected, length | z length | z site | z object | expected, position shuffle | z position | lower-tail p |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **617 / 615** | 43 / 25 | **1** | 0.6 | +0.50 | +0.50 | +0.45 | 0.5 | +0.65 | .900 |
| 34 / 32 | 10 / 210 | 1 | 1.0 | +0.05 | -0.10 | +0.04 | 0.7 | +0.35 | .842 |
| 821 / 820 | 8 / 146 | 1 | 0.8 | +0.25 | +0.46 | +0.25 | 0.5 | +0.69 | .911 |
| 792 / 809 | 7 / 1 | 0 | 0.0 | -0.08 | -0.06 | -0.05 | 0.0 | -0.08 | .994 |
| 219 / 220 | 5 / 224 | 0 | 0.6 | -0.88 | -0.78 | -0.82 | 0.5 | -0.75 | .604 |
| 401 / 400 | 5 / 196 | 0 | 0.7 | -0.90 | -0.54 | -0.51 | 0.2 | -0.41 | .852 |
| 791 / 790 | 5 / 22 | 0 | 0.1 | -0.25 | -0.23 | -0.22 | 0.0 | -0.22 | .953 |

This is a negative result with a power warning. Expected overlaps are below one
for every pair. The zeros for the small composites cannot distinguish
avoidance from scarcity. The useful result is that even the 617/615 anchor
does not point in the predicted direction under any control: **one observed
against 0.6 expected**. The corpus supplies no evidence that a doubled entry
inherits the no-repeat rule from its base.

## The profiles do not support literal repetition either

Position is an initial/medial/final vector. Context joins the complete
left-neighbour and right-neighbour vectors before taking cosine. Brackets give
the frequency-matched control median, 90th percentile, and the doubled pair's
percentile within that control.

| D / S | position cosine | matched control | neighbour cosine | matched control |
|---|---:|---:|---:|---:|
| **617 / 615** | **.420** | .925 / .993 / 13th | .083 | .107 / .462 / 44th |
| 34 / 32 | .734 | .737 / .989 / 50th | .113 | .051 / .303 / 70th |
| 821 / 820 | .903 | .797 / .992 / 63rd | .063 | .052 / .246 / 57th |
| 792 / 809 | .647 | .772 / .926 / 41st | .000 | .000 / .181 / 80th |
| 219 / 220 | .655 | .582 / .976 / 54th | .332 | .033 / .327 / 90th |
| 401 / 400 | **.994** | .663 / .974 / 98th | .018 | .054 / .326 / 30th |
| 791 / 790 | .970 | .692 / .966 / 92nd | .083 | .044 / .312 / 57th |

There is no family-wide likeness. 401 and 400 occupy nearly identical broad
positions, but do not share neighbours. 219 and 220 approach the control's
90th percentile for neighbour similarity, but not for position. 821/820 and
791/790 are ordinary on both comparisons. The base of 792 occurs once, so its
cosines are not interpretable.

This is not what one sign written with an optional repetition device should
look like. It is also not a clean independent-sign result: several pairs retain
one aspect of the base's distribution. The mixed pattern is closer to
derivation, but only one pair has enough data to make that precise.

## 617 settles the anchor

[12-slots.md](12-slots.md) placed 617 in the terminal-slot paradigm because it
excludes 740. Its base 615 does not behave remotely the same way.

| sign | texts | text-final | share | with 740 / expected by length / z | z site | z object | z exact-position shuffle |
|---|---:|---:|---:|---:|---:|---:|---:|
| **617** | 43 | 26 | **60%** | 6 / 21.7 / **-5.09** | **-4.90** | **-4.98** | **-2.07** |
| **615** | 25 | 1 | **4%** | 14 / 14.0 / +0.01 | +0.70 | +1.15 | +1.05 |

The exact-position control weakens 617's exclusion, as it must: two terminal
signs under-co-occur partly because they want the same place. It does not erase
it. Sign 615, meanwhile, occurs with 740 exactly as often as the length null
expects and a little *more* often than the position null expects.

So 617 is not two 615 tokens compressed into one catalogue entry. **Doubling
changes a non-terminal base into a terminal-slot filler. For this anchor,
doubling is derivational.**

## The numeral controls agree with derivation, not identity

The cases with an independently known graphic arithmetic are useful ground
truth: 34 is the long-stroke four made as two copies of long-stroke two, and 36
is six made as two copies of three.

| D / S | deduplicated tokens | position cosine | neighbour cosine | texts containing both |
|---|---:|---:|---:|---:|
| **34 / 32** | 11 / 217 | .734 | .113 | 1 |
| 36 / 33 | 3 / 149 | .734 | .053 | 0 |
| 56 / 55 | 3 / 36 | 1.000 | .128 | 0 |

Even the secure 34/32 case does not behave like one sign with two spellings.
Doubling changes the expressed value, so the result remains in the numeral
class without inheriting the base sign's local distribution. The tiny 36 and
56 samples cannot add more than a consistency check.

The non-numeral composites look much the same in aggregate: sometimes the broad
position survives, sometimes one side of the neighbour profile survives, but
the full distribution does not. The numeral cases therefore supply a model for
what “derivational” looks like in these statistics.

## Verdict

**The data rejects the repetition-device account.** No doubled/base pair shows
the predicted exclusion, and their profiles are not unusually alike after
frequency matching. The strongest case, 617, is positive evidence for
derivation: the doubled form fills a terminal paradigm that its base does not.
The known numerals show the same general principle—doubling produces a new
value, not a second token of the old sign.

That does **not** establish one productive doubling rule for all non-numerals.
Six of the seven composites have 12 or fewer distinct-text attestations, and
their expected base overlaps are below one. The defensible conclusion is
narrower: **doubled catalogue entries are not literal repetitions in text;
617 is derivational; the remaining non-numeral cases are unresolved one by
one.**

## What this does not license

Nothing here assigns a meaning or sound to 615, 617, or any other sign.
“Derivational” describes a measured change of distribution between a graphic
base and its doubled form. It does not say what feature was added, whether the
same feature applies to every doubled sign, or whether a scribe conceived the
two drawings as morphologically related. The modern font's decomposition is
evidence about encoded form; the positional corpus is the separate evidence
about use.
