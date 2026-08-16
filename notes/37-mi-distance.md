# 37 — Dependence extends to distance four, but most of it is local

## Result

Bias-corrected mutual information does **not** die immediately after adjacent
signs. Against a surrogate preserving every observed bigram exactly, the real
corpus retains small but reproducible excess MI at separations 2, 3, and 4.
Separations 5 and 6 do not survive the six-distance reading: k = 5 is only
nominally borderline and k = 6 is null.

The scale matters. At k = 1 the real corpus exceeds its exact-position null by
**1.231 bits**. Beyond what the bigrams already predict, excesses at k = 2–4
are only **0.068, 0.078, and 0.052 bits**. The corpus therefore has measurable
middle-distance dependency, but it is dominated by local order rather than a
slow, high-amplitude decay.

## Estimator and sampling units

For every separation `k`, the sample is all ordered pairs `(sign_i,
sign_{i+k})` within the 2,086 deduplicated `(text, site, object)` records from
the corrected `lines_merged.json`. Different k values have different sample
sizes because short texts contribute no distant pair.

The plug-in MI is severely upward biased in a 527-type inventory. I apply the
Miller–Madow entropy correction in bits:

```text
I_MM = I_plugin - (Kxy - Kx - Ky + 1) / (2 N ln 2)
```

where `Kx`, `Ky`, and `Kxy` are occupied marginal and joint cells at that
distance. This removes the leading finite-sample term; it does not make 573
pairs at k = 6 a large sample.

The pointwise 95% confidence band is a 1,000-run site × object stratified text
bootstrap. Since ordinary richness-like bootstrap MI is shifted upward by
duplicated records, the interval uses centered bootstrap deviations; the raw
bootstrap medians remain in the JSON. Texts, not isolated pairs, are the
resampling clusters.

## Two nulls

Every effect is displayed beside both controls.

### Exact-position null

Five hundred runs shuffle each absolute slot only within exact `(length,
position, site, object)` strata. This preserves frequency, position, length,
site, and medium while destroying which signs share a text.

### Exact-bigram surrogate

A fitted first-order model could blur the very bigrams it is supposed to hold
constant. Instead, the script uses an exact recombination move: among texts of
the same length, site, and object, suffixes are exchanged after a shared pivot
sign. The incoming prefix is unchanged; because the pivot is identical, the
two outgoing edges are merely exchanged; every internal suffix edge moves as a
block. Thus the complete directed bigram multiset is exactly invariant.

Each of 300 surrogates receives 30 sweeps. The preservation assertion is
checked in code. On average 49.97% of records differ from their original text
(minimum 47.99%), after about 19,224 effective tail permutations. The remaining
half are irreducible under the strict length/site/object move—mainly rare texts
without a shared pivot. That makes this control conservative: structure trapped
in an unrecombined record remains in the null.

## Curve

| k | pairs N | plug-in MI | MM correction | **MM MI, 95% bootstrap** | position null, 95% | excess / p | exact-bigram null, 95% | excess / p |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 7,073 | 3.093 | 0.194 | **2.899 (2.841–2.959)** | 1.668 (1.643–1.691) | **+1.231 / .002** | 2.899 (exact) | 0 / 1.000 |
| 2 | 5,023 | 2.365 | 0.265 | **2.101 (2.025–2.172)** | 1.670 (1.643–1.695) | **+0.431 / .002** | 2.033 (2.018–2.049) | **+0.068 / .0033** |
| 3 | 3,324 | 2.330 | 0.287 | **2.043 (1.962–2.132)** | 1.800 (1.769–1.832) | **+0.243 / .002** | 1.965 (1.941–1.987) | **+0.078 / .0033** |
| 4 | 2,025 | 2.489 | 0.291 | **2.198 (2.078–2.305)** | 2.063 (2.024–2.107) | **+0.135 / .002** | 2.145 (2.113–2.180) | **+0.052 / .0033** |
| 5 | 1,113 | 2.771 | 0.261 | **2.510 (2.359–2.653)** | 2.435 (2.382–2.484) | +0.075 / .002 | 2.471 (2.427–2.512) | +0.039 / .0498 |
| 6 | **573** | 3.219 | 0.204 | **3.015 (2.831–3.210)** | 2.960 (2.896–3.025) | +0.055 / .0579 | 2.996 (2.946–3.048) | +0.019 / .249 |

All MI values are bits. P-values are empirical upper tails.

The raw MM curve rises after k = 3, which would be nonsensical as evidence for
strengthening long-range structure. Both controls rise with it. This is the
residual sparse-table problem the brief warned about: as N falls from 7,073 to
573 while hundreds of cells remain occupied, even Miller–Madow cannot make
absolute MI values directly comparable. The meaningful curve is **real minus
its same-k control**, not the bold column alone.

Applying BH across the five nontrivial exact-bigram comparisons (k = 2–6)
leaves k = 2, 3, and 4. The nominal k = 5 p = .0498 does not survive (`.04`
is its step-up boundary),
and k = 6 is plainly uninformative. Against the less restrictive positional
null, k = 1–5 survive and k = 6 does not; the bigram control is the appropriate
answer to whether distant dependence is more than propagated adjacency.

## Interpretation

Three statements follow at different strengths:

1. **Local structure is overwhelming.** Adjacency contributes 1.231 bits above
   the positional pairing null. An exact-bigram surrogate must match k = 1 by
   construction, which it does to machine precision.
2. **The middle is not wholly unstructured.** At k = 2–4, the real corpus
   carries 0.05–0.08 bits beyond a corpus with identical bigrams, lengths,
   positions, sites, and objects. A first-order local slot system is therefore
   incomplete.
3. **The available corpus does not establish a slow long-range tail.** Only
   1,113 pairs remain at k = 5 and 573 at k = 6. The k = 5 excess is fragile to
   correction and k = 6 lies inside both controls. Claims past four signs are
   currently unsupported.

This refines note 12's open question. The middle of a text is sparse but not
merely noise: dependencies span several positions. The effect could arise from
floating edge constructions, repeated administrative fields, or other
epigraphic constraints; MI alone does not select among them. It supplies no
sign values, sound values, or language assignment.

## Reproduction

```bash
.venv/bin/python src/mi_distance.py
```

Derived results are in `data/parsed/mi_distance.json`.
