"""Do multi-numeral texts repeat [numeral][sign] or [sign][numeral] units?

Numeral tokens can be adjacent because additive quantities use runs of numeral
signs.  The fair unit is therefore a numeral *run* plus one neighboring
non-numeral sign.  A repeated-unit template predicts:

  * consecutive numeral runs have exactly one non-numeral sign between them;
  * every run can be paired on the same side, producing an alternating span;
  * intervening signs belong to a post-numeral vocabulary learned on the
    disjoint set of texts with exactly one numeral token;
  * paired signs do not repeat within a text.

The main null shuffles each absolute slot across texts of the same length, site,
and object class.  It preserves the complete positional marginals and both
metadata controls while breaking sequences.  The repeated-sign check instead
shuffles within each text, preserving the corpus's strong no-repeat pattern.
"""
import json
from collections import Counter, defaultdict

import numpy as np

N_PERM = 2500
RNG = np.random.default_rng(29)
NUMERALS = (set(range(1, 8)) | {31, 32, 33, 34, 35, 36} |
            set(range(12, 20)))

inscriptions = json.load(open("data/parsed/inscriptions.json"))
allograph = json.load(open("data/parsed/allograph_map.json"))["map"]
merge = {int(k): v for k, v in allograph.items()}


def inscription_lines(ins):
    out, current = [], []
    for g in ins["glyphs"] + [0]:
        if g == 0:
            if current:
                out.append(tuple(merge.get(x, x) for x in current[::-1]))
                current = []
        else:
            current.append(g)
    return out


recs, seen = [], set()
for ins in inscriptions:
    for text in inscription_lines(ins):
        key = (text, ins.get("site"))
        if key in seen:
            continue
        seen.add(key)
        recs.append({"text": text, "site": ins.get("site"),
                     "object": ins.get("obj_class")})


def runs(text):
    """Inclusive (start,end) positions of maximal numeral runs."""
    out = []
    i = 0
    while i < len(text):
        if text[i] not in NUMERALS:
            i += 1
            continue
        j = i
        while j + 1 < len(text) and text[j + 1] in NUMERALS:
            j += 1
        out.append((i, j))
        i = j + 1
    return out


# Independent training vocabulary: no multi-numeral test text contributes.
training_side = defaultdict(Counter)
for rec in recs:
    text = rec["text"]
    if sum(g in NUMERALS for g in text) != 1:
        continue
    for a, b in zip(text, text[1:]):
        if a in NUMERALS and b not in NUMERALS:
            training_side[b]["left"] += 1
        if a not in NUMERALS and b in NUMERALS:
            training_side[a]["right"] += 1
POST = {g for g, counts in training_side.items()
        if sum(counts.values()) >= 5 and
        counts["left"] / sum(counts.values()) >= .70}

print("=== independent post-numeral vocabulary ===")
print(f"  learned only on texts with exactly one numeral token")
print(f"  rule: >=5 adjacencies and >=70% [numeral, sign]")
print(f"  {len(POST)} signs: " + " ".join(map(str, sorted(POST))))


def raw_counts(records):
    multi = [r["text"] for r in records
             if sum(g in NUMERALS for g in r["text"]) >= 2]
    token_count = Counter(sum(g in NUMERALS for g in text) for text in multi)
    run_count = Counter(len(runs(text)) for text in multi)
    token_gaps = Counter()
    run_gaps = Counter()
    between = []
    multi_run = []
    forward_eligible = forward_repeat = 0
    reverse_eligible = reverse_repeat = 0
    forward_exact = reverse_exact = either_exact = all_gap_one = 0

    for text in multi:
        positions = [i for i, g in enumerate(text) if g in NUMERALS]
        token_gaps.update(b - a - 1 for a, b in zip(positions, positions[1:]))
        rr = runs(text)
        if len(rr) < 2:
            continue
        multi_run.append(text)
        gaps = []
        for (_, end), (start, _) in zip(rr, rr[1:]):
            gap = start - end - 1
            gaps.append(gap)
            run_gaps[gap] += 1
            between.extend(text[end + 1:start])
        gap_one = all(gap == 1 for gap in gaps)
        all_gap_one += gap_one

        after = [text[end + 1] for _, end in rr
                 if end + 1 < len(text) and text[end + 1] not in NUMERALS]
        before = [text[start - 1] for start, _ in rr
                  if start > 0 and text[start - 1] not in NUMERALS]
        f_eligible = len(after) == len(rr)
        r_eligible = len(before) == len(rr)
        forward_eligible += f_eligible
        reverse_eligible += r_eligible
        forward_repeat += f_eligible and len(after) != len(set(after))
        reverse_repeat += r_eligible and len(before) != len(set(before))
        f_exact = gap_one and f_eligible
        r_exact = gap_one and r_eligible
        forward_exact += f_exact
        reverse_exact += r_exact
        either_exact += f_exact or r_exact

    return {
        "multi_texts": len(multi), "token_count": token_count,
        "run_count": run_count, "token_gaps": token_gaps,
        "run_gaps": run_gaps, "multi_run_texts": len(multi_run),
        "between_n": len(between), "between_post": sum(g in POST for g in between),
        "all_gap_one": all_gap_one, "forward_exact": forward_exact,
        "reverse_exact": reverse_exact, "either_exact": either_exact,
        "forward_eligible": forward_eligible, "forward_repeat": forward_repeat,
        "reverse_eligible": reverse_eligible, "reverse_repeat": reverse_repeat,
    }


def metric_vector(records):
    c = raw_counts(records)
    token_pairs = sum(c["token_gaps"].values())
    run_pairs = sum(c["run_gaps"].values())
    nr = c["multi_run_texts"]
    return np.asarray([
        c["multi_texts"], c["multi_run_texts"],
        c["token_gaps"][0] / token_pairs if token_pairs else 0,
        c["run_gaps"][1] / run_pairs if run_pairs else 0,
        c["all_gap_one"] / nr if nr else 0,
        c["forward_exact"] / nr if nr else 0,
        c["reverse_exact"] / nr if nr else 0,
        c["either_exact"] / nr if nr else 0,
        c["between_post"] / c["between_n"] if c["between_n"] else 0,
    ])


observed_counts = raw_counts(recs)
observed = metric_vector(recs)

print("\n=== what the multi-numeral texts contain ===")
print(f"  texts with >=2 numeral tokens: {observed_counts['multi_texts']}")
print("  numeral tokens per text: " +
      ", ".join(f"{k}:{v}" for k, v in sorted(observed_counts["token_count"].items())))
print("  numeral runs per text: " +
      ", ".join(f"{k}:{v}" for k, v in sorted(observed_counts["run_count"].items())))
print("  gaps between consecutive numeral tokens (# non-numerals): " +
      ", ".join(f"{k}:{v}" for k, v in sorted(observed_counts["token_gaps"].items())))
print("  gaps between distinct numeral runs (# non-numerals): " +
      ", ".join(f"{k}:{v}" for k, v in sorted(observed_counts["run_gaps"].items())))


# Exact-position + site + object shuffle.  For every length/site/object group,
# independently permute each absolute column across texts.
groups = defaultdict(list)
for i, rec in enumerate(recs):
    groups[(len(rec["text"]), rec["site"], rec["object"])].append(i)
shuffle_groups = [(length, np.asarray(indices, dtype=int))
                  for (length, _site, _obj), indices in groups.items()
                  if len(indices) > 1]


def positional_corpus():
    texts = [list(rec["text"]) for rec in recs]
    for length, indices in shuffle_groups:
        for position in range(length):
            values = np.asarray([texts[i][position] for i in indices])
            values = RNG.permutation(values)
            for i, value in zip(indices, values):
                texts[i][position] = int(value)
    return [{**rec, "text": tuple(texts[i])} for i, rec in enumerate(recs)]


null = np.empty((N_PERM, len(observed)), dtype=float)
for run in range(N_PERM):
    null[run] = metric_vector(positional_corpus())

labels = [
    ("texts with >=2 numeral tokens", 0, "descriptive"),
    ("texts with >=2 numeral runs", 1, "descriptive"),
    ("adjacent share of token gaps", 2, "descriptive"),
    ("one-sign share of inter-run gaps", 3, "higher"),
    ("multi-run texts with every gap=1", 4, "higher"),
    ("complete [num-run, sign] spans", 5, "higher"),
    ("complete [sign, num-run] spans", 6, "higher"),
    ("complete spans in either direction", 7, "higher"),
    ("intervening tokens in POST vocab", 8, "higher"),
]

print("\n=== sequence tests against exact-position/site/object null ===")
print("  measure                              observed   null mean    null 95%       z    p low/high")
for label, col, prediction in labels:
    values = null[:, col]
    obs = observed[col]
    sd = values.std(ddof=1)
    z = (obs - values.mean()) / sd if sd else float("nan")
    p_low = (1 + np.sum(values <= obs)) / (N_PERM + 1)
    p_high = (1 + np.sum(values >= obs)) / (N_PERM + 1)
    lo, hi = np.quantile(values, [.025, .975])
    if col < 2:
        print(f"  {label:<37} {obs:>7.0f} {values.mean():>11.1f} "
              f"{lo:>7.1f}-{hi:<7.1f} {z:>6.2f} {p_low:.4f}/{p_high:.4f}")
    else:
        print(f"  {label:<37} {obs:>7.1%} {values.mean():>11.1%} "
              f"{lo:>7.1%}-{hi:<7.1%} {z:>6.2f} {p_low:.4f}/{p_high:.4f}")


# Repeated targets require repeated sign tokens.  A within-text shuffle is the
# relevant control because it preserves that no-repeat fact exactly, along with
# site, object, length, and each text's complete vocabulary.
def repeat_vector(texts):
    forward_eligible = forward_repeat = reverse_eligible = reverse_repeat = 0
    for text in texts:
        rr = runs(text)
        if len(rr) < 2:
            continue
        after = [text[end + 1] for _, end in rr
                 if end + 1 < len(text) and text[end + 1] not in NUMERALS]
        before = [text[start - 1] for start, _ in rr
                  if start > 0 and text[start - 1] not in NUMERALS]
        f_eligible = len(after) == len(rr)
        r_eligible = len(before) == len(rr)
        forward_eligible += f_eligible
        reverse_eligible += r_eligible
        forward_repeat += f_eligible and len(after) != len(set(after))
        reverse_repeat += r_eligible and len(before) != len(set(before))
    return np.asarray([forward_eligible, forward_repeat,
                       reverse_eligible, reverse_repeat], dtype=float)


multi_texts = [rec["text"] for rec in recs
               if sum(g in NUMERALS for g in rec["text"]) >= 2]
repeat_observed = repeat_vector(multi_texts)
repeat_null = np.empty((N_PERM, 4), dtype=float)
for run in range(N_PERM):
    shuffled = [tuple(int(x) for x in RNG.permutation(text))
                for text in multi_texts]
    repeat_null[run] = repeat_vector(shuffled)

print("\n=== does the same paired sign recur? no-repeat-preserving null ===")
print("  orientation   eligible texts  repeated target   null mean   null 95%   lower/upper p")
for label, e_col, r_col in (("[run, sign]", 0, 1), ("[sign, run]", 2, 3)):
    values = repeat_null[:, r_col]
    obs = repeat_observed[r_col]
    lo, hi = np.quantile(values, [.025, .975])
    p_low = (1 + np.sum(values <= obs)) / (N_PERM + 1)
    p_high = (1 + np.sum(values >= obs)) / (N_PERM + 1)
    print(f"  {label:<13} {repeat_observed[e_col]:>14.0f} {obs:>16.0f} "
          f"{values.mean():>11.2f} {lo:>5.0f}-{hi:<5.0f} "
          f"{p_low:.4f}/{p_high:.4f}")

print("\nPrediction directions for gap=1, complete spans, POST vocabulary, and")
print("non-repetition are all fixed before looking at the null.  The note reports")
print("that every sequence prediction is null or goes significantly backward.")
