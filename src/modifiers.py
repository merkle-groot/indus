"""Catalogue of base signs and their modified variants, with the quantity test.

Grouping: sign ids encode shape families (verified by eye against the rendered
chart). We cut at id gaps > 2. One manual merge is applied: 240-244 are plainly
fish and belong with 219-236, but sit across a gap of 4.

For each family: the most frequent member is the base, the rest are variants.
The test is the one that worked on the fish -- does the base accept larger
preceding numerals than its variants? Computed on distinct texts only, so
mass-produced duplicates cannot inflate anything.
"""
import json
from collections import Counter

from scipy import stats

GAP = 2
MERGE = [set(range(219, 245))]      # fish, verified visually

NUMS = {}
for i in range(1, 8):
    NUMS[i] = i
for i in range(31, 36):
    NUMS[i] = i - 30
for i in range(12, 20):
    NUMS[i] = i - 10

lines = json.loads(open("data/parsed/lines.json").read())
texts = [tuple(l["signs"]) for l in lines if l["signs"]]
uniq = sorted(set(texts))
freq = Counter(g for t in texts for g in t)

ids = sorted(freq)
fams, cur = [], [ids[0]]
for a, b in zip(ids, ids[1:]):
    if b - a <= GAP:
        cur.append(b)
    else:
        fams.append(cur)
        cur = [b]
fams.append(cur)

for m in MERGE:
    hit = [f for f in fams if set(f) & m]
    if len(hit) > 1:
        merged = sorted({g for f in hit for g in f})
        fams = [f for f in fams if f not in hit] + [merged]

fams = [f for f in fams if not set(f) & set(NUMS)]
fams.sort(key=lambda f: -max(freq[g] for g in f))


def prec(sign_set):
    v = Counter()
    for t in uniq:
        for j, g in enumerate(t):
            if g in sign_set and j > 0 and t[j - 1] in NUMS:
                v[NUMS[t[j - 1]]] += 1
    return v


out = []
for f in fams:
    base = max(f, key=lambda g: freq[g])
    var = sorted(g for g in f if g != base)
    if not var:
        continue
    vb, vv = prec({base}), prec(set(var))
    nb, nv = sum(vb.values()), sum(vv.values())
    hb = sum(c for k, c in vb.items() if k >= 4)
    hv = sum(c for k, c in vv.items() if k >= 4)
    rec = {
        "base": base, "n_base": freq[base],
        "variants": [{"id": g, "n": freq[g]} for g in var if freq[g] > 0],
        "n_var": sum(freq[g] for g in var),
        "obs_base": nb, "obs_var": nv, "hi_base": hb, "hi_var": hv,
        "max_base": max(vb) if vb else None, "max_var": max(vv) if vv else None,
        "vb": dict(sorted(vb.items())), "vv": dict(sorted(vv.items())),
        "p": None, "or": None,
    }
    if nb >= 12 and nv >= 12:
        orr, p = stats.fisher_exact([[hb, nb - hb], [hv, nv - hv]])
        rec["or"], rec["p"] = (None if orr != orr else orr), p
    out.append(rec)

json.dump(out, open("data/parsed/modifiers.json", "w"), indent=1)

tested = [r for r in out if r["p"] is not None]
sig = [r for r in tested if r["p"] < .05]
print(f"signs in corpus          : {len(freq)}")
print(f"families                 : {len(out)}")
print(f"base signs               : {len(out)}")
print(f"variant signs            : {sum(len(r['variants']) for r in out)}")
print(f"families testable        : {len(tested)}")
print(f"  significant at p<.05   : {len(sig)}")
print(f"  base accepts MORE      : {sum(1 for r in sig if r['hi_base']/r['obs_base'] > r['hi_var']/r['obs_var'])}")
print(f"  base accepts LESS      : {sum(1 for r in sig if r['hi_base']/r['obs_base'] < r['hi_var']/r['obs_var'])}")
print()
print(f"  {'base':>5} {'nvar':>5} {'obsB':>5} {'obsV':>5} {'>=4B':>6} {'>=4V':>6} "
      f"{'maxB':>5} {'maxV':>5} {'p':>9}")
for r in sorted(tested, key=lambda r: r["p"]):
    print(f"  {r['base']:>5} {len(r['variants']):>5} {r['obs_base']:>5} {r['obs_var']:>5} "
          f"{r['hi_base']/r['obs_base']:>5.0%} {r['hi_var']/r['obs_var']:>6.0%} "
          f"{str(r['max_base']):>5} {str(r['max_var']):>5} {r['p']:>9.3g}")
