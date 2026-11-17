"""Checks EVERY published trip-window row against the 2026-11-17 live re-read.

`research/reread_2026-11-17.json` covers the 13 rows the day plan uses.
`research/reread_2026-11-17_full_window.json` covers all 20 rows the canonical
data publishes between 2026-11-25 and 2026-12-02, including the multi-flight
Day 1A/1B/1C rows and the Day 2 restarts that a reader could mis-plan around.

These tests fail if `site/data.json` drifts from either record, so a later edit
cannot silently change a value that was re-read from the official page. They
also assert that the full-window record really does cover every published row in
the window, so the record cannot quietly stop being a complete check.
"""
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / "site" / "data.json").read_text(encoding="utf-8"))
RECORD = json.loads(
    (ROOT / "research" / "reread_2026-11-17_full_window.json").read_text(encoding="utf-8")
)

WINDOW_START = "2026-11-25"
WINDOW_END = "2026-12-02"


def published_window_rows():
    return [
        e
        for e in DATA["events"]
        if e.get("venue") == "venetian" and WINDOW_START <= e.get("date", "") <= WINDOW_END
    ]


def find_published(row):
    """The published row for a recorded row, matched on date, time and event number."""
    prefix = f"vl-dse-{row['date']}-{row['event']}-"
    return [e for e in DATA["events"] if e["id"].startswith(prefix)]


class FullWindowReread(unittest.TestCase):
    def test_record_is_dated_and_quoted(self):
        self.assertEqual(RECORD["retrievedOn"], "2026-11-17")
        self.assertTrue(RECORD["scheduleUrl"].startswith("https://www.venetianlasvegas.com/"))
        self.assertEqual(len(RECORD["rows"]), 20)

    def test_record_covers_every_published_trip_window_row(self):
        published = published_window_rows()
        self.assertEqual(
            len(published),
            len(RECORD["rows"]),
            "the live re-read must cover every published row in the trip window",
        )
        recorded = {(r["date"], r["time"], r["event"]) for r in RECORD["rows"]}
        published_keys = set()
        for e in published:
            # id format: vl-dse-<date>-<event no>-<time slug>
            parts = e["id"].split("-")
            date = "-".join(parts[2:5])
            event = parts[5]
            time = e["time"]
            published_keys.add((date, time, event))
        self.assertEqual(recorded, published_keys)

    def test_every_row_matches_the_live_official_page(self):
        for row in RECORD["rows"]:
            with self.subTest(row=f"{row['date']} {row['time']} #{row['event']}"):
                found = find_published(row)
                self.assertEqual(len(found), 1, f"expected one published row, found {len(found)}")
                (e,) = found
                self.assertEqual(e["date"], row["date"])
                self.assertEqual(e["time"], row["time"])
                self.assertEqual(e["buyIn"], row["buyIn"])
                self.assertEqual(e["guarantee"], row["guarantee"])

    def test_continuation_rows_are_never_single_entry_candidates(self):
        """A Day 2 restart or a multi-flight Day 1 row must not be sold as single entry."""
        for row in RECORD["rows"]:
            if not row["continuation"]:
                continue
            with self.subTest(row=f"{row['date']} #{row['event']}"):
                (e,) = find_published(row)
                self.assertFalse(
                    e.get("singleEntry"),
                    "a continuation or multi-flight row must not carry singleEntry=true",
                )
                self.assertIn(e.get("entryType"), {"multi-flight"})

    def test_every_row_still_carries_its_official_source_and_dates(self):
        for row in RECORD["rows"]:
            with self.subTest(row=f"{row['date']} #{row['event']}"):
                (e,) = find_published(row)
                self.assertTrue(e.get("scheduleUrl", "").startswith("https://www.venetianlasvegas.com/"))
                self.assertEqual(e.get("lastChecked"), "2026-11-17")
                self.assertEqual(e.get("lastVerified"), "2026-11-17")


if __name__ == "__main__":
    unittest.main()
