# Are the never-counted signs people in a hierarchy?

Script: `src/hierarchy.py`. Hypothesis: the 15 never-counted signs are roles in
a household or village — 400 as the head, others as members — and their
arrangement encodes rank.

## H1 — they do cluster together

| group | observed co-occurrences | expected | ratio |
|---|---|---|---|
| never-counted | 906 | 740.8 | **1.22** |
| counted | 471 | 496.6 | 0.95 |

Never-counted signs appear together more than chance; counted signs slightly
less. Consistent with a group of associated roles rather than one-owner-per-seal.
Strongest pairs: 60+920 at 6.9x expected, 741+920 at 4.2x, 100+740 at 1.9x.

## H2 — uniqueness does not discriminate

Both groups repeat within a text about 1% of the time (never-counted 24/1986,
counted 15/1463). No signal either way.

## H3 — the ordering is mostly slots, not rank

Raw result looked spectacular: **23 of 30** pairs strictly ordered, zero
transitivity violations. But that test is confounded. If sign A prefers position
0.3 and B prefers 0.9, A-before-B follows automatically with no ordering rule at
all.

Marginal positions (0 = text-initial, 1 = final):

```
920 .197   60 .306   741 .349   615 .369   742 .403   595 .531   435 .537
636 .557   690 .569  100 .644   740 .866    90 .869   400 .900   527 .926
151 .937
```

Controlling for this — simulating each sign's slot independently from its own
position distribution — **8 of 30 pairs survive**, down from 23. Real sequencing
constraints exist (60 before 741 at 0.97 observed vs 0.59 predicted; 920 before
60; 690 after 435) but two-thirds of the apparent hierarchy was just slot
preference.

## H4 — 400 is at the wrong end

Sign 400 sits at mean position **0.900**, near the text's end. So do 740 (.866),
90 (.869), 527 (.926), 151 (.937). If 400 were a head-of-household opening a
roster, it is in the wrong place. An authority-signs-last convention would
explain it, so this is suggestive rather than decisive.

## The problem the hypothesis cannot get past

**In any census you count the members.** Children, workers, livestock — that is
what a household or village record is *for*. These signs are never counted at
all: sign 400 has one numeral in 308 opportunities, sign 60 two in 173.

A roster whose entries cannot be enumerated is not a roster.

There is also a scale problem. Sign 740 appears in **943 of 1980 distinct
texts** — 48%. A father, or a king, in half of every document ever written is
implausible for a role term and quite ordinary for a grammatical or terminal
marker, which is what 740 (the "jar") is generally taken to be.

## Where this leaves it

The never-counted group is real and functionally distinct — it clusters, it
holds fixed positions, and 8 pairs carry genuine ordering beyond slot
preference. But the evidence points at these signs being the **frame** of a
formula (terminal markers, classifiers, grammatical elements) with the counted
signs as its **content**, rather than a cast of persons.

A weaker version survives: some never-counted signs could be titles or offices —
things named but not enumerated. That is compatible with everything here. What
the data will not support is the household reading specifically, because
households contain exactly the sort of thing you would count.
