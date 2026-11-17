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
        old = {"hash": "abc", "status": "HTTP 200", "checked": "2026-11-16"}
        result = compare_check(old, "HTTP 200", "abc")
        self.assertFalse(result["baseline"])
        self.assertFalse(result["changed"])
        self.assertFalse(result["unavailable"])
        self.assertFalse(result["statusChanged"])

    def test_different_body_is_a_change(self):
        old = {"hash": "old", "status": "HTTP 200", "checked": "2026-11-16"}
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
