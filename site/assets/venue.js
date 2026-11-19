/* Detailed venue pages: site/venues/*.html
 *
 * Renders one venue (or a set of venues) from the canonical site/data.json:
 * every published row for that room, then the hotels attached to it.
 * Adapted to the canonical data model by the integration session; the page
 * structure and the search boxes come from the prior session's venue pages.
 */
(function () {
  const venueAttr = document.body.dataset.venue || '';
  const venuesAttr = document.body.dataset.venues || '';
  const selected = venueAttr ? [venueAttr] :
    venuesAttr.split(',').map(String).map((s) => s.trim()).filter(Boolean);
  const root = location.pathname.includes('/venues/') ? '..' : '.';

  function cell(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, (m) =>
      ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[m]));
  }
  function link(url, label) {
    if (!url) return '';
    return '<a href="' + cell(url) + '" target="_blank" rel="noopener">' + cell(label) + '</a>';
  }
  function money(n) {
    return (typeof n === 'number' && isFinite(n)) ? '$' + n.toLocaleString('en-US') : '';
  }
  function entryBadge(e) {
    const status = e.rules && e.rules.singleEntry ? e.rules.singleEntry.status : 'not-verified';
    const map = {
      'single-entry-on-sheet': ['ok', 'Single entry on the sheet'],
      'none-printed': ['ok', 'No re-entry, rebuy or add-on printed'],
      'multiple-entries': ['warn', 'More than one entry possible'],
      'multi-buyin': ['warn', 'More than one entry possible'],
      'separate-flights': ['warn', 'Separate start flights'],
      // Printed cap on starting flights, but one paid re-entry is still allowed: not a one-entry event.
      'one-flight-cap': ['warn', 'One entry per flight + one re-entry'],
      'not-verified': ['bad', 'Entry rules not verified'],
      'not-allowed': ['ok', 'Re-entry not allowed'],
      'allowed': ['warn', 'Allowed'],
      'none': ['ok', 'None printed'],
      'paid-chip-gratuity': ['warn', 'Optional paid chip boost'],
      'not-cash-tournament': ['info', 'Seat prizes, not cash'],
      'special-format': ['info', 'Special format'],
      'implied-multiple': ['warn', 'Repeated entries expected'],
      'source-conflict': ['bad', 'Official sources disagree'],
      'partial': ['warn', 'Partly published'],
      'confirmed': ['ok', 'Confirmed'],
    };
    const pair = map[status] || ['info', status || 'Not stated'];
    return '<span class="badge ' + pair[0] + '">' + cell(pair[1]) + '</span>';
  }

  /* The scheduled re-check writes site/checks.json. A row whose official page has changed
     text since it was last read is marked here as well as on the main tables, so the venue
     page can never show a stale row without saying so. */
  function sourceBadges(urls) {
    const monitored = checks && Array.isArray(checks.urls) ? checks.urls : [];
    const rows = [...new Set((urls || []).filter(Boolean))]
      .map((url) => monitored.find((row) => row.url === url)).filter(Boolean);
    const out = [];
    const changed = rows.filter((row) => row.changed);
    const blocked = rows.filter((row) => !row.changed && (row.botBlocked || row.outcome === 'blocked' || row.outcome === 'redirected'));
    const unavailable = rows.filter((row) => !row.changed && !blocked.includes(row) &&
      (row.unavailable || row.status === 'unreachable' || /^HTTP [45]/.test(row.status || '')));
    if (changed.length) out.push('<span class="badge bad" title="' + cell(changed.map((r) => (r.label || r.url) + ': ' + (r.checked || '')).join('; ')) + '">Source changed · review</span>');
    if (blocked.length) out.push('<span class="badge info" title="' + cell(blocked.map((r) => (r.label || r.url) + ': ' + (r.status || 'blocked') + ' · ' + (r.checked || '')).join('; ')) + '">Blocked for the robot, not missing · read by hand</span>');
    if (unavailable.length) out.push('<span class="badge warn" title="' + cell(unavailable.map((r) => (r.label || r.url) + ': ' + (r.status || 'unavailable') + ' · ' + (r.checked || '')).join('; ')) + '">Source unavailable · recheck</span>');
    return out.join(' ');
  }

  let checks = null;
  Promise.all([
    fetch(root + '/data.json').then((r) => r.json()),
    fetch(root + '/checks.json').then((r) => (r.ok ? r.json() : null)).catch(() => null),
  ]).then(([d, c]) => {
    checks = c;
    const events = (d.events || []).filter((e) => selected.includes(e.venue));
    const hotels = (d.hotels || []).filter((h) => selected.includes(h.id) || selected.includes(h.venue));
    const ev = document.getElementById('venue-events');
    const ho = document.getElementById('venue-hotels');
    if (ev) ev.innerHTML = '<input type="search" placeholder="Filter events" ' +
      'style="margin-bottom:8px;width:min(320px,100%)">' + renderEvents(events, d);
    if (ho) ho.innerHTML = '<input type="search" placeholder="Filter hotels" ' +
      'style="margin-bottom:8px;width:min(320px,100%)">' + renderHotels(hotels);
    wireSearch(ev);
    wireSearch(ho);
    document.querySelectorAll('[data-asof]').forEach((e) => { e.textContent = d.asOf; });
  }).catch(() => {
    document.querySelectorAll('[data-load-error]').forEach((e) => { e.hidden = false; });
  });

  function renderEvents(events, d) {
    if (!events.length) return '<div class="empty"><strong>No published rows for this venue.</strong></div>';
    const rows = events.map((e) => {
      const venue = (d.venues || []).find((v) => v.id === e.venue);
      return '<tr>' +
        '<td>' + cell(e.date || 'Recurring') + '</td>' +
        '<td>' + cell(e.time || '') + '</td>' +
        '<td>' + cell(e.name) +
        (e.eligibility ? '<div class="muted" style="font-size:11px;margin-top:4px">Restricted: ' + cell(e.eligibility) + '</div>' : '') +
        (venue ? '<div class="muted" style="font-size:11px;margin-top:4px">' + cell(venue.pokerRoom) + '</div>' : '') +
        '</td>' +
        '<td>' + (money(e.buyIn) || '<span class="muted">Not published</span>') + '</td>' +
        '<td>' + (money(e.guarantee) || (e.guarantee ? cell(e.guarantee) : '<span class="muted">Not published</span>')) + '</td>' +
        '<td>' + (typeof e.ratio === 'number' ? e.ratio.toFixed(1) + '×' : '<span class="muted">—</span>') + '</td>' +
        '<td>' + cell(e.format) + '</td>' +
        '<td>' + entryBadge(e) + '</td>' +
        '<td>' + (e.lateReg ? cell(e.lateReg) : '<span class="muted">Not published</span>') + '</td>' +
        '<td>' + (e.lastVerified ? cell(e.lastVerified) : '<span class="muted">Not recorded</span>') +
        (e.lastChecked ? '<div class="muted" style="font-size:11px">values read ' + cell(e.lastChecked) + '</div>' : '') + '</td>' +
        '<td>' + link(e.structureUrl, 'Structure sheet') + ' ' + link(e.scheduleUrl, 'Schedule') +
        ' ' + sourceBadges([e.structureUrl, e.scheduleUrl,
          ...Object.values(e.rules || {}).map((rule) => rule && rule.source)]) + '</td>' +
        '</tr>';
    }).join('');
    return '<div class="table-wrap"><table><thead><tr><th>Date</th><th>Start</th><th>Tournament</th>' +
      '<th>Buy-in</th><th>Guaranteed pool</th><th>Pool ÷ fee</th><th>Format</th>' +
      '<th>Entry check</th><th>Late registration</th><th>Last checked</th><th>Official sources</th></tr></thead>' +
      '<tbody>' + rows + '</tbody></table></div>';
  }

  function renderHotels(hotels) {
    if (!hotels.length) return '<div class="empty"><strong>No hotel rows.</strong></div>';
    const rows = hotels.map((h) => {
      const quote = h.quote
        ? '<div class="muted" style="font-size:11px">Dated official total ' + h.quote.checkIn + ' → ' + h.quote.checkOut +
          ': $' + h.quote.total.toFixed(2) + ' including ' + h.quote.taxes.toFixed(2) + ' tax</div>'
        : '<div class="muted" style="font-size:11px">No dated checkout total in the reviewed material</div>';
      const quoteSources = [h.quote && h.quote.source, ...(h.quotes || []).map((item) => item.source)].filter(Boolean);
      const bookingLinks = h.bookingLinks || [];
      const rowSources = [h.source, h.feeSource, h.taxSource, ...quoteSources,
        ...bookingLinks.map((item) => item.url)].filter(Boolean);
      const quoteLink = h.quote && h.quote.source ? link(h.quote.source, 'Dated quote source') : '';
      const bookingLink = bookingLinks.length ? link(bookingLinks[0].url, 'Official booking link') : '';
      return '<tr>' +
        '<td>' + cell(h.name) + '</td>' +
        '<td>' + cell(h.venue || '') + '</td>' +
        '<td>' + (h.baseRateFloor ? '$' + h.baseRateFloor + ' – $' + h.baseRateCeiling : '<span class="muted">Not published</span>') + '</td>' +
        '<td>' + (h.resortFee ? '$' + h.resortFee + ' plus tax' : '<span class="muted">Not verified</span>') + '</td>' +
        '<td>' + (h.taxRate ? h.taxRate + '%' : '<span class="muted">Percentage not published</span>') + '</td>' +
        '<td>' + (h.trueNightlyLow ? '$' + h.trueNightlyLow.toFixed(2) + ' – $' + h.trueNightlyHigh.toFixed(2) +
          '<div class="muted" style="font-size:11px">floor from published components</div>' : '<span class="muted">Cannot be computed</span>') + quote + '</td>' +
        '<td>' + cell(h.cancellation || 'Not published') + '</td>' +
        '<td>' + cell(h.qualityNote || '') + '</td>' +
        '<td>' + (h.lastChecked ? cell(h.lastChecked) : 'Not recorded') + '</td>' +
        '<td>' + link(h.source, 'Room source') + ' ' + link(h.feeSource, 'Fee terms') + ' ' +
        quoteLink + ' ' + bookingLink + ' ' + sourceBadges(rowSources) + '</td>' +
        '</tr>';
    }).join('');
    return '<div class="table-wrap"><table><thead><tr><th>Hotel</th><th>Poker room</th><th>Published base rate</th>' +
      '<th>Mandatory resort fee</th><th>Tax</th><th>True cost per night</th><th>Cancellation deadline</th>' +
      '<th>Quality evidence</th><th>Last checked</th><th>Official sources</th></tr></thead><tbody>' + rows + '</tbody></table></div>';
  }

  function wireSearch(container) {
    if (!container) return;
    const input = container.querySelector('input');
    if (!input) return;
    input.addEventListener('input', () => {
      const q = input.value.toLowerCase();
      container.querySelectorAll('tbody tr').forEach(function (tr) {
        tr.hidden = !tr.textContent.toLowerCase().includes(q);
      });
    });
  }
})();
