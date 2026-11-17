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

    def test_nights_and_entries_columns_print_counts_not_money(self):
        """A 'Nights' cell must say a number of nights, an 'Entries' cell a number of entries.

        Regression: both columns used to render a dollar subtotal (nights x true nightly,
        entries x buy-in) under a header that names a count, so a reader scanning the
        like-for-like table saw money where a quantity belonged.
        """
        body = PAGE[PAGE.index("function buildCompare"):]
        cells = re.findall(r"'<td>' \+ ([^+]+?) \+", body)
        self.assertIn("nights + ' nights'", body)
        self.assertIn("entries + ' entries'", body)
        # The raw subtotals must still be shown, but only as a muted annotation.
        self.assertNotIn("'<td>' + (lodging ? money(lodging)", body)
        self.assertNotIn("'<td>' + money(tournament)", body)

    def test_entry_total_uses_the_exact_sum_not_a_rounded_mean(self):
        """Seven buy-ins sum to $2,600; their mean is $371.428571...

        Multiplying the published (rounded) mean by seven prints $2,600.01, a phantom cent
        on a page whose whole point is arithmetic a reader can check.
        """
        model = DATA["tripCostModel"]
        self.assertAlmostEqual(model["buyIn"], 371.43, places=2)
        self.assertEqual(model["tournamentTotal"], 2600.0)
        self.assertEqual(model["primaryBuyInSum"], 2600.0)
        self.assertAlmostEqual(model["entries"] * model["buyIn"], 2600.01, places=2)
        # both the page and the generator must consult the exact sum
        self.assertIn("model.primaryBuyInSum", PAGE)
        self.assertIn("buy_in_exact", (ROOT / "scripts" / "trip_cost.py").read_text(encoding="utf-8"))

    def test_parking_is_itemized_outside_the_core_formula(self):
        self.assertIn("entries × average buy-in + nights × true hotel cost", PAGE)
        self.assertIn("const coreEstimate = tournament + lodging;", PAGE)
        self.assertIn("const allIn = coreEstimate + parking;", PAGE)
        self.assertIn("Parking is not included in true room cost per night or in the core formula.", PAGE)


if __name__ == "__main__":
    unittest.main()
