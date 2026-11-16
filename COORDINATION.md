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
