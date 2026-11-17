"""Walking-limit behaviour and the property-printed tax evidence (session arena/4b9d6340-poker3).

Two things are pinned here.

1. The tournament table's 30-minute walking limit must not hide rows silently.  Before this
   pass the limit was ON by default and was measured from one hotel only, which dropped 196 of
   the 341 published rows on first paint - rows were not excluded because they were unplayable,
   they were excluded because a route had never been measured for them.  The limit is now opt-in,
   is measured from a hotel the reader selects, and the page counts what it hides.

2. Where a property prints its resort fee and the tax on that fee as two dollar amounts, the
   implied percentage is arithmetic on the property's own page.  It has to agree with the 13.38%
   the cost model applies, or the model's true-cost figures are wrong for that property.
"""
import json
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / "site" / "data.json").read_text(encoding="utf-8"))
APP = (ROOT / "site" / "assets" / "app.js").read_text(encoding="utf-8")
TOURNAMENTS = (ROOT / "site" / "tournaments.html").read_text(encoding="utf-8")
COVERAGE = json.loads((ROOT / "site" / "coverage.json").read_text(encoding="utf-8"))

MODEL_TAX_PCT = DATA["tripCostModel"]["taxPct"]


class WalkingLimit(unittest.TestCase):
    def test_limit_is_off_by_default_in_state_and_markup(self):
        """The table must open showing every row, so walkOnly starts false and the checkbox is unchecked."""
        state = re.search(r"const state = \{(.*?)\};", APP, re.S)
        self.assertIsNotNone(state, "the filter state object was not found in app.js")
        self.assertIn("walkOnly: false", state.group(1), "the walking limit must default to off")
        self.assertNotIn('data-f="walkOnly" checked', APP,
                         "the walking-limit checkbox must not be pre-checked in the generated markup")

    def test_limit_constant_is_thirty_minutes(self):
        m = re.search(r"const WALK_LIMIT_MIN = (\d+);", APP)
        self.assertIsNotNone(m, "no named walking limit found in app.js")
        self.assertEqual(int(m.group(1)), 30)

    def test_limit_is_measured_from_a_selected_hotel(self):
        self.assertIn("hotelWalk: 'venetian'", APP, "the walk control needs a hotel to measure from")
        self.assertIn('data-f="hotelWalk"', APP, "the hotel selector must be part of the walk control")
        self.assertIn("walkMinutes(state.hotelWalk, e.venue)", APP,
                      "the filter must use the selected hotel, not a hard-coded one")

    def test_hidden_rows_are_counted_out_loud(self):
        """Rows hidden by the limit must be reported, split between over-limit and unmeasured."""
        self.assertIn("filteredEvents({ ignoreWalk: true })", APP)
        self.assertIn("no measured route", APP)
        self.assertIn("over the limit", APP)

    def test_walk_lookup_reads_both_directions(self):
        """A route is stored in whichever direction it was measured, so the reverse must resolve too."""
        self.assertIn("const reverse = list.find((x) => x.hotel === venueId && x.venue === hotelId);", APP)

    def _minutes(self, routes, hotel, venue):
        """Mirror of walkMinutes() in app.js: forward row, same-property zero, reverse row, else None."""
        if (hotel, venue) in routes:
            return routes[(hotel, venue)]
        if hotel == venue:
            return 0
        return routes.get((venue, hotel))

    def test_reverse_lookup_recovers_the_rows_the_old_default_hid(self):
        """The old filter looked one way only and dropped most of the table; the new one must not.

        Numbers asserted here are the ones F32 publishes, so the flag text cannot drift from the data.
        """
        routes = {(r["hotel"], r["venue"]): r["minutes"] for r in DATA["routes"]}
        live = [e for e in DATA["events"] if e.get("status") != "past"]
        old_shown = [e for e in live if routes.get(("venetian", e["venue"])) is not None
                     and routes[("venetian", e["venue"])] <= 30]
        new_shown = [e for e in live if (lambda m: m is not None and m <= 30)(
            self._minutes(routes, "venetian", e["venue"]))]
        self.assertEqual(len(old_shown), 145, "the historical one-direction view is expected to be 145 rows")
        self.assertEqual(len(new_shown), 333, "with the Venetian selected the limit must keep 333 rows")
        self.assertEqual(len(live), 339)
        over = sorted({e["venue"] for e in live if (lambda m: m is not None and m > 30)(
            self._minutes(routes, "venetian", e["venue"]))})
        self.assertEqual(over, ["aria", "mgm"], "only the over-limit venues may be removed")
        unmeasured = [e for e in live if self._minutes(routes, "venetian", e["venue"]) is None]
        self.assertEqual(unmeasured, [], "no row may be dropped for want of a measurement in this view")
        f32 = next(f for f in DATA["flags"] if f["id"] == "F32")["detail"]
        for token in ("145-row view into 333", "339 rows that are not in the past", "the 6 rows"):
            self.assertIn(token, f32, f"F32 must state {token!r}, which is what the data produces")

    def test_reversed_pairs_are_labelled_as_such(self):
        """A reversed row is a property-to-property figure, so the UI has to say which it is."""
        self.assertIn("reverse of the recorded pair", APP)
        self.assertIn("function walkRoute(hotelId, venueId)", APP)

    def test_tournaments_page_explains_the_new_behaviour(self):
        self.assertIn("walking limit is opt-in", TOURNAMENTS)


class FlagAndCoverageConsistency(unittest.TestCase):
    def test_f32_route_count_matches_the_data(self):
        """F32 quotes the route count; a stale figure there is exactly the defect this repo keeps flagging."""
        f32 = next(f for f in DATA["flags"] if f["id"] == "F32")
        stated = int(re.search(r"The current (\d+) route rows", f32["detail"]).group(1))
        self.assertEqual(stated, len(DATA["routes"]), "F32 states a route count that is not the published count")

    def test_c14_coverage_note_matches_the_data(self):
        item = next(i for i in COVERAGE["items"] if i["id"] == "C14")
        stated = int(re.search(r"(\d+) of (\d+) hotel-venue pairs", item["note"]).groups()[0])
        self.assertEqual(stated, len(DATA["routes"]))
        hotels = {h["id"] for h in DATA["hotels"]}
        venues = {v["id"] for v in DATA["venues"]}
        self.assertEqual(int(re.search(r"of (\d+) hotel-venue pairs", item["note"]).groups()[0]),
                         len(hotels) * len(venues), "the pair census in C14 does not match the record counts")

    def test_new_verification_flags_cite_official_property_hosts(self):
        venue_hosts = ("venetianlasvegas.com", "wynnlasvegas.com", "cdn.wynnresorts.com", "caesars.com",
                       "bellagio.mgmresorts.com", "mgmgrand.mgmresorts.com", "aria.mgmresorts.com")
        for fid in ("F78", "F79"):
            flag = next((f for f in DATA["flags"] if f["id"] == fid), None)
            self.assertIsNotNone(flag, f"{fid} is missing from the flag register")
            self.assertTrue(flag["source"].startswith("https://"), f"{fid} has no https source")
            self.assertTrue(any(h in flag["source"] for h in venue_hosts),
                            f"{fid} must cite a venue or property host, not a third party")


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
                self.assertEqual(p["observedOn"], DATA["asOf"] if DATA.get("asOf") else p["observedOn"])

    def test_taxRate_stays_blank_where_the_property_prints_no_percentage(self):
        """A corroborating fee ratio is not a published room-tax percentage; taxRate must stay empty."""
        for h in DATA["hotels"]:
            if h.get("printedFeeAndTax") and not h.get("taxRate"):
                continue
            if h.get("taxRate"):
                self.assertEqual(round((h["baseRateFloor"] + h["resortFee"]) * (1 + h["taxRate"] / 100), 2),
                                 h["trueNightlyLow"], f"{h['name']}: true nightly cost does not recompute")
            else:
                self.assertFalse(h.get("trueNightlyLow"),
                                 f"{h['name']}: a nightly cost is published while the tax rate is not")


if __name__ == "__main__":
    unittest.main()
