#!/usr/bin/env python3
"""Unit tests for the live hotel-rate parser.

The parser is tested against the exact wording the official booking engines print,
so a change to the page format is caught here rather than silently producing a wrong
rate. No network access is used.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import check_hotel_rates as rates  # noqa: E402


CAESARS_TEXT = (
    "Sorry! Our website is currently experiencing technical difficulties. "
    "Please try your search again "
    "22 Rooms Found "
    "$223 Room Rate + $50 Daily Resort Fee = $273 / Night, Includes resort fee, Excludes Taxes "
    "Standard Rate $320 "
    "$235 Room Rate + $50 Daily Resort Fee = $285 / Night, Includes resort fee, Excludes Taxes "
    "Standard Rate $337 "
)

CAESARS_RESTICTED = (
    "Your arrival date is restricted. Please choose a new arrival date below."
)

VENETIAN_PLACEHOLDER = (
    "Select Dates Thu, Nov 19 Sun, Nov 22 Check Rates "
    "December 10, 2026 $XXX December 11, 2026 $XXX December 12, 2026 $XXX December 13, 2026 $XXX "
    "*Pricing shown is best available suite and rate, includes daily resort fee, excludes taxes."
)


class CaesarsParserTests(unittest.TestCase):
    def test_reads_the_cheapest_published_breakdown(self):
        parsed = rates.parse_caesars(CAESARS_TEXT)
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed["nightlyRate"], 223)
        self.assertEqual(parsed["resortFeeIncluded"], 50)
        self.assertEqual(parsed["nightlyWithFee"], 273)
        self.assertEqual(parsed["roomsFound"], 22)

    def test_ignores_the_standard_rate_comparison(self):
        parsed = rates.parse_caesars(CAESARS_TEXT)
        self.assertNotEqual(parsed["nightlyWithFee"], 320)

    def test_returns_none_when_no_breakdown_is_present(self):
        self.assertIsNone(rates.parse_caesars("No rooms available for those dates."))

    def test_detects_a_restricted_arrival_date(self):
        self.assertRegex(CAESARS_RESTICTED, rates.RESTRICTED_PATTERN)


class VenetianParserTests(unittest.TestCase):
    def test_placeholder_price_is_not_a_rate(self):
        self.assertIsNone(rates.parse_venetian(VENETIAN_PLACEHOLDER))

    def test_reads_a_real_price_when_one_is_printed(self):
        parsed = rates.parse_venetian("December 10, 2026 $323 December 11, 2026 $323")
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed["nightlyWithFee"], 323)


class StripTagTests(unittest.TestCase):
    def test_removes_scripts_and_tags(self):
        text = rates.strip_tags(
            "<html><script>var x = '$999';</script><p>Rate $223 / Night</p></html>"
        )
        self.assertNotIn("$999", text)
        self.assertIn("$223", text)


class UnknownPropertyTests(unittest.TestCase):
    def test_an_unknown_property_returns_a_clear_status(self):
        result = rates.lookup("not-a-hotel", "2026-12-10", "2026-12-14")
        self.assertEqual(result["status"], "no booking URL recorded for this property")

    def test_a_departure_before_arrival_is_refused(self):
        result = rates.lookup("horseshoe", "2026-12-14", "2026-12-10")
        self.assertEqual(result["status"], "the departure date must be after the arrival date")

    def test_a_zero_night_stay_is_refused(self):
        result = rates.lookup("horseshoe", "2026-12-10", "2026-12-10")
        self.assertEqual(result["status"], "the departure date must be after the arrival date")

    def test_an_unparseable_date_is_refused(self):
        result = rates.lookup("horseshoe", "10 December 2026", "2026-12-14")
        self.assertTrue(result["status"].startswith("bad date"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
