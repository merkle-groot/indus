# The fish family: is the modifier a number?

Script: `src/fish.py`. Prompted by sign 222 — a fish in brackets with a small
raised mark, which reads at a glance like exponent notation.

## The family

1023 tokens, 9.2% of the corpus. Rendering ids 215-260 shows it decomposes on
two axes: a **body modifier**, and an optional pair of **flanking strokes**.

| id | form | n |
|---|---|---|
| 220 | plain fish | 284 |
| 240 | fish + X cross | 256 |
| 235 | fish + roof/chevron | 186 |
| 233 | fish + top cross | 140 |
| 231 | fish + internal line | 60 |
| 226 | plain + flanking | 26 |
| 236 | roof + flanking | 21 |
| 222 | (fish) in brackets + raised hook | 16 |
| 241 | X + flanking | 10 |
| 232 | line + flanking | 8 |

This is the most-discussed sign family in Indus studies — Parpola's Dravidian
proposal hangs on it (fish = *mīn*, punning on "star").

## The modifier is not numeric

**It isn't graded.** Fish variants do substitute for one another in minimal
pairs, at 1.58x chance (p = 0.0016) — but that is weak next to the numerals'
2.69x (p = 3e-21), and the substitutions have no order to them:

```
X <-> roof  7      roof <-> topcross  7      plain <-> line  4
plain <-> topcross 4      plain <-> roof  4      X <-> plain  3
```

A numeral paradigm looks like 3-vs-4-vs-5 in one slot. This looks like a set of
categorical alternatives, not a scale.

**And the decisive point: fish variants are quantified from outside.** If the
modifier encoded a quantity, an explicit numeral in front would be redundant.
Instead a numeral precedes fish variants at roughly twice the corpus baseline:

| sign | form | n | preceded by a numeral |
|---|---|---|---|
| 220 | plain | 253 | **39.9%** |
| 240 | X | 200 | **38.5%** |
| 235 | roof | 110 | 31.8% |
| 231 | line | 45 | 31.1% |
| 233 | topcross | 114 | 20.2% |
| — | *corpus baseline* | — | *19.6%* |

The corpus counts fish the ordinary way, with a separate numeral sign in front.
So the marks on the body are doing something else.

## Flanking is not an allograph either

If flanked and unflanked forms were one sign written two ways, they should share
neighbours. Cosine similarity of their context vectors:

| pair | cosine | | reference pair | cosine |
|---|---|---|---|---|
| 220 vs 226 (plain) | 0.517 | | 220 vs 240 | 0.415 |
| 235 vs 236 (roof) | 0.454 | | 220 vs 235 | 0.269 |
| 240 vs 241 (X) | 0.367 | | 235 vs 240 | 0.549 |
| 231 vs 232 (line) | 0.254 | | | |

Flanked/unflanked pairs are no more alike than two unrelated fish signs. So
flanking distinguishes genuinely different signs — but what it distinguishes is
not recoverable from distribution alone.

## Byproduct: a three-sign template

Following the "value 2" trail from [05-radix.md](05-radix.md):

**`[817 | 820 | 861] + [short-stroke 2] + [fish variant]` occurs 68 times.**

Of the 142 contexts where a short-2 sits directly before a fish, 68 (47.9%) have
one of those three head signs in front. Commonest instances: `861 2 240` (10),
`861 2 235` (9), `817 2 240` (8), `817 2 235` (8).

This reinforces that the "2" there is not counting fish — it is the fixed middle
of a frozen three-slot formula.

## Verdict

The intuition that the fish is a **base sign carrying modifiers** is right, and
that compositional structure is real and important. The specific reading as
raised numeric notation is not supported: the modifiers are categorical rather
than graded, and the fish is quantified externally by ordinary numerals anyway.
