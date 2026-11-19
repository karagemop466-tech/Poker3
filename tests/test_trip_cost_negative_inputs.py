"""A negative cost component is refused, not computed.

Session arena/7d96049f, 2026-11-19. The unknown-is-not-zero repair (scripts/trip_cost.py's MISSING rule,
landed for flag F39 by session arena/03d48a10-poker3 in 612a4c0, and claimed earlier on PR #184, which was
left open and untouched) closed the case where a *blank* component was priced as zero. The same class of
error remained open on the other side of zero: `float(value)` accepted a negative component and the
arithmetic carried on, so a resort fee of -$55 printed a nightly cost $62.36 *below* the published charge
and a room tax of -13.38% printed a discount. Nothing on the site or in any official source can legitimately
produce a negative fee, a negative rate or a negative count; a stray minus sign is a transcription error,
and a total built from one is wrong in the direction that makes the trip look affordable.

So `_not_negative()` rejects it at the boundary, and a blank is still unknown rather than zero — the two
rules have to hold together, which is what the second test below is for.

No published value changes: every figure the site prints comes from non-negative published components.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from trip_cost import published_model, trip_cost, true_nightly  # noqa: E402

TAX = 13.38
FEE = 55.0


class NegativeComponentsAreRefused(unittest.TestCase):
    def test_true_nightly_rejects_each_negative_component(self):
        for rate, fee, tax, name in ((-119, FEE, TAX, "room rate"), (119, -FEE, TAX, "resort fee"),
                                     (119, FEE, -TAX, "room tax percentage")):
            with self.subTest(field=name):
                with self.assertRaises(ValueError) as caught:
                    true_nightly(rate, fee, tax)
                self.assertIn(name, str(caught.exception), "the error must name the field that is wrong")
                self.assertIn("negative", str(caught.exception).lower())

    def test_trip_cost_rejects_negative_entries_nights_buyin_and_parking(self):
        for args, name in (((7, -1, 7, 119, FEE, TAX, 20), "buy-in"),
                           ((-7, 371.43, 7, 119, FEE, TAX, 20), "entries"),
                           ((7, 371.43, -7, 119, FEE, TAX, 20), "nights"),
                           ((7, 371.43, 7, 119, FEE, TAX, -20), "parking per night")):
            with self.subTest(field=name):
                with self.assertRaises(ValueError) as caught:
                    trip_cost(*args)
                self.assertIn(name, str(caught.exception))

    def test_a_negative_is_refused_rather_than_silently_treated_as_unknown(self):
        """`-55` must not be accepted because it is 'not published' in disguise.

        MISSING is (None, ""); a negative number is present and wrong, so it raises where a blank
        returns None. If the two were conflated the guard would look satisfied while a hand-edited
        input file still produced a number.
        """
        self.assertIsNone(true_nightly(119, "", TAX), "a blank stays unknown and returns None")
        with self.assertRaises(ValueError):
            true_nightly(119, -FEE, TAX)

    def test_zero_is_still_accepted_on_both_sides_of_the_formula(self):
        self.assertEqual(true_nightly(119, 0, TAX), 134.92)
        self.assertEqual(true_nightly(119, FEE, 0), 174.0)
        self.assertEqual(trip_cost(0, 371.43, 7, 119, FEE, TAX, 0)["tripTotal"], 1380.96)  # lodging only

    def test_the_published_model_is_untouched_by_the_guard(self):
        model = published_model(7, 371.43, 7, buy_in_exact=2600)
        self.assertEqual(model["trueCostPerNight"], 197.28)
        self.assertEqual(model["lodgingTotal"], 1380.96)
        self.assertEqual(model["tournamentTotal"], 2600.0)
        self.assertEqual(model["parkingTotal"], 140.0)
        self.assertEqual(model["tripTotal"], 4120.96)
        self.assertEqual(model["alternateTripTotal"], 4835.24)


if __name__ == "__main__":
    unittest.main()
