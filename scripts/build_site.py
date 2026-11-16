#!/usr/bin/env python3
"""Generate the static site in site/ from site/data/*.json.

Run: python3 scripts/build_data.py && python3 scripts/build_site.py
"""
import json, os, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "site", "data")
OUT = os.path.join(ROOT, "site")

def load(name):
    with open(os.path.join(DATA, name)) as f:
        return json.load(f)

def esc(x):
    return html.escape(str(x if x is not None else ""))

def money(x):
    if x in (None, ""):
        return ""
    try:
        return "$" + f"{float(x):,.0f}"
    except ValueError:
        return esc(x)

def link(url, text="source"):
    if not url:
        return '<span class="unverified">—</span>'
    return f'<a href="{esc(url)}" target="_blank" rel="noopener">{esc(text)}</a>'

NAV = [
    ("index.html", "Overview"),
    ("tournaments.html", "Tournaments"),
    ("schedule.html", "Day plan"),
    ("hotels.html", "Hotels"),
    ("routes.html", "Walking routes"),
    ("calculator.html", "Trip calculator"),
    ("venues.html", "Venues"),
    ("workflow.html", "Workflow"),
    ("monitoring.html", "Monitoring"),
    ("sources.html", "Sources"),
    ("questions.html", "Questions"),
    ("suggestions.html", "Suggestions"),
    ("flagged.html", "Flagged for review"),
]

def shell(title, active, body, script=""):
    nav = "\n".join(
        f'<a href="{href}" class="{"active" if href == active else ""}">{label}</a>'
        for href, label in NAV)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} · Vegas Poker Planner</title>
<link rel="stylesheet" href="assets/site.css">
</head>
<body>
<header class="top">
  <div class="brand"><a href="index.html">♠ Vegas Poker Planner</a>
    <span class="tag">official-sources only · snapshot 2026-11-16</span></div>
  <input id="nav-toggle" type="checkbox" aria-label="Menu"><label for="nav-toggle" class="burger">☰</label>
  <nav>{nav}</nav>
</header>
<main>
{body}
</main>
<footer class="foot">
  <p>Every table row links its official venue source. Values that cannot be confirmed from an official source are blank and flagged on
  <a href="flagged.html">Flagged for review</a>. Guarantees are not forecasts. Ratio = guaranteed pool ÷ buy-in, descriptive only.</p>
  <p>Built 2026-11-16 from official Venetian, Wynn, Bellagio, ARIA and Caesars pages/PDFs · <a href="monitoring.html">scheduled re-check</a> runs daily.</p>
</footer>
<script src="assets/app.js"></script>
{script}
</body>
</html>
"""

def tbl(headers, rows, cls="", tid=""):
    th = "".join(f"<th>{h}</th>" for h in headers)
    body = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    idattr = f'id="{tid}"' if tid else ""
    return f'<div class="tablewrap"><table {idattr} class="{cls}"><thead><tr>{th}</tr></thead><tbody>{body}</tbody></table></div>'

# ---------------------------------------------------------------- load data
T = load("tournaments.json")
H = load("hotels.json")["hotels"]
R = load("rates.json")["rates"]
RO = load("routes.json")["routes"]
S = load("sources.json")["sources"]
F = load("flags.json")["flags"]
Q = load("questions.json")["questions"]
SG = load("suggestions.json")["suggestions"]
TOUR = T["tournaments"]
DAYPLAN = T["dayplan"]
META = T["meta"]
BY_ID = {t["id"]: t for t in TOUR}

def tlink(t, text=None):
    return f'<a href="#{esc(t["id"])}">{esc(text or t["name"])}</a>'

def src_cell(t):
    a = link(t.get("scheduleSource"), "schedule")
    b = link(t.get("structureSource"), "structure")
    return a + (" · " + b if t.get("structureSource") else "")

def entry_cell(t):
    e = t.get("entry", {})
    bits = []
    if e.get("reentry"):
        bits.append("re-entry: " + esc(e["reentry"]))
    if e.get("rebuy") and e["rebuy"] not in ("no clause printed", "n/a"):
        bits.append("rebuy: " + esc(e["rebuy"]))
    if e.get("addon") and e["addon"] not in ("no clause printed", "n/a"):
        bits.append("add-on: " + esc(e["addon"]))
    if not bits:
        bits.append(esc(e.get("reentry") or "not published"))
    return "<small>" + "<br>".join(bits) + "</small>"

BUCKET_CLS = {"single-path": "ok", "spend-more": "warn", "review": "rev", "satellite": "sat", "restart": "rev"}

def badge(t):
    return f'<span class="badge {BUCKET_CLS.get(t["bucket"], "rev")}">{esc(t["bucketLabel"])}</span>'

# ---------------------------------------------------------------- pages
def page_index():
    n_single = sum(1 for t in TOUR if t["bucket"] == "single-path")
    n_spend = sum(1 for t in TOUR if t["bucket"] == "spend-more")
    best = sorted([t for t in TOUR if t["bucket"] == "single-path" and t.get("ratio")],
                  key=lambda x: -x["ratio"])[:8]
    best_rows = [[
        t["date"], t["time"], f'{esc(t["name"])} <small>(#{esc(t["eventNo"])})</small>',
        money(t["buyIn"]), money(t["guarantee"]), f'{t["ratio"]:.1f}×',
        badge(t), src_cell(t)] for t in best]
    flags_hi = [f for f in F if f["level"] == "high"]
    body = f"""
<h1>Las Vegas poker trip planner</h1>
<p class="lede">Upcoming live tournaments near the Strip, verified line-by-line from venue-controlled pages and official structure PDFs
(retrieved 2026-11-16), with hotel true-cost math, walking-route checks, a day planner and a trip-cost calculator.
Everything is labelled with its source; anything unconfirmed is blank and <a href="flagged.html">flagged</a>.</p>

<div class="cards">
  <div class="card"><b>{len(TOUR)}</b> schedule rows collected <small>5 venues · {len([t for t in TOUR if t['venue']=='venetian'])} Venetian DSE IV</small></div>
  <div class="card"><b>{n_single}</b> single-start events <small>structure sheets read; no re-entry/rebuy/add-on wording printed</small></div>
  <div class="card"><b>{n_spend}</b> spend-more rows <small>re-entry / rebuy / add-on / multi-flight — kept separate</small></div>
  <div class="card"><b>{len(F)}</b> flagged items <small>{len(flags_hi)} high priority</small></div>
</div>

<h2>Executive summary</h2>
<ul class="summary">
  <li><b>What's live now:</b> Venetian <i>DeepStack Extravaganza IV</i> runs <b>Nov 16 – Dec 23, 2026</b> (64 events, $3.6M+ in stated guarantees).
  Wynn's <i>WPT World Championship</i> festival runs <b>Nov 27 – Dec 21, 2026</b> in parallel.</li>
  <li><b>Single-entry focus:</b> {n_single} Venetian single-start events have complete official structure sheets — buy-in, house-fee/prize split,
  starting stack, level length, late-registration cut-off and guarantee are all printed. No sheet prints a re-entry, rebuy or add-on clause.
  No sheet prints the words "single entry" either — written confirmation from tournament staff is still recommended before treating any event
  as a strict freezeout (<a href="flagged.html#FL13">FL13</a>).</li>
  <li><b>Spend-more events are quarantined:</b> all Wynn daily tournaments (explicit re-entry; Friday adds unlimited rebuys + a $100 add-on),
  the WPT festival (re-entry on every captured event), Bellagio weeklies (re-entry through level 8 plus paid chip-boost gratuities) and
  Venetian multi-flight events sit in their own section with the exact clause quoted.</li>
  <li><b>Value ranking (descriptive only):</b> best confirmed guarantee-per-dollar among single-start events is the $200 NLH bounty family
  (40× guaranteed pool per $1 of buy-in — note the guarantee includes total bounties) and the $800 NLH Bounty #36 (93.8×).
  Ratios are descriptive, not a forecast of payouts.</li>
  <li><b>Hotels:</b> true nightly cost = rate + resort fee + 13.38% tax (tax applies to rate and resort fee).
  Venetian/Palazzo publish poker-suite starting rates ($119/$209, play-qualified); Wynn ($55+tax fee), Bellagio ($55+tax) verified.
  Dated room rates and checkout totals remain blank until trip dates are fixed — <a href="flagged.html#FL09">FL09</a>.</li>
  <li><b>Schedule reality check:</b> the earliest verified start is 9:10 AM (a satellite) and 10:10 AM for regular events — no verified 8 AM start
  exists in this window (<a href="flagged.html#FL12">FL12</a>). Day plans use one primary event plus a conditional evening fallback, and
  flag pairs that cannot be played in sequence.</li>
  <li><b>Automation:</b> a scheduled GitHub Actions job re-checks every official URL each morning, stores dated snapshots, and marks rows
  whose source text changed (<a href="monitoring.html">Monitoring</a>).</li>
</ul>

<h2>Best confirmed single-start events by guaranteed pool ÷ buy-in</h2>
<p class="note">Descriptive ratio only — not a forecast. Bounty events whose guarantee includes total bounties are labelled in the event column.
Flights and satellites are excluded from this ranking.</p>
{tbl(["Date", "Start", "Event", "Buy-in", "Guarantee", "Ratio", "Entry status", "Sources"], best_rows)}

<h2>Start here</h2>
<ol class="steps">
  <li><a href="workflow.html">Workflow</a> — the six-step decision path (fix dates → confirm entry policy → compare events → hotel true cost → day plan → reconfirm).</li>
  <li><a href="tournaments.html">Tournaments</a> — search, date filter, single-entry toggle, structured rule fields per row.</li>
  <li><a href="calculator.html">Trip calculator</a> — entries × buy-ins + nights × true hotel cost.</li>
  <li><a href="questions.html">Questions</a> — the eight open questions blocking firm decisions.</li>
  <li><a href="suggestions.html">Suggestions</a> — proposed improvements to review before implementing.</li>
</ol>
"""
    return shell("Overview", "index.html", body)

def page_tournaments():
    rows = []
    for t in sorted(TOUR, key=lambda x: (x["date"] if x["date"][:4].isdigit() else "zzz", x.get("timeMin") or 0)):
        if t["bucket"] == "restart":
            continue
        fee = " / ".join(x for x in [
            money(t["houseFee"]) + " house" if t.get("houseFee") is not None else "",
            money(t["staffFee"]) + " staff" if t.get("staffFee") not in (None, 0) else "",
            money(t.get("lipsFee")) + " LIPS" if t.get("lipsFee") else "",
            money(t["prizeShare"]) + " prize" if t.get("prizeShare") is not None else "",
        ] if x) or '<span class="unverified">blank</span>'
        ratio = f'{t["ratio"]:.1f}×' if t.get("ratio") else ""
        chk = f'{esc(t["status"])} · {esc(t["lastChecked"])}'
        rows.append([
            (f'<span id="{esc(t["id"])}" data-bucket="{esc(t["bucket"])}" data-date="{esc(t["date"])}" '
             f'data-venue="{esc(t["venue"])}" data-verified="{esc(t["status"])}">{esc(t["date"])}</span>'), esc(t["time"]),
            f'<b>{esc(t["name"])}</b>' + (f' <small>(#{esc(t["eventNo"])}{"·" + esc(t["flight"]) if t.get("flight") and t["flight"] not in ("main","restart") else ""})</small>' if t.get("eventNo") else ""),
            money(t["buyIn"]) or '<span class="unverified">blank</span>',
            money(t["guarantee"]) or '<span class="unverified">blank</span>',
            fee, ratio, entry_cell(t), esc(t.get("lateReg") or "") + (f'<br><small>est. length {t["estDurationHours"]}h</small>' if t.get("estDurationHours") else ""),
            badge(t), src_cell(t), chk])
    body = f"""
<h1>Tournaments</h1>
<p class="lede">Every row links its official schedule and (when available) its official structure sheet. Fee columns show the printed
house-fee / staff-charge / prize-pool split from the structure sheet. “blank” means the official source does not print the value.</p>
<div class="filters">
  <input type="search" id="tSearch" placeholder="Search events, venues, buy-ins… (searches all tables on this page)">
  <label>Date <input type="date" id="tDate" min="2026-11-16" max="2026-12-23"></label>
  <label>Venue
    <select id="tVenue">
      <option value="">All venues</option>
      <option value="venetian">Venetian</option><option value="wynn">Wynn</option>
      <option value="bellagio">Bellagio</option><option value="aria">ARIA</option>
      <option value="horseshoe">Horseshoe</option>
    </select></label>
  <label>Entry
    <select id="tBucket">
      <option value="">All entries</option>
      <option value="single-path">Single-entry / freezeout-style only</option>
      <option value="spend-more">Spend-more only (re-entry, rebuys, add-ons, flights)</option>
      <option value="satellite">Satellites</option>
      <option value="review">Review</option>
    </select></label>
  <label class="chk"><input type="checkbox" id="tConfirmed"> confirmed rows only (sheet read)</label>
  <button id="tReset" type="button">Reset</button>
</div>
<p class="note">Toggle “Single-entry / freezeout-style only” to hide every event where money can buy extra entries, extra chips or extra starting
flights. Those rows stay visible in the spend-more bucket with the exact clause quoted. <b>Note (FL13):</b> no sheet prints the words
“single entry” — “freezeout-style” means sheet reviewed with no re-entry/rebuy/add-on wording.</p>
{tbl(["Date", "Start", "Event", "Buy-in", "Guarantee", "Fee split (house/staff/…/prize)", "Ratio", "Entry rules (from official sheet)", "Late reg", "Status", "Sources", "Checked"], rows, tid="tTable")}
<p class="note">Restart rows (Day 2 / Day 3) are listed in the <a href="schedule.html">day plan</a> instead.</p>
"""
    return shell("Tournaments", "tournaments.html", body)

def page_schedule():
    rows = []
    for d in DAYPLAN:
        ev_cells = []
        for eid in d["events"]:
            t = BY_ID[eid]
            mark = ""
            if eid == d["primary"]:
                mark = ' <span class="badge ok">primary</span>'
            elif eid == d["fallback"]:
                mark = ' <span class="badge warn">fallback</span>'
            ow = t.get("overlapWith") or []
            warn = f' <span class="badge rev" title="overlaps {len(ow)} other row(s)">overlap</span>' if ow else ""
            ev_cells.append(f'{tlink(t, t["name"])} <small>{esc(t["time"])} · {money(t["buyIn"])}</small>{mark}{warn}')
        prim = tlink(BY_ID[d["primary"]]) if d.get("primary") else '<span class="unverified">—</span>'
        fall = tlink(BY_ID[d["fallback"]]) if d.get("fallback") else '<span class="unverified">none needed</span>'
        rows.append([esc(d["date"]), esc(d["weekday"]), prim, fall, "<br>".join(ev_cells), esc(d.get("note") or "")])
    body = f"""
<h1>Day plan — primary + conditional fallback</h1>
<p class="lede">One primary event per day (highest confirmed guarantee-per-dollar among single-start events), plus a conditional fallback
you can only enter if you exit the earlier event before its late-registration closes. Overlap badges mark pairs that cannot be played
in sequence given start time, late-reg cut-off and the structure-derived duration estimate ({esc(META['formula'].split('.')[0])} — see
<a href="flagged.html#FL14">FL14</a> on estimates).</p>
<p class="note">No verified 8:00 AM start exists in this window; the earliest regular start is 10:10 AM (<a href="flagged.html#FL12">FL12</a>).
An all-day 8 AM–late plan would need an unpublished early daily (e.g., Horseshoe) — <a href="questions.html#Q05">Q05</a>.</p>
{tbl(["Date", "Day", "Primary", "Conditional fallback", "All events (with role)", "Notes"], rows)}
<h2>How to use this plan</h2>
<ol class="steps">
  <li>Play the <b>primary</b> event. It has the best confirmed ratio that day among single-start, sheet-confirmed events.</li>
  <li>If you bust before the <b>fallback</b>'s late-registration closes (shown on its row), you can switch; if not, your day ends with the primary.</li>
  <li><b>Overlap</b> badges mean the earlier event plausibly runs past the later event's registration window — treat those as either/or, never both.</li>
</ol>
"""
    return shell("Day plan", "schedule.html", body)

def page_hotels():
    rows = []
    on_site = {"venetian", "palazzo", "wynn", "bellagio", "aria"}
    for h in H:
        rows.append([
            f'<b>{esc(h["name"])}</b><br><small>{esc(h["address"])}</small>'
            f'<span data-within30="{"true" if h["id"] in on_site else "unknown"}" hidden></span>',
            money(h["resortFee"]) + " + tax" if h.get("resortFee") is not None else '<span class="unverified">blank</span>',
            "13.38% on rate + resort fee" if h.get("taxRate") else '<span class="unverified">blank</span>',
            esc(h["parking"] or "") or '<span class="unverified">blank</span>',
            esc(h["cancellation"] or "") or '<span class="unverified">blank</span>',
            esc(h["rateNote"]),
            '<span class="unverified">blank (no dated quote)</span>',
            link(h["rateSource"], "rate source") + " · " + link(h["resortFeeSource"], "fee source") +
            (" · " + link(h["cancellationSource"], "cancel") if h.get("cancellationSource") else ""),
            link(h["bookingUrl"], "check rates →"),
            esc(h["lastChecked"]),
        ])
    rate_rows = [[
        esc(r["observed"]), esc(dict((h["id"], h["name"]) for h in H).get(r["hotel"], r["hotel"])),
        esc(r["room"]), esc(r["rateLabel"]), money(r["resortFee"]), link(r["source"]), esc(r["note"])]
        for r in R]
    body = f"""
<h1>Hotels — true cost per night</h1>
<p class="lede">{esc(META['formula'])}</p>
<div class="filters">
  <input type="search" id="hSearch" placeholder="Search hotels, fees, policies… (all tables below)">
  <label class="chk"><input type="checkbox" id="h30"> ≤30-min walk to its venue (on-site or verified route)</label>
</div>
{tbl(["Hotel / address", "Resort fee", "Tax", "Parking", "Cancellation deadline", "Rate note", "Checkout total", "Sources", "Booking", "Checked"], rows, tid="hTable")}
<h2>Dated rate log</h2>
<p class="note">Rates are kept as a dated log, never overwritten. Each entry records what was published, when it was observed and the exact
source. Like-for-like comparison needs the same stay window, occupancy and room class — fix trip dates first (<a href="questions.html#Q01">Q01</a>).</p>
{tbl(["Observed", "Hotel", "Room", "Rate", "Resort fee", "Source", "Note"], rate_rows, tid="rTable")}
<h2>Like-for-like checklist (per stay)</h2>
<ul class="summary">
  <li>Checkout total (all-in, taxes + fees) — <span class="unverified">blank until a dated quote exists</span></li>
  <li>Nightly average (checkout total ÷ nights) — <span class="unverified">blank</span></li>
  <li>Mandatory resort fee + tax — verified at $55 + tax/night for Venetian, Palazzo, Wynn, Bellagio (sources above)</li>
  <li>Parking — verified per hotel (blank for ARIA)</li>
  <li>Cancellation deadline — verified per hotel (Venetian prepaid = non-refundable; Wynn 48 h; Bellagio 72 h)</li>
  <li>Rate timestamp — each rate-log row carries its observation date</li>
</ul>
"""
    return shell("Hotels", "hotels.html", body)

def page_routes():
    rows = []
    for r in RO:
        within = "yes" if r.get("within30") else ("—" if r.get("within30") is None else "no")
        w30 = "true" if r.get("within30") else ("false" if r.get("within30") is False else
              ("true" if "Same resort property" in r["walkingNote"] else "unknown"))
        rows.append([
            esc(r["hotelName"]), esc(r["venueName"]),
            esc(r["hotelAddress"]), esc(r["venueAddress"]),
            esc(r["walkingNote"]),
            link(r["mapLink"], "verify on Google Maps (walking)"),
            f'<span data-within30="{w30}">≤30 min: <b>{within}</b></span>',
            esc(r["lastChecked"]),
        ])
    body = f"""
<h1>Walking routes (≤30-minute limit)</h1>
<p class="lede">Official addresses for every hotel–venue pair, with a walking-directions link for verification.
<b>No walking time is claimed unless a map service result is recorded</b> — all minutes are blank this pass
(<a href="flagged.html#FL08">FL08</a>). Same-property pairs (Venetian/Palazzo → Venetian room, etc.) are on-site.
The ≤30-minute filter applies to verified values once filled.</p>
<div class="filters">
  <input type="search" id="rSearch" placeholder="Search routes, addresses…">
  <label class="chk"><input type="checkbox" id="r30"> verified ≤30-minute routes only</label>
</div>
{tbl(["Hotel", "Venue", "Hotel address (official)", "Venue address (official)", "Walking time", "Map verification", "30-min limit", "Checked"], rows, tid="rTable")}
<p class="note">To verify: open the map link (walking mode), record minutes + date in <code>site/data/routes.json</code>
(<code>walkingMinutes</code>, <code>walkingVerified: true</code>) and re-run <code>scripts/build_site.py</code>.
Suggestion <a href="suggestions.html#S05">S05</a> tracks this.</p>
"""
    return shell("Walking routes", "routes.html", body)

def page_calculator():
    opts = []
    for t in TOUR:
        if t["bucket"] in ("single-path", "spend-more") and t.get("buyIn"):
            opts.append((t["id"], f'{t["date"]} · {t["name"]} · {money(t["buyIn"])} · {t["venueName"]}'))
    opt_html = "\n".join(f'<option value="{esc(i)}" data-buyin="{BY_ID[i]["buyIn"]}" data-name="{esc(n)}"></option>'
                         for i, n in sorted(opts, key=lambda x: x[1]))
    hotel_opts = "\n".join(
        f'<option value="{esc(h["id"])}" data-fee="{h.get("resortFee") if h.get("resortFee") is not None else ""}">{esc(h["name"])}</option>'
        for h in H)
    body = f"""
<h1>Estimated trip cost calculator</h1>
<p class="lede">{esc(META['formula'])}</p>
<div class="calc">
  <section>
    <h2>1 · Entries</h2>
    <label>Event <input list="eventList" id="cEvent" placeholder="Type to search events…"></label>
    <datalist id="eventList">{opt_html}</datalist>
    <label>Entries (times to play) <input type="number" id="cEntries" value="1" min="0" step="1"></label>
    <button id="cAdd" type="button">Add entry</button>
    <ul id="cEntryList"></ul>
    <p>Entry subtotal: <b id="cEntryTotal">$0</b></p>
  </section>
  <section>
    <h2>2 · Stay</h2>
    <label>Hotel <select id="cHotel">{hotel_opts}</select></label>
    <label>Nights <input type="number" id="cNights" value="3" min="1" step="1"></label>
    <label>Dated nightly rate (USD, before fees/tax) <input type="number" id="cRate" min="0" step="1" placeholder="blank until quoted"></label>
    <label>Resort fee / night <input type="number" id="cFee" min="0" step="1" value="55"></label>
    <label class="chk"><input type="checkbox" id="cTaxFee" checked> apply 13.38% tax to resort fee too
      <small>(Bellagio terms: lodging taxes apply to the basic room rate and any resort fee)</small></label>
    <label class="chk"><input type="checkbox" id="cParking"> add parking $20/day (Venetian registered-guest rate)</label>
    <p>True nightly (rate + fee + tax): <b id="cTrueNightly">—</b><br>
       Stay subtotal: <b id="cStayTotal">—</b></p>
  </section>
  <section>
    <h2>3 · Estimated trip cost</h2>
    <p class="bignum" id="cGrand">—</p>
    <p class="note" id="cBreakdown">Add entries and a dated rate to see the total. Totals with blank rate are partial and say so.</p>
  </section>
</div>
<h2>Notes</h2>
<ul class="summary">
  <li>Buy-ins use the printed total entry fee from each structure sheet (house fee + staff charge + prize share).</li>
  <li>True nightly uses the official fee ($55 + tax at Venetian, Palazzo, Wynn, Bellagio) and the official Clark County room tax of 13.38%.</li>
  <li>Blank rate = no dated quote captured yet (<a href="flagged.html#FL09">FL09</a>). Venetian poker-suite rates start at $119/$209 but are play-qualified and not date-mapped.</li>
</ul>
"""
    return shell("Trip calculator", "calculator.html", body)

def venue_page(vid, title, blurb):
    evs = [t for t in TOUR if t["venue"] == vid and t["bucket"] != "restart"]
    hs = [h for h in H if h["venue"] == vid]
    rs = [r for r in RO if r["venue"] == vid or (r["hotel"] == vid)]
    rows = []
    for t in sorted(evs, key=lambda x: (x["date"] if x["date"][:4].isdigit() else "zzz", x.get("timeMin") or 0)):
        rows.append([esc(t["date"]), esc(t["time"]), esc(t["name"]),
                     money(t["buyIn"]) or '<span class="unverified">blank</span>',
                     money(t["guarantee"]) or '<span class="unverified">blank</span>',
                     f'{t["ratio"]:.1f}×' if t.get("ratio") else "", entry_cell(t), badge(t), src_cell(t), esc(t["lastChecked"])])
    hrows = [[esc(h["name"]), money(h["resortFee"]) + " + tax" if h.get("resortFee") is not None else '<span class="unverified">blank</span>',
              esc(h["rateNote"]), link(h["bookingUrl"], "check rates →"), esc(h["lastChecked"])] for h in hs]
    rrows = [[esc(r["hotelName"]) + " → " + esc(r["venueName"]), esc(r["walkingNote"]),
              link(r["mapLink"], "verify"), esc(r["lastChecked"])] for r in rs]
    body = f"""
<h1>{esc(title)}</h1>
<p class="lede">{blurb}</p>
<h2>Events</h2>
{tbl(["Date", "Start", "Event", "Buy-in", "Guarantee", "Ratio", "Entry rules", "Status", "Sources", "Checked"], rows) if rows else '<p class="unverified">No verified events for this venue in the current window.</p>'}
<h2>Hotels on property / nearby</h2>
{tbl(["Hotel", "Resort fee", "Rate note", "Booking", "Checked"], hrows) if hrows else '<p class="unverified">—</p>'}
<h2>Walking routes</h2>
{tbl(["Pair", "Walking time", "Map", "Checked"], rrows) if rrows else '<p class="unverified">—</p>'}
"""
    return shell(title, f"venue-{vid}.html", body)

def page_venues():
    cards = [
        ("venue-venetian.html", "The Venetian Poker Room", "DeepStack Extravaganza IV (Nov 16 – Dec 23, 2026) — 64 events, all structure sheets read."),
        ("venue-wynn.html", "Wynn Poker Room (Encore)", "Daily tournaments (all with published re-entry terms) + WPT World Championship festival (Nov 27 – Dec 21, 2026)."),
        ("venue-bellagio.html", "Bellagio Poker Room", "Weekly Friday/Saturday/Sunday tournaments — re-entry and paid chip boosts confirmed; Saturday buy-in conflict flagged."),
        ("venue-aria.html", "ARIA Poker Room", "Undated daily/nightly cadence from the official guide; current operation requires a phone check."),
        ("venue-others.html", "Other rooms (Horseshoe, and unavailable pages)", "Horseshoe: 6 daily tournament times confirmed, details unpublished. Golden Nugget, Resorts World, Circa, MGM Grand pages not retrievable."),
    ]
    body = "<h1>Venues</h1><p class='lede'>One page per poker room: its events, its hotels, and its walking routes.</p><div class='cards'>"
    for href, name, note in cards:
        body += f'<a class="card linkcard" href="{href}"><b>{esc(name)}</b><small>{esc(note)}</small></a>'
    body += "</div>"
    return shell("Venues", "venues.html", body)

def page_workflow():
    body = f"""
<h1>Decision workflow</h1>
<p class="lede">The six steps to go from “I want to play a lot of poker” to a booked, verified trip. Work them in order —
each step blocks the next until its inputs exist. Open items are tracked in <a href="questions.html">Questions</a>.</p>
<ol class="workflow">
  <li><b>Fix trip dates and the nightly budget/quality floor.</b>
    <small>Everything downstream (rate quotes, event shortlist, day plan) is date-specific. Until dates exist, hotel totals stay blank
    (<a href="flagged.html#FL09">FL09</a>). Use the <a href="calculator.html">trip calculator</a> to set the budget.</small></li>
  <li><b>Confirm entry policy for candidate events.</b>
    <small>Every candidate's structure sheet has been read (fee split, guarantee, late-reg printed; no re-entry/rebuy/add-on wording).
    Because no sheet prints “single entry” (<a href="flagged.html#FL13">FL13</a>), get written maximum-entry / no-rebuy / no-add-on
    confirmation from tournament staff before treating an event as a strict freezeout. Remove anything that allows extra entries
    from the strict path — those are already quarantined in the spend-more bucket.</small></li>
  <li><b>Compare surviving events on the verified fields.</b>
    <small>Guaranteed pool (labelled: bounty guarantees include total bounties), total entry fee (house + staff + prize split),
    starting stack / level duration, payout percentage, and daily schedule fit. Rank only after total entry fee and guarantee are
    confirmed — the ratio column does this descriptively.</small></li>
  <li><b>Get itemized hotel totals for the same stay; check the walk.</b>
    <small>Checkout total, nightly average, resort fee + tax, parking, cancellation deadline, rate timestamp — compared like-for-like.
    Verify each hotel–venue route under 30 minutes via the <a href="routes.html">route links</a>.</small></li>
  <li><b>Build one event per day first.</b>
    <small>The <a href="schedule.html">day plan</a> assigns a primary per day plus a conditional evening fallback that is only reachable
    if the earlier event exits before the later late-reg closes. Overlap badges mark impossible sequences.</small></li>
  <li><b>Reconfirm before nonrefundable payment.</b>
    <small>Re-check official schedules, rates and policies the day you book — or let the <a href="monitoring.html">scheduled re-check</a>
    flag changes for you. Never book nonrefundable against a flagged row.</small></li>
</ol>
<h2>Standing rules</h2>
<ul class="summary">
  <li>No double buy-ins, re-entries or add-ons in the strict path — anything that lets money buy advantage is listed separately with its clause.</li>
  <li>Never infer or fill values: if an official source doesn't print it, the cell is blank and flagged.</li>
  <li>Guarantees are descriptive, not forecasts. Ratio = guaranteed pool ÷ total entry fee.</li>
  <li>Bounty, flight and satellite events are labelled and ranked separately.</li>
  <li>Every row carries its source link and its last-checked date.</li>
</ul>
"""
    return shell("Workflow", "workflow.html", body)

def page_monitoring():
    changes = {}
    ch_path = os.path.join(DATA, "changes.json")
    if os.path.exists(ch_path):
        with open(ch_path) as f:
            changes = {c["id"]: c for c in json.load(f).get("changes", [])}
    srows = []
    for s in S:
        c = changes.get(s["id"], {})
        if c.get("changedSinceVerification"):
            status = '<span class="badge warn">source changed — re-check rows using it</span>'
            checked = c.get("lastChecked") or s["checked"]
        elif c:
            status = '<span class="badge ok">' + esc(c.get("note", "no change")) + "</span>"
            checked = c.get("lastChecked") or s["checked"]
        else:
            status = '<span class="badge ok">no change since verification</span>'
            checked = s["checked"]
        srows.append([esc(s["name"]), link(s["url"]), "daily" if s.get("dailyFeed") else "on change-check",
                      esc(checked), status])
    body = f"""
<h1>Monitoring — scheduled re-check of official sources</h1>
<p class="lede">A GitHub Actions job (<code>.github/workflows/daily-check.yml</code>) runs every morning (12:05 UTC ≈ 4:05 AM Las Vegas),
re-fetches every official URL listed below, stores dated text snapshots, and compares them with the previous snapshot.
Rows whose source text changed are marked on this page and in <code>site/data/changes.json</code>; the job commits the updated
snapshots and badges to <code>main</code>, which redeploys this site.</p>
<h2>What the morning feed covers</h2>
<ul class="summary">
  <li><b>Daily schedule feed:</b> Venetian DSE schedule (web + PDF), Wynn poker page, Wynn daily poster PDF, WPT schedule PDF,
  Bellagio poker page, ARIA poker page, Horseshoe page — each snapshotted under <code>snapshots/&lt;date&gt;/</code>.</li>
  <li><b>Change detection:</b> SHA-256 of normalized text per URL; any change flips the badge below to “source changed — re-check”.</li>
  <li><b>Row marking:</b> every tournament/hotel row records <code>lastChecked</code>; when its source changes, the row is listed in
  <code>changes.json</code> and shown here as needing re-verification.</li>
</ul>
<h2>Source register</h2>
{tbl(["Source", "URL", "Re-check", "Last checked", "Change status"], srows)}
<p class="note">This page reflects the repository snapshot as published. The badges update after the daily job's next commit.</p>
"""
    return shell("Monitoring", "monitoring.html", body)

def page_sources():
    rows = [[esc(s["name"]), link(s["url"]), esc(s["kind"]), "daily feed" if s.get("dailyFeed") else "",
             esc(s["checked"])] for s in S]
    extra = [[esc("Venetian structure sheets 1–37 (read in full 2026-11-16)"),
              link("https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html", "index of sheets"),
              "official", "", "2026-11-16"]]
    body = f"""
<h1>Sources</h1>
<p class="lede">Every official page and PDF used in this research pass, with the date each was retrieved. Third-party calendars were
not used to substantiate any value.</p>
{tbl(["Source", "URL", "Type", "Feed", "Checked"], rows + extra)}
"""
    return shell("Sources", "sources.html", body)

def page_questions():
    rows = [[esc(q["id"]), esc(q["q"]), esc(q["why"]), esc(q["how"]),
             esc(q.get("answer") or "— (open: needs user decision or room call)"),
             f'<span class="badge {"ok" if q.get("answer") else "rev"}">{esc(q["status"] if not q.get("answer") else "answered")}</span>'] for q in Q]
    body = f"""
<h1>Questions / information needed — and answers</h1>
<p class="lede">Each question names what is missing, why it blocks a decision, how to discover the answer, and the answer when one
could be established from official sources. Remaining open items need a user decision or a short phone call.</p>
{tbl(["ID", "Question", "Why it blocks", "How to discover", "Answer (verified) or status", "Status"], rows)}
<h2>Information we DO have (verified)</h2>
<ul class="summary">
  <li>Full Venetian DSE IV schedule and all 37 structure sheets (buy-in splits, stacks, late-reg, guarantees, payout %).</li>
  <li>Entry clauses for all captured Wynn daily and WPT events; Bellagio weeklies; the spend-more reasons for each.</li>
  <li>Resort fees, tax rate, parking and cancellation policies for Venetian, Palazzo, Wynn and Bellagio (ARIA partial).</li>
  <li>Official addresses for every hotel–venue pair.</li>
</ul>
<h2>Information we DO NOT have (and cannot infer)</h2>
<ul class="summary">
  <li>Trip dates; dated room rates; checkout totals (<a href="flagged.html#FL09">FL09</a>).</li>
  <li>Written one-entry-total confirmations (<a href="flagged.html#FL13">FL13</a>).</li>
  <li>Verified walking times (<a href="flagged.html#FL08">FL08</a>); actual event finish times (<a href="flagged.html#FL14">FL14</a>).</li>
  <li>Bellagio Saturday buy-in reality (<a href="flagged.html#FL01">FL01</a>); ARIA/Bellagio current operation (<a href="flagged.html#FL05">FL05</a>,
  <a href="flagged.html#FL06">FL06</a>); WPT Super Gold / World Championship entry terms (<a href="flagged.html#FL07">FL07</a>).</li>
</ul>
"""
    return shell("Questions", "questions.html", body)

def page_suggestions():
    rows = [[esc(s["id"]), f'<b>{esc(s["title"])}</b><br><small>{esc(s["detail"])}</small>',
             esc(s["impact"]), esc(s["effort"]), f'<span class="badge {"warn" if s["status"]=="needs decision" else "rev"}">{esc(s["status"])}</span>']
            for s in SG]
    body = f"""
<h1>Suggestions — review before implementing</h1>
<p class="lede">Improvements ranked by decision-making impact. Nothing here is implemented; pick the path you want and it will be
built in a later pass. S07 needs your decision first (which archived site to keep).</p>
{tbl(["ID", "Suggestion", "Impact", "Effort", "Status"], rows)}
<h2>Decision record</h2>
<p class="note">When you choose, record it here: date, chosen suggestion, and any constraints. Until then all rows stay “proposed”.</p>
"""
    return shell("Suggestions", "suggestions.html", body)

def page_flagged():
    rows = [[f'<span id="{esc(f["id"])}">{esc(f["id"])}</span>', esc(f["title"]),
             f'<span class="badge {"warn" if f["level"]=="high" else "rev"}">{esc(f["level"])}</span>',
             esc(f["finding"]), esc(f["next"]), link(f["source"])] for f in F]
    body = f"""
<h1>Flagged for review</h1>
<p class="lede">Irregularities, conflicts and unverified values found during line-by-line verification. None of these block the site;
they are published here so they can be reviewed after the site is live. Every item links the official source that produced it.</p>
{tbl(["ID", "Item", "Level", "Finding", "What to do", "Source"], rows)}
"""
    return shell("Flagged for review", "flagged.html", body)

def main():
    pages = {
        "index.html": page_index(),
        "tournaments.html": page_tournaments(),
        "schedule.html": page_schedule(),
        "hotels.html": page_hotels(),
        "routes.html": page_routes(),
        "calculator.html": page_calculator(),
        "venues.html": page_venues(),
        "venue-venetian.html": venue_page("venetian", "The Venetian Poker Room",
            "3355 S Las Vegas Blvd · DeepStack Extravaganza IV, Nov 16 – Dec 23, 2026. All 37 official structure sheets were read in full on 2026-11-16; every event below carries its fee split, stack, late-reg and guarantee from its sheet."),
        "venue-wynn.html": venue_page("wynn", "Wynn Poker Room (Encore)",
            "3131 S Las Vegas Blvd · Daily tournaments with published re-entry terms, plus the WPT World Championship festival, Nov 27 – Dec 21, 2026."),
        "venue-bellagio.html": venue_page("bellagio", "Bellagio Poker Room",
            "3600 S Las Vegas Blvd · Weekly Friday/Saturday/Sunday tournaments. Re-entry through level 8 and paid staff-gratuity chip boosts confirmed on the official sheets; the Saturday buy-in conflict is flagged."),
        "venue-aria.html": venue_page("aria", "ARIA Poker Room",
            "3730 S Las Vegas Blvd · 24 tables. The official guide's 1 PM / 7 PM cadence is undated and the current page says to call the room to confirm daily tournaments."),
        "venue-others.html": venue_page("horseshoe", "Other rooms",
            "Horseshoe Las Vegas (3645 S Las Vegas Blvd) — Hall of Fame Poker Room, 20 tables, 6 daily tournament times confirmed on the official page but times/buy-ins unpublished. Golden Nugget, Resorts World, Circa and MGM Grand official poker pages were not retrievable this pass (FL11)."),
        "workflow.html": page_workflow(),
        "monitoring.html": page_monitoring(),
        "sources.html": page_sources(),
        "questions.html": page_questions(),
        "suggestions.html": page_suggestions(),
        "flagged.html": page_flagged(),
    }
    for name, content in pages.items():
        with open(os.path.join(OUT, name), "w") as f:
            f.write(content)
    print("wrote", len(pages), "pages")

if __name__ == "__main__":
    main()
