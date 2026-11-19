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
        # One list per row, holding the sheet each cell's re-check date is read for. The date itself is
        # rendered from site/checks.json by app.js, so it is deliberately not asserted here.
        self.rechecks = []
        self.body = False
        self.cell = False

    def handle_starttag(self, tag, attrs):
        if tag == 'tbody':
            self.body = True
        if self.body and tag == 'tr':
            self.rows.append(([], []))
            self.rechecks.append([])
        if self.body and tag in ('td', 'th'):
            self.cell = True
            self.rows[-1][0].append('')
        if self.cell and tag == 'a':
            self.rows[-1][1].append(dict(attrs)['href'])
        if self.cell and tag == 'small':
            attributes = dict(attrs)
            if 'data-sheet-recheck' in attributes:
                self.rechecks[-1].append(attributes['data-sheet-recheck'])

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
        for i, ((cells, links), day) in enumerate(zip(parser.rows, plan)):
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
                # The date in this cell is rendered from site/checks.json at page load (see
                # renderSheetRechecks in site/assets/app.js), so the static page must name the sheet it
                # will read the re-check date for, and must not hardcode a date: a typed date is what
                # let the page claim 2026-11-19 above rows recorded at 2026-11-17 in the first place.
                self.assertIn('sheet re-check date: see the source log', cells[7],
                              'the cell must carry its no-JS fallback text')
                sheet = event['sheetUrl'].rsplit('/', 1)[-1]
                self.assertEqual([sheet], parser.rechecks[i],
                                  f"the cell must read the re-check date for {sheet}, the sheet this day's event quotes")

    def test_historical_cost_does_not_use_rounded_averages(self):
        quote = self.data['tripCostModel']['liveQuote']
        hotel = Decimal(str(quote['checkoutTotal']))
        fees = sum(day['primaryBuyIn'] for day in self.data['dayPlan'])
        self.assertIn(f'${fees:,} in entry fees', self.page)
        self.assertIn(f'${hotel + fees:,.2f}', self.page)
        self.assertIn(f"${hotel / quote['nights']:,.2f} per night", self.page)
