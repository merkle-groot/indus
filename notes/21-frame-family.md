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
collocation. Added as a documented override in `src/apply_merges.py`, joining
154+156. Neither the merge nor its absence changes any result — it is correct
rather than consequential.

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
