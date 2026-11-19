#!/usr/bin/env python3
"""Regression checks for session arena/e830d773-poker3 (2026-11-19).

Covers:
1. Official Caesars Entertainment parking rates (https://www.caesars.com/parking)
   for Caesars Palace ($20/day guest self-parking, $50/day valet) and Horseshoe
   Las Vegas ($20 Mon-Wed / $25 Thu-Sun self-parking, $40/day valet, with no
   fabricated flat single-night constant in parkingPerNight).
2. 2026-11-19 line-by-line re-reads of Wynn_Signature_Series_Schedule.pdf (38 rows),
   Poker-All_Daily_Structures.pdf (including the $205 vs $200 rebuy sum in F105),
   WPT_World_Championship_Structures.pdf, Bellagio hotel and Mandalay Bay poker pages.
3. Static-page factual accuracy across site/hotels.html, site/venues.html,
   site/venues/others.html, site/flagged.html, and site/coverage.json.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
DATA = json.loads((SITE / "data.json").read_text(encoding="utf-8"))
COVERAGE = json.loads((SITE / "coverage.json").read_text(encoding="utf-8"))
CAESARS_PARKING = "https://www.caesars.com/parking"


class CaesarsParkingAndHotelCompletenessTests(unittest.TestCase):
    def setUp(self):
        self.hotels = {h["id"]: h for h in DATA["hotels"]}

    def test_caesars_palace_carries_official_parking_dollars_and_per_night_rate(self):
        c = self.hotels["caesars"]
        self.assertEqual(c["parkingSource"], CAESARS_PARKING)
        self.assertEqual(c["parkingPerNight"], 20.0)
        self.assertEqual(c["lastChecked"], "2026-11-19")
        self.assertIn("Registered Hotel Guests: $20/day", c["parking"])
        self.assertIn("$50/day", c["parking"])
        self.assertNotIn("No dollar amount is published", c["parking"])

    def test_horseshoe_carries_weekday_weekend_parking_without_fake_flat_constant(self):
        h = self.hotels["horseshoe"]
        self.assertEqual(h["parkingSource"], CAESARS_PARKING)
        self.assertIsNone(h.get("parkingPerNight"),
                          "Horseshoe splits guest self-parking ($20 Mon-Wed / $25 Thu-Sun); must not fake one constant")
        self.assertEqual(h["lastChecked"], "2026-11-19")
        self.assertIn("Monday - Wednesday $20/day | Thursday - Sunday $25/day", h["parking"])
        self.assertIn("$40/day", h["parking"])
        self.assertNotIn("No dollar amount is published", h["parking"])

    def test_all_eight_hotels_publish_parking_figures_and_official_sources(self):
        self.assertEqual(len(self.hotels), 8)
        for hid, h in self.hotels.items():
            with self.subTest(hotel=hid):
                self.assertTrue(h.get("parking"), f"{hid}: empty parking text")
                self.assertTrue((h.get("parkingSource") or "").startswith("https://"), f"{hid}: bad parkingSource")
                self.assertNotIn("No dollar amount is published", h["parking"], f"{hid}: stale missing-dollar note")

    def test_caesars_parking_is_registered_in_monitored_sources(self):
        by_id = {s["id"]: s for s in DATA["sources"]}
        self.assertIn("caesars-parking", by_id)
        self.assertEqual(by_id["caesars-parking"]["url"], CAESARS_PARKING)
        self.assertEqual(by_id["caesars-parking"]["checked"], "2026-11-19")


class NonVenetianRereadTests(unittest.TestCase):
    def test_no_event_row_remains_stranded_at_2026_11_16(self):
        stranded = [e["id"] for e in DATA["events"] if e.get("lastChecked") == "2026-11-16"]
        self.assertEqual(stranded, [], f"event rows still at 2026-11-16: {stranded[:5]}")

    def test_wynn_signature_rows_reflect_schedule_reread_and_placeholder_structures(self):
        sig = [e for e in DATA["events"] if e["id"].startswith("wynn-sig-")]
        self.assertEqual(len(sig), 38)
        for e in sig:
            with self.subTest(row=e["id"]):
                self.assertEqual(e["lastChecked"], "2026-11-19")
                self.assertEqual(e["lastVerified"], "2026-11-17")
                self.assertEqual(e["rules"]["singleEntry"]["status"], "not-verified")
                self.assertIn("COMING SOON", e["rules"]["singleEntry"]["excerpt"])

    def test_wynn_daily_rows_and_rebuy_sum_flag(self):
        daily = [e for e in DATA["events"] if e["id"].startswith("wynn-daily-")]
        self.assertEqual(len(daily), 4)
        for e in daily:
            with self.subTest(row=e["id"]):
                self.assertEqual(e["lastChecked"], "2026-11-19")
                self.assertEqual(e["lastVerified"], "2026-11-19")
        friday = [e for e in daily if e["buyIn"] == 240][0]
        self.assertIn("F105", friday["note"])

    def test_reread_sources_carry_2026_11_19(self):
        by_id = {s["id"]: s for s in DATA["sources"]}
        for sid in ("wynn-sig-sched", "wynn-daily-struct", "wynn-wpt-struct",
                    "bell-hotel", "mandalay-poker", "caesars-parking"):
            with self.subTest(source=sid):
                self.assertEqual(by_id[sid]["checked"], "2026-11-19")


class StaticPageAccuracyTests(unittest.TestCase):
    def test_hotels_page_has_no_contradictory_hero_or_asof_misstamps(self):
        text = (SITE / "hotels.html").read_text(encoding="utf-8")
        self.assertNotIn("For the recommended trip dates it returned no suite at all", text)
        self.assertNotIn("captured on <span data-asof>", text)
        self.assertNotIn("opened on <span data-asof>", text)
        self.assertNotIn("priced the recommended window on <span data-asof>", text)
        self.assertNotIn("Resort fee and tax for MGM Grand and ARIA", text)
        self.assertNotIn("Horseshoe Las Vegas is the only reviewed property that published dated per-night rates", text)

    def test_venues_page_cites_correct_flags_and_route_dates(self):
        text = (SITE / "venues.html").read_text(encoding="utf-8")
        self.assertNotIn("read on\n        <span data-asof>", text)
        self.assertNotIn("flags F78 and F79", text)
        self.assertNotIn("(flag F80)", text)
        self.assertIn("F79, F80 and F103", text)
        self.assertIn("(flag F85)", text)

    def test_others_venue_page_names_all_five_rendered_rooms(self):
        text = (SITE / "venues" / "others.html").read_text(encoding="utf-8")
        for room in ("Bellagio", "MGM Grand", "Caesars Palace", "Horseshoe", "ARIA"):
            with self.subTest(room=room):
                self.assertIn(room, text)
        self.assertNotIn("<h1>ARIA &amp; Bellagio", text)

    def test_flagged_page_does_not_claim_mgm_or_aria_resort_fees_are_blank(self):
        text = (SITE / "flagged.html").read_text(encoding="utf-8")
        self.assertNotIn("MGM Grand and ARIA hotel resort fees", text)

    def test_coverage_c9_cites_f86_not_f79_and_is_fresh(self):
        c9 = next(item for item in COVERAGE["items"] if item["id"] == "C9")
        self.assertIn("(F86)", c9["note"])
        self.assertNotIn("(F79)", c9["note"])
        # Confirm scripts/coverage.py reproduces site/coverage.json without drift.
        before = (SITE / "coverage.json").read_text(encoding="utf-8")
        subprocess.run([sys.executable, str(ROOT / "scripts" / "coverage.py")],
                       cwd=ROOT, check=True, capture_output=True)
        after = (SITE / "coverage.json").read_text(encoding="utf-8")
        self.assertEqual(before, after, "site/coverage.json drifted from scripts/coverage.py")

    def test_session_flags_and_verbatim_record_exist(self):
        flags = {f["id"]: f for f in DATA["flags"]}
        self.assertEqual(len(flags), len(DATA["flags"]), "duplicate flag IDs")
        for fid in ("F102", "F103", "F104", "F105"):
            with self.subTest(flag=fid):
                self.assertIn(fid, flags)
                self.assertTrue(flags[fid]["source"].startswith("https://"))
        self.assertTrue((ROOT / "research" / "reread_2026-11-19_arena-e830d773.md").exists())


if __name__ == "__main__":
    unittest.main()
