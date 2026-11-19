"""Bot blocks must not be published as failures; counts must read as counts.

Three regressions are pinned here (session arena/16cd67ca-poker3, re-implementing
PR #130's fixes on current main):

1. `scripts/check_sources.py` classifies each fetch as fetched / blocked /
   redirected / unreachable / error and publishes `blocked` and `unavailable`
   separately; `failed` stays as the legacy alias for their total.
2. The Sources page labels a blocked row "Blocked for the robot, not missing ·
   read by hand" and checks that label BEFORE "Unavailable", so a block can
   never fall through to the worse label.
3. The calculator's like-for-like table leads its Nights and Entries columns
   with the count ("7 nights = ...", "7 entries = ..."), not with money.
4. `walkToVenetian()` returns the venue -> Venetian walk (Wynn 13 min), not
   the reverse Venetian -> venue walk (19 min) under a "walk to the Venetian"
   label.
"""
from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP_JS = (ROOT / "site" / "assets" / "app.js").read_text(encoding="utf-8")
CHECK_SOURCES = (ROOT / "scripts" / "check_sources.py").read_text(encoding="utf-8")
CALCULATOR = (ROOT / "site" / "calculator.html").read_text(encoding="utf-8")
DATA = json.loads((ROOT / "site" / "data.json").read_text(encoding="utf-8"))


class CheckSourcesSummaryTests(unittest.TestCase):
    def test_script_publishes_blocked_and_unavailable_separately(self):
        for needle in ('"blocked"', '"unavailable"', '"failed"'):
            self.assertIn(needle, CHECK_SOURCES, f"check_sources.py no longer writes {needle}")
        self.assertIn("def classify_outcome", CHECK_SOURCES)
        self.assertIn("BOT_BLOCKED_HOSTS", CHECK_SOURCES)

    def test_failed_is_the_legacy_alias_for_blocked_plus_unavailable(self):
        # The summary counts blocked (403/401/429/3xx) and unavailable
        # (unreachable/error) separately; failed is their total so older
        # readers keep working.
        self.assertIn('sum(1 for r in rows if r.get("unavailable"))', CHECK_SOURCES)


class BlockedBadgeTests(unittest.TestCase):
    def test_blocked_badge_is_checked_before_unavailable(self):
        # In the per-row badge helper, the blocked label must be tested before
        # the unavailable label: a blocked row is also unavailable=true, so
        # testing unavailable first would mislabel every block as a failure.
        helper = APP_JS[APP_JS.index("function sourceStatusBadges"):]
        helper = helper[: helper.index("function sourceLinks")]
        self.assertLess(helper.index("Blocked for the robot"), helper.index("Source unavailable"),
                        "blocked badge must be checked before the unavailable badge")

    def test_autochecks_table_labels_blocks_before_unavailable(self):
        table = APP_JS[APP_JS.index("data-autochecks"):]
        table = table[: table.index("cross-table search")]
        self.assertLess(table.index("Blocked for the robot"), table.index("Unavailable · not verified"),
                        "the autochecks table must label blocks before unavailability")

    def test_summary_shows_blocked_and_unavailable_counts(self):
        self.assertIn("Blocked for the robot", APP_JS)
        self.assertIn("sum.blocked", APP_JS)
        self.assertIn("sum.unavailable", APP_JS)


class CalculatorCountColumnTests(unittest.TestCase):
    def test_nights_and_entries_columns_lead_with_the_count(self):
        self.assertIn("nights + ' nights'", CALCULATOR)
        self.assertIn("entries + ' entries = '", CALCULATOR)

    def test_tournament_total_uses_the_published_exact_sum(self):
        self.assertIn("model.tournamentTotal", CALCULATOR)

    def test_published_model_carries_the_exact_sum(self):
        model = DATA["tripCostModel"]
        self.assertAlmostEqual(model["primaryBuyInSum"], 2600.00, places=2)
        self.assertAlmostEqual(model["tournamentTotal"], 2600.00, places=2)
        self.assertAlmostEqual(model["tripTotal"], 4120.96, places=2)
        self.assertAlmostEqual(model["liveQuote"]["tripTotal"], 6750.55, places=2)


class WalkDirectionTests(unittest.TestCase):
    def test_walk_to_venetian_looks_up_venue_to_venetian(self):
        fn = APP_JS[APP_JS.index("function walkToVenetian"):]
        fn = fn[: fn.index("function applyTournamentFilters")]
        self.assertIn("x.hotel === venue && x.venue === 'venetian'", fn,
                      "walkToVenetian must look up venue -> Venetian, not Venetian -> venue")

    def test_wynn_walk_to_venetian_is_13_not_19(self):
        routes = {(r["hotel"], r["venue"]): r["minutes"] for r in DATA["routes"]}
        self.assertEqual(routes[("wynn", "venetian")], 13)
        self.assertEqual(routes[("venetian", "wynn")], 19)


class ChangedSourceFlagTests(unittest.TestCase):
    def test_venetian_poker_page_change_is_flagged_for_manual_reread(self):
        flags = {f["id"]: f for f in DATA["flags"]}
        self.assertIn("F92", flags, "the 2026-11-18 wording change needs its own flag")
        flag = flags["F92"]
        self.assertEqual(flag["source"], "https://www.venetianlasvegas.com/resort/casino/poker.html")
        self.assertIn("2026-11-18", flag["detail"])
        self.assertIn("re-read", flag["detail"].lower())


if __name__ == "__main__":
    unittest.main()
