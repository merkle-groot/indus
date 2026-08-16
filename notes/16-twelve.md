# Every stroke sign as a number, and the twelve that was hiding

Script: `src/allstrokes.py`. [05-radix.md](05-radix.md) excluded the bracketed
and barred stroke signs and flagged it as its biggest open caveat: *"if any of
those encode higher values, the cliff could move."* It moves.

## Reading the glyphs instead of guessing from the id

Every stroke sign was rendered from the font at 380px and counted by eye
(`scratchpad/big.png`), not inferred from its number:

| sign | strokes | reading | n |
|---|---|---|---|
| 27 | 2+3+2 | 7, three rows | 5 |
| 28 | 3+3+2 | 8, three rows slanted | 4 |
| 29 | 3+3 | 6, slanted | 2 |
| 48 | 4+3 in ( ) | 7, bracketed | 14 |
| 49 | 7 in a row in ( ) | 7, bracketed | 4 |
| 50 | 8 long in ( ) | 8, bracketed | 1 |
| 51 | 5+4 under a bar | 9, roofed | 1 |
| **55** | **4+4+4** | **12, three rows** | **42** |
| 57 | 4+4+4 in ) ( | 12, bracketed | 1 |

Per the brief, the four bracket shapes — `( )`, `) (`, `) )`, `( (` — are treated
as one modifier. Ids 34, 36, 41, 56, 58 have no glyph in this font; 34 and 36
are read from their series, the rest are left out. **Sign 56 has 10 tokens and
remains unread — it is the one loose end here.**

## The corrected distribution

Deduplicated (the first pass was inflated by one mass-produced text appearing six
times):

| value | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | **12** |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| old | 271 | 744 | 289 | 76 | 53 | 32 | 50 | 6 | 2 | 0 | 0 | **0** |
| **new** | 271 | 742 | 289 | 76 | 53 | 37 | 60 | 9 | 3 | 0 | 0 | **37** |

## 12 is not the tail of the series — it is a spike

Fit the decay through values 4–9 and extrapolate:

| | expected | observed |
|---|---|---|
| 10 | 3.1 | 0 |
| 11 | 1.7 | 0 |
| **12** | **0.9** | **37** |

The absence of 10 and 11 is exactly what the decay predicts, so it is not
evidence of a ceiling. The 12 is forty times its extrapolation:
**Poisson P(≥37) = 1.4e-45**, and 5.5e-68 on the most conservative fit.

## Does 55 behave like a numeral?

Everything rests on this. Deduplicated, against the 1339 texts carrying a known
numeral:

| | numerals | sign 55 | sign 48 |
|---|---|---|---|
| mean position | 0.406 | **0.439** (p = .44) | 0.650 (p = .031) |
| overlap of what it precedes | — | **0.447** | 0.279 |

The overlap figure needs its own yardstick: split the known numerals in half and
compare them to each other and you get **0.483**. So 55 agrees with the numerals
about as well as the numerals agree among themselves. It sits in the numeral
slot and it counts the same nouns.

**55 passes. 48 fails** — it sits significantly later in the text and is
followed by the jar sign in all 14 occurrences. The bracketed forms are not
numerals wearing a modifier; 48 is its own sign with its own habit.

## What this does to the base-8 conclusion

**It kills it.** A single symbol for 12 is not something a base-8 system can
contain. The old reading — "values 1–7 with a hard boundary at 8" — was an
artefact of excluding the three-row signs.

The replacement is more interesting: values **1–9 decay smoothly**, 10 and 11 are
absent exactly as that decay predicts, and **12 stands alone as a separate,
well-attested quantity**. That is the shape of a higher unit, not a digit.

## But it is not a multiplied base

05-radix.md went looking for a symbol for the base and found none. 55 is the
best candidate yet, and it still does not close:

> 55 is preceded by a numeral in **8 of 36** occurrences (22%) against a 14%
> corpus base rate. **p = 0.23.**

Before deduplication this looked like 33% and significant; six copies of one
text were doing the work. There is no evidence that 55 is being multiplied the
way "3 dozen" would be. So it behaves like a numeral, it is a distinct quantity
around twelve, and nothing counts it.

## Where this leaves it

- **Base 8 is withdrawn.** It rested on an exclusion that turns out to matter.
- Values run 1–9 with an ordinary decay, then a discrete spike at 12.
- 55 is a genuine numeral by position and by what it counts.
- No multiplier structure, so "base 12" is not established either — only a
  duodecimal *unit*.
- An honest alternative that this corpus cannot rule out: three rows of four is
  a conventional **"many"** rather than a literal twelve. It would behave
  identically in every test run here.
- Sign 56 (10 tokens) is unreadable in this font and could change the picture
  again.

Credit where due: this came from the suggestion to stop treating the bracketed
and multi-row strokes as unclassifiable and read them as numbers with modifiers.
The modifier half of that idea did not survive; the numbers half overturned a
headline result.
