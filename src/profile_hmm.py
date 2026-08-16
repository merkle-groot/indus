"""Profile-HMM test of the optional-template account.

The corpus is deduplicated by (sequence, site, object class) before fitting.
The model is a conventional linear profile with M match states, an insertion
state before/between/after the matches, and a delete option at every match.
Insert states share an emission distribution so that a large M cannot buy M+1
unconstrained background vocabularies.

Evaluation is fixed before exploration:

* deterministic 80/20 held-out split, stratified by length, site group, object;
* likelihood conditional on observed text length, so all three models answer
  the same question rather than rewarding the HMM for fitting length;
* unigram and additively-smoothed bigram baselines;
* exact-column surrogates within length/site/object, preserving every positional
  marginal while destroying which slot occupants travel together;
* frequency-matched surrogates within site/object, preserving exact token
  counts and text lengths while destroying both pairing and position.

A template survives only if its held-out likelihood beats the bigram and its
improvement is beyond both surrogate distributions.  Match occupancy and the
terminal-paradigm emission mass are printed only as diagnostics of the selected
model; they are not used to select M.
"""
import argparse
import json
import math
from collections import Counter, defaultdict

import numpy as np

SEED = 31
TERMINAL = {740, 520, 390, 151, 527, 617, 156}
MATCH_GRID = tuple(range(1, 14))  # observed maximum text length is 13
EMISSION_PRIOR = 5.0
TRANSITION_PRIOR = 0.5


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


def split_records(records, rng):
    """Stable 80/20 split within coarse cells; tiny cells use a global draw."""
    cells = defaultdict(list)
    for i, rec in enumerate(records):
        length = min(len(rec["text"]), 8)
        site = rec["site"] if rec["site"] in {"SI1", "SI2"} else "other"
        obj = rec["object"] if rec["object"] in {"seal", "tablet"} else "other"
        cells[(length, site, obj)].append(i)
    test = set()
    for indices in cells.values():
        shuffled = list(rng.permutation(indices))
        n_test = max(1, round(.20 * len(indices))) if len(indices) >= 4 else 0
        test.update(shuffled[:n_test])
    # Put sparse-cell records into the test set at the same overall rate.
    target = round(.20 * len(records))
    remaining = [i for i in range(len(records)) if i not in test]
    if len(test) < target:
        test.update(rng.choice(remaining, target - len(test), replace=False).tolist())
    train = [i for i in range(len(records)) if i not in test]
    return np.asarray(train), np.asarray(sorted(test))


def encode(records, vocab_index):
    return [np.asarray([vocab_index[g] for g in rec["text"]], dtype=np.int32)
            for rec in records]


class ProfileHMM:
    def __init__(self, matches, vocab_size, background):
        self.m = matches
        self.v = vocab_size
        self.background = np.asarray(background, float)
        self.q = np.full(matches + 1, .12)  # insertion continuation
        self.delete = np.full(matches, .18)
        self.theta = np.tile(self.background, (matches, 1))
        self.phi = self.background.copy()

    def initialize(self, texts):
        counts = np.tile(EMISSION_PRIOR * self.background + 1e-8,
                         (self.m, 1))
        for text in texts:
            n = len(text)
            for i, token in enumerate(text):
                # Deterministic quantile alignment is an initialization only.
                j = min(self.m - 1, int((i + .5) * self.m / n))
                counts[j, token] += 1
        self.theta = counts / counts.sum(axis=1, keepdims=True)

    def forward_backward_batch(self, texts, collect=False):
        """Forward/backward for an equal-length batch.

        Vectorizing over texts turns the surrogate calibration from hours of
        Python loops into a tractable analysis without changing the model.
        """
        texts = np.asarray(texts, dtype=np.int32)
        batch, n = texts.shape
        m = self.m
        a = np.zeros((batch, n + 1, m + 1), float)
        a[:, 0, 0] = 1.0
        for i in range(n + 1):
            for j in range(m + 1):
                value = a[:, i, j]
                if i < n:
                    a[:, i + 1, j] += (value * self.q[j] *
                                        self.phi[texts[:, i]])
                if j < m:
                    leave = 1 - self.q[j]
                    a[:, i, j + 1] += value * leave * self.delete[j]
                    if i < n:
                        a[:, i + 1, j + 1] += (value * leave *
                                               (1 - self.delete[j]) *
                                               self.theta[j, texts[:, i]])
        probability = np.maximum(a[:, n, m] * (1 - self.q[m]), 1e-300)
        if not collect:
            return probability

        b = np.zeros((batch, n + 1, m + 1), float)
        b[:, n, m] = 1 - self.q[m]
        for i in range(n, -1, -1):
            for j in range(m, -1, -1):
                if i == n and j == m:
                    continue
                value = np.zeros(batch)
                if i < n:
                    value += (self.q[j] * self.phi[texts[:, i]] *
                              b[:, i + 1, j])
                if j < m:
                    leave = 1 - self.q[j]
                    value += leave * self.delete[j] * b[:, i, j + 1]
                    if i < n:
                        value += (leave * (1 - self.delete[j]) *
                                  self.theta[j, texts[:, i]] *
                                  b[:, i + 1, j + 1])
                b[:, i, j] = value
        ins = np.zeros(m + 1)
        leave = np.zeros(m + 1)
        delete = np.zeros(m)
        match = np.zeros(m)
        match_emit = np.zeros((m, self.v))
        insert_emit = np.zeros(self.v)
        for i in range(n + 1):
            for j in range(m + 1):
                av = a[:, i, j]
                if i < n:
                    post = (av * self.q[j] * self.phi[texts[:, i]] *
                            b[:, i + 1, j] / probability)
                    ins[j] += post.sum()
                    insert_emit += np.bincount(texts[:, i], weights=post,
                                                minlength=self.v)
                if j < m:
                    edge = av * (1 - self.q[j]) * self.delete[j]
                    post = edge * b[:, i, j + 1] / probability
                    delete[j] += post.sum()
                    leave[j] += post.sum()
                    if i < n:
                        edge = (av * (1 - self.q[j]) * (1 - self.delete[j]) *
                                self.theta[j, texts[:, i]])
                        post = edge * b[:, i + 1, j + 1] / probability
                        match[j] += post.sum()
                        leave[j] += post.sum()
                        match_emit[j] += np.bincount(texts[:, i], weights=post,
                                                     minlength=self.v)
        # Every path ends by leaving the final insertion state once.
        leave[m] = batch
        return probability, (ins, leave, delete, match, match_emit, insert_emit)

    @staticmethod
    def batches(texts):
        by_length = defaultdict(list)
        for text in texts:
            by_length[len(text)].append(text)
        return [np.stack(group) for group in by_length.values()]

    def fit(self, texts, max_iter=60, tolerance=1e-5):
        self.initialize(texts)
        batches = self.batches(texts)
        previous = -np.inf
        for iteration in range(max_iter):
            ins = np.zeros(self.m + 1)
            leave = np.zeros(self.m + 1)
            delete = np.zeros(self.m)
            match = np.zeros(self.m)
            match_emit = np.zeros((self.m, self.v))
            insert_emit = np.zeros(self.v)
            loglike = 0.0
            for batch in batches:
                probability, stats = self.forward_backward_batch(batch, collect=True)
                loglike += np.log(probability).sum()
                ins += stats[0]
                leave += stats[1]
                delete += stats[2]
                match += stats[3]
                match_emit += stats[4]
                insert_emit += stats[5]
            self.q = ((ins + TRANSITION_PRIOR) /
                      (ins + leave + 2 * TRANSITION_PRIOR))
            self.delete = ((delete + TRANSITION_PRIOR) /
                           (delete + match + 2 * TRANSITION_PRIOR))
            prior = EMISSION_PRIOR * self.background + 1e-8
            self.theta = match_emit + prior
            self.theta /= self.theta.sum(axis=1, keepdims=True)
            self.phi = insert_emit + prior
            self.phi /= self.phi.sum()
            if iteration and abs(loglike - previous) < tolerance * (1 + abs(previous)):
                break
            previous = loglike
        return iteration + 1

    def length_probability(self, n):
        """Probability of emitting n tokens, summing over their identities."""
        m = self.m
        a = np.zeros((n + 1, m + 1), float)
        a[0, 0] = 1.0
        for i in range(n + 1):
            for j in range(m + 1):
                value = a[i, j]
                if i < n:
                    a[i + 1, j] += value * self.q[j]
                if j < m:
                    leave = 1 - self.q[j]
                    a[i, j + 1] += value * leave * self.delete[j]
                    if i < n:
                        a[i + 1, j + 1] += value * leave * (1 - self.delete[j])
        return max(a[n, m] * (1 - self.q[m]), 1e-300)

    def conditional_ll(self, texts):
        by_length = {n: self.length_probability(n)
                     for n in {len(t) for t in texts}}
        groups = defaultdict(list)
        for i, text in enumerate(texts):
            groups[len(text)].append((i, text))
        values = np.empty(len(texts))
        for n, group in groups.items():
            indices = [i for i, _text in group]
            batch = np.stack([text for _i, text in group])
            n = batch.shape[1]
            values[indices] = (np.log(self.forward_backward_batch(batch)) -
                               math.log(by_length[n]))
        return values

    def occupancy(self, texts):
        matched = np.zeros(self.m)
        for batch in self.batches(texts):
            _, stats = self.forward_backward_batch(batch, collect=True)
            matched += stats[3]
        return matched / len(texts)


def baseline_models(train, test, vocab_size, alpha=.5):
    unigram = np.full(vocab_size, alpha)
    for text in train:
        np.add.at(unigram, text, 1)
    unigram /= unigram.sum()
    uni_ll = np.asarray([sum(math.log(unigram[x]) for x in text) for text in test])

    start = np.full(vocab_size, alpha)
    transition = np.full((vocab_size, vocab_size), alpha)
    for text in train:
        start[text[0]] += 1
        for a, b in zip(text, text[1:]):
            transition[a, b] += 1
    start /= start.sum()
    transition /= transition.sum(axis=1, keepdims=True)
    bi_ll = []
    for text in test:
        value = math.log(start[text[0]])
        value += sum(math.log(transition[a, b]) for a, b in zip(text, text[1:]))
        bi_ll.append(value)
    return uni_ll, np.asarray(bi_ll)


def fit_grid(records, train_idx, test_idx, vocab, max_iter):
    index = {g: i for i, g in enumerate(vocab)}
    encoded = encode(records, index)
    train = [encoded[i] for i in train_idx]
    test = [encoded[i] for i in test_idx]
    counts = np.full(len(vocab), 1e-8)
    for text in train:
        np.add.at(counts, text, 1)
    background = counts / counts.sum()
    uni_ll, bi_ll = baseline_models(train, test, len(vocab))
    rows, models = [], {}
    tokens = sum(map(len, test))
    for matches in MATCH_GRID:
        model = ProfileHMM(matches, len(vocab), background)
        iterations = model.fit(train, max_iter=max_iter)
        ll = model.conditional_ll(test)
        rows.append({"matches": matches, "nats_token": ll.sum() / tokens,
                     "delta_unigram": (ll.sum() - uni_ll.sum()) / tokens,
                     "delta_bigram": (ll.sum() - bi_ll.sum()) / tokens,
                     "iterations": iterations})
        models[matches] = model
    best = max(rows, key=lambda row: row["nats_token"])
    best_ll = models[best["matches"]].conditional_ll(test)
    return {"rows": rows, "best": best, "model": models[best["matches"]],
            "encoded": encoded, "uni": uni_ll.sum() / tokens,
            "bi": bi_ll.sum() / tokens, "tokens": tokens,
            "profile_ll": best_ll, "uni_ll": uni_ll, "bi_ll": bi_ll}


def positional_surrogate(records, rng):
    out = [{**rec, "text": list(rec["text"])} for rec in records]
    groups = defaultdict(list)
    for i, rec in enumerate(records):
        groups[(len(rec["text"]), rec["site"], rec["object"])].append(i)
    for (length, _site, _obj), indices in groups.items():
        for position in range(length):
            values = [out[i]["text"][position] for i in indices]
            values = rng.permutation(values)
            for i, value in zip(indices, values):
                out[i]["text"][position] = int(value)
    for rec in out:
        rec["text"] = tuple(rec["text"])
    return out


def frequency_surrogate(records, rng):
    out = [{**rec, "text": list(rec["text"])} for rec in records]
    groups = defaultdict(list)
    for i, rec in enumerate(records):
        groups[(rec["site"], rec["object"])].append(i)
    for indices in groups.values():
        tokens = [g for i in indices for g in out[i]["text"]]
        tokens = iter(rng.permutation(tokens).tolist())
        for i in indices:
            out[i]["text"] = [int(next(tokens)) for _ in out[i]["text"]]
    for rec in out:
        rec["text"] = tuple(rec["text"])
    return out


def summarize_surrogates(rows):
    for kind in ("position", "frequency"):
        chosen = [row for row in rows if row["kind"] == kind]
        m = np.asarray([row["matches"] for row in chosen])
        db = np.asarray([row["delta_bigram"] for row in chosen])
        du = np.asarray([row["delta_unigram"] for row in chosen])
        print(f"  {kind:<10} best M median {np.median(m):.1f} "
              f"[{np.quantile(m,.025):.1f}, {np.quantile(m,.975):.1f}]; "
              f"delta unigram {du.mean():+.4f} "
              f"[{np.quantile(du,.025):+.4f}, {np.quantile(du,.975):+.4f}]; "
              f"delta bigram {db.mean():+.4f} "
              f"[{np.quantile(db,.025):+.4f}, {np.quantile(db,.975):+.4f}]")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--surrogates", type=int, default=20)
    parser.add_argument("--max-iter", type=int, default=60)
    args = parser.parse_args()
    rng = np.random.default_rng(SEED)
    records = load_records()
    vocab = sorted({g for rec in records for g in rec["text"]})
    train_idx, test_idx = split_records(records, rng)
    print("=== corpus and frozen evaluation design ===")
    print(f"  merged lines -> deduplicated sequence/site/object: 2613 -> {len(records)}")
    print(f"  train/test texts: {len(train_idx)} / {len(test_idx)}")
    print(f"  inventory: {len(vocab)}; match-state grid: {MATCH_GRID[0]}..{MATCH_GRID[-1]}")
    print("  score: held-out log P(sign sequence | observed length), nats/token")
    print("  controls: exact length/position/site/object and frequency/site/object")

    real = fit_grid(records, train_idx, test_idx, vocab, args.max_iter)
    print("\n=== held-out model selection on the real corpus ===")
    print(f"  unigram {real['uni']:.4f}; bigram {real['bi']:.4f} nats/token")
    print("  M   profile LL   delta unigram   delta bigram   EM iterations")
    for row in real["rows"]:
        mark = " *" if row is real["best"] else ""
        print(f"  {row['matches']:>2} {row['nats_token']:>11.4f} "
              f"{row['delta_unigram']:>15.4f} {row['delta_bigram']:>14.4f} "
              f"{row['iterations']:>15}{mark}")

    print("\n=== held-out deltas within site and object controls ===")
    print("  stratum                 texts  tokens  profile-unigram  profile-bigram")
    test_records = [records[i] for i in test_idx]
    strata = [
        ("Mohenjo-daro", lambda r: r["site"] == "SI1"),
        ("Harappa", lambda r: r["site"] == "SI2"),
        ("other sites", lambda r: r["site"] not in {"SI1", "SI2"}),
        ("seals", lambda r: r["object"] == "seal"),
        ("tablets", lambda r: r["object"] == "tablet"),
        ("other objects", lambda r: r["object"] not in {"seal", "tablet"}),
    ]
    for label, predicate in strata:
        indices = [i for i, rec in enumerate(test_records) if predicate(rec)]
        tokens = sum(len(test_records[i]["text"]) for i in indices)
        if not tokens:
            continue
        dp = (real["profile_ll"][indices].sum() - real["uni_ll"][indices].sum()) / tokens
        db = (real["profile_ll"][indices].sum() - real["bi_ll"][indices].sum()) / tokens
        print(f"  {label:<23} {len(indices):>5} {tokens:>7} {dp:>16.4f} {db:>15.4f}")

    surrogate_rows = []
    for run in range(args.surrogates):
        for kind, maker in (("position", positional_surrogate),
                            ("frequency", frequency_surrogate)):
            surrogate = maker(records, rng)
            fitted = fit_grid(surrogate, train_idx, test_idx, vocab, args.max_iter)
            surrogate_rows.append({"kind": kind, "run": run,
                                   **fitted["best"]})
        print(f"  completed surrogate replicate {run + 1}/{args.surrogates}", flush=True)

    print("\n=== the same selection on controlled surrogate corpora ===")
    summarize_surrogates(surrogate_rows)
    best = real["best"]
    position_delta = [r["delta_bigram"] for r in surrogate_rows
                      if r["kind"] == "position"]
    frequency_delta = [r["delta_bigram"] for r in surrogate_rows
                       if r["kind"] == "frequency"]
    position_p = ((1 + sum(x >= best["delta_bigram"] for x in position_delta)) /
                  (len(position_delta) + 1))
    frequency_p = ((1 + sum(x >= best["delta_bigram"] for x in frequency_delta)) /
                   (len(frequency_delta) + 1))
    survives = (best["delta_bigram"] > 0 and
                best["delta_bigram"] > np.quantile(position_delta, .975) and
                best["delta_bigram"] > np.quantile(frequency_delta, .975))
    print(f"  real best vs surrogate delta-bigram: p(position)={position_p:.4f}, "
          f"p(frequency)={frequency_p:.4f}")
    print(f"  predeclared template survival rule: {'PASS' if survives else 'FAIL'}")

    model = real["model"]
    train_encoded = [real["encoded"][i] for i in train_idx]
    occupancy = model.occupancy(train_encoded)
    inv_vocab = np.asarray(vocab)
    print("\n=== selected profile diagnostics (not selection criteria) ===")
    print("  state occupancy  delete   top emissions                         terminal mass")
    for j in range(model.m):
        top = np.argsort(model.theta[j])[::-1][:6]
        emissions = " ".join(f"{inv_vocab[k]}:{model.theta[j,k]:.3f}" for k in top)
        terminal_mass = sum(model.theta[j, vocab.index(g)] for g in TERMINAL if g in vocab)
        print(f"  M{j+1:<2} {occupancy[j]:>9.1%} {model.delete[j]:>7.1%} "
              f"{emissions:<38} {terminal_mass:>8.3f}")
    terminal_state = max(range(model.m), key=lambda j: sum(
        model.theta[j, vocab.index(g)] for g in TERMINAL if g in vocab))
    terminal_top = [int(inv_vocab[k]) for k in np.argsort(model.theta[terminal_state])[::-1][:20]]
    recovered = sorted(TERMINAL & set(terminal_top))
    print(f"  strongest terminal-mass state: M{terminal_state+1}; "
          f"known members among its top 20: {recovered}")

    result = {
        "seed": SEED, "records": len(records), "train": len(train_idx),
        "test": len(test_idx), "vocabulary": len(vocab),
        "real": {"unigram": real["uni"], "bigram": real["bi"],
                 "grid": real["rows"], "best": real["best"]},
        "surrogates": surrogate_rows, "position_p": position_p,
        "frequency_p": frequency_p, "survives": bool(survives),
        "occupancy": occupancy.tolist(), "delete": model.delete.tolist(),
        "terminal_state": terminal_state + 1, "terminal_recovered_top20": recovered,
    }
    json.dump(result, open("data/parsed/profile_hmm.json", "w"), indent=1)
    print("\nwrote data/parsed/profile_hmm.json")


if __name__ == "__main__":
    main()
