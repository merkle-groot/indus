# Partial pooling finds three rare text-final candidates, with a model warning

Script: `src/hierarchical_finality.py`. The project normally drops signs below
20 tokens. On the merged inventory that leaves 447 of 527 signs outside a
standard per-sign test. Partial pooling cannot create attestations, but it can
put every sign on the same uncertainty scale.

## Model: a conditional positional baseline

The analysis uses **2086 deduplicated sequence x site x object records**, 9159
tokens, and all 527 merged signs. Exactly one of those tokens is final in each
text, so the corpus token-level base rate is **2086/9159 = 22.775%**.

For text *t*, the observed final token is treated as a choice among that text's
own positions:

```
P(position i is final | text t) = exp(u[sign_i]) / sum_j exp(u[sign_j])
```

This is a hierarchical conditional-logistic model. Each sign has a random
effect `u_sign ~ Normal(0, tau^2)`, and `tau` has a half-normal hyperprior. The
conditional likelihood is the control:

- a neutral sign has probability `1 / text length`, the exact within-text
  positional-shuffle baseline
- the alternatives come from the **same text**, so length, site, object class,
  and the complete sign multiset are held fixed
- site and object main effects are constant within a text and cancel; they are
  conditioned out rather than estimated from between-stratum differences

The posterior is a hand-rolled full-Hessian Laplace approximation, one of the
methods allowed in the brief. No new package was required. Under the main prior
the optimizer converges in 39 iterations, maximum gradient 0.00026, and the
Hessian's minimum eigenvalue is 3.60; no eigenvalue needed repair.

To report a common adjusted probability rather than each sign's raw mixture of
text lengths, a sign with effect *u* competes with `L-1` neutral positions over
the corpus's token-weighted length distribution. At `u=0` this standardization
is exactly the 22.775% corpus base rate.

The complete table of posterior means and 95% intervals for **all 527 signs** is
in `data/parsed/finality_posterior.json`. The note prints the validation group
and every rare positive result rather than 527 rows.

## The known terminal members all validate the model

| sign | tokens | final | raw final rate | adjusted posterior P(final), mean (95%) | P(above base) |
|---:|---:|---:|---:|---:|---:|
| 151 | 61 | 54 | 88.5% | 62.0% (50.7–72.4%) | >.999 |
| 156 | 78 | 63 | 80.8% | 59.1% (48.3–69.5%) | >.999 |
| 390 | 184 | 88 | 47.8% | 45.5% (38.4–52.9%) | >.999 |
| 520 | 179 | 154 | 86.0% | 72.9% (65.8–79.3%) | >.999 |
| 527 | 53 | 47 | 88.7% | 58.1% (46.7–69.0%) | >.999 |
| 617 | 49 | 32 | 65.3% | 45.2% (34.2–56.6%) | >.999 |
| 740 | 1011 | 741 | 73.3% | 76.1% (72.9–79.2%) | >.999 |
| **neutral base** | — | — | **22.8%** | **22.8%** | — |

All seven independently established members have posterior probability above
the base in effectively every draw. The strong terminal structure survives
shrinkage and the exact within-text control.

## The payoff: three of 416 rare identifiable non-numerals

There are **416 identifiable non-numeral signs below 20 tokens** after removing
known stroke numerals and the digitizer's unidentified-glyph markers. Only
three have a 95% adjusted interval wholly above the base; none has an interval
wholly below it.

| sign | tokens | final | raw rate | adjusted posterior mean (95%) | P(above base) | finals with an earlier known terminal filler |
|---:|---:|---:|---:|---:|---:|---:|
| **621** | 17 | 13 | 76.5% | **42.9% (29.8–56.8%)** | .999 | **10/13** |
| **679** | 12 | 10 | 83.3% | **42.5% (28.5–57.4%)** | .999 | **9/10** |
| **161** | 13 | 11 | 84.6% | **36.2% (23.8–49.8%)** | .983 | 2/11 |

The amount of shrinkage is the point. Raw rates of 77–85% become posterior
means of 36–43%, and the other 413 rare signs retain intervals crossing the
base. Partial pooling does not turn the rare tail into hundreds of findings.

These are candidates for **text-final behavior**, not automatically new
members of the 740/520 exclusion paradigm. The context distinguishes them:

- sign 679 directly follows 740 in **9 of its 10** final occurrences
- sign 621 most often follows 740, 390, or 520; ten of thirteen finals have an
  earlier known terminal filler
- sign 161 has an earlier known filler in only two of eleven finals

Thus 621 and 679 look like rare additions *after* the floating terminal slot,
parallel in position to the already-known 400/90 material. Sign 161 is the
cleaner candidate for a terminal filler, but it still needs the exclusion test
that its 13 tokens cannot power. A final-position model alone cannot decide the
difference.

## Prior sensitivity

The half-normal scale on `tau` was fitted at **A = 0.5, 1, and 2**. This is a
fourfold range from narrow to wide.

| hyperprior A | posterior tau mean (95%) | rare intervals wholly above base | candidates |
|---:|---:|---:|---|
| 0.5 | .356 (.314–.402) | 3 | 161, 621, 679 |
| **1.0** | **.356 (.316–.402)** | **3** | **161, 621, 679** |
| 2.0 | .357 (.314–.404) | 3 | 161, 621, 679 |

The inferred pooling scale and candidate set do not move. The data overwhelm
this particular hyperprior choice because 527 effects inform the common scale.
This does not test sensitivity to the likelihood or to the allograph map.

## Posterior predictive checks: the warning

Each predictive draw chooses exactly one final token from each observed text,
so length, site, object, and text vocabulary remain fixed in the check.

| statistic | observed | posterior-predictive mean | 95% interval | two-sided p |
|---|---:|---:|---:|---:|
| known-terminal share | **.565** | .514 | .495–.533 | .004 |
| 740 share | .355 | .343 | .326–.359 | .196 |
| top-10 final-sign share | **.717** | .639 | .618–.661 | .004 |
| distinct final signs | **210** | 253.9 | 238–270 | .004 |
| Mohenjo-daro known-terminal share | **.627** | .558 | .532–.585 | .004 |
| Harappa known-terminal share | .458 | .445 | .419–.475 | .395 |
| seal known-terminal share | **.636** | .563 | .539–.586 | .004 |
| tablet known-terminal share | .404 | .421 | .389–.455 | .335 |

The model reproduces 740, Harappa, and tablets, but it **underestimates the
concentration** of endings overall, especially on Mohenjo-daro seals. It spreads
predictive final tokens over about 254 signs where 210 are observed. One shared
Gaussian distribution of sign effects is not a full model of the terminal
paradigm, its exclusions, or medium-specific deployment.

That failure does not manufacture the three rare high effects; if anything the
model is visibly pulling extremes too hard toward the middle. But their
intervals are conditional on a likelihood that misses part of the structure.
They should be treated as candidates for direct re-testing in a larger corpus,
not promoted to established terminal signs.

## Verdict

Partial pooling makes a modest breach in the wall: every sign now receives an
estimate, all seven known terminal members validate, and **3 of 416** previously
untestable identifiable non-numerals have intervals above the corpus base rate.
The result is stable across the specified priors.

It does not remove the wall. Four hundred thirteen rare signs remain
indeterminate, two of the three hits appear to be post-terminal additions, and
the posterior predictive distribution is too diffuse. The concrete gain is a
three-sign candidate list with explicit uncertainty, not a recovered rare-sign
system.
