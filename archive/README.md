# archive/ — retired artefacts, kept for provenance

Nothing in this directory is published by the GitHub Pages artifact and nothing reads it at runtime.
`site/` is the only published directory, so a file here cannot be mistaken for a current value by a
reader who opens the live host.

| File | What it was | Why it is here | Date moved | Successor |
|---|---|---|---|---|
| `snapshot_2026-11-16_flags.json` | A 2026-11-16 snapshot of the flag register (`meta.builtAt 2026-11-16T19:50:18Z`) | It was reachable at the live host under `site/data/` and gave a second, older answer (flag F101). It is not read by any page or script. | 2026-11-19 | `site/data.json` → `flags` |
| `snapshot_2026-11-16_questions.json` | 2026-11-16 snapshot of the open questions | Same reason as above. | 2026-11-19 | `site/data.json` → `questions` |
| `snapshot_2026-11-16_suggestions.json` | 2026-11-16 snapshot of the suggestions list | Same reason as above. | 2026-11-19 | `site/data.json` → `suggestions` |
| `snapshot_2026-11-16_tournaments.json` | 2026-11-16 snapshot of the tournament rows | Same reason as above. Its rows predate every re-read recorded on the live rows. | 2026-11-19 | `site/data.json` → `events` |
| `daily_check_sources_2026-11-16.json` | The URL list read by `scripts/daily_check.py` | That script is retired and unused (no workflow references it); the scheduled checker reads the URL list out of `site/data.json` instead. Moving the file stops the live host serving a stale source list. | 2026-11-19 | `scripts/check_sources.py` |

Verification performed when moving these files (2026-11-19, session `arena/e94482ee-poker3`):

- Searched every page, script and test for a reader of each file. The only reader was
  `scripts/daily_check.py` (retired, no workflow reference) and `scripts/build_data.py`, which was removed
  because nothing referenced it. No HTML page or JavaScript asset fetches any of the five files; the only
  runtime fetches are `data.json`, `checks.json` and `feed/index.json`.
- `tests/test_sheet_page_not_stale.py` previously guarded only three of the eight retired names; it now
  asserts that all eight are absent from `site/data/`, so a restore fails the suite.
- No value was ever taken from these snapshots for a published row: every table row on the site is rendered
  from `site/data.json`.
