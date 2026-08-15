"""Is "1" rare because you simply don't write it?

Values run 1:282, 2:519, 3:386 once the frozen 817/861+2 collocation is removed.
That ordering is wrong for a counting system: you count one of something far
more often than seven. The standard explanation is that the singular is
**unmarked** -- a bare sign already means one, and you only add strokes for more
than one. If so, "1 X" and plain "X" are the same message.

That is a testable claim, and each test can refute it:

  U1 minimal pairs -- if the 1 is optional, texts should occur both with and
                      without it. Deleting a 2 changes the message, so value-1
                      minimal pairs should be commoner than value-2 or -3 pairs.
  U2 same targets  -- an optional singular marks the same nouns everything else
                      counts. If 1 attaches to its own private set of signs, it
                      is not a numeral at all.
  U3 free variation-- optional markers usually vary by scribe. Does writing the
                      1 split by site or object class?
  U4 position      -- "1 X" should sit where "n X" sits. If the 1 lives
                      somewhere else in the text, it is doing another job.
"""
import json
from collections import Counter, defaultdict

from scipy import stats

SHORT = set(range(1, 8))
LONG = {31, 32, 33, 34, 35}
TWOROW = set(range(12, 20))
TRIO = {817, 820, 861}


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
texts = []
for l in lines:
    s = [g for g in l["signs"] if g]
    if s:
        texts.append((tuple(s), l.get("site"), l.get("artifact")))
seqs = [t for t, _, _ in texts]
print(f"texts: {len(seqs)}   distinct: {len(set(seqs))}")

# ------------------------------------------------------------------ U1
print("\n=== U1: minimal pairs -- same text with and without the numeral ===")
have = set(seqs)
res = {}
for v in (1, 2, 3, 4):
    hits, opp = [], 0
    for t in set(seqs):
        for i, g in enumerate(t):
            if value(g) != v:
                continue
            # do not count the frozen collocation as an optional numeral
            if i and t[i - 1] in TRIO:
                continue
            opp += 1
            short = t[:i] + t[i + 1:]
            if short and short in have:
                hits.append((t, short))
    res[v] = (len(hits), opp)
    print(f"  value {v}: {len(hits)} of {opp} occurrences can be deleted and "
          f"still leave an attested text  ({len(hits)/max(opp,1):.1%})")
    for a, b in hits[:3]:
        print(f"      {list(a)}  ->  {list(b)}")

a1, n1 = res[1]
a2, n2 = res[2][0] + res[3][0], res[2][1] + res[3][1]
p = stats.fisher_exact([[a1, n1 - a1], [a2, n2 - a2]])[1]
print(f"\n  value 1 ({a1}/{n1}) vs values 2-3 ({a2}/{n2}):  p = {p:.4f}")
print("  prediction if 1 is optional: value 1 should be deletable MORE often")

# ------------------------------------------------------------------ U2
print("\n=== U2: does 1 count the same signs everything else counts? ===")
tgt = defaultdict(Counter)
for t in seqs:
    for i in range(len(t) - 1):
        v = value(t[i])
        if v is None or value(t[i + 1]) is not None:
            continue
        if i and t[i - 1] in TRIO:
            continue
        tgt[v][t[i + 1]] += 1
ones = tgt[1]
rest = Counter()
for v in range(2, 8):
    rest += tgt[v]
print(f"  distinct signs counted by 1      : {len(ones)} ({sum(ones.values())} tokens)")
print(f"  distinct signs counted by 2-7    : {len(rest)} ({sum(rest.values())} tokens)")
shared = set(ones) & set(rest)
print(f"  signs counted by both            : {len(shared)} "
      f"({len(shared)/len(ones):.0%} of 1's targets)")
print(f"  counted ONLY by 1                : {len(set(ones) - set(rest))}")

common = sorted(shared, key=lambda g: -(ones[g] + rest[g]))[:10]
print("\n  top shared targets      by 1   by 2-7   1's share")
for g in common:
    print(f"    {g:<20} {ones[g]:>5} {rest[g]:>7}     "
          f"{ones[g]/(ones[g]+rest[g]):.0%}")
tab = [[ones[g] for g in common], [rest[g] for g in common]]
print(f"  is 1 used on the same targets in the same proportions? "
      f"chi2 p = {stats.chi2_contingency(tab)[1]:.2e}")

# ------------------------------------------------------------------ U3
print("\n=== U3: does writing the 1 vary by site or object? ===")
for key, label in (("site", "site"), ("obj_class", "object class")):
    c1, cn = Counter(), Counter()
    for t, site, art in texts:
        rec = None
        for i in ins.values():
            pass
        k = site if key == "site" else None
        for i, g in enumerate(t):
            v = value(g)
            if v is None or (i and t[i - 1] in TRIO):
                continue
            (c1 if v == 1 else cn)[k] += 1
        if key != "site":
            break
    if key != "site":
        continue
    keys = [k for k, _ in (c1 + cn).most_common(5)]
    print(f"  {label}: " + "  ".join(f"{k}({c1[k]}/{c1[k]+cn[k]})" for k in keys))
    tab = [[c1[k] for k in keys], [cn[k] for k in keys]]
    print(f"    chi2 p = {stats.chi2_contingency(tab)[1]:.4f}   "
          f"(free variation would show a split)")

# object class needs the artefact join
byart = {}
for i in ins.values():
    byart[i["cisi"] or f"#{i['seal_id']}"] = i.get("obj_class")
c1, cn = Counter(), Counter()
for t, site, art in texts:
    k = byart.get(art)
    for i, g in enumerate(t):
        v = value(g)
        if v is None or (i and t[i - 1] in TRIO):
            continue
        (c1 if v == 1 else cn)[k] += 1
keys = [k for k, _ in (c1 + cn).most_common(4) if k]
print("  object class: " + "  ".join(f"{k}({c1[k]}/{c1[k]+cn[k]})" for k in keys))
tab = [[c1[k] for k in keys], [cn[k] for k in keys]]
print(f"    chi2 p = {stats.chi2_contingency(tab)[1]:.4f}")

# ------------------------------------------------------------------ U4
print("\n=== U4: does the 1 sit where other numerals sit? ===")
pos = defaultdict(list)
for t in seqs:
    if len(t) < 2:
        continue
    for i, g in enumerate(t):
        v = value(g)
        if v is None or (i and t[i - 1] in TRIO):
            continue
        pos[1 if v == 1 else 0].append(i / (len(t) - 1))
print(f"  value 1     : n={len(pos[1]):>4}  mean position {sum(pos[1])/len(pos[1]):.3f}")
print(f"  values 2-9  : n={len(pos[0]):>4}  mean position {sum(pos[0])/len(pos[0]):.3f}")
print(f"  Mann-Whitney p = {stats.mannwhitneyu(pos[1], pos[0]).pvalue:.2e}")
