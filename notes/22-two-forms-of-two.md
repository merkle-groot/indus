# Two ways to write "two", and they are not interchangeable

Script: `src/twoforms.py`. This revises a conclusion in
[05-radix.md](05-radix.md).

## The claim being revisited

05-radix.md found three parallel stroke series — short strokes, long strokes,
stacked rows — encoding the same values, and concluded the difference was
**graphic**: a writing convention, not a distinction that carries meaning. The
evidence was that the stacked form takes over exactly where a single row stops
being legible.

That still holds as far as it goes. But it predicts the forms should be
substitutable, and in one place they are emphatically not.

## Three signs that demand a "two", and the form they demand

| sign | occurrences | followed by **2** (short) | followed by **32** (long) | other |
|---|---|---|---|---|
| 817 | 120 | **102** | **0** | 18 |
| 861 | 148 | **118** | **0** | 30 |
| 820 | 142 | 74 | 5 | 63 |
| **840** | 62 | **2** | **22** | 38 |

Corpus-wide, the long form is **30%** of all value-2 tokens (224 of 742). So if
the two forms were freely interchangeable, 817 and 861 should show roughly 66
long ones between them.

They show **zero**, in 220 opportunities.

And 840 runs the other way: 22 long against 2 short, where chance says the
reverse. Fisher exact between the two collocations: **p = 2.5e-29**.

## 840 is a fourth frozen pair, and a new one

Sign 840 is followed by sign 32 in **22 of 62** occurrences — 35%, against a
corpus base rate of **2.29%**. **p = 1.2e-20.**

This was not in 05-radix.md, which found the collocation by searching for signs
followed by *any* numeral and so caught 817, 820 and 861. 840 was missed because
its partner is the long-stroke form.

The composite sign **843** confirms the binding independently: the database
stores it as `32 + 840 + 32` — sign 840 flanked by the long two on both sides.

## What this changes

The three stroke series are still the same numbers. Nothing here disturbs the
value assignments or the counts in [16-twelve.md](16-twelve.md).

What changes is the claim that the choice between them is free. Inside frozen
expressions it is not free at all — **each fixed phrase selects one form and
never varies it.** 817 and 861 take the short two 220 times and the long two
never; 840 does the opposite.

That is the behaviour of a spelling, not of handwriting. A scribe writing
817-then-two is not choosing between equivalent renderings; the phrase specifies
which one.

The honest statement is now narrower than 05-radix.md's:

> The short, long and stacked series encode the same values, and outside fixed
> expressions the choice between them looks graphic. Inside fixed expressions it
> is determined, and the determination is sign-specific.

## What it does not license

It does not show the forms differ in *meaning* — only that they differ in
distribution. A frozen phrase can specify an arbitrary variant for no reason
beyond convention, the way English spells "one" in "anyone" and never "1".

It also does not rescue any tiered or place-value reading. 05-radix.md's finding
that the series avoid each other across texts, and that no carry or place-value
composition appears anywhere, is untouched.

## Where it came from

A suggestion that sign 840 might be signs 405 and 407 written together. It is
not — 840 is two overlapping lens shapes where 405/407 are rakes on a stem, the
two sit in different parts of the text (mean position 0.419 against 0.795,
p < 0.0001), they share almost nothing in preceding context (cosine 0.036), and
**405 and 407 never occur adjacent anywhere in the corpus**, so the spelled-out
form a ligature would need does not exist.

But looking at where 840 sits is what surfaced the collocation. The wrong
hypothesis pointed at the right sign.
