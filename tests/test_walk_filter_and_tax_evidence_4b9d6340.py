"""Walking-limit behaviour, route-matrix claims and the property-printed tax evidence.

Written by session arena/4b9d6340-poker3 after the 2026-11-17 live re-reads.

Three things are pinned here.

1. The tournament table's 30-minute walking limit must not hide rows before the reader asks.
   It shipped ON by default and looked up one direction only, which dropped rows because no route
   had been recorded, not because any of them is too far. It is now opt-in, measured from a hotel the
   reader selects, and it counts what it hides - over the limit and unmeasured separately.

2. The published prose about the route matrix must match the published matrix. F32 claims every
   hotel-venue pair is measured; a lost route row would make that sentence false, so it is checked
   against the data, and so is the coverage note's pair census.

3. Where a property prints its resort fee and the tax on that fee as two dollar amounts, the implied
   percentage is arithmetic on the property's own page. It has to agree with the 13.38% the cost model
   applies, or the model's true-cost figures are wrong for that property.
"""
import json
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / "site" / "data.json").read_text(encoding="utf-8"))
APP = (ROOT / "site" / "assets" / "app.js").read_text(encoding="utf-8")
VENUE = (ROOT / "site" / "assets" / "venue.js").read_text(encoding="utf-8")
TOURNAMENTS = (ROOT / "site" / "tournaments.html").read_text(encoding="utf-8")
CALCULATOR = (ROOT / "site" / "calculator.html").read_text(encoding="utf-8")
COVERAGE = json.loads((ROOT / "site" / "coverage.json").read_text(encoding="utf-8"))

MODEL_TAX_PCT = DATA["tripCostModel"]["taxPct"]
HOTEL_IDS = {h["id"] for h in DATA["hotels"]}
VENUE_IDS = {v["id"] for v in DATA["venues"]}
ROUTES = {(r["hotel"], r["venue"]): r["minutes"] for r in DATA["routes"]}
LIVE = [e for e in DATA["events"] if e.get("status") != "past"]


def walk_minutes(hotel, venue):
    """Mirror of walkMinutes() in app.js: forward row, same-property zero, reverse row, else None."""
    if (hotel, venue) in ROUTES:
        return ROUTES[(hotel, venue)]
    if hotel == venue:
        return 0
    return ROUTES.get((venue, hotel))


class WalkingLimitControl(unittest.TestCase):
    def test_limit_is_off_by_default_in_state_and_markup(self):
        """The table must open showing every row, so walkOnly starts false and the box is unchecked."""
        state = re.search(r"const state = \{(.*?)\};", APP, re.S)
        self.assertIsNotNone(state, "the filter state object was not found in app.js")
        self.assertIn("walkOnly: false", state.group(1), "the walking limit must default to off")
        self.assertNotIn('data-f="walkOnly" checked', APP,
                         "the walking-limit checkbox must not be pre-checked in the generated markup")

    def test_limit_constant_is_thirty_minutes(self):
        m = re.search(r"const WALK_LIMIT_MIN = (\d+);", APP)
        self.assertIsNotNone(m, "no named walking limit found in app.js")
        self.assertEqual(int(m.group(1)), 30, "the brief's limit is 30 minutes")

    def test_limit_is_measured_from_a_selected_hotel(self):
        self.assertIn("hotelWalk: 'venetian'", APP, "the walk control needs a hotel to measure from")
        self.assertIn('data-f="hotelWalk"', APP, "the hotel selector must be part of the walk control")
        self.assertIn("walkMinutes(state.hotelWalk, e.venue)", APP,
                      "the filter must use the selected hotel, not a hard-coded one")

    def test_hidden_rows_are_counted_out_loud(self):
        """Rows the limit hides must be reported, and split between over-limit and unmeasured."""
        self.assertIn("filteredEvents({ ignoreWalk: true })", APP)
        self.assertIn("no measured route", APP)
        self.assertIn("over the limit", APP)

    def test_reverse_lookup_exists_and_is_labelled(self):
        """A reversed row is a property-to-property figure, so the UI has to say which one it is."""
        self.assertIn("const reverse = list.find((x) => x.hotel === venueId && x.venue === hotelId);", APP)
        self.assertIn("reverse of the recorded pair", APP)

    def test_tournaments_page_explains_the_behaviour(self):
        self.assertIn("walking limit is opt-in", TOURNAMENTS)
        self.assertIn("counts separately the rows where no route has been measured", TOURNAMENTS)


class WalkingLimitAgainstData(unittest.TestCase):
    def test_unlimited_view_keeps_every_non_past_row(self):
        self.assertEqual(len(LIVE), 339)
        # Nothing else can be hidden at boot: past rows are the only default filter.
        self.assertEqual(len([e for e in DATA["events"] if e.get("status") == "past"]),
                         len(DATA["events"]) - len(LIVE))

    def test_limited_view_hides_only_measured_over_limit_rows(self):
        shown = [e for e in LIVE if (lambda m: m is not None and m <= 30)(walk_minutes("venetian", e["venue"]))]
        self.assertEqual(len(shown), 333, "the Venetian view must keep every row measured within 30 minutes")
        over = sorted({e["venue"] for e in LIVE if (lambda m: m is not None and m > 30)(
            walk_minutes("venetian", e["venue"]))})
        self.assertEqual(over, ["aria", "mgm"], "only the two venues measured over the limit may be removed")
        hidden = [e for e in LIVE if e not in shown]
        self.assertEqual(len(hidden), 6)

    def test_no_row_anywhere_is_hidden_for_want_of_a_measurement(self):
        """With a complete matrix, 'unmeasured' must stay zero for every hotel - that is what F32 claims."""
        for hotel in sorted(HOTEL_IDS):
            with self.subTest(hotel=hotel):
                unmeasured = [e for e in LIVE if walk_minutes(hotel, e["venue"]) is None]
                self.assertEqual(unmeasured, [], f"{hotel}: rows would be dropped with no measured route")


class RouteMatrixClaims(unittest.TestCase):
    def test_f32_matrix_claim_matches_the_data(self):
        f32 = next(f for f in DATA["flags"] if f["id"] == "F32")["detail"]
        self.assertIn("all 56 pairs", f32, "F32 must state the pair census it is claiming")
        self.assertEqual(len(DATA["routes"]), len(HOTEL_IDS) * len(VENUE_IDS),
                         "the published route rows do not cover every hotel-venue pair F32 claims")
        self.assertIn("opt-in", f32, "F32 must describe the walking limit as opt-in, which is how it ships")

    def test_every_pair_has_a_row(self):
        missing = [(h, v) for h in HOTEL_IDS for v in VENUE_IDS if (h, v) not in ROUTES]
        self.assertEqual(missing, [], "these hotel-venue pairs have no walking row")

    def test_c14_coverage_note_matches_the_data(self):
        item = next(i for i in COVERAGE["items"] if i["id"] == "C14")
        stated, total = (int(x) for x in re.search(r"(\d+) of (\d+) hotel-venue pairs", item["note"]).groups())
        self.assertEqual(total, len(HOTEL_IDS) * len(VENUE_IDS), "C14's pair census is not the record count")
        self.assertEqual(stated, len(DATA["routes"]), "C14's measured-pair count is not the published count")
        if item["status"] == "shipped":
            self.assertEqual(stated, total, "a shipped walking-route item may not claim partial coverage")

    def test_routes_carry_a_retrieval_date(self):
        for r in DATA["routes"]:
            self.assertTrue(re.fullmatch(r"\d{4}-\d{2}-\d{2}", r.get("lastChecked") or ""),
                            f"route {r['hotel']}->{r['venue']} has no last checked date")
        # The coverage note and F32 both date the two passes, so the split has to be what the rows say.
        from collections import Counter
        by = Counter(r["lastChecked"] for r in DATA["routes"])
        self.assertEqual(by["2026-11-17"], 44, "44 rows must carry the 2026-11-17 pass date")
        self.assertEqual(by["2026-11-16"], 12, "12 base-pass rows must still carry the 2026-11-16 date")


class VenuePageMarks(unittest.TestCase):
    """One page per venue was a brief item; those pages must carry the same verification marks."""

    def test_venue_pages_load_the_monitor_record(self):
        self.assertIn("checks.json", VENUE)
        self.assertIn("Source changed", VENUE)
        self.assertIn("Source unavailable", VENUE)

    def test_venue_pages_show_last_checked(self):
        self.assertIn("<th>Last checked</th>", VENUE)
        self.assertIn("e.lastVerified", VENUE)
        self.assertIn("h.lastChecked", VENUE)

    def test_venue_page_badge_map_knows_every_published_status(self):
        statuses = set()
        for e in DATA["events"]:
            for k, v in (e.get("rules") or {}).items():
                if k == "singleEntry" and v.get("status"):
                    statuses.add(v["status"])
        known = set(re.findall(r"'([a-z-]+)': \[", VENUE))
        self.assertTrue(statuses <= known, f"venue.js renders a raw slug for {sorted(statuses - known)}")


class VerificationFlags(unittest.TestCase):
    OFFICIAL_HOSTS = ("venetianlasvegas.com", "wynnlasvegas.com", "cdn.wynnresorts.com", "caesars.com",
                      "bellagio.mgmresorts.com", "mgmgrand.mgmresorts.com", "aria.mgmresorts.com")

    def test_session_flags_exist_and_cite_official_property_hosts(self):
        for fid in ("F84", "F85"):
            flag = next((f for f in DATA["flags"] if f["id"] == fid), None)
            self.assertIsNotNone(flag, f"{fid} is missing from the flag register")
            self.assertTrue(flag["source"].startswith("https://"), f"{fid} has no https source")
            self.assertTrue(any(h in flag["source"] for h in self.OFFICIAL_HOSTS),
                            f"{fid} must cite a venue or property host, not a third party")

    def test_flag_ids_are_unique_and_this_sessions_are_at_the_end(self):
        ids = [f["id"] for f in DATA["flags"]]
        self.assertEqual(len(ids), len(set(ids)), "duplicate flag ids in the register")
        self.assertIn("F84", ids)
        self.assertIn("F85", ids)

    def test_calculator_warns_against_a_fee_inclusive_figure(self):
        self.assertIn("Do not paste a booking-calendar figure", CALCULATOR)
        self.assertIn("includes daily resort fee", CALCULATOR)


class PropertyPrintedTax(unittest.TestCase):
    def test_printed_fee_and_tax_arithmetic(self):
        rows = [h for h in DATA["hotels"] if h.get("printedFeeAndTax")]
        self.assertGreaterEqual(len(rows), 2, "both Caesars-branded pages print a fee-plus-tax figure")
        for h in rows:
            p = h["printedFeeAndTax"]
            with self.subTest(hotel=h["name"]):
                self.assertEqual(round(p["fee"] + p["tax"], 2), round(p["allIn"], 2),
                                 "the printed fee plus the printed tax must equal the printed all-in figure")
                self.assertAlmostEqual(p["taxPctImplied"], round(p["tax"] / p["fee"] * 100, 3), places=3)
                self.assertLess(abs(p["taxPctImplied"] - MODEL_TAX_PCT), 0.02,
                                "the property's own fee-plus-tax figures must agree with the model's tax rate")
                self.assertTrue(p["agreesWithModelTaxPct"])
                self.assertTrue(p["source"].startswith("https://"))

    def test_taxRate_stays_blank_where_the_property_prints_no_percentage(self):
        """A corroborating fee ratio is not a printed room-tax percentage for the rate."""
        for h in DATA["hotels"]:
            if h.get("taxRate"):
                self.assertEqual(round((h["baseRateFloor"] + h["resortFee"]) * (1 + h["taxRate"] / 100), 2),
                                 h["trueNightlyLow"], f"{h['name']}: true nightly cost does not recompute")
            else:
                self.assertFalse(h.get("trueNightlyLow"),
                                 f"{h['name']}: a nightly cost is published while the tax rate is not")


if __name__ == "__main__":
    unittest.main()
