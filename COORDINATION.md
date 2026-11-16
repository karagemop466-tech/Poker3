# COORDINATION.md — shared task board

Repo: `karagemop466-tech/Poker3` · Session: `arena-8fc8e9f1` · Branch: `arena/8fc8e9f1-poker3` (base `895478b`, `main`)

Note on branching: this session is bound to a single branch (`arena/8fc8e9f1-poker3`). The
`session-<id>/<task>` branch scheme in the original brief could not be used, so every task
below was done on this one branch in separate commits per task. The integration step is this
same branch, merged to `main` by PR.

Status legend: `unclaimed` · `in progress` · `done` · `needs review` (published on the Flagged for Review page)

| Task | Status | Owner (session) | Files / scope | Notes |
|---|---|---|---|---|
| T1 Repo review (line-by-line) | done | arena-8fc8e9f1 | `README.md`, repo metadata | See "Repo review" below. Flags F25 published. |
| T2 Tournament data (single-entry, Strip) | done (partial) | arena-8fc8e9f1 | `docs/data/tournaments.json`, `docs/data/multi_entry.json` | Official Wynn, Venetian, Bellagio sources. Partial: many rows still `pending` (structure not checked); Bellagio Saturday buy-in conflict (F02); DSE NYE and DSS only partly captured (F14). |
| T3 Hotel data (cost, resort fees, walking) | not started (data stub only) | arena-8fc8e9f1 | `docs/data/hotels.json` | Only Wynn resort fee confirmed on official terms ($55 with conflict $50, F05). Venetian, Bellagio, ARIA and Caesars fees unverified. Rates and walking times blank (F18). Not a complete ranking. |
| T4 Analysis, executive summary, Q&A, suggestions | not started (drafts published) | arena-8fc8e9f1 | `docs/summary.html`, `docs/questions.html`, `docs/suggestions.html`, `docs/data/questions.json`, `docs/data/suggestions.json` | Drafts are published. Suggestions await user choice. Hotel ranking and true-cost comparison are not done. |
| T5 Static site (GitHub Pages) | in progress | arena-8fc8e9f1 | `docs/**` | Ten pages built (dashboard, tables, flags, sources). Rendering verified in a DOM test (no script errors); no real-browser check. Pages settings not yet confirmed. |
| T6 Integration: merge, re-verify, build check, PR, merge, Pages deploy | not started | arena-8fc8e9f1 | whole repo | See Integration log. |

Status correction: an earlier version of this board marked T1, T2, T4 and T5 as done and T3 as done (partial). That was overstated. Corrected above.

Branch deviation: the brief specified per-task branches `session-<id>/<task>`. This session is bound to one branch, `arena/8fc8e9f1-poker3`, so all tasks are on that branch in separate commits.

## Repo review (T1)

Reviewed: `README.md` (1 line: `# Poker3`), git history (1 commit `895478b Initial commit`), and the branch list (`main`, `arena/8fc8e9f1-poker3`). Irregularities:

1. README is one line and has no description, setup, or data notes. (Flag F25)
2. No LICENSE file. (F25)
3. No `.gitignore`. (F25)
4. `COORDINATION.md` did not exist before this session. It was created here. (F25)
5. The brief asked for per-session branches (`session-<id>/<task>`). The platform rule for this session is one branch, so the per-session scheme was not used. (F25)

## Integration log (T6)

- Pending: PR link and merge result will be written here before the merge is requested.
- Known gaps at this point: hotel rates and walking times, most structure checks, DSE NYE and DSS schedules, and Caesars/MGM Grand/Golden Nugget/Resorts World/Circa/South Point/Orleans poker pages (F21).

## Sources and verification log

- Each task's sources are listed in `docs/sources.html` and `docs/data/sources.json`.
- Verification date for every fetched official page: **2026-11-16** (today, per the session clock).
- Irregularities for each task are on the Flagged for Review page (`docs/flagged.html`).
