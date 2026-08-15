"""Are our signs 817 and 861 really one sign, as Parpola's numbering says?

Both are near-obligatorily followed by the stroke sign for 2, and together they
account for most of the "2 outranks 1" anomaly in 04-numerals.md. Parpola gives
both the number P385. If that is right, the anomaly has one cause, not two.

But a merge is a claim that can fail. Two ids are the same sign only if they
behave the same way. Four tests, any of which can refute it:

  T1 what follows -- same sign, same collocate distribution
  T2 position     -- same sign, same place in the text
  T3 co-occurrence-- true allographs are usually complementary; a scribe picks
                     one. Seeing both in one text argues they contrast.
  T4 geography    -- allograph variation often splits by site
  820 is carried along as a control: it behaves similarly but Parpola does NOT
  merge it, so it should fail the tests that 817/861 pass.
"""
import json
from collections import Counter

from scipy import stats

TRIO = [817, 820, 861]
SHORT = set(range(1, 8))
LONG = {31, 32, 33, 34, 35}
TWOROW = set(range(12, 20))


def value(g):
    if g in SHORT:
        return g
    if g in LONG:
        return g - 30
    if g in TWOROW:
        return g - 10
    return None


lines = json.loads(open("data/parsed/lines.json").read())
ins = {i["seal_id"]: i for i in json.loads(open("data/parsed/inscriptions.json").read())}
Y2P = {int(k): v for k, v in json.load(open("data/parsed/crosswalk.json"))["y2p"].items()}

print("Parpola numbers:", {g: Y2P.get(g, "unmapped") for g in TRIO})

texts = [[g for g in l["signs"] if g] for l in lines]
site_of = {}
for l in lines:
    site_of[id(l)] = l.get("site")

# ------------------------------------------------------------------ T1
print("\n=== T1: what follows each sign ===")
foll = {g: Counter() for g in TRIO}
tot = {g: 0 for g in TRIO}
for t in texts:
    for a, b in zip(t, t[1:]):
        if a in foll:
            tot[a] += 1
            foll[a][value(b)] += 1
for g in TRIO:
    c = foll[g]
    num = sum(v for k, v in c.items() if k is not None)
    dist = ", ".join(f"{k}x{v}" for k, v in sorted(c.items(), key=lambda kv: -kv[1])
                     if k is not None)
    print(f"  {g}: {tot[g]:>4} followed by something, {num} by a numeral "
          f"({num/tot[g]:.1%})   {dist}")

# does 817's numeral distribution differ from 861's?  from 820's?
def numvec(g):
    return {k: v for k, v in foll[g].items() if k is not None}


def cmp(a, b):
    ka = numvec(a)
    kb = numvec(b)
    keys = sorted(set(ka) | set(kb))
    tab = [[ka.get(k, 0) for k in keys], [kb.get(k, 0) for k in keys]]
    # collapse to "value 2" vs "not 2" -- the only cell with real mass
    t2 = [[ka.get(2, 0), sum(v for k, v in ka.items() if k != 2)],
          [kb.get(2, 0), sum(v for k, v in kb.items() if k != 2)]]
    return stats.fisher_exact(t2)[1], t2


print("\n  is the numeral it takes the same? (value 2 vs anything else)")
for a, b in [(817, 861), (817, 820), (861, 820)]:
    p, t2 = cmp(a, b)
    print(f"    {a} vs {b}: {t2[0]} vs {t2[1]}   p = {p:.4f}"
          f"   {'same' if p > .05 else 'DIFFERENT'}")

# ------------------------------------------------------------------ T2
print("\n=== T2: position in the text ===")
pos = {g: [] for g in TRIO}
for t in texts:
    if len(t) < 2:
        continue
    for i, g in enumerate(t):
        if g in pos:
            pos[g].append(i / (len(t) - 1))
for g in TRIO:
    p = pos[g]
    print(f"  {g}: n={len(p):>4}  mean {sum(p)/len(p):.3f}")
for a, b in [(817, 861), (817, 820), (861, 820)]:
    u = stats.mannwhitneyu(pos[a], pos[b])
    print(f"    {a} vs {b}: Mann-Whitney p = {u.pvalue:.2e}"
          f"   {'same' if u.pvalue > .05 else 'DIFFERENT'}")

# also: absolute slot, since these sit near the start
print("\n  absolute slot from the start of the text")
for g in TRIO:
    s = [i for t in texts for i, x in enumerate(t) if x == g]
    print(f"  {g}: mean slot {sum(s)/len(s):.2f}  "
          f"first sign in text {sum(1 for x in s if x == 0)}/{len(s)} "
          f"({sum(1 for x in s if x==0)/len(s):.0%})")

# ------------------------------------------------------------------ T3
print("\n=== T3: do they ever share a text? ===")
present = {g: sum(1 for t in texts if g in t) for g in TRIO}
for a, b in [(817, 861), (817, 820), (861, 820)]:
    both = sum(1 for t in texts if a in t and b in t)
    exp = present[a] * present[b] / len(texts)
    print(f"  {a}+{b}: observed {both}, expected if independent {exp:.1f}")
print("  (true allographs of one sign are usually complementary: a scribe picks one)")

# ------------------------------------------------------------------ T4
print("\n=== T4: geography ===")
sites = {g: Counter() for g in TRIO}
for l in lines:
    s = l.get("site") or "?"
    for g in set(x for x in l["signs"] if x):
        if g in sites:
            sites[g][s] += 1
allsites = sorted({s for c in sites.values() for s in c},
                  key=lambda s: -sum(sites[g][s] for g in TRIO))[:5]
print("  " + "site".ljust(16) + "".join(f"{g:>8}" for g in TRIO))
for s in allsites:
    print(f"  {s[:15]:<16}" + "".join(f"{sites[g][s]:>8}" for g in TRIO))
tab = [[sites[g][s] for s in allsites] for g in (817, 861)]
print(f"  817 vs 861 across sites: chi2 p = {stats.chi2_contingency(tab)[1]:.4f}")

# ------------------------------------------------------------------ redo
print("\n=== the 'value 2' anomaly, recounted with 817+861 as one sign ===")
vals = Counter()
after = Counter()
for t in texts:
    prev = None
    for g in t:
        v = value(g)
        if v is not None:
            vals[v] += 1
            if prev in TRIO:
                after[v] += 1
        prev = g
print(f"  all numeral tokens by value : "
      f"{', '.join(f'{k}:{vals[k]}' for k in sorted(vals))}")
print(f"  of which sit after 817/820/861: "
      f"{', '.join(f'{k}:{after[k]}' for k in sorted(after))}")
rest = Counter({k: vals[k] - after.get(k, 0) for k in vals})
print(f"  excluding those             : "
      f"{', '.join(f'{k}:{rest[k]}' for k in sorted(rest))}")
p385 = sum(1 for t in texts for g in t if g in (817, 861))
print(f"\n  merged P385 tokens: {p385}   820 tokens: "
      f"{sum(1 for t in texts for g in t if g == 820)}")
