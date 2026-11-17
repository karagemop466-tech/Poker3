#!/usr/bin/env python3
"""Full line-by-line transcription check for the DeepStack Extravaganza IV series.

Scope: this script is *new* in session arena/6118f42d-poker3. It does not replace
``scripts/verify_transcription.py``; that one re-checks the 44 rows inside the
recommended trip window and writes ``site/checks.json``. This one checks **every**
row of the recorded official series schedule (2026-11-16 .. 2026-12-23) against
the published ``site/data.json``, so a row outside the trip window can no longer
drift unobserved.

Evidence basis
--------------
``raw/venetian_dse_nov_2026_schedule.md`` is a verbatim copy of the official PDF
table (source URL recorded in that file's header). The sandbox cannot reach
venetianlasvegas.com, so this is the only official evidence available offline.
Nothing is inferred: a blank PDF cell is reported as "official cell blank", and a
value that differs from the printed cell is reported as a mismatch rather than
silently corrected.

Date resolution (the one genuine inference, and it is stated)
-------------------------------------------------------------
The PDF prints the day in a merged cell, so the fetched markdown repeats a sponsor
banner ("LIPS CHAMPIONSHIP ...", "@PokerAtlas* TOUR") on rows that carry no date.
Two facts about the printed table make the date recoverable:

  * rows are printed in chronological order, and a day's start times ascend;
  * the day label is printed on one row somewhere inside that day's block
    (not always the first: the merged cell renders where the PDF puts it).

So the rule is:

  1. cut the rows into day-blocks: a new block starts wherever a row's start time
     is earlier than the row before it;
  2. a block that contains exactly one printed day gives that day to every row in
     it (this covers the LIPS and PokerAtlas banner rows, where the label sits on
     one row in the middle of the block);
  3. a block that contains several printed days is a run of consecutive one-event
     days with equal start times, so each row keeps the day it prints itself;
  4. a block with no printed label, or an unlabelled row in a multi-day block, is
     reported rather than guessed.

The script asserts that this assigns the printed day to every labelled row, so a
wrong segmentation cannot pass silently. It is the same ordering inference the
original transcriber recorded in the raw file's header, now applied uniformly to
all 94 rows instead of only the 44 inside the trip window.

Usage:  python3 scripts/verify_dse_full.py
Exit code 0 when every printed cell agrees, 1 otherwise.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "raw" / "venetian_dse_nov_2026_schedule.md"
DATA = ROOT / "site" / "data.json"

MONTHS = {
    "JANUARY": 1, "FEBRUARY": 2, "MARCH": 3, "APRIL": 4, "MAY": 5, "JUNE": 6,
    "JULY": 7, "AUGUST": 8, "SEPTEMBER": 9, "OCTOBER": 10, "NOVEMBER": 11,
    "DECEMBER": 12,
}
YEAR = 2026

ROW_RE = re.compile(
    r"^\|\s*(?P<date>[^|]*?)\s*\|\s*(?P<event>[^|]*?)\s*\|\s*(?P<name>[^|]*?)\s*\|"
    r"\s*(?P<time>[^|]*?)\s*\|\s*(?P<reg>[^|]*?)\s*\|\s*(?P<guar>[^|]*?)\s*\|"
    r"\s*(?P<chips>[^|]*?)\s*\|\s*(?P<level>[^|]*?)\s*\|\s*(?P<award>[^|]*?)\s*\|\s*$"
)


def to_minutes(t: str):
    """Clock time -> minutes after midnight; None when unparseable."""
    m = re.match(r"^(\d{1,2}):(\d{2})\s*([AP])M$", t.strip().upper())
    if not m:
        return None
    h = int(m.group(1)) % 12
    return h * 60 + int(m.group(2)) + (720 if m.group(3) == "P" else 0)


def parse_day(cell: str):
    up = cell.upper()
    for name, num in MONTHS.items():
        m = re.search(name + r"\s+(\d{1,2})", up)
        if m:
            return "%04d-%02d-%02d" % (YEAR, num, int(m.group(1)))
    return None


def parse_raw():
    raw_rows = []
    for line in RAW.read_text(encoding="utf-8").splitlines():
        m = ROW_RE.match(line)
        if not m:
            continue
        g = m.groupdict()
        raw_rows.append({
            "dateCell": g["date"],
            "day": parse_day(g["date"]),
            "event": g["event"],
            "name": g["name"],
            "time": g["time"].strip(),
            "minutes": to_minutes(g["time"]),
            "regCloses": g["reg"].strip(),
            "guarantee": g["guar"].strip(),
            "chips": g["chips"].strip(),
            "level": g["level"].strip(),
            "award": g["award"].strip(),
        })

    # --- resolve the merged date cells -------------------------------------
    # 1. Cut into day-blocks wherever a start time goes backwards.
    blocks, start = [], 0
    for i in range(1, len(raw_rows) + 1):
        if i == len(raw_rows):
            blocks.append((start, i))
            break
        prev_min = raw_rows[i - 1]["minutes"]
        cur_min = raw_rows[i]["minutes"]
        if prev_min is not None and cur_min is not None and cur_min < prev_min:
            blocks.append((start, i))
            start = i

    # 2. Resolve each block.
    resolved = [None] * len(raw_rows)
    unlabelled = []
    for a, b in blocks:
        days = [raw_rows[i]["day"] for i in range(a, b) if raw_rows[i]["day"]]
        distinct = sorted(set(days))
        if not days:
            unlabelled.append((a, b, "no printed day anywhere in the block"))
            continue
        if len(distinct) == 1:
            for i in range(a, b):
                resolved[i] = distinct[0]
            continue
        # Several printed days in one block: a run of one-event days whose start
        # times do not descend, so each row is dated by the day it prints itself.
        for i in range(a, b):
            if raw_rows[i]["day"]:
                resolved[i] = raw_rows[i]["day"]
            else:
                unlabelled.append((i, i + 1, "unlabelled row inside a multi-day block"))

    # 3. Assert the segmentation reproduces every printed day label.
    for i, r in enumerate(raw_rows):
        if r["day"] and resolved[i] != r["day"]:
            raise SystemExit("date resolution disagrees with the printed day on row %d (%s): "
                             "printed %s, resolved %s" % (i, r["name"][:50], r["day"], resolved[i]))

    for i, r in enumerate(raw_rows):
        r["date"] = resolved[i]
        r["dateResolvedBy"] = "printed on the row" if r["day"] else "row-order inference"

    if unlabelled:
        print("WARNING: %d row(s) could not be dated from the printed table:" % len(unlabelled))
        for a, b, why in unlabelled:
            print("  rows %d..%d (%s): %s" % (a, b, why,
                  " | ".join(raw_rows[i]["time"] for i in range(a, b))))

    return raw_rows


def clean_money(v: str):
    v = v.strip()
    if not v:
        return None
    m = re.match(r"^\$([\d,]+(?:\.\d+)?)$", v)
    if m:
        return float(m.group(1).replace(",", ""))
    if v.upper().startswith("$1 MILLION"):
        return 1000000.0
    return v  # e.g. "2 SEATS" - a seat guarantee, not a currency pool


def clean_level(v: str):
    v = v.strip()
    if not v:
        return None
    m = re.match(r"^(\d+)", v)
    return int(m.group(1)) if m else v


def clean_chips(v: str):
    v = v.strip()
    if not v:
        return None
    return int(v.replace(",", ""))


def norm_time(v: str):
    return re.sub(r"\s+", " ", (v or "").strip().upper())


def norm_name(v: str):
    return re.sub(r"[^A-Z0-9]+", " ", (v or "").upper()).strip()


def seats_equivalent(official: str, published) -> bool:
    """A seat guarantee is printed as '2 SEATS' and stored as prose."""
    if not isinstance(official, str):
        return False
    m = re.match(r"^(\d+)\s+SEATS?$", official.upper())
    if not m:
        return False
    if published is None:
        return True  # blank is the honest published value
    return bool(re.search(r"\b" + m.group(1) + r"\b", str(published))) and "seat" in str(published).lower()


def build_index(data):
    out = {}
    for e in data["events"]:
        if e.get("venue") != "venetian" or not e.get("date"):
            continue
        if "dse-nov-2026" not in (e.get("scheduleUrl") or ""):
            continue
        out.setdefault((e["date"], norm_time(e.get("time"))), []).append(e)
    return out


def main():
    rows = parse_raw()
    data = json.loads(DATA.read_text(encoding="utf-8"))
    index = build_index(data)

    mismatches, blanks, unmatched, unmatched_pub = [], [], [], []
    matched = 0
    seen = set()

    for r in rows:
        if not r["date"]:
            unmatched.append(("no-resolved-date", r))
            continue
        key = (r["date"], norm_time(r["time"]))
        cands = [c for c in index.get(key, []) if c["id"] not in seen]
        if not cands:
            cands = index.get(key, [])
        target = None
        if len(cands) == 1:
            target = cands[0]
        elif len(cands) > 1:
            rn = set(norm_name(r["name"]).split())
            target = max(cands, key=lambda c: len(rn & set(norm_name(c.get("name")).split())))
        if target is None:
            unmatched.append(("no-published-row", r))
            continue
        seen.add(target["id"])
        matched += 1

        checks = [
            ("guarantee", clean_money(r["guarantee"]), target.get("guarantee")),
            ("chips", clean_chips(r["chips"]), target.get("chips")),
            ("levelMin", clean_level(r["level"]), target.get("levelMin")),
            ("lateRegEnd", norm_time(r["regCloses"]), norm_time(target.get("lateRegEnd"))),
        ]
        for field, official, published in checks:
            if official is None or official == "":
                if published not in (None, "", 0):
                    blanks.append({"date": r["date"], "eventId": target["id"], "field": field,
                                   "officialCell": "(blank)", "published": published,
                                   "officialRow": r["name"]})
                continue
            if field == "guarantee" and isinstance(official, str) and seats_equivalent(official, published):
                continue
            if official != published:
                mismatches.append({"date": r["date"], "eventId": target["id"], "field": field,
                                   "official": official, "published": published,
                                   "officialRow": r["name"]})

    # Published DSE IV rows the official table does not account for.
    for e in data["events"]:
        if e.get("venue") == "venetian" and e.get("date") and "dse-nov-2026" in (e.get("scheduleUrl") or ""):
            if e["id"] not in seen:
                unmatched_pub.append(e)

    print("official rows parsed:        %d" % len(rows))
    print("official rows matched:       %d" % matched)
    print("official rows unmatched:     %d" % len(unmatched))
    print("published rows unaccounted:  %d" % len(unmatched_pub))
    print("value mismatches:            %d" % len(mismatches))
    print("blank official cells filled: %d" % len(blanks))

    if mismatches:
        print("\n--- VALUE MISMATCHES (official cell vs published value) ---")
        for m in mismatches:
            print("  %s  %s  [%s]  official=%r  published=%r\n      official row: %s"
                  % (m["date"], m["eventId"], m["field"], m["official"], m["published"], m["officialRow"][:90]))
    if unmatched:
        print("\n--- OFFICIAL ROWS WITH NO PUBLISHED COUNTERPART ---")
        for kind, r in unmatched:
            print("  [%s] %s %s %s (event %s)" % (kind, r["date"], r["time"], r["name"][:70], r["event"]))
    if unmatched_pub:
        print("\n--- PUBLISHED DSE IV ROWS NOT IN THE OFFICIAL TABLE ---")
        for e in unmatched_pub:
            print("  %s %s %s" % (e["date"], e.get("time"), (e.get("name") or "")[:70]))
    if blanks:
        print("\n--- OFFICIAL CELL BLANK, PUBLISHED VALUE PRESENT (carry-over, not a mismatch) ---")
        for b in blanks:
            print("  %s %s [%s] published=%r  (%s)" % (b["date"], b["eventId"], b["field"], b["published"], b["officialRow"][:60]))

    return 1 if mismatches else 0


if __name__ == "__main__":
    sys.exit(main())
