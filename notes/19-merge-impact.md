# If every look-alike sign is one character, what changes?

Script: `src/mergeimpact.py`. `src/shapes.py` grouped the rendered glyphs two
ways:

- **A — allograph sets** (41): the same drawing, drawn twice.
- **B — derivational families** (29): a base plus something added.

These are different claims. Merging an A set says two scribes drew one sign
differently. Merging a B family says a fish and a fish-with-a-bar-through-it are
the same character — which is exactly what
[07-fish-as-operand.md](07-fish-as-operand.md) measured a difference in. Both
are applied here, separately, and every headline result recomputed under each.

## M0 — the automatic sets recover all fifteen hand-picked groups

The fifteen groups identified by eye in [18-allographs.md](18-allographs.md),
checked against the shape clustering, which had no knowledge of them:

| | |
|---|---|
| recovered as a single A set | **14** |
| recovered as a single B family | **1** (154 + 156) |
| missed | **0** |

Fifteen for fifteen. Pixel geometry and human judgement agree completely on
this set, which is the strongest validation either method has had.

The one that came out as **B** rather than A is 154 + 156 — the shape pipeline
reads 156 as 154 with something added. Parpola merges them anyway (P004) and the
behavioural test in [18-allographs.md](18-allographs.md) passed. So the A/B line
is not perfectly sharp, which matters for what follows.

## M1 — inventory

| merges | signs | hapax | n≥20 (testable) | median count |
|---|---|---|---|---|
| none | 591 | 215 | 77 | 2 |
| **A only** | **529** | **178** | **81** | **3** |
| A + B | 490 | 168 | 77 | 3 |

**A-only is the sweet spot.** It cuts 62 signs, removes 37 hapax, and lifts the
median sign from 2 tokens to 3 — the first time anything in this project has
moved that number. Four signs newly become testable.

Going on to merge B *reduces* the testable count back to 77, because it folds
common signs into each other faster than it rescues rare ones. This is the same
pattern [10-more-data.md](10-more-data.md) found with Parpola's merges, and it
sets the boundary: collapse allographs, do not collapse derivations.

Note this is a real if modest correction to the earlier claim that allograph
collapsing buys nothing. Done at the right level, it buys a little.

## M2 — the terminal slot is untouched

| merges | 740 / 520 observed | expected | z |
|---|---|---|---|
| none | 5 | 91.7 | **−14.19** |
| A only | 5 | 91.8 | **−14.21** |
| A + B | 5 | 91.4 | **−14.19** |

The strongest finding in the project does not move at the third decimal place.

## M3 — the no-repeat rule survives

| merges | texts with a repeated sign | expected | z |
|---|---|---|---|
| none | 77 (3.7%) | 350 (16.9%) | −16.9 |
| A only | 78 (3.8%) | 353 (17.1%) | −17.5 |
| A + B | 113 (5.5%) | 379 (18.5%) | −16.0 |

Merging necessarily manufactures repeats — two different ids in one text become
the same sign twice — and under A + B the observed rate does climb from 3.7% to
5.5%. The depletion is so large that it barely registers.

## M4 — the one casualty

| merges | plain fish, coefficient > 3 | marked fish | p |
|---|---|---|---|
| none | 16/93 | 0/51 | **6.5e-04** |
| A only | 16/93 | 0/51 | **6.5e-04** |
| **A + B** | 16/130 | 0/14 | **0.37** |

Merging B families destroys the fish coefficient cap, and the reason is
circular: the finding is that a marked fish behaves differently from a plain
one, and the merge asserts they are the same character. Only 14 marked fish
survive as a separate category, so the test loses its power by construction.

**This is not evidence against the fish result.** It is the merge assuming the
conclusion away. But it does mean the two cannot both be held: either marked
fish are their own signs and the cap stands, or they are spelling variants and
the cap is meaningless. The corpus evidence — a measurable behavioural
difference at p = 6.5e-04 — favours keeping them apart.

## M5 — seals versus tablets is untouched

Harappa, what ends the text:

| merges | seals | tablets | p |
|---|---|---|---|
| none | 740: 38%, 520: 9%, 400: 2% | 400: 31%, 740: 23% | 3.4e-18 |
| A only | 740: 38%, 520: 9%, 400: 2% | 400: 31%, 740: 23% | 6.7e-18 |
| A + B | 740: 38%, 520: 9%, 400: 2% | 400: 31%, 740: 23% | 6.1e-18 |

Identical to the percentage point.

## Answer

**Almost nothing changes.** Four of the five headline results are unmoved:

- terminal slot: z = −14.2 in all three conditions
- no-repeat rule: z between −16 and −17.5 in all three
- seals vs tablets: p ≈ 1e-18 in all three
- and the fifteen hand-picked groups were independently confirmed 15/15

What is gained is a cleaner inventory: **591 → 529 signs, 215 → 178 hapax,
median token count 2 → 3, four new testable signs.** Real, and modest.

What is lost, only under B, is the fish coefficient cap — and that loss is an
artefact of the merge rather than a finding about the script.

The practical conclusion: **apply the A sets, keep the B families separate.**
That is also what the rest of the project's evidence says, since the B
distinctions carry behaviour ([06-fish.md](06-fish.md),
[07-fish-as-operand.md](07-fish-as-operand.md)) and the A distinctions do not.

The findings in this project do not rest on how finely the sign inventory is
cut. That is worth knowing, because sign identity is the single most disputed
question in Indus epigraphy, and it turns out not to be load-bearing here.
