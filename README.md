# Vegas Poker Planner

Source-first research dashboard for official Las Vegas poker tournament schedules and Strip-area lodging. The canonical GitHub Pages dashboard is in [`site/`](site/) and includes Overview, Tournaments, Day plan, Hotels, Trip cost, Venues (one page per room), Sources, Open questions, Suggestions, Flagged for review, and Change monitor.

The pages are **generated**. `scripts/build_site.py` reads the curated data files in `data/` and writes `site/data.json` plus every page. `site/data.json` is never edited by hand.

```sh
python3 scripts/curate_dse_iv.py      # transcribe the official Venetian DSE IV schedule and 37 structure sheets
python3 scripts/reconcile_dse_iv.py   # check all 94 rows against the official schedule PDF and the official event page
python3 scripts/build_site.py         # regenerate site/data.json and every page
python3 scripts/verify_site.py        # check sources, blanks, totals, links and navigation
python3 tests/test_canonical_site.py  # render-level checks on the generated pages
```

**Entry terms.** Every tournament row carries the sheet's own wording for four separate
questions: one entry, re-entry, add-on and rebuy, plus any paid chip boost. A sheet that is
silent is reported as silent. "1Day" is not proof of a single entry, and neither is the
absence of a re-entry rule.

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

Run `python3 scripts/verify_site.py`, `python3 scripts/reconcile_dse_iv.py`,
`python3 tests/test_canonical_site.py`, `node --check site/assets/app.js`, and
`python3 -m json.tool site/data.json`. Every canonical tournament and hotel row links to an
official source. See [`COORDINATION.md`](COORDINATION.md) for ownership, official source
register, integration history, verification and open review flags.

## Changing the data

1. Edit the curated file in `data/` (`venetian_dse_iv.json`, `rooms.json`, `hotels.json`,
   `routes.json`, `sources.json`, `flags.json`) with values read from an official source.
2. Record the source URL and the retrieval date in the same record.
3. Run `python3 scripts/build_site.py` to regenerate the site.
4. Run the verification commands above. A value that is not supported must stay blank and
   get an entry in `data/flags.json`.

To re-read a hotel rate for your own dates:

```sh
python3 scripts/check_hotel_rates.py --list
python3 scripts/check_hotel_rates.py --hotel horseshoe \
    --arrival 2026-12-10 --departure 2026-12-14 --write
```

The tool reads the property's own booking engine and appends a dated observation to the rate
log. It never invents a rate: if the engine will not return a price for the requested dates,
it records nothing and says why.

Official URLs are re-checked on a schedule by `scripts/check_sources.py`, which records the
retrieval time, the HTTP status and a content hash for each one. A changed hash is a review
signal, not proof that a tournament value changed.

## Expanded Poker3 research companion

`site/poker3/` adds a separate, source-linked Las Vegas field guide with tournament filters, a cautious date planner, room schedules, a sample hotel/fee comparison, route estimates, and a flagged-review register. The current live Pages setting still reports legacy `main`-root publishing, so the verified public path is [`/site/poker3/`](https://karagemop466-tech.github.io/Poker3/site/poker3/); the canonical dashboard at `/` is preserved. The existing Actions workflow uploads `site/`, where the same companion is available at `/poker3/` if Pages is switched to that source. The Dec. 10–14, 2026 two-adult hotel window is a research sample, not user-provided travel dates, and no strict-entry event is verified.

Run `python3 tests/smoke.py` to validate this companion. When serving the repository's `site/` directory locally, open `http://localhost:8000/poker3/`.

## Strip planner pages (session e125b4a2)

`planner/` holds this session's pages: landing page, Venetian DeepStack Extravaganza IV single-entry table with per-row official source links, re-entry table, hotels, schedule, executive summary, suggestions, Q&A, and flagged-for-review. Research tables behind them are in `data/tournaments.md`, `data/hotels.md`, `data/schedule.md`, and `pages/*.md`. These files are **not** published by `.github/workflows/pages.yml`, which deploys only `site/`. Publishing `planner/` would need a user decision.

## Single-entry site (session arena/d205f8ec-poker3)

`single-entry/` holds the single-entry Strip tournament planner: 1-day main list (53 rows; 47 cash events plus 5 satellites and 1 two-day event, each labelled), excluded events, hotel true-cost formula, schedule, questions, suggestions and flagged-for-review. Start at `single-entry/index.html`. Every row links an official Venetian source; all 22 main-list structure sheets were read in full. Single entry is not printed on those sheets, so the page says "no re-entry or add-on wording", not "single entry confirmed". This folder is **not** published by `.github/workflows/pages.yml` (which deploys only `site/`). Publishing it needs a user decision.
