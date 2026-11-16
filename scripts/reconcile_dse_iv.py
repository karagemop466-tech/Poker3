#!/usr/bin/env python3
"""Reconcile the curated Venetian DSE IV rows against two official transcriptions.

  raw/venetian_dse_nov_2026_schedule.md  - official schedule PDF (date, event, time,
                                          REG CLOSES, guarantee, chips, level)
  raw/venetian_dse4_official_page_rows.md - official event page (date, time, event #,
                                          structure-sheet number per row)

Every row in data/venetian_dse_iv.json must appear in both files with the same
date, time, structure-sheet number and registration close. Any difference is
printed and the script exits non-zero.

Run:  python3 scripts/reconcile_dse_iv.py
"""
from __future__ import annotations

import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]

MONTHS = {
    "JANUARY": 1, "FEBRUARY": 2, "MARCH": 3, "APRIL": 4, "MAY": 5, "JUNE": 6,
    "JULY": 7, "AUGUST": 8, "SEPTEMBER": 9, "OCTOBER": 10, "NOVEMBER": 11, "DECEMBER": 12,
}


def flight_of(name: str) -> str:
    """Flight / continuation token printed in an official event name."""
    u = name.upper()
    if "DAY 2 RESTART" in u:
        return "Day 2 Restart"
    if "DAY 3 RESTART" in u:
        return "Day 3 Restart"
    if "FINAL TABLE" in u:
        return "Final Table"
    m = re.search(r"(?<![0-9A-Z])(1[A-F])(?![0-9A-Z])", u)
    if m:
        return m.group(1)
    m = re.search(r"\bHOLD'EM ([1-6][A-F])\b", u)
    if m:
        return m.group(1)
    if "(2DAY)" in u:
        return "Day 1"
    return ""


def split_label(label: str):
    """'39 Day 2 Restart' -> ('39', 'Day 2 Restart');  '1A' -> ('1', '1A')."""
    parts = label.split(" ", 1)
    ev = parts[0]
    rest = parts[1].strip() if len(parts) > 1 else ""
    if not rest and re.fullmatch(r"\d+[A-F]", ev):
        # "1A".."1D" are event 1's flights; the flight token is the whole suffix.
        rest = ev
        ev = ev[:-1]
    return ev, rest


def pdf_rows():
    """Official schedule PDF transcription -> {(date, event_number, flight): {...}}."""
    text = (ROOT / "raw" / "venetian_dse_nov_2026_schedule.md").read_text(encoding="utf-8")
    out = {}
    for line in text.splitlines():
        if not line.startswith("| "):
            continue
        parts = [p.strip() for p in line.strip("|").split("|")]
        if len(parts) < 9:
            continue
        tag, evnum, evname, tm, reg, gtd, chips, level = parts[:8]
        m = re.match(r"^([A-Z]+), ([A-Za-z]+) (\d{1,2})$", tag)
        if not m:
            continue
        date = f"2026-{MONTHS[m.group(2).upper()]:02d}-{int(m.group(3)):02d}"
        out[(date, evnum, flight_of(evname))] = {
            "time": tm,
            "regClose": reg,
            "guarantee": gtd,
            "chips": chips,
            "level": level,
            "name": evname,
            "eventNumber": evnum,
        }
    return out


def page_rows():
    """Official event page transcription -> {(date, event_number, flight): {...}}."""
    text = (ROOT / "raw" / "venetian_dse4_official_page_rows.md").read_text(encoding="utf-8")
    out = {}
    for line in text.splitlines():
        if not line.startswith("| "):
            continue
        parts = [p.strip() for p in line.strip("|").split("|")]
        if len(parts) < 4:
            continue
        date_text, tm, label, sheet = parts[:4]
        m = re.match(r"[A-Za-z]+, ([A-Za-z]+) (\d{1,2}), (\d{4})", date_text)
        if not m:
            continue
        date = f"{m.group(3)}-{MONTHS[m.group(1).upper()]:02d}-{int(m.group(2)):02d}"
        ev, flight = split_label(re.sub(r"\s*\(Turbo\)$", "", label).strip())
        out[(date, ev, flight)] = {"time": tm, "sheet": int(sheet)}
    return out


def money(text):
    text = (text or "").strip()
    if not text or text in {"-", "—"}:
        return ""
    m = re.match(r"^\$([\d.]+)\s+MILLION$", text.upper())
    if m:
        return int(float(m.group(1)) * 1000000)
    m = re.match(r"^\$([\d,]+)", text)
    if m:
        return int(m.group(1).replace(",", ""))
    return ""


def main() -> int:
    doc = json.loads((ROOT / "data" / "venetian_dse_iv.json").read_text(encoding="utf-8"))
    pdf = pdf_rows()
    page = page_rows()
    problems = []

    print(f"official PDF rows parsed   : {len(pdf)}")
    print(f"official page rows parsed  : {len(page)}")
    print(f"curated rows               : {len(doc['events'])}")

    for event in doc["events"]:
        ev, flight = split_label(event["eventLabel"])
        key = (event["date"], ev, flight)
        if key not in pdf:
            problems.append(f"{key}: not found in the official schedule PDF transcription")
            continue
        p = pdf[key]
        if p["time"] != event["time"]:
            problems.append(f"{key}: time {event['time']} != PDF {p['time']}")
        if p["regClose"] != event["lateRegistrationCloses"]:
            problems.append(
                f"{key}: reg close {event['lateRegistrationCloses']!r} != PDF {p['regClose']!r}"
            )
        gtd = money(p["guarantee"])
        if gtd != "" and gtd != event["guarantee"]:
            problems.append(f"{key}: guarantee {event['guarantee']} != PDF {gtd}")
        if p["chips"] and int(p["chips"].replace(",", "")) != event["startingChips"]:
            problems.append(f"{key}: chips {event['startingChips']} != PDF {p['chips']}")
        if p["level"] and int(p["level"].split("/")[0]) != event["levelMinutes"]:
            problems.append(f"{key}: level {event['levelMinutes']} != PDF {p['level']}")

        if key not in page:
            problems.append(f"{key}: not found in the official event-page transcription")
            continue
        q = page[key]
        if q["time"] != event["time"]:
            problems.append(f"{key}: time {event['time']} != event page {q['time']}")
        sheet_no = int(re.search(r"structure_(\d+)\.pdf", event["structureSheet"]).group(1))
        if q["sheet"] != sheet_no:
            problems.append(
                f"{key}: structure sheet {sheet_no} != official page link {q['sheet']}"
            )

    # Every official row must be represented exactly once.
    curated = {(e["date"],) + split_label(e["eventLabel"]) for e in doc["events"]}
    for key in pdf:
        if key not in curated:
            problems.append(f"{key}: present in the official PDF but missing from the curated data")
    for key in page:
        if key not in curated:
            problems.append(f"{key}: present on the official event page but missing from the curated data")

    if problems:
        print(f"\n{len(problems)} difference(s):")
        for line in problems:
            print("  -", line)
        return 1
    print("\nOK: every curated row matches the official schedule PDF and the official event page.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
