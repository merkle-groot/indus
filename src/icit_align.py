"""Is our corpus numbering the same as ICIT's (Wells glyph codes)?

The ICIT online-database documentation (Fuls 2010, public at
epigraphica.de/indus/help_onlinedatabase.pdf) prints worked examples that
contain real text sequences in Wells's 3-digit sign codes, and states that the
sign cluster 400-740-176 "occurs 36 times on TAB:B, TAB:C, and TAB:I from
Harappa".

If our (Yajnadevam-derived) numbering is the same enumeration, that cluster --
mirror-reversed, because ICIT prints texts with the initial sign on the left
while our lines.json stores reading order the other way (see notes/27) -- should
appear about 36 times in our corpus, concentrated on Harappa tablets.

Run: .venv/bin/python3 src/icit_align.py
"""
import json
import collections

LINES = json.load(open("data/parsed/lines.json"))
INS = {i["cisi"]: i for i in json.load(open("data/parsed/inscriptions.json"))}
SITES = json.load(open("data/parsed/sites.json"))


def contains(seq, sub):
    m = len(sub)
    return any(seq[i:i + m] == sub for i in range(len(seq) - m + 1))


# ICIT documented example sequences (Wells codes), and their mirror reversals.
ICIT_EXAMPLES = {
    "400-740-176 (cluster, 36x Harappa tablets)": [400, 740, 176],
    "407-032-520-100-585-017-231 (MD seal)": [407, 32, 520, 100, 585, 17, 231],
    "520-033-706-233-002-817-798": [520, 33, 706, 233, 2, 817, 798],
    "033-705 (cluster)": [33, 705],
    "520-220-415-060-920": [520, 220, 415, 60, 920],
}


def main():
    print(f"corpus: {len(LINES)} lines\n")
    print(f"{'sequence':52} {'as-printed':>10} {'reversed':>9}")
    for name, sub in ICIT_EXAMPLES.items():
        fwd = sum(contains(l["signs"], sub) for l in LINES)
        rev = sum(contains(l["signs"], sub[::-1]) for l in LINES)
        print(f"{name:52} {fwd:>10} {rev:>9}")

    # The decisive one: 400-740-176 reversed, with provenance.
    sub = [176, 740, 400]
    hit = [l for l in LINES if contains(l["signs"], sub)]
    st = collections.Counter()
    ob = collections.Counter()
    for l in hit:
        st[SITES.get(l.get("site"), l.get("site"))] += 1
        i = INS.get(l.get("artifact"))
        if i:
            ob[i["obj_class"]] += 1
    print(f"\n[176,740,400] contiguous: {len(hit)} lines   (ICIT: 36x)")
    print(f"  sites : {dict(st)}")
    print(f"  object: {dict(ob)}")
    print(f"  distinct texts: {len(set(tuple(l['signs']) for l in hit))}")


if __name__ == "__main__":
    main()
