# Direction, and whether the corpus was normalised

Script: `src/direction_normalization.py`. Answer: **not quite**. The 2440 R/L
inscriptions were reversed into analytical reading order; the 103 L/R
inscriptions were left as stored. The terminal signs show that the latter
choice was wrong.

The raw inscriptions contain 2509 physical R/L lines and 104 L/R lines. After
deduplication within each subset those become 1875 and **89 distinct
sequences**. Under the old normalization:

| subset | sign | texts | starts | ends | shuffle E at either edge | z start | z end |
|---|---:|---:|---:|---:|---:|---:|---:|
| R/L | **740** | 907 | 5 | **668** | 206.6 | -16.42 | **+37.59** |
| R/L | **520** | 162 | 2 | **139** | 37.4 | -6.85 | **+19.65** |
| R/L | 400 | 186 | 1 | **167** | 51.2 | -8.41 | **+19.42** |
| **L/R** | **740** | 34 | **25** | **1** | 11.4 | **+5.09** | **-3.91** |
| **L/R** | **520** | 5 | **4** | **0** | 1.9 | +1.96 | -1.80 |
| **L/R** | 400 | 15 | **13** | **0** | 4.7 | **+4.78** | -2.66 |

The null shuffles tokens within each text, so length, vocabulary, site, and
object class are all held fixed. The result is a clean mirror image: the same
three right-edge signs are at the end of R/L texts and at the start of L/R
texts. This is not a geographic or object-composition effect.

Reverse the L/R rows and their terminal rates become:

| sign | starts | ends | end share | z end |
|---:|---:|---:|---:|---:|
| **740** | 1 | 25 | **74%** | **+5.09** |
| **520** | 0 | 4 | **80%** | +1.96 |
| **400** | 0 | 13 | **87%** | **+4.78** |

They now agree with the large subset almost percentage for percentage. There is
no residual evidence for a direction-specific layout; the old disagreement was
an ordering error.

## What changes

`src/eda.py` now reverses every raw `GLYPHSEQUENCE` line. `lines.json` and
`lines_merged.json` have been rebuilt before continuing the investigation.
The combined terminal localisation becomes slightly sharper:

| order | distinct sequence x site | 740 final | 740 z vs position shuffle | 520 final | 520 z |
|---|---:|---:|---:|---:|---:|
| old | 2027 | 704/981 = 72% | +36.5 | 151/179 = 84% | +19.3 |
| **corrected** | **2001** | **721/972 = 74%** | **+38.2** | **152/176 = 86%** | **+19.9** |

The number of distinct sequences changes because a corrected L/R sequence can
collapse onto an already-attested R/L sequence at the same site. That is the
only way reversal can affect a presence/absence result after deduplication.

## What does not change

The [12-slots.md](12-slots.md) headline is almost order-invariant. Reversal does
not alter which signs share a text or its length; only the re-deduplication just
described moves the third decimal place.

| order | observed | expected by length | z length | z site | z object |
|---|---:|---:|---:|---:|---:|
| old | 5 | 91.9 | **-14.217** | -12.626 | -12.671 |
| **corrected** | 5 | 90.8 | **-14.140** | -12.550 | -12.636 |

So the published **z = -14.1 remains z = -14.1**. The terminal-slot finding was
diluted positionally but not manufactured statistically.

## Verdict and honest limit

**The L/R rows should be reversed, and now are.** More precisely, the
`DIRECTION` field does not describe how the `GLYPHSEQUENCE` array itself should
be transformed: both subsets arrive with the same array orientation for this
analysis. Treating the label as an ordering instruction caused the 4% error.

This diagnosis uses the already-established 740/520 terminal paradigm as its
anchor. It therefore cannot independently prove the physical direction of any
individual artefact, and it does not license a claim that the database's
direction labels are palaeographically wrong. They may refer to the artefact,
impression, or display convention. The narrower, testable conclusion is that
conditional reversal makes the two corpus subsets contradictory, while one
uniform reversal makes their distributional structure agree.
