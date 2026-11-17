# Independent live re-check, session `arena/688eb797-poker3` — 2026-11-17 ~01:35 UTC

**Claim under test.** Every published DeepStack Extravaganza IV row matches the official schedule page.

**Method.** The official page
`https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html`
was fetched fresh from the venue host by this session (fetch_page, 4 chunks), transcribed to
`raw/dse_nov_2026_schedule_html_2026-11-17_session688e.md`, and passed through the repository's own
comparator `scripts/verify_live_official.py` with only the capture path pointed at this session's file:

- 94/94 rows agree with the canonical rows in `site/data.json` on **date, start time, event number,
  name, structure sheet, printed buy-in and printed guarantee**;
- 94/94 rows agree with the official schedule PDF on the ordered (event, time) sequence, and on every
  date the PDF prints;
- recurring Wynn rows re-matched the daily poster 4/4 (part of the same comparator run);
- dated official quotes re-reconciled to `(rate + resort fee) × 1.1338`.

**Result: EXIT 0 — "OK - the canonical rows match both official captures line by line."**

This is an independent third read of the same page on 2026-11-17 (after session `b573f10a`'s capture and
session `cf53e83c`'s), by a session that did not participate in writing the canonical rows.

**No value changed. No row was re-stamped beyond what the comparator asserts.**
