"""Is a doubled sign one sign or two?

The font encodes several catalogue entries as two copies of another entry:
617 = 615+615, 34 = 32+32, and so on.  There are three live models.

  repetition    D behaves like S and inherits the corpus-wide no-repeat rule
  independent   D has its own distribution, unrelated to S
  derivational  D stays in the same broad class but changes S's slot/context

All inference uses lines_merged.json.  Exact text sequences are deduplicated
globally for distributional tests; site and object controls retain at most one
copy of a sequence in each relevant stratum.  The controls are:

  * Mantel-Haenszel co-occurrence tests stratified separately by length, site,
    and object class, following slots.py;
  * an exact-position shuffle: for every text length, independently permute
    the signs occupying each absolute slot.  This preserves every sign's
    length-by-position occupancy while breaking which signs share a text;
  * unrelated sign pairs matched on both endpoint frequencies for position and
    left/right-neighbour cosine comparisons.
"""
import json
import math
import random
from collections import Counter, defaultdict

import numpy as np
from scipy import stats

RNG = random.Random(25)
N_SHUFFLE = 4000
MATCH_POOL = 200

# The seven sufficiently attested doubled entries identified in 20-composites.
# 792 is retained even though its base, 809, is a singleton: that failure of
# power is part of the result.  The two numeric checks below are supplemental.
TARGETS = [(617, 615), (34, 32), (821, 820), (792, 809),
           (219, 220), (401, 400), (791, 790)]
NUMERIC_CHECKS = [(34, 32), (36, 33), (56, 55)]


def dedup(rows, key):
    out, seen = [], set()
    for row in rows:
        k = key(row)
        if k in seen:
            continue
        seen.add(k)
        out.append(row)
    return out


lines = json.load(open("data/parsed/lines_merged.json"))
inscriptions = json.load(open("data/parsed/inscriptions.json"))
by_artifact = {i["cisi"] or f"#{i['seal_id']}": i for i in inscriptions}

rows = []
for line in lines:
    text = tuple(g for g in line["signs"] if g)
    if not text:
        continue
    meta = by_artifact.get(line.get("artifact"), {})
    rows.append({"text": text, "site": line.get("site"),
                 "object": meta.get("obj_class")})

# Global sequence distribution; separate deduplications retain cross-stratum
# attestations without allowing mass-produced copies inside a stratum to vote.
global_rows = dedup(rows, lambda r: r["text"])
site_rows = dedup(rows, lambda r: (r["text"], r["site"]))
object_rows = dedup(rows, lambda r: (r["text"], r["object"]))
texts = [r["text"] for r in global_rows]
freq = Counter(g for text in texts for g in text)

print("=== corpus ===")
print(f"  merged lines: {len(lines)}")
print(f"  distinct sequences: {len(global_rows)}")
print(f"  sequence x site attestations: {len(site_rows)}")
print(f"  sequence x object attestations: {len(object_rows)}")


def mh(a, b, recs, stratum):
    """Mantel-Haenszel z for presence of a and b; negative is avoidance."""
    groups = defaultdict(list)
    for rec in recs:
        groups[stratum(rec)].append(set(rec["text"]))
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


def exact_position_null(pairs):
    """Co-occurrence null preserving the occupant multiset of every L x slot."""
    by_length = defaultdict(list)
    for text in texts:
        by_length[len(text)].append(text)
    observed = {pair: sum(pair[0] in t and pair[1] in t for t in texts)
                for pair in pairs}
    sims = {pair: np.empty(N_SHUFFLE, dtype=float) for pair in pairs}
    for run in range(N_SHUFFLE):
        counts = Counter()
        for length, group in by_length.items():
            cols = [[text[j] for text in group] for j in range(length)]
            for col in cols:
                RNG.shuffle(col)
            for i in range(len(group)):
                present = {cols[j][i] for j in range(length)}
                for pair in pairs:
                    if pair[0] in present and pair[1] in present:
                        counts[pair] += 1
        for pair in pairs:
            sims[pair][run] = counts[pair]
    out = {}
    for pair, values in sims.items():
        obs = observed[pair]
        sd = values.std(ddof=1)
        out[pair] = {"observed": obs, "mean": values.mean(), "sd": sd,
                     "z": (obs - values.mean()) / sd if sd else float("nan"),
                     "p_lower": (1 + np.sum(values <= obs)) / (N_SHUFFLE + 1)}
    return out


def cosine(a, b):
    keys = set(a) | set(b)
    den = math.sqrt(sum(v * v for v in a.values()) *
                    sum(v * v for v in b.values()))
    return sum(a[k] * b[k] for k in keys) / den if den else float("nan")


pos = defaultdict(Counter)
left = defaultdict(Counter)
right = defaultdict(Counter)
context = defaultdict(Counter)
end = Counter()
texts_with = Counter()
for text in texts:
    for g in set(text):
        texts_with[g] += 1
    for i, g in enumerate(text):
        if len(text) == 1:
            pos[g]["initial"] += .5
            pos[g]["final"] += .5
        elif i == 0:
            pos[g]["initial"] += 1
        elif i == len(text) - 1:
            pos[g]["final"] += 1
        else:
            pos[g]["medial"] += 1
        if i:
            left[g][text[i - 1]] += 1
            context[g][("L", text[i - 1])] += 1
        if i + 1 < len(text):
            right[g][text[i + 1]] += 1
            context[g][("R", text[i + 1])] += 1
        if i == len(text) - 1:
            end[g] += 1


def metric(a, b):
    return {"position": cosine(pos[a], pos[b]),
            "left": cosine(left[a], left[b]),
            "right": cosine(right[a], right[b]),
            "context": cosine(context[a], context[b])}


all_signs = sorted(g for g, n in freq.items() if n >= 2)


def matched_baseline(a, b):
    """Nearest unrelated pairs by both endpoint log frequencies."""
    target = sorted((math.log1p(freq[a]), math.log1p(freq[b])))
    candidates = []
    for i, x in enumerate(all_signs):
        if x in (a, b):
            continue
        for y in all_signs[i + 1:]:
            if y in (a, b):
                continue
            here = sorted((math.log1p(freq[x]), math.log1p(freq[y])))
            distance = abs(target[0] - here[0]) + abs(target[1] - here[1])
            candidates.append((distance, x, y))
    candidates.sort()
    chosen = candidates[:min(MATCH_POOL, len(candidates))]
    vals = defaultdict(list)
    for _, x, y in chosen:
        for name, value in metric(x, y).items():
            if not math.isnan(value):
                vals[name].append(value)
    result = {}
    observed = metric(a, b)
    for name, values in vals.items():
        arr = np.asarray(values)
        result[name] = {"observed": observed[name],
                        "median": float(np.median(arr)),
                        "p90": float(np.quantile(arr, .9)),
                        "percentile": float(np.mean(arr <= observed[name]))
                        if not math.isnan(observed[name]) else float("nan")}
    return result


pairs_for_null = sorted(set(TARGETS + [(617, 740), (615, 740)]))
shuffle = exact_position_null(pairs_for_null)

print("\n=== D and S in the same text ===")
print("  pair       nD   nS  obs  E|len  z|len  z|site z|object  E|position z|position  p")
exclusion = {}
for d, s in TARGETS:
    length = mh(d, s, global_rows, lambda r: len(r["text"]))
    site = mh(d, s, site_rows, lambda r: r["site"])
    obj = mh(d, s, object_rows, lambda r: r["object"])
    pn = shuffle[(d, s)]
    exclusion[(d, s)] = (length, site, obj, pn)
    print(f"  {d:>3}/{s:<3} {texts_with[d]:>4} {texts_with[s]:>4} "
          f"{length['observed']:>4.0f} {length['expected']:>6.1f} {length['z']:>6.2f} "
          f"{site['z']:>7.2f} {obj['z']:>8.2f} {pn['mean']:>10.1f} "
          f"{pn['z']:>10.2f} {pn['p_lower']:>6.4f}")

print("\n=== positional and neighbour similarity ===")
print("  Pair    position cosine [matched med,p90,pct]   context cosine [matched med,p90,pct]")
baselines = {}
for d, s in TARGETS:
    base = matched_baseline(d, s)
    baselines[(d, s)] = base
    p, c = base.get("position", {}), base.get("context", {})
    def show(x):
        if not x or math.isnan(x["observed"]):
            return "not estimable"
        return (f"{x['observed']:.3f} [{x['median']:.3f},{x['p90']:.3f},"
                f"{x['percentile']:.0%}]")
    print(f"  {d:>3}/{s:<3} {show(p):<34} {show(c)}")

print("\n  left and right context separately")
print("  Pair     left cosine   right cosine")
for d, s in TARGETS:
    m = metric(d, s)
    print(f"  {d:>3}/{s:<3} {m['left']:>11.3f} {m['right']:>14.3f}")

print("\n=== is 615 a terminal-slot filler like 617? ===")
print("  sign    texts   final   final share   vs 740 obs/E|len/z   z|site z|object z|position")
terminal = {}
for g in (617, 615):
    length = mh(g, 740, global_rows, lambda r: len(r["text"]))
    site = mh(g, 740, site_rows, lambda r: r["site"])
    obj = mh(g, 740, object_rows, lambda r: r["object"])
    pn = shuffle[(g, 740)]
    terminal[g] = (length, site, obj, pn)
    print(f"  {g:>4} {texts_with[g]:>8} {end[g]:>7} {end[g]/texts_with[g]:>12.1%}   "
          f"{length['observed']:.0f}/{length['expected']:.1f}/{length['z']:+.2f}"
          f" {site['z']:>8.2f} {obj['z']:>8.2f} {pn['z']:>10.2f}")

print("\n=== numeric ground truth (including low-power checks) ===")
print("  D/S      nD/nS   position cosine   context cosine   co-occur")
for d, s in NUMERIC_CHECKS:
    m = metric(d, s)
    both = sum(d in text and s in text for text in texts)
    print(f"  {d:>2}/{s:<2} {freq[d]:>4}/{freq[s]:<4} {m['position']:>16.3f} "
          f"{m['context']:>16.3f} {both:>10}")

print("\nInterpretation is written in notes/25-doubled-signs.md; the script")
print("prints the failed comparisons as well as the anchor result.")
