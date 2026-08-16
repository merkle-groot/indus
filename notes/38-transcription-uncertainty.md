# 38 — The headlines survive transcription noise; most marginal edges do not

## Result

A conservative sign-specific noise model changes a median **668 of 9,159
tokens** per draw—7.3%, essentially the observed inter-digitizer disagreement
rate. After perturbing sign identities, rededuplicating, and rebuilding every
positional/site/object control 300 times:

| fixed finding | exact-corpus controlled effect | noise median (95% interval) | significant in draws |
|---|---:|---:|---:|
| no-repeat, positional z | −14.85 | **−11.79 (−14.17 to −10.03)** | **100%** |
| 740/520 exclusion, positional z | −5.45 | **−3.81 (−5.31 to −2.50)** | **100%** |
| terminal-set finality z | +47.47 | **+44.52 (+43.69 to +45.22)** | **100%** |
| numeral-side controlled z | +16.09 | **+12.85 (+10.62 to +15.82)** | **100%** |

The effects expected to shrug off disagreement do. The old numerical z values
of −19.1 for no-repeat and −14.1 for 740/520 used earlier baselines; under the
required exact-position/site/object controls their starting values are −14.85
and −5.45. The substantive findings remain far outside their controls after
transcription error.

The marginal pair results are different. The initial 817/861/820 exclusion
triad from notes 05 and 12 survives in only **1.7–20%** of draws. Within the
terminal network, only 740/520 is fully robust; 520/390 is borderline, and most
other individual edges are fragile under the exact positional baseline even
before noise. Correction pointers have been added to the notes that carry
those claims.

## Building the noise model

Note 10 found 161 artefacts in two independent digitizations. Of 146 with the
same sign count, 778 positions have a sign-list crosswalk on our side:

| | count |
|---|---:|
| aligned mapped positions | 778 |
| agreements | 725 |
| disagreements | **53 (6.81%)** |
| disagreements whose alternative maps back into our list | 40 |
| alternatives absent from our reverse crosswalk | 13 |

The model uses no sign values—only opaque sign-list IDs.

For source sign `g`, its perturbation probability is

```text
(observed disagreements_g + 20 × 53/778) / (comparisons_g + 20)
```

This is empirical-Bayes partial pooling. Well-observed signs retain their own
rate; thin and unseen signs approach the global rate. Examples show why pooling
is necessary:

| sign | aligned comparisons | disagreements | raw rate | shrunken rate |
|---:|---:|---:|---:|---:|
| 740 | 82 | 7 | 8.5% | 8.2% |
| 390 | 26 | 1 | 3.8% | 5.1% |
| 520 | 16 | 2 | 12.5% | 9.3% |
| 817 | 13 | 1 | 7.7% | 7.2% |
| 156 | 6 | 0 | 0% | 5.2% |
| 151 | 3 | 0 | 0% | 5.9% |

Conditional on changing, a token takes one of the observed alternative
identities for that source. Five equivalent disagreements from the global
alternative distribution back off thin source-specific confusion tables. If
the alternative sign-list ID has no reverse crosswalk, it receives a distinct
opaque negative ID rather than being falsely assigned to a known sign.

This is deliberately conservative in two ways. Pairwise disagreement is an
upper bound on the chance that *our* transcription is wrong—some disagreements
are errors in the other digitization or in the crosswalk—and independent
perturbations apply that upper bound to every corpus token. The 300 draws change
622–716 tokens at their 95% limits. Rededuplication leaves 2,082–2,086 records.

## Rerun, not error bars pasted onto old z values

Every draw starts from the already deduplicated corrected corpus, samples every
sign identity once, and then deduplicates the resulting `(text, site, object)`
records again. It rebuilds:

- the no-repeat null by shuffling every absolute slot inside exact `(length,
  site, object)` strata;
- all fixed-pair exclusions with the same shuffles;
- terminal-set finality against within-text position shuffles;
- note 28's side overdispersion, shuffling side labels within exact `(length,
  focal position, site, object)` strata.

There are 60 inner null runs per noisy corpus. Their Monte Carlo variability is
therefore included in the quoted uncertainty intervals rather than hidden. The
exact-corpus baseline uses 1,000 runs.

## Headline details

### No-repeat

The exact corpus has 78 repeated texts against a positional-null mean of 252.
Across noisy corpora its controlled z never approaches −1.96; the least extreme
end of the 95% interval is −10.03. Sign substitutions do manufacture repeats,
as expected, but nowhere near the number expected if the observed positional
columns were independently paired.

This supersedes note 09's frequency-draw z = −19.1 with a stricter result that
includes deduplication, position, site, object class, and transcription error.

### Terminal cohort

The exact corpus ends 1,179/2,086 = 56.5% of texts with one of the fixed seven
terminal signs, against 400.4 expected when each text's own signs are shuffled.
Under transcription noise the observed final share is **52.95% (52.18–53.89%)**
and its finality z remains above +43.7. The cohort's position is exceptionally
robust even though several pairwise edges inside it are not.

### Numeral side

The exact-corpus Q excess is 297.0 above its position/site/object null. Under
noise it is **219.7 (193.4–248.9)**. The eligible set varies only from 34 to 38
signs at the 95% limits, and every controlled z remains above +10.6. The global
finding in note 28 is robust. This analysis does not revalidate each of note
28's 15 individual BH calls; marginal sign-level calls should not inherit the
global interval.

## Which exclusion edges are fragile?

All rows use an exact absolute-position × site × object shuffle. “Survival” is
the fraction of noisy draws with z ≤ −1.96.

| fixed pair | exact z | noise median (95%) | survival |
|---|---:|---:|---:|
| **740/520** | **−5.45** | **−3.81 (−5.31 to −2.50)** | **100%** |
| 520/390 | −3.44 | −2.96 (−3.88 to −1.77) | 95% |
| 740/617 | −2.32 | −1.96 (−2.94 to −0.83) | **50%** |
| 740/527 | −1.42 | −1.20 (−2.26 to −0.12) | 9% |
| 740/156 | −1.56 | −1.39 (−2.43 to −0.35) | 11% |
| 740/390 | +0.30 | +0.33 (−0.91 to +1.41) | 0% |
| 740/151 | +0.07 | +0.17 (−0.90 to +1.25) | 0% |
| 817/861 | −1.22 | −0.85 (−2.10 to +0.66) | **3.7%** |
| 817/820 | −1.86 | −1.45 (−2.47 to −0.17) | **20%** |
| 861/820 | −0.88 | −0.82 (−1.89 to +0.42) | **1.7%** |

This table separates two causes of fragility:

1. note 12's length-stratified z values were already weakened by the correct
   absolute-position baseline—two signs that occupy the same edge position
   under-co-occur partly for free;
2. transcription alternatives then move enough tokens among visually close
   IDs to wash out effects near z ≈ −2 to −3.

The revised claim is precise. **There is a transcription-robust terminal
cohort, anchored by a transcription-robust 740/520 exclusion. There is not a
transcription-robust dense graph in which every listed member excludes 740.**
The 520/390 edge is strong in 95% of draws but its 95% interval crosses −1.96,
so it remains “borderline,” not promoted to robust.

Likewise, the 817/861/820 triad should no longer be cited as a controlled
three-way exclusion. Other evidence about their adjacency and graphic relation
can stand; this particular marginal pair network cannot carry it.

## What is still missing

Fifteen of 161 shared artefacts differ in sign count. Equal-length alignment
cannot identify whether either transcription inserted, deleted, joined, or
split a sign, so the model conditions on text length and propagates **identity
uncertainty only**. Inventing random insertions would add assumptions not
learned from the disagreements. The quoted intervals are therefore not total
epigraphic uncertainty.

Errors may also be correlated within a damaged artefact, whereas the bootstrap
perturbs tokens independently. The conservative use of the full pairwise
disagreement rate partly offsets that limitation but does not solve it. More
independent aligned transcriptions—or image-level adjudication—would be needed
for a full edit-error model.

## Reproduction

```bash
.venv/bin/python src/transcription_uncertainty.py
```

Derived results, including every sign-specific shrunken rate, are in
`data/parsed/transcription_uncertainty.json`.
