(() => {
  "use strict";
  const Logic = window.PokerPlannerLogic;
  const body = document.body;
  const ROOT = body.dataset.root || "./";
  const page = body.dataset.page || "overview";
  const venueId = body.dataset.venueId || "";
  const content = document.querySelector("[data-page-content]");
  const navItems = [
    ["index.html", "Overview", "▦"],
    ["tournaments.html", "Tournaments", "♠"],
    ["hotels.html", "Hotels & cost", "⌂"],
    ["schedule.html", "Day plan", "◷"],
    ["venues.html", "Venues", "⌖"],
    ["sources.html", "Sources", "↗"],
    ["questions.html", "Questions", "?"],
    ["suggestions.html", "Suggestions", "✦"],
    ["flagged.html", "Review flags", "⚑"],
  ];
  const esc = (value) => String(value ?? "").replace(/[&<>"']/g, (char) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  })[char]);
  const money = (value) => value == null || value === "" ? "Not published / unknown" : (typeof value === "number" ? `$${value.toLocaleString("en-US", { maximumFractionDigits: 2 })}` : esc(value));
  const rootLink = (file) => `${ROOT}${file}`;
  const validUrl = (url) => {
    try { const parsed = new URL(url); return parsed.protocol === "https:" ? parsed.href : ""; }
    catch (_) { return ""; }
  };
  const link = (url, label, extra = "") => {
    const safe = validUrl(url);
    return safe ? `<a href="${esc(safe)}" target="_blank" rel="noopener noreferrer" ${extra}>${esc(label)}</a>` : `<span class="muted">${esc(label)} — URL unavailable</span>`;
  };
  const formatDate = (value) => {
    if (!value) return "Undated / recurring lead";
    const parsed = new Date(`${value}T00:00:00Z`);
    return Number.isNaN(parsed.getTime()) ? esc(value) : new Intl.DateTimeFormat("en-US", { month: "short", day: "numeric", year: "numeric", timeZone: "UTC" }).format(parsed);
  };
  const sortByDateTime = (rows) => [...rows].sort((a, b) => (a.dateISO || "9999").localeCompare(b.dateISO || "9999") || (Logic.parseTime(a.time) ?? 9999) - (Logic.parseTime(b.time) ?? 9999));

  function activeHref(href) {
    if (page === "venue") return href === "venues.html";
    return (location.pathname.split("/").pop() || "index.html") === href;
  }

  function buildShell() {
    const header = document.querySelector("[data-shell-header]");
    const navMarkup = navItems.map(([href, label, icon]) => `<a href="${esc(rootLink(href))}" class="${activeHref(href) ? "active" : ""}"><span class="ico" aria-hidden="true">${icon}</span>${esc(label)}</a>`).join("");
    if (header) {
      header.innerHTML = `<a class="brand" href="${esc(rootLink("index.html"))}"><span class="brand-mark" aria-hidden="true">♠</span><span class="brand-label">Vegas Poker Planner</span></a><div class="global-search"><span class="search-icon" aria-hidden="true">⌕</span><input id="global-search" type="search" role="combobox" aria-expanded="false" aria-controls="global-results" placeholder="Search events, hotels, venues, sources…" autocomplete="off"><div class="global-results" id="global-results" role="listbox"></div></div><span class="top-tag">Research snapshot · <span data-asof>—</span></span>`;
    }
    document.querySelectorAll("[data-nav]").forEach((el) => { el.innerHTML = navMarkup; });
    document.querySelectorAll("[data-mobile-nav]").forEach((el) => { el.innerHTML = navItems.map(([href, label]) => `<a href="${esc(rootLink(href))}" class="${activeHref(href) ? "active" : ""}">${esc(label)}</a>`).join(""); });
  }

  buildShell();
  const emptyMonitor = { schemaVersion: 1, lastRun: null, changedCount: 0, failureCount: 0, changes: [], failures: [], sources: {} };
  const fetchJson = async (relative, fallback) => {
    try {
      const response = await fetch(`${ROOT}${relative}`, { cache: "no-store" });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json();
    } catch (_) { return fallback; }
  };

  Promise.all([
    fetchJson("data.json", null),
    fetchJson("data/source-monitor.json", emptyMonitor),
    fetchJson("data/hotel-rate-logs.json", { schemaVersion: 1, logs: [] }),
  ]).then(([loaded, monitored, rates]) => {
    if (!loaded) throw new Error("Could not load data.json");
    window.PokerPlannerData = loaded;
    window.PokerPlannerMonitor = monitored;
    window.PokerPlannerRateLogs = rates;
    document.querySelectorAll("[data-asof]").forEach((el) => { el.textContent = loaded.asOf || "not recorded"; });
    renderPage(loaded, monitored, rates);
    initGlobalSearch(loaded);
  }).catch((error) => {
    if (content) content.innerHTML = `<div class="notice danger"><strong>Dashboard data did not load.</strong> ${esc(error.message)}. Reload or inspect <a href="${esc(rootLink("data.json"))}">the snapshot JSON</a>.</div>`;
  });

  function renderPage(data, monitor, rateData) {
    if (!content) return;
    const renderers = {
      overview: () => renderOverview(data, monitor),
      tournaments: () => renderTournaments(data, monitor),
      hotels: () => renderHotels(data, monitor, rateData),
      schedule: () => renderSchedule(data, monitor),
      venues: () => renderVenues(data, monitor),
      venue: () => renderVenue(data, monitor),
      sources: () => renderSources(data, monitor),
      flags: () => renderFlags(data, monitor),
      questions: () => renderQuestions(data),
      suggestions: () => renderSuggestions(data),
    };
    content.innerHTML = `${(renderers[page] || renderers.overview)()}<div class="footer">Snapshot checked <span data-asof>${esc(data.asOf || "unknown")}</span>. Tournament schedules and hotel prices can change. Confirm every event rule, room rate, fee, tax and cancellation condition with the official source before booking or registering. Unknown values remain unknown.</div>`;
    if (page === "tournaments") initTournamentControls(data);
    if (page === "schedule") initScheduleControls(data);
    if (page === "hotels") initHotelCalculator(data);
    if (page === "sources") initSourceFilters(data, monitor);
    initTableSearch();
  }

  function stat(label, value, caption) {
    return `<div class="stat"><div class="stat-label">${esc(label)}</div><div class="stat-value">${esc(value)}</div><div class="stat-caption">${esc(caption)}</div></div>`;
  }

  function renderOverview(data, monitor) {
    const events = data.tournaments || [];
    const strict = events.filter(Logic.strictEligible);
    const dated = sortByDateTime(events.filter((event) => event.dateISO));
    const earliest = [...dated].sort((a, b) => (Logic.parseTime(a.time) ?? 9999) - (Logic.parseTime(b.time) ?? 9999))[0];
    const ven = data.scheduleCoverage || {};
    const changes = (monitor.changes || []).slice(-4).reverse();
    const monitorStatus = monitor.lastRun ? `Last checked ${formatTimestamp(monitor.lastRun)} · ${monitor.changedCount || 0} changed · ${monitor.failureCount || 0} unavailable` : "Scheduled source checks are configured but have not recorded a first run.";
    return `<section class="hero"><div class="eyebrow">Evidence-first poker trip planning · snapshot ${esc(data.asOf || "")}</div><h1>Plan around what the sources actually say.</h1><p>${esc(data.scope || "Official-source event and lodging snapshot.")} The strict-entry gate requires one entry total and explicit proof of no re-entry, rebuy, add-on or paid chip advantage.</p><div class="hero-meta">Full Venetian schedule coverage: ${esc(ven.listedRows || 0)} listed starts · ${esc(ven.eventNumbers || 0)} event numbers · ${esc(formatDate(ven.firstDate))}–${esc(formatDate(ven.lastDate))}. ${esc(ven.inferredDateRows || 0)} dates were inferred from omitted date labels in the extracted schedule and are individually marked.</div></section>
      <div class="notice danger"><strong>Strict-entry result: ${strict.length} verified events.</strong> No event currently passes every rule in the reviewed source set. “One day,” a single listed start, or silence about re-entry does not count as proof. <a href="${esc(rootLink("flagged.html"))}">See the open verification flags</a>.</div>
      <div class="stats">${stat("Tournament rows", events.length, "83 Venetian starts plus selected room leads")}${stat("Strict-entry verified", strict.length, "No inferred passes")}${stat("Hotels reviewed", (data.hotels || []).length, "Room prices remain unquoted")}${stat("Official sources", (data.officialSources || []).length, "Weekly change monitoring is configured")}</div>
      <section class="section"><div class="section-head"><div><h2>Quick decisions</h2><p>Use the complete tables to filter and inspect row-level evidence.</p></div></div><div class="cards"><article class="card"><span class="pill warn">Schedule coverage</span><h3>The Venetian schedule is now carried through Dec. 23</h3><p>${esc(ven.listedRows || 0)} scheduled Venetian starts from 64 event numbers are represented. The selected Wynn/WPT, daily Wynn, Bellagio and ARIA items remain a bounded sample—not a Strip-wide inventory.</p><a class="card-link" href="${esc(rootLink("tournaments.html"))}">Filter all rows →</a></article><article class="card"><span class="pill danger">Entry rules unresolved</span><h3>Nothing is promoted from silence</h3><p>Multi-flight, bounty, satellite, one-day and recurring formats are visible, but the detailed entry cap and paid-advantage rules still require event-specific confirmation.</p><a class="card-link" href="${esc(rootLink("questions.html"))}">Questions to ask the room →</a></article><article class="card"><span class="pill blue">Hotel cost planner</span><h3>Enter a live room quote to estimate a stay</h3><p>Published fees are separated from user-entered room rates and tax assumptions. The calculator labels a planning estimate; it never manufactures a checkout quote.</p><a class="card-link" href="${esc(rootLink("hotels.html"))}">Open hotel calculator →</a></article><article class="card"><span class="pill">Schedule conflict checks</span><h3>Compare start times—not finish-time promises</h3><p>Start-time gaps and venue changes are highlighted using a buffer you choose. Event duration and future finish times are not known from the schedule.</p><a class="card-link" href="${esc(rootLink("schedule.html"))}">Review start-time gaps →</a></article></div></section>
      <section class="section"><div class="section-head"><div><h2>Source monitor</h2><p>${esc(monitorStatus)}</p></div><a class="card-link" href="${esc(rootLink("sources.html"))}">Open source register →</a></div>${changes.length ? `<div class="source-list">${changes.map((change) => `<article class="source-item"><div class="source-left"><strong>${esc(change.name || change.id || "Official source changed")}</strong><small>${esc(change.summary || "Content fingerprint differs from the previous successful check.")}</small></div><span class="status changed">Changed</span></article>`).join("")}</div>` : `<div class="empty"><strong>${monitor.lastRun ? "No content changes recorded in the latest run." : "No monitor baseline yet."}</strong> ${monitor.lastRun ? "This describes the monitor snapshot only; it does not guarantee every source is unchanged." : "The first scheduled run establishes source fingerprints; changes will appear here and will not overwrite curated event data."}</div>`}</section>
      <section class="section"><div class="section-head"><div><h2>Early start and next checks</h2><p>Earliest listed start in this bounded snapshot: ${earliest ? `${esc(earliest.time)} on ${esc(formatDate(earliest.dateISO))} at ${esc(earliest.venue)}.` : "No dated start found."}</p></div></div><div class="grid-two"><article class="card"><span class="pill warn">8 AM target</span><h3>No 8:00 AM start found in the reviewed schedule sample</h3><p>The complete Venetian extraction includes a 9:10 AM milestone satellite on Dec. 12; this is earlier than the previously selected 10:10 AM starts. The snapshot does not claim to cover every Strip room.</p></article><article class="card"><span class="pill gray">Hotel totals</span><h3>Comparable checkout totals are still unavailable</h3><p>Venetian placeholders, a Wynn date mismatch and a Caesars booking error are logged. All hotel room-rate and all-in total cells remain blank until a usable date-matched quote is recorded.</p></article></div></section>`;
  }

  function strictLabel(event) {
    const status = event.strictStatus || "unverified";
    const labels = { verified: "Verified strict-entry", rejected: "Extra spend / re-entry documented", conflict: "Source conflict", unverified: "Entry rules unverified" };
    return `<span class="status ${esc(status)}">${esc(labels[status] || labels.unverified)}</span>`;
  }

  function ruleLabel(status) {
    const labels = {
      confirmed: "Confirmed", allowed: "Allowed", available: "Available", contradicted: "Not eligible", conflict: "Conflict",
      unknown: "Unknown", "not-stated": "Not stated", "not-allowed": "Explicitly not allowed", "not-allowed-per-flight": "One per flight only", no: "No bounty label", yes: "Bounty", multiple: "Multiple flights", "single-listed-start": "One listed start", satellite: "Satellite", conditional: "Conditional", "seat-award": "Seat award", "not-published": "Not published",
    };
    return labels[status] || status || "Unknown";
  }

  function monitorFor(sourceId, monitor, source) {
    const item = (monitor.sources || {})[sourceId];
    if (source && source.monitor === false) return `<span class="status unverified">Not polled</span>`;
    if (!item) return `<span class="status unverified">No monitor baseline</span>`;
    const state = item.status || "unchanged";
    const label = state === "failure" ? "Last check failed" : state === "changed" ? "Changed" : state === "baseline" ? "Baseline captured" : state === "unchanged" ? "No change seen" : state;
    return `<span class="status ${esc(state)}">${esc(label)}</span><span class="source-state">${esc(item.lastChecked ? formatTimestamp(item.lastChecked) : "")}</span>`;
  }

  function formatTimestamp(value) {
    if (!value) return "not recorded";
    const date = new Date(value);
    return Number.isNaN(date.getTime()) ? String(value) : date.toLocaleString("en-US", { timeZone: "UTC", dateStyle: "medium", timeStyle: "short" }) + " UTC";
  }

  function evidenceHtml(title, item, data, monitor) {
    if (!item) return `<div class="evidence-box"><strong>${esc(title)}</strong><p>Not recorded.</p></div>`;
    const src = (data.officialSources || []).find((source) => source.url === item.source);
    const srcId = src ? src.id : "";
    return `<div class="evidence-box"><strong>${esc(title)} · ${esc(ruleLabel(item.status))}</strong>${item.excerpt ? `<p>“${esc(item.excerpt)}”</p>` : ""}<p>${esc(item.note || "")}</p><p>Retrieved ${esc(item.retrievedAt || "date not recorded")}.</p><div class="source-links">${link(item.source, src ? src.name : "Open cited official source")}${srcId ? `<span class="source-state">${monitorFor(srcId, monitor, src)}</span>` : ""}</div></div>`;
  }

  function eventSourcesHtml(event, data, monitor) {
    const urls = [];
    for (const url of [event.schedule, event.structure, event.confirmSource]) if (url && !urls.includes(url)) urls.push(url);
    const evidenceItems = [...Object.values(event.rules || {}), event.entryFeeEvidence, event.guaranteeEvidence, event.dateEvidence].filter(Boolean);
    for (const item of evidenceItems) if (item.source && !urls.includes(item.source)) urls.push(item.source);
    const byUrl = new Map((data.officialSources || []).map((source) => [source.url, source]));
    const sourceList = urls.map((url) => {
      const source = byUrl.get(url);
      const label = url === event.schedule ? (event.scheduleLabel || "Official schedule") : url === event.structure ? "Official structure sheet" : url === event.confirmSource ? "Official venue page" : (source ? source.name : "Official rules evidence");
      return `<div class="source-item"><div class="source-left"><strong>${esc(label)}</strong><small>${esc(source ? source.kind : "Official source")}${source ? ` · checked ${esc(source.checked || "date not recorded")}` : ""}</small></div><div class="source-right">${link(url, "Open source")}${source ? monitorFor(source.id, monitor, source) : ""}</div></div>`;
    }).join("");
    const rules = Object.entries(event.rules || {}).map(([key, value]) => evidenceHtml(ruleTitle(key), value, data, monitor)).join("");
    return `<details class="source-details"><summary>Provenance & entry-rule evidence</summary><div class="source-list" style="margin-top:10px">${sourceList || `<div class="empty">No official source URL has been recorded.</div>`}</div><div class="evidence-grid">${evidenceHtml("Published buy-in", event.entryFeeEvidence, data, monitor)}${evidenceHtml("Published guarantee", event.guaranteeEvidence, data, monitor)}${event.dateEvidence ? evidenceHtml("Schedule date", event.dateEvidence, data, monitor) : ""}</div><h4 style="margin:14px 0 7px">Rule checks · unknown is not a pass</h4><div class="evidence-grid">${rules || `<div class="empty">Event-specific rule statements are not structured yet.</div>`}</div></details>`;
  }

  function ruleTitle(key) {
    const titles = { singleEntry: "One entry total", reEntry: "Re-entry", rebuy: "Rebuy", addOn: "Add-on", paidChipAdvantage: "Paid chip advantage", flights: "Starting flights", bounty: "Bounty format", satellite: "Satellite format" };
    return titles[key] || key;
  }

  function eventRow(event, data, monitor) {
    const date = event.dateISO ? `${esc(formatDate(event.dateISO))}${event.dateEvidence && event.dateEvidence.status !== "printed" ? ` <span class="pill warn">Date inferred</span>` : ""}` : `<span class="muted">${esc(event.date || "Undated recurring lead")}</span>`;
    const tags = (event.tags || []).slice(0, 4).map((tag) => `<span class="pill gray">${esc(tag.replaceAll("-", " "))}</span>`).join(" ");
    const buy = event.buyIn ? esc(event.buyIn) : `<span class="muted">Not published / unverified</span>`;
    const gtd = event.guarantee ? esc(event.guarantee) : `<span class="muted">Not published / not cash guarantee</span>`;
    const entry = event.entryStatus || "Strict-entry rule not verified.";
    return `<tr data-event-id="${esc(event.id)}"><td>${date}<span class="muted">${esc(event.time || "Time not published")}${event.registrationCloses ? ` · reg closes ${esc(event.registrationCloses)}` : ""}</span></td><td><strong>${esc(event.venue || "Unknown venue")}</strong><span class="muted">${esc(event.eventNumber ? `Event #${event.eventNumber}` : (event.format || ""))}</span></td><td><strong>${esc(event.event || "Event title not recorded")}</strong><div class="tag-list">${tags}</div><span class="muted">${esc(event.format || "Format not recorded")}</span></td><td>${buy}<span class="muted">published headline buy-in</span></td><td>${gtd}<span class="muted">${esc(event.guaranteeBasis || "not a payout forecast")}</span></td><td>${strictLabel(event)}<span class="muted">${esc(entry)}</span></td><td>${eventSourcesHtml(event, data, monitor)}</td></tr>`;
  }

  function renderTournaments(data, monitor) {
    const venues = [...new Map((data.tournaments || []).map((event) => [event.venueId, event.venue])).entries()].filter(([id]) => id);
    const query = new URLSearchParams(location.search);
    return `<section class="hero"><div class="eyebrow">Tournament schedule · row-level evidence</div><h1>Search the schedule. Keep the strict-entry gate honest.</h1><p>${esc(data.scheduleCoverage?.listedRows || 0)} Venetian starts through Dec. 23 are included, plus selected Wynn/WPT, recurring Wynn, Bellagio and ARIA leads. The inventory is not a complete Strip-wide calendar.</p></section>
      <div class="notice danger"><strong>No event currently passes the full single-entry rule.</strong> Only a row with one entry total explicitly confirmed and all additional-spend avenues explicitly ruled out could pass. An unmentioned rule stays unknown.</div>
      <section class="section"><div class="filter-panel"><div class="filter-grid"><label>From date<input type="date" id="event-from"></label><label>Through date<input type="date" id="event-to"></label><label>Venue<select id="event-venue"><option value="">All venues</option>${venues.map(([id, name]) => `<option value="${esc(id)}">${esc(name)}</option>`).join("")}</select></label><label>Search rows<input type="search" id="event-query" placeholder="Event, venue, guarantee, format…"></label><label class="check-label"><input type="checkbox" id="event-strict"> Strict-entry verified only</label><label class="check-label"><input type="checkbox" id="event-dated"> Hide undated recurring leads</label><button class="btn" id="event-reset" type="button">Reset filters</button></div></div>
      <div class="section-head"><div><h2>All listed event starts</h2><p>Buy-in and guarantee are published headline values where available; neither implies an entry cap, expected value, or actual payout.</p></div><div class="toolbar-actions"><button class="btn" id="event-export" type="button">Download filtered CSV</button></div></div><p class="filters-summary" id="event-count" aria-live="polite"></p><div class="table-wrap"><table><thead><tr><th>Date / start</th><th>Venue / event no.</th><th>Event / format</th><th>Buy-in</th><th>Guarantee</th><th>Eligibility status</th><th>Sources & provenance</th></tr></thead><tbody id="event-rows"></tbody></table></div><div class="empty" id="event-empty" hidden><strong>No rows match these filters.</strong> If strict-only is selected, this snapshot has no confirmed strict-entry event. This does not prove that no qualifying event exists in Las Vegas.</div><p class="smallprint">Rows with “Date inferred” use the checked-in Venetian parser’s row-order date reconstruction where the schedule omitted a repeated date label. The official schedule remains linked on every row.</p></section>`;
  }

  function initTournamentControls(data) {
    const from = document.querySelector("#event-from");
    const to = document.querySelector("#event-to");
    const venue = document.querySelector("#event-venue");
    const query = document.querySelector("#event-query");
    const strict = document.querySelector("#event-strict");
    const dated = document.querySelector("#event-dated");
    const rowsEl = document.querySelector("#event-rows");
    const countEl = document.querySelector("#event-count");
    const emptyEl = document.querySelector("#event-empty");
    const params = new URLSearchParams(location.search);
    query.value = params.get("q") || "";
    from.value = params.get("from") || "";
    to.value = params.get("to") || "";
    venue.value = params.get("venue") || "";
    strict.checked = params.get("strict") === "1";
    const update = () => {
      const results = Logic.filterEvents(data.tournaments || [], { from: from.value, to: to.value, venue: venue.value, query: query.value, strictOnly: strict.checked, datedOnly: dated.checked });
      rowsEl.innerHTML = sortByDateTime(results).map((event) => eventRow(event, data, window.PokerPlannerMonitor || emptyMonitor)).join("");
      countEl.textContent = `${results.length} of ${(data.tournaments || []).length} rows shown · ${results.filter(Logic.strictEligible).length} strict-entry verified in this view`;
      emptyEl.hidden = results.length > 0;
    };
    [from, to, venue, query, strict, dated].forEach((control) => control.addEventListener("input", update));
    document.querySelector("#event-reset").addEventListener("click", () => { from.value = ""; to.value = ""; venue.value = ""; query.value = ""; strict.checked = false; dated.checked = false; update(); });
    document.querySelector("#event-export").addEventListener("click", () => downloadCsv(sortByDateTime(Logic.filterEvents(data.tournaments || [], { from: from.value, to: to.value, venue: venue.value, query: query.value, strictOnly: strict.checked, datedOnly: dated.checked }))));
    update();
  }

  function csvCell(value) { return `"${String(value ?? "").replaceAll('"', '""')}"`; }
  function downloadCsv(rows) {
    const headers = ["date", "dateISO", "time", "venue", "eventNumber", "event", "buyIn", "guarantee", "format", "strictStatus", "entryStatus", "schedule", "structure"];
    const output = [headers.join(","), ...rows.map((row) => headers.map((key) => csvCell(row[key])).join(","))].join("\r\n");
    const blob = new Blob([output], { type: "text/csv;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a"); anchor.href = url; anchor.download = "vegas-poker-events.csv"; anchor.click(); URL.revokeObjectURL(url);
  }

  function hotelSourceLinks(hotel, monitor) {
    const links = [
      [hotel.source, "Hotel / room source"], [hotel.feeSource, "Fee terms"], [hotel.taxSource, "Tax / occupancy terms"], [hotel.parkingSource, "Parking terms"], [hotel.bookingSource, "Booking page"],
    ].filter(([url], index, all) => url && all.findIndex((item) => item[0] === url) === index);
    return `<div class="source-links">${links.map(([url, label]) => link(url, label)).join("")}</div>`;
  }

  function renderHotels(data, monitor, rateData) {
    const sample = data.sampleStay || { arrival: "", departure: "", occupancy: { rooms: 1, adults: 2, children: 0 } };
    const logs = rateData.logs || [];
    return `<section class="hero"><div class="eyebrow">Hotels · itemized terms and a local calculator</div><h1>Compare what you know. Leave the quote blank until it is real.</h1><p>Published resort fees, occupancy terms, cancellation notes and parking are separated from live room prices. Exact date-matched checkout totals have not been verified, so no hotel is ranked.</p></section>
      <div class="notice"><strong>Calculator output is a user-entered planning estimate, not a hotel quote.</strong> Room rate and tax values are blank until you enter them from the official checkout. Published fee inputs are prefilled where found; confirm offer exceptions and tax treatment before relying on any result. Your inputs stay in this browser.</div>
      <section class="section"><div class="section-head"><div><h2>Stay assumptions</h2><p>${esc(sample.label || "Set the exact dates and occupancy")}</p></div><span class="pill warn">${sample.userProvided ? "Traveler-provided dates" : "Research sample — edit before use"}</span></div><div class="filter-panel"><div class="global-fields"><label>Arrival<input type="date" data-stay-global="arrival" value="${esc(sample.arrival || "")}"></label><label>Departure<input type="date" data-stay-global="departure" value="${esc(sample.departure || "")}"></label><label>Rooms<input type="number" min="1" step="1" data-stay-global="rooms" value="${esc(sample.occupancy?.rooms || 1)}"></label><label>Adults<input type="number" min="0" step="1" data-stay-global="adults" value="${esc(sample.occupancy?.adults || 2)}"></label><label>Children<input type="number" min="0" step="1" data-stay-global="children" value="${esc(sample.occupancy?.children || 0)}"></label><label>Vehicles<input type="number" min="0" step="1" data-stay-global="vehicles" value="0"></label><button class="btn danger" type="button" id="reset-calculator">Clear saved calculator inputs</button></div><p class="smallprint" id="calculator-save-state">Inputs are saved locally in this browser only.</p></div></section>
      <section class="section"><div class="section-head"><div><h2>Hotel cost inputs</h2><p>Fill room rate, tax and any extra charges using the same dates, occupancy and room type for a fair comparison.</p></div></div><div class="cards">${(data.hotels || []).map((hotel) => hotelCard(hotel, logs.find((log) => log.hotelId === hotel.id), monitor)).join("")}</div></section>
      ${routesSection(data)}
      <section class="section"><div class="section-head"><div><h2>How the estimate is calculated</h2><p>All amounts are in USD.</p></div></div><div class="card"><p><strong>Room subtotal</strong> = nightly room rate × nights × rooms. <strong>Resort fee</strong> = fee per room/night × nights × rooms. <strong>Room tax</strong> uses the entered rate on room and known extra-occupant charges; resort-fee tax uses the separate entered rate. Parking and any other mandatory stay fees are added separately.</p><p>For a complete result, enter an exact room rate, both relevant tax rates, the resort-fee amount, extra-occupant fee when applicable, and any other mandatory charges. If you drive, enter parking per vehicle. Resort-fee waivers, packages, occupancy rules, room upgrades, and taxes can vary by booked offer; compare with the final checkout and folio.</p></div></section>`;
  }

  function routesSection(data) {
    const routes = data.routes || [];
    if (!routes.length) return "";
    return `<section class="section"><div class="section-head"><div><h2>Walking-route leads</h2><p>Third-party estimates are shown as leads, not verified entrance-to-entrance walking times.</p></div></div><div class="notice info"><strong>Thirty-minute threshold is not certified.</strong> Route start/end access points, casino indoor distances, accessibility and current pedestrian access have not been verified. Same-property rows mean the hotel and poker room share a property—not that the room-to-room walk has been measured.</div><div class="table-wrap"><table><thead><tr><th>From</th><th>To</th><th>Reported estimate</th><th>Distance</th><th>Evidence status</th><th>Source</th></tr></thead><tbody>${routes.map((route) => `<tr><td>${esc(route.from)}</td><td>${esc(route.to)}</td><td>${route.minutes == null ? "Not measured" : `${esc(route.minutes)} min (estimate)`}</td><td>${esc(route.distance || "Not recorded")}</td><td><span class="status unverified">${esc(route.verified ? "Verified" : route.sourceType || "Unverified")}</span></td><td>${link(route.source, route.sourceType === "official property relationship" ? "Property source" : "Route estimate")}</td></tr>`).join("")}</tbody></table></div></section>`;
  }

  function savedCalculator() {
    try { return JSON.parse(localStorage.getItem("vegas-poker-calculator-v1") || "{}"); }
    catch (_) { return {}; }
  }

  function inputValue(saved, hotel, field, fallback) {
    const stored = saved.hotels?.[hotel.id]?.[field];
    if (stored !== undefined) return stored;
    return fallback == null ? "" : fallback;
  }

  function numberField(hotel, field, label, value, hint, step = "0.01") {
    return `<div class="calc-field"><label>${esc(label)}<input type="number" min="0" step="${esc(step)}" data-hotel-field="${esc(hotel.id)}:${esc(field)}" value="${esc(value)}" placeholder="${field === "roomRate" ? "Enter exact-date quote" : "Enter / confirm"}"><span class="hint">${esc(hint)}</span></label></div>`;
  }

  function hotelCard(hotel, log, monitor) {
    const saved = savedCalculator();
    const inputs = saved.hotels?.[hotel.id] || {};
    const fee = inputValue(saved, hotel, "resortFee", hotel.resortFeeUsdPerNight);
    const roomTax = inputValue(saved, hotel, "roomTaxPercent", hotel.roomTaxRatePercent);
    const feeTax = inputValue(saved, hotel, "resortFeeTaxPercent", hotel.resortFeeTaxRatePercent);
    const extra = inputValue(saved, hotel, "extraOccupantRate", hotel.extraOccupantUsdPerPersonNight);
    const parking = inputValue(saved, hotel, "parkingPerVehicleNight", hotel.parkingUsdPerVehicleNight);
    const sourceId = (window.PokerPlannerData?.officialSources || []).find((source) => source.url === hotel.feeSource)?.id;
    return `<article class="card hotel-card" id="hotel-${esc(hotel.id)}" data-hotel-id="${esc(hotel.id)}"><div class="eyeline">${esc(hotel.area || "Las Vegas")}</div><span class="pill warn">Room quote not verified</span><h3>${esc(hotel.name)}</h3><p><strong>Near:</strong> ${esc(hotel.venue || "Poker room details not recorded")}</p><div class="evidence-box"><strong>Official fee / policy snapshot</strong><p>Resort fee: ${esc(hotel.resortFee || "Not verified")}. ${esc(hotel.resortFeePolicy || "Confirm the booked offer.")}</p><p>Tax: ${esc(hotel.taxes || "Not verified")}</p><p>Occupancy: ${esc(hotel.extraOccupantPolicy || "Confirm with the property.")}${hotel.extraOccupantUsdPerPersonNight != null ? ` Published extra-occupant fee: ${money(hotel.extraOccupantUsdPerPersonNight)} per person/night above two per room.` : ""}</p><p>Parking: ${esc(hotel.parking || "Not verified")}${hotel.parkingPolicyNote ? ` ${esc(hotel.parkingPolicyNote)}` : ""}</p><p>Cancellation: ${esc(hotel.cancellation || "Rate-specific terms not confirmed")}</p><p>Quality: ${esc(hotel.qualityNote || "Not independently scored.")}</p>${sourceId ? `<p class="source-state">${monitorFor(sourceId, monitor, (window.PokerPlannerData.officialSources || []).find((source) => source.id === sourceId))}</p>` : ""}${hotelSourceLinks(hotel, monitor)}</div>
        <h4 style="margin:15px 0 3px">Your inputs for this stay</h4><div class="calc-grid">${numberField(hotel, "roomRate", "Room rate / room / night", inputValue(saved, hotel, "roomRate", ""), "Enter exact-date rate from official checkout.")}${numberField(hotel, "roomTaxPercent", "Room / occupancy tax %", roomTax, hotel.roomTaxRateKnown ? "Published rate; reconfirm for your booking." : "Not recorded here; confirm and enter.")}${numberField(hotel, "resortFee", "Resort fee / room / night", fee, hotel.resortFeeUsdPerNight == null ? "Unknown — enter confirmed value or 0 if none." : "Published amount; confirm offer eligibility.")}${numberField(hotel, "resortFeeTaxPercent", "Resort-fee tax %", feeTax, hotel.resortFeeTaxRateKnown ? "Published tax input; reconfirm for your booking." : "Tax rate not recorded; confirm and enter.")}${numberField(hotel, "extraOccupantRate", "Extra occupant / person / night", extra, hotel.extraOccupantUsdPerPersonNight == null ? "Needed only when >2 occupants per room; confirm or enter 0." : "Published amount above two occupants per room.")}${numberField(hotel, "parkingPerVehicleNight", "Parking / vehicle / night", parking, hotel.parkingIncludedVehicleLimit ? `Included for up to ${hotel.parkingIncludedVehicleLimit} guest vehicle(s); confirm any extra-vehicle rate.` : (hotel.parkingUsdPerVehicleNight == null ? "If using a vehicle, confirm rate and enter it." : "Published hotel-guest rate / inclusion; confirm your case."))}${numberField(hotel, "otherMandatoryFees", "Other mandatory stay fees", inputValue(saved, hotel, "otherMandatoryFees", 0), "Enter total USD for the stay; default assumes 0.")}</div>
        <div class="estimate incomplete" data-estimate="${esc(hotel.id)}" aria-live="polite"><strong>Estimate not ready</strong>Enter an exact room rate and the missing tax/fee values.</div>
        <details class="source-details"><summary>Rate-search attempt log</summary>${log ? `<div class="evidence-box"><strong>${esc(log.status)} · ${esc(log.arrival)} to ${esc(log.departure)} · ${esc(log.nights)} nights · ${esc(log.occupancy?.adults || 0)} adults</strong><p>${esc(log.result)}</p><p>Room subtotal: ${log.roomSubtotalUsd == null ? "not captured" : money(log.roomSubtotalUsd)} · checkout total: ${log.checkoutTotalUsd == null ? "not captured" : money(log.checkoutTotalUsd)} · all-in comparable: ${log.allInComparable ? "yes" : "no"}</p><p>${esc(log.cancellationTerms || "")}</p>${link(log.source, "Open the attempted official search")}</div>` : `<p class="smallprint">No dated hotel-rate attempt is logged for this property.</p>`}</details></article>`;
  }

  function initHotelCalculator(data) {
    const saved = savedCalculator();
    const sample = data.sampleStay || {};
    document.querySelectorAll("[data-stay-global]").forEach((input) => {
      const key = input.dataset.stayGlobal;
      if (saved.global && saved.global[key] !== undefined) input.value = saved.global[key];
    });
    document.querySelectorAll("[data-hotel-field]").forEach((input) => {
      const [id, field] = input.dataset.hotelField.split(":");
      if (saved.hotels?.[id]?.[field] !== undefined) input.value = saved.hotels[id][field];
    });
    const globals = () => Object.fromEntries([...document.querySelectorAll("[data-stay-global]")].map((input) => [input.dataset.stayGlobal, input.value]));
    const save = () => {
      const value = { global: globals(), hotels: {} };
      document.querySelectorAll("[data-hotel-field]").forEach((input) => {
        const [id, field] = input.dataset.hotelField.split(":");
        value.hotels[id] ||= {};
        value.hotels[id][field] = input.value;
      });
      try { localStorage.setItem("vegas-poker-calculator-v1", JSON.stringify(value)); document.querySelector("#calculator-save-state").textContent = "Saved locally in this browser. No booking data is sent to a server."; }
      catch (_) { document.querySelector("#calculator-save-state").textContent = "Browser storage is unavailable; inputs will remain only until you leave this page."; }
    };
    const calcAll = () => {
      const global = globals();
      for (const hotel of data.hotels || []) {
        const read = (field) => document.querySelector(`[data-hotel-field="${CSS.escape(hotel.id)}:${CSS.escape(field)}"]`)?.value ?? "";
        const result = Logic.calculateStay({ arrival: global.arrival, departure: global.departure, rooms: global.rooms, adults: global.adults, children: global.children, vehicles: global.vehicles, parkingIncludedVehicles: hotel.parkingIncludedVehicleLimit || 0, roomRate: read("roomRate"), roomTaxPercent: read("roomTaxPercent"), resortFee: read("resortFee"), resortFeeTaxPercent: read("resortFeeTaxPercent"), extraOccupantRate: read("extraOccupantRate"), parkingPerVehicleNight: read("parkingPerVehicleNight"), otherMandatoryFees: read("otherMandatoryFees") });
        const target = document.querySelector(`[data-estimate="${CSS.escape(hotel.id)}"]`);
        if (!target) continue;
        if (result.complete) {
          target.classList.remove("incomplete");
          target.innerHTML = `<strong>Planning estimate · ${money(result.total)} total · ${money(result.nightlyAverage)} / night</strong>${result.nights} nights · ${result.rooms} room(s) · ${result.occupants} occupant(s). This is calculated from entered values, not an official quote.<div class="estimate-breakdown"><span>Room subtotal ${money(result.roomSubtotal)}</span><span>Room / occupancy tax ${money(result.roomTaxTotal)}</span><span>Resort fee ${money(result.resortFeeTotal)}</span><span>Resort-fee tax ${money(result.resortFeeTaxTotal)}</span><span>Extra occupants ${money(result.extraOccupantTotal)}</span><span>Parking ${money(result.parkingTotal)}</span><span>Other mandatory fees ${money(result.otherFees)}</span></div>`;
        } else {
          target.classList.add("incomplete");
          target.innerHTML = `<strong>Incomplete · no all-in total shown</strong>Known pre-tax inputs currently total ${money(result.knownPreTax)}. Missing / invalid: ${result.errors.map(esc).join(" ")}`;
        }
      }
    };
    document.querySelectorAll("[data-stay-global], [data-hotel-field]").forEach((input) => input.addEventListener("input", () => { save(); calcAll(); }));
    document.querySelector("#reset-calculator").addEventListener("click", () => { try { localStorage.removeItem("vegas-poker-calculator-v1"); } catch (_) {} location.reload(); });
    calcAll();
  }

  function renderSchedule(data) {
    const datedEvents = sortByDateTime((data.tournaments || []).filter((event) => event.dateISO));
    const events = datedEvents;
    const earliest = [...datedEvents].sort((a, b) => (Logic.parseTime(a.time) ?? 9999) - (Logic.parseTime(b.time) ?? 9999))[0];
    const dates = [...new Set(events.map((event) => event.dateISO))];
    return `<section class="hero"><div class="eyebrow">Day plan · schedule collision checks</div><h1>Start gaps are visible. Finish times are not.</h1><p>This check compares published start times against a travel / registration buffer you choose. It does not estimate tournament duration, guarantee a finish window, or certify an itinerary.</p><div class="hero-meta">Earliest time-of-day among dated rows: ${earliest ? `${esc(earliest.time)} · ${esc(formatDate(earliest.dateISO))} · ${esc(earliest.venue)}.` : "No dated event start available."}</div></section>
      <div class="notice info"><strong>Known limit:</strong> a morning tournament can run into evening starts, but field size and finish time are unknown. A start-gap warning only means two scheduled starts are close together; it does not determine whether late registration or a transition is possible.</div>
      <section class="section"><div class="filter-panel"><div class="filter-grid"><label>Travel / registration buffer (minutes)<input type="number" min="0" max="360" step="5" value="45" id="schedule-buffer"></label><label>From date<input type="date" id="schedule-from"></label><label>Through date<input type="date" id="schedule-to"></label><button class="btn" id="schedule-reset" type="button">Reset</button></div></div><div class="section-head"><div><h2>Start-time gaps within the chosen buffer</h2><p>Cross-venue pairs may require travel; same-venue pairs still require a room/registration check.</p></div></div><p id="schedule-conflict-count" class="filters-summary" aria-live="polite"></p><div id="schedule-conflicts" class="cards"></div><div id="schedule-no-conflicts" class="empty" hidden><strong>No start pair falls within this buffer.</strong> This is not proof that events can be played consecutively; duration and finish times are not known.</div></section>
      <section class="section"><div class="section-head"><div><h2>Dated event starts in the selected range</h2><p>${esc(dates.length)} calendar days represented in the current schedule snapshot.</p></div></div><div class="table-wrap"><table><thead><tr><th>Date</th><th>Start</th><th>Venue</th><th>Event</th><th>Registration closes</th><th>Entry status</th><th>Official source</th></tr></thead><tbody id="schedule-rows"></tbody></table></div></section>`;
  }

  function startTimeConflictCard(conflict, monitor, data) {
    const first = conflict.first;
    const second = conflict.second;
    const label = conflict.sameVenue ? "Same-venue start gap" : "Cross-venue start gap";
    return `<article class="card"><span class="pill ${conflict.sameVenue ? "warn" : "danger"}">${esc(label)} · ${esc(conflict.gapMinutes)} min</span><h3>${esc(formatDate(conflict.date))}</h3><p><strong>${esc(first.time)} · ${esc(first.venue)}</strong><br>${esc(first.event)}</p><p><strong>${esc(second.time)} · ${esc(second.venue)}</strong><br>${esc(second.event)}</p><p>${conflict.sameVenue ? "Same venue does not imply a playable sequence; ask about registration and event overlap." : "The two venues differ; confirm travel access, registration cutoff and whether the first event has ended."}</p><div class="source-links">${link(first.schedule, "First event source")}${link(second.schedule, "Second event source")}</div></article>`;
  }

  function initScheduleControls(data) {
    const bufferInput = document.querySelector("#schedule-buffer");
    const from = document.querySelector("#schedule-from");
    const to = document.querySelector("#schedule-to");
    const rows = sortByDateTime((data.tournaments || []).filter((event) => event.dateISO));
    const update = () => {
      const chosen = rows.filter((event) => (!from.value || event.dateISO >= from.value) && (!to.value || event.dateISO <= to.value));
      const conflicts = Logic.scheduleConflicts(chosen, bufferInput.value);
      document.querySelector("#schedule-conflict-count").textContent = `${conflicts.length} start-time pair(s) within ${bufferInput.value || 0} minutes · ${chosen.length} dated starts in range`;
      document.querySelector("#schedule-conflicts").innerHTML = conflicts.map((item) => startTimeConflictCard(item, window.PokerPlannerMonitor || emptyMonitor, data)).join("");
      document.querySelector("#schedule-no-conflicts").hidden = conflicts.length > 0;
      document.querySelector("#schedule-rows").innerHTML = chosen.map((event) => `<tr><td>${esc(formatDate(event.dateISO))}${event.dateEvidence && event.dateEvidence.status !== "printed" ? ` <span class="pill warn">Date inferred</span>` : ""}</td><td>${esc(event.time || "Unknown")}</td><td>${esc(event.venue || "Unknown")}</td><td><strong>${esc(event.event || "Unknown")}</strong><span class="muted">${esc(event.format || "")}</span></td><td>${esc(event.registrationCloses || "Not recorded")}</td><td>${strictLabel(event)}<span class="muted">${esc(event.entryStatus || "")}</span></td><td>${link(event.schedule, event.scheduleLabel || "Official schedule")}</td></tr>`).join("");
    };
    [bufferInput, from, to].forEach((input) => input.addEventListener("input", update));
    document.querySelector("#schedule-reset").addEventListener("click", () => { bufferInput.value = "45"; from.value = ""; to.value = ""; update(); });
    update();
  }

  function renderVenues(data, monitor) {
    const venues = data.venues || [];
    return `<section class="hero"><div class="eyebrow">Venue index · source-linked pages</div><h1>Choose a poker room, then inspect its dates and terms.</h1><p>Each venue page gathers the schedule leads, entry-rule status and official page links currently recorded for that room. Venue coverage is intentionally selective.</p></section><section class="section"><div class="cards">${venues.map((venue) => {
      const rows = (data.tournaments || []).filter((event) => event.venueId === venue.id);
      const path = `venues/${venue.id}.html`;
      return `<article class="card"><span class="pill blue">${esc(venue.area || "Las Vegas")}</span><h3>${esc(venue.name)}</h3><p>${esc(venue.summary || "Venue summary not recorded.")}</p><p><strong>${rows.length}</strong> linked schedule rows · ${esc(venue.status || "Status not recorded")}</p><a class="card-link" href="${esc(rootLink(path))}">Open ${esc(venue.name)} page →</a></article>`;
    }).join("")}</div></section><section class="section"><div class="section-head"><div><h2>Venue coverage caveat</h2><p>Other Strip and downtown rooms may have events that are outside this bounded source review.</p></div></div><div class="notice">This is not a complete Las Vegas tournament calendar. A room's recurring schedule, daily poster or undated guide is not a date-specific event confirmation.</div></section>`;
  }

  function renderVenue(data, monitor) {
    const venue = (data.venues || []).find((row) => row.id === venueId);
    if (!venue) return `<div class="empty"><strong>Venue page not found.</strong> Choose a venue from <a href="${esc(rootLink("venues.html"))}">the venue index</a>.</div>`;
    const rows = sortByDateTime((data.tournaments || []).filter((event) => event.venueId === venue.id));
    const sources = [...new Set([venue.scheduleSource, venue.roomSource, ...rows.flatMap((row) => [row.structure, row.schedule])].filter(Boolean))];
    return `<section class="hero venue-hero"><div><div class="eyebrow">Venue page · ${esc(venue.area || "Las Vegas")}</div><h1>${esc(venue.name)}</h1><p>${esc(venue.summary || "Source-linked event leads and venue information.")}</p><div class="venue-meta">${esc(venue.pokerRoom || "Poker room")}</div></div><div class="venue-meta">${rows.length} linked event rows<br>Checked ${esc(venue.lastChecked || data.asOf || "unknown")}</div></section>
      <div class="notice ${venue.id === "bellagio" ? "danger" : "info"}"><strong>${esc(venue.status || "Terms unverified")}</strong> A venue page is a research aid; confirm current dates, entry rules, and registration availability directly with the room.</div>
      <section class="section"><div class="section-head"><div><h2>Official source links</h2><p>All current schedule evidence recorded for this venue.</p></div></div><div class="source-list">${sources.map((url) => { const src = (data.officialSources || []).find((item) => item.url === url); return `<article class="source-item"><div class="source-left"><strong>${esc(src?.name || "Official venue source")}</strong><small>${esc(src?.kind || "Official source")} · ${esc(src?.checked || data.asOf || "date not recorded")}</small></div><div class="source-right">${link(url, "Open source")}${src ? monitorFor(src.id, monitor, src) : ""}</div></article>`; }).join("")}</div></section>
      <section class="section"><div class="section-head"><div><h2>Schedule rows (${rows.length})</h2><p>Every row retains its own source links, published buy-in / guarantee evidence and entry-rule status.</p></div><a class="card-link" href="${esc(rootLink("tournaments.html"))}?venue=${esc(venue.id)}">Open filterable schedule →</a></div>${rows.length ? `<div class="table-wrap"><table><thead><tr><th>Date / start</th><th>Event</th><th>Buy-in</th><th>Guarantee</th><th>Strict-entry status</th><th>Provenance</th></tr></thead><tbody>${rows.map((event) => `<tr><td>${esc(event.dateISO ? formatDate(event.dateISO) : event.date || "Undated")}<span class="muted">${esc(event.time || "Time unknown")}${event.dateEvidence && event.dateEvidence.status !== "printed" ? " · date inferred" : ""}</span></td><td><strong>${esc(event.event)}</strong><span class="muted">${esc(event.eventNumber ? `Event #${event.eventNumber} · ` : "")}${esc(event.format || "")}</span></td><td>${event.buyIn ? esc(event.buyIn) : "Unknown"}</td><td>${event.guarantee ? esc(event.guarantee) : "Not published"}</td><td>${strictLabel(event)}<span class="muted">${esc(event.entryStatus || "")}</span></td><td>${eventSourcesHtml(event, data, monitor)}</td></tr>`).join("")}</tbody></table></div>` : `<div class="empty">No event rows are linked to this venue in the snapshot.</div>`}</section>`;
  }

  function sourceMonitorCounts(data, monitor) {
    const monitored = (data.officialSources || []).filter((source) => source.monitor !== false);
    const records = monitor.sources || {};
    const baselined = monitored.filter((source) => records[source.id]?.sha256).length;
    const failed = monitored.filter((source) => records[source.id]?.status === "failure").length;
    return { monitored: monitored.length, baselined, failed, changes: (monitor.changes || []).length, changed: monitor.changedCount || 0 };
  }

  function renderSources(data, monitor) {
    const counts = sourceMonitorCounts(data, monitor);
    const changes = [...(monitor.changes || [])].sort((a, b) => String(b.detectedAt || "").localeCompare(String(a.detectedAt || "")));
    const failures = monitor.failures || [];
    return `<section class="hero"><div class="eyebrow">Official-source register · polling does not edit curated facts</div><h1>See the source, its history, and whether the monitor noticed a change.</h1><p>Weekly checks fingerprint official schedule, structure and hotel pages. A detected change is a review signal only: the monitor never rewrites event values or promotes an event to strict-entry eligible.</p></section>
      <div class="monitor-summary">${monitorChip("Monitored", counts.monitored)}${monitorChip("Baseline captured", counts.baselined)}${monitorChip("Latest changes", counts.changed)}${monitorChip("Latest failures", counts.failed)}</div>
      <div class="notice ${monitor.lastRun ? "info" : ""}"><strong>${monitor.lastRun ? `Last monitor run: ${esc(formatTimestamp(monitor.lastRun))}.` : "No monitor baseline has been recorded yet."}</strong> ${monitor.lastRun ? "The baseline enables future change comparisons; review differences in context before changing curated data." : "The first scheduled GitHub Actions run will establish baselines. This is not proof that pages have not changed since the manual research snapshot."}</div>
      <section class="section"><div class="section-head"><div><h2>Source changes</h2><p>Most recent changes recorded by the scheduled checker. A page hash change can also reflect formatting or site-template updates.</p></div></div>${changes.length ? `<div class="source-list">${changes.map((change) => `<article class="source-item"><div class="source-left"><strong>${esc(change.name || change.id)}</strong><small>${esc(change.summary || "Content fingerprint changed")} · ${esc(change.detectedAt || "date not recorded")}</small></div><div class="source-right">${link(change.url, "Review source")}<span class="status changed">Change detected</span></div></article>`).join("")}</div>` : `<div class="empty"><strong>${monitor.lastRun ? "No content change is recorded in the latest run." : "No change history yet."}</strong> ${monitor.lastRun ? "That does not guarantee the source is unchanged; it means the checker did not record a changed fingerprint." : "A first-run baseline is needed before content changes can be detected."}</div>`}</section>
      <section class="section"><div class="section-head"><div><h2>Latest check failures</h2><p>A temporary error is not treated as a source change.</p></div></div>${failures.length ? `<div class="source-list">${failures.map((failure) => `<article class="source-item"><div class="source-left"><strong>${esc(failure.name || failure.id)}</strong><small>${esc(failure.error || "Request failed")}</small></div><div class="source-right">${link(failure.url, "Retry source later")}<span class="status failure">Check failed</span></div></article>`).join("")}</div>` : `<div class="empty">No failures in the last recorded monitor run.</div>`}</section>
      <section class="section"><div class="section-head"><div><h2>Source register (${(data.officialSources || []).length})</h2><p>Booking-search URLs are intentionally excluded from scheduled monitoring; manual quote limitations remain in the hotel rate log.</p></div></div><div class="filter-panel"><div class="filter-grid"><label>Filter source rows<input id="source-query" type="search" placeholder="Name, ID, URL, type…"></label><label>Status<select id="source-status"><option value="">All sources</option><option value="monitored">Monitored</option><option value="unmonitored">Not polled</option><option value="changed">Changed</option><option value="failure">Last check failed</option><option value="unbaselined">No baseline yet</option></select></label></div></div><p id="source-count" class="filters-summary"></p><div class="source-list" id="source-list">${sourceRowsHtml(data, monitor)}</div></section>`;
  }

  function monitorChip(title, number) { return `<div class="monitor-chip"><strong>${esc(number)}</strong>${esc(title)}</div>`; }

  function sourceRowsHtml(data, monitor) {
    return (data.officialSources || []).map((source) => {
      const state = (monitor.sources || {})[source.id];
      const status = source.monitor === false ? "unmonitored" : !state?.sha256 ? "unbaselined" : state.status === "failure" ? "failure" : state.status === "changed" ? "changed" : "monitored";
      const statusLabel = source.monitor === false ? "Not polled" : !state?.sha256 ? "No baseline yet" : state.status === "failure" ? "Last check failed" : state.status === "changed" ? "Changed" : "Monitored";
      return `<article class="source-item" data-source-row data-source-status="${esc(status)}"><div class="source-left"><strong>${esc(source.name)}</strong><small>${esc(source.id)} · ${esc(source.kind || "official source")} · ${esc(source.checked || "check date not recorded")}</small><small>${esc(source.url)}</small></div><div class="source-right">${link(source.url, "Open source")}<span class="status ${status === "changed" ? "changed" : status === "failure" ? "failure" : status === "monitored" ? "unchanged" : "unverified"}">${esc(statusLabel)}</span>${state?.lastChecked ? `<span class="source-state">${esc(formatTimestamp(state.lastChecked))}</span>` : ""}</div></article>`;
    }).join("");
  }

  function initSourceFilters(data, monitor) {
    const query = document.querySelector("#source-query");
    const status = document.querySelector("#source-status");
    query.value = new URLSearchParams(location.search).get("q") || "";
    const rows = [...document.querySelectorAll("[data-source-row]")];
    const update = () => {
      const q = query.value.toLowerCase().trim();
      let shown = 0;
      rows.forEach((row) => {
        const matches = row.textContent.toLowerCase().includes(q) && (!status.value || row.dataset.sourceStatus === status.value);
        row.hidden = !matches;
        if (matches) shown += 1;
      });
      document.querySelector("#source-count").textContent = `${shown} of ${rows.length} source records shown`;
    };
    [query, status].forEach((input) => input.addEventListener("input", update));
    update();
  }

  function renderFlags(data, monitor) {
    return `<section class="hero"><div class="eyebrow">Open verification log · snapshot ${esc(data.asOf || "")}</div><h1>Unknowns stay visible until the source resolves them.</h1><p>These issues block confident rankings or itinerary claims, not publication. Every flag carries a next step and, where recorded, links back to primary material.</p></section><section class="section"><div class="cards">${(data.flags || []).map((flag) => {
      const sourceLinks = (flag.sourceIds || []).map((id) => (data.officialSources || []).find((source) => source.id === id)).filter(Boolean);
      const severityClass = flag.severity === "high" || flag.severity === "critical" ? "danger" : flag.severity === "medium" ? "warn" : "gray";
      return `<article class="card"><span class="pill ${severityClass}">${esc(flag.severity || "open")} · ${esc(flag.category || "Review")}</span><h3>${esc(flag.title)}</h3><p>${esc(flag.finding)}</p><p><strong>Next step:</strong> ${esc(flag.nextStep)}</p>${sourceLinks.length ? `<div class="source-links">${sourceLinks.map((source) => link(source.url, source.name)).join("")}</div>` : ""}</article>`;
    }).join("")}</div></section><section class="section"><div class="section-head"><div><h2>Current conservative conclusions</h2><p>What remains safe to say from the evidence set.</p></div></div><div class="grid-two"><article class="card"><h3>No strict-entry event confirmed</h3><p>Entry-rule silence is not treated as a no-re-entry/no-add-on guarantee. Explicitly extra-spend events remain separated in the data.</p></article><article class="card"><h3>No hotel ranked on a missing checkout total</h3><p>Date-specific booking failures and placeholders are preserved in the rate logs. Entered calculator estimates are separate from official quotes.</p></article></div></section>`;
  }

  function renderQuestions(data) {
    const questions = [
      ["Which exact dates and occupancy should the comparison use?", "The Dec. 10–14, 2026, two-adult stay in the rate log is only a working research sample.", "Provide arrival/departure, rooms, adults and children before comparing hotel totals."],
      ["Does this event permit exactly one entry total?", "A one-day label and a single listed flight do not prove an entry limit.", "Ask for written event-number-specific rules, including any later flight or re-entry."],
      ["Are re-entry, rebuy or add-ons possible?", "These are separate rule checks; a structure that does not mention one does not establish that it is forbidden.", "Ask the room to confirm each item separately."],
      ["Can paid gratuity or an add-on award extra chips?", "Bellagio weekly structures and Wynn daily sheets include examples of paid chip advantages.", "Check the exact structure sheet and entry receipt before calling an event strict-entry."],
      ["What is the final hotel checkout amount?", "Published nightly resort fees are not the same as a date-matched all-in stay total.", "Capture the final official checkout with room rate, taxes, fees, parking and cancellation terms."],
      ["Is the route actually under 30 minutes?", "Available route times are estimates; room-to-poker-room access points are not measured.", "Verify the guest and poker-room entrances on a current pedestrian map."],
      ["Can a second event start after the first?", "Start-time gaps do not establish finish time or registration overlap.", "Ask the room for late-registration cutoffs and realistic duration, then add travel and registration buffers."],
    ];
    return `<section class="hero"><div class="eyebrow">Open questions · before you register or book</div><h1>Close the decision-critical gaps first.</h1><p>These questions are kept separate from facts already verified from official sources.</p></section><section class="section"><div class="cards">${questions.map(([question, answer, next], index) => `<article class="card"><span class="pill blue">Question ${index + 1}</span><h3>${esc(question)}</h3><p>${esc(answer)}</p><p><strong>Ask / do:</strong> ${esc(next)}</p></article>`).join("")}</div></section><section class="section"><a class="card-link" href="${esc(rootLink("flagged.html"))}">See the current open flags →</a></section>`;
  }

  function renderSuggestions(data) {
    const actions = [
      ["Confirm strict rules by event number", "Obtain a current source sheet or written room confirmation for entry cap, re-entry, rebuy, add-on and paid chip advantages."],
      ["Use official booking checkout totals", "Compare identical dates, room type and occupancy. Record resort fee, tax, parking and cancellation conditions separately."],
      ["Keep manual research and automated polling separate", "The source monitor detects changes, but a person must review them before updating curated event facts."],
      ["Build a playable day only from registration cutoffs", "Use exact travel dates, realistic travel time and event duration guidance from the venue; do not assume a tournament is finished by a later start."],
      ["Expand beyond the current room sample", "Check primary sources room-by-room for other Strip venues; no complete market inventory is claimed."],
    ];
    return `<section class="hero"><div class="eyebrow">Recommended next actions</div><h1>Improve certainty before optimizing.</h1><p>These are workflow recommendations—not new tournament or hotel claims.</p></section><section class="section"><div class="cards">${actions.map(([title, text], i) => `<article class="card"><span class="pill">${String(i + 1).padStart(2, "0")}</span><h3>${esc(title)}</h3><p>${esc(text)}</p></article>`).join("")}</div></section><section class="section"><div class="notice info"><strong>No automated edits to curated findings.</strong> Weekly polling only updates <code>site/data/source-monitor.json</code>. A human must compare the official source and deliberately revise the research snapshot.</div></section>`;
  }

  function initTableSearch() {
    document.querySelectorAll("[data-table-search]").forEach((input) => {
      const table = document.querySelector(input.dataset.tableSearch);
      if (!table) return;
      input.addEventListener("input", () => {
        const query = input.value.toLowerCase().trim();
        table.querySelectorAll("tbody tr").forEach((row) => { row.hidden = !row.textContent.toLowerCase().includes(query); });
      });
    });
  }

  function initGlobalSearch(data) {
    const input = document.querySelector("#global-search");
    const results = document.querySelector("#global-results");
    if (!input || !results) return;
    const haystack = [];
    (data.tournaments || []).forEach((event) => haystack.push({ kind: "Tournament", name: `${event.event || "Event"} · ${event.venue || ""}`, meta: `${event.dateISO ? formatDate(event.dateISO) : event.date || "Undated"} · ${event.time || "Time unknown"} · ${event.strictStatus || "unverified"}`, href: `${rootLink("tournaments.html")}?q=${encodeURIComponent(event.event || "")}` }));
    (data.hotels || []).forEach((hotel) => haystack.push({ kind: "Hotel", name: hotel.name, meta: `${hotel.area || "Las Vegas"} · ${hotel.resortFee || "Fee unknown"}`, href: `${rootLink("hotels.html")}#hotel-${encodeURIComponent(hotel.id)}` }));
    (data.venues || []).forEach((venue) => haystack.push({ kind: "Venue", name: venue.name, meta: venue.area || "Las Vegas", href: rootLink(`venues/${venue.id}.html`) }));
    (data.officialSources || []).forEach((source) => haystack.push({ kind: "Official source", name: source.name, meta: `${source.id} · ${source.kind || "source"}`, href: `${rootLink("sources.html")}?q=${encodeURIComponent(source.id)}` }));
    (data.flags || []).forEach((flag) => haystack.push({ kind: "Review flag", name: flag.title, meta: flag.severity || "open", href: rootLink("flagged.html") }));
    const close = () => { results.classList.remove("open"); input.setAttribute("aria-expanded", "false"); };
    input.addEventListener("input", () => {
      const q = input.value.trim().toLowerCase();
      if (q.length < 2) { results.innerHTML = ""; close(); return; }
      const found = haystack.filter((item) => `${item.name} ${item.meta} ${item.kind}`.toLowerCase().includes(q)).slice(0, 9);
      results.innerHTML = found.length ? found.map((item) => `<a role="option" href="${esc(item.href)}"><strong>${esc(item.name)}</strong><small>${esc(item.kind)} · ${esc(item.meta)}</small></a>`).join("") : `<div class="source-item">No matches found.</div>`;
      results.classList.add("open"); input.setAttribute("aria-expanded", "true");
    });
    input.addEventListener("keydown", (event) => { if (event.key === "Escape") close(); if (event.key === "Enter" && results.querySelector("a")) { event.preventDefault(); results.querySelector("a").click(); } });
    document.addEventListener("click", (event) => { if (!event.target.closest(".global-search")) close(); });
  }
})();
