#!/usr/bin/env python3
"""README coverage prose must agree with generated coverage and canonical data.

Two previous sessions left the README summary at 21 shipped / 3 partial while
``site/coverage.json`` had moved to 22 shipped / 2 partial, and a calculator line
still said "eight entries" after the day plan settled on seven. These checks derive
the expected numbers from the published data instead of trusting either document.
"""
from __future__ import annotations

import json
import pathlib
import re
import unittest
from collections import Counter

ROOT = pathlib.Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
DATA = json.loads((ROOT / "site" / "data.json").read_text(encoding="utf-8"))
COVERAGE = json.loads((ROOT / "site" / "coverage.json").read_text(encoding="utf-8"))
TEXT = README.read_text(encoding="utf-8")


def coverage_table_rows():
    """The status rows in the README's Brief coverage traceability table."""
    section = TEXT.split("## Brief coverage traceability", 1)[1].split("\n## ", 1)[0]
    rows = []
    for line in section.splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 2 or cells[1] in {"Status", "---"}:
            continue
        rows.append((cells[0], cells[1]))
    return rows


class DocumentationConsistency(unittest.TestCase):
    def test_coverage_generated_date_matches_data_as_of(self):
        self.assertEqual(COVERAGE["generated"], DATA["asOf"])

    def test_data_counts_match_canonical_dataset(self):
        counts = COVERAGE["dataCounts"]
        self.assertEqual(counts["events"], len(DATA["events"]))
        self.assertEqual(counts["hotels"], len(DATA["hotels"]))
        self.assertEqual(counts["routes"], len(DATA["routes"]))
        self.assertEqual(counts["sources"], len(DATA["sources"]))
        self.assertEqual(counts["flags"], len(DATA["flags"]))
        self.assertEqual(counts["planDays"], len(DATA["dayPlan"]))

    def test_summary_counts_match_generated_matrix(self):
        match = re.search(
            r"Current result:\s*(\d+)\s+items\s+—\s*(\d+)\s+shipped,\s*(\d+)\s+partial.*?,\s*(\d+)\s+not-resolvable",
            TEXT,
            re.S,
        )
        self.assertIsNotNone(match, "README coverage summary was not found")
        total, shipped, partial, not_resolvable = (int(x) for x in match.groups())
        by_status = COVERAGE["coverageByStatus"]
        self.assertEqual(total, len(COVERAGE["items"]))
        self.assertEqual(shipped, by_status.get("shipped", 0))
        self.assertEqual(partial, by_status.get("partial", 0))
        self.assertEqual(not_resolvable, by_status.get("not-resolvable", 0))

    def test_readme_table_status_counts_match_generated_matrix(self):
        rows = coverage_table_rows()
        self.assertEqual(len(rows), len(COVERAGE["items"]), "README table row count differs from coverage.json")
        actual = Counter(status for _, status in rows)
        expected = Counter(COVERAGE["coverageByStatus"])
        self.assertEqual(actual, expected, f"README table statuses disagree: {dict(actual)} vs {dict(expected)}")

    def test_key_status_changes_are_not_reverted(self):
        rows = dict(coverage_table_rows())
        self.assertEqual(rows.get("Walking-route check, 30-minute limit"), "shipped")
        self.assertEqual(rows.get("Checkout total, nightly average, fee, tax, parking, cancellation, timestamp"), "partial")
        self.assertEqual(rows.get("Best hotels within walking distance, true cost/night"), "partial")
        self.assertEqual(rows.get("All-day schedule from 8 AM"), "not-resolvable")

    def test_calculator_description_uses_the_seven_planned_entries(self):
        self.assertNotIn("eight entries", TEXT)
        self.assertIn("seven planned entries and seven nights", TEXT)
        self.assertEqual(DATA["tripCostModel"]["entries"], 7)
        self.assertEqual(len(DATA["dayPlan"]), 7)

    def test_every_published_source_has_a_unique_id(self):
        ids = [s.get("id") for s in DATA["sources"]]
        self.assertTrue(all(ids), "a source row has no stable id")
        self.assertEqual(len(ids), len(set(ids)), "duplicate source ids in site/data.json")


if __name__ == "__main__":
    unittest.main()
