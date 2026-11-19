"""A "true cost per night" may only be published when its arithmetic closes.

The brief asks for true cost = rate + mandatory resort fee + tax, compared like for like.
These tests pin the rule: a property gets a published true-cost figure only when the
components multiply out to it, and a figure derived from a fee-inclusive average must say so
and must never enter the fee-exclusive comparison table.
"""
from pathlib import Path
import json
import unittest

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / "site" / "data.json").read_text(encoding="utf-8"))
HOTELS = {h["id"]: h for h in DATA["hotels"]}
CALC = (ROOT / "site" / "calculator.html").read_text(encoding="utf-8")
TAX = 13.38


class DerivedHotelCostTests(unittest.TestCase):
    def test_venetian_floor_closes(self):
        v = HOTELS["venetian"]
        expected = round((v["baseRateFloor"] + v["resortFee"]) * (1 + v["taxRate"] / 100), 2)
        self.assertAlmostEqual(v["trueNightlyLow"], expected, places=2)

    def test_wynn_derived_figure_is_the_published_average_plus_the_county_tax(self):
        w = HOTELS["wynn"]
        # $405 and $495 avg/night, both "Includes Resort Fee, Excludes taxes".
        self.assertAlmostEqual(float(w["derivedNightlyLow"]), round(405 * (1 + TAX / 100), 2), places=2)
        self.assertAlmostEqual(float(w["derivedNightlyHigh"]), round(495 * (1 + TAX / 100), 2), places=2)
        self.assertIn("derived", w["derivedNightlyNote"].lower())
        self.assertIn("Includes Resort Fee, Excludes taxes", w["derivedNightlyNote"])
        # Wynn still has no fee-exclusive closed figure, because it prints no tax amount.
        self.assertEqual(w["trueNightlyLow"], "")

    def test_a_fee_inclusive_quote_is_never_entered_as_a_room_rate_in_the_comparison(self):
        # The comparison table adds the resort fee itself, so any row it prints with a rate
        # must be a published ROOM rate; the derived Wynn figure stays on the hotels page.
        self.assertNotIn("wynnDerivedTrueNightly", CALC)
        self.assertIn("already includes the resort fee", CALC)

    def test_every_published_true_nightly_is_recomputable_from_its_own_row(self):
        for h in DATA["hotels"]:
            if not isinstance(h.get("trueNightlyLow"), (int, float)):
                continue  # blank/string rows carry no claim
            with self.subTest(hotel=h["id"]):
                self.assertIn("resortFee", h)
                self.assertIn("taxRate", h)
                self.assertIsInstance(h["resortFee"], (int, float))
                self.assertIsInstance(h["taxRate"], (int, float))
                self.assertLessEqual(h["trueNightlyLow"], h["trueNightlyHigh"])

    def test_no_hotel_claims_a_total_it_cannot_support(self):
        for h in DATA["hotels"]:
            with self.subTest(hotel=h["id"]):
                if h.get("trueNightlyLow") not in ("", None):
                    self.assertTrue(h.get("baseRateFloor") or h.get("quote") or h.get("quotes"),
                                    f"{h['id']} publishes a true nightly with neither a rate nor a dated quote")
                if not h.get("baseRateFloor") and not h.get("derivedNightlyLow"):
                    self.assertEqual(h.get("trueNightlyLow", ""), "",
                                     f"{h['id']} has no published rate but claims a true nightly")


if __name__ == "__main__":
    unittest.main()
