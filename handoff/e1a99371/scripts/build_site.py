#!/usr/bin/env python3
"""Build the Vegas Poker Trip Planner static dashboard into site/.

Reads the verified data in scripts/poker_data.py and writes:
  site/index.html            landing page + executive summary
  site/events.html           all tournament starts, with filters and search
  site/schedule.html         day-by-day plan with the overlap check
  site/hotels.html           hotels, true cost per night, 30-minute walk filter
  site/venues/venetian.html  one page per venue
  site/trip-cost.html        estimated trip cost calculator
  site/questions.html        open questions
  site/suggestions.html      improvement suggestions for a decision
  site/flagged.html          flagged for review
  site/sources.html          official source register
  site/changes.html          change monitoring log
  site/data/*.json           the same data as JSON, for scripting and the monitor

Every table row is rendered at build time from verified fields and links its
own official source. Nothing is inferred: unknown values render as a blank
cell plus an "unverified" marker and an entry on the Flagged page.
"""

from __future__ import annotations

import html
import json
import pathlib
import shutil
import sys
from datetime import date

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import poker_data as D  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
VENUES = SITE / "venues"

AS_OF = "2026-11-16"
TAX_RATE = D.TAX_RATE


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def e(value) -> str:
    """Escape for HTML output."""
    return html.escape("" if value is None else str(value), quote=True)


def money(value) -> str:
    if value in (None, ""):
        return ""
    return f"${value:,.0f}"


def unverified(note: str = "") -> str:
    title = note or "Not published on any official source checked"
    return f'<span class="uv" title="{e(title)}">unverified</span>'


def ext_link(url: str, label: str, cls: str = "") -> str:
    if not url:
        return ""
    c = f' class="{cls}"' if cls else ""
    return (
        f'<a{c} href="{e(url)}" target="_blank" rel="noopener noreferrer">{e(label)}</a>'
    )


NAV = [
    ("index.html", "Overview"),
    ("events.html", "Events"),
    ("schedule.html", "Day plan"),
    ("hotels.html", "Hotels"),
    ("venues/venetian.html", "Venue: Venetian"),
    ("trip-cost.html", "Trip cost"),
    ("questions.html", "Questions"),
    ("suggestions.html", "Suggestions"),    ("flagged.html", "Flagged"),
    ("sources.html", "Sources"),
    ("changes.html", "Changes"),
]


def page(title: str, slug: str, body: str, subtitle: str = "") -> str:
    up = "../" if "/" in slug else ""
    nav = "".join(
        f'<a href="{up}{link}" class="nav-link{" is-active" if link == slug else ""}">{label}</a>'
        for link, label in NAV
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)} | Vegas Poker Trip Planner</title>
<meta name="description" content="Source-linked dashboard for Las Vegas Strip poker tournaments, hotels and trip cost. Every row links an official source.">
<link rel="stylesheet" href="{up}assets/site.css">
</head>
<body>
<header class="topbar">
  <div class="wrap topbar-inner">
    <a class="brand" href="{up}index.html">
      <span class="brand-mark">VP</span>
      <span class="brand-text">Vegas Poker Trip Planner</span>
    </a>
    <form class="searchbox" role="search" onsubmit="return false;">
      <input id="siteSearch" type="search" placeholder="Search all tables&hellip;" autocomplete="off"
             aria-label="Search across every table on this page">
      <span id="searchCount" class="search-count" aria-live="polite"></span>
    </form>
  </div>
  <nav class="nav wrap" aria-label="Sections">{nav}</nav>
</header>
<main class="wrap">
  <div class="page-head">
    <h1>{e(title)}</h1>
    {f'<p class="subtitle">{e(subtitle)}</p>' if subtitle else ''}
  </div>
{body}
</main>
<footer class="footer wrap">
  <p>Snapshot {AS_OF}. Every figure on this site is read from an official venue or hotel page, or from an
  official PDF linked from one. Values an official source does not publish are left blank and marked
  <span class="uv">unverified</span>, with an entry on the <a href="{up}flagged.html">Flagged for review</a> page.
  Guarantees are contractual minimum prize pools, not forecasts of any player's return.</p>
</footer>
<script src="{up}assets/app.js"></script>
</body>
</html>
"""


def write(path: pathlib.Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


# ---------------------------------------------------------------------------
# derived event data
# ---------------------------------------------------------------------------

def to_minutes(t: str) -> int | None:
    """'3:40 PM' -> 940. Returns None when the source prints no time."""
    if not t:
        return None
    t = t.strip().replace("~", "").strip()
    for fmt_hint in ("AM", "PM"):
        if fmt_hint in t.upper():
            body = t.upper().replace(fmt_hint, "").strip()
            h, _, m = body.partition(":")
            try:
                hour = int(h)
                minute = int(m or 0)
            except ValueError:
                return None
            if fmt_hint == "PM" and hour != 12:
                hour += 12
            if fmt_hint == "AM" and hour == 12:
                hour = 0
            return hour * 60 + minute
    return None


EVENTS = D.build_events()

# Attach derived fields used by the schedule page.
for ev in EVENTS:
    ev["startMin"] = to_minutes(ev["start"])
    ev["regCloseMin"] = to_minutes(ev["regCloses"])
    ev["windowEndMin"] = ev["regCloseMin"] if ev["regCloseMin"] is not None else ev["startMin"]
    ev["ratio"] = round(ev["guarantee"] / ev["buyIn"], 1) if ev["guarantee"] and ev["buyIn"] else None
    ev["totalEntry"] = ev["buyIn"]

BUCKET_LABEL = {
    "single-entry-candidate": "Single-day candidate",
    "multi-entry": "Multi-entry (separate section)",
    "satellite": "Satellite (excluded)",
    "continuation": "Continuation day (excluded)",
}

CANDIDATES = [x for x in EVENTS if x["bucket"] == "single-entry-candidate"]
MULTI = [x for x in EVENTS if x["bucket"] == "multi-entry"]
SATS = [x for x in EVENTS if x["bucket"] == "satellite"]
CONT = [x for x in EVENTS if x["bucket"] == "continuation"]

DATES = sorted({x["date"] for x in EVENTS})


def day_events(iso: str):
    return [x for x in EVENTS if x["date"] == iso]


def overlap_pairs(iso: str):
    """Flag pairs whose registration windows overlap on the same day."""
    rows = [x for x in day_events(iso)
            if x["bucket"] in ("single-entry-candidate", "multi-entry")
            and x["startMin"] is not None and x["windowEndMin"] is not None]
    out = []
    for i in range(len(rows)):
        for j in range(i + 1, len(rows)):
            a, b = rows[i], rows[j]
            if a["startMin"] < b["windowEndMin"] and b["startMin"] < a["windowEndMin"]:
                out.append((a, b))
    return out


def day_plan(iso: str):
    """Primary event plus a conditional fallback for one day."""
    cands = [x for x in day_events(iso) if x["bucket"] == "single-entry-candidate"]
    if not cands:
        return None, []
    ordered = sorted(
        cands,
        key=lambda x: (-(x["guarantee"] or 0), -(x["startMin"] or 0)),
    )
    primary = ordered[0]
    fallbacks = [x for x in ordered[1:]]
    return primary, fallbacks


# ---------------------------------------------------------------------------
# page: index (executive summary)
# ---------------------------------------------------------------------------

def build_index() -> str:
    total_guaranteed = sum(x["guarantee"] or 0 for x in CANDIDATES)
    cheapest = min(CANDIDATES, key=lambda x: x["buyIn"])
    best_ratio = max((x for x in CANDIDATES if x["ratio"]), key=lambda x: x["ratio"], default=None)
    best_guarantee = max(CANDIDATES, key=lambda x: x["guarantee"] or 0)
    walk_ok = [h for h in D.HOTELS if h["walkMin"] <= 30]
    earliest = min(
        (x for x in EVENTS if x["startMin"] is not None), key=lambda x: x["startMin"]
    )
    earliest_cand = min(
        (x for x in CANDIDATES if x["startMin"] is not None), key=lambda x: x["startMin"]
    )

    kpis = [
        ("Events in scope", "64 event numbers / 94 scheduled starts",
         "DeepStack Extravaganza IV, Nov 16 - Dec 23, 2026", "events.html"),
        ("Single-day candidates", str(len(CANDIDATES)),
         "One-day events with no multi-flight structure", "events.html"),
        ("Excluded: multi-entry", str(len(MULTI)),
         "Multi-flight starts - a player may enter more than one flight", "events.html"),
        ("Excluded: satellites & Day 2+", str(len(SATS) + len(CONT)),
         "Satellites award seats, not cash; Day 2/3 rows are continuations", "events.html"),
        ("Cheapest candidate entry", money(cheapest["buyIn"]), cheapest["name"], "events.html"),
        ("Largest candidate guarantee", money(best_guarantee["guarantee"] or 0),
         best_guarantee["name"], "events.html"),
        ("Best guarantee / entry ratio",
         f"{best_ratio['ratio']:.1f}x" if best_ratio else "n/a",
         (best_ratio["name"] + " - bounty event, so its guarantee includes bounties")
         if best_ratio else "", "events.html"),
        ("Hotels within a 30-min walk", str(len(walk_ok)),
         f"of {len(D.HOTELS)} checked; ARIA fails at 31 min", "hotels.html"),
        ("Earliest verified start", f"{earliest_cand['start']} ({earliest_cand['dateLabel']})",
         f"Earliest of any start is {earliest['start']} (a satellite). No event starts at 8:00 AM",
         "schedule.html"),
    ]

    kpi_html = "".join(
        f"""<a class="card kpi" href="{link}">
      <div class="kpi-value">{e(value)}</div>
      <div class="kpi-label">{e(label)}</div>
      <div class="kpi-note">{e(note)}</div>
    </a>"""
        for value, label, note, link in kpis
    )

    body = f"""
<section class="hero">
  <h2>Executive summary</h2>
  <p class="lede">The Venetian's <strong>DeepStack Extravaganza IV</strong> runs
  <strong>November 16 - December 23, 2026</strong> and is the only Strip series for which every
  event start, structure sheet and entry fee could be verified from official sources on {AS_OF}.
  All {len(EVENTS)} scheduled starts across 64 event numbers are on the Events page, each linking the
  official schedule and its own structure sheet.</p>
</section>

<section class="kpi-grid">{kpi_html}</section>

<section class="panel">
  <h2>What is verified</h2>
  <ul class="ticks">
    <li>Every start time, date and event number, read from the official structures/results table
        ({ext_link('https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html', 'source S02')}).</li>
    <li>Every late-registration close time, starting stack and level length, read from the official
        schedule PDF ({ext_link('https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/dse-nov-2026-schedule.pdf', 'source S03')}).</li>
    <li>Every buy-in, house fee (rake + staff), prize-pool share, guarantee, payout percentage and
        age restriction, read from all 37 official structure sheets
        ({ext_link('https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_1.pdf', 'source S04')}).</li>
    <li>Venetian resort fee of <strong>$55 plus tax per night</strong>
        ({ext_link('https://www.venetianlasvegas.com/resort/resort-fee.html', 'S06')}) and the
        <strong>13.38% Clark County Room Tax</strong>
        ({ext_link('https://www.venetianlasvegas.com/legal/hotel-terms-and-conditions.html', 'S08')}).</li>
    <li>Walking times and distances from 17 Strip hotels to the Venetian poker room, each captured
        from Google Maps with the route link (sources S10-S26).</li>
  </ul>
</section>

<section class="panel">
  <h2>What is not verified, and why it matters</h2>
  <ol class="numbered">
    <li><strong>No event can be called "single entry".</strong> All 37 structure sheets were read in
        full. Not one prints the words single entry, freezeout, no re-entry or no add-on. The
        single-day events are labelled <em>"one-day event; sheet prints no re-entry or add-on"</em>, which
        is not the same thing. See {flag_link('F01')}.</li>
    <li><strong>Multi-flight events are excluded on an inference.</strong> Their sheets say
        <em>"Any player who bags chips for Day 2 may not play a subsequent flight"</em>, which only makes
        sense if more than one entry is allowed. See {flag_link('F02')}.</li>
    <li><strong>No date-specific hotel rate exists on any official page.</strong> Only the Venetian
        resort fee, the tax rate and the conditional poker rate ("from $119 / $209") are published.
        The true cost per night is therefore a calculator, not a table. See {flag_link('F-H1')}.</li>
    <li><strong>No finish time is published for any event</strong>, so the day plan compares
        registration windows rather than verified finish times. See {flag_link('F06')}.</li>
    <li><strong>No event starts at 8:00 AM.</strong> The earliest start anywhere in the series is
        {e(earliest['start'])} on {e(earliest['dateLabel'])} (event #{earliest['eventNo']}, a satellite);
        the earliest single-day candidate is {e(earliest_cand['start'])}. See {flag_link('F07')}.</li>
  </ol>
  <p class="callout">Read the <a href="questions.html">Questions</a> page before booking anything.
  It lists exactly what must be confirmed by phone or email, and the
  <a href="flagged.html">Flagged for review</a> page carries every irregularity with its source link.</p>
</section>

<section class="panel">
  <h2>The three best single-day candidates on guarantee per dollar</h2>
  {ratio_table(sorted([x for x in CANDIDATES if x['ratio']], key=lambda x: -x['ratio'])[:8])}
  <p class="note">Guaranteed pool divided by entry fee is a <strong>descriptive ratio</strong> for
  comparing events. It is not a forecast of any result. Bounty events are labelled because their
  guarantee is printed as "prize pool + total bounties", which is not like-for-like with a
  freezeout guarantee. Ranking is only shown after the entry fee and the guarantee have both been
  confirmed on the official sheet.</p>
</section>
"""
    return page(
        "Overview",
        "index.html",
        body,
        "Executive summary for the DeepStack Extravaganza IV trip, with every figure linked to its official source.",
    )


def flag_link(fid: str, up: str = "") -> str:
    return f'<a href="{up}flagged.html#{fid}">{fid}</a>'


def ratio_table(rows) -> str:
    head = ("Date", "Event", "Start", "Reg closes", "Entry", "To prize pool",
            "Guarantee", "Ratio", "Bounty", "Source")
    body = "".join(
        f"""<tr>
      <td data-label="Date">{e(r['dateLabel'])}</td>
      <td data-label="Event"><span class="evno">#{r['eventNo']}{e(r['flight'] and ' ' + r['flight'])}</span> {e(r['name'])}</td>
      <td data-label="Start">{e(r['start'])}</td>
      <td data-label="Reg closes">{e(r['regCloses']) if r['regCloses'] else unverified()}</td>
      <td data-label="Entry" class="num">{money(r['buyIn'])}</td>
      <td data-label="To prize pool" class="num">{money(r['prizePoolShare'])}</td>
      <td data-label="Guarantee" class="num">{e(r['guaranteeLabel']) if r['guaranteeLabel'] else unverified('No guarantee printed on the official sheet')}</td>
      <td data-label="Ratio" class="num strong">{f"{r['ratio']:.1f}x" if r['ratio'] else unverified()}</td>
      <td data-label="Bounty">{e(r['bounty'])}</td>
      <td data-label="Source">{ext_link(r['structureUrl'], r['structureLabel'])}</td>
    </tr>"""
        for r in rows
    )
    return f"""<div class="table-scroll"><table class="data" data-filterable>
    <thead><tr>{''.join(f'<th>{e(h)}</th>' for h in head)}</tr></thead>
    <tbody>{body}</tbody></table></div>"""


# ---------------------------------------------------------------------------
# page: events
# ---------------------------------------------------------------------------

def event_rows(rows):
    out = []
    for r in rows:
        if r["reEntry"] == "multi-flight":
            re_cell = '<span class="tag tag-bad">Multiple flights</span>'
        elif r["reEntry"] == "implied":
            re_cell = '<span class="tag tag-warn">Subsequent buy-ins referenced</span>'
        elif r["bucket"] == "satellite":
            re_cell = '<span class="tag">n/a (satellite)</span>'
        elif r["bucket"] == "continuation":
            re_cell = '<span class="tag">n/a (continuation)</span>'
        else:
            re_cell = '<span class="tag tag-ok">Not printed</span>'
        add_cell = (
            '<span class="tag tag-ok">Not printed</span>'
            if not r["addOn"]
            else e(r["addOn"])
        )
        out.append(
            f"""<tr data-bucket="{e(r['bucket'])}" data-date="{e(r['date'])}"
        data-guarantee="{r['guarantee'] or 0}" data-buyin="{r['buyIn']}"
        data-bounty="{e(r['bounty'])}" data-ratio="{r['ratio'] or 0}"
        data-eligibility="{e(r['eligibility'])}"
        data-search="{e((' '.join([r['name'], r['dateLabel'], r['entryType'], r['eligibility'], str(r['eventNo']), r['flight']])).lower())}">
      <td data-label="Date">{e(r['dateLabel'])}</td>
      <td data-label="Event #" class="num">#{r['eventNo']}{e(' ' + r['flight'] if r['flight'] else '')}</td>
      <td data-label="Event">{e(r['name'])}</td>
      <td data-label="Type"><span class="pill pill-{e(r['bucket'])}">{e(r['entryType'])}</span></td>
      <td data-label="Eligibility">{e(r['eligibility'])}</td>
      <td data-label="Start">{e(r['start'])}</td>
      <td data-label="Reg closes">{e(r['regCloses']) if r['regCloses'] else unverified('Not printed for continuation days')}</td>
      <td data-label="Entry" class="num">{money(r['buyIn'])}</td>
      <td data-label="House fee" class="num">{money(r['houseFee'])}</td>
      <td data-label="To prize pool" class="num">{money(r['prizePoolShare'])}</td>
      <td data-label="Guarantee" class="num">{e(r['guaranteeLabel']) if r['guaranteeLabel'] else unverified('No guarantee printed on the official sheet')}</td>
      <td data-label="Ratio" class="num strong">{f"{r['ratio']:.1f}x" if r['ratio'] else '—'}</td>
      <td data-label="Stack" class="num">{r['startingChips']:,}</td>
      <td data-label="Levels" class="num">{e(r['levelMinutes'])} min</td>
      <td data-label="Late reg">{e(r['lateReg'])}</td>
      <td data-label="Bounty">{e(r['bounty'])}</td>
      <td data-label="Re-entry rule">{re_cell}</td>
      <td data-label="Add-on rule">{add_cell}</td>
      <td data-label="Paid advantage"><span class="pa">{e(r['paidAdvantage'])}</span></td>
      <td data-label="Single-entry status"><span class="tag tag-warn">{e(r['singleEntryStatus'])}</span></td>
      <td data-label="Rule excerpt" class="excerpt">{e(r['ruleExcerpt'])}</td>
      <td data-label="Last checked">{e(r['lastChecked'])}</td>
      <td data-label="Sources" class="srcs">{ext_link(r['structureUrl'], 'Structure sheet')}<br>{ext_link(r['scheduleUrl'], 'Official schedule')}</td>
    </tr>"""
        )
    return "".join(out)


def events_table(rows, table_id=""):
    head = ("Date", "Event #", "Event", "Type", "Eligibility", "Start", "Reg closes", "Entry",
            "House fee", "To prize pool", "Guarantee", "Ratio", "Stack", "Levels",
            "Late reg", "Bounty", "Re-entry rule", "Add-on rule", "Paid advantage",
            "Single-entry status", "Rule excerpt (verbatim)", "Last checked", "Sources")
    return f"""<div class="table-scroll"><table class="data" data-filterable id="{table_id}">
  <thead><tr>{''.join(f'<th>{e(h)}</th>' for h in head)}</tr></thead>
  <tbody>{event_rows(rows)}</tbody></table></div>"""


def build_events_page() -> str:
    dates = "".join(
        f'<option value="{d}">{e(date.fromisoformat(d).strftime("%a %b %d, %Y"))}</option>'
        for d in DATES
    )
    body = f"""
<section class="panel">
  <h2>Filters</h2>
  <div class="filters" id="eventFilters">
    <label class="field">
      <span>Date</span>
      <select id="fDate"><option value="">Any date</option>{dates}</select>
    </label>
    <label class="field">
      <span>Min guarantee</span>
      <select id="fGuarantee">
        <option value="0">Any</option>
        <option value="10000">$10k+</option>
        <option value="25000">$25k+</option>
        <option value="40000">$40k+</option>
        <option value="75000">$75k+</option>
        <option value="150000">$150k+</option>
        <option value="300000">$300k+</option>
        <option value="500000">$500k+</option>
      </select>
    </label>
    <label class="field">
      <span>Max entry</span>
      <select id="fBuyin">
        <option value="100000">Any</option>
        <option value="200">$200 or less</option>
        <option value="300">$300 or less</option>
        <option value="400">$400 or less</option>
        <option value="600">$600 or less</option>
        <option value="800">$800 or less</option>
        <option value="1100">$1,100 or less</option>
      </select>
    </label>
    <label class="field checkbox">
      <input type="checkbox" id="fSingle" checked>
      <span>Single-day candidates only (hides multi-entry, satellites and Day 2+ rows)</span>
    </label>
    <label class="field checkbox">
      <input type="checkbox" id="fBounty">
      <span>Hide bounty events</span>
    </label>
    <label class="field">
      <span>Eligibility</span>
      <select id="fElig">
        <option value="all">Show everything</option>
        <option value="open">Open to me (hide 50+ and women-only events)</option>
        <option value="senior">Seniors (50+) events only</option>
        <option value="ladies">Women-only and LIPS events only</option>
      </select>
    </label>
    <label class="field checkbox">
      <input type="checkbox" id="fFreeze" disabled>
      <span title="No structure sheet prints a single-entry rule, so this filter cannot be satisfied yet. See flag F01.">
        Single-entry / freezeout confirmed only <em>(unavailable - see F01)</em></span>
    </label>
    <label class="field">
      <span>Sort by</span>
      <select id="fSort">
        <option value="date">Date, then start time</option>
        <option value="ratio">Guarantee / entry ratio</option>
        <option value="guarantee">Guarantee (high to low)</option>
        <option value="buyin">Entry fee (low to high)</option>
        <option value="start">Start time (earliest)</option>
      </select>
    </label>
  </div>
  <p class="note" id="eventCount"></p>
</section>

<section class="panel">
  <h2>Single-day candidates ({len(CANDIDATES)} starts)</h2>
  <p class="note">One-day events with no multi-flight structure. Every sheet prints the buy-in, fee,
  guarantee, stack, levels and late-registration window, and <strong>none prints a re-entry or
  add-on rule</strong>. That absence is not a confirmation of single entry - see
  {flag_link('F01')}.</p>
  {events_table(CANDIDATES, 'tblCandidates')}
</section>

<section class="panel">
  <h2>Multi-entry / multi-flight starts ({len(MULTI)}) - separate section</h2>
  <p class="note">These sheets contain "Any player who bags chips for Day 2 may not play a
  subsequent flight", which implies a player may enter more than one flight. They are excluded from
  the single-entry list on that basis, and because a player who busts a flight can buy into another
  one - which is exactly the "pay more for another chance" structure you want to avoid.</p>
  {events_table(MULTI, 'tblMulti')}
</section>

<section class="panel">
  <h2>Satellites ({len(SATS)}) - excluded</h2>
  <p class="note">Satellites award a seat into another event rather than a cash prize pool. They are
  listed for completeness and excluded from every ranking.</p>
  {events_table(SATS, 'tblSats')}
</section>

<section class="panel">
  <h2>Day 2 / Day 3 / final-table rows ({len(CONT)}) - excluded</h2>
  <p class="note">Continuation rows for multi-day events. They are not separate events and carry no
  buy-in of their own.</p>
  {events_table(CONT, 'tblCont')}
</section>
"""
    return page(
        "Events",
        "events.html",
        body,
        "Every scheduled start of DeepStack Extravaganza IV, filtered by date, entry fee, guarantee and entry structure.",
    )


# ---------------------------------------------------------------------------
# page: schedule
# ---------------------------------------------------------------------------

def build_schedule() -> str:
    blocks = []
    for iso in DATES:
        rows = day_events(iso)
        cands = [x for x in rows if x["bucket"] == "single-entry-candidate"]
        primary, fallbacks = day_plan(iso)
        pairs = overlap_pairs(iso)
        d = date.fromisoformat(iso)

        plan_bits = []
        if primary:
            plan_bits.append(
                f"""<p class="plan-primary"><span class="tag tag-ok">Primary</span>
        <strong>#{primary['eventNo']}{(' ' + primary['flight']) if primary['flight'] else ''} {e(primary['name'])}</strong><br>
        {e(primary['start'])} start, registration closes {e(primary['regCloses'] or 'not printed')},
        {money(primary['buyIn'])} entry, {e(primary['guaranteeLabel']) if primary['guaranteeLabel'] else 'no printed guarantee'},
        {primary['startingChips']:,} chips, {e(primary['levelMinutes'])} min levels.
        {ext_link(primary['structureUrl'], 'Structure sheet')}</p>"""
            )
        if primary and (primary["startMin"] or 0) >= 14 * 60:
            morning = [x for x in rows if x["bucket"] == "multi-entry"
                       and (x["startMin"] or 9999) < 12 * 60]
            extra = (
                " The morning slot on this date is multi-flight ("
                + ", ".join(f"#{x['eventNo']}{(' ' + x['flight']) if x['flight'] else ''}"
                            for x in morning)
                + "), which allows more than one entry."
            ) if morning else ""
            plan_bits.append(
                '<p class="plan-fallback"><span class="tag tag-warn">Evening only</span> '
                f"The only single-day event on this date starts at {e(primary['start'])}, so there is "
                "no single-entry option before then." + e(extra) + "</p>"
            )

        for fb in fallbacks:
            clashes = (
                primary is not None
                and (fb["startMin"] or 0) < (primary["windowEndMin"] or 0)
                and (primary["startMin"] or 0) < (fb["windowEndMin"] or 0)
            )
            if clashes:
                plan_bits.append(
                    f"""<p class="plan-clash"><span class="tag tag-bad">Cannot be played with the primary</span>
        #{fb['eventNo']}{(' ' + fb['flight']) if fb['flight'] else ''} {e(fb['name'])} at {e(fb['start'])}
        ({money(fb['buyIn'])} entry, {e(fb['guaranteeLabel']) if fb['guaranteeLabel'] else 'no printed guarantee'}).
        Its registration window ({e(fb['start'])} - {e(fb['regCloses'] or 'not printed')}) overlaps the primary
        event's, so pick one or the other. {ext_link(fb['structureUrl'], 'Structure sheet')}</p>"""
                )
            else:
                plan_bits.append(
                    f"""<p class="plan-fallback"><span class="tag tag-warn">Conditional fallback</span>
        #{fb['eventNo']}{(' ' + fb['flight']) if fb['flight'] else ''} {e(fb['name'])} at {e(fb['start'])}
        ({money(fb['buyIn'])} entry, {e(fb['guaranteeLabel']) if fb['guaranteeLabel'] else 'no printed guarantee'}).
        Enter this only after you are out of the primary event - the official sources do not publish
        finish times, so this cannot be scheduled. {ext_link(fb['structureUrl'], 'Structure sheet')}</p>"""
                )
        if not cands:
            multi = [x for x in rows if x["bucket"] == "multi-entry"]
            conts = [x for x in rows if x["bucket"] == "continuation"]
            bits = ['<p class="plan-fallback"><span class="tag">No single-day event</span>']
            if multi:
                names = ", ".join(
                    f"#{x['eventNo']}{(' ' + x['flight']) if x['flight'] else ''} at {x['start']}"
                    for x in multi
                )
                bits.append(
                    f"Only multi-flight starts run on this date ({names}). Those allow more than one "
                    "entry, so this day has no single-entry option."
                )
            else:
                bits.append("Nothing single-day is scheduled on this date.")
            if conts:
                bits.append(
                    " " + ", ".join(f"#{x['eventNo']}" for x in conts) +
                    " is a continuation day for an event that started earlier."
                )
            bits.append("</p>")
            plan_bits.append("".join(bits))

        if pairs:
            warn = '<ul class="overlap">' + "".join(  # noqa: E501
                f"""<li><strong>Overlap:</strong> #{a['eventNo']}{(' ' + a['flight']) if a['flight'] else ''}
            ({e(a['start'])} - {e(a['regCloses'] or 'not printed')}) and
            #{b['eventNo']}{(' ' + b['flight']) if b['flight'] else ''}
            ({e(b['start'])} - {e(b['regCloses'] or 'not printed')}).
            These registration windows overlap, so you cannot play both from the start.</li>"""
                for a, b in pairs
            ) + "</ul>"
        elif len(cands) >= 2:
            warn = ('<p class="plan-ok">No overlapping registration windows between the '
                    'single-day events on this date, so a morning event followed by an evening '
                    'event is <em>possible</em> - but not <em>guaranteed</em>, because no finish '
                    'time is published (see ' + flag_link("F06") + ').</p>')
        elif len(cands) == 1:
            warn = ('<p class="plan-ok">Only one single-day event runs on this date, so there is '
                    'nothing to sequence.</p>')
        else:
            warn = ('<p class="plan-ok">No single-day events on this date, so there is no '
                    'schedule to check for overlaps.</p>')

        rows_html = "".join(
            f"""<tr data-bucket="{e(x['bucket'])}">
      <td data-label="Start">{e(x['start'])}</td>
      <td data-label="Event #" class="num">#{x['eventNo']}{e(' ' + x['flight'] if x['flight'] else '')}</td>
      <td data-label="Event">{e(x['name'])}</td>
      <td data-label="Type"><span class="pill pill-{e(x['bucket'])}">{e(x['entryType'])}</span></td>
      <td data-label="Reg closes">{e(x['regCloses']) if x['regCloses'] else unverified()}</td>
      <td data-label="Entry" class="num">{money(x['buyIn'])}</td>
      <td data-label="Guarantee" class="num">{e(x['guaranteeLabel']) if x['guaranteeLabel'] else unverified()}</td>
      <td data-label="Source">{ext_link(x['structureUrl'], 'Sheet')}</td>
    </tr>"""
            for x in sorted(rows, key=lambda x: x["startMin"] if x["startMin"] is not None else 9999)
        )

        blocks.append(
            f"""<details class="day" {'open' if primary else ''}>
    <summary><span class="day-name">{e(d.strftime('%A, %B %d, %Y'))}</span>
      <span class="day-meta">{len(rows)} start(s) &middot; {len(cands)} single-day candidate(s)</span></summary>
    <div class="day-body">
      {''.join(plan_bits)}
      {warn}
      <div class="table-scroll"><table class="data" data-filterable>
        <thead><tr><th>Start</th><th>Event #</th><th>Event</th><th>Type</th>
        <th>Reg closes</th><th>Entry</th><th>Guarantee</th><th>Source</th></tr></thead>
        <tbody>{rows_html}</tbody>
      </table></div>
    </div>
  </details>"""
        )

    body = f"""
<section class="panel">
  <h2>How this plan is built</h2>
  <ol class="numbered">
    <li><strong>One event per day first.</strong> Each day gets a primary event - the single-day
        candidate with the largest printed guarantee. Everything else that day is a fallback.</li>
    <li><strong>Evening events are conditional, not scheduled.</strong> Most days have a morning or
        midday event and an evening event. The registration windows usually do not overlap, but no
        official source publishes a finish time, so an evening entry is only realistic if you are
        actually out of the earlier event.</li>
    <li><strong>Overlap check.</strong> For every date, every pair of starts is tested for
        overlapping registration windows. Where they overlap the site says so explicitly.</li>
    <li><strong>The earliest start is {e(min((x['start'] for x in EVENTS if x['bucket']=='single-entry-candidate'), key=lambda t: to_minutes(t)))}.</strong>
        There is no 8:00 AM event anywhere in this series. See {flag_link('F07')}.</li>
  </ol>
</section>

<section class="panel">
  <h2>Day by day</h2>
  <p class="note">Click a day to expand it. Rows marked
  <span class="pill pill-multi-entry">Multi-flight</span> are shown for context and are not part of
  the single-entry plan.</p>
  {''.join(blocks)}
</section>
"""
    return page(
        "Day plan",
        "schedule.html",
        body,
        "One primary event per day plus a conditional fallback, with an overlap check on every pair of starts.",
    )


# ---------------------------------------------------------------------------
# page: hotels
# ---------------------------------------------------------------------------

def tax_url(hotel: dict) -> str:
    for s in D.SOURCES:
        if s["id"] == hotel["taxSourceId"]:
            return s["url"]
    return ""


def build_hotels() -> str:
    rows = []
    for h in sorted(D.HOTELS, key=lambda x: x["walkMin"]):
        within = h["walkMin"] <= 30
        walk_cell = ext_link(h["walkUrl"], h["walkRoute"])
        fee_cell = (
            f'{money(h["resortFee"])} <span class="sub">{e(h["resortFeeLabel"])}</span>'
            if h["resortFee"] is not None
            else unverified("No official page for this hotel states the resort fee")
        )
        rate_cell = (
            unverified("No official page publishes a date-specific rate")
            if h["nightlyRate"] is None
            else money(h["nightlyRate"])
        )
        rows.append(
            f"""<tr data-walk="{h['walkMin']}" data-name="{e(h['name'].lower())}">
      <td data-label="Hotel"><strong>{e(h['name'])}</strong><div class="sub">{e(h['qualityNote'])}</div></td>
      <td data-label="Walk" class="num">{e(h['walkMin'])} min
        <div class="sub">{e(h['walkMi'])} mi</div>
        <div class="sub">{walk_cell}</div>
        <div class="sub">{'<span class="tag tag-ok">Within 30 min</span>' if within else '<span class="tag tag-bad">Over 30 min</span>'}</div>
      </td>
      <td data-label="Nightly rate" class="num">{rate_cell}</td>
      <td data-label="Resort fee" class="num">{fee_cell}</td>
      <td data-label="Tax">{e(h['taxLabel'])} {ext_link(tax_url(h), h['taxSourceId'])}</td>
      <td data-label="True cost / night" class="num">
        <div class="calc" data-resortfee="{h['resortFee'] if h['resortFee'] is not None else ''}">
          <input type="number" min="0" step="1" placeholder="rate" aria-label="Nightly base rate for {e(h['name'])}">
          <output class="calc-out">&mdash;</output>
        </div>
        <div class="sub">rate + fee, then {TAX_RATE * 100:.2f}% tax</div>
      </td>
      <td data-label="Parking">{e(h['parking']) if h['parking'] else unverified('Not read from an official page for this hotel')}</td>
      <td data-label="Booking">{ext_link(h['bookingUrl'], 'Official booking page')}</td>
      <td data-label="Rate note">{e(h['rateNote'])}</td>
      <td data-label="Cancellation">{e(h['cancellation']) if h['cancellation'] else unverified('Not read from an official page for this hotel')}</td>
      <td data-label="Status">{e(h['status'])}</td>
    </tr>"""
        )

    body = f"""
<section class="panel">
  <h2>True cost per night</h2>
  <p class="lede">No official page publishes a static, date-specific room rate - every booking engine
  renders its rates in the browser. What <em>is</em> published and verified is the fee structure, so the
  honest comparison is a calculator rather than a table:</p>
  <p class="formula"><strong>True cost per night = (nightly rate + resort fee) &times; (1 + {TAX_RATE * 100:.2f}%)</strong></p>
  <p class="note">Type a live rate into any row and the calculator applies the verified fee and the
  verified 13.38% Clark County Room Tax. The Venetian row is pre-filled with its resort fee; every
  other row's fee is still unverified, so leave it blank or type the fee your quote shows.</p>
  <div class="filters">
    <label class="field checkbox"><input type="checkbox" id="fWalk" checked>
      <span>Show hotels within a 30-minute walk only</span></label>
  </div>
</section>

<section class="panel">
  <h2>Hotels, closest first ({len(D.HOTELS)} checked)</h2>
  <div class="table-scroll"><table class="data" data-filterable id="tblHotels">
    <thead><tr>
      <th>Hotel</th><th>Walk to Venetian poker room</th><th>Nightly rate</th><th>Resort fee</th>
      <th>Tax</th><th>True cost / night</th><th>Parking</th><th>Booking</th>
      <th>Rate note</th><th>Cancellation</th><th>Status</th>
    </tr></thead>
    <tbody>{''.join(rows)}</tbody>
  </table></div>
  <p class="note">Walking times come from Google Maps walking directions, captured {AS_OF}, and each
  one links the exact route so you can re-check it. {flag_link('F-H5')} records that "The Mirage" no
  longer resolves on Google Maps and is therefore not listed.</p>
</section>

<section class="panel">
  <h2>What the Venetian's own pages confirm</h2>
  <ul class="ticks">
    <li>Resort fee <strong>$55 plus tax per night</strong>, payable on check-in.
        {ext_link('https://www.venetianlasvegas.com/resort/resort-fee.html', 'S06')}</li>
    <li><strong>13.38% Clark County Room Tax</strong> is not included in quoted daily rates.
        {ext_link('https://www.venetianlasvegas.com/legal/hotel-terms-and-conditions.html', 'S08')}</li>
    <li>Self-parking <strong>$20/day</strong> for registered guests, <strong>$40/day</strong> valet, and
        <strong>complimentary</strong> for poker players who play three hours or more - a supervisor must
        confirm the session. {ext_link('https://www.venetianlasvegas.com/resort/casino/poker/player-parking.html', 'S09')}</li>
    <li>Poker suite rates "start as low as $119 and $209", require six hours of live cash game or a
        buy-in to a $300-or-higher tournament <strong>per night stayed</strong>, are only published out to
        150 days, and are booked by phone on code EPOKR25 (866.255.8936). Missing the play requirement
        reverts that night to the prevailing rate.
        {ext_link('https://www.venetianlasvegas.com/resort/casino/poker/suite-rates.html', 'S07')}</li>
    <li>Check-in from 3:00 pm, check-out 11:00 am, and checking out early adds $100 plus tax.
        {ext_link('https://www.venetianlasvegas.com/legal/hotel-terms-and-conditions.html', 'S08')}</li>
  </ul>
</section>

<section class="panel">
  <h2>Rate log</h2>
  <p class="note">Rates are kept as a dated log, never as a single value, so you can see how a quote
  moves. The log is empty because no official page has published a rate for your dates yet.
  {flag_link('F-H1')}</p>
  <div class="table-scroll"><table class="data">
    <thead><tr><th>Logged</th><th>Hotel</th><th>Dates</th><th>Occupancy</th><th>Room</th>
    <th>Base rate</th><th>Resort fee</th><th>Tax</th><th>Total</th><th>Source</th></tr></thead>
    <tbody id="rateLogBody"><tr><td colspan="10" class="empty">No rate captured yet.</td></tr></tbody>
  </table></div>
</section>
"""
    return page(
        "Hotels",
        "hotels.html",
        body,
        "Walking distance to the Venetian poker room, verified fee structure, and a true-cost-per-night calculator.",
    )


# ---------------------------------------------------------------------------
# page: venue
# ---------------------------------------------------------------------------

def build_venue() -> str:
    slug = "venues/venetian.html"
    up = "../"
    total_g = sum(x["guarantee"] or 0 for x in CANDIDATES)
    body = f"""
<section class="hero">
  <h2>The Venetian Resort Las Vegas</h2>
  <p class="lede">Poker room: <strong>The Palazzo, level 2, Grand Canal Shoppes</strong>. Open 24 hours
  daily, 50 tables across 14,000 square feet - the largest poker room on the Strip.
  {ext_link('https://www.venetianlasvegas.com/resort/casino/poker.html', 'Official poker room page (S05)')}</p>
</section>

<section class="kpi-grid">
  <div class="card kpi"><div class="kpi-value">Nov 16 &ndash; Dec 23, 2026</div>
    <div class="kpi-label">DeepStack Extravaganza IV</div>
    <div class="kpi-note">More than $3.6M in guaranteed prize pools across the whole series</div></div>
  <div class="card kpi"><div class="kpi-value">{len(EVENTS)}</div>
    <div class="kpi-label">Scheduled starts</div>
    <div class="kpi-note">Across 64 event numbers</div></div>
  <div class="card kpi"><div class="kpi-value">{len(CANDIDATES)}</div>
    <div class="kpi-label">Single-day candidates</div>
    <div class="kpi-note">{money(total_g)} of combined guarantees</div></div>
  <div class="card kpi"><div class="kpi-value">0</div>
    <div class="kpi-label">Events confirmed as single entry</div>
    <div class="kpi-note">No sheet prints an entry-count rule - {flag_link('F01', up)}</div></div>
</section>

<section class="panel">
  <h2>Series at this venue</h2>
  <div class="table-scroll"><table class="data">
    <thead><tr><th>Series</th><th>Dates</th><th>Headline events</th><th>Status here</th><th>Source</th></tr></thead>
    <tbody>
      <tr><td>WPT Fall Festival</td><td>Oct 28 &ndash; Nov 15, 2026</td>
        <td>$1,100 NLH $500K GTD; $5,000 NLH $2M GTD; $600 NLH $300K GTD</td>
        <td>Finished before this snapshot - not researched</td>
        <td>{ext_link('https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament.html', 'S01')}</td></tr>
      <tr><td><strong>DeepStack Extravaganza IV</strong></td><td>Nov 16 &ndash; Dec 23, 2026</td>
        <td>$800 NLH $500K GTD; $2,200 NLH $1M GTD; $1,100 Seniors $300K GTD; $1,100 NLH $500K GTD; $600 NLH $150K GTD</td>
        <td><strong>Fully verified - all 37 structure sheets read</strong></td>
        <td>{ext_link('https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html', 'S02')}</td></tr>
      <tr><td>DeepStack Extravaganza NYE</td><td>Dec 24, 2026 &ndash; Jan 10, 2027</td>
        <td>$2,200 NLH $300K GTD; $1,600 NLH MSPT $400K GTD</td>
        <td>Series dates verified on the hub page; structure sheets not read</td>
        <td>{ext_link('https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-dec-2026.html', 'S01 hub')}</td></tr>
      <tr><td>DeepStack Showdown (January)</td><td>Jan 11 &ndash; Feb 14, 2027</td>
        <td>$250 NLH $100K GTD; $300 NLH $100K GTD; $400 NLH $75K GTD; $600 NLH $125K GTD; $800 NLH $150K GTD; $1,600 NLH $1M GTD</td>
        <td>Series dates verified on the hub page; structure sheets not read</td>
        <td>{ext_link('https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dss-jan-2027.html', 'S01 hub')}</td></tr>
      <tr><td>DeepStack Championship 2027</td><td>May &ndash; July 2027 (TBD)</td>
        <td>Details expected around March 2027</td>
        <td>Not scheduled in detail on the official page</td>
        <td>{ext_link('https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament.html', 'S01')}</td></tr>
    </tbody>
  </table></div>
</section>

<section class="panel">
  <h2>Hotels at or near this venue</h2>
  <p class="note">Walking times are to the Venetian poker room entrance. Full fee, tax and cancellation
  detail is on the <a href="{up}hotels.html">Hotels</a> page.</p>
  <div class="table-scroll"><table class="data" data-filterable>
    <thead><tr><th>Hotel</th><th>Walk</th><th>Distance</th><th>Resort fee</th><th>Route source</th><th>Booking</th></tr></thead>
    <tbody>
    {"".join(f'''<tr><td data-label="Hotel">{e(h['name'])}</td>
      <td data-label="Walk" class="num">{e(h['walkMin'])} min</td>
      <td data-label="Distance" class="num">{e(h['walkMi'])} mi</td>
      <td data-label="Resort fee" class="num">{money(h['resortFee']) if h['resortFee'] is not None else unverified('No official page states this fee')}</td>
      <td data-label="Route source">{ext_link(h['walkUrl'], 'Route')}</td>
      <td data-label="Booking">{ext_link(h['bookingUrl'], 'Official page')}</td></tr>''' for h in sorted(D.HOTELS, key=lambda x: x['walkMin']))}
    </tbody>
  </table></div>
</section>

<section class="panel">
  <h2>All events at this venue</h2>
  <p class="note">The complete DSE IV list is on the <a href="{up}events.html">Events</a> page, where
  the filters, the search box and the multi-entry section live. This page is the venue's own summary.</p>
  {ratio_table(sorted([x for x in CANDIDATES if x['ratio']], key=lambda x: -x['ratio']))}
</section>

<section class="panel">
  <h2>Room rules that affect planning</h2>
  <ul class="ticks">
    <li>Players must be 21+ and hold a Venetian Rewards card to enter any tournament (every structure sheet).</li>
    <li>Seniors events (24, 32, 49) require players to be 50+. A player under 50 who buys in forfeits
        both prize money and the buy-in.</li>
    <li>The LIPS Ladies main event (39) and its satellites (33, 37) are open to female players only.</li>
    <li>TDA rules apply to all Venetian Poker Room tournaments.</li>
    <li>Management reserves the right to cancel or change any tournament.</li>
  </ul>
</section>
"""
    p = page("Venue: The Venetian", slug, body,
             "DeepStack Extravaganza IV in full: series, events, hotels and room rules.")
    return p


# ---------------------------------------------------------------------------
# page: trip cost
# ---------------------------------------------------------------------------

def build_trip_cost() -> str:
    opts = "".join(
        f'<option value="{x["id"]}" data-buyin="{x["buyIn"]}" data-guarantee="{x["guarantee"] or 0}">'
        f'#{x["eventNo"]}{(" " + x["flight"]) if x["flight"] else ""} &middot; {e(x["dateLabel"])} '
        f'&middot; {e(x["name"])} &mdash; {money(x["buyIn"])}</option>'
        for x in sorted(CANDIDATES, key=lambda x: (x["date"], x["startMin"] or 0))
    )
    hotel_opts = "".join(
        f'<option value="{i}" data-fee="{h["resortFee"] if h["resortFee"] is not None else ""}">{e(h["name"])} &mdash; {h["walkMin"]} min walk</option>'
        for i, h in enumerate(sorted(D.HOTELS, key=lambda x: x["walkMin"]))
    )
    body = f"""
<section class="panel">
  <h2>Estimated cost of a trip</h2>
  <p class="formula"><strong>Trip cost = (entries &times; buy-in) + (nights &times; true nightly cost)</strong></p>
  <p class="formula"><strong>True nightly cost = (nightly rate + resort fee) &times; {1 + TAX_RATE:.4f}</strong>
    <span class="sub">the {TAX_RATE * 100:.2f}% is the verified Clark County Room Tax</span></p>

  <div class="calc-grid">
    <div class="calc-card">
      <h3>1 &middot; Tournament entries</h3>
      <label class="field"><span>Pick events (hold Ctrl/Cmd to select several)</span>
        <select id="tcEvents" multiple size="12">{opts}</select></label>
      <label class="field"><span>Number of entries in total</span>
        <input type="number" id="tcEntries" value="1" min="0" step="1"></label>
      <p class="calc-line">Entry subtotal: <output id="tcEntryTotal">$0</output></p>
      <p class="calc-line sub">Combined guarantee across the selected events:
        <output id="tcGuarantee">$0</output></p>
    </div>

    <div class="calc-card">
      <h3>2 &middot; Room</h3>
      <label class="field"><span>Hotel</span><select id="tcHotel">{hotel_opts}</select></label>
      <label class="field"><span>Nightly base rate from your live quote</span>
        <input type="number" id="tcRate" min="0" step="1" placeholder="0"></label>
      <label class="field"><span>Resort fee per night (blank = unverified for this hotel)</span>
        <input type="number" id="tcFee" min="0" step="1" placeholder="0"></label>
      <label class="field"><span>Nights</span><input type="number" id="tcNights" value="5" min="0" step="1"></label>
      <p class="calc-line">True cost per night: <output id="tcPerNight">$0</output></p>
      <p class="calc-line sub">Room subtotal: <output id="tcRoomTotal">$0</output></p>
    </div>

    <div class="calc-card">
      <h3>3 &middot; Extras</h3>
      <label class="field checkbox"><input type="checkbox" id="tcParkingCredit" checked>
        <span>I will play 3+ hours a day, so Venetian self-parking is complimentary
        ({ext_link('https://www.venetianlasvegas.com/resort/casino/poker/player-parking.html', 'S09')})</span></label>
      <label class="field"><span>Parking per day otherwise</span>
        <input type="number" id="tcParking" value="20" min="0" step="1"></label>
      <label class="field"><span>Days parking is needed</span>
        <input type="number" id="tcParkingDays" value="5" min="0" step="1"></label>
      <p class="calc-line">Parking total: <output id="tcParkingTotal">$0</output></p>
    </div>
  </div>

  <div class="total-card">
    <div class="total-label">Estimated total trip cost</div>
    <div class="total-value" id="tcTotal">$0</div>
    <div class="total-break" id="tcBreak"></div>
  </div>

  <p class="callout">This is a planning estimate built from your own inputs plus the verified fee and
  tax structure. It is not a quote. The nightly base rate and most resort fees are
  <span class="uv">unverified</span> because no official page publishes them for specific dates
  ({flag_link('F-H1')}). Re-run it once you have a live itemised quote.</p>
</section>

<section class="panel">
  <h2>What each extra entry costs</h2>
  <p class="note">A quick way to see whether a second event in a day is worth it. Entry fee is what the
  official sheet prints; the "to prize pool" column is what actually goes into the pool after the
  house fee.</p>
  <div class="table-scroll"><table class="data" data-filterable>
    <thead><tr><th>Event</th><th>Date</th><th>Entry</th><th>House fee</th><th>To prize pool</th>
    <th>Fee as % of entry</th><th>Guarantee</th><th>Source</th></tr></thead>
    <tbody>
    {"".join(f'''<tr><td data-label="Event">#{x['eventNo']}{e(' ' + x['flight'] if x['flight'] else '')} {e(x['name'])}</td>
      <td data-label="Date">{e(x['dateLabel'])}</td>
      <td data-label="Entry" class="num">{money(x['buyIn'])}</td>
      <td data-label="House fee" class="num">{money(x['houseFee'])}</td>
      <td data-label="To prize pool" class="num">{money(x['prizePoolShare'])}</td>
      <td data-label="Fee as % of entry" class="num">{x['houseFee'] / x['buyIn'] * 100:.1f}%</td>
      <td data-label="Guarantee" class="num">{e(x['guaranteeLabel']) if x['guaranteeLabel'] else unverified()}</td>
      <td data-label="Source">{ext_link(x['structureUrl'], x['structureLabel'])}</td></tr>'''
              for x in sorted(CANDIDATES, key=lambda x: -x['houseFee'] / x['buyIn']))}
    </tbody>
  </table></div>
</section>
"""
    return page(
        "Trip cost",
        "trip-cost.html",
        body,
        "Entries times buy-in, plus nights times the true nightly cost including resort fee and tax.",
    )


# ---------------------------------------------------------------------------
# page: questions
# ---------------------------------------------------------------------------

def build_questions() -> str:
    order = {"Blocker": 0, "High": 1, "Medium": 2, "Low": 3}
    rows = sorted(D.QUESTIONS, key=lambda q: order.get(q["priority"], 9))
    body_cards = "".join(
        f"""<details class="q" id="{e(q['id'])}">
    <summary>
      <span class="q-id">{e(q['id'])}</span>
      <span class="q-text">{e(q['question'])}</span>
      <span class="tag tag-{'bad' if q['priority'] == 'Blocker' else ('warn' if q['priority'] == 'High' else '')}">{e(q['priority'])}</span>
    </summary>
    <div class="q-body">
      <p><strong>What we already know.</strong> {e(q['known'])}</p>
      <p><strong>What we do not know.</strong> {e(q['unknown'])}</p>
      <p><strong>What it blocks.</strong> {e(q['blocks'])}</p>
      <p><strong>How to find out.</strong> {e(q['howToResolve'])}</p>
    </div>
  </details>"""
        for q in rows
    )
    body = f"""
<section class="panel">
  <h2>Questions that must be answered before a reasonable decision can be made</h2>
  <p class="lede">Each entry separates what the official sources already prove from what is still
  missing, and says exactly how to close the gap. Blocker items should be settled before you spend any
  money.</p>
</section>
<section class="panel">{body_cards}</section>
"""
    return page(
        "Questions",
        "questions.html",
        body,
        "What is known, what is unknown, and how to find out - before any decision is made.",
    )


# ---------------------------------------------------------------------------
# page: suggestions
# ---------------------------------------------------------------------------

def build_suggestions() -> str:
    cards = "".join(
        f"""<div class="card suggestion" id="{e(s['id'])}">
      <div class="s-head"><span class="s-id">{e(s['id'])}</span>
        <span class="tag tag-{'ok' if s['status'].startswith('Built') else ''}">{e(s['status'])}</span></div>
      <h3>{e(s['title'])}</h3>
      <p><strong>Problem.</strong> {e(s['problem'])}</p>
      <p><strong>Proposal.</strong> {e(s['proposal'])}</p>
      <p class="s-meta"><strong>Effort</strong> {e(s['effort'])} &middot; <strong>Value</strong> {e(s['value'])}</p>
      <p class="s-decision"><strong>Decision:</strong> <span class="tag tag-warn">{e(s['decision'])}</span></p>
    </div>"""
        for s in D.SUGGESTIONS
    )
    body = f"""
<section class="panel">
  <h2>Suggestions to improve decision making</h2>
  <p class="lede">Nothing here is implemented without a decision. Each card states the problem, the
  proposal, the effort and the value, so you can pick a path and only then ask for it to be built.
  Items already implemented are marked <span class="tag tag-ok">Built</span>.</p>
</section>

<section class="panel">
  <h2>Decision record</h2>
  <div class="table-scroll"><table class="data">
    <thead><tr><th>ID</th><th>Suggestion</th><th>Effort</th><th>Value</th><th>Status</th><th>Your decision</th></tr></thead>
    <tbody>
    {"".join(f'''<tr><td data-label="ID">{e(s['id'])}</td>
      <td data-label="Suggestion">{e(s['title'])}</td>
      <td data-label="Effort">{e(s['effort'])}</td>
      <td data-label="Value">{e(s['value'])}</td>
      <td data-label="Status">{e(s['status'])}</td>
      <td data-label="Decision"><span class="tag tag-warn">{e(s['decision'])}</span></td></tr>''' for s in D.SUGGESTIONS)}
    </tbody>
  </table></div>
</section>

<section class="suggestion-grid">{cards}</section>
"""
    return page(
        "Suggestions",
        "suggestions.html",
        body,
        "Improvement proposals with effort and value, awaiting a decision before implementation.",
    )


# ---------------------------------------------------------------------------
# page: flagged
# ---------------------------------------------------------------------------

def build_flagged() -> str:
    order = {"Blocker for the single-entry claim": 0, "Blocker for hotel ranking": 0,
             "High": 1, "Medium": 2, "Low": 3}
    rows = sorted(D.FLAGS, key=lambda f: order.get(f["severity"], 9))
    cards = "".join(
        f"""<details class="flag" id="{e(f['id'])}">
    <summary><span class="f-id">{e(f['id'])}</span>
      <span class="f-title">{e(f['title'])}</span>
      <span class="tag tag-{'bad' if f['severity'].startswith('Blocker') else ('warn' if f['severity'] == 'High' else '')}">{e(f['severity'])}</span></summary>
    <div class="f-body">
      <p>{e(f['detail'])}</p>
      <p><strong>Why it matters.</strong> {e(f['impact'])}</p>
      <p><strong>What to do.</strong> {e(f['action'])}</p>
      <p><strong>Source.</strong> {ext_link(f['source'], f['source'])}{(' &middot; register id ' + f['sourceId']) if f['sourceId'] else ''}</p>
    </div>
  </details>"""
        for f in rows
    )
    body = f"""
<section class="panel">
  <h2>Flagged for review</h2>
  <p class="lede">Every irregularity, gap and unverified value, each with a link to the official source
  that exposes it. Nothing here blocks the site - it is the list to work through before you commit
  money.</p>
  <p class="note">{len(D.FLAGS)} items. Two are blockers: the single-entry question
  ({flag_link('F01')}) and the missing date-specific hotel rates ({flag_link('F-H1')}).</p>
</section>
<section class="panel">{cards}</section>
"""
    return page(
        "Flagged for review",
        "flagged.html",
        body,
        "Every irregularity and unverified value, with the official source that exposes it.",
    )


# ---------------------------------------------------------------------------
# page: sources
# ---------------------------------------------------------------------------

def build_sources() -> str:
    rows = "".join(
        f"""<tr data-id="{e(s['id'])}">
      <td data-label="ID">{e(s['id'])}</td>
      <td data-label="Publisher">{e(s['publisher'])}</td>
      <td data-label="Source">{ext_link(s['url'], s['label'])}<div class="sub url">{e(s['url'])}</div></td>
      <td data-label="What it proves">{e(s['substantiates'])}</td>
      <td data-label="Last checked">{e(s['retrieved'])}</td>
    </tr>"""
        for s in D.SOURCES
    )
    body = f"""
<section class="panel">
  <h2>Official source register</h2>
  <p class="lede">Every number on this site resolves to one of these. Nothing is taken from a
  third-party listing, forum or aggregator.</p>
  <div class="table-scroll"><table class="data" data-filterable>
    <thead><tr><th>ID</th><th>Publisher</th><th>Source</th><th>What it proves</th><th>Last checked</th></tr></thead>
    <tbody>{rows}</tbody>
  </table></div>
</section>
"""
    return page(
        "Sources",
        "sources.html",
        body,
        "The official source register behind every figure on this site.",
    )


# ---------------------------------------------------------------------------
# page: changes
# ---------------------------------------------------------------------------

def build_changes() -> str:
    rows = "".join(
        f"""<tr>
      <td data-label="URL">{ext_link(s['url'], s['url'])}</td>
      <td data-label="What it proves">{e(s['label'])}</td>
      <td data-label="Baseline captured">{e(s['retrieved'])}</td>
      <td data-label="Last automated check"><span class="uv">not yet run</span></td>
      <td data-label="Status"><span class="tag">Baseline only</span></td>
    </tr>"""
        for s in D.SOURCES
    )
    body = f"""
<section class="panel">
  <h2>Change monitoring</h2>
  <p class="lede">Each official URL below is re-fetched on a schedule by a GitHub Actions workflow. The
  run stores a content hash and a snapshot; when a page differs from the stored snapshot the workflow
  opens an issue and the row shows a <span class="tag tag-warn">Changed</span> badge on this page.</p>
  <p class="note">As of {AS_OF} only the baseline snapshot exists, so every row reads "Baseline only".
  See {flag_link('F-X2')}.</p>
  <div class="table-scroll"><table class="data" data-filterable>
    <thead><tr><th>URL</th><th>What it proves</th><th>Baseline captured</th>
    <th>Last automated check</th><th>Status</th></tr></thead>
    <tbody>{rows}</tbody>
  </table></div>
</section>

<section class="panel">
  <h2>How to run a re-check yourself</h2>
  <pre class="code">gh workflow run monitor-sources.yml
# or let the schedule run it daily at 13:00 UTC</pre>
  <p class="note">The workflow writes <code>monitor/snapshots/&lt;hash&gt;.txt</code> and updates
  <code>monitor/state.json</code>. Review the diff in the issue it opens before changing any value on
  the site: a changed page is a prompt to re-verify, not to overwrite.</p>
</section>
"""
    return page(
        "Changes",
        "changes.html",
        body,
        "Scheduled re-checks of every official URL, with a record of what changed and when.",
    )


# ---------------------------------------------------------------------------
# JSON output
# ---------------------------------------------------------------------------

def dump_json() -> None:
    data_dir = SITE / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    payloads = {
        "events.json": {
            "asOf": AS_OF,
            "series": "DeepStack Extravaganza IV",
            "venue": "The Venetian Resort Las Vegas",
            "taxRate": TAX_RATE,
            "counts": {
                "all": len(EVENTS),
                "singleEntryCandidates": len(CANDIDATES),
                "multiEntry": len(MULTI),
                "satellite": len(SATS),
                "continuation": len(CONT),
            },
            "events": EVENTS,
        },
        "hotels.json": {"asOf": AS_OF, "taxRate": TAX_RATE, "hotels": D.HOTELS},
        "sources.json": {"asOf": AS_OF, "sources": D.SOURCES},
        "flags.json": {"asOf": AS_OF, "flags": D.FLAGS},
        "questions.json": {"asOf": AS_OF, "questions": D.QUESTIONS},
        "suggestions.json": {"asOf": AS_OF, "suggestions": D.SUGGESTIONS},
        "rate_log.json": {"asOf": AS_OF, "entries": D.RATE_LOG},
    }
    for name, payload in payloads.items():
        (data_dir / name).write_text(
            json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

# Only these paths are generated by this script; everything else under site/
# (notably site/poker3/, another session's artifact that CI also checks) is
# left untouched.
GENERATED_FILES = [
    "index.html", "events.html", "schedule.html", "hotels.html",
    "trip-cost.html", "questions.html", "suggestions.html",
    "flagged.html", "sources.html", "changes.html",
]
GENERATED_DIRS = ["venues", "data"]


def main() -> None:
    SITE.mkdir(parents=True, exist_ok=True)

    # Clear only the generated output so a rebuild cannot leave stale pages.
    for name in GENERATED_FILES:
        target = SITE / name
        if target.exists():
            target.unlink()
    for name in GENERATED_DIRS:
        target = SITE / name
        if target.exists():
            shutil.rmtree(target)

    write(SITE / "index.html", build_index())
    write(SITE / "events.html", build_events_page())
    write(SITE / "schedule.html", build_schedule())
    write(SITE / "hotels.html", build_hotels())
    write(VENUES / "venetian.html", build_venue())
    write(SITE / "trip-cost.html", build_trip_cost())
    write(SITE / "questions.html", build_questions())
    write(SITE / "suggestions.html", build_suggestions())
    write(SITE / "flagged.html", build_flagged())
    write(SITE / "sources.html", build_sources())
    write(SITE / "changes.html", build_changes())
    dump_json()

    # Assets live in scripts/assets so a clean rebuild cannot lose them.
    assets_src = pathlib.Path(__file__).resolve().parent / "assets"
    assets_dst = SITE / "assets"
    assets_dst.mkdir(parents=True, exist_ok=True)
    for asset in sorted(assets_src.iterdir()):
        shutil.copy2(asset, assets_dst / asset.name)

    print(f"Built site/: {len(EVENTS)} starts "
          f"({len(CANDIDATES)} candidates, {len(MULTI)} multi-entry, "
          f"{len(SATS)} satellite, {len(CONT)} continuation), "
          f"{len(D.HOTELS)} hotels, {len(D.SOURCES)} sources, {len(D.FLAGS)} flags.")


if __name__ == "__main__":
    main()
