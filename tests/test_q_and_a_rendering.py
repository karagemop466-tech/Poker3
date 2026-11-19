#!/usr/bin/env python3
"""The Q&A worksheet must render the evidence it exists to show.

`site/q-and-a.html` shipped on 2026-11-19 with three conversion defects that no
gate caught, because the file was missing from ``verify_site.py``'s ``PAGES`` and
from ``canonical_smoke.py``'s page table:

1. Every source cell used a Markdown autolink, ``<https://…>``. HTML parses that
   as an unknown element whose tag name is ``https:`` and whose "attributes" are
   the path segments, so **all 19 official source URLs were invisible and
   unclickable** — the one thing the brief requires of every table row.
2. The header row lived in its own empty table, with the first data row promoted
   into a second table's ``<thead>`` and a Markdown ``|---|`` separator left
   between them as literal text.
3. ``**ANSWERED**`` and friends were left literal, and the five-item "unblock"
   list was split into two lists by a stray ``<p>``.

Standard library only: CI installs PyYAML and nothing else.
"""
from __future__ import annotations

import pathlib
import re
import unittest
from html.parser import HTMLParser

ROOT = pathlib.Path(__file__).resolve().parents[1]
PAGE = ROOT / "site" / "q-and-a.html"


class Shape(HTMLParser):
    """Collects the structural facts these assertions need."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.tag_counts: dict[str, int] = {}
        self.hrefs: list[str] = []
        self.rows: list[list[list[str]]] = []   # rows -> cells -> hrefs in that cell
        self._row: list[list[str]] | None = None
        self._cell: list[str] | None = None
        self._text: list[str] = []
        self.text_parts: list[str] = []
        self.unknown_https_tags: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        self.tag_counts[tag] = self.tag_counts.get(tag, 0) + 1
        if tag.startswith("http"):
            self.unknown_https_tags.append(tag)
        if tag == "a":
            href = dict(attrs).get("href") or ""
            self.hrefs.append(href)
            if self._cell is not None:
                self._cell.append(href)
        elif tag == "tr":
            self._row = []
        elif tag in ("td", "th"):
            if self._row is None:
                self._row = []
            self._cell = []
            self._row.append(self._cell)

    def handle_endtag(self, tag: str) -> None:
        if tag == "tr" and self._row is not None:
            self.rows.append(self._row)
            self._row = None
            self._cell = None
        elif tag in ("td", "th"):
            self._cell = None

    def handle_data(self, data: str) -> None:
        self.text_parts.append(data)


class QandARendering(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.raw = PAGE.read_text(encoding="utf-8")
        cls.shape = Shape()
        cls.shape.feed(cls.raw)
        cls.text = "".join(cls.shape.text_parts)

    def test_no_markdown_survives_into_the_html(self) -> None:
        for label, pattern in (
            ("autolink", r"<https://"),
            ("bold", r"\*\*[A-Za-z][^*\n]*\*\*"),
            ("markdown link", r"\[[^\]\n]+\]\([^)\s]+\)"),
            ("table separator", r"\|---\|"),
        ):
            with self.subTest(artifact=label):
                self.assertIsNone(re.search(pattern, self.raw),
                                  f"unrendered Markdown ({label}) would display literally")

    def test_the_worksheet_is_one_table_of_header_plus_22_rows(self) -> None:
        self.assertEqual(self.shape.tag_counts.get("table"), 1,
                         "the worksheet must be one table, not a split pair")
        self.assertEqual(len(self.shape.rows), 23, "header + 22 question rows")
        self.assertEqual(len(self.shape.rows[0]), 5, "header must hold 5 columns")
        self.assertEqual(self.shape.tag_counts.get("th"), 5,
                         "only the header row may use <th>; data rows must be <td>")
        self.assertEqual(self.shape.tag_counts.get("td"), 110, "22 rows x 5 cells")

    def test_every_question_row_carries_a_source_link(self) -> None:
        """The brief: every table row carries a source link the reader can open.

        The column is "the official source, *or* the exact thing to ask", so a row
        whose value is genuinely unpublished links the site page that records the
        gap instead of inventing a venue URL. Either way it must be a link.
        """
        https_anchors = 0
        for n, row in enumerate(self.shape.rows[1:], start=1):
            with self.subTest(row=n):
                self.assertEqual(len(row), 5, f"row {n}: expected 5 cells")
                hrefs = [h for cell in row for h in cell]
                self.assertTrue(hrefs, f"row {n}: no source link at all")
                for href in hrefs:
                    self.assertTrue(
                        href.startswith("https://") or href.endswith(".html"),
                        f"row {n}: link is neither an https source nor a site page: {href}")
                https_anchors += sum(1 for h in hrefs if h.startswith("https://"))
        self.assertGreaterEqual(https_anchors, 19,
                                "the 19 official URLs this page was built to show are missing")

    def test_urls_are_text_not_unknown_elements(self) -> None:
        """<https://…> becomes an element; a real link keeps the URL as text."""
        self.assertEqual(self.shape.unknown_https_tags, [],
                         "an <https://…> autolink was parsed as an unknown element")
        self.assertIn("venetianlasvegas.com", self.text, "source hosts must be readable")
        self.assertGreaterEqual(self.text.count("https://"), 19,
                                "the source URLs must appear as visible text")

    def test_the_unblock_list_is_one_five_item_list(self) -> None:
        # Two <ol> openers with a single closer (or none) means the list split.
        self.assertEqual(self.raw.count("<ol>"), 1, "the 'five answers' list was split")
        self.assertEqual(self.raw.count("</ol>"), 1)
        self.assertEqual(self.raw.count("<li>"), 8, "3 legend items + 5 unblock items")
        self.assertEqual(self.raw.count("</li>"), self.raw.count("<li>"))

    def test_the_page_is_covered_by_the_standing_gates(self) -> None:
        """Root cause: the file was in no gate's page list, so nothing read it."""
        verify = (ROOT / "scripts" / "verify_site.py").read_text(encoding="utf-8")
        smoke = (ROOT / "tests" / "canonical_smoke.py").read_text(encoding="utf-8")
        self.assertIn('"q-and-a.html"', verify, "verify_site.py must check this page")
        self.assertIn('"q-and-a.html"', smoke, "canonical_smoke.py must check this page")

    def test_every_published_page_is_free_of_markdown_artifacts(self) -> None:
        """The gate must scan all of site/, not only a hand-maintained list."""
        patterns = (re.compile(r"<https://"), re.compile(r"\*\*[A-Za-z][^*\n]*\*\*"),
                    re.compile(r"\|---\|"))
        offenders = []
        for path in sorted((ROOT / "site").rglob("*.html")):
            text = path.read_text(encoding="utf-8")
            for pattern in patterns:
                if pattern.search(text):
                    offenders.append(f"{path.name}: {pattern.pattern}")
        self.assertEqual(offenders, [], f"unrendered Markdown published: {offenders}")


if __name__ == "__main__":
    unittest.main()
