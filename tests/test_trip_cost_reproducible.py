#!/usr/bin/env python3
"""Pin the dated trip quote and the reproducibility rule (CI gate on main).

Commit 5a9269d added a `perNight` block to site/data.json by hand and changed no
builder code. Every other check passed, but `verify.yml`'s last step — rebuild the
data file and `git diff --exit-code` — failed on main, because a rebuild removes
anything the builder does not emit.

Two things are pinned here:

1. the arithmetic of the dated Venetian quote: the per-night true costs are
   (rate + $55) x 1.1338 and must sum to the printed checkout total, and the
   hand-added per-night detail must be emitted by the builder, not pasted in;
2. every key of `tripCostModel` is builder output. The test re-runs the builder and
   compares the whole file, which is the same gate CI runs, so a manual edit can no
   longer reach main unrebuildable.
"""
from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "site/data.json"


class TripCostReproducible(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data = json.loads(DATA.read_text(encoding="utf-8"))
        cls.model = cls.data["tripCostModel"]

    def _per_night(self) -> dict:
        """The per-night detail, from the committed file or from a fresh build.

        The builder emits `perNight` inside `liveQuote`. A committed file that predates
        that change simply does not carry it yet; the arithmetic below is what matters,
        and it is checked against whatever the builder produces either way.
        """
        pn = (self.model.get("liveQuote") or {}).get("perNight") or self.model.get("perNight")
        if pn:
            return pn
        rebuilt = subprocess.run(["python3", str(ROOT / "scripts/data_source.py")],
                                 check=True, capture_output=True, cwd=ROOT)
        self.assertEqual(rebuilt.returncode, 0)
        fresh = json.loads(DATA.read_text(encoding="utf-8"))["tripCostModel"]
        detail = (fresh.get("liveQuote") or {}).get("perNight")
        self.assertIsNotNone(detail, "the builder does not emit the per-night quote detail")
        return detail

    def test_per_night_true_costs_sum_to_the_printed_checkout_total(self) -> None:
        pn = self._per_night()
        self.assertEqual(round(sum(pn["nightlyTrueCostDerived"]), 2), pn["printedTotal"],
                         "per-night derived costs do not sum to the printed total")
        for rate, true_cost in zip(pn["nightlyRates"], pn["nightlyTrueCostDerived"]):
            self.assertAlmostEqual(round((rate + pn["resortFeePerNight"]) * 1.1338, 2), true_cost, places=2)

    def test_live_quote_and_per_night_detail_describe_the_same_read(self) -> None:
        lq, pn = self.model["liveQuote"], self._per_night()
        self.assertEqual(lq["checkoutTotal"], pn["printedTotal"])
        self.assertEqual(lq["nights"], len(pn["nightlyRates"]))
        self.assertEqual(round(sum(pn["nightlyRates"]), 2), lq["roomRatesTotal"])
        self.assertEqual(lq["resortFeeTotal"], round(pn["resortFeePerNight"] * lq["nights"], 2))
        self.assertEqual(lq["taxTotal"], pn["printedTaxes"])

    def test_the_committed_data_file_is_builder_output(self) -> None:
        """The CI gate, run here too so a manual edit fails locally first."""
        before = DATA.read_bytes()
        try:
            subprocess.run(["python3", str(ROOT / "scripts/data_source.py")],
                           check=True, capture_output=True, cwd=ROOT)
            after = DATA.read_bytes()
        finally:
            DATA.write_bytes(before)
        self.assertEqual(before, after,
                         "site/data.json is not reproducible from the builder - a value was pasted in by hand")


if __name__ == "__main__":
    unittest.main()
