#!/usr/bin/env python3
"""Regression test for the 2026-11-19 live re-read of the Venetian DeepStack NYE schedule.

That official page is the only source for the date, start time, event number and structure sheet of
each of the 49 New Year's Eve rows. `raw/venetian_dse_nye_live_2026-11-19_7d96049f.md` is the dated
transcription of it. This test fails if the published catalog stops matching that capture, so a
rename, a re-timed row, a moved start date or a swapped structure sheet cannot slip in without the
evidence moving with it.

It also pins the limit of what the re-read proves: the schedule page was re-read on 2026-11-19, the
15 structure sheets were not, so `lastChecked` moved and `lastVerified` must not have.
"""
from __future__ import annotations

import json
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import verify_nye_live_2026_11_19 as v  # noqa: E402

DATA = json.loads((ROOT / "site" / "data.json").read_text(encoding="utf-8"))
NYE_ROWS = [e for e in DATA["events"] if e.get("scheduleUrl") == v.PAGE_URL]


class NYECaptureMatchesCatalog(unittest.TestCase):
    def test_capture_has_the_full_series(self):
        rows = v.read_capture()
        self.assertEqual(49, len(rows), "the official page printed 49 rows on 2026-11-19")
        self.assertEqual("2026-12-24", rows[0]["date"])
        self.assertEqual("2027-01-10", rows[-1]["date"])

    def test_catalog_holds_every_row_the_page_prints(self):
        self.assertEqual(49, len(NYE_ROWS), "the catalog must carry all 49 printed rows, no more and no fewer")

    def test_every_published_row_matches_the_capture(self):
        self.assertEqual(0, v.main(), "published DeepStack NYE rows must match the 2026-11-19 capture")

    def test_names_are_the_pages_own_words(self):
        """No paraphrasing: each published name is the page's wording, folded for style only."""
        cap = {v.norm(r["name"]) for r in v.read_capture()}
        for e in NYE_ROWS:
            with self.subTest(event=e["id"]):
                self.assertIn(v.norm(e["name"]), cap, "name is not the page's wording")

    def test_printed_year_defect_is_recorded_not_silently_corrected(self):
        """The three December 26 rows print 2025 on the page; the catalog keeps 2026 and flags it (F04/F41)."""
        rows = [r for r in v.read_capture() if r["date"] == "2026-12-26"]
        self.assertEqual(3, len(rows))
        raw = (ROOT / "raw" / "venetian_dse_nye_schedule_live_2026-11-19_7d96049f.md").read_text(encoding="utf-8")
        self.assertIn("Saturday, December 26, 2025", raw,
                      "the verbatim capture must keep the printed year so the flag has its evidence")
        self.assertIn("Tuesaday", raw, "the verbatim capture must keep the printed misspelling")
        ids = {f["id"] for f in DATA["flags"]}
        self.assertIn("F04", ids)
        self.assertIn("F41", ids)

    def test_read_date_moved_and_verification_date_did_not(self):
        """The page was re-read today; the sheets behind these rows were not. The dates must say so."""
        self.assertEqual(49, len(NYE_ROWS))
        for e in NYE_ROWS:
            with self.subTest(event=e["id"]):
                self.assertEqual("2026-11-19", e["lastChecked"],
                                 "a row re-read from the live page on 2026-11-19 must say so")
                self.assertEqual("2026-11-17", e["lastVerified"],
                                 "lastVerified belongs to the structure-sheet read; the NYE sheets were "
                                 "not re-read on 2026-11-19, so it must not be dragged forward")
                self.assertEqual("2026-11-19", e["recheck"]["date"])
                self.assertEqual(v.PAGE_URL, e["recheck"]["source"])

    def test_no_published_value_is_older_than_its_own_page_read(self):
        """A row cannot report a verification newer than the day its source was last read."""
        for e in NYE_ROWS:
            with self.subTest(event=e["id"]):
                self.assertLessEqual(e["lastVerified"], e["lastChecked"])
                self.assertLessEqual(e["lastChecked"], DATA["today"])


if __name__ == "__main__":
    unittest.main()
