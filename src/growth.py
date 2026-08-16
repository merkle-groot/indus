"""How do longer texts grow?

A form grows by filling optional fields, so a short record should look like a
long one with holes: `name / __ / __ / total` vs `name / date / qty / total`.
Sentences do not behave that way -- lengthening a sentence rearranges it.

The test: is a short text a **subsequence** of a longer one? (Same signs, same
order, gaps allowed -- exactly what "a form with some fields left blank" means.)

The trap, and it has bitten this project before (08-hierarchy.md): the corpus has
strong positional habits. 740 sits at the end, 817 at the start. Containment
will happen constantly by accident. So everything is measured against a null
that reproduces those habits exactly:

  N1 frequency  -- signs drawn by corpus frequency, text lengths preserved
  N2 positional -- each slot of a length-L text drawn from the real distribution
                   of signs at that slot in real length-L texts. This preserves
                   every positional preference and is the null that matters.

  G1 containment -- how many short texts are subsequences of a longer one?
  G2 chains      -- a form should nest deeply: T1 in T2 in T3 in ...
  G3 insertions  -- where does the extra sign go, and is it drawn from a
                    restricted set (a field) or from anywhere (a modifier)?
"""
import json
import random
from collections import Counter, defaultdict

RNG = random.Random(0)
N_SIM = 200

lines = json.loads(open("data/parsed/lines.json").read())
texts, seen = [], set()
for l in lines:
    t = tuple(g for g in l["signs"] if g)
    if len(t) < 2:
        continue
    k = (t, l.get("site"))
    if k in seen:
        continue
    seen.add(k)
    texts.append(t)
print(f"distinct texts: {len(texts)}")

bylen = defaultdict(list)
for t in texts:
    bylen[len(t)].append(t)
print("  " + "  ".join(f"{L}:{len(v)}" for L, v in sorted(bylen.items())))

signs = sorted({g for t in texts for g in t})
bit = {g: 1 << i for i, g in enumerate(signs)}


def mask(t):
    m = 0
    for g in t:
        m |= bit[g]
    return m


def is_sub(s, t):
    """Is s a subsequence of t?"""
    i = 0
    for g in t:
        if g == s[i]:
            i += 1
            if i == len(s):
                return True
    return False


def is_run(s, t):
    """Is s a contiguous block of t? (what a broken artefact would leave)"""
    return any(t[i:i + len(s)] == s for i in range(len(t) - len(s) + 1))


def containment(ts, gapped_only=False):
    """Fraction of texts that are a proper subsequence of some longer text.

    gapped_only: count a text only if it is a subsequence of some longer text
    and is a contiguous block of NO longer text. Breakage can produce a
    contiguous fragment; it cannot produce a text with a hole in the middle.
    """
    byl = defaultdict(list)
    for t in ts:
        byl[len(t)].append((mask(t), t))
    lens = sorted(byl)
    hits = 0
    for L in lens:
        longer = [(m, t) for LL in lens if LL > L for m, t in byl[LL]]
        for sm, s in byl[L]:
            sub = run = False
            for lm, t in longer:
                if sm & lm != sm:
                    continue
                if is_run(s, t):
                    run = True
                    break
                if is_sub(s, t):
                    sub = True
            if run:
                hits += not gapped_only
            elif sub:
                hits += 1
    return hits / len(ts)


# ------------------------------------------------------------------ nulls
freq = Counter(g for t in texts for g in t)
pool = list(freq.elements())

slotdist = defaultdict(list)
for t in texts:
    for i, g in enumerate(t):
        slotdist[(len(t), i)].append(g)


def sim_freq():
    out = []
    for t in texts:
        for _ in range(20):
            c = tuple(RNG.sample(pool, len(t)))
            if len(set(c)) == len(c):
                break
        out.append(c)
    return out


def sim_pos():
    out = []
    for t in texts:
        L = len(t)
        for _ in range(20):
            c = tuple(RNG.choice(slotdist[(L, i)]) for i in range(L))
            if len(set(c)) == len(c):
                break
        out.append(c)
    return out


print("\n=== G1: is a short text a longer text with holes? ===")
sims = {n: [fn() for _ in range(max(N_SIM // 20, 5))]
        for n, fn in (("frequency-matched", sim_freq),
                      ("position-matched", sim_pos))}
for gapped in (False, True):
    label = ("subsequence of a longer text" if not gapped else
             "GAPPED only -- has a hole, so breakage cannot explain it")
    obs = containment(texts, gapped)
    print(f"\n  {label}")
    print(f"    observed: {obs:.1%}")
    for name, corpora in sims.items():
        vals = [containment(c, gapped) for c in corpora]
        mu = sum(vals) / len(vals)
        sd = (sum((v - mu) ** 2 for v in vals) / max(len(vals) - 1, 1)) ** .5
        z = (obs - mu) / sd if sd else float("nan")
        print(f"    {name:<18} null {mu:.1%} (sd {sd:.1%})   z = {z:+.1f}")

# ------------------------------------------------------------------ G2
print("\n=== G2: how deep do the nestings go? ===")
byl = defaultdict(list)
for t in texts:
    byl[len(t)].append((mask(t), t))
lens = sorted(byl)
depth = {}
for L in lens:
    for sm, s in byl[L]:
        depth.setdefault(s, 1)
for L in lens:
    for sm, s in byl[L]:
        d = depth[s]
        for LL in lens:
            if LL <= L:
                continue
            for lm, t in byl[LL]:
                if sm & lm == sm and is_sub(s, t):
                    depth[t] = max(depth.get(t, 1), d + 1)
c = Counter(depth.values())
print("  longest nesting chain a text sits at the top of:")
for k in sorted(c):
    print(f"    depth {k}: {c[k]} texts")

# ------------------------------------------------------------------ G3
print("\n=== G3: where does the extra sign go? ===")
where = Counter()
added = Counter()
pairs = 0
for L in lens:
    if L + 1 not in byl:
        continue
    for sm, s in byl[L]:
        for lm, t in byl[L + 1]:
            if sm & lm != sm or not is_sub(s, t):
                continue
            # find the inserted position
            i = 0
            for j, g in enumerate(t):
                if i < len(s) and g == s[i]:
                    i += 1
                else:
                    where["start" if j == 0 else
                          "end" if j == len(t) - 1 else "middle"] += 1
                    added[g] += 1
                    break
            pairs += 1
print(f"  exact one-sign-longer pairs: {pairs}")
tot = sum(where.values())
for k in ("start", "middle", "end"):
    print(f"    inserted at {k:<7}: {where[k]:>4} ({where[k]/max(tot,1):.0%})")
print(f"\n  distinct signs ever inserted: {len(added)} "
      f"(corpus has {len(signs)})")
print("  most-inserted:", ", ".join(f"{g}({n})" for g, n in added.most_common(10)))
share = sum(n for _, n in added.most_common(10)) / max(sum(added.values()), 1)
print(f"  top 10 account for {share:.0%} of all insertions")

# does the terminal sign survive lengthening?
same_end = sum(1 for L in lens if L + 1 in byl
               for sm, s in byl[L] for lm, t in byl[L + 1]
               if sm & lm == sm and is_sub(s, t) and s[-1] == t[-1])
print(f"\n  pairs where the last sign is unchanged: {same_end}/{pairs} "
      f"({same_end/max(pairs,1):.0%})")
