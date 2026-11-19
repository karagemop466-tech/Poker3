#!/usr/bin/env python3
"""Regression test for session arena/4475a074-poker3's independent 2026-11-19 fresh read.

`raw/dse_schedule_live_2026-11-19_4475a074.md` is this session's own transcription of the
official DSE IV schedule page, read live on 2026-11-19 in all four chunks.
`scripts/verify_fresh_4475a074.py` canonicalises it and runs the same field-by-field
comparison as the primary capture. This test fails if the published catalog stops matching
this independent read, and also asserts the two independent reads agree with each other.
"""
from __future__ import annotations

import pathlib
import subprocess
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import verify_dse_live_2026_11_19 as v  # noqa: E402
import verify_fresh_4475a074 as fresh  # noqa: E402

FRESH_CANONICAL = ROOT / "raw" / "dse_schedule_live_2026-11-19_4475a074_canonical.md"


class FreshCaptureMatchesCatalog(unittest.TestCase):
    def test_fresh_capture_parses_to_the_full_series(self):
        # Regenerate the canonical file deterministically and confirm it has 94 rows.
        self.assertEqual(0, fresh.main())
        rows = v.read_capture(FRESH_CANONICAL)
        self.assertEqual(94, len(rows), "the fresh 2026-11-19 read printed 94 rows")
        self.assertEqual("2026-11-16", rows[0]["date"])
        self.assertEqual("2026-12-23", rows[-1]["date"])

    def test_fresh_read_agrees_with_primary_capture(self):
        """Two independent reads of the same page must agree field for field."""
        primary = v.read_capture()
        mine = v.read_capture(FRESH_CANONICAL)
        self.assertEqual(len(primary), len(mine))
        for a, b in zip(primary, mine):
            self.assertEqual(a["date"], b["date"])
            self.assertEqual(a["time"], b["time"])
            self.assertEqual(a["number"], b["number"])
            self.assertEqual(v.norm(a["name"]), v.norm(b["name"]))
            self.assertEqual(a["sheet"], b["sheet"])


if __name__ == "__main__":
    unittest.main()
