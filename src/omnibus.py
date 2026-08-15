"""Omnibus test: does motif explain ANY of the variation in sign content?

The per-sign scan pays a 666-test correction. This asks the question once,
which is far better powered: treat each artifact as a binary sign vector and
test whether artifacts sharing a motif are more similar to each other than
chance, permuting motif labels *within* site x object-class strata so site and
object type cannot supply the answer.

Statistic: PERMANOVA-style pseudo-F on Jaccard distances.
"""
import json
import sys
from collections import Counter

import numpy as np

RNG = np.random.default_rng(0)
N_PERM = 2000
MIN_MOTIF = 15
DEDUP = "--nodedup" not in sys.argv

seals = json.loads(open("data/parsed/inscriptions.json").read())
sites = json.loads(open("data/parsed/sites.json").read())
DROP = {None, "unrecorded", "unknown", "none", "Unknown"}

arts = []
for s in seals:
    m = s.get("motif")
    if m in DROP:
        continue
    txt = tuple(g for g in s["glyphs"] if g != 0)
    if not txt:
        continue
    arts.append({"text": txt, "signs": set(txt), "motif": m,
                 "stratum": (sites.get(s.get("site"), "?"), s.get("obj_class"))})

if DEDUP:
    seen, uniq = set(), []
    for a in arts:
        k = (a["text"], a["motif"])
        if k not in seen:
            seen.add(k)
            uniq.append(a)
    arts = uniq

mc = Counter(a["motif"] for a in arts)
arts = [a for a in arts if mc[a["motif"]] >= MIN_MOTIF]

vocab = sorted({g for a in arts for g in a["signs"]})
vi = {g: i for i, g in enumerate(vocab)}
X = np.zeros((len(arts), len(vocab)), bool)
for i, a in enumerate(arts):
    for g in a["signs"]:
        X[i, vi[g]] = True

motif = np.array([a["motif"] for a in arts])
strata = sorted({a["stratum"] for a in arts})
si = {s: i for i, s in enumerate(strata)}
stratum = np.array([si[a["stratum"]] for a in arts])

print(f"artifacts {len(arts)}   signs {len(vocab)}   motifs {len(set(motif))}   "
      f"strata {len(strata)}   dedup={DEDUP}")
print("  " + ", ".join(f"{m}({c})" for m, c in Counter(motif).most_common()))

# ---- Jaccard distance matrix
inter = (X.astype(np.int16) @ X.T.astype(np.int16)).astype(np.float64)
size = X.sum(1).astype(np.float64)
union = size[:, None] + size[None, :] - inter
D = 1.0 - np.divide(inter, union, out=np.zeros_like(inter), where=union > 0)
np.fill_diagonal(D, 0.0)

# ---- Gower-centred matrix; pseudo-F via trace algebra
n = len(arts)
A = -0.5 * D ** 2
G = A - A.mean(0, keepdims=True) - A.mean(1, keepdims=True) + A.mean()
tot = np.trace(G)


def pseudo_f(lab):
    """Between-group SS via sum over groups of centroid trace."""
    ss_w = 0.0
    groups = np.unique(lab)
    for g in groups:
        m = lab == g
        k = m.sum()
        if k < 2:
            continue
        ss_w += np.trace(G[np.ix_(m, m)]) - G[np.ix_(m, m)].sum() / k
    ss_b = tot - ss_w
    a, b = len(groups) - 1, n - len(groups)
    return (ss_b / a) / (ss_w / b)


obs = pseudo_f(motif)
by_strat = [np.flatnonzero(stratum == k) for k in range(len(strata))]
null = np.empty(N_PERM)
for t in range(N_PERM):
    p = motif.copy()
    for idx in by_strat:
        if len(idx) > 1:
            p[idx] = RNG.permutation(p[idx])
    null[t] = pseudo_f(p)

pv = (np.count_nonzero(null >= obs) + 1) / (N_PERM + 1)
r2 = None
# variance explained
ss_w = sum(np.trace(G[np.ix_(motif == g, motif == g)])
           - G[np.ix_(motif == g, motif == g)].sum() / max((motif == g).sum(), 1)
           for g in np.unique(motif))
r2 = (tot - ss_w) / tot

print(f"\npseudo-F observed : {obs:.4f}")
print(f"null mean / sd    : {null.mean():.4f} / {null.std():.4f}")
print(f"null 95th pct     : {np.percentile(null, 95):.4f}")
print(f"permutation p     : {pv:.4f}   ({N_PERM} stratified permutations)")
print(f"variance explained by motif (R2) : {r2:.4%}")
