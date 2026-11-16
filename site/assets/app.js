const navItems = [
  ['index.html', 'Overview', '\u25a6'],
  ['tournaments.html', 'Tournaments', '\u2660'],
  ['venues/index.html', 'Venues', '\u2302'],
  ['schedule.html', 'Day plan', '\u25f7'],
  ['calculator.html', 'Trip cost', '\u26a1'],
  ['questions.html', 'Open questions', '\u003f'],
  ['suggestions.html', 'Suggestions', '\u2726'],
  ['flagged.html', 'Flagged for review', '\u2691']
];
const file = location.pathname.split('/').pop() || 'index.html';
const inVenues = location.pathname.startsWith('/Poker3/venues/') ||
  location.pathname.startsWith('./venues/') || /^venues\//.test(location.pathname);

function nav() {
  const links = navItems.map(([href, label, icon]) =>
    '<a href="' + href + '" class="' + (file === href ||
    (inVenues && href === 'venues/index.html') ? 'active' : '') +
    '"><span class="ico">' + icon + '</span>' + label + '</a>').join('');
  document.querySelectorAll('[data-nav]').forEach(n => n.innerHTML = links);
  document.querySelectorAll('[data-mobile-nav]').forEach(n =>
    n.innerHTML = navItems.map(([href, label]) =>
      '<a href="' + href + '" class="' + (file === href ||
      (inVenues && href === 'venues/index.html') ? 'active' : '') +
      '">' + label + '</a>').join(''));
}
nav();

let db;
const tableState = new Map();

function cell(s) {
  return String(s ?? '').replace(/[&<>"]/g, m =>
    ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[m]));
}

function links(row) {
  return '<a href="' + cell(row.schedule) +
    '" target="_blank" rel="noopener">' +
    cell(row.scheduleLabel || 'Official event schedule') + '</a>' +
    (row.confirmSource ?
      '<span class="muted"><a href="' + cell(row.confirmSource) +
      '" target="_blank" rel="noopener">Current official room page / confirmation</a></span>' : '') +
    (row.structure ?
      '<span class="muted"><a href="' + cell(row.structure) +
      '" target="_blank" rel="noopener">Structure / event detail</a></span>' : '');
}

function hotelLinks(r) {
  return '<a href="' + cell(r.source) +
    '" target="_blank" rel="noopener">Official hotel source</a>' +
    '<span class="muted"><a href="' + cell(r.feeSource) +
    '" target="_blank" rel="noopener">Resort-fee source</a></span>' +
    '<span class="muted"><a href="' + cell(r.taxSource) +
    '" target="_blank" rel="noopener">Tax / hotel terms</a></span>' +
    (r.feeSourceAlt ?
      '<span class="muted"><a href="' + cell(r.feeSourceAlt) +
      '" target="_blank" rel="noopener">Older offer fee (flagged)</a></span>' : '');
}

function ruleChip(rule) {
  const v = String(rule.value ?? '').trim();
  const st = String(rule.status ?? '');
  return '<span class="muted" style="font-size:11px">' +
    (v ? cell(rule.value) + ' \u00b7 ' : '') + cell(st) +
    ' (checked ' + cell(rule.retrievalDate) + ')</span>';
}

function singleEntryMatch(row) {
  const re = ((row.rules ?? {}).singleEntry ?? {});
  return String(re.value ?? '').trim() !== '' ||
    String(re.status ?? '').toLowerCase().includes('confirmed');
}

function renderTable(el, rows) {
  const type = el.dataset.list;
  let cols = type === 'hotels' ?
    [['name', 'Hotel'], ['venue', 'Tournament venue'], ['baseRate', 'Nightly base rate'],
     ['resortFee', 'Resort fee'], ['taxes', 'Published tax information'],
     ['trueNightly', 'True total / night'], ['qualityNote', 'Quality evidence'],
     ['walking', 'Walking context'], ['rateNote', 'Rate conditions'],
     ['status', 'Assessment'], ['lastChecked', 'Last checked']] :
    [['date', 'Date'], ['time', 'Start'], ['venue', 'Venue'], ['event', 'Tournament'],
     ['buyIn', 'Buy-in'], ['guarantee', 'Guaranteed prize pool'],
     ['feeRatio', 'Guarantee \u00f7 buy-in'], ['format', 'Format'],
     ['entryStatus', 'Single-entry / spend check'], ['lastChecked', 'Last checked']];
  let html = '<div class="table-tools"><input type="search" ' +
    'placeholder="Filter rows" aria-label="Filter table">' +
    '<span class="toolbar-note">' + rows.length +
    ' rows \u00b7 use official links in the final column to verify details</span></div>' +
    '<div class="table-wrap"><table><thead><tr>' +
    cols.map(c => '<th>' + c[1] + '</th>').join('') +
    '<th>Official sources</th></tr></thead><tbody>' +
    rows.map(r => {
      const ev = type !== 'hotels';
      const overlap = ev && String(r.overlapNote ?? '').trim() ?
        '<div class="muted overlap" style="font-size:11px;margin-top:4px">\u2691 ' +
        cell(r.overlapNote) + '</div>' : '';
      const ratio = ev && (r.feeRatio ?? {}).value ?
        '<span style="white-space:nowrap">' + cell((r.feeRatio ?? {}).value) +
        '</span><span class="muted" style="font-size:11px;display:block">' +
        'descriptive ratio \u00b7 not a forecast</span>' :
        '<span class="muted">\u2014</span>';
      const entryCell = ev ?
        '<div>' + cell(r.entryStatus || 'Not published / unverified') + '</div>' +
        ruleChip((r.rules ?? {}).singleEntry) + overlap : '';
      return '<tr>' + cols.map(c => {
        if (c[0] === 'lastChecked') {
          return '<td>' + cell(r.lastChecked ?? '') + '</td>';
        }
        if (c[0] === 'feeRatio') {
          return '<td>' + ratio + '</td>';
        }
        if (ev && c[0] === 'event') {
          return '<td>' + cell(r[c[0]]) + '</td>' + overlap;
        }
        if (ev && c[0] === 'entryStatus') {
          return '<td>' + entryCell + '</td>';
        }
        return '<td>' + cell(r[c[0]]) + '</td>';
      }).join('') +
      '<td>' + (ev ? links(r) : hotelLinks(r)) + '</td></tr>';
    }).join('') + '</tbody></table></div>';
  el.innerHTML = html;
  const input = el.querySelector('input');
  input?.addEventListener('input', () => {
    const q = input.value.toLowerCase();
    el.querySelectorAll('tbody tr').forEach(tr =>
      tr.hidden = !tr.textContent.toLowerCase().includes(q));
  });
}

function initTables() {
  document.querySelectorAll('[data-list]').forEach(el => {
    const type = el.dataset.list;
    let rows = [];
    if (type === 'events') rows = db.tournaments.filter(x => x.bucket === 'review');
    if (type === 'spend') rows = db.tournaments.filter(x => x.bucket === 'spend-review');
    if (type === 'all-events') rows = db.tournaments;
    if (type === 'hotels') rows = db.hotels;
    tableState.set(el, { type, rows, el });
    renderTable(el, rows);
  });
}

function applyFilters() {
  document.querySelectorAll('[data-list]').forEach(el => {
    const st = tableState.get(el);
    if (!st) return;
    const q = document.getElementById('dateFilter');
    const d = q ? q.value : '';
    const se = document.getElementById('singleEntryFilter');
    const only = se && se.checked;
    const filtered = st.rows.filter(r => {
      if (st.type !== 'hotels' && d && String(r.date ?? '') !== d) return false;
      if (only) {
        const re = ((r.rules ?? {}).singleEntry ?? {});
        if (String(re.value ?? '').trim() === '' &&
          !String(re.status ?? '').toLowerCase().includes('confirmed')) return false;
      }
      return true;
    });
    renderTable(el, filtered);
    const note = el.querySelector('.toolbar-note');
    if (note) {
      note.textContent = filtered.length +
        (d ? ' rows match ' + d : '') +
        ' rows \u00b7 use official links in the final column to verify details' +
        (only ? ' \u2014 no row is confirmed single-entry at this snapshot; ' +
          'missing rules are left blank, not relabeled' : '');
    }
  });
}

function wireFilters() {
  const dateInput = document.getElementById('dateFilter');
  const seInput = document.getElementById('singleEntryFilter');
  const clearBtn = document.getElementById('clearFilters');
  dateInput?.addEventListener('change', applyFilters);
  seInput?.addEventListener('change', applyFilters);
  clearBtn?.addEventListener('click', () => {
    if (dateInput) dateInput.value = '';
    if (seInput) seInput.checked = false;
    applyFilters();
  });
}

fetch('data.json').then(r => r.json()).then(d => {
  db = d;
  initTables();
  document.querySelectorAll('[data-count]').forEach(el => {
    const type = el.dataset.count;
    el.textContent = type === 'events' ? d.tournaments.length :
      type === 'needsreview' ? d.tournaments.filter(x => x.bucket !== 'eligible').length :
      type === 'hotels' ? d.hotels.length : '\u2014';
  });
  document.querySelectorAll('[data-asof]').forEach(e => e.textContent = d.asOf);
  wireFilters();
}).catch(() => {
  document.querySelectorAll('[data-load-error]').forEach(e => e.hidden = false);
});
