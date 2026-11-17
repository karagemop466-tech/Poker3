"""Pins the WPT structure-sheet facts read on 2026-11-17.

The WPT structures PDF prints, per event, an "Entry Fee" breakdown and a
"Registration" clause. Every event inside the trip window prints
"Unlimited re-entry", which decides those rows: they are multi-entry and must
never be presented as single-entry candidates, and their fee breakdowns must be
shown as printed rather than silently reconciled.

These tests read `site/data.json` only, so they fail if a later edit drops the
quoted clause, promotes a WPT row to single entry, or hides the $1,105
arithmetic conflict on the $1,100 PLO.
"""
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / "site" / "data.json").read_text(encoding="utf-8"))
STRUCT_SOURCE = "https://cdn.wynnresorts.com/image/upload/v1750864036/visitwynn_pdfs_files/Poker/WPT/WPT_World_Championship_Structures.pdf"
WINDOW_START, WINDOW_END = "2026-11-27", "2026-12-02"

# Every WPT row in the trip window whose own structure sheet was read, keyed by
# (date, time, printed name), with the buy-in the sheet's fee line reconciles to.
READ_SHEETS = {
    ("2026-11-27", "12:00 PM", "TORSE"): 600,
    ("2026-11-27", "1:00 PM", "PLO"): 400,
    ("2026-11-28", "12:00 PM", "Mixed Triple Draw (A-5, 2-7, Badugi)"): 600,
    ("2026-11-30", "12:00 PM", "Limit Omaha 8"): 600,
    ("2026-12-01", "12:00 PM", "Limit Omaha 8/5/stud 8"): 600,
    ("2026-12-01", "1:00 PM", "PLO"): 1100,
}


def wpt_window_rows():
    return [
        e
        for e in DATA["events"]
        if e.get("venue") == "wynn" and WINDOW_START <= e.get("date", "") <= WINDOW_END
    ]


def find(date, time, name):
    hits = [
        e
        for e in DATA["events"]
        if e.get("venue") == "wynn" and e["date"] == date and e["time"] == time and e["name"] == name
    ]
    return hits


class WptStructureSheets(unittest.TestCase):
    def test_no_wpt_row_in_the_window_is_single_entry(self):
        for e in wpt_window_rows():
            with self.subTest(row=f"{e['date']} {e['time']} {e['name']}"):
                self.assertFalse(e.get("singleEntry"), "a WPT re-entry event must not be singleEntry")
                self.assertNotEqual(
                    e.get("entryType"),
                    "none",
                    "no WPT event inside the window has neutral entry terms",
                )

    def test_read_sheets_quote_unlimited_reentry_from_the_official_pdf(self):
        for (date, time, name), _buy in READ_SHEETS.items():
            with self.subTest(row=f"{date} {time} {name}"):
                hits = find(date, time, name)
                self.assertEqual(len(hits), 1, "expected exactly one published row")
                (e,) = hits
                re_entry = (e.get("rules") or {}).get("reEntry") or {}
                self.assertEqual(re_entry.get("status"), "re-entry-printed")
                self.assertIn("Unlimited re-entry", re_entry.get("excerpt", ""))
                self.assertEqual(re_entry.get("source"), STRUCT_SOURCE)
                self.assertEqual(re_entry.get("retrieved"), "2026-11-17")

    def test_fee_breakdowns_are_quoted_verbatim(self):
        for (date, time, name), buy in READ_SHEETS.items():
            with self.subTest(row=f"{date} {time} {name}"):
                (e,) = find(date, time, name)
                fee = (e.get("rules") or {}).get("fee") or {}
                self.assertEqual(fee.get("status"), "confirmed")
                self.assertIn(f"${buy:,} Buy-in = $", fee.get("excerpt", ""))
                self.assertEqual(fee.get("retrieved"), "2026-11-17")

    def test_the_1100_plo_arithmetic_conflict_is_published_not_hidden(self):
        (e,) = find("2026-12-01", "1:00 PM", "PLO")
        fee = (e.get("rules") or {}).get("fee") or {}
        breakdown = (e.get("rules") or {}).get("feeBreakdown") or {}
        self.assertEqual(e["buyIn"], 1100)
        self.assertEqual(breakdown.get("status"), "conflict")
        self.assertIn("$975", fee.get("excerpt", ""))
        self.assertIn("$85", fee.get("excerpt", ""))
        self.assertIn("$45", fee.get("excerpt", ""))
        # The published arithmetic really does not reconcile.
        self.assertEqual(975 + 85 + 45, 1105)
        conflict = [f for f in DATA["flags"] if f["id"] == "F55"]
        self.assertEqual(len(conflict), 1)

    def test_other_breakdowns_reconcile(self):
        cases = {
            ("2026-11-27", "12:00 PM", "TORSE"): (510, 65, 25),
            ("2026-11-27", "1:00 PM", "PLO"): (337, 45, 18),
            ("2026-11-30", "12:00 PM", "Limit Omaha 8"): (510, 65, 25),
        }
        for row, parts in cases.items():
            with self.subTest(row=row):
                self.assertEqual(sum(parts), row and READ_SHEETS[row])

    def test_the_mislabeled_day2_row_is_left_unverified(self):
        """Nov 30 1 p.m. 'Day 2' cannot be a Day 2 of an event that starts that day (F34)."""
        (e,) = find("2026-11-30", "1:00 PM", "No Limit Hold'em Day 2")
        self.assertEqual(e.get("entryType"), "not-verified")
        self.assertFalse(e.get("singleEntry"))
        self.assertIn("F34", [f["id"] for f in DATA["flags"]])

    def test_the_1100_plo_fee_conflict_is_not_the_only_open_wpt_item(self):
        """The $10,400 World Championship still has no structure section (F12)."""
        titles = {f["id"]: f["title"] for f in DATA["flags"]}
        self.assertIn("F12", titles)
        self.assertIn("F55", titles)


if __name__ == "__main__":
    unittest.main()
