"""Publication must depend on local validation, not a racing workflow run."""
from pathlib import Path
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[1]


class PagesGateTests(unittest.TestCase):
    def setUp(self):
        self.workflow = yaml.safe_load(
            (ROOT / '.github/workflows/pages.yml').read_text()
        )
        self.steps = self.workflow['jobs']['build']['steps']

    def test_validators_run_before_artifact_upload(self):
        upload = next(i for i, step in enumerate(self.steps)
                      if step.get('uses', '').startswith('actions/upload-pages-artifact@'))
        required = (
            'python3 scripts/verify_site.py',
            'python3 scripts/audit_951cd431.py',
            'python3 scripts/verify_live_official.py',
            'python3 scripts/audit_data.py',
            'python3 scripts/verify_entry_labels.py',
            "python3 -m unittest discover -s tests -p 'test_*.py' -v",
            'python3 tests/canonical_smoke.py',
            'node tests/canonical_render.js',
            'node --check site/assets/search.js',
        )
        for command in required:
            with self.subTest(command=command):
                matches = [(i, step) for i, step in enumerate(self.steps)
                           if command in step.get('run', '').splitlines()]
                self.assertEqual(len(matches), 1)
                index, step = matches[0]
                self.assertLess(index, upload)
                self.assertNotIn('if', step)
                self.assertFalse(step.get('continue-on-error', False))
                self.assertNotIn('continue-on-error', self.workflow['jobs']['build'])

    def test_yaml_dependency_installed_before_tests(self):
        install = next(i for i, step in enumerate(self.steps)
                       if "pip install 'PyYAML==6.0.3'" in step.get('run', ''))
        tests = next(i for i, step in enumerate(self.steps)
                     if 'unittest discover' in step.get('run', ''))
        self.assertLess(install, tests)

    def test_deploy_requires_successful_build(self):
        deploy = self.workflow['jobs']['deploy']
        self.assertEqual(deploy['needs'], 'build')
        self.assertNotIn('if', deploy)
        self.assertFalse(deploy.get('continue-on-error', False))


if __name__ == '__main__':
    unittest.main()
