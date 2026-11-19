"""The day plan must never present a fallback as a second event on the same day.

Defect fixed on 2026-11-19 (flagged as F94 on the Flagged for review page). On five of
the seven trip days the published "conditional fallback" was the very same event the
site simultaneously published as an "impossible sequence" against that day's primary.
The two blocks contradicted each other: one said the pair cannot be played, the other
offered the pair as the plan.

These tests do not re-read any official page and assert no new value. They check the
internal consistency of what is already published:

* every fallback carries an explicit sequence status and a plain-language note that
  matches it, so "replaces" and "playable after" can never be confused;
* a fallback marked "after" really does start after the primary's estimated finish plus
  the published transfer allowance;
* a fallback that is published as an impossible sequence is honestly labelled
  "replaces";
* the schedule page counts playable days, not calendar days.
"""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / "site" / "data.json").read_text())
PLAN = DATA["dayPlan"]
NOTES = DATA["planNotes"]

_CLOCK = re.compile(r"(\d{1,2}):(\d{2})\s*([ap])\.?m\.?", re.I)


def clock_minutes(text):
    if not text:
        return None
    m = _CLOCK.search(text)
    if not m:
        return None
    hh, mm, ap = int(m.group(1)), int(m.group(2)), m.group(3).lower()
    if hh == 12:
        hh = 0
    if ap == "p":
        hh += 12
    return hh * 60 + mm


class FallbackIsNotASecondEntry(unittest.TestCase):
    def setUp(self):
        self.events = {e["id"]: e for e in DATA["events"]}
        self.conflicts = {
            (c["date"], frozenset((c["first"], c["second"]))) for c in DATA["planConflicts"]
        }

    def test_every_fallback_has_a_sequence_status(self):
        for day in PLAN:
            with self.subTest(date=day["date"]):
                if not day["fallback"]:
                    self.assertEqual(day["fallbackSequence"], "")
                    continue
                self.assertIn(day["fallbackSequence"], ("after", "replaces", "unknown"))
                self.assertTrue(day["fallbackSequenceNote"])

    def test_fallback_note_matches_status(self):
        for day in PLAN:
            if not day["fallback"]:
                continue
            with self.subTest(date=day["date"]):
                note = day["fallbackSequenceNote"]
                if day["fallbackSequence"] == "replaces":
                    self.assertIn("Replaces the primary", note)
                    self.assertNotIn("Playable after the primary", note)
                elif day["fallbackSequence"] == "after":
                    self.assertIn("Playable after the primary", note)

    def test_after_status_really_starts_late_enough(self):
        transfer = NOTES["transfer"]
        for day in PLAN:
            if day["fallbackSequence"] != "after":
                continue
            event = self.events[day["fallback"]]
            start = clock_minutes(event["time"])
            end = self.events[day["primary"]]["endEstimateMin"]
            with self.subTest(date=day["date"]):
                self.assertIsNotNone(start)
                self.assertIsNotNone(end)
                self.assertGreaterEqual(
                    start, end + transfer,
                    "a fallback labelled 'playable after the primary' starts before the "
                    "primary's estimated finish plus the published transfer allowance",
                )

    def test_any_fallback_flagged_impossible_is_labelled_replaces(self):
        """The exact contradiction this session found must stay impossible."""
        for day in PLAN:
            if not day["fallback"]:
                continue
            key = (day["date"], frozenset((day["primary"], day["fallback"])))
            with self.subTest(date=day["date"]):
                if key in self.conflicts:
                    self.assertEqual(
                        day["fallbackSequence"], "replaces",
                        "this fallback is published as an impossible sequence against the "
                        "primary, so it cannot also be described as playable after it",
                    )
                    self.assertIn("Replaces the primary", day["fallbackSequenceNote"])

    def test_published_fallback_rule_states_the_replaces_reading(self):
        rule = NOTES["fallbackRule"].lower()
        self.assertIn("replaces the primary", rule)
        self.assertIn("never in addition to it", rule)


class SchedulePageCountsPlayableDays(unittest.TestCase):
    def test_schedule_copy_does_not_call_the_checkout_day_a_playable_day(self):
        page = (ROOT / "site" / "schedule.html").read_text()
        self.assertNotIn("Eight days", page)
        self.assertIn("Seven playable days", page)

    def test_day_plan_length_equals_playable_nights(self):
        self.assertEqual(len(PLAN), DATA["trip"]["days"])
        self.assertEqual(DATA["trip"]["days"], DATA["trip"]["nights"])
        self.assertNotIn(DATA["trip"]["end"], [d["date"] for d in PLAN])


if __name__ == "__main__":
    unittest.main()
