# Do signs associate with motifs?

Scripts: `src/sign_motif.py` (per-sign scan), `src/omnibus.py` (single omnibus test).

## The question

If certain signs appear only on elephant seals and never on unicorn seals, that
links something unreadable (the signs) to something visible (the animal). Motif
is recorded for 1622 of 2543 artifacts, so the test is possible.

## The two traps

**Confounding.** Motif is entangled with object type and site. The unicorn is
overwhelmingly a *seal* motif, and seals are overwhelmingly Mohenjo-daro. A
naive test rediscovers sign-vs-site and mislabels it iconography. Handled by
conditioning on site x object class (52-53 strata) and by permuting motif labels
*within* strata, so the null preserves all confounding structure.

**Duplicate texts.** This one nearly produced a false result. 243 of 1505
motif-bearing artifacts carry a text identical to another artifact's. One
11-sign text appears **11 times, every copy on a rhinoceros**. Another appears
10 times, all elephant. Those are not 11 independent observations of a
sign-rhinoceros association; they are one observation stamped 11 times.

## Result 1 — per-sign scan (74 signs x 9-10 motifs)

| | with duplicates | deduplicated |
|---|---|---|
| raw p < .05 | 67 / 810 | 12 / 666 |
| BH q < .05 | **25** | **0** |
| permutation null, mean discoveries | 0.23 | 0.18 |

With duplicates left in, 25 associations survive correction against a null that
produces 0.23 — apparently overwhelming. Collapse each distinct (text, motif)
pair to one observation and **all 25 vanish**. Nine of the 25 were rhinoceros
hits, i.e. that one 11-fold text.

The null result is properly calibrated, not merely a failure to clear a bar.
Under stratified permutation this test yields raw p<.05 at a rate of **1.8%**
(the CMH test is conservative with sparse strata, so 5% is not the right
reference). The observed rate is **12/666 = 1.8%** — exactly the null rate.
There is no excess signal whatsoever at the level of individual signs.

## Result 2 — omnibus test (better powered)

666 separate tests is a punishing correction. Asking once instead: treat each
artifact as a binary sign vector, take Jaccard distances, and test with a
PERMANOVA pseudo-F whether artifacts sharing a motif are more similar than
chance — permuting within the same strata. 2000 permutations.

| | pseudo-F | p | variance explained |
|---|---|---|---|
| with duplicates | 2.95 | **0.0005** | 1.89% |
| deduplicated | 1.58 | **0.069** | 1.05% |

## What this actually means

**The headline finding is negative, with a caveat.** After removing duplicate
texts and controlling for site and object type, no individual sign is
associated with any motif — the scan sits exactly on its own null. The omnibus
test, which has real power, lands at p = 0.069: a hint, not a result.

And even taken at face value the effect is trivially small. **Motif explains
about 1% of the variation in sign content.** Whatever governs which signs go on
an object, it is essentially not the animal.

**The duplicate-handling choice is doing enormous work** and deserves to be
stated rather than buried. Deduplication is the conservative call and it is the
right one for a significance test, because the copies are not independent
draws. But it is not obviously the right call *substantively*: if a workshop
repeatedly stamped one particular text onto rhinoceros seals, that is a real
regularity about Indus practice, just not one that 11 copies give 11 votes on.
The honest summary is that the truth lies between p=0.0005 and p=0.069, and the
data cannot currently separate "signs track motifs" from "some texts were mass
produced."

**Power is the binding constraint, not the method.** After dedup the smaller
motif classes are tiny: water buffalo 15, fish 17, tree 20, elephant 33,
rhinoceros 41. Nothing short of a much larger corpus will resolve a 1% effect
in classes that size.

## Candidates, explicitly post-hoc

Strongest raw signals after dedup, none surviving correction, listed only as
things to pre-register against new data — not as findings:

| sign | motif | OR | k/n | raw p |
|---|---|---|---|---|
| 820 | rhinoceros | 6.19 | 8/41 | 0.00024 |
| 460 | tree | inf | 4/20 | 0.0011 |
| 416 | rhinoceros | 11.63 | 2/41 | 0.0075 |
| 100 | gaur | 2.96 | 8/86 | 0.0096 |

Sign 820 with rhinoceros is the only one whose raw p would clear a
pre-registered single test. Treat it as a hypothesis, not a result.
