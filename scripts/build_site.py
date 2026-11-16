#!/usr/bin/env python3
"""Build the canonical GitHub Pages dashboard in site/ from the curated data files.

Inputs (all curated from official sources, see data/*.json and COORDINATION.md):
  data/venetian_dse_iv.json  - Venetian DeepStack Extravaganza IV schedule + 37 structure sheets
  data/rooms.json            - the other Strip poker rooms
  data/hotels.json           - hotels, fee/tax/parking/cancellation terms, dated rate log
  data/routes.json           - hotel <-> venue walking pairs
  data/sources.json          - official source register
  data/flags.json            - flagged irregularities and open questions

Outputs:
  site/data.json             - merged dataset used by the browser scripts
  site/*.html                - the published pages
  site/venues/*.html         - one page per venue

Nothing here invents a value: every number comes from a data file, and every row
keeps the source link that produced it.

Run:  python3 scripts/build_site.py
"""
from __future__ import annotations

import json
import pathlib
import re
from datetime import date, timedelta

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

BUCKET_LABEL = {
    "strict": "Single-entry confirmed",
    "spend": "Extra-spend format (separate section)",
    "multi": "Multi-flight: extra entries possible",
    "review": "Needs review",
}

VENETIAN_VENUE = {
    "id": "venetian",
    "name": "The Venetian Resort Las Vegas",
    "slug": "venetian",
    "pokerRoom": "The Venetian poker room (DeepStack Extravaganza IV is run here)",
    "address": "",
    "addressSourceId": "",
    "scheduleSourceId": "venetian-dse4",
    "coverage": "Official event schedule page, official schedule PDF and all 37 official structure sheets were read on 2026-11-16.",
    "note": "94 published schedule rows across 64 numbered events, November 16 - December 23, 2026.",
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


def money(value) -> str:
    if value in (None, "", 0) and value != 0:
        return ""
    if isinstance(value, (int, float)):
        return "$" + f"{value:,.0f}"
    return str(value)


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
        event["sourceIds"] = ["venetian-dse4", "venetian-dse4-pdf", "venetian-dse4-structures"]
        event["scheduleUrl"] = venetian["scheduleUrl"]
        event["sheetUrl"] = row["structureSheet"]
        events.append(event)

    for venue in rooms["venues"]:
        for row in venue["events"]:
            event = dict(row)
            event["venueId"] = venue["id"]
            event["scheduleUrl"] = ""
            event["sheetUrl"] = ""
            event["dateISO"] = ""
            events.append(event)

    bucket_of = {
        "single-entry confirmed": "strict",
        "extra-spend format": "spend",
        "multi-entry possible": "multi",
        "team format - needs review": "review",
        "needs review": "review",
    }
    for event in events:
        event["bucket"] = bucket_of.get(event.get("eligibility"), "review")
        event["bucketLabel"] = BUCKET_LABEL[event["bucket"]]
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

    # Venues: the Venetian plus the rooms file.
    venues = [VENETIAN_VENUE]
    for venue in rooms["venues"]:
        venues.append(venue)
    venue_by_id = {v["id"]: v for v in venues}
    for venue in venues:
        venue["eventCount"] = sum(1 for e in events if e["venueId"] == venue["id"])
        venue["strictCount"] = sum(
            1 for e in events if e["venueId"] == venue["id"] and e["bucket"] == "strict"
        )
        venue["hotels"] = [
            h["id"]
            for h in hotels["hotels"]
            if h["venue"].lower().startswith(venue["name"].split(" ")[0].lower())
            or venue["name"].split(" ")[0].lower() in h["venue"].lower()
        ]

    # Hotels: true nightly cost from the dated rate log.
    tax_rate = hotels["taxModel"]["roomTaxRate"]
    for hotel in hotels["hotels"]:
        observations = []
        for rate in hotel.get("rates", []):
            obs = dict(rate)
            obs["trueNightly"] = round(obs["nightlyWithFee"] * (1 + tax_rate), 2)
            obs["trueStay"] = round(obs["trueNightly"] * obs.get("nights", 0), 2)
            observations.append(obs)
        hotel["rateLog"] = sorted(observations, key=lambda r: (r["checked"], r.get("nightlyWithFee", 0)))
        latest = hotel["rateLog"][-1] if hotel["rateLog"] else None
        hotel["latestRate"] = latest
        hotel["trueNightly"] = latest["trueNightly"] if latest else ""
        hotel["trueStay"] = latest["trueStay"] if latest else ""
        hotel["rateStatus"] = (
            f"Latest dated observation: ${latest['nightlyWithFee']:,.0f} with resort fee, "
            f"${latest['trueNightly']:,.2f} with {tax_rate*100:.2f}% tax "
            f"(checked {latest['checked']}, {latest.get('roomType','')})"
            if latest
            else "No date-specific rate could be read from an official source - see Flagged for review"
        )

    # Routes with map links.
    hotel_by_id = {h["id"]: h for h in hotels["hotels"]}
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
        strict_rows = [e for e in rows if e["bucket"] == "strict"]
        spend_rows = [e for e in rows if e["bucket"] == "spend"]
        primary = strict_rows[0] if strict_rows else None
        fallback = None
        if primary is not None:
            for candidate in strict_rows[1:]:
                if (
                    primary["regCloseMinutes"] is not None
                    and candidate["startMinutes"] is not None
                    and candidate["startMinutes"] >= primary["regCloseMinutes"]
                ):
                    fallback = candidate
                    break
            if fallback is None and len(strict_rows) > 1:
                fallback = strict_rows[1]
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
                    verdict = "uncertain - start falls inside the first event's possible playing window"
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
                "events": rows,
                "primary": primary,
                "fallback": fallback,
                "spendEvents": spend_rows,
                "overlaps": pairs,
                "earliestStart": rows[0]["time"] if rows else "",
                "strictCount": len(strict_rows),
            }
        )

    dataset = {
        "asOf": venetian["checked"],
        "generatedBy": "scripts/build_site.py",
        "policy": {
            "strictRule": "An event counts as single-entry only when the official structure sheet for that event defines one buy-in and one starting stack and contains no re-entry, rebuy, add-on or second-buy-in provision. '1Day' in an event name is not proof.",
            "ratioRule": "Guaranteed pool divided by entry fee is shown as a description of the published guarantee, never as a forecast of what a player will win. Bounty guarantees include bounty money, so the cash-pool-to-buy-in ratio is shown next to it.",
            "costRule": "True nightly cost = published nightly rate including the resort fee, plus 13.38% Clark County room tax. It is an arithmetic restatement of published figures, not a quote.",
            "walkRule": "Walking times are third-party estimates unless a row says otherwise; no venue publishes walking times to another venue.",
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
        f'<a href="{base}{href}" class="{"active" if href == active else ""}"><span class="ico">{icon}</span>{esc(label)}</a>'
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
  <form class="global-search" data-global-search role="search">
    <input type="search" placeholder="Search every table on this page…" aria-label="Search all tables on this page" data-search-input>
  </form>
  <span class="top-tag">Official-source snapshot · checked <span data-asof>2026-11-16</span></span>
</header>
<nav class="mobile-nav" data-mobile-nav>{mobile_links}</nav>
<div class="layout">
  <aside class="sidebar">
    <div class="side-label">Plan your trip</div>
    <nav class="nav">{nav_links}</nav>
    <div class="side-note"><strong>Evidence first.</strong> Every row links the official page it came from. Blanks are intentional and listed on the Flagged for review page.</div>
  </aside>
  <main class="main">
{body}
    <div class="footer">Built from official venue pages on <span data-asof>2026-11-16</span>. Guarantees are descriptions of what a venue promises to publish, not forecasts of a payout. Verify prices, terms and schedules with the room before you pay. <a href="{base}flagged.html">Limitations and flagged items</a>.</div>
  </main>
</div>
<script src="{base}assets/app.js"></script>
{scripts}
</body>
</html>
"""


def table(headers, rows, cls="", row_attrs=None, empty_note=None):
    if not rows:
        return f'<p class="muted">{esc(empty_note or "No rows.")}</p>'
    head = "".join(f"<th>{esc(h)}</th>" for h in headers)
    body = []
    for index, row in enumerate(rows):
        cells = "".join(f"<td>{c}</td>" for c in row)
        attrs = (row_attrs or {}).get(index, "")
        body.append(f"<tr {attrs}>{cells}</tr>")
    return (
        f'<div class="table-wrap"><table class="{cls}"><thead><tr>{head}</tr></thead>'
        f"<tbody>{''.join(body)}</tbody></table></div>"
    )


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
    return "<span class=\"links\">" + "<br>".join(out) + "</span>"


def source_links_block(links):
    return "<ul class=\"linklist\">" + "".join(
        f'<li><a href="{esc(l["url"])}" target="_blank" rel="noopener">{esc(l["name"])}</a>'
        f' <span class="badge {"third-party" if l["kind"] == "third-party" else "official"}">{esc(l["kind"])}</span></li>'
        for l in links
    ) + "</ul>"
