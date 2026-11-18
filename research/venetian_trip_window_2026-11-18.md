# Live official re-check: Venetian trip-window schedule

**Checked:** 2026-11-18 UTC using the official Venetian schedule page.  
**Official source:** [DeepStack Extravaganza IV schedule](https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html)  
**Scope:** Schedule-page fields only for the 2026-11-23 through 2026-11-30 trip window: event date, start time, event number, printed name, and any buy-in/guarantee shown in the name. Structure-sheet rule excerpts, chip stacks, level lengths, late-registration cut-offs, hotel prices, and other venues were not re-read in this pass.

## Comparison

The official page states the series dates as November 16–December 23, 2026. Its table entries for November 23–30 were compared with the corresponding Venetian rows in `site/data.json`. All 19 rows matched on the schedule fields within this scope; no schedule correction was needed.

| Date | Official schedule entries compared |
|---|---|
| 2026-11-23 | 11:10 AM, #7, $400 NLH 1A, $75K GTD; 5:10 PM, #8, $200 NLH PKO, $8K GTD |
| 2026-11-24 | 11:10 AM, #7, $400 NLH 1B, $75K GTD; 5:10 PM, #9, $200 NLH Bounty, $8K GTD |
| 2026-11-25 | 11:00 AM, #7, $400 NLH Day 2 Restart; 11:10 AM, #10, $400 NLH, $15K GTD; 5:10 PM, #11, $200 NLH Bounty, $8K GTD |
| 2026-11-26 | 11:10 AM, #12, $300 NLH, $10K GTD; 5:10 PM, #13, $200 NLH Bounty, $8K GTD |
| 2026-11-27 | 11:10 AM, #14, $600 NLH, $30K GTD; 5:10 PM, #15, $200 NLH Bounty, $8K GTD |
| 2026-11-28 | 11:10 AM, #16, $600 NLH Bounty, $30K GTD; 12:10 PM, #17, $400 PLO Bounty, $15K GTD; 5:10 PM, #18, $200 NLH PokerAtlas Valuetown Bounty, $20K GTD |
| 2026-11-29 | 11:10 AM, #19, $400 NLH 1A, $75K GTD; 12:10 PM, #20, $300 PLO Double Board Bomb Pot, $10K GTD; 5:10 PM, #21, $200 NLH Bounty, $8K GTD |
| 2026-11-30 | 11:10 AM, #19, $400 NLH 1B, $75K GTD; 5:10 PM, #22, $200 NLH Bounty, $8K GTD |

The Day 2 Restart rows have no standalone printed guarantee in the schedule table. This pass did not independently verify their structure-sheet values; the earlier qualification in flag F63 remains applicable. The official table publishes neither an event finish time nor a maximum-entry-per-player rule. The 52 sheet-screened candidates remain unconfirmed as strict single-entry events until written venue confirmation is obtained (F31).

## Verification and limits

- Reached both live schedule-page chunks containing November 23–30 and compared all 19 visible table rows with the canonical Venetian entries. The source page's structure links point to official Venetian-hosted PDFs.
- `site/data.json` row-level `lastChecked` values are not advanced by this note: this pass rechecked schedule-page fields, not every rule/structure field carried by each row. Each rule object's own `retrieved` date remains the date its cited official structure sheet was read.
- No value was inferred or changed. This is a dated verification record, not an assertion that the schedule cannot change later.
