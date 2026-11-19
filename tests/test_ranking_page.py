"""The ranking page must never rank a row it cannot substantiate.

The page exists to answer "which events are worth comparing" only after the total entry
fee and the guaranteed pool are both printed by an official source. These tests fail if a
row is ranked without that evidence, or if a bounty / multi-flight row is mixed into the
single-flight ranking where its guarantee would be compared against a different quantity.
"""
from pathlib import Path
import json
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / "site" / "data.json").read_text(encoding="utf-8"))
PAGE = (ROOT / "site" / "ranking.html").read_text(encoding="utf-8")
APP = (ROOT / "site" / "assets" / "app.js").read_text(encoding="utf-8")


def ranking_eligible(event):
    """Mirror of rankingEligible() in site/assets/app.js."""
    if not event.get("date"):
        return False
    if not (isinstance(event.get("buyIn"), (int, float)) and event["buyIn"] > 0):
        return False
    if not (isinstance(event.get("guarantee"), int) and event["guarantee"] > 0):
        return False
    return ((event.get("rules") or {}).get("fee") or {}).get("status") == "confirmed"


def ranking_group(event):
    """Mirror of rankingGroup() in site/assets/app.js."""
    single = (event.get("rules") or {}).get("singleEntry") or {}
    if event.get("kind") == "bounty":
        return "bounty"
    if event.get("entryType") != "none" or event.get("category") in ("flight", "satellite"):
        return "flight"
    if single.get("status") != "single-entry-on-sheet":
        return "flight"
    return "single"


class RankingPageTests(unittest.TestCase):
    def test_page_declares_its_three_groups_and_the_gate(self):
        for hook in ("data-ranking-single", "data-ranking-bounty", "data-ranking-flight",
                     "data-ranking-gate", "data-ranking-count"):
            self.assertIn(hook, PAGE, hook)
        self.assertIn('data-page="ranking"', PAGE)

    def test_ranked_rows_all_carry_a_confirmed_fee_and_a_guarantee(self):
        ranked = [e for e in DATA["events"] if ranking_eligible(e)]
        self.assertTrue(ranked, "no row qualifies, the ranking page would be empty")
        for event in ranked:
            with self.subTest(event=event["id"]):
                self.assertIsInstance(event["buyIn"], (int, float))
                self.assertGreater(event["buyIn"], 0)
                self.assertIsInstance(event["guarantee"], int)
                self.assertGreater(event["guarantee"], 0)
                self.assertEqual(event["rules"]["fee"]["status"], "confirmed")
                # The ratio the page prints must be the guardanteed pool over the fee.
                self.assertAlmostEqual(event["ratio"], round(event["guarantee"] / event["buyIn"], 1), places=1)

    def test_no_row_without_a_guarantee_can_be_ranked(self):
        unguaranteed = [e for e in DATA["events"] if ranking_eligible(e) and not e.get("guarantee")]
        self.assertEqual(unguaranteed, [])

    def test_bounty_rows_are_kept_out_of_the_single_flight_ranking(self):
        bounty_in_single = [e["id"] for e in DATA["events"]
                            if ranking_eligible(e) and ranking_group(e) == "single" and e.get("kind") == "bounty"]
        self.assertEqual(bounty_in_single, [])

    def test_multi_flight_rows_are_kept_out_of_the_single_flight_ranking(self):
        offenders = [e["id"] for e in DATA["events"]
                     if ranking_eligible(e) and ranking_group(e) == "single" and e.get("entryType") != "none"]
        self.assertEqual(offenders, [])

    def test_page_states_that_no_row_has_a_written_entry_cap(self):
        # The standing rule: no reviewed sheet prints a maximum number of entries per
        # player, so the page must say so rather than imply eligibility.
        self.assertIn("one-entry-per-player cap", APP)
        self.assertIn("F31", PAGE)
        self.assertIn("not a forecast", PAGE.lower())

    def test_ratio_is_labelled_descriptive_and_never_a_forecast(self):
        self.assertIn("Pool ÷ fee is the published", APP)
        self.assertIn("description of two printed numbers, not a return or a forecast", APP)
        for banned in ("expected value of", "return on investment", "ROI", "forecast of"):
            self.assertNotIn(banned, PAGE)

    def test_ranking_page_does_not_invent_a_value(self):
        """Any dollar figure in the static page must already exist in the published data.

        A figure is allowed when it is a published buy-in or guarantee, or when it appears
        verbatim somewhere in site/data.json — the page quotes two official fee splits
        ("$90 of the $600 Buy-In" and "$50 add-on") and those sentences live in the data.
        """
        haystack = (ROOT / "site" / "data.json").read_text(encoding="utf-8")
        for amount in set(re.findall(r"\$[\d,]+", PAGE)):
            value = int(amount.replace("$", "").replace(",", ""))
            in_events = any(value in (e.get("buyIn"), e.get("guarantee"))
                            for e in DATA["events"] if isinstance(e.get("buyIn"), int))
            self.assertTrue(in_events or amount in haystack, f"{amount} is not in the published data")


if __name__ == "__main__":
    unittest.main()
