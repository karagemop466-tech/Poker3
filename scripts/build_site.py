#!/usr/bin/env python3
"""Build the canonical GitHub Pages dashboard in site/ from the curated data files.

Inputs (each curated from official sources only; see data/*.json and COORDINATION.md):
  data/venetian_dse_iv.json  - Venetian DeepStack Extravaganza IV: 94 schedule rows, 37 structure sheets
  data/rooms.json            - the other Strip poker rooms and their recurring official slates
  data/hotels.json           - hotels, fee/tax/parking/cancellation terms, dated rate log
  data/routes.json           - hotel <-> venue walking pairs
  data/sources.json          - official source register
  data/flags.json            - flagged irregularities and open questions

Outputs:
  site/data.json             - merged dataset read by the browser scripts
  site/*.html                - the published pages
  site/venues/*.html         - one page per venue

Nothing here invents a value. Every number comes from a data file and every row
keeps the source link that produced it. Where a value could not be read from an
official source it stays blank and is listed on the Flagged for review page.

Run:  python3 scripts/build_site.py
"""
from __future__ import annotations

import json
import pathlib
import re
from datetime import date, datetime, timedelta

ROOT = pathlib.Path(__file__).resolve().parents[1]
SITE = ROOT / "site"

NAV = [
    ("index.html", "Overview", "▦"),
    ("tournaments.html", "Tournaments", "♠"),
    ("schedule.html", "Day plan", "◷"),
    ("hotels.html", "Hotels", "⌂"),
    ("cost.html", "Trip cost", "∑"),
    ("venues/index.html", "Venues", "⌸"),
    ("sources.html", "Sources", "❑"),
    ("questions.html", "Open questions", "?"),
    ("suggestions.html", "Suggestions", "✦"),
    ("flagged.html", "Flagged for review", "⚑"),
    ("monitor.html", "Change monitor", "⟳"),
]

# How each entry verdict is grouped on the site.
VERDICT_BUCKET = {
    "unverified - single entry not stated": "unverified",
    "extra spend possible - one entry per flight": "multi",
    "extra spend possible - seat prize": "spend",
    "extra spend possible - multiple flights and a paid chip boost": "spend",
    "extra spend confirmed - the sheet sells further buy-ins": "spend",
    "extra spend confirmed - re-entries are sold": "spend",
    "extra spend confirmed - the sheet sells rebuys and an add-on": "spend",
    "extra spend confirmed - re-entries and an add-on are sold": "spend",
    "extra spend confirmed - re-entries and add-ons are sold": "spend",
    "extra spend confirmed - re-entries and a paid chip boost are sold": "spend",
    "extra spend confirmed - a paid chip boost is sold": "spend",
    "extra spend confirmed - the sheet sells an add-on": "spend",
    "team format - needs review": "review",
    "needs review": "review",
}

BUCKET_TITLE = {
    "strict": "One entry, confirmed by the structure sheet",
    "unverified": "Single entry not stated on the sheet",
    "multi": "Multi-flight: one entry per flight, so extra spend is possible",
    "spend": "Extra-spend format: the sheet sells more entries, or the prize is a seat",
    "review": "Needs review before you plan around it",
    "other": "Other official rooms",
}

BUCKET_NOTE = {
    "strict": "The official structure sheet states one entry and no re-entry, rebuy, add-on or paid chip boost.",
    "unverified": "The sheet was read in full and does not mention re-entry, rebuy, add-on or a paid chip boost. Silence is not proof, so these rows are not called single-entry. Ask the room before you rely on it.",
    "multi": "The sheet names separate starting flights and only bars players who bag chips from entering a later flight, so a player eliminated in one flight may buy into another.",
    "spend": "Either the sheet sells further buy-ins, or the prize is a seat, so each extra buy-in is another chance at the same prize.",
    "review": "The format or the published terms need a decision before this event is worth planning around.",
    "other": "Recurring official slates from the other Strip rooms. Each row keeps its own official source link.",
}

VENETIAN_VENUE = {
    "id": "venetian",
    "name": "The Venetian Resort Las Vegas",
    "slug": "venetian",
    "pokerRoom": "The Venetian poker room, at The Palazzo on level 2 of the Grand Canal Shoppes",
    "address": "3355 Las Vegas Blvd S, Las Vegas, NV 89109",
    "addressSourceId": "",
    "scheduleSourceId": "venetian-dse4",
    "coverage": "The official event page, the official schedule PDF and all 37 official structure sheets were read on 2026-11-16.",
    "note": "94 published schedule rows across 64 numbered events, November 16 to December 23, 2026.",
    "phone": "",
    "eventsAreRecurring": False,
}


# ---------------------------------------------------------------- helpers ----
def esc(value) -> str:
    if value is None:
        return ""
    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


def usd(value, decimals=0) -> str:
    if value is None or value == "":
        return ""
    try:
        number = float(value)
    except (TypeError, ValueError):
        return str(value)
    if decimals:
        return "$" + f"{number:,.{decimals}f}"
    return "$" + f"{number:,.0f}"


def parse_time(text) -> int | None:
    """'10:10 AM' -> minutes after midnight."""
    if not text:
        return None
    m = re.match(r"^\s*(\d{1,2}):(\d{2})\s*(AM|PM)\s*$", str(text), re.I)
    if not m:
        return None
    hour, minute, meridiem = int(m.group(1)), int(m.group(2)), m.group(3).upper()
    if meridiem == "PM" and hour != 12:
        hour += 12
    if meridiem == "AM" and hour == 12:
        hour = 0
    return hour * 60 + minute


def fmt_time(minutes) -> str:
    if minutes is None:
        return ""
    hour, minute = divmod(int(minutes), 60)
    meridiem = "AM" if hour < 12 else "PM"
    hour12 = hour % 12 or 12
    return f"{hour12}:{minute:02d} {meridiem}"


def ratio(numerator, denominator):
    if not numerator or not denominator:
        return ""
    return round(numerator / denominator, 2)


def load(name):
    return json.loads((ROOT / "data" / name).read_text(encoding="utf-8"))


def weekday(date_iso: str) -> str:
    try:
        return datetime.strptime(date_iso, "%Y-%m-%d").strftime("%A")
    except ValueError:
        return ""


# ------------------------------------------------------------ data assembly --
def build_dataset():
    venetian = load("venetian_dse_iv.json")
    rooms = load("rooms.json")
    hotels = load("hotels.json")
    routes = load("routes.json")
    sources = load("sources.json")
    flags = load("flags.json")

    source_by_id = {s["id"]: s for s in sources["sources"]}
    events = []

    for row in venetian["events"]:
        event = dict(row)
        event["venueId"] = "venetian"
        event["venueName"] = "The Venetian"
        event["sourceIds"] = ["venetian-dse4", "venetian-dse4-pdf", "venetian-dse4-structures"]
        event["scheduleUrl"] = venetian["scheduleUrl"]
        event["sheetUrl"] = row["structureSheet"]
        event["dateISO"] = event["date"]
        event["weekday"] = weekday(event["date"])
        event["isDated"] = True
        events.append(event)

    for venue in rooms["venues"]:
        for row in venue["events"]:
            event = dict(row)
            event["venueId"] = venue["id"]
            event["venueName"] = venue["name"]
            event["sourceIds"] = list(row.get("sourceIds", []))
            event["scheduleUrl"] = ""
            event["sheetUrl"] = ""
            event["dateISO"] = ""
            event["weekday"] = ""
            event["isDated"] = False
            events.append(event)

    for event in events:
        verdict = event.get("eligibility", "needs review")
        event["bucket"] = VERDICT_BUCKET.get(verdict, "review")
        event["bucketLabel"] = BUCKET_TITLE.get(event["bucket"], "Other")
        event["startMinutes"] = parse_time(event.get("time"))
        event["regCloseMinutes"] = parse_time(event.get("lateRegistrationCloses"))
        if event["startMinutes"] is not None and event["regCloseMinutes"] is not None:
            event["minLengthMinutes"] = event["regCloseMinutes"] - event["startMinutes"]
        else:
            event["minLengthMinutes"] = None
        event["gtdRatio"] = ratio(event.get("guarantee"), event.get("buyIn"))
        event["cashRatio"] = ratio(event.get("cashPoolPerEntry"), event.get("buyIn"))
        event["sourceLinks"] = [
            {
                "id": sid,
                "name": source_by_id[sid]["name"],
                "url": source_by_id[sid]["url"],
                "kind": source_by_id[sid]["kind"],
            }
            for sid in event.get("sourceIds", [])
            if sid in source_by_id
        ]

    venues = [VENETIAN_VENUE]
    for venue in rooms["venues"]:
        item = dict(venue)
        item["eventsAreRecurring"] = True
        venues.append(item)
    for venue in venues:
        venue["eventCount"] = sum(1 for e in events if e["venueId"] == venue["id"])
        venue["strictCount"] = sum(
            1 for e in events if e["venueId"] == venue["id"] and e["bucket"] == "strict"
        )

    # Hotels: true nightly cost from the dated rate log.
    tax_rate = hotels["taxModel"]["roomTaxRate"]
    for hotel in hotels["hotels"]:
        observations = []
        for rate in hotel.get("rates", []):
            obs = dict(rate)
            obs["trueNightly"] = round(obs["nightlyWithFee"] * (1 + tax_rate), 2)
            obs["trueStay"] = round(obs["trueNightly"] * obs.get("nights", 0), 2)
            obs["preTaxStay"] = round(obs["nightlyWithFee"] * obs.get("nights", 0), 2)
            observations.append(obs)
        hotel["rateLog"] = sorted(
            observations, key=lambda r: (r["checked"], r.get("nightlyWithFee", 0))
        )
        # The rate to plan with is the cheapest one published on the most recent check
        # date. The other observations on that date are the room types above it.
        latest = None
        if hotel["rateLog"]:
            newest_date = max(r["checked"] for r in hotel["rateLog"])
            on_newest = [r for r in hotel["rateLog"] if r["checked"] == newest_date]
            latest = min(on_newest, key=lambda r: r["nightlyWithFee"])
            hotel["newestDate"] = newest_date
            hotel["newestObservations"] = on_newest
            hotel["rateRange"] = {
                "lowest": min(r["nightlyWithFee"] for r in on_newest),
                "highest": max(r["nightlyWithFee"] for r in on_newest),
            }
        hotel["latestRate"] = latest
        hotel["trueNightly"] = latest["trueNightly"] if latest else ""
        hotel["trueStay"] = latest["trueStay"] if latest else ""
        hotel["preTaxStay"] = latest["preTaxStay"] if latest else ""
        hotel["hasRate"] = latest is not None
        # The nightly average across every dated observation of the same stay.
        if hotel["rateLog"]:
            hotel["nightlyAverage"] = round(
                sum(r["trueNightly"] for r in hotel["rateLog"]) / len(hotel["rateLog"]), 2
            )
            hotel["nightlyAveragePreTax"] = round(
                sum(r["preTaxStay"] / max(r.get("nights", 1), 1) for r in hotel["rateLog"])
                / len(hotel["rateLog"]),
                2,
            )
            hotel["observationCount"] = len(hotel["rateLog"])
        else:
            hotel["nightlyAverage"] = ""
            hotel["nightlyAveragePreTax"] = ""
            hotel["observationCount"] = 0
        # A checkout total is only published when every component of it is published.
        # The booking pages state the rate excludes taxes, so the tax-inclusive figure
        # is an estimate of the nightly cost, not the folio the guest is charged.
        hotel["checkoutTotal"] = ""
        hotel["checkoutTotalNote"] = (
            "not published: the official booking page states the rate excludes taxes, so the "
            "final folio is not a figure this site can quote"
        )
        hotel["trueStayNote"] = (
            "Tax-inclusive estimate of the stay: the published rate including the resort fee, "
            "plus 13.38% room tax, times the number of nights."
        )
        hotel["rateStatus"] = (
            f"Latest dated observation: {usd(latest['nightlyWithFee'])} per night with the resort fee, "
            f"{usd(latest['trueNightly'], 2)} with {tax_rate*100:.2f}% room tax "
            f"(checked {latest['checked']}, {latest.get('roomType','')})"
            if latest
            else "No date-specific rate could be read from an official source - see Flagged for review"
        )
        # The fee is published, so the fee total is known even when the rate is not.
        fee = hotel.get("resortFee", {})
        hotel["feeTotalKnown"] = bool(fee.get("nightly"))
        hotel["feeNightly"] = fee.get("nightly", "")

    # Routes with map links.
    hotel_by_id = {h["id"]: h for h in hotels["hotels"]}
    venue_by_id = {v["id"]: v for v in venues}
    for route in routes["routes"]:
        origin = hotel_by_id.get(route["fromId"], {})
        destination = venue_by_id.get(route["toVenueId"], {})
        origin_label = origin.get("address") or route["fromName"]
        dest_label = destination.get("address") or route["toName"]
        route["originLabel"] = origin_label
        route["destinationLabel"] = dest_label
        route["mapsUrl"] = (
            "https://www.google.com/maps/dir/?api=1&travelmode=walking&origin="
            + route["originLabel"].replace(" ", "+")
            + "&destination="
            + route["destinationLabel"].replace(" ", "+")
        )
        route["appleMapsUrl"] = (
            "https://maps.apple.com/?saddr="
            + route["originLabel"].replace(" ", "+")
            + "&daddr="
            + route["destinationLabel"].replace(" ", "+")
        )
        route["withinLimit"] = (
            bool(route["minutes"]) and route["minutes"] <= routes.get("walkLimitMinutes", 30)
        )
        route["sourceUrl"] = source_by_id.get(route.get("sourceId"), {}).get("url", "")

    # Day plan and overlap check, using published start and registration-close times.
    days = []
    venetian_days = sorted({e["date"] for e in events if e["venueId"] == "venetian"})
    for day in venetian_days:
        rows = sorted(
            [e for e in events if e["venueId"] == "venetian" and e["date"] == day],
            key=lambda e: (e["startMinutes"] if e["startMinutes"] is not None else 10**6),
        )
        # A primary event is the earliest one a traveller could enter without buying a
        # second entry. If every event that day needs extra spend, the primary is the
        # earliest of those and says so.
        eligible = [e for e in rows if e["bucket"] in {"strict", "unverified"}]
        extra = [e for e in rows if e["bucket"] in {"multi", "spend"}]
        primary = eligible[0] if eligible else (extra[0] if extra else None)
        primary_needs_extra_spend = primary is not None and primary["bucket"] in {"multi", "spend"}
        # The fallback is the next event that starts after the primary's registration
        # closes, so the two can be played in sequence. If nothing starts that late, the
        # next event of the day is offered and the overlap check says it may clash.
        fallback = None
        fallback_conflict = False
        if primary is not None:
            later = [
                e
                for e in rows
                if e is not primary
                and e["startMinutes"] is not None
                and primary["regCloseMinutes"] is not None
                and e["startMinutes"] >= primary["regCloseMinutes"]
            ]
            fallback = later[0] if later else None
            if fallback is None:
                others = [e for e in rows if e is not primary]
                fallback = others[0] if others else None
                fallback_conflict = fallback is not None
        pairs = []
        for i, first in enumerate(rows):
            for second in rows[i + 1 :]:
                if first["startMinutes"] is None or second["startMinutes"] is None:
                    continue
                if first["regCloseMinutes"] is None:
                    continue
                if second["startMinutes"] < first["regCloseMinutes"]:
                    verdict = "cannot be played in sequence"
                    detail = (
                        f"{second['eventLabel']} starts at {second['time']}, before "
                        f"{first['eventLabel']} registration closes at {first['lateRegistrationCloses']}"
                    )
                elif second["startMinutes"] <= first["regCloseMinutes"] + 120:
                    verdict = "uncertain - starts inside the first event's possible playing window"
                    detail = (
                        f"{second['eventLabel']} starts at {second['time']}, within two hours of "
                        f"{first['eventLabel']} registration closing at {first['lateRegistrationCloses']}"
                    )
                else:
                    continue
                pairs.append(
                    {
                        "first": first["eventLabel"],
                        "firstTime": first["time"],
                        "firstRegClose": first["lateRegistrationCloses"],
                        "second": second["eventLabel"],
                        "secondTime": second["time"],
                        "verdict": verdict,
                        "detail": detail,
                    }
                )
        days.append(
            {
                "date": day,
                "dateLabel": rows[0]["dateLabel"] if rows else day,
                "weekday": weekday(day),
                "events": rows,
                "primary": primary,
                "primaryNeedsExtraSpend": primary_needs_extra_spend,
                "fallback": fallback,
                "fallbackMayConflict": fallback_conflict,
                "spendEvents": [e for e in rows if e["bucket"] == "spend"],
                "overlaps": pairs,
                "earliestStart": rows[0]["time"] if rows else "",
                "eligibleCount": len(eligible),
                "firstEvent": rows[0] if rows else None,
            }
        )

    dataset = {
        "asOf": venetian["checked"],
        "generatedBy": "scripts/build_site.py",
        "policy": {
            "strictRule": "An event counts as one entry only when the official structure sheet for that event states one entry and contains no re-entry, rebuy, add-on or paid chip boost provision. A sheet that is silent is reported as silent, not as confirmed.",
            "ratioRule": "Guaranteed pool divided by entry fee describes what the venue promises to publish. It is never a forecast of a payout. A bounty guarantee includes bounty money, so the cash-pool-to-buy-in ratio is shown next to it.",
            "costRule": "True nightly cost = the published nightly rate including the resort fee, plus 13.38% Clark County room tax. It is an arithmetic restatement of published figures, not a quote, and the booking pages say the published rate excludes taxes.",
            "walkRule": "Walking times are third-party estimates unless a row says otherwise. No venue publishes walking times to another venue.",
            "rankingRule": "Tournaments are ranked only after the fee split and the guarantee have both been confirmed on an official structure sheet. Rows with a blank fee or a blank guarantee are not ranked.",
        },
        "sampleStay": hotels["sampleStay"],
        "taxModel": hotels["taxModel"],
        "venues": venues,
        "events": events,
        "hotels": hotels["hotels"],
        "routes": routes["routes"],
        "walkLimitMinutes": routes.get("walkLimitMinutes", 30),
        "sources": sources["sources"],
        "flags": flags["flags"],
        "days": days,
    }
    return dataset


# ------------------------------------------------------------- page shell ----
def page(active, title, body, base="", scripts=""):
    nav_links = "".join(
        f'<a href="{base}{href}" class="{"active" if href == active else ""}">'
        f'<span class="ico">{icon}</span>{esc(label)}</a>'
        for href, label, icon in NAV
    )
    mobile_links = "".join(
        f'<a href="{base}{href}" class="{"active" if href == active else ""}">{esc(label)}</a>'
        for href, label, _ in NAV
    )
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="{esc(title)} - official-source Las Vegas poker trip planner">
<title>{esc(title)} · Vegas Poker Planner</title>
<link rel="stylesheet" href="{base}assets/site.css">
</head>
<body>
<header class="topbar">
  <a class="brand" href="{base}index.html"><span class="brand-mark">♠</span><span>Vegas Poker Planner</span></a>
  <form class="global-search" data-global-search role="search" onsubmit="return false">
    <input type="search" placeholder="Search every table on this page…" aria-label="Search all tables on this page" data-search-input>
  </form>
  <span class="top-tag">Official-source snapshot · checked <span data-asof>2026-11-16</span></span>
</header>
<nav class="mobile-nav" data-mobile-nav>{mobile_links}</nav>
<div class="layout">
  <aside class="sidebar">
    <div class="side-label">Plan your trip</div>
    <nav class="nav">{nav_links}</nav>
    <div class="side-note"><strong>Evidence first.</strong> Every row links the official page it came from. A blank means the value could not be read from an official source and is listed on the Flagged for review page.</div>
  </aside>
  <main class="main">
{body}
    <div class="footer">Built from official venue pages on <span data-asof>2026-11-16</span>. A guarantee is what a venue publishes, not a forecast of a payout. Verify prices, terms and schedules with the room before you pay. <a href="{base}flagged.html">Limitations and flagged items</a>.</div>
  </main>
</div>
<script src="{base}assets/app.js"></script>
{scripts}
</body>
</html>
"""


def source_links(links, extra=""):
    out = []
    for link in links:
        badge = "third-party" if link["kind"] == "third-party" else "official"
        out.append(
            f'<a href="{esc(link["url"])}" target="_blank" rel="noopener">{esc(link["name"])} '
            f'<span class="badge {badge}">{badge}</span></a>'
        )
    if extra:
        out.append(extra)
    return '<span class="links">' + "<br>".join(out) + "</span>"


def source_links_block(links):
    return '<ul class="linklist">' + "".join(
        f'<li><a href="{esc(l["url"])}" target="_blank" rel="noopener">{esc(l["name"])}</a> '
        f'<span class="badge {"third-party" if l["kind"] == "third-party" else "official"}">'
        f'{esc(l["kind"])}</span></li>'
        for l in links
    ) + "</ul>"


def empty_note(text):
    return f'<p class="muted">{esc(text)}</p>'


# --------------------------------------------------------- shared fragments --
def format_label(event) -> str:
    """A short label for the format, kept separate from the entry rule.

    A bounty guarantee and a freezeout guarantee are not comparable, and a multi-flight
    event is a different shape from a one-day one, so the format is labelled on its own.
    """
    labels = []
    kind = (event.get("format") or "").lower()
    if "bounty" in kind:
        labels.append("bounty")
    if "pkO" in kind or "pko" in kind:
        labels.append("progressive knock-out")
    if "multi-flight" in kind:
        labels.append("multi-flight")
    if "satellite" in kind:
        labels.append("seat prize")
    if "omaha" in kind:
        labels.append("omaha")
    if "big o" in kind:
        labels.append("big O")
    if event.get("guaranteeIncludesBounties"):
        labels.append("guarantee includes bounties")
    if event.get("handed"):
        labels.append(event["handed"])
    if not labels:
        labels.append("freezeout")
    return "<br>".join(
        f'<span class="tag">{esc(label)}</span>' for label in labels
    )


def entry_terms_detail(event) -> str:
    """The four separate entry questions, with the sheet's own words."""
    rows = [
        ("One entry", event.get("singleEntry", "")),
        ("Re-entry", event.get("reEntry", "")),
        ("Add-on", event.get("addOn", "")),
        ("Rebuy", event.get("rebuy", "")),
        ("Paid chip boost", event.get("paidChipBoost", "")),
    ]
    items = "".join(
        f"<dt>{esc(name)}</dt><dd>{esc(value)}</dd>" for name, value in rows
    )
    fee = event.get("feeExcerpt", "")
    excerpt = event.get("ruleExcerpt", "")
    basis = event.get("entryRuleBasis", "")
    checked = event.get("lastChecked", "")
    return (
        '<details class="entry-detail"><summary>Entry terms and the sheet\'s words</summary>'
        f'<dl class="entry-fields">{items}</dl>'
        + (f'<p class="muted small"><strong>Fee split:</strong> {esc(fee)}</p>' if fee else "")
        + (f'<p class="muted small"><strong>Other rules:</strong> {esc(excerpt)}</p>' if excerpt else "")
        + (f'<p class="muted small"><strong>Why this label:</strong> {esc(basis)}</p>' if basis else "")
        + f'<p class="muted small">Structure sheet read on {esc(checked)}.</p>'
        + "</details>"
    )


def tournament_row(event):
    """One row of the tournament table, with the data attributes the filters use."""
    verdict = event.get("entryRule", "")
    guarantee = event.get("guarantee")
    if guarantee:
        guarantee_text = usd(guarantee)
        if event.get("guaranteeIncludesBounties"):
            guarantee_text += " <span class=\"muted\">(incl. bounties)</span>"
    else:
        guarantee_text = '<span class="muted">not published</span>'

    ratio_text = ""
    if event.get("cashRatio"):
        ratio_text = f"{event['cashRatio']}×"
    gtd_ratio = f"{event['gtdRatio']}×" if event.get("gtdRatio") else ""

    fee_text = ""
    if event.get("cashPoolPerEntry") and event.get("rakeAndStaff"):
        fee_text = (
            f"{usd(event['cashPoolPerEntry'])} to the pool, "
            f"{usd(event['rakeAndStaff'])} house fee and staff"
        )
    else:
        fee_text = '<span class="muted">not published</span>'

    entries = [
        esc(event["dateLabel"]) if event.get("dateLabel") else '<span class="muted">recurring</span>',
        esc(event.get("time", "")),
        esc(event.get("name", "")),
        format_label(event),
        usd(event.get("buyIn")) if event.get("buyIn") else '<span class="muted">not published</span>',
        guarantee_text,
        fee_text,
        ratio_text or '<span class="muted">n/a</span>',
        gtd_ratio or '<span class="muted">n/a</span>',
        esc(verdict),
    ]
    links = source_links(event.get("sourceLinks", []))
    if event.get("sheetUrl"):
        links += (
            f'<br><a href="{esc(event["sheetUrl"])}" target="_blank" rel="noopener">'
            f'Structure sheet <span class="badge official">official</span></a>'
        )
    if event.get("scheduleUrl"):
        links += (
            f'<br><a href="{esc(event["scheduleUrl"])}" target="_blank" rel="noopener">'
            f'Event schedule <span class="badge official">official</span></a>'
        )
    entries.append(links + entry_terms_detail(event))

    attrs = (
        f'data-row="tournament" '
        f'data-date="{esc(event.get("dateISO", ""))}" '
        f'data-venue="{esc(event.get("venueId", ""))}" '
        f'data-bucket="{esc(event.get("bucket", ""))}" '
        f'data-buyin="{esc(event.get("buyIn", ""))}" '
        f'data-guarantee="{esc(event.get("guarantee", ""))}" '
        f'data-cash-ratio="{esc(event.get("cashRatio") if event.get("cashRatio") is not None else "")}" '
        f'data-gtd-ratio="{esc(event.get("gtdRatio") if event.get("gtdRatio") is not None else "")}" '
        f'data-start="{esc(event.get("startMinutes") if event.get("startMinutes") is not None else "")}"'
    )
    return f"<tr {attrs}>" + "".join(f"<td>{c}</td>" for c in entries) + "</tr>"


TOURNAMENT_HEADERS = [
    "Date",
    "Start",
    "Tournament",
    "Format",
    "Buy-in",
    "Guaranteed pool",
    "Fee split",
    "Cash pool ÷ fee",
    "Guarantee ÷ fee",
    "Entry rule",
    "Official sources",
]


def filter_bar(dataset, show_date=True, show_venue=True, show_strict=True):
    dates = sorted({e["dateISO"] for e in dataset["events"] if e.get("dateISO")})
    venues = dataset["venues"]
    parts = ['<div class="filter-bar">']
    if show_date:
        parts.append(
            '<label class="filter">Date <select data-filter="date">'
            '<option value="">All dates</option>'
            + "".join(
                f'<option value="{esc(d)}">{esc(d)} ({esc(weekday(d))})</option>' for d in dates
            )
            + "</select></label>"
        )
    if show_venue:
        parts.append(
            '<label class="filter">Venue <select data-filter="venue">'
            '<option value="">All venues</option>'
            + "".join(
                f'<option value="{esc(v["id"])}">{esc(v["name"])}</option>' for v in venues
            )
            + "</select></label>"
        )
    if show_strict:
        parts.append(
            '<label class="filter checkbox">'
            '<input type="checkbox" data-filter="strict-only"> '
            "One entry confirmed by the structure sheet only"
            "</label>"
        )
    parts.append(
        '<label class="filter">Bucket <select data-filter="bucket">'
        '<option value="">All entry statuses</option>'
        + "".join(
            f'<option value="{esc(k)}">{esc(BUCKET_TITLE[k])}</option>'
            for k in ["strict", "unverified", "multi", "spend", "review"]
        )
        + "</select></label>"
    )
    parts.append(
        '<label class="filter">Sort <select data-filter="sort">'
        '<option value="date">By date</option>'
        '<option value="buyin">By buy-in (low to high)</option>'
        '<option value="guarantee">By guarantee (high to low)</option>'
        '<option value="ratio">By cash pool ÷ fee (high to low)</option>'
        "</select></label>"
    )
    parts.append(
        '<button type="button" class="btn" data-reset-filters>Reset filters</button>'
    )
    parts.append('</div>')
    parts.append('<p class="result-count" data-result-count></p>')
    return "".join(parts)


def tournament_table(dataset, events):
    rows = "".join(tournament_row(e) for e in events)
    return (
        '<div class="table-wrap"><table class="data-table" data-table="tournaments">'
        "<thead><tr>"
        + "".join(f"<th>{esc(h)}</th>" for h in TOURNAMENT_HEADERS)
        + "</tr></thead><tbody>"
        + rows
        + "</tbody></table></div>"
    )


# ------------------------------------------------------------- the pages ----
def build_index(dataset):
    days = dataset["days"]
    events = dataset["events"]
    hotels = dataset["hotels"]
    dated = [e for e in events if e.get("dateISO")]
    strict = [e for e in dated if e["bucket"] == "strict"]
    unverified = [e for e in dated if e["bucket"] == "unverified"]
    spend = [e for e in dated if e["bucket"] == "spend"]
    multi = [e for e in dated if e["bucket"] == "multi"]
    with_rate = [h for h in hotels if h.get("hasRate")]
    cheapest = sorted(with_rate, key=lambda h: h["trueNightly"])[:3]
    earliest = min(
        (e for e in dated if e.get("startMinutes") is not None),
        key=lambda e: e["startMinutes"],
    )
    stay = dataset["sampleStay"]

    body = f"""
<h1>Plan a Las Vegas poker trip from official sources only</h1>
<p class="lede">Every tournament, fee, guarantee, hotel rate and walking time on this site
comes from a venue's own page or an official PDF. Each row links the source it came from.
Where a value could not be read from an official source, the cell is blank and the item is
published on the <a href="flagged.html">Flagged for review</a> page instead of being guessed.</p>

<div class="stat-row">
  <div class="stat"><span class="stat-num">{len(dated)}</span><span class="stat-label">dated tournament rows<br>from official schedules</span></div>
  <div class="stat"><span class="stat-num">{len(strict)}</span><span class="stat-label">rows with one entry<br>confirmed by a structure sheet</span></div>
  <div class="stat"><span class="stat-num">{len(unverified)}</span><span class="stat-label">rows where the sheet is<br>silent about re-entry</span></div>
  <div class="stat"><span class="stat-num">{len(dataset["venues"])}</span><span class="stat-label">poker rooms<br>on the Strip</span></div>
  <div class="stat"><span class="stat-num">{len(with_rate)}</span><span class="stat-label">hotels with a dated<br>official rate</span></div>
</div>

<div class="panel-grid">
  <section class="panel">
    <h2>The short version</h2>
    <ol class="finding-list">
      <li><strong>The Venetian is the anchor.</strong> Its DeepStack Extravaganza IV series
        publishes 94 dated tournament rows with a structure sheet for every one of them, which is
        more official detail than any other room on the Strip publishes.</li>
      <li><strong>No sheet in this dataset proves a single total entry.</strong> Every structure
        sheet was read in full. {len(strict)} rows are confirmed one-entry; {len(unverified)} more
        come from sheets that simply do not mention re-entry, a rebuy, an add-on or a paid chip
        boost. Silence is reported as silence, not as confirmation.</li>
      <li><strong>{len(spend)} rows are confirmed extra-spend formats</strong> and
        {len(multi)} more are multi-flight, where a player eliminated in one flight may buy into
        another. Those are kept in their own sections rather than mixed in.</li>
      <li><strong>Hotels are ranked on true nightly cost</strong> &mdash; published rate plus the
        resort fee plus {dataset["taxModel"]["roomTaxRate"]*100:.2f}% room tax &mdash; not on the
        headline rate. Only {len(with_rate)} of {len(hotels)} hotels have a date-specific rate
        that could be read from an official page.</li>
      <li><strong>The earliest published start is {esc(earliest["time"])}</strong>
        ({esc(earliest["dateLabel"])}). No venue publishes an 8 a.m. start, so no all-day
        8 a.m. schedule is promised here.</li>
    </ol>
  </section>

  <section class="panel">
    <h2>Where to start</h2>
    <ul class="link-cards">
      <li><a href="tournaments.html"><strong>Tournaments</strong></a>
        <span>All {len(events)} rows with buy-in, guarantee, fee split, entry rule and source links.
        Filter by date, venue or entry status.</span></li>
      <li><a href="schedule.html"><strong>Day plan</strong></a>
        <span>What each day of the Venetian series looks like, with the primary and fallback
        event and the pairs that provably overlap.</span></li>
      <li><a href="hotels.html"><strong>Hotels</strong></a>
        <span>Exact-date rates, fees, tax, parking, cancellation deadlines and walking times.</span></li>
      <li><a href="cost.html"><strong>Trip cost</strong></a>
        <span>Work out what a stay plus a tournament schedule actually costs.</span></li>
      <li><a href="venues/index.html"><strong>Venues</strong></a>
        <span>One page per poker room with its own coverage and open questions.</span></li>
      <li><a href="questions.html"><strong>Open questions</strong></a>
        <span>The decisions still outstanding before money is committed, with what to ask and
        who to ask.</span></li>
    </ul>
  </section>
</div>

<section class="panel">
  <h2>Cheapest true nightly cost, like for like</h2>
  <p class="muted">Sample stay {esc(stay["label"])}. True nightly cost is the published rate with
  the resort fee, plus {dataset["taxModel"]["roomTaxRate"]*100:.2f}% Clark County room tax.
  It is a restatement of published numbers, not a quote.</p>
  {hotel_rank_table(dataset, cheapest)}
</section>

<section class="panel">
  <h2>How this site decides what is verified</h2>
  <div class="rule-grid">
    <div class="rule"><h3>One entry</h3><p>{esc(dataset["policy"]["strictRule"])}</p></div>
    <div class="rule"><h3>Guarantee ratio</h3><p>{esc(dataset["policy"]["ratioRule"])}</p></div>
    <div class="rule"><h3>True cost</h3><p>{esc(dataset["policy"]["costRule"])}</p></div>
    <div class="rule"><h3>Walking times</h3><p>{esc(dataset["policy"]["walkRule"])}</p></div>
    <div class="rule"><h3>Ranking</h3><p>{esc(dataset["policy"]["rankingRule"])}</p></div>
    <div class="rule"><h3>Sample dates</h3><p>{esc(stay["note"])}</p></div>
  </div>
</section>
"""
    return page("index.html", "Overview", body)


def hotel_rank_table(dataset, hotels):
    rows = []
    for hotel in hotels:
        latest = hotel.get("latestRate") or {}
        routes = [
            r for r in dataset["routes"] if r["fromId"] == hotel["id"] and r["toVenueId"] == "venetian"
        ]
        walk = routes[0] if routes else None
        walk_text = (
            f"{esc(walk['minutes'])} min"
            if walk and walk.get("minutes")
            else '<span class="muted">not measured</span>'
        )
        rows.append(
            f'<tr data-venue="{esc(hotel["id"])}">'
            f"<td>{esc(hotel['name'])}</td>"
            f"<td>{esc(hotel.get('venue',''))}</td>"
            f"<td>{usd(latest.get('nightlyWithFee'))}</td>"
            f"<td>{usd(hotel.get('feeNightly'))}</td>"
            f"<td>{usd(hotel.get('trueNightly'), 2)}</td>"
            f"<td>{esc(latest.get('roomType',''))}</td>"
            f"<td>{esc(latest.get('checked',''))}</td>"
            f"<td>{walk_text}</td>"
            f"<td>{source_links([{'id': 'x', 'name': 'Official booking page', 'url': hotel.get('officialUrl',''), 'kind': 'official'}])}</td>"
            "</tr>"
        )
    return (
        '<div class="table-wrap"><table class="data-table"><thead><tr>'
        "<th>Hotel</th><th>Poker room</th><th>Nightly with fee</th><th>Resort fee</th>"
        "<th>True nightly</th><th>Room type</th><th>Checked</th><th>Walk to the Venetian</th>"
        "<th>Official source</th></tr></thead><tbody>"
        + "".join(rows)
        + "</tbody></table></div>"
    )


def build_tournaments(dataset):
    events = dataset["events"]
    dated = [e for e in events if e.get("dateISO")]
    other = [e for e in events if not e.get("dateISO")]
    strict_count = sum(1 for e in events if e["bucket"] == "strict")
    if strict_count:
        strict_notice = ""
    else:
        strict_notice = """
<div class="notice">
  <strong>No event in this dataset is confirmed single-entry.</strong> Every official structure
  sheet that publishes an entry rule either sells more entries or says nothing about them, so
  the strict filter returns no rows. That is the honest result of reading the sheets rather
  than assuming that a silent sheet means a single entry.
</div>"""
    body = f"""
<h1>Tournaments</h1>
<p class="lede">{len(dated)} dated rows from official tournament schedules and
{len(other)} recurring rows from the other Strip rooms. Every row carries its own official
source link. The entry-rule column says what the structure sheet actually states &mdash;
where a sheet is silent, the row says so instead of claiming a single entry.</p>
{filter_bar(dataset)}
{strict_notice}
<div class="table-wrap"><table class="data-table" data-table="tournaments">
<thead><tr>{"".join(f"<th>{esc(h)}</th>" for h in TOURNAMENT_HEADERS)}</tr></thead>
<tbody>{"".join(tournament_row(e) for e in dated)}</tbody></table></div>

<h2>Recurring official slates from the other rooms</h2>
<p class="muted">These rooms publish a repeating slate rather than a dated calendar, so the rows
below are templates. Each one keeps the official page it was read from, and each one states
the entry rule that page prints.</p>
<div class="table-wrap"><table class="data-table" data-table="tournaments">
<thead><tr>{"".join(f"<th>{esc(h)}</th>" for h in TOURNAMENT_HEADERS)}</tr></thead>
<tbody>{"".join(tournament_row(e) for e in other)}</tbody></table></div>

<section class="panel">
  <h2>What the entry-rule column means</h2>
  <dl class="def-list">
    <dt>One entry, confirmed by the structure sheet</dt>
    <dd>The sheet states one entry and contains no re-entry, rebuy, add-on or paid chip boost
      provision.</dd>
    <dt>Single entry not stated on the sheet</dt>
    <dd>The sheet was read in full and does not mention re-entry, a rebuy, an add-on or a paid
      chip boost. That is not proof of a single entry, so the row is not called confirmed.
      Ask the room if it matters.</dd>
    <dt>Multi-flight: one entry per flight</dt>
    <dd>The sheet names separate starting flights and only bars players who bag chips for Day 2
      from entering a later flight. A player eliminated in one flight may buy into another.</dd>
    <dt>Extra-spend format</dt>
    <dd>Either the sheet sells further buy-ins outright, or the prize is a seat, so every extra
      buy-in is another chance at the same prize.</dd>
    <dt>Team format</dt>
    <dd>One buy-in covers more than one player, so the per-player cost is not the buy-in.</dd>
  </dl>
</section>
"""
    return page("tournaments.html", "Tournaments", body)


def build_schedule(dataset):
    days = dataset["days"]
    blocks = []
    for day in days:
        rows = "".join(
            f'<tr data-bucket="{esc(e["bucket"])}"><td>{esc(e["time"])}</td>'
            f'<td>{esc(e["eventLabel"])}</td>'
            f'<td>{esc(e["name"])}</td>'
            f'<td>{usd(e.get("buyIn"))}</td>'
            f'<td>{esc(e.get("lateRegistrationCloses") or "—")}</td>'
            f'<td>{esc(e.get("entryRule",""))}</td></tr>'
            for e in day["events"]
        )
        primary = day.get("primary")
        fallback = day.get("fallback")
        primary_text = (
            f'<strong>{esc(primary["eventLabel"])}</strong> at {esc(primary["time"])} '
            f'({esc(primary["name"])})'
            if primary
            else '<span class="muted">no eligible event</span>'
        )
        if day.get("primaryNeedsExtraSpend"):
            primary_text += (
                ' <span class="muted">This event needs a second entry to be worth playing, '
                "so the day has no single-entry option.</span>"
            )
        fallback_text = (
            f'<strong>{esc(fallback["eventLabel"])}</strong> at {esc(fallback["time"])} '
            f'({esc(fallback["name"])})'
            if fallback
            else '<span class="muted">no second event that day</span>'
        )
        if day.get("fallbackMayConflict"):
            fallback_text += (
                ' <span class="muted">This one may clash with the primary: it starts before '
                "the primary's registration closes.</span>"
            )
        if day["overlaps"]:
            overlap_rows = "".join(
                f'<tr><td>{esc(o["first"])} <span class="muted">{esc(o["firstTime"])}</span></td>'
                f'<td>{esc(o["second"])} <span class="muted">{esc(o["secondTime"])}</span></td>'
                f'<td class="verdict-{esc("bad" if o["verdict"].startswith("cannot") else "warn")}">'
                f"{esc(o['verdict'])}</td><td>{esc(o['detail'])}</td></tr>"
                for o in day["overlaps"]
            )
            overlap_html = (
                '<div class="table-wrap"><table class="data-table compact"><thead><tr>'
                "<th>First event</th><th>Second event</th><th>Verdict</th><th>Why</th>"
                f"</tr></thead><tbody>{overlap_rows}</tbody></table></div>"
            )
        else:
            overlap_html = '<p class="muted">No pair of events on this day provably overlaps.</p>'

        blocks.append(
            f"""
<article class="day-card" id="day-{esc(day["date"])}">
  <h3><span class="day-weekday">{esc(day["weekday"])}</span>
    <span class="day-date">{esc(day["dateLabel"])}</span>
    <span class="day-count">{day["eligibleCount"]} eligible</span></h3>
  <p class="day-plan-line"><strong>Primary:</strong> {primary_text}
     · <strong>Fallback:</strong> {fallback_text}</p>
  <div class="table-wrap"><table class="data-table compact"><thead><tr>
    <th>Start</th><th>Event #</th><th>Tournament</th><th>Buy-in</th>
    <th>Registration closes</th><th>Entry rule</th></tr></thead>
    <tbody>{rows}</tbody></table></div>
  <details><summary>Overlap check for this day</summary>
    <p class="muted">No venue publishes a finish time. Registration close is used as a hard
    lower bound on how long an event can run, so a pair is only called impossible when the
    second event starts before the first one's registration closes.</p>
    {overlap_html}
  </details>
</article>"""
        )

    earliest = min(
        (e["startMinutes"] for e in dataset["events"] if e.get("startMinutes") is not None)
    )
    body = f"""
<h1>Day plan</h1>
<p class="lede">A realistic day at the Venetian, built only from published start times and
registration-close times. The earliest published start in the whole dataset is
{fmt_time(earliest)}, so the first entry of each day starts when the room opens, not before.
Each day names a primary event and a fallback, and shows which pairs provably overlap.</p>
<div class="notice">
  <strong>There is no verified 8 a.m. start.</strong> The earliest published start across all
  official sources is {fmt_time(earliest)}. A full-day 8 a.m. plan cannot be promised from
  official material, so this plan starts when the room does.
</div>
{filter_bar(dataset, show_venue=False, show_strict=False)}
<div class="day-list">{"".join(blocks)}</div>
"""
    return page("schedule.html", "Day plan", body)


def build_hotels(dataset):
    stay = dataset["sampleStay"]
    tax = dataset["taxModel"]
    rows = []
    for hotel in dataset["hotels"]:
        latest = hotel.get("latestRate") or {}
        fee = hotel.get("resortFee", {})
        parking = hotel.get("parking", {})
        cancel = hotel.get("cancellation", {})
        quality = hotel.get("quality", {})
        link = {
            "id": hotel.get("officialUrl", ""),
            "name": "Official property page",
            "url": hotel.get("officialUrl", ""),
            "kind": "official",
        }
        fee_link = {
            "id": "fee",
            "name": "Fee and terms source",
            "url": hotel.get("officialUrl", ""),
            "kind": "official",
        }
        if hotel.get("hasRate"):
            rate_text = usd(latest.get("nightlyWithFee"))
            true_text = usd(hotel.get("trueNightly"), 2)
            stay_text = usd(hotel.get("trueStay"), 2)
            pretax_text = usd(hotel.get("preTaxStay"), 2)
            average_text = usd(hotel.get("nightlyAverage"), 2)
        else:
            rate_text = '<span class="muted">not published</span>'
            true_text = '<span class="muted">blank</span>'
            stay_text = '<span class="muted">blank</span>'
            pretax_text = '<span class="muted">blank</span>'
            average_text = '<span class="muted">blank</span>'
        rows.append(
            f'<tr data-hotel="{esc(hotel["id"])}">'
            f"<td><strong>{esc(hotel['name'])}</strong><br>"
            f'<span class="muted">{esc(hotel.get("venue",""))}</span></td>'
            f"<td>{rate_text}<br><span class='muted'>average {average_text} across "
            f"{hotel.get('observationCount', 0)} observation(s)</span>"
            + (
                f"<span class='muted'>published range {usd(hotel['rateRange']['lowest'])} "
                f"to {usd(hotel['rateRange']['highest'])}</span>"
                if hotel.get("rateRange")
                else ""
            )
            + "</td>"
            f"<td>{esc(fee.get('text',''))}</td>"
            f"<td>{esc(hotel.get('tax',{}).get('text',''))}</td>"
            f"<td>{true_text}</td>"
            f"<td>{pretax_text}<br><span class='muted'>{stay_text} with tax</span></td>"
            f"<td><span class='muted'>{esc(hotel.get('checkoutTotalNote',''))}</span></td>"
            f"<td>{esc(parking.get('text',''))}</td>"
            f"<td>{esc(cancel.get('text',''))}<br>"
            f"<span class='muted'>{esc(cancel.get('deadline','') or 'no deadline printed')}</span></td>"
            f"<td>{esc(quality.get('value',''))}<br>"
            f"<span class='muted'>{esc(quality.get('proxy',''))}</span></td>"
            f"<td>{esc(latest.get('checked',''))}<br>"
            f"<span class='muted'>{esc(latest.get('note',''))}</span>"
            f"{rate_log_detail(hotel)}</td>"
            f"<td>{source_links([link])}</td>"
            "</tr>"
        )
    headers = [
        "Hotel and poker room", "Nightly with fee", "Resort fee", "Tax", "True nightly",
        "Stay total", "Checkout total", "Parking", "Cancellation", "Quality", "Rate log",
        "Official source",
    ]
    body = f"""
<h1>Hotels</h1>
<p class="lede">Sample stay <strong>{esc(stay["label"])}</strong>. Rates are stored as dated
observations, not as one price: the same property can print several prices on the same day and
the price moves with demand. True nightly cost adds {tax["roomTaxRate"]*100:.2f}% Clark County
room tax to the published rate including the resort fee. A blank total means a component of
the calculation could not be read from an official page.</p>
{filter_bar(dataset, show_date=False, show_venue=False, show_strict=False)}
<div class="table-wrap"><table class="data-table" data-table="hotels"><thead><tr>
{"".join(f"<th>{esc(h)}</th>" for h in headers)}</tr></thead>
<tbody>{"".join(rows)}</tbody></table></div>

<section class="panel">
  <h2>How the totals are built</h2>
  <ul class="bullets">
    <li><strong>Room tax.</strong> {esc(tax["roomTaxBasis"])}</li>
    <li><strong>What the tax applies to.</strong> {esc(tax["appliesTo"])}</li>
    <li><strong>Method.</strong> {esc(tax["note"])}</li>
    <li><strong>Sample dates.</strong> {esc(stay["note"])}</li>
  </ul>
</section>

<section class="panel">
  <h2>Check the current rate for your own dates</h2>
  <p class="lede">The rate table above is a dated log, not a live quote. To price the same
  stay for different dates, run the lookup tool against the property's own booking engine and
  append the result to the log:</p>
  <pre class="code-block"><code>python3 scripts/check_hotel_rates.py --hotel horseshoe \\
    --arrival 2026-12-10 --departure 2026-12-14 --write</code></pre>
  <p class="muted">Known property ids: <code>horseshoe</code>, <code>caesars-palace</code>,
  <code>paris</code>, <code>venetian</code>, <code>wynn</code>, <code>bellagio</code>.
  Run it with <code>--list</code> for the full list and without <code>--write</code> to see
  the result without changing the log.</p>
  <p class="muted">The tool never invents a rate. If the booking engine will not return a price
  for the requested dates, it records nothing and says why. Each observation it writes keeps
  the URL, the retrieval timestamp, the room type and the occupancy it was read for.</p>
</section>

<section class="panel">
  <h2>Walking routes from these hotels to the tournament rooms</h2>
  <p class="muted">No venue publishes a walking time to another venue, so every time below is a
  third-party estimate and is labelled as one. A Google Maps walking link is included so each
  one can be checked under real conditions before you rely on it.</p>
  {route_table(dataset)}
</section>
"""
    return page("hotels.html", "Hotels", body)


def rate_log_detail(hotel) -> str:
    """The dated rate log for one property, newest first."""
    entries = []
    for observation in sorted(
        hotel.get("rateLog", []), key=lambda r: (r["checked"], r["nightlyWithFee"])
    ):
        entries.append(
            f"<tr><td>{esc(observation.get('checked',''))}</td>"
            f"<td>{esc(observation.get('arrival',''))} to {esc(observation.get('departure',''))}</td>"
            f"<td>{esc(observation.get('nights',''))}</td>"
            f"<td>{esc(observation.get('occupancy',''))}</td>"
            f"<td>{esc(observation.get('roomType',''))}</td>"
            f"<td>{usd(observation.get('nightlyRate'))}</td>"
            f"<td>{usd(observation.get('resortFeeIncluded'))}</td>"
            f"<td>{usd(observation.get('nightlyWithFee'))}</td>"
            f"<td>{usd(observation.get('trueNightly'), 2)}</td>"
            f"<td>{esc(observation.get('sourceId',''))}</td></tr>"
        )
    if not entries:
        return ""
    return (
        '<details class="entry-detail"><summary>Rate log '
        f'({len(entries)} dated observation(s))</summary>'
        '<div class="table-wrap"><table class="data-table compact"><thead><tr>'
        "<th>Checked</th><th>Arrival</th><th>Nights</th><th>Occupancy</th><th>Room type</th>"
        "<th>Room rate</th><th>Resort fee</th><th>Nightly with fee</th><th>True nightly</th>"
        "<th>Source</th></tr></thead><tbody>"
        + "".join(entries)
        + "</tbody></table></div></details>"
    )


def route_table(dataset):
    rows = []
    for route in dataset["routes"]:
        minutes = route.get("minutes")
        time_text = f"{minutes} min" if minutes else '<span class="muted">not measured</span>'
        within = (
            '<span class="verdict-ok">within the 30-minute limit</span>'
            if route.get("withinLimit")
            else (
                '<span class="verdict-warn">over the 30-minute limit</span>'
                if minutes
                else '<span class="muted">unknown</span>'
            )
        )
        link = ""
        if route.get("sourceUrl"):
            link = source_links(
                [
                    {
                        "id": "route",
                        "name": "Route estimate",
                        "url": route["sourceUrl"],
                        "kind": "third-party",
                    }
                ]
            )
        rows.append(
            f"<tr><td>{esc(route['fromName'])}</td><td>{esc(route['toName'])}</td>"
            f"<td>{time_text}</td><td>{esc(route.get('distance',''))}</td>"
            f"<td>{esc(route.get('type',''))}</td><td>{within}</td>"
            f'<td><a href="{esc(route["mapsUrl"])}" target="_blank" rel="noopener">Google Maps walk</a>'
            f'<br><a href="{esc(route["appleMapsUrl"])}" target="_blank" rel="noopener">Apple Maps walk</a></td>'
            f"<td>{link}</td></tr>"
        )
    return (
        '<div class="table-wrap"><table class="data-table"><thead><tr>'
        "<th>From</th><th>To</th><th>Walk</th><th>Distance</th><th>Type</th>"
        f"<th>30-minute rule</th><th>Check it yourself</th><th>Source</th></tr></thead>"
        f"<tbody>{''.join(rows)}</tbody></table></div>"
    )


def build_cost(dataset):
    stay = dataset["sampleStay"]
    tax = dataset["taxModel"]
    hotels = [h for h in dataset["hotels"] if h.get("hasRate")]
    events = [e for e in dataset["events"] if e.get("dateISO") and e.get("buyIn")]
    venue = [v for v in dataset["venues"] if v["id"] == "venetian"][0]

    buyin_options = sorted({e["buyIn"] for e in events})
    event_options = "".join(
        f'<option value="{esc(e["id"])}" data-buyin="{esc(e.get("buyIn"))}" '
        f'data-date="{esc(e.get("dateISO"))}">{esc(e["dateLabel"])} {esc(e["time"])} '
        f'{esc(e["name"])}</option>'
        for e in events
    )
    hotel_options = "".join(
        f'<option value="{esc(h["id"])}" data-nightly="{esc(h.get("trueNightly"))}" '
        f'data-nights="{esc(stay["nights"])}">{esc(h["name"])}</option>'
        for h in hotels
    )
    body = f"""
<h1>Trip cost</h1>
<p class="lede">A working estimate for what a stay plus a tournament schedule costs. Every input
comes from the official data on this site: the buy-in from the official structure sheet, the
nightly rate from the official booking page, and the tax rate from the official hotel terms.
Change the dates, the hotel and the number of entries and the totals update. The result is an
arithmetic estimate, not a quote.</p>

<div class="calculator" data-calculator>
  <div class="calc-cols">
    <div class="calc-field">
      <label for="calc-hotel">Hotel</label>
      <select id="calc-hotel" data-calc="hotel">
        <option value="">No hotel</option>
        {hotel_options}
      </select>
      <p class="muted small" data-calc-hotel-note></p>
    </div>
    <div class="calc-field">
      <label for="calc-arrival">Arrival</label>
      <input type="date" id="calc-arrival" data-calc="arrival" value="{esc(stay["arrival"])}">
    </div>
    <div class="calc-field">
      <label for="calc-departure">Departure</label>
      <input type="date" id="calc-departure" data-calc="departure" value="{esc(stay["departure"])}">
    </div>
    <div class="calc-field">
      <label for="calc-nights">Nights</label>
      <input type="number" id="calc-nights" data-calc="nights" min="0" value="{esc(stay["nights"])}">
    </div>
    <div class="calc-field">
      <label for="calc-entries">Tournament entries</label>
      <input type="number" id="calc-entries" data-calc="entries" min="0" value="1">
      <p class="muted small">How many buy-ins you plan to buy in total.</p>
    </div>
    <div class="calc-field">
      <label for="calc-event">Add a tournament to the entries</label>
      <select id="calc-event" data-calc="event">
        <option value="">No tournament selected</option>
        {event_options}
      </select>
    </div>
    <div class="calc-field">
      <label for="calc-parallel">Also playing in parallel (extra spend)</label>
      <input type="number" id="calc-parallel" data-calc="parallel" min="0" value="0">
      <p class="muted small">Extra entries you expect to make because of a multi-flight format
      or a seat-prize satellite.</p>
    </div>
  </div>

  <div class="calc-result" data-calc-result>
    <h3>Estimated total</h3>
    <p class="calc-total" data-calc-total>$0</p>
    <dl class="calc-breakdown" data-calc-breakdown></dl>
    <p class="muted small" data-calc-warning></p>
  </div>
</div>

<section class="panel">
  <h2>How the estimate is built</h2>
  <ul class="bullets">
    <li><strong>Room cost</strong> = true nightly cost × nights, where true nightly cost is the
      dated published rate including the resort fee, plus {tax["roomTaxRate"]*100:.2f}% room tax.</li>
    <li><strong>Tournament cost</strong> = entries × the buy-in on the official structure sheet.
      Multi-flight and seat-prize events are counted in the extra-spend field rather than
      assumed away.</li>
    <li><strong>Parking</strong> is not included. The Venetian publishes $20 a day for registered
      guests and $40 a day for valet, and other properties publish their own rates. Add them
      from the parking column on the <a href="hotels.html">Hotels</a> page.</li>
    <li><strong>Not included:</strong> travel, food, the $50 plus tax resort fee is already inside
      the nightly rate, and the final folio can differ from this estimate because the booking
      pages say the published rate excludes taxes.</li>
  </ul>
</section>

<section class="panel">
  <h2>Ranked tournament cost per dollar of published guarantee</h2>
  <p class="muted">Only rows whose fee split <em>and</em> guarantee are both confirmed on an
  official structure sheet are ranked. A guarantee is what the venue publishes, not a forecast
  of a payout, and bounty guarantees include bounty money, so the cash-pool ratio is shown
  next to it.</p>
  {ranking_table(dataset)}
</section>
"""
    return page("cost.html", "Trip cost", body)


def ranking_table(dataset):
    rows = []
    candidates = [
        e
        for e in dataset["events"]
        if e.get("dateISO") and e.get("buyIn") and e.get("guarantee") and e.get("cashPoolPerEntry")
    ]
    candidates.sort(key=lambda e: e["cashRatio"], reverse=True)
    for event in candidates:
        rows.append(
            f"<tr><td>{esc(event['dateLabel'])}<br><span class='muted'>{esc(event['time'])}</span></td>"
            f"<td>{esc(event['name'])}</td>"
            f"<td>{usd(event['buyIn'])}</td>"
            f"<td>{usd(event['guarantee'])}"
            + (" <span class='muted'>(incl. bounties)</span>" if event.get("guaranteeIncludesBounties") else "")
            + "</td>"
            f"<td>{esc(event['cashRatio'])}×</td>"
            f"<td>{esc(event['gtdRatio'])}×</td>"
            f"<td>{esc(event.get('entryRule',''))}</td>"
            f"<td>{source_links(event.get('sourceLinks', []))}</td></tr>"
        )
    return (
        '<div class="table-wrap"><table class="data-table"><thead><tr>'
        "<th>Date</th><th>Tournament</th><th>Buy-in</th><th>Guaranteed pool</th>"
        "<th>Cash pool ÷ fee</th><th>Guarantee ÷ fee</th><th>Entry rule</th>"
        "<th>Official source</th></tr></thead><tbody>"
        + "".join(rows)
        + "</tbody></table></div>"
    )


def build_venues_index(dataset):
    cards = []
    for venue in dataset["venues"]:
        venue_events = [e for e in dataset["events"] if e["venueId"] == venue["id"]]
        strict = sum(1 for e in venue_events if e["bucket"] == "strict")
        unverified = sum(1 for e in venue_events if e["bucket"] == "unverified")
        hotels = [
            h["name"]
            for h in dataset["hotels"]
            if venue["name"].split()[0].lower() in h.get("venue", "").lower()
            or h.get("venue", "").split()[0].lower() in venue["name"].lower()
        ]
        source = next(
            (s for s in dataset["sources"] if s["id"] == venue.get("scheduleSourceId")), None
        )
        cards.append(
            f"""
<article class="venue-card">
  <h3><a href="{esc(venue["slug"])}.html">{esc(venue["name"])}</a></h3>
  <p class="muted">{esc(venue.get("pokerRoom",""))}</p>
  <p>{esc(venue.get("coverage",""))}</p>
  <p class="venue-stats">
    <span><strong>{len(venue_events)}</strong> official rows</span>
    <span><strong>{strict}</strong> one entry confirmed</span>
    <span><strong>{unverified}</strong> single entry not stated</span>
  </p>
  {f"<p class='muted'>Hotels on this property: {esc(', '.join(hotels))}</p>" if hotels else ""}
  {f'<p><a href="{esc(source["url"])}" target="_blank" rel="noopener">{esc(source["name"])} <span class="badge official">official</span></a></p>' if source else ""}
</article>"""
        )
    body = f"""
<h1>Venues</h1>
<p class="lede">One page per poker room. Each page records what was read from that room's own
pages, which rows are dated, which are recurring, and what is still open for that room.</p>
<div class="venue-grid">{"".join(cards)}</div>
"""
    return page("venues/index.html", "Venues", body, base="../")


def build_venue(dataset, venue):
    venue_events = [e for e in dataset["events"] if e["venueId"] == venue["id"]]
    flags_for = [
        f for f in dataset["flags"] if any(f.get("id", "") in (e.get("note", "") or "") for e in venue_events)
    ]
    source = next(
        (s for s in dataset["sources"] if s["id"] == venue.get("scheduleSourceId")), None
    )
    source_block = ""
    if source:
        source_block = (
            f'<p><a href="{esc(source["url"])}" target="_blank" rel="noopener">'
            f'{esc(source["name"])} <span class="badge official">official</span></a></p>'
        )
    related = [
        s
        for s in dataset["sources"]
        if any(s["id"] in e.get("sourceIds", []) for e in venue_events)
    ]
    body = f"""
<h1>{esc(venue["name"])}</h1>
<p class="lede">{esc(venue.get("pokerRoom",""))}</p>
<div class="panel-grid">
  <section class="panel">
    <h2>What was read</h2>
    <p>{esc(venue.get("coverage",""))}</p>
    <p>{esc(venue.get("note",""))}</p>
    {source_block}
    <p class="muted">Official sources used for this room's rows:</p>
    {source_links_block(related) if related else empty_note("No source recorded.")}
  </section>
  <section class="panel">
    <h2>Room record</h2>
    <dl class="def-list">
      <dt>Address</dt><dd>{esc(venue.get("address") or "not recorded")}</dd>
      <dt>Official rows</dt><dd>{len(venue_events)}</dd>
      <dt>One entry confirmed</dt><dd>{sum(1 for e in venue_events if e["bucket"] == "strict")}</dd>
      <dt>Single entry not stated</dt><dd>{sum(1 for e in venue_events if e["bucket"] == "unverified")}</dd>
      <dt>Extra-spend formats</dt><dd>{sum(1 for e in venue_events if e["bucket"] == "spend")}</dd>
      <dt>Multi-flight</dt><dd>{sum(1 for e in venue_events if e["bucket"] == "multi")}</dd>
    </dl>
  </section>
</div>
<section class="panel">
  <h2>Every row for this room</h2>
  <div class="table-wrap"><table class="data-table" data-table="tournaments"><thead><tr>
  {"".join(f"<th>{esc(h)}</th>" for h in TOURNAMENT_HEADERS)}</tr></thead>
  <tbody>{"".join(tournament_row(e) for e in venue_events)}</tbody></table></div>
</section>
<p><a href="../index.html">← Back to the overview</a> · <a href="../tournaments.html">All tournaments</a></p>
"""
    return page(f"venues/{venue['slug']}.html", venue["name"], body, base="../")


def build_sources(dataset):
    official = [s for s in dataset["sources"] if s["kind"] == "official"]
    third = [s for s in dataset["sources"] if s["kind"] != "official"]

    def block(items):
        rows = []
        for s in items:
            rows.append(
                f'<tr><td>{esc(s["id"])}</td><td>{esc(s["name"])}</td>'
                f'<td><a href="{esc(s["url"])}" target="_blank" rel="noopener">{esc(s["url"])}</a></td>'
                f'<td>{esc(s.get("checked",""))}</td>'
                f'<td><span class="badge {"third-party" if s["kind"] != "official" else "official"}">'
                f'{esc(s["kind"])}</span></td>'
                f"<td>{esc(s.get('note',''))}</td></tr>"
            )
        return (
            '<div class="table-wrap"><table class="data-table"><thead><tr>'
            "<th>ID</th><th>Source</th><th>URL</th><th>Checked</th><th>Kind</th><th>Note</th>"
            "</tr></thead><tbody>"
            + "".join(rows)
            + "</tbody></table></div>"
        )

    body = f"""
<h1>Sources</h1>
<p class="lede">Every official page and PDF this site is built from, with the date it was last
checked. Third-party material is listed separately and is never used as evidence for a value;
it appears only where a route estimate or a conflict note needs one.</p>
<section class="panel">
  <h2>Official sources ({len(official)})</h2>
  {block(official)}
</section>
<section class="panel">
  <h2>Third-party estimates ({len(third)})</h2>
  <p class="muted">These are used only for walking-time estimates and are labelled as
  third-party wherever they appear. No tournament, fee, guarantee or hotel rate comes from
  them.</p>
  {block(third)}
</section>
<section class="panel">
  <h2>Scheduled rechecks</h2>
  <p>Official URLs are re-checked on a schedule by
  <code>scripts/check_sources.py</code>, which records the retrieval time, the HTTP status and a
  content hash for each one. A changed hash is a review signal, not proof that a tournament
  value changed: rotating page content can produce a false signal. The latest results are on
  the <a href="monitor.html">Change monitor</a> page.</p>
</section>
"""
    return page("sources.html", "Sources", body)


def build_flagged(dataset):
    blocks = []
    for flag in dataset["flags"]:
        severity = flag.get("severity", "medium")
        source_links_html = ""
        source_ids = flag.get("sourceIds") or []
        if source_ids:
            links = [
                {
                    "id": sid,
                    "name": next(
                        (s["name"] for s in dataset["sources"] if s["id"] == sid), sid
                    ),
                    "url": next((s["url"] for s in dataset["sources"] if s["id"] == sid), ""),
                    "kind": next(
                        (s["kind"] for s in dataset["sources"] if s["id"] == sid), "official"
                    ),
                }
                for sid in source_ids
            ]
            source_links_html = (
                "<p class='muted small'>Sources: "
                + ", ".join(
                    f'<a href="{esc(l["url"])}" target="_blank" rel="noopener">{esc(l["name"])}</a>'
                    for l in links
                )
                + "</p>"
            )
        blocks.append(
            f"""
<article class="flag flag-{esc(severity)}" id="{esc(flag['id'])}">
  <div class="flag-head">
    <span class="flag-id">{esc(flag['id'])}</span>
    <span class="flag-sev">{esc(severity)}</span>
    <span class="flag-cat">{esc(flag.get('category',''))}</span>
  </div>
  <h3>{esc(flag['title'])}</h3>
  <p>{esc(flag.get('finding',''))}</p>
  {f"<blockquote>{esc(flag['evidence'])}</blockquote>" if flag.get('evidence') else ""}
  <p><strong>Why it matters:</strong> {esc(flag.get('impact',''))}</p>
  <p><strong>What to do:</strong> {esc(flag.get('nextStep',''))}</p>
  {source_links_html}
</article>"""
        )
    body = f"""
<h1>Flagged for review</h1>
<p class="lede">Every item on this page is an open question, a conflict between official
sources, or a value that could not be read from an official page. None of them blocks the
build or the deployment. They are published so a reviewer can see exactly what is still
unresolved before money is committed.</p>
<p class="muted">{len(dataset["flags"])} items, checked {esc(dataset["asOf"])}.</p>
<div class="flag-list">{"".join(blocks)}</div>
"""
    return page("flagged.html", "Flagged for review", body)


def build_questions(dataset):
    days = dataset["days"]
    no_finish = sum(1 for d in days for o in d["overlaps"] if o["verdict"].startswith("cannot"))
    uncertain = sum(1 for d in days for o in d["overlaps"] if not o["verdict"].startswith("cannot"))
    questions = [
        (
            "Is a second buy-in possible in the one-day Venetian events?",
            "The one-day structure sheets are read in full and simply do not mention re-entry, a "
            "rebuy, an add-on or a paid chip boost. That is silence, not permission and not a "
            "refusal. The desk's actual policy for a player who is eliminated early is not published.",
            "Call the Venetian poker room and ask what happens if you are eliminated before "
            "registration closes. Ask them to put it in writing for the event number.",
            "The Venetian poker room. The official poker page lists the room and its hours.",
            "Affects every row in the 'Single entry not stated' bucket on the Tournaments page.",
        ),
        (
            "How late does each event actually run?",
            "Official sheets publish start time, blind levels, level length and the time "
            "registration closes. None of them publishes a finish time. A tournament can run "
            "hours past its registration cut-off, so this site cannot promise a precise end.",
            "Ask each room for the expected duration of the events on your shortlist, then re-run "
            "the overlap check on the Day plan page.",
            "The individual poker rooms.",
            f"{no_finish} pairs provably overlap and {uncertain} more are uncertain. Both counts "
            "are on the Day plan page.",
        ),
        (
            "What is the real nightly cost at The Venetian for my dates?",
            "The official booking calendar loads the stay but every nightly price renders as the "
            "placeholder '$XXX'. The property with a zero-minute walk to the tournament room is "
            "therefore the one property with no comparable cost in the hotel table.",
            "Open the booking engine in a browser for your dates, or call the reservations line, "
            "and record the nightly price including the resort fee.",
            "The Venetian. The hotel terms and conditions page carries the contact details.",
            "The hotel ranking and the Trip cost calculator both exclude it until a rate exists.",
        ),
        (
            "Which resort fee actually applies on the booking?",
            "The Caesars booking pages print the resort fee two ways on the same page: the price "
            "breakdown uses $50 at Horseshoe and $55 at Caesars Palace, while the fee policy line "
            "prints $56.63 and $62.30 including tax. The true nightly cost here uses the price "
            "breakdown figure, because that is what the booking engine itself adds.",
            "Confirm the fee on the checkout summary before paying. It is the last screen before "
            "the card is charged.",
            "The booking engine's checkout summary.",
            "About $7.53 a night at Horseshoe if the policy line is the charge instead.",
        ),
        (
            "What does the Wynn charge for the sample dates?",
            "The official booking URL was opened with the December 10 to 14 window and returned a "
            "page describing a one-night stay in mid-November. The price on that page cannot be "
            "attached to the requested dates, so no Wynn rate is published.",
            "Run the same search in a browser for your dates, or call the Wynn reservations line.",
            "The Wynn reservations line.",
            "The Wynn's daily tournament slate is also suspended during the WPT World Championship "
            "from November 27 to December 21, which covers most of the sample stay.",
        ),
        (
            "Is there any tournament that starts early enough for an all-day plan?",
            "The earliest published start anywhere in this dataset is 9:10 a.m., for a turbo "
            "milestone satellite on December 12. The earliest single-entry-candidate start is "
            "10:10 a.m. No venue publishes an 8 a.m. start.",
            "If an early start matters, ask the rooms whether a morning tournament can be added "
            "before the published slate.",
            "The individual poker rooms.",
            "The Day plan page starts each day at the earliest published start instead of at "
            "8 a.m.",
        ),
        (
            "Do South Point and ARIA run daily tournaments that could be planned around?",
            "South Point publishes its schedule and rule sheets as images, so the entry terms "
            "could not be read as text. ARIA publishes no tournament times or buy-ins at all and "
            "asks guests to call the room to confirm whether daily tournaments are running.",
            "Read the South Point rule-sheet images, or call both rooms for today's list and the "
            "entry rules.",
            "South Point and ARIA poker rooms.",
            "Both rooms are excluded from any ranking until their terms are readable.",
        ),
        (
            "Which Strip rooms are not covered at all?",
            "This dataset covers The Venetian, Wynn, Bellagio, MGM Grand, Caesars Palace, "
            "Horseshoe, the Golden Nugget, South Point and ARIA. Resorts World, Circa, Westgate, "
            "the Sahara, the Orleans, the Tropicana, Red Rock, the Palms and the downtown rooms "
            "other than the Golden Nugget are not.",
            "Decide which of those matter to you, then repeat the same structure-sheet check on "
            "each one.",
            "Each room's own site.",
            "A 'best tournament near the Strip' list built only from this dataset may miss a "
            "cheaper single-entry option.",
        ),
    ]
    blocks = []
    for index, (title, why, ask, who, impact) in enumerate(questions, start=1):
        blocks.append(
            f"""
<article class="qa">
  <h3><span class="qa-num">Q{index}</span>{esc(title)}</h3>
  <p>{esc(why)}</p>
  <p class="qa-ask"><strong>Ask:</strong> {esc(ask)}</p>
  <p><strong>Who to ask:</strong> {esc(who)}</p>
  <p class="muted"><strong>What it affects:</strong> {esc(impact)}</p>
</article>"""
        )
    body = f"""
<h1>Open questions</h1>
<p class="lede">The decisions that are still outstanding before money is committed. Each one
says what is unknown, what to ask, who to ask, and what on this site changes when the answer
arrives.</p>
<div class="qa-list">{"".join(blocks)}</div>
<section class="panel">
  <h2>What is already settled</h2>
  <ul class="bullets">
    <li>The Venetian's DeepStack Extravaganza IV schedule: {len(dataset["days"])} dates,
      {len(dataset["events"])} rows, reconciled line by line against the official schedule PDF
      and the official event page.</li>
    <li>All 37 official structure sheets read in full, with the entry rule each one states
      recorded against the numbered rule it comes from.</li>
    <li>The fee split, starting stack, level length, registration close and guarantee for every
      Venetian row, from the sheet itself.</li>
    <li>The hotel fee, tax and cancellation terms for the properties whose official pages
      publish them.</li>
  </ul>
</section>
"""
    return page("questions.html", "Open questions", body)


def build_suggestions(dataset):
    suggestions = [
        (
            "Add the remaining Strip rooms",
            "Nine rooms are covered. Resorts World, Circa, Westgate, the Sahara, the Orleans, "
            "the Tropicana, Red Rock, the Palms and the downtown rooms are not. Each needs the "
            "same structure-sheet check.",
            "High",
            "High",
            "Each added room needs its official schedule and structure sheets read in full, "
            "exactly like the Venetian's 37.",
        ),
        (
            "Read South Point's rule-sheet images",
            "South Point publishes nine rule-sheet images and a schedule graphic. The rules "
            "cannot be read as text today.",
            "Medium",
            "Medium",
            "Reading the images turns an unread room into a plannable one.",
        ),
        (
            "Capture finish times from each room",
            "No venue publishes them. With durations from the rooms, the overlap check on the "
            "Day plan page becomes exact instead of a lower bound.",
            "High",
            "Medium",
            "A phone call per room would make every scheduling statement on the site exact.",
        ),
        (
            "Add a live rate check for the hotels",
            "Rates move. A dated rate log is honest but stale the moment it is written. A "
            "scheduled check that records the current nightly rate per date range would keep "
            "the cost table live.",
            "Medium",
            "High",
            "The change monitor already exists; extending it to booking pages is the same "
            "mechanism.",
        ),
        (
            "Add a per-event walk estimate from the room to each hotel",
            "Four of the eight hotel-to-venue pairs have no walking time at all, including "
            "Caesars Palace, Paris and Bellagio to the Venetian.",
            "Medium",
            "Medium",
            "Each pair needs a measured time and a map link, the same as the existing rows.",
        ),
        (
            "Add tournament results after each event runs",
            "The official schedule page has a Results column for every row.",
            "Medium",
            "Low",
            "Results would let the site show actual prize pools against the guarantees.",
        ),
        (
            "Add the WPT festival events one by one",
            "The WPT World Championship at Wynn runs from November 27 to December 21 with more "
            "than 85 events. The series is listed as one row; the individual structure PDFs "
            "have not been read.",
            "Medium",
            "Medium",
            "Reading them event by event would add roughly 85 dated rows with their own entry "
            "rules.",
        ),
        (
            "Add a per-day cost estimator",
            "The Trip cost page calculates a stay plus a number of entries. It does not yet "
            "suggest which tournament to pair with which hotel for the best value.",
            "Low",
            "Medium",
            "It would need the ranking table to be trustworthy first.",
        ),
    ]
    rows = []
    for title, what, value, effort, note in suggestions:
        rows.append(
            f"<tr><td><strong>{esc(title)}</strong><br><span class='muted'>{esc(what)}</span></td>"
            f"<td>{esc(value)}</td><td>{esc(effort)}</td><td>{esc(note)}</td></tr>"
        )
    body = f"""
<h1>Suggestions</h1>
<p class="lede">What would make this planner more complete, and what each one costs to do.
These are for review, not commitments. Nothing here has been implemented by assumption.</p>
<div class="table-wrap"><table class="data-table"><thead><tr>
<th>Suggestion</th><th>Value</th><th>Effort</th><th>Notes</th>
</tr></thead><tbody>{"".join(rows)}</tbody></table></div>
<section class="panel">
  <h2>Decisions already taken, so they are not re-litigated</h2>
  <ul class="bullets">
    <li><strong>Cost and quality come before distance</strong>, but every hotel shown is within
      the 30-minute walking limit. A cheaper stay further out does not qualify.</li>
    <li><strong>Blank means blank.</strong> A value that could not be read from an official
      source is left empty and listed on the Flagged page, never filled with a plausible number.</li>
    <li><strong>Third-party material is never evidence.</strong> Walking estimates are labelled
      as estimates and carry a map link so a traveller can check them.</li>
    <li><strong>Nothing is ranked before its fee and guarantee are confirmed</strong> on an
      official sheet.</li>
  </ul>
</section>
"""
    return page("suggestions.html", "Suggestions", body)


def build_monitor(dataset):
    monitor_path = SITE / "data" / "source-monitor.json"
    monitor = {}
    if monitor_path.exists():
        try:
            monitor = json.loads(monitor_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            monitor = {}
    scrape_path = SITE / "data" / "schedule-scrape.json"
    scrape = {}
    if scrape_path.exists():
        try:
            scrape = json.loads(scrape_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            scrape = {}
    checks = monitor.get("checks", {})
    summary = ""
    differences = scrape.get("differences", [])
    if scrape:
        if differences:
            scrape_block = (
                f"<div class='notice'><strong>{len(differences)} difference(s) found.</strong> "
                "The official page no longer matches the curated rows. Check each one by hand "
                "before changing any published value.</div>"
                + '<div class="table-wrap"><table class="data-table"><thead><tr>'
                "<th>Kind</th><th>Date</th><th>Event</th><th>Detail</th></tr></thead><tbody>"
                + "".join(
                    f"<tr><td>{esc(d.get('kind',''))}</td>"
                    f"<td>{esc(d.get('date',''))}</td>"
                    f"<td>{esc(d.get('event',''))} {esc(d.get('flight',''))}</td>"
                    f"<td>{esc(d.get('detail') or (str(d.get('was')) + ' now ' + str(d.get('now'))))}</td></tr>"
                    for d in differences
                )
                + "</tbody></table></div>"
            )
        else:
            scrape_block = (
                f"<p class='muted'>Last scrape {esc(scrape.get('checkedAt',''))} &middot; "
                f"{esc(scrape.get('scrapedRowCount',0))} rows on the official page &middot; "
                "no differences against the curated data.</p>"
            )
    else:
        scrape_block = (
            "<p class='notice'>No schedule scrape has been recorded yet. The first scheduled "
            "run writes one.</p>"
        )
    if monitor:
        summary = (
            f"<p class='muted'>Last run {esc(monitor.get('checkedAt',''))} &middot; "
            f"{esc(monitor.get('officialSourceCount',0))} official URLs checked &middot; "
            f"{esc(monitor.get('changedCount',0))} changed &middot; "
            f"{esc(monitor.get('unavailableCount',0))} unavailable.</p>"
        )
    body = f"""
<h1>Change monitor</h1>
<p class="lede">Official URLs are re-checked on a schedule by
<code>scripts/check_sources.py</code>. For each URL it records the retrieval time, the HTTP
status, a content hash and whether the page changed since the last check. A changed hash is a
review signal, not proof that a tournament value changed: dynamic or rotating content produces
false signals. Open the page and check the value by hand before changing anything.</p>
{summary}
{"<p class='notice'>No monitor log has been committed yet. The first scheduled run writes one.</p>" if not checks else ""}
<div data-monitor-log>
{monitor_log_table(checks)}
</div>
<section class="panel">
  <h2>Live schedule scrape</h2>
  <p>The official Venetian event page is scraped on the same schedule and compared with the
  curated rows, so a changed start time, a changed structure sheet or an added event shows
  up here instead of silently going stale.</p>
  {scrape_block}
</section>

<section class="panel">
  <h2>How the monitor works</h2>
  <ul class="bullets">
    <li>Only URLs tagged as official in the source register are checked. Third-party route
      estimates are excluded on purpose.</li>
    <li>A first run records a baseline hash. Later runs compare against it.</li>
    <li>An unreachable URL is recorded as unavailable. It is never counted as unchanged and
      never as verified.</li>
    <li>The log is committed to the repository and the site is redeployed after each run.</li>
  </ul>
</section>
"""
    return page("monitor.html", "Change monitor", body)


def monitor_log_table(checks):
    """The monitor log is a mapping of source id -> result record."""
    if not checks:
        return empty_note("No monitor log yet. The first scheduled run writes one.")
    items = checks.items() if isinstance(checks, dict) else enumerate(checks)
    rows = []
    for source_id, check in items:
        if not isinstance(check, dict):
            continue
        status = check.get("result", "")
        cls = {
            "changed": "verdict-warn",
            "unchanged": "verdict-ok",
            "baseline": "",
            "unavailable": "verdict-bad",
        }.get(status, "")
        note = check.get("error") or check.get("note") or ""
        rows.append(
            f'<tr><td>{esc(check.get("lastChecked") or check.get("checkedAt", ""))}</td>'
            f'<td>{esc(source_id)}</td>'
            f'<td><a href="{esc(check.get("url", ""))}" target="_blank" rel="noopener">'
            f'{esc(check.get("name") or check.get("url", ""))}</a></td>'
            f'<td>{esc(check.get("httpStatus", ""))}</td>'
            f'<td class="{cls}">{esc(status)}</td>'
            f"<td>{esc(note)}</td></tr>"
        )
    return (
        '<div class="table-wrap"><table class="data-table"><thead><tr>'
        "<th>Checked at</th><th>ID</th><th>Source</th><th>HTTP</th><th>Result</th><th>Note</th>"
        "</tr></thead><tbody>"
        + "".join(rows)
        + "</tbody></table></div>"
    )


# ------------------------------------------------------------------- main ----
def write(path: pathlib.Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def main() -> int:
    dataset = build_dataset()
    SITE.mkdir(parents=True, exist_ok=True)

    write(SITE / "data.json", json.dumps(dataset, indent=1, ensure_ascii=False) + "\n")

    write(SITE / "index.html", build_index(dataset))
    write(SITE / "tournaments.html", build_tournaments(dataset))
    write(SITE / "schedule.html", build_schedule(dataset))
    write(SITE / "hotels.html", build_hotels(dataset))
    write(SITE / "cost.html", build_cost(dataset))
    write(SITE / "venues" / "index.html", build_venues_index(dataset))
    for venue in dataset["venues"]:
        write(SITE / "venues" / f"{venue['slug']}.html", build_venue(dataset, venue))
    write(SITE / "sources.html", build_sources(dataset))
    write(SITE / "questions.html", build_questions(dataset))
    write(SITE / "suggestions.html", build_suggestions(dataset))
    write(SITE / "flagged.html", build_flagged(dataset))
    write(SITE / "monitor.html", build_monitor(dataset))

    dated = [e for e in dataset["events"] if e.get("dateISO")]
    counts = {}
    for event in dated:
        counts[event["bucket"]] = counts.get(event["bucket"], 0) + 1
    print(f"wrote {SITE}/data.json : {len(dataset['events'])} events, {len(dataset['hotels'])} hotels, "
          f"{len(dataset['routes'])} routes, {len(dataset['flags'])} flags")
    print(f"  dated rows: {len(dated)} across {len(dataset['days'])} days")
    for bucket in ["strict", "unverified", "multi", "spend", "review"]:
        if counts.get(bucket):
            print(f"  {bucket}: {counts[bucket]}")
    print(f"  pages written: {len(list(SITE.glob('*.html'))) + len(list(SITE.glob('venues/*.html')))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
