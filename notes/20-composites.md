# Signs that are other signs written twice

Two errors of mine, found by asking to see the glyphs I had claimed did not
exist.

## Error 1 — "no glyph in the font" was mostly wrong

`data/parsed/glyphs.json` gives each sign a `unicode` field. I had been reading
it with a pattern that matched a **single** codepoint, `&#xE31C;`. Signs whose
field holds a *sequence* — `&#xE31C;&#xE31C;` — failed that pattern and I
recorded them as unrenderable.

**44 attested signs are sequences, 192 tokens.** They render perfectly; you just
have to emit every codepoint. Twenty of them, 142 tokens, are one sign repeated:

| sign | = | tokens |
|---|---|---|
| **617** | 615 + 615 | 59 |
| 34 | 32 + 32 | 18 |
| **56** | **55 + 55** | 10 |
| 821 | 820 + 820 | 10 |
| 792 | 809 + 809 | 9 |
| 219 | 220 + 220 | 6 |
| 401 | 400 + 400 | 5 |
| 791 | 790 + 790 | 5 |
| 36 | 33 + 33 | 3 |
| 893 | 892 + 892 | 3 |

The rest are mixtures — 41 is `31 + ? + 31`, 101 is `? + 100 + ?`, 552 is
`550 + 551`.

The genuinely unreadable set is only **twelve** signs, and none of them is a
mystery worth chasing: eleven carry `&#x2047;` — the DOUBLE QUESTION MARK, the
digitizer's own marker for *I could not identify this* — and one (999) is
blank. Together they are 16 tokens. There is no image to recover; the source
never had one.

## Error 2 — sign 56 is twenty-four

I wrote in [16-twelve.md](16-twelve.md) that sign 56 "cannot be read" and listed
it as the loose end that could move the numeral picture. It reads fine. It is
**sign 55 written twice**, and sign 55 is twelve strokes, so 56 is **twenty-four
strokes** — 3 rows of 8. Confirmed by rendering.

The doubling convention is not an assumption. It is checkable against two cases
where the answer is already known independently:

| composite | parts | doubling predicts | long-stroke series says |
|---|---|---|---|
| 34 | 32 + 32 | 2 + 2 = **4** | id − 30 = **4** ✓ |
| 36 | 33 + 33 | 3 + 3 = **6** | id − 30 = **6** ✓ |

Both agree. The composite is the sum of its parts, so **56 = 12 + 12 = 24**.

## But 24 cannot carry any weight

Deduplicated, sign 56 has **3 tokens**, not 10. The raw count was inflated by
repeated texts, and the three survivors are:

```
[56, 415, 60, 240, 772, 740]
[91, 56, 2, 417, 890, 892]
[31, 56, 705, 575]
```

Its behavioural profile is correspondingly meaningless — target overlap with the
numerals is 0.142 against a 0.483 baseline, on three data points.

So the corrected numeral distribution is:

| value | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 12 | 24 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| tokens | 271 | 742 | 289 | 76 | 53 | 37 | 60 | 9 | 3 | **37** | **3** |

What this changes and does not change:

- **Changes:** the script demonstrably *can* write above twelve, and the way it
  does so is by doubling. The loose end flagged in
  [16-twelve.md](16-twelve.md) is closed — sign 56 does not overturn anything.
- **Does not change:** twelve is still the only well-attested quantity above
  nine. Three tokens at 24 is a spelling, not a tier.
- **Slightly strengthens twelve.** If the writing system's device for going
  beyond a value is to double it, then a sign meaning "many" would not need a
  doubled form. A doubled twelve is more consistent with twelve being a real
  quantity than with it being a vague plural — which was the open alternative in
  [16-twelve.md](16-twelve.md). Weak evidence, on three tokens, but it points
  one way.

## Error 3 — the 154 + 156 merge got dropped

[18-allographs.md](18-allographs.md) accepted this merge on three independent
grounds. Then `apply_merges.py` applied the A sets mechanically, and 154 + 156
had been classified **B** by the shape pipeline, so it was silently excluded.

It is a borderline case that fell the wrong side of one threshold: their Dice
overlap is 0.776 rather than ~1.0, because the bodies are identical and the top
decoration differs. But their **chamfer distance is 0.0041, below the 0.00433
cut for an A set** — by that measure it qualifies. Add Parpola numbering both
P004, and a passed behavioural test, and three sources agree against one.

Restored as a documented override in `src/apply_merges.py`.

Fixing it exposed a second bug: the merge map was applied in a single pass, so a
sign mapped *onto* 154 stayed on 154 after 154 was itself remapped to 156.
Replaced with union-find, which also makes overlapping sets compose correctly
instead of the later one silently winning. Final inventory **591 → 528**.

## The general point

Forty-four of the corpus's 591 "signs" are not signs. They are another sign
written two or three times, and the database encodes them that way explicitly —
the information was sitting in plain view in a field I was parsing with too
narrow a pattern.

This has a bearing on the inventory question that
[19-merge-impact.md](19-merge-impact.md) was about. Sign 617 alone has 59 tokens
and is two copies of 615; it appeared as a distinct competitor in the terminal
slot analysis ([12-slots.md](12-slots.md)). Whether a doubled sign is one sign,
two signs, or a third thing is a real question and none of these notes have
asked it.
