# Vegas Poker Planner

Source-first Las Vegas Strip poker trip planner. The canonical GitHub Pages dashboard is in [`site/`](site/) and is
the only directory published by the Pages workflow.

| Page | What it does |
|---|---|
| `site/index.html` | Executive summary: the fixed trip, the primary event per day, and what is and is not confirmed. |
| `site/tournaments.html` | Every published tournament row, with date, venue, category and single-entry filters, a search box and a per-row rule panel. |
| `site/venues.html` | One page per Strip poker room, each with its events and its hotels (`browse.html?view=venue&key=…`). |
| `site/browse.html` | Venue and category subpages, so a bounty event is never mixed in with a plain freezeout. |
| `site/schedule.html` | One realistic primary event per day, a conditional fallback, the recurring room events, and the flagged impossible sequences. |
| `site/hotels.html` | Published rate components, the mandatory resort fee, tax, true cost per night, parking, cancellation deadlines, walking times and the dated rate log. |
| `site/questions.html` | The information still needed before booking, each with the official source behind the answer. |
| `site/suggestions.html` | Proposed improvements with impact, effort and the decision each one needs. |
| `site/flagged.html` | Every irregularity and unverified value, each with a link for manual review. |
| `site/sources.html` | The official source log, every structure sheet with its read status, the morning feed sources and the automated re-check results. |

## Evidence policy

Only official venue and property pages and official PDFs substantiate a value. A structure sheet that prints one buy-in,
one start flight and no re-entry, rebuy, add-on or second-flight clause is recorded as **single entry on the sheet**,
with the excerpt and the retrieval date attached; the site never claims a sheet uses the words “single entry”.
A row with a blank fee or guarantee is always explained by a note or a flag. The guaranteed-pool ÷ entry-fee figure is
a descriptive ratio, never a forecast. Walking minutes are Google Maps walking estimates, because no venue publishes a
walking time. Snapshot: **2026-11-16 UTC**.

## Data pipeline

```sh
python3 scripts/data_source.py        # rebuilds site/data.json from the source modules
```

| Module | Contents |
|---|---|
| `scripts/data_venetian.py` | The 64 official DeepStack Extravaganza IV rows, the NYE rows, and the facts read from all 37 DSE IV structure PDFs. |
| `scripts/data_venues.py` | Wynn daily, WPT and Signature Series rows, Bellagio, MGM Grand, Caesars Palace, Horseshoe and ARIA room events. |
| `scripts/data_hotels.py` | Hotel components, the dated rate log and the walking-route estimates. |
| `scripts/data_source.py` | Assembles `site/data.json`, the fixed trip profile, the day plan and the conflict flags. |

`research/structure_notes.md` records the read log for all 37 DSE IV structure PDFs.

## Scheduled checks

`.github/workflows/checks.yml` runs every morning at 05:00 Pacific:

- `scripts/check_sources.py` fetches every official URL behind the dashboard, stores a SHA-256 of the response and
  flags any source whose body changed. It never changes a tournament value on its own: a changed page is re-read by a
  human first. Results are published as `site/checks.json` and shown on the sources page.
- `scripts/daily_feed.py` pulls the schedule page of each Strip poker room and writes a dated snapshot under
  `site/feed/`, so a morning run can be compared with the previous morning instead of replacing it.

## Run locally

```sh
python3 -m http.server 8000 --directory site
```

Then open `http://localhost:8000`.

## Verification

```sh
python3 scripts/verify_site.py        # official-source, blank-value and link checks over site/data.json
python3 tests/canonical_smoke.py       # page structure plus a headless render check of every page
node --check site/assets/app.js
python3 -m json.tool site/data.json
```

`.github/workflows/verify.yml` runs all of these on every pull request and push to `main`.

## Prior-session artefacts

The repository also keeps earlier dashboards from merged parallel sessions: `docs/`, `verified/`, `planner/`,
`single-entry/`, the root-level pages, and `site/poker3/`. They are prior research artefacts with their own unresolved
rows and flags. They are not the canonical site and are not used as evidence for `site/data.json` unless re-checked
against the venue source. `site/poker3/` is still published at `/poker3/` because it lives inside the Pages artifact;
its conclusions predate this build and are more conservative, so treat it as an archive rather than as current data.

See [`COORDINATION.md`](COORDINATION.md) for ownership, the official source register, the integration history, the
verification record and the open review flags.
