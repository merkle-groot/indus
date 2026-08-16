# The right edge, indexed from the right

> **Uncertainty update — see
> [38-transcription-uncertainty.md](38-transcription-uncertainty.md).** The
> positional concentration of the fixed terminal cohort remains overwhelming,
> but most individual exclusion edges in the network below do not survive the
> exact-position plus transcription-noise analysis. 740/520 is robust;
> 520/390 is borderline; 740/617 survives half the draws; the tested 740/390,
> 740/527, 740/151, and 740/156 edges are fragile. The negative result for −2
> and −3 cohorts is unchanged.

Script: `src/right_positions.py`. [12-slots.md](12-slots.md) recovered a
terminal paradigm and then found 400 and 90 sitting behind it. That result was
assembled from a disagreement between two tests. Here every text is indexed
systematically from its end: last sign = -1, penultimate = -2, and so on.

## Setup and the positional null

The merged corpus gives **2001 distinct sequence-by-site attestations** of
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
| **-1** | 740 | 721 | 229.7 | **+38.2** |
| | 520 | 152 | 42.5 | **+19.9** |
| | 400 | 181 | 56.4 | **+19.9** |
| | 90 | 66 | 17.1 | **+13.5** |
| | 527 | 47 | 14.0 | +10.7 |
| | 151 | 53 | 18.6 | +10.0 |
| | 156 | 58 | 22.2 | +9.5 |
| | 407 | 59 | 22.1 | +9.3 |
| | 390 | 85 | 43.4 | +7.5 |
| | 617 | 29 | 12.1 | +5.9 |
| | 226 | 20 | 7.6 | +5.4 |
| | 700 | 20 | 11.9 | +3.0 |
| **-2** | 760 | 66 | 15.7 | **+14.5** |
| | 100 | 54 | 16.5 | **+10.6** |
| | 4 | 44 | 16.7 | +8.2 |
| | 585 | 18 | 4.6 | +7.1 |
| | 923 | 21 | 6.5 | +6.7 |
| | 3 | 57 | 28.8 | +6.4 |
| | 33 | 63 | 33.2 | +6.2 |
| | 142 | 28 | 11.1 | +6.2 |
| **-3** | 590 | 65 | 22.2 | **+10.3** |
| | 240 | 84 | 35.0 | **+9.3** |
| | 1 | 52 | 24.0 | +6.4 |
| | 435 | 21 | 6.6 | +6.3 |
| | 17 | 23 | 8.1 | +5.9 |
| | 415 | 33 | 15.3 | +5.1 |
| | 706 | 24 | 10.6 | +4.7 |
| | 2 | 134 | 93.9 | +4.6 |

At z >= 3 there are **12 localised signs at -1, 20 at -2, and 15 at -3**.
The later lists are not merely the tail of the -1 group: they contain their own
vocabularies.

Eighteen testable signs are flat over these three positions in the explicit
sense that no cell departs from the shuffle by |z| >= 3:

```
16 125 297 350 368 413 416 440 455
503 595 615 717 742 790 832 850 892
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
| **-1** | 12 | 37 | 20 | **17** |
| **-2** | 20 | 33 | **0** | **0** |
| **-3** | 15 | 91 | 1 | 1 |

The -1 result recovers and enlarges the terminal network.

| pair | observed | expected by length | z length | z site | z object |
|---|---:|---:|---:|---:|---:|
| **520 / 740** | 5 | 90.8 | **-14.14** | **-12.55** | **-12.66** |
| 156 / 740 | 6 | 30.7 | -6.34 | -6.99 | -6.93 |
| 527 / 740 | 6 | 26.1 | -5.86 | -5.36 | -5.30 |
| 390 / 740 | 54 | 89.3 | -5.85 | -4.71 | -4.34 |
| 617 / 740 | 6 | 22.8 | -5.26 | -5.00 | -5.10 |
| 151 / 740 | 8 | 26.4 | -5.10 | -5.51 | -5.66 |
| 390 / 520 | 0 | 16.8 | -4.56 | -4.28 | -4.43 |
| 226 / 740 | 3 | 13.6 | -4.18 | -3.94 | -4.07 |

Nine further, weaker -1 pairs survive all three controls; the script prints
them rather than hiding them. Several join 400, 90, and 407 to parts of the
network, but there is no single clique containing all eleven signs. Absolute
-1 therefore contains more than one functional layer.

The -2 cohort is the crucial failure: **zero of 33 powered pairs survives even
the length-stratified FDR scan.** Twenty signs prefer the penultimate position,
but they do not compete for one penultimate slot. Localisation alone would have
manufactured a paradigm here.

At -3, the sole exclusion is 1 versus 2:

| pair | observed | expected by length | z length | z site | z object |
|---|---:|---:|---:|---:|---:|
| 1 / 2 | 24 | 56.8 | -6.34 | -2.98 | -3.05 |

This is not a recovered -3 paradigm. It is the already-known 1/2 effect from
[12-slots.md](12-slots.md), where the frozen 817/861 + 2 construction makes 2
look exclusive while other numeral pairs co-occur freely. One pair does not
knit the sixteen localised signs into a cohort of competing fillers.

## 400 and 90 are not the -2 paradigm

The systematic indexing corrects the hand description in 12-slots. Both signs
are overwhelmingly at absolute -1, not -2:

| sign | -1 | -2 | -3 |
|---|---:|---:|---:|
| **400** | **87%** | 7% | 4% |
| **90** | **77%** | 9% | 3% |

And they do not exclude each other.

| pair | observed | expected by length | z length | z site | z object |
|---|---:|---:|---:|---:|---:|
| **400 / 90** | **7** | 7.4 | **-0.17** | -0.24 | -0.36 |
| 740 / 400 | 107 | 95.2 | +1.82 | +0.85 | +0.29 |
| 740 / 90 | 69 | 48.4 | **+4.83** | **+6.35** | **+6.16** |

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

The direction-corrected merged corpus has 538 one-sign-longer subsequence pairs under the exact
procedure of [13-growth.md](13-growth.md). A position-matched simulation draws
each slot of each length from its observed distribution, rejects repeats, and
recomputes the pairs 2000 times.

| preserved tail | observed | positional null | null 95% | z | relevant tail p |
|---|---:|---:|---:|---:|---:|
| last sign | **78.1%** | **88.5%** | 81.8–94.1% | **-3.28** | lower .0035 |
| **last two signs** | **62.5%** | **44.8%** | 35.3–55.0% | **+3.48** | upper **.0005** |

The old 77% headline dies to the control: terminal signs are so frequent that a
position-matched null keeps the last sign **more** often than the real pairs do.
It was consistent with the terminal result, but it was not independent evidence
for it. A correction pointer has been added to 13-growth.md.

The new result goes the other way. Growing pairs keep both final signs 63% of
the time against 45% expected. The effect is modest, but it clears the correct
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
