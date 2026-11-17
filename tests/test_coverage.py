"""T4: the brief-coverage matrix ships, resolves, and tells the truth.

Every claim in site/coverage.json must point at a file that exists and at a flag
that exists in the freshly built data; a shipped-with-flags or flagged-gap row
must actually carry flags; and the page must be wired into the site.
"""

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"


def load():
    data = json.loads((SITE / "data.json").read_text(encoding="utf-8"))
    cov = json.loads((SITE / "coverage.json").read_text(encoding="utf-8"))
    return data, cov


class CoverageMatrix(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data, cls.cov = load()

    def test_coverage_json_ships_with_the_site(self):
        self.assertTrue((SITE / "coverage.html").exists(), "coverage.html missing")
        self.assertTrue((SITE / "coverage.json").exists(), "coverage.json missing")
        html = (SITE / "coverage.html").read_text(encoding="utf-8")
        self.assertIn('data-page="coverage"', html)
        self.assertIn("assets/app.js", html)
        app = (SITE / "assets" / "app.js").read_text(encoding="utf-8")
        self.assertIn("coverage.html", app, "nav must link the coverage page")
        self.assertIn("renderCoverage", app)
        verify = (ROOT / "scripts" / "verify_site.py").read_text(encoding="utf-8")
        self.assertIn('"coverage.html"', verify, "verify_site must check coverage.html")

    def test_every_item_resolves_to_existing_pages_and_flags(self):
        flag_ids = {f["id"] for f in self.data["flags"]}
        numbered = set()
        for item in self.cov["items"]:
            self.assertIn("status", item)
            self.assertIn("item", item)
            numbered.add(item["n"])
            for page in item.get("ships", []):
                self.assertTrue(
                    (SITE / page).exists(),
                    f"item {item['n']} claims {page}, which does not exist",
                )
            for rel in item.get("files", []):
                self.assertTrue(
                    (ROOT / rel).exists(),
                    f"item {item['n']} claims {rel}, which does not exist",
                )
            for fid in item.get("flags", []):
                self.assertIn(
                    fid, flag_ids,
                    f"item {item['n']} cites {fid}, which is not in data.json flags",
                )
            if item["status"] in ("shipped-with-flags", "flagged-gap"):
                self.assertTrue(
                    item.get("flags"),
                    f"item {item['n']} is {item['status']} but cites no flag",
                )
        # The matrix must be contiguous: 1..N with no gaps or duplicates.
        self.assertEqual(sorted(numbered), list(range(1, len(numbered) + 1)))

    def test_summary_matches_the_items(self):
        summary = self.cov["summary"]
        counts = {}
        for item in self.cov["items"]:
            counts[item["status"]] = counts.get(item["status"], 0) + 1
        for status, n in counts.items():
            self.assertEqual(summary.get(status), n, f"summary mismatch for {status}")
        self.assertEqual(summary["flags"], len(self.data["flags"]))
        self.assertEqual(summary["questions"], len(self.data["questions"]))

    def test_questions_and_suggestions_claims_are_real(self):
        # Items 19 and 20 promise the Q&A and suggestion pages; pin the counts
        # the matrix reports so a stale build cannot masquerade as coverage.
        self.assertGreaterEqual(len(self.data["questions"]), 15)
        self.assertGreaterEqual(len(self.data["suggestions"]), 1)
        item19 = next(i for i in self.cov["items"] if i["n"] == 19)
        item20 = next(i for i in self.cov["items"] if i["n"] == 20)
        self.assertIn("questions.html", item19["ships"])
        self.assertIn("suggestions.html", item20["ships"])


if __name__ == "__main__":
    unittest.main()
