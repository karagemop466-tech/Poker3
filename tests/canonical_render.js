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
const fixtureEvent = data.events.find((event) => event.venue === 'venetian' && event.scheduleUrl);
const transcriptionPath = path.join(ROOT, 'site', 'checks.json');
const liveChecks = fs.existsSync(transcriptionPath) ? JSON.parse(fs.readFileSync(transcriptionPath, 'utf8')) : null;
const feedPath = path.join(ROOT, 'site', 'feed', 'index.json');
const feed = JSON.parse(fs.readFileSync(feedPath, 'utf8'));
const checksFixture = {
  transcription: liveChecks && liveChecks.transcription,
  lastRun: '2026-11-17T13:00:00+00:00',
  note: 'Test fixture only: a changed source is shown for UI verification.',
  urls: [{
    url: fixtureEvent.scheduleUrl,
    label: 'Fixture schedule',
    checked: '2026-11-17T13:00:00+00:00',
    status: 'HTTP 200',
    hash: 'new-hash',
    previousHash: 'old-hash',
    changed: true,
    unavailable: false,
  }, {
    url: fixtureEvent.structureUrl,
    label: 'Fixture structure',
    checked: '2026-11-17T13:00:00+00:00',
    status: 'HTTP 403',
    changed: false,
    unavailable: true,
  }],
};
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
    pathname: '/' + (page === 'home' ? 'index.html' : page === 'global-search' ? 'search.html' : page + '.html'),
    search: search || '',
    href: 'https://example.test/' + (page === 'global-search' ? 'search.html' : page + '.html') + (search || ''),
  };
  const sandbox = {
    document,
    location,
    URLSearchParams,
    URL,
    console,
    fetch: (url) => {
      if (String(url).endsWith('data.json')) {
        return Promise.resolve({ ok: true, json: () => Promise.resolve(data) });
      }
      if (String(url).endsWith('checks.json')) {
        return Promise.resolve({ ok: true, json: () => Promise.resolve(checksFixture) });
      }
      if (url === 'feed/index.json') {
        return Promise.resolve({ ok: true, json: () => Promise.resolve(feed) });
      }
      return Promise.resolve({ ok: false, json: () => Promise.resolve(null) });
    },
  };
  sandbox.globalThis = sandbox;
  vm.createContext(sandbox);
  const code = fs.readFileSync(path.join(ROOT, 'site', 'assets', 'app.js'), 'utf8');
  vm.runInContext(code, sandbox, { filename: 'app.js' });
  if (page === 'sources') {
    const feedCode = fs.readFileSync(path.join(ROOT, 'site', 'assets', 'feed.js'), 'utf8');
    vm.runInContext(feedCode, sandbox, { filename: 'feed.js' });
  }
  if (page === 'global-search') {
    const searchCode = fs.readFileSync(path.join(ROOT, 'site', 'assets', 'search.js'), 'utf8');
    vm.runInContext(searchCode, sandbox, { filename: 'search.js' });
  }
  return new Promise((resolve) => setTimeout(() => resolve(registry), 100));
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
  ['global-search', '?q=venetian'],
  ['calculator', ''],
];

/* The detailed venue pages use their own script and their own data attributes. */
function runVenuePage(venueAttr) {
  registry.clear();
  const body = { dataset: { venue: venueAttr } };
  const document = {
    body,
    querySelector(sel) { return hook(sel); },
    querySelectorAll(sel) { return [hook(sel)]; },
    getElementById(id) { return hook('#' + id); },
  };
  const sandbox = {
    document,
    location: { pathname: '/venues/venetian.html', search: '' },
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
  const code = fs.readFileSync(path.join(ROOT, 'site', 'assets', 'venue.js'), 'utf8');
  vm.runInContext(code, sandbox, { filename: 'venue.js' });
  return new Promise((resolve) => setTimeout(() => resolve(registry), 60));
}

(async () => {
  let failures = 0;
  for (const venue of ['venetian', 'wynn']) {
    const reg = await runVenuePage(venue);
    const ev = reg.get('#venue-events');
    const ho = reg.get('#venue-hotels');
    const evRows = ev ? (ev.html.match(/<tr>/g) || []).length : 0;
    const hoRows = ho ? (ho.html.match(/<tr>/g) || []).length : 0;
    if (evRows < 5 || hoRows < 1) {
      console.log(`FAIL  venue page ${venue}: ${evRows} event rows, ${hoRows} hotel rows`);
      failures++;
    } else {
      console.log(`ok    venue page ${venue}: ${evRows} event rows, ${hoRows} hotel rows`);
    }
  }
  for (const [page, search] of PAGES) {
    const reg = await runPage(page, search);
    let total = 0;
    reg.forEach((el) => { total += el.html.length + el.text.length; });
    const label = page + (search ? search : '');
    // Content assertions: a page that renders but omits a card is still a failure.
    if (page === 'sources') {
      const rendered = reg.get('[data-feed-results]').html;
      const feedPages = feed.rooms.flatMap((room) => room.pages);
      if (!rendered.includes(feed.generated) || (rendered.match(/<tr>/g) || []).length !== feedPages.length + 1 ||
          (rendered.match(/Open text snapshot/g) || []).length !== feedPages.filter((page) => page.snapshot).length ||
          (rendered.match(/Unavailable to feed/g) || []).length !== feedPages.filter((page) => !/^HTTP 2\d\d$/.test(page.status)).length) {
        console.log('FAIL  sources: morning feed row count, timestamps, availability, or evidence links are wrong');
        failures++;
      }
    }
    if (page === 'global-search' && !reg.get('[data-search-results]').html.includes('Morning feed attempt')) {
      console.log('FAIL  search: the morning feed attempt did not render');
      failures++;
    }
    if (page === 'hotels') {
      const pr = reg.get('[data-poker-rate]');
      if (!pr || !/poker-suite rate is held only if/.test(pr.html)) {
        console.log('FAIL  hotels: the poker-rate requirement card did not render');
        failures++;
      }
    }
    if (page === 'schedule') {
      const dp = reg.get('[data-plan]') || reg.get('[data-plan-summary]');
      if (!dp || !/2026-11-23/.test(dp.html + (reg.get('[data-plan-summary]') || {}).html)) {
        console.log('FAIL  schedule: the day plan does not start on the recommended trip date');
        failures++;
      }
    }
    const table = reg.get('[data-tournament-table]');
    const rows = table ? (table.html.match(/row-click/g) || []).length : 0;
    if (page === 'tournaments' && (!table.html.includes('Last checked / verified') || !table.html.includes('Source changed · review') || !table.html.includes('Source unavailable · recheck') || !reg.get('[data-filters]').html.includes('Single-entry / freezeout confirmed'))) {
      console.log(`FAIL  ${label}: row-level dates, source status badges or strict-entry filter are missing`);
      failures++;
    }
    if (page === 'schedule') {
      const plan = reg.get('[data-plan]');
      if (!plan || !plan.html.includes('Poker-rate condition for the night stayed')) {
        console.log(`FAIL  ${label}: the per-night poker-rate result did not render on the day plan`);
        failures++;
      }
    }
    if (page === 'hotels') {
      const table = reg.get('[data-hotel-table]');
      const log = reg.get('[data-rate-log]');
      if (!table || !table.html.includes('$54.95 plus tax') || !table.html.includes('$49.95 plus tax')) {
        console.log(`FAIL  ${label}: the Caesars Palace and Horseshoe resort fees did not render`);
        failures++;
      }
      if (!table || !table.html.includes('room-tax schedule')) {
        console.log(`FAIL  ${label}: the county room-tax reference did not render beside a blank property figure`);
        failures++;
      }
      if (!log || !log.html.includes('calendar cells for Nov. 16-30') || log.html.includes('$calendar')) {
        console.log(`FAIL  ${label}: dated rate-log observations did not render correctly`);
        failures++;
      }
    }
    if (page === 'sources') {
      const auto = reg.get('[data-autochecks]');
      if (!auto || !auto.html.includes('Content changed · manual review')) {
        console.log(`FAIL  ${label}: automated source-check status did not render`);
        failures++;
      }
    }
    if (page === 'global-search') {
      const results = reg.get('[data-search-results]');
      const wanted = ['Tournament', 'Hotel', 'Hotel rate log', 'Walking route', 'Official source',
        'Structure sheet', 'Morning schedule feed', 'Strip poker room coverage', 'Dated hotel booking link',
        'Dated hotel checkout quote', 'Hotel stay with no published quote', 'Hotel booking-calendar observation',
        'Per-date hotel booking link', 'Primary day-plan event', 'Conditional fallback event', 'Schedule overlap check',
        'Flag ·', 'Open question', 'Improvement suggestion', 'Trip cost model',
        'Automated official-source re-check', 'Official PDF transcription check', 'Source changed · review'];
      const missing = wanted.filter((labelText) => !results || !results.html.includes(labelText));
      if (missing.length) {
        console.log(`FAIL  ${label}: cross-table search missed ${missing.join(', ')}`);
        failures++;
      }
    }
    if (total < 500) {
      console.log(`FAIL  ${label}: rendered only ${total} characters`);
      failures++;
    } else if (page === 'tournaments' && rows < 10) {
      console.log(`FAIL  ${label}: only ${rows} tournament rows rendered`);
      failures++;
    } else if (page === 'sources') {
      const trans = reg.get('[data-transcription]');
      const tRows = trans ? (trans.html.match(/<tr>/g) || []).length : 0;
      if (tRows < 40) {
        console.log(`FAIL  ${label}: transcription table rendered ${tRows} rows, expected the official 44`);
        failures++;
      } else {
        console.log(`ok    ${label}: rendered ${total} characters, ${tRows} transcription rows`);
      }
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
