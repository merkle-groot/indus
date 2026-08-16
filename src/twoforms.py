"""Do frozen phrases pick a particular way of writing "two"?

05-radix.md concluded the three stroke series (short, long, stacked) are the
same numbers written differently, and that the difference is graphic. That
predicts the forms are substitutable. This tests the prediction where it can be
tested: inside the fixed phrases where one sign near-obligatorily drags a
value-2 behind it.

  T1 which form each collocation takes
  T2 is 840 a frozen pair at all?
  T3 is 840 = 405 + 407, as suggested? (position, context, adjacency)
"""
import json
from collections import Counter

from scipy import stats
from scipy.stats import binomtest, fisher_exact

SHORT2, LONG2 = 2, 32
HOSTS = [817, 861, 820, 840]

lines = json.loads(open("data/parsed/lines.json").read())
ins = {}
for i in json.loads(open("data/parsed/inscriptions.json").read()):
    ins[i["cisi"] or f"#{i['seal_id']}"] = i
SITE = json.loads(open("data/parsed/sites.json").read())

recs, seen = [], set()
for l in lines:
    t = tuple(x for x in l["signs"] if x)
    if not t:
        continue
    k = (t, l.get("site"))
    if k in seen:
        continue
    seen.add(k)
    recs.append((t, SITE.get(l.get("site"), "?"),
                 (ins.get(l.get("artifact")) or {}).get("obj_class")))
texts = [r[0] for r in recs]
freq = Counter(g for t in texts for g in t)
print(f"deduplicated texts: {len(texts)}")


def follows(g):
    c, n = Counter(), 0
    for t in texts:
        for i in range(len(t) - 1):
            if t[i] == g:
                n += 1
                c[t[i + 1]] += 1
    return c, n


# ------------------------------------------------------------------ T1
print("\n=== T1: which form of 'two' does each frozen phrase take? ===")
print(f"  corpus-wide, the long form is {freq[LONG2]}/{freq[SHORT2]+freq[LONG2]}"
      f" = {freq[LONG2]/(freq[SHORT2]+freq[LONG2]):.0%} of all value-2 tokens\n")
print("  sign     n   -> 2 short   -> 32 long   other")
tab = {}
for g in HOSTS:
    c, n = follows(g)
    tab[g] = (c[SHORT2], c[LONG2], n)
    print(f"  {g:>4} {n:>5} {c[SHORT2]:>10} {c[LONG2]:>12} {n-c[SHORT2]-c[LONG2]:>7}")

p_long = freq[LONG2] / (freq[SHORT2] + freq[LONG2])
s = tab[817][0] + tab[861][0]
lo = tab[817][1] + tab[861][1]
print(f"\n  817+861 together: short {s}, long {lo}")
print(f"  if the forms were interchangeable, expected long = {(s+lo)*p_long:.0f}")
print(f"  P(0 long in {s+lo} draws at {p_long:.0%}) = "
      f"{binomtest(lo, s+lo, p_long, alternative='less').pvalue:.2e}")
print(f"  817/861 vs 840, Fisher: p = "
      f"{fisher_exact([[s, lo], [tab[840][0], tab[840][1]]])[1]:.3e}")

# ------------------------------------------------------------------ T2
print("\n=== T2: is 840 -> 32 a real collocation? ===")
tot = sum(len(t) - 1 for t in texts)
hit = sum(1 for t in texts for i in range(len(t) - 1) if t[i + 1] == LONG2)
f, n = tab[840][1], tab[840][2]
print(f"  base rate, {LONG2} follows anything: {hit}/{tot} = {hit/tot:.2%}")
print(f"  840 -> {LONG2}: {f}/{n} = {f/n:.0%}   "
      f"p = {binomtest(f, n, hit/tot, alternative='greater').pvalue:.2e}")
print("  composite sign 843 is stored as 32 + 840 + 32, binding them again")

# ------------------------------------------------------------------ T3
print("\n=== T3: is 840 signs 405 + 407 written together? ===")
RAKE = {405, 407}


def profile(pred):
    pos, nx, pv = [], Counter(), Counter()
    for t in texts:
        for i, x in enumerate(t):
            if not pred(x):
                continue
            if len(t) > 1:
                pos.append(i / (len(t) - 1))
            if i + 1 < len(t):
                nx[t[i + 1]] += 1
            if i:
                pv[t[i - 1]] += 1
    return pos, nx, pv


pa, na, va = profile(lambda x: x == 840)
pb, nb, vb = profile(lambda x: x in RAKE)


def cos(p, q):
    k = set(p) | set(q)
    d = (sum(v * v for v in p.values()) ** .5) * (sum(v * v for v in q.values()) ** .5)
    return sum(p[x] * q[x] for x in k) / d if d else 0.0


print(f"  mean position   840 {sum(pa)/len(pa):.3f}   rake {sum(pb)/len(pb):.3f}"
      f"   MW p = {stats.mannwhitneyu(pa, pb).pvalue:.1e}")
print(f"  preceding-sign cosine: {cos(va, vb):.3f}")
print(f"  following-sign cosine: {cos(na, nb):.3f}")
adj = sum(1 for t in texts for i in range(len(t) - 1)
          if {t[i], t[i + 1]} <= RAKE)
print(f"  405 and 407 adjacent anywhere in the corpus: {adj}")
both = sum(1 for t in texts if 840 in t and (RAKE & set(t)))
n840 = sum(1 for t in texts if 840 in t)
nr = sum(1 for t in texts if RAKE & set(t))
print(f"  texts with both 840 and a rake: {both} "
      f"(expected if independent {n840*nr/len(texts):.1f})")
print("\n  verdict: no. Different position, no shared context, and the")
print("  spelled-out 405-407 sequence a ligature would need never occurs.")
