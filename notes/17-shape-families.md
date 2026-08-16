# Are 591 signs really 591 signs?

Scripts: `src/shapes.py` (rendering and grouping),
`src/shapes_validate.py` (external, null and corpus tests).

Figures: [shape-families.png](shape-families.png) is the complete contact sheet.
[shape-residuals.png](shape-residuals.png) shows the added ink.
[shape-disagreements.png](shape-disagreements.png) shows every disagreement
with Parpola. [shape-distance-distribution.png](shape-distance-distribution.png)
shows the cuts.

## The question

There are **591 distinct ids** in `data/parsed/lines.json`, not merely 400.
Are they 591 signs? Or did the catalogue split the same drawing into several
ids, and split base signs from forms carrying small marks?

The old scripts could not answer that. `src/families.py` cuts at id gaps over
five. `src/modifiers.py` cuts at gaps over two and manually repairs the fish
range. Both assume that nearby numbers look alike. This analysis ignores the
number when making a group. It reads the font.

## The three traps

**The font is evidence, not the inscriptions.** Exact equality in this font is
strong evidence that two catalogue ids have the same encoded drawing. It does
not prove that every palaeographic distinction survived font construction.
This matters for the high precision and low recall below.

**Containment is cheap.** A vertical stroke occurs inside hundreds of complex
signs. That does not make every complex sign a modified numeral. A proposed
base therefore has to cover a substantial part of the larger sign, as well as
being covered by it.

**Duplicate texts.** All corpus tests use exactly
`sorted(set(tuple(l["signs"]) for l in lines))`. The 2613 corpus lines become
**1980 distinct texts**. Token counts printed on the figures use the full
corpus; inferential tests do not.

## Rendering and comparison

The font is `data/yaj/src/assets/fonts/sk_indus_script-webfont.ttf`. Each
mapping in `data/parsed/glyphs.json` is rendered at 256 px. Multi-codepoint
mappings are rendered as sequences. Ink is thresholded, cropped, and put on a
64 x 64 canvas in two ways: aspect preserved, and width and height stretched
independently. The latter asks the weaker question, "would these match after
distortion?"

Registration searches scales 0.90, 1.00 and 1.10, and x/y shifts of -2, 0 and
2 pixels. Dice selects the alignment. IoU-equivalent Dice, both directional
containments, and chamfer distance remain separate fields in
`data/parsed/shape_families.json`. Connected components, holes, Euler number,
aspect and ink fraction are also recorded.

Twelve attested ids cannot be rendered. Id 999 has no mapping. Ids 12, 25,
106, 316, 376, 445, 515, 516, 546, 547 and 606 point to a codepoint absent from
the font cmap. They are excluded from shape comparison and remain singleton
signs in every inventory count. The composite mappings for 34, 36, 41, 56 and
58 do render; they are not silently discarded.

## Where the cuts came from

Complete-linkage clustering is used for allographs. Every pair in a set must
clear the same Dice-distance cut. Single linkage is used for derivation because
two modified forms need not resemble each other; every retained member must
still pass a direct common-base check.

| quantity | low component | high component | selected cut | evidence for two components |
|---|---:|---:|---:|---|
| nearest Dice distance | 0.000 | 0.377 | **0.0043** | BIC -1427 vs -367 |
| best directional containment | 0.704 | 0.849 | **0.792** | BIC -1023.9 vs -1024.2 |
| larger-sign coverage in containment tail | 0.238 | 0.570 | **0.570** | BIC -108.4 vs -82.7 |

The allograph split is real and sharp. The containment split is not. A
two-component model is worse by 0.3 BIC, effectively a tie. Its intersection is
reported because it is a reproducible criterion, but the resulting families
are candidates, not established equivalences. The extra coverage cut uses the
centre of the high-coverage component. This removes the generic-substroke
failure visible in a naive run.

## A — exact visual allographs

The analysis finds **41 sets containing 103 ids**. Merging each set removes
**62 ids**. Thirty-three sets are pairs. Six have three members, one has four,
and one has fifteen.

| examples | token counts | aspect Dice | aspect chamfer |
|---|---|---:|---:|
| 31, 600 | 145, 3 | 1.000 | 0.000 |
| 61, 62, 63 | 73, 2, 9 | 1.000 | 0.000 |
| 226, 234 | 26, 3 | 1.000 | 0.000 |
| 405, 407 | 2, 11 | 1.000 | 0.000 |
| 526, 527 | 3, 34 | 1.000 | 0.000 |

These are not merely close after registration. Their normalized pixels are
identical. Many ids map to the same font codepoint. That is why the fitted low
distance component sits at zero.

## External test — Parpola

The crosswalk supplies Parpola labels for 185 renderable attested ids. It
contains 53 expert-merged pairs in that universe.

| measure | result |
|---|---:|
| visual merged pairs in mapped universe | 21 |
| agree with Parpola | 20 |
| visual merge, Parpola separates | 1 |
| Parpola merge, visual separates | 33 |
| pair precision | **0.952** |
| pair recall | **0.377** |
| adjusted Rand | **0.540** |

The visual rule is conservative. Its sole false positive is 31 versus 600.
They are the same pixels and use the same font codepoint, while Parpola calls
them P144 and P145. On the supplied picture the visual merge is the more
natural decision. It could still reflect information lost when the font was
made.

The false negatives explain the low recall. Some look like genuine
palaeographic allographs: 336/337 and 803/806 retain the same outline with
internal strokes changed. Others are not the same drawing in this font at all:
790 is a circle while 850 is a bow-tie; 617 is a grid while 831 is an oval.
Parpola is plainly grouping at a level broader than pixel identity in those
cases. The disagreement sheet shows all 34 pairs, not selected examples.

## A null

Parpola labels were permuted 5000 times over the same 185 ids. This preserves
both visual and expert cluster sizes.

| | observed | permutation mean | null 95% | p |
|---|---:|---:|---:|---:|
| adjusted Rand | 0.540 | 0.00001 | -0.0018 to 0.0253 | **0.00020** |
| matching visual pairs | 20 | 0.066 | 0 to 1 | **0.00020** |

The visual structure is not the arbitrary output of a clustering algorithm.
It agrees with an independent expert classification far beyond chance.

## Distributional test of A

All 162 within-set pairs are tested, including pairs without Parpola labels.
Each gets a pool of 100 non-group pairs closest in the two endpoint
log-frequencies. Neither target sign may occur in its control pair. One control
per target is drawn 5000 times.

| measure | allograph pairs | matched non-groups | null 95% | p in predicted direction |
|---|---:|---:|---:|---:|
| initial/medial/final cosine | **0.740** | 0.531 | 0.479-0.584 | **0.00020** |
| left/right neighbour cosine | **0.185** | 0.038 | 0.021-0.058 | **0.00020** |
| co-occurrence rate | 0.0021 | 0.0034 | 0.0000-0.0113 | 0.439 |

Only one of 162 allograph pairs ever co-occurs, once. That direction is
consistent with alternation, but it is not unusual after frequency matching.
The position and neighbour results are the real cross-check. Exact visual
duplicates behave much more alike than equally frequent unrelated signs.

## B — base plus added ink

The conservative containment rule returns **29 families and 45 base-member
relations**. It covers 74 ids and 2144 full-corpus tokens. The contact sheet
puts the base first. Some examples:

| base | members | base in member | member in base |
|---|---|---:|---:|
| 220 | 231, 233 | 0.992, 0.947 | 0.871, 0.882 |
| 840 | 844 | 0.992 | 0.873 |
| 111 | 112 | 1.000 | 0.912 |
| 70 | 71 | 0.949 | 0.674 |
| 322 | 325 | 0.899 | 0.763 |
| 95 | 90, 98, 100, 142, 150 | 0.803-0.881 | 0.618-0.724 |

This recovers the plain fish with the internal-line and top-cross forms. It
does **not** recover the whole hand-identified fish family. Roof, X and flanking
change too much ink to clear the global rule. That is a useful failure: shape
containment alone does not reproduce the prior interpretation.

Residual ink is the member minus a one-pixel dilation of the aligned base. The
dilation suppresses registration fringes. It does not eliminate them, as the
residual sheet makes clear. Only **one residual class recurs across different
bases**: the internal vertical stroke in 220 to 231 and 111 to 112. The other
43 relations produce 43 separate residual classes. This is not evidence for a
small productive modifier inventory.

## Distributional test of B

The prediction is different here. A modifier can change a sign's behaviour.
Interchangeability is not required, and a two-sided comparison is reported.

| measure | base-member pairs | matched non-groups | null 95% | two-sided p |
|---|---:|---:|---:|---:|
| initial/medial/final cosine | 0.622 | 0.618 | 0.524-0.713 | 0.931 |
| left/right neighbour cosine | **0.138** | 0.085 | 0.045-0.133 | **0.029** |
| co-occurrence rate | 0.0152 | 0.0154 | 0.0037-0.0350 | 0.891 |

Five of 45 pairs co-occur, in 20 distinct texts. Position and co-occurrence are
ordinary after frequency matching. Neighbour overlap is a little higher than
chance. That supports shared graphical or functional cores, not identity. It
would be wrong to treat this as the allograph test repeated.

## Replacing id adjacency

The old gap-two rule, including its manual fish merge, contains 3029
within-family pairs. Only 23 of the 45 new
base-member relations fall inside them. The gap-five rule contains 15134 pairs
and catches 34 of 45. In the other direction, the shape rule recovers only
0.8% and 0.2% of those enormous pair sets.

| old proxy | old families | new relations inside old groups | share of new relations |
|---|---:|---:|---:|
| gap over 2 | 71 | 23 / 45 | 51.1% |
| gap over 5 | 13 | 34 / 45 | 75.6% |

So numbering has some shape order, but it is much too coarse to be a family
definition. Nearly a quarter of the shape relations cross even the gap-five
groups. Most pairs created by either adjacency cut have no visual containment
support.

## What this actually means

**The inventory is genuinely large.** Exact font-level allographs reduce 591
attested ids to **529**, a fall of 62 or **10.5%**. That result is externally
precise and distributionally supported. It is also tied to one modern font and
misses many broader expert allographs.

If every containment family is collapsed to its base, the nominal total is
**487**, a fall of 104 or **17.6%** from the raw inventory. That is the requested
A+B count. It is not an honest count of graphical primitives. Forty-five
derived forms require an estimated **44 modifier types**, because only one
residual repeats. Adding those modifiers back gives **531 primitives**. On this
evidence derivational factoring supplies no compression beyond A at all.

That negative result is the central result. The font confirms some duplicated
catalogue entries. It confirms local base-plus-mark relations, including two
plain-fish variants. It does not reveal a small reusable modifier system hiding
under hundreds of ids. The claim that the apparent inventory is absurdly large
is not supported by this test.
