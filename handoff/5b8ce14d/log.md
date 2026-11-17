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

## Progress record (2026-11-17 UTC)

Commits on `arena/5b8ce14d-poker3`: `dfef263` claim → `39ea638` T1 → `da255ae` T2 → `b3477cc` T1 cleanup and T2 record fix.

### T1 — F39 room tax
- County per-property rows are in `scripts/data_hotels.py` as reference text only. `taxRate` is still blank for every property (policy: only a figure the property prints).
- Read and cited: Appendix III chart "Resort Hotel in SD & PGC" at 13.38%; ARIA 3730 Las Vegas Blvd S; Bally's 3645 Las Vegas Blvd S; Caesars Palace licence 1136233.RES-001 (printed as "35/0 Las Vegas Blvd S").
- **Correction (self-found):** `39ea638` and the first draft of this log cited licence numbers and street numbers for Wynn, Bellagio, MGM Grand, ARIA's licence, Bally's licence and Venetian, plus a "Rates Effective 3-1-17" label and a "re-read line by line" claim. None of those values was read in this session. `b3477cc` removes them from `data_hotels.py`, `data_source.py` (F39) and `raw/`.
- The county guide read is dated July 2021 (chunks 0 and 3–11 of 12). It is not a 2026 confirmation.
- Horseshoe stays open. Bally's shares its street address (3645 Las Vegas Blvd S), but the county table uses the former name, so that is not a licence for Horseshoe.
- Caesars fee check: $7.35 on $54.95 and Horseshoe $6.68 on $49.95, both 13.38% to the cent. This is corroboration only.

### T2 — Strip room coverage and F17
- Official Caesars article (dated July 17, 2026; chunks 0–1 of 3 read) gives Caesars Palace: 10 a.m., 2 p.m., 6 p.m., 9 p.m., $100 buy-in, $1,000 guarantee, $50 add-on at the first break. It gives Horseshoe: 9 a.m., 11 a.m., 2 p.m., 5 p.m., 8 p.m., 11 p.m., buy-in not printed. These match the existing rows in `site/data.json`; no event rows changed.
- **F17 stands.** The earliest official start found is Horseshoe at 9:00 AM. No official 8 AM start was found.
- **F77 (new):** Planet Hollywood's poker room closed after Jan 31, 2026. Caesars' article names only Caesars Palace and Horseshoe. Planet Hollywood's poker pages returned HTTP 500 on this date. Source is the Review-Journal (third-party, citing Caesars).
- **F78 (new):** Resorts World's official pages read this session (`/gaming/casino-events/`, `/gaming/poker-room/poker-room-dining/`, the eblast page) show no poker tournament schedule. `/poker`, `/casino/poker/` and `/poker-room/` returned no page. Third-party times and buy-ins conflict, so no row is published.
- Flamingo: no official source found. Its status remains unresolved.
- `rwlasvegas.com` was added to the official-host allowlist (`scripts/verify_site.py`, test file) because it is the property's own site.
- **Scope note:** the claim listed `scripts/data_venues.py` and Paris. Neither was changed. Paris was not checked. Flamingo, Paris and Resorts World remain unresolved, and the rooms-on-site list is not expanded.

### Gate (on `b3477cc`)
- `scripts/data_source.py` regenerated `site/data.json` (341 events, 8 hotels, 15 routes, 43 sources, 74 flags). `scripts/build_addendum.py` regenerated `site/sheets.html`.
- `verify_site.py` passed. `audit_951cd431.py`: 0 failures. `verify_live_official.py`: 0 failures. `audit_data.py`: passed. `canonical_smoke.py`: passed.
- unittest: 129 OK.

### Open items (not blocking merge; shown on `site/flagged.html`)
- F31 (no written one-entry cap), F16 (no published finish times), F32 (walking times are Google Maps estimates), F56 (Wynn Signature structures unpublished), F17 (no 8 AM start), F39 (room-tax % blank; county reference only; the county listing is dated July 2021), F77, F78.
- Older flags (not touched here): a Wynn sheet note says "re-read line by line on 2026-11-17", which is unverified in the same way as the F39 wording. Walking-route origin addresses (Wynn 3131, Bellagio 3600) predate T1 and are used only in Maps links.

### Open next steps
1. Open PR to `main`, check the `verify` workflow, merge with `--merge`, and check the Pages deploy.
2. Questions and suggestions for the user are in the site's Questions and Suggestions sections (`site/`). Nothing is implemented from suggestions until the user chooses.
