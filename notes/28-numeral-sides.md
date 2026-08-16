# Does each counted sign fix which side its numeral goes on?

> **Transcription-uncertainty update — see
> [38-transcription-uncertainty.md](38-transcription-uncertainty.md).** The
> global controlled overdispersion survives every noise draw (z median 12.85,
> 95% 10.62–15.82; excess Q 193–249). The individual BH table below was not
> separately propagated and its marginal sign-level calls should not be treated
> as transcription-robust.

Script: `src/numeral_sides.py`. [24-linear-b.md](24-linear-b.md) pooled every
adjacency and found an almost even order. On the direction-corrected merged
corpus the same aggregate is **1218 numeral-then-sign against 1015
sign-then-numeral**, or 54.5% numeral-left. That still looks flexible.

It is the wrong level of analysis.

## The test

There are **37 non-numeral signs with at least 15 numeral adjacencies** among
2036 deduplicated sequence-by-site records. If each adjacency independently
chooses a side at the 54.5% corpus rate, the per-sign splits should cluster
around that rate. Pearson overdispersion across the 37 binomials measures how
far they spread.

The requested coin-flip mixture is only the first baseline. Position can create
a side rule for free: a sign near the text end has more room for a numeral on
its left. Three permutation controls therefore shuffle the observed side labels
within exact strata while keeping every sign's adjacency count fixed.

| null | observed Q | null mean | null 95% | upper p |
|---|---:|---:|---:|---:|
| independent coin flips | **826.3** | 37.0 | 22.1–55.3 | **.00020** |
| exact length + sign position | **826.3** | 506.0 | 471.8–542.0 | **.00020** |
| site + object class | **826.3** | 37.0 | 22.0–55.2 | **.00020** |
| **position + site + object** | **826.3** | **531.7** | **497.4–567.1** | **.00020** |

Q is 23 times its nominal 36 degrees of freedom. Position explains a large
part of that excess—the null jumps from 37 to 506—but the observed dispersion
still lies far beyond 5000 combined-control permutations.

The shape is not subtle:

| numeral-left share | signs |
|---:|---:|
| 0–10% | **5** |
| 10–30% | 4 |
| 30–70% | **4** |
| 70–90% | 14 |
| 90–100% | **10** |

**Fifteen of 37 signs are at least 90% one-sided. The independent-token null
expects 0.01 such signs and never produces more than one in 5000 runs.** The
pooled average was hiding a strongly polarised distribution.

## Every eligible sign

“Left” means `[numeral, sign]`; “right” means `[sign, numeral]`. Controlled
expectation and p come from the combined exact-position, site, and object
permutation. BH is over all 37 signs.

| sign | n | numeral left | numeral right | left share | controlled E(left) | controlled p | BH |
|---:|---:|---:|---:|---:|---:|---:|:---:|
| 817 | 107 | 0 | 107 | **0%** | 0.9 | .6391 | no |
| 820 | 99 | 3 | 96 | **3%** | 7.9 | .0040 | yes |
| 861 | 125 | 5 | 120 | **4%** | 10.9 | .0060 | yes |
| 297 | 19 | 1 | 18 | **5%** | 6.3 | .0024 | yes |
| 60 | 30 | 2 | 28 | **7%** | 10.0 | .0012 | yes |
| 705 | 73 | 11 | 62 | 15% | 30.4 | .0004 | yes |
| 741 | 39 | 7 | 32 | 18% | 18.7 | .0004 | yes |
| 706 | 39 | 8 | 31 | 21% | 19.5 | .0004 | yes |
| 368 | 31 | 8 | 23 | 26% | 15.2 | .0004 | yes |
| 503 | 19 | 7 | 12 | 37% | 8.6 | .4751 | no |
| 840 | 47 | 21 | 26 | 45% | 26.4 | .0532 | no |
| 900 | 43 | 27 | 16 | 63% | 24.9 | .4387 | no |
| 550 | 17 | 11 | 6 | 65% | 9.8 | .5863 | no |
| 798 | 24 | 17 | 7 | 71% | 13.2 | .0644 | no |
| 904 | 15 | 11 | 4 | 73% | 11.3 | 1.0000 | no |
| 740 | 80 | 59 | 21 | 74% | 64.2 | .0376 | no |
| 233 | 31 | 23 | 8 | 74% | 18.5 | .0520 | no |
| 806 | 25 | 19 | 6 | 76% | 13.6 | .0080 | yes |
| 803 | 38 | 30 | 8 | 79% | 22.9 | .0028 | yes |
| 390 | 83 | 67 | 16 | 81% | 68.7 | .5095 | no |
| 240 | 55 | 45 | 10 | 82% | 36.5 | .0084 | yes |
| 220 | 114 | 94 | 20 | 82% | 78.8 | .0004 | yes |
| 407 | 47 | 39 | 8 | 83% | 39.7 | .9246 | no |
| 700 | 25 | 21 | 4 | 84% | 20.5 | .9638 | no |
| 231 | 16 | 14 | 2 | 88% | 11.6 | .1804 | no |
| 575 | 16 | 14 | 2 | 88% | 11.3 | .0580 | no |
| 590 | 32 | 28 | 4 | 88% | 21.8 | .0028 | yes |
| 61 | 21 | 19 | 2 | **90%** | 16.2 | .1252 | no |
| 520 | 53 | 48 | 5 | **91%** | 48.9 | .7303 | no |
| 156 | 24 | 22 | 2 | **92%** | 22.6 | .9094 | no |
| 235 | 37 | 34 | 3 | **92%** | 24.4 | .0004 | yes |
| 226 | 16 | 15 | 1 | **94%** | 13.9 | .2464 | no |
| 140 | 19 | 18 | 1 | **95%** | 12.9 | .0008 | yes |
| 176 | 20 | 20 | 0 | **100%** | 16.6 | .0328 | no |
| 415 | 18 | 18 | 0 | **100%** | 14.5 | .0308 | no |
| 585 | 16 | 16 | 0 | **100%** | 13.9 | .0752 | no |
| 760 | 15 | 15 | 0 | **100%** | 14.5 | 1.0000 | no |

**Fifteen signs survive BH after all controls.** Some spectacular raw splits do
not. Sign 817's 0/107, for example, is almost completely predicted by its exact
positions and strata, so its controlled p is .64. Conversely, 220's 94/114 is
still extreme against a position-controlled expectation of 78.8.

That distinction is why a table of raw binomial p-values would be misleading.
The global effect survives position, and the per-sign table says which parts do.

## This is not only the known frozen phrases

The most obvious concern is that [22-two-forms-of-two.md](22-two-forms-of-two.md)
already established four fixed adjacencies: 817/861/820 + 2 and 840 + 32. They
necessarily contribute one-sided events.

Remove all four pairs and re-run the combined control:

| | events | eligible signs | observed Q | controlled mean | controlled 95% | p |
|---|---:|---:|---:|---:|---:|---:|
| all | 2233 | 37 | 826.3 | 531.7 | 497.4–567.1 | .00020 |
| **frozen pairs removed** | **1915** | **35** | **442.3** | **171.7** | **143.8–202.4** | **.00020** |

The effect halves, which is important: the frozen expressions carry a great
deal of the structure. It does not disappear. Sign-specific numeral placement
extends well beyond the four pairs already known.

## What correlates with side?

Position matters, as expected. Across the 37 signs, numeral-left share
correlates with mean position in the text: **Spearman rho = .464, p = .0038**.
Later signs tend to have the numeral on their left. The combined permutation
above shows that this is an explanation for part, not all, of the per-sign
effect.

The other available correlates were tested with Mantel-Haenszel controls:

| contrast; outcome = numeral on left | controls | OR | z | p |
|---|---|---:|---:|---:|
| seal vs tablet | sign, exact position, site | 1.71 | +0.87 | .387 |
| Mohenjo-daro vs Harappa | sign, exact position, object | 0.40 | -1.99 | .046 |
| **fish family vs other signs** | exact position, site, object | **5.27** | **+7.66** | **1.8e-14** |

Object class is null. The site difference is borderline and post-hoc; it would
not survive even a small correction for the correlates tested here.

The fish result is strong. Across all adjacency events, fish-family signs have
a numeral on the left **238/282 = 84%** of the time, against **980/1951 = 50%**
for other signs. The effect survives exact-position, site, and object control.
This independently agrees with [06-fish.md](06-fish.md): fish variants are
regularly preceded by numerals. It now adds that their opposite-side
adjacencies are unusually rare for their positions.

## Verdict

**There is sign-specific side structure, and the corpus average concealed it.**
The data does not pick one universal order. Instead it contains signs that
almost always precede an adjacent numeral, signs that almost always follow one,
and very few signs in the middle. Fifteen individual preferences survive the
full positional/site/object control, and the global overdispersion remains
after removing the known frozen phrases.

The sentence in 24-linear-b.md should therefore be narrowed. Indus still lacks
Linear B's *universal* commodity-then-number order. It does not lack order
altogether: **numeral side is partly sign-specific.** A correction pointer has
been added there.

## What this does not license

“Numeral adjacency” is an epigraphic relation, not proof that the neighboring
sign names the thing being counted. The 817/861 + 2 expressions demonstrate the
danger: a fixed pair can be one-sided without being a freely assembled count.
Nor does a preferred side establish a syntactic category, a sound, or a
language. The result licenses a distributional placement rule for particular
signs. Deciding which adjacencies are productive counting constructions is the
next question, not an assumption built into this one.
