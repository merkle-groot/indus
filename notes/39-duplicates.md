# 39 — Most surplus copies are local, but a third of copied texts circulate

## Result

The 2,613 transcribed lines contain 1,929 exact merged sequence types. Most are
singletons, but **250 types recur**, creating 684 attestations beyond the first.
Those excess attestations decompose cleanly:

| source of an additional attestation | count | share |
|---|---:|---:|
| another copy at a site already holding the text | **577** | **84.4%** |
| the first attestation at an additional site | **107** | **15.6%** |
| total beyond one per sequence | 684 | 100% |

Thus repetition is mainly local production, but circulation is not negligible.
Of the 250 repeated sequence types, **163 (65.2%) occur at one site** and **87
(34.8%) at two to four sites**. The two most geographically widespread short
texts appear at four sites; the numerically most copied text appears 33 times
across three sites and three object classes.

After controlling site and object class, locally copied texts are shorter and
use a narrower vocabulary than singleton texts. Their terminal-sign
distribution, however, is not unusually different once their heavy tablet
concentration and length are held fixed. This is evidence about production and
circulation of objects, not about sign values or language.

## What counts as a copy

Two levels answer different questions.

1. A **global sequence type** is one exact sign tuple regardless of metadata.
   Its raw count measures recurrence and its site count measures circulation.
2. A **local analytical unit** is one exact `(text, site, object class)` key,
   the same unit used for deduplication in rounds 31–38. A key with raw
   multiplicity greater than one is “locally copied.” It gets one vote in the
   structural comparison; its discarded multiplicity is the outcome, not a
   weight.

The second definition reproduces the project's data reduction exactly: 2,613
raw lines become 2,086 units, comprising 1,878 singleton keys and 208 copied
keys. The latter account for all **527 discarded within-stratum copies**.

Only eight excess rows repeat the same sequence on the same artefact. Most
duplication therefore represents distinct catalogue artefacts, not duplicate
database rows. A repeated line on one multi-line artefact may still be a real
layout phenomenon; it is reported rather than silently deleted.

## Copy-count distribution

| raw attestations of a sequence | sequence types |
|---:|---:|
| 1 | **1,679** |
| 2 | 131 |
| 3 | 50 |
| 4 | 21 |
| 5 | 12 |
| 6 | 8 |
| 7 | 9 |
| 8 | 7 |
| 9 | 1 |
| 10 | 3 |
| 11 | 2 |
| 12 | 1 |
| 17 | 1 |
| 29 | 2 |
| 30 | 1 |
| 33 | 1 |

The distribution is extremely concentrated: 87.0% of sequence types occur
once, while four types account for 121 raw attestations. There is no forty-copy
text in the corrected merged data; the observed maximum is 33.

Copy count is negatively associated with length across all 1,929 types
(Spearman ρ = **−.255**, p = 4.5×10⁻³⁰). Singleton types average 4.71 signs;
repeated types average 3.29. The controlled analysis below shows that this is
not merely because copied objects are disproportionately tablets.

## The most-copied sequences

| sequence | copies | length | terminal | sites | object classes |
|---|---:|---:|---:|---|---|
| `3 156` | **33** | 2 | 156 | SI2 26; SI1 6; SI29 1 | tablet 24; seal 7; sealing/tag 2 |
| `176 740 400` | **30** | 3 | 400 | SI2 29; SI1 1 | tablet 26; seal 2; rod 1; unknown 1 |
| `501 407 2 240 520` | **29** | 5 | 520 | **SI2 29** | **tablet 29** |
| `503 615 752 740` | **29** | 4 | 740 | **SI1 29** | tablet 25; unknown 4 |
| `33 700` | 17 | 2 | 700 | SI2 16; SI44 1 | tablet 14; pottery 2; unknown 1 |
| `235 705 33 845 407 321 407` | 12 | 7 | 407 | **SI1 12** | **tablet 12** |
| `803 415 220 318 920 255 436 690 590 407 740` | 11 | 11 | 740 | **SI2 11** | tablet 10; unknown 1 |
| `817 2 48 740` | 11 | 4 | 740 | SI29 10; SI1 1 | sealing/tag 10; seal 1 |
| `415 220 520` | 10 | 3 | 520 | SI2 9; SI1 1 | tablet 9; seal 1 |
| `630 740` | 10 | 2 | 740 | SI1 9; SI2 1 | tablet 10 |
| `806 845 61 407 850 900 740` | 10 | 7 | 740 | **SI1 10** | **tablet 10** |
| `840 32 740` | 9 | 3 | 740 | SI2 7; SI1 1; SI29 1 | tablet 7; seal 1; unknown 1 |

The table contains both phenomena the brief distinguished. The two 29-copy
texts are locally concentrated mass production: one occurs entirely at SI2 on
tablets, the other entirely at SI1 and mainly on tablets. In contrast, `3 156`
crosses three sites and three media, while `176 740 400` crosses two sites and
four object classes despite its SI2 tablet concentration.

Copied texts have no single length or terminal sign. Two of the top four are
very short; two are four or five signs. The list includes several terminal-set
members but also 400, 407, and 700. The controlled distribution test below is
therefore more informative than describing the top few.

## Site-local production versus circulation

| sites carrying a repeated type | repeated sequence types |
|---:|---:|
| 1 | **163** |
| 2 | 69 |
| 3 | 16 |
| 4 | 2 |

The widest-circulating sequences are not the most numerous:

| sequence | total attestations | sites | object classes |
|---|---:|---|---|
| `817 2` | 8 | SI2 3; SI13 3; SI16 1; SI25 1 | seal 5; tablet 3 |
| `61 740` | 6 | SI2 3; SI1 1; SI13 1; SI47 1 | seal 5; unknown 1 |
| `3 156` | 33 | SI2 26; SI1 6; SI29 1 | tablet, seal, sealing/tag |
| `840 32 740` | 9 | SI2 7; SI1 1; SI29 1 | tablet, seal, unknown |
| `13 840 740` | 7 | SI2 4; SI1 2; SI29 1 | seal 4; tablet 3 |
| `32 700` | 7 | SI2 5; SI22 1; SI25 1 | tablet 7 |
| `142 617` | 6 | SI1 3; SI2 2; SI3 1 | tablet, seal, unknown |

This separates count from reach. `817 2` and `61 740` have modest totals but
the broadest site distributions. The 29-copy tablet sequences have enormous
local depth and no geographical reach. “Copied text” is therefore not one
archaeological process.

## Object class is the major confound

Among the 2,086 one-vote local units:

| object class | units | copied units | copied rate | copied / singleton mean length |
|---|---:|---:|---:|---:|
| tablet | 451 | **144** | **31.9%** | 3.63 / 3.72 |
| sealing/tag | 29 | 5 | 17.2% | 4.60 / 4.29 |
| rod | 14 | 3 | 21.4% | 4.33 / 3.36 |
| pottery | 59 | 5 | 8.5% | 2.40 / 2.59 |
| seal | 1,353 | 46 | **3.4%** | 2.65 / 4.85 |
| unknown | 162 | 5 | 3.1% | 2.80 / 4.04 |

Small object classes are descriptive only. The large contrast is tablets
versus seals: a tablet unit is about nine times as likely as a seal unit to have
local copies. This independently sharpens note 14's medium difference. It is
also why an uncontrolled copied-versus-singleton comparison would be mostly an
object-class comparison.

## Controlled structural comparison

For length, copy labels are shuffled 5,000 times within exact `(site, object)`
strata. For vocabulary and terminal tests, labels are shuffled within exact
`(site, object, length)` strata. This preserves the observed number of copied
units in every metadata stratum, and for the latter tests preserves their whole
length profile. Respectively 1,917 and 1,290 units lie in strata where both
labels occur and can actually exchange.

### Length and vocabulary

| outcome | copied vs singleton observed | controlled null mean (95%) | p |
|---|---:|---:|---:|
| mean-length difference | **−1.101 signs** (3.40 vs 4.50) | −0.471 (−0.685 to −0.247) | **.0004** |
| vocabulary in 208 copied units | **157 signs** | 183.4 (171–196) | **.0004** |

Even after the null builds in tablet/seal/site composition, copied units are
about 0.63 signs shorter than expected beyond the metadata effect. At identical
site, object, and length profiles they use about 26 fewer sign types than a
random 208-unit subset. Local replication therefore selects a narrower,
shorter repertoire.

The vocabulary result is not the trivial comparison 157 versus the singleton
inventory of 514; the controlled null always assigns exactly 208 copy labels
inside the same length and metadata strata.

### Terminal distribution

| outcome | observed copied − singleton | controlled null mean (95%) | p |
|---|---:|---:|---:|
| ends in fixed seven-sign terminal cohort | −5.11 percentage points | −13.16 (−19.52 to −7.24) | **.0116** |
| total-variation distance over all terminal IDs | 0.293 | 0.350 (0.298–0.403) | upper p = .982 |

Copied texts raw-end in the fixed terminal cohort slightly *less* often than
singletons (51.9% versus 57.0%). But their tablet-heavy composition predicts a
much larger 13.2-point deficit. Conditional on site, object, and length, the
copied subset is actually about eight percentage points **more** terminal-cohort
heavy than expected.

That aggregate residual does not reduce to one terminal sign. Thirteen final
signs have at least 20 units; **none survives BH** in sign-by-sign copy tests.
Sign 156 is nominally enriched (10 copied units versus 5.15 expected,
p = .0436), but it fails the 13-test correction. The full terminal-identity
distribution is no more different than the controlled null—in fact its total
variation is slightly smaller. The honest result is a modest cohort-level
shift, not a special copied-text ending.

## Circulation, not decipherment

The duplicate data support a production account with at least two modes:

- deep local replication, concentrated especially on tablets;
- shallow cross-site circulation of a smaller set of short sequences across
  seals, tablets, tags, pottery, and unknown objects.

Local copies are shorter and draw from a restricted repertoire even after
medium and site are controlled. That pattern is consistent with standardized
object production, but the corpus contains no direct record of workshops,
chronology, ownership, or use. “Mass-produced” describes recurrence in the
catalogue; it does not establish a manufacturing technique or the function of
the tablet.

This is why deduplication remains mandatory for distributional script tests:
letting the 29 identical tablets vote 29 times would turn a production fact
into an apparent sign-order rule. Once removed from those tests, however, the
27 discarded votes are valuable evidence about the objects themselves. Notes
14 and 15 reached the boundary between medium and site; the duplicates show
that circulation and replication are another dimension of the same problem.
No sign value or language assignment follows.

## Reproduction

```bash
.venv/bin/python src/duplicate_circulation.py
```

Derived counts, the 20 most-copied and widest-circulating sequences, all
terminal-sign tests, and object-class tables are in
`data/parsed/duplicate_circulation.json`.
