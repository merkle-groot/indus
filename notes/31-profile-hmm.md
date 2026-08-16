# A profile HMM recovers the right edge, but not a corpus-wide template

Script: `src/profile_hmm.py`. [13-growth.md](13-growth.md) asked whether short
texts are long texts with holes by counting pairwise subsequences. A profile
HMM asks the question directly: how many ordered match positions are supported,
which positions may be deleted, and which signs fill each one?

## Evaluation was fixed before the fit

The analysis uses `lines_merged.json`, after the direction correction in
[27-direction.md](27-direction.md). One copy of each sequence is retained per
site and object class: **2613 lines become 2086 records**, with 527 attested
merged signs.

The model is a linear match/insert/delete profile. Each of *M* match states has
its own sign distribution and deletion probability. Insertion states occur
before, between, and after the matches; they share one emission distribution so
that increasing *M* does not buy *M* extra background vocabularies. The grid is
**M = 1...13**, ending at the observed maximum text length.

The deterministic 80/20 train/test split is stratified by text length, major
site, and object class. All likelihoods are conditional on observed text
length, so the HMM, unigram, and bigram answer the same question. Model width is
selected only by held-out log likelihood. No occupancy or known sign group is
used in fitting or selection.

Two control corpora are each fitted 20 times through the identical pipeline:

- **position control:** independently permute every absolute column within
  exact length x site x object strata. This keeps each sign's observed position
  and both metadata controls, while destroying which slot occupants travel
  together.
- **frequency control:** redistribute the exact tokens within site x object
  strata over texts of unchanged lengths. This keeps frequency, length, site,
  and object while destroying position and pairing.

A template was declared to survive only if it beat the bigram on held-out data
and its bigram advantage lay above 97.5% of **both** surrogate distributions.

## Held-out model selection

The selected real-corpus model has **12 match states**. It does beat the bigram,
but modestly.

| model | held-out nats/token | difference from unigram | difference from bigram |
|---|---:|---:|---:|
| unigram | -4.8086 | — | -0.0856 |
| bigram | -4.7230 | +0.0856 | — |
| **profile HMM, M=12** | **-4.6741** | **+0.1345** | **+0.0488** |

The peak is not just a truncated rising curve: M=11 scores -4.6928, M=12
-4.6741, and M=13 -4.6750. Several large fits reached the common 60-iteration
cap, applied identically to real and surrogate corpora; the near-tie between 12
and 13 is another reason not to read the selected integer literally.

The gain is not uniform across the required controls.

| held-out stratum | texts | tokens | HMM - unigram | HMM - bigram |
|---|---:|---:|---:|---:|
| Mohenjo-daro | 212 | 1003 | +0.1638 | +0.0340 |
| Harappa | 135 | 531 | +0.2117 | +0.0882 |
| other sites | 70 | 288 | -0.1100 | +0.0280 |
| seals | 272 | 1298 | +0.2260 | **+0.1085** |
| tablets | 88 | 319 | -0.0421 | **-0.1642** |
| other objects | 57 | 205 | -0.1706 | +0.0023 |

The apparent template is a seal result. On tablets the bigram is substantially
better than the selected profile. A single corpus-wide field count is already
hard to defend before looking at the null.

## The control rejects it

| corpus fitted through the same selection | selected M, median (95%) | HMM - unigram, mean (95%) | HMM - bigram, mean (95%) |
|---|---:|---:|---:|
| **real** | **12** | **+0.1345** | **+0.0488** |
| exact-position surrogate | 10 (5.5–13) | +0.0044 (-0.1128–+0.1131) | **+0.5539** (+0.4471–+0.6675) |
| frequency-matched surrogate | 1 (1–1.5) | -0.4535 (-0.5467–-0.3349) | **+0.2004** (+0.0798–+0.3293) |

Against both surrogate distributions, the one-sided empirical p for the real
HMM-minus-bigram improvement is **1.00**. The predeclared survival rule fails.

The size of the surrogate advantage needs care. Destroying real adjacent pairs
makes a fitted bigram poor, while a profile can still exploit absolute position
in the column-shuffled corpus. That is not evidence that the shuffled corpora
contain templates. It is exactly the warning: a profile HMM will fit positional
structure even when cross-position pairing has been destroyed. The real
HMM-minus-unigram gain is just above the position-null 95% interval, consistent
with genuine positional structure, but “better than a unigram” was not the bar.
A template had to beat the stronger sequence baseline in a way shuffled data
did not.

## What the selected profile aligned

The diagnostics explain why the model looked convincing. Occupancy is the
posterior share of training texts that emit from a match state rather than
delete it.

| match | occupancy | leading emissions | known terminal-set mass |
|---:|---:|---|---:|
| 1 | 11% | 32, 140, 491 | .015 |
| 2 | 62% | 820, 817, 861, 920 | .006 |
| 3 | 11% | 368, 455, 60 | .038 |
| 4 | 21% | 60, 390, 861 | .129 |
| 5 | 39% | 2, 741, 1 | .006 |
| 6 | 18% | 235, 798, 803 | .013 |
| 7 | 50% | 240, 32, 3, 233 | .007 |
| 8 | 22% | 220, 705, 706 | .026 |
| 9 | 32% | 33, 590, 17 | .014 |
| 10 | 40% | 760, 100, 390 | .059 |
| **11** | **94%** | **740, 520, 390, 156, 527, 151** | **.734** |
| 12 | 17% | **400, 90** | .027 |

The terminal paradigm appears cleanly. All seven pre-specified members—740,
520, 390, 151, 527, 617, and 156—are among match 11's top 20 emissions. Match
12 then absorbs the known post-terminal 400/90 material. This reproduces the
floating right-edge construction in [26-right-edge.md](26-right-edge.md)
without being told about it.

The rest is not a stable set of fields. Nine of twelve match states have under
50% occupancy, several split adjacent parts of already-known local expressions,
and the selected width changes freely in position-shuffled data. Calling those
nine states “optional fields” would convert a model's flexibility into an
epigraphic result.

## Verdict

**No corpus-wide template survives.** A 12-match profile has slightly better
held-out likelihood than the real-corpus bigram, but that advantage is smaller
than the advantages obtained on every controlled surrogate. It also reverses
on tablets. There is therefore no defensible answer of “twelve fields,” or of
any other field count, from this model.

The useful positive is narrower and already independently established: the HMM
finds a highly occupied terminal-paradigm state followed by a sparsely occupied
400/90 state. It sees the right edge and fails to establish comparable
corpus-wide structure. The stronger replacement for 13-growth is consequently
not a richer form; it is the same boundary found by the simpler controlled
tests.

This result assigns no reading to any sign. Match states are statistical
alignment positions, and their failure outside the right edge is a result about
this corpus and model, not evidence that the middle of every inscription is
unstructured.
