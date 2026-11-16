# Poker3 — Coordination Board

Shared task board for agent sessions working on this repo.
Status values: `unclaimed`, `in progress`, `done`, `needs review`.
A `needs review` item is published on the Flagged for Review page and does not block anything.

## Session conventions
- Session ID = the git branch this session works on: `arena/e125b4a2-poker3`.
- Claims are recorded here and committed/pushed immediately before work begins.
- Each session edits only files in its claimed scope. To change another session's file, log a request here instead.

## Tasks

| # | Task | Status | Owner (session ID) | File scope | Started | Done |
|---|------|--------|--------------------|------------|---------|------|
| 1 | Create COORDINATION.md task board | done | arena/e125b4a2-poker3 | COORDINATION.md | 2026-11-16 | 2026-11-16 |
| 2 | Research live upcoming poker tournaments near Las Vegas Strip (official sources only) | in progress | arena/e125b4a2-poker3 | data/tournaments.md | 2026-11-16 | — |
| 3 | Research hotels within walking distance (≤30 min) of tournaments; true per-night cost incl. resort fees | unclaimed | arena/e125b4a2-poker3 | data/hotels.md | — | — |
| 4 | Build all-day tournament schedule (8 AM start, single-entry only) | unclaimed | arena/e125b4a2-poker3 | data/schedule.md | — | — |
| 5 | Executive summary | unclaimed | arena/e125b4a2-poker3 | pages/executive-summary.md | — | — |
| 6 | Suggestions section (site improvement suggestions, review-before-implement) | unclaimed | arena/e125b4a2-poker3 | pages/suggestions.md | — | — |
| 7 | Q&A section (questions/informations/answers, missing-info discovery suggestions) | unclaimed | arena/e125b4a2-poker3 | pages/q-and-a.md | — | — |
| 8 | Flagged for Review page (unverified items, irregularities, source links) | unclaimed | arena/e125b4a2-poker3 | pages/flagged-for-review.md | — | — |
| 9 | GitHub Pages site: clean landing page + category subpages, dashboard tables | unclaimed | arena/e125b4a2-poker3 | index.html, pages/*.html, assets/ | — | — |
| 10 | Line-by-line verification: every table row has an official source link; blanks for unconfirmed | unclaimed | arena/e125b4a2-poker3 | all data/pages files | — | — |
| 11 | Final integration: merge branches, re-verify combined data, confirm site builds, publish GitHub Pages | unclaimed | arena/e125b4a2-poker3 | all | — | — |
| 12 | Pull request to main, merge, confirm GitHub Pages deploys, record PR link + merge result here | unclaimed | arena/e125b4a2-poker3 | COORDINATION.md | — | — |

## Notes
- No other active sessions known; this session claims all tasks with non-overlapping scope (single session).
- All values must come from official verified sources; never infer or fill in. Leave blank and flag unverified.
- Source: branch `arena/e125b4a2-poker3`, branched from `895478bc63d97e02ceca147a0ddc5869114578ab` of main.
