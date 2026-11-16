#!/usr/bin/env python3
from __future__ import annotations

import sys
import unittest
from email.message import Message
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import monitor_official_sources as monitor  # noqa: E402


class FakeResponse:
    def __init__(self, body: bytes, headers: dict[str, str] | None = None, status: int = 200):
        self._body = body
        self.headers = Message()
        for key, value in (headers or {}).items():
            self.headers[key] = value
        self.status = status

    def read(self, size: int = -1) -> bytes:
        return self._body if size < 0 else self._body[:size]

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def close(self) -> None:
        pass


class MonitorTests(unittest.TestCase):
    def test_html_fingerprint_ignores_script_noise_and_collapses_whitespace(self):
        first = b"<html><title>Schedule</title><main><p>Dec 10   $300</p><script>noise one</script></main></html>"
        second = b"<html><title>Schedule</title><main> <p>Dec 10 $300</p> <script>noise two</script></main></html>"
        self.assertEqual(monitor.normalized_body(first, "text/html; charset=utf-8"), monitor.normalized_body(second, "text/html; charset=utf-8"))
        self.assertNotEqual(monitor.normalized_body(first, "application/pdf"), monitor.normalized_body(second, "application/pdf"))

    def test_refuses_non_official_hosts(self):
        failure = monitor.validate_official_source({"id": "bad", "name": "Bad", "url": "https://example.com/schedule"})
        self.assertIn("Refusing non-approved", failure or "")
        self.assertIsNone(monitor.validate_official_source({"id": "ven", "name": "Venetian", "url": "https://www.venetianlasvegas.com/schedule"}))

    def test_redirects_cannot_leave_official_host_allowlist(self):
        handler = monitor.OfficialRedirectHandler()
        request = monitor.Request("https://www.venetianlasvegas.com/schedule")
        with self.assertRaises(HTTPError):
            handler.redirect_request(request, FakeResponse(b""), 302, "Found", Message(), "https://example.com/redirect")

    @patch("monitor_official_sources.open_official")
    def test_fetch_one_stores_content_hash_and_validators(self, open_official):
        open_official.return_value = FakeResponse(b"<html><main>Official schedule</main></html>", {"Content-Type": "text/html; charset=utf-8", "ETag": '"abc"', "Last-Modified": "Mon, 16 Nov 2026 00:00:00 GMT"})
        source = {"id": "ven", "name": "Venetian", "url": "https://www.venetianlasvegas.com/schedule"}
        result = monitor.fetch_one(source)
        self.assertEqual(result["status"], "fetched")
        self.assertEqual(len(result["sha256"]), 64)
        self.assertEqual(result["etag"], '"abc"')

    @patch("monitor_official_sources.open_official")
    def test_not_modified_preserves_prior_hash(self, open_official):
        open_official.side_effect = HTTPError("https://www.venetianlasvegas.com/schedule", 304, "Not Modified", Message(), None)
        previous = {"sha256": "a" * 64, "etag": '"abc"', "contentType": "text/html"}
        result = monitor.fetch_one({"id": "ven", "name": "Venetian", "url": "https://www.venetianlasvegas.com/schedule"}, previous)
        self.assertEqual(result["status"], "unchanged")
        self.assertEqual(result["sha256"], previous["sha256"])

    def test_first_run_baselines_then_change_is_logged(self):
        source = {"id": "ven", "name": "Venetian", "url": "https://www.venetianlasvegas.com/schedule"}
        baseline = monitor.merge_run_state({}, [{**source, "status": "fetched", "sha256": "a" * 64, "checkedAt": "2026-11-16T00:00:00Z"}], "2026-11-16T00:00:00Z")
        self.assertEqual(baseline["changedCount"], 0)
        self.assertEqual(baseline["sources"]["ven"]["status"], "baseline")
        changed = monitor.merge_run_state(baseline, [{**source, "status": "fetched", "sha256": "b" * 64, "checkedAt": "2026-11-23T00:00:00Z"}], "2026-11-23T00:00:00Z")
        self.assertEqual(changed["changedCount"], 1)
        self.assertEqual(changed["sources"]["ven"]["status"], "changed")
        self.assertEqual(changed["changes"][-1]["previousSha256"], "a" * 64)

    def test_failure_keeps_last_successful_fingerprint(self):
        source = {"id": "ven", "name": "Venetian", "url": "https://www.venetianlasvegas.com/schedule"}
        old = {"schemaVersion": 1, "sources": {"ven": {"id": "ven", "sha256": "a" * 64, "status": "unchanged"}}, "changes": []}
        result = monitor.merge_run_state(old, [{**source, "status": "failure", "error": "HTTP 503"}], "2026-11-23T00:00:00Z")
        self.assertEqual(result["sources"]["ven"]["sha256"], "a" * 64)
        self.assertEqual(result["sources"]["ven"]["status"], "failure")
        self.assertEqual(result["failureCount"], 1)


if __name__ == "__main__":
    unittest.main()
