# Corpus: sourcing and validation

## What we're using

`data/yaj/population-script.sql` from [yajnadevam/indus-website](https://github.com/yajnadevam/indus-website),
parsed by `src/parse_yaj.py` into `data/parsed/`.

Important: that repo's author advances a Sanskrit "cryptanalytic decipherment" that
the field does not accept. We are taking **only the epigraphic layer** from it —
which signs, in what order, on which artifact, from which site. None of the
decipherment claims are imported. The SQL's `DECIPHERMENT` table is ignored.

## What we rejected and why

| Source | Problem |
|---|---|
| `mayig/indus-valley-script-corpus` | Excellent format w/ allograph feature vectors, but only 179 artifacts (M-001…M-199). ~5% coverage. |
| `Kee2u/Deciphering_the_Indus_Valley_Script` | Wells/Fuls ICIT data lived on an AWS RDS instance that is gone. Repo ships tooling, not texts. |
| `ramnerd/IVC_script_decoded` | 556 sequences only, and ships a self-asserted full decoding. |

Keep `mayig` around — its allograph features are the best available answer to
"are these two glyphs the same sign?", which we will need.

## Shape of the data

```
artifacts            2543
lines of text        2613
sign tokens          11135
distinct signs        591
mean line length     4.26   median 4   max 13
hapax legomena        199   (34% of the sign inventory)
top 20 signs         48% of all tokens
top 100 signs        85% of all tokens
```

Sites: Mohenjo-daro 1202, Harappa 970, then a long tail (Lothal 80, Dholavira 74,
Kalibangan 54, …52 sites total).

## Reading order — resolved

Glyph sequences are stored **left-to-right as they appear on the artifact**.
The `DIRECTION` column says 2440 of 2543 are `R/L`, i.e. the script reads
right-to-left. So stored order is *reversed* relative to reading order.

This is confirmed against an external fact rather than taken on trust:

- Sign id **740** is the most frequent sign in the corpus at **11.4%** of all tokens.
- Its mean relative position is **0.109** from the left edge — hard against the
  left margin, which under R/L reading means hard against the **end** of the text.

That is the signature of the well-known "jar" sign (Mahadevan 342), universally
reported as both the most frequent Indus sign and overwhelmingly text-final.
The corpus reproduces this without being told to. Good evidence the digitization
is faithful.

`data/parsed/lines.json` therefore stores signs in **reading order** (reversed
from storage), one record per physical line.

## Known limitations of this corpus

- `ISCOMPLETE` is `Y` for all 2543 rows. The field carries no information, so we
  have **no damage/breakage flags**. Broken inscriptions are silently mixed in
  with intact ones. This will bias any claim about text-initial or text-final
  signs and needs a caveat on every such result.
- No allograph consolidation. 591 distinct ids at this granularity; whether that
  is 591 *signs* is exactly the disputed question. 34% hapax rate is a symptom —
  some of those singletons are probably variants of commoner signs, not signs.
- Sign ids here are this database's own numbering, not Mahadevan's M-numbers.
  Cross-referencing published results requires a mapping we do not yet have.
