#!/usr/bin/env python3
"""Every stored walking minute that claims a 2026-11-17 Google Maps read must match its raw capture.

`raw/google_maps_walk_2026-11-17.json` holds the route cards that were read in walking mode on 2026-11-17.
`scripts/data_hotels.py` ROUTES rows that carry a `walkCapture` key must reproduce the first card's minutes and
miles, use the same query as the capture, and name the capture's own record. A row cannot quietly drift from its
evidence, and a capture cannot be deleted without this test failing.
"""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

CAPTURE = json.loads((ROOT / "raw" / "google_maps_walk_2026-11-17.json").read_text(encoding="utf-8"))
RECORDS = {r["id"]: r for r in CAPTURE["records"]}
MODE_FLAT = ("mostly flat", "principalement plat")
LIMIT_MIN = 30


def _routes():
    import data_hotels as H  # imported lazily so a syntax error reports as a test failure
    return H.ROUTES, H.MAPS


class WalkCaptureIntegrity(unittest.TestCase):
    def test_capture_has_all_eight_hotels_to_venetian(self):
        pairs = {(r["id"].rsplit("-to-", 1)[0]) for r in CAPTURE["records"] if r["id"].endswith("-to-venetian")}
        self.assertEqual(pairs, {"palazzo", "wynn", "bellagio", "mgm", "caesars", "horseshoe", "aria"},
                         "the seven non-Venetian hotels must each have a capture to the Venetian poker room")
        self.assertIn("venetian-to-bellagio", RECORDS)
        self.assertIn("control-driving-venetian-to-bellagio", RECORDS)

    def test_every_walking_record_has_a_flat_mode_marker_and_a_card(self):
        for rid, rec in RECORDS.items():
            if rid.startswith("control-"):
                continue
            marker = rec["modeMarker"].lower()
            self.assertTrue(any(m in marker for m in MODE_FLAT), f"{rid}: walking-mode marker missing")
            self.assertTrue(rec["routes"], f"{rid}: no route cards")

    def test_driving_control_is_not_walking(self):
        ctrl = RECORDS["control-driving-venetian-to-bellagio"]
        self.assertFalse(any(m in ctrl["modeMarker"].lower() for m in MODE_FLAT))
        walk = RECORDS["venetian-to-bellagio"]
        self.assertGreater(walk["routes"][0]["minutes"], ctrl["routes"][0]["minutes"],
                           "walking must read longer than driving for the same pair")

    def test_stored_routes_reproduce_the_capture(self):
        routes, maps_template = _routes()
        checked = 0
        for row in routes:
            cap_id = row.get("walkCapture")
            if not cap_id:
                continue
            checked += 1
            rec = RECORDS[cap_id]
            first = rec["routes"][0]
            self.assertEqual(row["minutes"], first["minutes"], f"{cap_id}: minutes differ from the capture")
            self.assertEqual(row["miles"], first["miles"], f"{cap_id}: miles differ from the capture")
            self.assertEqual(row["lastReadOn"], CAPTURE["captured"], f"{cap_id}: read date differs")
            url = maps_template.format(o=row["mapsOrigin"], d=row["mapsDestination"])
            self.assertEqual(url, rec["url"], f"{cap_id}: the stored query does not reproduce the captured link")
        self.assertEqual(checked, 8, "seven non-Venetian hotels to the Venetian plus the Venetian-to-Bellagio reverse must carry a capture")

    def test_thirty_minute_limit_on_every_shown_route(self):
        """The 30-minute limit is applied to the recommended card. ARIA is out on every card shown."""
        for rid, rec in RECORDS.items():
            if rid.startswith("control-"):
                continue
            best = min(c["minutes"] for c in rec["routes"])
            worst = max(c["minutes"] for c in rec["routes"])
            if rid == "aria-to-venetian":
                self.assertGreater(best, LIMIT_MIN, "ARIA must be outside 30 minutes on every card shown")
            elif rid == "mgm-to-venetian":
                self.assertGreater(best, LIMIT_MIN)
            else:
                self.assertLessEqual(rec["routes"][0]["minutes"], LIMIT_MIN, f"{rid} recommended card over 30 min")
                self.assertLessEqual(worst, LIMIT_MIN + 10, f"{rid} alternate card unexpectedly long")

    def test_flags_point_to_the_capture_and_no_press_source_is_official(self):
        import data_source as D
        ids = {f["id"] for f in D.FLAGS}
        for needed in ("F77", "F78", "F79", "F80"):
            self.assertIn(needed, ids)
        for f in D.FLAGS:
            if f["id"] in ("F77", "F78", "F79", "F80"):
                self.assertTrue(f["source"].startswith("https://"), f["id"])


if __name__ == "__main__":
    unittest.main()
