"""Recover the form's fields from the no-repeat rule.

09-music.md found that Indus texts avoid reusing a sign far below chance, and
suggested they behave like a form with slots, each filled once. If that is true
the corpus should show the other half of the pattern: signs that COMPETE for the
same slot can never appear together either, because the slot holds one value.
"Monday" and "Tuesday" never share a date field.

So: find every pair of signs that co-occurs below chance, and see whether those
pairs knit into a few groups. A group of pairwise mutually exclusive signs is a
candidate slot, recovered from the data rather than assumed.

Three things this must not be fooled by:

  * Text length. Everything under-co-occurs when texts average 4 signs, and a
    2-sign text cannot hold a pair at all. Every test is stratified by length.
  * Geography and medium. A Harappa sign and a Mohenjo-daro sign never co-occur
    because they sit in different corpora, not because they compete. Re-tested
    stratified by site and by object class.
  * Mass production. Identical tablets stamped 40 times would manufacture any
    pattern. Texts are deduplicated first.

Two built-in validation targets. If the method works it should recover:
  * the stroke numerals, which must compete for one count slot
  * 817 and 861, shown complementary in 05-radix.md by a different route
"""
import json
from collections import Counter, defaultdict

from scipy import stats

MINN = 20          # a sign needs this many texts to be testable
FDR = 0.05

lines = json.loads(open("data/parsed/lines.json").read())
ins = {}
for i in json.loads(open("data/parsed/inscriptions.json").read()):
    ins[i["cisi"] or f"#{i['seal_id']}"] = i

recs, seen = [], set()
for l in lines:
    s = frozenset(g for g in l["signs"] if g)
    if len(s) < 2:
        continue
    key = (s, l.get("site"))
    if key in seen:
        continue
    seen.add(key)
    recs.append((s, l.get("site"),
                 (ins.get(l.get("artifact")) or {}).get("obj_class"), len(s)))

sets = [r[0] for r in recs]
print(f"distinct multi-sign texts : {len(sets)}")
df = Counter(g for s in sets for g in s)
V = sorted(g for g, n in df.items() if n >= MINN)
print(f"signs in >= {MINN} texts   : {len(V)}")

STRATA = {"length": 3, "site": 1, "object": 2}


def mh(g1, g2, keyi):
    """Mantel-Haenszel z for co-occurrence of g1,g2 across strata.

    Negative z means they co-occur BELOW chance given each stratum's marginals.
    Returns (z, observed, expected).
    """
    by = defaultdict(list)
    for r in recs:
        by[r[keyi]].append(r[0])
    num = den = 0.0
    o = e = 0.0
    for _, ss in by.items():
        n = len(ss)
        if n < 10:
            continue
        r1 = sum(1 for s in ss if g1 in s)
        r2 = sum(1 for s in ss if g2 in s)
        if r1 == 0 or r2 == 0 or r1 == n or r2 == n:
            continue
        a = sum(1 for s in ss if g1 in s and g2 in s)
        num += a - r1 * r2 / n
        den += r1 * r2 * (n - r1) * (n - r2) / (n * n * (n - 1))
        o += a
        e += r1 * r2 / n
    return (num / den ** .5 if den > 0 else 0.0), o, e


print("\ntesting every pair, stratified by text length...")
cand = []
for i in range(len(V)):
    for j in range(i + 1, len(V)):
        z, o, e = mh(V[i], V[j], STRATA["length"])
        if e < 3:                        # no power to detect avoidance
            continue
        cand.append((stats.norm.cdf(z), V[i], V[j], o, e, z))
cand.sort()
m = len(cand)
sig = []
for k, c in enumerate(cand, 1):
    if c[0] <= FDR * k / m:
        sig = cand[:k]
print(f"  testable pairs {m}   below chance at FDR {FDR}: {len(sig)}")

print("\nre-testing survivors stratified by site and by object class")
rows = []
for p, g1, g2, o, e, z in sig:
    zs = mh(g1, g2, STRATA["site"])[0]
    zo = mh(g1, g2, STRATA["object"])[0]
    rows.append([g1, g2, o, e, z, zs, zo, zs < -1.96 and zo < -1.96])
surv = [r for r in rows if r[7]]
print(f"  survive both controls: {len(surv)} of {len(rows)}")
print("\n  sign1  sign2   obs    exp      z   z|site  z|object  survives")
for g1, g2, o, e, z, zs, zo, ok in rows[:40]:
    print(f"  {g1:>5} {g2:>6} {o:>5} {e:>7.1f} {z:>6.2f} {zs:>7.2f} {zo:>8.2f}"
          f"   {'yes' if ok else 'no'}")

print("\n=== do the exclusive pairs knit into groups? ===")
adj = defaultdict(set)
for g1, g2, *_r, ok in rows:
    if ok:
        adj[g1].add(g2)
        adj[g2].add(g1)
cliques = []


def bk(R, P, X):
    if not P and not X:
        if len(R) >= 3:
            cliques.append(sorted(R))
        return
    piv = max(P | X, key=lambda v: len(adj[v]))
    for v in list(P - adj[piv]):
        bk(R | {v}, P & adj[v], X & adj[v])
        P = P - {v}
        X = X | {v}


if adj:
    bk(set(), set(adj), set())
cliques.sort(key=len, reverse=True)
print(f"  signs in a surviving exclusion : {len(adj)}")
print(f"  mutually-exclusive groups of 3+: {len(cliques)}")

seqs = [[g for g in l["signs"] if g] for l in lines]
mp = defaultdict(list)
for t in seqs:
    if len(t) > 1:
        for i, g in enumerate(t):
            mp[g].append(i / (len(t) - 1))
for c in cliques[:15]:
    ps = [sum(mp[g]) / len(mp[g]) for g in c]
    print(f"    {c}  pos {[f'{x:.2f}' for x in ps]}  spread {max(ps)-min(ps):.2f}")

print("\n=== validation anchors ===")
NUM = set(range(1, 8)) | {31, 32, 33, 34, 35} | set(range(12, 20))
nums = [g for g in V if g in NUM]
print(f"  testable numeral signs: {nums}")
for i in range(len(nums)):
    for j in range(i + 1, len(nums)):
        z, o, e = mh(nums[i], nums[j], STRATA["length"])
        if e >= 3:
            print(f"    {nums[i]:>3} vs {nums[j]:<3} obs {o:>3.0f} exp {e:>5.1f} "
                  f"z {z:+.2f}")
for a, b in [(817, 861), (817, 820), (861, 820)]:
    z, o, e = mh(a, b, STRATA["length"])
    print(f"  {a} vs {b}: obs {o:.0f} exp {e:.1f} z {z:+.2f}")

json.dump({"cliques": cliques,
           "pairs": [{"a": r[0], "b": r[1], "obs": r[2], "exp": r[3], "z": r[4],
                      "z_site": r[5], "z_obj": r[6], "survives": r[7]}
                     for r in rows]},
          open("data/parsed/slots.json", "w"), indent=1)
print("\nwrote data/parsed/slots.json")
