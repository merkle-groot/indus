# How do longer texts grow?

> **Revised in part by [26-right-edge.md](26-right-edge.md).** The 77% same-last-sign
> result below is not above its positional baseline: the exact-slot null predicts
> 89%. The newly tested last-two-sign tail is retained 63% against 45% expected.
> The evidence is for a two-sign tail as a unit, not exceptional stability of the
> final sign by itself.

Script: `src/growth.py`. A form grows by filling optional fields, so a short
record should look like a long one with holes. Sentences do not work that way —
lengthening a sentence rearranges it.

Test: is a short text a **subsequence** of a longer one — same signs, same
order, gaps allowed? That is exactly "the same form with some fields blank".

2035 distinct texts after deduplication.

## The control that matters

This project has been burned before: two-thirds of an apparent sign-ordering
result turned out to be positional-slot artefact ([08-hierarchy.md](08-hierarchy.md)).
So containment is measured against a null that reproduces the corpus's
positional habits exactly — each slot of a length-L text is drawn from the real
distribution of signs at that slot among real length-L texts. 740 still lands at
the end, 817 still lands at the start. Only the pairing is destroyed.

## G1 — texts do contain each other, twice as often as chance

| | observed | frequency null | position null |
|---|---|---|---|
| short text is a subsequence of a longer one | **22.4%** | 12.6% | 10.7% (**z = +20.3**) |

This is the first sequence-level result in the project that survives the
positional control instead of dissolving under it.

### But breakage is a live alternative

`ISCOMPLETE` is `Y` for all 2543 rows, so the corpus carries **no damage flags**
([01-corpus.md](01-corpus.md)). A broken seal shows a fragment of a longer text,
and a fragment is trivially a subsequence. That would produce this result with
no grammar involved.

The discriminator: breakage leaves a **contiguous** run. It cannot leave a text
with a hole in the middle. So re-run counting only short texts that are a
subsequence of some longer text and a contiguous block of **no** longer text:

| | observed | frequency null | position null |
|---|---|---|---|
| gapped containment only | **5.8%** | 4.1% | 4.1% (**z = +9.5**) |

**The effect survives, much diminished.** Of the 22.4%, roughly 16.6 points are
contiguous fragments that damage could account for; the breakage-proof residual
is 5.8% against 4.1% expected. Real, and a quarter the size of the headline
number. Anyone quoting the 22.4% without this caveat is quoting mostly broken
seals.

## G2 — the nesting is shallow

| chain depth | texts |
|---|---|
| 1 | 786 |
| 2 | 832 |
| 3 | 293 |
| 4 | 35 |
| 5 | 1 |

A form with, say, six optional fields should produce long chains of
progressively filled versions. Chains reach depth 5 exactly once. Most nesting
is a single step. This is the behaviour of a short template with one or two
optional positions, not a rich record layout.

## G3 — growth happens at the front, and the tail is fixed

478 pairs differ by exactly one sign.

| the extra sign is inserted | |
|---|---|
| at the start | **263 (55%)** |
| in the middle | 106 (22%) |
| at the end | 109 (23%) |

And the strongest single number here:

> **In 370 of 478 pairs (77%) the last sign is unchanged.**

Texts grow at the head and keep their tail. That is independently consistent
with [12-slots.md](12-slots.md), which found a terminal slot holding exactly one
filler — the slot stays filled by the same sign while the text lengthens in
front of it.

Insertions are also drawn from a restricted set: **110 of 580 signs** are ever
inserted, and the top ten account for 45% of all insertions.

```
400(56)  240(33)  235(31)  31(18)  233(16)
803(13)  176(13)  415(12)   90(11) 877(10)
```

Sign 400 leads by a wide margin — the same sign [12-slots.md](12-slots.md) found
sitting *behind* the jar sign in a position of its own.

## Verdict

**Partly yes.** Short texts really are longer texts with material removed, at
about twice the rate chance allows, and the pattern of growth is orderly: add at
the front, keep the ending, draw the addition from a small set.

But the honest accounting is:

- most of the raw containment signal is contiguous and could be broken artefacts
- the breakage-proof part is a modest 5.8% vs 4.1%
- nesting is shallow, so if this is a form it has very few optional fields

The result is more consistent with **a fixed ending plus a short expandable
head** than with a multi-field record layout. That is a weaker claim than "a
form with slots", and it is the one the data supports.
