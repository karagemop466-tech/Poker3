"""Keep the published morning feed tied to official evidence and actual requests."""
import contextlib
import io
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import urllib.error

from scripts import daily_feed
from scripts.verify_site import official

ROOT = Path(__file__).resolve().parents[1]


class FeedStatusTests(unittest.TestCase):
    def test_current_room_targets_and_schedule_documents(self):
        data = json.loads(daily_feed.DATA.read_text())
        sources = {s.get('id'): s['url'] for s in data['sources']}
        by_room = {row['id']: row['urls'] for row in daily_feed.room_targets(data)}
        self.assertEqual(set(by_room), {row['id'] for row in data['stripRooms'] if row['inFeed']})
        for room, documents in daily_feed.ROOM_DOCUMENTS.items():
            for doc in documents:
                self.assertIn(sources[doc], by_room[room])
        self.assertIn('https://www.caesars.com/caesars-palace/casino', by_room['caesars'])
        self.assertNotIn(sources['caesars-flyer'], by_room['horseshoe'])
        for urls in by_room.values():
            self.assertEqual(len(urls), len(set(urls)))
            self.assertTrue(urls and all(official(url) for url in urls))

    def test_http_outcomes_remain_distinct_and_do_not_overwrite_text(self):
        responses = {
            'html': (200, 'text/html', b'<p>11:10 AM</p>'),
            'pdf': (200, 'application/octet-stream', b'%PDF-fake bytes'),
            'redirect': (302, 'text/html', b'<p>Please enable cookies</p>'),
            'empty': (200, 'text/html', b'<html><script>test</script></html>'),
            'blocked': urllib.error.HTTPError('blocked', 403, 'Forbidden', {}, None),
            'timeout': TimeoutError('timeout'),
        }

        def fetch(key):
            reply = responses[key]
            if isinstance(reply, Exception):
                raise reply
            return reply

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data_path = root / 'data.json'
            data_path.write_text(json.dumps({'feed': [
                {'id': 'venue', 'name': 'Venue', 'schedule': 'html', 'extra': list(responses)[1:]},
            ]}))
            with patch.multiple(daily_feed, DATA=data_path, FEED=root / 'feed', fetch=fetch):
                with contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(daily_feed.main(), 0)
            index = json.loads((root / 'feed/index.json').read_text())
            pages = {row['url']: row for row in index['rooms'][0]['pages']}
            self.assertEqual([page['outcome'] for page in pages.values()], [
                'text', 'pdf-fingerprint', 'unavailable', 'no-text', 'unavailable', 'unavailable',
            ])
            self.assertEqual((root / pages['html']['snapshot']).read_text(), '11:10 AM')
            self.assertRegex(pages['pdf']['hash'], r'^[a-f0-9]{64}$')
            self.assertNotIn('hash', pages['redirect'])
            self.assertEqual(len(list((root / 'feed').glob('*.txt'))), 1)

    @unittest.skipUnless(shutil.which('node'), 'Node is required for the feed render test')
    def test_published_feed_renders_and_missing_record_stays_distinct(self):
        subprocess.run(['node', 'tests/feed_status_render.js'], cwd=ROOT, check=True)
