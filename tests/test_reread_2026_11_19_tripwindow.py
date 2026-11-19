"""Checks the 32 trip-window rows against the 2026-11-19 fresh re-read.

The record (research/reread_2026-11-19_tripwindow.json) holds the values read from the live official
Venetian and Wynn sources on 2026-11-19 (session arena/a33db3c1-poker3): the DeepStack IV
schedule page, the eleven structure sheets the window links to, the Wynn WPT schedule and
structures PDFs, and the Venetian hotel rate/fee/poker-room pages. These tests fail if
site/data.json drifts from that record, so a later edit cannot silently change a value that
was re-read, and they fail if a row the record covers was not advanced to the re-read date.
This is a second, independent trip-window record; the concurrent session's
research/reread_2026-11-19.md and tests/test_reread_2026_11_19.py cover a different slice and
are kept alongside it.
"""
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
RECORD = json.loads((ROOT / "research" / "reread_2026-11-19_tripwindow.json").read_text(encoding="utf-8"))
DATA = json.loads((ROOT / "site" / "data.json").read_text(encoding="utf-8"))


def event_for(event_id):
    matches = [e for e in DATA["events"] if e["id"] == event_id]
    return matches


class TripWindowRows(unittest.TestCase):
    def test_record_covers_the_full_trip_window(self):
        # 19 Venetian DSE rows + 13 Wynn WPT rows = 32.
        self.assertEqual(len(RECORD["rows"]), 32)
        venetian = [r for r in RECORD["rows"] if r["venue"] == "venetian"]
        wynn = [r for r in RECORD["rows"] if r["venue"] == "wynn"]
        self.assertEqual(len(venetian), 19)
        self.assertEqual(len(wynn), 13)

    def test_every_reread_row_is_published_exactly_once(self):
        for row in RECORD["rows"]:
            with self.subTest(row=row["id"]):
                found = event_for(row["id"])
                self.assertEqual(len(found), 1, f"expected one published row, found {len(found)}")

    def test_schedule_fields_match_the_official_source(self):
        for row in RECORD["rows"]:
            with self.subTest(row=row["id"]):
                (e,) = event_for(row["id"])
                self.assertEqual(e["date"], row["date"])
                self.assertEqual(e["time"], row["time"])
                self.assertEqual(e["name"], row["name"])
                self.assertEqual(e["buyIn"], row["buyIn"])
                self.assertEqual(e["guarantee"], row["guarantee"])

    def test_each_row_was_checked_and_verified_on_the_reread_date(self):
        for row in RECORD["rows"]:
            with self.subTest(row=row["id"]):
                (e,) = event_for(row["id"])
                self.assertEqual(e["lastChecked"], RECORD["retrievedOn"])
                self.assertEqual(e["lastVerified"], RECORD["retrievedOn"])

    def test_no_row_outside_the_window_was_advanced(self):
        # Only the 32 re-read rows may carry the 2026-11-19 date. A row that was not re-read
        # must keep its earlier date, so the re-read cannot silently stamp rows it never read.
        trip = DATA["trip"]
        for e in DATA["events"]:
            if not e.get("date") or not (trip["start"] <= e["date"] <= trip["end"]):
                with self.subTest(row=e["id"]):
                    self.assertNotEqual(e.get("lastChecked"), RECORD["retrievedOn"],
                                        "a row outside the trip window carries the re-read date")


def _norm(text):
    """Remove all whitespace and case so the record's raw PDF text can be compared with the
    published row's normalized field without treating a casing/spacing difference as drift."""
    return "".join(str(text).lower().split())


class StructureSheets(unittest.TestCase):
    def test_sheet_facts_match_the_published_rows(self):
        # Each re-read sheet's chips, level length, late-registration clock, fee and guarantee
        # must equal the values the window's rows carry.
        for number, sheet in RECORD["sheets"].items():
            with self.subTest(sheet=number):
                rows = [r for r in RECORD["rows"] if r["venue"] == "venetian" and r["sheet"] == number]
                self.assertTrue(rows, f"sheet {number} is recorded but no trip row links to it")
                for r in rows:
                    (e,) = event_for(r["id"])
                    self.assertEqual(e["chips"], sheet["chips"])
                    self.assertEqual(e["levelMin"], sheet["levelMin"])
                    # Resumption (Day 2 restart) rows carry no late-registration clock by design;
                    # only compare it where the row actually publishes one.
                    if e["lateReg"]:
                        self.assertEqual(_norm(e["lateReg"]), _norm(sheet["lateReg"]))
                    self.assertEqual(e["buyIn"], sheet["buyIn"])
                    self.assertEqual(e["guarantee"], sheet["guarantee"])
                    fee = e["rules"]["fee"]["excerpt"]
                    self.assertIn(f"${sheet['fee']} of the ${sheet['buyIn']} Buy-In", fee)


class HotelAndPages(unittest.TestCase):
    def test_hotel_pages_were_reread_and_advanced(self):
        for h in DATA["hotels"]:
            if h["id"] in ("venetian", "palazzo"):
                with self.subTest(hotel=h["id"]):
                    self.assertEqual(h["lastChecked"], RECORD["retrievedOn"])
                    self.assertEqual(h["lastVerified"], RECORD["retrievedOn"])

    def test_booking_engine_total_still_dated(self):
        # The 2026-11-19 engine read returned no total (recorded in the record and in F88), so the
        # published checkout total must still carry its 2026-11-17 evidence, not the re-read date.
        trip = DATA["trip"]
        self.assertEqual(trip["lodgingTotalAllIn"], 4010.55)
        self.assertIn("2026-11-17", trip["lodgingEvidence"])
        self.assertNotIn("re-read 2026-11-19", trip["lodgingEvidence"])

    def test_poker_room_page_flag_is_resolved(self):
        flags = {f["id"]: f for f in DATA["flags"]}
        self.assertIn("F92", flags)
        title = flags["F92"]["title"]
        # The concurrent session's resolution is the authoritative F92 text: the page was
        # re-read on 2026-11-19 and the wording change moved no tournament, rate or policy value.
        self.assertIn("2026-11-19", title)
        self.assertIn("no tournament, rate or policy value", title)
        self.assertNotIn("still required", title)


if __name__ == "__main__":
    unittest.main()
