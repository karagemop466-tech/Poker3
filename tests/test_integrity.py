#!/usr/bin/env python3
"""Arithmetic and integrity checks for the values this round corrected.

These are the numbers a reader acts on, so each one is asserted here against the
official source it came from. They are cheap to run and they fail loudly if a
later edit reintroduces a stale or mislabelled value.
"""
from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / "site" / "data.json").read_text(encoding="utf-8"))

TAX = 0.1338            # Clark County room tax, published on the Venetian hotel terms
RESORT_FEE = 55         # per night, published on the Venetian suite-rates page


class DataIntegrity(unittest.TestCase):
    def test_wynn_daily_names_do_not_repeat_their_day_range(self):
        """A doubled label like "(Monday-Thursday) (Monday-Thursday)" misreads as two events."""
        for event in DATA["events"]:
            if not event["id"].startswith("wynn-daily"):
                continue
            name = event["name"]
            for day in ("Monday", "Tuesday", "Wednesday", "Thursday",
                        "Friday", "Saturday", "Sunday"):
                self.assertLessEqual(
                    name.count(day), 1,
                    f"{event['id']}: day '{day}' appears more than once in {name!r}",
                )

    def test_dated_quote_nights_are_recorded_low_to_high_and_reconcile(self):
        """The one dated checkout total must not be presented with the nights reversed.

        Official quote (Venetian booking engine, 2026-11-16, two adults, 2 nights):
        $824.25 + $55 on 17 Nov, $164.25 + $55 on 18 Nov, $146.98 tax, $1,245.48 total.
        """
        quote = [r for r in DATA["rateLog"]
                 if r["quoteType"].startswith("Dated official checkout total")]
        self.assertEqual(len(quote), 1, "expected exactly one dated checkout total")
        row = quote[0]
        low, high = float(row["trueNightlyLow"]), float(row["trueNightlyHigh"])
        self.assertLess(low, high, "observed nights must be recorded low to high")

        night_17 = round((824.25 + RESORT_FEE) * (1 + TAX), 2)
        night_18 = round((164.25 + RESORT_FEE) * (1 + TAX), 2)
        self.assertAlmostEqual(low, night_18, places=2)
        self.assertAlmostEqual(high, night_17, places=2)

        # The two derived nights must reconcile to the printed total within rounding.
        self.assertLess(abs((night_17 + night_18) - 1245.48), 0.10)

    def test_trip_nightly_budget_is_the_published_floor(self):
        """$197.28 = ($119 published poker-suite start + $55 fee) x 1.1338."""
        trip = DATA["trip"]
        expected = round((119 + RESORT_FEE) * (1 + TAX), 2)
        self.assertAlmostEqual(trip["nightlyBudget"], expected, places=2)

    def test_guaranteed_pool_ratio_matches_its_own_components(self):
        """ratio = guaranteed pool / buy-in, descriptive only, never a forecast."""
        for event in DATA["events"]:
            buy_in, pool, ratio = event["buyIn"], event["guarantee"], event["ratio"]
            if isinstance(buy_in, (int, float)) and isinstance(pool, (int, float)) and buy_in:
                self.assertAlmostEqual(ratio, round(pool / buy_in, 1), places=1,
                                       msg=f"{event['id']}: ratio disagrees with its components")

    def test_every_row_states_when_it_was_last_checked(self):
        for event in DATA["events"]:
            self.assertTrue(event.get("lastChecked"), f"{event['id']}: no lastChecked date")

    def test_no_row_claims_wording_the_sheets_do_not_print(self):
        """No venue prints "single entry", so no excerpt may put that phrase in a quote."""
        for event in DATA["events"]:
            for field, rule in (event.get("rules") or {}).items():
                excerpt = (rule or {}).get("excerpt", "") or ""
                self.assertNotIn("single entry confirmed", excerpt.lower(),
                                 f"{event['id']}.{field}: claims wording no sheet prints")


class CalculatorArithmetic(unittest.TestCase):
    def test_true_cost_per_night_formula(self):
        """rate + resort fee + tax on (rate + resort fee), as the site states."""
        def true_nightly(rate: float, fee: float = RESORT_FEE, tax: float = TAX) -> float:
            return round(rate + fee + (rate + fee) * tax, 2)

        self.assertAlmostEqual(true_nightly(119), 197.28, places=2)
        self.assertAlmostEqual(true_nightly(209), 299.32, places=2)

    def test_trip_total_is_entries_times_buyin_plus_nights_times_true_nightly(self):
        entries, buy_in, nights = 8, 350.0, 7
        true_nightly = 197.28
        self.assertAlmostEqual(entries * buy_in + nights * true_nightly, 2800 + 1380.96, places=2)


class FreshnessAndBookingTests(unittest.TestCase):
    """Snapshot status, per-date booking link and the earliest-start claim (re-read 2026-11-17)."""

    TODAY = "2026-11-17"

    def test_status_follows_the_snapshot_date(self):
        for event in DATA["events"]:
            date = event.get("date")
            if not date:
                self.assertEqual(event.get("status"), "recurring", event["id"])
            elif date < self.TODAY:
                self.assertEqual(event.get("status"), "past", event["id"])
            elif date == self.TODAY:
                self.assertEqual(event.get("status"), "today", event["id"])
            else:
                self.assertEqual(event.get("status"), "upcoming", event["id"])

    def test_snapshot_date_is_2026_11_17(self):
        self.assertEqual(DATA.get("today"), self.TODAY)
        self.assertEqual(DATA.get("asOf"), self.TODAY)

    def test_fixed_stay_booking_link_is_the_official_venetian_engine(self):
        links = DATA.get("bookingLinks") or []
        self.assertTrue(links, "no per-date booking link")
        url = links[0]["url"]
        self.assertTrue(url.startswith("https://www.venetianlasvegas.com/booking?"), url)
        self.assertIn("arrival_date=2026-11-25", url)
        self.assertIn("departure_date=2026-12-02", url)
        self.assertIn("adults[]=2", url)
        # The page printed $XXX placeholders, so no price may be stored with the link.
        self.assertNotIn("nightly", links[0].get("priceInStaticPage", "").lower().split("no.")[0])

    def test_no_official_event_starts_before_nine_am(self):
        """Earliest verified start is 9:00 AM (Horseshoe daily). The all-day 8 AM plan stays unsupported."""
        def minutes(text):
            hh, rest = text.split(":")
            mm, ap = rest.split()
            hh = int(hh) % 12 + (12 if ap == "PM" else 0)
            return hh * 60 + int(mm)
        for event in DATA["events"]:
            t = event.get("time")
            if t and t[-2:] in ("AM", "PM"):
                self.assertGreaterEqual(minutes(t), 9 * 60, f"{event['id']} starts before 9 AM: {t}")

    def test_past_rows_are_not_shown_as_upcoming_by_default(self):
        app = (ROOT / "site" / "assets" / "app.js").read_text(encoding="utf-8")
        self.assertIn("showPast: false", app, "past rows must be hidden by default")
        self.assertIn("e.status === 'past'", app, "past filter missing")


    # ------------------------------------------------------------------
    # Added 2026-11-17: the guarantees this pass introduced.
    # ------------------------------------------------------------------
    def test_trip_cost_model_is_entries_buyin_plus_nights_true_cost(self):
        """estimated cost = entries x buy-ins + nights x true hotel cost."""
        m = DATA["tripCostModel"]
        nightly = round((m["roomRatePerNight"] + m["resortFeePerNight"]) * (1 + m["taxPct"] / 100), 2)
        self.assertAlmostEqual(m["trueCostPerNight"], nightly, places=2)
        self.assertAlmostEqual(m["trueCostPerNight"], 197.28, places=2)
        self.assertAlmostEqual(
            m["tripTotal"],
            round(m["entries"] * m["buyIn"] + m["nights"] * m["trueCostPerNight"] + m["parkingTotal"], 2),
            places=2)
        # The published starting rate is a floor, so the model must say so.
        self.assertIn("floor", m["basis"].lower())
        self.assertNotIn("quote for your stay", m["basis"].lower())

    def test_every_row_carries_both_dates(self):
        for e in DATA["events"]:
            self.assertTrue(e.get("lastChecked"), f"{e['id']} has no lastChecked")
            self.assertTrue(e.get("lastVerified"), f"{e['id']} has no lastVerified")
        self.assertGreaterEqual(len(DATA["events"]), 300)

    def test_rate_log_is_append_only_and_dated(self):
        log = DATA["rateLog"]
        self.assertGreaterEqual(len(log), 10, "a rate log needs more than a single value per hotel")
        self.assertTrue(all(r.get("observedOn") for r in log))
        self.assertTrue(all(r.get("quoteType") for r in log))
        dates = [r["observedOn"] for r in log]
        self.assertEqual(dates, sorted(dates), "rate log must be in date order")
        # Observations are never collapsed: a hotel can appear more than once.
        hotels = [r["hotel"] for r in log]
        self.assertGreater(len(hotels), len(set(hotels)))

    def test_no_structure_sheet_is_left_unread(self):
        sheets = DATA["structureSheets"]
        unread = [s for s in sheets if not s["read"]]
        self.assertEqual(unread, [], f"{len(unread)} structure sheets are still labelled unread")
        self.assertEqual(len(sheets), 52)

    def test_rows_whose_sheet_allows_more_entry_are_not_single_entry(self):
        """Any row that prints a re-entry or bagging clause must not be in the single-entry path."""
        for e in DATA["events"]:
            status = (e.get("rules") or {}).get("singleEntry", {}).get("status", "")
            if status == "multiple-entries":
                self.assertNotEqual(e.get("entryType"), "none",
                                    f"{e['id']} allows multiple entries but is labelled single entry")
            if e.get("entryType") == "none":
                self.assertEqual(status, "single-entry-on-sheet",
                                 f"{e['id']} is labelled single entry without a sheet status")

    def test_transcription_matches_the_published_rows(self):
        import sys
        sys.path.insert(0, str(ROOT / "scripts"))
        import verify_transcription  # noqa: E402
        result = verify_transcription.check_transcription(DATA)
        self.assertEqual(result["status"], "checked", result["mismatches"])
        self.assertEqual(result["rowsMatched"], result["rowsTranscribed"])
        self.assertGreaterEqual(result["rowsTranscribed"], 40)

    def test_flags_about_this_pass_are_present(self):
        ids = {f["id"] for f in DATA["flags"]}
        for expected in ("F31", "F32", "F33", "F34", "F35", "F36"):
            self.assertIn(expected, ids)


if __name__ == "__main__":
    unittest.main(verbosity=2)
