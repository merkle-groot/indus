"""Do seals and tablets use different templates?

Seals identify somebody; tablets are mass-produced tokens. If these texts are
records, the two media should be filling out different forms -- and object class
has only ever been used in this project as a nuisance variable to control for.

The confound is severe and has to lead the analysis:

    seals   : Mohenjo-daro 934, Harappa 256
    tablets : Harappa      673, Mohenjo-daro 212

Object class and city are almost the same variable. Anything measured on the raw
split is measuring geography. Every test below is therefore run **within each
city separately** and only then combined, and both cities carry enough of both
media to make that possible.

  O1 length     -- do the two media write texts of different lengths?
  O2 vocabulary -- do they draw on different signs?
  O3 terminal   -- 12-slots.md found a terminal slot with competing fillers.
                   Same slot, different filler = same form, different values.
                   This is the sharpest version of the question.
  O4 numerals   -- tokens should count; identity seals should not
  O5 skew       -- which individual signs pick a medium, controlling for city
"""
import json
from collections import Counter, defaultdict

from scipy import stats

CITY = {"SI1": "Mohenjo-daro", "SI2": "Harappa"}
MEDIA = ("seal", "tablet")
NUM = set(range(1, 8)) | {31, 32, 33, 34, 35} | set(range(12, 20))

lines = json.loads(open("data/parsed/lines.json").read())
ins = {}
for i in json.loads(open("data/parsed/inscriptions.json").read()):
    ins[i["cisi"] or f"#{i['seal_id']}"] = i

recs, seen = [], set()
for l in lines:
    t = tuple(g for g in l["signs"] if g)
    if not t:
        continue
    a = ins.get(l.get("artifact")) or {}
    oc, site = a.get("obj_class"), l.get("site")
    if oc not in MEDIA or site not in CITY:
        continue
    k = (t, site, oc)
    if k in seen:
        continue
    seen.add(k)
    recs.append((t, site, oc))

print("distinct texts on seals/tablets at the two big cities:")
c = Counter((s, o) for _, s, o in recs)
for site in CITY:
    print(f"  {CITY[site]:<14} " +
          "  ".join(f"{m} {c[(site,m)]}" for m in MEDIA))


def split(site):
    return {m: [t for t, s, o in recs if s == site and o == m] for m in MEDIA}


# ------------------------------------------------------------------ O1
print("\n=== O1: text length ===")
for site in CITY:
    d = split(site)
    a, b = [len(t) for t in d["seal"]], [len(t) for t in d["tablet"]]
    u = stats.mannwhitneyu(a, b)
    print(f"  {CITY[site]:<14} seal mean {sum(a)/len(a):.2f} (n={len(a)})   "
          f"tablet mean {sum(b)/len(b):.2f} (n={len(b)})   p = {u.pvalue:.1e}")

# ------------------------------------------------------------------ O2
print("\n=== O2: vocabulary ===")
for site in CITY:
    d = split(site)
    cs = {m: Counter(g for t in d[m] for g in t) for m in MEDIA}
    vs = {m: set(cs[m]) for m in MEDIA}
    sh = vs["seal"] & vs["tablet"]
    tot = {m: sum(cs[m].values()) for m in MEDIA}
    shared_tok = {m: sum(cs[m][g] for g in sh) / tot[m] for m in MEDIA}
    print(f"  {CITY[site]}")
    print(f"    distinct signs: seal {len(vs['seal'])}, tablet {len(vs['tablet'])}, "
          f"shared {len(sh)}")
    print(f"    share of tokens using a shared sign: "
          f"seal {shared_tok['seal']:.1%}, tablet {shared_tok['tablet']:.1%}")

# ------------------------------------------------------------------ O3
print("\n=== O3: what fills the terminal slot? ===")
TERM = [740, 520, 390, 151, 527, 617, 156, 400, 90]
for site in CITY:
    d = split(site)
    print(f"  {CITY[site]}")
    tab = []
    for m in MEDIA:
        last = Counter(t[-1] for t in d[m] if t)
        n = sum(last.values())
        tab.append([last[g] for g in TERM])
        top = ", ".join(f"{g}:{last[g]} ({last[g]/n:.0%})"
                        for g in sorted(TERM, key=lambda g: -last[g])[:4])
        print(f"    {m:<7} n={n:<4} {top}")
    keep = [i for i in range(len(TERM)) if tab[0][i] + tab[1][i] >= 5]
    t2 = [[tab[r][i] for i in keep] for r in (0, 1)]
    if len(keep) > 1:
        print(f"    same filler distribution? chi2 p = "
              f"{stats.chi2_contingency(t2)[1]:.2e}")

# ------------------------------------------------------------------ O4
print("\n=== O4: numerals ===")
for site in CITY:
    d = split(site)
    row = {}
    for m in MEDIA:
        n = sum(1 for t in d[m] if any(g in NUM for g in t))
        row[m] = (n, len(d[m]))
        print(f"  {CITY[site]:<14} {m:<7} {n}/{len(d[m])} texts carry a numeral "
              f"({n/len(d[m]):.1%})")
    a, b = row["seal"], row["tablet"]
    print(f"    p = {stats.fisher_exact([[a[0], a[1]-a[0]], [b[0], b[1]-b[0]]])[1]:.2e}")

# ------------------------------------------------------------------ O5
print("\n=== O5: which signs pick a medium? (Mantel-Haenszel over the two cities) ===")
docs = defaultdict(lambda: defaultdict(lambda: [0, 0]))
tot = defaultdict(lambda: [0, 0])
for t, s, o in recs:
    j = MEDIA.index(o)
    tot[s][j] += 1
    for g in set(t):
        docs[g][s][j] += 1

rows = []
for g, by in docs.items():
    n = sum(sum(v) for v in by.values())
    if n < 25:
        continue
    num = den = 0.0
    for s, (a, b) in by.items():
        N = tot[s][0] + tot[s][1]
        r1, c1 = a + b, tot[s][0]
        num += a - r1 * c1 / N
        den += r1 * (N - r1) * c1 * (N - c1) / (N * N * (N - 1))
    if den <= 0:
        continue
    z = num / den ** .5
    rows.append((z, g, n, sum(v[0] for v in by.values()),
                 sum(v[1] for v in by.values())))
rows.sort()
print(f"  signs testable: {len(rows)}")
print(f"  significantly medium-specific (|z|>3): "
      f"{sum(1 for r in rows if abs(r[0]) > 3)}")
print("\n  most tablet-loaded            most seal-loaded")
for i in range(10):
    l, r = rows[i], rows[-1 - i]
    print(f"    {l[1]:>4} z {l[0]:+.1f} ({l[3]}s/{l[4]}t)      "
          f"{r[1]:>4} z {r[0]:+.1f} ({r[3]}s/{r[4]}t)")
