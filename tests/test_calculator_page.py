"""Guard the trip-cost page against claims that outrun the canonical data."""
from pathlib import Path
import json
import re
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
PAGE = (ROOT / "site" / "calculator.html").read_text(encoding="utf-8")
APP = (ROOT / "site" / "assets" / "app.js").read_text(encoding="utf-8")
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
        # Parking is reported beside the core figure and added only to the all-in one. The
        # exact statement changed when a blank parking field became "unknown, not zero", so
        # the assertion is on the behaviour rather than on one spelling of the line.
        self.assertRegex(PAGE, r"const allIn = parking === null \? null : coreEstimate \+ parking;")
        self.assertIn("Parking is not included in true room cost per night or in the core formula.", PAGE)

    def test_a_blank_field_is_unknown_and_never_prices_as_zero(self):
        # F39: most reviewed properties publish a resort fee and no room-tax percentage.
        # Coercing that blank to 0% would print a nightly cost below the published charge.
        self.assertIn("A blank or invalid field is treated as <strong>unknown</strong>", PAGE)
        self.assertIn("if (!input || input.value.trim() === '') return null;", PAGE)
        self.assertNotIn("Number(form.taxRate.value) || 0", PAGE)
        self.assertNotIn("parseFloat(document.getElementById('calc-tax').value) || 0", PAGE)

    def test_hotel_widget_defaults_come_from_published_property_components(self):
        self.assertIn("(db.hotels || []).find((hotel) => hotel.id === 'venetian')", APP)
        self.assertIn("inputValue(venetian.baseRateFloor)", APP)
        self.assertIn("inputValue(venetian.resortFee)", APP)
        self.assertIn("inputValue(venetian.taxRate)", APP)
        self.assertIn("defaultNights", APP)
        self.assertNotIn('id="calc-rate" min="0" value="119"', APP)
        self.assertNotIn('id="calc-fee" min="0" value="55"', APP)

    def test_unknown_nightly_budget_is_not_displayed_as_zero(self):
        self.assertNotIn("t.nightlyBudget || 0", APP)
        self.assertIn("'Nightly budget not published; no amount is inferred.'", APP)
        self.assertIn("? '$' + t.nightlyBudget.toFixed(2) : 'Not published'", APP)

    def test_missing_hotel_components_are_cleared_not_reused_or_zeroed(self):
        self.assertIn("form.rate.value = b.dataset.rate", PAGE)
        self.assertIn("form.resortFee.value = b.dataset.fee", PAGE)
        self.assertIn("form.taxRate.value = b.dataset.tax", PAGE)
        self.assertIn("form.parking.value = b.dataset.parking", PAGE)
        self.assertNotIn("data-preset=\"quote\"", PAGE)

    def test_render_uses_exact_plan_and_keeps_quote_separate(self):
        script = PAGE.split("<script>")[-1].split("</script>")[0]
        fields = dict(re.findall(r'id="(\w+)"[^>]*value="([^"]+)"', PAGE))
        harness = r"""
const assert = require('node:assert/strict');
const db = require('./site/data.json');
const form = Object.fromEntries(Object.entries(FIELDS).map(([id, value]) => [id, {value}]));
const result = {}, breakdown = {}, body = {}, note = {}, quote = {append(link) { this.link = link; }};
const quoteLater = {append(link) { this.link = link; }};
form.addEventListener = (_, cb) => { form.update = cb; };
global.document = {
  getElementById: id => ({tripForm: form, result, breakdown})[id],
  querySelector: selector => ({'[data-cost-compare]': body, '[data-compare-note]': note,
    '[data-dated-quote]': quote, '[data-dated-quote-later]': quoteLater})[selector],
  querySelectorAll: () => [], createElement: () => ({})
};
global.fetch = async () => ({json: async () => db});
setImmediate(() => {
  assert.match(result.innerHTML, /\$3,980\.96/);
  assert.match(result.innerHTML, /\$4,120\.96/);
  assert.match(breakdown.innerHTML, /\$2,600\.00/);
  assert.match(quote.textContent, /\$4,010\.55/);
  assert.equal(quote.link.href, db.tripCostModel.liveQuote.sources.quote);
  // The second dated read is printed beside the first, never in place of it, and its all-in
  // per-night figure is the printed checkout total divided by the nights.
  assert.match(quoteLater.textContent, /\$3,619\.39/);
  assert.match(quoteLater.textContent, /\$517\.06/);
  assert.match(quoteLater.textContent, /\$2,807\.25/);
  assert.equal(quoteLater.link.href, db.tripCostModel.liveQuote.laterRead.source);
  form.entries.value = '1';
  form.update();
  assert.match(breakdown.innerHTML, /1 × \$371\.43 = \$371\.43/);
});
"""
        subprocess.run(["node", "-e", harness.replace("FIELDS", json.dumps(fields)) + script],
                       cwd=ROOT, check=True)


if __name__ == "__main__":
    unittest.main()
