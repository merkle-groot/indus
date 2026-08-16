# The frame/rake family, and a correction I had to make twice

Script: `src/framefamily.py`. This started as a question about one unreadable
sign and turned into a strong collocation plus a lesson about circular grouping.

## Where it started

Sign **316** is one of the twelve signs the digitizer could not identify
([20-composites.md](20-composites.md)). The suggestion was that it might be a
modification of sign **360**.

The database numbers signs roughly by shape, and 316 sits in a revealing place:

```
315   H frame: two uprights, one crossbar, no teeth
316   ??      the unidentified sign
317   ladder: two uprights, two rungs, no teeth
318   frame + crossbar + five teeth
320   curved frame + crossbar + four teeth
322   frame + crossbar + four teeth
323   frame + crossbar + five teeth
324   hourglass frame + three teeth
325   frame + hatched bar + four teeth
326   frame + two teeth
330   frame + two teeth      <- identical to 326
360   closed-top frame, two legs, no teeth
```

So 316 lives inside a family of frames, ladders and rakes, and 360 is the same
morphology. The instinct was sound: whatever 316 is, it is one of these.

## The real finding

Sign **920** follows this family far more than it follows anything else:

| | followed by 920 |
|---|---|
| the frame/rake family | **17 / 45 (38%)** |
| any sign in the corpus | **36 / 7028 (0.51%)** |

**p = 1.1e-27** on deduplicated texts. That is a frozen collocation on the scale
of the 817/861 + value-2 pair from [05-radix.md](05-radix.md), and it is
unaffected by any of the argument below about subdividing the family.

## The correction

I then claimed the family splits by shape — that *toothed* rakes take 920 and
*plain* frames do not — and reported p = 4e-06.

**That was circular.** I had assigned 324, 325, 326 and 330 to the "plain"
group. All four plainly have teeth. I had sorted them by their 920 count, which
is zero, rather than by their shape, and then tested whether the groups differed
in 920 rate. The grouping variable was the outcome variable.

Classified honestly, off the 260px renders and nothing else:

| | followed by 920 |
|---|---|
| toothed: 318, 320, 322, 323, 324, 325, 326, 330 | 15 / 27 (56%) |
| plain: 315, 317, 360 | 2 / 18 (11%) |

**p = 0.0041**, not 4e-06. And sign 317 is a plain ladder that takes 920 twice,
so the boundary leaks in the direction that hurts.

Then the robustness check that finishes it off:

| | | p |
|---|---|---|
| all toothed vs plain | 15/27 vs 2/18 | 0.0041 |
| **dropping sign 320** | **6/14 vs 2/18** | **0.096** |

Nine of the fifteen toothed hits are sign 320 by itself. "Teeth predict the 920"
is really "**sign 320 takes 920**", which is a different and much smaller claim.

**Withdrawn.** The family-level collocation stands; the shape-based subdivision
does not.

## 326 and 330 are one sign

Identified by eye and confirmed on the renders: closed frame, two outer legs,
two inner teeth, indistinguishable. Three texts between them, 0/3 on the 920
collocation.

**Correction:** I added this as an override in `src/apply_merges.py` and said
the shape pipeline had missed it. It had not — 326 and 330 were already one of
the 41 A sets and were already being merged. I had checked only the
*derivational* families, not the allograph sets. The override is redundant
(union-find absorbs it harmlessly) and the claim was wrong.

## What this says about sign 316

Less than I claimed last time.

- It is in the frame/rake family. That much is well supported by the numbering.
- It has 2 tokens, neither followed by 920. Against a family rate of 38% that is
  no evidence in either direction.
- I previously said this weakly favoured the plain-frame end, where 360 sits.
  That inference depended on the toothed/plain split, so it goes too.

One thing does hold: 316 and 323 sit adjacent on H-1005, and this corpus avoids
repeating a sign within a text ([09-music.md](09-music.md)), so those two are
not the same sign.

## And a problem with the photograph

[20-composites.md](20-composites.md) recorded a circled mark on H-1005 described
as "two long diagonal scratches crossing like an X". A frame or a rake is not an
X — and sign **530**, which is in that same four-sign inscription, *is* an
X-shaped sign. The circle is most likely on 530, one or two slots off target.

That extraction was self-reported as medium confidence and looks to have been
right to be. The M-802 and M-840 annotations are unaffected; those were pinned
by three and seven matched signs respectively.

## The lesson worth keeping

The [dossier](../dossier.html) lists "deduplicate first" and "control for
position" among the project's standing rules. This adds one:

> **Define groups before you look at the outcome.** Sorting signs by the
> behaviour you are about to test guarantees a significant result and teaches
> nothing.

It is the same failure mode as the 25 sign–motif associations that
deduplication erased ([03-sign-motif.md](03-sign-motif.md)) — a pattern
manufactured by the analysis rather than found in the data. The difference is
that this one took a second pair of eyes to catch.

## Two more merges, and the source's own similarity table

**318 + 323.** Identified by eye. Same structure — frame, crossbar, five teeth
— differing only in bar height and tooth length.

The evidence is split, and unlike 154+156 the pixel test is *against* it:

| for | against |
|---|---|
| both followed by 920 (2/2 and 2/4) | chamfer **0.0072**, above the 0.00433 A-set cut |
| next-sign cosine **0.816** | 226 px residual after alignment |
| never share a text | preceding-sign cosine 0.000 |
| shape pipeline already paired them (as a B family) | site/object cosines 0.32 / 0.29 |

Applied, but flagged in `src/apply_merges.py` as the weakest of the three
overrides. On 2 and 4 tokens the behavioural agreement is thin, and the
geometry genuinely disagrees. Merged the sign has 16 tokens and runs 4/6 on the
920 collocation.

Inventory now **591 → 527**.

### What the shape pipeline actually is

Only two eye-found merges were genuinely missed:

| | what the pipeline did |
|---|---|
| 154 + 156 | paired, but classified B (chamfer *below* the A cut — a threshold error) |
| 318 + 323 | paired, classified B (chamfer above the cut — arguably correct) |
| 326 + 330 | already an A set; already merged. My override was redundant. |

And then the finding that reframes all of it. Comparing the raw `unicode` field
in `glyphs.json` — a plain string comparison, no rendering — gives **41 groups
covering 103 attested ids**. The shape pipeline's A sets are **41 groups
covering 103 ids**, and they are the same 41.

The 256px rasterisation, the Dice and chamfer measures, the alignment search
over scale and offset, the two-component Gaussian mixture used to pick the
cut — for the A sets, all of it reproduces `glyphs.json` codepoint equality
exactly. Those ids do not merely look alike; the font draws them with the
*identical codepoint*, so they were never distinguishable in the first place.

That is not a criticism of the pipeline's B families, which do real work. But
the A half of it is a one-line string comparison wearing a lab coat, and the
right way to describe those 41 groups is "the database gave two numbers to one
glyph", not "clustering discovered these are the same".

### GLYPHSIMILARITY

The source SQL turns out to contain a table I had never parsed:
`GLYPHSIMILARITY(GLYPHID1, GLYPHID2)` — the database author's own record of
which signs resemble which.

It holds **69 pairs**, 51 of them between attested signs. It is silent on every
case examined here: 318/323, 326/330, 154/156, 316/360, 31/600, 817/861 — none
listed, and 316, 318 and 360 appear in it not at all.

So it neither confirms nor contradicts anything. Written to
`data/parsed/glyph_similarity.json` for completeness. Its main value is
negative: it is the third independent source (after Parpola's crosswalk and the
shape pipeline) to have no opinion on most of the inventory, which is a fair
summary of how settled Indus sign identity actually is.
