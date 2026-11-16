(() => {
  const appScript = document.currentScript;
  const dataUrl = new URL(appScript?.dataset.catalog || '../data/research.json', appScript?.src || window.location.href);
  const nav = [
    ['home', 'Overview', 'index.html'],
    ['schedule', 'Tournaments', 'schedule.html'],
    ['plan', 'Day planner', 'plan.html'],
    ['rooms', 'Poker rooms', 'rooms.html'],
    ['stay', 'Stay', 'stay.html'],
    ['routes', 'Routes', 'routes.html'],
    ['review', 'Flagged for Review', 'review.html']
  ];

  const esc = (value) => String(value ?? '').replace(/[&<>"']/g, (ch) => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  }[ch]));
  const sourceMap = (data) => Object.fromEntries(data.sources.map((source) => [source.id, source]));
  const strictCount = (data) => data.events.filter((event) => event.strictStatus === 'verified').length;
  const money = (value) => value == null ? 'Buy-in not listed' : `$${Number(value).toLocaleString('en-US')}`;
  const monthDay = (iso) => {
    const [year, month, day] = iso.split('-').map(Number);
    return new Intl.DateTimeFormat('en-US', { month: 'short', day: 'numeric', timeZone: 'UTC' }).format(new Date(Date.UTC(year, month - 1, day)));
  };
  const weekDay = (iso) => {
    const [year, month, day] = iso.split('-').map(Number);
    return new Intl.DateTimeFormat('en-US', { weekday: 'short', timeZone: 'UTC' }).format(new Date(Date.UTC(year, month - 1, day)));
  };
  const sourceLink = (source, label) => source
    ? `<a class="source-link" href="${esc(source.url)}" target="_blank" rel="noopener noreferrer">${esc(label || 'Official source')} ↗</a>`
    : '';
  const sourceLinks = (ids, sources, max = 3) => (ids || []).slice(0, max).map((id) => {
    const source = sources[id];
    return source ? sourceLink(source, source.kind === 'third-party' ? 'Route estimate' : source.name) : '';
  }).join('');

  const statusMeta = {
    rejected: { label: 'Extra entry / spend confirmed', css: 'rejected' },
    unverified: { label: 'Flagged for Review', css: 'unverified' },
    verified: { label: 'Strict-entry verified', css: 'verified' },
    mixed: { label: 'Mixed / conflicting terms', css: 'mixed' }
  };
  const badge = (status, label) => {
    const item = statusMeta[status] || { label: 'Reference', css: 'neutral' };
    return `<span class="badge badge--${item.css}">${esc(label || item.label)}</span>`;
  };
  const pageHead = (kicker, title, description, asOf) => `
    <div class="page-head">
      <div><span class="kicker">${esc(kicker)}</span><h1 class="page-title">${title}</h1><p class="page-subtitle">${description}</p></div>
      <div class="as-of">Research snapshot · ${esc(asOf)}</div>
    </div>`;

  function mountShell(data) {
    const current = document.body.dataset.page || 'home';
    const eligible = strictCount(data);
    const header = document.getElementById('site-header');
    const footer = document.getElementById('site-footer');
    if (header) {
      header.innerHTML = `
        <div class="container nav-shell">
          <a class="brand" href="index.html" aria-label="Poker3 home">
            <span class="brand-mark" aria-hidden="true">♠</span>
            <span class="brand-name"><strong>Poker3</strong><small>Vegas field guide</small></span>
          </a>
          <nav class="main-nav" id="main-nav" aria-label="Primary navigation">
            ${nav.map(([id, title, href]) => `<a class="nav-link ${current === id ? 'active' : ''}" href="${href}" ${current === id ? 'aria-current="page"' : ''}>${title}</a>`).join('')}
          </nav>
          <div class="nav-right">
            <a class="nav-status" href="review.html" aria-label="${eligible} strict-entry events verified"><b>${eligible}</b><span>verified matches</span></a>
            <button class="menu-toggle" type="button" aria-label="Open navigation" aria-expanded="false" aria-controls="main-nav">☰</button>
          </div>
        </div>`;
      const button = header.querySelector('.menu-toggle');
      const menu = header.querySelector('.main-nav');
      button?.addEventListener('click', () => {
        const open = menu.classList.toggle('open');
        button.setAttribute('aria-expanded', String(open));
        button.setAttribute('aria-label', open ? 'Close navigation' : 'Open navigation');
      });
    }
    if (footer) {
      footer.innerHTML = `
        <div class="container footer-inner">
          <div class="footer-copy">Poker3 · Research snapshot ${esc(data.meta.asOfLabel)} · Las Vegas time is Pacific Time.<br>Schedules, rules, rates, and availability can change. Confirm with the property before travel.</div>
          <div class="footer-links"><a href="methodology.html">Method & sources</a><a href="review.html">Open review list</a></div>
        </div>`;
    }
    document.title = `${document.body.dataset.title || 'Overview'} · Poker3`;
  }

  function eventEvidenceLinks(event, sources) {
    return (event.sourceIds || []).slice(0, 3).map((id) => {
      const source = sources[id];
      if (!source) return '';
      const label = source.kind === 'third-party'
        ? 'Third-party estimate'
        : (/series|schedule/.test(id) ? 'Official schedule' : 'Official event terms');
      return sourceLink(source, label);
    }).join('');
  }

  function eventCard(event, sources) {
    const status = statusMeta[event.strictStatus] || statusMeta.unverified;
    return `
      <article class="event-card">
        <div class="event-date"><strong>${esc(monthDay(event.date))}</strong><span>${esc(weekDay(event.date))} · ${esc(event.time)}</span></div>
        <div class="event-main">
          <h3>${esc(event.name)}</h3>
          <p>${esc(event.venue)} <span aria-hidden="true">·</span> ${esc(event.series)} <span aria-hidden="true">·</span> ${esc(event.format)}</p>
          <span class="event-reason">${esc(event.reason)}</span>
        </div>
        <div class="event-side">
          ${badge(event.strictStatus, status.label)}
          <strong>${esc(money(event.buyIn))}</strong>
          <div class="source-links event-sources">${eventEvidenceLinks(event, sources)}</div>
        </div>
      </article>`;
  }

  function renderHome(data, sources) {
    const root = document.querySelector('[data-content]');
    const seriesCount = new Set(data.events.map((event) => event.series)).size;
    const sample = data.meta.sampleStay;
    const featured = data.events.slice(0, 6);
    root.innerHTML = `
      <div class="container page-shell">
        <section class="hero" aria-labelledby="hero-title">
          <div class="hero-grid">
            <div>
              <span class="kicker">Las Vegas · tournament research</span>
              <h1 id="hero-title">Find a seat.<br><em>Keep the rules clear.</em></h1>
              <p class="hero-copy">A practical poker-room field guide built around your strict-entry test: one entry total, no re-entry, rebuy, add-on, or paid chip boost. Every listing is linked back to its source—and unknowns stay unknown.</p>
              <div class="hero-actions">
                <a class="button button-primary" href="schedule.html">Explore upcoming events <span aria-hidden="true">↗</span></a>
                <a class="button" href="plan.html">Open the day planner <span aria-hidden="true">→</span></a>
              </div>
            </div>
            <aside class="hero-check" aria-label="Strict-entry result">
              <div class="check-label">Strict-entry screen</div>
              <div class="zero"><strong>${strictCount(data)}</strong><span>verified matches</span></div>
              <p>No upcoming event is currently proven to satisfy every part of the rule. A blank or silent structure is not a pass.</p>
              <ul class="rule-list"><li>One entry total</li><li>No re-entry or rebuy</li><li>No add-on or paid chip advantage</li></ul>
            </aside>
          </div>
        </section>

        <section class="metric-grid" aria-label="Research snapshot">
          <div class="metric"><div class="metric-label">Verified strict-entry</div><div class="metric-value metric-accent">${strictCount(data)} <small>events</small></div></div>
          <div class="metric"><div class="metric-label">Series in snapshot</div><div class="metric-value">${seriesCount} <small>upcoming</small></div></div>
          <div class="metric"><div class="metric-label">Earliest daily start</div><div class="metric-value">9:00 <small>AM · Horseshoe</small></div></div>
          <div class="metric"><div class="metric-label">Working hotel window</div><div class="metric-value">4 <small>nights · ${esc(sample.guests)} guests</small></div></div>
        </section>

        <section class="section">
          <div class="notice critical"><span class="notice-icon" aria-hidden="true">!</span><div><strong>Do not treat “unverified” as eligible.</strong><p>Several Venetian one-day events have appealing buy-ins, but their structure sheets do not prove one entry total or rule out add-ons. The current WPT headline events allow repeat entries across flights or re-entries.</p></div></div>
        </section>

        <section class="section">
          <div class="section-heading"><div><span class="kicker">Upcoming schedule</span><h2>Featured starts worth checking</h2><p>Selected events from the official Venetian and Wynn/WPT calendars; this is not every event in either series.</p></div><a class="section-action" href="schedule.html">Full snapshot →</a></div>
          <div class="event-stack">${featured.map((event) => eventCard(event, sources)).join('')}</div>
        </section>

        <section class="section">
          <div class="section-heading"><div><span class="kicker">Explore the guide</span><h2>Everything around the felt</h2><p>Room schedules, a cautious day-start planner, hotel fee notes, walk estimates, and the unresolved questions.</p></div></div>
          <div class="category-grid">
            <a class="category-tile" href="schedule.html"><span class="category-icon">♧</span><h3>Tournament calendar</h3><p>Filter selected upcoming starts by date, venue, and entry-rule status.</p></a>
            <a class="category-tile" href="plan.html"><span class="category-icon">◷</span><h3>Day-start planner</h3><p>See concurrent start windows without pretending start times guarantee a full-day itinerary.</p></a>
            <a class="category-tile" href="rooms.html"><span class="category-icon">♠</span><h3>Poker rooms</h3><p>Compare daily times, buy-in notes, and the reasons a room is or is not a pass.</p></a>
            <a class="category-tile" href="stay.html"><span class="category-icon">⌂</span><h3>Stay & resort fees</h3><p>Review the dated sample window and keep taxes, fee conflicts, and starting offers visible.</p></a>
          </div>
          <div class="category-grid" style="margin-top:12px">
            <a class="category-tile" href="routes.html"><span class="category-icon">↗</span><h3>Walk estimates</h3><p>Route-provider estimates only; none are presented as property-confirmed walking times.</p></a>
            <a class="category-tile" href="review.html"><span class="category-icon">!</span><h3>Flagged for review</h3><p>Open questions and conflicting source details that should be resolved before booking or buying in.</p></a>
            <a class="category-tile" href="methodology.html"><span class="category-icon">≡</span><h3>Method & sources</h3><p>What counts as a strict pass, source hierarchy, and the original official references.</p></a>
            <a class="category-tile" href="plan.html"><span class="category-icon">◎</span><h3>Sample date</h3><p>${esc(sample.label)} is a research window, not a user-confirmed trip.</p></a>
          </div>
        </section>

        <section class="section">
          <div class="section-heading"><div><span class="kicker">Planning caveat</span><h2>Starts are not a playable itinerary</h2><p>Events overlap and can run for hours. The start-time list helps shortlist options; it cannot promise how many tournaments one player can complete.</p></div><a class="section-action" href="plan.html">View the planner →</a></div>
          <div class="text-panel"><h3>Current best answer</h3><p>The earliest confirmed recurring start found is <strong>9:00 a.m. at Horseshoe</strong>. The Venetian schedule also has a 9:10 a.m. satellite on Dec. 12. No 8:00 a.m. tournament start was confirmed. Exact end times and enough current entry terms are missing to calculate a reliable maximum-entry day.</p></div>
        </section>
      </div>`;
  }

  function renderSchedule(data, sources) {
    const root = document.querySelector('[data-content]');
    const venues = [...new Set(data.events.map((event) => event.venue))].sort();
    root.innerHTML = `
      <div class="container page-shell">
        ${pageHead('Tournament calendar', 'Upcoming starts, with the fine print attached.', 'A curated snapshot from official series schedules. “Rules not established” means the event has not passed the strict-entry screen.', data.meta.asOfLabel)}
        <div class="notice critical"><span class="notice-icon" aria-hidden="true">!</span><div><strong>${strictCount(data)} events currently pass the strict-entry screen.</strong><p>Known re-entry/add-on events are marked rejected; unclear events remain unverified. Use the source link to check the exact event sheet before you travel.</p></div></div>
        <section class="section mt-0" aria-label="Filter tournament schedule">
          <div class="filters">
            <div class="field search-field"><label for="event-search">Search events</label><input id="event-search" type="search" placeholder="Try Venetian, $600, WPT Prime…"></div>
            <div class="field"><label for="event-venue">Venue</label><select id="event-venue"><option value="">All venues</option>${venues.map((venue) => `<option value="${esc(venue)}">${esc(venue)}</option>`).join('')}</select></div>
            <div class="field"><label for="event-status">Entry-rule status</label><select id="event-status"><option value="">All statuses</option><option value="unverified">Flagged for Review</option><option value="rejected">Extra entry/spend confirmed</option><option value="verified">Strict-entry verified</option></select></div>
            <div class="field"><label for="event-date">Start date</label><input id="event-date" type="date" min="2026-11-16" max="2026-12-23"></div>
            <label class="checkbox-field"><input id="strict-only" type="checkbox"> Strict-entry only</label>
          </div>
          <div class="result-note"><span id="event-count" aria-live="polite"></span><span>Las Vegas local time · Pacific Time</span></div>
          <div class="event-stack" id="event-results"></div>
        </section>
        <section class="section"><div class="text-panel"><h3>Coverage note</h3><p>The Venetian and WPT schedules contain many more events than the selected rows shown here. Follow the official series links on each row for the full current calendar. Room dailies are in <a class="source-link" href="rooms.html">Poker rooms</a>; they are not duplicated as dated calendar entries.</p></div></section>
      </div>`;

    const list = document.getElementById('event-results');
    const count = document.getElementById('event-count');
    const search = document.getElementById('event-search');
    const venue = document.getElementById('event-venue');
    const status = document.getElementById('event-status');
    const date = document.getElementById('event-date');
    const strict = document.getElementById('strict-only');
    const update = () => {
      const query = search.value.trim().toLowerCase();
      const filtered = data.events.filter((event) => {
        const haystack = `${event.name} ${event.venue} ${event.series} ${event.game} ${event.reason}`.toLowerCase();
        return (!query || haystack.includes(query))
          && (!venue.value || event.venue === venue.value)
          && (!status.value || event.strictStatus === status.value)
          && (!date.value || event.date === date.value)
          && (!strict.checked || event.strictStatus === 'verified');
      });
      count.textContent = `${filtered.length} of ${data.events.length} selected event starts`;
      list.innerHTML = filtered.length ? filtered.map((event) => eventCard(event, sources)).join('') : '<div class="empty-state"><strong>No events match these filters.</strong>Try another date or turn off strict-entry-only. Unknown rules are not treated as a pass.</div>';
    };
    [search, venue, status, date, strict].forEach((control) => control.addEventListener('input', update));
    update();
  }

  function timeToMinutes(time) {
    const normalized = String(time).replace(/^[A-Za-z]+\s*[·,-]\s*/, '').trim();
    if (/^noon$/i.test(normalized)) return 12 * 60;
    if (/^midnight$/i.test(normalized)) return 24 * 60;
    const match = normalized.match(/(\d{1,2}):(\d{2})\s*(AM|PM)/i);
    if (!match) return 9999;
    let hours = Number(match[1]) % 12;
    if (match[3].toUpperCase() === 'PM') hours += 12;
    const minutes = hours * 60 + Number(match[2]);
    return hours < 5 ? minutes + 1440 : minutes;
  }
  function renderPlanner(data, sources) {
    const root = document.querySelector('[data-content]');
    const sampleDate = data.meta.sampleStay.arrival;
    root.innerHTML = `
      <div class="container page-shell">
        ${pageHead('Day-start planner', 'Build a day around real start times.', 'This is a start-window map, not a promise that one player can complete or enter every event shown.', data.meta.asOfLabel)}
        <div class="notice critical"><span class="notice-icon" aria-hidden="true">!</span><div><strong>No reliable maximum-entry itinerary can be verified yet.</strong><p>Current sources establish start times for some rooms, but not enough current event durations, registration cutoffs, and rules to guarantee a sequential day. Concurrent starts are alternatives, not a route to play all of them.</p></div></div>
        <section class="section" style="margin-top:20px">
          <div class="filters planner-controls">
            <div class="field"><label for="planner-date">Choose a date</label><input id="planner-date" type="date" min="2026-11-16" max="2026-12-23" value="${sampleDate}"></div>
            <div class="field"><label for="planner-duration">Assumed time at each event</label><input id="planner-duration" type="number" min="0.5" max="24" step="0.5" placeholder="Hours (e.g. 4)"></div>
            <label class="checkbox-field"><input id="planner-strict-only" type="checkbox"> Strict-verified only</label>
            <button class="button button-primary" type="button" id="planner-run">Model start sequence</button>
          </div>
          <div class="result-note"><span id="planner-label" aria-live="polite"></span><span>Times are local to Las Vegas (PT)</span></div>
          <div id="planner-results"></div>
          <div id="planner-itinerary" class="empty-state planner-itinerary" aria-live="polite"><strong>Optional scenario</strong> Enter your own hours-per-event assumption to model a best-case sequence. No event durations are published here.</div>
        </section>
        <section class="section"><div class="two-col">
          <div class="text-panel"><h3>What could make a start unusable?</h3><ul><li>Two or more events beginning at the same time.</li><li>A prior tournament may still be running; published start times do not include your bust-out or finish time.</li><li>Daily room terms may change or pause during a series. Wynn's regular dailies are suspended during its event series.</li></ul></div>
          <div class="text-panel"><h3>Earliest starts found</h3><p><strong>9:00 a.m. recurring:</strong> Horseshoe daily event; official current entry terms are not published in the source reviewed.</p><p><strong>9:10 a.m., Dec. 12:</strong> Venetian $260 NLH Turbo milestone satellite (Event #46); a second such satellite starts at 12:10 p.m. Neither has confirmed entry limits. <strong>4:10 p.m., Dec. 10 and 11:</strong> separate $260 milestone satellites. ${sourceLink(sources['venetian-satellite'], 'Dec. 12 structure')} ${sourceLink(sources['venetian-47-satellite'], 'Dec. 10–11 structure')}</p><p><strong>No 8:00 a.m. start</strong> was confirmed in the researched schedules.</p></div>
        </div></section>
      </div>`;
    const input = document.getElementById('planner-date');
    const out = document.getElementById('planner-results');
    const label = document.getElementById('planner-label');
    const duration = document.getElementById('planner-duration');
    const strictOnly = document.getElementById('planner-strict-only');
    const itinerary = document.getElementById('planner-itinerary');
    let dailyGroups = [];
    const render = () => {
      const selected = input.value;
      if (!selected) { dailyGroups = []; label.textContent = ''; out.innerHTML = '<div class="empty-state">Choose a date in the current research window.</div>'; return; }
      label.textContent = `${weekDay(selected)}, ${monthDay(selected)} · sample start windows`;
      const entries = [];
      data.events.filter((event) => event.date === selected).forEach((event) => entries.push({ time: event.time, minutes: timeToMinutes(event.time), event }));
      const inWpt = selected >= '2026-11-27' && selected <= '2026-12-21';
      data.rooms.filter((room) => room.schedule === 'Daily' || room.schedule === 'Non-series periods only').forEach((room) => {
        if (room.id === 'wynn-daily' && inWpt) return;
        room.times.forEach((time) => entries.push({ time, minutes: timeToMinutes(time), room }));
      });
      entries.sort((a, b) => a.minutes - b.minutes || ((a.event && !b.event) ? -1 : ((!a.event && b.event) ? 1 : 0)));
      const grouped = new Map();
      entries.forEach((entry) => {
        if (!grouped.has(entry.time)) grouped.set(entry.time, []);
        grouped.get(entry.time).push(entry);
      });
      dailyGroups = [...grouped.entries()];
      const blocks = dailyGroups.map(([time, starts]) => `
        <div class="card" style="display:grid;grid-template-columns:90px minmax(0,1fr);gap:14px;margin-bottom:9px;padding:15px 17px">
          <strong style="color:var(--green);font-size:13px">${esc(time)}${time === '2:00 AM' ? '<small style="display:block;color:var(--subtle);font-size:9px">overnight</small>' : ''}</strong>
          <div style="display:grid;gap:10px">${starts.map((start) => start.event
            ? `<div><div style="display:flex;flex-wrap:wrap;align-items:center;gap:8px"><strong style="font-size:12px">${esc(start.event.venue)} · ${esc(start.event.name)}</strong>${badge(start.event.strictStatus)}</div><p class="muted small" style="margin:5px 0 0">${esc(start.event.reason)}</p><div class="source-links event-sources">${eventEvidenceLinks(start.event, sources)}</div></div>`
            : `<div><div style="display:flex;flex-wrap:wrap;align-items:center;gap:8px"><strong style="font-size:12px">${esc(start.room.name)} daily start</strong>${badge(start.room.status)}</div><p class="muted small" style="margin:5px 0 0">${esc(start.room.terms)}</p></div>`).join('')}</div>
        </div>`).join('');
      const pause = inWpt ? '<div class="notice" style="margin-bottom:12px"><span class="notice-icon" aria-hidden="true">i</span><div><strong>Wynn regular daily schedule paused</strong><p>The WPT event series is in progress; use its series calendar instead of the regular daily poster.</p></div></div>' : '';
      out.innerHTML = pause + (blocks || '<div class="empty-state"><strong>No dated starts are in the selected snapshot.</strong>Room dailies and series schedules change; use the official calendars and call ahead.</div>');
    };
    const modelScenario = () => {
      if (!input.value) {
        itinerary.className = 'empty-state planner-itinerary';
        itinerary.innerHTML = '<strong>Choose a date first.</strong> The scenario needs a date and your own time-per-event assumption.';
        return;
      }
      const hours = Number(duration.value);
      if (!duration.value || !Number.isFinite(hours) || hours < 0.5 || hours > 24) {
        itinerary.className = 'empty-state planner-itinerary';
        itinerary.innerHTML = '<strong>Optional scenario</strong> Enter your own hours-per-event assumption (0.5–24) to model a best-case sequence. No event durations are published here.';
        return;
      }
      const candidates = dailyGroups.map(([time, starts]) => [time, starts.filter((start) => !strictOnly.checked || (start.event ? start.event.strictStatus === 'verified' : start.room.status === 'verified'))]).filter(([, starts]) => starts.length);
      const selectedGroups = [];
      let availableAgainAt = -Infinity;
      candidates.forEach((group) => {
        const startMinute = group[1][0].minutes;
        if (startMinute < availableAgainAt) return;
        selectedGroups.push(group);
        availableAgainAt = startMinute + hours * 60;
      });
      if (!selectedGroups.length) {
        itinerary.className = 'empty-state planner-itinerary';
        itinerary.innerHTML = strictOnly.checked
          ? '<strong>No strict-entry-verified starts for this date.</strong>There are currently zero verified events in the research snapshot; flagged and rejected options are excluded.'
          : '<strong>No starts to model for this date.</strong>Try another date in the research window.';
        return;
      }
      const hourLabel = hours.toLocaleString('en-US', { maximumFractionDigits: 1 });
      const steps = selectedGroups.map(([time, starts], index) => `
        <article class="itinerary-stop">
          <div class="itinerary-stop-head"><span>${String(index + 1).padStart(2, '0')}</span><strong>${esc(time)}</strong><small>candidate slot ${index + 1}</small></div>
          <div><p class="itinerary-choice">Choose one option at this start time; concurrent starts are alternatives.</p>
            <ul class="itinerary-options">${starts.map((start) => {
              const isEvent = Boolean(start.event);
              const item = isEvent ? start.event : start.room;
              const name = isEvent ? `${item.venue} · ${item.name}` : `${item.name} daily tournament`;
              const status = isEvent ? item.strictStatus : item.status;
              const note = isEvent ? item.reason : item.terms;
              const links = isEvent ? eventEvidenceLinks(item, sources) : sourceLinks(item.sourceIds, sources, 2);
              return `<li><div class="itinerary-option-title"><strong>${esc(name)}</strong>${badge(status)}</div><p>${esc(note)}</p><div class="source-links event-sources">${links}</div></li>`;
            }).join('')}</ul>
          </div>
        </article>`).join('');
      itinerary.className = 'planner-itinerary';
      itinerary.innerHTML = `
        <div class="itinerary-top"><div><span class="kicker">Hypothetical model</span><h3>${selectedGroups.length} candidate start slots</h3></div>${badge('unverified', 'Assumption-based only')}</div>
        <p class="planner-caveat">Assumes you can leave each event exactly ${hourLabel} hours after its scheduled start. This is a best-case spacing model—not a playable or verified itinerary. It does not model actual tournament duration, bust-out timing, walking/transfer time, registration cutoffs, or entry-rule eligibility. Follow each source and confirm with the room.</p>
        <div class="itinerary-list">${steps}</div>`;
    };
    input.addEventListener('change', () => { render(); modelScenario(); });
    duration.addEventListener('input', modelScenario);
    strictOnly.addEventListener('change', modelScenario);
    document.getElementById('planner-run').addEventListener('click', modelScenario);
    render();
    modelScenario();
  }

  function renderRooms(data, sources) {
    const root = document.querySelector('[data-content]');
    root.innerHTML = `
      <div class="container page-shell">
        ${pageHead('Poker-room index', 'Daily schedules, with unknowns kept visible.', 'Start-time references are not proof of tournament eligibility. Check current structures before registering.', data.meta.asOfLabel)}
        <div class="notice"><span class="notice-icon" aria-hidden="true">i</span><div><strong>Daily schedules can pause or change.</strong><p>Wynn's regular daily events are suspended during its tournament series. The WPT and Venetian series rows live in the <a class="source-link" href="schedule.html">tournament calendar</a>.</p></div></div>
        <section class="section"><div class="event-stack">
          ${data.rooms.map((room) => `
            <article class="card room-card">
              <div class="room-title"><h3>${esc(room.name)}</h3><span>${esc(room.area)} · ${esc(room.schedule)}</span>${badge(room.status)}</div>
              <div class="room-detail"><strong>${room.times.length ? 'Published start times' : 'Start times'}</strong>${room.times.length ? `<div class="time-pills">${room.times.map((time) => `<span class="time-pill">${esc(time)}</span>`).join('')}</div>` : '<span>Not established in the official source reviewed.</span>'}<p><strong style="margin-top:13px">Buy-in notes</strong>${esc(room.buyIns)}</p></div>
              <div class="room-detail"><strong>Entry-rule note</strong>${esc(room.terms)}<div class="source-links">${sourceLinks(room.sourceIds, sources, 3)}</div></div>
            </article>`).join('')}
        </div></section>
        <section class="section"><div class="text-panel"><h3>Strict-entry rule</h3><p>The room status is intentionally conservative. A page that lists a tournament time but omits re-entry or add-on rules is <strong>unverified</strong>, not a pass. A confirmed re-entry, rebuy, add-on, or paid chip bonus is marked as extra spend/entry.</p></div></section>
      </div>`;
  }

  function renderStay(data, sources) {
    const root = document.querySelector('[data-content]');
    const sample = data.meta.sampleStay;
    root.innerHTML = `
      <div class="container page-shell">
        ${pageHead('Hotel comparison', 'See the fee before the room price.', 'No actual stay dates were supplied. The dated search window below is a working sample, not a confirmed booking or recommendation.', data.meta.asOfLabel)}
        <div class="notice critical"><span class="notice-icon" aria-hidden="true">!</span><div><strong>Sample window only · ${esc(sample.label)}</strong><p>Rates are dynamic. Only one property returned a usable nightly rate card, and its fee/tax presentation conflicts. No four-night all-in total is stated.</p></div></div>
        <section class="section"><div class="card-grid">${data.hotels.map((hotel) => `
          <article class="card hotel-card">
            <div class="card-top"><div><span class="kicker">${esc(hotel.area)}</span><h3>${esc(hotel.name)}</h3></div>${badge(hotel.id === 'horseshoe' ? 'unverified' : 'mixed', hotel.id === 'horseshoe' ? 'Quote not final' : 'Rate not comparable')}</div>
            <div class="rate">${esc(hotel.sampleRate)}</div>
            <div class="fee-line">Resort fee: ${esc(hotel.fee)}</div>
            <p class="hotel-detail">${esc(hotel.details)}</p>
            <div class="card-bottom"><small>${esc(hotel.rateStatus)}</small><span class="source-links">${sourceLinks(hotel.sourceIds, sources, 2)}</span></div>
          </article>`).join('')}</div></section>
        <section class="section"><div class="section-heading"><div><span class="kicker">Known fee terms</span><h2>Base resort fees, before applicable tax</h2><p>These are published nightly fees, not room rates or a stay total.</p></div></div>
          <div class="card-grid">
            ${[['The Venetian','$55 / night + tax','venetian-fee'],['Wynn Las Vegas','$55 / night + tax','wynn-fee'],['MGM Grand','$50 / night + tax','mgm-fee'],['Bellagio','$55 / night + tax','bellagio-fee'],['ARIA','$55 / night + tax','aria-fee'],['Treasure Island','$49.95 / night + tax','ti-rooms']].map(([name,fee,id]) => `<div class="card"><span class="kicker">Resort-fee term</span><h3>${esc(name)}</h3><p class="card-lede">${esc(fee)}</p><div class="source-links">${sourceLink(sources[id], 'Official fee terms ↗')}</div></div>`).join('')}
          </div>
        </section>
        <section class="section"><div class="two-col"><div class="text-panel"><h3>Why no “cheapest hotel” winner?</h3><p>Venetian showed placeholder pricing, Wynn returned dates that did not match the query, and Treasure Island's NFR page is a from-price offer rather than a quote for all sample nights. Resort fees alone do not make room rates comparable.</p></div><div class="text-panel"><h3>For a real comparison</h3><p>Use the same arrival/departure dates, guest count, room type, cancellation terms, and tax/fee basis on each property's official checkout. Verify poker-room qualifying rates separately; don't count an advertised “from” price as available.</p><div class="source-links">${sourceLink(sources['horseshoe-booking'], 'Open sample Horseshoe search ↗')}</div></div></div></section>
        <div class="page-bottom-cta"><div><h2>Need a dated quote comparison?</h2><p>Replace the sample dates with the traveler's real dates before totaling fees or selecting a hotel.</p></div><a class="button" href="review.html">See pricing flags →</a></div>
      </div>`;
  }

  function renderRoutes(data, sources) {
    const root = document.querySelector('[data-content]');
    root.innerHTML = `
      <div class="container page-shell">
        ${pageHead('Getting around', 'Useful walk estimates, not official promises.', 'These are third-party pedestrian estimates. Casino entrances, indoor walkways, construction, crowds, mobility, and heat can change the real trip.', data.meta.asOfLabel)}
        <div class="notice"><span class="notice-icon" aria-hidden="true">i</span><div><strong>No property-confirmed walking times were found.</strong><p>Each route below links to Rome2Rio. Verify a current pedestrian route on the day, and allow extra time between casino poker rooms.</p></div></div>
        <section class="section"><div class="card-grid">${data.routes.map((route) => `
          <article class="card route-card">
            <span class="kicker">Rome2Rio · estimate</span>
            <h3>${esc(route.from)}</h3><div class="route-arrow" aria-hidden="true">↓ to ${esc(route.to)}</div>
            <div class="route-time">${esc(route.walk)}</div><div class="route-distance">${esc(route.distance)} · walking option</div>
            <div class="source-links">${sourceLink(sources[route.sourceId], 'Route source ↗')}</div>
          </article>`).join('')}</div></section>
        <p class="route-disclaimer">Times and distances are estimates as displayed by the route provider when checked. They are not official property directions, not accessibility advice, and do not account for navigating inside large resorts.</p>
      </div>`;
  }

  function renderReview(data, sources) {
    const root = document.querySelector('[data-content]');
    root.innerHTML = `
      <div class="container page-shell">
        ${pageHead('Flagged for review', 'Questions to settle before you spend.', 'The open issues are published rather than silently guessed. The strict-entry screen remains at zero until official terms prove otherwise.', data.meta.asOfLabel)}
        <div class="notice critical"><span class="notice-icon" aria-hidden="true">!</span><div><strong>${data.flags.length} open research flags · ${strictCount(data)} verified strict-entry events</strong><p>Resolve tournament terms with the poker room and hotel totals in official checkout before turning this snapshot into a travel plan.</p></div></div>
        <section class="section"><div class="flag-list">${data.flags.map((flag, index) => `
          <article class="flag-card">
            <div class="flag-index">${String(index + 1).padStart(2, '0')}</div>
            <div><div class="flag-category">${esc(flag.category)}</div><h3>${esc(flag.title)}</h3><p>${esc(flag.finding)}</p><p class="next-step"><strong>Next step:</strong> ${esc(flag.next)}</p><div class="source-links">${sourceLinks(flag.sourceIds, sources, 4)}</div></div>
            <div class="flag-severity">${badge(flag.level === 'critical' ? 'rejected' : flag.level === 'high' ? 'unverified' : 'mixed', flag.level)}</div>
          </article>`).join('')}</div></section>
        <div class="page-bottom-cta"><div><h2>See the evidence trail</h2><p>Browse official tournament, hotel, and route references used in this snapshot.</p></div><a class="button" href="methodology.html">Method & sources →</a></div>
      </div>`;
  }

  function renderMethod(data, sources) {
    const root = document.querySelector('[data-content]');
    const official = data.sources.filter((source) => source.kind === 'official');
    const thirdParty = data.sources.filter((source) => source.kind === 'third-party');
    root.innerHTML = `
      <div class="container page-shell">
        ${pageHead('Method & evidence', 'A conservative screen, not a guess.', 'Every material claim links to a fetched source. Official pages outrank third-party listings; source silence is left as uncertainty.', data.meta.asOfLabel)}
        <section class="section mt-0"><div class="two-col">
          <div class="text-panel"><h3>Strict-entry pass criteria</h3><p>To count as a pass, the current official terms must support all of the following:</p><ul><li>Only one entry per player for the whole event—not one per starting flight.</li><li>No re-entry after elimination and no rebuy.</li><li>No add-on, paid extra stack, or optional gratuity that awards additional tournament chips.</li><li>Entry limits must be stated or directly confirmed; silence is not proof.</li></ul></div>
          <div class="text-panel"><h3>Decision labels</h3><p><strong>Extra entry/spend confirmed:</strong> a published rule allows re-entry, rebuy, add-on, or chip-boost.</p><p><strong>Rules not established:</strong> no current official document proves every strict condition.</p><p><strong>Strict-entry verified:</strong> reserved for a current official source that confirms the full rule. There are no such events in this snapshot.</p></div>
        </div></section>
        <section class="section"><div class="notice"><span class="notice-icon" aria-hidden="true">i</span><div><strong>Scope and limits</strong><p>Reviewed ${esc(data.meta.asOfLabel)}. Tournament catalog rows are selected upcoming starts, not the complete calendars. Daily schedules and fee terms may change. The sample stay (${esc(data.meta.sampleStay.label)}) is an assumption. Route times are estimates, not property-confirmed directions.</p></div></div></section>
        <section class="section"><div class="section-heading"><div><span class="kicker">Source register</span><h2>Official sources (${official.length})</h2><p>Primary property, tournament-operator, and booking sources.</p></div></div><div class="source-list">${official.map((source) => `<article class="source-row"><div><strong>${esc(source.name)}</strong><p>${esc(source.note)}</p></div><a href="${esc(source.url)}" target="_blank" rel="noopener noreferrer">Open ↗</a></article>`).join('')}</div></section>
        <section class="section"><div class="section-heading"><div><span class="kicker">Leads only</span><h2>Third-party sources (${thirdParty.length})</h2><p>Used for route estimates or leads, never to certify a tournament entry rule.</p></div></div><div class="source-list">${thirdParty.map((source) => `<article class="source-row"><div><strong>${esc(source.name)}</strong><p>${esc(source.note)}</p></div><a href="${esc(source.url)}" target="_blank" rel="noopener noreferrer">Open ↗</a></article>`).join('')}</div></section>
      </div>`;
  }

  function run(data) {
    const sources = sourceMap(data);
    mountShell(data);
    const page = document.body.dataset.page || 'home';
    const renderers = {
      home: renderHome,
      schedule: renderSchedule,
      plan: renderPlanner,
      rooms: renderRooms,
      stay: renderStay,
      routes: renderRoutes,
      review: renderReview,
      methodology: renderMethod
    };
    (renderers[page] || renderHome)(data, sources);
  }

  fetch(dataUrl, { cache: 'no-store' })
    .then((response) => {
      if (!response.ok) throw new Error(`Research data request failed (${response.status})`);
      return response.json();
    })
    .then(run)
    .catch((error) => {
      console.error(error);
      const root = document.querySelector('[data-content]');
      if (root) root.innerHTML = '<div class="container page-shell"><div class="notice critical"><span class="notice-icon">!</span><div><strong>Research data could not be loaded.</strong><p>Reload the page. If you are previewing a local copy, serve the repository over HTTP instead of opening the file directly.</p></div></div></div>';
    });
})();
