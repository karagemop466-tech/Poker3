#!/usr/bin/env python3
"""Poll only curated official URLs and record change fingerprints.

The monitor is deliberately read-only with respect to research facts. It updates a
separate state file, never rewrites tournament/hotel values or eligibility labels.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import html
from html.parser import HTMLParser
import json
import re
import socket
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import HTTPRedirectHandler, Request, build_opener

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA = ROOT / "site/data.json"
DEFAULT_STATE = ROOT / "site/data/source-monitor.json"
MAX_BYTES = 16 * 1024 * 1024
USER_AGENT = "VegasPokerPlannerSourceMonitor/1.0 (+https://github.com/karagemop466-tech/Poker3)"

# Limit network requests to known official hosts. Booking/search endpoints are kept
# out of this list by `monitor: false` in the curated source register.
OFFICIAL_HOSTS = {
    "www.venetianlasvegas.com", "cdn.wynnresorts.com", "www.wynnlasvegas.com",
    "reservations.wynnlasvegas.com", "aria.mgmresorts.com", "bellagio.mgmresorts.com",
    "mgmgrand.mgmresorts.com", "assets.contentstack.io", "www.mgmresorts.com",
    "www.worldpokertour.com", "worldpokertour.com", "wptmedia-mig.s3.amazonaws.com",
    "treasureisland.com", "www.treasureisland.com", "www.caesars.com",
}


class OfficialRedirectHandler(HTTPRedirectHandler):
    """Follow redirects only when their destination remains on an approved host."""

    def redirect_request(self, request, response, code, message, headers, new_url):
        parsed = urlparse(new_url)
        if parsed.scheme != "https" or parsed.hostname not in OFFICIAL_HOSTS:
            raise HTTPError(new_url, code, "Refusing redirect outside official host allowlist", headers, response)
        return super().redirect_request(request, response, code, message, headers, new_url)


def open_official(request: Request, timeout: int):
    return build_opener(OfficialRedirectHandler()).open(request, timeout=timeout)


class TextExtractor(HTMLParser):
    """Extract stable visible text; ignore scripts/styles and hidden markup."""

    SKIP = {"script", "style", "noscript", "svg", "iframe", "template"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.depth = 0
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() in self.SKIP:
            self.depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() in self.SKIP and self.depth:
            self.depth -= 1

    def handle_data(self, data: str) -> None:
        if not self.depth:
            normalized = " ".join(data.split())
            if normalized:
                self.parts.append(normalized)


def normalized_body(body: bytes, content_type: str) -> bytes:
    """Normalize HTML/text before hashing; binary PDFs are hashed byte-for-byte."""
    mime = content_type.split(";", 1)[0].strip().lower()
    if mime in {"text/html", "application/xhtml+xml"}:
        charset_match = re.search(r"charset=([\w.-]+)", content_type, re.I)
        charset = charset_match.group(1) if charset_match else "utf-8"
        try:
            decoded = body.decode(charset, errors="replace")
        except LookupError:
            decoded = body.decode("utf-8", errors="replace")
        parser = TextExtractor()
        parser.feed(decoded)
        return " ".join(parser.parts).encode("utf-8")
    if mime.startswith("text/") or mime in {"application/json", "application/xml", "text/xml"}:
        charset_match = re.search(r"charset=([\w.-]+)", content_type, re.I)
        charset = charset_match.group(1) if charset_match else "utf-8"
        try:
            text = body.decode(charset, errors="replace")
        except LookupError:
            text = body.decode("utf-8", errors="replace")
        return " ".join(html.unescape(text).split()).encode("utf-8")
    return body


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def validate_official_source(source: dict[str, Any]) -> str | None:
    parsed = urlparse(str(source.get("url", "")))
    if parsed.scheme != "https" or parsed.hostname not in OFFICIAL_HOSTS:
        return f"Refusing non-approved official URL: {source.get('url', '')}"
    if not source.get("id") or not source.get("name"):
        return "Source record needs an id and name."
    return None


def fetch_one(source: dict[str, Any], previous: dict[str, Any] | None = None, timeout: int = 20, max_bytes: int = MAX_BYTES) -> dict[str, Any]:
    """Fetch one source; return a result record without mutating either input."""
    previous = previous or {}
    invalid = validate_official_source(source)
    base = {"id": source.get("id", ""), "name": source.get("name", ""), "url": source.get("url", ""), "checkedAt": utc_now()}
    if invalid:
        return {**base, "status": "failure", "error": invalid}
    headers = {"User-Agent": USER_AGENT, "Accept": "text/html,application/xhtml+xml,application/pdf,text/plain,application/xml;q=0.9,*/*;q=0.7"}
    if previous.get("etag"):
        headers["If-None-Match"] = previous["etag"]
    if previous.get("lastModified"):
        headers["If-Modified-Since"] = previous["lastModified"]
    request = Request(source["url"], headers=headers, method="GET")
    try:
        with open_official(request, timeout=timeout) as response:
            status_code = getattr(response, "status", 200)
            content_type = response.headers.get("Content-Type", "application/octet-stream")
            declared_length = response.headers.get("Content-Length")
            if declared_length and int(declared_length) > max_bytes:
                raise ValueError(f"Response too large ({declared_length} bytes; limit {max_bytes}).")
            body = response.read(max_bytes + 1)
            if len(body) > max_bytes:
                raise ValueError(f"Response exceeded {max_bytes} byte limit.")
            normalized = normalized_body(body, content_type)
            digest = hashlib.sha256(normalized).hexdigest()
            return {
                **base,
                "statusCode": status_code,
                "status": "fetched",
                "sha256": digest,
                "contentType": content_type.split(";", 1)[0].strip().lower(),
                "etag": response.headers.get("ETag"),
                "lastModified": response.headers.get("Last-Modified"),
                "contentLength": len(body),
            }
    except HTTPError as error:
        if error.code == 304 and previous.get("sha256"):
            return {
                **base,
                "statusCode": 304,
                "status": "unchanged",
                "sha256": previous["sha256"],
                "contentType": previous.get("contentType"),
                "etag": error.headers.get("ETag") or previous.get("etag"),
                "lastModified": error.headers.get("Last-Modified") or previous.get("lastModified"),
                "contentLength": previous.get("contentLength"),
            }
        return {**base, "status": "failure", "statusCode": error.code, "error": f"HTTP {error.code}: {error.reason}"}
    except (URLError, TimeoutError, socket.timeout, OSError, ValueError) as error:
        reason = getattr(error, "reason", error)
        return {**base, "status": "failure", "error": f"{type(error).__name__}: {reason}"}


def merge_run_state(previous_state: dict[str, Any], results: list[dict[str, Any]], run_at: str) -> dict[str, Any]:
    """Merge a complete monitor run while preserving a short change history."""
    state = dict(previous_state or {})
    old_sources = dict(state.get("sources") or {})
    changes = list(state.get("changes") or [])
    failures: list[dict[str, Any]] = []
    changed_this_run = 0
    successful_this_run = 0
    next_sources = dict(old_sources)

    for result in results:
        source_id = result["id"]
        previous = old_sources.get(source_id, {})
        record = dict(previous)
        record.update({"id": source_id, "name": result.get("name", ""), "url": result.get("url", ""), "lastChecked": result.get("checkedAt", run_at)})
        if result.get("status") == "failure":
            record.update({"status": "failure", "error": result.get("error", "Request failed")})
            if result.get("statusCode") is not None:
                record["statusCode"] = result["statusCode"]
            failures.append({"id": source_id, "name": result.get("name", ""), "url": result.get("url", ""), "error": result.get("error", "Request failed"), "statusCode": result.get("statusCode")})
            next_sources[source_id] = record
            continue

        successful_this_run += 1
        current_sha = result.get("sha256") or previous.get("sha256")
        prior_sha = previous.get("sha256")
        if result.get("status") == "unchanged":
            status = "unchanged"
        elif prior_sha is None:
            status = "baseline"
        elif current_sha != prior_sha:
            status = "changed"
            changed_this_run += 1
            changes.append({
                "id": source_id,
                "name": result.get("name", ""),
                "url": result.get("url", ""),
                "detectedAt": run_at,
                "previousSha256": prior_sha,
                "currentSha256": current_sha,
                "summary": "Normalized page content changed since the previous successful check. Review the official page before editing curated data.",
            })
        else:
            status = "unchanged"
        record.update({
            "status": status,
            "sha256": current_sha,
            "contentType": result.get("contentType") or previous.get("contentType"),
            "etag": result.get("etag") or previous.get("etag"),
            "lastModified": result.get("lastModified") or previous.get("lastModified"),
            "contentLength": result.get("contentLength") or previous.get("contentLength"),
        })
        record.pop("error", None)
        record.pop("statusCode", None)
        next_sources[source_id] = record

    # Keep source records that were once monitored, even if the current source list was narrowed.
    state.update({
        "schemaVersion": 1,
        "lastRun": run_at,
        "lastRunDate": run_at[:10],
        "checkedCount": len(results),
        "successCount": successful_this_run,
        "changedCount": changed_this_run,
        "failureCount": len(failures),
        "changes": changes[-100:],
        "failures": failures,
        "sources": next_sources,
        "message": "Source content changes are review signals only; curated event and hotel data are never rewritten by this monitor.",
    })
    return state


def load_json(path: Path, fallback: dict[str, Any]) -> dict[str, Any]:
    if not path.exists():
        return fallback
    return json.loads(path.read_text(encoding="utf-8"))


def run(data_path: Path, state_path: Path, timeout: int, workers: int, max_bytes: int, dry_run: bool = False) -> dict[str, Any]:
    data = load_json(data_path, {})
    sources = [source for source in data.get("officialSources", []) if source.get("monitor", True)]
    # Do not fetch third-party references or dynamic booking searches even if their
    # source record is accidentally marked monitorable.
    previous_state = load_json(state_path, {"schemaVersion": 1, "sources": {}, "changes": [], "failures": []})
    previous = previous_state.get("sources", {})
    sources = sorted(sources, key=lambda source: source.get("id", ""))
    results: list[dict[str, Any]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
        futures = {
            pool.submit(fetch_one, source, previous.get(source.get("id", "")), timeout, max_bytes): source
            for source in sources
        }
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())
    results.sort(key=lambda result: result.get("id", ""))
    run_at = utc_now()
    updated = merge_run_state(previous_state, results, run_at)
    if not dry_run:
        state_path.parent.mkdir(parents=True, exist_ok=True)
        state_path.write_text(json.dumps(updated, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Official sources checked: {len(results)} · success: {updated['successCount']} · changed: {updated['changedCount']} · failed: {updated['failureCount']}")
    if updated["changes"] and updated["changedCount"]:
        for item in updated["changes"][-updated["changedCount"]:]:
            print(f"CHANGE {item['id']}: {item['url']}")
    for item in updated["failures"]:
        print(f"FAIL {item['id']}: {item['error']}", file=sys.stderr)
    if dry_run:
        print("Dry run: monitor state was not written.")
    return updated


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA, help="Curated site data JSON")
    parser.add_argument("--state", type=Path, default=DEFAULT_STATE, help="Monitor state JSON to update")
    parser.add_argument("--timeout", type=int, default=20, help="Per-request timeout in seconds")
    parser.add_argument("--workers", type=int, default=8, help="Maximum concurrent official-source requests")
    parser.add_argument("--max-bytes", type=int, default=MAX_BYTES, help="Maximum bytes accepted per source response")
    parser.add_argument("--dry-run", action="store_true", help="Fetch and report without writing monitor state")
    args = parser.parse_args()
    run(args.data, args.state, args.timeout, args.workers, args.max_bytes, args.dry_run)


if __name__ == "__main__":
    main()
