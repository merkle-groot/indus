"""Treat duplicate texts as evidence about production and circulation.

Global exact sequences describe circulation across sites.  The structural
comparison uses the project's analytical deduplication key (text, site,
object): a key with raw multiplicity >1 is locally copied, and each key then
gets one vote.  Label permutations control exact site, object, and—except for
the length outcome—length.
"""
import json
from collections import Counter, defaultdict

import numpy as np
from scipy import stats

SEED = 39
RUNS = 5000
TERMINAL = {740, 520, 390, 151, 527, 617, 156}
OUT = "data/parsed/duplicate_circulation.json"


def load_rows():
    lines = json.load(open("data/parsed/lines_merged.json"))
    inscriptions = json.load(open("data/parsed/inscriptions.json"))
    by_artifact = {i["cisi"] or f"#{i['seal_id']}": i for i in inscriptions}
    rows = []
    for line in lines:
        text = tuple(g for g in line["signs"] if g)
        if not text:
            continue
        meta = by_artifact.get(line.get("artifact"), {})
        rows.append({"text": text, "site": line.get("site") or "unknown",
                     "object": meta.get("obj_class") or "unknown",
                     "artifact": line.get("artifact")})
    return rows


def packed_counter(counter):
    return {str(k): v for k, v in sorted(counter.items(), key=lambda x: str(x[0]))}


def global_sequences(rows):
    grouped = defaultdict(list)
    for row in rows:
        grouped[row["text"]].append(row)
    items = []
    for text, attestations in grouped.items():
        sites = Counter(r["site"] for r in attestations)
        objects = Counter(r["object"] for r in attestations)
        items.append({"text": list(text), "count": len(attestations), "length": len(text),
                      "terminal": text[-1], "sites": packed_counter(sites),
                      "site_count": len(sites), "objects": packed_counter(objects),
                      "object_count": len(objects),
                      "artifacts": len({r["artifact"] for r in attestations})})
    items.sort(key=lambda x: (-x["count"], x["text"]))
    distribution = Counter(x["count"] for x in items)
    repeated = [x for x in items if x["count"] > 1]
    local_excess = sum(sum(max(n-1, 0) for n in map(int, x["sites"].values())) for x in repeated)
    cross_site = sum(x["site_count"] - 1 for x in repeated)
    site_spread = Counter(x["site_count"] for x in repeated)
    by_spread = sorted(repeated, key=lambda x: (-x["site_count"], -x["count"], x["text"]))

    counts = np.asarray([x["count"] for x in items], float)
    lengths = np.asarray([x["length"] for x in items], float)
    rho, p = stats.spearmanr(counts, lengths)
    singleton = [x for x in items if x["count"] == 1]
    copied = repeated
    terminal_single = Counter(x["terminal"] for x in singleton)
    terminal_copy = Counter(x["terminal"] for x in copied)
    return {"sequence_types": len(items), "raw_attestations": len(rows),
            "same_sequence_same_artifact_excess_rows": sum(
                x["count"]-x["artifacts"] for x in items),
            "copy_count_distribution": packed_counter(distribution),
            "singleton_types": len(singleton), "repeated_types": len(copied),
            "excess_attestations": sum(x["count"]-1 for x in repeated),
            "local_excess_attestations": local_excess,
            "cross_site_first_attestations": cross_site,
            "repeated_type_site_spread": packed_counter(site_spread),
            "copy_count_length_spearman": {"rho": float(rho), "p": float(p)},
            "singleton_mean_length": float(np.mean([x["length"] for x in singleton])),
            "repeated_type_mean_length": float(np.mean([x["length"] for x in copied])),
            "singleton_terminal_top": packed_counter(dict(terminal_single.most_common(15))),
            "repeated_terminal_top": packed_counter(dict(terminal_copy.most_common(15))),
            "most_copied": items[:20], "widest_circulation": by_spread[:20]}


def local_units(rows):
    counts = Counter((r["text"], r["site"], r["object"]) for r in rows)
    return [{"text": text, "site": site, "object": obj, "copy_count": count,
             "copied": count > 1, "length": len(text), "terminal": text[-1]}
            for (text, site, obj), count in counts.items()]


def total_variation(labels, units):
    a = Counter(u["terminal"] for u, label in zip(units, labels) if label)
    b = Counter(u["terminal"] for u, label in zip(units, labels) if not label)
    keys = set(a) | set(b)
    na, nb = sum(a.values()), sum(b.values())
    return .5 * sum(abs(a[k]/na - b[k]/nb) for k in keys)


def stat_values(labels, units):
    copied = [u for u, label in zip(units, labels) if label]
    single = [u for u, label in zip(units, labels) if not label]
    copied_vocab = len({g for u in copied for g in u["text"]})
    terminal_rate = np.mean([u["terminal"] in TERMINAL for u in copied])
    singleton_terminal_rate = np.mean([u["terminal"] in TERMINAL for u in single])
    return {"vocabulary": copied_vocab,
            "terminal_rate_difference": terminal_rate-singleton_terminal_rate,
            "terminal_total_variation": total_variation(labels, units)}


def permute_labels(labels, units, fields, rng):
    result = labels.copy()
    groups = defaultdict(list)
    for i, unit in enumerate(units):
        groups[tuple(unit[f] for f in fields)].append(i)
    exchangeable = 0
    for cells in groups.values():
        if len({bool(labels[i]) for i in cells}) > 1:
            exchangeable += len(cells)
        values = labels[cells].copy()
        rng.shuffle(values)
        result[cells] = values
    return result, exchangeable


def interval(values):
    values = np.asarray(values, float)
    return {"mean": float(values.mean()), "lo": float(np.quantile(values,.025)),
            "hi": float(np.quantile(values,.975)), "sd": float(values.std(ddof=1))}


def structural_comparison(units, rng):
    labels = np.asarray([u["copied"] for u in units], bool)
    copied = [u for u in units if u["copied"]]
    single = [u for u in units if not u["copied"]]
    observed_length = np.mean([u["length"] for u in copied])-np.mean([u["length"] for u in single])
    observed = stat_values(labels, units)

    length_null = np.empty(RUNS)
    other_null = {key: np.empty(RUNS) for key in observed}
    exchangeable_length = exchangeable_other = 0
    for run in range(RUNS):
        perm, exchangeable_length = permute_labels(labels, units, ("site", "object"), rng)
        c = [u["length"] for u, label in zip(units, perm) if label]
        s = [u["length"] for u, label in zip(units, perm) if not label]
        length_null[run] = np.mean(c)-np.mean(s)
        perm, exchangeable_other = permute_labels(labels, units, ("site", "object", "length"), rng)
        values = stat_values(perm, units)
        for key in other_null:
            other_null[key][run] = values[key]

    def tested(value, null, tail="two"):
        base = interval(null)
        if tail == "upper":
            p = (1+np.sum(null >= value))/(len(null)+1)
        elif tail == "lower":
            p = (1+np.sum(null <= value))/(len(null)+1)
        else:
            p = min(1.0, 2*min((1+np.sum(null <= value))/(len(null)+1),
                               (1+np.sum(null >= value))/(len(null)+1)))
        return {"observed": float(value), "null": base, "p": float(p)}

    # Per-terminal-sign controlled distributions and BH over sufficiently
    # frequent final signs.
    final_frequency = Counter(u["terminal"] for u in units)
    final_signs = sorted(g for g, n in final_frequency.items() if n >= 20)
    observed_counts = Counter(u["terminal"] for u in copied)
    sign_null = {g: np.empty(RUNS, dtype=np.int16) for g in final_signs}
    for run in range(RUNS):
        perm, _ = permute_labels(labels, units, ("site", "object", "length"), rng)
        counts = Counter(u["terminal"] for u, label in zip(units, perm) if label)
        for g in final_signs:
            sign_null[g][run] = counts[g]
    sign_rows = []
    for g in final_signs:
        obs = observed_counts[g]
        values = sign_null[g]
        lower = (1+np.sum(values <= obs))/(RUNS+1)
        upper = (1+np.sum(values >= obs))/(RUNS+1)
        sign_rows.append({"sign": g, "all_units": final_frequency[g],
                          "copied_units": obs, "null_mean": float(values.mean()),
                          "null_interval": [float(np.quantile(values,.025)),float(np.quantile(values,.975))],
                          "p": float(min(1,2*min(lower,upper)))})
    ordered = sorted(sign_rows, key=lambda x: x["p"])
    discoveries = []
    for rank, row in enumerate(ordered, 1):
        if row["p"] <= .05*rank/len(ordered):
            discoveries = ordered[:rank]

    object_table = []
    for obj in sorted({u["object"] for u in units}):
        rows = [u for u in units if u["object"] == obj]
        cp = [u for u in rows if u["copied"]]
        sg = [u for u in rows if not u["copied"]]
        object_table.append({"object": obj, "units": len(rows), "copied_units": len(cp),
                             "copied_rate": len(cp)/len(rows),
                             "copied_mean_length": float(np.mean([u["length"] for u in cp])) if cp else None,
                             "singleton_mean_length": float(np.mean([u["length"] for u in sg])) if sg else None,
                             "copied_terminal_rate": float(np.mean([u["terminal"] in TERMINAL for u in cp])) if cp else None,
                             "singleton_terminal_rate": float(np.mean([u["terminal"] in TERMINAL for u in sg])) if sg else None})

    return {"units": len(units), "locally_copied_units": len(copied),
            "singleton_units": len(single),
            "raw_attestations_represented": sum(u["copy_count"] for u in units),
            "discarded_copies": sum(u["copy_count"]-1 for u in copied),
            "exchangeable_units_length_control": exchangeable_length,
            "exchangeable_units_full_control": exchangeable_other,
            "descriptive": {"copied_mean_length": float(np.mean([u["length"] for u in copied])),
                            "singleton_mean_length": float(np.mean([u["length"] for u in single])),
                            "copied_vocabulary": observed["vocabulary"],
                            "singleton_vocabulary": len({g for u in single for g in u["text"]}),
                            "copied_terminal_rate": float(np.mean([u["terminal"] in TERMINAL for u in copied])),
                            "singleton_terminal_rate": float(np.mean([u["terminal"] in TERMINAL for u in single]))},
            "controlled": {"length_difference": tested(observed_length, length_null),
                           "copied_vocabulary": tested(observed["vocabulary"], other_null["vocabulary"]),
                           "terminal_rate_difference": tested(observed["terminal_rate_difference"], other_null["terminal_rate_difference"]),
                           "terminal_total_variation": tested(observed["terminal_total_variation"], other_null["terminal_total_variation"], "upper")},
            "terminal_sign_tests": {"tested": len(sign_rows), "bh_discoveries": discoveries,
                                    "all": sorted(sign_rows, key=lambda x: x["sign"])},
            "by_object": object_table}


def main():
    rng = np.random.default_rng(SEED)
    rows = load_rows()
    units = local_units(rows)
    result = {"method": {"seed": SEED, "runs": RUNS,
                         "circulation_unit": "global exact sequence",
                         "structural_unit": "text x site x object",
                         "structural_null": "copy labels shuffled within site x object x length"},
              "global_sequences": global_sequences(rows),
              "local_copy_structure": structural_comparison(units, rng)}
    with open(OUT, "w") as handle:
        json.dump(result, handle, indent=2)
        handle.write("\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
