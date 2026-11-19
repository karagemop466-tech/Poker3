/* Headless check of the trip-cost calculator's unknown-value behaviour.
 *
 * The calculator used to coerce a blank field with `Number(x) || 0`, so a room-tax
 * percentage that no reviewed property publishes (flag F39) priced as 0% and the page
 * printed a nightly cost below the published charge. This harness executes the real
 * inline script from site/calculator.html against a stub DOM and asserts that:
 *
 *   1. a blank core field makes the total unknown, not zero;
 *   2. an explicit 0 is still honoured (parking waived, F86);
 *   3. a blank parking field leaves the core estimate but withholds the all-in one;
 *   4. the fully populated default still reproduces the published model, exactly.
 *
 * Run with:  node tests/test_calculator_unknown_inputs.js
 */
'use strict';

const fs = require('fs');
const path = require('path');
const vm = require('vm');

const ROOT = path.resolve(__dirname, '..');
const HTML = fs.readFileSync(path.join(ROOT, 'site', 'calculator.html'), 'utf8');
const DATA = JSON.parse(fs.readFileSync(path.join(ROOT, 'site', 'data.json'), 'utf8'));

/* The page has exactly one large inline <script> after the shared app.js; that is the
 * calculator. Extract it rather than re-implementing the arithmetic here. */
function calculatorScript() {
  const scripts = [...HTML.matchAll(/<script>([\s\S]*?)<\/script>/g)].map((m) => m[1]);
  const found = scripts.find((s) => s.includes("getElementById('tripForm')"));
  if (!found) throw new Error('calculator inline script not found in site/calculator.html');
  return found;
}

function field(name, value) {
  return {
    name,
    value,
    validity: { valid: true },
    addEventListener() {},
  };
}

function buildForm(values) {
  const form = {
    entries: field('entries', ''),
    buyIn: field('buyIn', ''),
    nights: field('nights', ''),
    rate: field('rate', ''),
    resortFee: field('resortFee', ''),
    taxRate: field('taxRate', ''),
    parking: field('parking', ''),
    addEventListener() {},
  };
  Object.keys(values).forEach((k) => { form[k].value = values[k]; });
  return form;
}

const DEFAULTS = {
  entries: '7', buyIn: '371.43', nights: '7',
  rate: '119', resortFee: '55', taxRate: '13.38', parking: '20',
};

async function run(values) {
  const form = buildForm(values);
  const out = { innerHTML: '', textContent: '' };
  const brk = { innerHTML: '', textContent: '' };
  const empty = { innerHTML: '', textContent: '', querySelector: () => null, querySelectorAll: () => [] };
  const document = {
    getElementById: (id) => (id === 'tripForm' ? form : id === 'result' ? out : id === 'breakdown' ? brk : null),
    querySelector: (sel) => (sel === '[data-dated-quote]' ? { textContent: '', append() {} } : empty),
    querySelectorAll: () => [],
    createElement: () => ({ textContent: '', href: '' }),
  };
  const sandbox = {
    document,
    console,
    Math,
    Number,
    Intl,
    fetch: () => Promise.resolve({ json: () => Promise.resolve(DATA) }),
  };
  sandbox.globalThis = sandbox;
  vm.createContext(sandbox);
  vm.runInContext(calculatorScript(), sandbox, { filename: 'calculator.html:inline' });
  /* The data-driven preset table resolves from a fetch; let it settle so the tests
   * assert the steady state a reader actually sees, not the pre-fetch default. */
  await tick();
  return { out, brk, form };
}

const tick = () => new Promise((resolve) => setTimeout(resolve, 0));

let failures = 0;

async function main() {
function check(label, condition, detail) {
  if (condition) {
    console.log('ok    ' + label);
  } else {
    failures += 1;
    console.log('FAIL  ' + label + (detail ? ' — ' + detail : ''));
  }
}

/* 1. The published default reproduces the published model.
 *
 * The page's "core" figure is entries x buy-in + nights x true hotel cost, and parking is
 * deliberately reported beside it rather than inside it (the page says so, and
 * tripCostModel.parkingTotal carries the same separation). So the published
 * lodgingTotal is what the core figure must contain, and the published tripTotal is what
 * core + parking must add up to. Both are asserted, so the exact-sum and phantom-cent
 * arithmetic from PR #180 cannot silently regress. */
{
  const { out, brk } = await run(DEFAULTS);
  const model = DATA.tripCostModel;
  const usd = (n) => '$' + n.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  check('default core estimate = tournament total + lodging total',
    out.innerHTML.includes(usd(model.tournamentTotal + model.lodgingTotal)), out.innerHTML);
  check('default all-in estimate equals the published trip total (core + parking)',
    out.innerHTML.includes(usd(model.tripTotal)), out.innerHTML);
  check('default breakdown states the true nightly cost', brk.innerHTML.includes(usd(model.trueCostPerNight)), brk.innerHTML);
  check('default breakdown states the exact-sum tournament total',
    brk.innerHTML.includes(usd(model.tournamentTotal)) && !brk.innerHTML.includes('$2,600.01'), brk.innerHTML);
}

/* 2. A blank tax percentage is unknown, never 0%. */
{
  const { out, brk } = await run(Object.assign({}, DEFAULTS, { taxRate: '' }));
  check('blank tax percentage makes the total unavailable', /unavailable/i.test(out.innerHTML), out.innerHTML);
  check('blank tax percentage names the missing field', /taxRate/.test(brk.innerHTML), brk.innerHTML);
  check('blank tax percentage does not print a dollar figure in the headline',
    !/\$\d/.test(out.innerHTML), out.innerHTML);
}

/* 3. A blank room rate is unknown. */
{
  const { out } = await run(Object.assign({}, DEFAULTS, { rate: '' }));
  check('blank room rate makes the total unavailable', /unavailable/i.test(out.innerHTML), out.innerHTML);
}

/* 4. An explicit 0 is honoured, not treated as missing. */
{
  const { out, brk } = await run(Object.assign({}, DEFAULTS, { parking: '0' }));
  check('explicit zero parking still prints the all-in total',
    out.innerHTML.includes('including parking'), out.innerHTML);
  check('explicit zero parking is shown as $0.00 in the breakdown',
    brk.innerHTML.includes('$0.00'), brk.innerHTML);
}

/* 5. A blank parking field keeps the core estimate but withholds the all-in one. */
{
  const { out, brk } = await run(Object.assign({}, DEFAULTS, { parking: '' }));
  check('blank parking keeps the core estimate', /Core trip estimate: <strong>\$/.test(out.innerHTML), out.innerHTML);
  check('blank parking withholds the parking-inclusive total',
    /parking-inclusive total unavailable/.test(out.innerHTML), out.innerHTML);
  check('blank parking says the all-in total is unavailable', /unavailable/.test(brk.innerHTML), brk.innerHTML);
}

/* 6. An invalid (negative) value is unknown, not a negative cost. */
{
  const form = buildForm(DEFAULTS);
  form.taxRate.value = '-5';
  form.taxRate.validity = { valid: false };
  const out = { innerHTML: '', textContent: '' };
  const brk = { innerHTML: '', textContent: '' };
  const empty = { innerHTML: '', textContent: '', querySelector: () => null, querySelectorAll: () => [] };
  const document = {
    getElementById: (id) => (id === 'tripForm' ? form : id === 'result' ? out : id === 'breakdown' ? brk : null),
    querySelector: (sel) => (sel === '[data-dated-quote]' ? { textContent: '', append() {} } : empty),
    querySelectorAll: () => [],
    createElement: () => ({ textContent: '', href: '' }),
  };
  const sandbox = { document, console, Math, Number, Intl,
    fetch: () => Promise.resolve({ json: () => Promise.resolve(DATA) }) };
  sandbox.globalThis = sandbox;
  vm.createContext(sandbox);
  vm.runInContext(calculatorScript(), sandbox, { filename: 'calculator.html:inline' });
  check('an invalid (out-of-range) field makes the total unavailable',
    /unavailable/i.test(out.innerHTML), out.innerHTML);
}

}

main().then(() => {
  if (failures) {
    console.log('\n' + failures + ' calculator check(s) failed');
    process.exit(1);
  }
  console.log('\ncalculator unknown-value checks passed');
}).catch((err) => {
  console.error(err);
  process.exit(1);
});
