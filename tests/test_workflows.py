#!/usr/bin/env python3
"""Workflow files must parse, and must not contain duplicate YAML keys.

A duplicate key is the failure mode that silently killed the source re-check:
two sessions each added a `push:` trigger to checks.yml, `yaml.safe_load`
happily kept the last one, and GitHub Actions rejected the file outright with
zero jobs scheduled. A permissive parse cannot see it, so this test uses a
loader that refuses duplicate keys.
"""
from __future__ import annotations

import pathlib
import unittest

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
WORKFLOWS = sorted((ROOT / ".github" / "workflows").glob("*.yml"))


class _StrictLoader(yaml.SafeLoader):
    """SafeLoader that raises on a duplicated mapping key."""


def _no_duplicates(loader, node, deep=False):
    keys = [loader.construct_object(key_node, deep=deep) for key_node, _ in node.value]
    duplicates = sorted({str(k) for k in keys if keys.count(k) > 1})
    if duplicates:
        raise yaml.constructor.ConstructorError(
            f"duplicate mapping key(s): {', '.join(duplicates)}")
    return yaml.SafeLoader.construct_mapping(loader, node, deep)


_StrictLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
                              _no_duplicates)


class WorkflowFiles(unittest.TestCase):
    def test_workflow_files_exist(self):
        self.assertTrue(WORKFLOWS, "no workflow files found")

    def test_each_workflow_parses_without_duplicate_keys(self):
        for path in WORKFLOWS:
            with self.subTest(workflow=path.name):
                with path.open() as handle:
                    yaml.load(handle, Loader=_StrictLoader)

    def test_each_workflow_declares_a_trigger(self):
        for path in WORKFLOWS:
            with self.subTest(workflow=path.name):
                with path.open() as handle:
                    data = yaml.load(handle, Loader=_StrictLoader)
                triggers = data[True] if True in data else data.get("on")
                self.assertIn(
                    triggers is not None and bool(triggers), (True,),
                    f"{path.name} declares no trigger")

    def test_the_source_recheck_job_cannot_trigger_itself(self):
        """checks.yml writes site/checks.json and site/feed; they must not trigger it."""
        path = ROOT / ".github" / "workflows" / "checks.yml"
        if not path.exists():
            self.skipTest("checks.yml not present")
        with path.open() as handle:
            data = yaml.load(handle, Loader=_StrictLoader)
        triggers = data[True] if True in data else data.get("on")
        paths = (triggers.get("push") or {}).get("paths") or []
        for forbidden in ("site/checks.json", "site/feed/**", "site/feed"):
            self.assertNotIn(forbidden, paths,
                             f"{forbidden} would make the re-check job trigger itself")


if __name__ == "__main__":
    unittest.main()
