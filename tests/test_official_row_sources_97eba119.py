#!/usr/bin/env python3
"""Independent, line-by-line audit of the published dashboard (session arena/97eba119, 2026-11-19).

The user's verification rule is absolute: *every table row must carry a source link to an
official site; a value that cannot be confirmed from an official source is left blank and
flagged as unverified; never infer or fill in a value.* `scripts/verify_site.py` is the
builder's own gate. This file is a separate, independent gate: it re-derives the same
invariants straight from `site/data.json` and from the published HTML files, without
importing the builder, so a defect in the builder cannot hide behind its own verifier.

It also guards the concrete live-site defect found on 2026-11-19: because GitHub Pages is
still the legacy "deploy from a branch: main /" setting while `pages.yml` publishes the
`site/` artifact at the same host (flag F29), canonical paths such as
`/Poker3/calculator.html` and `/Poker3/venues.html` returned **404** whenever the legacy
publisher won. Every canonical page now has a root-level redirect stub, so the path works
under either publisher. See `research/audit_2026-11-19_97eba119.md`.
"""
from __future__ import annotations

import json
import pathlib
import re
import unittest
from urllib.parse import urlparse

ROOT = pathlib.Path(__file__).resolve().parents[1]
SITE = ROOT / "site"

# Mirrors scripts/verify_site.py, kept local so this check does not import the builder.
# MGM's Contentstack host serves the official MGM Resorts poker PDFs linked from the
# resort pages; it is an official document host, not a third-party calendar.
OFFICIAL_SUFFIXES = (
    "venetianlasvegas.com",
    "wynnlasvegas.com",
    "wynnresorts.com",
    "bellagio.mgmresorts.com",
    "mgmgrand.mgmresorts.com",
    "mgmresorts.com",
    "aria.mgmresorts.com",
    "caesars.com",
    "assets.contentstack.io",
    "clarkcountynv.gov",
    "rwlasvegas.com",
    "google.com",
)


REPO_EVIDENCE_PREFIX = "https://github.com/karagemop466-tech/Poker3/"


def is_official(url: str) -> bool:
    if not isinstance(url, str) or not url.startswith("https://"):
        return False
    host = urlparse(url).netloc.lower()
    return any(host == s or host.endswith("." + s) for s in OFFICIAL_SUFFIXES)


def is_repo_evidence(url: str) -> bool:
    """Operational flags/q&a about this site legitimately cite this repository's own code.

    These are not venue data rows: a claim like "the workflow had a duplicate key" can
    only be checked against the workflow file itself. No third-party calendar or press
    article is allowed as a source for any row.
    """
    return isinstance(url, str) and url.startswith(REPO_EVIDENCE_PREFIX)


class RowSourceAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.db = json.loads((SITE / "data.json").read_text(encoding="utf-8"))

    def urls_on(self, row: dict) -> list[tuple[str, str]]:
        out = []
        for key in ("source", "scheduleUrl", "structureUrl", "sheetUrl", "url"):
            if row.get(key):
                out.append((key, row[key]))
        for rk, rv in (row.get("rules") or {}).items():
            if isinstance(rv, dict) and rv.get("source"):
                out.append(("rules." + rk, rv["source"]))
        return out

    def test_every_event_row_has_an_official_source_link(self) -> None:
        events = self.db["events"]
        self.assertGreater(len(events), 300)
        for e in events:
            urls = self.urls_on(e)
            self.assertTrue(urls, f"{e['id']}: no source link on the row")
            for key, url in urls:
                self.assertTrue(is_official(url), f"{e['id']}: {key} is not an official https URL: {url}")

    def test_every_event_has_read_dates_and_structured_rule_fields(self) -> None:
        for e in self.db["events"]:
            for key in ("lastChecked", "lastVerified"):
                self.assertTrue(re.fullmatch(r"20\d\d-\d\d-\d\d", str(e.get(key, ""))),
                                f"{e['id']}: missing or malformed {key}")
            rules = e.get("rules") or {}
            for rule in ("singleEntry", "reEntry", "addOn", "fee"):
                r = rules.get(rule)
                self.assertIsInstance(r, dict, f"{e['id']}: missing structured rule {rule}")
                self.assertTrue(r.get("excerpt"), f"{e['id']}: {rule} has no source excerpt")
                self.assertTrue(is_official(r.get("source", "")),
                                f"{e['id']}: {rule} has no official source link")
                self.assertTrue(re.fullmatch(r"20\d\d-\d\d-\d\d", str(r.get("retrieved", ""))),
                                f"{e['id']}: {rule} has no retrieval date")
            self.assertTrue(e.get("category"), f"{e['id']}: no category label")

    def test_no_confirmed_event_is_still_labelled_unverified(self) -> None:
        # Requirement: remove the "unverified" label from every event that is confirmed.
        for e in self.db["events"]:
            self.assertNotIn("unverified", json.dumps(e).lower(),
                             f"{e['id']}: still carries an unverified label")

    def test_blank_fee_or_guarantee_is_always_explained_or_flagged(self) -> None:
        for e in self.db["events"]:
            if e.get("buyIn") in ("", None) or e.get("guarantee") in ("", None):
                self.assertTrue(e.get("note") or e.get("guaranteeNote") or e.get("status"),
                                f"{e['id']}: blank fee/guarantee with no explanation")
        # An unexplained blank is never ranked: the day plan's primaries must be complete.
        by_id = {e["id"]: e for e in self.db["events"]}
        for day in self.db["dayPlan"]:
            p = by_id.get(day["primary"])
            if p:
                self.assertTrue(p.get("buyIn") and p.get("guarantee"),
                                f"{day['date']}: ranked primary has an unconfirmed fee or guarantee")

    def test_every_non_event_row_has_a_source_and_where_applicable_a_date(self) -> None:
        checks = (
            ("hotels", "source", True),
            ("routes", "source", True),
            ("rateLog", "source", True),
            ("flags", "source", False),
            ("questions", "source", False),
            ("sources", "url", True),
            ("structureSheets", "url", False),
        )
        for key, field, needs_date in checks:
            rows = self.db[key]
            self.assertTrue(rows, f"{key}: empty table")
            for r in rows:
                label = r.get("id") or r.get("name") or r.get("hotel") or key
                url = r.get(field, "")
                if key in ("flags", "questions") and is_repo_evidence(url):
                    # Only a site-operations row may cite the repo's own code, and only
                    # this repository is accepted. It is still a first-party source.
                    text = json.dumps(r).lower()
                    self.assertTrue(any(word in text for word in
                                        ("publish", "monitor", "workflow", "verifier",
                                         "script", "scheduled re-check", "process question")),
                                    f"{key}/{label}: repo evidence on a non-operational row")
                else:
                    self.assertTrue(is_official(url),
                                    f"{key}/{label}: {field} is not an official https URL: {url}")
                if needs_date:
                    date = r.get("lastChecked") or r.get("observedOn") or r.get("checked")
                    self.assertTrue(date, f"{key}/{label}: no last-checked / observed date")
        for s in self.db["structureSheets"]:
            self.assertTrue(s.get("read"), f"sheet {s['sheet']}: not marked read")
            self.assertTrue(s.get("readOn"), f"sheet {s['sheet']}: no read date")

    def test_unverified_strip_rooms_are_blank_and_flagged(self) -> None:
        for r in self.db["stripRooms"]:
            if not r.get("official"):
                self.assertTrue(r.get("flag"), f"{r['id']}: blank official page but no review flag")
                self.assertNotIn(r["id"], " ".join(f.get("id", "") for f in self.db["feed"]),
                                 f"{r['id']}: unverified room must not be a live-feed source")

    def test_every_canonical_page_has_a_root_path_guard(self) -> None:
        # The 404 fix: /Poker3/<page>.html must work under either Pages publisher.
        pages = sorted(list(SITE.glob("*.html")) + list((SITE / "venues").glob("*.html")))
        self.assertGreaterEqual(len(pages), 16)
        refresh = re.compile(r'http-equiv="refresh" content="0; url=([^"]+)"')
        for page in pages:
            rel = page.relative_to(SITE)
            counterpart = ROOT / rel
            self.assertTrue(counterpart.is_file(),
                            f"{rel}: no root-level path guard; /Poker3/{rel} 404s under the legacy publisher")
            text = counterpart.read_text(encoding="utf-8")
            m = refresh.search(text)
            self.assertIsNotNone(m, f"{rel}: root counterpart is not a redirect")
            target = m.group(1).split("?")[0].split("#")[0]
            resolved = (counterpart.parent / target).resolve()
            self.assertTrue(resolved.is_file(), f"{rel}: redirect target missing: {target}")
            self.assertEqual(resolved, page.resolve(),
                             f"{rel}: redirect does not lead to the canonical page")

    def test_coordination_board_has_no_merge_conflict_markers(self) -> None:
        text = (ROOT / "COORDINATION.md").read_text(encoding="utf-8")
        for line in text.splitlines():
            self.assertFalse(line.startswith(("<<<<<<<", "=======", ">>>>>>>")),
                             f"COORDINATION.md: leftover conflict marker: {line[:60]}")

    def test_no_broken_local_links_in_published_html(self) -> None:
        pages = sorted(list(SITE.glob("*.html")) + list((SITE / "venues").glob("*.html"))
                       + list(ROOT.glob("*.html")) + list((ROOT / "venues").glob("*.html")))
        href = re.compile(r'(?:href|src)\s*=\s*["\']([^"\']+)["\']')
        for page in pages:
            for raw in href.findall(page.read_text(encoding="utf-8")):
                if raw.startswith(("http://", "https://", "mailto:", "tel:", "#", "data:", "javascript:")):
                    self.assertFalse(raw.startswith("http://"), f"{page}: insecure link {raw}")
                    continue
                target = (page.parent / raw.split("?")[0].split("#")[0]).resolve()
                self.assertTrue(target.exists(), f"{page}: broken local link {raw}")


if __name__ == "__main__":
    unittest.main()
