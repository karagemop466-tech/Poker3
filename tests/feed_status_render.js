'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const code = fs.readFileSync('site/assets/feed-status.js', 'utf8');

function element() {
  return {
    children: [], hidden: true, textContent: '',
    append(child) { this.children.push(child); },
    replaceChildren(child) { this.children = [child]; },
  };
}
async function render(feed) {
  const elements = new Map(['status', 'results', 'rows'].map((k) => [`[data-feed-${k}]`, element()]));
  vm.runInNewContext(code, {
    URL,
    fetch: async (url) => {
      assert.equal(url, 'feed/index.json');
      return { ok: !!feed, json: async () => feed };
    },
    document: {
      querySelector: (sel) => elements.get(sel),
      createElement: element,
      createDocumentFragment: element,
    },
  });
  await new Promise(setImmediate);
  return ['status', 'results', 'rows'].map((k) => elements.get(`[data-feed-${k}]`));
}

(async () => {
  const published = JSON.parse(fs.readFileSync('site/feed/index.json', 'utf8'));
  const [current, table, rendered] = await render(published);
  assert.match(current.textContent, /^Latest published run:/);
  assert.equal(table.hidden, false);
  const publishedRows = rendered.children[0].children;
  const pages = published.rooms.flatMap((room) => room.pages);
  assert.equal(publishedRows.length, pages.length);
  for (const [i, page] of pages.entries()) {
    const source = publishedRows[i].children[1].children[0];
    assert.equal(source.href, new URL(page.url).href);
    if (page.snapshot) {
      assert.equal(publishedRows[i].children[3].children[0].href, page.snapshot);
      assert.ok(fs.existsSync(`site/${page.snapshot}`));
    }
  }
  const [fixtureStatus, , fixture] = await render({
    generated: '2026-11-19T12:10:00Z',
    rooms: [{ name: 'Test room', pages: [
      { url: 'https://example.com/schedule.pdf', status: 'HTTP 200', outcome: 'pdf-fingerprint', hash: 'f'.repeat(64) },
      { url: 'https://example.com/redirect', status: 'HTTP 302' },
      { url: 'javascript:alert(1)', status: 'HTTP 200', snapshot: 'feed/../file.txt' },
    ] }],
  });
  assert.match(fixtureStatus.textContent, /3 requests · 1 unavailable/);
  const [pdf, redirect, bad] = fixture.children[0].children;
  assert.match(pdf.children[2].textContent, /PDF fingerprint only/);
  assert.match(pdf.children[3].textContent, /SHA-256/);
  assert.match(redirect.children[2].textContent, /Unavailable/);
  assert.equal(bad.children[1].children.length, 0);
  assert.equal(bad.children[3].children.length, 0);
  const [missing, hidden] = await render(null);
  assert.match(missing.textContent, /No morning-feed record/);
  assert.equal(hidden.hidden, true);
})().catch((err) => { console.error(err); process.exitCode = 1; });
