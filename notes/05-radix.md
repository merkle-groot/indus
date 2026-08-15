# Is there a radix, and is it 10?

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
