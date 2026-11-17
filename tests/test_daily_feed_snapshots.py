"""Regression test for the morning daily-feed snapshot naming.

One Strip room can publish more than one schedule page. The Venetian feed, for
example, reads the DSE IV schedule page, the DSE NYE schedule page and the
poker-room page. Every page must keep its own dated snapshot, so a morning run
can be compared with the previous morning per page.

Before the fix, every page of a room wrote to the same
``<room>-<date>.txt`` filename, so the last page overwrote the earlier ones and
only the last page's text survived on disk. This test runs the feed with a fake
fetcher and asserts that each page produces a distinct snapshot file and that
the index records every one of them.
"""
from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/daily_feed.py"
spec = importlib.util.spec_from_file_location("daily_feed", SCRIPT)
feed = importlib.util.module_from_spec(spec)
assert spec.loader
spec.loader.exec_module(feed)


class DailyFeedSnapshotTests(unittest.TestCase):
    def _run(self, rooms: list[dict], bodies: dict[str, bytes]) -> dict:
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            data_path = root / "data.json"
            data_path.write_text(json.dumps({"feed": rooms}), encoding="utf-8")
            feed_dir = root / "feed"

            # Point the module at the temporary data and feed directories, and
            # replace the network fetch with a fake that returns a distinct body
            # for each URL so the snapshots must differ.
            original_data, original_feed, original_fetch = feed.DATA, feed.FEED, feed.fetch
            feed.DATA = data_path
            feed.FEED = feed_dir

            def fake_fetch(url: str):
                return 200, "text/html;charset=utf-8", bodies[url]

            feed.fetch = fake_fetch
            try:
                rc = feed.main()
            finally:
                feed.DATA, feed.FEED, feed.fetch = original_data, original_feed, original_fetch
            self.assertEqual(rc, 0)
            index = json.loads((feed_dir / "index.json").read_text(encoding="utf-8"))
            return index

    def test_each_page_of_a_room_gets_its_own_snapshot(self) -> None:
        rooms = [{
            "id": "venetian",
            "name": "The Venetian poker room",
            "schedule": "https://example.test/dse-nov.html",
            "extra": [
                "https://example.test/dse-dec.html",
                "https://example.test/poker.html",
            ],
        }]
        bodies = {
            "https://example.test/dse-nov.html": b"<html>DSE IV schedule page one</html>",
            "https://example.test/dse-dec.html": b"<html>DSE NYE schedule page two</html>",
            "https://example.test/poker.html": b"<html>poker room page three</html>",
        }
        index = self._run(rooms, bodies)
        entry = index["rooms"][0]
        self.assertEqual(len(entry["pages"]), 3)

        snapshots = [p["snapshot"] for p in entry["pages"]]
        self.assertEqual(len(set(snapshots)), 3, "each page must write a distinct snapshot file")

        # Every snapshot name is per-room, per-date and per-page (a digest slug
        # follows the date), never a single shared <room>-<date>.txt name.
        for snapshot in snapshots:
            self.assertTrue(snapshot.startswith("feed/venetian-"))
            self.assertRegex(snapshot, r"^feed/venetian-\d{4}-\d{2}-\d{2}-[0-9a-f]{8}\.txt$")

    def test_snapshots_do_not_overwrite_earlier_pages(self) -> None:
        rooms = [{
            "id": "wynn",
            "name": "Wynn poker room",
            "schedule": "https://example.test/wynn.html",
            "extra": ["https://example.test/wynn-daily.html"],
        }]
        bodies = {
            "https://example.test/wynn.html": b"<html>first page</html>",
            "https://example.test/wynn-daily.html": b"<html>second page</html>",
        }
        index = self._run(rooms, bodies)
        entry = index["rooms"][0]
        snapshots = [p["snapshot"] for p in entry["pages"]]
        self.assertEqual(len(set(snapshots)), 2)
        # The two snapshot filenames must differ only in the per-page digest slug,
        # not collapse onto one shared <room>-<date>.txt name.
        self.assertNotEqual(snapshots[0], snapshots[1])
        self.assertNotIn("wynn-2026-11-17.txt", snapshots)


if __name__ == "__main__":
    unittest.main()
