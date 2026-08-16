"""Are lines.json and lines_merged.json normalized to analytical reading order?

eda.py originally reversed R/L inscriptions and left L/R inscriptions alone.
Test that choice against the established terminal fillers 740 and 520, using
the raw GLYPHSEQUENCE arrays in inscriptions.json and the applied allograph map.

The positional null uniformly shuffles tokens within each text, so it preserves
length, content, site, and object class.  The 740/520 exclusion statistic is
also recomputed before and after correction with the length/site/object
Mantel-Haenszel controls used by slots.py.
"""
import json
import math
from collections import defaultdict

inscriptions = json.load(open("data/parsed/inscriptions.json"))
allograph = json.load(open("data/parsed/allograph_map.json"))["map"]
merge = {int(k): v for k, v in allograph.items()}


def physical_lines(inscription):
    out, current = [], []
    for g in inscription["glyphs"] + [0]:
        if g == 0:
            if current:
                out.append(tuple(merge.get(x, x) for x in current))
                current = []
        else:
            current.append(g)
    return out


def transform(raw, direction, corrected):
    # Old eda.py: reverse R/L, preserve L/R.  The corrected transform reverses
    # both because the L/R subset empirically has the same array orientation.
    return raw[::-1] if corrected or direction == "R/L" else raw


def direction_texts(direction, corrected=False):
    texts = [transform(raw, direction, corrected)
             for ins in inscriptions if ins["direction"] == direction
             for raw in physical_lines(ins) if raw]
    return sorted(set(texts))


def endpoint_stats(texts, g):
    containing = [text for text in texts if g in text]
    expected = sum(text.count(g) / len(text) for text in containing)
    variance = sum((text.count(g) / len(text)) * (1 - text.count(g) / len(text))
                   for text in containing)
    start = sum(text[0] == g for text in containing)
    end = sum(text[-1] == g for text in containing)
    sd = math.sqrt(variance)
    return {"n": len(containing), "start": start, "end": end,
            "expected": expected,
            "z_start": (start - expected) / sd if sd else float("nan"),
            "z_end": (end - expected) / sd if sd else float("nan")}


print("=== direction labels ===")
for direction in ("R/L", "L/R"):
    n_ins = sum(i["direction"] == direction for i in inscriptions)
    n_lines = sum(len(physical_lines(i)) for i in inscriptions
                  if i["direction"] == direction)
    n_distinct = len(direction_texts(direction))
    print(f"  {direction}: {n_ins} inscriptions, {n_lines} lines, "
          f"{n_distinct} distinct sequences")

print("\n=== endpoint test under the old normalization ===")
print("  subset sign  texts  starts   ends   E under within-text shuffle  z start   z end")
for direction in ("R/L", "L/R"):
    texts = direction_texts(direction)
    for g in (740, 520, 400):
        r = endpoint_stats(texts, g)
        print(f"  {direction:>4} {g:>4} {r['n']:>6} {r['start']:>7} {r['end']:>6} "
              f"{r['expected']:>29.1f} {r['z_start']:>8.2f} {r['z_end']:>7.2f}")

print("\n=== L/R after reversing those rows ===")
print("  sign  texts  starts   ends   end share   z end")
for g in (740, 520, 400):
    r = endpoint_stats(direction_texts("L/R", corrected=True), g)
    print(f"  {g:>4} {r['n']:>6} {r['start']:>7} {r['end']:>6} "
          f"{r['end']/r['n']:>10.1%} {r['z_end']:>7.2f}")


def combined_rows(corrected):
    rows = []
    for ins in inscriptions:
        for raw in physical_lines(ins):
            text = transform(raw, ins["direction"], corrected)
            if len(text) >= 2:
                rows.append({"text": text, "site": ins.get("site"),
                             "object": ins.get("obj_class")})
    return rows


def dedup(rows, key):
    out, seen = [], set()
    for row in rows:
        k = key(row)
        if k not in seen:
            seen.add(k)
            out.append(row)
    return out


def mh(rows, stratum):
    groups = defaultdict(list)
    for row in rows:
        groups[stratum(row)].append(set(row["text"]))
    num = den = observed = expected = 0.0
    for texts in groups.values():
        n = len(texts)
        a = sum(740 in text for text in texts)
        b = sum(520 in text for text in texts)
        if n < 2 or not a or not b or a == n or b == n:
            continue
        both = sum(740 in text and 520 in text for text in texts)
        e = a * b / n
        v = a * b * (n - a) * (n - b) / (n * n * (n - 1))
        observed += both
        expected += e
        num += both - e
        den += v
    return observed, expected, num / math.sqrt(den)


print("\n=== effect on the 740/520 headline and combined terminal rates ===")
print("  order       texts   740 end/n/z-shuffle   520 end/n/z-shuffle   "
      "740/520 obs/E/z|length  z|site z|object")
for label, corrected in (("old", False), ("corrected", True)):
    rows = combined_rows(corrected)
    seq_site = dedup(rows, lambda r: (r["text"], r["site"]))
    seq_obj = dedup(rows, lambda r: (r["text"], r["object"]))
    texts = [r["text"] for r in seq_site]
    a = endpoint_stats(texts, 740)
    b = endpoint_stats(texts, 520)
    le = mh(seq_site, lambda r: len(r["text"]))
    si = mh(seq_site, lambda r: r["site"])
    ob = mh(seq_obj, lambda r: r["object"])
    print(f"  {label:<9} {len(texts):>5}   {a['end']:>3}/{a['n']:<3}/{a['z_end']:>5.1f}"
          f"          {b['end']:>3}/{b['n']:<3}/{b['z_end']:>5.1f}"
          f"           {le[0]:.0f}/{le[1]:.1f}/{le[2]:.3f}"
          f"       {si[2]:>6.3f} {ob[2]:>8.3f}")

print("\nVerdict: reverse the L/R rows.  Pairwise exclusion is nearly invariant")
print("because reversal preserves membership and length; the small change comes")
print("only from re-deduplicating sequences after their order is corrected.")
