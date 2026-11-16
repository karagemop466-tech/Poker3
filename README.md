# Vegas Poker Trip Planner

Source-first static dashboard for Las Vegas poker tournaments and lodging. Start at [Overview](index.html). Pages:

- [Tournaments](tournaments.html): single-start main list (Venetian DeepStack Extravaganza IV), plus excluded events grouped by reason
- [Schedule](schedule.html): verified start times only; no all-day route, because finish times are unpublished
- [Hotels](hotels.html): official price/fee template; currently unverified
- [Questions & suggestions](questions.html): open information gaps and proposed site improvements (for review, not implemented)
- [Flagged for review](flagged.html): irregularities and conflicts; these do not block merges

**Data policy.** Only official venue, hotel, and tournament pages substantiate values. Unknown values stay blank and are flagged. Events are not called single-entry unless the official terms say so; the current main list says no sheet states it explicitly. Schedule information is not a booking guarantee.

**Research snapshot:** 2026-11-16 UTC. See [COORDINATION.md](COORDINATION.md) for the work log, branch and PR records.

The GitHub Pages workflow (`.github/workflows/pages.yml`) deploys the root site on pushes to `main`.
