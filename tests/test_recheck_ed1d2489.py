"""Pins the published dashboard to the independent 2026-11-17 re-read.

Record: research/recheck_2026-11-17_ed1d2489.json (session arena/ed1d2489-poker3).
Every value in that record was read from the venue's own host on 2026-11-17: all four
chunks of the official DeepStack Extravaganza IV schedule, the eight structure PDFs the
day plan relies on, the Venetian poker-suite rate page, the resort-fee page, the hotel
terms and conditions, and the Wynn resort policy page.

These tests fail if a published value drifts from the record, or if a claim is published
that the record does not support. They never fetch anything; the record is the artefact.
"""
import json
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
REC = json.loads((ROOT / "research" / "recheck_2026-11-17_ed1d2489.json").read_text(encoding="utf-8"))
DATA = json.loads((ROOT / "site" / "data.json").read_text(encoding="utf-8"))
TRIP = DATA["trip"]

EVENTS = {e["id"]: e for e in DATA["events"]}
FLAGS = {f["id"]: f for f in DATA["flags"]}
HOTELS = {h["id"]: h for h in DATA["hotels"]}
SHEETS = REC["sheetsReadThisPass"]


def ids_for(date, event):
    """Published ids for one official event number on one date (the time suffix varies)."""
    matches = []
    for i in EVENTS:
        parts = i.split("-")
        # id shape: vl-dse-<yyyy>-<mm>-<dd>-<event number>-<time>  (so parts[4] is the event number)
        if len(parts) < 7:
            continue
        if "-".join(parts[2:5]) == date and parts[5] == str(event):
            matches.append(i)
    return matches


def norm(text):
    """Whitespace- and spacing-insensitive comparison of a printed line.

    The PDF text layer prints '~ 4:55 PM' and '~4:55 PM' in different sheets for the same
    line, so spacing is normalised. Nothing else is: every digit, word and symbol is compared.
    """
    return re.sub(r"\s+", "", str(text)).lower()


class ScheduleRows(unittest.TestCase):
    def test_every_re_read_row_is_published(self):
        for row in REC["rows"]:
            with self.subTest(date=row["date"], event=row["event"]):
                self.assertTrue(ids_for(row["date"], row["event"]),
                                "row re-read from the official schedule is missing from the site")

    def test_rows_match_the_official_schedule(self):
        for row in REC["rows"]:
            with self.subTest(date=row["date"], event=row["event"]):
                found = [EVENTS[i] for i in ids_for(row["date"], row["event"])]
                match = [e for e in found if e["time"] == row["time"]]
                self.assertEqual(len(match), 1, "no single published row with the printed start time")
                e = match[0]
                self.assertEqual(e["date"], row["date"])
                self.assertEqual(e["buyIn"], row["buyIn"])
                self.assertEqual(e["guarantee"], row["guarantee"])
                self.assertTrue(e["name"].startswith(f"${row['buyIn']:,}".replace(",", ",")),
                                "published name does not begin with the printed buy-in")
                self.assertTrue(e["structureUrl"].endswith(f"structure_{row['sheet']}.pdf"),
                                "published row does not link the sheet the schedule page links")

    def test_trip_window_is_the_window_the_record_covers(self):
        """The record covers 25 Nov - 2 Dec; the trip ends on 30 Nov because 30 Nov and 1 Dec
        print no figure on the official booking calendar in any reading (F57), so a stay
        spanning them cannot be booked online. Every day in the trip must still be playable."""
        self.assertEqual(TRIP["start"], "2026-11-23")
        self.assertEqual(TRIP["end"], "2026-11-30")
        # The record's own rows for 1 and 2 December are outside the trip by the same finding.
        dates = {r["date"] for r in REC["rows"]}
        self.assertEqual(len([d for d in dates if TRIP["start"] <= d <= TRIP["playableEnd"]]), 5)
        self.assertIn("F57", FLAGS, "the unavailability finding behind this window must be published")

    def test_the_day_plan_covers_the_playable_days_and_no_more(self):
        """Check-in day through the day before check-out; the check-out day is not playable."""
        planned = [d["date"] for d in DATA["dayPlan"]]
        self.assertEqual(len(planned), int(TRIP["days"]))
        self.assertEqual(planned[0], TRIP["start"])
        self.assertTrue(all(d < TRIP["end"] for d in planned),
                        "the day plan includes the check-out date, which is not playable")


class StructureSheets(unittest.TestCase):
    def test_fee_line_chip_count_and_late_registration_match(self):
        for number, sheet in SHEETS.items():
            with self.subTest(sheet=number):
                url = f"dse_nov_2026-structure_{number}.pdf"
                rows = [e for e in DATA["events"] if e["venue"] == "venetian" and e["structureUrl"].endswith(url)]
                self.assertTrue(rows, f"no published row links sheet {number}")
                for e in rows:
                    self.assertEqual(e["rules"]["fee"]["excerpt"], sheet["feeLine"])
                    self.assertEqual(e["chips"], sheet["startingChips"])
                    self.assertEqual(e["levelMin"], sheet["levelMinutes"])
                    self.assertEqual(norm(e["lateReg"]), norm(sheet["lateRegistration"]))
                    self.assertEqual(e["rules"]["fee"]["status"], "confirmed")

    def test_guarantee_per_event_number(self):
        for number, sheet in SHEETS.items():
            by_event = sheet.get("guaranteeByEvent")
            if not by_event:
                continue
            with self.subTest(sheet=number):
                for event_no, printed in by_event.items():
                    rows = [EVENTS[i] for i in EVENTS
                            if EVENTS[i]["venue"] == "venetian"
                            and EVENTS[i]["structureUrl"].endswith(f"dse_nov_2026-structure_{number}.pdf")
                            and i.split("-")[5] == str(int(event_no))]
                    self.assertTrue(rows, f"event {event_no} on sheet {number} is not published")
                    for e in rows:
                        self.assertEqual(e["guarantee"], printed,
                                         f"event {event_no} guarantee does not match sheet {number}")

    def test_no_extra_entry_term_is_attributed_to_a_sheet_that_prints_none(self):
        for number, sheet in SHEETS.items():
            with self.subTest(sheet=number):
                self.assertFalse(sheet["reEntryPrinted"] or sheet["rebuyPrinted"] or sheet["addOnPrinted"])
                self.assertFalse(sheet["maxEntriesPrinted"])
                rows = [e for e in DATA["events"]
                        if e["venue"] == "venetian" and e["structureUrl"].endswith(f"dse_nov_2026-structure_{number}.pdf")]
                for e in rows:
                    self.assertEqual(e["rules"]["reEntry"]["status"], "none-printed")
                    self.assertEqual(e["rules"]["addOn"]["status"], "none-printed")
                    # "none-printed" is a document screen, never written confirmation (F31).
                    self.assertEqual(e["rules"]["singleEntry"]["status"], "single-entry-on-sheet")

    def test_no_row_claims_written_confirmation_of_one_entry(self):
        confirmed = [e["id"] for e in DATA["events"]
                     if (e["rules"].get("singleEntry") or {}).get("status") == "confirmed"
                     or (e["rules"].get("singleEntry") or {}).get("maxEntries") == 1]
        self.assertEqual(confirmed, [], "a row claims written confirmation of a one-entry cap that no source prints")

    def test_seniors_eligibility_is_quoted_from_the_sheet(self):
        sheet = SHEETS["17"]
        self.assertIn("50+", sheet["eligibility"])
        rows = [e for e in DATA["events"] if e["structureUrl"].endswith("dse_nov_2026-structure_17.pdf")]
        self.assertTrue(rows)
        for e in rows:
            self.assertIn("50+", e["eligibility"])


class HotelFacts(unittest.TestCase):
    def setUp(self):
        self.hotel = HOTELS["venetian"]
        self.rec = REC["hotel"]

    def test_published_components(self):
        self.assertEqual(self.hotel["baseRateFloor"], self.rec["publishedStartingRates"][0])
        self.assertEqual(self.hotel["baseRateCeiling"], self.rec["publishedStartingRates"][1])
        self.assertEqual(self.hotel["resortFee"], self.rec["resortFee"])
        self.assertEqual(self.hotel["taxRate"], self.rec["taxPct"])
        self.assertEqual(self.hotel["parkingPerNight"], self.rec["parkingPerNight"])
        self.assertIn(str(int(self.rec["incidentalPerNight"])), self.hotel["incidental"])
        self.assertIn(str(int(self.rec["incidentalPerNight"])), self.rec["incidentalExcerpt"])
        self.assertEqual(self.hotel["qualification"] and "EPOKR25" in self.hotel["qualification"], True)

    def test_true_nightly_cost_is_the_recorded_arithmetic(self):
        for rate, expected in ((self.rec["publishedStartingRates"][0], self.rec["trueNightlyFloor118"]),
                               (self.rec["publishedStartingRates"][1], self.rec["trueNightlyCeiling209"])):
            with self.subTest(rate=rate):
                computed = round((rate + self.rec["resortFee"]) * (1 + self.rec["taxPct"] / 100), 2)
                self.assertAlmostEqual(computed, expected, places=2)
        self.assertAlmostEqual(self.hotel["trueNightlyLow"], self.rec["trueNightlyFloor118"], places=2)
        self.assertAlmostEqual(self.hotel["trueNightlyHigh"], self.rec["trueNightlyCeiling209"], places=2)

    def test_no_dated_total_is_invented_for_the_trip_window(self):
        # The 2026-11-17 record above was written at an earlier read, for the then-trip window (25 Nov - 2 Dec).
        self.assertEqual(self.rec["datedCheckoutTotalForTripWindow"], "")
        # A later read on the same day priced the 23-30 Nov trip stay. The stored total must be exactly the printed one,
        # and it must be the rate-log entry for the same stay (not a figure derived from calendar cells).
        booking = DATA["bookingLinks"][0]
        self.assertIn("$4,010.55", booking["priceInStaticPage"])
        self.assertIn("arrival_date=2026-11-23", booking["url"])
        logged = [r for r in DATA["rateLog"] if r.get("quoteType", "").startswith("Dated official checkout total (2 adults, 7 nights")]
        # Two distinct official reads of the identical window are logged on 2026-11-17: the ~21:54 UTC
        # venetian-suite read ($4,010.55) and the ~22:15 UTC palazzo-suite read ($3,823.46, flag F78).
        # Both must be present, each with its own printed total; neither may duplicate or replace the other.
        self.assertEqual(len(logged), 2, "two distinct dated 7-night trip reads are logged")
        # Identify each read by its suite label, not by a dollar figure: each note cites the other's total
        # for comparison, so a money filter would match both rows.
        first = next((r for r in logged if "palazzo" not in r.get("quoteType", "").lower()), None)
        second = next((r for r in logged if "palazzo" in r.get("quoteType", "").lower()), None)
        self.assertIsNotNone(first, "the 21:54 UTC read ($4,010.55) must stay in the log")
        self.assertIsNotNone(second, "the 22:15 UTC read ($3,823.46) must be logged beside it")
        self.assertIn("4010.55", first["note"].replace(",", ""))
        self.assertIn("3823.46", second["note"].replace(",", ""))
        self.assertEqual(first["observedOn"], "2026-11-17")
        self.assertEqual(second["observedOn"], "2026-11-17")
        self.assertNotEqual(first.get("nightlyRates"), second.get("nightlyRates"),
                            "the two reads printed different nightly rates and must stay distinct")

    def test_every_hotel_fact_links_the_recorded_source(self):
        self.assertEqual(self.hotel["source"], self.rec["sources"]["pokerSuiteRate"])
        self.assertEqual(self.hotel["feeSource"], self.rec["sources"]["resortFee"])
        self.assertEqual(self.hotel["taxSource"], self.rec["sources"]["terms"])
        self.assertEqual(self.hotel["parkingSource"], self.rec["sources"]["terms"])


class WynnTerms(unittest.TestCase):
    def test_wynn_fee_and_check_in_match_the_live_policy_page(self):
        rec = REC["wynnResortTerms"]
        self.assertEqual(HOTELS["wynn"]["resortFee"], rec["resortFee"])
        self.assertEqual(rec["taxPct"], "", "the page prints no tax percentage; it must stay blank (F39)")
        self.assertEqual(HOTELS["wynn"]["taxRate"], "")
        self.assertEqual(HOTELS["wynn"]["source"], "https://www.wynnlasvegas.com/rooms-and-suites")
        self.assertEqual(HOTELS["wynn"]["feeSource"], rec["url"])


class PublishedClaims(unittest.TestCase):
    """Claims checked in prose and on the pages must match the record."""

    def text(self, *paths):
        blob = ""
        for rel in paths:
            blob += (ROOT / rel).read_text(encoding="utf-8")
        return blob

    def test_sheet_screened_count_matches_the_data(self):
        count = len([e for e in DATA["events"] if e["rules"]["singleEntry"]["status"] == "single-entry-on-sheet"])
        self.assertEqual(count, 52)
        self.assertNotIn("The 45 sheet-screened", self.text("site/tournaments.html"))
        self.assertIn("The 52 sheet-screened", self.text("site/tournaments.html"))
        self.assertIn("The 52 Venetian rows", json.dumps(FLAGS["F31"]))

    def test_flag_ids_are_unique_and_every_reference_resolves(self):
        ids = [f["id"] for f in DATA["flags"]]
        self.assertEqual(len(ids), len(set(ids)), "duplicate flag id")
        json_blob = json.dumps({k: DATA[k] for k in ("questions", "suggestions", "trip", "planNotes")})
        for rel in ("site/index.html", "site/tournaments.html", "site/schedule.html", "site/assets/app.js"):
            json_blob += self.text(rel)
        for ref in set(re.findall(r"\bF(\d{2})\b", json_blob)):
            self.assertIn(f"F{ref}", FLAGS, f"page cites F{ref}, which is not a published flag")

    def test_entry_cap_citations_point_at_the_entry_cap_flag(self):
        self.assertIn("one-entry-per-player", FLAGS["F31"]["title"])
        for rel in ("site/assets/app.js",):
            text = self.text(rel)
            self.assertNotIn("unconfirmed (F29)", text)
            self.assertNotIn("flagged item F29", text)

    def test_no_page_still_says_the_nye_sheets_were_not_read(self):
        for rel in ("site/index.html", "README.md"):
            text = self.text(rel)
            self.assertNotIn("15 structure sheets were not read", text)
            self.assertNotIn("but its 15 structure sheets were not read", text)
        self.assertNotIn("not read, so those rows cannot enter", json.dumps(DATA["trip"]["rationale"]))
        self.assertNotIn("Its structure sheet has not been read", json.dumps(DATA["questions"]))

    def test_stale_notice_citation_points_at_the_bellagio_flag(self):
        q10 = [q for q in DATA["questions"] if q["id"] == "Q10"][0]
        self.assertIn("F03", q10["answer"])
        self.assertIn("undated", FLAGS["F03"]["title"])

    def test_pool_notes_never_call_a_bounty_guarantee_a_cash_pool(self):
        for day in DATA["dayPlan"]:
            for field, note_field in (("primary", "primaryGuaranteeNote"), ("fallback", "fallbackGuaranteeNote")):
                eid = day.get(field)
                if not eid:
                    continue
                e = EVENTS[eid]
                note = day.get(note_field, "")
                if e["kind"] == "bounty":
                    self.assertIn("bounties", note, f"{eid} prints a bounty-inclusive guarantee with no pool note")

    def test_page_counts_are_render_time_not_hand_typed(self):
        """A count written into the HTML drifts the moment a row is added; these are data-driven."""
        for rel, token in (("site/questions.html", "Seventeen"),
                           ("site/questions.html", "four questions"),
                           ("site/suggestions.html", "Twelve"),
                           ("site/suggestions.html", "Three of them")):
            with self.subTest(page=rel, token=token):
                self.assertNotIn(token, self.text(rel))
        self.assertIn("data-question-count", self.text("site/questions.html"))
        self.assertIn("data-suggestion-count", self.text("site/suggestions.html"))
        self.assertIn("data-blocking-count", self.text("site/questions.html"))
        self.assertGreater(len(DATA["questions"]), 0)
        self.assertGreater(len(DATA["suggestions"]), 0)

    def test_checks_workflow_can_actually_run_outside_the_cron(self):
        wf = self.text(".github/workflows/checks.yml")
        self.assertIn("workflow_dispatch:", wf)
        self.assertIn("push:", wf, "a cron-only job cannot be proven to run; a path-filtered push gives it a real run")
        self.assertIn("scripts/check_sources.py", wf)


if __name__ == "__main__":
    unittest.main()
