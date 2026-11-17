#!/usr/bin/env python3
"""The sources page reads site/checks.json directly, so its shape is a contract.

`scripts/check_sources.py` publishes the URL record and `scripts/verify_transcription.py`
adds the row-by-row record to the same file. If either stops writing the keys that
`site/assets/app.js` reads, the sources page silently degrades to "no automated check
file yet" even though the record exists. These tests pin that contract, and they also
check that the committed file already satisfies it.
"""
from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKS = ROOT / "site" / "checks.json"
APP_JS = ROOT / "site" / "assets" / "app.js"


class ChecksSchema(unittest.TestCase):
    def test_record_has_the_keys_the_sources_page_reads(self):
        doc = json.loads(CHECKS.read_text(encoding="utf-8"))
        for key in ("generatedAt", "mode", "summary", "urls", "transcription"):
            self.assertIn(key, doc, f"site/checks.json has no '{key}' key")
        summary = doc["summary"]
        for key in ("urls", "fetched", "changed", "failed"):
            self.assertIn(key, summary, f"summary has no '{key}' count")
        self.assertIsInstance(doc["urls"], list)
        self.assertTrue(doc["urls"], "the URL record is empty")

    def test_every_url_row_can_be_rendered(self):
        doc = json.loads(CHECKS.read_text(encoding="utf-8"))
        for row in doc["urls"]:
            self.assertTrue(row.get("url", "").startswith("https://"), row)
            self.assertIn("status", row, row)
            self.assertIn("checked", row, row)

    def test_transcription_record_covers_the_official_rows(self):
        doc = json.loads(CHECKS.read_text(encoding="utf-8"))
        trans = doc["transcription"]
        self.assertEqual(trans["status"], "checked", trans.get("mismatches"))
        self.assertEqual(trans["rowsMatched"], trans["rowsTranscribed"])
        self.assertGreaterEqual(trans["rowsTranscribed"], 40)

    def test_the_page_still_reads_those_keys(self):
        js = APP_JS.read_text(encoding="utf-8")
        for needle in ("checks.summary", "checks.urls", "checks.transcription",
                       "checks.generatedAt", "checks.mode"):
            self.assertIn(needle, js, f"app.js no longer reads {needle}")

    def test_check_sources_publishes_the_page_shape(self):
        src = (ROOT / "scripts" / "check_sources.py").read_text(encoding="utf-8")
        for needle in ('"generatedAt"', '"mode"', '"summary"', '"fetched"', '"failed"'):
            self.assertIn(needle, src, f"check_sources.py no longer writes {needle}")
        # It must keep a prior transcription record rather than dropping it.
        self.assertIn('previous_payload.get("transcription")', src)

    def test_workflow_runs_both_recorders_in_order(self):
        raw = (ROOT / ".github" / "workflows" / "checks.yml").read_text(encoding="utf-8")
        # Ignore the explanatory comment block: only executed steps matter here.
        flow = "\n".join(line for line in raw.splitlines() if not line.lstrip().startswith("#"))
        first = flow.index("scripts/check_sources.py")
        second = flow.index("scripts/verify_transcription.py")
        verify = flow.index("scripts/verify_site.py")
        self.assertLess(first, second, "the URL record must be written before the transcription record")
        self.assertLess(second, verify, "both records must exist before the dashboard verifier runs")
        # The old defect: parsing checks.json before it is created.
        before_first = flow[:first]
        self.assertNotIn("json.tool site/checks.json", before_first)


if __name__ == "__main__":
    unittest.main(verbosity=2)
