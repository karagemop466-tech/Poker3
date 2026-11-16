# Poker3 — Las Vegas Strip poker trip planner

Source-first static site for Las Vegas Strip poker tournaments and lodging. Start at [Overview](index.html).

## Pages (root site, GitHub Pages)

- [Overview](index.html): executive summary and entry points
- [Tournaments](tournaments.html): 1-day main list (Venetian DeepStack Extravaganza IV, Nov 18 – Dec 23, 2026), plus excluded events grouped by reason, including the Wynn WPT festival
- [Schedule](schedule.html): verified start times and a sample day plan. No all-day 8 AM plan is possible because no 8 AM start is verified
- [Hotels](hotels.html): true cost per night formula with official resort-fee and tax inputs. Room rates are not published for the dates, so they are blank and flagged
- [Questions](questions.html): information needed before decisions, plus ways to find it
- [Suggestions](suggestions.html): site improvements, for review before any change
- [Flagged for review](flagged.html): irregularities, conflicts and unverified items. These do not block merges

## Parallel site (`docs/`)

Session `arena/8fc8e9f1-poker3` built a second, data-first site in `docs/` (JSON data files plus 10 pages). It is kept unchanged and is published at `/docs/` by the same Pages workflow. The two sites use the same source policy but different layouts. Which one to keep is a user decision (see COORDINATION.md).

## Data files

- `data/tournaments.md`: main list and excluded lists with sources
- `data/hotels.md`: hotel fee components and blank room-rate rows
- `docs/data/*.json`: the parallel site's data (sources, tournaments, hotels, questions, suggestions, flags)

## Verification policy

- Every table row carries a link to an official venue, hotel or structure-sheet source.
- A value that cannot be confirmed from an official source is left blank and flagged. Nothing is inferred.
- Third-party listings (Hendon Mob, PokerAtlas, PokerNews, reddit and similar) are not used for any value. Their conflicts are listed on the flagged page.
- "Single entry" is not printed on the Venetian structure sheets. The main list therefore says "no re-entry or add-on wording on the sheet". It does not claim that single entry is confirmed. See flag F1.

## Research snapshot

2026-11-16 UTC. Sessions that contributed to this branch:

- `arena/66708bda-poker3`: first root dashboard, conservative verification stance, GitHub Pages deploy (PRs #1 and #2).
- `arena/93641c21-poker3`: Venetian main list, excluded-by-reason tables and a 19-item flagged register (PR #6).
- `arena/8fc8e9f1-poker3`: `docs/` site and data (PR #8).
- `arena/d205f8ec-poker3`: this branch. 1-day main list checked row by row against all 22 structure sheets, hotel true-cost formula, questions, suggestions, and integration of the work above (PR #5).

Full logs and PR records are in [COORDINATION.md](COORDINATION.md).

## Key sources

- Venetian DeepStack Extravaganza IV schedule: https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html
- Venetian resort fee: https://www.venetianlasvegas.com/resort/resort-fee.html
- Venetian hotel terms (tax, parking): https://www.venetianlasvegas.com/legal/hotel-terms-and-conditions.html
- WPT World Championship festival: https://www.worldpokertour.com/article/wpt-world-championship-at-wynn-las-vegas-set-for-season-24-finale-with-over-85-events-and-20m-in-gte
- Wynn stay terms: https://www.wynnlasvegas.com/terms-and-conditions/848654

## Deployment

`.github/workflows/pages.yml` publishes the repository root to GitHub Pages on pushes to `main`. Repository Pages settings must allow GitHub Actions.
