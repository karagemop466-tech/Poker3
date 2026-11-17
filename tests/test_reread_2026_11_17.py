"""Checks the 13 trip-window rows and 7 structure sheets against the 2026-11-17 live re-read.

The record (research/reread_2026-11-17.json) holds the values transcribed from the official
Venetian pages.  These tests fail if site/data.json drifts from that record, so a later edit
cannot silently change a value that was re-read.
"""
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
RECORD = json.loads((ROOT / "research" / "reread_2026-11-17.json").read_text(encoding="utf-8"))
DATA = json.loads((ROOT / "site" / "data.json").read_text(encoding="utf-8"))


def event_for(row):
    """The published row whose id is vl-dse-<date>-<event number>-<time>."""
    prefix = f"vl-dse-{row['date']}-{row['event']}-"
    matches = [e for e in DATA["events"] if e["id"].startswith(prefix)]
    return matches


class TripWindowRows(unittest.TestCase):
    def test_every_trip_window_row_is_published_exactly_once(self):
        for row in RECORD["rows"]:
            with self.subTest(row=row["date"] + " #" + row["event"]):
                found = event_for(row)
                self.assertEqual(len(found), 1, f"expected one published row, found {len(found)}")

    def test_schedule_fields_match_the_official_schedule(self):
        for row in RECORD["rows"]:
            with self.subTest(row=row["date"] + " #" + row["event"]):
                (e,) = event_for(row)
                self.assertEqual(e["date"], row["date"])
                self.assertEqual(e["time"], row["time"])
                self.assertEqual(e["buyIn"], row["buyIn"])
                self.assertEqual(e["guarantee"], row["guarantee"])

    def test_sheet_fields_match_the_structure_sheet(self):
        for row in RECORD["rows"]:
            with self.subTest(row=row["date"] + " #" + row["event"]):
                (e,) = event_for(row)
                sheet = RECORD["sheets"][row["sheet"]]
                self.assertIn(row["event"], sheet["eventNumbers"])
                self.assertEqual(e["sheetUrl"], sheet["url"])
                self.assertEqual(e["chips"], sheet["startingChips"])
                self.assertEqual(e["lateRegEnd"], sheet["lateRegistrationClock"])
                self.assertEqual(e["rules"]["fee"]["excerpt"], sheet["feeLine"])

    def test_each_row_was_checked_on_the_reread_date(self):
        for row in RECORD["rows"]:
            with self.subTest(row=row["date"] + " #" + row["event"]):
                (e,) = event_for(row)
                self.assertEqual(e["lastChecked"], RECORD["retrievedOn"])

    def test_no_reread_sheet_prints_re_entry_rebuy_or_add_on_wording(self):
        # The record is the reading. A sheet that prints re-entry, rebuy or add-on text must be
        # recorded here and the row reclassified; none does, so every clause must say so.
        for number, sheet in RECORD["sheets"].items():
            with self.subTest(sheet=number):
                self.assertIn("No re-entry, rebuy or add-on clause printed.", sheet["clauses"])

    def test_structure_sheets_carry_the_reread_date(self):
        published = {s["sheet"]: s for s in DATA["structureSheets"] if s["venue"] == "venetian"}
        for number in RECORD["sheets"]:
            with self.subTest(sheet=number):
                self.assertEqual(published[int(number)].get("reReadOn"), RECORD["retrievedOn"])


class WptTripWindowRows(unittest.TestCase):
    """Six Wynn WPT rows matched to a printed section of the structure PDF (read 2026-11-17)."""

    def _event(self, event_id):
        matches = [e for e in DATA["events"] if e["id"] == event_id]
        self.assertEqual(len(matches), 1, f"{event_id} must be published exactly once")
        return matches[0]

    def test_matched_rows_carry_the_printed_re_entry_clause(self):
        for row in RECORD["wpt"]["rows"]:
            with self.subTest(row=row["id"]):
                e = self._event(row["id"])
                self.assertEqual(e["rules"]["reEntry"]["status"], "re-entry-printed")
                self.assertEqual(e["rules"]["reEntry"]["excerpt"], row["excerpt"])
                self.assertEqual(e["rules"]["reEntry"]["source"], RECORD["wpt"]["sheetUrl"])
                self.assertEqual(e["rules"]["reEntry"]["retrieved"], RECORD["wpt"]["retrievedOn"])

    def test_matched_rows_are_not_single_entry(self):
        for row in RECORD["wpt"]["rows"]:
            with self.subTest(row=row["id"]):
                e = self._event(row["id"])
                self.assertFalse(e["singleEntry"])
                self.assertEqual(e["rules"]["singleEntry"]["status"], "multiple-entries")

    def test_schedule_row_with_conflicting_date_stays_unverified(self):
        e = self._event("wynn-wpt-2026-11-30-011-100pm")
        self.assertEqual(e["rules"]["reEntry"]["status"], "not-verified")
        self.assertFalse(e["singleEntry"])


if __name__ == "__main__":
    unittest.main()
