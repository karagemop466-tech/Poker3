#!/usr/bin/env python3
"""Guards for the two label defects found on 2026-11-17 by session 4fbf8168.

1. **Parking, like-for-like (F86).** The recommended hotel published only its paid
   self-parking figures while the resort's own poker-room parking page prints a
   complimentary-parking rule for players — and the Wynn row in the same table did carry
   its poker-room benefit. A reader comparing the two rows was not comparing the same
   thing. The waiver is now quoted on the Venetian and Palazzo rows and beside the
   calculator's parking field, with the source page and the date it was read.
   No dollar total moved: the paid $20 per night is still what the site adds up, because
   no official source publishes a finish time (F16), so the three-hour condition cannot be
   confirmed for a named event.

2. **Candidate disclosure.** 45 of the 52 sheet-screened Venetian rows said the entry cap
   is unconfirmed; the 7 DeepStack NYE rows quoted the same screen without that sentence,
   so they read as a stronger claim than they are (the F74/F75 family). Every screened row
   now carries the identical disclosure, and `scripts/verify_entry_labels.py` fails if any
   row's label gets ahead of the text quoted under it.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / "site" / "data.json").read_text(encoding="utf-8"))
CAPTURE = (ROOT / "raw" / "venetian_player_parking_2026-11-17_4fbf8168.md").read_text(encoding="utf-8")
CALC_PAGE = (ROOT / "site" / "calculator.html").read_text(encoding="utf-8")
HOTELS = {h["id"]: h for h in DATA["hotels"]}
EVENTS = DATA["events"]
FLAGS = {f["id"]: f for f in DATA["flags"]}

PARKING_URL = "https://www.venetianlasvegas.com/resort/casino/poker/player-parking.html"
WAIVER = ("Players in the poker room who play three hours or more in tournament or cash games will receive "
          "complimentary self-parking for the day. Players must visit a supervisor at the end of their session to "
          "confirm qualifications for complimentary self-parking.")


def plain(text: str) -> str:
    """Collapse markdown blockquote wrapping so a quote is compared to prose, not layout."""
    lines = [re.sub(r"^\s*>+\s?", "", ln) for ln in (text or "").splitlines()]
    return re.sub(r"\s+", " ", " ".join(lines)).strip()


class ParkingWaiverIsPublished(unittest.TestCase):
    def test_the_capture_exists_and_is_attributed_to_the_official_page(self):
        self.assertIn(PARKING_URL, CAPTURE, "the capture must name the page it was read from")
        self.assertRegex(CAPTURE, r"Retrieved:\s*2026-11-17T\d{2}:\d{2}Z",
                         "the capture must carry the moment it was read")

    def test_the_waiver_quoted_on_both_venetian_rows_is_verbatim_from_the_capture(self):
        capture = plain(CAPTURE)
        for hid in ("venetian", "palazzo"):
            with self.subTest(hotel=hid):
                waiver = HOTELS[hid].get("parkingWaiver") or {}
                self.assertTrue(waiver, f"{hid} must publish the player parking waiver")
                self.assertIn(plain(waiver["excerpt"]), capture,
                              f"{hid}: quoted waiver is not what the page prints")
                self.assertEqual(waiver["excerpt"], WAIVER, "the waiver must be quoted in full, both sentences")
                self.assertEqual(waiver["source"], PARKING_URL)
                self.assertEqual(waiver["retrieved"], "2026-11-17")

    def test_the_table_row_itself_discloses_the_waiver(self):
        # app.js renders h.parking in the table and in the detail panel; the waiver has to be
        # in that string or the reader of the comparison table never sees it.
        for hid in ("venetian", "palazzo"):
            with self.subTest(hotel=hid):
                self.assertIn("three hours or more", HOTELS[hid]["parking"])
                self.assertIn("complimentary self-parking", HOTELS[hid]["parking"])

    def test_the_three_poker_hotels_are_comparable_on_parking(self):
        """Like-for-like: each recommended hotel states its own poker-room parking rule.

        This is the whole point of the defect — Wynn's row carried its poker-room benefit
        while the Venetian and Palazzo rows carried only their paid rates.
        """
        for hid in ("venetian", "palazzo", "wynn"):
            with self.subTest(hotel=hid):
                parking = HOTELS[hid]["parking"]
                self.assertIn("poker", parking.lower(),
                              f"{hid}: a hotel recommended for a poker trip must state the "
                              f"venue's poker-room parking rule, not only its paid rate")
        self.assertIn("Poker Room guests", HOTELS["wynn"]["parking"],
                      "the Wynn row keeps its own poker-room parking benefit")

    def test_the_paid_figure_is_still_what_the_site_adds_up(self):
        model = DATA["tripCostModel"]
        self.assertEqual(model["parkingPerNight"], 20.0, "the parking line must stay at the published fee")
        self.assertEqual(model["parkingTotal"], round(model["nights"] * 20.0, 2))
        self.assertFalse(model["parkingWaiver"]["appliedToTotals"])
        self.assertEqual(model["parkingWaiver"]["source"], PARKING_URL)
        self.assertEqual(model["parkingWaiver"]["excerpt"], WAIVER)
        self.assertEqual(model["tripTotal"],
                         round(model["tournamentTotal"] + model["lodgingTotal"] + model["parkingTotal"], 2),
                         "the trip total must remain the sum of its published parts")

    def test_calculator_page_shows_the_waiver_next_to_the_parking_field(self):
        self.assertIn(PARKING_URL.replace("https://", ""), CALC_PAGE)
        self.assertIn("three hours or more", CALC_PAGE)
        self.assertIn("F86", CALC_PAGE, "the calculator must point at the flag that records this")
        # The input still defaults to the paid figure — the waiver is optional, not assumed.
        self.assertRegex(CALC_PAGE.replace("\n", " "), r'id="parking"[^>]*value="20"')


    def test_the_row_discloses_what_the_capture_could_not_reproduce(self):
        """The one clause that is paraphrased, is marked as paraphrased.

        The page's Nevada-resident sentence could not be reproduced byte for byte from this
        environment, so the data paraphrases it instead of quoting it.  A silent quote of a
        sentence whose punctuation was not verified would look like a verbatim capture.
        """
        conditions = HOTELS["venetian"]["parkingWaiver"]["conditions"]
        self.assertIn("paraphrased", conditions)
        self.assertIn("byte for byte", conditions)
        # And every fragment that IS quoted has to be in the capture verbatim.
        capture = plain(CAPTURE)
        quoted = re.findall(r"(?<![\w'])'([^']{25,}?)'(?![\w'])", conditions)
        self.assertEqual(len(quoted), 2, "the row quotes the Sapphire sentence and the event-parking warning")
        for frag in quoted:
            with self.subTest(fragment=frag[:40]):
                self.assertIn(plain(frag), capture)


class CandidateDisclosure(unittest.TestCase):
    SCREEN = "single-entry-on-sheet"

    def screened(self):
        return [e for e in EVENTS
                if (e.get("rules") or {}).get("singleEntry", {}).get("status") == self.SCREEN]

    def test_every_screened_candidate_says_the_cap_is_unconfirmed(self):
        rows = self.screened()
        self.assertEqual(len(rows), 52, "the sheet screen put 52 Venetian rows in the candidate list")
        for e in rows:
            with self.subTest(event=e["id"]):
                excerpt = e["rules"]["singleEntry"]["excerpt"]
                self.assertRegex(
                    excerpt, r"does not state a per-player maximum|maximum-entry count|freezeout",
                    "a candidate row must disclose that the venue has not stated an entry cap",
                )

    def test_no_row_claims_a_written_cap_the_venue_never_printed(self):
        claimants = [e["id"] for e in EVENTS
                     if (e.get("rules") or {}).get("singleEntry", {}).get("status") == "confirmed"]
        self.assertEqual(claimants, [],
                         "no official Strip page read so far prints a one-entry-per-player cap (F31)")

    def test_the_verifier_passes_on_the_committed_data(self):
        proc = subprocess.run([sys.executable, str(ROOT / "scripts" / "verify_entry_labels.py")],
                              capture_output=True, text=True, cwd=ROOT)
        self.assertEqual(proc.returncode, 0, f"verify_entry_labels.py failed:\n{proc.stdout}\n{proc.stderr}")
        self.assertIn("entry-label integrity passed", proc.stdout)

    def test_the_verifier_rejects_a_row_whose_excerpt_grants_an_extra_entry(self):
        """The F75 shape: a candidate whose own quoted text contemplates a re-entry."""
        self.assertTrue(
            self._tripped('reEntry', 're-entry-printed',
                          'The $20 discount can be applied to the initial entry or any subsequent re-entry.'),
            "the verifier must reject a screened row whose re-entry excerpt grants a re-entry",
        )

    def test_the_verifier_rejects_a_confirmation_without_cap_wording(self):
        self.assertTrue(self._tripped('singleEntry', 'confirmed', 'The sheet prints one buy-in.'),
                        "the verifier must reject a 'confirmed' label with no cap in the quoted text")

    def _tripped(self, key: str, status: str, excerpt: str) -> bool:
        """True if the verifier rejects a mutated copy of the published data.

        The module is imported and its DATA retargeted at the mutated copy, so the real
        `site/data.json` is never touched and the check exercised is the one CI runs.
        """
        import contextlib
        import io
        import tempfile

        if str(ROOT / "scripts") not in sys.path:
            sys.path.insert(0, str(ROOT / "scripts"))
        import verify_entry_labels as v

        target = next(e for e in EVENTS
                      if (e.get("rules") or {}).get("singleEntry", {}).get("status") == self.SCREEN)
        payload = json.loads(json.dumps(DATA))
        row = next(e for e in payload["events"] if e["id"] == target["id"])
        row.setdefault("rules", {})[key] = {"status": status, "excerpt": excerpt,
                                            "source": "https://www.venetianlasvegas.com/x.pdf",
                                            "retrieved": "2026-11-17"}
        row["singleEntry"] = True
        with tempfile.TemporaryDirectory() as tmp:
            mutated = Path(tmp) / "data.json"
            mutated.write_text(json.dumps(payload), encoding="utf-8")
            real, v.DATA = v.DATA, mutated
            out = io.StringIO()
            try:
                with contextlib.redirect_stdout(out):
                    code = v.main()
            finally:
                v.DATA = real
            return code != 0 and "problem(s)" in out.getvalue()


class FlagRegister(unittest.TestCase):
    def test_f86_is_registered_officially_and_says_nothing_moved(self):
        f = FLAGS.get("F86")
        self.assertIsNotNone(f, "the parking defect must be on the flag register")
        self.assertEqual(f["area"], "Hotels")
        self.assertEqual(f["source"], PARKING_URL)
        self.assertIn("NO TOTAL WAS CHANGED", f["detail"])
        self.assertIn("F16", f["detail"], "the detail must say why the waiver is not netted off")
        self.assertIn("could not be reached", f["detail"],
                      "unreachable official pages are published as unavailable, never as unchanged")

    def test_the_parking_question_answer_names_the_waiver_and_its_page(self):
        q = next((x for x in DATA["questions"] if x["id"] == "Q12"), None)
        self.assertIsNotNone(q)
        self.assertEqual(q["source"], PARKING_URL)
        self.assertIn("three hours or more", q["answer"])
        self.assertIn("blank", q["answer"], "the properties that could not be reached stay blank, per the rule")


if __name__ == "__main__":
    unittest.main()
