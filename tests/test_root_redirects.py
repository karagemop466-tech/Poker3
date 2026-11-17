#!/usr/bin/env python3
"""The repository root must not publish stale research pages (flag F29).

The repository's Pages source is the legacy "deploy from a branch: main /" setting,
so GitHub publishes the whole repository root after every push. Every root-level
*.html research page was a 2026-11-16 template whose tables were deliberately blank,
which meant the root URL served conclusions the canonical dashboard contradicts - a
hotels page headed "No hotel ranking yet" beside a dashboard with eight priced
properties, for example.

Each of those files is now a redirect into site/. This test keeps it that way: a root
page either redirects into site/ or does not exist. Nothing is deleted; the old
content stays in version control.
"""
from __future__ import annotations

import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


class RootRedirects(unittest.TestCase):
    def setUp(self) -> None:
        self.pages = sorted(p for p in ROOT.glob("*.html") if p.is_file())

    def test_every_root_page_redirects_into_the_canonical_site(self) -> None:
        for page in self.pages:
            text = page.read_text(encoding="utf-8")
            self.assertIn("http-equiv=\"refresh\"", text,
                          f"{page.name}: a root page that is not a redirect is published at the site root")
            match = re.search(r"url=(site/[^\"']+)", text)
            self.assertIsNotNone(match, f"{page.name}: redirect has no site/ target")

    def test_every_redirect_target_exists(self) -> None:
        for page in self.pages:
            target = re.search(r"url=(site/[^\"']+)", page.read_text(encoding="utf-8")).group(1)
            self.assertTrue((ROOT / target).is_file(), f"{page.name}: redirects to a missing file {target}")

    def test_no_root_page_claims_a_stale_snapshot(self) -> None:
        for page in self.pages:
            text = page.read_text(encoding="utf-8")
            self.assertNotIn("Research snapshot 2026-11-16", text,
                             f"{page.name}: still publishes the 2026-11-16 snapshot as content")


if __name__ == "__main__":
    unittest.main()
