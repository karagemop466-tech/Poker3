#!/usr/bin/env python3
"""Brief-coverage traceability matrix.

Maps every numbered requirement in the user's brief to:
  * shipped  -> implemented on a published page (page + anchor given)
  * flagged  -> genuinely open; published on site/flagged.html (flag ids given)
  * partial  -> implemented but limited by an open evidence gap
  * not-resolvable -> no official source publishes the value; cannot be filled in without inferring

Output: site/coverage.json  (a data file; not an HTML page, so it cannot introduce
a broken link into the verified site).
"""
from __future__ import annotations

import json
from pathlib import Path

DATA = Path("site/data.json")
OUT = Path("site/coverage.json")

# Each entry: (id, requirement, status, location, flags, note)
ITEMS = [
    # ---- Core calculator / monitoring / data shape (brief top block) ----
    ("C1", "Trip-cost calculator: entries x buy-ins + nights x true hotel cost",
     "shipped", "site/calculator.html", [],
     "Computed from published components; dated Venetian quote (23-30 Nov 2026, $4,010.55 all-in) shown beside the $197.28 published-components floor."),
    ("C2", "Scheduled automatic re-check of every official URL; mark rows whose source changed",
     "shipped", ".github/workflows/checks.yml + site/checks.json + site/sources.html",
     ["F30"],
     "Single scheduled job (12:10 UTC + push trigger) fetches each official URL, stores a content hash of the visible text, flags genuine changes; unavailable URLs are never reported as changed."),
    ("C3", "Read every structure sheet; remove 'unverified' only where confirmed",
     "shipped", "site/sheets.html + site/tournaments.html (per-row rule panel)", ["F31"],
     "All 52 official sheets read (37 DSE IV + 15 NYE). No sheet prints a one-entry-per-player cap, so no row is labelled 'single entry confirmed'; sheet-screened candidates show the printed excerpt, source and retrieval date."),
    ("C4", "'Last checked' date on every row",
     "shipped", "site/data.json (lastChecked / lastVerified) + per-row display", [],
     "Every tournament, hotel, walking-route and source record carries a retrieval date; 301 of 341 event rows last checked 2026-11-17, the rest 2026-11-16."),
    ("C5", "Hotel rates kept as a dated log, not a single value",
     "shipped", "site/data.json (rateLog) + site/hotels.html", [],
     "Append-only rate log; each observation carries observedOn, source, fee, tax, quote type. Dated Venetian checkout quote 23-30 Nov 2026 ($4,010.55) logged; calendar cells explicitly not treated as prices (F47/F69)."),
    # ---- Venue pages / search / coordination ----
    ("C6", "One page per venue (Venetian, Wynn, others), each with its events and hotels",
     "shipped", "site/venues.html + site/venues/{venetian,wynn,others}.html + site/browse.html", [],
     "Seven Strip poker rooms; each venue page lists its dated events and its hotels with official source links."),
    ("C7", "Search box across all tables",
     "shipped", "site/search.html + top search form on every page", [],
     "Global search across tournaments, hotel rows, dated rates, walking routes, sources, questions and review flags; tournament table keeps its own local filters."),
    ("C8", "Shared COORDINATION.md task board before parallel sessions",
     "shipped", "COORDINATION.md", [],
     "Single shared board listing each task, status, owning session, scope and files; integration-owner convention for shared outputs."),
    # ---- Exact dates & occupancy / hotel cost components ----
    ("C9", "Capture checkout total, nightly average, mandatory resort fee, tax, parking, cancellation deadline, rate timestamp; compare like-for-like",
     "partial", "site/hotels.html + site/data.json (trip, rateLog, hotels)", ["F15", "F36", "F39", "F57"],
     "Venetian dated checkout total $4,010.55 (23-30 Nov 2026) with per-night rates, $55 fee, 13.38% tax, $20/$25/$40 parking, 11 a.m. checkout, $100 early checkout, $150 incidental. No property publishes a date-specific quote for other hotels; Wynn/Caesars/Horseshoe print no room-tax %."),
    # ---- Schedule / overlap ----
    ("C10", "Flag overlapping entries using start time, late-registration cutoff, plausible duration; primary event + conditional fallback per day",
     "shipped", "site/schedule.html (dayPlan / planConflicts)", ["F16", "F49", "F50"],
     "One primary sheet-screened candidate per day with a conditional fallback and reason; overlap flags under a disclosed six-hour session estimate. No venue publishes finish times (F16)."),
    ("C11", "Guarantee / entry fee shown as descriptive ratio, never a forecast; bounty/flight labelled separately",
     "shipped", "site/tournaments.html (ratio column + category labels)", [],
     "ratio = guarantee / buy-in recomputed for every numeric row; category labels separate multi-flight, satellite, bounty/PKO and extra-spend rows."),
    # ---- Table filters / rule fields ----
    ("C12", "Date selector showing only events on chosen days",
     "shipped", "site/tournaments.html", [],
     "From/To date selectors plus venue, category, format, single-entry and 30-minute-walk filters."),
    ("C13", "Structured rule fields per event: single-entry, re-entry, add-on, fee, each with source excerpt and retrieval date",
     "shipped", "site/data.json (events[].rules) + per-row rule panel", ["F31"],
     "singleEntry / reEntry / addOn / fee blocks each carry status, excerpt, source link and retrieved date; blanks explained by note or flag."),
    ("C14", "Walking-route check: official-address walking times per hotel-venue pair, 30-minute limit applied",
     "partial", "site/data.json (routes) + site/hotels.html", ["F32", "F67"],
     "15 of 56 hotel-venue pairs recorded as Google Maps walking estimates; no venue publishes a walking time. The tournament table's 30-minute "
     "limit is opt-in and measured from a hotel the reader selects; rows over the limit and rows with no measured route are counted separately so a "
     "missing estimate is never shown as an eliminated option; missing pairs not inferred."),
    # ---- Change monitoring (duplicate of C2 in brief; listed once) ----
    ("C15", "Re-check official pages on a schedule and flag any value that changed",
     "shipped", ".github/workflows/checks.yml + scripts/check_sources.py", ["F30"],
     "Same automated re-check as C2; changed hash = review signal only, never an automatic value change."),
    # ---- User's direct asks ----
    ("U1", "Find live upcoming Strip poker tournaments; rank by cost to enter and prize pool",
     "shipped", "site/tournaments.html", [],
     "341 rows with buy-in, guarantee and guarantee/entry-fee ratio; single-entry filters surface the cheapest credible entries."),
    ("U2", "Single-entry tournaments only; multi-entry / rebuy / add-on kept in a separate section",
     "shipped", "site/tournaments.html (single-entry toggle + category labels)", ["F31"],
     "Sheet-screened candidate list vs separate extra-spend bucket (re-entry/rebuys/add-ons/paid chip boosts/multi-flight) with the exact clause quoted per row. Strict confirmed-entry filter returns 0 because no sheet prints a per-player maximum."),
    ("U3", "Best hotels within walking distance; true cost per night incl. resort fee; cost/quality priority over distance, distance reasonable (<=30 min walk)",
     "partial", "site/hotels.html", ["F32", "F39", "F51", "F66"],
     "True cost/night = (rate + resort fee) x 1.1338 where published; walking estimates with 30-min filter; quality column blank because no official quality score exists (F19). Dated quote only for Venetian 23-30 Nov 2026."),
    ("U4", "Tournament schedule playable all day from 8 AM; enter as many live tournaments as possible",
     "not-resolvable", "site/schedule.html + site/flagged.html", ["F17"],
     "No official Strip room publishes an 8:00 AM start; earliest verified dated start 9:10 AM (Venetian satellite, seats not cash) and 10:00-10:10 AM main-list. All-day plan built from earliest verified starts instead; 8 AM gap flagged."),
    ("U5", "Executive summary of important details",
     "shipped", "site/index.html", [],
     "Landing page: fixed trip, primary event per day, confirmed vs not confirmed, stats, day plan."),
    ("U6", "Suggestions section: proposed improvements to review before implementing",
     "shipped", "site/suggestions.html", [],
     "Improvements with impact, effort and the decision each one needs; not implemented until chosen."),
    ("U7", "Clear list of questions/information/answers needed before any decision; suggestions to discover missing info",
     "shipped", "site/questions.html", [],
     "Decision questions, each with the official source behind the answer; open items stay flagged rather than inferred."),
    ("U8", "Repo review line by line; verify from official sources; provide links for manual review; flag irregularities",
     "shipped", "site/flagged.html + site/sources.html + scripts/verify_site.py", [],
     "72 flags, each with its official source link; verify_site.py enforces official-domain source links and intentional blanks for unverified values."),
    ("U9", "GitHub Pages live site: clean landing page + category subpages, dashboard tables, analysis and findings",
     "shipped", "site/ (published at https://karagemop466-tech.github.io/Poker3/)", ["F29"],
     "Canonical dashboard in site/; root index.html redirects into it; Pages reports status: built from main /."),
    ("U10", "Every table row carries an official source link; unverified left blank and flagged; never infer",
     "shipped", "site/tournaments.html + site/hotels.html + scripts/verify_site.py", [],
     "341/341 event rows carry an official schedule/structure source link; blanks are intentional and flagged; verification fails the build on a fabricated value."),
]


def load_counts():
    d = json.loads(DATA.read_text())
    return {
        "events": len(d.get("events", [])),
        "hotels": len(d.get("hotels", [])),
        "routes": len(d.get("routes", [])),
        "sources": len(d.get("sources", [])),
        "flags": len(d.get("flags", [])),
        "planDays": len(d.get("dayPlan", [])),
        "asOf": d.get("asOf"),
    }


def main():
    counts = load_counts()
    by_status = {}
    for _id, _req, status, _loc, _flags, _note in ITEMS:
        by_status[status] = by_status.get(status, 0) + 1
    payload = {
        "generated": "2026-11-17",
        "dataCounts": counts,
        "coverageByStatus": by_status,
        "items": [
            {
                "id": i,
                "requirement": r,
                "status": s,
                "location": loc,
                "flags": fl,
                "note": n,
            }
            for i, r, s, loc, fl, n in ITEMS
        ],
    }
    OUT.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"wrote {OUT} ({len(ITEMS)} items)")
    print("by status:", by_status)


if __name__ == "__main__":
    main()
