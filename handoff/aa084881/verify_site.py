#!/usr/bin/env python3
"""Offline integrity checks for the published site (site/).

Checks: data.json shape and official links; every flag ID referenced exists; every
table row on every page links at least one official https URL; local links and
fragments resolve; shared assets are linked; no page claims an unverified status.
"""
import html.parser
import json
import pathlib
import re
import sys
import urllib.parse

ROOT = pathlib.Path(__file__).resolve().parent
SITE = ROOT / "out"
OFFICIAL = {
    "www.venetianlasvegas.com", "cdn.wynnresorts.com", "www.wynnlasvegas.com",
    "bellagio.mgmresorts.com", "aria.mgmresorts.com", "assets.contentstack.io",
    # Attempted official property pages (flag F30). Recorded as attempts only.
    "www.caesars.com", "mgmgrand.com", "www.goldennugget.com", "www.rwlasvegas.com", "www.circalasvegas.com",
}
ASOF = "2026-11-16"
errors = []


def check(cond, msg):
    if not cond:
        errors.append(msg)


def official(url):
    p = urllib.parse.urlparse(url)
    return p.scheme == "https" and p.hostname in OFFICIAL


data = json.loads((ROOT / "data.json").read_text(encoding="utf-8"))
check(data.get("asOf") == ASOF, "data.json asOf must be 2026-11-16")
flags = set(data.get("flags", {}).keys())
check(len(flags) >= 20, "flag register too short")
cats = {"main", "bounty", "unclear", "excluded"}
for i, r in enumerate(data["tournaments"], 1):
    tag = f"tournament row {i} (#{r.get('id')})"
    check(r.get("category") in cats, f"{tag}: bad category")
    for k in ("buyIn", "guarantee", "houseFee", "prizePool", "lastChecked", "scheduleUrl", "structureUrl", "flags"):
        check(k in r, f"{tag}: missing key {k}")
    check(official(r.get("scheduleUrl", "")), f"{tag}: non-official schedule URL")
    if r.get("structureUrl"):
        check(official(r["structureUrl"]), f"{tag}: non-official structure URL")
    if r.get("guarantee") is not None:
        check(r.get("buyIn") is not None, f"{tag}: guarantee without confirmed buy-in")
    for f in r.get("flags", []):
        check(f in flags, f"{tag}: unknown flag {f}")
    if r.get("category") == "main":
        check(r.get("buyIn") is not None, f"{tag}: main-list row without buy-in")
        check(r.get("lastChecked") == ASOF, f"{tag}: main-list row not checked on {ASOF}")
for h in data["hotels"]:
    for url in h.get("sources", []):
        check(official(url), f"hotel {h['id']}: non-official source {url}")
    for f in h.get("flags", []):
        check(f in flags, f"hotel {h['id']}: unknown flag {f}")
    if h.get("trueNightly") is not None:
        check(h.get("quoteDate") and h.get("checkoutTotal") is not None,
              f"hotel {h['id']}: trueNightly needs a dated official quote")
    check(h.get("walkingMinutes") in ("", None), f"hotel {h['id']}: walking time must stay blank (no official source)")
for f, rec in data.get("flags", {}).items():
    for u in rec.get("sources", []):
        check(official(u) or u.startswith("https://"), f"flag {f}: non-https source")
for s in data.get("sources", []):
    check(official(s["url"]), f"monitor source {s['id']} is not official")
srcs = json.loads((SITE / "sources.json").read_text(encoding="utf-8"))
check(all(official(s["url"]) and s["kind"] == "official" for s in srcs["sources"]), "sources.json: non-official entry")


class Rows(html.parser.HTMLParser):
    """Collects <tr> rows inside <tbody> and the href/id/src values on each page."""

    def __init__(self):
        super().__init__()
        self.in_tbody = False
        self.row = None
        self.rows = []
        self.hrefs = []
        self.ids = set()
        self.srcs = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.ids.add(a["id"])
        if tag == "a" and a.get("href"):
            self.hrefs.append(a["href"])
        if tag == "link" and a.get("href"):
            self.hrefs.append(a["href"])
        if tag == "script" and a.get("src"):
            self.srcs.append(a["src"])
        if tag == "tbody":
            self.in_tbody = True
        if tag == "tr" and self.in_tbody:
            self.row = []
            self.rows.append((self.row, []))
            self._cur = self.rows[-1][1]

    def handle_endtag(self, tag):
        if tag == "tbody":
            self.in_tbody = False

    def handle_data(self, data):
        pass


pages = sorted(SITE.rglob("*.html"))
check(len(pages) >= 14, "expected the full page set")
for page in pages:
    if "poker3" in page.relative_to(SITE).parts:
        continue  # companion dashboard is verified by tests/smoke.py
    text = page.read_text(encoding="utf-8")
    parser = Rows()
    parser.feed(text)
    rel = page.relative_to(SITE)
    check("assets/site.css" in text and "assets/app.js" in text, f"{rel}: shared assets not linked")
    check("http://" not in text.replace("https://", ""), f"{rel}: plain http link")
    for href in parser.hrefs:
        if href.startswith(("https://", "mailto:", "tel:")):
            if href.startswith("https://"):
                check(urllib.parse.urlparse(href).hostname, f"{rel}: bad https link {href}")
            continue
        if href.startswith("#"):
            check(href[1:] in parser.ids, f"{rel}: missing fragment {href}")
            continue
        path = urllib.parse.urlparse(href).path
        check((page.parent / path).resolve().exists(), f"{rel}: broken local link {href}")
    # every rendered table row links an official https source
    body_rows = re.findall(r"<tbody>(.*?)</tbody>", text, flags=re.S)
    for tb in body_rows:
        for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", tb, flags=re.S):
            hrefs = re.findall(r"href=[\"']([^\"']+)[\"']", tr)
            ok = any(official(h) or h.startswith("../") or h.startswith("#") or h.endswith(".html")
                     or h.startswith("https://") for h in hrefs)
            if not ok or not any(h.startswith("https://") for h in hrefs):
                errors.append(f"{rel}: table row without an official https link: {re.sub('<[^>]+>', ' ', tr)[:120]}")
            for h in hrefs:
                if h.startswith("https://"):
                    check(official(h), f"{rel}: non-official link in table: {h}")
    check("single-entry confirmed" not in text.lower() and "confirmed single-entry" not in text.lower(),
          f"{rel}: claims single-entry is confirmed")

check(not (SITE / "poker3" / "data" / "__pycache__").exists(), "stray cache in site")

if errors:
    print("FAIL:")
    for e in errors:
        print(" -", e)
    sys.exit(1)
print(f"PASS: {len(data['tournaments'])} event rows, {len(data['hotels'])} hotel rows, "
      f"{len(data['flags'])} flags, {len(pages)} pages with official-linked table rows and valid local links.")
