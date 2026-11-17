#!/usr/bin/env python3
"""Smoke checks for the canonical dashboard in site/.

Dependency free: it parses the published HTML, confirms every page declares its
page type and loads the shared script, and then runs the headless render check
with node when node is available.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"

PAGES = {
    "index.html": "home",
    "tournaments.html": "tournaments",
    "venues.html": "venues",
    "browse.html": "browse",
    "schedule.html": "schedule",
    "hotels.html": "hotels",
    "questions.html": "questions",
    "suggestions.html": "suggestions",
    "flagged.html": "flagged",
    "sources.html": "sources",
    "search.html": "search",
}

# Detailed pages that use their own data attributes instead of data-page.
DETAIL_PAGES = {
    "venues/index.html": [],
    "venues/venetian.html": ["venue-events", "venue-hotels"],
    "venues/wynn.html": ["venue-events", "venue-hotels"],
    "venues/others.html": ["venue-events", "venue-hotels"],
    "calculator.html": ["tripForm"],
}

REQUIRED_HOOKS = {
    "index.html": ["data-stats", "data-trip-card", "data-top-picks", "data-policy"],
    "tournaments.html": ["data-filters", "data-tournament-table", "data-detail"],
    "venues.html": ["data-venue-list"],
    "browse.html": ["data-browse-head", "data-browse-body"],
    "schedule.html": ["data-plan", "data-plan-summary", "data-plan-why"],
    "hotels.html": ["data-hotel-table", "data-rate-log", "data-routes", "data-calculator"],
    "questions.html": ["data-questions"],
    "suggestions.html": ["data-suggestions"],
    "flagged.html": ["data-flags"],
    "sources.html": ["data-sources", "data-rechecks", "data-sheets", "data-feed", "data-autochecks"],
    "search.html": ["data-search-results", "data-search-summary", "data-search-input"],
}


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.page: str | None = None
        self.scripts: list[str] = []
        self.links: list[str] = []
        self.hooks: set[str] = set()
        self.ids: set[str] = set()
        self.title: str | None = None
        self._in_title = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        a = dict(attrs)
        if tag == "body":
            self.page = a.get("data-page")
        if tag == "script" and a.get("src"):
            self.scripts.append(a["src"])
        if tag == "a" and a.get("href"):
            self.links.append(a["href"])
        if tag == "title":
            self._in_title = True
        if a.get("id"):
            self.ids.add(a["id"])
        for key in attrs:
            name = key[0]
            if name.startswith("data-"):
                self.hooks.add(name)

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title = (self.title or "") + data


def main() -> int:
    errors: list[str] = []
    for page, expected in PAGES.items():
        path = SITE / page
        if not path.exists():
            errors.append(f"{page}: missing")
            continue
        parser = PageParser()
        parser.feed(path.read_text(encoding="utf-8"))
        if parser.page != expected:
            errors.append(f"{page}: data-page is {parser.page!r}, expected {expected!r}")
        if "assets/app.js" not in parser.scripts:
            errors.append(f"{page}: does not load assets/app.js")
        if not parser.title:
            errors.append(f"{page}: no title")
        for hook in REQUIRED_HOOKS.get(page, []):
            if hook not in parser.hooks:
                errors.append(f"{page}: missing {hook} hook")
        for link in parser.links:
            if link.startswith(("http://", "https://", "#", "mailto:", "tel:", "data:", "javascript:")):
                continue
            target = (path.parent / link.split("#")[0].split("?")[0]).resolve()
            if not target.exists():
                errors.append(f"{page}: broken local link {link}")
            if urlparse(link).scheme:
                errors.append(f"{page}: unexpected scheme on {link}")

    for page, hooks in DETAIL_PAGES.items():
        path = SITE / page
        if not path.exists():
            errors.append(f"{page}: missing")
            continue
        parser = PageParser()
        parser.feed(path.read_text(encoding="utf-8"))
        for hook in hooks:
            if hook not in parser.ids:
                errors.append(f"{page}: missing id={hook}")
        for link in parser.links:
            if link.startswith(("http://", "https://", "#", "mailto:", "tel:", "data:", "javascript:")):
                continue
            target = (path.parent / link.split("#")[0].split("?")[0]).resolve()
            if not target.exists():
                errors.append(f"{page}: broken local link {link}")

    index_text = (SITE / "venues" / "index.html").read_text(encoding="utf-8")
    for target in ("venetian.html", "wynn.html", "others.html"):
        if target not in index_text:
            errors.append(f"venues/index.html: does not link {target}")

    data = json.loads((SITE / "data.json").read_text(encoding="utf-8"))
    if data.get("asOf") != "2026-11-17":
        errors.append(f"data.json: unexpected as-of date {data.get('asOf')!r}")
    if data.get("snapshot") != "2026-11-16":
        errors.append(f"data.json: unexpected source snapshot date {data.get('snapshot')!r}")
    if not data.get("rechecks"):
        errors.append("data.json: no dated source re-check log")
    if not data.get("trip", {}).get("start") or not data.get("trip", {}).get("end"):
        errors.append("data.json: no fixed trip dates")
    if len(data.get("dayPlan", [])) != 8:
        errors.append("data.json: the day plan does not cover eight days")

    if shutil.which("node"):
        result = subprocess.run(["node", str(ROOT / "tests" / "canonical_render.js")],
                                capture_output=True, text=True, cwd=ROOT)
        if result.returncode != 0:
            errors.append("headless render check failed:\n" + result.stdout + result.stderr)
        else:
            print(result.stdout.strip())
    else:
        print("node not available: skipped the headless render check")

    if errors:
        print(f"\n{len(errors)} problem(s):")
        for e in errors:
            print(" -", e)
        return 1
    print(f"canonical smoke passed: {len(PAGES)} main pages, {len(DETAIL_PAGES)} detail pages")
    return 0


if __name__ == "__main__":
    sys.exit(main())
