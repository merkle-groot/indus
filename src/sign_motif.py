"""Do particular signs associate with particular motifs?

The obvious trap: motif is entangled with object type and site. The unicorn is
overwhelmingly a *seal* motif and seals are overwhelmingly *Mohenjo-daro*, so a
naive sign-vs-motif test will happily rediscover sign-vs-site and call it
iconography.

So we run three passes of increasing strictness:
  1. naive        -- sign presence vs motif, no controls (the wrong answer)
  2. stratified   -- Cochran-Mantel-Haenszel, conditioning on site x object class
  3. permutation  -- shuffle motif labels *within* those same strata and re-run
                     pass 2, to see how many "discoveries" the method invents
                     when the association is known to be absent.

Pass 3 is the one that decides whether pass 2 means anything.
"""
import json
from collections import Counter, defaultdict

import numpy as np
from scipy import stats

RNG = np.random.default_rng(0)
MIN_SIGN = 12      # sign must appear on at least this many artifacts
MIN_MOTIF = 15     # motif must have at least this many artifacts
N_PERM = 400
DEDUP = "--nodedup" not in __import__("sys").argv

seals = json.loads(open("data/parsed/inscriptions.json").read())
sites = json.loads(open("data/parsed/sites.json").read())

# ---------------------------------------------------------------- build table
DROP = {None, "unrecorded", "unknown", "none", "Unknown"}
arts = []
for s in seals:
    m = s.get("motif")
    if m in DROP:
        continue
    sg = {g for g in s["glyphs"] if g != 0}
    if not sg:
        continue
    arts.append({
        "signs": sg, "motif": m, "text": tuple(g for g in s["glyphs"] if g != 0),
        "stratum": (sites.get(s.get("site"), "?"), s.get("obj_class")),
    })

# Duplicate texts are not independent observations. One 11-sign text occurs 11
# times, every copy on a rhinoceros; another occurs 10 times, all elephant.
# Left in, they inflate exactly the associations we are testing for. Collapse
# each distinct (text, motif) pair to a single artifact.
if DEDUP:
    seen, uniq = set(), []
    for a in arts:
        key = (a["text"], a["motif"])
        if key not in seen:
            seen.add(key)
            uniq.append(a)
    print(f"dedup: {len(arts)} artifacts -> {len(uniq)} distinct (text, motif) pairs")
    arts = uniq

motif_n = Counter(a["motif"] for a in arts)
keep_motif = {m for m, c in motif_n.items() if c >= MIN_MOTIF}
arts = [a for a in arts if a["motif"] in keep_motif]

sign_n = Counter(g for a in arts for g in a["signs"])
keep_sign = sorted(g for g, c in sign_n.items() if c >= MIN_SIGN)

print(f"artifacts with a usable motif : {len(arts)}")
print(f"motifs tested (n>={MIN_MOTIF})        : {len(keep_motif)}  "
      + ", ".join(f"{m}({motif_n[m]})" for m, _ in motif_n.most_common() if m in keep_motif))
print(f"signs tested (on >={MIN_SIGN} artifacts): {len(keep_sign)}")
print(f"tests = {len(keep_sign)} signs x {len(keep_motif)} motifs "
      f"= {len(keep_sign) * len(keep_motif)}")

strata = sorted({a["stratum"] for a in arts})
str_ix = {s: i for i, s in enumerate(strata)}
print(f"strata (site x object class)  : {len(strata)}")

X = np.zeros((len(arts), len(keep_sign)), bool)     # artifact x sign presence
sign_ix = {g: i for i, g in enumerate(keep_sign)}
for i, a in enumerate(arts):
    for g in a["signs"]:
        if g in sign_ix:
            X[i, sign_ix[g]] = True
motif_of = np.array([a["motif"] for a in arts])
stratum_of = np.array([str_ix[a["stratum"]] for a in arts])


# ------------------------------------------------------------------ machinery
def bh(p):
    """Benjamini-Hochberg q-values."""
    p = np.asarray(p, float)
    o = np.argsort(p)
    q = np.empty_like(p)
    m = len(p)
    prev = 1.0
    for rank, i in enumerate(o[::-1]):
        prev = min(prev, p[i] * m / (m - rank))
        q[i] = prev
    return q


def cmh(present, is_motif, stratum, nstrat):
    """Cochran-Mantel-Haenszel 2x2xK: sign presence vs motif membership,
    conditioned on stratum. Returns (chi2, p, mh_odds_ratio)."""
    num = den = 0.0
    rnum = rden = 0.0
    for k in range(nstrat):
        m = stratum == k
        if not m.any():
            continue
        a = np.count_nonzero(present[m] & is_motif[m])
        b = np.count_nonzero(present[m] & ~is_motif[m])
        c = np.count_nonzero(~present[m] & is_motif[m])
        d = np.count_nonzero(~present[m] & ~is_motif[m])
        n = a + b + c + d
        if n < 2:
            continue
        r1, r2, c1, c2 = a + b, c + d, a + c, b + d
        if min(r1, r2, c1, c2) == 0:
            continue
        num += a - r1 * c1 / n
        den += r1 * r2 * c1 * c2 / (n * n * (n - 1))
        rnum += a * d / n
        rden += b * c / n
    if den <= 0:
        return 0.0, 1.0, np.nan
    chi2 = (abs(num) - 0.5) ** 2 / den if abs(num) > 0.5 else 0.0
    p = stats.chi2.sf(chi2, 1)
    or_ = rnum / rden if rden > 0 else np.inf
    return chi2, p, or_


def run(motifs, strat):
    """All sign x motif CMH tests. Returns list of dicts."""
    out = []
    for m in sorted(keep_motif):
        ism = motifs == m
        for g in keep_sign:
            j = sign_ix[g]
            chi2, p, or_ = cmh(X[:, j], ism, strat, len(strata))
            out.append({"sign": g, "motif": m, "p": p, "or": or_,
                        "n_with": int(np.count_nonzero(X[:, j] & ism)),
                        "n_motif": int(ism.sum()), "n_sign": int(X[:, j].sum())})
    return out


# --------------------------------------------------------------- 1. the naive pass
print("\n" + "=" * 72)
print("PASS 1  naive chi-square, sign presence x motif, NO controls")
print("=" * 72)
naive_p = []
for m in sorted(keep_motif):
    ism = motif_of == m
    for g in keep_sign:
        j = sign_ix[g]
        tab = [[np.count_nonzero(X[:, j] & ism), np.count_nonzero(X[:, j] & ~ism)],
               [np.count_nonzero(~X[:, j] & ism), np.count_nonzero(~X[:, j] & ~ism)]]
        naive_p.append(stats.chi2_contingency(tab, correction=True)[1]
                       if min(map(min, tab)) >= 0 and np.all(np.array(tab).sum(0) > 0)
                       else 1.0)
nq = bh(naive_p)
print(f"  raw p < .05     : {np.count_nonzero(np.array(naive_p) < .05)} / {len(naive_p)}")
print(f"  BH q < .05      : {np.count_nonzero(nq < .05)}")
print("  ^ do not believe these; site and object type are uncontrolled")

# ------------------------------------------------- 2. the stratified pass
print("\n" + "=" * 72)
print("PASS 2  CMH, conditioned on site x object class")
print("=" * 72)
res = run(motif_of, stratum_of)
q = bh([r["p"] for r in res])
for r, qq in zip(res, q):
    r["q"] = qq
hits = sorted([r for r in res if r["q"] < .05], key=lambda r: r["p"])
print(f"  raw p < .05     : {sum(r['p'] < .05 for r in res)} / {len(res)}")
print(f"  BH q < .05      : {len(hits)}")

# ------------------------------------------------- 3. the permutation control
print("\n" + "=" * 72)
print(f"PASS 3  permutation control: motif shuffled WITHIN strata, {N_PERM} runs")
print("=" * 72)
null_hits, null_raw = [], []
by_strat = [np.flatnonzero(stratum_of == k) for k in range(len(strata))]
for _ in range(N_PERM):
    perm = motif_of.copy()
    for idx in by_strat:
        if len(idx) > 1:
            perm[idx] = RNG.permutation(perm[idx])
    pr = run(perm, stratum_of)
    qr = bh([r["p"] for r in pr])
    null_hits.append(int(np.count_nonzero(qr < .05)))
    null_raw.append(int(np.count_nonzero(np.array([r["p"] for r in pr]) < .05)))
null_hits, null_raw = np.array(null_hits), np.array(null_raw)
print(f"  raw p<.05 under null      : mean {null_raw.mean():.1f} of {len(res)} "
      f"({null_raw.mean()/len(res):.1%}) -- nominal would be 5.0%")
print(f"  discoveries under the null: mean {null_hits.mean():.2f}, "
      f"median {np.median(null_hits):.0f}, 95th pct {np.percentile(null_hits, 95):.0f}, "
      f"max {null_hits.max()}")
emp_p = (np.count_nonzero(null_hits >= len(hits)) + 1) / (N_PERM + 1)
print(f"  observed: {len(hits)} discoveries -> empirical p = {emp_p:.4f}")

# ------------------------------------------------------------------- report
print("\n" + "=" * 72)
print("SURVIVING SIGN x MOTIF ASSOCIATIONS (q < .05, site+object controlled)")
print("=" * 72)
if not hits:
    print("  none survive BH q<.05\n")
    print("  strongest raw signals anyway (NOT significant after correction):")
    print(f"  {'sign':>6} {'motif':<28} {'OR':>7} {'k/n':>10} {'p':>9} {'q':>7}")
    for r in sorted(res, key=lambda r: r["p"])[:12]:
        print(f"  {r['sign']:>6} {r['motif']:<28} {r['or']:>7.2f} "
              f"{r['n_with']:>4}/{r['n_motif']:<5} {r['p']:>9.2g} {r['q']:>7.2f}")
else:
    print(f"  {'sign':>6} {'motif':<28} {'OR':>7} {'k/n':>10} {'q':>9}")
    for r in hits[:40]:
        print(f"  {r['sign']:>6} {r['motif']:<28} {r['or']:>7.2f} "
              f"{r['n_with']:>4}/{r['n_motif']:<5} {r['q']:>9.2g}")

json.dump({"hits": hits, "null_mean": float(null_hits.mean()),
           "null_p95": float(np.percentile(null_hits, 95)),
           "observed": len(hits), "empirical_p": float(emp_p)},
          open("data/parsed/sign_motif.json", "w"), indent=1)
