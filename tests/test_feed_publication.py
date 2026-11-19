"""Validate the published morning feed and all its generated links."""
import json
from pathlib import Path
import re
import unittest
from urllib.parse import urlsplit

SITE = Path(__file__).resolve().parents[1] / 'site'


class FeedPublication(unittest.TestCase):
    def test_feed_record_points_to_safe_existing_snapshots(self):
        record = json.loads((SITE / 'feed/index.json').read_text(encoding='utf-8'))
        self.assertTrue(record['generated'])
        self.assertTrue(record['rooms'])
        for room in record['rooms']:
            self.assertTrue(room['fetched'])
            self.assertTrue(room['pages'])
            for page in room['pages']:
                with self.subTest(source=page['url']):
                    url = urlsplit(page['url'])
                    self.assertEqual(url.scheme, 'https')
                    self.assertTrue(url.hostname)
                    self.assertTrue(page['status'])
                    if 'snapshot' in page:
                        self.assertTrue(re.fullmatch(r'HTTP 2\d\d', page['status']))
                        self.assertRegex(page['snapshot'], r'^feed/[a-z0-9-]+\.txt$')
                        self.assertTrue((SITE / page['snapshot']).is_file())


if __name__ == '__main__':
    unittest.main()
