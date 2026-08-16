"""Evaluate unsupervised boundary detection against frozen epigraphic structure.

Two standard local boundary scores are computed on deduplicated merged texts:

  PMI       low association between adjacent signs => cut
  branching high right entropy of the left sign plus high left entropy of the
            right sign => cut

Both are controlled against an exact positional/site/object null.  Within each
text-length/site/object stratum, columns are permuted independently.  This gives
the expected count of every bigram.  PMI is observed/expected log association;
branching entropy is observed entropy minus the entropy of the expected context
vectors.

Thresholds are label-free: the corpus median boundary-occurrence score, so each
method attempts to cut roughly half of all observed boundaries.  Evaluation is
done before looking at any novel proposal:

  must join: 817+2, 861+2, 840+32
  must cut:  immediately before a terminal filler at the right edge, allowing
             only the known post-terminal 400/90 signs after it
"""
import json
import math
from collections import Counter, defaultdict

import numpy as np
from scipy import stats

FROZEN = {(817, 2), (861, 2), (840, 32)}
TERMINAL = {740, 520, 390, 151, 527, 617, 156, 226}
POST_TERMINAL = {400, 90}
SMOOTH = .5

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

observed = Counter((a, b) for rec in recs
                   for a, b in zip(rec["text"], rec["text"][1:]))

# Expected pair counts under independent column shuffles within every complete
# length/site/object stratum.  This is the exact mean of the permutation null.
groups = defaultdict(list)
for rec in recs:
    groups[(len(rec["text"]), rec["site"], rec["object"])].append(rec["text"])
expected = Counter()
for (length, _site, _object), texts in groups.items():
    size = len(texts)
    for i in range(length - 1):
        left = Counter(text[i] for text in texts)
        right = Counter(text[i + 1] for text in texts)
        for a, na in left.items():
            for b, nb in right.items():
                expected[a, b] += na * nb / size


def contexts(pair_counts):
    right = defaultdict(Counter)
    left = defaultdict(Counter)
    for (a, b), value in pair_counts.items():
        right[a][b] = value
        left[b][a] = value
    return right, left


def entropy(counts):
    total = sum(counts.values())
    if not total:
        return 0.0
    return -sum((value / total) * math.log2(value / total)
                for value in counts.values() if value)


obs_right, obs_left = contexts(observed)
null_right, null_left = contexts(expected)
h_obs_right = {g: entropy(c) for g, c in obs_right.items()}
h_obs_left = {g: entropy(c) for g, c in obs_left.items()}
h_null_right = {g: entropy(c) for g, c in null_right.items()}
h_null_left = {g: entropy(c) for g, c in null_left.items()}


def pmi_join(a, b):
    """Positive means more binding than position/site/object predict."""
    return math.log2((observed[a, b] + SMOOTH) / (expected[a, b] + SMOOTH))


def pmi_cut(a, b):
    return -pmi_join(a, b)


def branch_cut(a, b):
    """Excess two-sided branching entropy; positive favors a boundary."""
    return ((h_obs_right.get(a, 0) - h_null_right.get(a, 0)) +
            (h_obs_left.get(b, 0) - h_null_left.get(b, 0)))


all_boundaries = [(a, b) for rec in recs
                  for a, b in zip(rec["text"], rec["text"][1:])]
pmi_threshold = float(np.median([pmi_cut(a, b) for a, b in all_boundaries]))
branch_threshold = float(np.median([branch_cut(a, b) for a, b in all_boundaries]))


def terminal_boundary(text, i):
    """Boundary i is directly before a terminal filler in its edge context."""
    b = text[i + 1]
    return (b in TERMINAL and
            (i + 1 == len(text) - 1 or
             all(g in POST_TERMINAL for g in text[i + 2:])))


labels = []
for rec in recs:
    text = rec["text"]
    for i, pair in enumerate(zip(text, text[1:])):
        if pair in FROZEN:
            labels.append({"pair": pair, "cut": False})
        if terminal_boundary(text, i):
            labels.append({"pair": pair, "cut": True})


def decision(method, pair):
    if method == "PMI":
        return pmi_cut(*pair) >= pmi_threshold
    if method == "branching":
        return branch_cut(*pair) >= branch_threshold
    return (pmi_cut(*pair) >= pmi_threshold and
            branch_cut(*pair) >= branch_threshold)


def auc(scores, outcomes):
    scores = np.asarray(scores)
    outcomes = np.asarray(outcomes, dtype=bool)
    ranks = stats.rankdata(scores)
    n1, n0 = outcomes.sum(), (~outcomes).sum()
    return (ranks[outcomes].sum() - n1 * (n1 + 1) / 2) / (n1 * n0)


def evaluation(method):
    predictions = [decision(method, row["pair"]) for row in labels]
    truth = [row["cut"] for row in labels]
    tp = sum(p and y for p, y in zip(predictions, truth))
    fp = sum(p and not y for p, y in zip(predictions, truth))
    tn = sum(not p and not y for p, y in zip(predictions, truth))
    fn = sum(not p and y for p, y in zip(predictions, truth))
    if method == "PMI":
        scores = [pmi_cut(*row["pair"]) for row in labels]
    elif method == "branching":
        scores = [branch_cut(*row["pair"]) for row in labels]
    else:
        scores = None
    return {"tp": tp, "fp": fp, "tn": tn, "fn": fn,
            "cut_precision": tp / (tp + fp) if tp + fp else float("nan"),
            "terminal_recall": tp / (tp + fn),
            "join_precision": tn / (tn + fn) if tn + fn else float("nan"),
            "frozen_recall": tn / (tn + fp),
            "auc": auc(scores, truth) if scores is not None else float("nan")}


print("=== corpus, null, and label-free thresholds ===")
print(f"  deduplicated sequence x site texts: {len(recs)}")
print(f"  observed boundary occurrences: {len(all_boundaries)}")
print(f"  observed boundary types: {len(observed)}")
print(f"  PMI cut-score median: {pmi_threshold:.3f}")
print(f"  branching residual median: {branch_threshold:.3f}")
print("  expected pair counts condition on exact length/position/site/object")

print("\n=== must-join ground truth ===")
print("  pair      obs  position/site/object E  PMI join residual  branch residual  PMI  branch")
for pair in sorted(FROZEN):
    print(f"  {pair[0]:>3}+{pair[1]:<3} {observed[pair]:>5} {expected[pair]:>23.1f} "
          f"{pmi_join(*pair):>18.3f} {branch_cut(*pair):>16.3f}  "
          f"{'join' if not decision('PMI',pair) else 'CUT ':>4} "
          f"{'join' if not decision('branching',pair) else 'CUT ':>6}")

frozen_instances = sum(observed[pair] for pair in FROZEN)
terminal_instances = sum(row["cut"] for row in labels)
terminal_types = {row["pair"] for row in labels if row["cut"]}
print(f"\n  labelled occurrences: {frozen_instances} frozen joins, "
      f"{terminal_instances} terminal cuts")
print(f"  terminal boundary types: {len(terminal_types)}")

print("\n=== held-out evaluation before inspecting any proposal ===")
print("  method       frozen types  frozen occurrences  terminal recall  "
      "labelled cut precision  labelled join precision   AUC")
for method in ("PMI", "branching", "consensus"):
    result = evaluation(method)
    protected_types = sum(not decision(method, pair) for pair in FROZEN)
    auc_text = f"{result['auc']:.3f}" if not math.isnan(result["auc"]) else "—"
    print(f"  {method:<11} {protected_types}/3          "
          f"{result['tn']:>3}/{frozen_instances:<3} ({result['frozen_recall']:.1%}) "
          f"{result['terminal_recall']:>14.1%} {result['cut_precision']:>23.1%} "
          f"{result['join_precision']:>23.1%} {auc_text:>6}")

print("\n  Precision is restricted to labelled boundaries: unlabelled corpus")
print("  boundaries are unknown, not silently counted as right or wrong.")
print("\nVerdict: PMI protects all three phrases but misses about a third of the")
print("terminal boundaries. Branching entropy cuts inside 840+32 and also misses")
print("about a third. The segmenter fails its ground truth, so no novel proposed")
print("segments are printed or promoted as findings.")
