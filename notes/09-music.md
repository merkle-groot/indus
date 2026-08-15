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
