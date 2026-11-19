"""A blank calculator input is an unknown, never a zero cost (M2).

`scripts/trip_cost.py` is the single definition of the arithmetic, and site/calculator.html and
site/data.json's `tripCostModel` both read it. Until now `true_nightly()` did `float(tax_pct or 0)`, so
an unpublished room-tax percentage was priced as *no* tax — while four of the eight hotels on the site
publish a mandatory resort fee and no tax percentage at all (F39). Every one of those properties was
therefore shown cheaper per night than the Venetian, whose 13.38% Clark County room tax is published,
for no reason except that a blank had been read as a zero. The same coercion sat in the page's own
`Number(form.x.value) || 0` reader, so a reader who cleared a box got a smaller total instead of a
shrug.

This is the repair PR #184 (`arena/5cfdd619-poker3`) claimed at 06:47 UTC and never published; that
session went quiet and its branch is untouched, so the fix is implemented here and its approach —
blank is unknown, explicit zero is a number — is kept. tests/test_calculator_missing_inputs_render.js
drives the same rule through the page's real script.

No published source value changes: every hotel row keeps the rate, fee and tax it was read with, and
what changes is that a line the sources cannot close is now left open.
"""
from __future__ import annotations

import json
import unittest
from pathlib import Path

import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import trip_cost as tc  # noqa: E402

CALCULATOR = (ROOT / "site" / "calculator.html").read_text(encoding="utf-8")
DATA = json.loads((ROOT / "site" / "data.json").read_text(encoding="utf-8"))


class TrueNightly(unittest.TestCase):
    def test_every_component_must_be_published(self):
        for rate, fee, tax in (("", 55, 13.38), (119, "", 13.38), (119, 55, ""),
                               (None, 55, 13.38), (119, None, 13.38), (119, 55, None)):
            with self.subTest(rate=rate, fee=fee, tax=tax):
                self.assertIsNone(tc.true_nightly(rate, fee, tax),
                                  "an unpublished component must leave the nightly cost unknown")

    def test_missing_tax_is_not_treated_as_zero_tax(self):
        """The regression: $119 + $55 with no published tax used to print the no-tax figure."""
        self.assertEqual(tc.true_nightly(119, 55, 13.38), 197.28)
        self.assertIsNone(tc.true_nightly(119, 55, ""), "197.28 with tax and 174.00 without are different claims")
        self.assertNotEqual(tc.true_nightly(119, 55, ""), tc.true_nightly(119, 55, 0))

    def test_explicit_zero_is_still_a_number(self):
        self.assertEqual(tc.true_nightly(119, 55, 0), 174.00)
        self.assertEqual(tc.true_nightly(119, 0, 13.38), 134.92)  # a waived fee is 0, not blank

    def test_negative_component_is_rejected_not_absorbed(self):
        with self.assertRaises(ValueError):
            tc.true_nightly(-119, 55, 13.38)


class TripCostTotals(unittest.TestCase):
    def test_each_line_is_computed_from_its_own_inputs(self):
        full = tc.trip_cost(7, 300, 7, 119, 55, 13.38, 20)
        self.assertEqual(full["coreEstimate"], round(7 * 300 + 7 * 197.28, 2))
        self.assertEqual(full["tripTotal"], round(full["coreEstimate"] + 140.0, 2))
        self.assertEqual(full["unknown"], [])

    def test_unknown_parking_leaves_the_core_estimate_available(self):
        model = tc.trip_cost(7, 300, 7, 119, 55, 13.38, "")
        self.assertIsNotNone(model["coreEstimate"], "the published formula needs no parking figure")
        self.assertIsNone(model["tripTotal"], "an all-in number without parking would be a different claim")
        self.assertEqual(model["unknown"], ["parking"])

    def test_unknown_hotel_component_leaves_the_entry_line_available(self):
        model = tc.trip_cost(7, 300, 7, "", "", "", "")
        self.assertEqual(model["tournamentTotal"], 2100.0)
        self.assertIsNone(model["trueCostPerNight"])
        self.assertIsNone(model["lodgingTotal"])
        self.assertIsNone(model["coreEstimate"])
        self.assertEqual(model["unknown"], ["room rate", "resort fee", "room tax", "parking"])

    def test_blank_entries_are_not_a_free_tournament(self):
        model = tc.trip_cost("", "", 7, 119, 55, 13.38, 20)
        self.assertIsNone(model["tournamentTotal"])
        self.assertIsNone(model["coreEstimate"])
        self.assertEqual(model["unknown"], ["entries", "buy-in"])

    def test_alternate_rate_prices_only_the_lodging_line(self):
        model = tc.trip_cost(7, 300, 7, 119, 55, 13.38, 20, extra_nights_at=209)
        self.assertEqual(model["alternateTrueCostPerNight"], 299.32)
        expected = round(7 * 300 + 7 * 299.32 + 140.0, 2)
        self.assertEqual(model["alternateTripTotal"], expected)
        # With parking unknown, the alternate core must still be offered and the all-in must not be.
        alt = tc.trip_cost(7, 300, 7, 119, 55, 13.38, "", extra_nights_at=209)
        self.assertIsNone(alt["alternateTripTotal"])

    def test_alternate_rate_is_unknown_when_tax_is_unknown(self):
        model = tc.trip_cost(7, 300, 7, 119, 55, "", 20, extra_nights_at=209)
        self.assertIsNone(model["alternateTrueCostPerNight"])
        self.assertIsNone(model["alternateTripTotal"])


class PublishedModelIsUnchanged(unittest.TestCase):
    """The repair must not move a single published figure: every Venetian input is on record."""

    def test_canonical_model_still_totals_the_published_numbers(self):
        model = DATA["tripCostModel"]
        self.assertEqual(model["trueCostPerNight"], 197.28)
        self.assertEqual(model["lodgingTotal"], 1380.96)
        self.assertEqual(model["tournamentTotal"], 2600.0)
        self.assertEqual(model["parkingTotal"], 140.0)
        self.assertEqual(model["tripTotal"], 4120.96)
        self.assertEqual(model["alternateTrueCostPerNight"], 299.32)
        self.assertEqual(model["alternateTripTotal"], 4835.24)
        self.assertEqual(model["unknown"], [], "every component of the Venetian floor is published")

    def test_builder_reproduces_the_published_model(self):
        rebuilt = tc.published_model(7, 371.43, 7, buy_in_exact=2600)
        for key, value in rebuilt.items():
            if key in ("liveQuote",):
                continue
            with self.subTest(key=key):
                self.assertEqual(DATA["tripCostModel"][key], value)


class PageFollowsTheSameRule(unittest.TestCase):
    def test_no_blank_is_described_as_zero(self):
        self.assertNotIn("Leave a field blank to treat it as zero", CALCULATOR)
        self.assertIn("A blank field is unknown, not zero", CALCULATOR)

    def test_the_reader_returns_null_rather_than_zero(self):
        self.assertNotIn("Number(form.entries.value) || 0", CALCULATOR)
        self.assertIn("if (raw === '' || (input.validity && !input.validity.valid)) return null;", CALCULATOR)
        self.assertIn("const show = (n) => (known(n) ? money(n) : UNKNOWN);", CALCULATOR)

    def test_a_hotel_preset_clears_what_the_property_does_not_publish(self):
        # The old handler skipped a box the property left blank, so the previously loaded
        # property's figure was priced against this property's row.
        self.assertNotIn("if (b.dataset.rate !== '') form.rate.value = b.dataset.rate;", CALCULATOR)
        self.assertIn("form.rate.value = b.dataset.rate;", CALCULATOR)
        self.assertIn("form.parking.value = b.dataset.parking;", CALCULATOR)

    def test_the_page_names_the_render_guard(self):
        for workflow in ("verify.yml", "pages.yml"):
            text = (ROOT / ".github" / "workflows" / workflow).read_text(encoding="utf-8")
            with self.subTest(workflow=workflow):
                self.assertIn("node tests/test_calculator_missing_inputs_render.js", text)


if __name__ == "__main__":
    unittest.main()
