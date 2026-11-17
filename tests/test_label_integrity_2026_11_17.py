#!/usr/bin/env python3
"""Pin the label defects found and fixed on 2026-11-17.

All three defects were labels, not values: a row whose own evidence contradicted
the category or the note printed beside it. They are pinned by test because a
label that contradicts a row's own excerpt is exactly the failure mode the
"verify line by line" rule exists to prevent.

1. Eleven DeepStack Extravaganza NYE rows carried the category
   "unverified - structure sheet not read" after all 15 NYE sheets had been read
   in full, while each of those rows already quoted its own sheet (flag F74).
2. NYE Event #29 sat in the single-entry candidate list while its sheet prints
   re-entry wording (flag F75). Found by this test, not by reading.
3. Six Wynn WPT rows carried the note "entry rules not yet read" while their rule
   panel quoted the registration clause from the official structures PDF (F76).

No network access is used: every check reads the published data file and the
verbatim excerpts it carries.
"""
from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "site/data.json"


class LabelIntegrity(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data = json.loads(DATA.read_text())

    def test_no_event_is_labelled_sheet_not_read_while_quoting_a_sheet(self) -> None:
        """A row may not claim its sheet is unread if its rules quote one."""
        offenders = []
        for ev in self.data["events"]:
            if ev.get("category") != "unverified":
                continue
            quotes = [r.get("excerpt", "") for r in ev.get("rules", {}).values() if isinstance(r, dict)]
            if any("buy-in" in q or "re-entry" in q or "No add-on provision" in q for q in quotes):
                offenders.append(ev["id"])
        self.assertEqual(offenders, [], f"rows labelled 'sheet not read' but quoting a sheet: {offenders}")

    def test_every_nye_row_uses_the_category_its_own_sheet_supports(self) -> None:
        """All 15 NYE sheets were read: 'none' -> candidate list, 'multi-buyin' -> extra-spend."""
        nye = [e for e in self.data["events"] if e["id"].startswith("vl-nye-")]
        self.assertEqual(len(nye), 49, "the NYE schedule published 49 rows when it was read")
        for ev in nye:
            status = ev["rules"]["singleEntry"]["status"]
            if status == "single-entry-on-sheet":
                self.assertIn(ev["category"], {"single", "special"},
                              f"{ev['id']}: no re-entry clause printed, so it cannot be 'unverified'/'extra'")
            elif status == "multiple-entries":
                self.assertIn(ev["category"], {"extra", "flight"},
                              f"{ev['id']}: prints multi-entry wording, so it cannot be a single-entry candidate")

    def test_no_row_says_rules_not_read_while_printing_the_rule(self) -> None:
        offenders = []
        for ev in self.data["events"]:
            note = ev.get("note", "")
            if "not yet read" not in note:
                continue
            quoted = [k for k, r in ev.get("rules", {}).items()
                      if isinstance(r, dict) and "Registration" in r.get("excerpt", "")]
            if quoted:
                offenders.append((ev["id"], quoted))
        self.assertEqual(offenders, [], f"rows claiming 'rules not yet read' while quoting them: {offenders}")

    def test_no_single_entry_row_carries_a_multi_entry_rule(self) -> None:
        """The candidate list and the extra-spend list may not overlap (flag F75).

        'special-format' is allowed in the 'special' category only: a team event's
        sheet constrains how a team fields its players rather than how many times a
        player may enter, and those rows are labelled and excluded from ranking.
        """
        allowed = {"single": {"single-entry-on-sheet"}, "special": {"single-entry-on-sheet", "special-format"}}
        for ev in self.data["events"]:
            cat = ev.get("category")
            if cat not in allowed:
                continue
            status = ev["rules"]["singleEntry"]["status"]
            self.assertIn(status, allowed[cat], f"{ev['id']}: {cat} row with status {status}")

    def test_flag_ids_are_unique(self) -> None:
        """Ids are cited from prose, so a duplicate would make a citation ambiguous.

        Gaps are expected and correct: retired ids are never renumbered, because the
        prose that cites a flag must keep pointing at the same finding.
        """
        ids = [f["id"] for f in self.data["flags"]]
        self.assertEqual(len(ids), len(set(ids)), "duplicate flag id")

    def test_every_flag_links_an_official_host(self) -> None:
        allowed = ("venetianlasvegas.com", "wynnlasvegas.com", "wynnresorts.com", "mgmresorts.com",
                   "contentstack.io", "caesars.com", "google.com", "lasvegasnevada.gov", "worldpokertour.com",
                   "clarkcountynv.gov", "rwlasvegas.com",  # Clark County Dept. of Business License (official county host, as in verify_site.py)
                   # findings about this repository's own publishing and build
                   "github.com/karagemop466-tech/Poker3")
        bad = [f["id"] for f in self.data["flags"]
               if not any(h in f.get("source", "") for h in allowed)]
        self.assertEqual(bad, [], f"flags with a non-official source: {bad}")


if __name__ == "__main__":
    unittest.main()
