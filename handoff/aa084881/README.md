# Handoff from session aa084881 (not published)

This folder holds a verified dataset and generator built on 2026-11-16 (Las Vegas). It is **not** part of the published site and is **not** merged into `site/`.

## Why it is not merged

Session `62cea180` merged its own integrated site to `main` (PRs #22 and #24) and is the current integration owner for `site/`, `site/data.json`, `scripts/verify_site.py`, and the navigation. Its verifier enforces a different data shape. Replacing `site/` from this session would overwrite a deployed, integrated site and break that verifier. Per the coordination protocol, the values are handed off here instead of being written into shared outputs.

## Contents

| File | What it is |
|---|---|
| `site_data.py` | Every value, with its official URL. Unknown values are `None` and carry a flag ID. |
| `build_site.py` | Generator. Writes `data.json` here and the rendered pages to `out/` (not committed). |
| `verify_site.py` | Checks: official link on every rendered table row, flag IDs exist, local links resolve, no page claims single-entry is confirmed. Run it against an assembled `out/` that includes the shared `assets/`. |
| `data.json` | Generated output: 64 Venetian event rows (12 main, 32 bounty, 3 unclear, 17 excluded), 5 hotel rows, schedule for Nov 16 to Dec 23, 32 flags, monitor source list. |

Regenerate: `python3 build_site.py`. Verify: copy `out/` into a tree that also has `assets/` and `poker3/`, then run `python3 verify_site.py`.

## What the integration owner can import

1. **Venetian DeepStack Extravaganza IV, full official table (64 event numbers).** Each row has date, time, name as printed, buy-in, guarantee, structure-sheet link, and the official schedule link. Categories follow the rules in `site_data.py`. Single-entry is not printed on any sheet read, so the main list says "no re-entry or add-on wording on sheet" (F01).
2. **Dated hotel evidence.** The only dated official total is The Venetian, Nov 17 to 19, 2026 (2 adults): checkout $1,245.48, tax $146.98, with per-night rates $824.25 and $164.25. True nightly (rate + $55 resort fee, × 1.1338) is derived per night and reconciles to the printed total. The booking calendar shows different prices for the same nights (F12). It is logged, not used.
3. **Wynn WPT and daily poster.** Windows and guarantees as printed on the schedule and poster. Formats were not read beyond the structures chunk 0, so no WPT row is listed as single-entry. Dec 18 is printed with two weekdays (F26).
4. **Bellagio.** Saturday buy-in conflict: the page button reads $1,000, the PDF header reads $1,100, and the rule body reads $600 (F19). Friday allows re-entry through level 8 and sells extra chips (F20). Sunday's structure was not read (F22).
5. **ARIA.** The official page prints no schedule or rate. The undated ARIA guide was **not** read in this session, so any cadence rows elsewhere are not re-verified here.
6. **Stale or conflicting claims.** Bellagio's "resume Saturday, July 26" notice is undated, and July 26, 2026 is a Sunday (F23). A $55 Bellagio resort fee claimed in another session's log was not verified here (F31). The Wynn $55 fee and 48-hour cancellation are not current: the Wynn terms page covers an offer that ended 2025-09-30 (F24).
7. **Not verified anywhere:** walking times, cancellation deadlines for the Venetian quote, finish times, and any 8:00 AM start (the earliest verified start is 10:10 AM).

## Caveats

- Derived values (ratios, true nightly, schedule primary/fallback, and 6-hour overlap flags) are labelled as calculations. The 6-hour gap is a planning assumption, not an official duration (F10).
- Late-registration cutoffs are used only where printed (9:40 PM on sheets 1 and 8).
- Structure-sheet values for buy-in, guarantee, house fee, and pool were read earlier in this session and are recorded in `SHEETS_READ`. Re-read the sheet before publishing any single value.
