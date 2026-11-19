"""Check the 2026-11-19 live re-read of the Venetian DSE IV trip-window rows (session arena/d2f205b3-poker3).

The record research/reread_2026-11-19_arena-d2f205b3.json holds rows read from the official
Venetian schedule page. Each must match a published Venetian event on date, time and buy-in.
"""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class TripWindowRereadTests(unittest.TestCase):
    def setUp(self):
        self.record = json.loads((ROOT / 'research/reread_2026-11-19_arena-d2f205b3.json').read_text(encoding='utf-8'))
        self.data = json.loads((ROOT / 'site/data.json').read_text(encoding='utf-8'))

    def test_every_live_row_matches_published_event(self):
        published = [(e['date'], e['time'], e['buyIn']) for e in self.data['events'] if e.get('venue') == 'venetian']
        rows = self.record['tripWindowRows']
        self.assertEqual(len(rows), 19)
        for r in rows:
            key = (r['date'], r['time'], r['buyIn'])
            self.assertIn(key, published, f'live row not in published data: {key}')

    def test_no_eight_am_row_on_official_page(self):
        self.assertEqual(self.record['earliestStartsOnPage']['eightAmRowsFound'], 0)

    def test_booking_engine_read_does_not_refresh_quote(self):
        self.assertFalse(self.record['bookingEngineRead']['quoteRefreshed'])


if __name__ == '__main__':
    unittest.main()
