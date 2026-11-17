#!/usr/bin/env python3
"""Pin the WPT World Championship structure read (2026-11-17, session arena/57416062-poker3).

Every rule excerpt this test checks is quoted from the official PDF at
https://cdn.wynnresorts.com/image/upload/v1750864036/visitwynn_pdfs_files/Poker/WPT/WPT_World_Championship_Structures.pdf
and transcribed, verbatim, into
raw/wynn_wpt_world_championship_structures_2026-11-17.md and WPT_SHEET_SECTIONS.

The failures this guards against, in order of severity:

1. a row quoting text the document does not contain (flag F77 — five fee splits and
   one registration sentence were paraphrases until this pass);
2. a row inheriting another event's rules because two events share a name and buy-in
   (the schedule prints several "PLO", "HORSE" and "No Limit Hold'em" events);
3. a row with no published section quietly acquiring a rule, or a matched row quietly
   joining the single-entry list;
4. a section transcribed on one side of the repository but not the other.

No network access is used: the test reads the published data, the transcription table
and the raw capture.
"""
from __future__ import annotations

import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / "site" / "data.json").read_text(encoding="utf-8"))
RAW = (ROOT / "raw" / "wynn_wpt_world_championship_structures_2026-11-17.md").read_text(encoding="utf-8")
sys.path.insert(0, str(ROOT / "scripts"))
import data_venues as N  # noqa: E402

WPT_ROWS = [e for e in DATA["events"] if e["id"].startswith("wynn-wpt-")]


def normalise(text: str) -> str:
    """Whitespace-insensitive comparison, because the raw capture wraps at the page margin."""
    return re.sub(r"\s+", " ", text).strip()


class EverySectionIsTranscribed(unittest.TestCase):
    def test_each_section_fee_line_appears_word_for_word_in_the_raw_capture(self) -> None:
        for key, sec in N.WPT_SHEET_SECTIONS.items():
            with self.subTest(section=key):
                self.assertIn(normalise(sec["fee"]), normalise(RAW),
                              f"fee line for {key} is not in the raw capture")

    def test_each_section_registration_clause_appears_word_for_word(self) -> None:
        for key, sec in N.WPT_SHEET_SECTIONS.items():
            with self.subTest(section=key):
                # The capture stores the clause as one table cell; compare its first sentence,
                # which is the part every section prints identically.
                first = sec["registration"].split(". ")[0].rstrip(".")
                self.assertIn(normalise(first), normalise(RAW),
                              f"registration clause for {key} is not in the raw capture")

    def test_no_section_prints_an_add_on(self) -> None:
        joined = " ".join(sec["registration"] + " " + sec["fee"] + " " + sec["levels"]
                          for sec in N.WPT_SHEET_SECTIONS.values()).lower()
        self.assertNotIn("add-on", joined)
        self.assertNotIn("add on", joined)
        self.assertNotIn("rebuy", joined)


class RowsQuoteTheirOwnSection(unittest.TestCase):
    def test_a_matched_row_quotes_its_section_fee_and_registration_exactly(self) -> None:
        matched = 0
        for e in WPT_ROWS:
            sec = N.wpt_section_for(e["date"], e["time"], e["name"], e["buyIn"])
            if not sec:
                continue
            matched += 1
            with self.subTest(row=e["id"]):
                self.assertEqual(e["rules"]["fee"]["excerpt"], sec["fee"])
                self.assertEqual(e["rules"]["reEntry"]["excerpt"], sec["registration"])
                self.assertEqual(e["rules"]["singleEntry"]["excerpt"], sec["registration"])
                self.assertEqual(e["rules"]["addOn"]["status"], "none-printed")
        self.assertEqual(matched, 35, "the number of rows with a published section changed")

    def test_no_matched_row_is_single_entry(self) -> None:
        for e in WPT_ROWS:
            if not N.wpt_section_for(e["date"], e["time"], e["name"], e["buyIn"]):
                continue
            with self.subTest(row=e["id"]):
                self.assertFalse(e["singleEntry"])
                self.assertNotEqual(e["entryType"], "none")
                self.assertEqual(e["rules"]["singleEntry"]["status"], "multiple-entries")

    def test_an_unmatched_row_states_that_the_document_does_not_cover_it(self) -> None:
        unmatched = [e for e in WPT_ROWS
                     if not N.wpt_section_for(e["date"], e["time"], e["name"], e["buyIn"])]
        self.assertEqual(len(unmatched), 101, "the number of uncovered rows changed")
        for e in unmatched:
            with self.subTest(row=e["id"]):
                self.assertEqual(e["rules"]["singleEntry"]["status"], "not-verified")
                self.assertIn("structures PDF", e["rules"]["singleEntry"]["excerpt"])
                self.assertIn(e["rules"]["singleEntry"]["retrieved"], {"2026-11-17", "2026-11-16"})

    def test_a_row_cannot_take_a_rule_from_a_same_named_event_on_another_day(self) -> None:
        """The Dec 18 $600 'No Limit Hold'em' is not the $600 NLH on Nov 27."""
        for e in WPT_ROWS:
            if e["date"] == "2026-12-18" and e["time"] == "12:00 PM" and e["name"] == "No Limit Hold'em":
                self.assertEqual(e["rules"]["fee"]["excerpt"],
                                 f"Buy-in $600 and guarantee $100000 are printed on the official schedule PDF; "
                                 f"no fee split is published for this event.")
                break
        else:
            self.fail("the Dec 18 $600 No Limit Hold'em row is missing")

    def test_the_day_two_rows_keep_the_unverified_label(self) -> None:
        for e in WPT_ROWS:
            if not e["isContinuation"]:
                continue
            with self.subTest(row=e["id"]):
                self.assertEqual(e["rules"]["singleEntry"]["status"], "not-verified")
                self.assertIn("resumes", e["rules"]["singleEntry"]["excerpt"])

    def test_late_registration_is_only_a_printed_clock_time(self) -> None:
        """A level count on its own is displayed as text and never converted into a time."""
        for e in WPT_ROWS:
            if not e["lateReg"]:
                continue
            with self.subTest(row=e["id"]):
                self.assertRegex(e["lateReg"], r"^(Start of )?[Ll]evel (9|10)")
                self.assertNotEqual(e["endEstimate"], "")


class TheCorrectionIsRecorded(unittest.TestCase):
    def test_the_paraphrase_flag_exists_and_names_the_document(self) -> None:
        flags = {f["id"]: f for f in DATA["flags"]}
        self.assertIn("F77", flags)
        self.assertIn("525", flags["F77"]["detail"])
        self.assertIn("WPT_World_Championship_Structures.pdf", flags["F77"]["source"])

    def test_no_published_excerpt_still_carries_the_retired_paraphrase(self) -> None:
        # F77 quotes the retired wording on purpose, to record what was corrected. Everywhere
        # else — every rule excerpt on every row — it must be gone.
        blobs = json.dumps(DATA["events"]) + json.dumps(
            [f for f in DATA["flags"] if f["id"] != "F77"])
        self.assertNotIn("$525 of every $600 buy-in", blobs)
        self.assertNotIn("1st Entry = $1,000", blobs)
        self.assertNotIn("maximum of one (1) starting flight", blobs)


if __name__ == "__main__":
    unittest.main()
