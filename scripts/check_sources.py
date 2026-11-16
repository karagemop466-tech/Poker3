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
    for h in data.get("hotels", []):
        add(h.get("source", ""), f"{h['name']} room source")
        add(h.get("feeSource", ""), f"{h['name']} fee terms")
        add(h.get("taxSource", ""), f"{h['name']} tax terms")
    return list(out.values())


def fetch(url: str) -> tuple[int, str, bytes]:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    context = ssl.create_default_context()
    with urllib.request.urlopen(request, timeout=TIMEOUT, context=context) as response:
        return response.status, response.headers.get("Content-Type", ""), response.read()


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
            if old and old.get("hash") and old["hash"] != digest:
                row["changed"] = True
                row["previousHash"] = old["hash"]
                row["previousChecked"] = old.get("checked", "")
                changed.append(row)
            else:
                row["changed"] = False
        except urllib.error.HTTPError as exc:
            row["status"] = f"HTTP {exc.code}"
            row["error"] = str(exc)
            row["changed"] = bool(old)
            if old and old.get("hash"):
                row["previousHash"] = old["hash"]
                changed.append(row)
        except Exception as exc:  # noqa: BLE001 - the checker must survive one bad URL
            row["status"] = "unreachable"
            row["error"] = f"{type(exc).__name__}: {exc}"
            row["changed"] = bool(old)
            if old and old.get("hash"):
                row["previousHash"] = old["hash"]
                changed.append(row)
        rows.append(row)
        print(f"{row['status']:>14}  {url}")

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
