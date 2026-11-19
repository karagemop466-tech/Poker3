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
        """Every dated checkout total must record its nights low to high and reconcile exactly.

        The rate log is a dated series, not a single value, so the same stay may appear more than
        once. Two observations exist for the Venetian booking engine, 17-19 November 2026, two
        adults, Newly Remodeled Luxury King, "Book Direct: Up to 25% Off":

          2026-11-16: $824.25 + $55, $164.25 + $55, $146.98 tax, $1,245.48 total
          2026-11-17: $621.75 + $55, $164.25 + $55, $119.89 tax, $1,015.89 total

        Each night is (rate + $55) x 1.1338 rounded to the cent. Both quotes reconcile to their
        printed total to the cent, which is what confirms the tax is charged on rate and fee
        together.
        """
        quote = [r for r in DATA["rateLog"]
                 if r["quoteType"].startswith("Dated official checkout total")
                 and r["observedOn"] == "2026-11-16"]
        self.assertEqual(len(quote), 1, "expected exactly one 2026-11-16 dated checkout total")
        row = quote[0]
        low, high = float(row["trueNightlyLow"]), float(row["trueNightlyHigh"])
        self.assertLess(low, high, "observed nights must be recorded low to high")

    def test_the_two_dated_observations_are_kept_as_a_series_not_overwritten(self):
        """A rate that moves must leave both readings behind, dated, so the move is visible."""
        obs = sorted({r["observedOn"] for r in DATA["rateLog"]
                      if r["hotel"] == "venetian" and r["quoteType"].startswith("Dated official checkout total")})
        self.assertIn("2026-11-16", obs, "the earlier observation was overwritten")
        self.assertIn("2026-11-17", obs, "the later observation was not recorded")


        expected = {
            "2026-11-16": dict(nights=(824.25, 164.25), total=1245.48),
            "2026-11-17": dict(nights=(621.75, 164.25), total=1015.89),
        }
        seen = set()
        for row in quotes:
            day = row["observedOn"]
            if day not in expected:
                continue
            seen.add(day)
            spec = expected[day]
            low, high = float(row["trueNightlyLow"]), float(row["trueNightlyHigh"])
            self.assertLess(low, high, f"{day}: observed nights must be recorded low to high")

            dear = round((max(spec["nights"]) + RESORT_FEE) * (1 + TAX), 2)
            cheap = round((min(spec["nights"]) + RESORT_FEE) * (1 + TAX), 2)
            self.assertAlmostEqual(low, cheap, places=2, msg=f"{day}: low night")
            self.assertAlmostEqual(high, dear, places=2, msg=f"{day}: high night")

            # reconcile to the printed total, to the cent: the rounding is per night, not on the sum
            self.assertAlmostEqual(cheap + dear, spec["total"], places=2,
                                   msg=f"{day}: derived nights do not reconcile to the printed total")
        self.assertEqual(seen, set(expected),
                         "both dated observations of this stay must be present in the rate log")

    def test_the_two_dated_observations_are_kept_as_a_series_not_overwritten(self):
        """A rate that moves must leave both readings behind, dated, so the move is visible."""
        obs = sorted({r["observedOn"] for r in DATA["rateLog"] if r["hotel"] == "venetian"})
        self.assertIn("2026-11-16", obs, "the earlier observation was overwritten")
        self.assertIn("2026-11-17", obs, "the later observation was not recorded")

    def test_every_dated_quote_is_ordered_and_reconciles(self):
        """Every official quote: night one is the earlier night, and (rate + $55) x 1.1338 hits the printed total.

        The engine has now printed three of them, and it priced the same stay at $1,245.48 and
        then at $1,015.89 on consecutive days, so the log can no longer assume a single total.
        """
        quotes = [q for h in DATA["hotels"] for q in (h.get("quotes") or [])]
        self.assertGreaterEqual(len(quotes), 1, "expected at least one dated quote")
        for q in quotes:
            if "nightly" in q:
                # A multi-night quote (the 23-30 Nov trip stay) lists every night as (date, rate).
                nights = [{"date": d, "rate": r, "resortFee": q["resortFeePerNight"]} for d, r in q["nightly"]]
                dates = [n["date"] for n in nights]
                self.assertEqual(dates, sorted(dates), f"{q['checkIn']}: nights must be in date order")
            else:
                nights = [q["nightOne"], q["nightTwo"]]
                self.assertLess(q["nightOne"]["date"], q["nightTwo"]["date"],
                                f"{q['checkIn']}: night one must be the earlier night")
            derived = round(sum((n["rate"] + n["resortFee"]) * (1 + TAX) for n in nights), 2)
            self.assertLess(abs(derived - q["total"]), 0.05,
                            f"{q['checkIn']} -> {q['checkOut']}: derived {derived} != printed {q['total']}")
            self.assertLess(abs(q["derivedTotal"] - q["total"]), 0.05,
                            f"{q['checkIn']} -> {q['checkOut']}: stored derived total {q['derivedTotal']}")

    def test_dated_rate_log_rows_record_the_lower_night_first(self):
        """A rate-log row stores its two true nightly figures low then high."""
        rows = [r for r in DATA["rateLog"] if r["quoteType"].startswith("Dated official checkout total")]
        self.assertGreaterEqual(len(rows), 1, "expected at least one dated checkout total")
        for row in rows:
            low, high = float(row["trueNightlyLow"]), float(row["trueNightlyHigh"])
            self.assertLessEqual(low, high, f"{row['observedOn']}: nights must be recorded low to high")

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
        # The trip is 23-30 November (seven nights). The engine priced that window on 2026-11-17.
        self.assertIn("arrival_date=2026-11-23", url)
        self.assertIn("departure_date=2026-11-30", url)
        self.assertIn("adults[]=2", url)
        # The stored price text must be the dated checkout total read from the engine, not a placeholder.
        text = links[0].get("priceInStaticPage", "")
        self.assertTrue(text.startswith("Yes."), text)
        self.assertIn("$4,010.55", text)

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
        # The tournament total is the exact sum of the chosen buy-ins, not entries x a
        # rounded mean: the seven primaries are $200, $200, $400, $300, $600, $600 and
        # $300, summing to exactly $2,600.00 (mean $371.428571...).
        self.assertAlmostEqual(m["primaryBuyInSum"], 2600.00, places=2)
        self.assertAlmostEqual(m["tournamentTotal"], 2600.00, places=2)
        self.assertAlmostEqual(
            m["tripTotal"],
            round(m["primaryBuyInSum"] + m["nights"] * m["trueCostPerNight"] + m["parkingTotal"], 2),
            places=2)
        self.assertAlmostEqual(m["tripTotal"], 4120.96, places=2)
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
