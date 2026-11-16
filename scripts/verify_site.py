#!/usr/bin/env python3
"""Offline integrity checks for the canonical source-linked dashboard."""
from __future__ import annotations

import json
import pathlib
import re
import urllib.parse
from datetime import date
from html.parser import HTMLParser

ROOT = pathlib.Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
OFFICIAL_HOSTS = {
    "www.venetianlasvegas.com", "cdn.wynnresorts.com", "www.wynnlasvegas.com",
    "reservations.wynnlasvegas.com", "aria.mgmresorts.com", "bellagio.mgmresorts.com",
    "mgmgrand.mgmresorts.com", "assets.contentstack.io", "www.mgmresorts.com",
    "worldpokertour.com", "www.worldpokertour.com", "wptmedia-mig.s3.amazonaws.com",
    "treasureisland.com", "www.treasureisland.com", "www.caesars.com",
}


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.hrefs: list[str] = []
        self.ids: set[str] = set()

    def handle_starttag(self, _tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if values.get("href"):
            self.hrefs.append(values["href"] or "")
        if values.get("src"):
            self.hrefs.append(values["src"] or "")
        if values.get("id"):
            self.ids.add(values["id"] or "")


def load_json(path: pathlib.Path):
    return json.loads(path.read_text(encoding="utf-8"))


def official_url(url: str, description: str) -> None:
    parsed = urllib.parse.urlparse(url)
    assert parsed.scheme == "https" and parsed.hostname in OFFICIAL_HOSTS, f"{description}: non-approved official URL {url}"


def check_local_links() -> int:
    pages = sorted(SITE.glob("*.html")) + sorted((SITE / "venues").glob("*.html"))
    for page in pages:
        text = page.read_text(encoding="utf-8")
        parser = LinkParser()
        parser.feed(text)
        for href in parser.hrefs:
            if href.startswith(("https://", "http://", "mailto:", "tel:", "data:", "javascript:")):
                continue
            if href.startswith("#"):
                assert href[1:] in parser.ids, f"{page.relative_to(ROOT)}: missing fragment {href}"
                continue
            local_path = urllib.parse.urlparse(href).path
            if not local_path:
                continue
            resolved = (page.parent / local_path).resolve()
            assert resolved.is_file(), f"{page.relative_to(ROOT)}: broken local reference {href}"
        assert "data-shell-header" in text and "data-page-content" in text, f"{page.name}: missing app shell mount"
        assert "site.css" in text and "logic.js" in text and "app.js" in text, f"{page.name}: missing shared assets"
    return len(pages)


def main() -> None:
    data = load_json(SITE / "data.json")
    assert data.get("schemaVersion") == 2, "canonical dashboard schemaVersion must be 2"
    assert data.get("asOf") == "2026-11-16"
    assert data["tournaments"], "Expected event rows"
    assert data["hotels"], "Expected hotel rows"
    assert data.get("scheduleCoverage", {}).get("listedRows") == 83, "Expected full 83-row Venetian schedule extraction"
    assert data["scheduleCoverage"].get("eventNumbers") == 64
    assert data["scheduleCoverage"].get("firstDate") == "2026-11-16"
    assert data["scheduleCoverage"].get("lastDate") == "2026-12-23"

    sources = data["officialSources"]
    source_ids = {source["id"] for source in sources}
    source_urls = {source["url"] for source in sources}
    assert len(source_ids) == len(sources), "source IDs must be unique"
    assert len(source_urls) == len(sources), "official-source URLs must be unique"
    for source in sources:
        assert source.get("name") and source.get("kind")
        assert isinstance(source.get("monitor"), bool), f"{source['id']}: monitor must be explicit"
        official_url(source["url"], f"source {source['id']}")
    for flag in data.get("flags", []):
        for source_id in flag.get("sourceIds", []):
            assert source_id in source_ids, f"Flag {flag.get('id')}: missing source ID {source_id}"

    event_ids = set()
    for index, row in enumerate(data["tournaments"], start=1):
        assert row.get("id") and row["id"] not in event_ids, f"Tournament row {index}: missing or duplicate id"
        event_ids.add(row["id"])
        for field in ("date", "time", "venue", "event", "entryStatus", "schedule", "strictStatus", "rules", "sourceIds", "lastChecked"):
            assert field in row, f"Tournament row {index}: missing {field}"
        assert row["strictStatus"] in {"verified", "rejected", "unverified", "conflict"}
        assert isinstance(row.get("tags", []), list)
        for source_id in row["sourceIds"]:
            assert source_id in source_ids, f"Tournament {row['id']}: missing source ID {source_id}"
        for field in ("schedule", "structure", "confirmSource"):
            if row.get(field):
                official_url(row[field], f"Tournament {row['id']} {field}")
                assert row[field] in source_urls, f"Tournament {row['id']} {field} URL not in source register"
        for key in ("entryFeeEvidence", "guaranteeEvidence"):
            assert row.get(key, {}).get("source"), f"Tournament {row['id']}: missing {key} source"
            official_url(row[key]["source"], f"Tournament {row['id']} {key}")
        for name, rule in row["rules"].items():
            assert rule.get("status"), f"Tournament {row['id']}: missing {name} status"
            assert rule.get("source"), f"Tournament {row['id']}: missing {name} evidence source"
            official_url(rule["source"], f"Tournament {row['id']} {name}")
        if row.get("dateISO"):
            date.fromisoformat(row["dateISO"])
        if row["strictStatus"] == "verified":
            assert row["rules"].get("singleEntry", {}).get("status") == "confirmed", f"{row['id']}: strict pass needs explicit single-entry confirmation"
            for rule_name in ("reEntry", "rebuy", "addOn", "paidChipAdvantage"):
                assert row["rules"].get(rule_name, {}).get("status") in {"not-allowed", "not-available", "none", "no"}, f"{row['id']}: strict pass lacks explicit {rule_name} exclusion"

    venetian = [row for row in data["tournaments"] if row.get("venueId") == "venetian"]
    assert len(venetian) == 83
    assert len({row["eventNumber"] for row in venetian}) == 64
    assert sum(row.get("dateEvidence", {}).get("status") != "printed" for row in venetian) == 13
    assert all(row["strictStatus"] == "unverified" for row in venetian), "Do not infer strict-entry eligibility from silence"
    assert sum(row["strictStatus"] == "verified" for row in data["tournaments"]) == 0

    hotel_ids = set()
    for index, hotel in enumerate(data["hotels"], start=1):
        assert hotel.get("id") and hotel["id"] not in hotel_ids, f"Hotel row {index}: missing or duplicate ID"
        hotel_ids.add(hotel["id"])
        for field in ("name", "resortFee", "trueNightly", "baseRate", "source", "feeSource", "taxSource", "lastChecked"):
            assert field in hotel, f"Hotel row {index}: missing {field} key"
        assert hotel["trueNightly"] == "", "Never publish a calculator value as a verified hotel total"
        assert hotel["baseRate"] == "", "No exact-date room quote is verified"
        assert hotel.get("checkoutTotalUsd") is None
        for field in ("source", "feeSource", "taxSource", "bookingSource", "parkingSource"):
            if hotel.get(field):
                official_url(hotel[field], f"Hotel {hotel['id']} {field}")

    stay = data.get("sampleStay", {})
    assert stay.get("userProvided") is False, "Research sample must remain distinguished from traveler dates"
    rate_data = load_json(SITE / "data/hotel-rate-logs.json")
    assert rate_data["schemaVersion"] == 1
    assert len(rate_data["logs"]) == len(data["hotels"])
    assert all(item.get("allInComparable") is False for item in rate_data["logs"])
    assert all(item.get("checkoutTotalUsd") is None for item in rate_data["logs"])
    assert all(item.get("hotelId") in hotel_ids for item in rate_data["logs"])

    monitor = load_json(SITE / "data/source-monitor.json")
    assert monitor["schemaVersion"] == 1
    assert "sources" in monitor and "changes" in monitor and "failures" in monitor
    for source_id, record in monitor["sources"].items():
        assert source_id in source_ids, f"Monitor contains unknown source ID {source_id}"
        official_url(record["url"], f"Monitor source {source_id}")

    pages = check_local_links()
    print(f"PASS: {len(data['tournaments'])} event rows ({len(venetian)} Venetian starts through Dec. 23), {len(sources)} source records, {len(data['hotels'])} hotels with blank unquoted totals, {len(rate_data['logs'])} rate-search logs, and {pages} pages with valid local links. Strict-entry passes: 0.")


if __name__ == "__main__":
    main()
