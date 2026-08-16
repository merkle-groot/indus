# Unsupervised segmentation fails its frozen ground truth

Script: `src/segmentation.py`. The corpus now has two kinds of structure strong
enough to use as an evaluation set: three frozen adjacent pairs and the terminal
slot. This note asks whether two ordinary unsupervised boundary scores recover
both before trusting anything else they propose.

## Corpus and control

The analysis uses **2036 deduplicated sequence-by-site texts** after allograph
merging and direction correction. They contain 6966 adjacent-boundary
occurrences of 2793 types.

Two scores are evaluated:

- **PMI:** an adjacent pair is joined when it occurs more often than expected;
  low association favours a cut.
- **branching entropy:** a boundary is favoured when the left sign has many
  possible continuations and the right sign has many possible predecessors.

Raw versions of both scores would rediscover position. The control therefore
shuffles every absolute column independently within exact text-length, site,
and object-class strata. The PMI score is observed against the resulting
expected bigram count. The branching score is observed context entropy minus
the entropy of the corresponding null context vector. Thus the effect and its
position/site/object control are the same quantities throughout.

No threshold was tuned on the known examples. Each method cuts at the median
score over all boundary occurrences, a label-free rule that asks it to cut
roughly half the corpus boundaries.

## First test: do not split the frozen pairs

The three must-join pairs are fixed in advance from
[22-two-forms-of-two.md](22-two-forms-of-two.md). Positive PMI residual means a
stronger join than the controlled null predicts. Positive branching residual
would favour a boundary; the median branching threshold is -4.640.

| frozen pair | observed | position/site/object expected | PMI join residual | branching residual | PMI decision | branching decision |
|---|---:|---:|---:|---:|---|---|
| 817+2 | 102 | 32.7 | +1.626 | -6.463 | join | join |
| 861+2 | 120 | 39.6 | +1.587 | -6.395 | join | join |
| 840+32 | 22 | 3.3 | +2.560 | -4.283 | join | **cut** |

PMI passes this small test: it protects all 244 occurrences of all three pair
types. Branching entropy fails it. It cuts all 22 occurrences of `840+32`, so
it protects only 222/244 frozen-pair occurrences.

## Second test: cut before the terminal slot

A known cut is the boundary immediately before one of the eight terminal
fillers established in [12-slots.md](12-slots.md). A filler still counts when
only the known post-terminal signs 400 or 90 follow it. This supplies **1343
must-cut occurrences of 298 boundary types**.

The table evaluates the frozen joins and terminal cuts together. Precision is
restricted to these labelled boundaries; unlabelled corpus boundaries are
unknown and are not silently called errors. “Join precision” is the share of
labelled join decisions that really are frozen pairs.

| method | frozen types kept | frozen occurrences kept | terminal recall | labelled cut precision | labelled join precision | AUC |
|---|---:|---:|---:|---:|---:|---:|
| controlled PMI | **3/3** | **244/244 = 100.0%** | 67.7% | 100.0% | 36.0% | .777 |
| controlled branching entropy | **2/3** | **222/244 = 91.0%** | 63.5% | 97.5% | 31.2% | .887 |
| cut only when both agree | **3/3** | **244/244 = 100.0%** | 54.3% | 100.0% | 28.4% | — |

The high cut precision is not enough. PMI misses 32.3% of known terminal
boundaries; branching entropy misses 36.5%. Requiring agreement protects the
phrases only by reducing terminal recall to 54.3%. The modest join precision
also shows that protecting a frozen pair does not make the other joined
boundaries reliable segment interiors.

## Verdict

**These methods do not segment this corpus reliably.** PMI recovers the three
frozen pairs but not a third of the known terminal cuts. Branching entropy both
misses more than a third of those cuts and breaks the independently established
`840+32` phrase. Their consensus is more conservative but less useful.

Because the ground-truth test fails, the script deliberately prints no novel
segment proposals and this note reports none as findings. The short texts and
sparse boundary-type counts do not support an unsupervised segmentation claim
from these local statistics.

## What this does not license

This is a failure of two local segmenters on this corpus, not evidence that the
texts have no internal units. It does not weaken the frozen-pair or terminal-slot
results used as ground truth. Nor does it justify adjusting thresholds until
those examples pass: with only three must-join types, that would turn evaluation
into training. Other models may fare better, but they need an equally explicit,
position- and metadata-controlled test before their proposed boundaries can be
treated as epigraphic structure.
