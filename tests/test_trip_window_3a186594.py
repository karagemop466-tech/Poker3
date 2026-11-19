"""Regression for the 2026-11-19 live read of the Venetian DSE IV trip-window rows (session 3a186594).

The live rows in raw/ must match site/data.json exactly, and the checker must fail when a
published value drifts (checked on a temporary copy of the data, never on the real file).
"""
import importlib.util
import json
import pathlib
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "verify_trip_window_3a186594", ROOT / "scripts" / "verify_trip_window_3a186594.py")
checker = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(checker)


class TripWindowLiveRead(unittest.TestCase):
    def test_live_rows_match_published_data(self):
        self.assertEqual(checker.main(), 0)

    def test_window_has_twenty_live_rows(self):
        self.assertEqual(len(checker.live_rows()), 19)

    def test_window_is_the_published_trip(self):
        self.assertEqual(checker.trip_window(), ("2026-11-23", "2026-11-30"))

    def test_checker_fails_on_drifted_time(self):
        data = json.loads(checker.DATA.read_text())
        for e in data["events"]:
            if e["venue"] == "venetian" and e["date"] == "2026-11-23" and e["time"] == "11:10 AM":
                e["time"] = "11:00 AM"
                break
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / "data.json"
            path.write_text(json.dumps(data))
            original = checker.DATA
            checker.DATA = path
            try:
                self.assertEqual(checker.main(), 1)
            finally:
                checker.DATA = original


if __name__ == "__main__":
    unittest.main()
