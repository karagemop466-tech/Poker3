#!/usr/bin/env python3
"""Line-by-line check of the DeepStack Extravaganza NYE schedule page.

Scope: session arena/37292d23-poker3, 2026-11-17. The scheduled monitor flagged
the NYE schedule page (dse-dec-2026.html) as CHANGED on the visible-text basis at
2026-11-17T20:48:34Z. This script compares the session's fresh capture of that
page, ``raw/dse_dec_2026_schedule_2026-11-17_37292d23.md``, against every NYE row
published in ``site/data.json``.

What is compared per row
------------------------
* the calendar date (month and day; the printed year 2025 on the three
  December 26 rows is accepted only because flag F04/F41 is published);
* the printed start time;
* the printed event number (read from the published row id);
* the printed buy-in, extracted from the printed event name;
* the printed guarantee ("$NNK GTD"), extracted from the printed event name;
* the structure sheet number the row links.

A printed row with no guarantee may only map to a published row with a blank
guarantee, or to a restart row whose carried-over guarantee is disclosed by the
published flag F63.  Nothing else may fill a blank cell.

Usage:  python3 scripts/verify_nye_live.py
Exit code 0 when every printed cell agrees, 1 otherwise.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "raw" / "dse_dec_2026_schedule_2026-11-17_37292d23.md"
DATA = ROOT / "site" / "data.json"

MONTHS = {m: i for i, m in enumerate(
    ["January", "February", "March", "April", "May", "June", "July",
     "August", "September", "October", "November", "December"], start=1)}


def norm_time(v: str) -> str:
    return re.sub(r"\s+", " ", (v or "").strip().upper())


def norm_name(v: str) -> str:
    v = re.sub(r"<br\s*/?>", " ", v or "", flags=re.I)
    return re.sub(r"[^A-Z0-9]+", " ", v.upper()).strip()


def parse_raw(path: Path) -> list[dict]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) != 5 or cells[0] in ("Date", "---"):
            continue
        date_s, time_s, ev_s, name_s, sheet_s = cells
        m = re.match(r"^[A-Za-z]+, ([A-Za-z]+) (\d{1,2}), (\d{4})$", date_s.strip())
        if not m:
            raise SystemExit(f"unparseable date cell: {date_s!r}")
        month, day, year = MONTHS[m.group(1)], int(m.group(2)), int(m.group(3))
        printed_year = year
        if year == 2025:
            # The page prints 2025 for December 26; the published rows use 2026
            # and disclose the printed typo under flags F04/F41.
            year = 2026
        rows.append({
            "date": f"{year:04d}-{month:02d}-{day:02d}",
            "printedYear": printed_year,
            "time": norm_time(time_s),
            "event": str(int(ev_s)),
            "name": name_s,
            "sheet": int(sheet_s),
        })
    return rows


def buy_in(name: str) -> int | None:
    m = re.search(r"\$([\d,]+)", name)
    return int(m.group(1).replace(",", "")) if m else None


def guarantee(name: str) -> int | None:
    m = re.search(r"\$([\d,]+)K GTD", name, flags=re.I)
    return int(m.group(1).replace(",", "")) * 1000 if m else None


def main() -> int:
    rows = parse_raw(RAW)
    data = json.loads(DATA.read_text(encoding="utf-8"))
    flags = {f["id"] for f in data.get("flags", [])}
    published = {}
    for e in data["events"]:
        if "dse-dec-2026" in (e.get("scheduleUrl") or ""):
            published[e["id"]] = e

    errors: list[str] = []
    notes: list[str] = []
    matched_ids = set()

    required_flags = {"F04", "F41", "F63"}
    missing = required_flags - flags
    if missing:
        errors.append(f"flags required to publish this comparison are missing: {sorted(missing)}")

    print(f"official rows parsed:    {len(rows)}")
    print(f"published NYE rows:      {len(published)}")

    for r in rows:
        if r["printedYear"] == 2025 and "F04" in flags:
            pass  # disclosed typo, mapped above
        elif r["printedYear"] not in (2026, 2027):
            errors.append(f"{r['date']} {r['time']}: unexpected printed year {r['printedYear']}")

        # Locate the published row by date + time + event number (read from the
        # row id, e.g. vl-nye-2026-12-24-1-1110am).
        def id_parts(row_id: str):
            m = re.match(r"^vl-nye-(\d{4}-\d{2}-\d{2})-(\d+)-", row_id)
            return m.groups() if m else (None, None)

        candidates = [e for e in published.values()
                      if e["date"] == r["date"]
                      and norm_time(e.get("time")) == r["time"]
                      and id_parts(e["id"]) == (r["date"], r["event"])]
        if len(candidates) != 1:
            errors.append(f"{r['date']} {r['time']} event {r['event']}: "
                          f"{len(candidates)} published counterpart(s)")
            continue
        p = candidates[0]
        matched_ids.add(p["id"])

        p_buy = buy_in(r["name"])
        if p_buy != p.get("buyIn"):
            errors.append(f"{p['id']}: buy-in printed {p_buy} vs published {p.get('buyIn')}")

        p_gtd = guarantee(r["name"])
        if p_gtd is not None:
            if p_gtd != p.get("guarantee"):
                errors.append(f"{p['id']}: guarantee printed {p_gtd} vs published {p.get('guarantee')}")
        else:
            if "Restart" in r["name"]:
                if p.get("guarantee") and "F63" not in flags:
                    errors.append(f"{p['id']}: restart row carries a guarantee without flag F63")
                elif p.get("guarantee"):
                    notes.append(f"{p['id']}: restart guarantee {p.get('guarantee')} disclosed by F63")
            elif p.get("guarantee") not in (None, ""):
                errors.append(f"{p['id']}: printed cell has no guarantee but published "
                              f"{p.get('guarantee')!r} without a restart disclosure")

        if not str(p.get("structureUrl") or "").endswith(f"structure_{r['sheet']}.pdf"):
            errors.append(f"{p['id']}: structure printed {r['sheet']} vs published "
                          f"{p.get('structureUrl')}")

        if norm_name(r["name"]) != norm_name(p.get("name") or ""):
            errors.append(f"{p['id']}: name differs\n    printed : {norm_name(r['name'])}\n"
                          f"    published: {norm_name(p.get('name') or '')}")

    orphans = [e for eid, e in published.items() if eid not in matched_ids]
    for e in orphans:
        errors.append(f"published NYE row not present on the live page: {e['id']} "
                      f"{e['date']} {e.get('time')} {e.get('name')!r}")

    print(f"official rows matched:   {len(matched_ids)}")
    print(f"published rows orphaned: {len(orphans)}")
    print(f"restart disclosures:     {sum(1 for n in notes if 'F63' in n)}")
    print(f"errors:                  {len(errors)}")

    if notes:
        print("\n--- DISCLOSED CARRY-OVERS (expected, published as flags) ---")
        for n in notes:
            print("  " + n)
    if errors:
        print("\n--- MISMATCHES ---")
        for e in errors:
            print("  " + e)
        return 1
    print("\nOK - every printed NYE schedule row agrees with the published rows line by line.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
