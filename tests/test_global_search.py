"""Regression checks for the canonical site's cross-table search surface."""
from __future__ import annotations

import pathlib
import re
import shutil
import subprocess
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SITE = ROOT / "site"


class GlobalSearchPage(unittest.TestCase):
    def test_search_page_uses_the_complete_renderer(self):
        page = (SITE / "search.html").read_text(encoding="utf-8")
        self.assertIn('<body data-page="global-search">', page)
        self.assertIn('data-global-search-form', page)
        self.assertIn('data-search-results', page)
        self.assertIn('aria-live="polite"', page)
        self.assertIn('name="q"', page)
        self.assertIn('src="assets/search.js"', page)
        # Keeping a distinct page key prevents app.js from also rendering its
        # older, narrower search index over the complete results.
        app = (SITE / "assets" / "app.js").read_text(encoding="utf-8")
        self.assertIn("if (PAGE === 'search') renderSearchResults", app)
        self.assertNotIn("if (PAGE === 'global-search') renderSearchResults", app)

    def test_index_includes_every_data_backed_table_family(self):
        script = (SITE / "assets" / "search.js").read_text(encoding="utf-8")
        required = [
            "catalog.venues", "catalog.events", "catalog.hotels", "catalog.rateLog",
            "catalog.routes", "catalog.sources", "catalog.structureSheets", "catalog.feed",
            "catalog.stripRooms", "catalog.bookingLinks", "hotel.quotes", "hotel.noQuoteWindows",
            "hotel.calendarObservation", "catalog.dayPlan", "catalog.planConflicts", "catalog.flags",
            "catalog.questions", "catalog.suggestions", "catalog.tripCostModel", "checks.urls",
            "transcription.rows",
        ]
        for field in required:
            with self.subTest(field=field):
                self.assertIn(field, script)

    def test_external_results_are_http_links_and_user_text_is_escaped(self):
        script = (SITE / "assets" / "search.js").read_text(encoding="utf-8")
        self.assertIn("parsed.protocol === 'https:' || parsed.protocol === 'http:'", script)
        for expression in ("esc(record.type)", "esc(record.title)", "esc(record.detail)", "esc(record.checked)", "esc(url)"):
            with self.subTest(expression=expression):
                self.assertIn(expression, script)

    def test_mobile_header_keeps_the_search_form_visible(self):
        css = (SITE / "assets" / "site.css").read_text(encoding="utf-8")
        self.assertIn(".top-search{grid-area:search;display:flex", css)
        self.assertIn(".mobile-nav{top:96px}", css)
        self.assertNotRegex(css, re.compile(r"\.top-search\s*\{\s*display\s*:\s*none", re.I))
        self.assertIn(".global-search-controls", css)

    @unittest.skipUnless(shutil.which("node"), "Node.js is required for the headless render check")
    def test_real_catalog_search_renders_every_record_family(self):
        result = subprocess.run(
            ["node", str(ROOT / "tests" / "canonical_render.js")],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("global-search?q=venetian", result.stdout)
        self.assertIn("all pages rendered", result.stdout)


if __name__ == "__main__":
    unittest.main()
