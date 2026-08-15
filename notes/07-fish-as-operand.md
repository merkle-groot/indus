# Fish as operand, mark as operator

Script: `src/fish_operator.py`. This tests a *different* hypothesis from
[06-fish.md](06-fish.md). There the mark was proposed as the number and was
rejected. Here the **fish is the value and the mark is a function applied to
it** — e.g. a unit multiplier.

## Result: one prediction holds, and holds hard

**Marked fish are never preceded by a numeral above 3.**

| | 1 | 2 | 3 | 4 | 6 | 7 | total | share >= 4 |
|---|---|---|---|---|---|---|---|---|
| plain fish (220) | 5 | 57 | 14 | 6 | 9 | 1 | 92 | **17.4%** |
| marked fish | 24 | 113 | 6 | 0 | 0 | 0 | 143 | **0.0%** |

Fisher exact, odds ratio infinite, **p = 1.3e-07**.

This survives both controls that killed earlier findings:

- **Frozen template.** Excluding every `[817|820|861] + [2] + [fish]`
  occurrence, still p = 5.9e-07.
- **Mass production.** Recomputed on distinct texts only, still p = 1.3e-07.
  The 17 high-value cases occur across **16 distinct texts**, so this is not one
  formula repeated.

Examples of `[>=4] [plain fish]`, all distinct:

```
4 220 60 706 33 520          6 220 520
14 220                        16 220 520 400
95 390 2 4 220                140 900 190 297 2 16 220 740 90
820 2 14 220 740 90           545 908 31 16 220 740 90
```

Plain fish is counted freely up to 7. Marked fish is counted only 1, 2 or 3.
That is exactly the behaviour of a **higher unit taking a small coefficient**,
which is what the operator hypothesis predicts and what the plain-numeral
hypothesis does not.

## The other predictions

**P1 — do fish substitute for stroke numerals in minimal pairs?** No.

| substitution | observed | expected | lift |
|---|---|---|---|
| numeral <-> numeral | 106 | 24.7 | **4.29** |
| fish <-> fish | 46 | 16.4 | **2.81** |
| numeral <-> fish | 46 | 40.2 | 1.14 (p = 0.34) |

Two separate closed paradigms that do not mix. Under a naive "fish is a digit"
reading this is fatal. Under the *unit* reading it is expected — "hundred" and
"3" are not interchangeable either.

**P2 — do marked fish require an operand more often?** No, slightly the reverse:
plain 39.9% vs marked 32.7% (p = 0.057). Ambiguous; a base unit can be counted
more freely than a compound one.

**P4 — position.** Numerals sit at 0.393, fish at 0.433, baseline 0.500
(p = 3.5e-05). Fish sit just *after* numerals, consistent with `[count] [unit]`.

**P5 — stacking.** Fish repeat freely: 175 texts carry two or more, and there
are 175 adjacent fish-fish pairs. Operators usually do not chain; units do.

## Verdict

This is now the **best-supported account of the fish marks** we have. It made a
prediction that nothing else predicted — that the mark should restrict the
accompanying quantity — and that prediction survived two controls that
destroyed earlier findings.

It is not proven. The ceiling at 3 shows the mark *constrains quantity*; it does
not uniquely establish multiplication. A rival reading fits the same data: the
marked forms could denote something not counted in large amounts — a title, a
rank, a named individual — and plain fish a bulk commodity.

The discriminating test would be whether `[k] [marked fish]` and
`[k x N] [plain fish]` are in complementary distribution for some fixed N. That
needs either a candidate value for N or a larger corpus.

## Revision to 06-fish.md

That note concluded the marks are "categorical, not numeric". Narrow the claim:
the marks are not **numerals** — they do not form a graded series and do not
substitute for stroke numbers. But they are not inert category labels either.
They govern how much of the thing can be counted, which is a quantitative role.
