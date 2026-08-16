# Do seals and tablets use different templates?

Script: `src/objforms.py`. Seals identify somebody; tablets are mass-produced
tokens. If these texts are records, the two media should be filling out
different forms. Object class has only ever been a nuisance variable here.

## The confound leads the analysis

```
seals   : Mohenjo-daro 934, Harappa 256
tablets : Harappa      673, Mohenjo-daro 212
```

Medium and city are nearly the same variable. Every test is run **within each
city** and only then combined. Deduplicated counts:

| | seal | tablet |
|---|---|---|
| Mohenjo-daro | 928 | 83 |
| Harappa | 254 | 387 |

Mohenjo-daro's tablet sample is thin (83), so Harappa carries the weight.

## O1 — tablets are shorter, at Harappa

| | seal | tablet | p |
|---|---|---|---|
| Mohenjo-daro | 4.85 | 4.39 | .06 |
| Harappa | 4.73 | **3.51** | **9e-13** |

## O2 — same vocabulary

At Harappa the two media share 139 signs, and shared signs account for **89.4%**
of seal tokens and **88.4%** of tablet tokens. They are not writing in different
scripts or different registers. Whatever differs, it is not the inventory.

## O3 — the same slot, filled differently

The sharpest version of the question. [12-slots.md](12-slots.md) established a
terminal slot holding exactly one filler. What fills it?

**Harappa**

| ends the text | seal | tablet |
|---|---|---|
| 740 (jar) | **95 (37%)** | 92 (24%) |
| **400** | 9 (4%) | **118 (30%)** |
| 520 | 23 (9%) | 13 (3%) |
| 390 | 9 (4%) | 8 (2%) |

chi2 **p = 1.1e-14**. Mohenjo-daro, on its thin sample, agrees: p = 1.1e-04.

**Same structure, different value in one field.** That is exactly what "two
forms sharing a layout" looks like, and it is the strongest evidence in this
project for the record reading.

### What tablets actually do with 400

Not a straight substitution. Among texts ending in 400:

| | ends in 400 | of those, also contain 740 |
|---|---|---|
| seals | 45 | 10 (**22%**) |
| tablets | 124 | 75 (**60%**) |

Tablets are not replacing the jar sign with 400 — they are **appending 400
behind it**. That is the post-terminal position found independently in
[12-slots.md](12-slots.md) (400 follows 740 in 91 of 109 co-occurrences) and in
[13-growth.md](13-growth.md), where 400 was the single most-inserted sign. Three
different tests, one convention: **tablets add a sign after the ending that
seals leave off.**

## O4 — numerals go the wrong way

Prediction: tokens count things, identity seals do not. The data says the
opposite.

| | seal | tablet | p |
|---|---|---|---|
| Mohenjo-daro | **58.8%** | 43.4% | 7e-03 |
| Harappa | **61.0%** | 35.1% | 1e-10 |

Seals carry numerals far more often than tablets, consistently at both cities.
This also matches [11-unmarked-one.md](11-unmarked-one.md), where tablets wrote
the optional "1" at half the seal rate. **The mass-produced tokens are the ones
that do not count.** Whatever tablets are, they are not tallies, and the obvious
commodity-chit reading of them is wrong.

## O5 — which signs pick a medium

64 signs testable, **7** medium-specific at |z| > 3 (Mantel-Haenszel across the
two cities).

| most tablet-loaded | | most seal-loaded | |
|---|---|---|---|
| **400** | z = −8.6 | **2** | z = +7.9 |
| 176 | −2.6 | 820 | +3.6 |
| 100 | −2.4 | 60 | +3.3 |
| 435 | −2.2 | 817 | +3.3 |
| 700 | −2.2 | 31 | +3.1 |

Sign 400 is far and away the most medium-specific sign in the corpus. And the
seal-loaded list is the frozen collocation from [05-radix.md](05-radix.md) —
817, 820, 861 and the value-2 stroke, all together.

Checking that directly: the pattern "817/820/861 immediately followed by a 2"
appears in **18.5% of seal texts and 5.7% of tablet texts**. The formula is a
seal convention.

## Verdict

**Yes, and the difference is structural rather than lexical.** The two media
share a sign inventory and a slot layout, then differ in what they put in the
slots:

- tablets append **400** after the terminal sign; seals mostly do not
- seals carry the frozen **X+2** opening formula three times as often
- seals carry numerals nearly twice as often
- tablets are a sign shorter

The pieces line up with everything else: a fixed ending
([12-slots.md](12-slots.md)), growth at the front ([13-growth.md](13-growth.md)),
and now a medium-dependent choice of what goes in the last two positions.

Caveat: Mohenjo-daro contributes only 83 tablets, so the within-city replication
is one strong test and one weak one. The Harappa result is not in doubt; whether
it is a Harappa convention or a tablet convention is only partly separated.
