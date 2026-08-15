# What the objects are

Produced by `src/objects.py`. Adds `obj_code`, `obj_class`, `motif` to
`data/parsed/inscriptions.json`.

## Where this metadata came from

Two tables the first pass ignored:

- `FEATURE` + `ICONOGRAPHYFEATURES` — a CISI-style object-type code per artifact.
  25 codes, exactly one per artifact, all 2543 covered.
- `ICONOGRAPHY` — the field symbol (the animal/motif engraved on the object).
  Covers 1622 of 2543; the remaining 921 have no row.

The repo's frontend `usefulMaps.js` supplies expansions for both vocabularies.
Its `qualityMap` is unreliable — it maps `TAB:C` to "Tag" when `TAB` is plainly
*tablet* everywhere else, and the author left a `// Not too sure about this`
comment on `IMPL`. So we group by the prefix before the colon rather than
trusting that map. `symbolMap` looks sound and is used for motifs, with
sub-variants (`Bull1:W`, `Goat:4`) collapsed to the depicted subject.

## Object classes

| class | n | share |
|---|---|---|
| seal | 1469 | 57.8% |
| tablet | 897 | 35.3% |
| pottery | 70 | 2.8% |
| sealing/tag | 64 | 2.5% |
| rod | 17 | 0.7% |
| misc | 14 | 0.6% |
| implement | 8 | 0.3% |
| bangle | 4 | 0.2% |

At full granularity: stamp seals `SEAL:S` 1211, bas-relief tablets `TAB:B` 456,
incised tablets `TAB:I` 292, rectangular seals `SEAL:R` 232, copper tablets
`TAB:C` 149. Everything else is under 50.

**Seals and tablets are 93% of the corpus.** Any statement about "the Indus
script" is overwhelmingly a statement about two object types.

## Materials

Steatite 1469, faience 229, clay 214, copper 154, terracotta 25, ivory 15,
then singletons (gold, shell, limestone, gypsum, bone…). 417 unrecorded.
Note `Steatite` and `steatite` appear as separate values — uncleaned.

## Motifs

| motif | n | share |
|---|---|---|
| one-horned bull ("unicorn") | 1019 | 40.1% |
| *unrecorded* | 921 | 36.2% |
| unknown/other | 115 | 4.5% |
| gaur | 88 | 3.5% |
| rhinoceros | 63 | 2.5% |
| elephant | 51 | 2.0% |
| humped bull | 44 | 1.7% |
| zebu | 44 | 1.7% |
| tree | 27 | 1.1% |
| fish | 21 | 0.8% |

Long tail: goat, water buffalo, tiger, hare, turtle, bird, ass, composite
animals, anthropomorphic figures, a three-headed deity (3), pipal trees,
crosses, a maze.

Of the 1622 artifacts with a recorded motif, the one-horned bull is **63%**.
On seals specifically it is 939 of the 1181 seals with a motif — **80%**.

## The interesting cross-tabs

**Object type splits by site.** Seals cluster at Mohenjo-daro (934 of 1469);
tablets cluster at Harappa (673 of 897). Mohenjo-daro yields 934 seals and 212
tablets; Harappa yields 256 seals and 673 tablets — close to inverted.

Do not over-read this yet. It could be a genuine functional difference between
the two cities, or it could be excavation and publication history. Needs a
check against dig reports before it means anything.

**Text length tracks object type.**

| class | mean signs per artifact | max |
|---|---|---|
| seal | 4.83 | 17 |
| sealing/tag | 4.53 | 9 |
| tablet | 3.81 | 11 |
| rod | 3.71 | 5 |
| pottery | 2.70 | 7 |

(Per *artifact*, summing across lines — hence maxima above the 13-sign longest
single line.) Seals carry the longest texts, pottery graffiti the shortest.

**Motif concentrates by object type.** Pottery is essentially motif-free (69 of
70 unrecorded). Sealings/tags carry unicorns (33) and elephants (11) but little
else. Tablets are mostly unrecorded, and where recorded they are far more
diverse than seals — rhinoceros 41 and humped bull 37 rank near the top, where
on seals the unicorn swamps everything.

## Caveats

- The 921 unrecorded motifs are not "objects without a motif" — pottery and many
  tablets genuinely have no field symbol, but for seals a blank is more likely a
  gap in the database. The two cases are not distinguished. Don't treat
  UNRECORDED as a category.
- Still no damage flags (see [01-corpus.md](01-corpus.md)), so length statistics
  by object class mix intact and broken texts.
