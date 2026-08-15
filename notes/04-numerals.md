# Numerals, and the denomination hypothesis

Scripts: `src/signchart.py` (renders every sign so identity is checkable by eye),
`src/numerals.py` (the tests).

## Identifying the numerals

The database gives numeric ids, not descriptions, so which signs are stroke
groups is not recoverable from the data alone. Rendering the sign chart with the
embedded font settles it, and reveals that **the ids encode stroke count**:

| series | ids | form |
|---|---|---|
| short strokes | 1-7 | one row, small: 1=`\|` … 7=`\|\|\|\|\|\|\|` |
| long strokes | 31-35 | one row, full height: 31=`\|` … 35=`\|\|\|\|\|` |
| two-row groups | 12-19 | stacked: 16=`\|\|\|/\|\|\|`, 19=`\|\|\|\|\|/\|\|\|\|` |

Together **1788 tokens, 16.1% of the corpus**. Deliberately excluded: ids 41-51
and 55, which are strokes with brackets, bars or hooks (`(\|\|\|\|)`, strokes
under a rule). They may well be numerals too; leaving them out is conservative.

Counts by value:

```
short   1:153  2:583  3:160  4:65  5:39  6:2   7:3
long    1:145  2:261  3:209  4:18  5:15
tworow  3:22   5:7    6:38   7:54  8:6   9:3
```

Frequency falls off steeply with magnitude, which is what numeral systems do.
One anomaly worth noting: **"2" outranks "1" in both single-row series**, by
nearly 4x in the short series. Genuine numerals usually have 1 most frequent.
Either sign 2 is not "two", or these are not pure cardinal counts.

## The denomination test

If inscriptions worked like coinage -- fixed legend, variable value -- then among
texts differing in exactly one slot, that slot should be a numeral unusually
often. 2813 such minimal pairs exist among the 1980 distinct texts. The design
is within-pair: the varying slot is compared against the shared slots of the
same pairs, so text length, formula and vocabulary are all held constant.

| | numerals | rate |
|---|---|---|
| varying slot | 527 / 5626 | **9.4%** |
| shared slots | 533 / 4012 | **13.3%** |

Odds ratio **0.67**, p = 1.7e-09.

**The prediction fails, and fails in the opposite direction.** The numeral is
*more* likely to be part of the fixed legend than to be the thing that varies.
Whatever distinguishes two near-identical Indus texts, it is usually not the
number.

## What did turn up instead

**Numerals form a closed substitution class.** Given that one variant in a
minimal pair is a numeral, the other is a numeral **25.2%** of the time against
9.4% expected under independence — a **2.69x** enrichment, binomial
p = 3.3e-21. When a numeral does vary, it is replaced by another numeral, and in
45 cases by one from the same stroke series. Examples, with the numeral slot
blanked:

```
[_ 900 740]   3 vs 4 vs 5     (short)
[_ 154]       3 vs 4 vs 5     (short)
[_ 700]       2 vs 3 vs 4     (long)
[_ 390]       6 vs 7 vs 8     (two-row)
[817 2 _ 390] 3 vs 4 vs 5     (short)
```

That is a paradigm: a slot with a defined set of mutually substitutable fillers.
It is real notational structure and it is exactly what a quantity field looks
like.

**Numerals sit early.** Mean relative position 0.393 against a 0.500 baseline,
Mann-Whitney p = 1.6e-29. In reading order they come before what they modify.

**They precede a specific small set of signs.** Lift over corpus frequency for
the sign immediately following a numeral:

| sign | lift | | sign | lift |
|---|---|---|---|---|
| 700 | 4.24 | | 220 | 2.37 |
| 156 | 4.01 | | 240 | 2.01 |
| 390 | 2.40 | | 803 | 2.01 |

And sign 740 — the frequent text-final "jar" — is *depleted* after numerals at
0.40x, consistent with numerals living in the front half and 740 anchoring the
end.

## Reading

The stroke signs behave like numerals on every structural test: closed
substitution class, steep frequency decay with magnitude, consistent early
position, and a restricted set of following heads. Calling them quantities is
well supported.

The **denominations** framing specifically is not. Coinage varies the value
against a constant design; these texts hold the number constant and vary
something else. The shape is closer to `[quantity] [commodity-or-title] …
[terminal sign]` as a *whole fixed record* — each object stating its own
complete formula — than to a series struck in multiple values.

This is compatible with the mainstream administrative reading (seals as
ownership/consignment marks), and it puts a real constraint on it: the
distinguishing information between two similar records lives outside the numeral
slot.

## Caveats

- Stroke count is inferred from id by visual inspection of the rendered chart,
  verified for 16/17/18/19 and 31/32/33/35 but not exhaustively. If the id-to-count
  mapping breaks anywhere, the *value* claims move; the substitution-class and
  position results do not, since they only need the set membership.
- Bracketed and barred stroke signs (41-51, 55) are excluded. Including them
  would enlarge the numeral class and could shift rates.
- Minimal pairs are computed over distinct texts, so the mass-production
  duplicates from [03-sign-motif.md](03-sign-motif.md) cannot inflate the counts.
- "2 outranks 1" is unexplained and should be resolved before leaning on the
  value assignments.
