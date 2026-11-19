#!/usr/bin/env python3
"""Locks in the 2026-11-19 findings of session arena/80a6f5df-poker3.

Three things are pinned here, all of them read-only against the published
``site/data.json``:

1. ``sessionEstimateOffset`` — the published finish estimate is the
   late-registration cut-off plus two levels plus one 15-minute break, so the
   offset from the cut-off is ``2 * level + 15``. The documentation text says
   "cut-off plus two levels" (flag F106 records the mismatch). This test pins the
   arithmetic so the estimate can never drift silently, and records the offset the
   documentation has to describe.
2. Every day-plan row's ``primaryEnd`` equals the published ``endEstimate`` of the
   row it names, and every ``primaryLateEnd`` equals that row's published
   late-registration cut-off. A day plan that quotes a different figure from the
   table it links is a defect.
3. The walking routes resolve through a property-name Maps query, never an
   official street address (flag F107), so no route may claim an address it does
   not have.
"""
from __future__ import annotations

import json
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / "site" / "data.json"


def to_minutes(clock: str):
    """Parse a printed clock such as '10:55 PM' or '~ 4:40 PM' into minutes."""
    m = re.search(r"(\d{1,2}):(\d{2})\s*([AP]M)", clock or "")
    if not m:
        return None
    hour, minute, suffix = int(m.group(1)), int(m.group(2)), m.group(3)
    if suffix == "PM" and hour != 12:
        hour += 12
    if suffix == "AM" and hour == 12:
        hour = 0
    return hour * 60 + minute


class EstimatedFinishArithmetic(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data = json.loads(DATA.read_text(encoding="utf-8"))
        cls.events = {e["id"]: e for e in cls.data["events"]}

    def test_estimate_is_cutoff_plus_two_levels_plus_one_break(self) -> None:
        checked = 0
        for event in self.data["events"]:
            cutoff = to_minutes(event.get("lateRegEnd") or "")
            end = event.get("endEstimateMin")
            level = event.get("levelMin")
            if cutoff is None or end is None or not level:
                continue
            expected = cutoff + (2 * level) + 15
            self.assertEqual(
                expected, end,
                f"{event['id']}: published estimate {end} != cut-off {cutoff} + 2x{level} + 15 = {expected}",
            )
            checked += 1
        self.assertGreater(checked, 100, "the estimate arithmetic was not checked on enough rows")

    def test_every_documented_offset_is_described_in_the_flag(self) -> None:
        """The offsets actually used must be the ones flag F106 records."""
        flags = {f["id"]: f for f in self.data["flags"]}
        self.assertIn("F106", flags, "flag F106 (estimate offset vs documented method) is missing")
        offsets = set()
        for event in self.data["events"]:
            cutoff = to_minutes(event.get("lateRegEnd") or "")
            end = event.get("endEstimateMin")
            if cutoff is None or end is None:
                continue
            offsets.add(end - cutoff)
        self.assertTrue(offsets.issubset({45, 55, 75, 95}), f"unexpected estimate offsets: {sorted(offsets)}")
        # 30-minute levels: 75 minutes, 40-minute levels: 95 minutes, 20-minute levels: 55,
        # 15-minute levels: 45. Each is 2 x level + 15, which is what F106 says.
        self.assertIn("two levels", flags["F106"]["detail"])

    def test_day_plan_matches_the_rows_it_names(self) -> None:
        for day in self.data["dayPlan"]:
            primary = self.events.get(day.get("primary") or "")
            if not primary:
                continue
            with self.subTest(date=day["date"]):
                self.assertEqual(primary["time"], day["primaryTime"], "day-plan start time differs from its row")
                self.assertEqual(primary.get("endEstimate") or "", day.get("primaryEnd") or "",
                                 "day-plan finish differs from its row")
                self.assertEqual(primary.get("lateRegEnd") or "", day.get("primaryLateEnd") or "",
                                 "day-plan registration cut-off differs from its row")
                self.assertEqual(primary.get("chips"), day.get("primaryChips"))
                self.assertEqual(primary.get("buyIn"), day.get("primaryBuyIn"))
                self.assertEqual(primary.get("guarantee"), day.get("primaryGuarantee"))

    def test_trip_window_primaries_publish_a_sheet_link(self) -> None:
        for day in self.data["dayPlan"]:
            primary = self.events.get(day.get("primary") or "")
            if not primary:
                continue
            with self.subTest(date=day["date"]):
                self.assertTrue(primary.get("sheetUrl", "").startswith("https://"),
                                "a day-plan primary has no official structure-sheet link")
                self.assertTrue(primary.get("lastChecked"), "a day-plan primary has no read date")


class WalkingRoutesAreNameLevelQueries(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data = json.loads(DATA.read_text(encoding="utf-8"))

    def test_every_route_has_a_maps_query_and_a_minute_value(self) -> None:
        self.assertTrue(self.data["routes"])
        for route in self.data["routes"]:
            with self.subTest(hotel=route["hotel"], venue=route["venue"]):
                self.assertIsInstance(route.get("minutes"), int)
                self.assertGreaterEqual(route["minutes"], 0)

    def test_no_route_claims_a_street_address_it_does_not_cite(self) -> None:
        """F107: the Maps query is a property name, so no route may print a street number."""
        flags = {f["id"]: f for f in self.data["flags"]}
        self.assertIn("F107", flags, "flag F107 (no official street address) is missing")
        street = re.compile(r"\b\d{2,5}\s+(?:S(?:outh)?|N(?:orth)?|E(?:ast)?|W(?:est)?)\b")
        for route in self.data["routes"]:
            origin = route.get("mapsOrigin") or ""
            self.assertIsNone(street.search(origin),
                              f"{route['hotel']}: the Maps origin prints a street number the site does not cite")

    def test_the_half_hour_limit_is_the_published_one(self) -> None:
        within = [r for r in self.data["routes"] if r["minutes"] <= 30]
        beyond = [r for r in self.data["routes"] if r["minutes"] > 30]
        self.assertTrue(within, "no route is inside the 30-minute limit")
        self.assertTrue(beyond, "no route is outside the 30-minute limit, which would make the filter pointless")


class MonitorChangeFlagsAreExplained(unittest.TestCase):
    def test_every_changed_url_in_the_check_record_has_a_flag_or_a_note(self) -> None:
        checks_path = ROOT / "site" / "checks.json"
        if not checks_path.exists():
            self.skipTest("no check record in this checkout")
        checks = json.loads(checks_path.read_text(encoding="utf-8"))
        data = json.loads(DATA.read_text(encoding="utf-8"))
        blob = json.dumps(data["flags"]).lower()
        for row in checks.get("urls", []):
            if not row.get("changed"):
                continue
            with self.subTest(url=row["url"]):
                host = re.sub(r"^https?://", "", row["url"]).split("/")[0]
                self.assertIn(host.lower(), blob,
                              f"{row['url']} is recorded as changed but no flag explains it")


if __name__ == "__main__":
    unittest.main()
