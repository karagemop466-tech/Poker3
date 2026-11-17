#!/usr/bin/env python3
"""Scheduled re-check of every official URL behind the dashboard.

Run from the repository root:

    python3 scripts/check_sources.py

It fetches each official URL, stores a SHA-256 of the response body and compares
it with the hash recorded in site/checks.json.  A URL whose body changed is
flagged, and the flags are published on the sources page.

The script never changes a tournament value by itself.  A changed page means a
human has to look at the official source again before any number moves, so the
script only records the change and the reason.

Network access is required.  It is designed to run in GitHub Actions; it is
safe to run anywhere with outbound HTTPS.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import pathlib
import ssl
import sys
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
DATA = SITE / "data.json"
CHECKS = SITE / "checks.json"

USER_AGENT = "Poker3SourceChecker/1.0 (+https://karagemop466-tech.github.io/Poker3/)"
TIMEOUT = 30


def official_targets(data: dict) -> list[dict]:
    """Every official URL the dashboard depends on, with a readable label."""
    out: dict[str, dict] = {}

    def add(url: str, label: str) -> None:
        if url and url.startswith("https://") and url not in out:
            out[url] = {"url": url, "label": label}

    for s in data.get("sources", []):
        add(s["url"], s["name"])
    for sheet in data.get("structureSheets", []):
        add(sheet["url"], f"{sheet['series']} structure sheet {sheet['sheet']}")
    for room in data.get("feed", []):
        add(room["schedule"], f"{room['name']} schedule page")
        for extra in room.get("extra", []):
            add(extra, f"{room['name']} extra source")
    for e in data.get("events", []):
        add(e.get("scheduleUrl", ""), f"Schedule for {e['name']}")
        add(e.get("structureUrl", ""), f"Structure sheet for {e['name']}")
        for rule_name, rule in (e.get("rules") or {}).items():
            if isinstance(rule, dict):
                add(rule.get("source", ""), f"{e['name']} {rule_name} rule")
    for h in data.get("hotels", []):
        for field, label in (
            ("source", "room source"), ("feeSource", "fee terms"), ("taxSource", "tax terms"),
            ("feeSourceAlt", "alternate fee terms"), ("parkingSource", "parking terms"),
            ("cancellationSource", "cancellation terms"), ("bookingUrl", "booking page"),
            ("calendarUrl", "booking calendar"),
        ):
            add(h.get(field, ""), f"{h['name']} {label}")
        quote = h.get("quote") or {}
        add(quote.get("source", ""), f"{h['name']} dated quote")
    for row in data.get("rateLog", []):
        add(row.get("source", ""), f"{row.get('hotel', 'Hotel')} rate observation")
        add(row.get("feeSource", ""), f"{row.get('hotel', 'Hotel')} fee source")
        add(row.get("taxSource", ""), f"{row.get('hotel', 'Hotel')} tax source")
    for route in data.get("routes", []):
        add(route.get("source", ""), f"{route.get('hotel', '')} to {route.get('venue', '')} official address")
    return list(out.values())


def fetch(url: str) -> tuple[int, str, bytes]:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    context = ssl.create_default_context()
    with urllib.request.urlopen(request, timeout=TIMEOUT, context=context) as response:
        return response.status, response.headers.get("Content-Type", ""), response.read()


def compare_check(old: dict | None, status: str, digest: str | None) -> dict:
    """Classify a fetch without conflating a failed request with changed content."""
    available = status.startswith("HTTP 2")
    prior_hash = (old or {}).get("hash")
    changed = bool(available and prior_hash and digest and prior_hash != digest)
    baseline = bool(available and not prior_hash)
    return {
        "changed": changed,
        "unavailable": not available,
        "baseline": baseline,
        "previousHash": prior_hash or None,
        "previousChecked": (old or {}).get("checked", "") or None,
        "statusChanged": bool(old and old.get("status") != status),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Re-check every official URL used by the dashboard.")
    parser.add_argument("--only", default="", help="only check URLs whose label contains this text")
    parser.add_argument("--dry-run", action="store_true", help="do not write site/checks.json")
    args = parser.parse_args()

    data = json.loads(DATA.read_text(encoding="utf-8"))
    previous = {}
    if CHECKS.exists():
        try:
            previous = {u["url"]: u for u in json.loads(CHECKS.read_text(encoding="utf-8")).get("urls", [])}
        except (ValueError, KeyError):
            previous = {}

    targets = official_targets(data)
    if args.only:
        needle = args.only.lower()
        targets = [t for t in targets if needle in t["label"].lower() or needle in t["url"].lower()]

    now = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()
    rows = []
    changed = []
    for target in targets:
        url = target["url"]
        row = {"url": url, "label": target["label"], "checked": now}
        old = previous.get(url)
        try:
            status, ctype, body = fetch(url)
            digest = hashlib.sha256(body).hexdigest()
            row["status"] = f"HTTP {status}"
            row["hash"] = digest
            row["bytes"] = len(body)
        except urllib.error.HTTPError as exc:
            row["status"] = f"HTTP {exc.code}"
            row["error"] = str(exc)
        except Exception as exc:  # noqa: BLE001 - the checker must survive one bad URL
            row["status"] = "unreachable"
            row["error"] = f"{type(exc).__name__}: {exc}"

        row.update(compare_check(old, row["status"], row.get("hash")))
        if row["changed"]:
            changed.append(row)
        rows.append(row)
        state = "CHANGED" if row["changed"] else "UNAVAILABLE" if row["unavailable"] else "BASELINE" if row["baseline"] else "unchanged"
        print(f"{row['status']:>14}  {state:>11}  {url}")

    payload = {
        "lastRun": now,
        "note": ("Automated re-check of every official URL behind this dashboard. A changed flag means the page body "
                 "differs from the stored hash and a human must re-read the source before any value is changed."),
        "urls": rows,
        "changedCount": len(changed),
        "changed": [r["url"] for r in changed],
    }
    if not args.dry_run:
        CHECKS.write_text(json.dumps(payload, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"\nwrote {CHECKS} with {len(rows)} URLs, {len(changed)} changed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
