#!/usr/bin/env python3
"""Compare the 2026-11-19 live read of the official Venetian DSE IV trip-window rows (trip profile dates in site/data.json: 2026-11-23 to 2026-11-30)
(raw/dse_nov_2026_trip_window_live_2026-11-19_arena-3a186594.md) with site/data.json.

Exit 0 only if every live row matches exactly one published row on date, time, event name
(case and the page's own 'LImit' typo ignored, sub-description after ' - ' ignored), buy-in,
guarantee and structure-sheet file name, and every published trip-window row is matched.
"""
import datetime
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RAW = ROOT / "raw" / "dse_nov_2026_trip_window_live_2026-11-19_arena-3a186594.md"
DATA = ROOT / "site" / "data.json"


def norm_name(s):
    s = s.split(" - ")[0].split("<br>")[0]
    s = s.replace("NLH", "No Limit Hold'em").replace("LImit", "Limit")
    return re.sub(r"\s+", " ", s).strip().lower()


def trip_window():
    trip = json.loads(DATA.read_text())["trip"]
    return trip["start"], trip["end"]


def live_rows():
    out = []
    for line in RAW.read_text().splitlines():
        if not line.startswith("| ") or line.startswith("| Date") or line.startswith("| ---"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        date_txt, time_txt, num, name, sheet = cells[:5]
        day = datetime.datetime.strptime(date_txt.split(", ", 1)[1], "%B %d, %Y").date().isoformat()
        out.append({"date": day, "time": time_txt, "num": int(num), "name": name, "sheet": sheet})
    return out


def main():
    live = live_rows()
    start, end = trip_window()
    data = json.loads(DATA.read_text())["events"]
    pub = [e for e in data if e["venue"] == "venetian" and start <= e["date"] <= end]
    problems = []
    used = set()
    for r in live:
        hits = []
        for i, e in enumerate(pub):
            if i in used or e["date"] != r["date"] or e["time"] != r["time"]:
                continue
            sheet = (e.get("sheetUrl") or e.get("structureUrl") or "").rsplit("/", 1)[-1]
            if norm_name(e["name"]) != norm_name(r["name"]):
                continue
            if sheet != r["sheet"]:
                continue
            hits.append(i)
        if len(hits) != 1:
            problems.append(f"{r['date']} {r['time']} #{r['num']} {r['name']!r}: {len(hits)} matches")
            continue
        used.add(hits[0])
        e = pub[hits[0]]
        # buy-in and guarantee are printed in the name, so cross-check the numbers too
        printed = re.search(r"\$([\d,]+)", r["name"])
        if printed and int(printed.group(1).replace(",", "")) != e["buyIn"]:
            problems.append(f"{r['date']} {r['time']}: buy-in {e['buyIn']} vs printed {printed.group(1)}")
        g = re.search(r"\$([\d.]+)K GTD", r["name"])
        if g and e.get("guarantee") != round(float(g.group(1)) * 1000):
            problems.append(f"{r['date']} {r['time']}: guarantee {e.get('guarantee')} vs printed {g.group(1)}K")
    for i, e in enumerate(pub):
        if i not in used:
            problems.append(f"published row not on live page: {e['date']} {e['time']} {e['name']!r}")
    print(f"live rows: {len(live)}  published trip-window rows: {len(pub)}  matched: {len(used)}")
    for p in problems:
        print("MISMATCH:", p)
    print("PASS" if not problems else "FAIL")
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main())
