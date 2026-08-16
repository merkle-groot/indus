# The right edge, indexed from the right

Script: `src/right_positions.py`. [12-slots.md](12-slots.md) recovered a
terminal paradigm and then found 400 and 90 sitting behind it. That result was
assembled from a disagreement between two tests. Here every text is indexed
systematically from its end: last sign = -1, penultimate = -2, and so on.

## Setup and the positional null

The merged corpus gives **2027 distinct sequence-by-site attestations** of
length at least two and **80 signs in at least 20 texts**. Repeated copies at
one site get one vote; an attestation at another site remains available to the
site-stratified control.

The null is a shuffle of the signs *inside each text*. It preserves the text's
length, vocabulary, site, object class, and repeat pattern. For a text of length
L containing c copies of a sign, the chance that a specified shuffled slot
contains it is exactly c/L. Summing those probabilities gives the expected
occupancy and its variance without Monte Carlo error.

The script prints the complete 80-sign x six-position matrix. The leading
localisations at the first three positions are:

| right position | sign | observed | shuffle expectation | z |
|---:|---:|---:|---:|---:|
| **-1** | 740 | 704 | 232.5 | **+36.5** |
| | 520 | 151 | 43.7 | **+19.3** |
| | 400 | 173 | 58.0 | **+18.2** |
| | 90 | 66 | 17.1 | **+13.5** |
| | 527 | 47 | 14.3 | +10.5 |
| | 151 | 53 | 19.1 | +9.7 |
| | 407 | 57 | 22.6 | +8.6 |
| | 156 | 56 | 23.2 | +8.5 |
| | 390 | 80 | 44.4 | +6.4 |
| | 617 | 28 | 12.1 | +5.5 |
| | 226 | 19 | 7.6 | +5.0 |
| **-2** | 760 | 67 | 16.0 | **+14.6** |
| | 100 | 56 | 16.7 | **+11.0** |
| | 4 | 42 | 16.7 | +7.6 |
| | 585 | 18 | 4.6 | +7.1 |
| | 923 | 21 | 6.5 | +6.7 |
| | 142 | 27 | 11.1 | +5.8 |
| | 3 | 56 | 30.3 | +5.7 |
| | 33 | 61 | 34.2 | +5.5 |
| **-3** | 590 | 65 | 22.2 | **+10.3** |
| | 240 | 84 | 36.0 | **+9.0** |
| | 435 | 21 | 6.9 | +6.1 |
| | 1 | 51 | 24.2 | +6.1 |
| | 17 | 23 | 8.1 | +5.9 |
| | 415 | 32 | 15.6 | +4.7 |
| | 706 | 24 | 10.6 | +4.7 |
| | 2 | 134 | 93.9 | +4.6 |

At z >= 3 there are **11 localised signs at -1, 20 at -2, and 16 at -3**.
The later lists are not merely the tail of the -1 group: they contain their own
vocabularies.

Twenty-one testable signs are flat over these three positions in the explicit
sense that no cell departs from the shuffle by |z| >= 3:

```
16 55 125 140 297 350 368 413 416 440 455
503 595 615 700 717 742 790 832 850 892
```

“Flat” here means no sharp preference among the first three right positions,
not uniform over the entire text. A sign could still be strongly left-anchored
or localised farther from the end.

## Occupancy is not a paradigm

A real slot needs both localisation and competing fillers. Within each cohort,
every powered pair was tested for exclusion by Mantel-Haenszel stratified by
length, corrected by BH, and then required to remain negative when stratified
by site and by object class.

| cohort | localised signs | powered pairs | BH discoveries | survive site + object |
|---:|---:|---:|---:|---:|
| **-1** | 11 | 33 | 19 | **16** |
| **-2** | 20 | 34 | **0** | **0** |
| **-3** | 16 | 106 | 1 | 1 |

The -1 result recovers and enlarges the terminal network.

| pair | observed | expected by length | z length | z site | z object |
|---|---:|---:|---:|---:|---:|
| **520 / 740** | 5 | 91.9 | **-14.22** | **-12.63** | **-12.70** |
| 156 / 740 | 6 | 31.8 | -6.50 | -7.17 | -7.13 |
| 527 / 740 | 6 | 26.5 | -5.93 | -5.42 | -5.46 |
| 390 / 740 | 54 | 89.8 | -5.91 | -4.80 | -4.50 |
| 617 / 740 | 6 | 22.8 | -5.26 | -4.97 | -5.07 |
| 151 / 740 | 8 | 26.5 | -5.12 | -5.57 | -5.62 |
| 390 / 520 | 0 | 17.0 | -4.58 | -4.31 | -4.47 |
| 226 / 740 | 3 | 13.6 | -4.19 | -3.92 | -4.05 |

Eight further, weaker -1 pairs survive all three controls; the script prints
them rather than hiding them. Several join 400, 90, and 407 to parts of the
network, but there is no single clique containing all eleven signs. Absolute
-1 therefore contains more than one functional layer.

The -2 cohort is the crucial failure: **zero of 34 powered pairs survives even
the length-stratified FDR scan.** Twenty signs prefer the penultimate position,
but they do not compete for one penultimate slot. Localisation alone would have
manufactured a paradigm here.

At -3, the sole exclusion is 1 versus 2:

| pair | observed | expected by length | z length | z site | z object |
|---|---:|---:|---:|---:|---:|
| 1 / 2 | 24 | 57.0 | -6.35 | -2.96 | -3.01 |

This is not a recovered -3 paradigm. It is the already-known 1/2 effect from
[12-slots.md](12-slots.md), where the frozen 817/861 + 2 construction makes 2
look exclusive while other numeral pairs co-occur freely. One pair does not
knit the sixteen localised signs into a cohort of competing fillers.

## 400 and 90 are not the -2 paradigm

The systematic indexing corrects the hand description in 12-slots. Both signs
are overwhelmingly at absolute -1, not -2:

| sign | -1 | -2 | -3 |
|---|---:|---:|---:|
| **400** | **82%** | 8% | 4% |
| **90** | **77%** | 8% | 3% |

And they do not exclude each other.

| pair | observed | expected by length | z length | z site | z object |
|---|---:|---:|---:|---:|---:|
| **400 / 90** | **7** | 7.5 | **-0.20** | -0.24 | -0.34 |
| 740 / 400 | 109 | 97.4 | +1.78 | +0.86 | +0.30 |
| 740 / 90 | 69 | 48.4 | **+4.82** | **+6.39** | **+6.20** |

So “a second position behind the terminal slot” remains a useful relational
description, but it is not absolute position -2. When 400 or 90 is appended
after 740, the appended sign occupies -1 and **740 moves to -2**. The terminal
paradigm floats one place left. Re-indexing by the edge cannot make a latent
slot align when optional material follows it.

There is also no evidence that 400 and 90 are the two values of one slot. They
co-occur exactly at expectation, often adjacent. They are two post-terminal
signs, not a mutually exclusive pair.

## The right-anchored boundary

The boundary is now explicit:

- **-1 has a large, controlled exclusion network**: this is where the terminal
  paradigm is usually observed, mixed with appended 400/90 material.
- **-2 has strong individual positional preferences but no exclusion at all.**
- **-3 has no cohort-level paradigm**, only the previously explained 1/2 pair.

Thus the recoverable *paradigmatic* structure stops after the first absolute
right position. The construction itself can span two signs because 400 or 90
may follow a terminal filler, but there is no general -2 slot and no -3 slot.
That distinction—one floating terminal paradigm plus optional following
material—is the result.

## Do growing texts keep their last two signs?

The merged corpus has 493 one-sign-longer subsequence pairs under the exact
procedure of [13-growth.md](13-growth.md). A position-matched simulation draws
each slot of each length from its observed distribution, rejects repeats, and
recomputes the pairs 2000 times.

| preserved tail | observed | positional null | null 95% | z | relevant tail p |
|---|---:|---:|---:|---:|---:|
| last sign | **77.5%** | **88.0%** | 81.2–93.6% | **-3.34** | lower .0020 |
| **last two signs** | **62.1%** | **47.7%** | 37.4–58.4% | **+2.68** | upper **.0045** |

The old 77% headline dies to the control: terminal signs are so frequent that a
position-matched null keeps the last sign **more** often than the real pairs do.
It was consistent with the terminal result, but it was not independent evidence
for it. A correction pointer has been added to 13-growth.md.

The new result goes the other way. Growing pairs keep both final signs 62% of
the time against 48% expected. The effect is modest, but it clears the correct
baseline. This is consistent with a short right-edge construction moving as a
unit, including a terminal filler plus optional following material.

## What this does not license

An exact right position is not automatically a grammatical slot. The -2
failure demonstrates that directly: twenty signs are sharply localised there
and none forms a controlled exclusion pair. Nor does the two-sign growth result
identify what either position does. Damage remains unmarked in the source, and
short fragments can contribute subsequence pairs. The evidence licenses a
right-anchored structural boundary and a floating terminal paradigm, not a
reading of any sign or a complete template for the text.
