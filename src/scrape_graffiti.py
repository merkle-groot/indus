"""Cache the public Tamil Nadu megalithic-graffiti API for round 40.

The API is unauthenticated but is still treated politely: this harvester sends
an identifying browser-style User-Agent, makes requests sequentially, waits
between network hits, and never re-fetches a cached response unless ``--force``
is supplied.  Raw JSON, the SPA bundle, and downloaded glyph images stay under
gitignored ``data/graffiti/``; only analysis aggregates are committed.

The default ``core`` phase downloads the collection-level endpoints, every
site detail, and concordances for the 42 advertised base signs.  ``audit`` also
tries plausible undocumented ``filter`` groupings and extracts URL-like strings
from the current JavaScript bundle.  ``full`` additionally downloads all
catalogue glyphs, the referenced Indus images, and the convergence control.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import http.client
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/graffiti"
RAW = DATA / "raw"
IMAGES = DATA / "images"
BASE = "https://api.tamilknowledgecampus.in/graffiti/"
SPA = "https://tngraffiti.in/"
IMAGE_BASE = "https://graffiti-signs.s3.us-east-1.amazonaws.com/"
CONTROL_RECORD = "https://zenodo.org/api/records/7965768"
DELAY_SECONDS = 0.25
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36 "
    "indus-round40-scholarly-harvester/1.0"
)


def slug(value: str) -> str:
    value = re.sub(r"[^A-Za-z0-9._-]+", "-", value).strip("-")
    return value[:180] or "index"


class CacheClient:
    def __init__(self, force: bool = False, delay: float = DELAY_SECONDS):
        self.force = force
        self.delay = delay
        self.network_requests = 0
        self.connections = {}

    def cached_error(self, path: Path) -> bool:
        """Whether a previous allowed HTTP error is already cached for this target."""
        return any(path.parent.glob(path.name + ".http-*"))

    def fetch(self, url: str, path: Path, *, allow_error: bool = False) -> bytes | None:
        if path.exists() and not self.force:
            return path.read_bytes()
        if allow_error and not self.force and self.cached_error(path):
            return None
        path.parent.mkdir(parents=True, exist_ok=True)
        request = urllib.request.Request(
            url,
            headers={"User-Agent": USER_AGENT, "Accept": "application/json,text/html,*/*"},
        )
        if self.network_requests:
            time.sleep(self.delay)
        try:
            with urllib.request.urlopen(request, timeout=90) as response:
                body = response.read()
        except urllib.error.HTTPError as exc:
            if allow_error:
                body = exc.read()
                error_path = path.with_suffix(path.suffix + f".http-{exc.code}")
                error_path.write_bytes(body)
                self.network_requests += 1
                return None
            raise
        path.write_bytes(body)
        self.network_requests += 1
        return body

    def fetch_persistent(self, url: str, path: Path, *, allow_error: bool = False):
        """Fetch through a reused HTTPS connection (important for many S3 glyphs)."""
        if path.exists() and not self.force:
            return path.read_bytes()
        if allow_error and not self.force and self.cached_error(path):
            return None
        path.parent.mkdir(parents=True, exist_ok=True)
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme != "https":
            return self.fetch(url, path, allow_error=allow_error)
        if self.network_requests:
            time.sleep(self.delay)
        connection = self.connections.get(parsed.netloc)
        if connection is None:
            connection = http.client.HTTPSConnection(parsed.netloc, timeout=90)
            self.connections[parsed.netloc] = connection
        target = parsed.path + (("?" + parsed.query) if parsed.query else "")
        try:
            connection.request("GET", target, headers={"User-Agent": USER_AGENT,
                                                        "Accept": "*/*"})
            response = connection.getresponse()
            body = response.read()
        except (OSError, http.client.HTTPException):
            connection.close()
            connection = http.client.HTTPSConnection(parsed.netloc, timeout=90)
            self.connections[parsed.netloc] = connection
            connection.request("GET", target, headers={"User-Agent": USER_AGENT,
                                                        "Accept": "*/*"})
            response = connection.getresponse()
            body = response.read()
        self.network_requests += 1
        if response.status >= 400:
            if allow_error:
                path.with_suffix(path.suffix + f".http-{response.status}").write_bytes(body)
                return None
            raise RuntimeError(f"HTTP {response.status} for {url}")
        if 300 <= response.status < 400:
            location = response.getheader("Location")
            if not location:
                raise RuntimeError(f"redirect without Location for {url}")
            return self.fetch(urllib.parse.urljoin(url, location), path,
                              allow_error=allow_error)
        path.write_bytes(body)
        return body

    def json(self, endpoint: str, *, params: dict[str, str] | None = None,
             name: str | None = None, allow_error: bool = False):
        query = urllib.parse.urlencode(params or {})
        url = urllib.parse.urljoin(BASE, endpoint)
        if query:
            url += "?" + query
        label = name or slug(endpoint + ("-" + query if query else ""))
        body = self.fetch_persistent(url, RAW / f"{label}.json", allow_error=allow_error)
        if body is None:
            return None
        return json.loads(body)


def records(payload):
    """Return the first evident list of records without assuming an API wrapper."""
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        for key in ("data", "results", "result", "items", "signs", "sites"):
            if isinstance(payload.get(key), list):
                return payload[key]
    return []


def find_values(value, key_pattern):
    pattern = re.compile(key_pattern, re.I)
    found = []
    if isinstance(value, dict):
        for key, child in value.items():
            if pattern.search(str(key)) and isinstance(child, (str, int, float)):
                found.append(child)
            found.extend(find_values(child, key_pattern))
    elif isinstance(value, list):
        for child in value:
            found.extend(find_values(child, key_pattern))
    return found


def distinct_strings(payload, key_pattern):
    return sorted({str(x).strip() for x in find_values(payload, key_pattern)
                   if str(x).strip()})


def harvest_core(client: CacheClient):
    payloads = {}
    for endpoint, name, params in (
        ("sites", "sites", None),
        ("filter", "filter-sign", {"groupBy": "sign"}),
        ("base-sign", "base-sign", None),
        ("fields-symbols", "fields-symbols", None),
        ("options", "options", None),
        ("indus", "indus", None),
    ):
        payloads[name] = client.json(endpoint, params=params, name=name)

    # Prefer the explicit options vocabulary; fall back to the sites payload.
    site_names = distinct_strings(payloads["options"], r"^(site|siteName|site_name)$")
    if len(site_names) < 10:
        site_names = distinct_strings(payloads["sites"], r"^(site|siteName|site_name|name)$")
    for site in site_names:
        client.json("sites/" + urllib.parse.quote(site, safe=""),
                    name="site-" + slug(site), allow_error=True)
        # This filtered aggregate supplies sign x depth within one excavation;
        # the unfiltered /sites payload contains only separate marginals.
        client.json("filter", params={"site": site},
                    name="filter-site-" + slug(site), allow_error=True)

    # Depth must not be pooled across sites or ceramic/context classes.  Query
    # only combinations actually advertised by each site's marginal payload;
    # this yields sign x depth within site x ware x habitation strata.
    site_rows = {str(row.get("site")): row for row in records(payloads["sites"])}
    for site in site_names:
        row = site_rows.get(site, {})
        site_records = row.get("records", {})
        wares = [str(x["key"]) for x in site_records.get("material", [])] or [None]
        habitats = [str(x["key"]) for x in site_records.get("habitation", [])] or [None]
        for ware in wares:
            for habitat in habitats:
                params = {"site": site}
                if ware:
                    params["material"] = ware
                if habitat:
                    params["habitation"] = habitat
                signature = "|".join(str(params.get(k, ""))
                                     for k in ("site", "material", "habitation"))
                suffix = hashlib.sha256(signature.encode()).hexdigest()[:10]
                name = "filter-stratum-" + slug(site)[:70] + "-" + suffix
                client.json("filter", params=params, name=name, allow_error=True)

    base_ids = distinct_strings(
        payloads["base-sign"],
        r"^(id|sign|signId|sign_id|baseSign|base_sign|b_gov_sign)$")
    # Numeric ids only: names, counts, and image paths can share loose key names.
    base_ids = sorted({x for x in base_ids if re.fullmatch(r"\d+", x)}, key=int)
    for sign_id in base_ids:
        client.json(f"sign/{sign_id}", name=f"sign-{int(sign_id):04d}",
                    allow_error=True)
        client.json("concordance", params={"signQuery": sign_id},
                    name=f"concordance-{int(sign_id):04d}", allow_error=True)
    return payloads, site_names, base_ids


def audit(client: CacheClient):
    attempted = {}
    # These include common API groupings and the dimensions advertised by
    # /options.  HTTP failures are cached separately and reported, not hidden.
    for group in ("sherd", "pottery", "accession", "object", "record", "site",
                  "ware", "habitation", "depth", "sign"):
        attempted[group] = client.json(
            "filter", params={"groupBy": group}, name="audit-filter-" + group,
            allow_error=True)

    html = client.fetch(SPA, RAW / "spa-index.html")
    bundle_urls = []
    if html:
        bundle_urls = sorted(set(re.findall(r'(?:src|href)="([^"]+\.js(?:\?[^"]*)?)"',
                                            html.decode("utf-8", "replace"))))
    for i, path in enumerate(bundle_urls):
        url = urllib.parse.urljoin(SPA, path)
        client.fetch(url, RAW / f"spa-bundle-{i:02d}.js", allow_error=True)

    report = {
        "filter_groupby_attempts": {
            key: ({"returned": len(records(value)),
                   "top_level_type": type(value).__name__} if value is not None
                  else {"http_error": True})
            for key, value in attempted.items()
        },
        "bundle_urls": bundle_urls,
    }
    (RAW / "audit-summary.json").write_text(json.dumps(report, indent=2) + "\n")
    return report


def collect_image_references(value):
    refs = set()
    if isinstance(value, dict):
        for key, child in value.items():
            if isinstance(child, str) and re.search(r"image|photo|url|path", key, re.I):
                if re.search(r"\.(?:png|jpe?g|webp|gif|svg)(?:\?|$)", child, re.I):
                    refs.add(child)
            refs.update(collect_image_references(child))
    elif isinstance(value, list):
        for child in value:
            refs.update(collect_image_references(child))
    return refs


def image_url(ref: str) -> str:
    if ref.startswith(("http://", "https://")):
        return ref
    return urllib.parse.urljoin(IMAGE_BASE, ref.lstrip("/"))


def embedded_json(bundle: str, variable: str):
    marker = variable + "=JSON.parse('"
    start = bundle.find(marker)
    if start < 0:
        raise RuntimeError(f"could not find embedded {variable} mapping in SPA bundle")
    start += len(marker)
    end = bundle.find("')", start)
    if end < 0:
        raise RuntimeError(f"unterminated embedded {variable} mapping")
    # ast handles the JavaScript string's ordinary backslash escapes before
    # json parses its content.
    return json.loads(ast.literal_eval("'" + bundle[start:end] + "'"))


def download_glyphs(client: CacheClient, filter_payload):
    bundles = sorted(RAW.glob("spa-bundle-*.js"))
    if not bundles:
        audit(client)
        bundles = sorted(RAW.glob("spa-bundle-*.js"))
    bundle = bundles[-1].read_text()
    drawing_map = {str(x["dsign"]).strip(): str(x["rsign"])
                   for x in embedded_json(bundle, "va")}
    sign_ids = [str(row["sign"]).strip() for row in records(filter_payload)]
    missing, manifest = [], []
    for sign_id in sign_ids:
        if sign_id.endswith("C"):
            ref = f"composites/{sign_id}.png"
        elif sign_id in drawing_map:
            ref = f"bv-signs/{drawing_map[sign_id]}.png"
        else:
            missing.append(sign_id)
            continue
        path = IMAGES / ref
        body = client.fetch_persistent(image_url(ref), path, allow_error=True)
        manifest.append({"sign": sign_id, "source": ref,
                         "cache": str(path.relative_to(DATA)),
                         "downloaded": body is not None})
    payload = {"images": manifest, "missing_mapping": sorted(missing)}
    (RAW / "graffiti-image-manifest.json").write_text(
        json.dumps(payload, indent=2) + "\n")
    return len(sign_ids), sum(x["downloaded"] for x in manifest), len(missing)


def download_indus_crosswalk_images(client: CacheClient, crosswalk):
    manifest = []
    for row in crosswalk:
        for field in ("sealimg", "potimg"):
            if not row.get(field):
                continue
            ref = "indus/" + str(row[field]).strip() + ".png"
            path = IMAGES / ref
            body = client.fetch_persistent(image_url(ref), path, allow_error=True)
            manifest.append({"field": field, "source": ref,
                             "cache": str(path.relative_to(DATA)),
                             "downloaded": body is not None})
    (RAW / "indus-image-manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n")
    return len(manifest), sum(x["downloaded"] for x in manifest)


def download_control(client: CacheClient):
    body = client.fetch(CONTROL_RECORD, RAW / "control-zenodo-7965768.json")
    metadata = json.loads(body)
    candidates = [x for x in metadata.get("files", [])
                  if x.get("key") == "Pottery_Marks_PDF.zip"]
    if len(candidates) != 1:
        raise RuntimeError("Zenodo pottery-mark PDF archive is absent or ambiguous")
    record = candidates[0]
    url = record.get("links", {}).get("self") or record.get("links", {}).get("content")
    path = DATA / "control" / record["key"]
    archive = client.fetch(url, path)
    checksum = str(record.get("checksum", ""))
    if checksum.startswith("md5:"):
        observed = hashlib.md5(archive).hexdigest()  # nosec - source integrity only
        if observed != checksum.split(":", 1)[1]:
            raise RuntimeError(f"control checksum mismatch: {observed}")
    return {"file": record["key"], "bytes": len(archive), "checksum": checksum,
            "license": metadata.get("metadata", {}).get("license", {})}


def harvest_full(client: CacheClient, filter_payload):
    graffiti = download_glyphs(client, filter_payload)
    indus = download_indus_crosswalk_images(client,
                                             json.loads((RAW / "indus.json").read_text()))
    control = download_control(client)
    return {"graffiti": graffiti, "indus_crosswalk": indus, "control": control}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("phase", choices=("core", "audit", "full"), default="core", nargs="?")
    parser.add_argument("--force", action="store_true",
                        help="replace cached successful responses")
    parser.add_argument("--delay", type=float, default=DELAY_SECONDS,
                        help="seconds between network requests (default: 0.25)")
    args = parser.parse_args()
    client = CacheClient(force=args.force, delay=args.delay)
    payloads, site_names, base_ids = harvest_core(client)
    report = None
    if args.phase in ("audit", "full"):
        report = audit(client)
    full_counts = None
    if args.phase == "full":
        full_counts = harvest_full(client, payloads["filter-sign"])
    print(json.dumps({
        "phase": args.phase,
        "network_requests": client.network_requests,
        "sites_discovered": len(site_names),
        "base_ids_discovered": len(base_ids),
        "audit": report,
        "full_assets": full_counts,
        "cache": str(DATA.relative_to(ROOT)),
    }, indent=2))


if __name__ == "__main__":
    main()
