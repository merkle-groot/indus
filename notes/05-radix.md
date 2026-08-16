# Is there a radix, and is it 10?

> **Pair-network uncertainty — see
> [38-transcription-uncertainty.md](38-transcription-uncertainty.md).** The
> 817/861, 817/820, and 861/820 exclusion edges used later as a validation triad
> survive only 3.7%, 20%, and 1.7% of exact-position transcription-noise draws.
> Adjacency and graphic evidence in this note are separate; the three-way
> exclusion claim should be treated as fragile.

> **SUPERSEDED IN PART — see [16-twelve.md](16-twelve.md).** The base-8 reading
> below rests on excluding the bracketed and multi-row stroke signs. Reading
> those as numbers reveals a well-attested value **12** (sign 55, 37 deduplicated
> tokens, Poisson p = 1.4e-45 against the extrapolated decay), which base 8
> cannot accommodate. The cliff-after-7 arithmetic here is still correct as far
> as it goes; the conclusion drawn from it is withdrawn.

Scripts: `src/radix.py`, `src/radix2.py`.

## Corrected values

The first pass had a bug: two-row ids were read as their raw value. The rendered
chart shows id 16 = `|||/|||` = six strokes, so **two-row value = id - 10**.
Corrected combined counts across all three series:

```
1:298   2:846   3:391   4:86   5:61   6:40   7:57   8:6   9:3     (nothing >=10)
```

## The two-row series is graphic, not a tier

| value | single-row | two-row | two-row share |
|---|---|---|---|
| 1 | 298 | 0 | 0% |
| 3 | 369 | 22 | 5.6% |
| 5 | 54 | 7 | 11.5% |
| 6 | 2 | 38 | **95.0%** |
| 7 | 3 | 54 | **94.7%** |
| 8-9 | 0 | 9 | 100% |

Two-row takes over precisely where a single row of strokes stops being legible.
It is a writing convention, not a higher order. Consistent with this, the three
series *avoid* each other slightly across texts (observed/expected 0.71-0.94),
where genuine tiers of one system would co-occur constantly.

So there is **no place-value composition** visible anywhere in the corpus.

## The cliff after 7

Values 4-7 sit on a plateau (86, 61, 40, 57) and then collapse to 6 and 3.
Fitting the plateau and extrapolating:

| fit range | predicts value 8 | observed | Poisson P(<=obs) |
|---|---|---|---|
| 4-7 | 38.9 | 6 | 7.4e-11 |
| 5-7 | 48.4 | 6 | 1.9e-14 |
| 3-7 (conservative) | 21.5 | 6 | 8.6e-05 |

The drop is a genuine discontinuity, not ordinary decay.

**The graphic-difficulty explanation fails.** The obvious objection is that 8
and 9 are rare because they need more strokes. But 8 is `||||/||||` — perfectly
symmetric, two equal rows — while 7 is `||||/|||`, asymmetric. If drawing effort
were the cause, the symmetric one should not be the rarer. It is **9x rarer**
(54 tokens vs 6).

## Radix scan

| B | tokens < B | tokens >= B | violation rate | verdict |
|---|---|---|---|---|
| 4 | 1535 | 253 | 14.2% | violated |
| 5 | 1621 | 167 | 9.3% | leaky |
| 6 | 1682 | 106 | 5.9% | leaky |
| 7 | 1722 | 66 | 3.7% | leaky |
| **8** | **1779** | **9** | **0.50%** | clean truncation |
| 9 | 1785 | 3 | 0.17% | clean |
| 10+ | 1788 | 0 | 0% | unconstrained from above |

**Answer: the data supports base 8 better than base 10.** Bases 4-7 are
positively violated. Base 8 is the smallest base with a clean truncation. Bases
10, 11, 12 have zero violations only because nothing above 9 is attested at
all — they are unfalsified rather than supported.

The discriminating argument against 10: under base 10, values 8 and 9 are
ordinary digits written exactly the way 6 and 7 are, so they should occur at
comparable rates. Observed 9 tokens against 97. Under base 8, 8 and 9 are not
digits at all, and the handful attested are the expected trickle of
irregular or non-numeric uses.

## No higher-unit symbol found (but something else was)

A base-B system needs a symbol for B. The obvious candidates are signs sitting
even earlier than numerals. Testing whether they are immediately followed by a
numeral more than the 16.1% base rate:

| sign | n | followed by numeral | lift | p |
|---|---|---|---|---|
| 817 | 139 | **87.8%** | 5.47 | 1.8e-77 |
| 861 | 158 | **81.6%** | 5.08 | 9.4e-74 |
| 820 | 144 | **68.1%** | 4.24 | 5.4e-44 |

These are not multipliers. The numeral that follows them is **value 2, 93.7% of
the time** — and specifically the short-stroke form.

| sign | n | distribution of following value |
|---|---|---|
| 861 | 129 | 2 x128, 3 x1 |
| 817 | 122 | 2 x118, 1 x1, 3 x2, 4 x1 |
| 820 | 98 | 2 x81, 1 x15, 3 x2 |

That is a frozen collocation, not arithmetic: three signs that are
near-obligatorily followed by one specific stroke sign.

### This resolves the "2 outranks 1" anomaly

From [04-numerals.md](04-numerals.md): sign 2 was inexplicably ~4x more common
than sign 1. **327 of its 583 tokens (56%) sit immediately after 817, 820 or
861.** In those positions it is not counting anything; it is the second half of
a fixed two-sign unit. Excluding them, values run 1:282, 2:519, 3:386 — still
top-heavy, but no longer bizarre.

### Re-run with Parpola's numbering (`src/merge817.py`)

[10-more-data.md](10-more-data.md) turned up that Parpola gives **817 and 861 the
same number, P385**, while 820 is a separate sign, **P378**. If that is right,
the collocation has two sources, not three. Tested four ways, with 820 as a
control that should *fail* whatever 817/861 pass:

| test | 817 vs 861 | 817/861 vs 820 |
|---|---|---|
| numeral it takes (2 vs other) | 118:4 vs 128:1, **p = .20 same** | p = .0008 / p < .0001 **different** |
| site distribution | chi2 **p = .40 same** | — |
| do they share a text? | 1 observed vs 9.4 expected — **complementary** | 1 vs 8.4; 4 vs 9.8 |
| position | 87% vs 69% text-initial, **p = .006 different** | 77% initial |

The control behaves exactly as it should: 820 is the only one of the three that
regularly takes **value 1** (15 times, against 1 for 817 and 0 for 861). The
test can tell these signs apart, and it separates precisely the one Parpola
separates. That is a real validation of the crosswalk.

Three of four tests support merging 817 and 861. The dissent is position: 817 is
text-initial 87% of the time against 861's 69%, and that gap survives control
for text length (CMH z = 2.74, p = .006). Nothing systematic precedes 861 when
it is not initial — the preceding signs are a scatter of 5, 3, 3, 2, 2 — so this
looks like a difference in deployment rather than a different construction.

Note that complementary distribution (test 3) does **not** by itself prove one
sign. Two *different* signs competing for the same slot would look identical
here, which is exactly what [09-music.md](09-music.md) found the whole corpus
doing. It is consistent with the merge, not evidence for it.

**Verdict: accept the merge, with a caveat.** The counts do not change — 327 of
846 value-2 tokens still sit after the trio — but the explanation gets simpler:

| | tokens forcing a following 2 |
|---|---|
| **P385** (817+861, 314 tokens) | **246** |
| P378 (820, 157 tokens) | 81 |

So 75% of the anomaly is **one sign**, not three coincidences. Excluding the
collocation, values still run 1:282, 2:519, 3:386 — unchanged, since this was
always a question of *why*, not *how many*.

## Bottom line

- Base 8 is the best-supported radix; base 10 is merely unfalsified.
- But the support is entirely from an *absence* — a cliff after 7. No carry, no
  place value, and no symbol for the base were found, which is what you would
  really want before claiming a base.
- The honest statement: **stroke numerals in this corpus express values 1-7,
  with a hard boundary at 8.** Whether that boundary is a radix or simply the
  largest quantity anyone had reason to stamp on a seal cannot be settled from
  1788 tokens with nothing above 9.

## Caveats

- Rests on id -> stroke-count mapping, verified by eye for 16/17/18/19 and
  31/32/33/35 but not exhaustively.
- Bracketed and barred stroke signs (ids 41-51, 55) remain excluded. If any of
  those encode higher values, the cliff could move.

> **Revised in part by [22-two-forms-of-two.md](22-two-forms-of-two.md).** The
> three stroke series do encode the same values, but the choice between them is
> *not* free inside frozen expressions: 817 and 861 take the short two 220 times
> and the long two never, while sign 840 takes the long two 22 times against 2
> short (p = 2.5e-29). A fourth frozen pair, 840 + 32, was missed here.
