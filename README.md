# Poker3

Las Vegas Strip poker tournament vacation planner — single-entry tournaments only.

## What this is
A static GitHub Pages site that collects, organizes, and analyzes upcoming Las Vegas Strip poker tournaments (single entry only — no re-entry, no double buy-in, no add-ons), walking-distance hotels with true cost per night (room rate + resort fee + taxes + parking), an all-day playing schedule, an executive summary, a questions/unknowns list, site-improvement suggestions (review before implementing), and a Flagged for Review page.

## Site structure (GitHub Pages)
- `index.html` — landing page + executive summary
- `pages/tournaments.html` — single-entry tournament table (main list) + separate multi-entry/re-entry section
- `pages/hotels.html` — hotel candidates and true-cost-per-night formula
- `pages/schedule.html` — suggested all-day playing schedule
- `pages/questions.html` — questions that must be answered before any decision
- `pages/suggestions.html` — site improvement suggestions (review before implementing)
- `pages/flagged.html` — irregularities and unverified items
- `css/style.css` — site stylesheet
- `data/tournaments.md` — tournament source-of-record with official links
- `data/hotels.md` — hotel source-of-record with official links
- `COORDINATION.md` — shared task board (status, sources, verification)

## Verification policy
Every table row carries a link to an official source. Values that cannot be confirmed from an official source are left blank and flagged as unverified — nothing is inferred or filled in.

## Sources
- Venetian DeepStack Extravaganza IV: https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html
- WPT World Championship: https://www.worldpokertour.com/article/wpt-world-championship-at-wynn-las-vegas-set-for-season-24-finale-with-over-85-events-and-20m-in-gte
- Venetian hotel terms (resort fee, tax, parking): https://www.venetianlasvegas.com/legal/hotel-terms-and-conditions.html
- Wynn stay terms: https://www.wynnlasvegas.com/terms-and-conditions/848654
