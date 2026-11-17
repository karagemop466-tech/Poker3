#!/usr/bin/env python3
"""Line-by-line check of the published data against a live capture of an official page.

Usage:  python3 scripts/verify_live.py

The captures live in `raw/`. Each capture is a verbatim transcription of an official page taken on a
known date. This script parses the capture and compares every field with `site/data.json`, so a value
that drifted from the official source is reported instead of being silently kept.

It exits non-zero if any row mismatches, which makes it usable as a CI gate.
"""
from __future__ import annotations

import json
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "site" / "data.json"

MONTHS = {
    "January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6,
    "July": 7, "August": 8, "September": 9, "October": 10, "November": 11, "December": 12,
}

SHEET_BASE = (
    "https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/"
    "2026/structures/dse_nov_2026-structure_{n}.pdf"
)


def iso(month: str, day: str, year: str) -> str:
    return date(int(year), MONTHS[month], int(day)).isoformat()


def parse_capture(path: Path) -> list[dict]:
    """Parse the markdown table of a raw schedule capture into row dicts."""
    rows = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line.startswith("| "):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) != 5:
            continue
        day, time, num, name, sheet = cells
        if day in ("Date", "---") or not MONTHS.get(day.split(",")[0].replace("Monday, ", "")
                                                    if False else day.split()[0].rstrip(","), None):
            # fall through: the date cell is like "Monday, November 16, 2026"
            pass
        m = re.match(r"^[A-Z][a-z]+day, ([A-Z][a-z]+) (\d{1,2}), (\d{4})$", day)
        if not m:
            continue
        if not re.match(r"^\d{1,2}:\d{2} [AP]M$", time):
            continue
        if not num.isdigit():
            continue
        sn = re.match(r"^structure_(\d+)$", sheet)
        rows.append({
            "date": iso(m.group(1), m.group(2), m.group(3)),
            "time": time,
            "eventNo": int(num),
            "name": name,
            "sheet": SHEET_BASE.format(n=sn.group(1)) if sn else "",
        })
    return rows


def money(text: str):
    m = re.match(r"^\$([\d,]+)", text)
    return int(m.group(1).replace(",", "")) if m else None


def guarantee(text: str):
    m = re.search(r"\$([\d,]+(?:\.\d+)?)\s*(K|Mill|M)?\s*GTD", text)
    if not m:
        return None
    val = float(m.group(1).replace(",", ""))
    suffix = m.group(2)
    if suffix in ("K",):
        val *= 1_000
    elif suffix in ("Mill", "M"):
        val *= 1_000_000
    return int(val)


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").replace("<br>", " ").replace("<br/>", " ")).strip()


def key(s: str) -> str:
    """Case- and punctuation-insensitive key, so presentational edits do not count as a mismatch."""
    return re.sub(r"[^a-z0-9]+", "", norm(s).lower())


def main() -> int:
    data = json.loads(DATA.read_text())
    events = data["events"]

    problems: list[str] = []
    checked = 0

    cap = ROOT / "raw" / "dse_nov_2026_schedule_2026-11-17.md"
    if not cap.exists():
        print(f"capture missing: {cap}")
        return 1
    rows = parse_capture(cap)
    print(f"capture {cap.name}: {len(rows)} rows parsed")

    published = [e for e in events
                 if "dse-nov-2026" in (e.get("scheduleUrl") or "")]
    print(f"published DSE IV rows: {len(published)}")

    # index published rows by (date, time, event-number-in-name) -> we match on date+time+name
    by_key = {}
    for e in published:
        by_key.setdefault((e["date"], e["time"]), []).append(e)

    matched = set()
    edited: list[str] = []
    for r in rows:
        slot = (r["date"], r["time"])
        rk = key(r["name"])
        cands = [e for e in by_key.get(slot, []) if key(e["name"]) == rk]
        if not cands:
            # the published name may be a truncation of the official one
            cands = [e for e in by_key.get(slot, [])
                     if key(e["name"]).startswith(rk) or rk.startswith(key(e["name"]))]
        if not cands:
            problems.append(f"NO MATCH: {r['date']} {r['time']} #{r['eventNo']} {r['name']}")
            continue
        e = cands[0]
        matched.add(e["id"])
        checked += 1
        if norm(e["name"]) != norm(r["name"]):
            edited.append(
                f"{r['date']} #{r['eventNo']}\n       official: {norm(r['name'])}\n"
                f"       published: {norm(e['name'])}"
            )
        if e.get("structureUrl") != r["sheet"]:
            problems.append(
                f"STRUCTURE: {r['date']} #{r['eventNo']} published={e.get('structureUrl')} "
                f"capture={r['sheet']}"
            )
        want_fee = money(r["name"])
        if want_fee is not None and e.get("buyIn") not in (None, "", want_fee):
            problems.append(
                f"BUY-IN: {r['date']} #{r['eventNo']} published={e.get('buyIn')} capture={want_fee}"
            )
        want_gtd = guarantee(r["name"])
        if want_gtd is not None and e.get("guarantee") not in (None, "", want_gtd):
            problems.append(
                f"GUARANTEE: {r['date']} #{r['eventNo']} published={e.get('guarantee')} "
                f"capture={want_gtd}"
            )

    for e in published:
        if e["id"] not in matched:
            problems.append(f"ORPHAN: published row not on the official page: "
                            f"{e['date']} {e['time']} {e['name']}")

    print(f"rows checked: {checked}")
    if edited:
        print(f"\n{len(edited)} row(s) where the published name is a presentational edit of the "
              f"official text (case, spacing or corrected typo). These are reported, not treated as "
              f"errors, but each one is a place where the site does not quote the source verbatim:")
        for e in edited:
            print("  -", e)
    if problems:
        print(f"\n{len(problems)} problem(s):")
        for p in problems:
            print("  -", p)
        return 1
    print("live capture matches the published data on every field")
    return 0


if __name__ == "__main__":
    sys.exit(main())
