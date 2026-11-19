"""Blank or invalid price components are not evidence that the component is free."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from trip_cost import trip_cost, true_nightly  # noqa: E402


class MissingInputTests(unittest.TestCase):
    def test_unknown_rate_fee_or_tax_does_not_produce_a_nightly_cost(self):
        for rate, fee, tax in [
            (100, 20, None),
            (100, "", 13.38),
            ("", 20, 13.38),
            ("not a number", 20, 13.38),
            (100, -1, 13.38),
        ]:
            with self.subTest(rate=rate, fee=fee, tax=tax):
                self.assertIsNone(true_nightly(rate, fee, tax))
        self.assertEqual(true_nightly(100, 0, 0), 100)

    def test_unknown_components_never_create_an_all_in_total(self):
        defaults = dict(
            entries=2,
            buy_in=100,
            nights=3,
            rate=100,
            resort_fee=20,
            tax_pct=13.38,
            parking_per_night=0,
            extra_nights_at=150,
        )
        for key in defaults:
            if key == "extra_nights_at":
                continue
            with self.subTest(key=key):
                result = trip_cost(**{**defaults, key: None})
                self.assertIsNone(result["tripTotal"])
                if key != "rate":
                    self.assertIsNone(result["alternateTripTotal"])
                else:
                    # The alternate rate is independently published and can still be priced.
                    self.assertIsNotNone(result["alternateTripTotal"])
        self.assertEqual(trip_cost(**defaults)["tripTotal"], 608.18)

    def test_missing_parking_does_not_erase_known_tournament_and_lodging_parts(self):
        result = trip_cost(2, 100, 3, 100, 20, 13.38)
        self.assertEqual(result["tournamentTotal"], 200)
        self.assertEqual(result["trueCostPerNight"], 136.06)
        self.assertEqual(result["lodgingTotal"], 408.18)
        self.assertIsNone(result["parkingTotal"])
        self.assertIsNone(result["tripTotal"])

    def test_explicit_zero_is_valid_and_not_treated_as_missing(self):
        self.assertEqual(true_nightly(100, 0, 0), 100)
        result = trip_cost(0, 0, 0, 0, 0, 0, parking_per_night=0)
        self.assertEqual(result["tournamentTotal"], 0)
        self.assertEqual(result["trueCostPerNight"], 0)
        self.assertEqual(result["parkingTotal"], 0)
        self.assertEqual(result["tripTotal"], 0)

    def test_invalid_counts_and_rates_remain_unknown(self):
        result = trip_cost("2.5", 100, 1, "unknown", 20, 13.38, parking_per_night=0)
        self.assertIsNone(result["entries"])
        self.assertIsNone(result["tournamentTotal"])
        self.assertIsNone(result["roomRatePerNight"])
        self.assertIsNone(result["trueCostPerNight"])
        self.assertIsNone(result["tripTotal"])

    def test_exact_buy_in_sum_is_independent_of_missing_average_input(self):
        result = trip_cost(None, None, 1, 100, 0, 0, parking_per_night=0, buy_in_exact=200)
        self.assertEqual(result["tournamentTotal"], 200)
        self.assertEqual(result["tripTotal"], 300)

    def test_invalid_exact_sum_does_not_silently_replace_other_known_inputs(self):
        result = trip_cost(2, 100, 1, 100, 0, 0, parking_per_night=0, buy_in_exact="-1")
        self.assertEqual(result["tournamentTotal"], 200)
        self.assertEqual(result["tripTotal"], 300)


class RenderTests(unittest.TestCase):
    def test_browser_calculator_handles_unknowns_and_hotel_presets(self):
        import subprocess

        root = Path(__file__).resolve().parents[1]
        subprocess.run(["node", "tests/test_calculator_missing_inputs_render.js"], cwd=root, check=True)

    def test_hotel_page_widget_handles_unknowns_without_zeroing(self):
        import subprocess

        root = Path(__file__).resolve().parents[1]
        subprocess.run(["node", "tests/test_hotel_cost_widget_render.js"], cwd=root, check=True)


if __name__ == "__main__":
    unittest.main()
