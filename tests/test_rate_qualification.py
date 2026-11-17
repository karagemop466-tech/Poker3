"""Checks the poker-rate qualification arithmetic the day plan depends on.

The Venetian poker-suite rate requires six hours of live cash play OR a buy-in
to a $300 or higher tournament, for each night stayed. A day plan that silently
relies on $200 events to qualify the nightly rate would be wrong, so this test
recomputes, straight from `site/data.json`, which planned nights a single-entry
tournament of $300+ actually covers, and asserts the published statement matches
the arithmetic.

If a future edit adds a $300+ single-entry event on Nov 30 or Dec 1, this test
fails until F56 and the plan note are updated - which is the point.
"""
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / "site" / "data.json").read_text(encoding="utf-8"))

RATE_THRESHOLD = 300  # "$300 or higher tournament", Venetian poker suite rate page


def best_single_entry_buy_in(date):
    """Largest published buy-in among sheet-screened single-entry events on a date."""
    buys = [
        e.get("buyIn")
        for e in DATA["events"]
        if e.get("date") == date and e.get("singleEntry") and isinstance(e.get("buyIn"), (int, float))
    ]
    return max(buys) if buys else None


class PokerRateQualification(unittest.TestCase):
    def test_each_planned_night_states_whether_it_can_be_qualified(self):
        planned = [p for p in DATA["dayPlan"] if p.get("primaryBuyIn")]
        self.assertEqual(len(planned), 8)
        qualifying, unqualifying = [], []
        for day in planned:
            best = best_single_entry_buy_in(day["date"])
            if best is not None and best >= RATE_THRESHOLD:
                qualifying.append(day["date"])
            else:
                unqualifying.append(day["date"])
        # Six of the eight planned days carry a $300+ single-entry event.
        self.assertEqual(len(qualifying), 6, qualifying)
        # Nov 30 and Dec 1 have no $300+ single-entry event published.
        self.assertIn("2026-11-30", unqualifying)
        self.assertIn("2026-12-01", unqualifying)
        # The stay is seven nights, 2026-11-25 to 2026-12-01 inclusive; 2026-12-02
        # is the checkout day and bills no night of its own. Both unqualifiable
        # days inside the stay are nights, so two of seven nights cannot be
        # qualified by a tournament from this plan.
        self.assertEqual(DATA["trip"]["nights"], 7)
        self.assertEqual(DATA["trip"]["end"], "2026-12-02")
        stay_nights = {"2026-11-25", "2026-11-26", "2026-11-27", "2026-11-28",
                       "2026-11-29", "2026-11-30", "2026-12-01"}
        self.assertEqual(len(stay_nights), DATA["trip"]["nights"])
        unqualifying_nights = [d for d in unqualifying if d in stay_nights]
        self.assertEqual(len(unqualifying_nights), 2, unqualifying_nights)
        self.assertEqual(set(unqualifying_nights), {"2026-11-30", "2026-12-01"})

    def test_flag_f44_exists_and_names_the_two_nights(self):
        flags = {f["id"]: f for f in DATA["flags"]}
        self.assertIn("F56", flags)
        detail = flags["F56"]["detail"]
        self.assertIn("2026-11-30", detail)
        self.assertIn("2026-12-01", detail)
        self.assertIn("$300", detail)

    def test_the_answer_does_not_claim_all_nights_are_covered(self):
        q16 = next(q for q in DATA["questions"] if q["id"] == "Q16")
        answer = q16["answer"]
        # It must admit the shortfall rather than assert full coverage.
        self.assertIn("five of the seven nights", answer)
        self.assertNotIn("the plan counts $300+ entries against nights", answer)

    def test_multiflight_rows_never_count_as_the_qualifying_entry(self):
        """A $400 multi-flight row is not a single entry, so it cannot qualify the rate."""
        for date in ("2026-11-30", "2026-12-01"):
            rows = [
                e
                for e in DATA["events"]
                if e.get("date") == date and (e.get("buyIn") or 0) >= RATE_THRESHOLD
            ]
            self.assertTrue(rows, "expected some $300+ rows on " + date)
            for e in rows:
                with self.subTest(row=e["id"]):
                    self.assertFalse(
                        e.get("singleEntry"),
                        "the $300+ rows on these dates are multi-flight, not single entry",
                    )


if __name__ == "__main__":
    unittest.main()
