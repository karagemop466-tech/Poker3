"""Blank price components are not evidence of a free component."""
import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from trip_cost import trip_cost, true_nightly


class MissingInputTests(unittest.TestCase):
    def test_unknown_tax_or_fee_does_not_produce_nightly_cost(self):
        for rate, fee, tax in [(100, 20, None), (100, '', 13.38), ('', 20, 13.38)]:
            self.assertIsNone(true_nightly(rate, fee, tax))
        self.assertEqual(true_nightly(100, 0, 0), 100)

    def test_unknown_components_do_not_create_all_in_total(self):
        defaults = dict(entries=2, buy_in=100, nights=3, rate=100, resort_fee=20,
                        tax_pct=13.38, parking_per_night=0, extra_nights_at=150)
        for key in defaults:
            if key == 'extra_nights_at':
                continue
            with self.subTest(key=key):
                values = {**defaults, key: None}
                result = trip_cost(**values)
                self.assertIsNone(result['tripTotal'])
                if key != 'rate':
                    self.assertIsNone(result['alternateTripTotal'])
                else:
                    self.assertIsNotNone(result['alternateTripTotal'])
        self.assertEqual(trip_cost(**defaults)['tripTotal'], 608.18)

    def test_exact_tournament_sum_is_independent_evidence(self):
        result = trip_cost(None, None, 1, 100, 0, 0, buy_in_exact=200)
        self.assertEqual(result['tripTotal'], 300)

class RenderTests(unittest.TestCase):
    def test_browser_calculator_unknowns(self):
        import subprocess
        root = Path(__file__).resolve().parents[1]
        subprocess.run(['node', 'tests/test_calculator_missing_inputs_render.js'], cwd=root, check=True)
