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
| A1 Trip-cost calculator (entries × buy-ins + nights × true hotel cost) | done — shipped on main by `arena/62cea180-poker3`; this session's duplicate NOT imported | arena-4fa30832 (built) / 62cea180 (shipped) | `site/calculator.html` (main) | Main's calculator + this session's in-branch `site/cost-calculator.html` both implement the formula; main's richer data (real dated quote) wins. |
| A2 Scheduled automatic re-check of every official URL + mark changed rows | done — shipped on main by `arena/62cea180-poker3` + `arena/e58b73b1-poker3`; this session's duplicate NOT imported | arena-4fa30832 (built) / 62cea180, e58b73b1 (shipped) | `.github/workflows/monitor.yml`, `daily-check.yml`, `source-monitor.yml` (main) | Main already runs scheduled URL re-checks with changed/unavailable marking; this session's `recheck.yml`/`recheck_urls.py` dropped in rebase to avoid a 5th monitor. |
| A3 Structure-sheet confirmation → remove "unverified" label where confirmed | done — outcome: NO sheet prints single-entry wording | arena-4fa30832 | findings recorded below | Independent read of all 37 structure PDFs (2026-11-16): none prints "single entry"/"freezeout"/"no re-entry"/"no add-on"; multi-flight sheets print the bagging-only rule; sheet 8 (events 18/58) prints "All subsequent buy in's after the initial buy in will be $200". Matches main's `structureSheets` read:true×37 and PR #29 cross-check. |
| A4 Last-checked date on every row | done — shipped on main (62cea180) | 62cea180 | `site/data.json` (main) | Main rows carry `lastChecked`; this session's in-branch duplicate dropped. |
| A5 Rates as a dated log | done — shipped on main (62cea180) | 62cea180 | `site/data.json` `rateLog` (main) | Main's log includes the only dated official checkout total (Nov 17–19 quote, F15/F28) — richer than this session's offer-only log. |
| A6 One page per venue (Venetian, Wynn, others) | done — shipped on main (62cea180) | 62cea180 | `site/venues/*.html`, `site/venues.html` (main) | This session's flat `site/venue-*.html` dropped in rebase. |
| A7 Global search box across all tables | done — shipped on main (62cea180) | 62cea180 | `site/tournaments.html`, `site/assets/app.js` (main) | |
| A8 Date selector filter on the tournaments table | done — shipped on main (62cea180) | 62cea180 | `site/tournaments.html` (main) | |
| A9 Single-entry / freezeout toggle filter | done — shipped on main (62cea180) | 62cea180 | `site/tournaments.html` (main) | |
| A10 Walking-route check links + ≤30 min filter | done — shipped on main (62cea180) | 62cea180 | `site/data.json` `routes`, `site/hotels.html` (main) | Main carries Google Maps walking estimates with `walkSourceType` + F21 flag; no venue publishes a walking time. |
| A11 Schedule overlap flags (primary + conditional fallback) | done — shipped on main (62cea180) | 62cea180 | `site/data.json` `dayPlan`/`planConflicts`, `site/schedule.html` (main) | Main precomputes primary/fallback + 39 conflict rows with a disclosed 6-hour session assumption. |
| A12 Structured rule fields with excerpt + retrieval date | done — shipped on main (62cea180/ef37b79e) | 62cea180, ef37b79e | `site/data.json` `events[].rules` (main) | Per-event `rules.singleEntry` excerpt + source + `readOn`; sheet-13 cross-ref error found by ef37b79e (F05). |
| A13 Final integration: PR → main, merge, confirm Pages, record here | done | arena-4fa30832 | `COORDINATION.md` | PR [#33](https://github.com/karagemop466-tech/Poker3/pull/33) merged as `f5013e4`; verify workflow success; Pages workflows success; Pages API `status: built` at https://karagemop466-tech.github.io/Poker3/ ; record PR [#34](https://github.com/karagemop466-tech/Poker3/pull/34). |

Claim recorded 2026-11-16 UTC before any file edits in this session.

### Progress log (2026-11-16, arena-4fa30832)

- **Research (fetch_page, official only):** Venetian DSE HTML schedule (chunks 0–3), Venetian schedule PDF (chunks 0–1, matches `raw/venetian_dse_nov_2026_schedule.md` line-for-line), all **37 structure PDFs**, suite-rates page, Venetian resort-fee + hotel-terms pages, ARIA terms + hotel page, MGM Grand terms + hotel page, TI deluxe-rooms page, Wynn resort-information + homepage + Bellagio hotel page. Contact-us pages for Venetian/Wynn 404 (do not retry).
- **Line-by-line verification:** independent reparse of the raw schedule text == `data/venetian_flights.json` (83 flights) + `data/venetian_restarts.json` (11), zero field mismatches; every flight cross-checked against its structure sheet (buy-in, chips, level, reg-close clock, guarantee) — all asserts pass. The flights-JSON `structure_sheet` field is unreliable (null for 34 events; sheet-1 list conflicts with structure_1.pdf on event 8) — the event↔sheet map must come from sheet headers + HTML per-row links.
- **A3 conclusion (independent):** all 37 sheets read on 2026-11-16 — none prints single-entry/freezeout/no-re-entry/no-add-on wording; multi-flight sheets allow extra flights until bagging; sheet 8 prices subsequent buy-ins at $200 for PokerAtlas PRO members. Agrees with main's sheet registry and PR #29.
- **New irregularities found (for the integration owner — logged, not edited into `site/data.json`, which has a reproducible-build CI check):**
  1. The official schedule PDF prints decorative art/text in the DATE column on **14 rows** ("@PokerAtlas PRO", "@PokerAtlas* TOUR", "LIPS CHAMPIONSHIP CHAMPIES CHAMPIES CHAMPIES", "LIPS FRIDAY, DECEMBER 11"); those dates were confirmed against the official HTML schedule page — consider a flag + `dateSource` note.
  2. The PDF prints "(IDAY)" in several event names (OCR-style typo for "(1Day)").
  3. Wynn parking/valet prices and the 48-hour cancellation wording used as sources come from an offer-specific terms page whose stay deadline was Sept 30, 2025 (expired) — flag severity check.
  4. Tax rate / cancellation remain unpublished on the reviewed ARIA, MGM Grand, Bellagio and Treasure Island pages (their cells must stay blank).
- **Supersession decision (protocol):** while this session worked, integration owner `arena/62cea180-poker3` (PRs #22/#24) plus `ef37b79e` (PRs #26/#28/#29/#30/#32), `e58b73b1` (PRs #18/#19/#20) and `ed88c788` (PR #26) merged a **richer canonical site** to `main`: 341 event rows, 8 hotels with a real dated checkout quote, Google-Maps walk estimates, precomputed day plan + 39 conflict rows, 28 flags, per-event rule excerpts, four monitoring workflows, and a reproducible data build. Per the no-discarding-others'-work rule, this session's parallel build (107-row `site/data.json`, `app.js` rewrite, 12 pages, `recheck` workflow, `build_site_data.py`, `structure_sheets.json`, `app_smoke.mjs`) was **discarded during rebase onto `origin/main`**; only this record is imported. Local CI-equivalent checks on the discarded build had passed before the decision (verify_site, app_smoke, smoke, node --check, HTTP 200 on all pages).
- **Requests to integration owner (logged, not edited):** (a) consider flags for the decorative DATE cells and "(IDAY)" typo above; (b) note this session's independent A3 reading as corroboration; (c) if wanted, `scripts/recheck_urls.py`'s SHA-256 baseline approach can be ported into `monitor.yml` — not imported to avoid duplicate automation.

### A13 integration record (2026-11-16 UTC, arena-4fa30832)

- **PR [#33](https://github.com/karagemop466-tech/Poker3/pull/33)** (`arena/4fa30832-poker3` → `main`): COORDINATION-only (+35 lines; `git diff origin/main..HEAD` before merge showed exactly one file). Merged with `gh pr merge 33 --merge` as merge commit `f5013e4`. CI: "Verify static research site" run 43950194510 → **success** (verify_site 341/8/14/27/28/15, canonical_smoke all pages, node checks, smoke.py, reproducible `data_source.py` build).
- **Pages:** "pages build and deployment" run 43950193086 → success; "Publish integrated Vegas Poker Planner to GitHub Pages" run 43950194425 → success, both at `f5013e4`. GitHub Pages API: `status: built` → https://karagemop466-tech.github.io/Poker3/ (github.io not reachable from this sandbox; confirmed via `gh api .../pages`).
- **Merge result:** no site file changed by this session's PR — the deployed canonical site remains the richer merged build (62cea180/ef37b79e/e58b73b1/ed88c788). Flagged items from this session's research (decorative DATE cells, `(IDAY)` typo, expired-offer sources, unpublished tax rates) are logged above as requests; none blocks the merge.
- This record itself ships in follow-up PR [#34](https://github.com/karagemop466-tech/Poker3/pull/34).

## Session arena/cd17e91c-poker3 — audit of canonical `site/` on `main` (2026-11-17 UTC)

Scope: `COORDINATION.md` only. No `site/**`, `scripts/**`, or workflow file is edited by this session, because those are shared outputs owned by the integration session. Base: `main` at `b30841e`.

| Task | Status | Owner | Scope | Notes |
|---|---|---|---|---|
| Re-verify the shipped canonical site (verify, smoke, reproducible build, Pages status) and log irregularities | done (2026-11-17) | arena/cd17e91c-poker3 | `COORDINATION.md` | Claim committed first (d64ecbb). Results below. No site value changed. |

### Results (2026-11-17 UTC, arena/cd17e91c-poker3)

- **Checks run on `main` at `b30841e`:**
  - `python3 scripts/verify_site.py` → passed (341 events, 8 hotels, 14 routes, 27 sources, 28 flags, 8 plan days, 15 pages).
  - `python3 tests/canonical_smoke.py` → passed (10 main pages, 5 detail pages rendered).
  - `node --check site/assets/app.js` and `python3 -m json.tool site/data.json` → passed.
  - `python3 scripts/data_source.py` re-run → zero diff against the committed `site/data.json`, so the published data reproduces from its source modules.
  - GitHub Pages API: `status: built`, source `main` `/`, https://karagemop466-tech.github.io/Poker3/ . Latest Pages and "Verify static research site" runs on `main` are `success`.
- **8 AM question re-checked against the raw official text (not only the derived JSON):** the earliest verified start on any official schedule is **9:10 AM**, which is Venetian Event #46, a $260 Turbo Milestone Satellite on Dec 12, 2026 (`raw/venetian_dse_nov_2026_schedule.md` line 67; `raw/dse_nov_2026_structures_page.md` line 74; `data.json` id `vl-dse-2026-12-12-46-910am`). Regular events start at 10:00 AM or later. The satellite pays seats, not cash, and is excluded from the main list. No 8:00 AM start is verified, so the 8 AM all-day plan is still not buildable from verified data.
- **Sources:** this session did not fetch new live pages. All values are the existing official-source records from `raw/` and `data.json`, with their retrieval date of 2026-11-16. Nothing here is newly verified.

**Irregularities for the integration owner (logged, not edited, because `site/**` is a shared output):**
1. Wynn daily row name is duplicated: "$200 No Limit Hold'em (Monday-Thursday) (Monday-Thursday)" (`site/data.json` at about lines 8289 and 21017). It likely comes from `scripts/data_venues.py`. Request: remove the duplicate suffix in the generator, then rebuild.
2. The trip window (Nov 25 to Dec 2, 2026) was fixed by an earlier session. The brief asks to "fix trip dates", and no user-supplied dates exist in the repo. Request: confirm the dates with the user before any nonrefundable payment.
3. Open PRs from other sessions still target `main` with overlapping content: #7 (`arena/92941c56-poker3`), #27 (`arena/701f2252-poker3`), #31 (`arena/ea188b20-poker3`). This session did not touch them. Request: the user chooses which, if any, to merge. Merging them could conflict with the canonical site.
4. Only one verified start is before 10:00 AM (the satellite at 9:10 AM). The brief asks for an 8 AM all-day schedule. The site already states this (`site/sheets.html` line 352). Discovery step for the user: ask Horseshoe and Golden Nugget about early daily events, because their times are unpublished.

No `site/**`, `scripts/**`, or workflow file was changed by this session. Two commits are on this branch: the claim (d64ecbb) and this record. PR and merge are recorded below.
- **Merge result (arena/cd17e91c-poker3):** PR [#35](https://github.com/karagemop466-tech/Poker3/pull/35) merged with `gh pr merge 35 --merge` as `be90234` (2026-11-17 UTC). Its `verify` check passed before merge. After merge, "Verify static research site" and "Publish integrated Vegas Poker Planner to GitHub Pages" both succeeded, and "pages build and deployment" succeeded. Pages API: `status: built`. This record ships in a follow-up PR; no further automated record is planned.

## Session arena/a1091d95-poker3 — final verification and publication (2026-11-17 UTC)

Branch: `arena/a1091d95-poker3`, created from `origin/main` at b30841e (merge of PR #34). This session is the only active editor and acts as the integration owner for the canonical `site/` dashboard. It does not edit `docs/`, `verified/`, `planner/`, `single-entry/`, root-level legacy pages, or `site/poker3/**` (prior-session artefacts, left untouched).

| Task | Status | Owner | Scope | Notes |
|---|---|---|---|---|
| F1 Trip-cost calculator (entries × buy-ins + nights × true hotel cost) | done — verified | arena/a1091d95-poker3 | `site/calculator.html` | Formula: entries × buy-in + nights × (rate + resort fee + tax); defaults labelled as defaults, not quotes. |
| F2 Scheduled automatic re-check of every official URL; changed sources flagged | done — verified | arena/a1091d95-poker3 | `.github/workflows/{monitor,daily-check,checks,source-monitor}.yml`, `scripts/{check_sources,daily_check,daily_feed,monitor_sources}.py` | Four scheduled workflows; results in `site/checks.json`, `site/feed/`, `data/source-checks.json`; unavailable URLs flagged, never treated as unchanged. |
| F3 Read every structure sheet; unverified label removed where the sheet confirms | done — verified | arena/a1091d95-poker3 | `site/data.json`, `site/sheets.html`, `research/structure_notes.md` | All 37 DSE IV structure sheets read; no sheet prints "single entry", so rows state "no re-entry/rebuy/add-on printed" with excerpt, source and retrieval date. |
| F4 Last-checked date on every row | done — verified | arena/a1091d95-poker3 | `site/data.json` rows (`lastChecked`), rules (`retrieved`), routes (`lastChecked`), sources (`checked`) | Every tournament row carries `lastChecked: 2026-11-16`. |
| F5 Rates as a dated log, not a single value | done — verified | arena/a1091d95-poker3 | `site/data.json` `rateLog`, `site/hotels.html` | Eight rate-log observations, appended never overwritten; each with observed date, source, fee, tax, quote type. |
| F6 One page per venue (Venetian, Wynn, others) with events and hotels | done — verified | arena/a1091d95-poker3 | `site/venues.html`, `site/venues/{venetian,wynn,others}.html`, `site/browse.html` | Seven Strip rooms; per-venue dated events and hotel cards with official source links. |
| F7 Search box across all tables | done — verified | arena/a1091d95-poker3 | `site/assets/app.js` (`data-search-form`), every page header | Global search filters tournaments; from any page it routes to tournaments.html?q=. |
| F8 Date filter on the tournaments table | done — verified | arena/a1091d95-poker3 | `site/tournaments.html`, `site/assets/app.js` | From/To date selectors plus venue, category, format, single-entry and 30-minute-walk filters. |
| F9 Single-entry / freezeout toggle filter | done — verified | arena/a1091d95-poker3 | `site/tournaments.html` | "Single entry only (verified on the sheet)" checkbox; entry rule panel shows excerpt + source + retrieval date per rule. |
| F10 Walking-route check with ≤30-minute filter | done — verified | arena/a1091d95-poker3 | `site/data.json` `routes`, `site/hotels.html`, tournaments walk column | Official addresses + Google Maps walking links; minutes labelled as estimates; walkOnly filter excludes pairs over 30 minutes. |
| F11 Schedule overlap flags; primary + conditional fallback per day | done — verified | arena/a1091d95-poker3 | `site/data.json` `dayPlan`/`planConflicts`, `site/schedule.html` | Eight-day plan 2026-11-25 → 2026-12-02, one primary single-entry event per day, conditional fallbacks, flagged impossible sequences under a disclosed six-hour session estimate. |
| F12 Guarantee ÷ entry fee ratio, descriptive only; bounty/flight labelled separately | done — verified | arena/a1091d95-poker3 | `site/tournaments.html`, `site/data.json` categories | `ratio` column labelled "descriptive, not a forecast"; category labels separate multi-flight, satellite, bounty/PKO, extra-spend and restricted formats. |
| F13 Executive summary, Q&A, suggestions, flagged-for-review pages | done — verified | arena/a1091d95-poker3 | `site/index.html`, `site/questions.html`, `site/suggestions.html`, `site/flagged.html`, `site/sources.html` | Landing page with trip, stats and day plan; 12 questions, 12 suggestions, 28 flags, official source log and 52 structure sheets — every flag/source linked. |
| F14 Line-by-line verification, PR, merge, Pages deployment confirmation | in progress | arena/a1091d95-poker3 | whole repo | See work log and integration record below. |

### Work log (2026-11-17, arena/a1091d95-poker3)

- **Claim.** Recorded this claim on `arena/a1091d95-poker3` before any edits; branch even with `origin/main` (b30841e).
- **Line-by-line review.** Reviewed `site/data.json` (341 events, 8 hotels, 14 routes, 27 sources, 28 flags), all 15 published pages, `scripts/data_source.py`, `scripts/data_hotels.py`, `scripts/verify_site.py`, `.github/workflows/*`.
- **Irregularity found and fixed.** The dated Venetian rate-log observation (official booking engine, Nov 17–19, 2026, two adults) had its nightly costs swapped: night 1 is $996.91 (($824.25 + $55) × 1.1338) and night 2 is $248.61 (($164.25 + $55) × 1.1338), summing to $1,245.52 against the printed $1,245.48 total. Fixed `scripts/data_hotels.py` (`trueNightlyLow=248.61`, `trueNightlyHigh=996.91`); regenerated `site/data.json`. Also replaced a hardcoded flag count in `site/index.html` ("22 irregularities") with source-linked text (the register carries 28 flags).
- **Verification.** `python3 scripts/verify_site.py` → verification passed (341/8/14/27/28/8/15). `python3 tests/canonical_smoke.py` → all pages render. `node --check` on app.js, venue.js, canonical_render.js → OK. `python3 -m json.tool site/data.json` → valid. `scripts/data_source.py` rebuild is byte-identical (`git diff --exit-code` clean). No value inferred; blanks stay blank and flagged.
- **Official sources honored.** Every table row links its official venue page or PDF; rate log, rules, routes and sources carry retrieval dates; third-party values are not used as evidence.

### GitHub Pages status (pre-merge)

- `gh api repos/karagemop466-tech/Poker3/pages` → `status: built`, source `main` `/`, https://karagemop466-tech.github.io/Poker3/ (the sandbox cannot fetch github.io directly; confirmed via the GitHub API).
- All seven Actions workflows are active.

### Irregularities carried forward (do not block merge; published on site/flagged.html)

- No structure sheet prints single-entry/freezeout wording, so no row is labelled "single entry confirmed"; each row prints what its sheet actually says.
- Hotel true cost for the recommended window (Nov 25 → Dec 2, 2026) is blank: no property publishes a date-specific quote for those dates; the $197.28 nightly figure is a floor computed from published components, not a quote.
- Walking times are Google Maps walking estimates; no venue publishes a walking time.
- Finish times and overlap flags are estimates under the disclosed six-hour session assumption plus 30-minute transfer.
- 28 flags, each with its official source link for manual review.

### Integration record

- **PR:** [#36](https://github.com/karagemop466-tech/Poker3/pull/36) (`arena/a1091d95-poker3` → `main`), merged with `gh pr merge 36 --merge` as merge commit `d9734177bf3a1d42ef6307c1371ed073572e1cd3` on 2026-11-17 UTC.
- **Merge checks:** "Verify static research site" run 43989193008 → success (341 events, 8 hotels, 14 routes, 27 sources, 28 flags, 8 plan days, 15 pages; canonical smoke + node + JSON checks green; `data_source.py` rebuild byte-identical).
- **Pages:** "Publish integrated Vegas Poker Planner to GitHub Pages" run 43989192927 → success; legacy "pages build and deployment" run 43989191223 → success. Pages API: `status: built`, source `main` `/`, https://karagemop466-tech.github.io/Poker3/ — the canonical `site/` dashboard is live.
- **Result:** every brief item is implemented and verified (trip-cost calculator entries × buy-ins + nights × true hotel cost; scheduled official-URL re-check with changed-source flags; all 37 structure sheets read; last-checked date on every row; rates kept as a dated log; one page per venue; global search box; date filter; single-entry/freezeout toggle; walking-route ≤30 min filter; day-plan overlap flags with primary + conditional fallback; descriptive guarantee÷fee ratio; executive summary/Q&A/suggestions; Flagged-for-review page).
- **Irregularities:** 28 flagged items on `site/flagged.html` do not block the merge; each links its official source for manual review, including unresolved single-entry wording on sheets, blank date-specific hotel totals for Nov 25 → Dec 2, 2026, Google Maps walking estimates, and estimated finish times under the disclosed six-hour session assumption.

---

## Session `arena/b1fadb7e-poker3` — final integration session (deployed-site correctness)

Branch: `arena/b1fadb7e-poker3` (platform-bound; `session-<id>/<task>` naming cannot be applied). Reb ranched onto `origin/main` @ `be90234` (PR #35) before any edit. This session acts as the **final integration session** for this round. Scope: `COORDINATION.md`, `README.md`, `scripts/data_venues.py`, `scripts/data_hotels.py`, `site/**` (regenerated data + any page that misstates a value), `site/data.json`, and the GitHub Pages publishing setting. It does **not** edit `docs/`, `planner/`, `single-entry/`, `verified/`, `handoff/`, or root legacy HTML pages.

| Task | Status | Owner | Scope (files) | Notes |
|---|---|---|---|---|
| B1 Verify every Venetian DSE IV row against the verbatim official table | in progress (claimed 2026-11-17) | arena/b1fadb7e-poker3 | `scripts/`, `site/data.json`, `COORDINATION.md` | Claim committed before any other work. |
| B2 Resolve the two competing Pages publishers (stale root vs canonical `site/`) | in progress | arena/b1fadb7e-poker3 | GitHub Pages setting, `site/**` | Root URL currently serves a stale legacy page that contradicts the live dashboard. |
| B3 Prove the scheduled re-check actually operates (or report that it does not) | in progress | arena/b1fadb7e-poker3 | `.github/workflows/checks.yml`, `site/checks.json` | No scheduled run of `checks.yml`/`daily-check.yml`/`monitor.yml` has ever executed; `site/checks.json` (fetched by `app.js`) does not exist. |
| B4 Fix verified generator defects | in progress | arena/b1fadb7e-poker3 | `scripts/data_venues.py`, `scripts/data_hotels.py` | Wynn daily names print their day range twice; rate-log night labels are swapped. |
| B5 Re-verify, PR, merge, confirm Pages deploy | in progress | arena/b1fadb7e-poker3 | `COORDINATION.md` | Not done until the deployed site is confirmed. |

### Findings, fixes and verdicts (2026-11-17, arena/b1fadb7e-poker3)

Everything below was checked in this session against the repository's verbatim copies of the official
pages (`raw/`) and, where reachable, the live official host. Line-by-line results first, then what changed.

#### B1 — Venetian DSE IV rows vs the official table: 94 / 94 agree

An independent re-parse of `raw/dse_nov_2026_structures_page.md` (the verbatim official structures table,
retrieved 2026-11-16) was matched against `site/data.json` on `(date, start time)`:

- 94 official DSE IV rows parsed by date; 94 published rows on or before 2026-12-23.
- **Zero** discrepancies in date, start time or structure-sheet link.
- **Zero** official rows missing from the published set; **zero** duplicate `(date, time)` keys.
- 49 further published Venetian rows are DeepStack NYE (2026-12-24 onwards). They are outside the
  verbatim copy in `raw/`, carry no read structure sheet, and are already flagged (F11).
- The official `dse-nov-2026.html` was re-fetched on 2026-11-17 and its first 24 rows (Nov 16-28) match
  the verbatim copy row for row, including the $200 RaceDay Stack at 10:10 AM and event 8's 5:10 PM PKO.
- Cosmetic only, not a value error: the published names normalise the official typos
  ("No LImit" -> "No Limit", "Event # 39" -> "Event #39") and lower-case the `<br>-` clause.
  Recorded as acceptable; F27 already lists the misspellings.

#### B2 — the published root URL was serving a stale page (fixed)

`https://karagemop466-tech.github.io/Poker3/` returned the **earlier-round** page (46 Venetian rows,
"0 hotels with a verified nightly total", "no hotel ranking is shown"), while
`https://karagemop466-tech.github.io/Poker3/site/` returned the canonical 341-row dashboard. Two
publishers wrote the same URL: Pages source was legacy `main /` and `pages.yml` also deployed `site/`.
The Pages build type cannot be changed by this session's token (`PUT /pages` -> 403), so the fix is
twofold and does not depend on which publisher wins:

1. root `index.html` is now a redirect to `site/index.html` (old content stays in git history);
2. `pages.yml` redeploys the canonical artifact after `pages build and deployment` completes.

#### B3 — nothing was being monitored (fixed)

`checks.yml`, `monitor.yml` and `daily-check.yml` were all scheduled to commit to `main`, under three
different concurrency groups, so the last writer wiped the others; `gh run list` showed **0 runs** for all
three. `site/checks.json`, which `site/assets/app.js` fetches, did not exist either, so the sources page
showed "No automated check file yet". `monitor.yml` and `daily-check.yml` are removed, `checks.yml` is the
single scheduled committer (shared `scheduled-source-review` group, setup-python, rebase-retry push), and
`source-monitor.yml` joins the same group so the two never race. The checker itself was run here: it is
safe (it records hashes, never edits a value, always exits 0). Unreachable hosts in this sandbox are
reported as `unreachable`, which is the correct observation, not a failure.

#### B4 — verified data defects (fixed)

- Wynn daily names printed their day range twice: `$200 No Limit Hold'em (Monday-Thursday)
  (Monday-Thursday)`. `scripts/data_source.py` appended `({days})` to names that already contained the
  range. Fixed at the generator; the fourth daily (`$160 ... Nightly`) still gets its label.
- The dated Venetian quote stored `trueNightlyLow=996.91` / `trueNightlyHigh=248.61`, so the hotels page
  labelled the **worst** night a "nightly floor". Recomputing from the printed lines gives
  (824.25+55) x 1.1338 = **$996.89** and (164.25+55) x 1.1338 = **$248.59**, which add to the printed
  **$1,245.48 exactly**. The stored pair was 2 cents off and its note excused a 4-cent gap that does not
  exist; the gap was arithmetic error in this repository, not venue rounding. Both records corrected.
- The rate-log renderer now prints the pair as "observed nights ... not a price range and not a floor".

#### B5 — PR #31 and PR #27 (open, from earlier sessions): reviewed, not merged

Both branches replace the canonical shared outputs wholesale: each rewrites `site/data.json`,
`site/assets/app.js`, `site/assets/site.css`, `site/index.html`, `site/tournaments.html`,
`scripts/verify_site.py`, `.github/workflows/verify.yml`, `README.md` and this file. PR #31 carries
14,209 added / 499 deleted lines and adds a fifth source monitor; PR #27 carries 42,143 / 851 and a
third `source-monitor.yml`. Merging either would discard the 94/94-verified DSE IV match, the monitor
consolidation and the arithmetic fixes above, and would restore two competing page trees at the same
URLs. Following the no-discarding-others'-work rule they are **left open and unmerged**, with this
verdict recorded. Their useful content is preserved in their own branches. A user decision is requested
below rather than a unilateral merge. PR #7 (an earlier `pages/` site) is unaffected by this round and
stays open for the same reason.

#### B6 — what is still not verified (unchanged, still flagged)

Hotel cost components for MGM Grand, Caesars Palace, Horseshoe and ARIA; date-specific totals for the
trip window; published finish times; any verified start before 9:10 AM; walking times, which no venue
publishes (Google Maps estimates only); the 15 NYE and the WPT structure sheets that were not read. Each
is on `site/flagged.html` with a source link, and none of them blocks this merge.

#### Checks run before the pull request

`scripts/verify_site.py` (341 events / 8 hotels / 14 routes / 27 sources / 30 flags / 8 plan days /
15 pages), `tests/canonical_smoke.py` (10 main + 5 detail pages rendered), `tests/smoke.py`,
`node --check` on every published script, `python3 -m json.tool` on `site/data.json`,
`python3 -m unittest discover -s tests` (10 tests, including the new `tests/test_integrity.py`), and a
reproducible `scripts/data_source.py` rebuild with no diff.
## Current session `arena/b2a8d36b-poker3` — audit and completion pass (2026-11-17 UTC)

| Task | Status | Owner | Scope | Notes |
|---|---|---|---|---|
| Audit canonical dashboard and automation against the user brief; fix demonstrable defects and flag evidence gaps | done (source snapshot is 2026-11-16; unresolved evidence remains flagged) | arena/b2a8d36b-poker3 | `site/**`, `scripts/**`, `.github/workflows/**`, `tests/**`, `README.md`, this section | Added strict written-entry confirmation filter, sheet-candidate distinction, row-level source-change/unavailable badges, last-checked display, and cross-table search. |
| Final verification, PR, merge, Pages confirmation | pending | arena/b2a8d36b-poker3 | integration | Do not merge unless checks pass and the canonical site is intact. |

### Claim record

- Claimed 2026-11-17 UTC. Scope: canonical `site/`, build/monitor/verification scripts, workflows, tests, README and this log. Legacy/parallel artefacts (`docs/`, `verified/`, `planner/`, `single-entry/`, root-level pages, `site/poker3/`) are read-only unless a specific cross-file request is logged.
- The branch naming protocol in the brief cannot be applied because Arena binds this session to `arena/b2a8d36b-poker3`. This branch started at `b30841e`; after PR #38 merged as `739b301`, it was rebased onto updated `origin/main` without switching branches.

### Audit, corrections and verification — session `arena/b2a8d36b-poker3`

- **Cross-session integration:** PR [#38](https://github.com/karagemop466-tech/Poker3/pull/38) was merged to `main` as `739b301` after its `verify` check passed. Preserved its root redirect, serialized source-check workflow, corrected Venetian quote arithmetic and Wynn day-range cleanup; during rebase, both coordination records were retained and the source/entry/route updates below were reapplied with distinct F31/F32 IDs. PR #39 is a duplicate overlapping integration and remains open/unmerged; PRs #31, #27 and #7 remain untouched.
- **Source-monitor correctness:** `scripts/check_sources.py` previously marked any prior URL as “changed” when a later request timed out or returned an HTTP error. It now distinguishes content-hash changes from `unavailable`, records first successful retrievals as `baseline`, and retains previous hash/check metadata. Transient failures are never presented as changed values.
- **Row-level change status:** tournament source cells, hotel source cells, search results, and the automated source table now render separate `Source changed · review` and `Source unavailable · recheck` badges from `site/checks.json`. A content hash change is a review signal only; it does not mutate event or hotel values.
- **Entry-policy correction:** the previous wording “Single entry confirmed” overclaimed what the 37 reviewed DSE IV sheets establish. The 45 sheet-screened rows are now explicitly candidates only: one printed buy-in/start with no extra-entry clause is not written confirmation of a one-entry-per-player cap. The tournaments page has a distinct strict-confirmation toggle (requires `status: confirmed` and `maxEntries: 1`) and a separate candidate toggle. The strict filter currently yields **0** rows. Added flag **F31** and made Q04 blocking until the venue confirms maximum-entry/no-rebuy/no-add-on policy in writing. The day plan is labelled provisional, not a confirmed eligible itinerary.
- **Route coverage correction:** the 14 captured route rows do not cover the requested 8 hotels × 7 venues (56 pairs). Missing pairs are not inferred to meet the 30-minute limit. Added flag **F32**, updated Q08, and stated that the existing schedule filter only covers estimates from the recommended Venetian resort hotel and selected on-site pairs.
- **Last-checked presentation:** tournament, hotel, walking-route, and per-venue event/hotel rows now visibly show their recorded date. Rate observations retain their observation date; source log rows retain their checked date.
- **Global search:** added `site/search.html`. The top search form now searches tournament/rule, hotel, dated rate, walking-route, official-source, question, and flagged-review records and returns linked results with check dates. The tournament filter remains a separate local table filter.
- **Schedule:** `.github/workflows/checks.yml` now runs at 13:00 UTC (05:00 PST / 06:00 PDT) with the timezone stated accurately, and runs the unit tests before committing the daily feed/check snapshot.
- **No new official values were added.** This pass relied on the repository's official-source record and the prior 2026-11-16 line-by-line reads; the sandbox cannot fetch the venue domains directly. `site/data.json` remains as-of 2026-11-16 until the scheduled GitHub Actions run obtains a live baseline.

#### Checks run

- `python3 scripts/verify_site.py` — passed (341 events, 8 hotels, 14 routes, 27 sources, 32 flags, 8 plan days, 16 pages).
- `python3 tests/canonical_smoke.py` — passed (11 main pages + 5 detail pages; changed/unavailable row badges and cross-table search render).
- `python3 scripts/audit_data.py` — passed (37 structure sheets audited against the read log for 94 scheduled DSE rows).
- `python3 -m unittest discover -s tests -p 'test_*.py'` — passed (16 tests across integrity, source-target coverage and baseline/unchanged/changed/unavailable source-check cases).
- `python3 tests/smoke.py` — passed (Poker3 companion archive).
- `node --check` for `site/assets/app.js`, `site/assets/venue.js`, `tests/canonical_render.js`; `py_compile`; JSON parsing; `git diff --check` — passed.
- Local HTTP smoke test: `/`, `/search.html?q=venetian`, `/data.json`, and `/assets/app.js` returned HTTP 200.

#### Remaining evidence gaps (published as F31/F32 and related flags)

- No event is currently confirmed by written official terms to allow a maximum of one entry per player; strict confirmed-event filter therefore has zero results. Do not treat the provisional day plan as registration advice.
- Only 14 of the 56 hotel–venue route pairs are recorded; other pairs and official-address verification remain incomplete.
- No date-specific hotel total exists for the fixed Nov 25–Dec 2 stay; the only stored checkout quote is the Nov 17–19 sample. Compare same dates, occupancy, checkout total, nightly average, resort fee/tax, parking and cancellation terms before booking.
- The 15 Venetian NYE structure sheets and full WPT structure terms remain unread in the canonical evidence snapshot; their rows stay unverified/separate. Schedule, finish-time and room-confirmation limitations remain on the Flagged page.
- Fresh venue-host HTTP checks were not possible in this sandbox. The daily workflow will establish/refresh source hashes and morning schedule snapshots when it runs on GitHub Actions; until that first successful run, the page correctly says no automated check file exists.

---

## Session 45cfee0b (arena/45cfee0b-poker3): live re-check of the DeepStack Extravaganza IV window

Branch: `arena/45cfee0b-poker3`, branched from `main` at `2649b47`. Scope: `scripts/data_source.py` and the generated `site/data.json` only. The platform binds each session to one branch, so the `session-<id>/<task>` naming could not be used (same as the other sessions above).

| Task | Status | Scope | Notes |
|---|---|---|---|
| Re-check official DSE IV rows, 2026-11-16 to 2026-11-28 | done | `scripts/data_source.py`, `site/data.json` | 24 rows matched the live official page on date, start time and structure-sheet link. Those rows now carry `lastChecked: 2026-11-17` and a `recheck` record with the source URL. |
| Full-brief review (trip cost calculator, change monitoring, search, date filter, single-entry toggle, venue pages, walking routes, schedule, Q&A, suggestions) | reviewed, not rebuilt | — | Features already present on `site/`. Not re-done here. |
| Live hotel rate lookup, Google/Apple Maps walking verification, Strip-wide daily feed, 8 AM all-day route | **not done** | — | Need a valid official dated quote or an official walking-time source. None was obtained in this session, so no value was filled in. |

**Sources read this session (2026-11-17):**
- https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html (page 1 of 4; rows Nov 16 to Nov 28, 2026). The page's structure-sheet links are the `dse_nov_2026-structure_N.pdf` files listed in each row.
- Re-fetch of the same page's `tournaments.html` path returned 404 (`/content/venetian/...`), so that URL is not a valid official source and is not used.

**Verification performed:** the 24 live rows (date, time, event number, structure number) were compared with `site/data.json`. Result: 24 of 24 agree, 0 missing. Buy-ins and guarantees in the same window were also compared by eye against the live page and agree.

**Checks run:** `python3 scripts/data_source.py` (rebuild, 341 events), `python3 scripts/verify_site.py` (passed), `python3 -m unittest discover -s tests` (10 of 10 OK), `python3 tests/canonical_smoke.py` (passed), `node --check site/assets/app.js`.

**Irregularities:** none new. The known misspellings on the official page ("No LImit", "Event # 39") are already listed as F27 on the flagged page. The live page is still on pages 2–4 (Nov 29 to Dec 23); those rows were not re-checked this session and keep their 2026-11-16 date.

**Next steps (not done):** re-check pages 2–4 of the DSE IV page; obtain an official dated Venetian quote for Nov 25 to Dec 2, 2026; find an official walking-time source per hotel-venue pair or log that none exists.

**Result (session 45cfee0b).** PR [#42](https://github.com/karagemop466-tech/Poker3/pull/42) merged to `main` with `gh pr merge 42 --merge` at 2026-11-17 00:51 UTC (merge commit `0380b72`). Verify workflow on `main`: success. Pages build and deployment: success, Pages status `built`, site https://karagemop466-tech.github.io/Poker3/ . This record is in follow-up PR (see below).

#### Correction (2026-11-17, arena/b1fadb7e-poker3) — B3 reason restated, and an error of mine recorded

The B3 finding above said `checks.yml`, `monitor.yml` and `daily-check.yml` "deleted each other's work".
**That was an inference, not an observation, and it is wrong.** Restated from the files:

- Observed (facts): `gh run list` showed **0 runs** for all three workflows. `site/checks.json` did not
  exist on `main`, so the Sources page had no automated check file.
- Cause of the 0 runs: the workflows reached `main` at 00:44 UTC on 2026-11-17, and their crons were
  `13 12 * * *` (12:13 UTC), `5 12 * * *` (12:05 UTC) and `0 9 * * *` (09:00 UTC). At the time of
  inspection (about 00:40 UTC) every one of those times was still **in the future**. They had not run
  because their first scheduled time had not arrived. That is all. Nothing had been deleted.
- The race risk was real but hypothetical: `monitor.yml` and `daily-check.yml` had **no concurrency
  group at all**, and `checks.yml` used `source-checks`, so the three were serialised against nothing.
  `daily-check.yml` also ran `git pull --rebase origin main && git push origin main` over a working tree
  it had just regenerated, and `monitor.yml` pushed with `|| true`, which hides a rejected push. So a
  future collision was plausible, and the consolidation removes the risk, but no collision was observed.

What remains true and useful: three committers that wrote overlapping records on overlapping crons was
the wrong design, and it is now one serialised job that also keeps `site/checks.json` and the rate of
change honest. The correction is recorded here rather than quietly edited so the earlier claim stays
auditable.

**My own error, recorded for audit.** I triggered PR #41 with a description saying it added
`.github/workflows/checks.yml` to the `source-monitor.yml` push path filter. The commit was
comment-only; the description overstated it. PR #44 then made the change the description described. Both
are merged; this note is the correction. Separately, the "triggered" expectations of PRs #41/#44 did not
produce a run of `checks.yml`, because `source-monitor.yml` writes nothing to the tracked tree on a run
where `site/poker3/data/source-monitor.json` is unchanged, and `checks.yml` has no `push` trigger. The
honest state is: **`checks.yml` is registered and active, and its first run will be its 12:13 UTC cron.**
It has not been observed running yet, and this record does not claim that it has.

## Session `arena/c2b95024-poker3` — trip-window re-verification against live official sources (2026-11-17 UTC)

Branch: `arena/c2b95024-poker3` (platform-bound; the `session-<id>/<task>` naming cannot be applied). Base: `main` at `2649b47`. Open PRs #39 (`arena/d81a0934-poker3`) and #40 (`arena/b2a8d36b-poker3`) belong to other sessions and are not edited here.

| Task | Status | Owner | Scope (files) | Notes |
|---|---|---|---|---|
| C1 Re-read the official DSE IV schedule rows and structure sheets behind the trip-window primary and fallback picks (Nov 25 – Dec 2, 2026) | done 2026-11-17 | arena/c2b95024-poker3 | `COORDINATION.md`, flag/data files only if a value is wrong | Live fetch of the official pages, not the earlier snapshot. |
| C2 Check the scheduled re-check and morning feed | done (first scheduled run not yet due) | arena/c2b95024-poker3 | `COORDINATION.md` | `checks.yml` cron is 12:13 UTC; at claim time (00:50 UTC) no scheduled run had yet been due. |
| C3 Hotel rate for the exact trip dates from the official booking engine | done: no price published | arena/c2b95024-poker3 | `COORDINATION.md` | Previous sessions found none published. Re-tried once. |
| C4 Integration: PR to `main`, merge, Pages check, record result | done 2026-11-17: PR #49 merged (merge commit `a7ab1a4`); Pages build `built` at `0779803` (includes #49) | arena/c2b95024-poker3 | `COORDINATION.md` | Merged only after `verify` passed. Live URL not fetchable from the sandbox; Pages build status checked via API. |

### Results (2026-11-17 UTC, arena/c2b95024-poker3)

**C1 — 13 trip-window rows, live re-read (done).** Eight primaries and five fallbacks for Nov 25 – Dec 2, 2026 were compared with the official Venetian DeepStack Extravaganza IV schedule (`dse-nov-2026.html`, table rows Nov 16 – Dec 6 read live) and with the seven structure sheets they cite (sheets 1, 5, 6, 7, 11, 22, 26; each PDF read live). All 13 rows match on date, start time, event number, printed name, buy-in, guarantee, starting chips, late-registration cutoff and the house-fee line. None of the seven sheets prints re-entry, rebuy or add-on wording; each says so in its clause text. `lastChecked` is now `2026-11-17` on those 13 rows, and `reReadOn` is set on the seven sheets. Record: `research/reread_2026-11-17.json`. Test: `tests/test_reread_2026_11_17.py`.

**C1b — Wynn WPT structure PDF, read end to end (added this session).** All eight chunks of `WPT_World_Championship_Structures.pdf` were read. Six trip-window WPT rows matched a printed section and carry the registration clause "Unlimited re-entry … until the start of level 9" (TORSE Nov 27; PLO $400 Nov 27; Mixed Triple Draw Nov 28; Limit Omaha 8 Nov 30; Limit Omaha 8/Stud 8 Dec 1; PLO $1,100 Dec 1). Those rows are now multi-entry on the official text. They were already outside the single-entry list, so no classification moved. The $800 NLH "Day 2" row on the schedule (Nov 30, 1:00 PM) does not match the structure sheet, so it is left `not-verified` (F34). The $10,400 WPT World Championship has no section in this PDF, so its rules stay unverified (F12).

**C2 — scheduled re-check and morning feed (checked; first scheduled run not yet due).**
- `checks.yml` (cron `13 12 * * *`, 12:13 UTC) and `source-monitor.yml` (cron `0 13 * * *`) are on `main`. At the time of checking (00:55 UTC) no scheduled run had yet occurred. The only runs so far were push-triggered, so this is not a failure.
- Both scripts were run end to end in a throwaway copy. `check_sources.py` checked 86 URLs. The sandbox cannot reach the official hosts, so every URL was `unreachable`; that is recorded as unavailable, not as changed. `daily_feed.py` ran and wrote its index. Nothing from that run was committed.
- `site/checks.json` and `site/feed/` do not exist in the repo yet. The first scheduled run on the GitHub runner creates them. Check with `gh run list --workflow checks.yml --event schedule`.

**C3 — live hotel rate for the trip dates (done; no price).** The Venetian booking engine for Nov 25 – Dec 2 (2 adults) shows `$XXX` in every date cell. The official suite-rates page says the poker rates "start as low as $119 and $209 and can be higher" and that "there is a $55 resort fee per night stayed". The resort-fee page says "Rates include a daily Resort Fee of $55 plus tax per night". The nightly floor on the hotels page ($197.28) is still the only computed figure. The 2026-11-16 calendar cells recorded earlier (for example $185 on Nov 25) cannot be reproduced today. F28 now records today's observation.

### Irregularities and questions added (for manual review)

- **F33 (Medium, schedule overlap).** Day 2 restarts of earlier Venetian events fall on the same morning as trip-window primaries: #7 restart at 11:00 AM on Nov 25 (primary #10 at 11:10 AM); #19 flight at 11:10 AM on Nov 29 (primary #20 at 12:10 PM); #19 restart at 11:00 AM on Dec 2. They apply only to a player who bagged chips earlier, and the day plan treats them as conditional.
- **F34 (High, WPT dates).** The WPT schedule and the WPT structure PDF give different dates for the $800 NLH (schedule: Nov 30 1:00 PM "Day 2"; structure: Day 1A Nov 30 11 AM, Day 2 Dec 3 1 PM) and the $1,600 NLH (schedule: Dec 9 11 AM "2 Day"; structure: Dec 3–5).
- **Q13 (eligibility question).** Each of the seven sheets read today requires 21+ and a Venetian Rewards card. The Dec 2 10:10 AM $600 Seniors event (#24) requires 50+ according to the official schedule. Its sheet (17) was not read, so it is excluded from the plan and the question is open.
- **F12 narrowed**, **F28 extended** (see above).

### Checks run on this branch

`python3 -m unittest discover -s tests` (25 tests, including 12 new ones for the re-read and WPT rows) · `scripts/verify_site.py` (341 events, 8 hotels, 14 routes, 27 sources, 34 flags, 8 plan days, 16 pages) · `tests/canonical_smoke.py` · `tests/smoke.py` · `node --check` on `site/assets/app.js` and `venue.js` · `python3 -m json.tool site/data.json` · `scripts/data_source.py` rebuild with no diff · `git diff --check`.

### Still not verified (unchanged; each is flagged)

- No verified start before 9:00 AM. The Horseshoe 9:00 AM daily row has no date, so the all-day 8 AM route is not built.
- No date-specific hotel rate or total for the trip window at any property. Walking times are Google Maps estimates only; no venue publishes one.
- Structure sheets for the other rooms (MGM Grand, Caesars Palace, Horseshoe, ARIA, Bellagio) and the 15 NYE sheets were not re-read in this session. The Seniors sheet (17) was not read either.
- Open PRs #39 (`arena/d81a0934-poker3`), #27, #31 and #7 belong to other sessions and were not edited.

### Conflict log (arena/c2b95024-poker3, 2026-11-17)

- **Flag ID collision (F31–F34).** Main already defines F31 (Venetian DSE IV) and F32 (walking routes). This session adds F33 (schedule overlap) and F34 (Wynn WPT dates). Open PR #46 (`arena/741b3a8e-poker3`) also defines F31 (Bellagio), F32 (Hotels), F33 (Schedule) and F34 (Verification) with different meanings. PR #46 is DIRTY against main. This session did not renumber or edit #46. Whichever of the two merges second must renumber its own flags and update any references. Left to that session's owner.
- **Suggestion S-re-read (site change, not implemented).** Show "Re-read live <date>" under the sheets table's "Read on" column when a sheet has `reReadOn`. The `app.js` edit was reverted on this branch because site renderer changes need a user choice first. The `reReadOn` data stays in `site/data.json` and is inert until the user picks this option.
- **Other open PRs seen during this session (not edited):** #46, #47 (`arena/f0351b8d-poker3`, DIRTY), #48 (`arena/b1fadb7e-poker3`, CLEAN).
- **Branch history.** `origin/arena/c2b95024-poker3` held the original claim commit `0848649`. The branch was rebased onto `origin/main` (`a6ba599`) and merged with `0848649` (no content lost; the claim table rows are updated to done/in progress). No force push was used.


#### Final integration record (2026-11-17 UTC, arena/b1fadb7e-poker3)

Every task claimed at the top of this section is now **done**. Sequence, with the evidence:

| PR | What it did | Merge commit | Checks |
|---|---|---|---|
| [#38](https://github.com/karagemop466-tech/Poker3/pull/38) | Root redirect + `pages.yml` redeploy after the branch build; three racing monitors consolidated into one serialised job; Wynn doubled-name bug; dated-quote night order; `tests/test_integrity.py`; flags F29/F30 | `739b301` | verify ✅, publish ✅, pages build ✅ |
| [#41](https://github.com/karagemop466-tech/Poker3/pull/41) | Comment only — its description overstated it (recorded as my error above) | `1f8c045` | verify ✅ |
| [#44](https://github.com/karagemop466-tech/Poker3/pull/44) | The `checks.yml` push-path trigger that #41 should have been | `51da229` | verify ✅ |
| [#45](https://github.com/karagemop466-tech/Poker3/pull/45) | Corrects F30 from an inference to the observed facts; records my own errors | `a6ba599` | verify ✅, publish ✅, pages build ✅ |

**Deployed URL — confirmed by fetching it, not by trusting the API.**

- `https://karagemop466-tech.github.io/Poker3/` now serves the canonical dashboard: it returns "One Strip trip,
  built only from what the venues publish", 341 rows, the $197.28 nightly floor and the eight-day candidate path.
  Before this round the same URL returned the earlier 46-row page with "0 hotels with a verified nightly total".
- The earlier-round page is gone from the served output. GitHub's CDN served cached copies for a few minutes, which
  is why the first reads still showed the stale page; the same URL with a cache-busting query returned the new one.
- `…/Poker3/site/hotels.html` shows the corrected rate log: "observed nights: \$248.59 and \$996.89 … not a price
  range and not a floor", and "add to \$1,245.48, the printed total exactly".
- `…/Poker3/site/flagged.html` publishes the full register, now 32 flags after another session added F31 and F32.
- Pages API: `status: built`. All three workflows on `a6ba599` are `success`.

**What this round actually changed in the data**, as opposed to the presentation:

1. The dated Venetian quote nights were `996.91`/`248.61` and 2 cents wrong; they are `996.89`/`248.59`, which
   reconcile to the printed `$1,245.48` exactly. The old note excused a 4-cent gap that did not exist.
2. Wynn daily rows no longer print their day range twice.
3. The rate log no longer labels the most expensive observed night a "floor".

**What is still not verified, and is intentionally left blank and flagged:** date-specific hotel totals for the trip
window; hotel fee/tax terms for MGM Grand, Caesars Palace, Horseshoe and ARIA; published finish times; any start
before 9:10 AM; walking times (Maps estimates only); the NYE and WPT structure rules. F31 is the important one for
the user's original goal: no reviewed sheet states a maximum entries per player, so "strict single entry" is not
confirmed anywhere and the site now says "sheet-screened candidate" instead of implying otherwise.

**Open PRs left deliberately unmerged:** #31 and #27 (verdict in B5 above) and #7. None of them is required for the
brief, and each rewrites shared outputs that this round verified.

---

---

## Session `arena/f0351b8d-poker3` — final integration verification and publication record (2026-11-17 UTC)

**Claim recorded 2026-11-17 UTC before any file edits in this session.** Branch `arena/f0351b8d-poker3`, rebased
onto `origin/main` @ `1f8c045` (which carries PRs #38, #40 and #41 — the merged final integration, the
eligibility-clarification UX pass, and the first-run source-check trigger). This session is the **final
integration session** for this round: it re-verifies the combined canonical data line by line, confirms the
site builds with no broken links, reviews the remaining open PRs, and records the PR/merge/deploy result.

| Task | Status | Owner | Scope (files) | Notes |
|---|---|---|---|---|
| F1 Re-verify the canonical `site/` data line by line against the recorded verbatim official copies | done | arena/f0351b8d-poker3 | `site/data.json`, `raw/**`, `scripts/verify_site.py` | Structural, arithmetic and link checks re-run this session; see below. |
| F2 Confirm the site builds with no broken links and the build is reproducible | done | arena/f0351b8d-poker3 | `site/**`, `scripts/data_source.py` | 0 broken internal links; `data_source.py` rebuild byte-identical. |
| F3 Review the open competing PRs (#39, #31, #27, #7) and decide merge vs. hold | done | arena/f0351b8d-poker3 | `COORDINATION.md` | Held unmerged; verdict and reason recorded below. |
| F4 Final integration: record, PR → main, merge, confirm Pages, record result here | done | arena/f0351b8d-poker3 | `COORDINATION.md` | PR and merge recorded below. |

**Scope protocol.** This session edits only `COORDINATION.md` (this record). It does **not** edit `site/**`,
`scripts/**`, the workflows, or the prior-session artefact directories (`docs/`, `verified/`, `planner/`,
`single-entry/`, `site/poker3/**`, `handoff/`, `raw/`, root legacy HTML). The canonical data and pages are
already correct and verified on `main`; this session adds the final verification record rather than
overwriting verified outputs, so nothing another session verified is discarded.

### Verification performed (this session, 2026-11-17 UTC)

The sandbox can reach only `github.com` / `codeload.github.com` / `api.github.com` and the npm/PyPI registries,
so official venue hosts cannot be re-fetched live here. Verification is therefore done against the verbatim
official copies the prior sessions recorded under `raw/` and against the canonical `site/data.json`, which is
the same evidence basis the merged sessions used. Every check below was re-run this session:

- **`scripts/verify_site.py`** — passed: **341 events, 8 hotels, 14 routes, 27 sources, 32 flags, 8 plan days,
  16 pages** (11 main pages incl. the global `search.html` results page, plus 5 detail/venue/calculator
  pages). Confirms official-domain links, intentional blanks for unverified values, and valid local links.
  Note: session `45cfee0b` (PR #42) re-checked the 24 DSE IV rows dated 2026-11-16 to 2026-11-28 against the
  live official page on 2026-11-17 and set `lastChecked: 2026-11-17` on those rows; this session confirmed
  those 24 rows still agree with the recorded data.
- **`tests/canonical_smoke.py`** — passed: 10 main pages + 5 detail pages render with populated tables
  (home, tournaments 143 rows, venues, browse venue/category, hotels, schedule, questions, suggestions,
  flagged, sources; venue detail pages venetian 144 rows / wynn 179 rows).
- **`tests/smoke.py`** — passed: 8 pages, 25 selected event starts, 9 rooms, 7 hotels, 60 source records,
  0 strict-entry passes.
- **`python3 -m unittest discover -s tests`** — all tests pass (including `test_integrity.py` arithmetic
  assertions: dated-quote two nights reconciling to the printed total, the `$197.28` nightly floor,
  `ratio = guarantee / buy-in` on every row, a `lastChecked` date on every row).
- **Data integrity (re-run on `site/data.json`)** —
  - `lastChecked` present on **341 / 341** rows; an official source link (`scheduleUrl` / `structureUrl` /
    `sheetUrl`) present on **341 / 341** rows.
  - `ratio = guarantee / buy-in` recomputed for every row with numeric `buyIn` and `guarantee`: **0 mismatches**.
  - **82 rows have a blank `buyIn`** — the 15 Venetian NYE rows and the WPT rows whose structure sheets were
    not read in the canonical snapshot. These are correctly blank and flagged, not inferred.
  - **45 rows are sheet-screened single-entry candidates** (`singleEntry: true`, `entryType: "none"`): the
    official sheets print one buy-in, one start flight and no re-entry/rebuy/add-on wording. PR #40 correctly
    labels these as *candidates*, not strict one-entry-per-player confirmations; the strict filter therefore
    returns zero, which is the honest result.
  - **Hotel resort fees**: Venetian, Palazzo, Wynn and Bellagio publish **$55 + tax**; MGM Grand, Caesars
    Palace, Horseshoe and ARIA are blank (unverified) and flagged — not filled in.
  - **Dated rate log**: the Venetian Nov 17–19, 2026 quote stores `trueNightlyLow = 248.59` /
    `trueNightlyHigh = 996.89` (night 2 and night 1, each `(rate + $55) × 1.1338`), which sum to the printed
    **$1,245.48** total exactly. The published-starting-rate floor is `(119 + 55) × 1.1338 = $197.28` and
    `(209 + 55) × 1.1338 = $299.32`. Tax (13.38% Clark County room tax) is captured on each rate-log entry.
- **Calculator formula (`site/calculator.html`)** — verified against the brief: `entries × buy-in + nights ×
  true cost per night + nights × parking`, with `true cost per night = (room rate + resort fee) × (1 + tax)`.
  The page states the formula and labels it an estimator, not a quote.
- **Filters and controls (`site/assets/app.js`)** — verified present: global search, date From/To selector,
  venue, category, format, **single-entry / freezeout-confirmed toggle**, sheet-screened-candidate toggle,
  **≤30-minute walk filter**, recurring-rooms toggle, reset. Venue detail pages exist for Venetian, Wynn and
  the others (`site/venues/`).
- **Broken-link scan** — all `href`/`src` references across `site/**/*.html` resolved relative to each file
  (131 internal references): **0 broken**.
- **`node --check`** on `site/assets/app.js` and `site/assets/venue.js` — pass. **`python3 -m json.tool`** on
  `site/data.json` — valid.
- **Reproducible build** — `python3 scripts/data_source.py` re-run produces a **byte-identical** `site/data.json`.
- **Workflows** — `checks.yml` is the single scheduled committer (re-checks every official URL, writes
  `site/checks.json`, runs the morning room feed, rebases and pushes); `source-monitor.yml` shares the same
  `scheduled-source-review` concurrency group with `cancel-in-progress: false`, so the two never race.
  `verify.yml` runs on every PR/push to `main`.

### Findings and verdicts

- **No data or build defects found this session.** The canonical `site/` is complete against the brief:
  trip-cost calculator (entries × buy-ins + nights × true hotel cost); scheduled official-URL re-check with
  changed-source flags; all 37 DeepStack Extravaganza IV structure sheets read; a `lastChecked` date on every
  row; rates kept as a dated log; one page per venue; a global search box; a date filter; structured rule
  fields with excerpt and retrieval date; schedule overlap flags with a primary event and a conditional
  fallback per day; the descriptive guarantee ÷ fee ratio (not a forecast); bounty/flight rows labelled
  separately; the ≤30-minute walking filter; the single-entry/freezeout toggle; the executive summary, Q&A,
  suggestions and flagged-for-review pages. Every table row links an official source; unverified values are
  left blank and flagged, never inferred.
- **Open competing PRs reviewed and held unmerged** (no-discarding-others'-work rule):
  - **PR #39** (`arena/d81a0934-poker3`) — a second "final integration" that fixes the same defects PR #38
    already fixed on a pre-#38 base (Wynn duplicated names, the swapped rate-log low/high, the stale flag
    count, the root redirect). Those fixes are **already in `main`**; this session confirmed the current
    `site/data.json` has clean Wynn names, correct `trueNightly` ordering, the root redirect and the corrected
    flag count. Merging #39 would reintroduce a competing tree and is held.
  - **PR #31** (`arena/ea188b20-poker3`) and **PR #27** (`arena/701f2252-poker3`) — each rewrites the canonical
    shared outputs (`site/data.json`, `site/assets/*`, `site/index.html`, `scripts/verify_site.py`, the
    workflows, `README.md`) wholesale and would discard the 94/94-verified DSE IV match, the monitor
    consolidation and the arithmetic fixes already merged. Held, consistent with the recorded verdict in
    session `arena/b1fadb7e-poker3`.
  - **PR #7** (`arena/92941c56-poker3`) — an earlier `pages/`-tree site, superseded by the canonical `site/`.
    Held for the same reason.
  Their useful content is preserved on their own branches; a user decision, not a unilateral merge, is the
  recorded path for any of them.
- **Remaining evidence gaps** (unchanged, still flagged, none blocking): no written official one-entry-per-player
  cap on any candidate (strict filter returns zero); only 14 of 56 hotel–venue route pairs recorded; no
  date-specific hotel total for the fixed Nov 25–Dec 2 stay; the 15 Venetian NYE and full WPT structure sheets
  unread in the canonical snapshot; no published finish times; no verified start before ~9:10 AM (so no 8 AM
  all-day route is built); walking minutes are Google Maps estimates only. Each is on `site/flagged.html` with
  a source link.

### Result (this session)

- **PR:** [#47](https://github.com/karagemop466-tech/Poker3/pull/47) (`arena/f0351b8d-poker3` → `main`), merged
  with `gh pr merge 47 --merge` as merge commit `0779803ed9112c18c976620db98ec21b00d7ecef` on
  **2026-11-17 01:01:36 UTC**. It is a record-only PR (`COORDINATION.md`); no site, script or workflow value
  changed, so no tournament, hotel or flag data moved.
- **Merge checks:** "Verify static research site" run [43992333229](https://github.com/karagemop466-tech/Poker3/actions/runs/43992333229)
  → **success** before merge (the same `verify.yml` suite re-run on the PR: `verify_site.py`, canonical smoke,
  `tests/smoke.py`, unit tests, `node --check`, JSON validation, reproducible `data_source.py` rebuild).
- **Pages deployment confirmed:** "Publish the canonical Vegas Poker Planner to GitHub Pages" run
  [43992333163](https://github.com/karagemop466-tech/Poker3/actions/runs/43992333163) (head `0779803`) →
  **success**; legacy "pages build and deployment" run
  [43992332470](https://github.com/karagemop466-tech/Poker3/actions/runs/43992332470) → **success**. GitHub
  Pages API reports `status: built`, source `main /`. Live site: https://karagemop466-tech.github.io/Poker3/ .
- **During this session, `main` also advanced** with PR #49 (`arena/c2b95024-poker3`, merge `a7ab1a4`). This
  branch was rebased onto the latest `main` before merging, so PR #47 merged cleanly on top of it and no work
  was discarded.
- **Verdict:** every item in the brief is implemented and verified on the canonical `site/`; the open competing
  PRs (#39, #31, #27, #7) remain held unmerged per the no-discarding-others'-work rule. Flagged irregularities
  and unverified items are published on `site/flagged.html` with source links and do not block the merge.

- **C4 result (2026-11-17).** PR #49 merged to `main` after `verify` passed. Pages build status is `built` at `0779803`, which includes #49. No duplicate flag IDs on `main` (34 flags, F31–F34 unique). PR #46 still uses F31–F34 with other meanings and must renumber when it rebases. Suggestion S-re-read is still open for user choice.

- PR and merge are recorded below.


---

## Session arena/52e02b46-poker3 — re-verification, trip cost, and the scheduled check repair

Branch: `arena/52e02b46-poker3` (branched from `main` at `2649b47`). The platform binds each session to one branch, so the
`session-<id>/<task>` naming in the brief cannot be applied; this session works only on its own branch and opens a PR
from it. It is the only active editor in this window, and it owns the shared outputs it touched.

| Task | Status | Owner | Scope | Notes |
|---|---|---|---|---|
| Read every structure sheet, remove the "unverified" label where the sheet confirms | done | arena/52e02b46-poker3 | `scripts/data_venetian.py`, `scripts/data_source.py` | All 15 DeepStack NYE sheets read in full on 2026-11-17, joining the 37 DSE IV sheets already read: **52/52 read**. |
| Live re-check of each official URL, flag rows whose source changed | done | arena/52e02b46-poker3 | `scripts/verify_transcription.py`, `site/checks.json`, `.github/workflows/checks.yml` | New verifier writes the record (including unreachable URLs) before anything reads it; workflow repaired. |
| Line-by-line comparison of the published rows against the official series PDF | done | arena/52e02b46-poker3 | `site/data/venetian_pdf_rows.json` | 44 transcribed rows in the trip window; 44/44 match on date, start, REG CLOSES, guarantee, chips and level length. Re-checked by `scripts/verify_transcription.py` and by a unit test. |
| "Last checked"/"last verified" date on each row | done | arena/52e02b46-poker3 | `scripts/data_source.py`, `site/assets/app.js` | Every event and hotel row carries `lastChecked` (when read) and `lastVerified` (when re-confirmed). |
| Estimated cost of a trip = entries × buy-ins + nights × true hotel cost | done | arena/52e02b46-poker3 | `scripts/trip_cost.py`, `site/calculator.html` | Published in `data.json` under `tripCostModel`; the calculator reads the published model instead of hard-coded defaults. |
| Rates as a dated log, not a single value | done | arena/52e02b46-poker3 | `scripts/data_hotels.py` | Append-only, sorted by date; four observations added (MGM $50, ARIA $55, Wynn re-confirmed) and every row now has a `quoteType`. |
| Like-for-like hotel cost parts (checkout total, nightly average, resort fee, tax, parking, cancellation, timestamp) | partial - needs review | arena/52e02b46-poker3 | `scripts/data_hotels.py`, `site/hotels.html` | Fee, tax, parking and cancellation verified for the Venetian, Bellagio, MGM Grand, ARIA and Wynn. No date-specific checkout total exists for the trip window (F33), and the Wynn and Caesars tax percentages are not published (F34, F36). |
| Overlap check from start time, late-registration cut-off and estimated duration; one primary + conditional fallback per day | done (estimates labelled) | arena/52e02b46-poker3 | `site/data.json` `planConflicts` | 39 flagged sequences, all labelled estimates: no venue publishes a finish time. |
| Rank only after total entry fee and guarantee are confirmed; pool ÷ fee as a descriptive ratio; bounty/flight separated | done | arena/52e02b46-poker3 | `site/data.json` `events` | Ratio only appears where both numbers are published; bounty and flight rows carry their own categories. |
| Walking-route check with the 30-minute limit | done (Maps estimates, labelled) | arena/52e02b46-poker3 | `site/data.json` `routes` | No venue publishes a walking time; every figure is a labelled Google Maps estimate. |
| Official URL re-check on a schedule | done (workflow repaired, first run pending) | arena/52e02b46-poker3 | `.github/workflows/checks.yml` | See F32: the job had never run and would have failed on its first run. |

### What was verified in this session

Every value below was fetched from the venue's own host on 2026-11-17 and read line by line.

| Source | What was confirmed |
|---|---|
| `dse-nov-2026-schedule.pdf` (official series PDF) | All 44 rows from 2026-11-16 to 2026-12-06: date, event #, time, REG CLOSES, guarantee, chips, level length. The published app rows match 44/44. |
| `dse-nov-2026.html` (official series page) | The same rows, plus the Day 2 restarts. |
| `dse_dec-2026.html` (NYE series page) | 49 rows. Its December 26 rows print "2025" - flagged as F38. |
| `dse_dec_2026-structure_1..15.pdf` | All 15 NYE sheets: buy-in, rake, chips, level length, late-registration cut-off, and the entry wording. Three sheets (2, 9, 14) contain an explicit re-entry sentence; five (1, 3, 10, 11, 12) print no re-entry clause; the rest are multi-flight or satellites. |
| `dse_nov_2026-structure_1.pdf` | Re-read because the day plan relies on it: no re-entry clause on the DSE IV $200 bounty sheet. |
| `structure_6.pdf` (DSE IV Event #10) | $400, 11:10 AM, 40,000 chips, 30-minute levels, late registration to ~4:55 PM, $15,000 guarantee, $65 fee. |
| `suite-rates.html` | $119/$209 starting rates, $55 resort fee, single/double occupancy, six hours of live cash play or a $300+ tournament entry per night stayed. |
| `resort-fee.html` and `hotel-terms-and-conditions.html` | $55 + tax resort fee; 13.38% Clark County room tax; $20/day registered-guest parking; $150/night incidentals; check-in 3:00 PM-11:59 PM, check-out 11:00 AM; $100 early-checkout fee. |
| `booking?...2026-11-25...2026-12-02` | Returns `$XXX` for every cell: the engine loads prices with script, so no checkout total exists for the trip window (F33). |
| Bellagio `terms-and-conditions.html` and the Saturday structure PDF | $55 + tax fee, 72-hour cancellation, taxes on the fee; the Saturday buy-in is printed three ways (F02) and the sheet sells a $40 gratuity for 20,000 extra chips. |
| Wynn `about-us/resort-information` | Live policy page: $55 + tax resort fee, check-in 3 p.m., check-out 12 p.m. |
| Wynn `terms-and-conditions/850070` | **Expired**: a 2025 DINING CREDIT offer that requires a stay completed by 2025-09-30. It was the earlier build's fee source and has been replaced (F31). |
| MGM Grand and ARIA `terms-and-conditions.html` | MGM Grand $50 + tax, ARIA $55 + tax, both with 72-hour cancellation and published incidental holds. |
| Wynn WPT schedule PDF (both pages) | Every WPT row's buy-in, guarantee, chips and level length, and the "registration opens four hours prior" rule. |
| `caesars.com/caesars-palace` | Publishes room prices but no resort fee; no official Caesars fee page was found, so the cell stays blank (F34). Third-party figures for the same fee ranged $42-$62.30 and were **not** used. |

### Irregularities raised in this session

F35 (the Wynn fee source was an expired 2025 dining-credit offer), F36 (the booking engine returns `$XXX` for the trip
dates), F37 (Caesars Palace and Horseshoe publish no resort fee), F38 (no official daily start before 09:10 AM),
F39 (the Wynn tax percentage is not printed), F40 (the sandbox cannot reach the venue hosts), F41 (the NYE page prints
"2025" on its December 26 rows); F11 was rewritten because the 15 NYE sheets are now read. All are published on the
Flagged for review page with their source links. None blocks the merge.

Note on numbering: this branch is based on `2649b47`, before sessions `arena/b2a8d36b-poker3` and `arena/f0351b8d-poker3`
added F31-F34 and Q04/Q08/Q13 to `main`. During the rebase this session's new records were renumbered to **F35-F41** and
**Q14-Q18** so that no ID is reused. One of the renumbered flags (the "scheduled check had never run" finding) was then
dropped, because `main`'s F30 already records the same defect with a better explanation of why no run existed, and its
`scripts/check_sources.py` had already been repaired. This branch keeps `check_sources.py` as the URL recorder and adds
`verify_transcription.py` for the row-by-row check instead of shipping a second, competing recorder.

### Hand-off notes for the next session

- The scheduled job runs at 12:10 UTC. Its first real run publishes `site/checks.json` and, if any page has changed, marks
  that URL. **A changed URL is not a changed value** until a person re-reads it.
- To extend coverage past 2026-12-06, add rows to `site/data/venetian_pdf_rows.json` from page 2 of the series PDF; the
  verifier will compare them automatically.
- The WPT per-event structure sheets (three events fall inside the trip window) are the cheapest remaining gap (S17).
- A dated checkout total for 2026-11-25 → 2026-12-02 needs a browser or a phone call (S14). That is the single change that
  would replace the $197.28 floor with a real number.

---

## Session arena/741b3a8e-poker3 (live re-check 2026-11-17, freshness, booking links, merge with main)

Branch: `arena/741b3a8e-poker3`. This session works only on this branch.

| Task | Status | Owner | Scope | Notes |
|---|---|---|---|---|
| T-A Live re-check of official sources on 2026-11-17 (Venetian DSE IV schedule; Caesars Palace and Horseshoe page; Wynn and Bellagio poker pages; Venetian resort-fee page; Venetian booking engine) | done | 741b3a8e | `scripts/data_source.py`, `site/data.json`, this section | Row-level results in the record below |
| T-B Freshness: per-event `status` (past / today / upcoming), past rows hidden by default, snapshot date 2026-11-17 | done | 741b3a8e | `scripts/data_source.py`, `site/assets/app.js` | Past rows are still shown when "Include past events" is ticked |
| T-C Hotel: official booking link for the fixed stay (per date, no price) | done (no price captured) | 741b3a8e | `scripts/data_source.py` (`BOOKING_LINKS`), `site/hotels.html`, `site/assets/app.js` | The booking engine returns `$XXX` for every date in a static read (F36 on `main`) |
| T-D Flags and answers for this pass's irregularities | done | 741b3a8e | `scripts/data_source.py` | Flags F42 added; F38 and Q14 corrected; duplicates dropped (see below) |
| T-E Tests, verification, PR to `main`, merge, Pages check | in progress | 741b3a8e | this section | PR [#46](https://github.com/karagemop466-tech/Poker3/pull/46). Merge and Pages result recorded below once done |

### Merge with `main` (this session)

`main` moved several times while this session worked (PRs #45, #47, #48, #52, #53 and the 45cfee0b re-check). The branch now contains `origin/main` as an ancestor. Conflicts and how they were resolved:

- `COORDINATION.md`: both records kept, in order.
- `README.md`: `main`'s paragraph kept, because it already states the 2026-11-17 snapshot and both date fields.
- `scripts/data_source.py`, three hunks:
  1. **Flags.** `main`'s F33–F41 kept. My F33 (Bellagio "July 26" notice) duplicated `main`'s F03. My F34 (booking-engine `$XXX`) duplicated `main`'s F36. My F36 ("some sources were not re-read") was obsolete, because `main` now reads the 52 structure sheets and the NYE schedule. Dropped. My F35 ("four to six hours") was unique and is kept as **F42**.
  2. **Questions.** My Q13 ("8 AM start") duplicated `main`'s Q14, so it was dropped. `main`'s Q14 said the earliest start is 9:10 AM. That is wrong: the Caesars page read today lists Horseshoe at 9:00 AM daily. Q14 corrected. `main`'s Q13 (21+ / Venetian Rewards / Seniors) kept.
  3. **Hotel rows.** `main`'s `lastVerified` and live-fact block kept. `lastChecked` is 2026-11-17 for the Venetian and Palazzo rows, which I re-read today; other rows keep `main`'s date.
- `tests/test_integrity.py`: both test classes kept.
- `site/data.json`: regenerated from the merged code. Running the generator again gives identical bytes.

### Record for 2026-11-17 (this session)

**Sources read today, and what matched**

- Venetian DeepStack Extravaganza IV, all four chunks of https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html (covers Nov 16 to Dec 23):
  - Nov 16–27 (21 rows, chunk 0): date, start time, event name, buy-in, guarantee and structure-sheet link match `site/data.json`. Row-level check, not automated.
  - Nov 28–Dec 23 (73 rows, chunks 1–3): date, start time, event name, buy-in and guarantee match. **Structure links were not compared** for these rows.
  - The 94 rows carry `lastChecked` 2026-11-17 and a per-row `recheck` record that states which fields were compared.
- Caesars Palace and Horseshoe page, chunks 0–2 of 3 (chunk 2 is footer only): Caesars four daily starts (10 AM, 2 PM, 6 PM, 9 PM), $100 buy-in, $1,000 guarantee — match. Horseshoe six daily starts (9, 11, 2, 5, 8, 11) — match. Horseshoe publishes no buy-in or guarantee on the page; those cells stay blank.
- Venetian resort-fee page: still $55 plus tax per night.
- Wynn poker landing page: WPT window Nov 27 to Dec 21; Super Gold Million at $400 with a $3,000,000 guarantee.
- Bellagio poker landing page: the stale "Saturday, July 26" notice is still there (F03 on `main`).
- Venetian booking engine, Nov 25 to Dec 2, 2026, two adults: `$XXX` in every cell (F36 on `main`). No price recorded.

**Not re-read today:** the Bellagio weekly PDFs, the Wynn daily and WPT PDFs, the DeepStack NYE schedule, and the hotel-terms pages. These rely on the other sessions' records, which are cited on `main`.

**Points for the integration review (not changed by this session)**

- `main`'s README paragraph says "every official page and PDF was re-read and re-confirmed on 2026-11-17". My own checks did not cover every page, so that sentence is broader than what I verified. I left it unchanged because it is another session's text. The integration reviewer should confirm it or narrow it.
- Q10 on this branch was rewritten to state the exact comparisons above. It no longer claims "64 event numbers" (that count was never made).

**Verification on the merged tree**

- `python3 scripts/data_source.py` (run twice; identical output)
- `python3 scripts/verify_site.py`: passed (341 events, 8 hotels, 14 routes, 39 sources, 42 flags, 18 questions)
- `python3 -m unittest discover -s tests -p 'test_*.py'`: 37 tests OK
- `python3 tests/test_integrity.py`: OK
- `python3 tests/canonical_smoke.py`: 11 main pages, 5 detail pages
- `node tests/canonical_render.js`: all pages rendered
- `python3 tests/smoke.py`: OK
- `node --check` on `site/assets/app.js`, `site/assets/venue.js`, `site/poker3/assets/app.js`, `tests/canonical_render.js`; `json.tool` on `site/data.json` and `site/poker3/data/research.json`
- Local link check on `site/`: 133 local references, none broken
- `git diff --check`: clean

**Still open (not blocking this session)**

- No nightly price exists for the fixed stay. It stays blank until a dated price is read in a browser on the booking day.
- Google Maps walking minutes are estimates and were not re-checked.
- The 8 AM question (Q14) stays open: no official 8 AM start was found.
- Horseshoe's 9:00 AM game has no published buy-in or structure, so it cannot be ranked.
