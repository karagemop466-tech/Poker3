# Poker3

Las Vegas Strip poker tournament vacation planner — single-entry tournaments only.

## What this is
A source-first static dashboard for evaluating Las Vegas tournament schedules and lodging. It collects upcoming Strip poker tournaments (single entry only — no re-entry, no double buy-in, no add-ons), walking-distance hotels with true cost per night (room rate + resort fee + taxes + parking), an all-day playing schedule, an executive summary, questions that must be resolved before booking, site-improvement suggestions (review before implementing), and a Flagged for Review register.

## Research snapshot
2026-11-16 UTC. Two Arena sessions contributed:

- Session `arena/66708bda-poker3` (earlier): conservative root-level dashboard, deployed to GitHub Pages. Found that aria.com publishes ARIA tournament times (1 p.m. / 7 p.m.) but no date-specific events, buy-ins, guarantees, entry rules, or duration — treated as incomplete, not a qualified single-entry event. Third-party listings not accepted as verification.
- Session `arena/d205f8ec-poker3` (current): 53 single-entry (1Day) events from the Venetian DeepStack Extravaganza IV (Nov 18 – Dec 23, 2026), each linked to the official Venetian schedule and structure-sheet PDFs; multi-entry/re-entry events kept in a separate section; Wynn WPT World Championship Festival reviewed. Hotel true-cost formula with official fees/taxes.

## Verification policy
Every table row carries a link to an official venue/hotel source. Values that cannot be confirmed from an official source are left blank and flagged as unverified — nothing is inferred or filled in. See flagged.html.

## Site (GitHub Pages, root of main)
- index.html — landing page + executive summary
- tournaments.html — single-entry table (main list) + separate multi-entry/re-entry section
- hotels.html — hotel candidates and true-cost-per-night formula
- schedule.html — suggested all-day playing schedule
- questions.html — questions that must be answered before any decision
- suggestions.html — site improvement suggestions (review before implementing)
- flagged.html — irregularities and unverified items
- style.css — stylesheet
- data/tournaments.md, data/hotels.md — source-of-record files
- COORDINATION.md — shared task board with both sessions' claims and work logs
- .github/workflows/pages.yml — Pages deploy workflow (root site on pushes to main; repository Pages settings must permit GitHub Actions)

## Key sources
- Venetian DeepStack Extravaganza IV: https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html
- WPT World Championship: https://www.worldpokertour.com/article/wpt-world-championship-at-wynn-las-vegas-set-for-season-24-finale-with-over-85-events-and-20m-in-gte
- Venetian hotel terms (resort fee, tax, parking): https://www.venetianlasvegas.com/legal/hotel-terms-and-conditions.html
- Wynn stay terms: https://www.wynnlasvegas.com/terms-and-conditions/848654
- ARIA poker times (incomplete source): https://aria.com/en/nightlife.html
