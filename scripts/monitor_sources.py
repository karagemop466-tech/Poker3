#!/usr/bin/env python3
"""Scheduled official-source change monitor.

Re-checks every official URL in site/data.json on a schedule, keeps a dated
check log (data/source-checks.json), and writes flags for URLs whose content
changed (data/source-changes.json) including which data rows reference them.
Never fails the build: network errors are recorded as check errors.
"""
import hashlib
import json
import pathlib
import urllib.error
import urllib.request
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / "site" / "data.json"
CHECKS = ROOT / "data" / "source-checks.json"
CHANGES = ROOT / "data" / "source-changes.json"
TIMEOUT = 20
UA = "VegasPokerPlanner-monitor/1.0 (scheduled official-source re-check)"


def load_json(path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return default


def sha256_of(data):
    return hashlib.sha256(data).hexdigest()


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            body = resp.read()
            return {
                "status": resp.status,
                "sha256": sha256_of(body),
                "etag": resp.headers.get("ETag"),
                "lastModified": resp.headers.get("Last-Modified"),
                "contentLength": resp.headers.get("Content-Length"),
                "error": None,
            }
    except Exception as exc:  # network errors are recorded, not raised
        return {"status": None, "sha256": None, "etag": None,
                "lastModified": None, "contentLength": None,
                "error": repr(exc)}


def main():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    today = datetime.now(timezone.utc).date().isoformat()
    sources = data.get("sources") or data.get("officialSources") or []
    previous = load_json(CHECKS, {"generatedAt": None, "checks": []})
    prev_by_url = {}
    for entry in previous.get("checks", []):
        prev_by_url.setdefault(entry["url"], []).append(entry)

    new_checks = []
    for source in sources:
        url = source["url"]
        result = fetch(url)
        entry = {
            "date": today,
            "url": url,
            "name": source.get("name", ""),
            "status": result["status"],
            "sha256": result["sha256"],
            "etag": result["etag"],
            "lastModified": result["lastModified"],
            "contentLength": result["contentLength"],
            "error": result["error"],
        }
        new_checks.append(entry)

    out_checks = {"generatedAt": today, "checks": new_checks}
    CHECKS.write_text(json.dumps(out_checks, indent=2) + "\n", encoding="utf-8")

    changes = []
    for entry in new_checks:
        url = entry["url"]
        history = prev_by_url.get(url, [])
        previous_entry = history[-1] if history else None
        changed = False
        note = []
        if previous_entry:
            if entry["sha256"] and previous_entry.get("sha256") and \
               entry["sha256"] != previous_entry["sha256"]:
                changed = True
                note.append("content hash changed since " +
                            previous_entry.get("date", "previous check"))
            elif entry["status"] != previous_entry.get("status"):
                changed = True
                note.append("HTTP status changed to " + str(entry["status"]))
        else:
            note.append("first check")
        if changed or not history:
            rows_affected = rows_referencing_url(data, url)
            changes.append({
                "date": today,
                "url": url,
                "name": entry["name"],
                "previousChecked": previous_entry["date"] if previous_entry else None,
                "changed": changed,
                "note": "; ".join(note),
                "error": entry["error"],
                "rowsAffected": rows_affected,
            })

    out_changes = {"generatedAt": today, "changes": changes}
    CHANGES.write_text(json.dumps(out_changes, indent=2) + "\n", encoding="utf-8")

    print("checked", len(sources), "official sources on", today)
    print("changed flags:", len([c for c in changes if c["changed"]]))
    for c in changes:
        print(" -", c["date"], c["name"], "|", c["note"], "| rows:", c["rowsAffected"])


def rows_referencing_url(data, url):
    """Which published rows point at this URL (canonical field names)."""
    rows = []
    for index, row in enumerate(data.get("events", []) or data.get("tournaments", []), start=1):
        for field in ("scheduleUrl", "structureUrl", "schedule", "structure", "confirmSource"):
            if row.get(field) == url:
                rows.append({"kind": "tournament", "row": index,
                             "event": row.get("name") or row.get("event", ""), "field": field})
        for rule, body in (row.get("rules") or {}).items():
            if isinstance(body, dict) and body.get("source") == url:
                rows.append({"kind": "tournament", "row": index,
                             "event": row.get("name", ""), "field": "rules." + rule})
    for index, row in enumerate(data.get("hotels", []), start=1):
        for field in ("source", "feeSource", "taxSource", "feeSourceAlt"):
            if row.get(field) == url:
                rows.append({"kind": "hotel", "row": index,
                             "name": row.get("name", ""), "field": field})
    return rows


if __name__ == "__main__":
    main()
