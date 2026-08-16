"""If every look-alike sign is one character, what actually changes?

`src/shapes.py` grouped the rendered glyphs two ways:

  A  allograph sets        -- shapes that are the same drawing, 41 sets
  B  derivational families -- a base plus something added, 29 families

These are not the same claim. Merging an A set says two scribes drew one sign
differently. Merging a B family says a fish and a fish-with-a-bar-through-it are
the same character -- which contradicts 07-fish-as-operand.md, where the marked
fish behaves measurably differently from the plain one (never takes a
coefficient above 3, p = 1.3e-07).

So both are applied, separately, and every headline result is recomputed under
each. The question is not whether the merges are defensible but which findings
survive them.

  M0 agreement  -- do the automatic A sets recover the 15 groups picked by eye?
  M1 inventory
  M2 terminal slot          (12-slots.md -- the strongest result)
  M3 the no-repeat rule     (09-music.md)
  M4 the fish coefficient cap (07-fish-as-operand.md -- B only)
  M5 seals vs tablets       (14-object-forms.md)
"""
import json
from collections import Counter, defaultdict

import numpy as np
from scipy import stats

RNG = np.random.default_rng(0)
sf = json.load(open("data/parsed/shape_families.json"))
A_SETS = [s["members"] for s in sf["allograph_sets"]]
B_FAMS = [[f["base"]] + [m["id"] for m in f["members"]]
          for f in sf["derivational_families"]]
HAND = json.load(open("data/parsed/usermerges.json"))["groups"]

lines = json.loads(open("data/parsed/lines.json").read())
ins = {}
for i in json.loads(open("data/parsed/inscriptions.json").read()):
    ins[i["cisi"] or f"#{i['seal_id']}"] = i
raw = [(tuple(g for g in l["signs"] if g), l.get("site"),
        (ins.get(l.get("artifact")) or {}).get("obj_class")) for l in lines]
raw = [r for r in raw if r[0]]
base_freq = Counter(g for t, _, _ in raw for g in t)


def build(groups):
    m = {}
    for grp in groups:
        keep = max(grp, key=lambda i: base_freq[i])
        for i in grp:
            m[i] = keep
    return m


MAPS = {"none": {}, "A only": build(A_SETS), "A + B": build(A_SETS + B_FAMS)}


def corpus(m, dedup=True):
    out, seen = [], set()
    for t, s, o in raw:
        t2 = tuple(m.get(g, g) for g in t)
        if dedup:
            k = (t2, s)
            if k in seen:
                continue
            seen.add(k)
        out.append((t2, s, o))
    return out


# ------------------------------------------------------------------ M0
print("=== M0: do the automatic sets recover the 15 groups picked by eye? ===")
aidx = {}
for k, s in enumerate(A_SETS):
    for i in s:
        aidx[i] = k
bidx = {}
for k, s in enumerate(B_FAMS):
    for i in s:
        bidx[i] = k
hit_a = hit_b = miss = 0
for g in HAND:
    ka = {aidx.get(i) for i in g}
    kb = {bidx.get(i) for i in g}
    if len(ka) == 1 and None not in ka:
        hit_a += 1
        tag = f"A set {ka.pop()}"
    elif len(kb) == 1 and None not in kb:
        hit_b += 1
        tag = f"B family {kb.pop()}"
    else:
        miss += 1
        tag = "not recovered"
    print(f"  {str(g):<20} {tag}")
print(f"\n  recovered as one A set: {hit_a}   as one B family: {hit_b}   "
      f"missed: {miss}")

# ------------------------------------------------------------------ M1
print("\n=== M1: inventory ===")
print(f"  {'merges':<10} {'signs':>6} {'hapax':>7} {'n>=20':>7} {'median':>7}")
for name, m in MAPS.items():
    c = Counter(g for t, _, _ in corpus(m) for g in t)
    n = len(c)
    print(f"  {name:<10} {n:>6} {sum(1 for v in c.values() if v==1):>7} "
          f"{sum(1 for v in c.values() if v>=20):>7} "
          f"{sorted(c.values())[n//2]:>7}")

# ------------------------------------------------------------------ M2
print("\n=== M2: the terminal slot ===")


def mh(recs, a, b):
    by = defaultdict(list)
    for t, _, _ in recs:
        by[len(t)].append(set(t))
    num = den = o = e = 0.0
    for _, ss in by.items():
        n = len(ss)
        if n < 10:
            continue
        r1 = sum(1 for s in ss if a in s)
        r2 = sum(1 for s in ss if b in s)
        if not r1 or not r2 or r1 == n or r2 == n:
            continue
        x = sum(1 for s in ss if a in s and b in s)
        num += x - r1 * r2 / n
        den += r1 * r2 * (n - r1) * (n - r2) / (n * n * (n - 1))
        o += x
        e += r1 * r2 / n
    return (num / den ** .5 if den > 0 else 0.0), o, e


for name, m in MAPS.items():
    recs = [r for r in corpus(m) if len(r[0]) > 1]
    j, s = m.get(740, 740), m.get(520, 520)
    if j == s:
        print(f"  {name:<10} 740 and 520 merged into one sign — test destroyed")
        continue
    z, o, e = mh(recs, j, s)
    print(f"  {name:<10} 740/520: obs {o:.0f} exp {e:.1f}  z = {z:+.2f}")

# ------------------------------------------------------------------ M3
print("\n=== M3: the no-repeat rule ===")
for name, m in MAPS.items():
    recs = corpus(m)
    ts = [t for t, _, _ in recs]
    obs = sum(1 for t in ts if len(set(t)) < len(t))
    tok = [g for t in ts for g in t]
    freq = Counter(tok)
    V = sorted(freq)
    p = np.array([freq[g] for g in V], float)
    p /= p.sum()
    lens = [len(t) for t in ts]
    sim = []
    for _ in range(300):
        d = RNG.choice(len(V), size=sum(lens), p=p)
        i = r = 0
        for L in lens:
            if len(set(d[i:i + L].tolist())) < L:
                r += 1
            i += L
        sim.append(r)
    mu, sd = float(np.mean(sim)), float(np.std(sim))
    print(f"  {name:<10} texts with a repeat: {obs} ({obs/len(ts):.1%})  "
          f"expected {mu:.0f} ({mu/len(ts):.1%})  z = {(obs-mu)/sd:+.1f}")

# ------------------------------------------------------------------ M4
print("\n=== M4: the fish coefficient cap (B merges only) ===")
NUM = set(range(1, 8)) | {31, 32, 33, 34, 35} | set(range(12, 20))


def val(g):
    return g if g < 8 else g - 30 if g > 30 else g - 10


for name, m in MAPS.items():
    plain, marked = [], []
    for t, _, _ in corpus(m):
        for i, g in enumerate(t):
            if i == 0 or t[i - 1] not in NUM:
                continue
            v = val(t[i - 1])
            g0 = g
            if m.get(220, 220) == m.get(g0, g0) and g0 != 220:
                pass
            if g0 == m.get(220, 220):
                plain.append(v)
            elif g0 in (m.get(x, x) for x in (231, 233, 226, 234)):
                marked.append(v)
    if not marked:
        print(f"  {name:<10} marked fish no longer exist as separate signs")
        continue
    hi_p = sum(1 for v in plain if v > 3)
    hi_m = sum(1 for v in marked if v > 3)
    tab = [[hi_p, len(plain) - hi_p], [hi_m, len(marked) - hi_m]]
    print(f"  {name:<10} plain fish coeff>3: {hi_p}/{len(plain)}   "
          f"marked: {hi_m}/{len(marked)}   "
          f"p = {stats.fisher_exact(tab)[1]:.2e}")

# ------------------------------------------------------------------ M5
print("\n=== M5: seals vs tablets, what ends the text (Harappa) ===")
for name, m in MAPS.items():
    recs = [r for r in corpus(m) if r[1] == "SI2" and r[2] in ("seal", "tablet")]
    j, f4 = m.get(740, 740), m.get(400, 400)
    tab = []
    for oc in ("seal", "tablet"):
        d = [t for t, _, o in recs if o == oc]
        last = Counter(t[-1] for t in d)
        keys = sorted({m.get(x, x) for x in (740, 400, 520, 390)})
        tab.append([last[k] for k in keys])
        print(f"  {name:<10} {oc:<7} n={len(d):<4} " +
              "  ".join(f"{k}:{last[k]/max(len(d),1):.0%}" for k in keys))
    keep = [i for i in range(len(tab[0])) if tab[0][i] + tab[1][i] >= 5]
    if len(keep) > 1:
        t2 = [[tab[r][i] for i in keep] for r in (0, 1)]
        print(f"  {name:<10} -> chi2 p = {stats.chi2_contingency(t2)[1]:.2e}\n")
