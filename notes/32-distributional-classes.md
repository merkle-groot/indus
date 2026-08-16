# Distributional class induction does not clear its known-group test

Script: `src/distributional_classes.py`. The previous rounds mostly tested
specified signs or pairs. This round asks whether sign classes emerge from
two-sided context vectors without being named in advance.

## Corpus, threshold, and positional control

The script uses the direction-corrected `lines_merged.json` and keeps one copy
of a sequence per site and object class: **2086 records, 527 signs**.

A sign needs **at least 20 deduplicated tokens**. This is the same practical
floor used by earlier pair tests. A left-plus-right context vector has at most
about two observed neighbor events per token; below 20, fewer than roughly 40
events are divided across more than a thousand possible context cells. The cut
retains **80 signs** and excludes 447. It is not claimed to make the 80 dense;
it only prevents the rarest tail from determining the decomposition.

Raw contexts would rediscover position. For every focal-sign/neighbor cell the
script computes the exact expected count under independent absolute-column
shuffles within **text length x site x object class**. The features are clipped
signed Pearson residuals `(observed - expected) / sqrt(expected + .5)`, with
left and right neighbors kept separate. This removes an ending sign's free
association with the edge and holds both metadata controls fixed.

Rows are normalized, reduced to ten dimensions by SVD, normalized again, and
clustered by k-means. The cluster count is chosen by silhouette over **k =
2...15**, without reference to any known sign set.

## The evaluation gate came first

Three known groups are evaluated before any novel cluster can be printed:

- all seven terminal-paradigm members are eligible: 151, 156, 390, 520, 527,
  617, 740
- eleven established stroke numerals are eligible: 1, 2, 3, 4, 5, 16, 17,
  31, 32, 33, 55
- six fish-family signs are eligible: 220, 226, 231, 233, 235, 240

For a group to count as recovered, one cluster must contain at least 70% of its
eligible members, at least 50% of that cluster must belong to the group, its
within-group pair coassignment must beat 100 position-shuffled pipeline runs at
p <= .05, and the median within-group pair must co-cluster in at least 70% of
200 stratified text bootstraps. These criteria were fixed before memberships
were inspected. All three known groups had to pass before exploration.

## Label-free selection is itself unstable

The original sample chooses **k = 14**, silhouette **0.2576**. The next choices
are close: k=15 scores .2495 and k=13 scores .2483. Across text bootstraps the
chosen k has median 14 but a **95% range of 9–15**. The corpus does not strongly
determine the granularity of its partition.

## Known-group results, next to the control

“Pair rate” is the share of pairs inside the known group assigned to one
cluster. The null is the same statistic after exact position/site/object column
shuffling. Bootstrap stability is the median coassignment probability across
the known group's pairs.

| known group | eligible | best overlap / cluster size | recall | precision | pair rate | position-null mean (97.5%) | p | bootstrap pair median | pass |
|---|---:|---:|---:|---:|---:|---:|---:|---:|:---:|
| terminal | 7 | 2 / 4 | **28.6%** | 50.0% | 9.5% | 6.1% (16.8%) | .337 | **4.5%** | no |
| numerals | 11 | 5 / 6 | **45.5%** | 83.3% | 18.2% | 7.0% (12.7%) | .020 | **2.5%** | no |
| fish variants | 6 | 5 / 5 | **83.3%** | **100%** | 66.7% | 6.5% (20.0%) | .010 | **21.0%** | no |

### Terminal paradigm: not recovered

The seven signs fragment across four clusters. The largest overlap is only 156
and 390, in a four-member cluster also containing 407 and 900. This is not a
near miss. Its pair rate is ordinary under the positional null and its
bootstrap stability is almost zero.

This does not contradict [12-slots.md](12-slots.md). The terminal group was
established primarily by **mutual exclusion**, while this method represents
immediate left/right neighbors after removing edge position. A context-vector
clustering that cannot reconstruct the group has failed its evaluation; it has
not retested the exclusion evidence directly.

### Numerals: a real fragment, not the class

Signs 3, 4, 5, 16, and 17 form five of a six-member cluster; 61 is the outsider.
That coassignment exceeds the positional null. But six other eligible numerals,
including the frequent 1, 2, 31, 32, 33, and 55, split elsewhere, so recall is
only 45.5%. More decisively, the median numeral pair co-clusters in only **2.5%
of bootstraps**. The attractive five-sign subset is not a stable recovery of the
known numeral class.

### Fish variants: the point estimate works and the bootstrap does not

Five signs—220, 231, 233, 235, and 240—form a pure cluster. Only the eligible
flanked sign 226 falls outside. This is well beyond the position-shuffled null
and is the best result of the three anchors.

It still fails the predeclared stability test: the median pair coassigns in only
**21%** of text bootstraps, far below 70%. With only 80 sparse rows, small
changes in sampled texts rotate the SVD space and change both k and cluster
boundaries. Reporting the five-member point estimate as an induced class would
hide that dependence.

## Verdict

**This corpus does not support unsupervised sign-class induction at this
size.** The controlled SVD/k-means pipeline misses the terminal paradigm,
recovers less than half the numerals, and produces an appealing but unstable
five-fish cluster. None passes all of recall, purity, positional-null, and
bootstrap criteria.

The exploration gate therefore remains closed. The script deliberately prints
no novel cluster memberships and this note reports none. Adjusting the token
threshold, SVD dimension, k range, or recovery rule after seeing these results
would train on the three examples rather than evaluate class induction.

This is a method-and-sample-size failure, not evidence that distributional
classes do not exist. It says that at 2086 short texts, controlled immediate
contexts are not sufficient to recover even the classes already supported by
independent epigraphic tests.
