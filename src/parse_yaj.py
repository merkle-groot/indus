"""Parse the yajnadevam population-script.sql into plain JSON.

We only want the raw epigraphic data (which signs, in what order, on which
artifact) -- not the author's decipherment claims.
"""
import json
import re
import sys
from pathlib import Path

SQL = Path(sys.argv[1] if len(sys.argv) > 1 else "data/yaj/population-script.sql")
OUT = Path(sys.argv[2] if len(sys.argv) > 2 else "data/parsed")


def rows(table, text):
    """Yield tuples of python values from `INSERT INTO <table> ... VALUES (...),(...);`"""
    m = re.search(r"INSERT INTO %s\s*\([^)]*\)\s*VALUES\s*(.*?);\s*\n" % table, text, re.S)
    if not m:
        return
    for tup in re.finditer(r"\(((?:[^()\"]|\"(?:[^\"\\]|\\.)*\")*)\)", m.group(1)):
        yield [coerce(f) for f in split_fields(tup.group(1))]


def split_fields(body):
    """Split a VALUES tuple on commas that are outside double-quoted strings."""
    out, buf, in_str, esc = [], [], False, False
    for ch in body:
        if esc:
            buf.append(ch)
            esc = False
        elif ch == "\\":
            buf.append(ch)
            esc = True
        elif ch == '"':
            in_str = not in_str
            buf.append(ch)
        elif ch == "," and not in_str:
            out.append("".join(buf))
            buf = []
        else:
            buf.append(ch)
    out.append("".join(buf))
    return out


def coerce(f):
    f = f.strip()
    if f.startswith('"'):
        return f[1:-1].replace('\\"', '"')
    if f.upper() == "NULL" or f == "":
        return None
    try:
        return float(f) if "." in f else int(f)
    except ValueError:
        return f


text = SQL.read_text(encoding="utf-8", errors="replace")

seals = {r[0]: {"seal_id": r[0], "site": r[1], "material": r[2], "cisi": r[3]}
         for r in rows("SEAL", text)}
for sid, complete, direction in ((r[0], r[1], r[2]) for r in rows("INSCRIPTION", text)):
    if sid in seals:
        seals[sid]["complete"] = complete == "Y"
        seals[sid]["direction"] = direction
for sid, desc in ((r[0], r[1]) for r in rows("ICONOGRAPHY", text)):
    if sid in seals:
        seals[sid]["iconography"] = desc

seq = {}
for sid, gid, idx in ((r[0], r[1], r[2]) for r in rows("GLYPHSEQUENCE", text)):
    seq.setdefault(sid, []).append((idx, gid))
for sid, pairs in seq.items():
    if sid in seals:
        seals[sid]["glyphs"] = [g for _, g in sorted(pairs)]

glyphs = {r[0]: {"glyph_id": r[0], "unicode": r[1]} for r in rows("GLYPH", text)}
sites = {r[0]: r[1] for r in rows("SITE", text)}

OUT.mkdir(parents=True, exist_ok=True)
texts = [s for s in seals.values() if s.get("glyphs")]
(OUT / "inscriptions.json").write_text(json.dumps(texts, indent=1, ensure_ascii=False))
(OUT / "glyphs.json").write_text(json.dumps(list(glyphs.values()), indent=1, ensure_ascii=False))
(OUT / "sites.json").write_text(json.dumps(sites, indent=1, ensure_ascii=False))

tokens = sum(len(s["glyphs"]) for s in texts)
print(f"artifacts in SEAL table : {len(seals)}")
print(f"with a glyph sequence   : {len(texts)}")
print(f"total sign tokens       : {tokens}")
print(f"distinct signs used     : {len({g for s in texts for g in s['glyphs']})}")
print(f"GLYPH table entries     : {len(glyphs)}")
print(f"sites                   : {len(sites)}")
