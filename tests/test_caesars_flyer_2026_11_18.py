"""Caesars Palace daily NLH rows must match the official 2026 flyer (read 2026-11-18).

Source: https://www.caesars.com/content/dam/empire/clv/casino/poker/tournament-schedule/clv-poker-daily-nlh-tournament-flyer-2026.pdf
(linked as "View Schedule" from https://www.caesars.com/caesars-palace/casino).
The flyer prints: 10 AM $100, 2 PM $160, 6 PM $100, 9 PM $160; $1,000 guarantee;
20,000 chips; 20-minute levels; $50 optional add-on at the first break; re-entry
within the first break; registration closes at the start of level seven.
"""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FLYER = ("https://www.caesars.com/content/dam/empire/clv/casino/poker/tournament-schedule/"
         "clv-poker-daily-nlh-tournament-flyer-2026.pdf")


class CaesarsFlyerRows(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        data = json.loads((ROOT / "site" / "data.json").read_text(encoding="utf-8"))
        cls.rows = sorted((e for e in data["events"] if e.get("venue") == "caesars"),
                          key=lambda e: e["id"])
        cls.flags = {f["id"]: f for f in data["flags"]}

    def test_four_daily_events_with_flyer_times_and_buy_ins(self):
        got = [(r["time"], r["buyIn"]) for r in self.rows]
        self.assertEqual(got, [("10:00 AM", 100), ("2:00 PM", 160), ("6:00 PM", 100), ("9:00 PM", 160)])

    def test_guarantee_is_flyer_value(self):
        self.assertEqual({r["guarantee"] for r in self.rows}, {1000})

    def test_every_row_cites_the_flyer(self):
        for r in self.rows:
            self.assertEqual(r["sheetUrl"], FLYER, r["id"])
            self.assertEqual(r["scheduleUrl"], FLYER, r["id"])

    def test_reentry_and_addon_are_recorded_and_keep_rows_out_of_single_entry(self):
        for r in self.rows:
            rules = r["rules"]
            self.assertEqual(rules["reEntry"]["status"], "allowed", r["id"])
            self.assertEqual(rules["addOn"]["status"], "allowed", r["id"])
            self.assertEqual(rules["singleEntry"]["status"], "multiple-entries", r["id"])
            self.assertEqual(rules["reEntry"]["retrieved"], "2026-11-18", r["id"])

    def test_fee_excerpt_matches_buy_in(self):
        for r in self.rows:
            fee = r["rules"]["fee"]["excerpt"]
            if r["buyIn"] == 100:
                self.assertIn("$100 buy in", fee)
            else:
                self.assertIn("$160 buy in", fee)

    def test_flag_f90_and_f73_are_published(self):
        self.assertIn("F90", self.flags)
        self.assertIn("$160", self.flags["F90"]["title"])
        self.assertIn("flyer", self.flags["F73"]["title"].lower())


if __name__ == "__main__":
    unittest.main()
