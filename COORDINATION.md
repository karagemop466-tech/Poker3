# COORDINATION.md: shared task board

Created 2026-11-16 by session `f332570d` (branch `arena/f332570d-poker3`, based on `main` @ 895478b).

## Protocol (from the task)

- Claim a task here before starting it, with session ID and file scope. Never start a task another session has claimed.
- Session branches are named `session-<id>/<task>`. **Exception, see flag F20:** this session is restricted to a single branch, `arena/f332570d-poker3`. All work is on that branch, so no `session-*` branches were created.
- Commit small. Run `git pull --rebase` before every push.
- Log conflicts in the conflict log below.
- Only the final integration step edits shared outputs (site table data, `index.html`, navigation, `sources.html`) and publishes.

## Task board

| Task | Session | Status | File scope | Notes |
|---|---|---|---|---|
| T1 Collect official Venetian DSE IV schedule | f332570d | done | `raw/venetian_dse_nov_2026_schedule.md`, `data/venetian_*.json` | Verbatim text saved, parsed by `scripts/parse_official.py`. 83 flights, 11 restart or final rows. |
| T2 Collect official Wynn WPT schedule | f332570d | done | `raw/wynn_wpt_world_championship_schedule.md`, `data/wynn_wpt.json` | 136 rows, 116 with buy-in. 8 calendar conflicts (flag F03). |
| T3 Venetian structure sheets | f332570d | partial | `scripts/parse_official.py` (SHEET mapping) | 7 sheets read; 24 of 83 flights linked to a read sheet. 59 not yet checked. |
| T4 Wynn WPT structures | f332570d | partial | none (notes only) | First 3 of 8 chunks read. Re-entry verified for four Nov 27 rows. |
| T5 Hotel fees and parking (official) | f332570d | done for 3 hotels | `scripts/data.py` (HOTELS) | Venetian, Wynn, Resorts World. Room rates, tax and walking times not verified. |
| T6 Other Strip rooms (MGM, Caesars, Horseshoe, Aria, Bellagio, etc.) | — | **not started** | — | No official pages collected. Flag F13. |
| T7 Build site | f332570d | done | `scripts/build.py`, 12 HTML pages | Generated from data only. |
| T8 Final integration and publish | f332570d | in progress | shared outputs (table data, `index.html`, nav, `sources.html`) | PR and merge below. |

## Conflict log

- No conflicts. This session is the only writer on this branch.
- Note: the Pages URL returned SSL_ERROR_SYSCALL from the sandbox during the session. The sandbox cannot reach `*.github.io` (not in the allowed hosts list), so reachability is checked through the GitHub Pages API instead.

## Integration record

- PR: _to be filled after creation_
- Merge result: _to be filled after merge_
- Pages status: _to be filled after deploy check_
