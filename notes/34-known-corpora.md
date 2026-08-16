# 34 — A known-corpus control is possible, but only partly

## Result

On an exactly matched slice of 1,000 records and 100 sign/component types,
Indus does **not** simply pattern with either comparison corpus. Its no-repeat
effect is much stronger than both a deciphered administrative corpus and a
real non-linguistic emblem corpus. Its sign-specific numeral-side structure is
shared with the administrative corpus, although the latter is almost uniformly
one-sided. The 740/520 exclusion is the only pairwise exclusion to survive the
same scan in either ordered corpus.

That is not a classifier. The only usable non-linguistic data are unordered
two-dimensional emblems, so terminal and numeral-side tests are undefined for
them. On the statistics that can be compared, the answer is mixed rather than
“Indus patterns with X.”

## Data and provenance

### Known ordered sign corpus

I used ORACC's *Early Dynastic IIIa administrative texts* archive
([download](https://oracc.museum.upenn.edu/json/epsd2-admin-ed3a.zip)). The
archive's own catalogue says “CC0,” links the
[CC0 1.0 dedication](https://creativecommons.org/publicdomain/zero/1.0/), and
has timestamp `2022-12-07T11:16:27`. The downloaded ZIP's SHA-256 is
`8d4b7bfb6cba7190c2c150ca8b24860c25a430e6ffd0f18ce03ff49092a0a645`.

The unit is a transcribed line. Top-level ORACC grapheme descriptions are sign
tokens; ORACC's numeric annotation supplies the numeral flag. I excluded 2,857
lines containing an unreadable or unparsable grapheme and seven empty lines,
then deduplicated exact `(sequence, provenience, object type)` records. That
removed 10,912 copies and left 9,611 lines. Sign identities are replaced by
opaque IDs in the derived output: no transcription is copied into the repo.

This is an attested, deciphered administrative corpus with short records, not a
claim that its document conventions match the Indus corpus.

### Known non-linguistic sign system

I used the Kansas cattle-brand data accompanying Youngblood et al.,
[“Statistical signals of copying are robust to time- and
space-averaging”](https://doi.org/10.1017/ehs.2023.5), pinned to source commit
[`01e05a5`](https://github.com/masonyoungblood/cattle_brand_data/tree/01e05a546f0d30a4c6c2c35f57fae0e6633a6c5e).
These are registered emblems: the source's 13-character code contains four
component fields plus a body-location field. I excluded 178 malformed codes
and deduplicated the same design at the same registry location across books,
removing 56,551 repeated records and retaining 35,056.

The GitHub repository states no licence. Its raw data therefore remain under
gitignored `data/external/`; only aggregate statistics are committed. This is
also why the script pins a commit and checksum rather than vendoring the CSV.

Crucially, the four component fields do **not** encode a reading sequence. The
source's diagram is a two-dimensional brand, and the last component field can
even distinguish relative arrangements. Treating catalogue-field order as
text order would invent the very evidence this control is meant to test.
Consequently:

- component count, inventory, hapax rate, and within-emblem repetition are
  defined;
- “terminal sign” and “numeral side” are not defined and were not run;
- the repeat null reallocates the unordered components conditional on component
  count, rather than pretending they occupy textual positions.

I also checked the public Linear B sequence release discussed in note 24. Its
first 513 records are observed sequences, but the remainder are augmented or
duplicated and the observed subset contains no usable numeral annotation. The
ORACC archive therefore supplies the cleaner complete ordered control. Public
potters'-mark and *mon* collections located during the search were images or
feature catalogues of isolated two-dimensional marks, not tokenized sequences;
they cannot make the missing ordered non-linguistic comparison.

## Matching and controls

The full corpora differ too much in size and inventory for direct effect-size
comparison:

| corpus | deduplicated records | tokens | inventory | mean length | hapax / inventory | repeated records |
|---|---:|---:|---:|---:|---:|---:|
| Indus | 2,086 | 9,159 | 527 | 4.391 | 177 / 527 (33.6%) | 78 (3.7%) |
| ED IIIa | 9,611 | 34,695 | 1,365 | 3.610 | 426 / 1,365 (31.2%) | 535 (5.6%) |
| cattle brands | 35,056 | 91,427 | 459 | 2.608 | 117 / 459 (25.5%) | 2,947 (8.4%) |

For the like-for-like analysis I retained records composed entirely of each
corpus's 100 most frequent types, then drew 1,000 without replacement while
requiring all 100 types to occur. There were respectively 1,061, 1,996, and
29,224 eligible records. Thus every comparison below has exactly `N = 1,000`
and `V = 100`. Top-100 restriction necessarily makes the matched hapax statistic
nearly vacuous; the full-corpus row above is the honest descriptive hapax
comparison.

For both ordered corpora, each null shuffle permutes an absolute position only
within exact `(length, position, site, object class)` strata. For the brand
repeat test, the length-conditioned component pool is the strongest available
unordered analogue; registry locations are too sparse to support a useful
within-location shuffle and object class is constant. There are 500 null runs,
so their direct empirical tail resolution is `1/501 = .002`.

## Like-for-like results

### Length, hapax, and no-repeat

| corpus | mean length | hapax types | texts with repeat | matched null mean (95%) | z | lower-tail p |
|---|---:|---:|---:|---:|---:|---:|
| Indus | 4.069 | 0 | 28 (2.8%) | 107.7 (94–124) | **−10.37** | .002 |
| ED IIIa | 3.689 | 1 | 90 (9.0%) | 63.1 (50–77) | **+3.85** | 1.000 |
| cattle brands | 2.679 | 0 | 94 (9.4%) | 83.3 (68–100) | +1.34 | .908 |

Every effect is next to its control. Indus alone has strong repeat avoidance.
The known ordered corpus repeats *more* than its positional control, while
cattle-brand repetition is compatible with its unordered control. The old
frequency-draw baseline is not used.

### Terminal-slot exclusion

I scanned all pairs whose members occurred in at least 20 matched records. For
each pair, its co-occurrence count was compared with the same 500 exact-position
surrogates. The normal approximation to that surrogate distribution supplies
the one-sided p-values for BH, because 500 empirical permutations cannot resolve
the roughly `10^-5` tail required by 1,485–2,145 simultaneous tests. The direct
empirical p is reported beside the selected effect and bottoms out at .002.

| corpus | eligible signs | pairs | BH exclusions | strongest observed | positional-null mean (95%) | z | empirical p |
|---|---:|---:|---:|---:|---:|---:|---:|
| Indus | 55 | 1,485 | **1** | 740+520: 2 | 13.01 (8–19) | **−4.03** | .002 |
| ED IIIa | 66 | 2,145 | 0 | opaque pair: 0 | 8.85 (4–14) | −3.52 | .002 |
| cattle brands | — | — | — | **infeasible: no linear order** | — | — | — |

The sole BH survivor is the preregistered 740/520 terminal pair. The known
ordered corpus contains suggestive pairwise exclusions, as any sparse corpus
will, but none survives the complete scan. This does not imply an absence of
structure there; it says this particular rare-pair statistic is not a generic
detector of an ordered sign system.

### Numeral side

As in note 28, the statistic is Pearson overdispersion across non-numeral signs
with at least 15 numeral adjacencies. Side labels are permuted within exact
`(length, focal position, site, object)` strata.

| corpus | adjacency events | eligible signs | pooled numeral-left | observed Q | null mean (95%) | upper p |
|---|---:|---:|---:|---:|---:|---:|
| Indus | 1,056 | 23 | 52.1% | **462.8** | 347.5 (325.5–370.6) | .002 |
| ED IIIa | 747 | 16 | 97.0% | **242.2** | 44.3 (22.2–77.8) | .002 |
| cattle brands | — | — | — | **infeasible: no order or numeral annotation** | — | — |

Both ordered corpora have sign-dependent numeral adjacency beyond position and
metadata. Their effects are not the same shape: ED IIIa is almost uniformly
numeral-left, whereas Indus has a nearly balanced pooled direction and the
signal is heterogeneity among signs. This validates the statistic as capable
of detecting known administrative ordering, while warning against equating two
significant Q values.

## What the control answers

The comparison does **not** sort the three corpora onto a single linguistic ↔
non-linguistic axis:

- full-corpus hapax share puts Indus close to the known ordered corpus, but it
  is descriptive because the inventories are unmatched;
- numeral-side overdispersion occurs in both ordered corpora;
- no-repeat avoidance and the surviving terminal exclusion are distinctive to
  Indus in this matched analysis;
- the non-linguistic corpus cannot adjudicate any statistic requiring order.

The positive result is methodological: the pipeline distinguishes different
kinds of structure rather than returning the same answer everywhere. The
negative result is equally important: available open non-linguistic sign data
do not provide the ordered control required to classify the Indus pattern.
Nothing here assigns values to Indus signs or identifies a language.

## Reproduction

```bash
.venv/bin/python src/known_corpora.py
```

The script downloads pinned source files into `data/external/`, verifies both
SHA-256 checksums and ORACC's embedded CC0 statement, and writes only derived
statistics to `data/parsed/known_corpora.json`.
