/* Render the scheduled retrieval log, not a second tournament catalog. */
(() => {
  'use strict';

  const status = document.querySelector('[data-feed-status]');
  const table = document.querySelector('[data-feed-results]');
  const rows = document.querySelector('[data-feed-rows]');
  if (!status || !table || !rows) return;

  function officialLink(url) {
    try {
      const parsed = new URL(url);
      return parsed.protocol === 'https:' && !parsed.username && !parsed.password ? parsed : null;
    } catch {
      return null;
    }
  }

  function outcome(page) {
    // Older runs predate the explicit outcome field. Keep them readable without
    // describing an HTTP 302 (or an empty response) as a successful capture.
    if (!/^HTTP 2\d\d$/.test(page.status) || page.outcome === 'unavailable') return 'Unavailable';
    if (page.snapshot) return 'Text captured';
    if (page.outcome === 'pdf-fingerprint' || (/pdf/i.test(page.contentType || '') && page.hash)) {
      return 'PDF fingerprint only';
    }
    return 'No text captured';
  }

  function cell(tr, text) {
    const td = document.createElement('td');
    td.textContent = text;
    tr.append(td);
    return td;
  }

  function link(td, url, label) {
    const a = document.createElement('a');
    a.href = url;
    a.textContent = label;
    td.replaceChildren(a);
  }

  async function render() {
    try {
      const response = await fetch('feed/index.json');
      if (!response.ok) throw new Error('Feed record unavailable');
      const feed = await response.json();
      if (!Array.isArray(feed.rooms) || !feed.generated || !Number.isFinite(Date.parse(feed.generated))) {
        throw new Error('Invalid feed record');
      }
      const fragment = document.createDocumentFragment();
      let count = 0;
      let unavailable = 0;
      for (const room of feed.rooms) {
        for (const page of Array.isArray(room.pages) ? room.pages : []) {
          const tr = document.createElement('tr');
          cell(tr, room.name || room.id);
          const source = cell(tr, 'Source link unavailable');
          const url = officialLink(page.url);
          if (url) {
            const filename = url.pathname.split('/').pop();
            link(source, url.href, filename ? `${url.hostname} · ${filename}` : url.hostname);
          }
          const result = outcome(page);
          cell(tr, `${result}${page.status ? ` · ${page.status}` : ''}`);
          const evidence = cell(tr, '—');
          if (result === 'Text captured' && /^feed\/[a-z0-9_-]+\.txt$/i.test(page.snapshot)) {
            link(evidence, page.snapshot, 'Read text snapshot');
          } else if (result === 'PDF fingerprint only' && /^[a-f0-9]{64}$/.test(page.hash)) {
            evidence.textContent = `SHA-256: ${page.hash.slice(0, 12)}… (full hash in raw record)`;
          }
          fragment.append(tr);
          count += 1;
          if (result === 'Unavailable') unavailable += 1;
        }
      }
      const timestamp = new Date(feed.generated).toISOString().slice(0, 16).replace('T', ' ');
      status.textContent = count
        ? `Latest published run: ${timestamp} UTC · ${count} requests · ${unavailable} unavailable.`
        : `Published run: ${timestamp} UTC · no source results recorded.`;
      rows.replaceChildren(fragment);
      table.hidden = count === 0;
    } catch {
      status.textContent = 'No morning-feed record could be loaded. This does not say whether any room is open.';
    }
  }

  render();
})();
