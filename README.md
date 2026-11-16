# Vegas Poker Planner

Source-first research dashboard for official Las Vegas poker tournament schedules and Strip-area lodging. The canonical GitHub Pages dashboard is in [`site/`](site/) and includes Overview, Tournaments, Hotels, Day plan, Open questions, Suggestions, and Flagged for review.

The repository also retains earlier root-level and `docs/` dashboards from merged parallel sessions. They are prior research artifacts with their own unresolved rows/flags; they are not the canonical site artifact and are not used as evidence for `site/data.json` unless rechecked against the venue source.

**Evidence policy:** only official venue/hotel pages and official PDFs substantiate canonical findings. “1Day” is not proof of single entry. Unknown entry rules, unpriced hotel totals, and unverified walking times remain flagged or blank. Guarantees are not forecasts of actual payouts. Snapshot: 2026-11-16 UTC.

## Run locally

```sh
python3 -m http.server 8000 --directory site
```

Then open `http://localhost:8000`.

## GitHub Pages

`.github/workflows/pages.yml` publishes the static `site/` directory on pushes to `main`; GitHub Pages must be enabled with GitHub Actions as its source. The workflow does not scrape or synthesize schedule data.

## Verification and sources

Run `python3 scripts/verify_site.py`, `node --check site/assets/app.js`, and `python -m json.tool site/data.json`. Every canonical tournament and hotel row links to an official source. See [`COORDINATION.md`](COORDINATION.md) for ownership, official source register, integration history, verification and open review flags.

## Expanded Poker3 research companion

`site/poker3/` adds a separate, source-linked Las Vegas field guide with tournament filters, a cautious date planner, room schedules, a sample hotel/fee comparison, route estimates, and a flagged-review register. It is included automatically in the existing Pages artifact at `/poker3/`; the canonical dashboard at `/` is preserved. The Dec. 10–14, 2026 two-adult hotel window is a research sample, not user-provided travel dates, and no strict-entry event is verified.

Run `python3 tests/smoke.py` to validate this companion. When serving the repository's `site/` directory locally, open `http://localhost:8000/poker3/`.

## Strip planner pages (session e125b4a2)

`planner/` holds this session's pages: landing page, Venetian DeepStack Extravaganza IV single-entry table with per-row official source links, re-entry table, hotels, schedule, executive summary, suggestions, Q&A, and flagged-for-review. Research tables behind them are in `data/tournaments.md`, `data/hotels.md`, `data/schedule.md`, and `pages/*.md`. These files are **not** published by `.github/workflows/pages.yml`, which deploys only `site/`. Publishing `planner/` would need a user decision.

## Single-entry site (session arena/d205f8ec-poker3)

`single-entry/` holds the single-entry Strip tournament planner: 1-day main list (53 rows; 47 cash events plus 5 satellites and 1 two-day event, each labelled), excluded events, hotel true-cost formula, schedule, questions, suggestions and flagged-for-review. Start at `single-entry/index.html`. Every row links an official Venetian source; all 22 main-list structure sheets were read in full. Single entry is not printed on those sheets, so the page says "no re-entry or add-on wording", not "single entry confirmed". This folder is **not** published by `.github/workflows/pages.yml` (which deploys only `site/`). Publishing it needs a user decision.
