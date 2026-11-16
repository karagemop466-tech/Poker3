# COORDINATION.md

Shared task board for the Poker3 project (Las Vegas Strip poker tournament planner).

Status values: unclaimed | in progress | done | needs review

## Session claim log
- Session `arena/66708bda-poker3` (earlier): claimed all repository files; built conservative root-level dashboard; deployed to GitHub Pages (run 43930736171, 2026-11-16) at https://karagemop466-tech.github.io/Poker3/ ; PRs #1 and #2 merged into main. Work log preserved below.
- Session `arena/d205f8ec-poker3` (current): comprehensive single-entry tournament data (Venetian DSE IV), hotel true-cost data, full site rebuild at root level, integration of both sessions' work. Working branch `arena/d205f8ec-poker3`.

## Task board

| # | Task | Status | Owning session | Files touched | Sources / verification | Notes |
|---|------|--------|----------------|---------------|------------------------|-------|
| 1 | Research and build poker-trip dashboard + verification/flag pages | done | arena/66708bda-poker3 | all repository files (root level) | aria.com/en/nightlife.html (ARIA times only; not date-specific) | Conservative stance: 0 events fully verified as single-entry at that time; third-party listings not accepted. Deployed to GitHub Pages successfully. |
| 2 | Create COORDINATION.md shared task board | done | arena/d205f8ec-poker3 | COORDINATION.md | n/a | Combined board; both sessions' claims logged |
| 3 | Repo review line-by-line; flag irregularities | done | arena/d205f8ec-poker3 | README.md, repo root | n/a | Repo began as 8-byte README only; both sessions' work retained in git history |
| 4 | Research upcoming Las Vegas Strip poker tournaments (single entry only) | done | arena/d205f8ec-poker3 | tournaments.html, data/tournaments.md | venetianlasvegas.com DSE IV page + structure sheets; worldpokertour.com press release + structures PDF | 53 single-entry (1Day) events Nov 18–Dec 23, 2026, each with official schedule + structure-sheet links; multi-entry/re-entry events (incl. Wynn WPT festival) in separate section |
| 5 | Research hotels within 30-min walk of tournaments; true cost/night incl. resort fees + taxes | done | arena/d205f8ec-poker3 | hotels.html, data/hotels.md | venetianlasvegas.com (official); wynnlasvegas.com (official stay terms) | $55+tax resort fee, 13.38% Clark County tax, $20/day Venetian parking confirmed. Nov–Dec 2026 room rates not yet published => blank + flagged |
| 6 | Executive summary of important details | done | arena/d205f8ec-poker3 | index.html | Tied to tasks 4, 5 | On landing page |
| 7 | Clear list of questions / information / answers needed before decisions; suggestions to discover missing info | done | arena/d205f8ec-poker3 | questions.html | n/a | 10 questions + prior session's open questions preserved |
| 8 | Site improvement suggestions section (review before implementing) | done | arena/d205f8ec-poker3 | suggestions.html | n/a | 10 suggestions + decision record table |
| 9 | Site creation: landing page + category pages, dashboard tables, analysis | done | arena/d205f8ec-poker3 | index.html, style.css, tournaments.html, hotels.html, schedule.html, questions.html, suggestions.html, flagged.html | n/a | Root-level GitHub Pages static site; all internal links verified OK |
| 10 | Verification: every table row has official source link; unverified left blank and flagged | done | arena/d205f8ec-poker3 | all pages | Official sources per row | Prior session's conservative conclusion preserved in flagged.html + questions.html |
| 11 | "Flagged for Review" page listing irregularities + unverified items with source links | done | arena/d205f8ec-poker3 | flagged.html | COORDINATION.md | Includes prior session review (F1–F9, C1–C3, ARIA-only finding) |
| 12 | Integration: merge branches, re-verify combined data, no broken links | done | arena/d205f8ec-poker3 | full site | n/a | main merged into arena/d205f8ec-poker3; conflicts resolved without discarding prior session's work |
| 13 | GitHub Pages publish; confirm deploy; create PR from integration branch to main; merge; record PR link + merge result here | in progress | arena/d205f8ec-poker3 | repo + GitHub Pages | n/a | PR #5 created; merge pending after Pages re-enablement on main |

## Earlier session work log (preserved)
- Repository was a minimal README-only checkout; no existing site or other coordination entries.
- Scope consolidated into that session because no other task owners existed. Work stayed on Arena-assigned branch `arena/66708bda-poker3`.
- Official-source check: ARIA poker information, https://aria.com/en/nightlife.html, describes tournaments daily at 1 p.m. and nightly at 7 p.m. It does not substantiate date-specific events, buy-ins, guarantees, entry rules, or duration. Thus it is listed as incomplete and not a qualified single-entry event.
- Third-party calendar listings were not accepted as verification. They are labeled non-authoritative in flagged.html. No unsupported tournament rows, guarantees, hotel rates, resort fees or distances were added.
- Manual line-by-line review of authored tables and source links; automated local HTML relative-link check passed. GitHub Pages build/deploy succeeded in run 43930736171 (2026-11-16).
- Claim commit: 058a8a4.
- PR #1: https://github.com/karagemop466-tech/Poker3/pull/1 — merged with `gh pr merge 1 --merge`. Pages deployment completed successfully.
- PR #2: https://github.com/karagemop466-tech/Poker3/pull/2 — merged; docs: record successful pages deployment.

## Integration notes (current session)
- main had advanced (d3d6dff) since arena/d205f8ec-poker3 was created from 895478b. Merging main into the feature branch produced add/add conflicts in COORDINATION.md, README.md, index.html.
- Resolution: one coherent root-level site built from the current session's comprehensive, source-linked data; the earlier session's root HTML files were superseded but their findings are preserved in flagged.html and questions.html, and their full work log is recorded above. Their branch `arena/66708bda-poker3` and commits remain in git history — nothing was deleted.
- All internal links verified; every table row carries an official source link; blank cells are intentional and flagged.
