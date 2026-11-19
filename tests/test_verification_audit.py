#!/usr/bin/env python3
"""Regression checks for the 2026-11-19 requirements audit (session arena/8194609f).

These tests keep the new verification page honest: every audit row must link
evidence, the corrected venue pages must not publish stale claims again, and the
shared coordination board must never carry git conflict markers.
"""
from __future__ import annotations

import json
import re
import unittest
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / "site" / "data.json").read_text(encoding="utf-8"))
SITE = ROOT / "site"

OFFICIAL_SUFFIXES = (
    "venetianlasvegas.com", "wynnlasvegas.com", "wynnresorts.com",
    "mgmresorts.com", "contentstack.io", "caesars.com", "clarkcountynv.gov",
    "assets.caesars.com",
)
PROJECT_HOSTS = ("github.com",)


def is_official(url: str) -> bool:
    if not url.startswith("https://"):
        return False
    host = urlparse(url).netloc.lower()
    return any(host == h or host.endswith("." + h) for h in OFFICIAL_SUFFIXES)


def is_project(url: str) -> bool:
    if not url.startswith("https://"):
        return False
    host = urlparse(url).netloc.lower()
    return any(host == h or host.endswith("." + h) for h in PROJECT_HOSTS)


class VerificationDataTests(unittest.TestCase):
    def test_all_three_audit_sections_are_published(self):
        for key in ("verification", "verificationReads", "verificationRows"):
            self.assertIn(key, DATA, f"data.json is missing {key}")
            self.assertTrue(DATA[key], f"{key} is empty")

    def test_every_requirement_row_links_evidence(self):
        rows = DATA["verification"]
        self.assertEqual(len(rows), 40, "expected one row per instruction in the brief")
        ids = [r["id"] for r in rows]
        self.assertEqual(len(ids), len(set(ids)), "duplicate requirement id")
        for r in rows:
            with self.subTest(id=r["id"]):
                self.assertTrue(r["requirement"].strip())
                self.assertTrue(r["status"].strip())
                self.assertTrue(r["evidence"].strip())
                self.assertEqual(r["checked"], "2026-11-19")
                self.assertTrue(r["pages"], "no implementation page listed")
                self.assertTrue(r["sources"], "no evidence link listed")
                for page in r["pages"]:
                    href = page["href"]
                    if href.startswith("https://"):
                        self.assertTrue(is_project(href), f"{r['id']}: unexpected external page {href}")
                        continue
                    self.assertTrue((SITE / href.split("?")[0].split("#")[0]).exists(),
                                    f"{r['id']}: missing page {href}")
                for src in r["sources"]:
                    self.assertTrue(is_official(src["url"]) or is_project(src["url"]),
                                    f"{r['id']}: non-https or non-evidence URL {src['url']}")
                    if src["kind"] == "official":
                        self.assertTrue(is_official(src["url"]),
                                        f"{r['id']}: an 'official' link is not an official host")

    def test_official_reads_are_verbatim_and_linked(self):
        reads = DATA["verificationReads"]
        self.assertGreaterEqual(len(reads), 15)
        for r in reads:
            with self.subTest(id=r["id"]):
                self.assertTrue(is_official(r["url"]), r["url"])
                self.assertTrue(r["excerpt"].strip())
                self.assertTrue(r["value"].strip())
                self.assertEqual(r["checked"], "2026-11-19")
                self.assertEqual(r["result"], "no value changed")

    def test_trip_window_rows_match_the_published_dataset(self):
        rows = DATA["verificationRows"]
        self.assertEqual(len(rows), 19)
        by_id = {e["id"]: e for e in DATA["events"]}
        for r in rows:
            with self.subTest(row=r["rowId"]):
                self.assertIn(r["rowId"], by_id)
                e = by_id[r["rowId"]]
                self.assertEqual(e["date"], r["date"])
                self.assertEqual(e["time"], r["time"])
                self.assertEqual(e["buyIn"], r["buyIn"])
                self.assertEqual(e["guarantee"], r["guarantee"])
                self.assertTrue((e.get("sheetUrl") or "").endswith(r["sheet"]),
                                f"{r['rowId']}: sheet link disagrees with the read")
                self.assertTrue(is_official(r["source"]))

    def test_new_flags_are_present_and_ids_are_unique(self):
        flags = DATA["flags"]
        ids = [f["id"] for f in flags]
        self.assertEqual(len(ids), len(set(ids)), "duplicate flag id in the register")
        self.assertIn("F101", ids)
        # Parallel sessions own F98 (markers) and F100 (stale venue pages); no duplicates here.
        self.assertEqual(ids.count("F101"), 1, "F101 is duplicated")
        for f in flags:
            self.assertTrue(f.get("source"), f"{f['id']}: no source link")
            self.assertTrue(f.get("detail"), f"{f['id']}: no detail")


class CorrectedPagesTests(unittest.TestCase):
    STALE = (
        "the NYE rows stay unverified",
        "no date-specific room quote exists",
        "The only dated checkout total found",
        "checked 2026-11-16",
    )

    def test_venue_pages_no_longer_claim_unverified_nye_or_missing_quotes(self):
        for name in ("index.html", "venetian.html", "wynn.html", "others.html"):
            text = (SITE / "venues" / name).read_text(encoding="utf-8")
            for phrase in self.STALE:
                with self.subTest(page=name, phrase=phrase):
                    self.assertNotIn(phrase, text, f"venues/{name} still publishes stale text: {phrase}")

    def test_coordination_board_has_no_conflict_markers(self):
        text = (ROOT / "COORDINATION.md").read_text(encoding="utf-8")
        for line in text.splitlines():
            self.assertFalse(line.startswith(("<<<<<<<", "=======", ">>>>>>>")),
                             f"orphan conflict marker: {line[:80]}")

    def test_verification_page_and_renderer_are_registered(self):
        page = (SITE / "verification.html").read_text(encoding="utf-8")
        self.assertIn('data-page="verification"', page)
        for hook in ("data-verification-summary", "data-verification",
                     "data-verification-reads", "data-verification-rows"):
            self.assertIn(hook, page)
        app = (SITE / "assets" / "app.js").read_text(encoding="utf-8")
        self.assertIn("['verification.html', 'Verification'", app)
        self.assertIn("function renderVerification()", app)
        self.assertIn("if (PAGE === 'verification') renderVerification();", app)
        for path in (ROOT / "scripts" / "verify_site.py", ROOT / "tests" / "canonical_smoke.py"):
            self.assertIn('"verification.html"', path.read_text(encoding="utf-8"))
        self.assertTrue((ROOT / "verification.html").exists())
        self.assertIn("site/verification.html", (ROOT / "verification.html").read_text(encoding="utf-8"))
        self.assertTrue((ROOT / "research" / "verification_2026-11-19_arena-8194609f.md").exists())

    def test_no_broken_local_links_in_the_audit_page(self):
        page = SITE / "verification.html"
        for href in re.findall(r'href="([^"]+)"', page.read_text(encoding="utf-8")):
            if href.startswith(("https://", "http://", "#", "mailto:")):
                continue
            self.assertTrue((page.parent / href.split("#")[0].split("?")[0]).exists(),
                            f"verification.html: broken local link {href}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
