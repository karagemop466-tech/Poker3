(function () {
  const venueName = document.body.dataset.venue || '';
  const venuesAttr = document.body.dataset.venues || '';
  const selected = venueName ? [venueName] :
    venuesAttr.split(',').map(String).map(s => s.trim()).filter(Boolean);
  const root = location.pathname.includes('/venues/') ? '..' : '.';

  function cell(s) {
    return String(s ?? '').replace(/[&<>"]/g, m =>
      ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[m]));
  }
  function link(url, label) {
    return '<a href="' + cell(url) + '" target="_blank" rel="noopener">' + cell(label) + '</a>';
  }

  fetch(root + '/data.json').then(r => r.json()).then(d => {
    const events = d.tournaments.filter(t => selected.includes(t.venue));
    const hotels = d.hotels.filter(h => selected.includes(h.venue));
    const ev = document.getElementById('venue-events');
    const ho = document.getElementById('venue-hotels');
    if (ev) ev.innerHTML = '<input type="search" placeholder="Filter events" ' +
      'style="margin-bottom:8px;width:min(320px,100%)">' + renderEvents(events);
    if (ho) ho.innerHTML = '<input type="search" placeholder="Filter hotels" ' +
      'style="margin-bottom:8px;width:min(320px,100%)">' + renderHotels(hotels);
    wireSearch(ev);
    wireSearch(ho);
  }).catch(() => {
    document.querySelectorAll('[data-load-error]').forEach(e => e.hidden = false);
  });

  function renderEvents(events) {
    if (!events.length) return '<div class="empty"><strong>No scheduled events for this venue in the reviewed snapshot.</strong></div>';
    let rows = '';
    events.forEach(r => {
      const ratio = (r.feeRatio ?? {}).value;
      rows += '<tr>' +
        '<td>' + cell(r.date || 'Recurring / undated') + '</td>' +
        '<td>' + cell(r.time || '') + '</td>' +
        '<td>' + cell(r.event || '') + (r.overlapNote ?
          '<div class="muted overlap" style="font-size:11px;margin-top:4px">\u2691 ' + cell(r.overlapNote) + '</div>' : '') + '</td>' +
        '<td>' + cell(r.buyIn || '') + '</td>' +
        '<td>' + cell(r.guarantee || '') + '</td>' +
        (ratio ? '<td style="white-space:nowrap">' + cell(ratio) + '</td>' : '<td class="muted">\u2014</td>') +
        '<td>' + cell(r.format || '') + '</td>' +
        '<td>' + cell(r.entryStatus || 'Not published / unverified') + '</td>' +
        '<td>' + cell(r.lastChecked || '') + '</td>' +
        '<td>' + link(r.schedule, 'Official event schedule') +
        (r.structure ? ' ' + link(r.structure, 'Structure') : '') + '</td>' +
        '</tr>';
    });
    return '<table><thead><tr><th>Date</th><th>Start</th><th>Tournament</th><th>Buy-in</th>' +
      '<th>Guarantee</th><th>Guarantee \u00f7 buy-in</th><th>Format</th>' +
      '<th>Single-entry / spend check</th><th>Last checked</th><th>Official sources</th></tr></thead>' +
      '<tbody>' + rows + '</tbody></table>';
  }

  function renderHotels(hotels) {
    if (!hotels.length) return '<div class="empty"><strong>No hotel records for this venue in the reviewed snapshot.</strong></div>';
    let rows = '';
    hotels.forEach(h => {
      let log = '';
      (h.rateLog || []).forEach(e => {
        log += '<div style="font-size:11px"><div class="muted" style="margin-top:2px">Checked ' + cell(e.date) +
          ' \u00b7 ' + cell(e.rate) + '</div><div class="muted" style="font-size:11px">' + cell(e.note) + '</div></div>';
      });
      rows += '<tr>' +
        '<td>' + cell(h.name) + '</td>' +
        '<td>' + cell(h.venue) + '</td>' +
        '<td>' + cell(h.baseRate || '') + '</td>' +
        '<td>' + cell(h.resortFee || '') + '</td>' +
        '<td>' + cell(h.taxes || '') + '</td>' +
        '<td class="muted">' + (h.trueNightly ? cell(h.trueNightly) : 'blank \u2014 no date-specific quote') + '</td>' +
        '<td>' + cell(h.walking || '') + '</td>' +
        '<td>' + cell(h.rateNote || '') + log + '</td>' +
        '<td>' + cell(h.status || '') + '</td>' +
        '<td>' + cell(h.lastChecked || '') + '</td>' +
        '<td>' + link(h.source, 'Hotel') +
        ' ' + link(h.feeSource, 'Fee') +
        (h.taxSource ? ' ' + link(h.taxSource, 'Tax') : '') +
        (h.feeSourceAlt ? ' ' + link(h.feeSourceAlt, 'Older fee (flagged)') : '') + '</td>' +
        '</tr>';
    });
    return '<table><thead><tr><th>Hotel</th><th>Venue</th><th>Nightly base rate</th><th>Resort fee</th>' +
      '<th>Tax information</th><th>True total / night</th><th>Walking context</th>' +
      '<th>Rate conditions + dated log</th><th>Assessment</th><th>Last checked</th><th>Official sources</th></tr></thead>' +
      '<tbody>' + rows + '</tbody></table>';
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
