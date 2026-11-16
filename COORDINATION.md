# Coordination board

Snapshot: 2026-11-16 UTC.

**Protocol note (current session).** The platform binds this session to `arena/db5ab1d1-poker3`; the `session-<id>/<task>` naming in the brief cannot be applied here. The previous session records below are historical. This session is the only active editor recorded at start and is integrating the published `site/` dashboard plus its daily source monitor. It will not edit other historical dashboards or change branches.

| Task | Status | Owner session | Scope | Branch | PR |
|---|---|---|---|---|---|
| Research and build poker-trip dashboard + verification/flag pages (prior session) | done (data gaps remain flagged) | arena session 66708bda | all repository files | `arena/66708bda-poker3` | #1, #2 (merged to `main`) |
| Venetian DeepStack Extravaganza IV main list, schedule, excluded-by-reason tables, hotel template, flagged register, questions (historical session) | done. Flagged items published; they do not block merge. | arena session 93641c21 (integration owner) | root site files, README, COORDINATION (shared outputs) | `arena/93641c21-poker3` | [#6](https://github.com/karagemop466-tech/Poker3/pull/6), merged |
| Dashboard decision tools, venue pages, per-row evidence metadata, and scheduled official-source change monitoring (current session) | in progress | arena/db5ab1d1-poker3 | `site/**`, `scripts/source_monitor.py`, `.github/workflows/**`, `tests/**`, `README.md`, `COORDINATION.md` | `arena/db5ab1d1-poker3` | — |

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

- PR: [#6](https://github.com/karagemop466-tech/Poker3/pull/6), merged 2026-11-16 18:47:13 UTC with `gh pr merge 6 --merge` (merge commit `4af9596`).
- Pages: deploy run [43932491105](https://github.com/karagemop466-tech/Poker3/actions/runs/43932491105) completed `success`; Pages API reports `status: built`, source `main` `/`.
- Live site: https://karagemop466-tech.github.io/Poker3/ (the sandbox cannot reach github.io directly; deployment confirmed via GitHub API and run status).
- Follow-up that records this result: [#10](https://github.com/karagemop466-tech/Poker3/pull/10). Its merge needed a clean rebase onto `main` after another session's merge (PR #8). The conflict was in this file only; both sections were kept.
- Cross-session note: arena-8fc8e9f1 publishes a separate site in `docs/`, which overlaps this root site. Both are served by the same Pages workflow; the user should choose which to keep. This session did not edit `docs/`.

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
- PR: [#8](https://github.com/karagemop466-tech/Poker3/pull/8) (arena/8fc8e9f1-poker3 → main), merge commit `83e85d0`, merged with `--merge` on 2026-11-16.
- Merge check: no broken internal links across `docs/*.html` and root `*.html`; all `docs/` inline scripts parse; ten pages render in a DOM test (nav present, tables populated, no script errors). Real-browser check not possible in the sandbox.
- Pages deployment: "Publish site to GitHub Pages" succeeded and Pages status `built` at `83e85d0`. Site root https://karagemop466-tech.github.io/Poker3/ ; this session's pages at `/docs/`.
- Remaining work (not done): hotel rates and walking times, most structure checks, DeepStack NYE/Showdown full schedules, other Strip rooms, 8 AM plan (no verified early start).

---

## Session f332570d (verified-only site in `verified/`)

Branch: `arena/f332570d-poker3` (single branch for this session; the `session-<id>/<task>` naming could not be used, as other sessions recorded above).

Placement decision: this session's pages live in `verified/`. Root and `docs/` are not edited, so the root dashboard (session 93641c21) and the docs site (session 8fc8e9f1) are unchanged. The Pages workflow deploys the whole repository on pushes to `main`, so all three sites are published together. Choosing which to keep is a user decision.

| Task | Status | Owner | Scope | Notes |
|---|---|---|---|---|
| T1 Venetian DSE IV official schedule (verbatim text + parser) | done | f332570d | `raw/venetian_dse_nov_2026_schedule.md`, `data/venetian_*.json`, `scripts/parse_official.py` | 83 flights, 11 restart or final-table rows; 13 dates inferred from row order (marked). |
| T2 Wynn WPT official schedule (verbatim text + parser) | done | f332570d | `raw/wynn_wpt_world_championship_schedule.md`, `data/wynn_wpt.json` | 136 rows, 116 with buy-in; 8 Dec 18 weekday conflicts (flag F03). |
| T3 Venetian structure sheets | partial | f332570d | `scripts/parse_official.py` (sheet mapping) | 7 sheets read; 24 of 83 flights linked to a read sheet; 59 not yet checked (F07). |
| T4 Wynn WPT structures | partial | f332570d | notes only | First 3 of 8 chunks read; re-entry verified for 4 Nov 27 rows (F11). |
| T5 Official hotel fees: Venetian, Wynn, Resorts World | done | f332570d | `scripts/data.py` | Fees and parking only. Room rates, tax and walking times are not verified (F15, F16). |
| T6 Other Strip rooms (MGM, Caesars, Horseshoe, Aria, Bellagio, etc.) | not started | — | — | No official pages collected (F13). |
| T7 Build `verified/` site (12 pages) | done | f332570d | `verified/*.html`, `scripts/build.py` | Generated only from the data files; every table row links its source. |
| T8 Integration, PR and merge | in progress | f332570d | `verified/`, this section | See integration record below. |

Differences from the root site, for the user to compare: the root site lists single-start events only and excludes multi-flight events; the `verified/` site lists all 83 flights with a status column, and lists Wynn WPT re-entry rows separately.

Conflict log:
- 2026-11-16: an earlier version of this branch put its pages at the repository root. That would have overwritten root pages from sessions 93641c21 and 66708bda (index, flagged, hotels, questions, schedule). The pages were moved to `verified/` before merging `origin/main`, so no shared file was changed.
- 2026-11-16: `COORDINATION.md` add/add conflict on merge of `origin/main`. Resolved by keeping `main`'s content in full and appending this section.

Integration record:
- PR: https://github.com/karagemop466-tech/Poker3/pull/12 (`arena/f332570d-poker3` into `main`; updated to the `verified/` layout).
- Merge result: recorded in the follow-up section after the merge.

## Current session arena/ada1dd4d-poker3 — final integration

Branch: `arena/ada1dd4d-poker3`. The session began from the Arena-provided initial snapshot before the parallel PRs had reached its local `main`; it claimed the task on its managed branch and later rebased onto the updated `origin/main`. This integration preserves all earlier merged session histories above. `site/` is selected as the canonical published dashboard; the earlier root and `docs/` dashboards remain in the repository as prior research artifacts, not the current Pages artifact.

| Task | Status | Owner | Scope | Notes |
|---|---|---|---|---|
| Expanded official-source schedule/hotel research, clean dashboard, questions, suggestions, day plan | implemented; unknown terms remain flagged | arena-ada1dd4d-poker3 | `site/**`, `scripts/**`, `.github/workflows/**`, `README.md`, this section | Current primary evidence only; site verification passes, but no tournament is confirmed strictly single-entry. |
| Verify one-entry / no-re-entry / no-add-on rules | needs review | arena-ada1dd4d-poker3 | `site/data.json`, `site/tournaments.html`, `site/flagged.html` | Candidates with missing terms are not marked eligible. |
| Obtain date-specific hotel totals and verify walking/time feasibility | needs review | arena-ada1dd4d-poker3 | `site/data.json`, `site/hotels.html`, `site/flagged.html` | Dates/occupancy absent; totals and route times blank. |

### Integration log

- Initial claim commit `3ba73ae` was pushed to the current Arena branch. At that initial point, this clone had only the README and no task board or competing claim. Other sessions then merged PRs #1, #2, #6, #8, #10 and subsequent changes into `main`; this session fetched and preserved those changes.
- Rebasing onto updated `main` exposed shared-file conflicts in `COORDINATION.md`, `README.md` and `.github/workflows/pages.yml`. Conflicts were resolved by retaining the full current-main coordination history, combining README purpose/verification information, and selecting `site/` as the canonical Pages artifact. Earlier root and `docs/` files were not deleted. The current integration is the decision point requested by the shared-task-board protocol.
- The prior `docs/` data includes useful research but also rows marked pending, partial hotel data, and source conflicts. It is not copied into the canonical table without primary-source verification. It remains in the repository for audit and is linked as a prior-research archive, with clear noncanonical status.
- ARIA source recheck: `https://aria.com/en/nightlife.html` currently serves nightlife content, not tournament terms. Current official poker page https://aria.mgmresorts.com/en/casino/poker.html asks guests to call/check @ARIAPoker for whether daily events are running. A separate official guide https://aria.mgmresorts.com/content/dam/MGM/aria/casino/poker/aria-casino-poker-gentlemans-guide.pdf says daily 1 p.m. / nightly 7 p.m. but is undated. The canonical site retains this only as an undated, unconfirmed cadence.

### Current official sources and verification

Checked 2026-11-16. Canonical tournament rows link to venue-controlled schedules or official documents; hotel facts link to official room-rate, fee and tax terms. No third-party calendars substantiate data in `site/data.json`.

- Venetian: https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html and https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament.html. Dated table rows checked; linked official structure PDFs were inspected for the listed one-day, RaceDay, bounty and multi-flight samples. “1Day” is not treated as one-entry proof.
- Wynn: https://www.wynnlasvegas.com/casino/poker, daily poster https://cdn.wynnresorts.com/image/upload/v1752011166/visitwynn_pdfs_files/Poker/Daily%20Tournaments/poker-daily-tournament-poster.pdf, and WPT schedule https://cdn.wynnresorts.com/image/upload/v1757097329/visitwynn_pdfs_files/Poker/WPT/WPT_World_Championship_Schedule.pdf. Rebuy is isolated as extra-spend.
- Bellagio: https://bellagio.mgmresorts.com/en/casino/poker.html and its linked Friday $600 NLH, Saturday NLH, and Sunday $400 H.O.R.S.E. structure PDFs. Friday and Sunday PDFs explicitly allow re-entry and an optional paid staff gratuity that adds chips; these are in the spend-more section. Saturday source conflicts are flagged. Hotel room page https://bellagio.mgmresorts.com/en/hotel.html gives room classes but no date-specific quote; hotel terms https://bellagio.mgmresorts.com/en/terms-and-conditions.html publish a $55 daily resort fee plus applicable tax and state lodging tax applies to both rate and resort fee.
- Venetian hotel: https://www.venetianlasvegas.com/resort/casino/poker/suite-rates.html, https://www.venetianlasvegas.com/resort/resort-fee.html, https://www.venetianlasvegas.com/legal/hotel-terms-and-conditions.html. The $119/$209 starting-rate wording is not mapped to individual towers in the reviewed text, so base and all-in totals remain blank. Terms state 13.38% room tax on daily rate and $55 + applicable tax resort fee.
- Wynn hotel: https://www.wynnlasvegas.com/rooms-and-suites, general terms https://www.wynnlasvegas.com/terms-and-conditions/850070, and an expired 2024 offer page https://www.wynnlasvegas.com/terms-and-conditions/849723. General/current terms reviewed state $55 + tax; expired offer states $50 + tax. The historical discrepancy is flagged; actual booked terms control. Exact room price remains blank.
- ARIA: current poker page and undated official guide URLs above.

Automated checks (rerun after Bellagio hotel/fee integration on 2026-11-16): `python3 scripts/verify_site.py`, `node --check site/assets/app.js`, `python -m json.tool site/data.json`, `git diff --check`; all pass. The verifier reports 40 official-linked tournament rows, 4 hotel rows with blank unquoted totals, and 7 pages with valid local links. It checks official domains, explicit blanks for unknown values, and local links. Earlier local HTTP smoke tests returned 200 for overview, tournaments and JSON data. Bellagio terms confirm a $55 + tax resort fee; nightly room rates/totals remain blank. Entry rules, walking routes, live room confirmation, finish-time scheduling and complete Strip-wide coverage remain flagged.

### Open current-session flags

- Official materials reviewed do not explicitly establish one total entry per player for most candidate rows; no unsupported event is promoted as eligible.
- Wynn Friday rebuy and Bellagio re-entry/optional-gratuity formats stay separate from the strict-entry path.
- Wynn official fee terms include $55 + tax in current/general terms and $50 + tax in an expired 2024 offer; confirm fee on the actual booking.
- Bellagio Saturday NLH source conflict: page/title says $1,000, PDF header says $1,100, and its rule breakdown says $600; no rank assigned.
- ARIA official guide is undated; current page says to confirm daily events.
- Exact hotel totals (including Bellagio), walking minutes, 8 AM start, tournament finish times and full Strip inventory are not established. Hotel quality is not ranked because no common official quality metric was verified.

### Current PR / deployment

- PR #3: [Add official-source Las Vegas poker planning dashboard](https://github.com/karagemop466-tech/Poker3/pull/3), merged 2026-11-16 18:58:24 UTC with merge commit `9238a312132be3c160be1ff58239ff3d20880c61`.
- PR verification workflow [43934330871](https://github.com/karagemop466-tech/Poker3/actions/runs/43934330871) completed successfully before merge.
- Post-merge verification [43934421009](https://github.com/karagemop466-tech/Poker3/actions/runs/43934421009), custom Pages build/deploy [43934421019](https://github.com/karagemop466-tech/Poker3/actions/runs/43934421019), and GitHub Pages deployment run [43934420545](https://github.com/karagemop466-tech/Poker3/actions/runs/43934420545) all completed successfully at commit `9238a31`.
- GitHub Pages API reports `status: built`; published site: https://karagemop466-tech.github.io/Poker3/ (the sandbox cannot fetch `github.io` directly). The configured custom artifact is `site/`.

---

## Session e125b4a2 (Strip planner pages, per-row verified data)

Branch: `arena/e125b4a2-poker3`. This session's files are kept in their own folder so no shared root or `verified/` file is overwritten.

| Task | Status | Owner | Scope | Notes |
|---|---|---|---|---|
| Venetian DSE IV single-entry research (per-row sources) | done | e125b4a2 | `data/tournaments.md` | 44 single-entry events with official structure-sheet links; 9 re-entry rows listed separately. |
| Hotel research and true per-night cost template | done (rates and fees unverified) | e125b4a2 | `data/hotels.md` | Room rates blank and flagged. Resort fees from third-party listings only, flagged. |
| All-day schedule (single entry) | done | e125b4a2 | `data/schedule.md` | 8 AM start not available; earliest verified start 10:10 AM. |
| Executive summary, suggestions, Q&A, flagged-for-review pages | done | e125b4a2 | `planner/*.html`, `pages/*.md` | Suggestions are for review, not implemented. |
| Integration, PR and merge | done | e125b4a2 | this section | PR [#9](https://github.com/karagemop466-tech/Poker3/pull/9) merged to `main` as 91b04ef (`--merge`, 2026-11-16). Pages workflow run 43934665531 success; verify run 43934665612 success; Pages API status `built`. Live URL not checked from the sandbox (github.io unreachable). `planner/` is not deployed: the Pages workflow publishes only `site/`. |

**Placement decision.** Earlier, this branch's HTML pages overwrote shared root pages during a merge. They are now in `planner/`, and root and `verified/` and `docs/` are unchanged by this session.

---

## Session arena/d205f8ec-poker3 (single-entry site in `single-entry/`)

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

- PR: [#5](https://github.com/karagemop466-tech/Poker3/pull/5) (`arena/d205f8ec-poker3` → `main`). **Merged** with a merge commit, `35f8e03`, 2026-11-16 19:02 UTC. Not auto-merged; merged explicitly after a clean mergeability check.
- Pages: workflow "Publish site to GitHub Pages" for `35f8e03`, run [43935075713](https://github.com/karagemop466-tech/Poker3/actions/runs/43935075713): **build and deploy succeeded**. Pages API reports `status: built`, source `main` `/`. Published content is `site/` only (per `.github/workflows/pages.yml`). `single-entry/` is in the repository but is **not** published.
- Follow-up: this record is committed on the branch and merged to `main` as a separate PR. That is the same pattern used by PRs #10 and #12.

**Requests for a user decision (not blocking):**

- **R1.** Publish `single-entry/` on Pages. It needs a change to `.github/workflows/pages.yml` that copies it into the artifact (for example, `cp -r single-entry site/single-entry` before upload). That changes a file owned by the `site/` integration, so it was not made here.
- **R2.** Choose which of the five sites to publish (`site/`, `planner/`, `verified/`, `docs/`, `single-entry/`) and whether to retire the duplicates.
- **R3.** Confirm the single-entry status of each main-list row. No structure sheet prints it, so the rows say "no re-entry or add-on wording on sheet" (flag F1).

**Irregularities** (do not block merge): `single-entry/flagged.html` S1–S8 and the 19-item register from session 93641c21.

## Session `arena/779af4ba-poker3` — source-linked companion dashboard

- Added the Poker3 field guide at `site/poker3/`, keeping the existing canonical `site/` dashboard and its research intact. The current Pages workflow uploads the entire `site/` tree, so the companion is published under `/poker3/` without changing the Pages workflow.
- Includes 25 selected upcoming event starts, 9 room records, 7 hotel records, 7 third-party walk estimates, 60 source records, and 9 review flags. All listed source IDs resolve. No event is verified for one-entry-total/no-re-entry/no-rebuy/no-add-on/no-paid-chip-boost eligibility.
- The Dec. 10–14, 2026, two-adult hotel search is a research sample, not user-provided travel dates. Hotel all-in totals remain unconfirmed; route times remain third-party estimates.
- Planner scenarios use a user-entered time-at-event assumption and are explicitly not verified or guaranteed itineraries. Unknown terms are labeled “Flagged for Review.”
- Checks: `node --check site/poker3/assets/app.js`; `python3 tests/smoke.py`; JSON validation; headless DOM rendering/interaction checks on all eight pages, event filters, the mobile navigation, planner date/scenario controls, and internal links.

## Current session arena/db5ab1d1-poker3 — claim log

- **Claim · 2026-11-16 UTC.** Claimed the integration task above before implementation. Scope is limited to the current published `site/` dashboard, its verification/monitoring code, tests, README, and this board. Historical `docs/`, `planner/`, `verified/`, `single-entry/`, and root-level dashboards are out of scope.
- The board was already present on the current base commit (`e9af34c`); this claim is recorded on the assigned active branch. No parallel task owner was listed as active.
