# Could the signs be musical notation?

Script: `src/music.py`. Answer: no, and the test that kills it turns out to be
useful for everything else.

## The discriminating property is repetition

A melody reuses its pitches — that is what makes it a melody. So the question is
whether signs recur inside a text, measured against what you would get by
drawing signs at random from the corpus's own frequency distribution (2000
simulations, matched to the real length distribution).

| | observed | expected by chance |
|---|---|---|
| texts containing a repeated sign | 91 / 2613 (**3.5%**) | 428 (**16.4%**) |
| repeated tokens | 97 | 506 |
| a sign directly after itself | 18 / 8522 (**0.21%**) | 204 (**2.40%**) |

**z = −19.1.** The script does not merely fail to repeat; it repeats far *less*
than chance. Immediate repetition — the most ordinary thing a melody does — runs
eleven times below the random baseline.

## The inventory is also wrong

- **591 distinct signs.** A pitch set is 5–12, maybe 20–30 with ornaments.
- **153 signs are needed to cover 90% of tokens.** The top 7 cover 29%.
- **34% of signs appear exactly once.** A scale has no hapax pitches.
- Mean sequence length **4.26**, which is a motif, not a piece.

A seven-note scale would put essentially 100% of tokens in seven symbols. This
distribution is a vocabulary, not a scale.

## The finding worth keeping

Texts avoid reusing a sign. Combined with the short lengths, an Indus
inscription behaves less like a *sequence* and more like a **set of distinct
field values** — a form with slots, each filled once.

That is consistent with the record reading that has emerged elsewhere in this
project ([04-numerals.md](04-numerals.md), [08-hierarchy.md](08-hierarchy.md)):
a fixed template of positions, each taking one value from its own paradigm. It
also explains why positional statistics have been so productive here while
sequence statistics keep dissolving under controls.

## What would survive

Only a version where each sign is a whole named motif or piece rather than a
pitch — which is no longer musical *notation*, and carries no prediction this
corpus could test.

## Follow-up: could the numerals be repeat counts?

A good save — if `[3][X]` means "X three times", literal repetition would be
compressed away and the low repetition rate would be an artefact of the
encoding. But run-length encoding only removes **adjacent** repeats. A melody
that returns to a pitch later still writes that sign twice.

Splitting the two kinds (1500 simulations):

| kind of repetition | observed | expected | z |
|---|---|---|---|
| adjacent (sign twice in a row) | 18 | 204.0 | −12.9 |
| **non-adjacent (sign returns later)** | **74** | **271.4** | **−13.5** |

Compression explains the first row. It cannot explain the second, and the second
is just as depleted: 2.8% of texts versus 10.4% expected. Indus texts avoid
returning to a sign, and returning to a pitch is what melody *is*.

The note set would also be wrong. **244 distinct signs are preceded by a numeral
at some point**, covering 90% of the corpus — that is a vocabulary being
quantified, not a scale being counted out.
