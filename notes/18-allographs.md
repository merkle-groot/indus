# Fifteen allograph merges read off the chart

Script: `src/usermerges.py`. Fifteen groups of sign ids proposed as the same
symbol, identified by eye from the rendered sign chart:

```
154,156   544,563   850,856   775,776   595,597
541,561   511,514   411,413   350,351   307,308
229,242   160,161   31,600    275,276,278   61,62,63
```

Re-rendered at 115px (`scratchpad/groups.png`) and checked one group at a time.
All fifteen look right on the glyphs. Allograph identification is a
palaeographic judgement, so that is the primary evidence; the statistics below
can only corroborate, contradict, or stay silent.

## What Parpola's numbering says

| | |
|---|---|
| agrees | **1** |
| conflicts | **1** |
| no opinion (crosswalk covers fewer than 2 members) | 13 |

- **154 + 156 → P004.** Independent confirmation from the crosswalk built in
  [10-more-data.md](10-more-data.md).
- **31 + 600 — the crosswalk disagrees**, mapping 31 → P144 and 600 → P145,
  and pairing 600 with **32** instead.

On the glyphs the crosswalk is wrong. Rendered side by side, 31 and 600 are both
a single plain vertical stroke; 32 is two strokes. Sign 600 has 3 tokens, so
nothing rides on it — but it is worth recording that the imported crosswalk has
at least one visible error, which is the kind of thing that should temper how
much weight it carries elsewhere. This is the second independent hit against it,
after [05-radix.md](05-radix.md) found the 817/861 merge only three-quarters
supported.

The crosswalk's silence on 13 of 15 groups is itself informative: it covers 185
of 591 ids, and these merges live almost entirely in the rare tail it never
reached.

## Only two groups can be tested at all

A behavioural test needs both members to be reasonably common. Thirteen of the
fifteen groups pair a common sign with a rare one, so they are simply not
testable. The method here is the one that validated Parpola's 817/861 merge:
same position, same neighbours, same medium.

Baseline first — two *unrelated* common signs share a next-sign profile at
cosine **0.097** (median) and **0.604** (90th percentile). A real merge should
beat the 90th percentile.

**154 vs 156 — passes.**

| | 154 (n=33) | 156 (n=43) |
|---|---|---|
| mean position | 0.899 | 0.840 |
| | p = **.55** | |
| next-sign cosine | **0.803** | (baseline 90th pct 0.604) |
| site cosine | 0.920 | |
| object cosine | **1.000** | |

Same position, same following context well above baseline, same distribution
across sites and media — and Parpola independently calls them one sign. The
preceding-sign cosine is only 0.198, which is the one dissenting number.

**61 vs 63 — mixed.**

Position agrees (p = .48), but next-sign cosine is 0.148 and preceding 0.166,
both around the baseline median rather than above the 90th percentile. On 9
tokens for 63 that is weak evidence either way, but it does not corroborate. The
glyphs also differ slightly: 61 and 62 carry a crossing stroke that 63 appears
to lack. **This is the least supported of the fifteen.**

## What accepting all fifteen buys

| | signs | hapax | n≥20 (testable) | median count |
|---|---|---|---|---|
| as-is | 591 | 215 (36%) | 77 | 2 |
| + these 15 merges | **574** | 207 (36%) | **78** | 2 |

420 tokens are involved, out of 9098. Two signs newly cross the testability
line: **413** (21) and **850** (22).

This is consistent with what [10-more-data.md](10-more-data.md) found for
Parpola's own merges — **allograph collapsing does not break the data ceiling.**
The hapax rate does not move at all. Correctness is its own reason to do this,
but it is not a route around corpus size.

## One result does improve

Merging 154 into 156 produces a sign in 73 texts that ends 75% of them, and it
sharpens the strongest finding in the project. Exclusion against the jar sign
740, in the terminal slot from [12-slots.md](12-slots.md):

| | observed | expected | z |
|---|---|---|---|
| 740 / 520 | 5 | 91.8 | −14.20 |
| 740 / 390 | 54 | 89.7 | −5.89 |
| **740 / 156 (merged)** | **6** | **31.2** | **−6.40** |
| 740 / 151 | 8 | 26.5 | −5.11 |
| 740 / 527 | 6 | 22.6 | −5.28 |

Separately they scored −4.73 and −4.33. Merged, the sign becomes the
**third-strongest competitor for the terminal slot**, ahead of 151, 527 and 617.
Splitting one sign in two had been diluting a real paradigm member.

## Status

- All fifteen accepted on the glyphs; map written to
  `data/parsed/usermerges.json`.
- 154+156 is the one group with both independent confirmation and a passed
  behavioural test.
- 61+62+63 is flagged as unconfirmed — 63 may be a separate sign.
- The merges are stored as a map rather than applied to `lines.json`, so every
  earlier result stands as computed and any analysis can opt in.
