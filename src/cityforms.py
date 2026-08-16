"""Does the form differ by city?

14-object-forms.md found seals and tablets filling the terminal slot with
different signs, but left one question open: Harappa supplies 387 of the 470
tablets, so "tablet convention" and "Harappa convention" were only partly
separated. This is the mirror analysis -- city as the variable, medium as the
control -- and it settles that question directly.

Regional variation inside a shared template is what local administrative
practice looks like, so a positive result here strengthens the record reading.
A null result would say the form is uniform across the civilisation.

  C1 disentangle -- is ending in 400 a tablet habit or a Harappa habit?
                    Four cells: {MD, Harappa} x {seal, tablet}. If it tracks
                    medium, MD tablets do it too. If it tracks city, Harappa
                    seals do it.
  C2 length      -- within medium
  C3 terminal    -- terminal filler by city, within medium
  C4 numerals    -- by city, within medium
  C5 skew        -- which signs pick a city, controlling for medium
  C6 small sites -- do the minor towns follow one capital or the other?
"""
import json
from collections import Counter, defaultdict

from scipy import stats

SITE = json.loads(open("data/parsed/sites.json").read())
MD, HA = "SI1", "SI2"
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
    k = (t, l.get("site"), a.get("obj_class"))
    if k in seen:
        continue
    seen.add(k)
    recs.append((t, l.get("site"), a.get("obj_class")))


def cell(site, med):
    return [t for t, s, o in recs if s == site and o == med]


# ------------------------------------------------------------------ C1
print("=== C1: is ending in 400 a tablet habit or a Harappa habit? ===")
print("        n     ends in 400    ends in 740")
grid = {}
for site in (MD, HA):
    for med in MEDIA:
        d = cell(site, med)
        e4 = sum(1 for t in d if t[-1] == 400)
        e7 = sum(1 for t in d if t[-1] == 740)
        grid[(site, med)] = (e4, len(d))
        print(f"  {SITE[site][:12]:<13}{med:<7} {len(d):>4}  "
              f"{e4:>4} ({e4/max(len(d),1):>4.0%})   {e7:>4} ({e7/max(len(d),1):>4.0%})")

a, b = grid[(MD, "tablet")], grid[(HA, "tablet")]
print(f"\n  tablets, MD vs Harappa : {a[0]}/{a[1]} vs {b[0]}/{b[1]}   "
      f"p = {stats.fisher_exact([[a[0],a[1]-a[0]],[b[0],b[1]-b[0]]])[1]:.2e}")
a, b = grid[(MD, "seal")], grid[(HA, "seal")]
print(f"  seals,   MD vs Harappa : {a[0]}/{a[1]} vs {b[0]}/{b[1]}   "
      f"p = {stats.fisher_exact([[a[0],a[1]-a[0]],[b[0],b[1]-b[0]]])[1]:.2e}")
a, b = grid[(HA, "seal")], grid[(HA, "tablet")]
print(f"  Harappa, seal vs tablet: {a[0]}/{a[1]} vs {b[0]}/{b[1]}   "
      f"p = {stats.fisher_exact([[a[0],a[1]-a[0]],[b[0],b[1]-b[0]]])[1]:.2e}")

# ------------------------------------------------------------------ C2
print("\n=== C2: text length, within medium ===")
for med in MEDIA:
    x, y = [len(t) for t in cell(MD, med)], [len(t) for t in cell(HA, med)]
    print(f"  {med:<7} MD {sum(x)/len(x):.2f} (n={len(x)})   "
          f"Harappa {sum(y)/len(y):.2f} (n={len(y)})   "
          f"p = {stats.mannwhitneyu(x, y).pvalue:.1e}")

# ------------------------------------------------------------------ C3
print("\n=== C3: terminal filler by city, within medium ===")
TERM = [740, 400, 520, 390, 90, 151, 527, 617, 156]
for med in MEDIA:
    print(f"  {med}")
    tab = []
    for site in (MD, HA):
        d = cell(site, med)
        last = Counter(t[-1] for t in d)
        tab.append([last[g] for g in TERM])
        n = len(d)
        top = ", ".join(f"{g}:{last[g]/n:.0%}"
                        for g in sorted(TERM, key=lambda g: -last[g])[:4])
        print(f"    {SITE[site][:12]:<13} n={n:<4} {top}")
    keep = [i for i in range(len(TERM)) if tab[0][i] + tab[1][i] >= 5]
    if len(keep) > 1:
        t2 = [[tab[r][i] for i in keep] for r in (0, 1)]
        print(f"    same distribution? chi2 p = {stats.chi2_contingency(t2)[1]:.2e}")

# ------------------------------------------------------------------ C4
print("\n=== C4: numerals by city, within medium ===")
for med in MEDIA:
    row = []
    for site in (MD, HA):
        d = cell(site, med)
        n = sum(1 for t in d if any(g in NUM for g in t))
        row.append((n, len(d)))
        print(f"  {med:<7} {SITE[site][:12]:<13} {n}/{len(d)} ({n/max(len(d),1):.1%})")
    a, b = row
    print(f"    p = {stats.fisher_exact([[a[0],a[1]-a[0]],[b[0],b[1]-b[0]]])[1]:.2e}")

# ------------------------------------------------------------------ C5
print("\n=== C5: which signs pick a city? (MH stratified by medium) ===")
docs = defaultdict(lambda: defaultdict(lambda: [0, 0]))
tot = defaultdict(lambda: [0, 0])
for t, s, o in recs:
    if s not in (MD, HA) or o not in MEDIA:
        continue
    j = 0 if s == MD else 1
    tot[o][j] += 1
    for g in set(t):
        docs[g][o][j] += 1
rows = []
for g, by in docs.items():
    n = sum(sum(v) for v in by.values())
    if n < 25:
        continue
    num = den = 0.0
    for o, (x, y) in by.items():
        N = tot[o][0] + tot[o][1]
        r1, c1 = x + y, tot[o][0]
        if N < 10:
            continue
        num += x - r1 * c1 / N
        den += r1 * (N - r1) * c1 * (N - c1) / (N * N * (N - 1))
    if den <= 0:
        continue
    rows.append((num / den ** .5, g, sum(v[0] for v in by.values()),
                 sum(v[1] for v in by.values())))
rows.sort()
print(f"  testable {len(rows)}   city-specific at |z|>3: "
      f"{sum(1 for r in rows if abs(r[0]) > 3)}")
print("\n  most Harappa                  most Mohenjo-daro")
for i in range(10):
    l, r = rows[i], rows[-1 - i]
    print(f"    {l[1]:>4} z {l[0]:+.1f} ({l[2]}md/{l[3]}h)     "
          f"{r[1]:>4} z {r[0]:+.1f} ({r[2]}md/{r[3]}h)")

# ------------------------------------------------------------------ C6
print("\n=== C6: do the smaller towns follow a capital? ===")
small = [s for s, n in Counter(r[1] for r in recs).items()
         if 25 <= n < 400 and s not in (MD, HA)]
ref = {}
for site in (MD, HA):
    d = [t for t, s, o in recs if s == site]
    c = Counter(g for t in d for g in t)
    tot_ = sum(c.values())
    ref[site] = {g: v / tot_ for g, v in c.items()}


def cosine(p, q):
    keys = set(p) | set(q)
    num = sum(p.get(k, 0) * q.get(k, 0) for k in keys)
    return num / ((sum(v * v for v in p.values()) ** .5) *
                  (sum(v * v for v in q.values()) ** .5))


print("  site            n   ends-740  ends-400   sim(MD)  sim(Harappa)  leans")
for s in sorted(small, key=lambda s: -sum(1 for r in recs if r[1] == s)):
    d = [t for t, ss, o in recs if ss == s]
    c = Counter(g for t in d for g in t)
    tot_ = sum(c.values())
    p = {g: v / tot_ for g, v in c.items()}
    sm, sh = cosine(p, ref[MD]), cosine(p, ref[HA])
    e7 = sum(1 for t in d if t[-1] == 740) / len(d)
    e4 = sum(1 for t in d if t[-1] == 400) / len(d)
    print(f"  {SITE.get(s,s)[:14]:<15} {len(d):>3}  {e7:>7.0%}  {e4:>7.0%}   "
          f"{sm:>7.3f}  {sh:>11.3f}   "
          f"{'Mohenjo-daro' if sm > sh else 'Harappa'}")
