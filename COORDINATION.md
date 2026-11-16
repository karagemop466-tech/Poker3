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

- PR: [#6](https://github.com/karagemop466-tech/Poker3/pull/6), merged 2026-11-16 18:47:13 UTC with `gh pr merge 6 --merge` (merge commit `4af9596`).
- Pages: deploy run [43932491105](https://github.com/karagemop466-tech/Poker3/actions/runs/43932491105) completed `success`; Pages API reports `status: built`, source `main` `/`.
- Live site: https://karagemop466-tech.github.io/Poker3/ (the sandbox cannot reach github.io directly; deployment confirmed via GitHub API and run status).
- Follow-up that records this result: PR_RECORD_PLACEHOLDER.
