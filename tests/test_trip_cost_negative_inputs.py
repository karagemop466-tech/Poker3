"""A negative cost component is refused, never computed into a total.

Session arena/7d96049f, 2026-11-19. The unknown-is-not-zero repair closed the case where a
*blank* component was priced as zero. The same class of error remained open on the other side
of zero: a negative component is not a discount, it is a transcription error, and a total built
from one prints below the published charge — a resort fee of -$55 would take $62.36 off a night
and a room tax of -13.38% would print a discount. Nothing on the site or in any official source
can legitimately produce a negative fee, rate or count.

`_optional_number()` in scripts/trip_cost.py refuses such a value the same way it refuses a
blank: it returns None, so the field stays unknown and the arithmetic never runs on it. That is
deliberately *not* a raised error. The project rule is that an unconfirmable value is left blank
and flagged, not allowed to fail the build, and the site's existing calculator tests pin a blank
and a negative to the same unknown outcome (tests/test_calculator_missing_inputs.py asserts
`true_nightly(100, -1, 13.38) is None`). This file keeps the negative half of that contract
explicit so a future edit cannot quietly start computing on a minus sign.

No published value changes: every figure the site prints comes from non-negative published
components.
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
    def test_true_nightly_refuses_each_negative_component(self):
        """A negative rate, fee or tax percentage yields no nightly cost at all."""
        for rate, fee, tax, name in ((-119, FEE, TAX, "room rate"), (119, -FEE, TAX, "resort fee"),
                                     (119, FEE, -TAX, "room tax percentage")):
            with self.subTest(field=name):
                self.assertIsNone(
                    true_nightly(rate, fee, tax),
                    f"a negative {name} must not produce a nightly cost",
                )

    def test_trip_cost_refuses_negative_entries_nights_buyin_and_parking(self):
        for args, name in (((7, -1, 7, 119, FEE, TAX, 20), "buy-in"),
                           ((-7, 371.43, 7, 119, FEE, TAX, 20), "entries"),
                           ((7, 371.43, -7, 119, FEE, TAX, 20), "nights"),
                           ((7, 371.43, 7, 119, FEE, TAX, -20), "parking per night")):
            with self.subTest(field=name):
                result = trip_cost(*args)
                self.assertIsNone(
                    result.get("tripTotal"),
                    f"a negative {name} must not be priced into a trip total",
                )

    def test_a_negative_is_refused_rather_than_computed_as_a_discount(self):
        """`-55` must not be accepted in disguise as a cheaper night.

        The refusal is observable as "no number comes back", which is the same unknown outcome
        a blank produces. What must never happen is a nightly cost below the published charge.
        """
        self.assertIsNone(true_nightly(119, "", TAX), "a blank stays unknown and returns None")
        self.assertIsNone(true_nightly(119, -FEE, TAX), "a negative fee stays unknown too")
        # The negative must not silently become a discount: no figure is returned at all.
        self.assertNotEqual(true_nightly(119, -FEE, TAX), 62.36)

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
