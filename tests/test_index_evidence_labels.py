"""The landing page must not present an automated hash re-check as a value verification.

Irregularity found on 2026-11-19. site/index.html printed "2026-11-19" beside each of the
seven candidate rows under a column headed "Source / last checked", while the row data in
site/data.json records lastChecked and lastVerified as 2026-11-17. The 2026-11-19 date is
real, but it is a different claim: scripts/check_sources.py re-fetched the seven structure
PDFs on 2026-11-19 and found no change (site/checks.json, generatedAt 2026-11-19T05:33:18Z).
A hash match proves the document did not change; it does not re-verify a number by eye.

These tests pin the distinction so it cannot silently collapse again. They assert no new
tournament value.
"""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"

# The seven primary candidate sheets, in trip order.
SHEETS = [
    "dse_nov_2026-structure_30.pdf",
    "dse_nov_2026-structure_1.pdf",
    "dse_nov_2026-structure_6.pdf",
    "dse_nov_2026-structure_5.pdf",
    "dse_nov_2026-structure_7.pdf",
    "dse_nov_2026-structure_11.pdf",
    "dse_nov_2026-structure_22.pdf",
]


class LandingEvidenceLabels(unittest.TestCase):
    def setUp(self):
        self.page = (SITE / "index.html").read_text()
        self.data = json.loads((SITE / "data.json").read_text())

    def test_column_does_not_claim_a_value_read(self):
        self.assertIn("Source / sheet re-checked", self.page)
        self.assertNotIn("Source / last checked", self.page)

    def test_page_explains_the_date_is_an_automated_recheck(self):
        self.assertIn("What the date in the last column means", self.page)
        self.assertIn("last automated re-check", self.page)
        # The distinction must be stated, not implied.
        self.assertIn("not re-verify a number by eye", self.page)

    def test_page_states_the_dates_the_rows_actually_carry(self):
        """Whatever the page says the rows' read dates are, the data must agree.

        The page used to print a fixed `lastChecked 2026-11-17` line; when the 2026-11-19
        full-page re-read moved 94 rows forward (flag F97) that line became a stale claim about
        the data it sits above. This test ties the sentence to the data so it cannot drift again.
        """
        events = {e["id"]: e for e in self.data["events"]}
        dates = {events[day["primary"]]["lastChecked"] for day in self.data["dayPlan"]
                 if day["primary"] in events}
        for date in dates:
            with self.subTest(date=date):
                self.assertIn(f"lastChecked {date}", self.page)

    def test_recheck_record_actually_supports_the_date(self):
        """The landing page date must be backed by a fetched row, not by a clean row.

        This test used to require `record["changed"] is False` for all seven primary
        sheets. That made a genuine source change fail the build: on 2026-11-19 the
        scheduled re-check (07:56 UTC) recorded a visible-text change on the Wynn
        booking engine and the run went red in the workflow's verification step. A
        changed source is exactly what the monitor exists to surface, so it must not
        be an error. What must hold is that the date printed on the landing page is
        the date the sheet was actually fetched; whether the bytes moved is reported
        on the Sources page and the Flagged for review page instead.
        """
        checks = json.loads((SITE / "checks.json").read_text())
        self.assertTrue(checks["generatedAt"])
        by_url = {u["url"]: u for u in checks["urls"]}
        for sheet in SHEETS:
            matches = [u for url, u in by_url.items() if url.endswith(sheet)]
            with self.subTest(sheet=sheet):
                self.assertTrue(matches, f"{sheet} is not in the automated re-check record")
                record = matches[0]
                # The row must carry a real fetch timestamp and a real HTTP outcome.
                self.assertRegex(record["checked"], r"^\d{4}-\d{2}-\d{2}T")
                self.assertTrue(str(record["status"]).startswith("HTTP 2"), record["status"])
                # It must have been fetched on the day the page claims, or later.
                self.assertGreaterEqual(record["checked"][:10], checks["generatedAt"][:10])

    def test_row_data_still_carries_its_own_read_and_verify_dates(self):
        # Each row states the date ITS OWN value was read and the date that document was last
        # confirmed still true. Both are floors: a later documented read may sit on top of the
        # 2026-11-17 re-read pass, and the sheet behind the money values is what pins
        # lastVerified. The dates are never borrowed from the automated hash check.
        events = {e["id"]: e for e in self.data["events"]}
        for day in self.data["dayPlan"]:
            if not day["primary"]:
                continue
            event = events[day["primary"]]
            with self.subTest(event=event["id"]):
                self.assertGreaterEqual(event["lastChecked"], "2026-11-17")
                self.assertGreaterEqual(event["lastVerified"], "2026-11-17")
                self.assertLessEqual(event["lastVerified"], self.data["today"])
                # lastVerified must belong to the structure sheet this row's rules quote, and
                # the excerpt date must agree with it. A row cannot claim a re-verification on a
                # day its own sheet was not read.
                self.assertTrue(event["sheetUrl"], event["id"])
                if event["rules"]["fee"].get("retrieved") == "2026-11-19":
                    self.assertEqual(event["lastVerified"], "2026-11-19", event["id"])


if __name__ == "__main__":
    unittest.main()
