"""Round 40: compare the Tamil Nadu graffiti and Indus sign inventories.

Only abundance, catalogue structure, graphical form, and site-stratified depth
are analysed.  The public API has no per-sherd sequences: concordance s1..s6
are graphical constituents of one composite sign, not ordered text tokens.
Consequently no terminal, repeat, co-occurrence, numeral-side, or segmentation
statistic is implemented here.
"""
from __future__ import annotations

import ast
import hashlib
import io
import json
import math
import re
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from scipy import ndimage, optimize, stats

import inventory_estimators as inventory
import shapes


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data/graffiti/raw"
IMAGE_DIR = ROOT / "data/graffiti/images"
CONTROL_ARCHIVE = ROOT / "data/graffiti/control/Pottery_Marks_PDF.zip"
OUT = ROOT / "data/parsed/graffiti_compare.json"
FIGURE = ROOT / "notes/graffiti-shape-control.png"
SEED = 40
RUNS = 1000
SHAPE_BOOT = 5000
UNKNOWN = inventory.UNKNOWN


def load(name):
    return json.loads((RAW / name).read_text())


def api_rows(name):
    value = load(name)
    return value.get("data", []) if isinstance(value, dict) else value


def finite(value):
    if isinstance(value, float) and not np.isfinite(value):
        return None
    if isinstance(value, dict):
        return {str(k): finite(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [finite(x) for x in value]
    if isinstance(value, np.generic):
        return finite(value.item())
    return value


def aggregate_dimension(rows, dimension):
    out = Counter()
    for row in rows:
        for item in row.get("result", {}).get(dimension, []):
            out[str(item["key"]).strip()] += int(item["value"])
    return out


def frequency_summary(freq):
    spectrum = Counter(freq.values())
    return {
        "types": len(freq),
        "tokens": int(sum(freq.values())),
        "hapax": spectrum[1],
        "hapax_rate": spectrum[1] / len(freq),
        "frequency_spectrum": ({str(i): spectrum[i] for i in range(1, 11)} |
                               {">10": sum(v for k, v in spectrum.items() if k > 10)}),
        "top_signs": [{"sign": sign, "tokens": count}
                      for sign, count in freq.most_common(15)],
    }


def abundance_estimators(freq):
    return inventory.estimators(Counter(freq))


def sample_frequency_without_replacement(freq, size, rng):
    labels = np.asarray(list(freq), dtype=object)
    counts = np.asarray([freq[x] for x in labels], dtype=int)
    sample = rng.multivariate_hypergeometric(counts, size)
    return Counter({str(label): int(n) for label, n in zip(labels, sample) if n})


def heaps_from_frequency(freq, rng, runs=500, sample_tokens=None):
    tokens = np.repeat(np.asarray(list(freq), dtype=object), list(freq.values()))
    sample_tokens = len(tokens) if sample_tokens is None else sample_tokens
    if sample_tokens > len(tokens):
        raise ValueError("Heaps sample cannot exceed the available token count")
    fractions = np.asarray([.05, .10, .20, .35, .50, .75, 1.0])
    thresholds = np.maximum(1, np.rint(fractions * sample_tokens).astype(int))
    curves = np.zeros((runs, len(thresholds)), float)
    heaps = np.zeros((runs, 4), float)
    for run in range(runs):
        # A truncated random permutation simultaneously draws the matched
        # sample without replacement and randomizes its accumulation order.
        order = rng.permutation(tokens)[:sample_tokens]
        seen = set()
        j = 0
        for i, token in enumerate(order, 1):
            seen.add(token)
            while j < len(thresholds) and i >= thresholds[j]:
                curves[run, j] = len(seen)
                j += 1
        slope, intercept = np.polyfit(np.log(thresholds), np.log(curves[run]), 1)
        k = float(np.exp(intercept))
        heaps[run] = (k, slope, k * (2 * sample_tokens) ** slope,
                      k * (10 * sample_tokens) ** slope)
    median = np.median(curves, axis=0)
    slope, intercept = np.polyfit(np.log(thresholds), np.log(median), 1)
    k = float(np.exp(intercept))
    return {
        "method": ("sample without replacement to the matched token count, then random "
                   "token order reconstructed from the frequency spectrum"),
        "runs": runs,
        "curve": [{"tokens": int(n), "types_median": float(m),
                   "lo": float(lo), "hi": float(hi)}
                  for n, m, lo, hi in zip(thresholds, median,
                                         np.quantile(curves, .025, axis=0),
                                         np.quantile(curves, .975, axis=0))],
        "beta": float(slope),
        "beta_order_interval": [float(x) for x in np.quantile(heaps[:, 1], [.025, .975])],
        "at_2x_tokens": float(k * (2 * sample_tokens) ** slope),
        "at_2x_order_interval": [float(x) for x in np.quantile(heaps[:, 2], [.025, .975])],
        "at_10x_tokens": float(k * (10 * sample_tokens) ** slope),
    }


def inventory_comparison(graffiti_freq, rng):
    records = inventory.load_records(str(ROOT / "data/parsed/lines_merged.json"))
    indus_records = inventory.handle_unknown(records, "exclude_unknown")
    indus_freq = inventory.abundance(indus_records)
    target = min(sum(graffiti_freq.values()), sum(indus_freq.values()))
    if sum(graffiti_freq.values()) > target:
        draws = [sample_frequency_without_replacement(graffiti_freq, target, rng)
                 for _ in range(500)]
        estimates = [abundance_estimators(x) for x in draws]
        graffiti_matched = {
            key: {"median": float(np.median([x[key] for x in estimates])),
                  "interval": [float(y) for y in np.quantile(
                      [x[key] for x in estimates], [.025, .975])]}
            for key in ("observed", "f1", "f2", "sample_coverage",
                        "good_turing_coverage_total", "chao1", "ace")
        }
    else:
        point = abundance_estimators(graffiti_freq)
        graffiti_matched = {k: {"median": float(point[k]), "interval": None}
                             for k in ("observed", "f1", "f2", "sample_coverage",
                                       "good_turing_coverage_total", "chao1", "ace")}
    indus_point = abundance_estimators(indus_freq)
    return {
        "matched_tokens": target,
        "full": {
            "graffiti": abundance_estimators(graffiti_freq),
            "indus": indus_point,
        },
        "matched": {
            "graffiti": graffiti_matched,
            "indus": {k: {"median": float(indus_point[k]), "interval": None}
                      for k in ("observed", "f1", "f2", "sample_coverage",
                                "good_turing_coverage_total", "chao1", "ace")},
        },
        "heaps_matched": {
            "graffiti": heaps_from_frequency(graffiti_freq, rng,
                                              sample_tokens=target),
            "indus": heaps_from_frequency(indus_freq, rng,
                                           sample_tokens=target),
        },
        "indus_records": len(indus_records),
    }


def gini(values):
    values = np.sort(np.asarray(values, float))
    if len(values) < 2 or values.sum() == 0:
        return 0.0
    raw = np.sum((2 * np.arange(1, len(values) + 1) - len(values) - 1) * values)
    return float((raw / (len(values) * values.sum())) * len(values) / (len(values) - 1))


def branching_structure(rows, rng):
    graffiti = {"variants": Counter(), "composites": Counter()}
    for row in rows:
        sign = str(row["sign"]).strip()
        base = int(sign.split(".", 1)[0])
        if sign.endswith("C"):
            graffiti["composites"][base] += 1
        elif "." in sign:
            graffiti["variants"][base] += 1
    for kind in graffiti:
        for base in range(1, 43):
            graffiti[kind][base] += 0

    modifiers = json.loads((ROOT / "data/parsed/modifiers.json").read_text())
    indus = Counter({int(f["base"]): len(f["variants"]) for f in modifiers})
    gv = np.asarray(list(graffiti["variants"].values()), float)
    gc = np.asarray(list(graffiti["composites"].values()), float)
    iv = np.asarray(list(indus.values()), float)

    # Counts divided by their corpus mean remove the different total inventories.
    ks = stats.ks_2samp(gv / gv.mean(), iv / iv.mean(), alternative="two-sided")
    nboot = 10000
    diff = np.empty(nboot)
    for i in range(nboot):
        diff[i] = (gini(rng.choice(gv, len(gv), replace=True)) -
                   gini(rng.choice(iv, len(iv), replace=True)))
    observed_diff = gini(gv) - gini(iv)
    # Centered bootstrap sign test for a zero difference.
    centered = diff - np.median(diff)
    p_gini = (1 + np.sum(np.abs(centered) >= abs(observed_diff))) / (nboot + 1)
    log_rate_ratio = math.log((gv.sum() / len(gv)) / (iv.sum() / len(iv)))
    se = math.sqrt(1 / gv.sum() + 1 / iv.sum())
    z = log_rate_ratio / se
    return {
        "counts": {
            "graffiti": {"bases": len(gv), "variants": int(gv.sum()),
                         "composites": int(gc.sum())},
            "indus": {"bases": len(iv), "variants": int(iv.sum()),
                      "composites": None,
                      "why_no_composites": (
                          "the Indus catalogue has 44 multi-codepoint renderings, but they are "
                          "not a base-indexed class commensurate with TNSDA graphical composites")},
        },
        "per_base": {
            "graffiti_variants": {str(k): v for k, v in sorted(graffiti["variants"].items())},
            "graffiti_composites": {str(k): v for k, v in sorted(graffiti["composites"].items())},
            "indus_variants": {str(k): v for k, v in sorted(indus.items())},
        },
        "summaries": {
            "graffiti_variants": {"mean": float(gv.mean()), "median": float(np.median(gv)),
                                  "sd": float(gv.std(ddof=1)), "gini": gini(gv),
                                  "max": int(gv.max())},
            "graffiti_composites": {"mean": float(gc.mean()), "median": float(np.median(gc)),
                                    "sd": float(gc.std(ddof=1)), "gini": gini(gc),
                                    "max": int(gc.max())},
            "indus_variants": {"mean": float(iv.mean()), "median": float(np.median(iv)),
                               "sd": float(iv.std(ddof=1)), "gini": gini(iv),
                               "max": int(iv.max())},
        },
        "formal_tests": {
            "variant_rate_ratio_graffiti_over_indus": math.exp(log_rate_ratio),
            "poisson_rate_z": z,
            "poisson_rate_two_sided_p": float(2 * stats.norm.sf(abs(z))),
            "normalized_count_ks_d": float(ks.statistic),
            "normalized_count_ks_p": float(ks.pvalue),
            "gini_difference": observed_diff,
            "gini_bootstrap_interval": [float(x) for x in np.quantile(diff, [.025, .975])],
            "gini_centered_two_sided_p": float(p_gini),
        },
    }


def bh_adjust(records, pkey="p"):
    order = sorted(range(len(records)), key=lambda i: records[i][pkey])
    q = np.ones(len(records))
    running = 1.0
    for rank_index in range(len(order) - 1, -1, -1):
        i = order[rank_index]
        rank = rank_index + 1
        running = min(running, records[i][pkey] * len(order) / rank)
        q[i] = running
    for record, value in zip(records, q):
        record["q_bh"] = float(value)


def g_test(table):
    table = np.asarray(table, float)
    total = table.sum()
    if total == 0:
        return 0.0
    expected = table.sum(1)[:, None] * table.sum(0)[None, :] / total
    good = (table > 0) & (expected > 0)
    return float(2 * np.sum(table[good] * np.log(table[good] / expected[good])))


def weighted_depth_bins(depth_counts):
    total = sum(depth_counts.values())
    cumulative = 0
    result = {}
    for depth, count in sorted(depth_counts.items()):
        percentile = (cumulative + count / 2) / total
        result[depth] = min(2, int(percentile * 3))
        cumulative += count
    return result


def depth_site_arrays():
    sites, failures = [], []
    paths = sorted(RAW.glob("filter-stratum-*.json"))
    level = "site x ware x habitation" if paths else "site"
    if not paths:
        paths = sorted(RAW.glob("filter-site-*.json"))
    for path in paths:
        payload = json.loads(path.read_text())
        applied = payload.get("appliedFilters", {})
        selected = applied.get("site", [])
        site = selected[0] if selected else path.stem
        ware = (applied.get("material") or [None])[0]
        habitat = (applied.get("habitation") or [None])[0]
        stratum = " | ".join(str(x) for x in (site, ware, habitat) if x is not None)
        rows = payload.get("data", [])
        occurrence = sum(int(row["occurrence"]) for row in rows)
        if occurrence == 0:
            failures.append({"stratum": stratum, "reason": "filter returned zero rows"})
            continue
        depth_totals = Counter()
        parsed_rows = []
        invalid = Counter()
        for row in rows:
            sign = str(row["sign"]).strip()
            cells = []
            for item in row.get("result", {}).get("depth", []):
                key = str(item["key"]).strip()
                if re.fullmatch(r"\d+(?:\.\d+)?", key):
                    depth = float(key)
                    count = int(item["value"])
                    cells.append((depth, count))
                    depth_totals[depth] += count
                else:
                    invalid[key] += int(item["value"])
            parsed_rows.append((sign, cells))
        if not depth_totals:
            failures.append({"stratum": stratum, "reason": "no numeric depth",
                             "occurrences": occurrence, "invalid_depth": dict(invalid)})
            continue
        bins = weighted_depth_bins(depth_totals)
        signs = sorted({sign for sign, cells in parsed_rows if cells})
        sign_index = {sign: i for i, sign in enumerate(signs)}
        sign_codes, bin_codes = [], []
        for sign, cells in parsed_rows:
            for depth, count in cells:
                sign_codes.extend([sign_index[sign]] * count)
                bin_codes.extend([bins[depth]] * count)
        sites.append({"site": site, "stratum": stratum, "ware": ware,
                      "habitation": habitat, "stratification_level": level,
                      "sign_names": signs,
                      "sign_codes": np.asarray(sign_codes, dtype=np.int32),
                      "bin_codes": np.asarray(bin_codes, dtype=np.int8),
                      "invalid": dict(invalid), "occurrence": occurrence,
                      "numeric_depth_tokens": len(sign_codes),
                      "unique_depths": len(depth_totals)})
    return sites, failures


def site_table(site, bins=None):
    b = site["bin_codes"] if bins is None else bins
    return np.bincount(site["sign_codes"] * 3 + b,
                       minlength=len(site["sign_names"]) * 3).reshape(-1, 3)


def depth_statistics(sites):
    eligible = [site for site in sites if site["numeric_depth_tokens"] >= 20 and
                len(set(site["bin_codes"])) >= 2]

    def statistics_for(bin_values=None):
        total_g, weighted_j, weight, richness_delta = 0.0, 0.0, 0, 0
        for i, site in enumerate(eligible):
            table = site_table(site, None if bin_values is None else bin_values[i])
            total_g += g_test(table)
            shallow = set(np.flatnonzero(table[:, 0]))
            deep = set(np.flatnonzero(table[:, 2]))
            union = shallow | deep
            jaccard = len(shallow & deep) / len(union) if union else 1.0
            n = int(table[:, [0, 2]].sum())
            weighted_j += n * jaccard
            weight += n
            richness_delta += len(deep) - len(shallow)
        return np.asarray([total_g, weighted_j / weight, richness_delta], float)

    observed = statistics_for()
    rng = np.random.default_rng(SEED + 1)
    null = np.zeros((RUNS, 3), float)
    originals = [site["bin_codes"] for site in eligible]
    for run in range(RUNS):
        shuffled = [rng.permutation(x) for x in originals]
        null[run] = statistics_for(shuffled)

    omnibus = [
        {"name": "g2", "p": float((1 + np.sum(null[:, 0] >= observed[0])) /
                                    (RUNS + 1))},
        {"name": "jaccard", "p": float((1 + np.sum(null[:, 1] <= observed[1])) /
                                         (RUNS + 1))},
        {"name": "richness_delta", "p": float(
            (1 + np.sum(np.abs(null[:, 2] - np.median(null[:, 2])) >=
                        abs(observed[2] - np.median(null[:, 2])))) / (RUNS + 1))},
    ]
    bh_adjust(omnibus)
    omnibus_q = {x["name"]: x["q_bh"] for x in omnibus}

    # Per-sign deep-vs-shallow Cochran-Mantel-Haenszel score tests.
    all_signs = sorted({sign for site in eligible for sign in site["sign_names"]})
    tests = []
    for sign in all_signs:
        numerator = variance = 0.0
        observed_sign = 0
        direction_numer = 0.0
        for site in eligible:
            if sign not in site["sign_names"]:
                continue
            table = site_table(site)
            row = table[site["sign_names"].index(sign), [0, 2]].astype(float)
            col = table[:, [0, 2]].sum(0).astype(float)
            n = col.sum()
            if n <= 1:
                continue
            m1 = row.sum()
            expected_deep = m1 * col[1] / n
            var = m1 * (n - m1) * col[1] * col[0] / (n * n * (n - 1))
            numerator += row[1] - expected_deep
            variance += var
            observed_sign += int(m1)
            direction_numer += row[1] - expected_deep
        if observed_sign >= 20 and variance > 0:
            z = numerator / math.sqrt(variance)
            tests.append({"sign": sign, "shallow_deep_tokens": observed_sign,
                          "z_deeper_positive": float(z),
                          "p": float(2 * stats.norm.sf(abs(z)))})
    bh_adjust(tests)
    selected = sorted([x for x in tests if x["q_bh"] < .05], key=lambda x: x["q_bh"])
    return {
        "method": ("numeric depths converted to weighted within-stratum terciles; depths are "
                   "permuted only within site x ware x habitation; strata require >=20 "
                   "numeric-depth tokens"),
        "eligible_sites": len({x["site"] for x in eligible}),
        "eligible_strata": len(eligible),
        "eligible_site_names": sorted({x["site"] for x in eligible}),
        "eligible_stratum_names": [x["stratum"] for x in eligible],
        "numeric_depth_tokens": sum(x["numeric_depth_tokens"] for x in sites),
        "corpus_tokens": sum(int(x["occurrence"]) for x in api_rows("filter-sign.json")),
        "observed": {"site_stratified_g2": observed[0],
                     "weighted_shallow_deep_jaccard": observed[1],
                     "deep_minus_shallow_richness_sum": int(observed[2])},
        "null": {
            "runs": RUNS,
            "g2_mean": float(null[:, 0].mean()),
            "g2_95pct": [float(x) for x in np.quantile(null[:, 0], [.025, .975])],
            "g2_upper_p": float((1 + np.sum(null[:, 0] >= observed[0])) / (RUNS + 1)),
            "g2_bh_q_across_three_omnibus_readouts": omnibus_q["g2"],
            "jaccard_mean": float(null[:, 1].mean()),
            "jaccard_95pct": [float(x) for x in np.quantile(null[:, 1], [.025, .975])],
            "jaccard_lower_p": float((1 + np.sum(null[:, 1] <= observed[1])) / (RUNS + 1)),
            "jaccard_bh_q_across_three_omnibus_readouts": omnibus_q["jaccard"],
            "richness_delta_95pct": [float(x) for x in np.quantile(null[:, 2], [.025, .975])],
            "richness_delta_two_sided_p": float(
                (1 + np.sum(np.abs(null[:, 2] - np.median(null[:, 2])) >=
                            abs(observed[2] - np.median(null[:, 2])))) / (RUNS + 1)),
            "richness_delta_bh_q_across_three_omnibus_readouts":
                omnibus_q["richness_delta"],
        },
        "sign_tests": {"tested": len(tests), "bh_q_lt_05": len(selected),
                       "selected": selected},
    }


def embedded_json(bundle, variable):
    marker = variable + "=JSON.parse('"
    start = bundle.find(marker) + len(marker)
    end = bundle.find("')", start)
    return json.loads(ast.literal_eval("'" + bundle[start:end] + "'"))


def sequence_audit():
    audit_files = sorted(RAW.glob("audit-filter-*.json"))
    digests = {path.stem: hashlib.sha256(path.read_bytes()).hexdigest()
               for path in audit_files}
    concordance = load("concordance-0001.json")["unique_response"]
    example = next(row for row in concordance if str(row.get("sn", "")).strip() == "1.1C")
    bundle = sorted(RAW.glob("spa-bundle-*.js"))[-1].read_text()
    rmrl_to_tnsda = {int(row["RMRL"]): str(row["TNSDA"])
                     for row in embedded_json(bundle, "Uae")}
    slots = [example.get(f"s{i}") for i in range(1, 7) if example.get(f"s{i}") is not None]
    keys = set()

    def walk(value):
        if isinstance(value, dict):
            keys.update(map(str, value))
            for child in value.values():
                walk(child)
        elif isinstance(value, list):
            for child in value:
                walk(child)
    for name in ("sites.json", "filter-sign.json", "base-sign.json", "options.json",
                 "indus.json", "sign-0001.json", "concordance-0001.json"):
        walk(load(name))
    suspect = sorted(k for k in keys if re.search(
        r"sherd|accession|catalog|artefact|artifact|object|inscription|sequence", k, re.I))
    return {
        "unsupported_groupby_files": len(audit_files),
        "unsupported_groupby_all_byte_identical": len(set(digests.values())) == 1,
        "returned_groupby": sorted({load(path.name).get("groupBy") for path in audit_files}),
        "record_identifier_key_search": suspect,
        "spa_api_endpoints": ["base-sign", "sites", "fields-symbols", "sign/<base>",
                              "concordance", "options", "filter", "indus"],
        "concordance_component_example": {
            "catalogue_sign": str(example["sn"]).strip(),
            "rmrl_slots": slots,
            "slots_mapped_back_to_tnsda_signs": [rmrl_to_tnsda.get(int(x)) for x in slots],
            "position": example["position"],
            "interpretation": "position of queried sign 1 inside composite 39 + 1",
        },
        "conclusion": "no per-sherd sign sequence or accession identifier is exposed",
        "infeasible_tests": ["terminal-slot", "co-occurrence exclusion", "no-repeat",
                             "numeral-side", "segmentation"],
    }


def corpus_description(rows):
    freq = Counter({str(row["sign"]).strip(): int(row["occurrence"]) for row in rows})
    dimensions = {name: aggregate_dimension(rows, name)
                  for name in ("site", "habitation", "material", "depth")}
    site_endpoint = {row["site"]: int(row["occurence"])
                     for row in api_rows("sites.json")}
    site_differences = [
        {"site": site, "filter_total": count,
         "sites_endpoint_total": site_endpoint.get(site),
         "difference": site_endpoint.get(site, 0) - count}
        for site, count in dimensions["site"].items()
        if site_endpoint.get(site) != count
    ]
    indus_records = inventory.handle_unknown(
        inventory.load_records(str(ROOT / "data/parsed/lines_merged.json")),
        "exclude_unknown")
    indus_freq = inventory.abundance(indus_records)
    return {
        "corpus_table": {
            "graffiti": {**frequency_summary(freq), "sites": len(dimensions["site"]),
                         "records": int(sum(freq.values())),
                         "unit": "aggregated graffiti-sign occurrence (normally one sherd-mark)"},
            "indus": {**frequency_summary(indus_freq),
                      "sites": len({x["site"] for x in indus_records}),
                      "records": len(indus_records),
                      "mean_text_length": sum(indus_freq.values()) / len(indus_records),
                      "unit": "deduplicated ordered text"},
        },
        "site": {"totals": dict(dimensions["site"].most_common()),
                 "endpoint_discrepancies": site_differences},
        "habitation": dict(dimensions["habitation"].most_common()),
        "ware": dict(dimensions["material"].most_common()),
        "depth": {"returned_total": sum(dimensions["depth"].values()),
                  "unique_returned_labels": len(dimensions["depth"]),
                  "top_labels": dict(dimensions["depth"].most_common(30)),
                  "options_band_count": len(load("options.json")["options"]["depth"]),
                  "note": ("filter results return raw numeric depths plus Surface/NA, not merely "
                           "the 38 selection bands")},
        "catalogue_categories_current_api": {
            "base": sum(bool(re.fullmatch(r"\d+", sign)) for sign in freq),
            "variant": sum(bool(re.fullmatch(r"\d+\.\d+", sign)) for sign in freq),
            "composite": sum(sign.endswith("C") for sign in freq),
        },
    }, freq


def otsu(values):
    values = np.asarray(values, dtype=np.uint8).ravel()
    hist = np.bincount(values, minlength=256).astype(float)
    weight1 = np.cumsum(hist)
    weight2 = values.size - weight1
    mean1 = np.cumsum(hist * np.arange(256)) / np.maximum(weight1, 1)
    total = np.sum(hist * np.arange(256))
    mean2 = (total - np.cumsum(hist * np.arange(256))) / np.maximum(weight2, 1)
    score = weight1 * weight2 * (mean1 - mean2) ** 2
    return int(np.argmax(score[:-1]))


def raster_to_mask(array):
    array = np.asarray(array)
    if array.ndim == 3 and array.shape[2] == 4 and np.any(array[:, :, 3] < 250):
        alpha = array[:, :, 3]
        threshold = max(8, otsu(alpha))
        mask = alpha > threshold
    else:
        if array.ndim == 3:
            grey = np.asarray(Image.fromarray(array).convert("L"))
        else:
            grey = array.astype(np.uint8)
        border = np.concatenate((grey[0], grey[-1], grey[:, 0], grey[:, -1]))
        background = float(np.median(border))
        contrast = np.abs(grey.astype(float) - background).astype(np.uint8)
        threshold = max(12, otsu(contrast))
        mask = contrast > threshold
    # Remove isolated rendering dust but retain fine one-pixel strokes.
    labels, n = ndimage.label(mask, np.ones((3, 3)))
    if n:
        sizes = np.bincount(labels.ravel())
        keep = sizes >= max(2, int(mask.sum() * .0005))
        keep[0] = False
        mask = keep[labels]
    return mask


def normalize_array(array):
    mask = raster_to_mask(array)
    return shapes.normalize(mask, preserve_aspect=True)


def control_array_to_mask(array):
    """Isolate the incised/embossed lines from Hlavica's full sherd drawing.

    Pages include headings, a scale, and the outline of a grey-filled sherd.
    The largest mid-grey component is the sherd; retaining dark strokes only
    inside an eroded version removes all three page-layout elements while
    preserving the documented mark.  The erosion deliberately clips strokes
    at a broken sherd edge rather than importing that edge as part of a mark.
    """
    grey = np.asarray(array, dtype=np.uint8)
    sherd_pixels = (grey >= 170) & (grey <= 235)
    # A transecting mark can divide the grey fill into several islands; close
    # stroke-width gaps before selecting the sherd component.
    sherd_pixels = ndimage.binary_closing(sherd_pixels, np.ones((3, 3)), iterations=5)
    labels, n = ndimage.label(sherd_pixels, np.ones((3, 3)))
    if not n:
        return None
    sizes = np.bincount(labels.ravel())
    sizes[0] = 0
    sherd = ndimage.binary_fill_holes(labels == int(np.argmax(sizes)))
    interior = ndimage.binary_erosion(sherd, iterations=4)
    mark = (grey < 165) & interior
    labels, n = ndimage.label(mark, np.ones((3, 3)))
    if n:
        sizes = np.bincount(labels.ravel())
        keep = sizes >= 2
        keep[0] = False
        mark = keep[labels]
    return shapes.normalize(mark, preserve_aspect=True)


def indus_sample_to_mask(array):
    """Crop the red TNSDA target box from a seal/pottery photograph."""
    rgba = np.asarray(array)
    if rgba.ndim == 3 and rgba.shape[2] >= 3:
        rgb = rgba[:, :, :3].astype(float)
        red = ((rgb[:, :, 0] > 100) &
               (rgb[:, :, 0] > 1.45 * (rgb[:, :, 1] + 1)) &
               (rgb[:, :, 0] > 1.45 * (rgb[:, :, 2] + 1)))
        labels, n = ndimage.label(red, np.ones((3, 3)))
        if n:
            sizes = np.bincount(labels.ravel())
            sizes[0] = 0
            target = labels == int(np.argmax(sizes))
            ys, xs = np.nonzero(target)
            if len(xs):
                y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
                inset = max(3, int(round(.12 * min(y1 - y0, x1 - x0))))
                if y1 - y0 > 2 * inset and x1 - x0 > 2 * inset:
                    rgba = rgba[y0 + inset:y1 - inset, x0 + inset:x1 - inset]
    return normalize_array(rgba)


def load_graffiti_masks(rows):
    manifest = load("graffiti-image-manifest.json")
    by_sign = {x["sign"]: ROOT / "data/graffiti" / x["cache"]
               for x in manifest["images"] if x["downloaded"]}
    ids, masks, missing = [], [], []
    for row in rows:
        sign = str(row["sign"]).strip()
        path = by_sign.get(sign)
        if not path or not path.exists():
            missing.append(sign)
            continue
        with Image.open(path) as image:
            mask = normalize_array(np.asarray(image.convert("RGBA")))
        if mask is None or mask.sum() < 4:
            missing.append(sign)
            continue
        ids.append(sign)
        masks.append(mask)
    return ids, np.asarray(masks, dtype=bool), missing


def load_control_masks(force=False):
    cache = ROOT / "data/graffiti/control/pottery_mark_rasters.npz"
    if cache.exists() and not force:
        z = np.load(cache, allow_pickle=False)
        meta = json.loads(str(z["meta"]))
        if meta.get("extraction") == "dark strokes inside closed-and-eroded grey sherd v2":
            return list(map(str, z["ids"])), z["masks"].astype(bool), meta
    if not CONTROL_ARCHIVE.exists():
        raise FileNotFoundError("run src/scrape_graffiti.py full to obtain the control")
    try:
        import pymupdf
    except ImportError:
        import fitz as pymupdf
    ids, masks, rejected = [], [], []
    with zipfile.ZipFile(CONTROL_ARCHIVE) as archive:
        names = sorted(x for x in archive.namelist() if x.lower().endswith(".pdf"))
        for name in names:
            try:
                document = pymupdf.open(stream=archive.read(name), filetype="pdf")
                page = document[0]
                pixmap = page.get_pixmap(matrix=pymupdf.Matrix(1.5, 1.5), alpha=False,
                                         colorspace=pymupdf.csGRAY)
                array = np.frombuffer(pixmap.samples, dtype=np.uint8).reshape(
                    pixmap.height, pixmap.width)
                mask = control_array_to_mask(array)
                if mask is None or mask.sum() < 4:
                    rejected.append({"file": name, "reason": "blank after normalization"})
                else:
                    ids.append(name)
                    masks.append(mask)
                document.close()
            except Exception as exc:
                rejected.append({"file": name, "reason": type(exc).__name__})
    cache.parent.mkdir(parents=True, exist_ok=True)
    meta = {"pdf_files": len(ids) + len(rejected), "rendered": len(ids),
            "rejected": rejected,
            "extraction": "dark strokes inside closed-and-eroded grey sherd v2"}
    np.savez_compressed(cache, ids=np.asarray(ids), masks=np.asarray(masks, np.uint8),
                        meta=np.asarray(json.dumps(meta)))
    return ids, np.asarray(masks, dtype=bool), meta


def merged_indus_masks():
    raster = shapes.render_all()
    records = inventory.handle_unknown(
        inventory.load_records(str(ROOT / "data/parsed/lines_merged.json")),
        "exclude_unknown")
    wanted = set(inventory.abundance(records))
    take = [i for i, sign in enumerate(map(int, raster["ids"])) if sign in wanted]
    return [int(raster["ids"][i]) for i in take], raster["aspect"][take].astype(bool)


def cross_shape_matrices(query, target):
    q = query.reshape(len(query), -1).astype(np.float32)
    t = target.reshape(len(target), -1).astype(np.float32)
    qi = q.sum(1)
    ti = t.sum(1)
    intersection = q @ t.T
    dice = 2 * intersection / (qi[:, None] + ti[None, :] + 1e-9)
    qdt = np.asarray([ndimage.distance_transform_edt(~x) for x in query],
                     dtype=np.float32).reshape(len(query), -1)
    tdt = np.asarray([ndimage.distance_transform_edt(~x) for x in target],
                     dtype=np.float32).reshape(len(target), -1)
    q_to_t = (q @ tdt.T) / (qi[:, None] + 1e-9)
    t_to_q = ((t @ qdt.T) / (ti[:, None] + 1e-9)).T
    chamfer = (q_to_t + t_to_q) / (2 * math.hypot(shapes.CANVAS, shapes.CANVAS))
    return dice.astype(np.float32), chamfer.astype(np.float32)


def skeletonize_mask(mask):
    """Morphological skeleton using a symmetric 3x3 cross element."""
    element = ndimage.generate_binary_structure(2, 1)
    work = mask.copy()
    skeleton = np.zeros_like(work)
    while work.any():
        opened = ndimage.binary_opening(work, structure=element)
        skeleton |= work & ~opened
        work = ndimage.binary_erosion(work, structure=element)
    return skeleton


def nearest_chamfer(query, target, *, rotations=False, skeleton=False):
    q = np.asarray([skeletonize_mask(x) for x in query]) if skeleton else query
    t = np.asarray([skeletonize_mask(x) for x in target]) if skeleton else target
    turns = range(4) if rotations else range(1)
    best = np.full(len(q), np.inf, float)
    for turn in turns:
        rotated = np.rot90(q, turn, axes=(1, 2))
        _, distance = cross_shape_matrices(rotated, t)
        best = np.minimum(best, distance.min(1))
    return best


def mask_descriptors(masks):
    result = []
    for mask in masks:
        crop = shapes.crop_ink(mask)
        h, w = crop.shape
        components = ndimage.label(crop, np.ones((3, 3)))[1]
        padded = np.pad(crop, 1)
        bg, nbg = ndimage.label(~padded, np.ones((3, 3)))
        border = set(np.unique(np.r_[bg[0], bg[-1], bg[:, 0], bg[:, -1]]))
        holes = sum(label not in border for label in range(1, nbg + 1))
        result.append([math.log(w / h), crop.mean(), components, holes])
    return np.asarray(result, float)


def unique_mask_indices(masks):
    seen, keep, groups = {}, [], []
    for i, mask in enumerate(masks):
        key = hashlib.sha256(np.packbits(mask).tobytes()).digest()
        if key not in seen:
            seen[key] = len(keep)
            keep.append(i)
            groups.append([i])
        else:
            groups[seen[key]].append(i)
    return np.asarray(keep, int), groups


def aligned_dice_screened(query, target, chamfer, candidates=16):
    candidates = min(candidates, len(target))
    candidate_ix = np.argpartition(chamfer, candidates - 1, axis=1)[:, :candidates]
    transforms = [(scale, dy, dx) for scale in shapes.SCALES
                  for dy in shapes.SHIFTS for dx in shapes.SHIFTS]
    target_transformed = np.asarray([
        [shapes.transform(mask, *parameters) for parameters in transforms]
        for mask in target], dtype=bool)
    target_ink = target.sum((1, 2))
    best_dice = np.zeros(len(query), float)
    best_target = np.zeros(len(query), int)
    for i, mask in enumerate(query):
        choice = candidate_ix[i]
        qink = mask.sum()
        selected_transforms = target_transformed[choice]
        inter_a = np.count_nonzero(selected_transforms & mask[None, None, :, :], axis=(2, 3))
        dice_a = 2 * inter_a / (qink + selected_transforms.sum((2, 3)) + 1e-9)
        q_transformed = np.asarray([shapes.transform(mask, *p) for p in transforms])
        inter_b = np.count_nonzero(
            q_transformed[:, None, :, :] & target[choice][None, :, :, :], axis=(2, 3))
        dice_b = 2 * inter_b / (q_transformed.sum((1, 2))[:, None] +
                               target_ink[choice][None, :] + 1e-9)
        per_target = np.maximum(dice_a.max(1), dice_b.max(0))
        j = int(np.argmax(per_target))
        best_dice[i] = per_target[j]
        best_target[i] = choice[j]
    return best_dice, best_target


def compare_distance_samples(a, b, rng):
    a, b = np.asarray(a), np.asarray(b)
    mw = stats.mannwhitneyu(a, b, alternative="less")
    boot = np.empty(SHAPE_BOOT)
    for i in range(SHAPE_BOOT):
        boot[i] = (np.median(rng.choice(b, len(b), replace=True)) -
                   np.median(rng.choice(a, len(a), replace=True)))
    return {
        "n_a": len(a), "n_control": len(b),
        "median_a": float(np.median(a)), "median_control": float(np.median(b)),
        "median_control_minus_a": float(np.median(b) - np.median(a)),
        "bootstrap_95pct": [float(x) for x in np.quantile(boot, [.025, .975])],
        "probability_a_closer_auc": float(1 - mw.statistic / (len(a) * len(b))),
        "mann_whitney_less_p": float(mw.pvalue),
    }


def row_sign(row):
    if row.get("tnsda") is not None:
        value = str(row["tnsda"])
    else:
        image = row.get("sealimg") or row.get("potimg") or ""
        value = re.sub(r"-(?:Seal|Pottery)$", "", str(image), flags=re.I)
    return value.strip().rstrip(".")


def crosswalk_validation(graffiti_ids, graffiti_masks, indus_ids, indus_masks,
                         graffiti_chamfer, rng):
    manifest = load("indus-image-manifest.json")
    paths = {x["source"]: ROOT / "data/graffiti" / x["cache"]
             for x in manifest if x["downloaded"]}
    gindex = {sign: i for i, sign in enumerate(graffiti_ids)}
    rows = [row for row in load("indus.json") if len(row) > 1]
    selected = []
    sample_masks = []
    for row in rows:
        sign = row_sign(row)
        if sign not in gindex:
            continue
        alternatives = []
        for field in ("sealimg", "potimg"):
            if not row.get(field):
                continue
            ref = "indus/" + str(row[field]).strip() + ".png"
            path = paths.get(ref)
            if not path or not path.exists():
                continue
            with Image.open(path) as image:
                mask = indus_sample_to_mask(np.asarray(image.convert("RGBA")))
            if mask is None or mask.sum() < 4:
                continue
            _, distance = cross_shape_matrices(np.asarray([mask]), indus_masks)
            alternatives.append((float(distance[0].min()), int(distance[0].argmin()),
                                 mask, field, ref))
        if not alternatives:
            continue
        sample_distance, target, sample_mask, field, ref = min(alternatives)
        query = gindex[sign]
        distances = graffiti_chamfer[query]
        pair_distance = float(distances[target])
        rank = int(1 + np.sum(distances < pair_distance))
        selected.append({
            "sign": sign, "rmrl": row.get("rmrl"), "imnobase": row.get("imnobase"),
            "sample_field": field, "sample_image": ref,
            "own_indus_id_inferred_from_sample": indus_ids[target],
            "sample_to_own_indus_chamfer": sample_distance,
            "graffiti_to_asserted_own_shape_chamfer": pair_distance,
            "nearest_possible_chamfer": float(distances.min()),
            "asserted_target_rank": rank,
        })
        sample_masks.append(sample_mask)
    if not selected:
        return {"usable_rows": 0, "failure": "no crosswalk images could be normalized"}
    targets = np.asarray([indus_ids.index(x["own_indus_id_inferred_from_sample"])
                          for x in selected], int)
    queries = np.asarray([gindex[x["sign"]] for x in selected], int)
    observed = np.asarray([x["graffiti_to_asserted_own_shape_chamfer"] for x in selected])
    null = np.zeros(SHAPE_BOOT)
    for run in range(SHAPE_BOOT):
        shuffled = rng.permutation(targets)
        null[run] = graffiti_chamfer[queries, shuffled].mean()

    sample_masks = np.asarray(sample_masks, bool)
    _, sample_chamfer = cross_shape_matrices(sample_masks, indus_masks)
    sample_dice, _ = aligned_dice_screened(sample_masks, indus_masks, sample_chamfer)
    exact_cut = 0.0043
    return {
        "endpoint_rows": len(load("indus.json")),
        "substantive_rows": len(rows),
        "usable_rows": len(selected),
        "explicit_tnsda_rows": sum(row.get("tnsda") is not None for row in rows),
        "method": ("infer the nearest sign in this project's Parpola-derived font from "
                   "TNSDA's paired Indus seal/pottery image, then rank that own-font target "
                   "against every own-font sign for the paired graffiti glyph"),
        "target_rank": {
            "top_1": sum(x["asserted_target_rank"] <= 1 for x in selected),
            "top_5": sum(x["asserted_target_rank"] <= 5 for x in selected),
            "top_10": sum(x["asserted_target_rank"] <= 10 for x in selected),
            "median": float(np.median([x["asserted_target_rank"] for x in selected])),
        },
        "pair_distance": {
            "mean": float(observed.mean()), "median": float(np.median(observed)),
            "random_pair_mean": float(null.mean()),
            "random_pair_95pct": [float(x) for x in np.quantile(null, [.025, .975])],
            "lower_p": float((1 + np.sum(null <= observed.mean())) / (SHAPE_BOOT + 1)),
        },
        "glyph_source_check": {
            "sample_images_exact_under_note17_dice_cut": int(
                np.sum(1 - sample_dice <= exact_cut)),
            "of": len(sample_dice),
            "median_best_aligned_dice": float(np.median(sample_dice)),
            "reading": ("pixel agreement under the pre-existing note-17 allograph cut; "
                        "zero/low agreement argues against identical modern glyph art, but "
                        "does not prove independent archaeological exemplars"),
        },
        "rows": selected,
    }


def shape_control(rows, rng):
    graffiti_ids, graffiti_masks, missing = load_graffiti_masks(rows)
    control_ids, control_masks, control_meta = load_control_masks()
    indus_ids, indus_masks = merged_indus_masks()
    indus_raw_n = len(indus_ids)
    indus_keep, indus_groups = unique_mask_indices(indus_masks)
    indus_ids = [indus_ids[i] for i in indus_keep]
    indus_masks = indus_masks[indus_keep]
    _, graffiti_chamfer = cross_shape_matrices(graffiti_masks, indus_masks)
    raw_noncomp = np.asarray([i for i, sign in enumerate(graffiti_ids)
                              if not sign.endswith("C")], int)
    raw_composite = np.asarray([i for i, sign in enumerate(graffiti_ids)
                                if sign.endswith("C")], int)
    nc_keep, nc_groups = unique_mask_indices(graffiti_masks[raw_noncomp])
    co_keep, co_groups = unique_mask_indices(graffiti_masks[raw_composite])
    noncomp_ix = raw_noncomp[nc_keep]
    composite_ix = raw_composite[co_keep]
    control_keep, control_groups = unique_mask_indices(control_masks)
    control_ids = [control_ids[i] for i in control_keep]
    control_masks = control_masks[control_keep]
    _, control_chamfer = cross_shape_matrices(control_masks, indus_masks)
    noncomp = graffiti_chamfer[noncomp_ix].min(1)
    composite = graffiti_chamfer[composite_ix].min(1)
    graffiti_nearest = np.r_[noncomp, composite]
    control_nearest = control_chamfer.min(1)

    # Inventory-size and graphical-complexity matching: 588 base/variant marks
    # are assigned without replacement to the nearest of 636 control drawings
    # in four standardized descriptor dimensions.
    gd = mask_descriptors(graffiti_masks[noncomp_ix])
    cd = mask_descriptors(control_masks)
    pooled = np.vstack((gd, cd))
    center, scale = pooled.mean(0), pooled.std(0)
    scale[scale == 0] = 1
    gz, cz = (gd - center) / scale, (cd - center) / scale
    cost = ((gz[:, None, :] - cz[None, :, :]) ** 2).sum(2)
    gi, ci = optimize.linear_sum_assignment(cost)
    matched_control = control_nearest[ci]
    matched_graffiti = noncomp[gi]
    paired = stats.wilcoxon(matched_graffiti, matched_control, alternative="less")

    skeleton_noncomp = nearest_chamfer(graffiti_masks[noncomp_ix], indus_masks,
                                       skeleton=True)
    skeleton_control = nearest_chamfer(control_masks, indus_masks, skeleton=True)
    rotated_noncomp = nearest_chamfer(graffiti_masks[noncomp_ix], indus_masks,
                                      rotations=True)
    rotated_control = nearest_chamfer(control_masks, indus_masks, rotations=True)
    rotated_skeleton_noncomp = nearest_chamfer(
        graffiti_masks[noncomp_ix], indus_masks, rotations=True, skeleton=True)
    rotated_skeleton_control = nearest_chamfer(
        control_masks, indus_masks, rotations=True, skeleton=True)

    # The note-17 cutoff was selected before this round from the within-Indus
    # allograph split, so it is not tuned to either comparison corpus.
    noncomp_dice, _ = aligned_dice_screened(
        graffiti_masks[noncomp_ix], indus_masks, graffiti_chamfer[noncomp_ix])
    control_dice, _ = aligned_dice_screened(control_masks, indus_masks, control_chamfer)
    exact_cut = 0.0043

    fig, ax = plt.subplots(figsize=(7.4, 4.5))
    for values, label, color in ((noncomp, "graffiti bases + variants", "#b64442"),
                                 (composite, "graffiti composites", "#d19752"),
                                 (control_nearest, "Moravian pottery-mark control", "#356f86")):
        values = np.sort(values)
        ax.step(values, np.arange(1, len(values) + 1) / len(values),
                where="post", label=f"{label} (n={len(values)})", color=color)
    ax.set(xlabel="nearest symmetric chamfer distance to an Indus sign",
           ylabel="cumulative share", title="Shape overlap needs a convergence baseline")
    ax.legend(frameon=False, loc="lower right")
    ax.grid(alpha=.15)
    fig.tight_layout()
    fig.savefig(FIGURE, dpi=180)
    plt.close(fig)

    crosswalk = crosswalk_validation(graffiti_ids, graffiti_masks, indus_ids, indus_masks,
                                     graffiti_chamfer, rng)
    return {
        "inventories": {"graffiti_rendered": len(graffiti_ids),
                        "graffiti_missing": missing,
                        "graffiti_raw_noncomposite": len(raw_noncomp),
                        "graffiti_raw_composite": len(raw_composite),
                        "graffiti_noncomposite": len(noncomp_ix),
                        "graffiti_composite": len(composite_ix),
                        "deduplication": "exact normalized 64x64 pixel identity within category",
                        "indus_merged_rendered": len(indus_ids),
                        "indus_exact_pixel_ids_removed": indus_raw_n - len(indus_ids),
                        "control": len(control_ids),
                        "control_raw": sum(len(x) for x in control_groups),
                        "control_metadata": control_meta},
        "metric": ("64x64 aspect-preserving masks; symmetric centered chamfer exactly as "
                   "src/shapes.py; aligned Dice with the same 0.90/1.00/1.10 scales and "
                   "±2-pixel shifts, screened to the 16 nearest chamfer candidates"),
        "continuous_comparisons": {
            "graffiti_base_variant_vs_control_all": compare_distance_samples(
                noncomp, control_nearest, rng),
            "graffiti_composite_vs_control_all": compare_distance_samples(
                composite, control_nearest, rng),
            "graffiti_all_vs_control_all": compare_distance_samples(
                graffiti_nearest, control_nearest, rng),
            "skeletonized_base_variant_vs_control": compare_distance_samples(
                skeleton_noncomp, skeleton_control, rng),
            "rotation_invariant_base_variant_vs_control": compare_distance_samples(
                rotated_noncomp, rotated_control, rng),
            "rotation_invariant_skeletonized_base_variant_vs_control":
                compare_distance_samples(rotated_skeleton_noncomp,
                                         rotated_skeleton_control, rng),
            "complexity_matched_base_variant_vs_control": {
                "pairs": len(gi),
                "median_graffiti": float(np.median(matched_graffiti)),
                "median_control": float(np.median(matched_control)),
                "median_control_minus_graffiti": float(
                    np.median(matched_control - matched_graffiti)),
                "wilcoxon_less_p": float(paired.pvalue),
                "descriptor_standardized_mean_difference_after_match": [
                    float(x) for x in (gz[gi] - cz[ci]).mean(0)],
                "balance_warning": ("poor common support; at least one absolute standardized "
                                    "mean difference exceeds 0.25" if
                                    np.max(np.abs((gz[gi] - cz[ci]).mean(0))) > .25 else None),
            },
        },
        "preexisting_allograph_cut": {
            "dice_distance_cut": exact_cut,
            "graffiti_base_variant_matches": int(np.sum(1 - noncomp_dice <= exact_cut)),
            "graffiti_base_variant_total": len(noncomp_dice),
            "control_matches": int(np.sum(1 - control_dice <= exact_cut)),
            "control_total": len(control_dice),
            "graffiti_rate": float(np.mean(1 - noncomp_dice <= exact_cut)),
            "control_rate": float(np.mean(1 - control_dice <= exact_cut)),
        },
        "crosswalk": crosswalk,
        "figure": str(FIGURE.relative_to(ROOT)),
    }


def provenance():
    metadata = load("control-zenodo-7965768.json")
    files = {}
    for name in ("sites.json", "filter-sign.json", "base-sign.json", "options.json",
                 "indus.json"):
        path = RAW / name
        files[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    return {
        "access_date": "2026-08-17",
        "api_base": "https://api.tamilknowledgecampus.in/graffiti/",
        "site": "https://tngraffiti.in",
        "raw_cache": "data/graffiti/ (gitignored)",
        "core_sha256": files,
        "control": {
            "doi": "10.5281/zenodo.7965768",
            "title": metadata.get("metadata", {}).get("title"),
            "license": metadata.get("metadata", {}).get("license"),
            "file": "Pottery_Marks_PDF.zip",
            "repository_checksum": next(
                (x.get("checksum") for x in metadata.get("files", [])
                 if x.get("key") == "Pottery_Marks_PDF.zip"), None),
        },
    }


def main():
    rng = np.random.default_rng(SEED)
    rows = api_rows("filter-sign.json")
    description, graffiti_freq = corpus_description(rows)
    depth_sites, depth_failures = depth_site_arrays()
    result = {
        "method": {"seed": SEED, "permutation_runs": RUNS,
                   "shape_bootstrap_runs": SHAPE_BOOT},
        "provenance": provenance(),
        "sequence_audit": sequence_audit(),
        "description": description,
        "inventory_saturation": inventory_comparison(graffiti_freq, rng),
        "branching": branching_structure(rows, rng),
        "stratigraphy": depth_statistics(depth_sites) |
            {"site_failures": depth_failures},
        "shape_control": shape_control(rows, rng),
    }
    OUT.write_text(json.dumps(finite(result), indent=2) + "\n")
    print(json.dumps({
        "output": str(OUT.relative_to(ROOT)),
        "corpus": result["description"]["corpus_table"],
        "sequence": result["sequence_audit"]["conclusion"],
        "shape": result["shape_control"]["continuous_comparisons"],
        "stratigraphy": result["stratigraphy"]["observed"] |
            {"null": result["stratigraphy"]["null"]},
    }, indent=2))


if __name__ == "__main__":
    main()
