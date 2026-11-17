#!/usr/bin/env python3
"""Guard against trip-window drift between the plan and the prose that describes it.

The trip was moved twice. It was 25 Nov - 2 Dec, then 17-19 Nov for quoting, and it is now
**23-30 November 2026** (seven nights, check-out 11:00 on 30 Nov). Flags F54, F28, F15, F36
and suggestion S21 kept describing the retired 25 Nov - 2 Dec window after the move: F54
said two nights did not qualify for the poker rate and named 30 Nov and 1 Dec, which are
not in the stay at all, while the nights that actually fail are 23 and 24 November.

These tests tie the prose to `site/data.json`, so a future window change cannot leave a
flag describing a stay that is no longer booked.
"""
from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / "site" / "data.json").read_text(encoding="utf-8"))

TRIP_START, TRIP_END = "2026-11-23", "2026-11-30"


class TripWindow(unittest.TestCase):
    def test_trip_profile_matches_this_test(self):
        self.assertEqual(DATA["trip"]["start"], TRIP_START)
        self.assertEqual(DATA["trip"]["end"], TRIP_END)
        self.assertEqual(DATA["trip"]["nights"], 7)

    def test_every_plan_day_falls_inside_the_stay(self):
        for day in DATA["dayPlan"]:
            self.assertGreaterEqual(day["date"], TRIP_START, day["date"])
            self.assertLess(day["date"], TRIP_END, f"{day['date']} is a departure day, not a playable night")

    def test_flags_do_not_describe_the_retired_window_as_current(self):
        """A flag may mention the old window only as history, never as the live plan."""
        banned = [
            "leave Nov 30 and Dec 1",
            "a $200 primary on Nov 30 and Dec 1",
            "for 2026-11-25 to 2026-12-02 is also",
            "still unpriced",
        ]
        blob = json.dumps(DATA, ensure_ascii=False)
        for phrase in banned:
            self.assertNotIn(phrase, blob, f"retired trip-window wording survives: {phrase!r}")

    def test_poker_rate_flag_names_the_nights_that_actually_fail(self):
        """F54 must name 23 and 24 November, the two nights whose primary is under $300."""
        failing = [d["date"] for d in DATA["dayPlan"]
                   if d.get("primaryBuyIn") is not None and d["primaryBuyIn"] < 300]
        self.assertEqual(failing, ["2026-11-23", "2026-11-24"])
        f54 = next(f for f in DATA["flags"] if f["id"] == "F54")
        self.assertIn("23 and 24 November", f54["detail"])
        for wrong in ("Nov 30 and Dec 1", "Nov 30, 1 December", "Dec 2 $200 entry"):
            self.assertNotIn(wrong, f54["detail"])

    def test_poker_rate_flag_agrees_with_the_day_plan_fields(self):
        unsatisfied = [d["date"] for d in DATA["dayPlan"] if d.get("pokerRateSatisfied") is False]
        self.assertEqual(unsatisfied, ["2026-11-23", "2026-11-24"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
