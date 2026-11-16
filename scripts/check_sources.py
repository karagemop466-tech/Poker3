#!/usr/bin/env python3
"""Check official source URLs and record page-content changes without copying page data.

The monitor is deliberately a change signal, not an extractor: humans still verify any
changed value against the linked official source before editing tournament/hotel facts.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import datetime as dt
import hashlib
import json
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CATALOG = ROOT / "site/poker3/data/research.json"
DEFAULT_OUTPUT = ROOT / "site/poker3/data/source-monitor.json"
# The canonical dashboard keeps its own source register and its own monitor log.
CANONICAL_CATALOG = ROOT / "data/sources.json"
CANONICAL_OUTPUT = ROOT / "site/data/source-monitor.json"
USER_AGENT = "Poker3OfficialSourceMonitor/1.0 (+https://github.com/karagemop466-tech/Poker3)"


def utc_now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0)


def fetch(url: str, timeout: int = 25) -> tuple[int, bytes]:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT, "Accept": "text/html,application/pdf,*/*"},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        status = int(response.status)
        body = response.read(12 * 1024 * 1024 + 1)
    if len(body) > 12 * 1024 * 1024:
        raise ValueError("response exceeded 12 MiB safety limit")
    if status < 200 or status >= 300:
        raise urllib.error.HTTPError(url, status, "non-success response", response.headers, None)
    return status, body


def check_one(source: dict[str, Any], previous: dict[str, Any], checked_at: str,
              fetcher=fetch) -> tuple[str, dict[str, Any]]:
    source_id = source["id"]
    old = previous.get(source_id, {})
    result: dict[str, Any] = {
        "url": source["url"],
        "name": source.get("name", source_id),
        "lastChecked": checked_at,
        "changed": None,
        "result": "unavailable",
        "httpStatus": None,
        "contentHash": old.get("contentHash"),
        "error": None,
    }
    try:
        status, content = fetcher(source["url"])
        digest = hashlib.sha256(content).hexdigest()
        result.update({"httpStatus": status, "contentHash": digest, "error": None})
        old_hash = old.get("contentHash")
        if not old_hash:
            result.update({"changed": False, "result": "baseline"})
        elif old_hash != digest:
            result.update({"changed": True, "result": "changed"})
        else:
            result.update({"changed": False, "result": "unchanged"})
    except Exception as exc:  # Network, TLS, HTTP and parsing errors are evidence gaps.
        result["error"] = f"{type(exc).__name__}: {str(exc)[:240]}"
        result["httpStatus"] = getattr(exc, "code", None)
    return source_id, result


def run(catalog_path: Path = DEFAULT_CATALOG, output_path: Path = DEFAULT_OUTPUT,
        fetcher=fetch, checked_at: str | None = None, delay: float = 0.15) -> dict[str, Any]:
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    previous_doc = json.loads(output_path.read_text(encoding="utf-8")) if output_path.exists() else {}
    previous = previous_doc.get("checks", {})
    official = [source for source in catalog.get("sources", [])
                if source.get("kind") == "official" and source.get("url", "").startswith("https://")]
    timestamp = checked_at or utc_now().isoformat().replace("+00:00", "Z")
    checks: dict[str, dict[str, Any]] = {}
    # Bounded concurrency keeps the daily check quick without hammering a property site.
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
        futures = [pool.submit(check_one, source, previous, timestamp, fetcher) for source in official]
        for future in concurrent.futures.as_completed(futures):
            source_id, record = future.result()
            checks[source_id] = record
            if delay:
                time.sleep(delay)
    document = {
        "checkedAt": timestamp,
        "officialSourceCount": len(official),
        "changedCount": sum(record["changed"] is True for record in checks.values()),
        "unavailableCount": sum(record["result"] == "unavailable" for record in checks.values()),
        "checks": dict(sorted(checks.items())),
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({key: document[key] for key in ("checkedAt", "officialSourceCount", "changedCount", "unavailableCount")}, indent=2))
    return document


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--canonical",
        action="store_true",
        help="also check the canonical dashboard source register in data/sources.json",
    )
    args = parser.parse_args()
    run(args.catalog, args.output)
    if args.canonical:
        run(CANONICAL_CATALOG, CANONICAL_OUTPUT)


if __name__ == "__main__":
    main()
