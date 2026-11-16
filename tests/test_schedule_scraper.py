#!/usr/bin/env python3
"""Unit tests for the Venetian schedule scraper.

The scraper is tested against a saved fragment of the official event page's table, so a
change to the page format is caught here rather than silently reporting "no differences".
No network access is used.
"""
from __future__ import annotations

import json
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import scrape_venetian_schedule as scraper  # noqa: E402


SAMPLE_ROWS = """
<table><tbody>
<tr><td>Monday, November 16, 2026</td><td>11:10 AM</td><td>1</td>
<td>$300 No Limit Hold'em 1A $75K GTD</td>
<td><a href="https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_10.pdf">View</a></td><td>&mdash;</td></tr>
<tr><td>Monday, November 16, 2026</td><td>5:10 PM</td><td>1</td>
<td>$300 No Limit Hold'em 1B $75K GTD</td>
<td><a href="https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_9.pdf">View</a></td><td>&mdash;</td></tr>
<tr><td>Saturday, December 12, 2026</td><td>10:10 AM</td><td>47</td>
<td>$2,200 No Limit Hold'em 1A $1 Mill GTD<br>- PokerAtlas Championship Title Event</td>
<td><a href="https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_21.pdf">View</a></td><td>&mdash;</td></tr>
<tr><td>Wednesday, December 23, 2026</td><td>5:10 PM</td><td>64</td>
<td>$200 No Limit Hold'em Bounty $8K GTD (1Day)</td>
<td><a href="https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_1.pdf">View</a></td><td></td></tr>
</tbody></table>
"""


class ParseTests(unittest.TestCase):
    def test_reads_every_row(self):
        rows = scraper.parse_rows(SAMPLE_ROWS)
        self.assertEqual(len(rows), 4)

    def test_reads_the_date_and_time(self):
        rows = scraper.parse_rows(SAMPLE_ROWS)
        self.assertEqual(rows[0]["date"], "2026-11-16")
        self.assertEqual(rows[0]["time"], "11:10 AM")
        self.assertEqual(rows[3]["date"], "2026-12-23")

    def test_reads_the_structure_sheet_number(self):
        rows = scraper.parse_rows(SAMPLE_ROWS)
        self.assertEqual(rows[0]["structureSheet"], 10)
        self.assertEqual(rows[1]["structureSheet"], 9)
        self.assertEqual(rows[2]["structureSheet"], 21)
        self.assertEqual(rows[3]["structureSheet"], 1)

    def test_reads_the_event_number(self):
        rows = scraper.parse_rows(SAMPLE_ROWS)
        self.assertEqual(rows[0]["eventNumber"], "1")
        self.assertEqual(rows[2]["eventNumber"], "47")

    def test_finds_the_flight_suffix(self):
        self.assertEqual(scraper.flight_label("$300 No Limit Hold'em 1A $75K GTD"), "1A")
        self.assertEqual(scraper.flight_label("$300 No Limit Hold'em 1B $75K GTD"), "1B")
        self.assertEqual(
            scraper.flight_label("$300 No Limit Hold'em Day 2 Restart"), "Day 2 Restart"
        )
        self.assertEqual(
            scraper.flight_label("$300 No Limit Hold'em LIPS Final Table"), "Final Table"
        )
        self.assertEqual(
            scraper.flight_label("$800 No Limit Hold'em LIPS Ladies (2Day)"), "Day 1"
        )
        self.assertEqual(scraper.flight_label("$200 No Limit Hold'em Bounty $8K GTD (1Day)"), "")

    def test_ignores_rows_with_no_readable_date(self):
        rows = scraper.parse_rows(
            "<tr><td>soon</td><td>10:10 AM</td><td>1</td><td>x</td></tr>"
        )
        self.assertEqual(rows, [])


class CompareTests(unittest.TestCase):
    def setUp(self):
        self.curated = json.loads(
            (ROOT / "data" / "venetian_dse_iv.json").read_text(encoding="utf-8")
        )["events"]
        self.scraped = scraper.parse_rows(SAMPLE_ROWS)

    def test_a_matching_page_reports_no_difference(self):
        # The sample rows exist in the curated data with the same values.
        differences = scraper.compare(self.scraped, self.curated)
        kinds = {d["kind"] for d in differences}
        self.assertNotIn("start time changed", kinds)
        self.assertNotIn("structure sheet changed", kinds)

    def test_a_changed_start_time_is_reported(self):
        rows = [dict(r) for r in self.scraped]
        rows[0]["time"] = "1:10 PM"
        differences = scraper.compare(rows, self.curated)
        changed = [d for d in differences if d["kind"] == "start time changed"]
        self.assertEqual(len(changed), 1)
        self.assertEqual(changed[0]["now"], "1:10 PM")

    def test_a_changed_structure_sheet_is_reported(self):
        rows = [dict(r) for r in self.scraped]
        rows[0]["structureSheet"] = 17
        differences = scraper.compare(rows, self.curated)
        changed = [d for d in differences if d["kind"] == "structure sheet changed"]
        self.assertEqual(len(changed), 1)
        self.assertEqual(changed[0]["now"], 17)

    def test_a_new_row_on_the_page_is_reported(self):
        rows = [dict(r) for r in self.scraped]
        rows.append(
            {
                "date": "2026-12-24",
                "time": "11:10 AM",
                "eventNumber": "65",
                "name": "$200 No Limit Hold'em Bounty (1Day)",
                "structureSheet": 1,
                "guarantee": "",
            }
        )
        differences = scraper.compare(rows, self.curated)
        added = [d for d in differences if d["kind"] == "added on the official page"]
        self.assertEqual(len(added), 1)
        self.assertEqual(added[0]["event"], "65")

    def test_a_row_missing_from_the_page_is_reported(self):
        differences = scraper.compare([], self.curated)
        missing = [d for d in differences if d["kind"] == "no longer on the official page"]
        self.assertEqual(len(missing), len(self.curated))


if __name__ == "__main__":
    unittest.main(verbosity=2)
