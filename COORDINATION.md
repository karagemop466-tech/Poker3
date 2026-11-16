# Coordination board

Snapshot: 2026-11-16 UTC.

**Protocol note.** The platform binds each session to one branch. This session works only on `arena/93641c21-poker3`; the `session-<id>/<task>` naming in the brief cannot be applied here. This session is the only active editor, so it acts as the integration owner for every shared output (tournament data, index, navigation, schedule, flags).

| Task | Status | Owner session | Scope | Branch | PR |
|---|---|---|---|---|---|
| Research and build poker-trip dashboard + verification/flag pages (prior session) | done (data gaps remain flagged) | arena session 66708bda | all repository files | `arena/66708bda-poker3` | #1, #2 (merged to `main`) |
| Venetian DeepStack Extravaganza IV main list, schedule, excluded-by-reason tables, hotel template, flagged register, questions (this session) | done. Flagged items published; they do not block merge. | arena session 93641c21 (integration owner) | root site files, README, COORDINATION (shared outputs) | `arena/93641c21-poker3` | [#6](https://github.com/karagemop466-tech/Poker3/pull/6), merged |

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

- Added the Poker3 field guide at `site/poker3/`, keeping the existing canonical `site/` dashboard and its research intact. The Pages API currently reports legacy publishing from `main` `/`, so the live path is `/site/poker3/`; the existing Actions artifact would publish the same directory at `/poker3/` if that source is enabled. No Pages setting was changed.
- PR [#16](https://github.com/karagemop466-tech/Poker3/pull/16) merged as `e9af34c`. The site workflow and legacy Pages deployment both completed successfully (runs `43937059855` and `43937059073`); the live content at `/site/poker3/` was fetched and verified.
- Includes 25 selected upcoming event starts, 9 room records, 7 hotel records, 7 third-party walk estimates, 60 source records, and 9 review flags. All listed source IDs resolve. No event is verified for one-entry-total/no-re-entry/no-rebuy/no-add-on/no-paid-chip-boost eligibility.
- The Dec. 10–14, 2026, two-adult hotel search is a research sample, not user-provided travel dates. Hotel all-in totals remain unconfirmed; route times remain third-party estimates.
- Planner scenarios use a user-entered time-at-event assumption and are explicitly not verified or guaranteed itineraries. Unknown terms are labeled “Flagged for Review.”
- Checks: `node --check site/poker3/assets/app.js`; `python3 tests/smoke.py`; JSON validation; headless DOM rendering/interaction checks on all eight pages, event filters, the mobile navigation, planner date/scenario controls, and internal links.

## Current session `arena/e58b73b1-poker3` — trip estimate and source-change monitor

| Task | Status | Owner session | Scope | Branch | Notes |
|---|---|---|---|---|---|
| Add scenario trip-cost calculator, dated hotel-rate observations, and scheduled official-source change checks | done; first live baseline completed (7 official URLs unavailable) | `arena/e58b73b1-poker3` | `site/poker3/assets/app.js`, `site/poker3/assets/app.css`, `site/poker3/data/research.json`, `site/poker3/data/source-monitor.json`, `scripts/check_sources.py`, `.github/workflows/source-monitor.yml`, `.github/workflows/verify.yml`, `tests/**`, `COORDINATION.md` | `arena/e58b73b1-poker3` | 52 official URLs checked; 0 changed; 7 unavailable (timeouts or HTTP 403) remain flagged. No new tournament/hotel values inferred. |

### Implementation and verification — session `arena/e58b73b1-poker3`

- Added an interactive trip-cost scenario to `site/poker3/plan.html` (rendered from the shared app): `entries × buy-in + nights × ((nightly room rate + nightly mandatory resort fee) × (1 + tax rate))`. The 13.38% tax is a clearly labeled user-requested assumption, not re-verified tax advice. Missing values stay blank; event buy-ins may be prefilled from the existing source-backed catalog, but eligibility remains unverified unless the event row says otherwise.
- Replaced hotel `sampleRate` single-value fields with `rateHistory` arrays. Existing Horseshoe dated sample observation is recorded with its official booking source and conflicting fee presentation; checkout total, tax, parking, cancellation deadline, and exact rate timestamp remain blank because the existing official-page evidence does not establish them. Other hotels have empty rate logs rather than invented quotes.
- Added `scripts/check_sources.py` and `.github/workflows/source-monitor.yml`: daily 13:00 UTC checks of every HTTPS source tagged `official` in `site/poker3/data/research.json`, storing retrieval time, HTTP status, hash, and changed/unchanged/baseline/unavailable result in `site/poker3/data/source-monitor.json`. The scheduled workflow commits the monitor log to `main` and deploys a refreshed Pages artifact. Third-party route sources are deliberately excluded.
- Official-source URLs being monitored are the URLs in the catalog's `sources` records (`kind: official`); no additional event, price, rule, route, or hotel claim was introduced in this session. Existing official references include the Venetian, Wynn/WPT, Caesars/Horseshoe, MGM/Bellagio/ARIA, South Point, Westgate, and Treasure Island sites and PDFs.
- Page-content hash changes are review signals, not proof that a tournament value changed; changed and unavailable sources are visibly marked on rows linked to them. Dynamic/rotating content may create false-positive change signals. Check the linked page manually before changing any event or rate data.
- Verification performed locally: `python3 -m unittest discover -s tests -p 'test_*.py'` (baseline/change/unchanged/fetch-failure cases), `python3 tests/smoke.py` (8 published companion pages, event/source associations, and dated rate-log schema), `node --check site/poker3/assets/app.js`, `python3 -m json.tool` for both JSON files, `python3 scripts/verify_site.py`, `python3 -m py_compile scripts/check_sources.py`, and `git diff --check` all passed. The first live monitor run is recorded below.
- **Open review item:** seven official URLs were unavailable during the initial run (six timeouts, one HTTP 403); these are marked unavailable per source, not treated as unchanged or verified. Check again on the next daily run.
- PR [#18](https://github.com/karagemop466-tech/Poker3/pull/18) merged into `main` on 2026-11-16 19:20 UTC as `c694fe1`; the ordinary Pages build/deploy workflow was queued at that commit. A manual `gh workflow run` attempt returned HTTP 403 (`Resource not accessible by integration`), so a `push` path trigger for catalog/monitor/workflow changes is being added to guarantee an initial monitor run after this integration without waiting for the first cron; monitor-log-only commits do not match those paths, preventing recursion.
- Follow-up PR [#19](https://github.com/karagemop466-tech/Poker3/pull/19) added the push-path trigger after workflow dispatch was denied; merged 2026-11-16 19:21 UTC as `b72bedb`.
- Initial live check/deploy: workflow run [43938523153](https://github.com/karagemop466-tech/Poker3/actions/runs/43938523153) succeeded, including Pages deploy. It checked 52 official URLs at `2026-11-16T19:22:25Z`: 45 first-baseline fetches, 7 unavailable, 0 content changes. Unavailable: `aria-fee`, `aria-poker`, `bellagio-fee`, `bellagio-poker`, `mgm-fee`, `mgm-poker` (read timeouts), and `golden-nugget` (HTTP 403). See `site/poker3/data/source-monitor.json` for all per-source results and exact errors. Pages API reports `built`, source `main` `/`.
- Row-level official source links now show the last-check UTC timestamp and distinguish changed pages from unavailable checks. The timestamp is a retrieval time, not a claim that every event's terms were re-reviewed by a human.
- PR [#20](https://github.com/karagemop466-tech/Poker3/pull/20) merged 2026-11-16 19:25 UTC as `5e72fb2`. Pages build/deploy run [43939158118](https://github.com/karagemop466-tech/Poker3/actions/runs/43939158118) completed successfully. The current Pages API reports `built` from `main` `/` at https://karagemop466-tech.github.io/Poker3/.
## Session `arena/62cea180-poker3` — current integration owner (2026-11-16 UTC)

Branch: `arena/62cea180-poker3`, created from `origin/main` at e9af34c. This session is the only active editor and acts as the integration owner for the shared `site/` dashboard and its data files.

| Task | Status | Owner session | Scope | Branch | PR |
|---|---|---|---|---|---|
| Trip cost calculator (entries × buy-ins + nights × true hotel cost) | done | 62cea180 | site/calculator.html, site/assets/app.js | arena/62cea180-poker3 | — |
| Search box across all tables | done | 62cea180 | site/assets/app.js table filters | arena/62cea180-poker3 | — |
| Date filter on tournaments table | done | 62cea180 | site/tournaments.html, site/assets/app.js | arena/62cea180-poker3 | — |
| Single-entry / freezeout toggle filter | done | 62cea180 | site/tournaments.html, site/assets/app.js | arena/62cea180-poker3 | — |
| Venue pages: Venetian, Wynn, others (events + hotels per venue) | done | 62cea180 | site/venues/*.html | arena/62cea180-poker3 | — |
| "Last checked" date on every row | done | 62cea180 | site/data.json rows + table render | arena/62cea180-poker3 | — |
| Structured rule fields per event (single-entry / re-entry / add-on / fee, each with source excerpt + retrieval date) | done | 62cea180 | site/data.json tournament `rules` blocks | arena/62cea180-poker3 | — |
| Hotel rates kept as a dated log (not a single value) | done | 62cea180 | site/data.json hotels `rateLog` | arena/62cea180-poker3 | — |
| Schedule overlap flags (start time + plausible duration; primary + fallback per day) | done | 62cea180 | site/data.json `overlapNote`, site/schedule.html | arena/62cea180-poker3 | — |
| Guarantee ÷ entry fee descriptive ratio (not a forecast); bounty/flight rows labelled separately | done | 62cea180 | site/data.json, tournaments table render | arena/62cea180-poker3 | — |
| Change monitoring: scheduled re-check of each official URL; flag rows whose source changed | done | 62cea180 | scripts/monitor_sources.py, .github/workflows/monitor.yml, data/source-checks.json | arena/62cea180-poker3 | — |
| Verification, tests, PR, merge, GitHub Pages deploy confirmation | done | 62cea180 | scripts/verify_site.py, tests/smoke.py, repo-wide links | arena/62cea180-poker3 | — |

**Scope protocol.** Each session edits only its claimed scope. Shared outputs (`site/index.html`, navigation, `site/data.json`, `site/assets/*`, pages, `COORDINATION.md`) are changed only on this integration branch. If a task needs a file claimed by another session, the request is logged here instead of editing it directly.

**Source-currency policy (this session).** No tournament row is labelled "single entry" or "freezeout confirmed": the reviewed official structure sheets do not print an entry cap, so the structured rule fields carry blank values flagged unverified with retrieval date 2026-11-16. No hotel all-in total is asserted: `trueNightly` stays blank and rates are kept as a dated log (`rateLog`), not a single value. External re-verification of venue pages is handled by the scheduled monitor workflow; this session's local content relies on the 2026-11-16 official-source snapshot recorded in earlier sessions' work logs.

**Irregularities carried forward (do not block merge; published on Flagged for review):** single-entry status unresolved on all candidates; hotel true cost blank; 8 AM start unverified; walking times unverified; Wynn WPT and Bellagio source conflicts logged.

### Work log (session 62cea180)

- **2026-11-16 · Claim.** Recorded this claim on `arena/62cea180-poker3` before feature work. Branch is even with `origin/main` (e9af34c).

- **2026-11-16 · Integration.** PR #22 (`arena/62cea180-poker3` → `main`), merged with `gh pr merge 22 --merge` as merge commit `2733c0e`. Pages workflow "Publish integrated Vegas Poker Planner to GitHub Pages" run 43940338076: success; Pages API reports `status: built`, source `main` `/`. Verify workflow also passed. Live site: https://karagemop466-tech.github.io/Poker3/ (root `site/` tree), plus `/poker3/` companion from prior sessions.
- No values were inferred: single-entry status remains unresolved on all candidates (blank rule fields flagged unverified), `trueNightly` stays blank, rates are a dated log (`rateLog`), walking times unverified — all published on Flagged for review with source links.

## Session `arena/aa084881-poker3` — handoff (2026-11-16 UTC)

- **Outcome.** The consolidated rebuild (`site/`) is **not merged**. Session `arena/62cea180-poker3` merged its own integrated site to `main` (PRs #22 and #24) and is the current integration owner for `site/`, `site/data.json`, `scripts/verify_site.py`, and navigation. Merging this session's full site would overwrite that deployed site and break its verifier schema. This is a protocol conflict, not a verification failure: the rebuild passed its own checks.
- **Handoff location.** `handoff/aa084881/` (not published): `site_data.py` (every value with its official URL), `build_site.py` (generator), `verify_site.py` (checks), `data.json` (generated), and `README.md` (what to import, what was not verified).
- **Requests to integration owner `62cea180` (logged, not edited here).**
  1. Import the full official Venetian DeepStack IV table (64 event numbers, classified in `handoff/aa084881/site_data.py`).
  2. Show the Venetian Nov 17-19, 2026 quote ($1,245.48 checkout; tax $146.98) as the only dated hotel total, and log the calendar conflict (F12).
  3. Keep Bellagio Saturday's buy-in conflict ($1,000 page / $1,100 PDF / $600 rule body), Friday re-entry, and the Sunday structure as unread (F19-F22).
  4. Keep Wynn terms as an expired offer (F24) and Dec 18 weekday conflict open (F26).
  5. Do not present the ARIA undated cadence rows as verified. The ARIA guide was not read in this session.
- **Cross-session request (unchanged).** Extend the daily monitor (`.github/workflows/source-monitor.yml` + `scripts/monitor_sources.py`, owner 62cea180 / e58b73b1) to the Venetian DSE, Wynn, Bellagio and ARIA official URLs in `handoff/aa084881/site_data.py` (`MONITOR_SOURCES`). This session did not edit either file.
- **Branch and PR.** Branch `arena/aa084881-poker3` now holds only this handoff (on top of `origin/main`). The earlier site commits were replaced by this handoff, so the branch no longer carries a site rebuild. A force-with-lease push was used on this session's own branch.
---

## Current session `arena/ed88c788-poker3` — final integration and republication

Branch: `arena/ed88c788-poker3` (base `main` at `e9af34c`). This session is the only active editor, so it
takes the integration-owner role for every shared output: the canonical `site/` artifact, the combined data
set, navigation, the schedule plan, the flag register and the source log. No other session holds a live claim
on this branch, so the scope below is non-overlapping.

| Task | Status | Owner session | Scope | Files | Notes |
|---|---|---|---|---|---|
| Source-data modules for the canonical set | in progress | arena/ed88c788-poker3 | new source modules | `scripts/data_venetian.py`, `scripts/data_venues.py`, `scripts/data_hotels.py`, `scripts/data_source.py` | Builds `site/data.json` from official-source rows only. Every row keeps its official URL and the 2026-11-16 retrieval date. |
| Canonical rebuild of `site/` | in progress | arena/ed88c788-poker3 | canonical Pages artifact | `site/index.html`, `site/tournaments.html`, `site/hotels.html`, `site/schedule.html`, `site/questions.html`, `site/suggestions.html`, `site/flagged.html`, `site/sources.html`, `site/browse.html`, `site/assets/app.js`, `site/assets/site.css`, `site/data.json` | Replaces the superseded 40-row snapshot with the verified set. |
| Automated re-check + morning daily feed | in progress | arena/ed88c788-poker3 | automation | `scripts/check_sources.py`, `scripts/daily_feed.py`, `.github/workflows/checks.yml`, `site/checks.json`, `site/feed/**` | Scheduled URL re-check with content hashes and changed-value flags; daily per-room schedule feed. |
| Verification, PR, merge, deployment | pending | arena/ed88c788-poker3 | whole repo | `scripts/verify_site.py`, `tests/`, this section | Line-by-line re-verification, no broken links, PR to `main`, explicit merge, deployment confirmation recorded here. |

### Claim record (this session)

- **Claimed:** `site/**` (canonical artifact), `scripts/data_*.py`, `scripts/data_source.py`,
  `scripts/verify_site.py`, `scripts/check_sources.py`, `scripts/daily_feed.py`, `tests/**`,
  `.github/workflows/**`, `research/structure_notes.md`, `README.md`, `COORDINATION.md`.
- **Not claimed, not edited:** `docs/`, `verified/`, `planner/`, `single-entry/`, `pages/`, root-level HTML
  pages from earlier sessions, `raw/`, `data/`. They stay in the repository as prior research artefacts.
- **Cross-file requests:** none. No other session is active, so no edit is made to another session's files.
- **Commit discipline:** small, frequent commits; `git pull --rebase origin arena/ed88c788-poker3` before every push.

### Source position at claim time

- All 37 official DSE IV structure PDFs read directly on 2026-11-16 (`research/structure_notes.md`, commit `8ba5967`).
- Official DSE IV schedule (64 rows), DSE NYE schedule, Wynn daily poster and structures, Wynn WPT schedule,
  Wynn Signature Series schedule, Bellagio Friday/Saturday/Sunday PDFs, MGM Grand $120 structure and weekly
  sheet, Caesars/Horseshoe tournament page, ARIA guide, and the Venetian/Wynn/Bellagio hotel terms pages.
- Google Maps walking estimates captured 2026-11-16 for the hotel-to-Venetian routes; they are labelled as
  estimates because no venue publishes a walking time.

### Standing constraints honoured

- No value is inferred. Anything not confirmed from an official source stays blank and is listed on
  `site/flagged.html` with a link for manual review.
- The guaranteed-pool ÷ entry-fee figure is shown as a descriptive ratio only, never as a forecast.
- Bounty, multi-flight and satellite formats are labelled separately from the single-entry list.
- Trip dates, nightly budget and quality floor are fixed by this session rather than asked for, and the
  reasoning is published.

### Work log (session arena/ed88c788-poker3)

**Canonical rebuild.** `site/` was rebuilt from the source modules instead of being patched row by row. The data now
carries 341 tournament rows, 8 hotel rows, 14 walking-route rows, 27 official sources, 27 flags, 12 questions, 12
suggestions, a fixed trip profile, an eight-day plan and the flagged impossible sequences.

| Page | Content |
|---|---|
| `site/index.html` | Executive summary, the fixed trip, the primary event per day, what is confirmed and what is not. |
| `site/tournaments.html` | Every row with date from/to, venue, category, format and single-entry filters, a search box and a per-row rule panel carrying the excerpt, the source link and the retrieval date. |
| `site/venues.html` | Seven Strip poker rooms; each opens `browse.html?view=venue&key=…` with its events and its hotels. |
| `site/browse.html` | Venue and category subpages so bounty, flight, satellite and extra-spend rows are never mixed in with plain freezeouts. |
| `site/schedule.html` | One primary event per day, a conditional fallback with its reason, the recurring room events for that weekday, and the flagged impossible sequences. |
| `site/hotels.html` | Published rate components, mandatory resort fee, tax, true cost per night, parking, cancellation deadline, walking times, the cost calculator and the dated rate log. |
| `site/questions.html` | Twelve decision questions, each with the official source behind the answer. |
| `site/suggestions.html` | Twelve improvements with impact, effort and the decision each one needs. |
| `site/flagged.html` | 27 irregularities and unverified items, each with a link for manual review. |
| `site/sources.html` | The official source log, the 52 structure sheets with read status, the morning feed sources and the automated re-check output. |

**Decisions fixed by this session, as instructed, without asking.**

- Trip: 2026-11-25 to 2026-12-02, seven nights, on the Venetian / Palazzo resort. It is the eight-day window with the
  most single-entry events verified on an official structure sheet (14) and at least one on every day.
- Nightly budget: $197.28, the floor computed from the published components ($119 published starting rate + $55
  mandatory resort fee, then 13.38% Clark County room tax). It is labelled a floor, not a quote.
- Quality floor: no comparable official quality score exists, so the quality column stays blank and the floor is an
  evidence test instead: the property must publish its own poker-room rate, keep the poker room on site and publish
  its fee, tax and cancellation terms.
- Bankroll: the eight recommended entries total $2,800 in buy-ins; with a 25% buffer, $3,500.

**Line-by-line verification (this session).**

- `scripts/audit_data.py` parses `research/structure_notes.md`, the read log for all 37 DSE IV structure PDFs, and
  compares every buy-in, rake, prize-pool share, chip count, level length, late-registration line and guarantee with
  the canonical data. It also checks that every scheduled DSE row points at a sheet that was read, that the event name
  starts with that sheet's buy-in and that the flight categorisation matches the sheet. The audit caught one real
  error, now fixed: sheet 4 (event 59) was carrying a $400 buy-in instead of the $600 printed on the sheet.
- The DSE IV schedule was re-read and all 64 rows match the official page on date, time, event number, name and
  structure-sheet link.
- The DSE NYE schedule was re-read and all 49 rows match the official page.
- The Wynn WPT schedule PDF was re-read: 136 rows, and the per-date row counts match the PDF exactly for all 24 dates.
- The Wynn Signature Series PDF was re-read: 38 rows, all matched, and the guarantee column now carries the printed
  seat counts for the milestone satellites.
- The Wynn daily structures PDF was re-read: the $200 Monday-Thursday ($10,000 guarantee), $240 Friday rebuy
  ($40,000), $200 Saturday-Sunday ($25,000) and $160 nightly ($10,000) terms, fee splits, chip counts, add-on chip
  amounts, level lengths and registration cut-offs all match the canonical rows.
- `scripts/verify_site.py` checks the canonical data and every published page: official-domain source links on every
  row and every rule excerpt, a retrieval date on every excerpt, an explanation for every blank fee or guarantee, the
  arithmetic behind each true nightly cost, a source on every flag, the single-entry rule behind every recommended
  primary event, and every local link in every page.
- `tests/canonical_smoke.py` plus `tests/canonical_render.js` render all ten pages headlessly and confirm each one
  produces content, including 143 tournament rows on the default filter.

**New findings from the second verification pass, added to the flag register.**

- F23 the Ladies Championship entry fee is printed twice, differently ($1,100 in the column, $11,100 in the footnote).
- F24 the "$1,000,000 Added" on the WPT World Championship comes from ClubWPT Gold, which is not available in Nevada.
- F25 the discounted-entry footnote markers do not resolve cleanly against the footnote list.
- F26 three Wynn Signature Series rows carry an extra empty cell that shifts the guarantee column.
- F27 the DSE schedule page misspells "Limit" on four rows.

**Automation added.**

- `scripts/check_sources.py` fetches every official URL behind the dashboard, stores a SHA-256 of the response and
  flags any source whose body changed. It never changes a tournament value on its own: a changed page is re-read by a
  human first. Output: `site/checks.json`, shown on the sources page.
- `scripts/daily_feed.py` pulls the schedule page of each Strip poker room every morning and writes a dated snapshot
  under `site/feed/`, so a morning run can be compared with the previous morning instead of replacing it.
- `.github/workflows/checks.yml` runs both at 05:00 Pacific daily and commits the results when they change.
- `.github/workflows/verify.yml` now runs the canonical verifier, the canonical smoke test, the JSON checks, the
  JavaScript syntax checks and a rebuild of `site/data.json` to prove the published data is reproducible.

**Environment note.** The sandbox cannot open HTTPS connections to the venue hosts, so `scripts/check_sources.py`
and `scripts/daily_feed.py` report "unreachable" here and are designed to run on the GitHub Actions runner. The
scripts handle a failed fetch without aborting and record the status instead.

**Cross-session note.** `site/poker3/` is a companion dashboard from a merged prior session. It still publishes at
`/poker3/` because it lives inside the Pages artifact, and its conclusions predate this build: it records no verified
strict-entry event, while this build verifies 45 dated rows whose sheets print one buy-in, one start flight and no
re-entry, rebuy or add-on clause. It is an archive, not the current data. The other prior dashboards (`docs/`,
`verified/`, `planner/`, `single-entry/`, the root pages) are untouched.

### Integration with the other sessions' work (this session)

`main` advanced while this session was building: session `arena/62cea180-poker3` published an integrated site (PRs #22
and #24), session `arena/e58b73b1-poker3` added a trip-cost calculator and a source-change monitor, and session
`arena/aa084881-poker3` handed off a verified dataset in `handoff/aa084881/`. The canonical rebuild was merged with
`main` rather than over it, and the following decisions were taken:

- **Canonical data and pages.** `site/data.json`, `site/assets/app.js`, `site/index.html`, `site/tournaments.html` and
  `scripts/verify_site.py` are this session's versions: 341 rows read line by line from the official sources, with the
  audit script and the rule excerpts attached. The earlier 40-row snapshot is replaced, not merged.
- **Kept and adapted.** The calculator (`site/calculator.html`), the detailed venue pages (`site/venues/`), the
  companion source monitor (`scripts/check_sources_poker3.py`, renamed from `scripts/check_sources.py` so the canonical
  checker keeps that name) and `scripts/monitor_sources.py` are all kept. `site/assets/venue.js` was rewritten against
  the canonical data model, and `scripts/monitor_sources.py` now reads the canonical `sources` section and the
  canonical row fields. Their copy was corrected where it claimed that no row can be labelled single entry: that
  statement was true before the 37 structure sheets were read, and the sheets now in the data say otherwise.
- **Deployment race removed.** `source-monitor.yml` no longer uploads and deploys the Pages artifact; only
  `.github/workflows/pages.yml` publishes, so the two workflows cannot cancel each other.
- **Dated hotel quote imported and re-verified.** The handoff recorded one dated official total for The Venetian,
  November 17-19, 2026, two adults. This session opened the venue's own booking engine again and confirmed it: $824.25
  + $55 on the 17th, $164.25 + $55 on the 18th, $146.98 of tax, $1,245.48 total, average rate $549.25, for a 650 sq ft
  "Newly Remodeled Luxury King" suite. It is now in the canonical rate log and on the hotels page, with the calendar
  disagreement recorded as F28. The booking engine publishes no price at all for the recommended trip window of
  November 25 to December 2, 2026, so the nightly budget stays at the published starting-rate floor and is labelled a
  floor rather than a quote.
- **Not merged.** PR #7 (session `arena/92941c56-poker3`, a separate `pages/` site) is left open and untouched; it
  overlaps the root pages and is another session's work to decide on.

### Result (session arena/ed88c788-poker3)

- **PR [#25](https://github.com/karagemop466-tech/Poker3/pull/25)**, `arena/ed88c788-poker3` → `main`, merged
  2026-11-16 19:43:01 UTC with `gh pr merge 25 --merge` (merge commit `84e0c16`). It replaced the earlier 40-row
  canonical snapshot with the verified 341-row build, merged the other sessions' venue pages, calculator and monitors,
  and imported the dated Venetian booking-engine quote.
- **Verification before the merge:** `python3 scripts/verify_site.py` (341 events, 8 hotels, 14 routes, 27 sources,
  28 flags, 8 plan days, 15 pages, all links resolved), `python3 scripts/audit_data.py` (all 37 DSE IV structure
  sheets match the read log), `python3 tests/canonical_smoke.py` (10 main pages and 5 detail pages render),
  `python3 tests/smoke.py` (the Poker3 companion), `python3 -m unittest discover -s tests` (the source-monitor
  tests), `node --check` on both client scripts and a local HTTP check of all 19 published files.
- **CI on the branch:** the `verify` workflow run [43942078713](https://github.com/karagemop466-tech/Poker3/actions/runs/43942078713)
  completed successfully for the merged head.
- **Pages:** the Pages workflow run [43942226904](https://github.com/karagemop466-tech/Poker3/actions/runs/43942226904)
  and the legacy deployment run [43942226549](https://github.com/karagemop466-tech/Poker3/actions/runs/43942226549)
  both completed successfully; the Pages API reports `status: built`.
- **Live:** the canonical dashboard is published at https://karagemop466-tech.github.io/Poker3/site/ and was fetched
  and read back after the deployment: 341 published rows, 45 single-entry rows verified on the official sheets, the
  fixed 2026-11-25 → 2026-12-02 trip and the eight-day plan are all present. The repository root is still published
  by the legacy branch deployment, so a follow-up workflow change re-runs the Actions deployment after the legacy job
  and puts the canonical artifact at the site root as well.
- **Open cross-session item (not blocking):** PR [#7](https://github.com/karagemop466-tech/Poker3/pull/7) from
  `arena/92941c56-poker3` is still open and touches the root `index.html` and `pages/`. It was left untouched. If it
  is merged later it will need a rebase, and the root `index.html` will then hold that session's earlier snapshot
  rather than the canonical dashboard.


---

## Session `arena/ef37b79e-poker3` — full structure-sheet verification + canonical `site/` rebuild

Branch: `arena/ef37b79e-poker3` (branched from `main` @ `e9af34c`, PR #16). **Platform deviation:** the brief's `session-<id>/<task>` branch naming is unavailable in this environment; the Arena session branch name is used instead. This session edited only `data/`, `scripts/`, `site/` (canonical dashboard + new data pages), `.github/workflows/daily-check.yml`, `scripts/verify_site.py`, and this section of `COORDINATION.md`. Prior artifacts (`docs/`, `planner/`, `verified/`, `single-entry/`, root `*.html`, `raw/`, `pages/`) were read but not modified.

| Task | Status | Owner | Scope | Notes |
|---|---|---|---|---|
| Read every Venetian DSE IV structure sheet line-by-line | done | ef37b79e | `data/sheet_extracts.jsonl`, `scripts/build_data.py` | All 37 sheets (dse_nov_2026-structure_1..37.pdf) read 2026-11-16: fee splits, stacks, level lengths, late-reg cut-offs, guarantees, payout %, bounty amounts, entry clauses. |
| Remove unverified labels where confirmed; keep blanks+flags elsewhere | done | ef37b79e | `site/data/tournaments.json` | 46 single-start events now carry "verified" with printed fee split; entry status wording is "no re-entry/rebuy/add-on wording on sheet" (never "single entry confirmed" — FL13). |
| Spend-more quarantine (re-entry / rebuys / add-ons / paid chip boosts / multi-flight) | done | ef37b79e | same | 48 rows in a separate bucket with the exact clause quoted (Wynn dailies + WPT festival + Bellagio weeklies + Venetian multi-flight). |
| Hotel true-cost + dated rate log + booking links | done (rates blank+flagged) | ef37b79e | `site/data/hotels.json`, `rates.json` | Formula: rate + resort fee + 13.38% tax (tax on rate and fee per Bellagio terms; Venetian terms state 13.38% Clark County room tax). Venetian/Palazzo poker-suite starting rates $119/$209 logged as dated observations, not date-mapped. |
| Walking-route check (official addresses + 30-min filter + map links) | done (times blank+flagged FL08) | ef37b79e | `site/data/routes.json`, `site/routes.html` | Official addresses for all pairs; Google Maps walking links per pair for verification; minutes never guessed. |
| Day plan (primary + conditional fallback, overlap flags) | done | ef37b79e | `site/schedule.html` | Overlap flags from start time + late-reg + structure-derived duration (estimates labelled, FL14). No verified 8 AM start exists (FL12); earliest regular start 10:10 AM. |
| Trip-cost calculator, per-venue pages, workflow, monitoring, questions/answers, suggestions, flagged page | done | ef37b79e | `site/*.html`, `site/assets/` | 18 pages; search box across all tables; date filter; single-entry toggle; descriptive ratio column (never a forecast). |
| Scheduled automatic re-check marking changed sources | done | ef37b79e | `scripts/daily_check.py`, `.github/workflows/daily-check.yml` | 12:05 UTC daily; dated snapshots in `snapshots/<date>/` (30-day retention); `site/data/changes.json` feeds "source changed" badges on the Monitoring page. |
| CI gates | done | ef37b79e | `scripts/verify_site.py`, `.github/workflows/verify.yml` | Official-domain check, fee-split presence for verified rows, ratio consistency, blank-not-fabricated rule, local-link + flag-coverage checks. All green locally. |

### Sources checked this session (2026-11-16, official only)

- Venetian DSE IV web schedule (all 4 chunks) + all 37 linked structure PDFs; schedule PDF parses (`data/venetian_flights.json`, `venetian_restarts.json`) cross-checked against the web schedule.
- Venetian suite-rates, resort-fee and hotel-terms pages (13.38% Clark County room tax; $55 + tax fee; $20/$25/$40 parking; $100 early-departure; poker rate code EPOKR25 with 6h cash or $300+ tournament buy-in per night).
- Wynn poker hub, daily tournament poster PDF, daily structures/terms PDF (all 4 dailies' fee splits + entry clauses), WPT schedule PDF, WPT structures/terms PDF (chunks 0–7: general terms, action clock, and event terms for $600 NLH $400K, TORSE, $400 PLO, Mixed Triple Draw, $800 NLH $1M, Limit O8, O8/Stud8, $1,100 PLO, $1,600 NLH $1M, HORSE, WPT Prime $1,100, $600 Turbo, $1,600 PLO Mystery Bounty), Wynn terms 850070 (fee/parking/cancellation).
- Bellagio poker page + Friday $600 / Saturday NLH / Sunday $400 H.O.R.S.E. PDFs + Bellagio reservation terms (fee/tax/cancellation).
- ARIA poker page (undated cadence; call to confirm) + Horseshoe casino page (6 daily tournament times confirmed, details unpublished). Golden Nugget / Resorts World / Circa / MGM Grand pages not retrievable (FL11).

### Irregularities found (all on `site/flagged.html` with source links; none block merge)

FL01 Bellagio Saturday buy-in three-way conflict ($1,000 link / $1,100 header / $600 breakdown); FL02 WPT $1,100 PLO fee breakdown sums to $1,105 (confirmed current); FL03 sheet 8 "subsequent buy-ins" clause (#18/#58); FL04 Wynn terms page carries an expired offer window; FL05 Bellagio undated "July 26" resume notice; FL06 ARIA undated cadence; FL07 WPT Super Gold Million / $10,400 World Championship entry terms beyond the 30-page PDF fetch limit; FL08 walking times not verified anywhere official; FL09 dated hotel rates/checkout totals blank; FL10 stale "Day 2 (9/13/26)" date in Bellagio Saturday sheet; FL11 four rooms' pages not retrievable; FL12 no verified 8 AM start; FL13 "single entry" is never printed by any venue; FL14 finish-time estimates are structure-derived.

Note: earlier sessions logged a README.md/COORDINATION.md "contents swapped" irregularity; in the current tree the files match their names (README = project overview, COORDINATION.md = this board). No rename needed.

### Merge plan

1. Commit on `arena/ef37b79e-poker3`; `git pull --rebase origin main` before each push.
2. Open PR to `main` with summary, sources and flagged irregularities (file-by-file review in the PR body).
3. Verify the PR check run is green (`verify.yml`: verify_site.py + smoke.py + JSON/JS checks); fix and retry if red.
4. Merge with `gh pr merge <n> --merge` (explicit number, no auto-merge).
5. Confirm GitHub Pages deploy (`pages.yml` uploads `site/`); record the PR link and merge result here in a follow-up commit merged as a second PR (same pattern as PRs #10/#12).

### Result (session `arena/ef37b79e-poker3`)

- PR: [#28](https://github.com/karagemop466-tech/Poker3/pull/28) (`arena/ef37b79e-poker3` → `main`), **merged** with `gh pr merge 28 --merge` on 2026-11-16, merge commit `568e007`. Verify workflow run [43943933823](https://github.com/karagemop466-tech/Poker3/actions/runs/43943933823) passed before merge.
- Pages: "Publish integrated Vegas Poker Planner to GitHub Pages" run [43944032455](https://github.com/karagemop466-tech/Poker3/actions/runs/43944032455) **success**; pages build/deployment run [43944031008](https://github.com/karagemop466-tech/Poker3/actions/runs/43944031008) **success**; Pages API reports `status: built`, source `main` `/`. Live site: https://karagemop466-tech.github.io/Poker3/ (the sandbox cannot reach github.io; deployment confirmed via GitHub API and run status). The verification addendum is published at `/sheets.html`, linked from the nav as "Sheet verification".
- Conflict resolutions logged: merges of `origin/main` into the branch (after PR #25, after PR #26, and after PR #29); each time the integration-owner versions of shared files were kept in full and `COORDINATION.md` was unioned. No other session's content was discarded.
- This record itself is delivered as a follow-up PR merged to `main` (same pattern as PRs #10/#12/#25).

## Session `arena/e1a99371-poker3` — independent structure-sheet verification (handoff)

### Scope collision, and how it was resolved

This branch was created at `e9af34c`, before session `arena/62cea180-poker3` /
`arena/ed88c788-poker3` claimed and merged the canonical site integration
(PRs #22–#26). Both sessions independently built a canonical dashboard covering
the same pages, so the two lines of work overlap.

**Resolution: their canonical site on `main` is kept, unmodified.** It is more
complete (341 events across 7 venues vs my 94 Venetian-only rows), it is already
merged, and its CI passes. My competing generator is preserved unpublished under
`handoff/e1a99371/`, following the convention session `arena/aa084881-poker3`
established with `handoff/aa084881/`. Nothing from the other session was
discarded or overwritten.

### What this session contributes

1. **`raw/dse_nov_2026_structures_page.md`** — a verbatim copy of the official
   Venetian structures/results HTML table, retrieved 2026-11-16, with an explicit
   date for every row and a link to each structure sheet. This is the evidence
   that settles the date question described below, and it is additive: nothing
   else in the repository contains it.
2. **An independent cross-check of the published data** — see the result below.
3. **`handoff/e1a99371/`** — my verified data module (`scripts/poker_data.py`),
   the site generator (`scripts/build_site.py`), its assets, a source monitor and
   the JSON outputs. Unpublished, reproducible with
   `python3 handoff/e1a99371/scripts/build_site.py` (it writes into `site/`, so it
   is deliberately NOT wired into any workflow).

### Verification performed

- All 37 official DSE IV structure sheets read in full on 2026-11-16: every
  buy-in, house fee, prize-pool share, guarantee, starting stack, level duration,
  late-registration window, payout percentage and age restriction.
- **Date authority is the official HTML table, not the schedule PDF.** The PDF's
  DATE column contains non-date banner strings ("@PokerAtlas PRO",
  "@PokerAtlas* TOUR", "LIPS CHAMPIONSHIP CHAMPIES CHAMPIES CHAMPIES",
  "LIPS FRIDAY, DECEMBER 11") where a weekday/date should be. Any date taken from
  PDF row order is therefore an inference. The HTML page gives a full explicit
  date per row. This is recorded because earlier passes dated rows by inference.
- Venetian fee pages verified: $55 + tax/night resort fee; 13.38% Clark County
  Room Tax; $20/day guest self-parking and $40 valet; 3+ hours of poker play =
  free self-parking that day; poker rate from $119/$209 on code EPOKR25 requiring
  6 hours live cash or a $300+ tournament buy-in per night; 3:00 pm check-in,
  11:00 am check-out, $100 + tax early departure; $150/night incidental deposit.
- 18 hotels: Google Maps walking times and distances to the Venetian poker room,
  each with the route URL. Walking queries only return true walking routes with
  the `data=!4m2!4m1!3e2` suffix; the `?travelmode=walking` form silently returns
  driving/transit mixes.

### Cross-check result (the headline number)

My 94 independently-read DSE IV starts were compared field-for-field against the
published `site/data.json` rows, keyed on (date, start time, buy-in):

- **91 of 94 matched on every field compared** (buy-in, guarantee, starting
  chips, level minutes, registration close).
- **0 rows had no counterpart** — every start I read is present.
- **3 rows differ on one field**: events #3, #4 and #5 (sheet 18, RaceDay Stack)
  record level minutes as `20/15` in my read and `20` in the published data. The
  RaceDay sheet steps down from 20-minute to 15-minute levels, so the published
  value captures only the first. Minor, cosmetic, and logged here rather than
  edited, because `site/data.json` is owned by the integration session.

**The published canonical data is therefore confirmed correct against an
independent reading of the official structure sheets.** Dates in particular match
the HTML table, not the inferred PDF ordering.

### Flags this session would add (recorded, not published)

F01 no sheet prints an entry-count rule, so nothing can be called "single entry"
· F02 multi-flight re-entry inferred from "Any player who bags chips for Day 2 may
not play a subsequent flight" · F03 events 18/58 are the only 1Day sheets
referencing subsequent buy-ins and carry a PokerAtlas PRO paid-membership rake
discount · F04 bounty guarantees mix prize pool and bounties · F05 events 3/4/5/6
print no guarantee · F06 no finish time is published for any event · F07 earliest
start is 9:10 AM (a satellite) / 10:10 AM (earliest candidate), never 8:00 AM ·
F08 the schedule PDF's DATE column contains non-date strings · F-H1 no official
page publishes a date-specific rate · F-H2 13.38% verified only on the Venetian's
own page · F-H3 Wynn's fee and terms pages both return 404 · F-H4 Encore routes
6 min longer than Wynn despite being adjacent · F-H5 "The Mirage" no longer
resolves on Google Maps · F-H6 Resorts World route flagged restricted/private ·
F-X2 the monitor had not run a second pass at the time of writing.

### Requests for a user decision (not blocking)

- **R4.** Confirm the single-entry status per event by phone or email —
  `lv_cas_poker@venetianlasvegas.com`, 702.414.7657. Nothing else can be settled
  until this is. No structure sheet prints it.
- **R5.** Retire the duplicate trees (`docs/`, `verified/`, `planner/`,
  `single-entry/`, root-level pages, `site/poker3/`) now that `site/` carries the
  verified data — or say which to keep. `site/poker3/` is still referenced by
  `verify.yml`.
- **R6.** Decide whether to fold the RaceDay level detail (`20/15` for events
  #3/#4/#5) into the published data.

### Checks run on this branch

`python3 scripts/verify_site.py` → verification passed (341 events, 8 hotels,
14 routes, 27 sources, 28 flags, 15 pages) · `python3 tests/canonical_smoke.py` →
passed (10 main pages, 5 detail pages) · `python3 tests/smoke.py` → OK ·
`node --check site/assets/app.js` → OK · `node --check site/poker3/assets/app.js`
→ OK · `python3 scripts/data_source.py` + `git diff --exit-code site/data.json` →
reproducible, no diff.
 (verify: independent cross-check of published DSE IV data against all 37 official structure sheets)

### Result (session `arena/e1a99371-poker3`)

- PR: [#29](https://github.com/karagemop466-tech/Poker3/pull/29) (`arena/e1a99371-poker3` → `main`). **Merged** with a merge commit on 2026-11-16. Checks on the PR: workflow "Verify static research site" **passed** (run [43944160863](https://github.com/karagemop466-tech/Poker3/actions/runs/43944160863)).
- One conflict on rebase: `COORDINATION.md` against session `arena/ef37b79e-poker3`'s record. Resolved by keeping **both** sections in full, in order. No other session's text was removed. Verified afterwards that all five session records (`e1a99371`, `ef37b79e`, `ed88c788`, `62cea180`, `779af4ba`) are still present.
- Pages: workflow "Publish integrated Vegas Poker Planner to GitHub Pages", run [43944299631](https://github.com/karagemop466-tech/Poker3/actions/runs/43944299631): **success**. Pages API reports `status: built`, source `main` `/`, url https://karagemop466-tech.github.io/Poker3/ .
- Overlap with session `arena/ef37b79e-poker3`: that session also read all 37 official structure sheets and shipped its own verification layer (`data/sheet_extracts.jsonl`, `scripts/build_data.py`, `scripts/build_addendum.py`, `site/sheets.html`). My sheet reads were done independently and are preserved as `raw/dse_nov_2026_structures_page.md` (verbatim official HTML table) and under `handoff/e1a99371/`. **Neither session's work was overwritten** — the two are complementary: theirs publishes a per-sheet page, mine cross-checks the published row data.
- Status: **done**. Nothing further is blocked. Outstanding items are the three user decisions recorded above (R4 single-entry confirmation, R5 duplicate-tree retirement, R6 RaceDay level detail).

## Session arena-4fa30832 (canonical `site/` feature completion + automated re-check + final integration)

Branch: `arena/4fa30832-poker3` (platform-bound; the `session-<id>/<task>` naming cannot be applied). This session acts as the **final integration session** for this round: it merges `origin/main`, completes the remaining brief items on the canonical published dashboard (`site/`), re-verifies the combined data line by line, confirms the site builds with no broken links, publishes via PR to `main`, and records the result here. It does not edit `docs/`, `verified/`, `planner/`, `single-entry/`, root-level legacy pages, or `site/poker3/**` (owned by earlier sessions; left untouched).

| Task | Status | Owner | Scope (files) | Notes |
|---|---|---|---|---|
| A1 Trip-cost calculator (entries × buy-ins + nights × true hotel cost) | in progress | arena-4fa30832 | `site/cost-calculator.html`, `site/assets/app.js` | Uses only verified data; blanks shown as blanks. |
| A2 Scheduled automatic re-check of every official URL + mark changed rows | in progress | arena-4fa30832 | `scripts/recheck_urls.py`, `.github/workflows/recheck.yml`, `site/url_hashes.json`, `site/recheck.json` | Daily cron; content-hash diff vs baseline; changed rows flagged on the site. |
| A3 Structure-sheet confirmation → remove "unverified" label where confirmed | in progress | arena-4fa30832 | `site/data.json`, `site/tournaments.html` | Only labels supported by an official sheet excerpt are changed; excerpt + retrieval date stored per row. |
| A4 Last-checked date on every row | in progress | arena-4fa30832 | `site/data.json`, `site/assets/app.js` | `lastChecked` per tournament/hotel/source row. |
| A5 Rates as a dated log (not a single value) | in progress | arena-4fa30832 | `site/data.json`, `site/hotels.html` | `rateLog[]` per hotel; each entry dated with official source. |
| A6 One page per venue (Venetian, Wynn, others) with events + hotels | in progress | arena-4fa30832 | `site/venues/venetian.html`, `site/venues/wynn.html`, `site/venues/others.html` | Generated from `data.json`. |
| A7 Global search box across all tables | in progress | arena-4fa30832 | `site/assets/app.js`, `site/index.html` | Site-wide search over tournaments + hotels. |
| A8 Date selector filter on the tournaments table | in progress | arena-4fa30832 | `site/assets/app.js`, `site/tournaments.html` | Shows only events on chosen day(s). |
| A9 Single-entry / freezeout toggle filter | in progress | arena-4fa30832 | `site/assets/app.js`, `site/tournaments.html` | Toggle + bucket filter; no event is asserted eligible without official wording. |
| A10 Walking-route check links + ≤30 min filter | in progress | arena-4fa30832 | `site/hotels.html`, `site/assets/app.js` | Official-address directions links (Google/Apple Maps) for manual verification; measured times stay blank until verified. |
| A11 Schedule overlap flags (start time + late-reg cutoff + plausible duration) | in progress | arena-4fa30832 | `site/schedule.html`, `site/assets/app.js` | Primary event + conditional fallback per day; estimates labelled as estimates. |
| A12 Structured rule fields (single-entry / re-entry / add-on / fee) with source excerpt + retrieval date | in progress | arena-4fa30832 | `site/data.json`, `site/tournaments.html` | Blank when not published. |
| A13 Final integration: PR → main, merge, confirm Pages, record here | pending | arena-4fa30832 | `COORDINATION.md`, `.github/workflows/*` | Re-verify combined data; do not merge a broken site. |

Claim recorded 2026-11-16 UTC before any file edits in this session.
