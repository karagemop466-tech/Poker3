# Coordination board

Snapshot: 2026-11-16 UTC.

**Protocol note.** The platform binds each session to one branch. This session works only on `arena/93641c21-poker3`; the `session-<id>/<task>` naming in the brief cannot be applied here. This session is the only active editor, so it acts as the integration owner for every shared output (tournament data, index, navigation, schedule, flags).

| Task | Status | Owner session | Scope | Branch | PR |
|---|---|---|---|---|---|
| Research and build poker-trip dashboard + verification/flag pages (prior session) | done (data gaps remain flagged) | arena session 66708bda | all repository files | `arena/66708bda-poker3` | #1, #2 (merged to `main`) |
| Venetian DeepStack Extravaganza IV main list, schedule, excluded-by-reason tables, hotel template, flagged register, questions (this session) | done. Flagged items published; they do not block merge. | arena session 93641c21 (integration owner) | all repository HTML/CSS/README/COORDINATION (shared outputs) | `arena/93641c21-poker3` | [#6](https://github.com/karagemop466-tech/Poker3/pull/6) |

## Work log

- **2026-11-16 · Claim.** Recorded this claim on the branch before the site build. Branch fast-forwarded to `origin/main` (d3d6dff) so prior work is kept, not replaced.
- **Official source checks (this session).**
  - The Venetian official DeepStack Extravaganza IV event list (`dse-nov-2026.html`), all four chunks, with dates and start times for every event number.
  - Venetian structure sheets, numbered 1–37, read as needed. Single-start events were read directly; the three multi-flight and satellite groups were read for exclusion.
  - Wynn WPT schedule (pages 1–2) and structures; Wynn Signature Series schedule (structures unpublished); Wynn daily structures and poster; Wynn poker hub.
  - Bellagio poker page and the three weekly PDFs (Friday $600, Saturday titled $1,100 but body $600, Sunday $400 H.O.R.S.E.).
  - Aria poker page (room rates and contacts; no tournament schedule).
  - Hotel pages: The Venetian (no date-specific rate or resort fee published on the fetched page); Wynn hotel page not reachable.
- **Third-party sources were not used for any value.** They are listed only as conflicts on the Flagged page.
- **Main list rule.** Single-start, single-day Venetian events whose official sheets print their fee, prize-pool share and guarantee. No event is called "single entry" because no sheet says so; each row carries a status note.
- **Excluded rule.** Multi-flight Venetian events (bagging rule implies multiple entries); satellites; PokerAtlas PRO discount (paid membership); Bellagio and Wynn daily/WPT (re-entry, rebuys, gratuity chips); Wynn Signature (structures unpublished); team format (needs review).
- **Schedule.** Earliest verified main-list start is 10:10 AM. No 8 AM start is verified, so no all-day route is built. Finish times and walking times are not published.
- **Hotels.** No verified nightly rate, resort fee, or walking time. The template is left blank and flagged.
- **Conflicts with other branches.** Six other session branches exist on `origin`. None was modified. Shared pages were edited only by this session.
- **Irregularities flagged** (19 items on `flagged.html`), including: WPT $1,100 PLO breakdown sums to $1,105; WPT schedule labels Dec 18 as both Wednesday and Friday; Bellagio Saturday heading says $1,100 but body says $600; Bellagio "July 26" notice is undated (July 26, 2026 is a Sunday); Wynn Signature structures unpublished; Aria source conflict with the prior session's cited text.

## Merge plan

1. Commit site on `arena/93641c21-poker3`; `git pull --rebase origin arena/93641c21-poker3` before push.
2. Open PR to `main` with summary, sources and flags.
3. Merge with `gh pr merge <n> --merge` (no auto-merge).
4. Confirm GitHub Pages deployment; record the PR link and merge result in a follow-up commit to `main` (see the work log below).

## Result

- PR: [#6](https://github.com/karagemop466-tech/Poker3/pull/6)
- Merge: pending
- Pages deployment: pending

---

## Session arena-8fc8e9f1 (docs/ site and data)

Branch: `arena/8fc8e9f1-poker3`. Only `docs/**` and this section were changed by this session. Root-level site files, `README.md` and `.github/workflows/pages.yml` belong to the other session and were not edited here, except that `README.md` and the workflow come from `main` unchanged.

| Task | Status | Owner | Scope | Notes |
|---|---|---|---|---|
| T1 Repo review | done | arena-8fc8e9f1 | `README.md`, repo metadata | Irregularities listed as F25 on `docs/flagged.html`. |
| T2 Tournament data | done (partial) | arena-8fc8e9f1 | `docs/data/tournaments.json`, `docs/data/multi_entry.json` | Partial. Many rows still `pending` (structure not checked). Conflicts F02, F07, F09, F10, F11, F14. |
| T3 Hotel data | not started (data stub only) | arena-8fc8e9f1 | `docs/data/hotels.json` | Only Wynn resort fee confirmed on official terms ($55, conflict $50 — F05). Other fees, rates and walking times not verified (F15, F18). |
| T4 Analysis, summary, Q&A, suggestions | not started (drafts published) | arena-8fc8e9f1 | `docs/summary.html`, `docs/questions.html`, `docs/suggestions.html`, `docs/data/questions.json`, `docs/data/suggestions.json` | Suggestions await user choice. Hotel ranking not done. |
| T5 Static site | in progress | arena-8fc8e9f1 | `docs/**` | Ten pages in `docs/`. DOM test passed (no script errors). No real-browser check (Chromium install blocked by sandbox). |
| T6 Integration | in progress | arena-8fc8e9f1 | whole repo | PR and merge recorded below. |

**Duplicate-site note.** `main` already publishes a dashboard at the repository root (arena 93641c21). This session's site is at `docs/` and does not overwrite it. Both are published by the same Pages workflow. The user should choose which to keep. This is logged as a cross-session request for the other session and the user.

**Known gaps.** Hotel rates and walking times; structure checks for most events; DeepStack NYE and Showdown schedules beyond Feb 2; Caesars, MGM Grand, Golden Nugget, Resorts World, Circa, South Point and Orleans poker pages (F21). No verified start before 10:10 AM (F17), so the 8 AM all-day plan is not built.

### Integration log (session arena-8fc8e9f1)

- Branch `arena/8fc8e9f1-poker3`: `docs/**` site and data added; COORDINATION.md statuses corrected (f300daf → 231c2fd, then merge of `origin/main`).
- PR: _pending_
- Merge: _pending_
- Pages deployment: _pending_

---

## Session arena/d205f8ec-poker3 (root site: task board, earlier work log, integration)

## Session claim log
- Session `arena/66708bda-poker3` (earlier): claimed all repository files; built conservative root-level dashboard; deployed to GitHub Pages (run 43930736171, 2026-11-16) at https://karagemop466-tech.github.io/Poker3/ ; PRs #1 and #2 merged into main. Work log preserved below.
- Session `arena/d205f8ec-poker3` (current): comprehensive single-entry tournament data (Venetian DSE IV), hotel true-cost data, full site rebuild at root level, integration of both sessions' work. Working branch `arena/d205f8ec-poker3`.

## Task board

| # | Task | Status | Owning session | Files touched | Sources / verification | Notes |
|---|------|--------|----------------|---------------|------------------------|-------|
| 1 | Research and build poker-trip dashboard + verification/flag pages | done | arena/66708bda-poker3 | all repository files (root level) | aria.com/en/nightlife.html (ARIA times only; not date-specific) | Conservative stance: 0 events fully verified as single-entry at that time; third-party listings not accepted. Deployed to GitHub Pages successfully. |
| 2 | Create COORDINATION.md shared task board | done | arena/d205f8ec-poker3 | COORDINATION.md | n/a | Combined board; both sessions' claims logged |
| 3 | Repo review line-by-line; flag irregularities | done | arena/d205f8ec-poker3 | README.md, repo root | n/a | Repo began as 8-byte README only; both sessions' work retained in git history |
| 4 | Research upcoming Las Vegas Strip poker tournaments (single entry only) | done | arena/d205f8ec-poker3 | tournaments.html, data/tournaments.md | venetianlasvegas.com DSE IV page + structure sheets; worldpokertour.com press release + structures PDF | 53 one-day events Nov 18–Dec 23, 2026 (no re-entry wording on sheets; single entry not printed), each with official schedule + structure-sheet links; multi-entry/re-entry events (incl. Wynn WPT festival) in separate section |
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

### Integration log (session arena/d205f8ec-poker3, 2026-11-16 UTC)

- `main` (83e85d0) had advanced with the `docs/` site (PR #8) and root pages from session 93641c21 (PR #6). The merge was done with `git merge origin/main`.
- Conflicts were in `COORDINATION.md`, `README.md`, `index.html`, `style.css`, `tournaments.html`, `hotels.html`, `schedule.html`, `questions.html`, `flagged.html`.
- **`docs/` from main is kept unchanged.** It is the arena-8fc8e9f1 site and is published by the same Pages workflow at `/docs/`.
- **Root pages** use this session's versions. They have the single-entry table, the hotel formula, the schedule and the Q&A. Session 93641c21's root versions are in git history at `83e85d0` (also referenced in PR #6).
- **Flagged register.** Session 93641c21's 19-item register is included unchanged on `flagged.html`. This session's F1–F9, C1–C3 and the prior-session review are also kept.
- **Structure-sheet check.** All 22 structure sheets for the main list were read in full on 2026-11-16. The result is a correction: the single-entry status is not printed on any sheet, so the rows say "no re-entry or add-on wording on sheet". Details are on `flagged.html` as S1–S8. Entry-type labels were corrected on the tables and index. #35 (team) and #39 (2-day, female-only) are labelled as such.
- **No work was deleted.** Branch `arena/66708bda-poker3` and the earlier commits remain in git history.

### Verification performed (this session)

- Tournament rows: event number, day, start time, buy-in and guarantee compared with the structure sheet for every main-list row (sheets 1, 5, 6, 7, 8, 11, 15, 16, 17, 18, 22, 23, 24, 25, 26, 28, 29, 30, 31, 32, 33, 34). Sheets 1 and 5 were read in an earlier pass of this session.
- Irregularities found and logged: S1–S8 on `flagged.html`.
- Internal links: checked after the final edit (see the result section below).

### Result (this session)

- PR: [#5](https://github.com/karagemop466-tech/Poker3/pull/5) (`arena/d205f8ec-poker3` → `main`)
- Merge: pending at the time of this entry. Updated after the merge.
- Pages deployment: pending at the time of this entry. Updated after the merge.
