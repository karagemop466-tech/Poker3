"""Offline regressions: a real compressed PDF text stream must affect monitoring.

Synthetic PDFs are test fixtures, never evidence for a tournament value.
"""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zlib

from scripts import check_sources as monitor


def pdf_with_fee(fee):
    stream = zlib.compress(f"BT /F1 12 Tf (Buy-in ${fee}) Tj ET".encode())
    return (b"%PDF-1.4\n1 0 obj\n<< /Filter /FlateDecode /Length "
            + str(len(stream)).encode() + b" >>\nstream\n" + stream
            + b"\nendstream\nendobj\n%%EOF\n")


class PdfMonitorTests(unittest.TestCase):
    def test_compressed_rule_change_moves_hash_even_with_equal_length(self):
        first, second = pdf_with_fee(300), pdf_with_fee(400)
        self.assertEqual(len(first), len(second))
        self.assertNotEqual(monitor.content_hash(first, "application/pdf"),
                            monitor.content_hash(second, "application/pdf"))

    def test_pdf_signature_overrides_generic_mime(self):
        body = pdf_with_fee(300)
        digest = hashlib.sha256(body).hexdigest()
        for mime in ("application/pdf", "APPLICATION/PDF", "application/octet-stream", ""):
            self.assertEqual(monitor.content_hash(body, mime), digest)
            self.assertEqual(monitor.comparison_basis(body, mime), monitor.PDF_HASH_BASIS)
            self.assertEqual(monitor.visible_text(body, mime), "")

    def test_migration_reuses_valid_legacy_raw_baseline(self):
        old = {"hash": "raw-before", "textHash": "flawed-streamless-digest",
               "hashBasis": monitor.HASH_BASIS, "status": "HTTP 200",
               "checked": "2026-11-18"}
        for current, expected in (("raw-before", False), ("raw-after", True)):
            result = monitor.compare_check(old, "HTTP 200", current, monitor.PDF_HASH_BASIS)
            self.assertEqual(result["changed"], expected)
            self.assertFalse(result["wordingChanged"], "byte changes are not verified wording changes")
            self.assertFalse(result["baseline"])
            self.assertFalse(result["basisReset"])
            self.assertEqual(result["previousHash"], "raw-before")
            self.assertIsNone(result["previousTextHash"])

    def test_pdf_without_history_records_baseline_not_change(self):
        result = monitor.compare_check(None, "HTTP 200", "raw", monitor.PDF_HASH_BASIS)
        self.assertTrue(result["baseline"])
        self.assertFalse(result["changed"])

    def test_unavailable_pdf_is_not_changed(self):
        result = monitor.compare_check({"hash": "raw"}, "HTTP 403", None, monitor.PDF_HASH_BASIS)
        self.assertTrue(result["unavailable"])
        self.assertFalse(result["changed"])

    def test_metadata_change_is_conservatively_flagged(self):
        first = pdf_with_fee(300)
        self.assertNotEqual(monitor.content_hash(first, "application/pdf"),
                            monitor.content_hash(first + b"% metadata update", "application/pdf"))

    def test_recorder_publishes_pdf_change_and_keeps_html_noise_separate(self):
        url = "https://official.example/structure.pdf"
        html_url = "https://official.example/schedule"
        old_pdf, new_pdf = pdf_with_fee(300), pdf_with_fee(400)
        old_html = b"<script>nonce=1</script><p>Schedule</p>"
        new_html = b"<script>nonce=2</script><p>Schedule</p>"
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            data, checks = root / "data.json", root / "checks.json"
            data.write_text(json.dumps({"sources": [
                {"name": "Official PDF", "url": url},
                {"name": "Official HTML", "url": html_url},
            ]}))
            checks.write_text(json.dumps({"transcription": {"status": "checked"}, "urls": [
                {"url": url, "hash": hashlib.sha256(old_pdf).hexdigest(),
                 "textHash": "legacy", "hashBasis": monitor.HASH_BASIS, "status": "HTTP 200"},
                {"url": html_url, "hash": hashlib.sha256(old_html).hexdigest(),
                 "textHash": monitor.content_hash(old_html, "text/html"),
                 "hashBasis": monitor.HASH_BASIS, "status": "HTTP 200"},
            ]}))
            def fake_fetch(target):
                return (200, "application/pdf", new_pdf) if target == url else (200, "text/html", new_html)
            with patch.object(monitor, "DATA", data), patch.object(monitor, "CHECKS", checks), \
                    patch.object(monitor, "fetch", fake_fetch), patch("sys.argv", ["check_sources.py"]):
                self.assertEqual(monitor.main(), 0)
            record = json.loads(checks.read_text())
            pdf, html = record["urls"]
            self.assertTrue(pdf["changed"])
            self.assertFalse(pdf["wordingChanged"])
            self.assertFalse(pdf["rawOnly"])
            self.assertEqual(pdf["comparisonKind"], "pdf-bytes")
            self.assertNotIn("textChars", pdf, "the monitor did not extract PDF text")
            self.assertFalse(html["changed"])
            self.assertTrue(html["rawOnly"])
            self.assertEqual(record["changed"], [url])
            self.assertEqual(record["summary"]["changed"], 1)
            self.assertEqual(record["transcription"]["status"], "checked")
            self.assertIn("metadata-only", record["note"])


if __name__ == "__main__":
    unittest.main()
