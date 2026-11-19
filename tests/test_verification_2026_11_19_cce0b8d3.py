"""Regression checks for the independent 2026-11-19 re-verification (session arena-cce0b8d3).

The record in research/verification_2026-11-19_arena-cce0b8d3.json was read from
the live official pages on 2026-11-19. These tests fail if any published
trip-window value drifts from that record. They do not re-fetch the venue pages
and they do not change any venue value.
"""
import json
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RECORD = os.path.join(ROOT, "research", "verification_2026-11-19_arena-cce0b8d3.json")
DATA = os.path.join(ROOT, "site", "data.json")


def _norm(value):
    text = str(value or "").lower()
    text = text.replace("’", "'").replace("‘", "'").replace("~ ", "~")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _sheet_number(url):
    # DSE IV sheets only; the NYE series reuses the same structure numbers in
    # dse_dec_2026-structure_<N>.pdf and must not be matched to a DSE IV sheet.
    match = re.search(r"dse_nov_2026-structure_(\d+)\.pdf$", url or "")
    return int(match.group(1)) if match else None


class VerificationRecordTests(unittest.TestCase):
    def setUp(self):
        with open(RECORD, encoding="utf-8") as f:
            self.record = json.load(f)
        with open(DATA, encoding="utf-8") as f:
            self.data = json.load(f)
        self.events = self.data["events"]

    def test_record_is_dated_and_declares_zero_diffs(self):
        self.assertEqual(self.record["readOn"], "2026-11-19")
        self.assertEqual(self.record["result"]["valueDiffs"], 0)
        self.assertEqual(len(self.record["venetian_schedule"]), 19)
        self.assertEqual(len(self.record["wynn_schedule"]), 13)
        self.assertEqual(len(self.record["structure_sheets"]), 7)

    def test_venetian_trip_window_rows_match_live_schedule(self):
        checked = 0
        for row in self.record["venetian_schedule"]:
            matches = [e for e in self.events
                       if e.get("venue") == "venetian" and e.get("date") == row["date"]
                       and e.get("time") == row["time"]]
            self.assertEqual(len(matches), 1, f"{row['date']} {row['time']}: {len(matches)} published rows")
            event = matches[0]
            self.assertEqual(_norm(event["name"]), _norm(row["name"]), event["id"])
            self.assertEqual(event.get("buyIn"), row["buyIn"], event["id"])
            self.assertEqual(event.get("guarantee"), row["guarantee"], event["id"])
            self.assertEqual(_sheet_number(event.get("sheetUrl")), row["sheet"], event["id"])
            checked += 1
        self.assertEqual(checked, 19)

    def test_wynn_trip_window_rows_match_live_schedule(self):
        checked = 0
        for row in self.record["wynn_schedule"]:
            matches = [e for e in self.events
                       if e["id"].startswith("wynn-wpt") and e.get("date") == row["date"]
                       and e.get("time") == row["time"]]
            self.assertEqual(len(matches), 1, f"{row['date']} {row['time']}: {len(matches)} published rows")
            event = matches[0]
            self.assertEqual(_norm(event["name"]), _norm(row["event"]), event["id"])
            self.assertEqual(event.get("buyIn"), row["buyIn"], event["id"])
            self.assertEqual(event.get("guarantee") or "", row["guarantee"] or "", event["id"])
            self.assertEqual(event.get("chips"), row["chips"], event["id"])
            checked += 1
        self.assertEqual(checked, 13)

    def test_primary_structure_sheets_match_live_pdfs(self):
        for sheet in self.record["structure_sheets"]:
            rows = [e for e in self.events if _sheet_number(e.get("sheetUrl")) == sheet["sheet"]]
            self.assertTrue(rows, f"sheet {sheet['sheet']} has no published rows")
            for event in rows:
                self.assertEqual(event.get("chips"), sheet["chips"], event["id"])
                self.assertEqual(event.get("levelMin"), sheet["levelMin"], event["id"])
                self.assertEqual(_norm(event.get("lateReg")), _norm(sheet["lateReg"]), event["id"])
                parts = event["id"].split("-")
                number = parts[5] if len(parts) > 5 else ""
                if number in sheet["guaranteeByEvent"]:
                    self.assertEqual(event.get("guarantee"),
                                     sheet["guaranteeByEvent"][number], event["id"])

    def test_hotel_facts_match_live_pages(self):
        hotels = {h["id"]: h for h in self.data["hotels"]}
        venetian = hotels["venetian"]
        self.assertEqual(venetian["baseRateFloor"], 119)
        self.assertEqual(venetian["baseRateCeiling"], 209)
        self.assertEqual(venetian["resortFee"], 55)
        self.assertEqual(venetian["taxRate"], 13.38)
        self.assertEqual(venetian["parkingPerNight"], 20)
        self.assertIn("11:00 AM", venetian["checkInOut"])
        self.assertIn("3:00 PM", venetian["checkInOut"])
        self.assertIn("non-refundable", venetian["cancellation"])

        wynn = hotels["wynn"]
        self.assertEqual(wynn["resortFee"], 55)
        self.assertIn("12 p.m.", wynn["checkInOut"])
        self.assertIn("3 p.m.", wynn["checkInOut"])

    def test_open_flags_are_still_recorded(self):
        flags = {f["id"]: f for f in self.data["flags"]}
        self.assertIn("F93", flags)  # booking engine still prints no checkout total
        self.assertIn("F56", flags)  # Wynn Signature structures still "coming soon"
        self.assertIn("F31", flags)  # written one-entry cap still unpublished


if __name__ == "__main__":
    unittest.main()
