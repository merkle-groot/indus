# Structural comparison with Linear B

Script: `src/linearb_compare.py`. The point of comparing with Linear B is that
we **know what Linear B says** and how its tablets are laid out. So this is a
falsifiable structural comparison, not a phonetic guess. It tests one question:
does the Indus corpus behave like a Mycenaean palace-accounting script?

Linear B facts below are from the standard descriptions (Ventris/Chadwick and
after); Indus figures are computed on the deduplicated corpus.

## The two systems side by side

| | Linear B | Indus (this corpus) |
|---|---|---|
| era | ~1450–1200 BCE | ~2600–1900 BCE |
| status | **deciphered** (Greek) | undeciphered |
| syllabograms | ~88 | — |
| logograms / ideograms | ~100–170 (commodities) | — |
| total sign inventory | **~260** | **591** (527 after merges) |
| hapax rate | most complex ideograms are hapax | 36% |
| mean text length | short accounting entries | **4.4 signs** |
| numerals | decimal, distinct signs 1 / 10 / 100 / 1000 / 10000, each repeated up to 9× | **additive 1–9, a "twelve" unit, no higher powers** |
| largest quantity attested | into the **ten-thousands** | **26** |
| word order | rigid: **commodity logogram → number** | see below |

Two things match and three do not, and the mismatches are the informative part.

## What matches

**Short administrative labels with embedded numerals.** Both are dominated by
brief entries that pair a small number of identity/commodity signs with a
quantity. Nobody is writing sentences. Our mean of 4.4 signs is an accounting
entry, not prose, exactly as in Linear B.

**A layout with fixed positions.** Linear B entries are slotted (heading,
commodity, number). The terminal slot and the frozen collocations found in
[12-slots.md](12-slots.md) and [22-two-forms-of-two.md](22-two-forms-of-two.md)
are the same kind of positional grammar.

## What does not match, and why it matters

### 1. No rigid commodity-then-number order

Linear B is strict: the commodity logogram stands **immediately before** the
number that counts it. If Indus were the same, numeral-noun adjacencies should
run overwhelmingly one way.

| | count |
|---|---|
| noun then numeral | 1038 |
| numeral then noun | 1206 |

**1.16 : 1.** Essentially no fixed order. A Mycenaean scribe never wrote the
sheep after the count; an Indus text does it both ways almost equally. Whatever
governs Indus word order, it is not the Linear B commodity-number rule.

### 2. No closed commodity class

Linear B commodities are a small **closed set** of logograms, and the complex
ones are mostly hapax — they label specific goods and appear rarely. In Indus,
the signs that sit directly after a numeral are:

- **226 distinct signs** — not a small closed set
- the **common** signs, not rare ones: 220 (a fish, 93×), 390 (62×), 740 the jar
  (58×), 520 the arrow (47×)
- diffuse: the top 15 cover only 45% of post-numeral tokens

So the "thing being counted" in Indus is drawn from the ordinary high-frequency
vocabulary, not from a dedicated commodity sign-list. That is unlike a palace
inventory and more like... something else. The fish sign being the single most
counted thing is notable, and consistent with
[07-fish-as-operand.md](07-fish-as-operand.md).

### 3. The numerals are far too small

This is the sharpest divergence. Linear B exists to tally palace stores — flocks
of hundreds of sheep, thousands of units of grain — and has distinct signs for
10, 100, 1000, 10000 to do it.

**Indus never expresses a quantity above 26**, and 26 occurs once. The
distribution:

```
1:177  2:542  3:256  4:88  5:74  6:56  7:57  8:20  9:20
10:7   11:1   12:27  13:3  14:3  15:3  16:1  24:1  25:1  26:1
```

Nothing above single digits except the "twelve" unit and a handful of small
sums. A script whose largest number is 26 is **not doing bulk accounting.** You
cannot run a palace granary with a system that cannot write "200".

## What the comparison actually tells us

Indus shares Linear B's *format* — short slotted labels with numbers — but not
its *function*. The Linear B match breaks on three counts: no fixed
commodity-number order, no closed commodity list, and a numeral system that tops
out around twelve.

The small-number ceiling is the strongest single fact. It rules out the reading
that these are inventory tallies of goods in quantity, and points instead at
something where the numbers are **small by nature**: ranks, counts of people or
named entities, calendar or measure units, or identifiers, rather than
warehouse quantities. That is consistent with what
[08-hierarchy.md](08-hierarchy.md) and the record-formula reading have found
from the other direction.

It also sharpens why decipherment-by-analogy fails here. Indus is not a
Mycenaean-style account, so mapping Linear B's *categories* onto it would be
wrong even before we get to sound values. The productive comparison is
structural and it delivered a negative constraint: **whatever Indus texts are,
they are not quantity inventories.**

## The honest limit

We are comparing a deciphered syllabary-plus-logogram system against an
undeciphered one of unknown type. The match in "short labels with numerals" is
real but weak — it is true of almost any administrative script, including
cuneiform receipts. The three mismatches are the load-bearing result, and they
are all internal to the Indus data: the word-order ratio, the diffuse
post-numeral vocabulary, and the numeral ceiling would hold as facts about this
corpus even if Linear B had never been mentioned. Linear B supplied the
questions; the answers are ours.

## Aside: the contemporary language landscape

For the record, since it comes up. Candidate languages in or near the mature
Harappan (2600–1900 BCE):

- **Dravidian** (proto-) — the leading hypothesis (Parpola's *meen* rebus).
- **Elamite** — contemporary neighbour in SW Iran; an "Elamo-Dravidian" link is
  proposed.
- **Indo-Aryan / Vedic Sanskrit** — arrives **later** (~1500 BCE), which is the
  standard objection to Sanskrit readings of a script that predates it.
- **Sumerian / Akkadian** — the Mesopotamian trade partners; not related, but a
  script *model* and the source of the Meluhha references.
- **Munda / Austroasiatic** — a minority substrate hypothesis.

None of this is exploitable without a bilingual, and there is none. The Meluhha
cuneiform seals name Indus individuals but do not translate the script. That is
why every result in this project is distributional: a language mapping can be
made to fit and cannot be tested, whereas the structure can be measured.
