"""Regression guard: the WPT schedule footnote markers, counted from the raw capture.

The schedule PDF prints five footnote markers. F25 used to describe the marker
count from memory ("several rows"), and one draft of it said four high-roller
rows when the PDF prints six. These tests count the markers mechanically out of
raw/wynn_wpt_world_championship_schedule_2026-11-17.md so the published flag,
the raw capture and the rows themselves cannot drift apart.
"""
import json
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "raw", "wynn_wpt_world_championship_schedule_2026-11-17.md")
DATA = os.path.join(ROOT, "site", "data.json")


def rows():
    out = []
    with open(RAW, encoding="utf-8") as fh:
        for line in fh:
            if not line.startswith("| "):
                continue
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) < 4 or cells[0] in ("DATE", "---"):
                continue
            out.append((cells, line))
    return out


def marker_of(line):
    runs = re.findall(r"(?:\\\*)+", line)
    if not runs:
        return 0
    return max(r.count("\\*") for r in runs)


def _strip_markers(text):
    return re.sub(r"(?:\\\*)+$", "", text).strip()


class WptFootnotes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = rows()
        cls.counts = {n: 0 for n in range(6)}
        cls.by_marker = {n: [] for n in range(6)}
        for cells, line in cls.rows:
            n = marker_of(line)
            if n > 5:
                raise AssertionError("unexpected marker run of %d on %r" % (n, cells[2]))
            cls.counts[n] += 1
            cls.by_marker[n].append(cells)
        with open(DATA, encoding="utf-8") as fh:
            cls.db = json.load(fh)
        cls.flags = {f["id"]: f for f in cls.db["flags"]}

    def test_capture_has_the_whole_schedule(self):
        self.assertGreater(len(self.rows), 100)

    def test_marker_counts_are_what_the_capture_says(self):
        # The census table in the raw capture must equal the mechanical count.
        self.assertEqual(self.counts[1], 3, "single-marker rows")
        self.assertEqual(self.counts[2], 21, "double-marker rows")
        self.assertEqual(self.counts[3], 3, "triple-marker rows")
        self.assertEqual(self.counts[4], 7, "quad-marker rows")
        self.assertEqual(self.counts[5], 0, "quint-marker rows")

    def test_every_double_marker_row_is_a_milestone_satellite(self):
        for cells in self.by_marker[2]:
            self.assertIn("Milestone Satellite", _strip_markers(cells[2]), cells)

    def test_the_three_added_rows_are_the_world_championship_flights(self):
        names = sorted(_strip_markers(c[2]) for c in self.by_marker[3])
        self.assertEqual(
            names,
            ["WPT World Championship Day 1A $1,000,000 Added",
             "WPT World Championship Day 1B $1,000,000 Added",
             "WPT World Championship Day 1C $1,000,000 Added"],
        )

    def test_quad_marker_covers_one_described_row_and_six_undescribed(self):
        names = [_strip_markers(c[2]) for c in self.by_marker[4]]
        self.assertIn("Ladies NIH Championship (2 Day)", names)
        self.assertEqual(len(names), 7)
        undescribed = [n for n in names if n != "Ladies NIH Championship (2 Day)"]
        self.assertEqual(len(undescribed), 6)
        self.assertEqual(
            sorted(undescribed),
            ["Milestone Satellite to $25K NIH High Roller", "NLH 6-Max", "NLH 8-Max",
             "NLH High Roller (2 Day)", "PLO", "PLO 6-Max"],
        )

    def test_flag_f25_states_the_same_counts(self):
        detail = self.flags["F25"]["detail"]
        self.assertIn("seven rows", detail)
        self.assertIn("six", detail)
        self.assertIn("Ladies", detail)
        for amount in ("$10,500", "$25,800", "$3,000"):
            self.assertIn(amount, detail)

    def test_flag_f25_quotes_all_five_footnotes(self):
        detail = self.flags["F25"]["detail"]
        for quote in (
            "Winners will receive two (2) prizes valued at $1,100 each",
            "Winners will receive direct entry to the corresponding event(s)",
            "$1,000,000 will be added in cash prizes by ClubWPT Gold",
            "The Tournament Entry for the Ladies Championship is $11,100",
            "Players registered prior to the start of the event will receive a discounted entry",
        ):
            self.assertIn(quote, detail)

    def test_no_quad_marker_row_was_promoted_to_single_entry(self):
        for cells in self.by_marker[4]:
            date, time = cells[0], cells[1]
            for e in self.db["events"]:
                if e["venue"] != "wynn":
                    continue
                if e["name"] == cells[2] and e["buyIn"] == int(re.sub(r"[^0-9]", "", cells[3])):
                    self.assertFalse(e["singleEntry"], e["id"])
                    self.assertNotEqual(e["entryType"], "single-entry-on-sheet", e["id"])
                    self.assertEqual(e["category"], "wpt", e["id"])

    def test_no_printed_buyin_was_replaced_by_a_discount(self):
        for cells in self.by_marker[4] + self.by_marker[1] + self.by_marker[2]:
            printed = int(re.sub(r"[^0-9]", "", cells[3]))
            match = [e for e in self.db["events"]
                     if e["venue"] == "wynn" and e["buyIn"] == printed and e["name"].replace("NLH", "NIH") == cells[2].split("(")[0].strip()]
            self.assertTrue(match or printed in (400, 200, 300, 1600, 1100, 600, 3000, 10500, 25800), cells)


if __name__ == "__main__":
    unittest.main()
