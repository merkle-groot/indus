"""Recover right-edge structure by indexing every text from its end.

For each sign occurring in at least 20 deduplicated multi-sign texts, build a
sign x right-position occupancy matrix.  The null uniformly shuffles the tokens
inside each text.  Its expectation and variance are computed exactly: for a
text of length L containing c copies of a sign, any specified slot contains the
sign with probability c/L.  This preserves text membership, length, site,
object, and the corpus's no-repeat pattern; only position is removed.

Signs enriched at -1, -2, or -3 by z >= 3 form a position cohort.  Within each
cohort, the pairwise mutual-exclusion scan from slots.py is repeated: first
stratified by length with BH correction, then checked by site and object class.

Finally, the one-sign-longer comparison from growth.py is repeated on the
merged corpus, now asking whether both final signs survive.  A simulated corpus
draws every L x left-slot from its observed distribution, so the null preserves
the positional preferences that make final-sign agreement common for free.
"""
import json
import math
import random
from collections import Counter, defaultdict

import numpy as np
from scipy import stats

MIN_N = 20
LOCAL_Z = 3.0
FDR = .05
MAX_RIGHT = 6
N_GROWTH_SIM = 2000
RNG = random.Random(26)

lines = json.load(open("data/parsed/lines_merged.json"))
inscriptions = json.load(open("data/parsed/inscriptions.json"))
by_artifact = {i["cisi"] or f"#{i['seal_id']}": i for i in inscriptions}

raw = []
for line in lines:
    text = tuple(g for g in line["signs"] if g)
    if len(text) < 2:
        continue
    raw.append({"text": text, "site": line.get("site"),
                "object": by_artifact.get(line.get("artifact"), {}).get("obj_class")})


def dedup(rows, key):
    out, seen = [], set()
    for row in rows:
        k = key(row)
        if k in seen:
            continue
        seen.add(k)
        out.append(row)
    return out


# This matches growth.py and most of the earlier stratified scripts: repeated
# copies at one site get one vote; an independent cross-site attestation stays.
recs = dedup(raw, lambda r: (r["text"], r["site"]))
obj_recs = dedup(raw, lambda r: (r["text"], r["object"]))
texts = [r["text"] for r in recs]
freq = Counter(g for text in texts for g in text)
testable = sorted(g for g, n in freq.items() if n >= MIN_N)

print("=== corpus ===")
print(f"  merged lines: {len(lines)}")
print(f"  distinct sequence x site, length >= 2: {len(recs)}")
print(f"  signs in >= {MIN_N} texts: {len(testable)}")


def occupancy(g, right_k):
    """Observed and exact within-text positional-shuffle moments."""
    eligible = [text for text in texts if len(text) >= right_k]
    observed = sum(text[-right_k] == g for text in eligible)
    probabilities = [text.count(g) / len(text) for text in eligible if g in text]
    expected = sum(probabilities)
    variance = sum(p * (1 - p) for p in probabilities)
    z = (observed - expected) / math.sqrt(variance) if variance else float("nan")
    return {"observed": observed, "expected": expected,
            "z": z, "eligible": len(eligible)}


matrix = {g: {k: occupancy(g, k) for k in range(1, MAX_RIGHT + 1)}
          for g in testable}

print("\n=== sign x right-position occupancy matrix ===")
print("  Each cell is observed / exact positional-shuffle expectation / z.")
print("  sign     n       -1             -2             -3             -4")
for g in sorted(testable, key=lambda x: (-freq[x], x)):
    cells = []
    for k in range(1, 5):
        r = matrix[g][k]
        cells.append(f"{r['observed']:>3}/{r['expected']:>4.1f}/{r['z']:>+5.1f}")
    print(f"  {g:>4} {freq[g]:>5}  " + "  ".join(cells))

cohorts = {k: sorted(g for g in testable if matrix[g][k]["z"] >= LOCAL_Z)
           for k in (1, 2, 3)}
flat = sorted(g for g in testable
              if max(abs(matrix[g][k]["z"]) for k in (1, 2, 3)) < LOCAL_Z)

print(f"\n=== localisation at z >= {LOCAL_Z:g} against the position shuffle ===")
for k in (1, 2, 3):
    ranked = sorted(cohorts[k], key=lambda g: matrix[g][k]["z"], reverse=True)
    print(f"  -{k} ({len(ranked)} signs): " +
          ", ".join(f"{g}({matrix[g][k]['z']:.1f})" for g in ranked))
print(f"  flat over -1..-3 ({len(flat)} signs; no |z| >= {LOCAL_Z:g}): " +
      ", ".join(map(str, flat)))


def mh(a, b, rows, stratum):
    """Mantel-Haenszel z for co-occurrence; negative means avoidance."""
    groups = defaultdict(list)
    for row in rows:
        groups[stratum(row)].append(set(row["text"]))
    num = den = observed = expected = 0.0
    used = 0
    for ss in groups.values():
        n = len(ss)
        if n < 2:
            continue
        na = sum(a in s for s in ss)
        nb = sum(b in s for s in ss)
        if not na or not nb or na == n or nb == n:
            continue
        both = sum(a in s and b in s for s in ss)
        e = na * nb / n
        v = na * nb * (n - na) * (n - nb) / (n * n * (n - 1))
        observed += both
        expected += e
        num += both - e
        den += v
        used += 1
    return {"observed": observed, "expected": expected,
            "z": num / math.sqrt(den) if den else float("nan"),
            "strata": used}


def exclusion_scan(signs):
    tested = []
    for i, a in enumerate(signs):
        for b in signs[i + 1:]:
            length = mh(a, b, recs, lambda r: len(r["text"]))
            if length["expected"] < 3:
                continue
            tested.append({"a": a, "b": b, "length": length,
                           "p": stats.norm.cdf(length["z"])})
    tested.sort(key=lambda r: r["p"])
    discoveries = []
    for rank, row in enumerate(tested, 1):
        if row["p"] <= FDR * rank / len(tested):
            discoveries = tested[:rank]
    for row in discoveries:
        row["site"] = mh(row["a"], row["b"], recs, lambda r: r["site"])
        row["object"] = mh(row["a"], row["b"], obj_recs, lambda r: r["object"])
        row["survives"] = row["site"]["z"] < -1.96 and row["object"]["z"] < -1.96
    return tested, discoveries, [r for r in discoveries if r["survives"]]


scans = {}
print("\n=== pairwise exclusion inside each right-position cohort ===")
for k in (1, 2, 3):
    tested, discoveries, survivors = exclusion_scan(cohorts[k])
    scans[k] = (tested, discoveries, survivors)
    print(f"\n  -{k}: {len(cohorts[k])} signs, {len(tested)} powered pairs, "
          f"{len(discoveries)} at BH q<{FDR}, {len(survivors)} survive site+object")
    if not survivors:
        print("      no surviving pairs")
    for row in survivors:
        le, si, ob = row["length"], row["site"], row["object"]
        print(f"    {row['a']:>4}/{row['b']:<4} obs {le['observed']:>4.0f} "
              f"exp {le['expected']:>5.1f}  z {le['z']:>6.2f}  "
              f"z|site {si['z']:>6.2f}  z|object {ob['z']:>6.2f}")

print("\n=== the two signs previously assigned to the position behind 740 ===")
print("  pair      obs   E|length   z|length   z|site   z|object")
for a, b in ((400, 90), (740, 400), (740, 90)):
    le = mh(a, b, recs, lambda r: len(r["text"]))
    si = mh(a, b, recs, lambda r: r["site"])
    ob = mh(a, b, obj_recs, lambda r: r["object"])
    print(f"  {a:>3}/{b:<3} {le['observed']:>6.0f} {le['expected']:>10.1f} "
          f"{le['z']:>10.2f} {si['z']:>8.2f} {ob['z']:>10.2f}")
for g in (400, 90):
    shares = [matrix[g][k]["observed"] / freq[g] for k in (1, 2, 3)]
    print(f"  {g}: share at -1/-2/-3 = " + "/".join(f"{x:.0%}" for x in shares))


# ---------------------------------------------------------------- growth check
def growth_counts(corpus):
    """One-sign-longer subsequence pairs and preserved right edge.

    Deleting one sign from the longer sequence enumerates every possible
    one-sign-shorter subsequence. Counter weights reproduce growth.py's
    sequence-x-site observations without a quadratic nested loop.
    """
    by_length = defaultdict(Counter)
    for text in corpus:
        by_length[len(text)][text] += 1
    pairs = same_one = same_two = 0
    for length, shorter in by_length.items():
        for long_text, n_long in by_length.get(length + 1, {}).items():
            deletions = {long_text[:j] + long_text[j + 1:]
                         for j in range(len(long_text))}
            for short_text in deletions:
                n_short = shorter.get(short_text, 0)
                if not n_short:
                    continue
                weight = n_short * n_long
                pairs += weight
                same_one += weight * (short_text[-1] == long_text[-1])
                same_two += weight * (short_text[-2:] == long_text[-2:])
    return pairs, same_one / pairs if pairs else 0, same_two / pairs if pairs else 0


slot_distribution = defaultdict(list)
for text in texts:
    for i, g in enumerate(text):
        slot_distribution[(len(text), i)].append(g)


def simulate_position_corpus():
    out = []
    for text in texts:
        length = len(text)
        for _ in range(20):
            draw = tuple(RNG.choice(slot_distribution[(length, i)])
                         for i in range(length))
            if len(set(draw)) == length:
                break
        out.append(draw)
    return out


observed_growth = growth_counts(texts)
growth_null = np.asarray([growth_counts(simulate_position_corpus())
                          for _ in range(N_GROWTH_SIM)], dtype=float)

print("\n=== growth.py cross-check: do one-sign-longer pairs keep the last two? ===")
print(f"  observed pairs: {observed_growth[0]:.0f}")
print("  measure           observed   position-null mean   null 95%       z    p lower/upper")
for label, col in (("same last sign", 1), ("same last two", 2)):
    values = growth_null[:, col]
    obs = observed_growth[col]
    z = (obs - values.mean()) / values.std(ddof=1)
    p_upper = (1 + np.sum(values >= obs)) / (N_GROWTH_SIM + 1)
    p_lower = (1 + np.sum(values <= obs)) / (N_GROWTH_SIM + 1)
    lo, hi = np.quantile(values, [.025, .975])
    print(f"  {label:<16} {obs:>8.1%} {values.mean():>20.1%} "
          f"{lo:>7.1%}-{hi:<7.1%} {z:>6.2f} {p_lower:.4f}/{p_upper:.4f}")

print("\n  The first number is the 13-growth last-sign statistic after direction correction.")
print("  Its positional control is new; the last-two comparison is the requested extension.")
