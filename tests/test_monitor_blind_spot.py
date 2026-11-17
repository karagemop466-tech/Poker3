"""The change monitor must be honest about what it cannot see.

Found on 2026-11-17: the five Venetian booking-engine URLs differ only in the dates
in the query string, and the server returns the same rendered shell for all of them,
so the scheduled re-check reports "unchanged" on the page that carries the hotel
budget whether the price moved or not. On that day the identical official query
printed $4,010.55 at 21:54 UTC and $3,823.46 at about 22:07 UTC (flag F78) while the
monitor reported no change (flag F77).

`mark_query_blind` now detects that situation from the stored response hashes and
marks the affected URLs, so the sources page says "change not detectable here"
instead of showing a green "unchanged".

These tests pin the detection and the published record.
"""
import json
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_sources as cs  # noqa: E402

CHECKS = ROOT / "site" / "checks.json"


class QueryBlindDetection(unittest.TestCase):
    def test_urls_that_differ_only_in_the_query_but_return_the_same_text_are_marked(self):
        rows = [
            {"url": "https://example.com/book?a=1&b=2", "textHash": "same"},
            {"url": "https://example.com/book?a=1&b=3", "textHash": "same"},
            {"url": "https://example.com/book?a=1&b=4", "textHash": "same"},
        ]
        marked = cs.mark_query_blind(rows)
        self.assertEqual(len(marked), 3)
        for row in rows:
            self.assertTrue(row.get("queryBlind"))
            self.assertIn("F77", row["queryBlindReason"])

    def test_urls_with_different_visible_text_are_not_marked(self):
        rows = [
            {"url": "https://example.com/book?a=1", "textHash": "one"},
            {"url": "https://example.com/book?a=2", "textHash": "two"},
        ]
        self.assertEqual(cs.mark_query_blind(rows), [])
        self.assertFalse(rows[0].get("queryBlind"))

    def test_a_single_url_on_a_path_is_never_marked(self):
        rows = [{"url": "https://example.com/book?a=1", "textHash": "one"}]
        self.assertEqual(cs.mark_query_blind(rows), [])

    def test_different_paths_are_never_grouped_together(self):
        rows = [
            {"url": "https://example.com/book?a=1", "textHash": "same"},
            {"url": "https://example.com/suite?a=1", "textHash": "same"},
        ]
        self.assertEqual(cs.mark_query_blind(rows), [])


class PublishedMonitorRecord(unittest.TestCase):
    def setUp(self):
        self.checks = json.loads(CHECKS.read_text(encoding="utf-8"))

    def test_the_booking_urls_are_published_as_not_change_checkable(self):
        blind = self.checks.get("queryBlind") or []
        booking = [u for u in blind if "venetianlasvegas.com/booking" in u]
        self.assertTrue(booking, "the booking URLs must be published as blind to change detection")
        self.assertEqual(self.checks["summary"].get("queryBlind"), len(blind))

    def test_every_marked_url_carries_its_reason(self):
        for row in self.checks.get("urls", []):
            if row.get("queryBlind"):
                self.assertTrue(row.get("queryBlindReason"), row["url"])
                self.assertIn("F77", row["queryBlindReason"])

    def test_the_record_explains_the_blind_spot_in_words(self):
        self.assertIn("queryBlind", self.checks.get("note", ""))

    def test_the_flagging_page_carries_the_finding(self):
        data = json.loads((ROOT / "site" / "data.json").read_text(encoding="utf-8"))
        flag = next((f for f in data["flags"] if f["id"] == "F77"), None)
        self.assertIsNotNone(flag, "F77 must be published")
        self.assertIn("queryBlind", flag["detail"] + flag["title"])
        self.assertTrue(flag["source"].startswith("https://"))


if __name__ == "__main__":
    unittest.main()
