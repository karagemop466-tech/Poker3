"""A robot block is an observation about the runner, not a dead link.

The scheduled checker runs on a GitHub-hosted datacenter IP. Several Strip venues answer a
datacenter client with HTTP 403, a bot redirect or a timeout while serving a normal browser.
Before this test the published record called all of them "failed", which reads on the Sources
page as though seventeen official sources were broken. They were not: every one was re-read by
hand on 2026-11-17 and every published value behind them was corroborated.
"""
import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_sources  # noqa: E402

CHECKS = json.loads((ROOT / "site" / "checks.json").read_text(encoding="utf-8"))
APP = (ROOT / "site" / "assets" / "app.js").read_text(encoding="utf-8")


class OutcomeClassificationTests(unittest.TestCase):
    def test_success_and_failure_kinds_are_named_separately(self):
        self.assertEqual(check_sources.classify_outcome("HTTP 200"), "fetched")
        for blocked in ("HTTP 403", "HTTP 401", "HTTP 429"):
            self.assertEqual(check_sources.classify_outcome(blocked), "blocked", blocked)
        self.assertEqual(check_sources.classify_outcome("HTTP 302"), "redirected")
        self.assertEqual(check_sources.classify_outcome("unreachable"), "unreachable")
        self.assertEqual(check_sources.classify_outcome("HTTP 500"), "error")

    def test_a_successful_fetch_is_never_counted_as_blocked_or_unavailable(self):
        for status in ("HTTP 200", "HTTP 204"):
            self.assertEqual(check_sources.classify_outcome(status), "fetched")


class PublishedRecordTests(unittest.TestCase):
    def test_every_url_carries_an_outcome(self):
        missing = [u["url"] for u in CHECKS["urls"] if "outcome" not in u]
        self.assertEqual(missing, [], "every checked URL must name what happened to it")

    def test_summary_separates_blocked_from_unavailable(self):
        s = CHECKS["summary"]
        blocked = sum(1 for u in CHECKS["urls"] if u.get("outcome") in ("blocked", "redirected"))
        unavailable = sum(1 for u in CHECKS["urls"] if u.get("outcome") in ("unreachable", "error"))
        self.assertEqual(s.get("blocked"), blocked)
        self.assertEqual(s.get("unavailable"), unavailable)
        # legacy alias kept so an older reader does not silently change meaning
        self.assertEqual(s.get("failed"), unavailable)

    def test_counts_reconcile_to_the_url_total(self):
        s = CHECKS["summary"]
        self.assertEqual(s["urls"], len(CHECKS["urls"]))
        self.assertEqual(s["fetched"] + s["blocked"] + s["unavailable"], s["urls"])

    def test_a_bot_block_is_not_labelled_unavailable_on_the_page(self):
        self.assertIn("Blocked for the robot, not missing", APP)
        # the blocked badge must be tested BEFORE the unavailable badge
        self.assertLess(
            APP.index("Blocked for the robot, not missing"),
            APP.index("Unavailable · not verified"),
        )

    def test_note_explains_that_a_block_is_not_a_dead_link(self):
        note = CHECKS["note"]
        self.assertIn("does not mean the page is gone", note)
        self.assertIn("bot", note.lower())


if __name__ == "__main__":
    unittest.main()
