/* Headless check of the landing page's "Source / sheet re-checked" column.
 *
 * The column used to be a date typed into site/index.html. It is now read out of site/checks.json at
 * render time, which is the only way it can stay true: the scheduled monitor rewrites that record every
 * morning, and on 2026-11-19 the page's typed date was the thing a regression test pinned to a literal
 * day — so the monitor's own gate went red on any day a venue re-published a sheet and the record of the
 * change was never committed (CI run 44482186623).
 *
 * This runs site/assets/app.js against a SYNTHETIC record (never the committed one, whose contents move)
 * and asserts the four states a cell can be in: unchanged, changed, blocked for the robot, and not
 * covered by any run. Run with:  node tests/sheet_recheck_render.js
 */
'use strict';

const fs = require('fs');
const path = require('path');
const vm = require('vm');

const ROOT = path.resolve(__dirname, '..');
const data = JSON.parse(fs.readFileSync(path.join(ROOT, 'site', 'data.json'), 'utf8'));

const BASE = 'https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/';
const sheets = (data.events || [])
  .filter((e) => (data.dayPlan || []).some((d) => d.primary === e.id))
  .map((e) => String(e.sheetUrl || '').split('/').pop())
  .filter(Boolean);

function makeElement(selector) {
  return {
    selector,
    html: '',
    text: '',
    title: '',
    className: '',
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
    setAttribute(k, v) { this[k] = v; },
  };
}

// One cell per trip-window sheet, exactly as site/index.html marks them up.
const cells = new Map();
for (const sheet of sheets) {
  const cell = makeElement('small[data-sheet-recheck]');
  cell.dataset.sheetRecheck = sheet;
  cell.textContent = 'sheet re-check date: see the source log';
  cells.set(sheet, cell);
}

const registry = new Map();
function hook(sel) {
  if (!registry.has(sel)) registry.set(sel, makeElement(sel));
  return registry.get(sel);
}

const record = {
  generatedAt: '2026-12-31T13:00:00+00:00',
  mode: 'synthetic fixture',
  urls: [
    // Two runs for the first sheet: the later one must win.
    { url: BASE + sheets[0], checked: '2026-11-17T13:00:00+00:00', status: 'HTTP 200', changed: false, hashBasis: 'raw' },
    { url: BASE + sheets[0], checked: '2026-12-30T13:00:00+00:00', status: 'HTTP 200', changed: false, hashBasis: 'raw' },
    // A re-published sheet: the cell must say so, in a colour, and not pretend to be a clean re-read.
    { url: BASE + sheets[1], checked: '2026-12-30T13:00:00+00:00', status: 'HTTP 200', changed: true,
      previousHash: 'old', hashBasis: 'raw' },
    // A robot-blocked URL is not a source change.
    { url: BASE + sheets[2], checked: '2026-12-30T13:00:00+00:00', status: 'HTTP 403', changed: false,
      botBlocked: true, outcome: 'blocked', unavailable: true },
    // sheets[3] is deliberately absent: a sheet the monitor does not cover must not borrow a date.
  ],
};

const document = {
  body: { dataset: { page: 'home' } },
  querySelector: (sel) => hook(sel),
  querySelectorAll: (sel) => (sel === '[data-sheet-recheck]' ? [...cells.values()] : [hook(sel)]),
};
const sandbox = {
  document,
  location: { pathname: '/index.html', search: '', href: '' },
  URLSearchParams,
  console,
  fetch: (url) => {
    if (String(url).endsWith('data.json')) return Promise.resolve({ ok: true, json: () => Promise.resolve(data) });
    if (String(url).endsWith('checks.json')) return Promise.resolve({ ok: true, json: () => Promise.resolve(record) });
    return Promise.resolve({ ok: false, json: () => Promise.resolve(null) });
  },
};
sandbox.globalThis = sandbox;
vm.createContext(sandbox);
vm.runInContext(fs.readFileSync(path.join(ROOT, 'site', 'assets', 'app.js'), 'utf8'), sandbox, { filename: 'app.js' });

const failures = [];
function expect(label, actual, want) {
  if (actual !== want) failures.push(`${label}: got ${JSON.stringify(actual)}, want ${JSON.stringify(want)}`);
}
const has = (text, needle) => text.indexOf(needle) >= 0;

setTimeout(() => {
  expect('one cell per trip-window sheet', cells.size, 7);

  const newest = cells.get(sheets[0]).textContent;
  expect('the newest recorded run wins', has(newest, 're-checked 2026-12-30'), true);
  expect('an unchanged document is described as unchanged', has(newest, 'byte-for-byte unchanged'), true);
  expect('a clean re-check is not styled as an alarm', cells.get(sheets[0]).className, 'muted');
  expect('the cell names its source record', has(cells.get(sheets[0]).title, 'site/checks.json'), true);
  expect('the cell refuses to overstate what a hash proves',
    has(cells.get(sheets[0]).title, 'does not re-verify any printed value'), true);

  const changed = cells.get(sheets[1]);
  expect('a re-published sheet is labelled CHANGED', has(changed.textContent, 'CHANGED'), true);
  expect('and says a human must re-read it', has(changed.textContent, 're-read by hand'), true);
  expect('and is styled as a warning', changed.className, 'badge danger');

  const blocked = cells.get(sheets[2]);
  expect('a robot block is not called a source change', has(blocked.textContent, 'CHANGED'), false);
  expect('a robot block says it was blocked', has(blocked.textContent, 'blocked for the robot'), true);

  const missing = cells.get(sheets[3]);
  expect('a sheet with no recorded run says so', missing.textContent, 'no automated re-check recorded');
  expect('and does not invent a date', has(missing.textContent, '20'), false);

  if (failures.length) {
    failures.forEach((f) => console.error('FAIL ' + f));
    process.exit(1);
  }
  console.log(`sheet re-check render OK · ${cells.size} trip-window cells · 4 record states exercised`);
}, 120);
