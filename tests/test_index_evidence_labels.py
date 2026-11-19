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
        self.assertIn("lastChecked 2026-11-17", self.page)
        # The distinction must be stated, not implied.
        self.assertIn("not re-verify a number by eye", self.page)

    def test_recheck_record_actually_supports_the_date(self):
        checks = json.loads((SITE / "checks.json").read_text())
        self.assertTrue(checks["generatedAt"].startswith("2026-11-19"))
        by_url = {u["url"]: u for u in checks["urls"]}
        for sheet in SHEETS:
            matches = [u for url, u in by_url.items() if url.endswith(sheet)]
            with self.subTest(sheet=sheet):
                self.assertTrue(matches, f"{sheet} is not in the automated re-check record")
                record = matches[0]
                self.assertTrue(record["checked"].startswith("2026-11-19"))
                self.assertIs(record["changed"], False)

    def test_row_data_still_carries_its_own_read_and_verify_dates(self):
        events = {e["id"]: e for e in self.data["events"]}
        for day in self.data["dayPlan"]:
            if not day["primary"]:
                continue
            event = events[day["primary"]]
            with self.subTest(event=event["id"]):
                # The row must carry its own read/verify dates from the 2026-11-17 pass or a
                # later one. The 2026-11-19 trip-window re-read (session arena/a33db3c1-poker3)
                # legitimately advanced these primary rows past 2026-11-17, so the dates must not
                # fall back before the pass that read them, not stay pinned to it.
                self.assertGreaterEqual(event["lastChecked"], "2026-11-17")
                self.assertGreaterEqual(event["lastVerified"], "2026-11-17")


if __name__ == "__main__":
    unittest.main()
