"""Regression checks for the 2026-11-19 manual re-read of flags F17, F31 and F92.

These assert that the published flag text and the dated research record carry
the evidence read on 2026-11-19 and the official sources behind it. They do not
re-fetch the venue pages, and they do not change any venue value.
"""
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def _load_flags():
    with open(os.path.join(ROOT, "site", "data.json"), encoding="utf-8") as f:
        return {f_["id"]: f_ for f_ in json.load(f)["flags"]}


RECORD = os.path.join(ROOT, "research", "reread_2026-11-19.md")

OFFICIAL_URLS = [
    "https://www.venetianlasvegas.com/resort/casino/poker.html",
    "https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html",
    "https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-apr-2023.html",
]


class RereadRecordTests(unittest.TestCase):
    def setUp(self):
        with open(RECORD, encoding="utf-8") as f:
            self.text = f.read()

    def test_record_cites_each_official_page_read(self):
        for url in OFFICIAL_URLS:
            self.assertIn(url, self.text)

    def test_record_states_no_value_was_changed(self):
        self.assertIn("No venue value", self.text)

    def test_record_keeps_f31_open_and_names_the_venue_question(self):
        self.assertIn("F31", self.text)
        self.assertIn("still open", self.text)
        self.assertIn("maximum number of entries per player", self.text)

    def test_record_flags_booking_quote_as_unconfirmed(self):
        self.assertIn("loading", self.text)
        self.assertIn("$4,010.55", self.text)


class RereadFlagTests(unittest.TestCase):
    def setUp(self):
        self.flags = _load_flags()

    def test_f92_is_narrowed_to_the_banner_rollover(self):
        flag = self.flags["F92"]
        self.assertEqual(flag["severity"], "Low")
        self.assertIn("Re-read 2026-11-19", flag["title"])
        self.assertIn("WPT Fall Festival", flag["detail"])
        self.assertIn("DeepStack Extravaganza IV", flag["detail"])
        self.assertIn("no tournament", flag["title"].lower() + flag["detail"].lower())

    def test_f17_records_the_live_earliest_start_rows(self):
        detail = self.flags["F17"]["detail"]
        self.assertIn("2026-11-19", detail)
        self.assertIn("9:10 AM", detail)
        self.assertIn("December 12", detail)
        self.assertIn("10:10 AM", detail)
        self.assertIn("no 8:00 AM start is published", self.flags["F17"]["title"])

    def test_f31_keeps_open_status_and_records_the_2023_label(self):
        flag = self.flags["F31"]
        self.assertEqual(flag["severity"], "High")
        self.assertIn("Re-read 2026-11-19", flag["detail"])
        self.assertIn("One Entry Only with One Hour of Registration", flag["detail"])
        self.assertIn("F31 remains open", flag["detail"])


if __name__ == "__main__":
    unittest.main()
