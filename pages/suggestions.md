# Suggestions — Site & Decision-Making Improvements

**Purpose:** A place to review and choose improvement paths BEFORE implementing changes. None of these are implemented yet; each is a proposal for review.
**Status:** Proposed (not implemented)

## Suggestions for the website (this repo)

| # | Suggestion | Expected benefit | Effort | Dependencies | Decision needed? |
|---|------------|------------------|--------|--------------|------------------|
| S1 | Add a "Buy-in filter" toggle (e.g., ≤$200, $201–$500, $501–$1,000, $1,000+) on the tournaments page | Faster identification of best-value events | Low | Tournament table data | No |
| S2 | Add a "Date filter" / calendar view so users can see which single-entry tournaments run on their travel dates | Easier schedule building | Medium | Full event date data | No |
| S3 | Add a "True cost" hotel calculator: user enters room rate, site auto-computes resort fee + tax + parking | Transparent hotel comparison | Low | Hotel fee data | No |
| S4 | Add a conflict-checker for the schedule (warns if two selected events overlap) | Prevents double-booking | Medium | Event start times + durations | No |
| S5 | Add source-link icons on every table row (already planned) | Trust and verifiability | Low | Source URLs | No |
| S6 | Add a "Flagged for review" badge on unverified table cells | Clear data-quality signal | Low | Flagged-items list | No |
| S7 | Add email/calendar export (.ics) of the selected tournament schedule | Helps users plan travel | Medium | Schedule data | No |
| S8 | Add a "My shortlist" feature (save favorite tournaments/hotels to local storage) | Personal planning | Medium | Front-end storage | No |

## Suggestions for gathering missing information

| # | Missing information | How to discover it | Owner | Suggested action |
|---|---------------------|-------------------|-------|------------------|
| M1 | ARIA Poker Open individual event buy-ins, guarantees, and entry rules | Call/visit ARIA poker room or monitor arialasvegas.com/casino/poker (was HTTP 500 on 2026-11-16) | Research | Retry official ARIA page; call ARIA Poker Room at (702) 590-7111 |
| M2 | WPT World Championship per-event re-entry rules (non-marquee events) | Request Wynn/ WPT event structure sheets | Research | Check wynnpoker.com or WPT.com structure sheets |
| M3 | Official hotel room rates + resort fees for specific Nov–Dec 2026 dates | Direct booking on each hotel's official site | User / travel | Book direct; confirm mandatory fees in writing before paying |
| M4 | Exact walking times/routes between hotels and venues | Google Maps / Clark County pedestrian bridge info | User | Walk the route or check map before relying on it |
| M5 | Whether Venetian 1Day events explicitly prohibit re-entry (structure sheets list no re-entry clause, but do not state "no re-entry") | Ask Venetian poker room floor staff / tournament director | Research | Confirm in writing before assuming freezeout |
| M6 | MGM Grand daily $120 NLH tournament details (entry rules, guarantees) | MGM Grand poker room official page | Research | Not currently confirmed from an official source |

## Review process
Before implementing any suggestion above: (1) review benefit vs effort, (2) confirm data sources, (3) update COORDINATION.md, (4) implement on a feature branch, (5) verify the site still builds with no broken links, (6) merge via pull request.
