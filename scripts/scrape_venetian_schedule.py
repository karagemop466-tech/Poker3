#!/usr/bin/env python3
"""Scrape the official Venetian DeepStack Extravaganza IV schedule page and report
which rows have changed.

The scraper reads the venue's own event page, which publishes a row per tournament with
the date, start time, event number, event name, guarantee and a link to that row's
structure sheet. It compares what it finds with the curated rows in
`data/venetian_dse_iv.json` and prints the difference.

It never edits the curated file. A human reads the official page, checks the difference
against the linked structure sheet, and only then updates `data/venetian_dse_iv.json` and
re-runs the build. That is deliberate: the scraper is a change signal, not an extractor
that silently rewrites published values.

Run:
  python3 scripts/scrape_venetian_schedule.py            # report differences
  python3 scripts/scrape_venetian_schedule.py --json     # machine-readable output
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import re
import sys
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCHEDULE_URL = (
    "https://www.venetianlasvegas.com/resort/casino/poker/"
    "deepstack-extravaganza-poker-tournament/dse-nov-2026.html"
)
CURATED = ROOT / "data" / "venetian_dse_iv.json"
USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0 Safari/537.36"
)

MONTHS = {
    "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
    "july": 7, "august": 8, "september": 9, "october": 10, "november": 11, "december": 12,
}

ROW_PATTERN = re.compile(
    r"<tr[^>]*>\s*<td[^>]*>\s*(?P<date>[A-Za-z]+,\s*[A-Za-z]+\s+\d{1,2},\s*\d{4})\s*</td>"
    r"\s*<td[^>]*>\s*(?P<time>\d{1,2}:\d{2}\s*[AP]M)\s*</td>"
    r"\s*<td[^>]*>\s*(?P<event>\d+)\s*</td>"
    r"\s*<td[^>]*>(?P<name>.*?)</td>"
    r"(?P<rest>.*?)</tr>",
    re.I | re.S,
)
SHEET_PATTERN = re.compile(r"dse_nov_2026-structure_(\d+)\.pdf")
GUARANTEE_PATTERN = re.compile(r"\$([\d.,]+)\s*(GTD|Mill)\b", re.I)


def strip_tags(fragment: str) -> str:
    text = re.sub(r"(?s)<[^>]+>", " ", fragment)
    text = text.replace("&nbsp;", " ").replace("&amp;", "&").replace("&#39;", "'")
    return re.sub(r"\s+", " ", text).strip()


def fetch(url: str, timeout: int = 40) -> str:
    request = urllib.request.Request(
        url, headers={"User-Agent": USER_AGENT, "Accept": "text/html,*/*"}
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read(8 * 1024 * 1024 + 1).decode("utf-8", "replace")


def parse_rows(html: str) -> list[dict]:
    rows = []
    for match in ROW_PATTERN.finditer(html):
        date_text = match.group("date")
        date_match = re.match(
            r"[A-Za-z]+,\s*([A-Za-z]+)\s+(\d{1,2}),\s*(\d{4})", date_text
        )
        if not date_match:
            continue
        month = MONTHS.get(date_match.group(1).lower())
        if not month:
            continue
        date = f"{date_match.group(3)}-{month:02d}-{int(date_match.group(2)):02d}"
        rest = match.group("rest")
        sheet = SHEET_PATTERN.search(rest)
        name = strip_tags(match.group("name"))
        guarantee = GUARANTEE_PATTERN.search(name)
        rows.append(
            {
                "date": date,
                "time": re.sub(r"\s+", " ", match.group("time")).upper(),
                "eventNumber": match.group("event"),
                "name": name,
                "structureSheet": int(sheet.group(1)) if sheet else "",
                "guarantee": guarantee.group(1).replace(",", "") if guarantee else "",
            }
        )
    return rows


def flight_label(name: str) -> str:
    """The flight or continuation suffix in an official event name."""
    upper = name.upper()
    if "DAY 2 RESTART" in upper:
        return "Day 2 Restart"
    if "DAY 3 RESTART" in upper:
        return "Day 3 Restart"
    if "FINAL TABLE" in upper:
        return "Final Table"
    m = re.search(r"\b(1[A-F])\b", upper)
    if m:
        return m.group(1)
    if "(2DAY)" in upper:
        return "Day 1"
    return ""


def split_label(label: str) -> tuple[str, str]:
    """'26 1A' -> ('26', '1A');  '1A' -> ('1', '1A');  '39 Day 1' -> ('39', 'Day 1')."""
    match = re.match(r"^(\d+)\s*(.*)$", label.strip())
    if not match:
        return label.strip(), ""
    number, rest = match.group(1), match.group(2).strip()
    if not rest:
        return number, ""
    if re.fullmatch(r"[A-F]", rest):
        # '1A'..'1F' are event 1's flights: the whole label is the flight.
        return number, number + rest
    return number, rest


def compare(scraped: list[dict], curated: list[dict]) -> list[dict]:
    """Every difference between the live page and the curated rows."""
    curated_by_key = {}
    for row in curated:
        event_number, flight = split_label(row.get("eventLabel", ""))
        curated_by_key[(row["date"], event_number, flight)] = row

    differences = []
    seen = set()
    for row in scraped:
        flight = flight_label(row["name"])
        k = (row["date"], row["eventNumber"], flight)
        seen.add(k)
        current = curated_by_key.get(k)
        if current is None:
            differences.append(
                {
                    "kind": "added on the official page",
                    "date": row["date"],
                    "event": row["eventNumber"],
                    "flight": flight,
                    "detail": row["name"],
                    "url": SCHEDULE_URL,
                }
            )
            continue
        if row["time"] != current.get("time"):
            differences.append(
                {
                    "kind": "start time changed",
                    "date": row["date"],
                    "event": row["eventNumber"],
                    "flight": flight,
                    "was": current.get("time"),
                    "now": row["time"],
                    "url": SCHEDULE_URL,
                }
            )
        sheet_match = re.search(r"structure_(\d+)\.pdf", current.get("structureSheet", ""))
        if sheet_match and row["structureSheet"] and int(sheet_match.group(1)) != row["structureSheet"]:
            differences.append(
                {
                    "kind": "structure sheet changed",
                    "date": row["date"],
                    "event": row["eventNumber"],
                    "flight": flight,
                    "was": int(sheet_match.group(1)),
                    "now": row["structureSheet"],
                    "url": SCHEDULE_URL,
                }
            )
    for k, current in curated_by_key.items():
        if k not in seen:
            differences.append(
                {
                    "kind": "no longer on the official page",
                    "date": current.get("date"),
                    "event": current.get("eventLabel"),
                    "detail": current.get("name"),
                    "url": SCHEDULE_URL,
                }
            )
    return differences


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    args = parser.parse_args()

    try:
        html = fetch(SCHEDULE_URL)
    except Exception as exc:
        print(f"could not read the official page: {type(exc).__name__}: {str(exc)[:200]}")
        return 1

    scraped = parse_rows(html)
    curated = json.loads(CURATED.read_text(encoding="utf-8"))["events"]
    differences = compare(scraped, curated)
    checked_at = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()

    if args.json:
        print(
            json.dumps(
                {
                    "checkedAt": checked_at,
                    "url": SCHEDULE_URL,
                    "scrapedRowCount": len(scraped),
                    "curatedRowCount": len(curated),
                    "differences": differences,
                },
                indent=2,
                ensure_ascii=False,
            )
        )
        return 1 if differences else 0

    print(f"Checked {SCHEDULE_URL}")
    print(f"Checked at {checked_at}")
    print(f"Rows on the official page: {len(scraped)}   rows in the curated data: {len(curated)}")
    if not differences:
        print("\nNo differences. The curated rows still match the official schedule page.")
        return 0
    print(f"\n{len(differences)} difference(s) to review by hand:")
    for difference in differences:
        print(f"  - {difference['kind']}: {difference.get('date')} event {difference.get('event')}"
              + (f" {difference['flight']}" if difference.get("flight") else ""))
        if difference.get("was") is not None:
            print(f"      was {difference['was']}  now {difference.get('now')}")
        if difference.get("detail"):
            print(f"      {difference['detail']}")
        print(f"      {difference['url']}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
