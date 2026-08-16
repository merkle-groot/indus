"""Harvest harappa.com text for anything bearing on the sign analysis.

harappa.com sits behind Cloudflare and 403s programmatic requests. Two modes:

  --archive  (default) pull the pages from the Internet Archive, which mirrors
             the site publicly and serves it without a challenge. Proven to
             work; this is what produced notes/23-harappa-com.md.
  --live     hit harappa.com directly with a browser User-Agent. Run this
             yourself if you want it; it is your session and your call.

Both modes are deliberately polite: single-threaded, one request at a time, a
delay between requests, exponential backoff on 429/503, and an on-disk cache so
a re-run costs nothing. Output is text only -- no images, nothing republished.

  python3 src/scrape_harappa.py --list          # build the URL list, no fetching
  python3 src/scrape_harappa.py --limit 200     # fetch 200 pages via the archive
  python3 src/scrape_harappa.py --live --limit 200
  python3 src/scrape_harappa.py --scan          # rank what has been fetched

Everything lands in data/harappa/ , which is gitignored -- the text is
harappa.com's, not ours, and does not belong in a public repo.
"""
import argparse
import html
import json
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

OUT = Path("data/harappa")
PAGES = OUT / "pages"
URLS = OUT / "urls.txt"
INDEX = OUT / "index.json"
CDX = ("http://web.archive.org/cdx/search/cdx?url=harappa.com*&fl=original"
       "&collapse=urlkey&limit=40000&filter=statuscode:200")
UA_ARCHIVE = "indus-script-research (+https://github.com/merkle-groot/indus)"
UA_LIVE = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
           "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")

# terms that would make a page worth reading for this project
TERMS = [
    "sign", "script", "inscription", "seal", "sign list", "corpus", "cisi",
    "mahadevan", "parpola", "wells", "fuls", "concordance", "grapheme",
    "allograph", "jar sign", "fish sign", "arrow sign", "numeral", "stroke",
    "frequency", "sequence", "segmentation", "sign frequency", "positional",
]
SKIP_EXT = (".jpg", ".jpeg", ".png", ".gif", ".css", ".js", ".pdf", ".ico",
            ".svg", ".zip", ".mp3", ".mp4", ".woff", ".ttf")


def build_urls():
    OUT.mkdir(parents=True, exist_ok=True)
    print("fetching the archive URL list ...")
    req = urllib.request.Request(CDX, headers={"User-Agent": UA_ARCHIVE})
    raw = urllib.request.urlopen(req, timeout=120).read().decode(errors="replace")
    seen, keep = set(), []
    for line in raw.splitlines():
        u = line.strip()
        if not u:
            continue
        u = u.split("?")[0].rstrip("/")
        u = re.sub(r"^http://", "https://", u)
        u = re.sub(r"^https://harappa\.com", "https://www.harappa.com", u)
        low = u.lower()
        if low.endswith(SKIP_EXT) or "/cdn-cgi/" in low:
            continue
        # crawler artefacts: a second scheme or host inside the path
        if low.count(".com") > 1 or "http" in low[8:]:
            continue
        if u in seen:
            continue
        seen.add(u)
        keep.append(u)
    keep.sort()
    URLS.write_text("\n".join(keep))
    print(f"  {len(keep)} unique content URLs -> {URLS}")
    return keep


def strip_html(t):
    t = re.sub(r"(?s)<(script|style|nav|header|footer|form).*?</\1>", " ", t)
    title = re.search(r"(?s)<title[^>]*>(.*?)</title>", t)
    t = re.sub(r"(?s)<[^>]+>", "\n", t)
    t = html.unescape(t)
    lines = [l.strip() for l in t.split("\n")]
    body = "\n".join(l for l in lines if len(l) > 40)
    return (html.unescape(title.group(1)).strip() if title else ""), body


def fetch(url, live, tries=4):
    target = url if live else \
        "http://web.archive.org/web/2023id_/" + url
    ua = UA_LIVE if live else UA_ARCHIVE
    delay = 3.0
    for k in range(tries):
        try:
            req = urllib.request.Request(target, headers={"User-Agent": ua})
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as e:
            if e.code in (429, 503, 504):
                time.sleep(delay)
                delay *= 2
                continue
            return None
        except Exception:
            time.sleep(delay)
            delay *= 2
    return None


def harvest(live, limit, pause):
    PAGES.mkdir(parents=True, exist_ok=True)
    urls = URLS.read_text().splitlines() if URLS.exists() else build_urls()
    idx = json.loads(INDEX.read_text()) if INDEX.exists() else {}
    todo = [u for u in urls if u not in idx][:limit]
    print(f"{len(idx)} cached, fetching {len(todo)} "
          f"({'LIVE harappa.com' if live else 'Internet Archive'})")
    for n, u in enumerate(todo, 1):
        raw = fetch(u, live)
        if raw:
            title, body = strip_html(raw)
            name = re.sub(r"[^a-z0-9]+", "-", u.split("harappa.com/")[-1].lower())[:120]
            (PAGES / f"{name or 'index'}.txt").write_text(f"{u}\n{title}\n\n{body}")
            idx[u] = {"title": title, "chars": len(body), "file": f"{name}.txt"}
        else:
            idx[u] = {"title": None, "chars": 0, "file": None}
        if n % 20 == 0 or n == len(todo):
            INDEX.write_text(json.dumps(idx, indent=1))
            ok = sum(1 for v in idx.values() if v["chars"])
            print(f"  {n}/{len(todo)}   {ok} pages with text")
        time.sleep(pause)
    INDEX.write_text(json.dumps(idx, indent=1))


def scan():
    idx = json.loads(INDEX.read_text())
    rows = []
    for u, v in idx.items():
        if not v.get("file"):
            continue
        p = PAGES / v["file"]
        if not p.exists():
            continue
        txt = p.read_text().lower()
        hits = {t: txt.count(t) for t in TERMS if t in txt}
        score = sum(hits.values())
        if score:
            rows.append((score, u, v["title"], hits))
    rows.sort(reverse=True)
    print(f"{len(rows)} pages mention at least one term, of "
          f"{sum(1 for v in idx.values() if v.get('chars'))} fetched\n")
    for s, u, t, h in rows[:40]:
        top = ", ".join(f"{k}:{n}" for k, n in
                        sorted(h.items(), key=lambda kv: -kv[1])[:5])
        print(f"  {s:>5}  {(t or '')[:52]:<54} {top}")
        print(f"         {u}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--live", action="store_true",
                    help="fetch harappa.com directly instead of the archive")
    ap.add_argument("--list", action="store_true", help="build the URL list only")
    ap.add_argument("--scan", action="store_true", help="rank what is cached")
    ap.add_argument("--limit", type=int, default=250)
    ap.add_argument("--pause", type=float, default=1.5,
                    help="seconds between requests")
    a = ap.parse_args()
    if a.list:
        build_urls()
    elif a.scan:
        scan()
    else:
        harvest(a.live, a.limit, a.pause)
        print("\nnow run:  python3 src/scrape_harappa.py --scan")
