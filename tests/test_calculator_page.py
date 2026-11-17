"""Guard the trip-cost page against claims that outrun the canonical data."""
from pathlib import Path
import json
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
PAGE = (ROOT / "site" / "calculator.html").read_text(encoding="utf-8")
DATA = json.loads((ROOT / "site" / "data.json").read_text(encoding="utf-8"))


class CalculatorPageTests(unittest.TestCase):
    def test_defaults_match_the_canonical_trip_cost_model(self):
        model = DATA["tripCostModel"]
        self.assertEqual(int(re.search(r'id="entries"[^>]*value="([^"]+)"', PAGE).group(1)), model["entries"])
        self.assertAlmostEqual(
            float(re.search(r'id="buyIn"[^>]*value="([^"]+)"', PAGE).group(1)),
            model["buyIn"],
        )
        self.assertEqual(int(re.search(r'id="nights"[^>]*value="([^"]+)"', PAGE).group(1)), model["nights"])
        self.assertAlmostEqual(float(re.search(r'id="rate"[^>]*value="([^"]+)"', PAGE).group(1)), model["roomRatePerNight"])
        self.assertAlmostEqual(float(re.search(r'id="resortFee"[^>]*value="([^"]+)"', PAGE).group(1)), model["resortFeePerNight"])
        self.assertAlmostEqual(float(re.search(r'id="taxRate"[^>]*value="([^"]+)"', PAGE).group(1)), model["taxPct"])
        self.assertAlmostEqual(float(re.search(r'id="parking"[^>]*value="([^"]+)"', PAGE).group(1)), model["parkingPerNight"])

    def test_page_does_not_mislabel_candidates_as_confirmed_single_entry(self):
        self.assertIn("not confirmed single-entry", PAGE)
        self.assertIn("F31", PAGE)
        self.assertNotIn("verified single-entry entries", PAGE)
        self.assertEqual(sum(event.get("entryType") == "single-entry-confirmed" for event in DATA["events"]), 0)

    def test_parking_is_itemized_outside_the_core_formula(self):
        self.assertIn("entries × average buy-in + nights × true hotel cost", PAGE)
        self.assertIn("const coreEstimate = tournament + lodging;", PAGE)
        self.assertIn("const allIn = coreEstimate + parking;", PAGE)
        self.assertIn("Parking is not included in true room cost per night or in the core formula.", PAGE)


if __name__ == "__main__":
    unittest.main()
