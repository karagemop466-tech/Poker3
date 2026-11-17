import unittest

from scripts.check_sources import compare_check, official_targets


class CompareCheckTests(unittest.TestCase):
    def test_targets_include_each_rule_and_hotel_component_source(self):
        data = {
            "events": [{"name": "Test Event", "rules": {"fee": {"source": "https://venue.test/fee"}}}],
            "hotels": [{"name": "Test Hotel", "parkingSource": "https://hotel.test/parking",
                        "quote": {"source": "https://hotel.test/quote"}}],
            "rateLog": [{"hotel": "Test Hotel", "source": "https://hotel.test/rate"}],
            "routes": [{"hotel": "Test Hotel", "venue": "Test Room", "source": "https://venue.test/address"}],
        }
        targets = official_targets(data)
        urls = {target["url"] for target in targets}
        self.assertEqual(urls, {
            "https://venue.test/fee", "https://hotel.test/parking", "https://hotel.test/quote",
            "https://hotel.test/rate", "https://venue.test/address",
        })

    def test_success_without_history_is_a_baseline_not_unchanged(self):
        result = compare_check(None, "HTTP 200", "abc")
        self.assertTrue(result["baseline"])
        self.assertFalse(result["changed"])
        self.assertFalse(result["unavailable"])

    def test_same_body_is_unchanged(self):
        old = {"hash": "rawabc", "textHash": "abc", "status": "HTTP 200", "checked": "2026-11-16"}
        result = compare_check(old, "HTTP 200", "abc")
        self.assertFalse(result["baseline"])
        self.assertFalse(result["changed"])
        self.assertFalse(result["unavailable"])
        self.assertFalse(result["statusChanged"])

    def test_different_body_is_a_change(self):
        old = {"hash": "rawold", "textHash": "old", "status": "HTTP 200", "checked": "2026-11-16"}
        result = compare_check(old, "HTTP 200", "new")
        self.assertTrue(result["changed"])
        self.assertFalse(result["unavailable"])
        self.assertEqual(result["previousHash"], "old")
        self.assertEqual(result["previousChecked"], "2026-11-16")

    def test_http_error_is_unavailable_not_content_changed(self):
        old = {"hash": "old", "status": "HTTP 200", "checked": "2026-11-16"}
        result = compare_check(old, "HTTP 403", None)
        self.assertFalse(result["changed"])
        self.assertTrue(result["unavailable"])
        self.assertTrue(result["statusChanged"])

    def test_unreachable_is_not_reported_as_a_content_change(self):
        old = {"hash": "old", "status": "HTTP 200"}
        result = compare_check(old, "unreachable", None)
        self.assertFalse(result["changed"])
        self.assertTrue(result["unavailable"])


if __name__ == "__main__":
    unittest.main()


class VisibleTextTests(unittest.TestCase):
    """A raw-byte hash of a venue page is noise; the visible text hash is the signal."""

    def test_scripts_styles_and_tags_do_not_reach_the_hash(self):
        from scripts.check_sources import content_hash
        a = content_hash(b"<html><script>var r=1;</script><p>Event 10  $400</p></html>", "text/html")
        b = content_hash(b"<html><script>var r=999;</script><div>Event 10&nbsp; $400</div></html>", "text/html")
        self.assertEqual(a, b, "a rotating script or a tag difference must not look like a content change")

    def test_a_real_editorial_change_moves_the_hash(self):
        from scripts.check_sources import content_hash
        a = content_hash(b"<p>Guarantee: $15,000</p>", "text/html")
        b = content_hash(b"<p>Guarantee: $20,000</p>", "text/html")
        self.assertNotEqual(a, b)

    def test_pdf_bytes_are_compared_on_extracted_text(self):
        from scripts.check_sources import content_hash
        a = content_hash(b"%PDF-1.4\nstream binary-one endstream\nStart Time: 11:10 AM", "application/pdf")
        b = content_hash(b"%PDF-1.4\nstream binary-two endstream\nStart Time: 11:10 AM", "application/pdf")
        self.assertEqual(a, b)

    def test_a_record_without_a_text_hash_seeds_a_new_baseline(self):
        """Rolling this change out must not flag all 79 pages at once."""
        from scripts.check_sources import compare_check
        legacy = {"hash": "rawabc", "status": "HTTP 200", "checked": "2026-11-17"}
        result = compare_check(legacy, "HTTP 200", "brand-new-text-hash")
        self.assertFalse(result["changed"])
        self.assertTrue(result["basisReset"])
        self.assertTrue(result["baseline"])

    def test_compare_check_uses_the_text_hash_it_is_given(self):
        from scripts.check_sources import compare_check
        old = {"hash": "raw-old", "textHash": "text-1", "status": "HTTP 200"}
        self.assertFalse(compare_check(old, "HTTP 200", "text-1")["changed"])
        self.assertTrue(compare_check(old, "HTTP 200", "text-2")["changed"])
