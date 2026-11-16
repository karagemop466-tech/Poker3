/* Headless render check for the canonical dashboard.
 *
 * Loads site/data.json, stubs just enough DOM for site/assets/app.js, runs the
 * script for every page type and reports what each page rendered.  Run with:
 *
 *   node tests/canonical_render.js
 */
'use strict';

const fs = require('fs');
const path = require('path');
const vm = require('vm');

const ROOT = path.resolve(__dirname, '..');
const data = JSON.parse(fs.readFileSync(path.join(ROOT, 'site', 'data.json'), 'utf8'));

function makeElement(selector) {
  const el = {
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
  return el;
}

const registry = new Map();
function hook(selector) {
  if (!registry.has(selector)) registry.set(selector, makeElement(selector));
  return registry.get(selector);
}

function runPage(page, search) {
  registry.clear();
  const body = { dataset: { page } };
  const document = {
    body,
    querySelector(sel) { return hook(sel); },
    querySelectorAll(sel) { return [hook(sel)]; },
  };
  const location = {
    pathname: '/' + (page === 'home' ? 'index.html' : page + '.html'),
    search: search || '',
    href: '',
  };
  const sandbox = {
    document,
    location,
    URLSearchParams,
    console,
    fetch: (url) => {
      if (String(url).endsWith('data.json')) {
        return Promise.resolve({ ok: true, json: () => Promise.resolve(data) });
      }
      return Promise.resolve({ ok: false, json: () => Promise.resolve(null) });
    },
  };
  sandbox.globalThis = sandbox;
  vm.createContext(sandbox);
  const code = fs.readFileSync(path.join(ROOT, 'site', 'assets', 'app.js'), 'utf8');
  vm.runInContext(code, sandbox, { filename: 'app.js' });
  return new Promise((resolve) => setTimeout(() => resolve(registry), 60));
}

const PAGES = [
  ['home', ''],
  ['tournaments', ''],
  ['venues', ''],
  ['browse', '?view=venue&key=wynn'],
  ['browse', '?view=category&key=extra'],
  ['hotels', ''],
  ['schedule', ''],
  ['questions', ''],
  ['suggestions', ''],
  ['flagged', ''],
  ['sources', ''],
];

(async () => {
  let failures = 0;
  for (const [page, search] of PAGES) {
    const reg = await runPage(page, search);
    let total = 0;
    reg.forEach((el) => { total += el.html.length + el.text.length; });
    const label = page + (search ? search : '');
    const table = reg.get('[data-tournament-table]');
    const rows = table ? (table.html.match(/row-click/g) || []).length : 0;
    if (total < 500) {
      console.log(`FAIL  ${label}: rendered only ${total} characters`);
      failures++;
    } else if (page === 'tournaments' && rows < 10) {
      console.log(`FAIL  ${label}: only ${rows} tournament rows rendered`);
      failures++;
    } else {
      console.log(`ok    ${label}: rendered ${total} characters` + (page === 'tournaments' ? `, ${rows} rows` : ''));
    }
  }
  if (failures) {
    console.log(`\n${failures} page(s) did not render`);
    process.exit(1);
  }
  console.log('\nall pages rendered');
})();
