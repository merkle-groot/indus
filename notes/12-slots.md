# Turning the no-repeat rule into slots

Script: `src/slots.py`. [09-music.md](09-music.md) found that texts avoid
reusing a sign far below chance and proposed a form with slots, each filled
once. That predicts a second pattern: signs *competing* for a slot can never
appear together either, because the slot holds one value. Monday and Tuesday
never share a date field.

So: find every pair that co-occurs below chance, and see whether the pairs knit
into groups. A group of pairwise mutually exclusive signs is a slot recovered
from the data rather than assumed.

## Setup

2007 distinct multi-sign texts (deduplicated — mass-produced tablets would
manufacture any pattern), 77 signs appearing in ≥20 of them, 1069 testable
pairs. Every test is Mantel-Haenszel **stratified by text length**, because a
2-sign text cannot hold a pair at all and short texts under-co-occur for free.
Survivors are re-tested stratified by **site** and by **object class**, since two
signs from different cities never meet for reasons that have nothing to do with
grammar.

## The method works — one anchor passes, one fails

**Passes.** 817, 820 and 861 were shown mutually exclusive in
[05-radix.md](05-radix.md) by a completely different route. This method finds
them cold:

| pair | observed | expected | z |
|---|---|---|---|
| 817 / 861 | 1 | 12.4 | −3.59 |
| 817 / 820 | 1 | 11.9 | −3.48 |
| 861 / 820 | 4 | 14.2 | −3.01 |

**Fails.** The stroke numerals were the other anchor: if a text has one count
field, values should exclude each other. They do not.

```
1 vs 2   obs  24  exp 56.8  z -6.36
1 vs 4   obs  10  exp  3.5  z +3.70    <- co-occur MORE than chance
2 vs 4   obs  22  exp 13.2  z +3.02    <- likewise
2 vs 3   obs  28  exp 28.1  z -0.02
```

This is informative rather than fatal: a text can perfectly well count two
different things, "3 of X and 2 of Y". **Numerals are not one slot**, so the
one-count-field version of the form idea is wrong. The strong 1-vs-2 exclusion
is the frozen 817/861+2 collocation leaking through.

## The global answer is no

| | |
|---|---|
| testable pairs | 1069 |
| below chance at FDR 0.05 | 50 |
| surviving site + object controls | **42** |
| distinct signs involved | **35 of 77** |
| mutually exclusive groups of 3+ | 5 |

Five groups, and they overlap each other and mostly fail the obvious check that
a slot's members should sit in the same place:

```
[741, 817, 820, 861]   positions .35 .08 .15 .16   spread 0.27   plausible
[390, 520, 740]        positions .72 .92 .87       spread 0.21   plausible
[2, 60, 400]           positions .36 .31 .90       spread 0.59   not a slot
[60, 400, 861]         positions .31 .90 .16       spread 0.74   not a slot
[60, 817, 861]         positions .31 .08 .16       spread 0.22   plausible
```

**The no-repeat rule does not decompose the script into a handful of fields.**
Fewer than half the testable signs participate at all, and what comes out is a
couple of local paradigms, not a form.

## What does come out, and it is the strongest effect in the project

The single largest result anywhere in these notes:

> **520 and 740 appear together 6 times where chance predicts 90.**
> z = −14.1, and −12.4 / −12.6 after controlling for site and object class.

740 is in 981 texts, 520 in 179. Six overlaps. And both are text-final signs —
740 ends 72% of the texts it appears in, 520 ends 84%. They are competing for
the same position.

Chasing that: take every sign that both appears in ≥25 texts and ends ≥40% of
them, and test the set pairwise.

| sign | texts | ends text | share |
|---|---|---|---|
| 740 | 981 | 704 | 72% |
| 400 | 210 | 175 | 83% |
| 520 | 179 | 151 | 84% |
| 390 | 177 | 80 | 45% |
| 90 | 84 | 66 | 79% |
| 151 | 61 | 53 | 87% |
| 527 | 45 | 39 | 87% |

**17 of 41 pairs are mutually exclusive**, and most of the rest simply lack
power (expected counts of 2–4). The core paradigm:

```
740 / 520   obs   5  exp 90.3   z -14.12
740 / 390   obs  54  exp 89.6   z  -5.87
740 / 527   obs   6  exp 22.6   z  -5.27
740 / 617   obs   6  exp 22.8   z  -5.25
740 / 151   obs   8  exp 26.4   z  -5.10
740 / 156   obs   2  exp 16.0   z  -4.73
520 / 390   obs   0  exp 16.6   z  -4.52
```

**There is a terminal slot, and it takes exactly one filler.**

## The two exceptions sharpen it

Two signs habitually end texts yet do *not* exclude 740:

- **90 / 740: z = +4.83** — they co-occur *more* than chance
- **400 / 740: z = −0.20** — indifferent

If they shared the terminal slot this could not happen. Checking the order when
they do co-occur:

| | before 740 | after 740 |
|---|---|---|
| 400 | 18 | **91** |
| 90 | 7 | **62** |

They sit *after* the jar sign. So "ends the text" and "fills the terminal slot"
are two different things, and there are **two consecutive positions** at the end
of an Indus text: a terminal slot with competing fillers (740, 520, 390, 151,
527, 617, 156…), and a further position behind it that 400 and 90 occupy.

Note this is only visible because the exclusion test disagreed with the raw
"which sign ends the text" count. The naive statistic would have put 400 and 520
in the same box.

## Where this leaves it

- The slot idea is **local, not global**. There is no small set of fields that
  organises the script. 35 of 77 signs show any exclusion at all.
- But the **terminal slot is real and strong** — the clearest structural fact
  this project has found, and it survives every control available.
- A second position exists behind it.
- The one-count-field reading is refuted: numerals co-occur freely.

The honest summary is that Indus texts have recoverable *positional grammar at
the end*, which is where writing systems usually put their most formulaic
material, and nothing comparably crisp anywhere else. Whether the middle is
unstructured or merely too sparse to test is, as always, undecidable at 11135
tokens ([10-more-data.md](10-more-data.md)).
