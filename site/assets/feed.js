/* Display recorded downloads, without interpreting them as event verification. */
'use strict';

(() => {
  const host = document.querySelector('[data-feed-results]');
  if (!host) return;
  const escape = (value) => String(value ?? '').replace(/[&<>"']/g, (ch) => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
  }[ch]));
  const isSuccess = (page) => /^HTTP 2\d\d$/.test(page.status);
  const snapshotLink = (page) => isSuccess(page) && /^feed\/[a-z0-9-]+\.txt$/.test(page.snapshot || '')
    ? `<a href="${escape(page.snapshot)}">Open text snapshot</a>`
    : isSuccess(page) ? '<span class="muted">No text captured</span>' : '<span class="muted">No capture</span>';
  const officialUrl = (value) => {
    try {
      const url = new URL(value);
      return url.protocol === 'https:' ? url.href : '';
    } catch (_) {
      return '';
    }
  };

  fetch('feed/index.json').then((response) => {
    if (!response.ok) throw new Error('Feed record unavailable');
    return response.json();
  }).then((record) => {
    const rows = record.rooms.flatMap((room) => room.pages.map((page) => ({ room, page })));
    if (!record.generated || !rows.length) throw new Error('No recorded feed attempts');
    const fetched = rows.filter(({ page }) => isSuccess(page)).length;
    const body = rows.map(({ room, page }) => {
      const url = officialUrl(page.url);
      const success = isSuccess(page);
      return `<tr><th scope="row">${escape(room.name)}</th>
        <td>${url ? `<a href="${escape(url)}">Official source</a>` : 'Source unavailable'}</td>
        <td>${escape(room.fetched || record.generated)}</td>
        <td><span class="badge ${success ? 'ok' : 'warn'}">${success ? 'Fetched' : 'Unavailable to feed'}</span>
          ${escape(page.status)}</td><td>${snapshotLink(page)}</td></tr>`;
    }).join('');
    host.innerHTML = `<p class="toolbar-note">Last run: <time datetime="${escape(record.generated)}">${escape(record.generated)}</time>.
      ${fetched} of ${rows.length} official URLs returned HTTP 2xx across ${record.rooms.length} configured rooms.</p>
      <div class="table-wrap"><table><thead><tr><th scope="col">Poker room</th><th scope="col">Source</th>
      <th scope="col">Attempted at</th><th scope="col">Fetch status</th><th scope="col">Saved evidence</th></tr></thead>
      <tbody>${body}</tbody></table></div>`;
  }).catch(() => {
    host.textContent = 'No feed record could be loaded. The official links below are still available for direct review.';
  });
})();
