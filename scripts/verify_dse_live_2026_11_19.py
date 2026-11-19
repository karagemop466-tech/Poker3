#!/usr/bin/env python3
"""Verify every published Venetian DSE IV row against the 2026-11-19 live capture.

Run from the repository root:

    python3 scripts/verify_dse_live_2026_11_19.py

The capture is `raw/venetian_dse_nov_2026_live_2026-11-19.md`, a transcription of the
visible text of the official schedule page read on 2026-11-19. This script compares it
with `site/data.json` row by row on the five fields the page itself prints:

    date, start time, event number, event name and structure-sheet URL

It never edits data. It fails loudly when a published row disagrees with the capture, so
the catalog and the dated evidence cannot drift apart.
"""
from __future__ import annotations

import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
CAPTURE = ROOT / "raw" / "venetian_dse_nov_2026_live_2026-11-19.md"
DATA = ROOT / "site" / "data.json"

ROW = re.compile(
    r"^\|\s*(\d+)\s*\|\s*(\d{4}-\d{2}-\d{2})\s*\|\s*([^|]+?)\s*\|\s*(\d+)\s*\|\s*([^|]+?)\s*\|\s*(\d+)\s*\|\s*$"
)


def norm(s: str) -> str:
    """Fold the cosmetic differences the page reader introduces.

    The official page prints `<br>` between the event name and its subtitle and
    escapes capitals inconsistently ("No LImit"). Neither changes the value, so both
    sides are normalised before comparison. Nothing else is relaxed.
    """
    s = s.replace("<br>", " - ").replace("&amp;", "&")
    s = re.sub(r"\s+-\s+", " - ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s.lower()


def read_capture() -> list[dict]:
    rows = []
    for line in CAPTURE.read_text(encoding="utf-8").splitlines():
        m = ROW.match(line.strip())
        if not m:
            continue
        n, date, time, number, name, sheet = m.groups()
        rows.append(dict(n=int(n), date=date, time=time.strip(), number=int(number),
                         name=name.strip(), sheet=int(sheet)))
    return rows


def published() -> list[dict]:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    out = []
    for e in data["events"]:
        if e["venue"] != "venetian":
            continue
        # DeepStack Extravaganza IV only. The NYE series has its own page and capture.
        if "dse-nov-2026" not in (e.get("scheduleUrl") or ""):
            continue
        sheet = e.get("structureUrl") or ""
        m = re.search(r"structure_(\d+)\.pdf$", sheet)
        if not m:
            continue
        out.append(dict(id=e["id"], date=e["date"], time=e["time"], name=e["name"],
                        sheet=int(m.group(1)), buyIn=e.get("buyIn"),
                        guarantee=e.get("guarantee")))
    return out


def main() -> int:
    cap = read_capture()
    pub = published()
    if len(cap) != 94:
        print(f"FAIL: capture has {len(cap)} rows, expected 94")
        return 1
    if len(pub) != len(cap):
        print(f"FAIL: catalog has {len(pub)} Venetian structure-sheet rows, capture has {len(cap)}")
        return 1

    problems = []
    for c, p in zip(cap, pub):
        if c["date"] != p["date"]:
            problems.append(f"row {c['n']}: date {p['date']} != capture {c['date']}")
        if c["time"].upper() != p["time"].upper():
            problems.append(f"row {c['n']}: time {p['time']} != capture {c['time']}")
        if c["sheet"] != p["sheet"]:
            problems.append(f"row {c['n']}: sheet {p['sheet']} != capture {c['sheet']}")
        if norm(c["name"]) != norm(p["name"]):
            problems.append(f"row {c['n']}: name\n    catalog: {p['name']}\n    capture: {c['name']}")

    if problems:
        print(f"FAIL: {len(problems)} mismatch(es) between the catalog and the 2026-11-19 capture")
        for x in problems:
            print(" -", x)
        return 1

    print(f"verified {len(cap)} published Venetian rows against the 2026-11-19 live capture "
          f"(date, start time, structure sheet, event name)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
