# 35 — The inventory is not saturated

## Result

After removing the twelve database codes that mean “unidentified,” the corpus
contains **515 merged** or **579 unmerged** identifiable sign types. Coverage,
lower-bound, and extrapolation estimators disagree substantially:

| inventory | observed | Good–Turing coverage total (95%) | Chao1 (95%) | ACE (95%) | Heaps at 2× tokens (95% order band) |
|---|---:|---:|---:|---:|---:|
| merged | 515 | 524.6 (510.1–539.5) | **715.4 (682.8–756.4)** | **694.7 (668.0–726.9)** | 719.5 (688.2–752.1) |
| unmerged | 579 | 592.3 (576.6–608.6) | **808.8 (775.5–853.5)** | **824.4 (792.8–859.2)** | 822.2 (790.2–858.0) |

The merged point estimate is therefore not “528 signs.” It is **at least 515
identifiable types in this deduplicated corpus, plausibly around 700–715 under
the abundance estimators**, conditional on the current allograph policy. The
wide disagreement is more honest than one preferred integer. Good–Turing says
that little *token probability mass* is unseen; Chao1 and ACE say that mass can
nevertheless contain many very rare types.

## Corpus and controls

I use `lines_merged.json` for the merged analysis and the unmerged sign IDs only
for the requested sensitivity comparison. Both are deduplicated first as exact
`(text, site, object class)` records. Merging turns some formerly different
texts into copies, so the two deduplicated sample sizes legitimately differ:
2,086 merged versus 2,094 unmerged records.

Inventory and abundance are invariant to permutation of token positions. An
exact positional shuffle therefore returns the identical frequency spectrum,
not a stochastic null; the script records that invariant rather than displaying
a fake p-value. Site and object class enter the uncertainty calculation through
a stratified text bootstrap, which resamples the original number of records
inside each `(site, object)` stratum. Texts, not individual tokens, are the
sampling clusters.

The 95% intervals are centered percentile intervals from 1,000 such bootstraps.
An ordinary richness-bootstrap percentile interval is known to shift sharply
downward because a resample omits many already rare observed types. The script
therefore centers bootstrap deviations on the full-sample estimate and records
the raw bootstrap median in the JSON so that this correction is auditable.

## The twelve unidentified codes

Note 20 identified eleven sign IDs whose glyph is `DOUBLE QUESTION MARK`—the
digitizer's “could not identify this” marker—and blank ID 999. They contribute
16 deduplicated tokens. Removing them makes one resulting two-token record a
duplicate, so exclusion plus rededuplication lowers the analysed token count by
18. They are not twelve evidence-bearing sign types.

I ran three fixed treatments without tuning:

1. **recorded:** pretend the twelve database IDs are twelve distinct signs;
2. **collapsed:** treat all twelve as one `UNK` marker;
3. **excluded (main):** remove those tokens, rededuplicate, and estimate the
   identifiable inventory.

| inventory / treatment | observed | singletons | Good–Turing | Chao1 | ACE |
|---|---:|---:|---:|---:|---:|
| merged, recorded | 527 | 177 | 537.4 | 740.4 | 722.9 |
| merged, collapsed | 516 | 168 | 525.6 | 716.4 | 695.7 |
| **merged, excluded** | **515** | **168** | **524.6** | **715.4** | **694.7** |
| unmerged, recorded | 591 | 214 | 605.1 | 833.5 | 854.2 |
| unmerged, collapsed | 580 | 205 | 593.2 | 809.8 | 825.4 |
| **unmerged, excluded** | **579** | **205** | **592.3** | **808.8** | **824.4** |

Collapsing rather than excluding changes the inventory by exactly the retained
`UNK` category and barely moves any estimator. Treating the twelve labels as
real types inflates the singleton-sensitive estimates by roughly 23–29 types.
The qualitative result does not depend on this choice.

Nothing estimates how many real signs lie behind the 16 unreadable tokens.
They could repeat known signs or include unseen ones. Excluding them defines an
identifiable inventory, not a proof that their information content is zero.

## Frequency spectrum

After excluding unidentified markers:

| count per sign | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | >10 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| merged: number of signs | **168** | 69 | 41 | 29 | 27 | 15 | 15 | 21 | 7 | 12 | 111 |
| unmerged: number of signs | **205** | 90 | 44 | 31 | 24 | 15 | 14 | 22 | 10 | 13 | 111 |

The singleton and doubleton counts drive Chao1. For merged signs,
`f1 = 168` and `f2 = 69`; the bias-corrected unseen term is
`f1(f1−1) / [2(f2+1)] = 200.4`. Allograph merging removes 37 singleton types
and 21 doubletons, which is why the estimated total falls by about one hundred,
not merely the 64 observed labels it merges away.

Sample coverage is nevertheless high: 98.16% merged and 97.76% unmerged. This
is not saturation of the *number* of types. Good–Turing estimates the unseen
probability mass as `f1/N`; dividing observed richness by estimated coverage is
the conservative “coverage total” in the table. A long tail can carry little
mass and many types, so Good–Turing and Chao1 answer different questions.

## Accumulation and Heaps extrapolation

Randomizing whole-text order 500 times gives the accumulation curve. Bands are
conditional order bands, not new-corpus confidence intervals.

| tokens sampled | merged types, median (95%) | unmerged types, median (95%) |
|---:|---:|---:|
| about 5% | 144 (130–159) | 149 (135–163) |
| about 10% | 204 (189–220) | 213 (196–230) |
| about 20% | 281 (265–297) | 298 (280–317) |
| about 50% | 405 (391–419) | 445 (427–460) |
| about 75% | 468 (455–480) | 522 (508–533) |
| 100% | **515** | **579** |

The slope is still visibly positive at the corpus endpoint. A power-law Heaps
fit `V(n) = K n^β` gives:

| inventory | β (95% order band) | projected at 2× tokens | projected at 10× tokens |
|---|---:|---:|---:|
| merged | 0.425 (0.394–0.456) | 719 (688–752) | 1,425 (1,306–1,564) |
| unmerged | 0.454 (0.422–0.484) | 822 (790–858) | 1,706 (1,567–1,865) |

Heaps law has no finite asymptote, so these are sample-size projections, **not
estimates of a fixed true alphabet**. Ten-fold extrapolation is especially
fragile. Its useful result is the absence of a plateau, and its 2× projection
agrees strikingly well with merged Chao1 despite being fit by a different
route.

## Zipf fit

A log–log least-squares fit of token count against frequency rank gives:

| inventory | exponent α | log–log R² |
|---|---:|---:|
| merged | 1.467 | .952 |
| unmerged | 1.431 | .960 |

This is a compact description of the heavy tail, not a classification test.
Finite samples from many generative processes yield approximately rank-power
curves, and the high R² is partly mechanical when hundreds of rare types share
counts of one or two.

## What this does and does not establish

It establishes that the attested merged inventory is far from a secure ceiling.
Under the main treatment, Chao1 and ACE put roughly 180–200 identifiable types
beyond the 515 observed, and a doubled corpus is projected to reach about 720.
The merge policy is load-bearing: the corresponding unmerged totals are about
810–825.

It does **not** identify a script type. Inventory size depends on allography,
composites, proper-name-like rarity, specialist notation, corpus sampling, and
the historical span represented. No threshold converts 700 estimated signs
into a decipherment claim. These estimates constrain future descriptions of
the sign list; they do not classify the system or assign a value to any sign.

## Reproduction

```bash
.venv/bin/python src/inventory_estimators.py
```

Derived results are in `data/parsed/inventory_estimates.json`.
