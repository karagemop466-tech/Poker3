#!/usr/bin/env python3
"""Verification for the canonical dashboard in site/.

Checks, in order:
  1. data.json parses and has the expected sections.
  2. Every tournament row carries at least one official source link, and every
     rule excerpt carries its own source and retrieval date.
  3. Every source link is on a venue-controlled or property-controlled domain.
  4. A row with a blank fee or guarantee is marked unverified, partial or in
     conflict, so a blank is never a silent hole.
  5. Every hotel row carries a source, and a computed true nightly cost matches
     the published components it claims to use.
  6. Every flag carries a source link.
  7. Day-plan rows are explicitly provisional sheet-screened candidates with
     confirmed fees/guarantees; they are not treated as strict-entry eligible
     without a written max-one-entry rule.
  8. Every local link in every published HTML page resolves to a file that
     exists, and every page loads the shared script.
"""
from __future__ import annotations

import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"

OFFICIAL_HOSTS = (
    "venetianlasvegas.com",
    "wynnlasvegas.com",
    "wynnresorts.com",
    "cdn.wynnresorts.com",
    "bellagio.mgmresorts.com",
    "mgmgrand.mgmresorts.com",
    "mgmresorts.com",
    "caesars.com",
    "aria.mgmresorts.com",
    "google.com",
    # Clark County government schedule of combined transient lodging rates (Appendix III),
    # the governing tax schedule for the unincorporated Strip properties.
    "clarkcountynv.gov",
    # MGM Resorts' own content delivery host, linked from the official resort pages.
    "assets.contentstack.io",
    # Resorts World Las Vegas, the property's own site (poker-room page reference, flag F80).
    "rwlasvegas.com",
)

PAGES = (
    "index.html", "tournaments.html", "venues.html", "browse.html", "schedule.html",
    "hotels.html", "questions.html", "suggestions.html", "flagged.html", "sources.html", "search.html",
    "ranking.html",
)

# Detailed pages that carry their own data attributes instead of data-page.
DETAIL_PAGES = (
    "venues/index.html", "venues/venetian.html", "venues/wynn.html", "venues/others.html",
    "calculator.html",
)

UNVERIFIED_STATUSES = {"not-verified", "source-conflict", "partial", "not-allowed"}


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []
        self.scripts: list[str] = []
        self.hooks: list[str] = []
        self.page: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        a = dict(attrs)
        if tag == "a" and a.get("href"):
            self.links.append(a["href"])
        if tag == "script" and a.get("src"):
            self.scripts.append(a["src"])
        if tag == "body" and a.get("data-page"):
            self.page = a["data-page"]
        for key, value in attrs:
            if key.startswith("data-"):
                self.hooks.append(key)


def fail(message: str, errors: list[str]) -> None:
    errors.append(message)


def official(url: str) -> bool:
    if not url.startswith("https://"):
        return False
    host = urlparse(url).netloc.lower()
    return any(host == h or host.endswith("." + h) for h in OFFICIAL_HOSTS)


def main() -> int:
    errors: list[str] = []
    data = json.loads((SITE / "data.json").read_text(encoding="utf-8"))

    for key in ("events", "hotels", "routes", "sources", "flags", "questions",
                "suggestions", "venues", "categories", "trip", "dayPlan"):
        if key not in data:
            fail(f"data.json is missing the '{key}' section", errors)

    events = data["events"]
    if not events:
        fail("data.json has no tournament rows", errors)
    for collection in ("events", "hotels", "routes"):
        for index, row in enumerate(data.get(collection, []), start=1):
            if not row.get("lastChecked"):
                fail(f"{collection} row {index} has no lastChecked date", errors)
    for index, row in enumerate(data.get("rateLog", []), start=1):
        if not row.get("observedOn"):
            fail(f"rateLog row {index} has no observation date", errors)

    ids = set()
    for e in events:
        eid = e.get("id")
        if eid in ids:
            fail(f"duplicate event id: {eid}", errors)
        ids.add(eid)
        for key in ("scheduleUrl", "structureUrl"):
            url = e.get(key) or ""
            if url and not official(url):
                fail(f"{eid}: {key} is not an official URL: {url}", errors)
        if not (e.get("scheduleUrl") or e.get("structureUrl")):
            fail(f"{eid}: no official source link on the row", errors)
        rules = e.get("rules") or {}
        if not rules:
            fail(f"{eid}: no entry-rule records", errors)
        for rule, body in rules.items():
            if not body.get("source"):
                fail(f"{eid}: rule '{rule}' has no source", errors)
            elif not official(body["source"]):
                fail(f"{eid}: rule '{rule}' source is not official: {body['source']}", errors)
            if not body.get("excerpt"):
                fail(f"{eid}: rule '{rule}' has no excerpt", errors)
            if not body.get("retrieved"):
                fail(f"{eid}: rule '{rule}' has no retrieval date", errors)
        statuses = {b.get("status") for b in rules.values()}
        if not e.get("buyIn"):
            if not (statuses & {"not-verified", "source-conflict", "partial"}):
                fail(f"{eid}: blank entry fee but no rule is marked unverified", errors)
            if not e.get("note"):
                fail(f"{eid}: blank entry fee and no note explaining it", errors)
        if not e.get("guarantee"):
            if not (statuses & {"not-verified", "source-conflict", "partial", "not-cash-tournament"}) and not e.get("note"):
                fail(f"{eid}: blank guarantee and no note explaining it", errors)
        if e.get("singleEntry") and e.get("entryType") != "none":
            fail(f"{eid}: singleEntry flag does not match the entry type", errors)
        if e.get("entryType") == "none" and e.get("category") == "extra":
            fail(f"{eid}: single-entry row placed in the extra-spend category", errors)

    for h in data["hotels"]:
        if not h.get("source") or not official(h["source"]):
            fail(f"hotel {h.get('id')}: missing or non-official source", errors)
        if h.get("trueNightlyLow"):
            expected = round((h["baseRateFloor"] + h["resortFee"]) * (1 + h["taxRate"] / 100), 2)
            if abs(expected - h["trueNightlyLow"]) > 0.01:
                fail(f"hotel {h.get('id')}: true nightly cost {h['trueNightlyLow']} != {expected}", errors)
        elif not h.get("status"):
            fail(f"hotel {h.get('id')}: no true nightly cost and no status note", errors)

    # --- verification dates and the published cost model -----------------
    for e in events:
        if not e.get("lastChecked"):
            fail(f"event {e.get('id')}: no lastChecked date", errors)
        if not e.get("lastVerified"):
            fail(f"event {e.get('id')}: no lastVerified date", errors)
    for h in data["hotels"]:
        if not h.get("lastVerified"):
            fail(f"hotel {h.get('id')}: no lastVerified date", errors)
    for r in data.get("rateLog", []):
        if not r.get("observedOn"):
            fail("rateLog row without observedOn date", errors)
        if not r.get("quoteType"):
            fail("rateLog row without a quoteType", errors)

    model = data.get("tripCostModel") or {}
    if not model:
        fail("no tripCostModel published", errors)
    else:
        nightly = round((model["roomRatePerNight"] + model["resortFeePerNight"])
                        * (1 + model["taxPct"] / 100), 2)
        if abs(nightly - model["trueCostPerNight"]) > 0.01:
            fail(f"tripCostModel: true nightly {model['trueCostPerNight']} != {nightly}", errors)
        # The tournament total is the exact sum of the chosen buy-ins, not entries x a
        # rounded mean. Seven primaries summing to $2,600 have a mean of $371.428571...,
        # so entries x buyIn prints $2,600.01. Check the exact sum when it is published.
        entry_basis = model.get("primaryBuyInSum")
        if not isinstance(entry_basis, (int, float)):
            entry_basis = model["entries"] * model["buyIn"]
        total = round(entry_basis + model["nights"] * model["trueCostPerNight"]
                      + model["parkingTotal"], 2)
        if abs(total - model["tripTotal"]) > 0.01:
            fail(f"tripCostModel: trip total {model['tripTotal']} != entries x buy-in + nights x nightly + parking ({total})",
                 errors)
        if model["tripTotal"] != round(model["tournamentTotal"] + model["lodgingTotal"] + model["parkingTotal"], 2):
            fail("tripCostModel: components do not add up to the published total", errors)
        for key in ("startingRate", "resortFee", "tax", "parking"):
            if not official(model.get("sources", {}).get(key, "")):
                fail(f"tripCostModel: source '{key}' is missing or not official", errors)
        if not any("starting rate" in str(model.get("basis", "")).lower() or
                   "floor" in str(model.get("basis", "")).lower() for _ in [0]):
            fail("tripCostModel: basis must state that the figure is a floor, not a quote", errors)

    # The transcription file must exist and cover the rows it claims to cover.
    trans = SITE / "data" / "venetian_pdf_rows.json"
    if not trans.exists():
        fail("site/data/venetian_pdf_rows.json is missing", errors)
    else:
        doc = json.loads(trans.read_text(encoding="utf-8"))
        ids = {e["id"] for e in events}
        for row in doc.get("rows", []):
            if row.get("eventId") not in ids:
                fail(f"transcription row {row.get('eventId')} does not exist in data.json", errors)
        if len(doc.get("rows", [])) < 40:
            fail("transcription covers fewer than 40 rows", errors)

    for f in data["flags"]:
        if not f.get("source"):
            fail(f"flag {f.get('id')}: no source", errors)
        elif not official(f["source"]):
            # A flag about this site's own publishing or its own automation cannot
            # cite a casino page: the evidence is the repository or its Actions
            # runs. Those flags must say so explicitly with area "Publishing" or
            # "Monitoring" and cite a GitHub URL, so an uncited data flag can
            # never slip through this exemption.
            repo_hosted = str(f["source"]).startswith("https://github.com/karagemop466-tech/Poker3")
            if not (f.get("area") in {"Publishing", "Monitoring"} and repo_hosted):
                fail(f"flag {f.get('id')}: non-official source outside the publishing/monitoring exemption", errors)
        if not f.get("detail"):
            fail(f"flag {f.get('id')}: no detail", errors)

    for s in data["sources"]:
        if not official(s.get("url", "")):
            fail(f"source {s.get('id')}: not an official URL", errors)
        if not s.get("checked"):
            fail(f"source {s.get('id')}: no check date", errors)

    by_id = {e["id"]: e for e in events}
    for day in data["dayPlan"]:
        if day["primary"]:
            e = by_id.get(day["primary"])
            if not e:
                fail(f"plan {day['date']}: primary id not in events", errors)
            else:
                if e["entryType"] != "none":
                    fail(f"plan {day['date']}: primary candidate has printed extra-entry terms", errors)
                single_rule = (e.get("rules") or {}).get("singleEntry") or {}
                if single_rule.get("status") != "single-entry-on-sheet":
                    fail(f"plan {day['date']}: primary candidate has no sheet-screening evidence", errors)
                if not e.get("buyIn") or not e.get("guarantee"):
                    fail(f"plan {day['date']}: primary has no confirmed fee and guarantee", errors)
                if e.get("eligibility"):
                    fail(f"plan {day['date']}: primary is restricted: {e['eligibility']}", errors)
        if day["fallback"] and day["fallback"] not in by_id:
            fail(f"plan {day['date']}: fallback id not in events", errors)
        if not day.get("fallbackReason"):
            fail(f"plan {day['date']}: no reason recorded for the fallback choice", errors)

    for page in PAGES:
        path = SITE / page
        if not path.exists():
            fail(f"missing page: {page}", errors)
            continue
        parser = LinkParser()
        parser.feed(path.read_text(encoding="utf-8"))
        if parser.page is None:
            fail(f"{page}: no data-page attribute on <body>", errors)
        if "assets/app.js" not in parser.scripts:
            fail(f"{page}: does not load assets/app.js", errors)
        for link in parser.links:
            if link.startswith(("http://", "https://", "#", "mailto:", "tel:", "data:", "javascript:")):
                if link.startswith("http://"):
                    fail(f"{page}: insecure link {link}", errors)
                continue
            target = (path.parent / link.split("#")[0].split("?")[0]).resolve()
            if not target.exists():
                fail(f"{page}: broken local link {link}", errors)

    for page in DETAIL_PAGES:
        path = SITE / page
        if not path.exists():
            fail(f"missing detail page: {page}", errors)
            continue
        parser = LinkParser()
        parser.feed(path.read_text(encoding="utf-8"))
        for link in parser.links:
            if link.startswith(("http://", "https://", "#", "mailto:", "tel:", "data:", "javascript:")):
                if link.startswith("http://"):
                    fail(f"{page}: insecure link {link}", errors)
                continue
            target = (path.parent / link.split("#")[0].split("?")[0]).resolve()
            if not target.exists():
                fail(f"{page}: broken local link {link}", errors)

    for asset in ("assets/app.js", "assets/site.css", "assets/venue.js"):
        if not (SITE / asset).exists():
            fail(f"missing asset {asset}", errors)

    print(f"events: {len(events)}  hotels: {len(data['hotels'])}  routes: {len(data['routes'])}  "
          f"sources: {len(data['sources'])}  flags: {len(data['flags'])}  "
          f"plan days: {len(data['dayPlan'])}  pages: {len(PAGES) + len(DETAIL_PAGES)}")
    if errors:
        print(f"\n{len(errors)} problem(s):")
        for e in errors:
            print(" -", e)
        return 1
    print("verification passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
