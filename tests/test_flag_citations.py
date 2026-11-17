"""Every F-number cited on the published site must exist in the flag register.

Found on 2026-11-17: the README cited (F38) for the "30 November and 1 December
publish no price" finding, but the register carries that finding as F57 and has no
F38 at all. A reader who follows the citation finds nothing. This test scans every
published page, the README and the prose inside site/data.json for flag citations
and fails if any of them points at an ID the register does not define.

It also checks the reverse direction loosely: the register's own IDs must be
unique, and the README's stated item count must match the register, so a stale
count cannot survive.
"""
import json
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / "site" / "data.json").read_text(encoding="utf-8"))
FLAGS = DATA["flags"]
FLAG_IDS = {f["id"] for f in FLAGS}

CITATION = re.compile(r"\bF(\d{1,3})\b")

# Files whose prose is shown to a reader and may cite a flag.
PUBLISHED_TEXT_FILES = sorted(
    p for p in (ROOT / "site").rglob("*.html")
) + [ROOT / "README.md"]


class FlagRegister(unittest.TestCase):
    def test_flag_ids_are_unique(self):
        ids = [f["id"] for f in FLAGS]
        self.assertEqual(len(ids), len(set(ids)), "duplicate flag IDs in the register")

    def test_every_flag_carries_a_source_link(self):
        for flag in FLAGS:
            with self.subTest(flag=flag["id"]):
                self.assertTrue(flag.get("source"), f"{flag['id']} has no source link")
                self.assertTrue(flag.get("detail"), f"{flag['id']} has no detail")
                self.assertTrue(flag.get("title"), f"{flag['id']} has no title")

    def test_readme_item_count_matches_the_register(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        match = re.search(r"\((\d+) items, rendered from `site/data\.json`\)", readme)
        self.assertIsNotNone(match, "the README no longer states the flagged-item count")
        self.assertEqual(int(match.group(1)), len(FLAGS),
                         "the README's flagged-item count does not match site/data.json")


class FlagCitations(unittest.TestCase):
    def test_every_cited_flag_id_exists_in_the_register(self):
        unknown = {}
        for path in PUBLISHED_TEXT_FILES:
            text = path.read_text(encoding="utf-8", errors="replace")
            for raw in CITATION.findall(text):
                fid = "F" + raw
                if fid not in FLAG_IDS:
                    unknown.setdefault(fid, set()).add(str(path.relative_to(ROOT)))
        self.assertEqual(unknown, {},
                         "the site cites flag IDs that the register does not define")

    def test_flag_prose_inside_data_json_only_cites_real_flags(self):
        """The data file's own prose is rendered on the pages, so it is checked too."""
        text = json.dumps(DATA, ensure_ascii=False)
        unknown = sorted({"F" + raw for raw in CITATION.findall(text)} - FLAG_IDS)
        self.assertEqual(unknown, [],
                         "site/data.json prose cites flag IDs that the register does not define")

    def test_the_new_findings_are_published_with_their_sources(self):
        """F77 and F78 are this session's two findings; both must be present and sourced."""
        for fid in ("F77", "F78"):
            with self.subTest(flag=fid):
                self.assertIn(fid, FLAG_IDS)
                flag = next(f for f in FLAGS if f["id"] == fid)
                self.assertTrue(flag["source"].startswith("https://"), flag["source"])
        self.assertIn("F78", json.dumps(DATA["questions"]), "Q05/Q15 must cite F78")
        self.assertIn("F78", json.dumps(DATA["trip"]), "the trip profile must cite F78")


if __name__ == "__main__":
    unittest.main()
