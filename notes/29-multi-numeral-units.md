# Multi-numeral texts: is `[num][sign]` a repeating unit?

Script: `src/multi_numeral_units.py`. [12-slots.md](12-slots.md) showed that
numerals co-occur and offered “3 of X and 2 of Y” as an explanation. That was a
plausible gloss, not a tested result. This tests the sequence it requires.

## Numeral tokens are not numeral fields

There are **323 deduplicated sequence-by-site texts with at least two numeral
tokens**.

| numeral tokens | texts |
|---:|---:|
| 2 | 259 |
| 3 | 59 |
| 4 | 4 |
| 5 | 1 |

But adjacent additive signs can form one quantity. Collapse every uninterrupted
numeral sequence into a run:

| numeral runs | texts |
|---:|---:|
| **1** | **172** |
| 2 | 127 |
| 3 | 24 |

More than half of the nominal multi-numeral texts contain only one run. They do
not supply two candidate count units at all. The sequence test therefore uses
the **151 texts with at least two separate numeral runs**.

## The positional null

For each text length, site, and object class, the sign in every absolute slot is
shuffled across texts independently. This preserves the full sign-by-position
matrix, the length distribution, and both metadata controls. It destroys only
which slot occupants occur together as a sequence. There are 2500 shuffles.

Adjacent numeral signs are allowed inside one run. A repeated forward unit is
defined as `[numeral run][one non-numeral sign]`; the reverse test uses
`[one sign][numeral run]`. A complete alternating span must have exactly one
non-numeral between every two runs and a partner for the final run on the same
side.

## The gaps go in the wrong direction

Across all numeral-token pairs, the number of intervening non-numerals is:

| gap | pairs |
|---:|---:|
| 0 | **218** |
| 1 | 78 |
| 2 | 50 |
| 3 | 35 |
| 4 | 12 |

After adjacent tokens are collapsed into runs, the 175 remaining gaps are
`1:78, 2:50, 3:35, 4:12`. A repeating unit predicts a spike at one. The spike
is smaller than positional structure alone predicts.

| measure | observed | positional/site/object null | null 95% | z | lower-tail p |
|---|---:|---:|---:|---:|---:|
| one-sign share of inter-run gaps | **44.6%** | **59.8%** | 53.6–65.7% | **-4.88** | **.0004** |
| texts where every inter-run gap is one | **60/151 = 39.7%** | **57.4%** | 50.6–63.6% | **-5.31** | **.0004** |
| complete `[num-run, sign]` spans | **53/151 = 35.1%** | **50.1%** | 43.3–56.6% | **-4.46** | **.0004** |
| complete `[sign, num-run]` spans | **37/151 = 24.5%** | **42.9%** | 36.5–49.1% | **-5.61** | **.0004** |
| complete span in either direction | **58/151 = 38.4%** | **55.2%** | 48.4–61.7% | **-4.97** | **.0004** |

Every prediction is not merely absent but significantly reversed. Numerals have
positional preferences that make alternating spans fairly common by accident.
The real texts alternate **less** often than that baseline.

## The intervening vocabulary also fails

Using the test texts themselves to define “post-numeral vocabulary” would be
circular: the first sign in a gap is, by construction, observed after a
numeral. The vocabulary is therefore frozen on a disjoint training set—texts
with exactly one numeral token. A sign enters if it has at least five numeral
adjacencies there and at least 70% put the numeral on its left. Twenty-nine
signs qualify.

| between-run tokens | in trained post-numeral vocabulary | share | positional/site/object null | z | lower-tail p |
|---:|---:|---:|---:|---:|---:|
| 331 | 141 | **42.6%** | **47.4%** | -1.99 | **.0188** |

Again the direction is wrong. The signs between numeral runs are slightly
*depleted* for the independently learned post-numeral vocabulary. They are not
a repeated draw from the sign class found after single numerals.

## “The same sign is not counted twice” supplies no rescue

The corpus already avoids repeating any sign
([09-music.md](09-music.md)). A low repeated-target rate would therefore be
automatic. This control shuffles order within each text, keeping its exact sign
multiset—and hence the no-repeat property—fixed.

| orientation | texts where every run has a partner | same partner repeated | no-repeat-preserving null | null 95% | upper p |
|---|---:|---:|---:|---:|---:|
| `[run, sign]` | 131 | **2** | 0.67 | 0–2 | .140 |
| `[sign, run]` | 97 | **1** | 0.72 | 0–3 | .523 |

The observed counts are not unusually low. In the forward orientation they are
actually above the null mean. “The same target is not repeated” is just the
general no-repeat rule and provides no evidence for count units.

## Verdict

**There is no repeating numeral–sign sequence template.** Only 151 of 323
multi-numeral-token texts contain more than one numeral run. Within those, gaps
of one are depleted, complete alternating spans are depleted in both
directions, the independently trained post-numeral vocabulary is depleted, and
target non-repetition is exactly what the corpus-wide no-repeat rule predicts.

The “3 of X and 2 of Y” line in 12-slots.md is therefore withdrawn, and a
correction pointer has been added there. Its statistical result remains: more
than one numeral can occur in a text, so numerals do not fill one exclusive
slot. What those multiple signs are doing is unresolved. In 172 texts they form
one contiguous numeral run; in 151 they occupy multiple positions, but not as
the proposed repeating units.

## What this does not license

Failure of this template does not make the numeral identifications doubtful,
nor does it show that no individual numeral–sign adjacency expresses a count.
It rejects one sequence-level generalisation: reading every separated numeral
as the start or end of a repeated two-part unit. Adjacent numeral runs may be
additive quantities, frozen expressions may contain numeral-shaped signs, and
different constructions can coexist. The corpus does not currently separate
those possibilities, so no replacement gloss is offered.
