"""Hierarchical partial pooling for sign-specific text-final propensity.

This is a conditional logistic choice model.  In every deduplicated text, the
observed final token is chosen from the text's own token positions:

    P(position i is final | text) = exp(u[sign_i]) / sum_j exp(u[sign_j])

Conditioning on the complete text gives the exact positional-shuffle baseline
and holds length, site, object class, and vocabulary fixed.  Site/object main
effects would be constant inside a text and therefore cancel; they are
conditioned out rather than estimated.

Per-sign effects have a shared Normal(0, tau^2) prior and tau has a half-normal
hyperprior.  The joint posterior is approximated at its mode with the full
Laplace Hessian.  Hyperprior scales 0.5, 1, and 2 provide the requested prior
sensitivity.  Posterior predictive draws choose exactly one final token from
each observed text, preserving the conditional design.
"""
import argparse
import json
import math
from collections import Counter, defaultdict

import numpy as np
from scipy import optimize
from scipy.special import logsumexp

SEED = 33
PRIOR_SCALES = (0.5, 1.0, 2.0)
MAIN_PRIOR = 1.0
RARE_THRESHOLD = 20

TERMINAL = {740, 520, 390, 151, 527, 617, 156}
NUMERALS = ({1, 2, 3, 4, 5, 6, 7, 13, 14, 15, 16, 17, 18, 19,
             27, 28, 29, 31, 32, 33, 34, 35, 36, 55, 56,
             48, 49, 50, 51, 57})


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


def unreadable_signs():
    glyphs = json.load(open("data/parsed/glyphs.json"))
    return ({row["glyph_id"] for row in glyphs if "2047" in row.get("unicode", "")}
            | {999})


def make_groups(records, sign_index):
    groups = defaultdict(list)
    for i, rec in enumerate(records):
        groups[len(rec["text"])].append((i, [sign_index[g] for g in rec["text"]]))
    return {length: {"record": np.asarray([i for i, _ in rows], dtype=int),
                     "signs": np.asarray([text for _, text in rows], dtype=int)}
            for length, rows in groups.items()}


def objective(theta, groups, n_signs, prior_scale):
    u = theta[:n_signs]
    z = theta[n_signs]
    tau2 = math.exp(2 * z)
    value = 0.0
    gradient = np.zeros_like(theta)
    for group in groups.values():
        signs = group["signs"]
        scores = u[signs]
        normalizer = logsumexp(scores, axis=1)
        value += np.sum(normalizer - scores[:, -1])
        probabilities = np.exp(scores - normalizer[:, None])
        gradient[:n_signs] += np.bincount(
            signs.ravel(), weights=probabilities.ravel(), minlength=n_signs)
        gradient[:n_signs] -= np.bincount(signs[:, -1], minlength=n_signs)

    # Normal random effects plus half-normal(tau | prior_scale), including the
    # Jacobian for z=log(tau): (J-1)z rather than Jz.
    value += .5 * np.dot(u, u) / tau2
    value += (n_signs - 1) * z + .5 * tau2 / (prior_scale ** 2)
    gradient[:n_signs] += u / tau2
    gradient[n_signs] = (-np.dot(u, u) / tau2 + (n_signs - 1) +
                         tau2 / (prior_scale ** 2))
    return value, gradient


def posterior_hessian(mode, groups, n_signs, prior_scale):
    u = mode[:n_signs]
    z = mode[n_signs]
    tau2 = math.exp(2 * z)
    hessian = np.zeros((n_signs + 1, n_signs + 1), float)
    hessian[np.arange(n_signs), np.arange(n_signs)] = 1 / tau2
    for group in groups.values():
        for signs in group["signs"]:
            scores = u[signs]
            probabilities = np.exp(scores - logsumexp(scores))
            # Aggregate duplicate sign positions before forming diag(q)-qq'.
            unique, inverse = np.unique(signs, return_inverse=True)
            q = np.bincount(inverse, weights=probabilities)
            block = np.diag(q) - np.outer(q, q)
            hessian[np.ix_(unique, unique)] += block
    cross = -2 * u / tau2
    hessian[:n_signs, n_signs] = cross
    hessian[n_signs, :n_signs] = cross
    hessian[n_signs, n_signs] = (2 * np.dot(u, u) / tau2 +
                                 2 * tau2 / (prior_scale ** 2))
    return hessian


def fit_model(groups, n_signs, prior_scale, draws, rng):
    initial = np.zeros(n_signs + 1)
    initial[-1] = math.log(.75)
    result = optimize.minimize(
        lambda x: objective(x, groups, n_signs, prior_scale), initial,
        jac=True, method="L-BFGS-B", bounds=[(None, None)] * n_signs + [(-5, 3)],
        options={"maxiter": 1500, "ftol": 1e-11, "gtol": 1e-7, "maxls": 50})
    hessian = posterior_hessian(result.x, groups, n_signs, prior_scale)
    eigenvalues, eigenvectors = np.linalg.eigh(hessian)
    clipped = np.maximum(eigenvalues, 1e-8)
    transform = eigenvectors / np.sqrt(clipped)[None, :]
    standard = rng.normal(size=(draws, n_signs + 1))
    samples = result.x + standard @ transform.T
    return {"mode": result.x, "samples": samples, "success": bool(result.success),
            "message": result.message, "iterations": result.nit,
            "gradient_max": float(np.max(np.abs(result.jac))),
            "hessian_min_eigenvalue": float(eigenvalues.min()),
            "hessian_clipped": int(np.sum(eigenvalues < 1e-8))}


def adjusted_probabilities(u_samples, length_counts):
    """Common-mix P(final): sign competes with L-1 neutral effects.

    Lengths are weighted by token opportunities.  At u=0 this is exactly the
    corpus base rate: number of texts / number of tokens.
    """
    token_total = sum(length * n for length, n in length_counts.items())
    odds = np.exp(np.clip(u_samples, -20, 20))
    out = np.zeros_like(odds)
    for length, n in length_counts.items():
        weight = length * n / token_total
        out += weight * odds / (odds + length - 1)
    return out


def summarize_signs(signs, records, samples, length_counts, base_rate):
    frequency = Counter(g for rec in records for g in rec["text"])
    final = Counter(rec["text"][-1] for rec in records)
    earlier_terminal = Counter()
    predecessors = defaultdict(Counter)
    for rec in records:
        text = rec["text"]
        g = text[-1]
        earlier_terminal[g] += any(x in TERMINAL for x in text[:-1])
        if len(text) > 1:
            predecessors[g][text[-2]] += 1
    probability = adjusted_probabilities(samples[:, :len(signs)], length_counts)
    rows = []
    for j, sign in enumerate(signs):
        p = probability[:, j]
        u = samples[:, j]
        rows.append({
            "sign": sign, "tokens": frequency[sign], "finals": final[sign],
            "raw_final_rate": final[sign] / frequency[sign],
            "finals_with_earlier_terminal": earlier_terminal[sign],
            "top_final_predecessors": predecessors[sign].most_common(5),
            "effect_mean": float(u.mean()),
            "effect_q025": float(np.quantile(u, .025)),
            "effect_q975": float(np.quantile(u, .975)),
            "p_final_mean": float(p.mean()),
            "p_final_q025": float(np.quantile(p, .025)),
            "p_final_q975": float(np.quantile(p, .975)),
            "pr_above_base": float(np.mean(p > base_rate)),
        })
    return rows


def posterior_predictive(records, signs, sign_index, samples, draws, rng):
    chosen = np.linspace(0, len(samples) - 1, draws, dtype=int)

    def statistics(final_signs):
        counts = Counter(final_signs)
        total = len(final_signs)
        result = {
            "terminal_share": sum(g in TERMINAL for g in final_signs) / total,
            "740_share": counts[740] / total,
            "top10_share": sum(n for _g, n in counts.most_common(10)) / total,
            "distinct_final_signs": len(counts),
        }
        for label, predicate in (
            ("mohenjo_daro_terminal_share", lambda r: r["site"] == "SI1"),
            ("harappa_terminal_share", lambda r: r["site"] == "SI2"),
            ("seal_terminal_share", lambda r: r["object"] == "seal"),
            ("tablet_terminal_share", lambda r: r["object"] == "tablet"),
        ):
            subset = [g for g, rec in zip(final_signs, records) if predicate(rec)]
            result[label] = (sum(g in TERMINAL for g in subset) / len(subset)
                             if subset else float("nan"))
        return result

    observed = statistics([rec["text"][-1] for rec in records])
    simulated = {key: [] for key in observed}
    encoded = [np.asarray([sign_index[g] for g in rec["text"]], dtype=int)
               for rec in records]
    for draw in chosen:
        u = samples[draw, :len(signs)]
        finals = []
        for rec, indices in zip(records, encoded):
            score = u[indices]
            probability = np.exp(score - logsumexp(score))
            finals.append(rec["text"][rng.choice(len(indices), p=probability)])
        stats = statistics(finals)
        for key, value in stats.items():
            simulated[key].append(value)
    output = {}
    for key, values in simulated.items():
        values = np.asarray(values)
        lower = (1 + np.sum(values <= observed[key])) / (len(values) + 1)
        upper = (1 + np.sum(values >= observed[key])) / (len(values) + 1)
        output[key] = {"observed": float(observed[key]),
                       "mean": float(values.mean()),
                       "q025": float(np.quantile(values, .025)),
                       "q975": float(np.quantile(values, .975)),
                       "tail_p": float(min(1, 2 * min(lower, upper)))}
    return output

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--draws", type=int, default=4000)
    parser.add_argument("--ppc-draws", type=int, default=500)
    args = parser.parse_args()
    rng = np.random.default_rng(SEED)
    records = load_records()
    signs = sorted({g for rec in records for g in rec["text"]})
    sign_index = {g: i for i, g in enumerate(signs)}
    groups = make_groups(records, sign_index)
    frequency = Counter(g for rec in records for g in rec["text"])
    final = Counter(rec["text"][-1] for rec in records)
    length_counts = Counter(len(rec["text"]) for rec in records)
    tokens = sum(frequency.values())
    base_rate = len(records) / tokens
    unreadable = unreadable_signs()

    print("=== corpus and conditional control ===")
    print(f"  merged, deduplicated sequence/site/object texts: {len(records)}")
    print(f"  tokens: {tokens}; signs: {len(signs)}; P(any token is final): {base_rate:.3%}")
    print("  each observed final token competes only with tokens in its own text")
    print("  => exact control for length, positional opportunities, site, object,")
    print("     and the text's complete sign multiset")
    print(f"  random effects: {len(signs)} sign intercepts; tau ~ HalfNormal(A)")

    fits = {}
    summaries = {}
    for scale in PRIOR_SCALES:
        fit = fit_model(groups, len(signs), scale, args.draws, rng)
        rows = summarize_signs(signs, records, fit["samples"], length_counts, base_rate)
        tau = np.exp(fit["samples"][:, -1])
        high = {row["sign"] for row in rows
                if row["tokens"] < RARE_THRESHOLD and row["sign"] not in NUMERALS
                and row["sign"] not in unreadable and
                row["p_final_q025"] > base_rate}
        low = {row["sign"] for row in rows
               if row["tokens"] < RARE_THRESHOLD and row["sign"] not in NUMERALS
               and row["sign"] not in unreadable and
               row["p_final_q975"] < base_rate}
        fits[scale] = fit
        summaries[scale] = {"rows": rows, "tau_mean": float(tau.mean()),
                            "tau_q025": float(np.quantile(tau, .025)),
                            "tau_q975": float(np.quantile(tau, .975)),
                            "rare_high": high, "rare_low": low}
        print(f"\n=== prior A={scale:g} ===")
        print(f"  optimizer success={fit['success']} in {fit['iterations']} iterations; "
              f"max |gradient|={fit['gradient_max']:.3g}")
        print(f"  Hessian min eigenvalue={fit['hessian_min_eigenvalue']:.4g}; "
              f"clipped directions={fit['hessian_clipped']}")
        print(f"  tau posterior mean {tau.mean():.3f}, 95% "
              f"{np.quantile(tau,.025):.3f}-{np.quantile(tau,.975):.3f}")
        print(f"  rare identifiable non-numerals with CI wholly above base: {len(high)}")
        print(f"  rare identifiable non-numerals with CI wholly below base: {len(low)}")

    main = summaries[MAIN_PRIOR]
    print("\n=== known terminal-slot members, main prior ===")
    print("  sign tokens finals raw rate  posterior adjusted P(final), mean [95%]  "
          "Pr(above base)")
    by_sign = {row["sign"]: row for row in main["rows"]}
    for sign in sorted(TERMINAL):
        row = by_sign[sign]
        print(f"  {sign:>4} {row['tokens']:>6} {row['finals']:>6} "
              f"{row['raw_final_rate']:>8.1%}  {row['p_final_mean']:>8.1%} "
              f"[{row['p_final_q025']:.1%}, {row['p_final_q975']:.1%}] "
              f"{row['pr_above_base']:>13.3f}")

    print("\n=== previously untestable rare candidates, main prior ===")
    candidates = sorted((by_sign[g] for g in main["rare_high"]),
                        key=lambda row: -row["p_final_mean"])
    print(f"  rule: <{RARE_THRESHOLD} tokens, identifiable non-numeral, "
          f"95% interval entirely above {base_rate:.1%}")
    print("  sign tokens finals raw rate  posterior mean [95%]  Pr(above base)  "
          "finals after known terminal")
    for row in candidates:
        print(f"  {row['sign']:>4} {row['tokens']:>6} {row['finals']:>6} "
              f"{row['raw_final_rate']:>8.1%} {row['p_final_mean']:>8.1%} "
              f"[{row['p_final_q025']:.1%}, {row['p_final_q975']:.1%}] "
              f"{row['pr_above_base']:>13.3f} "
              f"{row['finals_with_earlier_terminal']:>11}/{row['finals']:<3}")

    sets = [summaries[scale]["rare_high"] for scale in PRIOR_SCALES]
    intersection = set.intersection(*sets)
    union = set.union(*sets)
    print("\n=== prior sensitivity of rare high candidates ===")
    for scale in PRIOR_SCALES:
        print(f"  A={scale:g}: {len(summaries[scale]['rare_high'])}: " +
              " ".join(map(str, sorted(summaries[scale]["rare_high"]))))
    print(f"  intersection {len(intersection)}; union {len(union)}; "
          f"stable share {len(intersection)/len(union) if union else 1:.1%}")

    ppc = posterior_predictive(records, signs, sign_index,
                               fits[MAIN_PRIOR]["samples"], args.ppc_draws, rng)
    print("\n=== conditional posterior predictive checks, main prior ===")
    print("  statistic                         observed   PPC mean    PPC 95%       tail p")
    for key, row in ppc.items():
        print(f"  {key:<32} {row['observed']:>8.3f} {row['mean']:>10.3f} "
              f"{row['q025']:>7.3f}-{row['q975']:<7.3f} {row['tail_p']:>7.3f}")

    # Complete all-sign table under the main prior; sensitivity summaries stay
    # compact because their purpose is conclusion movement, not three copies.
    output = {
        "seed": SEED, "records": len(records), "tokens": tokens,
        "signs": len(signs), "base_rate": base_rate,
        "model": "Laplace hierarchical conditional logistic",
        "control": "within-text conditional choice; length/site/object/multiset fixed",
        "main_prior_scale": MAIN_PRIOR,
        "tau": {"mean": main["tau_mean"], "q025": main["tau_q025"],
                "q975": main["tau_q975"]},
        "sign_posteriors": main["rows"],
        "rare_high": sorted(main["rare_high"]),
        "rare_low": sorted(main["rare_low"]),
        "sensitivity": {
            str(scale): {"tau_mean": summaries[scale]["tau_mean"],
                         "tau_q025": summaries[scale]["tau_q025"],
                         "tau_q975": summaries[scale]["tau_q975"],
                         "rare_high": sorted(summaries[scale]["rare_high"]),
                         "rare_low_count": len(summaries[scale]["rare_low"]),
                         "optimizer_success": fits[scale]["success"],
                         "optimizer_iterations": fits[scale]["iterations"],
                         "gradient_max": fits[scale]["gradient_max"],
                         "hessian_min_eigenvalue": fits[scale]["hessian_min_eigenvalue"],
                         "hessian_clipped": fits[scale]["hessian_clipped"]}
            for scale in PRIOR_SCALES},
        "rare_high_intersection": sorted(intersection),
        "rare_high_union": sorted(union), "ppc": ppc,
    }
    json.dump(output, open("data/parsed/finality_posterior.json", "w"), indent=1)
    print("\nwrote complete 527-sign table to data/parsed/finality_posterior.json")


if __name__ == "__main__":
    main()
