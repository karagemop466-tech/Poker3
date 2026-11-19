#!/usr/bin/env python3
"""The day plan must never publish an impossible sequence.

`site/data.json` prints a fallback rule directly beneath the day plan:

    "Fallback = the next sheet-screened candidate that starts after the primary's
     estimated finish plus a 30-minute transfer, so it can actually be played after
     the primary."

Before 2026-11-19 the builder did not apply that rule. It took the next eligible row
by guarantee and called it a fallback even when it started inside the primary's
session, so five of the seven trip days named a fallback that overlapped the primary
that sat next to it on the same page. This test pins the rule.
"""
from __future__ import annotations

import json
import pathlib
import unittest
from datetime import datetime

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / "site" / "data.json"


def clock_minutes(value: str) -> int:
    t = datetime.strptime(value.strip().upper(), "%I:%M %p")
    return t.hour * 60 + t.minute


class FallbackHonoursItsOwnRule(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db = json.loads(DATA.read_text(encoding="utf-8"))
        cls.by_id = {e["id"]: e for e in cls.db["events"]}
        cls.transfer = cls.db["planNotes"]["transfer"]

    def test_rule_is_published(self):
        """The published rule must state both readings, because the page prints both labels."""
        rule = self.db["planNotes"]["fallbackRule"]
        self.assertIn("playable after the primary", rule)
        self.assertIn("replaces the primary", rule)
        self.assertIn("same-day alternative", rule)

    def test_no_fallback_starts_before_the_primary_finishes(self):
        for day in self.db["dayPlan"]:
            if not day["fallback"]:
                continue
            primary = self.by_id[day["primary"]]
            fallback = self.by_id[day["fallback"]]
            ready = clock_minutes(primary["time"]) + primary["sessionMin"] + self.transfer
            self.assertGreaterEqual(
                clock_minutes(fallback["time"]), ready,
                f"{day['date']}: fallback {fallback['name']} at {fallback['time']} starts before the primary "
                f"{primary['name']} can realistically finish ({primary['endEstimate']}) plus the transfer")

    def test_an_overlapping_row_is_labelled_an_alternative(self):
        for day in self.db["dayPlan"]:
            if not day["fallbackAlternativeId"]:
                continue
            self.assertFalse(day["fallback"], f"{day['date']} names both a fallback and an alternative")
            self.assertIn("same-day alternative", day["fallbackReason"])

    def test_every_day_of_the_trip_has_a_primary(self):
        self.assertEqual(7, len(self.db["dayPlan"]))
        for day in self.db["dayPlan"]:
            self.assertTrue(day["primary"], f"{day['date']} has no primary candidate")


if __name__ == "__main__":
    unittest.main()
