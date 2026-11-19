"""The scheduled monitor must keep publishing its record, whatever the venues do.

Why this file exists. `checks.yml` is the job that re-reads every official URL behind the dashboard and
commits the result to `site/checks.json` — the "automatic re-check of each official URL on a schedule, and
mark rows whose source changed" requirement, running unattended each morning. On 2026-11-19 it failed:
the URL re-check and the transcription re-check both passed, the regression gate after them failed, and
because the commit step had no `if:`, the record of the change was never committed (CI run
44482186623). The gate failed on `tests/test_index_evidence_labels.py`, which asserted that
`site/checks.json` was dated `2026-11-19` and that no structure PDF had changed — two assertions that
cannot survive a normal day of the job doing its work, because the same job rewrites that file every
morning. A monitor whose test suite forbids change stops reporting change.

These tests pin the three properties that make that failure mode impossible to reintroduce:

1. the record is committed and pushed on `always()`, so a red gate cannot silence it (and the gate still
   runs its checks and still fails the run, so a real regression is not hidden);
2. the record writer never writes `site/data.json`, so a detected change is reported, never auto-applied;
3. no test may assert a fixed calendar date against the regenerated record — the time bomb itself.
"""
from __future__ import annotations

import pathlib
import re
import unittest

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "checks.yml"
MONITOR = ROOT / "scripts" / "check_sources.py"
TESTS = ROOT / "tests"


class RecordPublication(unittest.TestCase):
    def setUp(self):
        self.doc = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))
        self.steps = {s.get("name"): s for s in self.doc["jobs"]["recheck"]["steps"] if s.get("name")}

    def test_the_job_still_carries_both_recorders_before_the_gate(self):
        names = list(self.steps)
        self.assertLess(names.index("Re-check every official URL behind the dashboard"),
                        names.index("Verify the dashboard still passes its own checks"))
        self.assertLess(names.index("Re-check the transcribed series-PDF rows against the published data"),
                        names.index("Record the check results on the main branch"))

    def test_the_record_and_its_push_run_even_when_the_gate_is_red(self):
        for name in ("Record the check results on the main branch",
                     "Push the record to main, tolerating a concurrent merge"):
            with self.subTest(step=name):
                condition = self.steps[name].get("if") or ""
                self.assertIn("always()", condition,
                              f"{name} must carry an always() guard: without it a failing regression gate "
                              "skips the commit and the site never learns that a source changed")
                self.assertIn("cancelled()", condition, "a cancelled run must not push")

    def test_the_gate_still_gates(self):
        """Publication is unconditional; the check is not made to lie about its result."""
        gate = self.steps["Verify the dashboard still passes its own checks"]
        self.assertNotIn("continue-on-error", gate,
                         "the gate must keep failing the run when a real regression appears")
        self.assertIsNone(gate.get("if"), "the gate must run normally on a green path")

    def test_the_gate_runs_the_suite_and_the_verifier(self):
        run = self.steps["Verify the dashboard still passes its own checks"]["run"]
        for needle in ("python3 -m unittest discover -s tests", "scripts/verify_site.py",
                       "node --check site/assets/app.js"):
            self.assertIn(needle, run)

    def test_the_record_is_not_committed_when_it_cannot_be_parsed(self):
        """always() must not become 'commit whatever half-written file the job left behind'."""
        run = self.steps["Record the check results on the main branch"]["run"]
        self.assertIn("not valid JSON", run)
        self.assertIn("was not written this run", run)
        self.assertLess(run.index("json.loads"), run.index("git commit"),
                        "the record must be parsed before it is committed")


class MonitorNeverEditsValues(unittest.TestCase):
    def test_the_recorder_writes_only_its_own_record(self):
        src = MONITOR.read_text(encoding="utf-8")
        self.assertIn("CHECKS.write_text", src, "the monitor must still publish its record")
        for forbidden in ("DATA.write_text", 'SITE / "data.json").write_text', "data.json\", \"w\""):
            self.assertNotIn(forbidden, src,
                             f"a changed page is a review signal; the monitor must not write values ({forbidden})")

    def test_a_changed_row_states_what_it_compared(self):
        src = MONITOR.read_text(encoding="utf-8")
        self.assertIn('"hashBasis"', src)
        self.assertIn('"previousHash"', src)
        self.assertIn('"wordingChanged"', src,
                      "a byte change and a wording change are different claims and must not collapse")


class RenderGuardIsWired(unittest.TestCase):
    """The live date cell is only protected if its render check actually runs.

    A guard that no workflow invokes is a file in a directory: it passes forever and catches nothing.
    """

    def test_both_gates_run_the_sheet_recheck_render_check(self):
        for name in ("pages.yml", "verify.yml"):
            with self.subTest(workflow=name):
                text = (ROOT / ".github" / "workflows" / name).read_text(encoding="utf-8")
                self.assertIn("node tests/sheet_recheck_render.js", text,
                              f"{name} must run the render check, or a regression in the date cell is published anyway")
        smoke = (ROOT / "tests" / "canonical_smoke.py").read_text(encoding="utf-8")
        self.assertIn('"sheet_recheck_render.js"', smoke, "the local smoke runner must run it too")

    def test_the_render_check_uses_a_synthetic_record(self):
        """It may not read site/checks.json: that file is rewritten every morning by design."""
        src = (ROOT / "tests" / "sheet_recheck_render.js").read_text(encoding="utf-8")
        self.assertNotIn("'site', 'checks.json'", src.replace('"', "'"))
        self.assertIn("synthetic fixture", src.lower())


class NoTimeBombsInTheCheckPath(unittest.TestCase):
    """A test that names a fixed date, for a file the job regenerates, fails the job on a later day.

    Only the two regenerated records are covered — `site/checks.json` (written by this job every
    morning) and `site/feed/index.json` (written by the same step). Dates baked into `site/data.json`
    are committed evidence and are legitimately asserted; they change only when a session changes them.
    """

    REGENERATED_READ = re.compile(r'(generatedAt|\["checked"\]|\[.checked.\])')
    LITERAL_DAY = re.compile(r'(startswith|==)\s*\(?\s*"20\d\d-\d\d-\d\d"')
    CHECKS_CONTEXT = re.compile(r"checks|CHECKS|feed|FEED")

    def test_no_test_asserts_a_literal_date_against_a_regenerated_record(self):
        offenders = []
        for path in sorted(TESTS.glob("test_*.py")):
            text = path.read_text(encoding="utf-8")
            if not self.CHECKS_CONTEXT.search(text):
                continue
            for lineno, line in enumerate(text.splitlines(), 1):
                # Only a real assertion counts. Prose that quotes the removed assertion — including the
                # explanation above it, which has to name the date it removed — must not trip this.
                if "self.assert" not in line:
                    continue
                if "checks" in line.lower() and self.REGENERATED_READ.search(line) and self.LITERAL_DAY.search(line):
                    offenders.append(f"{path.name}:{lineno}: {line.strip()}")
        self.assertEqual([], offenders,
                         "assert a relation (ordering, parseability, coverage) instead of a date: the job "
                         "rewrites these files every morning, so a literal date is a self-inflicted outage")

    def test_the_guard_itself_still_catches_the_pattern_that_broke_the_job(self):
        """The removed assertion, rebuilt from parts so this file does not offend its own scan."""
        day = "2026-11" + "-19"
        sample = 'self.assertTrue(checks["generatedAt"].startswith("%s"))' % day
        line_found = bool(self.REGENERATED_READ.search(sample) and self.LITERAL_DAY.search(sample))
        self.assertTrue(line_found, "the scanner regressed; the job is exposed again")


if __name__ == "__main__":
    unittest.main()
