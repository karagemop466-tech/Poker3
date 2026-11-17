#!/usr/bin/env python3
"""Line-by-line transcription check for the Wynn WPT World Championship series.

Scope: new in session arena/6118f42d-poker3. Complements
``scripts/verify_dse_full.py``, which does the same job for the Venetian
DeepStack Extravaganza IV series.

Which rows are in scope
-----------------------
The 136 rows whose ``scheduleUrl`` is the official WPT World Championship
schedule PDF. The published data also holds Wynn Signature Series rows and the
Wynn daily room events; those come from different official PDFs and are out of
scope here, even though several of them share the ``wpt`` category (that
category means "a Wynn series PDF", not "this one PDF").

Evidence basis
--------------
``raw/wynn_wpt_world_championship_schedule.md`` is a verbatim copy of the
official WPT World Championship schedule PDF (source URL in that file's header).
The sandbox cannot reach wynnresorts.com or its CDN, so the recorded copy is the
only official evidence available offline. Rows whose official cells are empty are
reported as "official cell blank"; a value that differs from the printed cell is
reported as a mismatch and is never silently corrected.

The weekday printed beside each date is checked against the calendar, because the
official PDF is already known to self-contradict on some rows (flag F03/F34 in
the Flagged register). That check is a source irregularity report, not a reason
to change a date: the date column is taken as printed.

Usage:  python3 scripts/verify_wpt_full.py
Exit code 0 when every printed cell agrees, 1 otherwise.
"""

from __future__ import annotations

import calendar
import datetime as dt
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "raw" / "wynn_wpt_world_championship_schedule.md"
DATA = ROOT / "site" / "data.json"

SCHEDULE_PDF = "WPT_World_Championship_Schedule.pdf"
YEAR = 2026
MONTHS = {m.lower()[:3]: i for i, m in enumerate(calendar.month_abbr) if m}
WEEKDAYS = {d.lower()[:3]: i for i, d in enumerate(calendar.day_abbr) if d}
WEEKDAYS_FULL = {d.lower(): i for i, d in enumerate(calendar.day_name)}

ROW_RE = re.compile(
    r"^\|\s*(?P<date>[^|]*?)\s*\|\s*(?P<time>[^|]*?)\s*\|\s*(?P<event>[^|]*?)\s*\|"
    r"\s*(?P<buyin>[^|]*?)\s*\|\s*(?P<guar>[^|]*?)\s*\|\s*(?P<chips>[^|]*?)\s*\|"
    r"\s*(?P<levels>[^|]*?)\s*\|\s*$"
)


def parse_date(cell: str):
    """'Nov. 27 Friday' -> ('2026-11-27', 'friday', True/False weekday agrees)."""
    c = cell.replace(".", " ").strip()
    m = re.match(r"^([A-Za-z]+)\s+(\d{1,2})(?:\s+([A-Za-z]+))?$", c)
    if not m:
        return None, None, None
    mon = MONTHS.get(m.group(1)[:3].lower())
    if not mon:
        return None, None, None
    try:
        d = dt.date(YEAR, mon, int(m.group(2)))
    except ValueError:
        return None, None, None
    printed = m.group(3)
    agrees = None
    if printed:
        want = WEEKDAYS_FULL.get(printed.lower(), WEEKDAYS.get(printed[:3].lower()))
        if want is not None:
            agrees = (d.weekday() == want)
    return d.isoformat(), (printed or ""), agrees


def parse_time(cell: str):
    c = cell.strip().lower().replace(".", "")
    m = re.match(r"^(\d{1,2})(?::(\d{2}))?\s*([ap])m$", c)
    if not m:
        return None
    h = int(m.group(1)) % 12
    return h * 60 + int(m.group(2) or 0) + (720 if m.group(3) == "p" else 0)


def clean_money(v: str):
    """Parse a printed money cell. Footnote asterisks ('$10,500*****') are part of
    the printed cell but not of the amount, so they are stripped before parsing."""
    v = v.strip()
    if not v:
        return None
    m = re.match(r"^\$([\d,]+(?:\.\d+)?)\**$", v)
    return float(m.group(1).replace(",", "")) if m else v


def clean_chips(v: str):
    v = v.strip()
    return int(v.replace(",", "")) if v else None


def norm_name(v: str):
    return re.sub(r"[^A-Z0-9]+", " ", (v or "").upper()).strip()


def main():
    rows = []
    for line in RAW.read_text(encoding="utf-8").splitlines():
        m = ROW_RE.match(line)
        if not m:
            continue
        g = m.groupdict()
        date, printed_day, day_agrees = parse_date(g["date"])
        if not date:
            continue
        rows.append({
            "date": date,
            "printedDay": printed_day,
            "dayAgrees": day_agrees,
            "dateCell": g["date"].strip(),
            "minutes": parse_time(g["time"]),
            "timeCell": g["time"].strip(),
            "name": g["event"].strip(),
            "buyIn": clean_money(g["buyin"]),
            "guarantee": clean_money(g["guar"]),
            "chips": clean_chips(g["chips"]),
            "levels": g["levels"].strip(),
        })

    data = json.loads(DATA.read_text(encoding="utf-8"))
    wpt = [e for e in data["events"] if SCHEDULE_PDF in (e.get("scheduleUrl") or "") and e.get("date")]
    by_key = {}
    for e in wpt:
        by_key.setdefault((e["date"], e.get("time", "").upper()), []).append(e)

    def pub_minutes(e):
        m = re.match(r"^(\d{1,2}):(\d{2})\s*([AP])M$", (e.get("time") or "").strip().upper())
        if not m:
            return None
        h = int(m.group(1)) % 12
        return h * 60 + int(m.group(2)) + (720 if m.group(3) == "P" else 0)

    mismatches, blanks, unmatched, ambiguous = [], [], [], []
    weekday_conflicts = []
    seen = set()

    for r in rows:
        if r["dayAgrees"] is False:
            weekday_conflicts.append((r["date"], r["dateCell"], calendar.day_name[
                dt.date.fromisoformat(r["date"]).weekday()]))
        # Candidates: same date and the same clock time, never already used.
        cands = [e for e in wpt
                 if e["date"] == r["date"] and pub_minutes(e) == r["minutes"] and e["id"] not in seen]
        if not cands:
            unmatched.append(r)
            continue
        # Several events share one start time on this schedule, so the name is the
        # tiebreaker and an exact normalised-name match always wins.
        rn = norm_name(r["name"])
        exact = [e for e in cands if norm_name(e.get("name")) == rn]
        if exact:
            target = exact[0]
        else:
            rt = set(rn.split())
            scored = sorted(cands, key=lambda e: -len(rt & set(norm_name(e.get("name")).split())))
            target = scored[0]
            if not (rt & set(norm_name(target.get("name")).split())):
                # No name evidence at all: record it rather than guess.
                ambiguous.append((r, [e["id"] for e in cands]))
        seen.add(target["id"])

        if any(r is a for a, _ in ambiguous):
            continue
        for field, official, published in (
            ("buyIn", r["buyIn"], target.get("buyIn")),
            ("chips", r["chips"], target.get("chips")),
            ("guarantee", r["guarantee"], target.get("guarantee")),
        ):
            if official is None:
                if published not in (None, "", 0):
                    blanks.append((r["date"], target["id"], field, published, r["name"]))
                continue
            if isinstance(official, str):
                # seat guarantees ("75 Seats") are stored as prose
                m = re.match(r"^(\d+)\s+SEATS?$", official.upper())
                if m and published is not None and str(m.group(1)) in str(published):
                    continue
                if official != published:
                    mismatches.append((r["date"], target["id"], field, official, published, r["name"]))
                continue
            if isinstance(published, str):
                m = re.match(r"^(\d+)\s+SEATS?$", published.upper())
                if m and int(m.group(1)) == int(official):
                    continue
            if official != published:
                mismatches.append((r["date"], target["id"], field, official, published, r["name"]))

    unaccounted = [e for e in wpt if e["id"] not in seen]

    print("official rows parsed:        %d" % len(rows))
    print("official rows matched:       %d" % (len(rows) - len(unmatched)))
    print("official rows unmatched:     %d" % len(unmatched))
    print("published wpt rows:          %d" % len(wpt))
    print("published rows unaccounted:  %d" % len(unaccounted))
    print("value mismatches:            %d" % len(mismatches))
    print("blank official cells filled: %d" % len(blanks))
    print("printed-weekday conflicts:   %d" % len(weekday_conflicts))
    print("rows matched without a name: %d" % len(ambiguous))

    if mismatches:
        print("\n--- VALUE MISMATCHES ---")
        for date, eid, field, off, pub, name in mismatches:
            print("  %s %s [%s] official=%r published=%r  (%s)" % (date, eid, field, off, pub, name[:60]))
    if unmatched:
        print("\n--- OFFICIAL ROWS WITH NO PUBLISHED COUNTERPART ---")
        for r in unmatched:
            print("  %s %s %s (buy-in %s, guarantee %s)" % (r["date"], r["timeCell"], r["name"][:60], r["buyIn"], r["guarantee"]))
    if unaccounted:
        print("\n--- PUBLISHED WPT ROWS NOT IN THE OFFICIAL TABLE ---")
        for e in unaccounted:
            print("  %s %s %s" % (e["date"], e.get("time"), (e.get("name") or "")[:60]))
    if ambiguous:
        print("\n--- MATCHED ON DATE AND TIME ONLY (no name evidence; treated as unverified) ---")
        for r, ids in ambiguous:
            print("  %s %s %s -> candidates %s" % (r["date"], r["timeCell"], r["name"][:55], ids))
    if weekday_conflicts:
        print("\n--- PRINTED WEEKDAY DISAGREES WITH THE CALENDAR (source irregularity) ---")
        for date, cell, actual in weekday_conflicts:
            print("  %s printed as %r; that date is a %s" % (date, cell, actual))
    if blanks:
        print("\n--- OFFICIAL CELL BLANK, PUBLISHED VALUE PRESENT ---")
        for date, eid, field, pub, name in blanks:
            print("  %s %s [%s] published=%r  (%s)" % (date, eid, field, pub, name[:60]))

    return 1 if mismatches else 0


if __name__ == "__main__":
    sys.exit(main())
