# 36 — All four headlines replicate; the exploratory paradigm scan is mildly inflated

## Result

The four fixed headline findings replicate in both halves of a random split and
on both sides of a disjoint site split:

- repeat avoidance;
- 740/520 exclusion;
- final concentration of the seven-member terminal set;
- sign-specific numeral-side overdispersion.

The by-site result is the more important one. SI1 supplies 1,065 records and all
other sites 1,021; no site appears in both samples. Every effect retains the
same direction and clears the controlled 95% interval in both.

The pipeline calibration is reassuring but not immaculate. Pairwise BH scans
produce a false discovery in **1/300 = 0.33%** of pairing-destroyed corpora, and
the full numeral-side pipeline returns p ≤ .05 in **4/300 = 1.33%**. Random
frequency-matched seven-sign “paradigms” pass the two-part paradigm rule **7.1%**
of the time, a little above nominal. That is a quantitative warning for future
exploration. All four established headlines nevertheless sit far outside the
corresponding empirical null distributions.

## Design fixed before looking at the halves

The input is 2,086 exact `(text, site, object class)` records from the corrected
`lines_merged.json`. The random split is performed inside every site × object
stratum, with odd records assigned randomly, yielding halves of 1,045 and
1,041. The geographical split is SI1 versus every other site. SI1 is used
because it is the one site whose 1,065 records alone balance the remaining
1,021; this is a corpus partition, not a site chosen for its outcome.

The four tests are fixed versions of previous results:

1. **No-repeat:** number of texts containing a repeated sign. Null signs are
   shuffled in each absolute slot within exact `(length, site, object)` strata.
2. **740/520:** number of texts containing both fixed signs, against the same
   exact-position/site/object shuffle.
3. **Terminal paradigm:** number of texts ending in one of the fixed set
   `{740, 520, 390, 151, 527, 617, 156}`. Its positional null shuffles signs
   within each text, holding its length, vocabulary, site, and object fixed.
4. **Numeral side:** note 28's Pearson overdispersion, with side labels shuffled
   inside exact `(length, focal position, site, object)` strata. Because a half
   contains half the events, the eligibility threshold is fixed at 8 rather
   than retrospectively retaining only full-corpus signs with 15.

There are 1,000 permutations per confirmation test. Every effect is reported
next to its null. Wilson intervals in the repeat and terminal tables describe
the observed proportions; the permutation interval describes the controlled
null, not sampling uncertainty.

## Random split

### No-repeat

| sample | N | repeated texts, rate (95% Wilson) | positional-null mean (95%) | z | lower p |
|---|---:|---:|---:|---:|---:|
| half 1 | 1,045 | 34, 3.25% (2.34–4.51%) | 127.7 (111–144) | **−11.03** | .001 |
| half 2 | 1,041 | 44, 4.23% (3.16–5.63%) | 116.9 (102–132) | **−9.16** | .001 |

### Fixed 740/520 exclusion

| sample | observed together | positional-null mean (95%) | z | lower p |
|---|---:|---:|---:|---:|
| half 1 | 2 | 14.80 (9–21) | **−4.16** | .001 |
| half 2 | 4 | 12.37 (7–18) | **−2.91** | .002 |

The effect is weaker in half 2 but remains outside every but one of 1,000 null
runs. It is a replicated fixed-pair result, not a new pair selected within each
half.

### Terminal-set finality

| sample | terminal-set finals, rate (95% Wilson) | within-text null mean (95%) | z | upper p |
|---|---:|---:|---:|---:|
| half 1 | 583, 55.8% (52.8–58.8%) | 195.5 (173–218) | **+33.24** | .001 |
| half 2 | 596, 57.3% (54.2–60.2%) | 204.0 (181–227) | **+33.75** | .001 |

### Numeral-side overdispersion

| sample | adjacency events / eligible signs | observed Q | controlled mean (95%) | excess Q | upper p |
|---|---:|---:|---:|---:|---:|
| half 1 | 1,198 / 41 | 472.0 | 314.0 (288.6–340.5) | **+158.0** | .001 |
| half 2 | 1,105 / 34 | 399.5 | 290.1 (265.8–314.9) | **+109.3** | .001 |

All four pass independently in both random halves. The effect sizes differ by
ordinary sampling amounts, but no finding depends on one favourable partition.

## Disjoint site split

### No-repeat and 740/520

| sample | N | repeated texts | repeat null (95%) | repeat z | 740/520 observed | pair null (95%) | pair z |
|---|---:|---:|---:|---:|---:|---:|---:|
| SI1 | 1,065 | 41 (3.85%; 2.85–5.18%) | 145.8 (129–163) | **−12.00** | 6 | 19.60 (13–26) | **−3.90** |
| all other sites | 1,021 | 37 (3.62%; 2.64–4.96%) | 105.9 (92–121) | **−9.44** | 0 | 8.20 (4–13) | **−3.37** |

Both one-sided permutation p-values are ≤ .002. The raw 740/520 allocation is
geographically uneven—six co-occurrences at SI1 and none elsewhere—but the
depletion relative to each sample's own positional expectation occurs in both.

### Terminal set and numeral side

| sample | terminal final rate (95% Wilson) | final null (95%) | final z | numeral Q | side null (95%) | excess Q |
|---|---:|---:|---:|---:|---:|---:|
| SI1 | 62.7% (59.8–65.6%) | 200.9 (179–225) | **+39.18** | 513.5 | 310.8 (284.0–337.8) | **+202.7** |
| all other sites | 50.0% (47.0–53.1%) | 199.6 (178–222) | **+28.11** | 355.6 | 274.0 (252.7–296.7) | **+81.5** |

All p-values are .001. SI1 has the stronger terminal concentration and side
heterogeneity, which agrees with the site's distinct form distribution in note
15. The other-site half is not a weakened version obtained by sharing signs or
texts with SI1: it is a disjoint geographical confirmation.

## Empirical calibration

### Pairing-destroyed corpora

I generated 300 corpora by shuffling every absolute slot within exact
`(length, site, object)` strata. Each surrogate preserves:

- the complete length distribution;
- each position's frequency spectrum;
- site and object composition;
- every sign's overall and positional frequency;

and destroys only which signs are paired in one text. These are the required
surrogates, not independent frequency draws.

| pipeline output | real corpus | surrogate mean (95%) | empirical lower/upper p | empirical false-positive rate |
|---|---:|---:|---:|---:|
| texts with a repeat | **78** | 251.0 (230–273) | lower .0033 | 5.7% at the discrete 5% cutoff |
| 740/520 together | **6** | 27.69 (20–35.5) | lower .0033 | 7.3% at the discrete 5% cutoff |
| any BH exclusion among 3,160 pairs | **yes; min z −5.47** | 1 of 300 corpora | — | **0.33% familywise** |
| numeral-side pipeline | excess Q **+297.8** | excess Q −2.1 (−27.3–23.4) | upper .001 internally | **1.33%** |

The first two false-positive rates use empirical fifth-percentile cutoffs and
are slightly above 5% because count distributions have ties. The more useful
numbers are the exploratory familywise scan and the complete side pipeline:
neither is anti-conservative in these surrogates.

### Fabricated hypotheses in the real corpus

Random labels can still encounter real structure, so I also fabricated
hypotheses rather than only fabricating corpora.

For 5,000 random pairs among the 80 signs attested in at least 20 texts, 4.66%
have nominal lower-tail p < .05. That is almost exactly calibrated. However,
**0.20%** cross the single-pair Bonferroni threshold for 3,160 possible pairs,
far above the mathematical null expectation. These are not necessarily false
relationships—the labels are random but the corpus contains real exclusions.
The result says that choosing a pair after browsing remains dangerous even
when the individual z looks spectacular.

For 5,000 synthetic seven-sign “paradigms,” each member was frequency-rank
matched within five ranks to a member of the known terminal set. A synthetic
set passes only if:

1. its within-text finality z is at least +1.645; and
2. one of its 21 internal pairs clears `.05 / 21` against the pairing null.

**7.06% pass.** This is the most direct estimate of the garden-of-forking-paths
cost in the old exploratory pipeline. It is modestly, not catastrophically,
above 5%; a newly noticed seven-sign paradigm should be treated as a hypothesis
until separately confirmed.

The established terminal set is nowhere near that border:

| | finality z | random-set 95% | best internal pair p | two-part pass |
|---|---:|---:|---:|:---:|
| known terminal set | **+47.47** | −15.51 to +7.32 | **9.3×10⁻⁸** | yes |

## Do the headlines sit outside the calibrated null?

Yes, explicitly:

- repeat count 78 is below the surrogate 95% range 230–273;
- 740/520 count 6 is below 20–35.5;
- the real pair scan reaches z = −5.47, while only one surrogate scan returns
  any BH discovery at all;
- numeral-side excess Q is +297.8 against a surrogate 95% range −27.3 to +23.4;
- terminal-set finality z = +47.5 exceeds the 97.5th percentile of matched
  fabricated sets, +7.32, and its internal exclusion also passes.

Thus the project's four fixed headlines survive a confirmatory reading. The
calibration does not vindicate every earlier marginal z. It puts a concrete
**7% false-positive price on exploratory paradigm construction** and a 4.7%
price on uncorrected browsed pairs. Those are the discount rates to carry into
future rounds.

## Reproduction

```bash
.venv/bin/python src/confirm_calibrate.py
```

Derived results are in `data/parsed/confirmation_calibration.json`.
