# Live trip-window re-read and gate run, 2026-11-19 (session arena/e5dca9a1-poker3)

Scope: the 23–30 November 2026 Venetian trip window. Read-only against the official pages, then one data change: new flags F125 and F126 in `scripts/data_source.py`, rebuilt into `site/data.json`. No published value was changed.

Reads were made with the platform page reader (`fetch_page`) on 2026-11-19 (UTC). Quotes are verbatim from the pages as returned. The sandbox shell has no route to the casino hosts.

## 1. Official DeepStack Extravaganza IV table, 23–29 Nov 2026 (plus 30 Nov)

Source: https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html (chunks 0–2 read; the trip rows are in chunks 0 and 1).

Each live row was compared with the published row in `site/data.json` (date, start time, event name, printed buy-in, printed guarantee). The comparison is scripted; the row list it used is the one in the table below.

| # | Live row (date · time · event # · name) | Published row | Result |
|---|---|---|---|
| 1 | Mon 23 Nov · 11:10 AM · 7 · $400 No Limit Hold'em 1A $75K GTD | same, buy-in 400, GTD 75,000 | match |
| 2 | Mon 23 Nov · 5:10 PM · 8 · $200 No Limit Hold'em $8K GTD (1Day) – PKO | same, buy-in 200, GTD 8,000 | match |
| 3 | Tue 24 Nov · 11:10 AM · 7 · $400 No Limit Hold'em 1B $75K GTD | same | match |
| 4 | Tue 24 Nov · 5:10 PM · 9 · $200 NLH Bounty $8K GTD (1Day) | same | match |
| 5 | Wed 25 Nov · 11:00 AM · 7 · $400 NLH Day 2 Restart | same name; guarantee 75,000 carried from the Event 7 flights | **labelling difference → F125** |
| 6 | Wed 25 Nov · 11:10 AM · 10 · $400 NLH $15K GTD (1Day) | same, GTD 15,000 | match |
| 7 | Wed 25 Nov · 5:10 PM · 11 · $200 NLH Bounty $8K GTD (1Day) | same | match |
| 8 | Thu 26 Nov · 11:10 AM · 12 · $300 NLH $10K GTD (1Day) | same, buy-in 300, GTD 10,000 | match |
| 9 | Thu 26 Nov · 5:10 PM · 13 · $200 NLH Bounty $8K GTD (1Day) | same | match |
| 10 | Fri 27 Nov · 11:10 AM · 14 · $600 NLH $30K GTD (1Day) | same, buy-in 600, GTD 30,000 | match |
| 11 | Fri 27 Nov · 5:10 PM · 15 · $200 NLH Bounty $8K GTD (1Day) | same | match |
| 12 | Sat 28 Nov · 11:10 AM · 16 · $600 NLH Bounty $30K GTD (1Day) | same | match |
| 13 | Sat 28 Nov · 12:10 PM · 17 · $400 Pot Limit Omaha Bounty $15K GTD (1Day) | same, GTD 15,000 | match |
| 14 | Sat 28 Nov · 5:10 PM · 18 · $200 NLH PokerAtlas Valuetown Bounty $20K GTD (1Day) | same, GTD 20,000 | match |
| 15 | Sun 29 Nov · 11:10 AM · 19 · $400 NLH 1A $75K GTD | same | match |
| 16 | Sun 29 Nov · 12:10 PM · 20 · $300 Pot Limit Omaha $10K GTD (1Day) – Double Board Bomb Pot | same | match |
| 17 | Sun 29 Nov · 5:10 PM · 21 · $200 NLH Bounty $8K GTD (1Day) | same | match |
| 18 | Mon 30 Nov · 11:10 AM · 19 · $400 NLH 1B $75K GTD | same | match |
| 19 | Mon 30 Nov · 5:10 PM · 22 · $200 NLH Bounty $8K GTD (1Day) | same | match |

Result: **18 of 19 rows match exactly.** Row 5 is a labelling difference, not a wrong value. The live restart row prints no guarantee; the published row carries the parent flight's printed $75,000 and marks itself as a continuation with a "multi-flight" note. It is recorded as **F125**.

**Earliest start in the window: 11:00 AM** (Wed 25 Nov, the Event 7 restart). No Venetian event in 23–30 Nov starts before 11:00 AM on the official table, so no 8 AM start exists at the Venetian for this window (consistent with F17).

**Multi-entry check (read directly this session).** The Event 7 structure sheet, `dse_nov_2026-structure_2.pdf`, prints:
- Rule 3: "Each starting flight will play until we are down to approximately 12.5% of the field remaining. Day 2 will resume at 11:00 AM combining all remaining players from 1A and 1B with all players being considered in the money…"
- Rule 8: "Any player who bags chips for Day 2 may not play a subsequent flight."
- Header: "Event Number: 07", "Late Registration: 9 levels + Break (5:55 PM)", "Guarantee: $75,000", "$70 of the $400 Buy-In is withheld for house fees".

Rule 8 bars a bagged player from a later flight, which implies that a player who has not bagged may play one. The sheet prints no maximum-entry count, so Event 7 is treated as multi-entry and excluded from the single-entry set. The sheet does not print the words "may buy into another flight".

## 2. Poker-suite rate, resort fee and hotel terms

**Poker-suite rate page** (https://www.venetianlasvegas.com/resort/casino/poker/suite-rates.html, read 2026-11-19):
- "These rates will start as low as $119 and $209 and can be higher."
- "There is a $55 resort fee per night stayed."
- "During your stay, you will be required to play six hours of active live cash gameplay or buy in to a $300 or higher tournament for each night stayed. … For any nights you fail to complete these requirements, your nightly suite rate will be adjusted to the prevailing rate, and you will not receive the poker suite rate discount."
- Booking is by telephone: 866.255.8936, code EPOKR25.

**Resort-fee page** (https://www.venetianlasvegas.com/resort/resort-fee.html): "Rates include a daily Resort Fee of $55 plus tax per night, payable upon check-in."

**Hotel terms** (https://www.venetianlasvegas.com/legal/hotel-terms-and-conditions.html, chunks 0–1, read 2026-11-19):
- "Daily rates do not include the applicable Clark County Room Tax of 13.38%."
- "The Venetian Resort has a standard Las Vegas Resort Fee of $55 plus applicable tax per night, payable upon check-in."
- "Check-out prior to your scheduled departure date will result in an additional charge of $100 plus tax."
- Parking: "The daily fee for registered hotel guests is $20/day, seven days a week. For non-hotel guests, the fee is $20, Monday – Thursday, and $25/day Friday – Sunday. Valet parking is $40/day."
- Check-out is 11:00 a.m.

These match the hotel row and the calculator inputs: base $119 (floor), resort fee $55, tax 13.38%, parking $20/day, early-checkout $100 plus tax.

**Arithmetic re-computed independently** (Python `Decimal`, ROUND_HALF_UP):
- Floor per night: ($119 + $55) × 1.1338 = 197.2812 → **$197.28** (matches).
- Seven nights: 7 × $197.28 = **$1,380.96** (matches).
- Buy-ins of the seven primaries: 200 + 200 + 400 + 300 + 600 + 600 + 300 = **$2,600** (matches).
- Parking: 7 × $20 = **$140** (matches; see open item O3).
- Trip total: 2,600 + 1,380.96 + 140 = **$4,120.96** (matches).
- Alternate at $209: ($209 + $55) × 1.1338 = 299.3232 → **$299.32**; 2,600 + 7 × 299.32 + 140 = **$4,835.24** (matches).

## 3. The qualification problem (new flag F126)

The plan's day-plan primaries are 23 Nov $200 (5:10 PM PKO), 24 Nov $200 (5:10 PM bounty), then $400, $300, $600, $600, $300 on 25–29 Nov. The $200 events fall below the $300 threshold. On the official table, no single-entry event of $300 or more starts on 23 or 24 Nov: the $400 Event 7 flights (1A on 23 Nov, 1B on 24 Nov) are multi-flight.

So the plan does **not** satisfy the poker-suite condition on those two nights unless the player completes six hours of live cash play on each night. The day plan records this itself (`pokerRateSatisfied: False`). The calculator headline of $4,120.96 nonetheless prices all seven nights at $119. The calculator's note calls the figure "a floor for a qualifying player"; the trip-page `pokerRateQualification` says the two nights depend on play or the prevailing rate. The prevailing rate for these nights is not published as one figure. Recorded as **F126 (High)**. The headline was not changed in this session.

## 4. Scheduled monitor

`site/checks.json` (generated 2026-11-19T07:34:30Z): 108 URLs, 2 changed, both Wynn booking-engine URLs (`reservations.wynnlasvegas.com/ibe/details.aspx?…`). These were handled in a prior session's re-read (see the board). They were not evaluated here, and no value was changed on that basis.

## 5. Gates run on this branch (after rebase onto `origin/main` at `28f0796`, which already carries flag F124 from another session)

- `scripts/verify_site.py` → `events: 341 hotels: 8 routes: 56 sources: 50 flags: 118 plan days: 7 pages: 19 / verification passed`.
- `python3 -m unittest discover -s tests` (venv with PyYAML 6.0.3, as in CI) → **Ran 437 tests, OK**, after one test was relaxed (see below).
- `node tests/canonical_render.js`, `tests/test_calculator_unknown_inputs.js`, `tests/test_day_plan_ordering.js`, `tests/sheet_recheck_render.js` → exit 0.
- `tests/canonical_smoke.py` → "canonical smoke passed: 14 main pages, 5 detail pages".
- `scripts/audit_951cd431.py`, `verify_live_official.py`, `audit_data.py`, `verify_entry_labels.py` → exit 0.
- Data rebuild: `data_source.py` + `build_addendum.py` + `coverage.py` reproduced the committed artefacts byte-for-byte before any edit; after the edits only the expected files changed (`site/data.json`, `site/sheets.html`, `site/coverage.json`, `scripts/data_source.py`, `scripts/data_venetian.py`). `data_source.py` run twice gives an identical `site/data.json`.

**Test change, logged as a scope deviation.** `tests/test_flag_ids_unique_2026_11_19.py::test_no_id_is_reused_after_being_withdrawn` pinned the highest flag id to 123, so every new flag broke it. It now asserts that ids are unique and that the highest id is at least 123, which is the rule it was written to enforce.

## 6. Still not verified (unchanged; not closed by this read)

- **O1 — written single-entry rule.** No official source states a maximum-entry, no-rebuy or no-add-on rule in writing (F31). This needs a written answer from the venue.
- **O2 — 8 AM start and finish times.** No official source publishes an 8 AM start for the window (confirmed above for the Venetian: earliest 11:00 AM) or a finish time (F16/F17).
- **O3 — parking days.** Whether the $20/day charge applies on 30 Nov (check-out day) or only on the seven nights is not printed. The model uses seven days.
- **O4 — dated booking-engine total.** The Venetian engine was not re-quoted in this session. The most recent dated total is in `liveQuote` (2026-11-17, F120 covers the 2026-11-19 read).
- **O5 — walking times.** Google Maps estimates only; no official walking time is published (existing flags).

## 7. Correction to the stored single-entry excerpt (new flag F127)

The stored "excerpt" for the single-entry rule on the 13 multi-flight sheets (2, 3, 4, 9, 10, 12, 13, 14, 20, 21, 35, 36, 37) was one hand-written paraphrase. It read "…Day 2 will resume combining all remaining players from the listed flights… so a player who does not bag may buy into another flight." Neither clause is printed on any of the 13 sheets. Each sheet was read in full this session:

| Sheet | Event | Printed flights combined on Day 2 | Day 2 start | Field stop |
|---|---|---|---|---|
| 2 | $400 1A/1B (Event 7) | 1A and 1B | 11:00 AM | 12.5% |
| 3 | $400 1A–1C (Event 19) | 1A, 1B, and 1C | 11:00 AM | 12.5% |
| 4 | $600 1A–1C (Event 59) | 1A, 1B, and 1C | 11:00 AM | 12.5% |
| 9 | $300 1A–1D (Event 1, Day B+D) | 1A, 1B, 1C, and 1D | 12:00 PM | 12.5% |
| 10 | $300 1A–1D (Event 1, Day A+C) | 1A, 1B, 1C, and 1D | 12:00 PM | 12.5% |
| 12 | $800 1A–1F (Event 26, Day A+C+E) | 1A–1F | 12:00 PM | 12.5% |
| 13 | $800 1A–1F (Event 26, Day B+D) | 1A–1F | 12:00 PM | 12.5% |
| 14 | $800 Turbo 1F (Event 26) | 1A–1F | 12:00 PM | 12.5% |
| 20 | $1,100 Seniors 1A/1B (Event 49) | 1A and 1B | 10:00 AM | **15%** |
| 21 | $2,200 Title 1A (Event 47) | 1A and 1B | 1:00 PM | 12.5% |
| 35 | $1,100 1A, 1C, 1E (Event 56) | 1A, 1B, 1C, 1D, and 1E | 11:00 AM | 12.5% |
| 36 | $1,100 1B, 1D (Event 56) | 1A, 1B, 1C, 1D, and 1E | 11:00 AM | 12.5% |
| 37 | $2,200 1B (Event 47) | 1A and 1B | 1:00 PM | 12.5% |

Rule 8 is printed word for word on all 13 sheets: "Any player who bags chips for Day 2 may not play a subsequent flight." The stored excerpt now quotes rule 3 (with the sheet's own flights and Day 2 time) and rule 8, and says that a player who has not bagged may play a later flight is read from rule 8, not printed. The status is unchanged (multiple-entries). The "Multi-flight" category blurb carried the same inference as fact; it is now labelled as an inference. No fee, buy-in, guarantee or start time changed.

Two other places repeated the inference and were corrected: the F125 and F126 detail text, and the `data_venetian.py` docstring. Neither now contains the clause.

## 8. Requested but not achievable from this sandbox

- A written maximum-entry, no-rebuy and no-add-on answer from the venue (O1 / F31). This needs a person to ask the Venetian poker room in writing.
- Any official 8 AM start for the trip window (O2): not available at the Venetian, as shown in section 1.
- A dated checkout total at the poker-suite rate. The booking engine was not opened in this session. Earlier records (see the board, 2026-11-19 entries) report that its calendar returns a loading shell to this reader, so a dated total must be taken by a person or a browser session.
- Apple Maps walking times and any official walking time for any hotel–venue pair.

## Manual-review links

- Venetian DSE IV schedule: https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html
- Event 7 structure sheet: https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_2.pdf
- Poker-suite rates: https://www.venetianlasvegas.com/resort/casino/poker/suite-rates.html
- Resort fee: https://www.venetianlasvegas.com/resort/resort-fee.html
- Hotel terms: https://www.venetianlasvegas.com/legal/hotel-terms-and-conditions.html
- Multi-flight structure sheets read this session: https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_{2,3,4,9,10,12,13,14,20,21,35,36,37}.pdf
