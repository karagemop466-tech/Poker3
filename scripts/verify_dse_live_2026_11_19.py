#!/usr/bin/env python3
"""Verify every published Venetian DSE IV row against the 2026-11-19 live capture.

Run from the repository root:

    python3 scripts/verify_dse_live_2026_11_19.py

The capture is `raw/venetian_dse_nov_2026_live_2026-11-19.md`, a transcription of the
visible text of the official schedule page read on 2026-11-19. Pass a different capture
path as the first argument to check an independent second read of the same page (for
example `raw/dse_schedule_live_2026-11-19_ade0718f.md`). This script compares the capture
with `site/data.json` row by row on the fields the page itself prints:

    date, start time, event number, event name, printed buy-in, printed guarantee and
    structure-sheet URL

The buy-in and guarantee are read from the printed name column ("$2,200 ... $1 Mill GTD"),
which is where the page carries them; a resumption row (Day 2 / Final Table) does not
repeat its event's guarantee, so that one field is skipped for those rows and counted.

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


def printed_amount(text: str, suffix: str = "") -> int | None:
    """Parse a printed dollar amount: ``$2,200`` / ``$75K`` / ``$1 Mill`` (optionally followed by ``GTD``)."""
    pattern = r"\$([\d,]+)\s*(K|Mill|Million)?" + (r"\s*GTD" if suffix else "")
    m = re.search(pattern, text, re.I)
    if not m:
        return None
    value = int(m.group(1).replace(",", ""))
    unit = (m.group(2) or "").lower()
    if unit == "k":
        value *= 1_000
    elif unit in ("mill", "million"):
        value *= 1_000_000
    return value


def read_capture(path: pathlib.Path | None = None) -> list[dict]:
    rows = []
    capture = path or CAPTURE
    for line in capture.read_text(encoding="utf-8").splitlines():
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
                        guarantee=e.get("guarantee"), continuation=bool(e.get("isContinuation"))))
    return out


def main(capture: pathlib.Path | None = None) -> int:
    cap = read_capture(capture)
    pub = published()
    if len(cap) != 94:
        print(f"FAIL: capture has {len(cap)} rows, expected 94")
        return 1
    if len(pub) != len(cap):
        print(f"FAIL: catalog has {len(pub)} Venetian structure-sheet rows, capture has {len(cap)}")
        return 1

    problems, continuations = [], []
    for c, p in zip(cap, pub):
        if c["date"] != p["date"]:
            problems.append(f"row {c['n']}: date {p['date']} != capture {c['date']}")
        if c["time"].upper() != p["time"].upper():
            problems.append(f"row {c['n']}: time {p['time']} != capture {c['time']}")
        if c["sheet"] != p["sheet"]:
            problems.append(f"row {c['n']}: sheet {p['sheet']} != capture {c['sheet']}")
        if norm(c["name"]) != norm(p["name"]):
            problems.append(f"row {c['n']}: name\n    catalog: {p['name']}\n    capture: {c['name']}")
        fee = printed_amount(c["name"])
        if fee is not None and p["buyIn"] != fee:
            problems.append(f"row {c['n']}: buy-in {p['buyIn']!r} != printed {fee}")
        gtd = printed_amount(c["name"], suffix="GTD")
        if gtd is not None:
            if p["guarantee"] != gtd:
                problems.append(f"row {c['n']}: guarantee {p['guarantee']!r} != printed {gtd}")
        elif isinstance(p["guarantee"], (int, float)) and not p["continuation"]:
            problems.append(f"row {c['n']}: guarantee {p['guarantee']} published but no GTD is printed")
        elif p["continuation"]:
            continuations.append(c["n"])

    if problems:
        print(f"FAIL: {len(problems)} mismatch(es) between the catalog and the 2026-11-19 capture")
        for x in problems:
            print(" -", x)
        return 1

    print(f"verified {len(cap)} published Venetian rows against the 2026-11-19 live capture "
          f"(date, start time, structure sheet, event name, printed buy-in, printed guarantee); "
          f"{len(continuations)} resumption rows carry their event's guarantee because the restart "
          f"row does not repeat it")
    return 0


if __name__ == "__main__":
    arg = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else None
    sys.exit(main(arg))
