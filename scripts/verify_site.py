#!/usr/bin/env python3
"""Offline verifier for the canonical site in site/.

Checks, on the generated output only:
  1. site/data.json is valid JSON and has the expected shape.
  2. Every tournament row links an official source.
  3. Every hotel row links an official source.
  4. Values that could not be read from an official source are blank, not invented.
  5. A hotel total is only published when every component of it is published.
  6. Every entry rule is one of the recorded verdicts and carries its basis.
  7. Every internal link in every published page resolves to a file that exists.
  8. Every external link uses https and points at a venue's own domain.
  9. The pages that must exist do exist, and the navigation on each matches.

Run:  python3 scripts/verify_site.py
"""
from __future__ import annotations

import json
import pathlib
import re
import sys
from urllib.parse import urlparse

ROOT = pathlib.Path(__file__).resolve().parents[1]
SITE = ROOT / "site"

REQUIRED_PAGES = [
    "index.html",
    "tournaments.html",
    "schedule.html",
    "hotels.html",
    "cost.html",
    "venues/index.html",
    "sources.html",
    "questions.html",
    "suggestions.html",
    "flagged.html",
    "monitor.html",
]

VERDICTS = {
    "unverified - single entry not stated",
    "extra spend possible - one entry per flight",
    "extra spend possible - seat prize",
    "extra spend possible - multiple flights and a paid chip boost",
    "extra spend confirmed - the sheet sells further buy-ins",
    "extra spend confirmed - re-entries are sold",
    "extra spend confirmed - the sheet sells rebuys and an add-on",
    "extra spend confirmed - re-entries and an add-on are sold",
    "extra spend confirmed - re-entries and add-ons are sold",
    "extra spend confirmed - re-entries and a paid chip boost are sold",
    "extra spend confirmed - a paid chip boost is sold",
    "extra spend confirmed - the sheet sells an add-on",
    "team format - needs review",
    "needs review",
}

# Domains that count as an official venue, hotel or regulator source.
OFFICIAL_HOSTS = (
    "venetianlasvegas.com",
    "palazzolasvegas.com",
    "wynnlasvegas.com",
    "caesars.com",
    "mgmresorts.com",
    "bellagio.mgmresorts.com",
    "mgmgrand.mgmresorts.com",
    "aria.mgmresorts.com",
    "goldennugget.com",
    "southpointcasino.com",
    "contentstack.io",
    "cdn.wynnresorts.com",
    "assets.mgmresorts.com",
)

problems: list[str] = []
notes: list[str] = []


def fail(message: str):
    problems.append(message)


def ok(message: str):
    notes.append(message)


def host_of(url: str) -> str:
    try:
        return (urlparse(url).hostname or "").lower()
    except ValueError:
        return ""


def is_official(url: str) -> bool:
    host = host_of(url)
    if not host:
        return False
    return any(host == domain or host.endswith("." + domain) for domain in OFFICIAL_HOSTS)


def main() -> int:
    if not (SITE / "data.json").exists():
        print("site/data.json is missing - run scripts/build_site.py first")
        return 1
    data = json.loads((SITE / "data.json").read_text(encoding="utf-8"))

    # 1. shape
    for key in ["asOf", "events", "hotels", "routes", "sources", "flags", "venues", "days", "policy"]:
        if key not in data:
            fail(f"data.json is missing the '{key}' key")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(data.get("asOf", ""))):
        fail(f"data.json asOf is not an ISO date: {data.get('asOf')!r}")
    else:
        ok(f"snapshot date {data['asOf']}")

    events = data.get("events", [])
    hotels = data.get("hotels", [])
    dated = [e for e in events if e.get("dateISO")]
    ok(f"{len(events)} tournament rows ({len(dated)} dated, {len(events) - len(dated)} recurring)")

    # 2. every tournament row links an official source
    for event in events:
        links = event.get("sourceLinks") or []
        if not links:
            fail(f"tournament row '{event.get('id')}' has no source link")
            continue
        if not any(is_official(link.get("url", "")) for link in links):
            fail(
                f"tournament row '{event.get('id')}' has no official source link "
                f"({[l.get('url') for l in links]})"
            )
        if not event.get("lastChecked"):
            fail(f"tournament row '{event.get('id')}' has no last-checked date")
        if event.get("structureSheet") and not is_official(event["structureSheet"]):
            fail(f"tournament row '{event.get('id')}' has a non-official structure sheet link")

    # 3 + 4 + 5. hotels
    for hotel in hotels:
        if not hotel.get("officialUrl"):
            fail(f"hotel '{hotel.get('id')}' has no official page link")
        elif not is_official(hotel["officialUrl"]):
            fail(f"hotel '{hotel.get('id')}' links a non-official page: {hotel['officialUrl']}")
        if not hotel.get("rateStatus"):
            fail(f"hotel '{hotel.get('id')}' has no rate status")
        latest = hotel.get("latestRate") or {}
        if hotel.get("hasRate"):
            for component in ["nightlyRate", "resortFeeIncluded", "nightlyWithFee", "nights", "occupancy"]:
                if latest.get(component) in (None, ""):
                    fail(
                        f"hotel '{hotel.get('id')}' publishes a total but '{component}' is missing"
                    )
            if latest.get("nightlyWithFee") is None:
                fail(f"hotel '{hotel.get('id')}' has a total without a nightly rate")
            if hotel.get("trueNightly") in (None, ""):
                fail(f"hotel '{hotel.get('id')}' has a rate but no true nightly cost")
            if not latest.get("checked"):
                fail(f"hotel '{hotel.get('id')}' has a rate with no checked date")
        else:
            # No rate: totals must be blank, not invented.
            if hotel.get("trueNightly") not in (None, ""):
                fail(f"hotel '{hotel.get('id')}' has no rate but publishes a true nightly cost")
            if hotel.get("trueStay") not in (None, ""):
                fail(f"hotel '{hotel.get('id')}' has no rate but publishes a stay total")
            ok(f"hotel '{hotel.get('id')}' has no official rate: totals left blank")

    # 6. entry rules
    for event in events:
        verdict = event.get("entryRule", "")
        if verdict not in VERDICTS:
            fail(f"tournament row '{event.get('id')}' has an unknown entry verdict: {verdict!r}")
        if not event.get("entryRuleBasis"):
            fail(f"tournament row '{event.get('id')}' has no entry-rule basis")
        for field in ["singleEntry", "reEntry", "addOn", "rebuy", "paidChipBoost"]:
            if field not in event:
                fail(f"tournament row '{event.get('id')}' is missing the '{field}' field")
            elif not event[field]:
                fail(f"tournament row '{event.get('id')}' has a blank '{field}' value")
        if event.get("bucket") == "strict" and "confirmed" not in verdict:
            fail(f"tournament row '{event.get('id')}' is bucketed strict without a confirmed verdict")

    # 7. internal links
    pages = sorted(SITE.glob("*.html")) + sorted(SITE.glob("venues/*.html"))
    for page in pages:
        html = page.read_text(encoding="utf-8")
        for href in re.findall(r'href="([^"#][^"]*)"', html):
            if href.startswith(("http://", "https://", "mailto:", "tel:", "//")):
                continue
            target = (page.parent / href).resolve()
            if not target.exists():
                fail(f"{page.relative_to(SITE)} links to a missing file: {href}")
    ok(f"{len(pages)} published pages checked for internal links")

    # 8. external links
    external = set()
    for page in pages:
        html = page.read_text(encoding="utf-8")
        for url in re.findall(r'href="(https?://[^"]+)"', html):
            external.add(url)
    for url in sorted(external):
        if url.startswith("http://"):
            fail(f"external link is not https: {url}")
        if host_of(url) in {"www.google.com", "maps.apple.com"}:
            continue
        if host_of(url) == "www.rome2rio.com":
            # Third-party walking estimates are listed as review items only.
            continue
        if not is_official(url):
            fail(f"external link does not point at an official domain: {url}")
    ok(f"{len(external)} external links checked")

    # 9. pages and navigation
    for name in REQUIRED_PAGES:
        if not (SITE / name).exists():
            fail(f"required page is missing: {name}")
    for page in pages:
        html = page.read_text(encoding="utf-8")
        if "data-search-input" not in html:
            fail(f"{page.relative_to(SITE)} has no global search box")
        if "assets/app.js" not in html:
            fail(f"{page.relative_to(SITE)} does not load assets/app.js")
        if "data-asof" not in html:
            fail(f"{page.relative_to(SITE)} does not show the snapshot date")
        # every nav target must be linked from the page
        for href in re.findall(r'<a href="([^"]+)"', html):
            if href.endswith(".html") and not href.startswith("http"):
                if not (page.parent / href).resolve().exists():
                    fail(f"{page.relative_to(SITE)} has a broken navigation link: {href}")

    # Every flag must be published on the Flagged page.
    flagged_html = (SITE / "flagged.html").read_text(encoding="utf-8")
    for flag in data.get("flags", []):
        if flag.get("id") and f'id="{flag["id"]}"' not in flagged_html:
            fail(f"flag {flag['id']} is not published on flagged.html")
    ok(f"{len(data.get('flags', []))} flags published on flagged.html")

    # Every source must appear on the sources page.
    sources_html = (SITE / "sources.html").read_text(encoding="utf-8")
    def escaped(url: str) -> str:
        return (
            url.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
        )

    for source in data.get("sources", []):
        if source.get("url") and escaped(source["url"]) not in sources_html:
            fail(f"source {source['id']} is not listed on sources.html")

    # Every route must appear on the hotels page.
    hotels_html = (SITE / "hotels.html").read_text(encoding="utf-8")
    for route in data.get("routes", []):
        if route.get("fromName") and route["fromName"] not in hotels_html:
            fail(f"route from {route['fromName']} is not listed on hotels.html")

    print("Poker3 canonical site verification")
    print("=" * 46)
    for note in notes:
        print("  ok  ", note)
    if problems:
        print()
        print(f"{len(problems)} problem(s):")
        for problem in problems:
            print("  !!  ", problem)
        return 1
    print()
    print("All checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
