#!/usr/bin/env python3
"""Parse the verbatim official schedule text in raw/ into JSON.

Run from repo root:  python3 scripts/parse_official.py
Outputs:
  data/venetian_flights.json  (Venetian DSE IV flights with a buy-in)
  data/venetian_restarts.json (Day 2/3 restarts and final-table rows, not flights)
  data/wynn_wpt.json          (Wynn WPT World Championship rows)

Rules (no values are invented):
  * A value is copied from the printed row. Blank cells stay None.
  * Venetian rows often omit the day label when the day does not change.
    The day is then taken from row order: a time that goes back from PM to AM
    means a new day. Such rows are marked date_source="inferred from row order".
  * Restart and final-table rows have no buy-in; they are kept apart.
  * Wynn rows always print a date label; a label that conflicts with the
    calendar is kept as printed and marked calendar_conflict=True.
"""
import datetime as dt
import json
import os
import re

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RAW = os.path.join(ROOT, "raw")
OUT = os.path.join(ROOT, "data")
os.makedirs(OUT, exist_ok=True)

MONTHS = {m: i for i, m in enumerate(
    ["JANUARY", "FEBRUARY", "MARCH", "APRIL", "MAY", "JUNE", "JULY", "AUGUST",
     "SEPTEMBER", "OCTOBER", "NOVEMBER", "DECEMBER"], 1)}
WEEKDAYS = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"]


def clean(s):
    s = s.replace("\\*", "*").strip()
    return s


def money_to_int(s):
    s = clean(s)
    if not s:
        return None
    m = re.fullmatch(r"\$?([\d,]+)", s)
    if m:
        return int(m.group(1).replace(",", ""))
    # printed as "$1 MILLION" on event #47 of the Venetian schedule
    m = re.fullmatch(r"\$([\d.]+) MILLION", s.upper())
    if m:
        return int(float(m.group(1)) * 1_000_000)
    return None


def parse_time(s):
    return dt.datetime.strptime(s.strip(), "%I:%M %p").time()


def table_rows(path):
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line.startswith("|"):
                continue
            if set(line.replace("|", "").strip()) <= set("-: "):
                continue
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            rows.append(cells)
    return rows


# ------------------------------------------------------------ Venetian
VEN_SRC = os.path.join(RAW, "venetian_dse_nov_2026_schedule.md")
VEN_URL = "https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/dse-nov-2026-schedule.pdf"
DATE_RE = re.compile(r"(MONDAY|TUESDAY|WEDNESDAY|THURSDAY|FRIDAY|SATURDAY|SUNDAY),\s+(JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER)\s+(\d+)")

# Structure sheets opened and read this session (see raw notes in README/sources).
# event number -> sheet number, or a (event, name-suffix) -> sheet for split events.
SHEET_BY_EVENT = {
    "1": "10",    # $300 Event 1 (1A-1D), sheet 10
    "7": "2",     # #7 $400 NLH 1A/1B, sheet 2
    "3": "18", "4": "18", "5": "18",   # RaceDay Stack, sheet 18
    "33": "19", "37": "19",            # LIPS Ladies satellites, sheet 19
    # $200 bounty / PKO events, sheet 1 (events confirmed by sheet 1 in earlier reading)
    "8": "1", "9": "1", "11": "1", "13": "1", "15": "1", "21": "1", "22": "1",
    "23": "1", "25": "1", "60": "1", "61": "1", "62": "1", "64": "1",
}
SHEET_26 = {"1A": "12", "1C": "12", "1E": "12"}  # structure_12 is labelled Days A/C/E


def parse_venetian():
    rows = table_rows(VEN_SRC)
    cur_date = None
    prev_time = None
    flights, restarts = [], []
    order = 0
    for cells in rows:
        if len(cells) < 9:
            continue
        date_cell, eno, name, time_s, reg, gtd, chips, lvl, coin = cells[:9]
        if date_cell.upper().startswith("DATE"):
            continue
        t = parse_time(time_s)
        m = DATE_RE.search(date_cell.upper())
        if m:
            cur_date = dt.date(2026, MONTHS[m.group(2)], int(m.group(3)))
            date_source = "printed"
        else:
            if cur_date is None:
                raise SystemExit("row before any date: " + str(cells))
            if prev_time is not None and t < prev_time and prev_time.hour >= 12 and t.hour < 12:
                cur_date = cur_date + dt.timedelta(days=1)
                date_source = "inferred from row order (day label omitted, time returns to AM)"
            else:
                date_source = "inferred from row order (day label omitted)"
        prev_time = t
        weekday_printed = None
        if m:
            weekday_printed = m.group(1).title()
        order += 1
        name = clean(name)
        base = dict(
            order=order,
            date=cur_date.isoformat(),
            weekday=cur_date.strftime("%A"),
            date_source=date_source if not m else "printed",
            weekday_printed=weekday_printed,
            event_no=eno,
            name=name,
            time=time_s,
            reg_closes=reg or None,
            guarantee=money_to_int(gtd),
            guarantee_text=clean(gtd) or None,
            chips=money_to_int(chips),
            levels=clean(lvl) or None,
            coin=clean(coin) or None,
            source=VEN_URL,
        )
        buy_m = re.search(r"\$([\d,]+)", name)
        buy = int(buy_m.group(1).replace(",", "")) if buy_m else None
        is_restart = ("RESTART" in name.upper()) or ("FINAL TABLE" in name.upper()) or (buy is None and not reg)
        if is_restart:
            restarts.append(base)
            continue
        base["buy_in"] = buy
        # guarantee text "2 SEATS" -> satellite seats (no dollar guarantee)
        base["satellite"] = "SATELLITE" in name.upper()
        # sheet linkage: only sheets opened and read
        sheet = None
        if eno == "26":
            # Sheet 12 labels its days A/C/E; mapping those to flight names 1A/1C/1E
            # is NOT confirmed, so no #26 flight is marked as checked.
            sheet = None
        elif eno in SHEET_BY_EVENT:
            sheet = SHEET_BY_EVENT[eno]
        base["structure_sheet"] = sheet
        base["structure_sheet_url"] = (
            f"https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_{sheet}.pdf"
            if sheet else None)
        flights.append(base)
    return flights, restarts


# ------------------------------------------------------------ Wynn WPT
WPT_SRC = os.path.join(RAW, "wynn_wpt_world_championship_schedule.md")
WPT_URL = "https://cdn.wynnresorts.com/image/upload/v1757097329/visitwynn_pdfs_files/Poker/WPT/WPT_World_Championship_Schedule.pdf"
WPT_DATE_RE = re.compile(r"^(\w+)\.?\s+(\d+)\s+(\w+)$")
WPT_MONTHS = {"Nov": 11, "Dec": 12}


def parse_wpt():
    rows = table_rows(WPT_SRC)
    out = []
    order = 0
    for cells in rows:
        if len(cells) < 7:
            continue
        date_label, time_s, event, buy, gtd, chips, lvl = cells[:7]
        if date_label.upper().startswith("DATE"):
            continue
        order += 1
        m = re.match(r"(\w+)\.?\s+(\d+)\s+(\w+)", date_label)
        mon, day, wd_printed = m.group(1), int(m.group(2)), m.group(3)
        cal = dt.date(2026, WPT_MONTHS[mon[:3]], day)
        conflict = cal.strftime("%A") != wd_printed
        buy_val = money_to_int(re.sub(r"\*+", "", buy))
        footnotes = "".join(sorted(set(re.findall(r"\*+", buy + gtd + event))))
        out.append(dict(
            order=order,
            date=cal.isoformat(),
            date_label_printed=date_label,
            weekday=cal.strftime("%A"),
            calendar_conflict=conflict,
            time=time_s,
            event=clean(event),
            buy_in=buy_val,
            buy_in_text=clean(buy) or None,
            guarantee=money_to_int(gtd),
            guarantee_text=clean(gtd) or None,
            chips=money_to_int(chips),
            levels=clean(lvl) or None,
            footnote_markers=footnotes or None,
            source=WPT_URL,
        ))
    return out


def main():
    flights, restarts = parse_venetian()
    with open(os.path.join(OUT, "venetian_flights.json"), "w", encoding="utf-8") as f:
        json.dump(flights, f, indent=1)
    with open(os.path.join(OUT, "venetian_restarts.json"), "w", encoding="utf-8") as f:
        json.dump(restarts, f, indent=1)
    wpt = parse_wpt()
    with open(os.path.join(OUT, "wynn_wpt.json"), "w", encoding="utf-8") as f:
        json.dump(wpt, f, indent=1)
    inferred = [r for r in flights if not r["date_source"].startswith("printed")]
    print(f"venetian flights={len(flights)} restarts/finals={len(restarts)} inferred dates={len(inferred)}")
    for r in inferred:
        print("  inferred:", r["date"], r["time"], "#" + r["event_no"], r["name"][:50], "|", r["date_source"][:30])
    conf = [r for r in wpt if r["calendar_conflict"]]
    print(f"wpt rows={len(wpt)} calendar conflicts={len(conf)}")
    for r in conf:
        print("  conflict:", r["date_label_printed"], r["time"], r["event"][:50])
    print("wpt rows with no buy-in (structure/final-table rows):", sum(1 for r in wpt if r["buy_in"] is None))


if __name__ == "__main__":
    main()
