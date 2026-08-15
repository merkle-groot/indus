"""Hypothesis: the never-counted signs are people/roles in a household or
village, and their arrangement encodes a hierarchy.

Predictions that distinguish this from the alternatives:

  H1 co-occurrence -- a household has several members, so role signs should
     appear together in one text MORE than chance. If instead each seal names
     one owner, they should be mutually EXCLUSIVE (less than chance).
  H2 uniqueness -- you have one father. Role signs should rarely repeat within
     a text, unlike commodity signs.
  H3 consistent order -- a hierarchy means rank, and rank means that when two
     roles co-occur they appear in a fixed order. Test each pair, then check
     whether the significant orderings are transitive enough to form one chain.
  H4 the top -- if 400 is the head, it should sit at one extreme.

Also worth noting up front: in a household census you would count the children
and the animals. The never-counted signs are never counted at all, which is
awkward for a roster reading before we even start.
"""
import json
from collections import Counter, defaultdict
from itertools import combinations

import numpy as np
from scipy import stats

NUM = set(range(1, 8)) | set(range(12, 20)) | set(range(31, 36))
NEVER = [615, 527, 742, 595, 636, 400, 90, 60, 690, 435, 741, 100, 740, 920, 151]
COUNTED = [700, 384, 585, 226, 156, 803, 790, 55, 900, 140, 840, 923, 503, 220,
           575, 390, 240, 61, 904, 845, 806, 235]

lines = json.loads(open("data/parsed/lines.json").read())
texts = [tuple(l["signs"]) for l in lines if l["signs"]]
uniq = sorted(set(texts))
freq = Counter(g for t in texts for g in t)
N = len(uniq)

# ------------------------------------------------------------------ H1
print("=== H1: do never-counted signs co-occur with each other? ===")
print("  roster reading -> more than chance;  one-owner reading -> less\n")


def cooc(group, label):
    pres = {g: np.array([g in t for t in uniq]) for g in group}
    obs = exp = 0
    hits = []
    for a, b in combinations(group, 2):
        o = int((pres[a] & pres[b]).sum())
        e = pres[a].sum() * pres[b].sum() / N
        obs += o
        exp += e
        if e >= 1:
            hits.append((a, b, o, e))
    print(f"  {label}: observed co-occurrences {obs}, expected {exp:.1f}, "
          f"ratio {obs/exp if exp else 0:.2f}")
    return hits


h_never = cooc(NEVER, "never-counted")
cooc(COUNTED, "counted      ")
print("\n  strongest never-counted pairs (obs vs exp):")
for a, b, o, e in sorted(h_never, key=lambda r: -(r[2] - r[3]))[:8]:
    print(f"    {a:>4} + {b:<4} obs {o:>3}  exp {e:>5.1f}  ratio {o/e:.2f}")

# ------------------------------------------------------------------ H2
print("\n=== H2: do they repeat within a text? ===")
print("  a household has one father; a commodity can repeat\n")
for label, group in (("never-counted", NEVER), ("counted", COUNTED)):
    rep = tot = 0
    for t in uniq:
        c = Counter(g for g in t if g in group)
        for g, k in c.items():
            tot += 1
            rep += k > 1
    print(f"  {label:<14} {rep}/{tot} sign-in-text instances repeat "
          f"({rep/tot:.1%})")

# ------------------------------------------------------------------ H3
print("\n=== H3: is there a consistent order among them? ===")
print("  rank implies that when two roles co-occur, one always precedes\n")


def order_test(group, label):
    pairs = []
    for a, b in combinations(group, 2):
        ab = ba = 0
        for t in uniq:
            if a in t and b in t:
                ia, ib = t.index(a), t.index(b)
                ab += ia < ib
                ba += ib < ia
        if ab + ba >= 6:
            p = stats.binomtest(max(ab, ba), ab + ba, .5).pvalue
            pairs.append((a, b, ab, ba, p))
    strict = [q for q in pairs if q[4] < .05]
    print(f"  {label}: {len(pairs)} pairs with >=6 co-occurrences, "
          f"{len(strict)} strictly ordered (p<.05)")
    return pairs, strict


pairs, strict = order_test(NEVER, "never-counted")
for a, b, ab, ba, p in sorted(strict, key=lambda q: q[4])[:12]:
    first, second, n1, n2 = (a, b, ab, ba) if ab > ba else (b, a, ba, ab)
    print(f"    {first} before {second}: {n1} vs {n2}   p={p:.3g}")

if strict:
    # can the strict orderings be arranged in one chain? (test transitivity)
    edge = {}
    for a, b, ab, ba, p in strict:
        edge[(a, b) if ab > ba else (b, a)] = True
    nodes = sorted({x for e in edge for x in e})
    viol = 0
    tri = 0
    for x, y, z in combinations(nodes, 3):
        for p1, p2, p3 in [((x, y), (y, z), (x, z)), ((x, z), (z, y), (x, y))]:
            if p1 in edge and p2 in edge:
                tri += 1
                if (p3[1], p3[0]) in edge:
                    viol += 1
    print(f"\n  transitivity: {tri} chains of two orderings, {viol} contradicted")
    # rank by wins
    wins = Counter()
    for (a, b) in edge:
        wins[a] += 1
        wins[b] += 0
    print("  implied ordering, earliest first:")
    print("   ", " > ".join(str(g) for g, _ in
                            sorted(wins.items(), key=lambda kv: -kv[1])))

# ------------------------------------------------------------------ H4
print("\n=== H4: where does 400 sit? ===")
for g in [400, 740, 60, 90, 690]:
    pos = [j / (len(t) - 1) for t in texts if len(t) > 1
           for j, s in enumerate(t) if s == g]
    once = sum(1 for t in uniq if t.count(g) == 1)
    inn = sum(1 for t in uniq if g in t)
    print(f"  sign {g:>4}  n={freq[g]:>4}  mean position {np.mean(pos):.3f}  "
          f"appears in {inn} distinct texts, exactly once in {once}")
print("  (0.0 = text-initial, 1.0 = text-final, corpus baseline 0.500)")
