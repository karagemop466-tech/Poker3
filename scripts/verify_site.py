#!/usr/bin/env python3
"""Offline integrity checks for the static research dashboard."""
import json
import pathlib
import re
import urllib.parse

ROOT = pathlib.Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
OFFICIAL_DOMAINS = {
    "www.venetianlasvegas.com",
    "cdn.wynnresorts.com",
    "www.wynnlasvegas.com",
    "aria.mgmresorts.com",
}

with (SITE / "data.json").open(encoding="utf-8") as f:
    data = json.load(f)
assert data["asOf"] == "2026-11-16"
assert data["tournaments"], "Expected official tournament records"
assert data["hotels"], "Expected lodging records"

for index, row in enumerate(data["tournaments"], start=1):
    for field in ("date", "time", "venue", "event", "entryStatus", "schedule"):
        assert row.get(field), f"Tournament row {index}: missing {field}"
    assert "buyIn" in row and "guarantee" in row, f"Tournament row {index}: unknown values must be explicit blanks"
    for field in ("schedule", "structure", "confirmSource"):
        if row.get(field):
            url = urllib.parse.urlparse(row[field])
            assert url.scheme == "https" and url.hostname in OFFICIAL_DOMAINS, (
                f"Tournament row {index}: non-official {field} URL {row[field]}"
            )

for index, row in enumerate(data["hotels"], start=1):
    for field in ("name", "venue", "resortFee", "trueNightly", "source", "feeSource", "taxSource"):
        assert field in row, f"Hotel row {index}: missing {field} key"
    assert row["trueNightly"] == "", "Do not populate a total without a date-specific quote"
    for field in ("source", "feeSource", "taxSource"):
        url = urllib.parse.urlparse(row[field])
        assert url.scheme == "https" and url.hostname in OFFICIAL_DOMAINS, (
            f"Hotel row {index}: non-official {field} URL {row[field]}"
        )

for page in SITE.glob("*.html"):
    text = page.read_text(encoding="utf-8")
    ids = set(re.findall(r'\bid="([^"]+)"', text))
    for href in re.findall(r'href="([^"]+)"', text):
        if href.startswith(("https://", "mailto:", "tel:")):
            continue
        if href.startswith("#"):
            assert href[1:] in ids, f"{page.name}: missing fragment {href}"
            continue
        path = urllib.parse.urlparse(href).path
        assert (page.parent / path).resolve().exists(), f"{page.name}: broken local link {href}"
    assert "assets/site.css" in text and "assets/app.js" in text, f"{page.name}: shared assets not linked"

print(
    f"PASS: {len(data['tournaments'])} official-linked tournament rows, "
    f"{len(data['hotels'])} hotel rows with blank unquoted totals, "
    f"and {len(list(SITE.glob('*.html')))} pages with valid local links."
)
