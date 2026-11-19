"""Regression checks for the 2026-11-19 primary-sheet re-read (session arena/7d533b48-poker3).

They assert the published flag F93, the corrected Q14/Q15 answers, the F17 trip-window clarification and the dated
research record. They do not fetch the venue pages.
"""
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RECORD = os.path.join(ROOT, "research", "reread_2026-11-19_7d533b48.md")


def _data():
    with open(os.path.join(ROOT, "site", "data.json"), encoding="utf-8") as f:
        return json.load(f)


class PrimarySheetRereadTests(unittest.TestCase):
    def setUp(self):
        self.data = _data()
        self.flags = {f["id"]: f for f in self.data["flags"]}
        self.questions = {q["id"]: q for q in self.data["questions"]}
        with open(RECORD, encoding="utf-8") as f:
            self.record = f.read()

    def test_booking_price_gap_is_flagged_as_high(self):
        flag = self.flags["F93"]
        self.assertEqual(flag["severity"], "High")
        self.assertIn("loading", flag["detail"])
        self.assertIn("$4,010.55", flag["detail"])
        self.assertIn("EPOKR25", flag["detail"])

    def test_q15_no_longer_carries_the_placeholder_sentence(self):
        answer = self.questions["Q15"]["answer"]
        self.assertNotIn("printed $XXX", answer)
        self.assertIn("F93", answer)
        self.assertIn("not a price for today", answer)

    def test_q14_states_the_trip_window_start(self):
        self.assertIn("11:00 AM on 25 November", self.questions["Q14"]["answer"])

    def test_f17_states_the_trip_window_restart(self):
        detail = self.flags["F17"]["detail"]
        self.assertIn("no opening event starts before 11:10 AM", detail)
        self.assertIn("11:00 AM on 25 November", detail)
        self.assertIn("9:10 AM", detail)  # the 4c657755 facts stay in place

    def test_record_cites_the_primary_sheets_and_the_overlap(self):
        for sheet in ("structure_30", "structure_1", "structure_6", "structure_5",
                      "structure_7", "structure_11", "structure_22", "structure_2"):
            self.assertIn(sheet, self.record)
        self.assertIn("4c657755", self.record)
        self.assertIn("F93", self.record)
        self.assertNotIn("F94", self.record)


if __name__ == "__main__":
    unittest.main()
