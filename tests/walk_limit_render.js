/* Headless check of the tournament table's 30-minute walking limit.
 *
 * Runs site/assets/app.js for the tournaments page against site/data.json, then switches
 * the walking limit on with The Venetian selected and re-renders.  It asserts the row counts
 * and the wording of the note that reports what the limit hides, so the filter can never again
 * drop most of the table silently.  Run with:  node tests/walk_limit_render.js
 */
'use strict';

const fs = require('fs');
const path = require('path');
const vm = require('vm');

const ROOT = path.resolve(__dirname, '..');
const data = JSON.parse(fs.readFileSync(path.join(ROOT, 'site', 'data.json'), 'utf8'));

function makeElement(selector) {
  return {
    selector,
    html: '',
    text: '',
    hidden: true,
    dataset: {},
    value: '',
    checked: false,
    type: 'text',
    tagName: 'DIV',
    set innerHTML(v) { this.html = v; },
    get innerHTML() { return this.html; },
    set textContent(v) { this.text = String(v); },
    get textContent() { return this.text; },
    scrollIntoView() {},
    addEventListener() {},
    querySelector(sel) { return makeElement(sel); },
    querySelectorAll() { return []; },
    setAttribute() {},
  };
}

const registry = new Map();
function hook(selector) {
  if (!registry.has(selector)) registry.set(selector, makeElement(selector));
  return registry.get(selector);
}

const document = {
  body: { dataset: { page: 'tournaments' } },
  querySelector: (sel) => hook(sel),
  querySelectorAll: (sel) => [hook(sel)],
};
const sandbox = {
  document,
  location: { pathname: '/tournaments.html', search: '', href: '' },
  URLSearchParams,
  console,
  fetch: (url) => Promise.resolve({ ok: String(url).endsWith('data.json'), json: () => Promise.resolve(data) }),
};
sandbox.globalThis = sandbox;
vm.createContext(sandbox);
vm.runInContext(fs.readFileSync(path.join(ROOT, 'site', 'assets', 'app.js'), 'utf8'), sandbox, { filename: 'app.js' });

const rowCount = (html) => (html.match(/<tr class="row-click"/g) || []).length;
const noteOf = (html) => (html.match(/<p class="toolbar-note">([\s\S]*?)<\/p>/) || [, ''])[1].replace(/\s+/g, ' ').trim();

const failures = [];
function expect(label, actual, want) {
  if (actual !== want) failures.push(`${label}: got ${JSON.stringify(actual)}, want ${JSON.stringify(want)}`);
}

setTimeout(() => {
  const liveRows = data.events.filter((e) => e.status !== 'past').length;

  // 1. Default view: the limit is off, so nothing may be hidden.
  const openHtml = hook('[data-tournament-table]').html;
  const openRows = rowCount(openHtml);
  expect('default view shows every non-past row', openRows, liveRows);
  expect('default view reports no walking limit', openHtml.includes('Walking limit ('), false);
  expect('state starts with the limit off', vm.runInContext('state.walkOnly', sandbox), false);

  // 2. Switch the limit on from The Venetian: only measured, over-limit rows may disappear.
  vm.runInContext("state.walkOnly = true; state.hotelWalk = 'venetian'; applyTournamentFilters();", sandbox);
  const walkHtml = hook('[data-tournament-table]').html;
  const walkRows = rowCount(walkHtml);
  expect('walk limit from the Venetian keeps 333 rows', walkRows, 333);
  expect('hidden rows equal the rows the data puts over 30 minutes', liveRows - walkRows, 6);
  const note = noteOf(walkHtml);
  expect('the note names the hotel it measures from', note.includes('from The Venetian Resort'), true);
  expect('the note counts the over-limit rows', note.includes('6 measured over the limit'), true);
  expect('the note counts unmeasured rows separately', note.includes('0 with no measured route'), true);

  // 3. A hotel with few measured routes must report the unmeasured rows, not hide them quietly.
  vm.runInContext("state.hotelWalk = 'mgm'; applyTournamentFilters();", sandbox);
  const mgmNote = noteOf(hook('[data-tournament-table]').html);
  expect('the MGM view separates the two reasons', /(\d+) measured over the limit, (\d+) with no measured route/.test(mgmNote), true);

  // 4. Every shown row must carry the walk from the hotel that is selected, with its date.
  vm.runInContext("state.hotelWalk = 'venetian'; applyTournamentFilters();", sandbox);
  const html = hook('[data-tournament-table]').html;
  expect('rows are labelled with the walk from the selected hotel', html.includes('min walk from The Venetian Resort'), true);
  // The matrix is complete, so no row may need the reverse fallback in this view; if one did, it must be labelled.
  const reversed = (html.match(/reverse of the recorded pair/g) || []).length;
  expect('the reverse label only appears where a pair is resolved backwards', reversed, 0);

  if (failures.length) {
    failures.forEach((f) => console.error('FAIL ' + f));
    process.exit(1);
  }
  console.log(`walk limit render OK · ${openRows} rows by default · ${walkRows} with the limit on from The Venetian`);
}, 80);
