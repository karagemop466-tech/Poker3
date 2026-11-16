# Poker3 · Las Vegas Poker Field Guide

A small, static research dashboard for upcoming Las Vegas poker tournaments, room schedules, hotel fee terms, and route estimates. The main screen applies a conservative **strict-entry** test:

- One entry total for the whole tournament
- No re-entry or rebuy
- No add-on, paid extra stack, or gratuity-for-chips
- Unknown terms stay unverified—not eligible

**Current research result:** no upcoming tournament is verified to satisfy every condition. The site keeps the distinction between known extra-spend rules and missing evidence visible.

## Pages

- `index.html` — snapshot and featured starts
- `schedule.html` — filterable selection of upcoming series events
- `plan.html` — concurrent start windows plus an optional best-case sequence model using the user's own time-per-event assumption; never presented as a guaranteed itinerary
- `rooms.html` — daily poker-room schedules and eligibility notes
- `stay.html` — sample-date hotel/rate comparison and published resort fees
- `routes.html` — third-party walk estimates, labeled as such
- `review.html` — unresolved facts and source conflicts
- `methodology.html` — criteria and source register

## Run locally

No package install or build step is needed. From this directory, serve the static files over HTTP:

```sh
python -m http.server 8000 --bind 0.0.0.0
```

Then open `http://localhost:8000`. The app loads `data/research.json` relative to the site files. The repository's GitHub Pages site is configured to publish the root of `main`.

## Validate

```sh
python tests/smoke.py
```

The smoke test checks the catalog shape, source references, strict-entry result, and local page assets/links.

## Updating research

Edit `data/research.json`. Add a source record before referencing it from an event, room, hotel, or review flag. Keep `meta.asOf` current, preserve exact distinctions between confirmed rules and missing rules, and do not promote an event to `verified` unless a current official source proves every strict-entry condition. Rates and schedules are snapshots and should be rechecked before travel.
