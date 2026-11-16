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
    "bellagio.mgmresorts.com",
    "assets.contentstack.io",
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
    assert re.match(r"^\d{4}-\d{2}-\d{2}$", row.get("lastChecked", "")), (
        f"Tournament row {index}: lastChecked must be a date"
    )
    rules = row.get("rules", {})
    assert isinstance(rules, dict), f"Tournament row {index}: rules must be an object"
    for key in ("singleEntry", "reEntry", "addOn", "fee"):
        assert key in rules, f"Tournament row {index}: rules missing {key}"
        assert "retrievalDate" in rules[key], f"Tournament row {index}: rules.{key} missing retrievalDate"
    fr = row.get("feeRatio", {})
    assert "value" in fr and "note" in fr, f"Tournament row {index}: feeRatio missing value/note"
    assert isinstance(row.get("overlapNote", ""), str), f"Tournament row {index}: overlapNote must be a string"
    for field in ("schedule", "structure", "confirmSource"):
        if row.get(field):
            url = urllib.parse.urlparse(row[field])
            assert url.scheme == "https" and url.hostname in OFFICIAL_DOMAINS, (
                f"Tournament row {index}: non-official {field} URL {row[field]}"
            )

for index, row in enumerate(data["hotels"], start=1):
    for field in ("name", "venue", "resortFee", "trueNightly", "source", "feeSource", "taxSource", "lastChecked"):
        assert field in row, f"Hotel row {index}: missing {field} key"
    assert row["trueNightly"] == "", "Do not populate a total without a date-specific quote"
    assert re.match(r"^\d{4}-\d{2}-\d{2}$", row.get("lastChecked", "")), (
        f"Hotel row {index}: lastChecked must be a date"
    )
    rate_log = row.get("rateLog", [])
    assert isinstance(rate_log, list) and rate_log, f"Hotel row {index}: rateLog must be a non-empty dated log"
    for entry in rate_log:
        for field in ("date", "rate", "source"):
            assert field in entry, f"Hotel row {index}: rateLog entry missing {field}"
        assert re.match(r"^\d{4}-\d{2}-\d{2}$", entry.get("date", "")), (
            f"Hotel row {index}: rateLog date must be a date"
        )
    for field in ("source", "feeSource", "taxSource", "feeSourceAlt"):
        if row.get(field):
            url = urllib.parse.urlparse(row[field])
            assert url.scheme == "https" and url.hostname in OFFICIAL_DOMAINS, (
                f"Hotel row {index}: non-official {field} URL {row[field]}"
            )

# Dated check logs produced by the scheduled monitor
for path, shape in (
    (ROOT / "data" / "source-checks.json", ("checks",)),
    (ROOT / "data" / "source-changes.json", ("changes",)),
):
    assert path.exists(), f"Missing {path.name} (run scripts/monitor_sources.py)"
    log = json.loads(path.read_text(encoding="utf-8"))
    assert "generatedAt" in log, f"{path.name}: missing generatedAt"
    for key in shape:
        assert key in log and isinstance(log[key], list), f"{path.name}: missing {key} list"

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
