"""Generalise the fish result: which sign families show a modifier that caps
the quantity you may write in front of them?

Grouping: the id numbering encodes shape families (verified by eye on the
rendered chart -- strokes 1-35, fish 215-244, U-forms 700-786, circles
790-845). We cut families at id gaps > 5.

Within a family the *base* is taken to be the most frequent member and the
*variants* are the rest. For each family we ask the question that worked on the
fish: does the base accept larger preceding numerals than its variants do?
"""
import json
from collections import Counter, defaultdict

from scipy import stats

GAP = 5
MIN_BASE = 20      # base must be reasonably attested
MIN_OBS = 12       # need this many numeral-preceded observations per side

NUMS = {}
for i in range(1, 8):
    NUMS[i] = i
for i in range(31, 36):
    NUMS[i] = i - 30
for i in range(12, 20):
    NUMS[i] = i - 10

lines = json.loads(open("data/parsed/lines.json").read())
texts = [tuple(l["signs"]) for l in lines if l["signs"]]
uniq = sorted(set(texts))          # dedup: mass production must not inflate
freq = Counter(g for t in texts for g in t)

# ------------------------------------------------------------- families
ids = sorted(freq)
fams, cur = [], [ids[0]]
for a, b in zip(ids, ids[1:]):
    if b - a <= GAP:
        cur.append(b)
    else:
        fams.append(cur)
        cur = [b]
fams.append(cur)

# numerals are their own thing, not a "base + modifier" family
fams = [f for f in fams if not set(f) & set(NUMS)]

print(f"families found (gap>{GAP}): {len(fams)}")
print(f"  sizes: {Counter(len(f) for f in fams).most_common()}\n")


def preceding_values(sign_set):
    """Values of numerals immediately preceding any sign in the set."""
    v = Counter()
    for t in uniq:
        for j, g in enumerate(t):
            if g in sign_set and j > 0 and t[j - 1] in NUMS:
                v[NUMS[t[j - 1]]] += 1
    return v


rows = []
for f in fams:
    base = max(f, key=lambda g: freq[g])
    variants = [g for g in f if g != base]
    if freq[base] < MIN_BASE or not variants:
        continue
    vb, vv = preceding_values({base}), preceding_values(set(variants))
    nb, nv = sum(vb.values()), sum(vv.values())
    if nb < MIN_OBS or nv < MIN_OBS:
        continue
    hb = sum(c for k, c in vb.items() if k >= 4)
    hv = sum(c for k, c in vv.items() if k >= 4)
    orr, p = stats.fisher_exact([[hb, nb - hb], [hv, nv - hv]])
    rows.append({
        "base": base, "n_base": freq[base], "variants": variants,
        "n_var_tokens": sum(freq[g] for g in variants),
        "obs_base": nb, "obs_var": nv,
        "hi_base": hb, "hi_var": hv,
        "rate_base": hb / nb, "rate_var": hv / nv,
        "or": orr, "p": p,
        "maxval_base": max(vb) if vb else 0, "maxval_var": max(vv) if vv else 0,
    })

rows.sort(key=lambda r: r["p"])
print(f"families testable (base>={MIN_BASE} tokens, >={MIN_OBS} obs each side): {len(rows)}\n")
print(f"  {'base':>5} {'#var':>5} {'obsB':>5} {'obsV':>5} "
      f"{'>=4 base':>9} {'>=4 var':>8} {'maxB':>5} {'maxV':>5} {'p':>9}")
for r in rows:
    print(f"  {r['base']:>5} {len(r['variants']):>5} {r['obs_base']:>5} {r['obs_var']:>5} "
          f"{r['rate_base']:>8.1%} {r['rate_var']:>8.1%} "
          f"{r['maxval_base']:>5} {r['maxval_var']:>5} {r['p']:>9.3g}")

sig = [r for r in rows if r["p"] < .05 and r["rate_base"] > r["rate_var"]]
print(f"\n  families where the base outranks its variants at p<.05: {len(sig)}")
print(f"  bases: {[r['base'] for r in sig]}")

json.dump(rows, open("data/parsed/families.json", "w"), indent=1)
print("\nwrote data/parsed/families.json")
