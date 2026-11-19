"""A value no official source published is unknown, never zero.

Several reviewed properties publish a mandatory resort fee and no room-tax percentage
(flag F39). Treating that missing percentage as 0% would print a nightly cost below the
published charge, and treating a blank entry count as zero would print a zero-dollar
tournament budget. Both are evidence errors, not arithmetic ones, so both are asserted
here against the module the dashboard actually publishes from.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from trip_cost import published_model, trip_cost, true_nightly  # noqa: E402

TAX = 13.38
FEE = 55.0


class UnknownIsNotZeroTests(unittest.TestCase):
    def test_missing_tax_percentage_does_not_produce_a_nightly_cost(self):
        self.assertIsNone(true_nightly(119, FEE, None))
        self.assertIsNone(true_nightly(119, FEE, ''))

    def test_missing_rate_or_fee_does_not_produce_a_nightly_cost(self):
        self.assertIsNone(true_nightly(None, FEE, TAX))
        self.assertIsNone(true_nightly(119, None, TAX))

    def test_an_explicit_zero_is_still_zero(self):
        # A waived parking fee (F86) and a zero-tax state are real inputs, not decimals.
        self.assertEqual(true_nightly(119, FEE, 0), 174.0)
        self.assertEqual(trip_cost(7, 371.43, 7, 119, FEE, TAX, 0)['parkingTotal'], 0.0)

    def test_unknown_entry_count_withholds_the_tournament_total(self):
        out = trip_cost(None, 371.43, 7, 119, FEE, TAX, 20)
        self.assertIsNone(out['entries'])
        self.assertIsNone(out['tournamentTotal'])
        self.assertIsNone(out['tripTotal'])
        # The lodging side is still computable and is still published.
        self.assertEqual(out['lodgingTotal'], 1380.96)

    def test_unknown_parking_withholds_only_the_all_in_total(self):
        out = trip_cost(7, 371.43, 7, 119, FEE, TAX, None, buy_in_exact=2600)
        self.assertEqual(out['tournamentTotal'], 2600.0)
        self.assertEqual(out['lodgingTotal'], 1380.96)
        self.assertIsNone(out['parkingTotal'])
        self.assertIsNone(out['tripTotal'])

    def test_the_published_model_is_unchanged_by_the_repair(self):
        model = published_model(7, 371.43, 7, buy_in_exact=2600)
        self.assertEqual(model['tournamentTotal'], 2600.0)
        self.assertEqual(model['trueCostPerNight'], 197.28)
        self.assertEqual(model['lodgingTotal'], 1380.96)
        self.assertEqual(model['parkingTotal'], 140.0)
        self.assertEqual(model['tripTotal'], 4120.96)
        self.assertEqual(model['alternateTrueCostPerNight'], 299.32)
        self.assertEqual(model['alternateTripTotal'], 4835.24)


if __name__ == '__main__':
    unittest.main()
