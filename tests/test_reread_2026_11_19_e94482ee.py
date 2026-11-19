"""Guards for the 2026-11-19 live re-read performed by session arena/e94482ee-poker3.

What was actually read live on 2026-11-19, and what each test below pins:

  * the Venetian DeepStack Extravaganza IV schedule page (all four chunks) — the 19 rows inside the
    trip window 2026-11-23 … 2026-11-30;
  * the eleven structure sheets those rows link (1, 2, 3, 5, 6, 7, 8, 11, 22, 26, 30), read in full;
  * the Wynn WPT World Championship schedule PDF — the 13 rows inside the same window;
  * the Venetian hotel terms, resort-fee, poker-suite-rate and poker-parking pages;
  * the Venetian booking engine for 2 adults, 23-30 Nov 2026, which printed a full itemised total
    ($3,619.39) after earlier reads the same day had returned only a loading shell;
  * the Wynn resort-information and parking pages, and caesars.com/parking.

No tournament, hotel, fee, guarantee or route VALUE changed in that pass. What changed is that:
  * the second dated quote is published beside the first (flag F110);
  * F93 is corrected to "partially resolved", because a later read the same day disproved its claim;
  * the eleven sheets' re-read date is recorded on every rule panel (`rechecked`) without overwriting
    the original read date (`retrieved`), so a reader is not told a 2026-11-16 read was made today;
  * Wynn's registered-guest parking is published as the $0 the property prints.
"""
from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / "site" / "data.json").read_text(encoding="utf-8"))
PAGE = (ROOT / "site" / "hotels.html").read_text(encoding="utf-8")
CALC = (ROOT / "site" / "calculator.html").read_text(encoding="utf-8")
INDEX = (ROOT / "site" / "index.html").read_text(encoding="utf-8")
APP = (ROOT / "site" / "assets" / "app.js").read_text(encoding="utf-8")

TRIP = [e for e in DATA["events"] if "2026-11-23" <= e["date"] <= "2026-11-30"]
VENETIAN_SHEETS = {1, 2, 3, 5, 6, 7, 8, 11, 22, 26, 30}


def sheet_number(event):
    url = event.get("sheetUrl") or ""
    stem = url.rsplit("_", 1)[-1].split(".")[0]
    return int(stem) if stem.isdigit() else None


class SecondDatedQuote(unittest.TestCase):
    """The 2026-11-19 booking-engine read, published beside — never instead of — the 2026-11-17 read."""

    def setUp(self):
        self.model = DATA["tripCostModel"]
        self.later = self.model["liveQuote"]["laterRead"]

    def test_both_reads_are_kept(self):
        self.assertAlmostEqual(self.model["liveQuote"]["checkoutTotal"], 4010.55, places=2)
        self.assertEqual(self.model["liveQuote"]["quoteDate"], "2026-11-17")
        self.assertAlmostEqual(self.later["checkoutTotal"], 3619.39, places=2)
        self.assertEqual(self.later["quoteDate"], "2026-11-19")
        dates = {r["observedOn"] for r in DATA["rateLog"] if r["hotel"] in ("venetian", "palazzo")}
        self.assertTrue({"2026-11-16", "2026-11-17", "2026-11-19"} <= dates,
                        "the rate log must keep every dated observation, not only the newest")

    def test_printed_parts_add_to_the_printed_total(self):
        self.assertAlmostEqual(sum(self.later["nightlyRates"]), 2807.25, places=2)
        self.assertEqual(len(self.later["nightlyRates"]), 7)
        self.assertAlmostEqual(self.later["resortFeeTotal"], 385.00, places=2)
        self.assertAlmostEqual(self.later["preTaxSubtotal"], 3192.25, places=2)
        self.assertAlmostEqual(self.later["preTaxSubtotal"] + self.later["taxTotal"],
                               self.later["checkoutTotal"], places=2)

    def test_tax_discrepancy_is_published_not_smoothed(self):
        """13.38% of the printed pre-tax subtotal is 2 cents below the printed tax; the record says so."""
        self.assertAlmostEqual(self.later["taxExpected"], 427.12, places=2)
        self.assertAlmostEqual(self.later["taxDifference"], 0.02, places=2)
        self.assertIn("two cents", DATA["tripCostModel"]["liveQuote"]["laterRead"]["note"])

    def test_all_in_per_night_is_the_printed_total_over_the_nights(self):
        self.assertAlmostEqual(self.later["allInPerNight"], round(3619.39 / 7, 2), places=2)
        self.assertAlmostEqual(self.later["allInPerNight"], 517.06, places=2)
        # The printed Average Rate includes the resort fee and excludes tax, so it must not be
        # presented as the all-in figure.
        self.assertTrue(self.later["averageRateIncludesFee"])
        self.assertNotAlmostEqual(self.later["printedAverageRate"], self.later["allInPerNight"], places=2)

    def test_every_page_that_quotes_a_total_quotes_both(self):
        for name, page in (("hotels", PAGE), ("calculator", CALC), ("index", INDEX)):
            self.assertIn("4,010.55", page, f"{name} lost the 2026-11-17 total")
            self.assertIn("3,619.39", page, f"{name} lost the 2026-11-19 total")
        self.assertIn("laterRead", CALC)

    def test_flag_f93_no_longer_claims_no_total_exists(self):
        f93 = next(f for f in DATA["flags"] if f["id"] == "F93")
        self.assertIn("Partially resolved", f93["title"])
        self.assertIn("3,619.39", f93["detail"])
        f107 = next(f for f in DATA["flags"] if f["id"] == "F110")
        self.assertIn("3,619.39", f107["detail"])
        self.assertEqual(f107["source"], self.later["source"])


class StructureSheetReRead(unittest.TestCase):
    """The eleven sheets behind the trip window were re-read on 2026-11-19; the date is on every rule panel."""

    def test_every_trip_row_records_the_reread_date_without_back_dating_the_read(self):
        checked = 0
        for event in TRIP:
            if event["venue"] != "venetian":
                continue
            if sheet_number(event) not in VENETIAN_SHEETS:
                continue
            for name, rule in event["rules"].items():
                if not isinstance(rule, dict) or not rule.get("source", "").endswith(".pdf"):
                    continue
                self.assertEqual(rule.get("rechecked"), "2026-11-19",
                                 f"{event['id']} {name}: no 2026-11-19 re-read recorded")
                self.assertIn(rule.get("retrieved"), ("2026-11-16", "2026-11-19"),
                              f"{event['id']} {name}: the original read date was overwritten")
                checked += 1
        self.assertGreater(checked, 40, "expected every rule panel on the eleven sheets to be covered")

    def test_printed_fee_split_and_clause_per_sheet(self):
        """One representative row per sheet: the printed fee must equal rake/buy-in exactly as published."""
        expected = {
            1: ("$40 of the $200", 200, 8000),
            5: ("$58 of the $300", 300, 10000),
            6: ("$65 of the $400", 400, 15000),
            7: ("$90 of the $600", 600, 30000),
            11: ("$90 of the $600", 600, 30000),
            22: ("$58 of the $300", 300, 10000),
            26: ("$60 of the $400", 400, 15000),
            30: ("$40 of the $200", 200, 8000),
            2: ("$70 of the $400", 400, 75000),
            3: ("$70 of the $400", 400, 75000),
            8: ("$40 of the $200", 200, 20000),
        }
        seen = set()
        for event in TRIP:
            n = sheet_number(event)
            if event["venue"] != "venetian" or n not in expected or n in seen:
                continue
            seen.add(n)
            prefix, buy_in, guarantee = expected[n]
            self.assertTrue(event["rules"]["fee"]["excerpt"].startswith(prefix),
                            f"{event['id']}: printed fee is not {prefix!r}")
            self.assertEqual(event["buyIn"], buy_in, event["id"])
            self.assertEqual(event["guarantee"], guarantee, event["id"])
        self.assertEqual(seen, VENETIAN_SHEETS, "a sheet behind the trip window is not represented")

    def test_the_multi_entry_sheets_are_not_labelled_single_entry(self):
        """Sheets 2, 3 and 8 print extra-entry wording; their rows must stay out of the single-entry set."""
        for event in TRIP:
            if sheet_number(event) in (2, 3, 8) and event["venue"] == "venetian":
                self.assertNotEqual(event["rules"]["singleEntry"]["status"], "single-entry-on-sheet",
                                    f"{event['id']} is on a sheet that prints extra-entry wording")
                self.assertFalse(event["singleEntry"], event["id"])

    def test_no_row_claims_a_written_one_entry_confirmation(self):
        """52 rows are sheet-screened only (F31). None may be promoted to confirmed by this pass."""
        self.assertEqual(sum(e.get("entryType") == "single-entry-confirmed" for e in DATA["events"]), 0)
        screened = [e for e in DATA["events"]
                    if e["rules"]["singleEntry"]["status"] == "single-entry-on-sheet"]
        self.assertEqual(len(screened), 52)


class HotelFactsReRead(unittest.TestCase):
    def test_wynn_registered_guest_parking_is_a_published_zero(self):
        wynn = next(h for h in DATA["hotels"] if h["id"] == "wynn")
        self.assertEqual(wynn["parkingPerNight"], 0.0)
        self.assertIn("complimentary parking for all Wynn and Encore Resort and Tower Suite registered guests",
                      wynn["parking"])
        self.assertIn("$25", wynn["parking"], "the unregistered-guest rate must stay beside the waived one")

    def test_venetian_terms_values_are_unchanged(self):
        venetian = next(h for h in DATA["hotels"] if h["id"] == "venetian")
        self.assertEqual(venetian["resortFee"], 55)
        self.assertEqual(venetian["parkingPerNight"], 20.0)
        self.assertIn("13.38%", venetian["cancellation"] + json.dumps(venetian.get("taxNote", "")))
        model = DATA["tripCostModel"]
        self.assertEqual(model["taxPct"], 13.38)
        self.assertEqual(model["resortFeePerNight"], 55.0)
        self.assertEqual(model["parkingPerNight"], 20.0)

    def test_the_rate_log_renderer_shows_every_night_and_an_all_in_figure(self):
        self.assertIn("Printed room rates per night", APP)
        self.assertIn("All-in per night", APP)
        self.assertIn("nightlyRates", APP)


if __name__ == "__main__":
    unittest.main()
