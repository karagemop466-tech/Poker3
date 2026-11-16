# Poker3

Las Vegas Strip poker tournament planner — live upcoming single-entry tournaments, hotels within walking distance, all-day schedules, and verified sources.

**Goal:** Collect, organize, and analyze live upcoming poker tournaments near the Las Vegas Strip; find the best tournaments by cost to enter vs prize pool (single entry only); keep re-entry/double-buy-in/add-on tournaments in a separate section; find hotels within a 30-minute walk with true per-night cost (room + resort fee + tax + parking); build an all-day playing schedule; publish a GitHub Pages site.

## Site (GitHub Pages)
- `index.html` — landing dashboard
- `tournaments.html` — single-entry table (recommended) + separate re-entry table
- `hotels.html` — hotel table with true cost per night
- `schedule.html` — all-day single-entry schedule
- `executive-summary.html` — key findings
- `suggestions.html` — improvement proposals (review before implementing)
- `q-and-a.html` — pre-decision questions/information/answers
- `flagged-for-review.html` — unverified items & irregularities

## Data files
- `data/tournaments.md` — verified tournament tables (Venetian DeepStack Extravaganza IV + WPT World Championship)
- `data/hotels.md` — hotel research
- `data/schedule.md` — schedule research

## Verification policy
Every table row links to an official source. Values not confirmed from an official source are left blank and flagged on the Flagged for Review page. Nothing is inferred or filled in.

**Research date:** 2026-11-16
**Branch:** `arena/e125b4a2-poker3`
