"""The dated checkout total must stay on the published record, reconciling to the cent.

A parallel integration landed the same official booking-engine reading first (session
arena/4c7b94ab-poker3: `VENETIAN_QUOTE_TRIP`, `nightly` pairs, `TRIP.lodgingTotalAllIn`),
so this test pins the *published* shape of that quote rather than an earlier draft's field
names, plus the research capture kept in `research/` as provenance. It reads site/data.json
only and never imports the builder.
"""

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = json.loads((ROOT / "site" / "data.json").read_text(encoding="utf-8"))
CAPTURE = json.loads(
    (ROOT / "research" / "trip_window_quote_2026-11-17_d1a97472.json").read_text(encoding="utf-8")
)

EXPECTED_TOTAL = 4010.55
TRIP_ARRIVAL = "2026-11-23"
TRIP_DEPARTURE = "2026-11-30"
RESORT_FEE = 55.00
EXPECTED_NIGHTLY = [164.25, 164.25, 201.75, 231.75, 1649.25, 554.25, 186.75]
EXPECTED_TRUE = [248.59, 248.59, 291.10, 325.12, 1932.28, 690.77, 274.10]


def trip_quote():
    v = next(h for h in DATA["hotels"] if h["id"] == "venetian")
    return v, next(q for q in v.get("quotes", []) if q.get("checkIn") == TRIP_ARRIVAL)


def trip_rate_row():
    return next(r for r in DATA["rateLog"]
                if r.get("hotel") == "venetian" and r.get("observedOn") == "2026-11-17"
                and "checkout total" in r.get("quoteType", "")
                and "7 nights" in r.get("quoteType", ""))


class TripWindowCheckoutTotal(unittest.TestCase):
    def test_capture_matches_the_published_quote(self):
        ven, q = trip_quote()
        self.assertEqual(q["total"], EXPECTED_TOTAL)
        self.assertEqual(q["taxes"], 473.30)
        self.assertEqual(q["averageRate"], 505.32)
        self.assertEqual(q["resortFeePerNight"], RESORT_FEE)
        self.assertEqual(q["source"], CAPTURE["source"])
        self.assertEqual(q["observedOn"], "2026-11-17")

        # The dated capture records the same seven nightly rates and their arithmetic.
        self.assertEqual([n["rate"] for n in CAPTURE["nightsList"]], EXPECTED_NIGHTLY)
        self.assertAlmostEqual(CAPTURE["total"], EXPECTED_TOTAL, places=2)
        self.assertAlmostEqual(CAPTURE["taxes"], 473.30, places=2)
        self.assertAlmostEqual(CAPTURE["resortFees"], 385.00, places=2)
        self.assertEqual(CAPTURE["calendar"], "https://www.venetianlasvegas.com/booking?"
                         "adults[]=2&arrival_date=2026-11-23&children[]=0"
                         "&departure_date=2026-11-30&view=calendar")

    def test_every_dated_quote_reconciles_to_the_printed_total(self):
        for hotel in DATA["hotels"]:
            for q in hotel.get("quotes", []):
                if "total" not in q or not isinstance(q.get("total"), (int, float)):
                    continue
                nights = q.get("nightly")
                if not nights:
                    # Older dated reads were stored without the nightly breakdown; the
                    # published shapes that carry it must reconcile exactly.
                    continue
                fee = q.get("resortFeePerNight", RESORT_FEE)
                derived = [round((rate + fee) * 1.1338, 2) for _, rate in nights]
                self.assertAlmostEqual(sum(derived), q["total"], places=2,
                                       msg=f"{hotel['id']} {q.get('checkIn')} derived total")
                if "derivedNightly" in q:
                    self.assertEqual(q["derivedNightly"], derived)
                if "taxes" in q:
                    room = sum(rate for _, rate in nights)
                    self.assertAlmostEqual(room + fee * len(nights), q["total"] - q["taxes"],
                                           places=2,
                                           msg=f"{hotel['id']} {q.get('checkIn')} subtotal")

    def test_venetian_trip_quote_derived_nightly_add_up(self):
        _, q = trip_quote()
        self.assertEqual(q["derivedTotal"], EXPECTED_TOTAL)
        self.assertEqual(q["derivedNightly"], EXPECTED_TRUE)
        self.assertAlmostEqual(sum(q["derivedNightly"]), EXPECTED_TOTAL, places=2)
        for (_, rate), truth in zip(q["nightly"], EXPECTED_TRUE):
            self.assertAlmostEqual(round((rate + RESORT_FEE) * 1.1338, 2), truth, places=2)
        # Sum check with per-night rounding = printed total.
        self.assertAlmostEqual(
            sum(round((rate + RESORT_FEE) * 1.1338, 2) for _, rate in q["nightly"]),
            EXPECTED_TOTAL, places=2)

    def test_rate_log_row_for_the_stay_is_dated_and_sources(self):
        row = trip_rate_row()
        self.assertEqual(row["tax"], "473.30 printed (7 nights)")
        self.assertIn("164.25 (Nov 23)", row["publishedStartingRates"])
        self.assertIn("55.00 per night", row["resortFee"])
        self.assertIn("4,010.55", row["note"])
        self.assertIn("505.32", row["note"])
        self.assertEqual(row["nightlyRates"], EXPECTED_NIGHTLY)
        self.assertEqual(row["nightlyTrueCost"], EXPECTED_TRUE)
        self.assertIn("23-30 Nov 2026", row["quoteType"])
        self.assertTrue(row["source"].startswith("https://www.venetianlasvegas.com/booking"))
        self.assertLessEqual(row["observedOn"], DATA["asOf"])

    def test_venetian_booking_links_carry_the_whole_stay(self):
        ven, _ = trip_quote()
        labels = [b["label"] for b in ven.get("bookingLinks", [])]
        self.assertIn("whole trip, 7 nights", labels)
        trip = next(b for b in ven["bookingLinks"] if b["label"] == "whole trip, 7 nights")
        self.assertIn(f"arrival_date={TRIP_ARRIVAL}", trip["url"])
        self.assertIn(f"departure_date={TRIP_DEPARTURE}", trip["url"])
        self.assertEqual(len([l for l in labels if l.endswith("(1 night)")]), 7)
        for b in ven["bookingLinks"]:
            self.assertTrue(b["url"].startswith("https://www.venetianlasvegas.com/booking?"))

    def test_trip_cost_model_quotes_the_dated_total(self):
        trip = DATA["trip"]
        self.assertEqual(trip["nights"], 7)
        self.assertEqual(trip["start"], TRIP_ARRIVAL)
        self.assertEqual(trip["end"], TRIP_DEPARTURE)
        self.assertEqual(trip["lodgingTotalAllIn"], EXPECTED_TOTAL)
        self.assertEqual(trip["nightlyObservedAverage"], 572.94)
        self.assertEqual(trip["nightlyBudget"], 197.28)
        self.assertEqual(trip["lodgingTotalBeforeTax"], 3537.25)
        self.assertIn("checkout total of $4,010.55", trip.get("lodgingEvidence", ""))

    def test_flags_note_the_dated_total_and_keep_the_superseded_history(self):
        by_id = {f["id"]: f for f in DATA["flags"]}
        f15, f36 = by_id["F15"], by_id["F36"]
        self.assertTrue(f15["title"].startswith("RESOLVED 2026-11-17"))
        self.assertIn("checkout total", f15["title"])
        self.assertIn("4,010.55", f15["title"] + f15["detail"])
        # F36 keeps its superseded `$XXX` wording so the change stays auditable, but must
        # now record that the engine did print a total (the schema test pins `$XXX` here).
        self.assertIn("$XXX", f36["title"])
        self.assertIn("4,010.55", f36["title"] + f36["detail"])
        # The open fee question stays open (F51), with the resort-fee page as evidence.
        f51 = by_id["F51"]
        self.assertIn("resort-fee page", f51["detail"])

    def test_no_computed_figure_is_stored_as_a_booking_price(self):
        ven, _ = trip_quote()
        price_fields = [str(v) for k, v in ven.items() if "price" in k.lower()]
        blob = json.dumps(price_fields)
        self.assertNotIn("4010.55", blob.replace(",", ""))
        self.assertNotIn("per night all-in", blob)

    def test_calendar_cells_are_not_the_quote(self):
        by_id = {f["id"]: f for f in DATA["flags"]}
        f69 = by_id["F69"]
        self.assertIn("not the quote", f69["title"])
        self.assertIn("cells", (f69["title"] + f69["detail"]).lower())


if __name__ == "__main__":
    unittest.main()
