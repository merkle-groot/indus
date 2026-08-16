"""Induce sign classes from controlled left/right contexts.

The context matrix is observed minus the exact expectation under independent
column shuffles within length/site/object strata.  Thus terminal position,
site, and object class cannot create a class by themselves.  Signed Pearson
residuals are clipped, row-normalized, reduced by SVD, and clustered by k-means;
k is selected by silhouette without reference to any known sign set.

Evaluation precedes exploration.  Three anchors are frozen in advance:
terminal fillers, established stroke numerals, and the fish family.  A grouping
is recovered only if one cluster has >=70% recall and >=50% precision, its
pair-coassignment exceeds 97.5% of exact-position shuffled corpora, and its
median bootstrap pair stability is >=70%.  Novel cluster membership is printed
only if all three anchors pass.
"""
import argparse
import json
from collections import Counter, defaultdict

import numpy as np
from sklearn.cluster import KMeans
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import normalize

SEED = 32
MIN_TOKENS = 20
SVD_DIMENSIONS = 10
K_GRID = tuple(range(2, 16))
RESIDUAL_CLIP = 5.0

TERMINAL = {740, 520, 390, 151, 527, 617, 156}
NUMERALS = ({1, 2, 3, 4, 5, 6, 7, 13, 14, 15, 16, 17, 18, 19,
             27, 28, 29, 31, 32, 33, 34, 35, 36, 55, 56,
             48, 49, 50, 51, 57})
FISH = {220, 240, 235, 233, 231, 226, 236, 222, 241, 243, 232, 234}
ANCHORS = {"terminal": TERMINAL, "numerals": NUMERALS, "fish": FISH}


def load_records():
    lines = json.load(open("data/parsed/lines_merged.json"))
    inscriptions = json.load(open("data/parsed/inscriptions.json"))
    by_artifact = {i["cisi"] or f"#{i['seal_id']}": i for i in inscriptions}
    records, seen = [], set()
    for line in lines:
        text = tuple(g for g in line["signs"] if g)
        if not text:
            continue
        obj = by_artifact.get(line.get("artifact"), {}).get("obj_class")
        key = (text, line.get("site"), obj)
        if key in seen:
            continue
        seen.add(key)
        records.append({"text": text, "site": line.get("site"), "object": obj})
    return records


def context_residuals(records, eligible, contexts):
    row = {g: i for i, g in enumerate(eligible)}
    col = {g: i for i, g in enumerate(contexts)}
    width = len(contexts)
    observed = np.zeros((len(eligible), 2 * width), float)
    expected = np.zeros_like(observed)

    groups = defaultdict(list)
    for rec in records:
        groups[(len(rec["text"]), rec["site"], rec["object"])].append(rec["text"])

    for (length, _site, _object), texts in groups.items():
        size = len(texts)
        position_counts = [Counter(text[i] for text in texts) for i in range(length)]
        for i in range(length):
            focal = position_counts[i]
            left = Counter({"<BOS>": size}) if i == 0 else position_counts[i - 1]
            right = (Counter({"<EOS>": size}) if i == length - 1
                     else position_counts[i + 1])
            for g, ng in focal.items():
                if g not in row:
                    continue
                r = row[g]
                for neighbor, nn in left.items():
                    expected[r, col[neighbor]] += ng * nn / size
                for neighbor, nn in right.items():
                    expected[r, width + col[neighbor]] += ng * nn / size
        for text in texts:
            for i, g in enumerate(text):
                if g not in row:
                    continue
                left = "<BOS>" if i == 0 else text[i - 1]
                right = "<EOS>" if i == length - 1 else text[i + 1]
                observed[row[g], col[left]] += 1
                observed[row[g], width + col[right]] += 1

    residual = (observed - expected) / np.sqrt(expected + .5)
    residual = np.clip(residual, -RESIDUAL_CLIP, RESIDUAL_CLIP)
    residual = normalize(residual, norm="l2")
    return residual, observed, expected


def cluster_matrix(matrix, seed):
    dimensions = min(SVD_DIMENSIONS, matrix.shape[0] - 2, matrix.shape[1] - 1)
    embedding = TruncatedSVD(n_components=dimensions, random_state=seed).fit_transform(matrix)
    embedding = normalize(embedding, norm="l2")
    rows = []
    models = {}
    for k in K_GRID:
        if k >= len(embedding):
            continue
        model = KMeans(n_clusters=k, random_state=seed, n_init=50).fit(embedding)
        score = silhouette_score(embedding, model.labels_, metric="euclidean")
        rows.append((score, k))
        models[k] = model
    score, chosen_k = max(rows)
    return models[chosen_k].labels_, chosen_k, score, embedding, sorted(rows, reverse=True)


def group_metrics(group, eligible, labels):
    indices = [eligible.index(g) for g in sorted(group & set(eligible))]
    members = len(indices)
    if members < 2:
        return {"members": members, "pair_rate": 0.0, "recall": 0.0,
                "precision": 0.0, "cluster": None, "cluster_size": 0}
    label_counts = Counter(labels[i] for i in indices)
    best_label, overlap = label_counts.most_common(1)[0]
    cluster_size = int(np.sum(labels == best_label))
    best_members = [eligible[i] for i in indices if labels[i] == best_label]
    cluster_members = [eligible[i] for i in range(len(eligible))
                       if labels[i] == best_label]
    pairs = [(a, b) for ii, a in enumerate(indices) for b in indices[ii + 1:]]
    pair_rate = np.mean([labels[a] == labels[b] for a, b in pairs])
    return {"members": members, "pair_rate": float(pair_rate),
            "recall": overlap / members, "precision": overlap / cluster_size,
            "cluster": int(best_label), "cluster_size": cluster_size,
            "overlap": overlap, "best_members": best_members,
            "cluster_members": cluster_members}


def positional_surrogate(records, rng):
    out = [{**rec, "text": list(rec["text"])} for rec in records]
    groups = defaultdict(list)
    for i, rec in enumerate(records):
        groups[(len(rec["text"]), rec["site"], rec["object"])].append(i)
    for (length, _site, _object), indices in groups.items():
        for position in range(length):
            values = rng.permutation([out[i]["text"][position] for i in indices])
            for i, value in zip(indices, values):
                out[i]["text"][position] = int(value)
    for rec in out:
        rec["text"] = tuple(rec["text"])
    return out


def stratified_bootstrap(records, rng):
    groups = defaultdict(list)
    for rec in records:
        groups[(len(rec["text"]), rec["site"], rec["object"])].append(rec)
    out = []
    for group in groups.values():
        draws = rng.integers(0, len(group), size=len(group))
        out.extend(group[i] for i in draws)
    return out


def pair_coassignment(labels, n):
    out = np.zeros((n, n), float)
    for i in range(n):
        out[i] = labels == labels[i]
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--surrogates", type=int, default=100)
    parser.add_argument("--bootstraps", type=int, default=200)
    args = parser.parse_args()
    rng = np.random.default_rng(SEED)
    records = load_records()
    frequency = Counter(g for rec in records for g in rec["text"])
    eligible = sorted(g for g, n in frequency.items() if n >= MIN_TOKENS)
    contexts = sorted(frequency) + ["<BOS>", "<EOS>"]

    print("=== corpus and predeclared evaluation ===")
    print(f"  deduplicated sequence/site/object records: {len(records)}")
    print(f"  signs with >= {MIN_TOKENS} tokens: {len(eligible)} / {len(frequency)}")
    print("  threshold rationale: below 20 tokens, a two-sided context profile has")
    print("  fewer than about 40 observed neighbor events before subdivision")
    print(f"  features: signed residuals from exact length/position/site/object null")
    print(f"  SVD dimensions: {SVD_DIMENSIONS}; k grid: {K_GRID[0]}..{K_GRID[-1]}")
    print("  anchor pass: recall>=.70, precision>=.50, positional-null p<=.05,")
    print("               and median bootstrap within-group pair stability>=.70")
    for name, group in ANCHORS.items():
        included = sorted(group & set(eligible))
        print(f"  {name:<9}: {len(included)} eligible: {' '.join(map(str, included))}")

    matrix, _observed, _expected = context_residuals(records, eligible, contexts)
    labels, chosen_k, silhouette, embedding, grid = cluster_matrix(matrix, SEED)
    metrics = {name: group_metrics(group, eligible, labels)
               for name, group in ANCHORS.items()}
    print("\n=== label-free model selection ===")
    print(f"  chosen k={chosen_k}; silhouette={silhouette:.4f}")
    print("  leading k candidates: " + ", ".join(
        f"k={k}:{score:.4f}" for score, k in grid[:6]))

    null = {name: [] for name in ANCHORS}
    for run in range(args.surrogates):
        surrogate = positional_surrogate(records, rng)
        smatrix, _, _ = context_residuals(surrogate, eligible, contexts)
        slabels, _k, _score, _embedding, _grid = cluster_matrix(smatrix, SEED + run + 1)
        for name, group in ANCHORS.items():
            null[name].append(group_metrics(group, eligible, slabels)["pair_rate"])

    coassign = np.zeros((len(eligible), len(eligible)), float)
    chosen_ks = []
    for run in range(args.bootstraps):
        sample = stratified_bootstrap(records, rng)
        bmatrix, _, _ = context_residuals(sample, eligible, contexts)
        blabels, bk, _score, _embedding, _grid = cluster_matrix(
            bmatrix, SEED + 1000 + run)
        coassign += pair_coassignment(blabels, len(eligible))
        chosen_ks.append(bk)
    coassign /= args.bootstraps

    print("\n=== known-group recovery before exploration ===")
    print("  group      n  best cluster overlap/size  recall precision pair rate  "
          "position-null  p    bootstrap pair median  PASS")
    passed = {}
    for name, group in ANCHORS.items():
        result = metrics[name]
        indices = [eligible.index(g) for g in sorted(group & set(eligible))]
        pairs = [coassign[a, b] for ii, a in enumerate(indices)
                 for b in indices[ii + 1:]]
        bootstrap_median = float(np.median(pairs)) if pairs else 0.0
        values = np.asarray(null[name])
        p = (1 + np.sum(values >= result["pair_rate"])) / (len(values) + 1)
        ok = (result["recall"] >= .70 and result["precision"] >= .50 and
              p <= .05 and bootstrap_median >= .70)
        passed[name] = bool(ok)
        result.update({"position_null_mean": float(values.mean()),
                       "position_null_95": np.quantile(values, [.025, .975]).tolist(),
                       "position_p": float(p),
                       "bootstrap_pair_median": bootstrap_median, "pass": bool(ok)})
        print(f"  {name:<9} {result['members']:>2} "
              f"{result.get('overlap',0):>7}/{result['cluster_size']:<7} "
              f"{result['recall']:>7.1%} {result['precision']:>9.1%} "
              f"{result['pair_rate']:>9.1%} {values.mean():>8.1%} "
              f"{np.quantile(values,.975):>6.1%} {p:>5.3f} "
              f"{bootstrap_median:>20.1%}  {'yes' if ok else 'NO'}")
        print(" " * 13 + "best-cluster known members: " +
              " ".join(map(str, result.get("best_members", []))) +
              "; full cluster: " +
              " ".join(map(str, result.get("cluster_members", []))))

    all_pass = all(passed.values())
    print("\n=== exploration gate ===")
    if all_pass:
        print("  all anchors passed; stable novel clusters may be inspected")
        for cluster in sorted(set(labels)):
            members = [eligible[i] for i in np.flatnonzero(labels == cluster)]
            if len(members) < 3:
                continue
            indices = np.flatnonzero(labels == cluster)
            stability = np.mean([coassign[a, b] for ii, a in enumerate(indices)
                                 for b in indices[ii + 1:]])
            if stability >= .70:
                print(f"  cluster {cluster}: stability {stability:.1%}: " +
                      " ".join(map(str, members)))
    else:
        print("  FAIL: known groupings were not all recovered.")
        print("  No novel cluster memberships are printed or promoted.")
    print(f"  bootstrap selected k: median {np.median(chosen_ks):.1f}, "
          f"95% {np.quantile(chosen_ks,.025):.1f}-{np.quantile(chosen_ks,.975):.1f}")

    result = {
        "seed": SEED, "records": len(records), "inventory": len(frequency),
        "threshold": MIN_TOKENS, "eligible": eligible,
        "svd_dimensions": SVD_DIMENSIONS, "chosen_k": int(chosen_k),
        "silhouette": float(silhouette), "anchors": metrics,
        "all_anchors_pass": all_pass,
        "bootstrap_k": {"median": float(np.median(chosen_ks)),
                         "q025": float(np.quantile(chosen_ks, .025)),
                         "q975": float(np.quantile(chosen_ks, .975))},
    }
    json.dump(result, open("data/parsed/distributional_classes.json", "w"), indent=1)
    print("\nwrote data/parsed/distributional_classes.json")


if __name__ == "__main__":
    main()
