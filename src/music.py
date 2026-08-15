"""Could the signs be musical notation?

The discriminating property is repetition. A melody reuses its pitches
constantly -- that is what makes it a melody. Written language mostly does not
repeat the same word inside a five-word phrase.

  M1 inventory  -- a pitch set is small. How big is this one?
  M2 repetition -- do signs recur within a text, and is that more or less than
                   you would get by drawing signs at random from the corpus's
                   own frequency distribution? Below independence means the
                   script actively AVOIDS repetition, which no melody does.
  M3 immediate  -- melodies repeat a note back-to-back often. Do signs?
  M4 profile    -- within a scale, pitch use is fairly even and every pitch
                   recurs. A vocabulary is steeply skewed with many hapax.
"""
import json
from collections import Counter

import numpy as np

RNG = np.random.default_rng(0)
N_SIM = 2000

lines = json.loads(open("data/parsed/lines.json").read())
texts = [tuple(l["signs"]) for l in lines if l["signs"]]
tok = [g for t in texts for g in t]
freq = Counter(tok)
V = sorted(freq)
p = np.array([freq[g] for g in V], float)
p /= p.sum()

print("=== M1: inventory size ===")
print(f"  distinct signs            : {len(V)}")
print(f"  tokens                    : {len(tok)}")
print(f"  signs seen exactly once   : {sum(1 for g in V if freq[g] == 1)} "
      f"({sum(1 for g in V if freq[g]==1)/len(V):.0%})")
print(f"  mean sequence length      : {len(tok)/len(texts):.2f}")
print("  a pitch set is typically 5-12; ornaments might push it to ~20-30")

# ------------------------------------------------------------------ M2
print("\n=== M2: repetition within a sequence ===")
obs_rep = sum(1 for t in texts if len(set(t)) < len(t))
obs_tok = sum(len(t) - len(set(t)) for t in texts)
sim_rep, sim_tok = [], []
lens = [len(t) for t in texts]
for _ in range(N_SIM):
    r = tk = 0
    draws = RNG.choice(len(V), size=sum(lens), p=p)
    i = 0
    for L in lens:
        s = draws[i:i + L]
        i += L
        u = len(set(s.tolist()))
        r += u < L
        tk += L - u
    sim_rep.append(r)
    sim_tok.append(tk)
sim_rep, sim_tok = np.array(sim_rep), np.array(sim_tok)
print(f"  texts containing a repeated sign : {obs_rep} / {len(texts)} "
      f"({obs_rep/len(texts):.1%})")
print(f"  expected if signs were drawn independently from their own")
print(f"  corpus frequencies               : {sim_rep.mean():.0f} "
      f"({sim_rep.mean()/len(texts):.1%})  sd {sim_rep.std():.1f}")
z = (obs_rep - sim_rep.mean()) / sim_rep.std()
print(f"  z = {z:+.1f}   -> the script repeats "
      f"{'LESS' if z < 0 else 'MORE'} than chance")
print(f"  repeated tokens: observed {obs_tok}, expected {sim_tok.mean():.0f}")

# ------------------------------------------------------------------ M3
print("\n=== M3: immediate repetition (a sign directly after itself) ===")
adj = sum(1 for t in texts for x, y in zip(t, t[1:]) if x == y)
bigrams = sum(len(t) - 1 for t in texts)
exp_adj = bigrams * float((p ** 2).sum())
print(f"  observed  : {adj} / {bigrams} adjacent pairs ({adj/bigrams:.3%})")
print(f"  expected  : {exp_adj:.1f} ({exp_adj/bigrams:.3%})")
print("  melodies do this constantly; here it is essentially absent")

# ------------------------------------------------------------------ M4
print("\n=== M4: usage profile ===")
top = freq.most_common()
for k in (5, 12, 20, 50):
    share = sum(c for _, c in top[:k]) / len(tok)
    print(f"  top {k:>3} signs cover {share:>5.1%} of all tokens")
print(f"  a 7-note scale would put ~100% of tokens in the top 7; "
      f"here the top 7 cover {sum(c for _,c in top[:7])/len(tok):.0%}")

# how many signs would a "scale" need to cover 90%?
run = 0
for i, (_, c) in enumerate(top, 1):
    run += c
    if run / len(tok) >= .90:
        print(f"  signs needed to cover 90% of tokens: {i}")
        break
