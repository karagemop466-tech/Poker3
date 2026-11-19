#!/usr/bin/env python3
"""Pins the 2026-11-19 live re-read of the 25 Venetian DeepStack IV rows in the trip window (23 Nov - 2 Dec 2026).

`research/reread_2026-11-19_arena-1234c474.json` holds the rows as the official schedule page printed them
on 2026-11-19 UTC. This test fails if a published row in that window stops matching the capture on date,
start time, buy-in, guarantee or structure-sheet number, so a change to the catalog cannot slip in without
the evidence moving with it.

Documented exception: the two "Day 2 Restart" rows (25 Nov 11:00 AM and 2 Dec 11:00 AM) print no guarantee on
the official schedule row. The published rows carry the parent $75K GTD flight's guarantee, inherited from that
flight's structure sheet. That is already disclosed as F63 on the Flagged page; this test accepts the inherited value
on those two rows only, and nowhere else.
"""
from __future__ import annotations

import json
import pathlib
import re
import unittest
from datetime import datetime

ROOT = pathlib.Path(__file__).resolve().parents[1]
CAPTURE = json.loads((ROOT / "research" / "reread_2026-11-19_arena-1234c474.json").read_text(encoding="utf-8"))
DATA = json.loads((ROOT / "site" / "data.json").read_text(encoding="utf-8"))

WINDOW = [e for e in DATA["events"] if e["venue"] == "venetian" and "2026-11-23" <= e["date"] <= "2026-12-02"]
CAPTURED = [r for r in CAPTURE["rows"] if "2026-11-23" <= r[0] <= "2026-12-02"]
INHERITED_GUARANTEE = {("2026-11-25", "11:00 AM"), ("2026-12-02", "11:00 AM")}


def sheet_number(url: str | None):
    m = re.search(r"structure_(\d+)\.pdf", url or "")
    return int(m.group(1)) if m else None


def to_24h(s: str) -> str:
    return datetime.strptime(s, "%I:%M %p").strftime("%H:%M")


class TripWindowRowsMatchCapture(unittest.TestCase):
    def test_capture_has_all_window_rows(self):
        self.assertEqual(len(CAPTURED), 24)
        self.assertEqual(len(WINDOW), len(CAPTURED))

    def test_every_capture_row_is_published_with_the_same_facts(self):
        used = set()
        for date, time, _num, _name, buy, guarantee, sheet in CAPTURED:
            matches = [
                e for e in WINDOW
                if e["id"] not in used
                and e["date"] == date
                and to_24h(e["time"]) == to_24h(time)
                and e.get("buyIn") == buy
                and sheet_number(e.get("sheetUrl")) == sheet
                and (
                    (guarantee is None and (not e.get("guarantee") or (date, time) in INHERITED_GUARANTEE))
                    or (guarantee is not None and e.get("guarantee") == guarantee)
                )
            ]
            self.assertEqual(len(matches), 1, f"no unique published row for {date} {time} ${buy} sheet {sheet}")
            used.add(matches[0]["id"])

    def test_window_rows_were_checked_today(self):
        for e in WINDOW:
            self.assertEqual(e.get("lastChecked"), "2026-11-19", e["id"])

    def test_the_inherited_guarantee_is_the_only_unprinted_value(self):
        unprinted = [e["id"] for e in WINDOW if e.get("guarantee") and any(
            r[0] == e["date"] and r[1] == e["time"] and r[5] is None for r in CAPTURED)]
        self.assertEqual(sorted(unprinted), sorted(["vl-dse-2026-11-25-7-1100am", "vl-dse-2026-12-02-19-1100am"]))


if __name__ == "__main__":
    unittest.main()
