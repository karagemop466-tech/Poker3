# Vegas Poker Planner

Evidence-first Las Vegas poker tournament and hotel planning dashboard. The canonical GitHub Pages site is [`site/`](site/). It preserves official source links and does not infer tournament entry rules, room rates, taxes, or walking times that the reviewed sources do not establish.

## Current snapshot

- The data catalog contains **102 event rows**: all **83 Venetian DeepStack Extravaganza IV scheduled starts** (64 event numbers, Nov. 16–Dec. 23, 2026), plus selected Wynn/WPT, Wynn recurring, Bellagio, and ARIA leads. It is not a complete Las Vegas room inventory.
- **No event is verified as strict single-entry.** A pass requires explicit proof of one entry total and explicit exclusion of re-entry, rebuy, add-on, and paid chip advantage. “One day” and source silence are not proof.
- Eight hotel records and a separate dated search log are included. No usable, comparable date-matched room checkout total was captured; published fees are not room-rate quotes.
- The Dec. 10–14, 2026, two-adult hotel search is a research sample, not travel dates supplied by the user. Thirteen Venetian dates in the parsed row set are reconstructed from omitted date labels and are marked in the dashboard.

## Dashboard features

- Global search across event rows, hotels, venues, official sources, and review flags; independent table search and CSV export.
- Tournament date, venue, and strict-entry filters. A strict-only result can be empty without implying no qualifying event exists elsewhere.
- Separate source-linked venue pages for Venetian, Wynn, Bellagio, and ARIA.
- A local hotel-cost calculator. Room rates and missing tax/fee inputs must be supplied by the user; results are labeled estimates, not official quotes, and are stored only in the current browser's local storage.
- A schedule start-gap checker with a user-selected travel/registration buffer. It does not predict tournament finish times or guarantee a playable itinerary.
- Per-row provenance, a hotel rate-search log, a source-change page, and a flagged-for-review register.

## Run locally

```sh
python3 -m http.server 8000 --bind 0.0.0.0 --directory site
```

Then open `http://localhost:8000`. The separate Poker3 companion is at `/poker3/`.

## Official-source monitor

The scheduled workflow `.github/workflows/monitor-official-sources.yml` polls curated official URLs weekly (Monday at 14:23 UTC) and can also be run manually. It checks only approved official hosts and skips sources explicitly marked `monitor: false` (including dynamic hotel booking searches). HTML is normalized to visible text; PDFs are fingerprinted as bytes. The monitor writes only `site/data/source-monitor.json`; it **never rewrites schedule, price, or eligibility facts**. Detected changes are review signals for a human. When run on `main`, the workflow commits the monitor state so it is visible on the dashboard.

A first run creates the baseline; no baseline is currently asserted. A failed request preserves the last successful content hash and is recorded separately from a source change.

## Verification

Run the offline checks from the repository root:

```sh
python3 scripts/verify_site.py
python3 -m unittest discover -s tests -p 'test_*.py' -v
node --check site/assets/logic.js
node --check site/assets/app.js
node tests/test_site_logic.js
python3 tests/smoke.py
```

The checks validate the 83-row Venetian coverage and date range, unique source IDs, official-source host allowlists, per-event provenance, strict-entry gating, blank unquoted hotel totals, rate-log completeness, local links, monitor state structure, hotel-calculator math, date filters, and schedule-gap logic. No network request is needed for tests.

`.github/workflows/pages.yml` publishes the entire `site/` tree through GitHub Pages. `.github/workflows/verify.yml` runs the offline validation on pull requests and pushes to `main`.

## Repository history and noncanonical research

The repository retains earlier root-level and `docs/` dashboards from merged parallel sessions. They are prior research artifacts with their own unresolved rows/flags; they are not the canonical published site and are not used as evidence for `site/data.json` unless rechecked against the venue source.

`site/poker3/` is an expanded research companion with its own source catalog, schedule planner, and review pages; it remains published alongside the canonical dashboard. The Dec. 10–14, 2026 two-adult window in that companion is also a research sample, not user-provided travel dates.

`planner/`, `verified/`, and `single-entry/` contain earlier session outputs and are not separately published by the current Pages workflow. `data/`, `raw/`, and `scripts/parse_official.py` keep earlier source extracts and parser outputs for audit. See [`COORDINATION.md`](COORDINATION.md) for the shared task board, ownership history, and earlier integration notes.
