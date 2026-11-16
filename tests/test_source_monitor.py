import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/check_sources.py"
spec = importlib.util.spec_from_file_location("check_sources", SCRIPT)
monitor = importlib.util.module_from_spec(spec)
assert spec.loader
spec.loader.exec_module(monitor)


class MonitorTests(unittest.TestCase):
    def test_baseline_then_change_then_unchanged(self):
        source = {"id": "official", "kind": "official", "url": "https://official.example/page"}
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            catalog = root / "catalog.json"
            output = root / "monitor.json"
            catalog.write_text(json.dumps({"sources": [source, {
                "id": "third", "kind": "third-party", "url": "https://other.example/"}]}))
            current = {"body": b"version one"}

            def fake_fetch(_url):
                return 200, current["body"]

            first = monitor.run(catalog, output, fake_fetch, "2026-11-16T13:00:00Z", delay=0)
            self.assertEqual(first["checks"]["official"]["result"], "baseline")
            self.assertFalse(first["checks"]["official"]["changed"])
            self.assertNotIn("third", first["checks"])

            current["body"] = b"version two"
            second = monitor.run(catalog, output, fake_fetch, "2026-11-17T13:00:00Z", delay=0)
            self.assertEqual(second["checks"]["official"]["result"], "changed")
            self.assertTrue(second["checks"]["official"]["changed"])

            third = monitor.run(catalog, output, fake_fetch, "2026-11-18T13:00:00Z", delay=0)
            self.assertEqual(third["checks"]["official"]["result"], "unchanged")
            self.assertFalse(third["checks"]["official"]["changed"])

    def test_fetch_failure_does_not_overwrite_last_good_hash(self):
        source = {"id": "official", "url": "https://official.example/page"}
        old = {"official": {"contentHash": "saved-hash"}}

        def fail(_url):
            raise TimeoutError("slow")

        _, result = monitor.check_one(source, old, "2026-11-16T13:00:00Z", fail)
        self.assertEqual(result["result"], "unavailable")
        self.assertIsNone(result["changed"])
        self.assertEqual(result["contentHash"], "saved-hash")
        self.assertIn("TimeoutError", result["error"])


if __name__ == "__main__":
    unittest.main()
