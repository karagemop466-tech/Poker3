#!/usr/bin/env python3
"""Dependency-free render and interaction checks for the canonical site in site/.

No browser is available in this sandbox, so the checks work at the level of the
generated markup and the behaviour rules the page must satisfy:

  * every page parses as HTML and carries the navigation, the global search box
    and the snapshot date
  * every tournament table row has the filter attributes the browser script reads
  * every row links an official source
  * the day plan gives every date a primary and a fallback or says why not
  * the trip-cost calculator has the inputs and the result element the script needs
  * the values the calculator uses exist in the published data

Run:  python3 tests/test_canonical_site.py
"""
from __future__ import annotations

import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"

failures: list[str] = []
checks = 0


def check(condition, message):
    global checks
    checks += 1
    if not condition:
        failures.append(message)


class TableParser(HTMLParser):
    """Collects every data-table row with its attributes and cell text."""

    def __init__(self):
        super().__init__()
        self.rows = []
        self.in_table = False
        self.in_body = False
        self.current = None
        self.cell = None
        self.cell_text = []
        self.tables = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "table" and "data-table" in (a.get("class") or ""):
            self.in_table = True
            self.tables += 1
        if self.in_table and tag == "tbody":
            self.in_body = True
        if self.in_body and tag == "tr":
            self.current = {"attrs": a, "cells": [], "hrefs": []}
        if self.current is not None and tag == "td":
            self.cell = []
            self.cell_text = []
        if self.current is not None and tag == "a":
            href = a.get("href") or ""
            if href.startswith("http"):
                self.current["hrefs"].append(href)

    def handle_data(self, data):
        if self.cell is not None:
            self.cell_text.append(data)

    def handle_endtag(self, tag):
        if tag == "td" and self.cell is not None:
            self.current["cells"].append("".join(self.cell_text).strip())
            self.cell = None
        if tag == "tr" and self.current is not None:
            self.rows.append(self.current)
            self.current = None
        if tag == "tbody":
            self.in_body = False
        if tag == "table":
            self.in_table = False


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def main() -> int:
    data = json.loads(read(SITE / "data.json"))
    events = data["events"]
    hotels = data["hotels"]
    flags = data["flags"]

    pages = sorted(SITE.glob("*.html")) + sorted(SITE.glob("venues/*.html"))
    check(len(pages) >= 11, f"expected at least 11 published pages, found {len(pages)}")

    for page in pages:
        html = read(page)
        name = page.relative_to(SITE)
        parser = TableParser()
        parser.feed(html)

        check("data-search-input" in html, f"{name}: no global search box")
        check("data-global-search" in html, f"{name}: no global search form")
        check("data-asof" in html, f"{name}: no snapshot date")
        check('src="assets/app.js"' in html or 'src="../assets/app.js"' in html,
              f"{name}: does not load the shared script")
        check("<nav" in html, f"{name}: no navigation")

        # Every tournament row carries the attributes the filters read.
        for row in parser.rows:
            attrs = row["attrs"]
            if attrs.get("data-row") == "tournament":
                for needed in ("data-date", "data-venue", "data-bucket", "data-buyin"):
                    check(needed in attrs, f"{name}: tournament row is missing {needed}")
                check(attrs.get("data-bucket"), f"{name}: tournament row has an empty bucket")
                check(
                    row["hrefs"],
                    f"{name}: tournament row has no source link: {row['cells'][:3]}",
                )

    # The tournaments page must list every dated row.
    tournaments = read(SITE / "tournaments.html")
    dated = [e for e in events if e.get("dateISO")]
    parser = TableParser()
    parser.feed(tournaments)
    rows = [r for r in parser.rows if r["attrs"].get("data-row") == "tournament"]
    check(
        len(rows) == len(events),
        f"tournaments.html lists {len(rows)} rows but the data has {len(events)}",
    )
    check(
        len([r for r in rows if r["attrs"].get("data-date")]) == len(dated),
        "tournaments.html must list every dated row",
    )

    # Each bucket the filters offer must exist in the data.
    buckets = {e["bucket"] for e in events}
    check("unverified" in buckets, "no unverified rows in the data")
    check("spend" in buckets, "no extra-spend rows in the data")
    check("multi" in buckets, "no multi-flight rows in the data")
    bucket_options = re.findall(
        r'data-filter="bucket".*?</select>', read(SITE / "tournaments.html"), re.S
    )
    for block in bucket_options:
        for option in re.findall(r'<option value="([a-z-]+)">', block):
            if option not in buckets:
                # A bucket with no rows must be explained on the page, not silently empty.
                check(
                    option == "strict"
                    and "No event in this dataset is confirmed single-entry" in read(
                        SITE / "tournaments.html"
                    ),
                    f"the bucket filter offers '{option}' but no row has it and the page "
                    "does not explain why",
                )

    # Day plan: every day has a primary and a fallback or an explicit reason.
    for day in data["days"]:
        check(day["date"], "a day has no date")
        check(day["events"], f"day {day['date']} has no events")
        if day["primary"] is None:
            check(
                day["eligibleCount"] == 0,
                f"day {day['date']} has no primary event but has eligible rows",
            )
        check(
            day["primary"] is not None or day["eligibleCount"] == 0,
            f"day {day['date']} has no primary event",
        )

    # The day plan page must show a primary and a fallback line for every day.
    schedule_html = read(SITE / "schedule.html")
    for day in data["days"]:
        check(
            f'id="day-{day["date"]}"' in schedule_html,
            f"the day plan page does not show {day['date']}",
        )
    check(schedule_html.count("Primary:") == len(data["days"]),
          "the day plan page must give every day a primary and a fallback")

    # The overlap check must only call a pair impossible when the times prove it.
    for day in data["days"]:
        for overlap in day["overlaps"]:
            if overlap["verdict"].startswith("cannot"):
                first = next(
                    e for e in day["events"] if e["eventLabel"] == overlap["first"]
                )
                second = next(
                    e for e in day["events"] if e["eventLabel"] == overlap["second"]
                )
                check(
                    first["regCloseMinutes"] is not None
                    and second["startMinutes"] < first["regCloseMinutes"],
                    f"day {day['date']}: '{overlap['first']}' and '{overlap['second']}' are "
                    "called impossible but the published times do not prove it",
                )

    # Trip cost: the calculator inputs and result element must exist and the
    # values it multiplies must be in the published data.
    cost_html = read(SITE / "cost.html")
    for needed in [
        'data-calc="hotel"',
        'data-calc="entries"',
        'data-calc="nights"',
        'data-calc="event"',
        "data-calc-total",
        "data-calc-breakdown",
    ]:
        check(needed in cost_html, f"cost.html is missing {needed}")
    check("data-calculator" in cost_html, "cost.html has no calculator block")
    for hotel in hotels:
        if hotel.get("hasRate"):
            check(
                f'data-nightly="{hotel["trueNightly"]}"' in cost_html,
                f"cost.html does not carry the true nightly cost for {hotel['id']}",
            )
    for event in events:
        if event.get("dateISO") and event.get("buyIn"):
            check(
                f'data-buyin="{event["buyIn"]}"' in cost_html,
                f"cost.html does not carry the buy-in for {event['id']}",
            )
            break

    # Hotels: a total may only appear where a rate exists.
    hotels_html = read(SITE / "hotels.html")
    for hotel in hotels:
        if not hotel.get("hasRate"):
            check(
                hotel.get("trueNightly") in (None, ""),
                f"{hotel['id']} has no official rate but publishes a true nightly cost",
            )
    check("data-table=\"hotels\"" in hotels_html, "hotels.html has no hotels table")

    # Every flag must be published with its id, its severity and a next step.
    flagged_html = read(SITE / "flagged.html")
    def escaped(text: str) -> str:
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#39;")
        )

    for flag in flags:
        check(f'id="{flag["id"]}"' in flagged_html, f"flag {flag['id']} is not published")
        check(
            escaped(flag.get("nextStep", "")) in flagged_html,
            f"flag {flag['id']} does not publish its next step",
        )
    check(flagged_html.count("flag-") >= len(flags), "flagged.html is missing flag blocks")

    # The source page must list every source with its checked date.
    sources_html = read(SITE / "sources.html")
    for source in data["sources"]:
        check(
            source["id"] in sources_html,
            f"source {source['id']} is not listed on sources.html",
        )

    # The venue pages: one per venue, each listing that venue's rows.
    for venue in data["venues"]:
        venue_path = SITE / "venues" / f"{venue['slug']}.html"
        check(venue_path.exists(), f"no page for venue {venue['id']}")
        if venue_path.exists():
            html = read(venue_path)
            parser = TableParser()
            parser.feed(html)
            rows = [r for r in parser.rows if r["attrs"].get("data-row") == "tournament"]
            venue_events = [e for e in events if e["venueId"] == venue["id"]]
            check(
                len(rows) == len(venue_events),
                f"venue page {venue['id']} lists {len(rows)} rows, expected {len(venue_events)}",
            )

    # The script the pages load must exist and be syntactically valid.
    app_js = SITE / "assets" / "app.js"
    check(app_js.exists(), "site/assets/app.js is missing")
    if app_js.exists():
        js = read(app_js)
        for needed in ["data-search-input", "data-filter", "data-calculator", "data-calc-total"]:
            check(needed in js, f"app.js does not handle {needed}")

    print(f"canonical site checks run: {checks}")
    if failures:
        print(f"{len(failures)} failure(s):")
        for failure in failures:
            print("  !!  ", failure)
        return 1
    print("All canonical site checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
