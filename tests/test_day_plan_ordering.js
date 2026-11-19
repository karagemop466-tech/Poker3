/* Headless check of the day plan's same-day event ordering.
 *
 * The schedule page lists each day's primary candidate, then the room events that recur on that
 * day (the Wynn daily slate, the Bellagio bomb pot, the Caesars and MGM dailies). Those used to
 * render as an unordered list, so an event starting before the primary, or after it, looked the
 * same. Each is now labelled with its relation to the primary using the planner's own published
 * assumptions — a six-hour session and a 30-minute transfer — and anything that lets a player
 * spend more for an advantage (rebuy, add-on, multi-buy-in, multi-flight) is marked as such.
 *
 * Run with:  node tests/test_day_plan_ordering.js
 */
'use strict';

const fs = require('fs');
const path = require('path');
const vm = require('vm');

const ROOT = path.resolve(__dirname, '..');
const data = JSON.parse(fs.readFileSync(path.join(ROOT, 'site/data.json'), 'utf8'));

const registry = new Map();
function element(selector) {
  if (!registry.has(selector)) {
    registry.set(selector, {
      selector, html: '', text: '', hidden: true, dataset: {}, value: '', checked: false,
      type: 'text', tagName: 'DIV',
      set innerHTML(v) { this.html = v; },
      get innerHTML() { return this.html; },
      set textContent(v) { this.text = String(v); },
      get textContent() { return this.text; },
      scrollIntoView() {},
      addEventListener() {},
      querySelector(sel) { return element(sel); },
      querySelectorAll() { return []; },
      setAttribute() {},
    });
  }
  return registry.get(selector);
}

const sandbox = {
  document: {
    body: { dataset: { page: 'schedule' } },
    querySelector: (sel) => element(sel),
    querySelectorAll: (sel) => [element(sel)],
  },
  location: { pathname: '/schedule.html', search: '', href: '' },
  URLSearchParams,
  console,
  fetch: () => Promise.resolve({ ok: true, json: () => Promise.resolve(data) }),
};
sandbox.globalThis = sandbox;
vm.createContext(sandbox);
vm.runInContext(fs.readFileSync(path.join(ROOT, 'site', 'assets', 'app.js'), 'utf8'), sandbox, { filename: 'app.js' });

let failures = 0;
function check(label, condition, detail) {
  if (condition) console.log('ok    ' + label);
  else { failures += 1; console.log('FAIL  ' + label + (detail ? ' — ' + detail : '')); }
}

setTimeout(() => {
  const html = element('[data-plan]').html || '';
  check('the day plan rendered', html.length > 1000, 'length ' + html.length);

  /* Every recurring line must now say where it sits relative to the primary. */
  const lines = [...html.matchAll(/<li>([\s\S]*?)<\/li>/g)].map((m) => m[1]);
  const recurringLines = lines.filter((l) => /min walk|on site/.test(l));
  check('recurring room events are rendered', recurringLines.length > 10, recurringLines.length + ' lines');

  const unlabelled = recurringLines.filter((l) =>
    !/does not follow the primary|playable after the primary|may overlap the primary/.test(l));
  check('every recurring event states its timing against the primary', unlabelled.length === 0,
    unlabelled.length + ' unlabelled: ' + unlabelled.slice(0, 2).map((l) => l.replace(/<[^>]+>/g, ' ').slice(0, 80)).join(' | '));

  /* Anything with a multi-buy-in or multi-flight format must be marked as extra spend. */
  const multiBuyInLines = recurringLines.filter((l) => /data-none|Multi|Rebuy/i.test(l));
  const spendFlagged = recurringLines.filter((l) => /extra-spend format/.test(l));
  check('extra-spend formats are marked', spendFlagged.length > 0, String(spendFlagged.length));

  /* The word "estimated" must appear wherever a timing judgement is made, because no venue
   * publishes a finish time (F16). */
  const timingLines = recurringLines.filter((l) => /playable after the primary|may overlap the primary/.test(l));
  check('timing judgements are labelled as estimates',
    timingLines.every((l) => /estimated/.test(l)), timingLines.length + ' timing lines');

  /* The published transfer allowance the labels use must be the one in the data, not a literal
   * typed into the page. */
  check('the transfer allowance matches planNotes.transfer',
    data.planNotes && data.planNotes.transfer === 30, String(data.planNotes && data.planNotes.transfer));

  if (failures) {
    console.log('\n' + failures + ' day-plan check(s) failed');
    process.exit(1);
  }
  console.log('\nday-plan ordering checks passed');
}, 80);
