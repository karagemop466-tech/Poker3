# COORDINATION.md

Shared task board for the Poker3 project (Las Vegas Strip poker tournament planner).
Session: `arena/d205f8ec-poker3` (single active session in this checkout).

Status values: unclaimed | in progress | done | needs review

| # | Task | Status | Owning session | Files touched | Sources / verification | Notes |
|---|------|--------|----------------|---------------|------------------------|-------|
| 1 | Create COORDINATION.md shared task board | done | arena/d205f8ec-poker3 | COORDINATION.md | n/a | Claimed and committed on branch arena/d205f8ec-poker3 |
| 2 | Repo review line-by-line; flag irregularities | done | arena/d205f8ec-poker3 | README.md, repo root | n/a | Irregularities flagged: README was only "# Poker3" (8 bytes); no site files, no data, no .gitignore, no GitHub Pages config. Built site from scratch. |
| 3 | Research upcoming Las Vegas Strip poker tournaments (single entry only) | done | arena/d205f8ec-poker3 | data/tournaments.md + site pages | venetianlasvegas.com DSE IV page + structure sheets; worldpokertour.com press release + structures PDF | Venetian DSE IV Nov 16-Dec 23: (1Day) events have NO re-entry clause in structure sheets => single entry; flighted events (1A-1F) => multi-entry separate section. Wynn WPT festival: re-entry on nearly all events => separate section. Full schedule captured Nov 17-Dec 23. |
| 4 | Research hotels within 30-min walk of tournaments; true cost/night incl. resort fees + taxes | done | arena/d205f8ec-poker3 | data/hotels.md (or site data) | venetianlasvegas.com (official); wynnlasvegas.com (official stay terms) | Venetian: $55+tax resort fee, 13.38% Clark County room tax, $20/day guest self-parking. Wynn/Encore: $55+tax resort fee (~$62.36 w/ tax), free guest self-parking. Room rates for Nov-Dec 2026 not yet published => blank + flagged. |
| 5 | Executive summary of important details | done | arena/d205f8ec-poker3 | site/index.html | Tied to tasks 3, 4 | On landing page |
| 6 | Clear list of questions / information / answers needed before decisions; suggestions to discover missing info | done | arena/d205f8ec-poker3 | site/pages/questions.html | n/a | 10 questions + discovery suggestions |
| 7 | Site improvement suggestions section (review before implementing) | done | arena/d205f8ec-poker3 | site/pages/suggestions.html | n/a | 10 suggestions + decision record table |
| 8 | Site creation: landing page + category subpages, dashboard-style tables, analysis | done | arena/d205f8ec-poker3 | site pages, css/style.css | n/a | GitHub Pages static site: index.html, tournaments.html, hotels.html, schedule.html, questions.html, suggestions.html, flagged.html. All internal links OK. |
| 9 | Verification: every table row has official source link; unverified left blank and flagged | done | arena/d205f8ec-poker3 | all site pages | Official sources per row | 117 external source links in data/tournaments.md; all internal links verified; blank cells flagged on data pages |
| 10 | "Flagged for Review" page listing irregularities + unverified items with source links | done | arena/d205f8ec-poker3 | site/pages/flagged.html | COORDINATION.md | F1-F9 unverified items; C1-C3 source conflicts; repo irregularities |
| 11 | Integration: final branch, rebuild verification, no broken links | in progress | arena/d205f8ec-poker3 | full site | n/a | Files staged at repo root for GitHub Pages; commit + push, then enable Pages |
| 12 | GitHub Pages publish; confirm deploy; create PR from integration branch to main; merge; record PR link + merge result here | unclaimed | arena/d205f8ec-poker3 | repo + GitHub Pages | n/a | Do not merge a broken site |

## Claim log
- Session `arena/d205f8ec-poker3` claims all tasks above on branch `arena/d205f8ec-poker3`. No other active sessions in this checkout; if another session appears, it must claim tasks here before starting and keep scopes non-overlapping.
