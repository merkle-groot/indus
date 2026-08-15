# Is "1" rare because you don't write it?

Script: `src/unmarked_one.py`. Once the frozen 817/861+2 collocation is removed
([05-radix.md](05-radix.md)), values run:

```
1:282   2:519   3:386   4:86   5:61   6:40   7:57
```

That ordering is wrong for a counting system. You count one of something far
more often than seven, so 1 in third place needs explaining. The standard
explanation is that the **singular is unmarked**: a bare sign already means one
of the thing, and strokes are added only for more than one. If so, `1 X` and
plain `X` are the same message, and the real count for 1 is invisible.

Four tests, each able to refute it.

## U1 — the 1 is more deletable

If the marker is optional, the same text should appear both with and without it.
Deleting a genuine 2 changes the message; deleting an optional 1 does not.

| value | occurrences whose deletion leaves an attested text | |
|---|---|---|
| **1** | **18 / 252** | **7.1%** |
| 2 | 11 / 438 | 2.5% |
| 3 | 15 / 265 | 5.7% |
| 4 | 7 / 70 | 10.0% |

Raw comparison, 1 against 2–3: p = .034. Deletability is confounded with text
length (a short text's reduced form is far likelier to be attested), so
stratified by length: **CMH z = 2.65, p = .008**. It survives.

Real examples:

```
31 460 520      ->  460 520
31 388 740      ->  388 740
31 240 740 90   ->  240 740 90
```

**Caveat, and it is not small.** Value 4 is deletable at 10%, higher than 1. On
7 hits that is noise, but it means deletability is not unique to 1. And all the
power sits in texts of length 2–5: from length 6 up, *no* numeral of any value
has an attested reduced form, because the corpus is too sparse to contain both
versions of a longer text. This test is running on about 120 informative
occurrences.

## U2 — it counts the same things

| | distinct targets | tokens |
|---|---|---|
| counted by 1 | 92 | 199 |
| counted by 2–7 | 162 | 981 |
| counted by both | 56 | — |

61% of 1's targets are also counted by other values, and 1 sits in the ordinary
counting slot for signs like 240, 156, 235. So 1 is not a private symbol
attached to its own vocabulary — it is a numeral like the rest.

It is used in slightly different proportions across targets (chi2 p = .039),
which is weak and expected either way.

## U3 — writing it varies by site and by object

This is the strongest result. An optional marker in free variation splits by
scribal community. It does.

| | writes the 1 | |
|---|---|---|
| seals | 190 / 880 | **22%** |
| tablets | 37 / 344 | **11%** |
| pottery | 7 / 45 | 16% |

chi2 **p = .0001**. By site, also p = .0001 (SI1 148/724 = 20%, SI29 16/46 = 35%,
SI16 16/41 = 39%).

Whether a 1 gets written depends on where you are and what you are writing on —
which is the behaviour of an optional convention, not of information content.
Tablets, the mass-produced end of the corpus, drop it twice as often as seals.

## U4 — it sits where numerals sit

| | n | mean position |
|---|---|---|
| value 1 | 282 | 0.431 |
| values 2–9 | 1153 | 0.406 |

Mann-Whitney **p = .32** — indistinguishable. The 1 is not doing some other job
elsewhere in the text; it occupies the numeral slot.

## Verdict

**Supported, not proven.** Three of four tests pass, and the fourth is neutral
in the right direction:

- it behaves positionally like a numeral (U4)
- it counts the same nouns other numerals count (U2)
- it is droppable in a way 2 and 3 are not (U1, p = .008)
- whether it is written depends on scribe and medium, not on content (U3)

Taken together the reading is that a bare sign means one, and the stroke is an
optional emphasis or clarification. Under that reading the observed 282 tokens
are the visible remainder of a much larger true count, and the underlying
distribution does fall monotonically from 1 the way a counting system should.

What would settle it is a matched pair of near-identical seals from one site,
one writing the 1 and one not. U1 found 18 such pairs; that is enough to suggest
it and not enough to close it. As everywhere else in this project, the binding
constraint is corpus size ([10-more-data.md](10-more-data.md)).
