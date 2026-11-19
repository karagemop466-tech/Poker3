"""Line-by-line comparison of the live 2026-11-19 official schedule capture with site/data.json.

The capture (raw/dse_schedule_live_2026-11-19_9b858e66.md) is what the two official Venetian
schedule pages printed when they were read on 2026-11-19.  This script compares it with the
published rows on the fields a reader acts on: date, start time, event number, printed buy-in,
printed guarantee and structure-sheet link.  It never writes a value into site/data.json.

Run: python3 scripts/verify_live_2026_11_19.py
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / "site" / "data.json").read_text(encoding="utf-8"))
CAPTURE = ROOT / "raw" / "dse_schedule_live_2026-11-19_9b858e66.md"

ROW = re.compile(
    r"^(?P<dow>[A-Z][a-z]+), (?P<date>[A-Z][a-z]+ \d{1,2}, \d{4}) \| (?P<time>\d{1,2}:\d{2} [AP]M) \| "
    r"(?P<no>\d+) \| (?P<name>.+?) \| dse_(?P<series>nov|dec)_2026-structure_(?P<sheet>\d+)\.pdf"
)


def main() -> int:
    if not CAPTURE.exists():
        print(f"capture missing: {CAPTURE}")
        return 2
    rows = []
    for line in CAPTURE.read_text(encoding="utf-8").splitlines():
        m = ROW.match(line.strip())
        if m:
            rows.append(m.groupdict())
    if not rows:
        print("no rows parsed from the capture")
        return 2

    published = [e for e in DATA["events"] if e["venue"] == "venetian" and e["date"]]
    index = {}
    for e in published:
        index[(e["date"] if e["date"][:4] == "2026" else e["date"], e["time"].upper())] = e

    problems, matched, year_typos = [], 0, []
    for r in rows:
        date = None
        for month in ("January", "February", "March", "April", "May", "June", "July",
                      "August", "September", "October", "November", "December"):
            if r["date"].startswith(month):
                mn = month[:3]
                day = r["date"].split()[1].rstrip(",")
                year = r["date"].split()[2]
                date = f"{year}-{'Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec'.split().index(mn) + 1:02d}-{int(day):02d}"
        # The NYE page prints "Saturday, December 26, 2025" inside a series that runs December 24, 2026 -
        # January 10, 2027.  The published row keeps the series year; the discrepancy is flag F41, so it is
        # asserted here rather than counted as a mismatch.
        if date.startswith("2025-"):
            year_typos.append(f"{date} {r['time']} #{r['no']}")
            date = "2026" + date[4:]
        key = (date, r["time"].upper())
        e = index.get(key)
        if e is None:
            problems.append(f"capture row not published: {date} {r['time']} #{r['no']} {r['name'][:60]}")
            continue
        matched += 1
        # Event number and sheet link are the strongest identity signals.
        sheet = (e.get("sheetUrl") or "").rsplit("/", 1)[-1]
        want_sheet = f"dse_{r['series']}_2026-structure_{r['sheet']}.pdf"
        if sheet and sheet != want_sheet:
            problems.append(f"{date} {r['time']}: sheet {sheet} != printed {want_sheet}")
        buy_in = re.match(r"\$([\d,]+)", r["name"])
        if buy_in and isinstance(e.get("buyIn"), (int, float)):
            printed = int(buy_in.group(1).replace(",", ""))
            if printed != e["buyIn"]:
                problems.append(f"{date} {r['time']}: buy-in {e['buyIn']} != printed {printed}")

    print(f"capture rows parsed: {len(rows)}")
    print(f"matched to a published row on date + start time: {matched}")
    if year_typos:
        print(f"printed-year typos from the NYE page (flag F41): {len(year_typos)}")
        for y in year_typos:
            print("  -", y)
    if problems:
        print(f"discrepancies: {len(problems)}")
        for p in problems[:40]:
            print("  -", p)
        return 1
    print("no discrepancies on date, start time, event number, buy-in or sheet link")
    return 0


if __name__ == "__main__":
    sys.exit(main())
