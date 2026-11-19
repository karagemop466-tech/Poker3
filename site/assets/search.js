/* Global search for every data-backed table in the canonical dashboard.
 * Values and URLs are read only from the catalog, checks and feed records.
 */
'use strict';

(() => {
  const $ = (selector) => document.querySelector(selector);
  const esc = (value) => String(value == null ? '' : value).replace(/[&<>"']/g, (ch) => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
  }[ch]));
  const money = (value) => (typeof value === 'number' && Number.isFinite(value)
    ? '$' + value.toLocaleString('en-US', { maximumFractionDigits: 2 }) : '');
  const normalize = (value) => String(value == null ? '' : value).toLowerCase()
    .normalize('NFKD').replace(/[\u0300-\u036f]/g, '');
  const flatten = (value) => {
    if (value == null) return '';
    if (Array.isArray(value)) return value.map(flatten).join(' ');
    if (typeof value === 'object') return Object.values(value).map(flatten).join(' ');
    return String(value);
  };
  const httpUrl = (value) => {
    if (typeof value !== 'string') return '';
    try {
      const parsed = new URL(value);
      return parsed.protocol === 'https:' || parsed.protocol === 'http:' ? parsed.href : '';
    } catch (_) {
      return '';
    }
  };

  const host = $('[data-search-results]');
  const summary = $('[data-search-summary]');
  const form = $('[data-global-search-form]');
  const input = form && form.querySelector('[name="q"]');
  if (!host || !summary || !form || !input) return;

  let catalog = null;
  let checks = null;
  let feedRecord = null;
  let records = [];

  function venueName(id) {
    const venue = (catalog.venues || []).find((row) => row.id === id);
    return venue ? venue.name : String(id || '');
  }
  function hotelName(id) {
    const hotel = (catalog.hotels || []).find((row) => row.id === id);
    return hotel ? hotel.name : String(id || '');
  }
  function eventSources(event) {
    if (!event) return [];
    return [event.scheduleUrl, event.structureUrl, event.sheetUrl,
      ...Object.values(event.rules || {}).map((rule) => rule && rule.source)].filter(Boolean);
  }
  function eventFor(id) {
    return (catalog.events || []).find((event) => event.id === id);
  }
  function sourcesForHotel(hotel) {
    return [hotel.source, hotel.feeSource, hotel.taxSource, hotel.parkingSource,
      hotel.cancellationSource, hotel.cancellationDetailSource,
      ...(hotel.quotes || []).map((quote) => quote.source),
      ...(hotel.bookingLinks || []).map((link) => link.url),
      ...(hotel.noQuoteWindows || []).map((window) => window.url),
      hotel.calendarObservation && hotel.calendarObservation.windowA && hotel.calendarObservation.windowA.url,
      hotel.calendarObservation && hotel.calendarObservation.windowB && hotel.calendarObservation.windowB.url]
      .filter(Boolean);
  }
  function changeStatus(url) {
    const row = checks && Array.isArray(checks.urls)
      ? checks.urls.find((item) => item.url === url) : null;
    if (!row) return '';
    const title = esc(`${row.label || row.url}: ${row.checked || ''}`);
    if (row.changed || row.wordingChanged) return `<span class="badge bad" title="${title}">Source changed · review</span>`;
    if (row.botBlocked || row.status === 'blocked') return `<span class="badge info" title="${title}">Blocked for crawler · read by hand</span>`;
    if (row.unavailable || row.status === 'unreachable' || /^HTTP [45]/.test(row.status || '')) {
      return `<span class="badge warn" title="${title}">Source unavailable · recheck</span>`;
    }
    return '';
  }
  function sourceCell(urls, mapUrl, internal) {
    const unique = [...new Set((urls || []).map(httpUrl).filter(Boolean))];
    const links = unique.map((url, index) => {
      const label = unique.length > 1 ? `Official source ${index + 1}` : 'Official source';
      return `<span class="search-source"><a href="${esc(url)}" target="_blank" rel="noopener">${label}</a> ${changeStatus(url)}</span>`;
    });
    const map = httpUrl(mapUrl);
    if (map) links.push(`<span class="search-source"><a href="${esc(map)}" target="_blank" rel="noopener">Google Maps walking estimate</a></span>`);
    if (!links.length && internal) {
      links.push(`<a href="${esc(internal.href)}">${esc(internal.label)}</a>`);
    }
    if (!links.length) links.push('<span class="muted">No source link recorded · see <a href="flagged.html">Flagged for review</a></span>');
    return links.join('<span class="muted"> · </span>');
  }
  function addRecord({ type, group, title, when = '', detail = '', checked = '', sourceUrls = [], mapUrl = '', internal = null, searchable = '' }) {
    const urls = (sourceUrls || []).map(httpUrl).filter(Boolean);
    records.push({
      type, group: group || type, title: String(title || ''), when: String(when || ''),
      detail: String(detail || ''), checked: String(checked || ''), urls, mapUrl: httpUrl(mapUrl), internal,
      searchable: normalize([type, title, when, detail, checked, searchable, urls.join(' ')].join(' ')),
    });
  }

  function indexCatalog() {
    records = [];

    (catalog.venues || []).forEach((venue) => addRecord({
      type: 'Venue', title: venue.name, when: '',
      detail: [venue.pokerRoom, venue.series, venue.note].filter(Boolean).join(' · '),
      checked: catalog.verifiedOn || catalog.asOf,
      sourceUrls: [venue.page, venue.schedule], searchable: flatten(venue),
    }));

    const byEventId = new Map((catalog.events || []).map((event) => [event.id, event]));
    (catalog.events || []).forEach((event) => {
      const ruleText = Object.entries(event.rules || {}).map(([key, rule]) =>
        `${key}: ${rule && rule.status || ''} ${rule && rule.excerpt || ''}`).join(' · ');
      addRecord({
        type: `Tournament · ${venueName(event.venue)}`, group: 'Tournament',
        title: event.name, when: event.date || 'Recurring',
        detail: [event.time, money(event.buyIn), money(event.guarantee), event.format,
          event.category, event.entryType, ruleText, event.note, event.eligibility].filter(Boolean).join(' · '),
        checked: event.lastChecked || '', sourceUrls: eventSources(event), searchable: flatten(event),
      });
    });

    (catalog.hotels || []).forEach((hotel) => addRecord({
      type: 'Hotel', title: hotel.name, when: '',
      detail: [hotel.rooms, hotel.baseRateNote, hotel.resortFeeNote, hotel.taxNote,
        hotel.trueNightlyLow && `True nightly floor ${money(hotel.trueNightlyLow)}`,
        hotel.parking, hotel.cancellation, hotel.status].filter(Boolean).join(' · '),
      checked: hotel.lastChecked || '', sourceUrls: sourcesForHotel(hotel), searchable: flatten(hotel),
    }));

    (catalog.rateLog || []).forEach((row) => addRecord({
      type: 'Hotel rate log', group: 'Rate log', title: hotelName(row.hotel), when: row.observedOn || '',
      detail: [row.publishedStartingRates, row.resortFee, row.tax,
        row.trueNightlyLow && `${money(Number(row.trueNightlyLow))}–${money(Number(row.trueNightlyHigh))} true nightly`,
        row.quoteType, row.note].filter(Boolean).join(' · '),
      checked: row.observedOn || '', sourceUrls: [row.source, row.feeSource, row.taxSource], searchable: flatten(row),
    }));

    (catalog.routes || []).forEach((route) => addRecord({
      type: 'Walking route', title: `${hotelName(route.hotel)} → ${venueName(route.venue)}`,
      when: '', detail: [route.minutes === 0 ? 'On site' : `${route.minutes} minutes`,
        route.miles && `${route.miles} miles`, route.via, route.note, route.walkSourceType].filter(Boolean).join(' · '),
      checked: route.lastChecked || route.lastReadOn || '', sourceUrls: [route.source], mapUrl: route.mapsUrl,
      searchable: flatten(route),
    }));

    (catalog.sources || []).forEach((source) => addRecord({
      type: 'Official source', title: source.name, detail: source.type || '',
      checked: source.checked || '', sourceUrls: [source.url], searchable: flatten(source),
    }));

    (catalog.structureSheets || []).forEach((sheet) => addRecord({
      type: 'Structure sheet', title: `${sheet.series} · sheet ${sheet.sheet}`,
      detail: [venueName(sheet.venue), sheet.read ? 'Read' : 'Not read', sheet.readOn && `read ${sheet.readOn}`,
        sheet.reReadOn && `re-read ${sheet.reReadOn}`, sheet.note].filter(Boolean).join(' · '),
      checked: sheet.reReadOn || sheet.readOn || '', sourceUrls: [sheet.url], searchable: flatten(sheet),
    }));

    (catalog.feed || []).forEach((feed) => addRecord({
      type: 'Morning schedule feed', title: feed.name, detail: 'Official schedule source and extra series pages',
      checked: catalog.asOf || '', sourceUrls: [feed.schedule, ...(feed.extra || [])], searchable: flatten(feed),
    }));

    (feedRecord && feedRecord.rooms || []).forEach((room) => (room.pages || []).forEach((page) => {
      const fetched = /^HTTP 2\d\d$/.test(page.status);
      addRecord({
        type: 'Morning feed attempt', title: room.name, when: feedRecord.date || '',
        detail: [fetched ? 'Fetched' : 'Unavailable to feed', page.status,
          fetched && page.snapshot ? 'Text snapshot recorded' : 'No text captured'].filter(Boolean).join(' · '),
        checked: room.fetched || feedRecord.generated || '', sourceUrls: [page.url],
      });
    }));

    (catalog.stripRooms || []).forEach((room) => addRecord({
      type: 'Strip poker room coverage', title: room.name,
      detail: [room.status, room.statusBasis, room.evidence, room.inFeed ? 'In morning feed' : 'Not in morning feed', room.flag].filter(Boolean).join(' · '),
      checked: room.read || '', sourceUrls: [room.official],
      internal: !room.official ? { href: 'flagged.html', label: 'Review Flagged for review' } : null,
      searchable: flatten(room),
    }));

    (catalog.bookingLinks || []).forEach((booking) => addRecord({
      type: 'Dated hotel booking link', title: booking.property, when: booking.checkedOn || '',
      detail: [booking.stay, booking.priceInStaticPage].filter(Boolean).join(' · '),
      checked: booking.checkedOn || '', sourceUrls: [booking.url, booking.source, booking.feeSource],
      searchable: flatten(booking),
    }));

    (catalog.hotels || []).forEach((hotel) => {
      (hotel.quotes || (hotel.quote ? [hotel.quote] : [])).forEach((quote) => addRecord({
        type: 'Dated hotel checkout quote', title: quote.property || hotel.name,
        when: quote.observedOn || '',
        detail: [quote.checkIn && `${quote.checkIn} → ${quote.checkOut}`,
          quote.nights && `${quote.nights} nights`, quote.total && `checkout ${money(quote.total)}`,
          quote.averageRate && `average ${money(quote.averageRate)}`, quote.offer, quote.note].filter(Boolean).join(' · '),
        checked: quote.observedOn || '', sourceUrls: [quote.source, hotel.feeSource, hotel.taxSource], searchable: flatten(quote),
      }));
      (hotel.noQuoteWindows || []).forEach((window) => addRecord({
        type: 'Hotel stay with no published quote', title: hotel.name,
        when: `${window.checkIn || ''} → ${window.checkOut || ''}`,
        detail: [window.nights && `${window.nights} nights`, window.result].filter(Boolean).join(' · '),
        checked: hotel.lastChecked || '', sourceUrls: [window.url], searchable: flatten(window),
      }));
      const observation = hotel.calendarObservation;
      if (observation) {
        [observation.windowA, observation.windowB].filter(Boolean).forEach((window) => {
          (window.cells || []).forEach(([date, value]) => addRecord({
            type: 'Hotel booking-calendar observation', title: `${hotel.name} · ${date}`,
            when: date, detail: `${window.label || 'Calendar'}: ${value === 'placeholder' ? '$XXX placeholder' : value === '' ? 'no price' : money(value)}; calendar cells are not checkout quotes`,
            checked: observation.observedOn || '', sourceUrls: [window.url], searchable: flatten([observation.footnote, window.label, date, value]),
          }));
        });
      }
      (hotel.bookingLinks || []).forEach((link) => addRecord({
        type: 'Per-date hotel booking link', title: `${hotel.name} · ${link.label || 'official booking page'}`,
        detail: link.note || 'Official date-specific booking link; rate is not inferred from the link.',
        checked: hotel.lastChecked || '', sourceUrls: [link.url], searchable: flatten(link),
      }));
    });

    (catalog.dayPlan || []).forEach((day) => {
      for (const [kind, id, fallbackName, time, buyIn, guarantee, reason] of [
        ['Primary day-plan event', day.primary, day.primaryName, day.primaryTime, day.primaryBuyIn, day.primaryGuarantee, day.pokerRateBasis],
        ['Conditional fallback event', day.fallback, day.fallbackName, day.fallbackTime, day.fallbackBuyIn, day.fallbackGuarantee, day.fallbackReason],
      ]) {
        const event = byEventId.get(id);
        addRecord({
          type: kind, group: 'Day plan', title: event ? event.name : fallbackName || id,
          when: day.date || '',
          detail: [venueName(event ? event.venue : kind === 'Primary day-plan event' ? day.primaryVenue : day.fallbackVenue),
            time && `starts ${time}`, money(buyIn), money(guarantee), reason].filter(Boolean).join(' · '),
          checked: event && event.lastChecked || '', sourceUrls: eventSources(event),
          searchable: flatten(day),
        });
      }
      (day.recurring || []).forEach((item) => {
        const event = (catalog.events || []).find((row) => row.venue === item.venue && row.name === item.name && row.time === item.time);
        addRecord({
          type: 'Recurring day-plan event', group: 'Day plan', title: item.name,
          when: day.date || '', detail: [venueName(item.venue), item.time, money(item.buyIn), item.walk && `${item.walk} min walk`].filter(Boolean).join(' · '),
          checked: event && event.lastChecked || '', sourceUrls: eventSources(event), searchable: flatten(item),
        });
      });
    });

    (catalog.planConflicts || []).forEach((conflict) => {
      const first = byEventId.get(conflict.first);
      const second = byEventId.get(conflict.second);
      addRecord({
        type: 'Schedule overlap check', group: 'Schedule check', title: `${conflict.firstName} ↔ ${conflict.secondName}`,
        when: conflict.date || '',
        detail: conflict.detail || '',
        checked: [first && first.lastChecked, second && second.lastChecked].filter(Boolean).sort().join(' · '),
        sourceUrls: [...eventSources(first), ...eventSources(second)], searchable: flatten(conflict),
      });
    });

    (catalog.flags || []).forEach((flag) => addRecord({
      type: `Flag · ${flag.severity || ''}`, group: 'Flagged for review', title: flag.title,
      detail: [flag.id, flag.area, flag.detail].filter(Boolean).join(' · '),
      checked: catalog.asOf || '', sourceUrls: [flag.source], searchable: flatten(flag),
    }));

    (catalog.questions || []).forEach((question) => addRecord({
      type: 'Open question', group: 'Questions', title: question.question,
      detail: [question.answer, question.why, question.how, question.blocking].filter(Boolean).join(' · '),
      checked: catalog.asOf || '', sourceUrls: [question.source], searchable: flatten(question),
    }));

    (catalog.suggestions || []).forEach((suggestion) => addRecord({
      type: 'Improvement suggestion', group: 'Suggestions', title: suggestion.title,
      detail: [suggestion.detail, `Impact: ${suggestion.impact}`, `Effort: ${suggestion.effort}`,
        `Decision: ${suggestion.decision}`].join(' · '),
      checked: catalog.asOf || '', internal: { href: 'suggestions.html', label: 'Open the suggestions page' },
      searchable: flatten(suggestion),
    }));

    if (catalog.tripCostModel) {
      addRecord({
        type: 'Trip cost model', group: 'Trip cost', title: catalog.tripCostModel.hotel || 'Estimated trip cost',
        detail: [catalog.tripCostModel.formula, `${catalog.tripCostModel.entries} entries × ${money(catalog.tripCostModel.buyIn)}`,
          `${catalog.tripCostModel.nights} nights × ${money(catalog.tripCostModel.trueCostPerNight)} per night`,
          `Total ${money(catalog.tripCostModel.tripTotal)}`].filter(Boolean).join(' · '),
        checked: catalog.asOf || '', sourceUrls: Object.values(catalog.tripCostModel.sources || {}),
        searchable: flatten(catalog.tripCostModel),
      });
    }

    const checkedAt = checks && (checks.generatedAt || checks.lastRun || checks.checkedAt) || '';
    (checks && checks.urls || []).forEach((row) => addRecord({
      type: 'Automated official-source re-check', group: 'Source monitoring',
      title: row.label || row.url, when: row.checked || checkedAt,
      detail: [row.status, row.changed ? 'Content changed · manual review' : '',
        row.wordingChanged ? 'Visible wording changed' : '', row.unavailable ? 'Unavailable' : '',
        row.botBlocked ? 'Crawler blocked' : '', row.basisReset ? 'Baseline re-seeded' : ''].filter(Boolean).join(' · '),
      checked: row.checked || checkedAt, sourceUrls: [row.url], searchable: flatten(row),
    }));

    const transcription = checks && checks.transcription;
    (transcription && transcription.rows || []).forEach((row) => {
      const event = byEventId.get(row.eventId);
      addRecord({
        type: 'Official PDF transcription check', group: 'PDF checks', title: row.name,
        when: row.date || '',
        detail: [row.time, row.regCloses && `registration closes ${row.regCloses}`,
          row.guarantee && `guarantee ${money(Number(row.guarantee))}`,
          row.chips && `${Number(row.chips).toLocaleString('en-US')} chips`, row.levelMin && `${row.levelMin} minute levels`,
          row.mismatch ? 'Mismatch' : row.inData ? 'Matches published row' : 'Not matched'].filter(Boolean).join(' · '),
        checked: transcription.checked || '',
        sourceUrls: [transcription.source, ...eventSources(event)], searchable: flatten(row),
      });
    });
  }

  function render(query) {
    const terms = normalize(query).trim().split(/\s+/).filter(Boolean);
    if (!terms.length) {
      summary.textContent = 'Enter a query to search every published data-backed table.';
      host.innerHTML = '<div class="empty"><strong>No query entered.</strong> Search tournaments, hotel terms and dated rates, walking routes, official sources, structure sheets, schedules and overlap checks, questions, flags, automated re-checks, or suggestions.</div>';
      return;
    }
    const matches = records.filter((record) => terms.every((term) => record.searchable.includes(term)));
    const groups = new Set(matches.map((record) => record.group));
    summary.textContent = `${matches.length} matching rows across ${groups.size} table categories for “${query}”.`;
    if (!matches.length) {
      host.innerHTML = '<div class="empty"><strong>No matches.</strong> Try an event name, property, date, buy-in, rule excerpt, source status, or flag ID.</div>';
      return;
    }
    host.innerHTML = `<div class="table-wrap global-search-table"><table><thead><tr><th>Table</th><th>Date / observed</th><th>Record</th><th>Matching details</th><th>Last checked</th><th>Source / review</th></tr></thead><tbody>${matches.map((record) =>
      `<tr><td>${esc(record.type)}</td><td>${esc(record.when)}</td><td class="event-name">${esc(record.title)}</td><td>${esc(record.detail)}</td><td>${esc(record.checked)}</td><td>${sourceCell(record.urls, record.mapUrl, record.internal)}</td></tr>`).join('')}</tbody></table></div>`;
  }

  input.value = new URLSearchParams(location.search).get('q') || '';
  form.addEventListener('submit', (event) => {
    event.preventDefault();
    const query = input.value.trim();
    if (typeof history !== 'undefined' && history.replaceState) {
      const next = new URL(location.href);
      if (query) next.searchParams.set('q', query);
      else next.searchParams.delete('q');
      history.replaceState(null, '', next);
    }
    render(query);
  });
  input.addEventListener('input', () => render(input.value));

  Promise.all([
    fetch('data.json').then((response) => {
      if (!response.ok) throw new Error(`data.json returned ${response.status}`);
      return response.json();
    }),
    fetch('checks.json').then((response) => response.ok ? response.json() : null).catch(() => null),
    fetch('feed/index.json').then((response) => response.ok ? response.json() : null).catch(() => null),
  ]).then(([data, checkData, feedData]) => {
    catalog = data;
    checks = checkData;
    feedRecord = feedData;
    indexCatalog();
    render(input.value);
  }).catch(() => {
    summary.textContent = 'The published search catalog could not be loaded.';
    host.innerHTML = '<div class="notice"><strong>Search unavailable.</strong> The catalog could not be read. Please use the source, tournament, hotel, and flagged pages directly.</div>';
  });
})();
