"""The landing page must not present an automated hash re-check as a value verification.

Irregularity found on 2026-11-19. site/index.html printed "2026-11-19" beside each of the
seven candidate rows under a column headed "Source / last checked", while the row data in
site/data.json records lastChecked and lastVerified as 2026-11-17. The 2026-11-19 date is
real, but it is a different claim: scripts/check_sources.py re-fetched the seven structure
PDFs on 2026-11-19 and found no change (site/checks.json, generatedAt 2026-11-19T05:33:18Z).
A hash match proves the document did not change; it does not re-verify a number by eye.

These tests pin the distinction so it cannot silently collapse again. They assert no new
tournament value.

Second irregularity, found 2026-11-19 (session arena/7d96049f). The guard written to catch that drift
asserted the literal date (`generatedAt.startswith("2026-11-19")`) and that no structure PDF had changed
(`assertIs(record["changed"], False)`). `scripts/check_sources.py` rewrites `site/checks.json` inside the
same scheduled job that runs these tests, so both assertions were time bombs: the first failed from the
next day onwards, and the second failed whenever a venue re-published a sheet. Both sat in the job's
verification gate, which sits before the step that commits the record, so a detected source change
suppressed the publication of the record of that change (CI run 44482186623). The assertions below are
relational instead, and the page now renders the date out of the record rather than from typed HTML.
"""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"


def iso_day(value):
    """Return the YYYY-MM-DD part of an ISO timestamp, or '' when it is not one.

    Deliberately not a fixed date: these tests must keep passing the day the scheduled monitor
    rewrites site/checks.json, because that rewrite is the job working, not the job failing.
    """
    m = re.match(r"^(\d{4}-\d{2}-\d{2})T\d{2}:\d{2}:\d{2}", str(value or ""))
    return m.group(1) if m else ""


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
        """The record must cover each trip-window sheet, and stay self-consistent.

        This test was written on 2026-11-19 as `checks["generatedAt"].startswith("2026-11-19")` plus
        `assertIs(record["changed"], False)` for each of the seven sheets. Both were time bombs, and the
        second was the worse one: `scripts/check_sources.py` re-runs every morning and rewrites
        `site/checks.json` in the same job that runs these tests, so (a) from 2026-11-20 the literal date
        could never match again, and (b) any venue that re-published a structure PDF — even for a
        metadata-only reason — failed the gate. That gate sits before the job's "record the check results"
        step, so the change monitor stopped publishing its own record precisely when a source changed
        (CI run 44482186623, 2026-11-19: the URL re-check and transcription steps passed, the gate failed,
        the record commit was skipped).

        A change on a booking-engine URL is the expected case, not a failure: `reservations.wynnlasvegas.com`
        re-renders its visible text on every request, so both of its rows were marked changed on 2026-11-19 at
        07:56 UTC while no published value moved. `wordingChanged` is the field that separates that noise from
        a venue re-publishing a document, and it is asserted on the Flagged-for-review and Sources pages rather
        than demanded to be false here.

        What the test can honestly require, on any day, is invariance: the record must exist, it must cover
        the seven sheets, its own timestamps must be internally consistent, and a row that reports a change
        must say what it compared. "The venue changed nothing" is not a requirement the site can impose on
        the venues, and a detected change is the job's expected output, not its failure.
        """
        checks = json.loads((SITE / "checks.json").read_text())
        generated = iso_day(checks["generatedAt"])
        self.assertTrue(generated, f"generatedAt {checks['generatedAt']!r} is not an ISO timestamp")
        by_url = {u["url"]: u for u in checks["urls"]}
        for sheet in SHEETS:
            matches = [u for url, u in by_url.items() if url.endswith(sheet)]
            with self.subTest(sheet=sheet):
                self.assertTrue(matches, f"{sheet} is not in the automated re-check record")
                record = matches[0]
                checked = iso_day(record["checked"])
                self.assertTrue(checked, f"{sheet}: checked {record['checked']!r} is not an ISO timestamp")
                # The row must record an actual fetch outcome, not a placeholder date (the check
                # session arena/c336248a landed alongside this one: the point is that the sheet was
                # really retrieved, not that it looked clean).
                self.assertTrue(str(record["status"]).startswith("HTTP 2"), record["status"])
                # The fetch cannot postdate the record that publishes it. This direction is the only
                # safe one: a run that starts before midnight UTC and finishes after it would make
                # "checked >= generatedAt" false for a perfectly ordinary fetch.
                self.assertLessEqual(checked, generated,
                                     f"{sheet}: checked {checked} is dated after the run that wrote it ({generated})")
                self.assertIsInstance(record["changed"], bool, f"{sheet}: changed must be a recorded boolean")
                if record["changed"]:
                    # A change without its comparison basis is not reviewable by a human.
                    self.assertTrue(record.get("hashBasis") or record.get("previousHash"),
                                    f"{sheet}: a reported change must state what was compared")
                    self.assertTrue(record.get("previousHash"),
                                    f"{sheet}: a reported change must keep the hash it compared against")

    def test_the_page_never_hardcodes_a_recheck_date(self):
        """The column's date must come from the record, so it cannot go stale or get ahead of it."""
        import re as _re
        block = self.page[self.page.index("data-reviewed-candidates"):]
        cells = _re.findall(r"<small data-sheet-recheck=\"([^\"]+)\">([^<]*)</small>", block)
        self.assertEqual(len(SHEETS), len(cells), "one re-check cell per trip-window sheet")
        for name, fallback in cells:
            with self.subTest(sheet=name):
                self.assertIn(name, [s.split("/")[-1] for s in SHEETS], "cell names a sheet outside the trip window")
                self.assertNotRegex(fallback, r"20\d\d-\d\d-\d\d",
                                    "a hardcoded date in the static page is the drift this guard exists to stop")

    def test_the_app_reads_the_date_from_the_record(self):
        """app.js must derive the cell from site/checks.json and label a change as a change."""
        js = (SITE / "assets" / "app.js").read_text(encoding="utf-8")
        self.assertIn("function renderSheetRechecks", js)
        self.assertIn("data-sheet-recheck", js)
        body = js[js.index("function renderSheetRechecks"):js.index("function renderHome")]
        self.assertIn("checks.urls", body, "the cell must read the record, not the page")
        self.assertIn("CHANGED", body, "a changed source must be labelled in the cell")
        self.assertIn("does not re-verify any printed value", body,
                      "the cell must say what a hash re-check does not prove")
        # It must be wired into the landing-page render, or it never runs.
        home = js[js.index("function renderHome"):]
        self.assertIn("renderSheetRechecks();", home[:400])

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
