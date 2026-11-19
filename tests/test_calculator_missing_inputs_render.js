/* Headless check: an unpriced input must not become a $0 line in the trip total.
 *
 * The page's own script read every box with `Number(value) || 0`, so an empty "room tax rate" was not
 * "unknown" — it was zero tax, and an empty "resort fee" was a fee-less stay. The site's evidence rule
 * is the opposite: a figure no official source publishes stays blank and is flagged (F39 is exactly
 * the case this catches — Wynn, Caesars Palace, Horseshoe and Bellagio publish a mandatory resort fee
 * but no room-tax percentage). This runs the inline script of site/calculator.html against a stub form
 * and asserts the totals go unknown, line by line, while an explicit 0 is still honoured as an answer.
 *
 * Run with:  node tests/test_calculator_missing_inputs_render.js
 */
'use strict';

const fs = require('fs');
const path = require('path');
const vm = require('vm');
const re = require('util');

const ROOT = path.resolve(__dirname, '..');
const page = fs.readFileSync(path.join(ROOT, 'site', 'calculator.html'), 'utf8');
const data = JSON.parse(fs.readFileSync(path.join(ROOT, 'site', 'data.json'), 'utf8'));

// The page's own inline script (everything after the app.js include).
const script = page.match(/<script>\n([\s\S]*?)\n<\/script>/)[1];

function element() {
  const el = {
    html: '', text: '', hidden: true, dataset: {},
    set innerHTML(v) { this.html = v; }, get innerHTML() { return this.html; },
    set textContent(v) { this.text = String(v); }, get textContent() { return this.text; },
    append() {}, querySelectorAll() { return []; }, addEventListener() {},
  };
  return el;
}
function field(value) { return { value: String(value), validity: { valid: true } }; }

const DEFAULTS = { entries: 7, buyIn: 371.43, nights: 7, rate: 119, resortFee: 55, taxRate: 13.38, parking: 20 };
const form = { inputs: {} };
for (const [name, value] of Object.entries(DEFAULTS)) form[name] = field(value);
let onInput = null;
form.addEventListener = (type, fn) => { if (type === 'input') onInput = fn; };

const elements = {
  tripForm: form,
  result: element(),
  breakdown: element(),
};
const query = {
  '[data-hotel-presets]': element(),
  '[data-cost-compare]': element(),
  '[data-compare-note]': element(),
  '[data-dated-quote]': element(),
};

const sandbox = {
  console,
  Number, Math, isFinite, Object, Array, String, JSON, Promise, setTimeout, re,
  document: {
    getElementById: (id) => elements[id] || element(),
    querySelector: (sel) => query[sel] || element(),
    querySelectorAll: () => [],
    createElement: () => element(),
  },
  fetch: (url) => Promise.resolve({ ok: String(url).endsWith('data.json'), json: () => Promise.resolve(data) }),
};
sandbox.globalThis = sandbox;
vm.createContext(sandbox);
vm.runInContext(script, sandbox, { filename: 'calculator-inline.js' });

const failures = [];
function expect(label, actual, want) {
  if (actual !== want) failures.push(`${label}: got ${JSON.stringify(actual)}, want ${JSON.stringify(want)}`);
}
const has = (text, needle) => text.indexOf(needle) >= 0;

function rerender(values) {
  for (const [name, value] of Object.entries(values)) form[name].value = String(value);
  onInput();
}
const out = () => elements.result.html;
const brk = () => elements.breakdown.html;

setTimeout(() => {
  // 1. The sourced default: nothing is blank, so every line is a number.
  rerender(DEFAULTS);
  expect('default core estimate', has(out(), '$3,980.96'), true);
  expect('default all-in', has(out(), '$4,120.96'), true);
  expect('default has no unknown line', has(brk(), '>unknown<'), false);

  // 2. A missing room-tax percentage is the F39 case: fee published, tax not.
  rerender({ ...DEFAULTS, taxRate: '' });
  expect('blank tax yields no total', has(out(), '$3,980.96'), false);
  expect('blank tax is reported as unknown', has(out(), '>unknown<'), true);
  expect('blank tax names the missing field', has(out(), 'room tax rate'), true);
  expect('blank tax is not silently zero tax', has(brk(), '$197.28'), false);
  expect('the entry line still stands on its own', has(brk(), '$2,600'), true);

  // 3. A missing resort fee must not price a fee-less stay.
  rerender({ ...DEFAULTS, resortFee: '' });
  expect('blank fee yields no nightly cost', has(brk(), '$197.28'), false);
  expect('blank fee is unknown, not zero', has(out(), '$0.00'), false);

  // 4. A missing entry count prices the hotel line but not the core total.
  rerender({ ...DEFAULTS, entries: '' });
  expect('blank nights/entries keeps the hotel line', has(brk(), '1,380.96'), true);
  expect('blank entries removes the core total', has(out(), '$3,980.96'), false);
  expect('blank entries names the field', has(out(), 'number of entries'), true);

  // 5. A missing parking figure leaves the core estimate intact and the all-in unknown.
  rerender({ ...DEFAULTS, parking: '' });
  expect('blank parking leaves the core estimate', has(out(), '$3,980.96'), true);
  expect('blank parking makes the all-in unknown', has(out(), 'including parking <span class="muted">unknown</span>'), true);
  expect('blank parking is not $0', has(brk(), '= $0.00'), false);

  // 6. An explicit zero is an answer: 0% tax and a waived parking fee compute normally.
  rerender({ ...DEFAULTS, taxRate: 0, parking: 0 });
  expect('explicit zero tax is honoured', has(brk(), '$174.00'), true);
  expect('explicit zero parking is honoured', has(brk(), '7 nights × $0.00 = $0.00'), true);
  expect('explicit zeros still total', has(out(), '$3,818.00'), true);

  // 7. Everything blank: the page must offer no number at all.
  rerender({ entries: '', buyIn: '', nights: '', rate: '', resortFee: '', taxRate: '', parking: '' });
  expect('all blank prints no core total', has(out(), '$'), false);
  expect('all blank says which fields are missing', has(out(), 'left blank'), true);

  // 8. A non-numeric value is treated as unknown, not as 0 via Number() coercion.
  rerender({ ...DEFAULTS, rate: 'abc' });
  expect('garbage in the rate box is unknown', has(out(), '>unknown<'), true);

  if (failures.length) {
    failures.forEach((f) => console.error('FAIL ' + f));
    process.exit(1);
  }
  console.log('calculator unknown-input render OK · 8 input states exercised · no blank priced as zero');
}, 120);
