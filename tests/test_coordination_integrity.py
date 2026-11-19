"""Keep the shared task board free of accidentally published conflict markers."""
from pathlib import Path
import unittest


class CoordinationIntegrityTests(unittest.TestCase):
    def test_no_merge_conflict_markers(self):
        board = Path(__file__).resolve().parents[1] / 'COORDINATION.md'
        markers = [(i, line) for i, line in enumerate(board.read_text(encoding='utf-8').splitlines(), 1)
                   if line.startswith(('<<<<<<< ', '=======', '>>>>>>> '))]
        self.assertEqual(markers, [], f'unresolved merge markers: {markers}')
