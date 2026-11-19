#!/usr/bin/env python3
"""No retired dashboard may publish a second answer at the live host.

The GitHub Pages source is the repository root, so `docs/`, `planner/` and `verified/`
are all still reachable at https://karagemop466-tech.github.io/Poker3/. Those pages were
built from an older, incomplete data set; `docs/` in particular still says hotel rates and
walking times are unverified, which the canonical `site/` contradicts with a dated log.

Each legacy page must therefore remain a redirect to an existing canonical page.
"""
from __future__ import annotations

import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
LEGACY = ("docs", "planner", "verified")
REFRESH = re.compile(r'http-equiv="refresh" content="0; url=([^"]+)"')


class LegacyPagesAreRedirects(unittest.TestCase):
    def test_every_legacy_page_redirects_to_an_existing_page(self):
        checked = 0
        for directory in LEGACY:
            base = ROOT / directory
            if not base.is_dir():
                continue
            for page in sorted(base.glob("*.html")):
                text = page.read_text(encoding="utf-8")
                match = REFRESH.search(text)
                self.assertIsNotNone(match, f"{page.relative_to(ROOT)} is still a live dashboard, not a redirect")
                target = match.group(1).split("?")[0].split("#")[0]
                resolved = (base / target).resolve()
                self.assertTrue(resolved.exists(), f"{page.relative_to(ROOT)} redirects to missing {target}")
                self.assertIn("site", resolved.parts, f"{page.relative_to(ROOT)} must redirect into the canonical site/")
                checked += 1
        self.assertGreaterEqual(checked, 30, "expected the three retired dashboards to be covered")

    def test_the_root_pages_are_still_redirects(self):
        for page in ("index.html", "hotels.html", "flagged.html", "tournaments.html", "schedule.html"):
            text = (ROOT / page).read_text(encoding="utf-8")
            self.assertRegex(text, r'http-equiv="refresh"', f"root {page} must redirect into site/")


if __name__ == "__main__":
    unittest.main()
