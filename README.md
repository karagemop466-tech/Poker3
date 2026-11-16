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

## Strip planner pages (session e125b4a2)

`planner/` holds this session's pages: landing page, Venetian DeepStack Extravaganza IV single-entry table with per-row official source links, re-entry table, hotels, schedule, executive summary, suggestions, Q&A, and flagged-for-review. Research tables behind them are in `data/tournaments.md`, `data/hotels.md`, `data/schedule.md`, and `pages/*.md`. These files are **not** published by `.github/workflows/pages.yml`, which deploys only `site/`. Publishing `planner/` would need a user decision.
