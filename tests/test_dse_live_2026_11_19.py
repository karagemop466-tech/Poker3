#!/usr/bin/env python3
"""Regression test for the 2026-11-19 live re-read of the Venetian DSE IV schedule.

The official page is the only source for the date, start time and structure sheet of a
DeepStack Extravaganza IV event. `raw/venetian_dse_nov_2026_live_2026-11-19.md` is the
dated transcription of that page. This test fails if the published catalog stops
matching it, so a rename or a re-timed row cannot slip in without the evidence moving
with it.
"""
from __future__ import annotations

import json
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import verify_dse_live_2026_11_19 as v  # noqa: E402


class LiveCaptureMatchesCatalog(unittest.TestCase):
    def test_capture_has_the_full_series(self):
        rows = v.read_capture()
        self.assertEqual(94, len(rows), "the official page printed 94 rows on 2026-11-19")
        self.assertEqual("2026-11-16", rows[0]["date"])
        self.assertEqual("2026-12-23", rows[-1]["date"])

    def test_every_published_row_matches_the_capture(self):
        self.assertEqual(0, v.main(), "published Venetian rows must match the 2026-11-19 capture")

    def test_names_are_the_pages_own_words(self):
        """No paraphrasing: each published name appears verbatim in the capture."""
        cap = {v.norm(r["name"]) for r in v.read_capture()}
        data = json.loads((ROOT / "site" / "data.json").read_text(encoding="utf-8"))
        rows = [e for e in data["events"]
                if e["venue"] == "venetian" and "dse-nov-2026" in (e.get("scheduleUrl") or "")]
        self.assertEqual(94, len(rows))
        for e in rows:
            self.assertIn(v.norm(e["name"]), cap, f"{e['id']} name is not the page's wording")


SECOND_CAPTURE = ROOT / "raw" / "dse_schedule_live_2026-11-19_ade0718f.md"


class SecondIndependentCapture(unittest.TestCase):
    """A second read of the same page on the same day must agree, field for field.

    Two independent captures make agreement evidence rather than an assumption, and either one
    failing against the catalog is a finding. See flag F97 for why the rows' read dates are
    asserted here as well.
    """

    def test_second_capture_has_the_full_series(self):
        rows = v.read_capture(SECOND_CAPTURE)
        self.assertEqual(94, len(rows), "the second capture must transcribe all 94 printed rows")

    def test_catalog_matches_the_second_capture(self):
        self.assertEqual(0, v.main(SECOND_CAPTURE))

    def test_the_two_captures_agree_with_each_other(self):
        first = [(r["date"], r["time"], r["number"], r["sheet"]) for r in v.read_capture()]
        second = [(r["date"], r["time"], r["number"], r["sheet"]) for r in v.read_capture(SECOND_CAPTURE)]
        self.assertEqual(first, second)

    def test_every_dse_iv_row_carries_the_2026_11_19_read(self):
        data = json.loads((ROOT / "site" / "data.json").read_text(encoding="utf-8"))
        rows = [e for e in data["events"]
                if e["venue"] == "venetian" and "dse-nov-2026" in (e.get("scheduleUrl") or "")]
        self.assertEqual(94, len(rows))
        for e in rows:
            with self.subTest(event=e["id"]):
                self.assertEqual("2026-11-19", e["lastChecked"], "flag F97: a later read must not be dragged back")
                self.assertEqual("2026-11-19", e["lastVerified"])


if __name__ == "__main__":
    unittest.main()
