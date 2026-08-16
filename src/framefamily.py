"""The frame/rake family and the sign 920 collocation.

Started from a suggestion that unidentified sign 316 might be a modification of
sign 360. The database numbers signs roughly by shape, and 316 sits inside a
family of frames, ladders and rakes -- so the instinct was sound.

What came out was a strong collocation, and a methodological failure worth
keeping in the repo rather than quietly fixing.

  F1 family rate  -- how often is this family followed by sign 920?
  F2 the bad split -- the version that sorted signs by the OUTCOME
  F3 the honest split -- the same test with groups read off the glyph shapes
  F4 robustness   -- does the split survive dropping its biggest contributor?

Shape classes below are read off renders at 260px (see notes/21-frame-family.md)
and are fixed before any 920 count is taken. That ordering is the whole point.
"""
import json
from collections import Counter

from scipy.stats import binomtest, fisher_exact

TARGET = 920
# --- assigned from the glyph renders, BEFORE looking at any 920 count ---
TOOTHED = [318, 320, 322, 323, 324, 325, 326, 330]   # frame + teeth below
PLAIN = [315, 317, 360]                              # frame or ladder, no teeth
FAMILY = TOOTHED + PLAIN
# --- the grouping I used first, which sorted 324/325/326/330 by their 920
#     count rather than their shape. Kept so the error is reproducible. ---
BAD_TOOTHED = [317, 318, 320, 322, 323]
BAD_PLAIN = [315, 324, 325, 326, 330, 360]

lines = json.loads(open("data/parsed/lines.json").read())
texts, seen = [], set()
for l in lines:
    t = tuple(x for x in l["signs"] if x)
    if not t:
        continue
    k = (t, l.get("site"))
    if k in seen:
        continue
    seen.add(k)
    texts.append(t)
print(f"deduplicated texts: {len(texts)}")


def rate(ids):
    """(times followed by TARGET, times in a non-final slot)"""
    ids = set(ids)
    n = f = 0
    for t in texts:
        for i in range(len(t) - 1):
            if t[i] in ids:
                n += 1
                f += t[i + 1] == TARGET
    return f, n


base_f = sum(1 for t in texts for i in range(len(t) - 1) if t[i + 1] == TARGET)
base_n = sum(len(t) - 1 for t in texts)
base = base_f / base_n
print(f"base rate: {TARGET} follows anything in {base_f}/{base_n} = {base:.2%}")

# ------------------------------------------------------------------ F1
print("\n=== F1: the family as a whole ===")
for g in FAMILY:
    f, n = rate([g])
    print(f"  {g:>4}  {'toothed' if g in TOOTHED else 'plain  '}  {f}/{n}")
ff, fn = rate(FAMILY)
print(f"\n  family {ff}/{fn} = {ff/fn:.0%}  vs base {base:.2%}")
print(f"  p = {binomtest(ff, fn, base, alternative='greater').pvalue:.2e}")

# ------------------------------------------------------------------ F2
print("\n=== F2: the circular split (groups defined by the outcome) ===")
a, an = rate(BAD_TOOTHED)
b, bn = rate(BAD_PLAIN)
print(f"  'toothed' {a}/{an}   'plain' {b}/{bn}   "
      f"p = {fisher_exact([[a, an - a], [b, bn - b]])[1]:.2e}")
print("  324, 325, 326 and 330 all have teeth. They were filed as plain because")
print("  their 920 count is zero -- i.e. sorted by the variable under test.")

# ------------------------------------------------------------------ F3
print("\n=== F3: the honest split (groups from the glyph shapes) ===")
a, an = rate(TOOTHED)
b, bn = rate(PLAIN)
print(f"  toothed {a}/{an} = {a/an:.0%}   plain {b}/{bn} = {b/bn:.0%}   "
      f"p = {fisher_exact([[a, an - a], [b, bn - b]])[1]:.4f}")
print("  note 317 is a plain ladder and takes 920 twice, so the line leaks.")

# ------------------------------------------------------------------ F4
print("\n=== F4: does it survive dropping its biggest contributor? ===")
for drop in (None, 320):
    tt = [g for g in TOOTHED if g != drop]
    a, an = rate(tt)
    b, bn = rate(PLAIN)
    lab = "all toothed" if drop is None else f"minus {drop}"
    print(f"  {lab:<14} {a}/{an} vs {b}/{bn}   "
          f"p = {fisher_exact([[a, an - a], [b, bn - b]])[1]:.4f}")
print("\n  Nine of the fifteen toothed hits are sign 320 alone. The shape-based")
print("  split is withdrawn; the family-level collocation stands.")

# ------------------------------------------------------------------ 316
print("\n=== sign 316, the unidentified member ===")
f, n = rate([316])
print(f"  followed by {TARGET}: {f}/{n}  (family rate {ff/fn:.0%}) -- no power")
for l in lines:
    s = [x for x in l["signs"] if x]
    if 316 in s:
        fam = [x for x in s if x in FAMILY]
        print(f"  {l.get('artifact')}: {s}   other family members: {fam}")
print("  316 and 323 are adjacent on H-1005, and this corpus avoids repeating a")
print("  sign within a text, so they are not the same sign.")

# ------------------------------------------------------------------ 326/330
print("\n=== 326 and 330 ===")
c = sum(1 for t in texts if 326 in t or 330 in t)
print(f"  identical on the renders; {c} texts between them, "
      f"{rate([326, 330])[0]}/{rate([326, 330])[1]} on the {TARGET} collocation")
print("  merged as a documented override in src/apply_merges.py")
