"""Fifteen proposed allograph merges, read off the sign chart by eye.

Allograph identification is fundamentally a palaeographic judgement -- two
shapes either are the same sign or they are not, and no statistic settles it.
What statistics CAN do is three things:

  U1 corroborate  -- does an independent source (Parpola's numbering, via the
                     crosswalk in 10-more-data.md) agree, disagree, or say
                     nothing?
  U2 test         -- where both members are common enough, do they behave the
                     same way? Same position, same neighbours, same medium.
                     This is the test that validated Parpola's 817/861 merge
                     and rejected 820 (see 05-radix.md).
  U3 measure      -- what does accepting all fifteen actually buy?

Most of these groups pair a common sign with a rare one, so U2 can only run on
a few of them. That limit is stated rather than hidden.
"""
import json
from collections import Counter, defaultdict

from scipy import stats

GROUPS = [
    [154, 156], [544, 563], [850, 856], [775, 776], [595, 597],
    [541, 561], [511, 514], [411, 413], [350, 351], [307, 308],
    [229, 242], [160, 161], [31, 600], [275, 276, 278], [61, 62, 63],
]
MINTEST = 8          # both members need this many tokens for U2

lines = json.loads(open("data/parsed/lines.json").read())
ins = {}
for i in json.loads(open("data/parsed/inscriptions.json").read()):
    ins[i["cisi"] or f"#{i['seal_id']}"] = i

recs, seen = [], set()
for l in lines:
    t = tuple(g for g in l["signs"] if g)
    if not t:
        continue
    k = (t, l.get("site"))
    if k in seen:
        continue
    seen.add(k)
    recs.append((t, l.get("site"),
                 (ins.get(l.get("artifact")) or {}).get("obj_class")))
texts = [r[0] for r in recs]
freq = Counter(g for t in texts for g in t)

# ------------------------------------------------------------------ U1
print("=== U1: what does Parpola's numbering say? ===")
cw = json.load(open("data/parsed/crosswalk.json"))
Y2P = {int(k): v for k, v in cw["y2p"].items()}
agree = conflict = silent = 0
for g in GROUPS:
    ps = {i: Y2P.get(i) for i in g}
    known = {i: p for i, p in ps.items() if p}
    if len(known) < 2:
        silent += 1
        note = "no opinion (crosswalk covers <2 members)"
    elif len(set(known.values())) == 1:
        agree += 1
        note = f"AGREES -- all are {list(known.values())[0]}"
    else:
        conflict += 1
        note = f"CONFLICTS -- {known}"
    print(f"  {str(g):<20} {note}")
print(f"\n  agrees {agree}   conflicts {conflict}   no opinion {silent}")

# the crosswalk's own view of 600
print(f"\n  note: the crosswalk maps 600 -> {Y2P.get(600)} and "
      f"32 -> {Y2P.get(32)}, i.e. it pairs 600 with 32, not 31.")
print("  Rendered at 115px, 600 and 31 are both a single plain vertical")
print("  stroke and 32 is two. On the glyphs, the chart is right and the")
print("  crosswalk is wrong. Only 3 tokens ride on it either way.")

# ------------------------------------------------------------------ U2
print("\n=== U2: do the testable pairs behave alike? ===")
pos = defaultdict(list)
nxt = defaultdict(Counter)
prv = defaultdict(Counter)
site = defaultdict(Counter)
obj = defaultdict(Counter)
for t, s, o in recs:
    for i, g in enumerate(t):
        if len(t) > 1:
            pos[g].append(i / (len(t) - 1))
        if i + 1 < len(t):
            nxt[g][t[i + 1]] += 1
        if i:
            prv[g][t[i - 1]] += 1
        site[g][s] += 1
        obj[g][o] += 1


def cos(a, b):
    k = set(a) | set(b)
    d = (sum(v * v for v in a.values()) ** .5) * (sum(v * v for v in b.values()) ** .5)
    return sum(a[x] * b[x] for x in k) / d if d else 0.0


# baseline: how similar are two *different* common signs, on average?
common = [g for g, n in freq.items() if n >= 25]
base = []
for i in range(len(common)):
    for j in range(i + 1, len(common)):
        base.append(cos(nxt[common[i]], nxt[common[j]]))
base.sort()
med = base[len(base) // 2]
p90 = base[int(len(base) * .90)]
print(f"  baseline: two unrelated common signs share a next-sign profile at")
print(f"  cosine {med:.3f} (median), {p90:.3f} (90th pct). A real merge should")
print(f"  beat the 90th percentile.\n")

tested = 0
for g in GROUPS:
    mem = [i for i in g if freq[i] >= MINTEST]
    if len(mem) < 2:
        continue
    tested += 1
    a, b = mem[0], mem[1]
    u = stats.mannwhitneyu(pos[a], pos[b])
    cn, cp = cos(nxt[a], nxt[b]), cos(prv[a], prv[b])
    st = cos(site[a], site[b])
    ob = cos(obj[a], obj[b])
    verdict = "consistent" if (u.pvalue > .05 and max(cn, cp) > p90) else "mixed"
    print(f"  {a} (n={freq[a]}) vs {b} (n={freq[b]})")
    print(f"    position   mean {sum(pos[a])/len(pos[a]):.3f} vs "
          f"{sum(pos[b])/len(pos[b]):.3f}   p = {u.pvalue:.3f}")
    print(f"    next sign  cosine {cn:.3f}      prev sign cosine {cp:.3f}")
    print(f"    site {st:.3f}   object {ob:.3f}      -> {verdict}")
print(f"\n  testable groups: {tested} of {len(GROUPS)} "
      f"(both members need >={MINTEST} tokens)")

# ------------------------------------------------------------------ U3
print("\n=== U3: what does accepting all fifteen buy? ===")
M = {}
for g in GROUPS:
    base_id = max(g, key=lambda i: freq[i])
    for i in g:
        M[i] = base_id
after = Counter()
for g, n in freq.items():
    after[M.get(g, g)] += n


def stat(c, label):
    n = len(c)
    hap = sum(1 for v in c.values() if v == 1)
    print(f"  {label:<22} signs {n:>4}   hapax {hap:>4} ({hap/n:.0%})   "
          f"n>=20 {sum(1 for v in c.values() if v >= 20):>3}   "
          f"median {sorted(c.values())[n//2]}")


stat(freq, "as-is")
stat(after, "+ these 15 merges")
moved = [(M[i], after[M[i]]) for g in GROUPS for i in g
         if M[i] == i and freq[i] < 20 <= after[i]]
print(f"\n  signs newly crossing the n>=20 testable line: "
      f"{sorted(set(moved)) if moved else 'none'}")
print(f"  tokens involved in the 15 groups: "
      f"{sum(freq[i] for g in GROUPS for i in g)} of {sum(freq.values())}")

json.dump({"groups": GROUPS, "map": {str(k): v for k, v in M.items()}},
          open("data/parsed/usermerges.json", "w"), indent=1)
print("\nwrote data/parsed/usermerges.json")
