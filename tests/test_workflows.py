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
