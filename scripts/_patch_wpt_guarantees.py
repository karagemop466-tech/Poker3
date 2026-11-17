#!/usr/bin/env python3
"""One-off correction of seven guarantee cells in the WPT transcript.

Each fix is a single cell brought back into agreement with the verbatim official
table recorded in raw/wynn_wpt_world_championship_schedule.md. Nothing is
inferred: a cell the official PDF leaves empty becomes '-', and a cell the PDF
prints becomes the printed value.

Rows are numbered as they appear in WYNN_WPT_ROWS (0-based).

 59  2026-12-12 2:00 PM  WPT Prime Championship Final Table          '75 Seats' -> '-'
 60  2026-12-12 2:00 PM  Super Gold Million Mystery Bounty Day 2     '75 Seats' -> '-'
 76  2026-12-14 12:00 PM Mixed Triple Draw (A-5, 2-7, Badugi) (2 Day)'25 Seats' -> '-'
 84  2026-12-15 11:00 AM Milestone Satellite ... 1C/Day 2            '-' -> '10 Seats'
 96  2026-12-18 6:00 PM  Milestone Satellite to $3,000 NLH           '-' -> '25 Seats'
116  2026-12-19 12:00 PM WPT World Championship Day 5                '10 Seats' -> '-'
117  2026-12-19 12:00 PM No Limit Hold'em Day 2                      '10 Seats' -> '-'

Run from the repository root:  python3 scripts/_patch_wpt_guarantees.py
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
TARGET = ROOT / "scripts" / "data_venues.py"

OLD_NEW = [
    ("2026-12-12|2:00 PM|WPT Prime Championship Final Table|-|75 Seats|-|-|**",
     "2026-12-12|2:00 PM|WPT Prime Championship Final Table|-|-|-|-|**"),
    ("2026-12-12|2:00 PM|Super Gold Million Mystery Bounty Day 2|-|75 Seats|-|-|**",
     "2026-12-12|2:00 PM|Super Gold Million Mystery Bounty Day 2|-|-|-|-|**"),
    ("2026-12-14|12:00 PM|Mixed Triple Draw (A-5, 2-7, Badugi) (2 Day)|1100|25 Seats|40000|40|**",
     "2026-12-14|12:00 PM|Mixed Triple Draw (A-5, 2-7, Badugi) (2 Day)|1100|-|40000|40|**"),
    ("2026-12-15|11:00 AM|Milestone Satellite to $10,400 World Championship 1C/Day 2|1100|-|20000|25|***",
     "2026-12-15|11:00 AM|Milestone Satellite to $10,400 World Championship 1C/Day 2|1100|10 Seats|20000|25|***"),
    ("2026-12-18|6:00 PM|Milestone Satellite to $3,000 NLH|400|-|20000|20",
     "2026-12-18|6:00 PM|Milestone Satellite to $3,000 NLH|400|25 Seats|20000|20"),
    ("2026-12-19|12:00 PM|WPT World Championship Day 5|-|10 Seats|-|-|**",
     "2026-12-19|12:00 PM|WPT World Championship Day 5|-|-|-|-|**"),
    ("2026-12-19|12:00 PM|No Limit Hold'em Day 2|-|10 Seats|-|-|**",
     "2026-12-19|12:00 PM|No Limit Hold'em Day 2|-|-|-|-|**"),
]

NOTE = "\n".join([
    "# Transcript of the official WPT World Championship schedule PDF: one line per",
    "# printed row, fields  date | start | event | buy-in | guarantee | chips | levels | marks.",
    "# '-' means the official cell is empty.",
    "#",
    "# Re-checked line by line against raw/wynn_wpt_world_championship_schedule.md on",
    "# 2026-11-17 by scripts/verify_wpt_full.py, which reports 136/136 rows matched and",
    "# names every difference. Seven guarantee cells were corrected in that pass: a",
    "# satellite's seat guarantee had been carried onto the non-satellite rows that share",
    "# its date and start time (rows 59, 60, 76, 116, 117 of this block), and two",
    "# satellites had lost the seat guarantee the PDF prints on their own row (rows 84, 96).",
    "",
])


def main():
    src = TARGET.read_text(encoding="utf-8")
    for old, new in OLD_NEW:
        n = src.count(old)
        if n != 1:
            raise SystemExit("expected exactly one match for %r, found %d" % (old, n))
        src = src.replace(old, new)
    marker = 'WYNN_WPT_ROWS = """'
    if marker not in src:
        raise SystemExit("WYNN_WPT_ROWS marker not found")
    if "Transcript of the official WPT World Championship schedule PDF" in src:
        print("note already present; skipping")
    else:
        src = src.replace(marker, NOTE + marker, 1)
    TARGET.write_text(src, encoding="utf-8")
    print("corrected %d guarantee cells in scripts/data_venues.py" % len(OLD_NEW))


if __name__ == "__main__":
    main()
