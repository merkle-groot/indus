"""Validate the visual groups produced by :mod:`shapes`.

All corpus statistics use distinct sign sequences.  The script scores exact
allograph groups against Parpola, supplies a label-permutation null, compares
position/context/co-occurrence against frequency-matched non-group pairs, and
adds the results to ``data/parsed/shape_families.json``.
"""

from __future__ import annotations

import json
import math
from collections import Counter, defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import adjusted_rand_score

import shapes


ROOT = Path(__file__).resolve().parents[1]
CROSSWALK_PATH = ROOT / "data/parsed/crosswalk.json"
DISAGREE_PATH = ROOT / "notes/shape-disagreements.png"
DISTRIBUTION_PATH = ROOT / "notes/shape-distance-distribution.png"
RNG_SEED = 1379
N_PERM = 5000


def pair_set(groups, key="members"):
    out = set()
    for group in groups:
        members = group[key]
        if members and isinstance(members[0], dict):
            members = [m["id"] for m in members]
        for i, a in enumerate(members):
            for b in members[i + 1:]:
                out.add(tuple(sorted((int(a), int(b)))))
    return out


def parpola_validation(out, rasters, pair):
    cw = json.loads(CROSSWALK_PATH.read_text())
    y2p = {int(k): v for k, v in cw["y2p"].items()}
    renderable = set(map(int, rasters["ids"]))
    universe = sorted(renderable & set(y2p))
    visual_pairs_all = pair_set(out["allograph_sets"])
    visual_pairs = {p for p in visual_pairs_all if p[0] in universe and p[1] in universe}
    true_pairs = {(a, b) for i, a in enumerate(universe) for b in universe[i + 1:]
                  if y2p[a] == y2p[b]}
    tp = visual_pairs & true_pairs
    fp = visual_pairs - true_pairs
    fn = true_pairs - visual_pairs
    precision = len(tp) / len(visual_pairs) if visual_pairs else None
    recall = len(tp) / len(true_pairs) if true_pairs else None

    visual_label = {}
    for gi, group in enumerate(out["allograph_sets"]):
        for gid in group["members"]:
            visual_label[gid] = f"A{gi}"
    pred = [visual_label.get(g, f"singleton-{g}") for g in universe]
    truth = [y2p[g] for g in universe]
    ari = adjusted_rand_score(truth, pred)

    rng = np.random.default_rng(RNG_SEED)
    perm_ari = np.empty(N_PERM)
    perm_tp = np.empty(N_PERM, dtype=int)
    truth_arr = np.asarray(truth, dtype=object)
    pred_arr = np.asarray(pred, dtype=object)
    pred_pair_indices = [(universe.index(a), universe.index(b)) for a, b in visual_pairs]
    for k in range(N_PERM):
        shuffled = rng.permutation(truth_arr)
        perm_ari[k] = adjusted_rand_score(shuffled, pred_arr)
        perm_tp[k] = sum(shuffled[i] == shuffled[j] for i, j in pred_pair_indices)
    null = {
        "method": "permute Parpola labels over mapped renderable ids; cluster sizes preserved",
        "permutations": N_PERM,
        "observed_ari": float(ari),
        "null_ari_mean": float(perm_ari.mean()),
        "null_ari_95pct": [float(x) for x in np.quantile(perm_ari, [.025, .975])],
        "ari_p_upper": float((1 + np.sum(perm_ari >= ari)) / (N_PERM + 1)),
        "observed_matching_pairs": len(tp),
        "null_matching_pairs_mean": float(perm_tp.mean()),
        "null_matching_pairs_95pct": [float(x) for x in np.quantile(perm_tp, [.025, .975])],
        "matching_pairs_p_upper": float((1 + np.sum(perm_tp >= len(tp))) / (N_PERM + 1)),
    }
    idx = {int(g): i for i, g in enumerate(rasters["ids"])}
    def disagreement_record(p, kind):
        a, b = p
        i, j = idx[a], idx[b]
        return {
            "a": a, "b": b, "parpola_a": y2p[a], "parpola_b": y2p[b],
            "kind": kind,
            **shapes.score_pair(i, j, pair),
        }
    # Most visually similar expert merges first; visually merged disagreements
    # are exact ties and sort by id for determinism.
    false_negative = sorted((disagreement_record(p, "Parpola merges; visual separates")
                             for p in fn), key=lambda x: (-x["dice_aspect"], x["a"], x["b"]))
    false_positive = sorted((disagreement_record(p, "visual merges; Parpola separates")
                             for p in fp), key=lambda x: (x["a"], x["b"]))
    return {
        "universe_mapped_renderable_ids": len(universe),
        "parpola_same_pairs": len(true_pairs),
        "visual_same_pairs_in_universe": len(visual_pairs),
        "true_positive_pairs": len(tp),
        "false_positive_pairs": len(fp),
        "false_negative_pairs": len(fn),
        "pair_precision": precision,
        "pair_recall": recall,
        "adjusted_rand": float(ari),
        "false_negatives": false_negative,
        "false_positives": false_positive,
        "null": null,
    }


def render_disagreements(validation, rasters):
    idx = {int(g): i for i, g in enumerate(rasters["ids"])}
    # Show every disagreement while keeping the sheet at a readable width.
    rows = validation["false_negatives"] + validation["false_positives"]
    if not rows:
        return
    fig, axes = plt.subplots(len(rows), 2, figsize=(4.2, max(3, len(rows) * 1.05)),
                             squeeze=False)
    for y, rec in enumerate(rows):
        for x, key in enumerate(("a", "b")):
            gid = rec[key]
            ax = axes[y, x]
            ax.imshow(rasters["aspect"][idx[gid]], cmap="gray_r", vmin=0, vmax=1)
            ax.axis("off")
            ax.set_title(f"{gid} / {rec['parpola_' + key]}", fontsize=8)
        axes[y, 0].set_ylabel("P+ V−" if rec["kind"].startswith("Parpola") else "P− V+",
                             fontsize=7)
    fig.suptitle("Parpola/visual allograph disagreements\nP+ V−: expert merge missed; P− V+: visual merge rejected")
    fig.tight_layout(rect=(0, 0, 1, .99))
    fig.savefig(DISAGREE_PATH, dpi=180, bbox_inches="tight")
    plt.close(fig)


def profile_matrices(ids, distinct_texts):
    idx = {g: i for i, g in enumerate(ids)}
    n = len(ids)
    pos = np.zeros((n, 3), float)
    context = np.zeros((n, 2 * n), float)
    presence = np.zeros((n, len(distinct_texts)), np.float32)
    freq = np.zeros(n, float)
    text_freq = np.zeros(n, float)
    for ti, text in enumerate(distinct_texts):
        seen = set()
        for k, gid in enumerate(text):
            if gid not in idx:
                continue
            i = idx[gid]
            freq[i] += 1
            seen.add(i)
            if len(text) == 1:
                pos[i, 0] += .5
                pos[i, 2] += .5
            elif k == 0:
                pos[i, 0] += 1
            elif k == len(text) - 1:
                pos[i, 2] += 1
            else:
                pos[i, 1] += 1
            if k and text[k - 1] in idx:
                context[i, idx[text[k - 1]]] += 1
            if k + 1 < len(text) and text[k + 1] in idx:
                context[i, n + idx[text[k + 1]]] += 1
        for i in seen:
            presence[i, ti] = 1
            text_freq[i] += 1
    def cosine_matrix(x):
        norm = np.linalg.norm(x, axis=1)
        return (x @ x.T) / (norm[:, None] * norm[None, :] + 1e-12)
    return {
        "position": cosine_matrix(pos),
        "context": cosine_matrix(context),
        "cooccur_count": presence @ presence.T,
        "cooccur_rate": (presence @ presence.T) /
            (np.minimum(text_freq[:, None], text_freq[None, :]) + 1e-12),
        "freq": freq,
        "text_freq": text_freq,
    }


def target_pairs(out, kind):
    if kind == "allographs":
        return sorted(pair_set(out["allograph_sets"]))
    return sorted(tuple(sorted((f["base"], m["id"])))
                  for f in out["derivational_families"] for m in f["members"])


def matched_distribution_test(out, rasters, distinct_texts, kind):
    ids = list(map(int, rasters["ids"]))
    idx = {g: i for i, g in enumerate(ids)}
    prof = profile_matrices(ids, distinct_texts)
    targets = [p for p in target_pairs(out, kind) if p[0] in idx and p[1] in idx]
    target_idx = [(idx[a], idx[b]) for a, b in targets]
    excluded = set(targets)
    candidates = [(i, j) for i in range(len(ids)) for j in range(i + 1, len(ids))
                  if (ids[i], ids[j]) not in excluded and prof["freq"][i] and prof["freq"][j]]
    ci = np.asarray([p[0] for p in candidates], dtype=int)
    cj = np.asarray([p[1] for p in candidates], dtype=int)
    clog_lo = np.minimum(np.log1p(prof["freq"][ci]), np.log1p(prof["freq"][cj]))
    clog_hi = np.maximum(np.log1p(prof["freq"][ci]), np.log1p(prof["freq"][cj]))
    rng = np.random.default_rng(RNG_SEED + (0 if kind == "allographs" else 1))
    pools = []
    for i, j in target_idx:
        lo, hi = sorted((math.log1p(prof["freq"][i]), math.log1p(prof["freq"][j])))
        distance = np.abs(clog_lo - lo) + np.abs(clog_hi - hi)
        # Independent controls: neither target sign may appear in its control.
        valid = (ci != i) & (ci != j) & (cj != i) & (cj != j)
        take_n = min(100, int(valid.sum()))
        selection = np.flatnonzero(valid)[np.argpartition(distance[valid], take_n - 1)[:take_n]]
        pools.append(selection)

    metrics = {
        "position_cosine": prof["position"],
        "neighbour_cosine": prof["context"],
        "cooccur_rate": prof["cooccur_rate"],
    }
    result = {
        "distinct_texts": len(distinct_texts),
        "pairs": len(targets),
        "frequency_measure": "occurrences in distinct texts",
        "matching": "100 nearest non-group pairs by the two endpoint log-frequencies; target signs excluded",
        "prediction": ("allographs should have higher position/neighbour similarity and lower co-occurrence"
                       if kind == "allographs" else
                       "no interchangeability prediction; modifier may change distribution"),
        "metrics": {},
    }
    for name, matrix in metrics.items():
        observed_values = np.asarray([matrix[i, j] for i, j in target_idx], float)
        null = np.empty(N_PERM)
        for k in range(N_PERM):
            chosen = [pool[rng.integers(len(pool))] for pool in pools]
            null[k] = np.mean([matrix[ci[q], cj[q]] for q in chosen])
        obs = float(observed_values.mean()) if len(observed_values) else None
        if obs is None:
            continue
        upper = (1 + np.sum(null >= obs)) / (N_PERM + 1)
        lower = (1 + np.sum(null <= obs)) / (N_PERM + 1)
        result["metrics"][name] = {
            "observed_mean": obs,
            "matched_null_mean": float(null.mean()),
            "matched_null_95pct": [float(x) for x in np.quantile(null, [.025, .975])],
            "p_upper": float(upper),
            "p_lower": float(lower),
            "p_two_sided": float(min(1, 2 * min(upper, lower))),
        }
    co_counts = [prof["cooccur_count"][i, j] for i, j in target_idx]
    result["cooccurrence"] = {
        "pairs_ever_cooccurring": int(sum(x > 0 for x in co_counts)),
        "pairs_never_cooccurring": int(sum(x == 0 for x in co_counts)),
        "total_distinct_text_cooccurrences": int(sum(co_counts)),
    }
    return result


def adjacency_comparison(out, freq):
    ids = sorted(freq)
    nums = set(range(1, 8)) | set(range(12, 20)) | set(range(31, 36))
    proposed = set(target_pairs(out, "derivational"))
    result = {}
    for gap in (2, 5):
        groups, cur = [], [ids[0]]
        for a, b in zip(ids, ids[1:]):
            if b - a <= gap:
                cur.append(b)
            else:
                groups.append(cur); cur = [b]
        groups.append(cur)
        if gap == 2:
            # Match src/modifiers.py's one manual repair exactly.
            fish = set(range(219, 245))
            hit = [g for g in groups if set(g) & fish]
            if len(hit) > 1:
                merged = sorted({x for g in hit for x in g})
                groups = [g for g in groups if g not in hit] + [merged]
        groups = [g for g in groups if len(g) > 1 and not set(g) & nums]
        old_pairs = pair_set([{"members": g} for g in groups])
        result[f"gap_{gap}"] = {
            "families": len(groups),
            "within_family_pairs": len(old_pairs),
            "proposed_derivational_pairs_also_within_old_family": len(proposed & old_pairs),
            "share_of_proposed_pairs": len(proposed & old_pairs) / len(proposed) if proposed else None,
            "share_of_old_pairs_recovered": len(proposed & old_pairs) / len(old_pairs) if old_pairs else None,
        }
    return result


def plot_score_distributions(out, pair):
    dice_distance = 1 - pair["aspect_dice"]
    nn_d = np.partition(dice_distance + np.eye(len(dice_distance)) * 10, 0, axis=1)[:, 0]
    c1, c2 = pair["aspect_contain"], pair["aspect_contain_reverse"]
    high = np.maximum(c1, c2).copy(); np.fill_diagonal(high, 0)
    nn_c = high.max(axis=1)
    tri = np.triu_indices(len(high), 1)
    contain_cut = out["method"]["derivational_cut"]["containment"]["cut"]
    coverage = np.minimum(c1, c2)[tri][np.maximum(c1, c2)[tri] >= contain_cut]
    fig, axes = plt.subplots(1, 3, figsize=(12, 3.3))
    axes[0].hist(nn_d, bins=45, color="#4C78A8")
    axes[0].axvline(out["method"]["allograph_cut"]["cut"], color="#D62728")
    axes[0].set(title="Nearest-neighbour Dice distance", xlabel="1 − aligned Dice")
    axes[1].hist(nn_c, bins=45, color="#59A14F")
    axes[1].axvline(contain_cut, color="#D62728")
    axes[1].set(title="Best directional containment", xlabel="fraction contained")
    axes[2].hist(coverage, bins=35, color="#F28E2B")
    axes[2].axvline(out["method"]["derivational_cut"]["larger_sign_coverage"]["cut"],
                    color="#D62728")
    axes[2].set(title="Larger-sign coverage in tail", xlabel="reverse containment")
    for ax in axes: ax.set_ylabel("signs / pairs")
    fig.tight_layout()
    fig.savefig(DISTRIBUTION_PATH, dpi=180, bbox_inches="tight")
    plt.close(fig)


def validate():
    if not shapes.OUT_PATH.exists():
        out = shapes.build()
    else:
        out = json.loads(shapes.OUT_PATH.read_text())
    rasters = shapes.render_all()
    pair = shapes.pairwise(rasters)
    external = parpola_validation(out, rasters, pair)
    render_disagreements(external, rasters)
    # Critical corpus rule: exact sign sequences, not artifact rows.
    distinct_texts = sorted(set(tuple(line["signs"]) for line in rasters["lines"]
                                if line["signs"]))
    distribution = {
        "deduplication": "sorted(set(tuple(line['signs']) for line in lines))",
        "original_lines": len(rasters["lines"]),
        "distinct_texts": len(distinct_texts),
        "allographs": matched_distribution_test(out, rasters, distinct_texts, "allographs"),
        "derivational": matched_distribution_test(out, rasters, distinct_texts, "derivational"),
    }
    out["validation"] = {
        "external_parpola": external,
        "shape_null": external["null"],
        "distributional_distinct_texts": distribution,
        "id_adjacency_comparison": adjacency_comparison(out, rasters["freq"]),
    }
    out["artifacts"]["disagreement_sheet"] = str(DISAGREE_PATH.relative_to(ROOT))
    out["artifacts"]["score_distributions"] = str(DISTRIBUTION_PATH.relative_to(ROOT))
    plot_score_distributions(out, pair)
    shapes.OUT_PATH.write_text(json.dumps(out, indent=2) + "\n")
    return out


def print_summary(out):
    inv = out["inventory"]
    ext = out["validation"]["external_parpola"]
    print("=== shape analysis: validated ===")
    print("wrote:")
    for p in ("src/shapes.py", "src/shapes_validate.py",
              "data/parsed/shape_families.json", "data/parsed/shape_rasters.npz",
              "data/parsed/shape_pairwise.npz", "data/parsed/shape_residuals.npz",
              "notes/shape-families.png", "notes/shape-residuals.png",
              "notes/shape-disagreements.png", "notes/shape-distance-distribution.png"):
        print(f"  {p}")
    print(f"headline: {inv['attested_ids']} attested ids; "
          f"{inv['allograph_reduction']} allograph merges; "
          f"{len(out['derivational_families'])} derivational families")
    print(f"effective inventory before / A / A+B: {inv['attested_ids']} / "
          f"{inv['after_allograph_merges']} / "
          f"{inv['after_collapsing_derivational_families']}")
    print(f"Parpola: precision {ext['pair_precision']:.3f}; recall {ext['pair_recall']:.3f}; "
          f"adjusted Rand {ext['adjusted_rand']:.3f}")


if __name__ == "__main__":
    print_summary(validate())
