#!/usr/bin/env python3
"""Every canonical page path must resolve under both GitHub Pages publishers.

The Pages source is still the legacy ``main /`` branch setting, while
``pages.yml`` also uploads ``site/`` as an Actions artifact. When the artifact
publisher wins, ``site/calculator.html`` is served at ``/Poker3/calculator.html``.
When the legacy publisher wins, only the repository root is served, so a missing
root-level file is a 404. An independent live read on 2026-11-19 found exactly
that split: root ``/calculator.html`` and ``/venues/wynn.html`` returned GitHub's
404 while ``/site/calculator.html`` and ``/site/venues/wynn.html`` served the
pages. ``scripts/build_legacy_redirects.py`` now generates a root-level redirect
for every canonical page path that has no root counterpart.

These tests pin the invariant without needing network access.
"""
from __future__ import annotations

import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
REFRESH = re.compile(r'http-equiv="refresh" content="0; url=([^"]+)"')
CANONICAL = re.compile(r'<link rel="canonical" href="([^"]+)"')


class RootCanonicalShortlinks(unittest.TestCase):
    def setUp(self) -> None:
        self.pages = sorted(p for p in SITE.glob("**/*.html") if p.is_file())

    def test_every_canonical_page_has_a_root_level_counterpart(self) -> None:
        self.assertTrue(self.pages, "no canonical HTML pages found")
        for page in self.pages:
            rel = page.relative_to(SITE)
            root = ROOT / rel
            with self.subTest(page=rel.as_posix()):
                self.assertTrue(root.is_file(), f"missing root-level counterpart for {rel}")
                text = root.read_text(encoding="utf-8")
                self.assertIn('http-equiv="refresh"', text, f"{rel}: root counterpart is not a redirect")
                match = REFRESH.search(text)
                self.assertIsNotNone(match, f"{rel}: no refresh target")
                target = match.group(1).split("?")[0].split("#")[0]
                resolved = (root.parent / target).resolve()
                self.assertEqual(
                    resolved, page.resolve(),
                    f"{rel}: refresh target {target} does not resolve to the canonical page",
                )
                self.assertIn(str(SITE.resolve()), [str(p) for p in resolved.parents] + [str(resolved)],
                              f"{rel}: refresh target escapes site/")

    def test_canonical_link_points_at_the_same_page(self) -> None:
        for page in self.pages:
            rel = page.relative_to(SITE)
            root = ROOT / rel
            text = root.read_text(encoding="utf-8")
            match = CANONICAL.search(text)
            self.assertIsNotNone(match, f"{rel}: no canonical link")
            canonical = match.group(1).split("?")[0].split("#")[0]
            resolved = (root.parent / canonical).resolve()
            with self.subTest(page=rel.as_posix()):
                self.assertEqual(resolved, page.resolve(),
                                 f"{rel}: canonical link {canonical} does not resolve to the canonical page")

    def test_no_conflict_markers_in_generated_redirects(self) -> None:
        for page in self.pages:
            rel = page.relative_to(SITE)
            text = (ROOT / rel).read_text(encoding="utf-8")
            for marker in ("<<<<<<<", "=======", ">>>>>>>"):
                self.assertNotIn(marker, text, f"{rel}: unresolved merge marker {marker}")


if __name__ == "__main__":
    unittest.main()
