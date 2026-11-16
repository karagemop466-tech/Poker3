# Poker3 — Coordination Board

Shared task board for agent sessions working on this repo.
Status values: `unclaimed`, `in progress`, `done`, `needs review`.
A `needs review` item is published on the Flagged for Review page and does not block anything.

## Session conventions (per repo protocol)
- Each session works on its own branch; shared outputs (index, navigation, table data) are changed only by the final integration session.
- Never discard another session's work. Merge conflicts are resolved by preserving both bodies of work and logging the resolution.

## Sessions on this repo
| Session | Branch | Role |
|---------|--------|------|
| arena/66708bda | arena/66708bda-poker3 | Prior session — dashboard + verification/flag pages (PRs #1, #2 merged) |
| arena/93641c21 | arena/93641c21-poker3 | Prior integration owner — root site, Venetian DSE IV list, flags, questions (PR #6 merged) |
| arena/8fc8e9f1 | arena/8fc8e9f1-poker3 | Prior session — docs/ site + data (PR #8 merged) |
| arena/e125b4a2-poker3 | arena/e125b4a2-poker3 | Current session — per-row verified tables, extra pages, integration (this board) |

## Tasks (reconciled across sessions)

| # | Task | Status | Owner (session) | File scope | Branch / PR |
|---|------|--------|-----------------|------------|-------------|
| 1 | Repo review / metadata | done | arena/66708bda | README.md, repo metadata | #1, #2 merged to main |
| 2 | Tournament data | done (partial; gaps flagged) | arena/66708bda | docs/data/tournaments.json, docs/data/multi_entry.json | #1, #2 |
| 3 | Hotel data | not started (data stub only) | arena/66708bda | docs/data/hotels.json | stub |
| 4 | Analysis, summary, Q&A, suggestions | done (drafts published) | arena/66708bda | docs/summary.html, docs/questions.html, docs/suggestions.html | drafts |
| 5 | Static site (docs/ edition) | done | arena/8fc8e9f1 | docs/** | #8 merged to main |
| 6 | Venetian DSE IV main list, schedule, excluded-by-reason tables, hotel template, flagged register, questions (root site) | done; flagged items do not block merge | arena/93641c21 | root HTML + COORDINATION (shared outputs) | #6 merged to main |
| 7 | Per-row verified tournament tables (this session) | done | arena/e125b4a2-poker3 | data/tournaments.md (Venetian DSE IV structure sheets 1–37; WPT marquee events) | this branch |
| 8 | Hotel research + true-cost template (this session) | done; rates/fees unverified | arena/e125b4a2-poker3 | data/hotels.md | this branch |
| 9 | All-day single-entry schedule (this session) | done; no 8 AM start verified | arena/e125b4a2-poker3 | data/schedule.md | this branch |
| 10 | Executive summary + suggestions + Q&A + Flagged for Review (this session) | done | arena/e125b4a2-poker3 | executive-summary.html, suggestions.html, q-and-a.html, flagged-for-review.html, pages/*.md | this branch |
| 11 | Line-by-line verification (this session) | done | arena/e125b4a2-poker3 | every Table A/B row links to official source | this branch |
| 12 | Integration: merge prior main into this branch, resolve conflicts without discarding work | done | arena/e125b4a2-poker3 | COORDINATION.md, README.md, root HTML | this branch → PR #9 → main |
| 13 | PR to main, merge, confirm GitHub Pages deploys, record PR link + merge result | in progress | arena/e125b4a2-poker3 | main branch, Pages deployment | PR #9 |

## Work log
- 2026-11-16: Current session branched from 895478b (initial commit). Unknowingly duplicated prior sessions' work because local `main` was stale.
- 2026-11-16: Discovered GitHub `main` (83e85d0) already contains prior sessions' integrated site (root + docs/) via PRs #1, #2, #6, #8.
- 2026-11-16: Merged `origin/main` into `arena/e125b4a2-poker3`. Conflicts in COORDINATION.md, README.md, index.html, tournaments.html, hotels.html, schedule.html resolved by KEEPING main's shared root site files (prior sessions' integrated output, not discarded) and adding this session's unique files (data/*.md, pages/*.md, executive-summary.html, suggestions.html, q-and-a.html, flagged-for-review.html, css/style.css). Both bodies of work preserved.
- 2026-11-16: PR #9 opened from arena/e125b4a2-poker3 to main.

## Merge plan (remaining)
1. Push resolved `arena/e125b4a2-poker3` (PR #9 auto-updates and becomes mergeable).
2. `gh pr merge 9 --merge` (no auto-merge).
3. Confirm GitHub Pages deployment at https://karagemop466-tech.github.io/Poker3/.
4. Record PR link and merge result below; mark task 13 done.

## PR / merge result (to be filled after merge)
- PR: https://github.com/karagemop466-tech/Poker3/pull/9
- Merge: pending
- Pages deployment: pending

## Flagged / unverified items (do not block launch)
See pages/flagged-for-review.md (this session) and docs/flagged.html + root flagged.html (prior sessions). Notable: ARIA Poker Open event details (official page HTTP 500), WPT non-marquee entry rules, hotel room rates, resort fees (third-party only), walking-time estimates, no 8 AM start verified.
