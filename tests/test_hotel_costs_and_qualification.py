"""Pins the 2026-11-17 hotel-cost closure and the per-night poker-rate result.

Written by session arena/191afa75-poker3 after reading the official Caesars property
booking pages and the Venetian poker-suite rate page.  Every assertion below is either
(a) a figure the property itself printed, (b) arithmetic on published figures, or
(c) a guarantee that this repository does not publish a number a property never printed.
"""
import json
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / "site" / "data.json").read_text(encoding="utf-8"))
HOTELS = {h["id"]: h for h in DATA["hotels"]}
PLAN = DATA["dayPlan"]
RATE_LOG = DATA["rateLog"]
FLAGS = {f["id"]: f for f in DATA["flags"]}


class HotelCostsFromOfficialPages(unittest.TestCase):
    def test_caesars_palace_fee_is_the_printed_pre_tax_figure(self):
        h = HOTELS["caesars"]
        self.assertEqual(h["resortFee"], 54.95)
        self.assertIn("$62.30 ($54.95 plus $7.35 tax)", h["resortFeeNote"])
        self.assertTrue(h["feeSource"].startswith("https://www.caesars.com/"))

    def test_horseshoe_fee_is_the_printed_pre_tax_figure(self):
        h = HOTELS["horseshoe"]
        self.assertEqual(h["resortFee"], 49.95)
        self.assertIn("$56.63 ($49.95 plus $6.68 tax)", h["resortFeeNote"])
        self.assertIn("$50 per day", h["incidental"])

    def test_no_property_publishes_a_tax_rate_that_is_not_shown_as_a_reference(self):
        """A taxRate may only be a figure the property printed; the county figure is a reference."""
        for h in DATA["hotels"]:
            if h["id"] in ("caesars", "horseshoe", "wynn", "bellagio"):
                self.assertEqual(h["taxRate"], "", f"{h['id']}: tax rate was invented")
            if h["taxRate"] == "":
                self.assertTrue(
                    any(phrase in h["taxNote"] for phrase in
                        ("does not print a room-tax percentage", "prints no room-tax percentage",
                         "without a percentage", "percentage is not printed",
                         "no room-tax percentage")),
                    f"{h['id']}: a blank tax rate must be explained as not printed by the property")

    def test_blank_true_cost_is_explained_by_a_status_note(self):
        for h in DATA["hotels"]:
            if not h.get("trueNightlyLow"):
                self.assertTrue(h.get("status"), f"{h['id']}: blank cost with no status note")

    def test_horseshoe_calendar_cells_are_logged_twice_because_they_moved(self):
        rows = [r for r in RATE_LOG if r["hotel"] == "horseshoe" and r["observedOn"] == "2026-11-17"]
        self.assertEqual(len(rows), 2, "both December readings must be kept, never overwritten")
        self.assertTrue(all("quoteType" in r and r["quoteType"] for r in rows))
        self.assertTrue(any("01:26 UTC" in r["note"] for r in rows), "the earlier reading is named")

    def test_trip_window_calendar_sum_matches_the_logged_arithmetic(self):
        """Nov 25 to Dec 1 cells, read off the page, add to the figure quoted in the log."""
        cells = {d: v for d, v in [
            ("2026-11-25", 55), ("2026-11-26", 55), ("2026-11-27", 181), ("2026-11-28", 115),
            ("2026-11-29", 272), ("2026-11-30", 470), ("2026-12-01", 379)]}
        self.assertEqual(sum(cells.values()), 1527)
        row = [r for r in RATE_LOG if r["hotel"] == "horseshoe" and "1,527.00" in r["note"]]
        self.assertTrue(row, "the logged note must state the same sum")

    def test_no_third_party_host_is_used_as_a_hotel_source(self):
        for h in DATA["hotels"]:
            for key in ("source", "feeSource", "taxSource", "parkingSource", "cancellationSource"):
                url = h.get(key) or ""
                if not url:
                    continue
                self.assertTrue(url.startswith("https://"), url)
                host = url.split("/")[2]
                self.assertTrue(
                    any(host.endswith(o) for o in
                        ("venetianlasvegas.com", "wynnlasvegas.com", "caesars.com", "mgmresorts.com")),
                    f"{h['id']}.{key}: unexpected source host {host}")


class PokerRateQualificationOfThePlan(unittest.TestCase):
    """The Venetian poker-suite rate is conditional; the plan must say which nights fail it."""

    CONDITION = 300

    def test_every_planned_day_carries_a_result(self):
        for day in PLAN:
            self.assertIn("pokerRateSatisfied", day, day["date"])
            self.assertIn("pokerRateBasis", day)
            self.assertIn("pokerRateCondition", day)
            self.assertIn("live cash", day["pokerRateCondition"])

    def test_result_is_exactly_the_published_threshold_applied_to_the_primary(self):
        for day in PLAN:
            expected = bool(day["primaryBuyIn"]) and day["primaryBuyIn"] >= self.CONDITION
            self.assertEqual(day["pokerRateSatisfied"], expected, day["date"])

    def test_two_nights_before_departure_do_not_qualify(self):
        nights = [d for d in PLAN if d["date"] < DATA["trip"]["end"]]
        self.assertEqual(len(nights), 7, "the trip is seven nights")
        failing = [d["date"] for d in nights if not d["pokerRateSatisfied"]]
        # The two $200 primaries sit at the start of the window now that the trip is 23-30 November:
        # the window moved so that it no longer spans 30 November and 1 December, which print no
        # figure on the official booking calendar in any reading (F57).
        self.assertEqual(failing, ["2026-11-23", "2026-11-24"])

    def test_the_gap_is_flagged_and_answered(self):
        self.assertIn("F54", FLAGS)
        self.assertEqual(FLAGS["F54"]["severity"], "High")
        q = [q for q in DATA["questions"] if q["id"] == "Q16"][0]
        self.assertIn("five", q["answer"].lower())
        # The two nights that miss the $300 test are the window's first two, not its last two.
        self.assertIn("Nov 23 and Nov 24", q["answer"])
        self.assertNotIn("Nov 30 and Dec 1", q["answer"], "stale trip window in the Q16 answer")


class CrossReferencesResolve(unittest.TestCase):
    """A pointer to a flag that does not exist sends a reviewer to the wrong item."""

    def _ids(self, key):
        return {row["id"] for row in DATA[key]}

    def test_every_flag_question_and_suggestion_id_mentioned_in_the_data_exists(self):
        pools = {"F": self._ids("flags"), "Q": self._ids("questions"), "S": self._ids("suggestions")}
        texts = []

        def walk(node):
            if isinstance(node, dict):
                for value in node.values():
                    walk(value)
            elif isinstance(node, list):
                for value in node:
                    walk(value)
            elif isinstance(node, str):
                texts.append(node)

        for key in ("flags", "questions", "suggestions", "trip", "planNotes", "hotels", "policy", "scope"):
            walk(DATA.get(key))
        for text in texts:
            for match in re.findall(r"\b([FQS]\d{2})\b", text):
                self.assertIn(match, pools[match[0]], f"dangling reference {match} in: {text[:80]}")

    def test_page_scripts_and_static_pages_do_not_point_at_a_retired_id(self):
        live = {row["id"] for row in DATA["flags"]} | {row["id"] for row in DATA["questions"]} \
            | {row["id"] for row in DATA["suggestions"]}
        for path in sorted((ROOT / "site").glob("*.html")) + [ROOT / "site" / "assets" / "app.js"]:
            for match in re.findall(r"\b([FQS]\d{2})\b", path.read_text(encoding="utf-8")):
                self.assertIn(match, live, f"{path.name} references {match}, which is not published")


class PublishedSourcesCoverWhatTheyClaim(unittest.TestCase):
    def test_new_official_pages_are_in_the_monitored_source_list(self):
        urls = {s["url"] for s in DATA["sources"]}
        self.assertTrue(any("propCode=clv" in u for u in urls), "Caesars Palace booking page not listed")
        self.assertTrue(any("propCode=blv" in u for u in urls), "Horseshoe booking page not listed")
        self.assertTrue(any("Signature_Series_Structures" in u for u in urls),
                        "the placeholder structures file is listed so the monitor sees it change")

    def test_the_placeholder_source_is_recorded_as_a_placeholder(self):
        row = [s for s in DATA["sources"] if "Signature_Series_Structures" in s["url"]][0]
        self.assertIn("COMING SOON", row["name"])

    def test_signature_rows_say_the_source_is_a_placeholder_rather_than_unread(self):
        rows = [e for e in DATA["events"] if e["id"].startswith("wynn-sig-")]
        self.assertTrue(rows)
        for e in rows:
            self.assertEqual(e["rules"]["singleEntry"]["status"], "not-verified")
            self.assertIn("COMING SOON", e["rules"]["singleEntry"]["excerpt"])
            self.assertEqual(e["rules"]["singleEntry"]["retrieved"], "2026-11-17")


if __name__ == "__main__":
    unittest.main()
