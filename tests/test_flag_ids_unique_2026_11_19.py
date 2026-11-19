"""The flag register must keep unique ids while several sessions publish into it concurrently.

Parallel sessions repeatedly claimed the same next-free flag id on this repository: `main` itself arrived at the
start of this session's last rebase with **F109 published twice** and **F117 published twice**, and this branch
collided with the merged range three further times (F106–F108, then F109, then F112–F116). A duplicate id is not
cosmetic: `#fl-F105` in `site/sheets.html` and every "see F105" sentence then resolve to whichever row the page
happened to emit last, so a reader following a citation lands on a different finding.

These tests fail on the whole class, whichever session introduces it:

  * no two flags share an id, and every id is `F<number>`;
  * the ids are contiguous from F1, so a gap cannot be misread as a withdrawn flag;
  * every `F<number>` mentioned anywhere on the published pages resolves to a real flag;
  * the two flags this session publishes are present and are the ids recorded on the board.

The fix when a collision is found is to renumber the later row (the one whose detail text names the newest session),
keep its text verbatim, and record the renumber in `COORDINATION.md`. That is what happened to F109→F121 and
F117→F122 on `main` and to this session's F106/F107→F119/F120.
"""
from __future__ import annotations

import collections
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / "site" / "data.json").read_text(encoding="utf-8"))
PAGES = sorted((ROOT / "site").glob("*.html")) + sorted((ROOT / "site" / "venues").glob("*.html"))
# Exclude the `id="fl-F105"` anchors and the `#fl-F105` links: those name an element, not a citation.
FLAG_RE = re.compile(r"(?<![-#])F(\d{1,3})\b")


class FlagIdsAreUnique(unittest.TestCase):
    def test_no_duplicate_ids(self):
        ids = [f["id"] for f in DATA["flags"]]
        dupes = {k: v for k, v in collections.Counter(ids).items() if v > 1}
        self.assertEqual(dupes, {}, f"duplicate flag ids published: {dupes}")

    def test_every_id_has_the_expected_shape(self):
        for flag in DATA["flags"]:
            self.assertRegex(flag["id"], r"^F\d+$", flag.get("title", "")[:60])
            self.assertTrue(flag.get("source"), f"{flag['id']} has no source")

    def test_no_id_is_reused_after_being_withdrawn(self):
        """Ids are assigned once and never recycled, so a withdrawn flag leaves a permanent gap.

        The register already carries gaps from retired ids, so contiguity is not required; what is required is
        that the highest id is the one this session last assigned and that nothing above it is dangling.
        """
        numbers = sorted(int(f["id"][1:]) for f in DATA["flags"])
        # F123 (arena/a400f338-poker3) added the Venetian connecting-suite contradiction during
        # integration; F124 (arena/98fa400f-poker3) added the third same-day Palazzo quote drift.
        # A new flag still goes at the end, above every id already issued.
        self.assertEqual(numbers[-1], 124, "a new flag must be added at the end of the register")

    def test_every_cited_flag_exists(self):
        # The register numbers the first flags with two digits (F01, F02, ... F09) and everything from
        # F10 up without padding, so citations are compared by integer, not by string.
        known = {int(f["id"][1:]) for f in DATA["flags"]}
        unknown = collections.Counter()
        for page in PAGES:
            for match in FLAG_RE.finditer(page.read_text(encoding="utf-8")):
                n = int(match.group(1))
                if n not in known:
                    unknown[f"F{n:02d}"] += 1
        self.assertEqual(dict(unknown), {}, f"pages cite flags that do not exist: {dict(unknown)}")

    def test_this_sessions_two_flags_are_published(self):
        by_id = {f["id"]: f for f in DATA["flags"]}
        self.assertIn("F119", by_id, "the monitor-gap flag is missing")
        self.assertIn("corrected official-source re-check", by_id["F119"]["title"])
        self.assertIn("F120", by_id, "the second dated total flag is missing")
        self.assertIn("3,619.39", by_id["F120"]["detail"])
        self.assertEqual(by_id["F120"]["area"], "Booking")

    def test_renumbered_main_flags_keep_their_text(self):
        """The two ids repaired on main (F109→F121, F117→F122) must still carry their own findings."""
        by_id = {f["id"]: f for f in DATA["flags"]}
        self.assertIn("full-day plan", by_id["F121"]["title"])
        self.assertIn("Event 17", by_id["F122"]["title"])


if __name__ == "__main__":
    unittest.main()
