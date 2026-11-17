# Session arena/5b8ce14d-poker3 — log

Branch: `arena/5b8ce14d-poker3` (platform-bound; the `session-<id>/<task>` naming cannot be applied).
Branched from `b9c8d77`; fast-forwarded to `origin/main` @ `6a40bca` (PR #109) before any edit.
Narrative for this session lives here, not in the shared `COORDINATION.md`, so parallel branches
append to disjoint files (see the structural fix proposed in the 6d1b2adb record).

## Claim (recorded before any data edit, 2026-11-17 UTC)

| Task | Status | Owner | Files in scope | Notes |
|---|---|---|---|---|
| T1 Resolve F39: room-tax % at Wynn, Caesars Palace, Horseshoe from official terms pages | in progress | arena/5b8ce14d-poker3 | `scripts/data_hotels.py`, `scripts/data_source.py` (flag text only), `site/data.json` (regenerated), `raw/official_excerpts_2026-11-17.md` (appended excerpts) | Keep the flag if no official page prints a percentage; never infer 13.38% for a property whose own page does not print it. |
| T2 Strip room coverage and earliest-start check (F17, F21): official poker pages for Resorts World, Planet Hollywood/Paris/Flamingo (Caesars), and recheck Caesars/Horseshoe/Bellagio daily starts | in progress | arena/5b8ce14d-poker3 | `scripts/data_venues.py`, `raw/**` (new captures), `scripts/data_source.py` (flag text only), `site/data.json` | Add a row only when the official page prints the event name, start time and buy-in. |
| T3 Integration: `verify.yml` gate green locally (incl. `test_workflows`, which needs pyyaml), PR to `main`, merge, Pages check, record in this log and a short index line in `COORDINATION.md` | pending | arena/5b8ce14d-poker3 | whole repo | Flagged irregularities do not block merge; they ship on `site/flagged.html`. |
