"""Detect drift between the dated executive brief and the canonical trip data."""
import json
import unittest
from decimal import Decimal
from html.parser import HTMLParser
from pathlib import Path

SITE = Path(__file__).resolve().parents[1] / 'site'


class ReviewedRows(HTMLParser):
    def __init__(self):
        super().__init__()
        self.rows = []
        self.body = False
        self.cell = False

    def handle_starttag(self, tag, attrs):
        if tag == 'tbody':
            self.body = True
        if self.body and tag == 'tr':
            self.rows.append(([], []))
        if self.body and tag in ('td', 'th'):
            self.cell = True
            self.rows[-1][0].append('')
        if self.cell and tag == 'a':
            self.rows[-1][1].append(dict(attrs)['href'])

    def handle_data(self, data):
        if self.cell:
            self.rows[-1][0][-1] += data

    def handle_endtag(self, tag):
        if tag == 'tbody':
            self.body = False
        if tag in ('td', 'th'):
            self.cell = False


class DecisionSummary(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((SITE / 'data.json').read_text())
        self.page = (SITE / 'index.html').read_text()

    def test_reviewed_sheet_rows_match_trip(self):
        parser = ReviewedRows()
        parser.feed(self.page)
        events = {e['id']: e for e in self.data['events']}
        plan = self.data['dayPlan']
        self.assertEqual(len(plan), len(parser.rows))
        for (cells, links), day in zip(parser.rows, plan):
            event = events[day['primary']]
            with self.subTest(event=event['id']):
                self.assertEqual(cells[0], 'Nov ' + day['date'][-2:])
                self.assertEqual(cells[2], event['time'])
                self.assertEqual(cells[3].lstrip('~'), event['lateRegEnd'])
                self.assertEqual(cells[4], f"${event['buyIn']}")
                self.assertEqual(cells[5].split()[0], f"${event['guarantee']:,}")
                self.assertEqual('incl. bounties' in cells[5], event['kind'] == 'bounty')
                self.assertEqual(cells[6], f"{event['chips']:,}")
                self.assertEqual(links, [event['sheetUrl']])
                self.assertIn('2026-11-19', cells[7])

    def test_historical_cost_does_not_use_rounded_averages(self):
        quote = self.data['tripCostModel']['liveQuote']
        hotel = Decimal(str(quote['checkoutTotal']))
        fees = sum(day['primaryBuyIn'] for day in self.data['dayPlan'])
        self.assertIn(f'${fees:,} in entry fees', self.page)
        self.assertIn(f'${hotel + fees:,.2f}', self.page)
        self.assertIn(f"${hotel / quote['nights']:,.2f} per night", self.page)
