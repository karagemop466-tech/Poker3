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
| 2 | Research live upcoming poker tournaments near Las Vegas Strip (official sources only) | done | arena/e125b4a2-poker3 | data/tournaments.md | 2026-11-16 | 2026-11-16 |
| 3 | Research hotels within walking distance (≤30 min) of tournaments; true per-night cost incl. resort fees | done | arena/e125b4a2-poker3 | data/hotels.md | 2026-11-16 | 2026-11-16 |
| 4 | Build all-day tournament schedule (8 AM start, single-entry only) | done | arena/e125b4a2-poker3 | data/schedule.md + schedule.html | 2026-11-16 | 2026-11-16 |
| 5 | Executive summary | done | arena/e125b4a2-poker3 | executive-summary.html | 2026-11-16 | 2026-11-16 |
| 6 | Suggestions section (site improvement suggestions, review-before-implement) | done | arena/e125b4a2-poker3 | suggestions.html | 2026-11-16 | 2026-11-16 |
| 7 | Q&A section (questions/informations/answers, missing-info discovery suggestions) | done | arena/e125b4a2-poker3 | q-and-a.html | 2026-11-16 | 2026-11-16 |
| 8 | Flagged for Review page (unverified items, irregularities, source links) | done | arena/e125b4a2-poker3 | flagged-for-review.html | 2026-11-16 | 2026-11-16 |
| 9 | GitHub Pages site: clean landing page + category subpages, dashboard tables | in progress | arena/e125b4a2-poker3 | index.html, *.html, css/style.css | 2026-11-16 | — |
| 10 | Line-by-line verification: every table row has an official source link; blanks for unconfirmed | done | arena/e125b4a2-poker3 | all data/pages files | 2026-11-16 | 2026-11-16 |
| 11 | Final integration: commit, enable GitHub Pages, verify build + no broken links | in progress | arena/e125b4a2-poker3 | all | 2026-11-16 | — |
| 12 | Pull request to main, merge, confirm GitHub Pages deploys, record PR link + merge result here | unclaimed | arena/e125b4a2-poker3 | COORDINATION.md | — | — |

## Sources verified (official)
- Venetian DSE IV schedule: https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html
- Venetian DSE IV structure sheets: .../content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_N.pdf
- WPT World Championship schedule PDF: https://wptmedia-mig.s3.amazonaws.com/wp-content/uploads/2026/09/WPT-World-Championship-Festival-Schedule-Season-24.pdf
- WPT World Championship Terms & Conditions: https://wptmedia-mig.s3.amazonaws.com/wp-content/uploads/2026/11/WPT_World_Championship_Structures.pdf
- WPT press release (marquee event entry rules): NewsBreak-hosted WPT Season 24 release
- ARIA Poker Open dates/venue: @ARIAPoker X post; Hendon Mob venue listing

## Flagged / unverified items (do not block launch)
F1–F12 as listed on pages/flagged-for-review.md and flagged-for-review.html. Notable: ARIA Poker Open event details (official page HTTP 500), WPT non-marquee entry rules, hotel room rates, resort fees (third-party only), walking time estimates, no 8 AM start exists.
