"""Every workflow file must parse, with no duplicate mapping keys.

A duplicate key is not a style problem: GitHub rejects the whole workflow and the run
shows `failure` with zero jobs and no log. That is what happened to `checks.yml` on
`main` (two `push:` blocks under `on:`), which is why the scheduled re-check could never
run (flag F30). Bundled PyYAML silently keeps the last duplicate, so this test uses a
strict loader that refuses one.
"""
import pathlib
import unittest

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
WORKFLOWS = sorted((ROOT / ".github" / "workflows").glob("*.yml"))


class StrictLoader(yaml.SafeLoader):
    """SafeLoader that refuses duplicate keys instead of silently overwriting them."""


def _no_duplicates(loader, node, deep=False):
    seen = set()
    for key_node, _value in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in seen:
            raise ValueError(f"duplicate key {key!r} at line {key_node.start_mark.line + 1}")
        seen.add(key)
    return yaml.SafeLoader.construct_mapping(loader, node, deep)


StrictLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _no_duplicates
)


class WorkflowFiles(unittest.TestCase):
    def test_there_is_at_least_one_workflow(self):
        self.assertTrue(WORKFLOWS)

    def test_every_workflow_parses_with_no_duplicate_keys(self):
        for path in WORKFLOWS:
            with self.subTest(workflow=path.name):
                yaml.load(path.read_text(encoding="utf-8"), Loader=StrictLoader)

    def test_every_workflow_declares_a_trigger_and_a_job(self):
        for path in WORKFLOWS:
            with self.subTest(workflow=path.name):
                doc = yaml.load(path.read_text(encoding="utf-8"), Loader=StrictLoader)
                # PyYAML reads the unquoted `on:` key as the boolean True.
                triggers = doc.get(True, doc.get("on"))
                self.assertIsNotNone(triggers, "no on: trigger")
                self.assertTrue(doc.get("jobs"), "no jobs")

    def test_every_cron_has_five_fields(self):
        for path in WORKFLOWS:
            doc = yaml.load(path.read_text(encoding="utf-8"), Loader=StrictLoader)
            triggers = doc.get(True, doc.get("on")) or {}
            schedule = triggers.get("schedule") if isinstance(triggers, dict) else None
            if not schedule:
                continue
            for entry in schedule:
                with self.subTest(workflow=path.name, cron=entry.get("cron")):
                    self.assertEqual(len(str(entry["cron"]).split()), 5)

    def test_scheduled_recheck_cannot_trigger_itself(self):
        """The job writes site/checks.json and site/feed/**, so neither may trigger it."""
        doc = yaml.load(
            (ROOT / ".github" / "workflows" / "checks.yml").read_text(encoding="utf-8"),
            Loader=StrictLoader,
        )
        triggers = doc.get(True, doc.get("on"))
        paths = (triggers.get("push") or {}).get("paths") or []
        for written in ("site/checks.json", "site/feed/**", "site/feed"):
            with self.subTest(path=written):
                self.assertNotIn(
                    written, paths,
                    "the job writes this file, so including it would make the job trigger itself")

    def test_scheduled_recheck_can_run_without_a_cron_wait(self):
        doc = yaml.load(
            (ROOT / ".github" / "workflows" / "checks.yml").read_text(encoding="utf-8"),
            Loader=StrictLoader,
        )
        triggers = doc.get(True, doc.get("on"))
        self.assertIn("schedule", triggers)
        self.assertIn("workflow_dispatch", triggers)
        self.assertIn("push", triggers,
                      "a cron-only job cannot be proven to run when the token cannot dispatch it (403)")


if __name__ == "__main__":
    unittest.main()

class ScheduledRecordPublishing(unittest.TestCase):
    """The scheduled job must always publish the record it was run to produce.

    On 2026-11-19 the run for merge commit 5f001742 executed every recorder, then
    failed in the "Verify the dashboard still passes its own checks" step. The two
    steps that commit and push the record were skipped, so a correct observation of
    108 official URLs was discarded and the published site kept the previous run's
    timestamp for another day. `check_sources.py` had already written the record to
    disk; only the workflow threw it away.

    The fix keeps the dashboard check as a failure signal but makes it unable to
    block publication. These tests pin that ordering so it cannot silently revert.
    """

    def setUp(self):
        raw = (ROOT / ".github" / "workflows" / "checks.yml").read_text(encoding="utf-8")
        self.raw = raw
        self.doc = yaml.load(raw, Loader=StrictLoader)
        self.steps = self.doc["jobs"]["recheck"]["steps"]

    def _step(self, fragment):
        for step in self.steps:
            if fragment in (step.get("name") or ""):
                return step
        self.fail(f"checks.yml has no step named like {fragment!r}")

    def test_dashboard_check_cannot_suppress_the_record(self):
        verify = self._step("Verify the dashboard still passes")
        self.assertTrue(
            verify.get("continue-on-error"),
            "the dashboard check must not abort the job before the record is published",
        )
        self.assertEqual(verify.get("id"), "dashboard",
                         "the outcome is re-raised at the end, so the step needs an id")

    def test_record_and_push_steps_run_even_after_a_failed_check(self):
        for name in ("Record the check results on the main branch",
                     "Push the record to main"):
            with self.subTest(step=name):
                self.assertEqual(self._step(name).get("if"), "always()",
                                 f"{name!r} must run even when the check above failed")

    def test_the_job_still_goes_red_when_the_dashboard_is_broken(self):
        gate = self._step("Fail the run if the dashboard check failed")
        self.assertEqual(gate.get("if"), "steps.dashboard.outcome == 'failure'")
        self.assertIn("exit 1", gate["run"])

    def test_publishing_happens_before_the_failure_gate(self):
        names = [s.get("name") or "" for s in self.steps]
        push = names.index("Push the record to main, tolerating a concurrent merge")
        gate = names.index("Fail the run if the dashboard check failed")
        self.assertLess(push, gate, "the record must be pushed before the run is failed")
