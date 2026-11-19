# Venetian DeepStack Extravaganza NYE — independent live capture, 2026-11-19 (UTC)

Source: https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-dec-2026.html
Read: 2026-11-19 (UTC) by session `arena/7d96049f-poker3`, reader chunks 0 and 1 of the page reader's
markdown conversion, both chunks.

Page header lines reproduced verbatim:

```
# DeepStack Extravaganza NYE
**December 24, 2026 – January 10, 2027**
More than $1.1 Million in guaranteed tournament prize pools
```

Why this file exists. This is the only official page behind the 49 Venetian New Year's Eve rows in
`site/data.json`, and all 49 of those rows carried `lastChecked 2026-11-17` — the last row group in the
catalog that had not been re-read since the 17 November pass. `scripts/verify_nye_live_2026_11_19.py`
compares this transcription field by field against those published rows, and
`tests/test_nye_live_2026_11_19.py` fails if they drift apart. The verbatim reader output, including the
misspelled weekday labels, is kept in `raw/venetian_dse_nye_schedule_live_2026-11-19_7d96049f.md`.

Reading rules (no inference): the page prints no buy-in column and no guarantee column, so the buy-in is
the figure the event name itself begins with and the guarantee is the `$nK GTD` token inside the name.
`Structure` is the number in the Structures column, i.e. `dse_dec_2026-structure_<n>.pdf`. Every Results
cell is blank or an em dash; no result is published, so none is recorded.

Two printed defects are reproduced as served, not corrected:

- Three rows dated "December 26" carry the year **2025** in the Date column. The series header says
  "December 24, 2026 – January 10, 2027", and the row's own weekday label says Saturday, which is
  2026-12-26 (2025-12-26 was a Friday). The Date column below therefore carries 2026-12-26 and the year
  on the page is flagged (F41, re-confirmed still present on the live page on 2026-11-19).
- Two rows dated January 5, 2027 print the weekday as **"Tuesaday"**. 2027-01-05 is a Tuesday, so the
  label is a typo in the page, not a date conflict.

| # | Date | Time | Event | Name | Structure |
|---|---|---|---|---|---|
| 1 | 2026-12-24 | 11:10 AM | 1 | $400 No Limit Hold'em $15K GTD (1Day) | 1 |
| 2 | 2026-12-24 | 5:10 PM | 2 | $200 No Limit Hold'em Bounty $8K GTD (1Day) | 2 |
| 3 | 2026-12-25 | 11:10 AM | 3 | $400 No Limit Hold'em $15K GTD (1Day) | 1 |
| 4 | 2026-12-25 | 5:10 PM | 4 | $200 No Limit Hold'em Bounty $8K GTD (1Day) | 2 |
| 5 | 2026-12-26 | 11:10 AM | 5 | $600 No Limit Hold'em Bounty $40K GTD (1Day) - $200 bounties to start & $500 bounties in the money | 3 |
| 6 | 2026-12-26 | 3:10 PM | 6 | $260 NLH Milestone Satellite (1Day) - Awards 1 in 5 (20%) Direct Entry into Event # 08 | 4 |
| 7 | 2026-12-26 | 6:10 PM | 7 | $260 NLH Milestone Satellite (1Day) - Awards 1 in 5 (20%) Direct Entry into Event # 08 | 4 |
| 8 | 2026-12-27 | 11:10 AM | 8 | $1,100 No Limit Hold'em 1A $300K GTD - Ante Up Championship | 6 |
| 9 | 2026-12-27 | 3:10 PM | 9 | $260 NLH Milestone Satellite (1Day) - Awards 1 in 5 (20%) Direct Entry into Event # 08 | 4 |
| 10 | 2026-12-27 | 6:10 PM | 10 | $260 NLH Milestone Satellite (1Day) - Awards 1 in 5 (20%) Direct Entry into Event # 08 | 4 |
| 11 | 2026-12-28 | 11:10 AM | 8 | $1,100 No Limit Hold'em 1B $300K GTD - Ante Up Championship | 6 |
| 12 | 2026-12-28 | 3:10 PM | 11 | $260 NLH Milestone Satellite (1Day) - Awards 1 in 5 (20%) Direct Entry into Event # 08 | 4 |
| 13 | 2026-12-28 | 6:10 PM | 12 | $260 NLH Milestone Satellite (1Day) - Awards 1 in 5 (20%) Direct Entry into Event # 08 | 4 |
| 14 | 2026-12-29 | 11:10 AM | 8 | $1,100 No Limit Hold'em 1C $300K GTD - Ante Up Championship | 6 |
| 15 | 2026-12-29 | 5:10 PM | 13 | $200 No Limit Hold'em Bounty $8K GTD (1Day) | 2 |
| 16 | 2026-12-30 | 11:00 AM | 8 | $1,100 No Limit Hold'em Ante Up Day 2 Restart - Play Down to Final 7 - Streamed Final Table (POKERGO) | 6 |
| 17 | 2026-12-30 | 11:10 AM | 14 | $600 No Limit Hold'em $50K GTD (1Day) | 12 |
| 18 | 2026-12-30 | 3:10 PM | 15 | $200 NLH Milestone Satellite (1Day) - Awards Direct Entry into Event # 20 | 5 |
| 19 | 2026-12-30 | 6:10 PM | 16 | $200 NLH Turbo Milestone Satellite (1Day) - Awards Direct Entry into Event # 20 | 7 |
| 20 | 2026-12-31 | 10:00 AM | 8 | $1,100 No Limit Hold'em Ante Up Day 3 Restart - Streamed Final Table (POKERGO) | 6 |
| 21 | 2026-12-31 | 11:10 AM | 17 | $400 No Limit Hold'em $15K GTD (1Day) | 1 |
| 22 | 2026-12-31 | 3:10 PM | 18 | $200 NLH Milestone Satellite (1Day) - Awards Direct Entry into Event # 20 | 5 |
| 23 | 2026-12-31 | 6:10 PM | 19 | $200 NLH Turbo Milestone Satellite (1Day) - Awards Direct Entry into Event # 20 | 7 |
| 24 | 2027-01-01 | 11:10 AM | 20 | $1,600 No Limit Hold'em MSPT 1A $400K GTD - $40 Reduced Rake until the start of Level 4 | 8 |
| 25 | 2027-01-01 | 3:10 PM | 21 | $200 NLH Milestone Satellite (1Day) - Awards Direct Entry into Event # 20 | 5 |
| 26 | 2027-01-01 | 5:10 PM | 22 | $200 No Limit Hold'em Bounty $8K GTD (1Day) | 2 |
| 27 | 2027-01-02 | 10:10 AM | 23 | $200 NLH Milestone Satellite (1Day) - Awards Direct Entry into Event # 20 | 5 |
| 28 | 2027-01-02 | 11:10 AM | 20 | $1,600 No Limit Hold'em MSPT 1B $400K GTD | 8 |
| 29 | 2027-01-02 | 3:10 PM | 24 | $200 NLH Milestone Satellite (1Day) - Awards Direct Entry into Event # 20 | 5 |
| 30 | 2027-01-02 | 5:10 PM | 25 | $200 NLH PokerAtlas Valuetown Bounty $20K GTD (1Day) - POKERATLAS PRO MEMBER $20 RAKE DISCOUNT | 9 |
| 31 | 2027-01-03 | 11:10 AM | 20 | $1,600 No Limit Hold'em MSPT 1C $400K GTD | 8 |
| 32 | 2027-01-03 | 5:10 PM | 26 | $200 No Limit Hold'em Bounty $8K GTD (1Day) | 2 |
| 33 | 2027-01-04 | 11:10 AM | 20 | $1,600 No Limit Hold'em MSPT Day 2 Restart | 8 |
| 34 | 2027-01-04 | 11:10 AM | 27 | $250 No Limit Hold'em 1A $75K GTD (1Day) - Day 1 Payouts with 5% advancing to Day 2 - $10 Reduced Rake for Entry before 11:10 AM | 15 |
| 35 | 2027-01-04 | 5:10 PM | 27 | $250 No Limit Hold'em 1B $75K GTD (1Day) - Day 1 Payouts with 5% advancing to Day 2 - $10 Reduced Rake for Entry before 5:10 PM | 15 |
| 36 | 2027-01-05 | 11:10 AM | 27 | $250 No Limit Hold'em 1C $75K GTD (1Day) - Day 1 Payouts with 5% advancing to Day 2 | 15 |
| 37 | 2027-01-05 | 5:10 PM | 27 | $250 No Limit Hold'em 1D $75K GTD (1Day) - Day 1 Payouts with 5% advancing to Day 2 | 15 |
| 38 | 2027-01-06 | 11:10 AM | 28 | $400 No Limit Hold'em $15K GTD (1Day) | 11 |
| 39 | 2027-01-06 | 12:00 PM | 27 | $250 No Limit Hold'em Day 2 Restart | 15 |
| 40 | 2027-01-06 | 5:10 PM | 29 | $200 No Limit Hold'em Bounty $8K GTD (1Day) - Show Your CES Badge - $10 RAKE DISCOUNT | 2 |
| 41 | 2027-01-07 | 11:10 AM | 30 | $300 No Limit Hold'em 1A $100K GTD (1Day) | 13 |
| 42 | 2027-01-07 | 5:10 PM | 30 | $300 No Limit Hold'em 1B $100K GTD (1Day) - Show Your CES Badge - $10 RAKE DISCOUNT | 14 |
| 43 | 2027-01-08 | 11:10 AM | 30 | $300 No Limit Hold'em 1C $100K GTD (1Day) | 13 |
| 44 | 2027-01-08 | 5:10 PM | 30 | $300 No Limit Hold'em 1D $100K GTD (1Day) - Show Your CES Badge - $10 RAKE DISCOUNT | 14 |
| 45 | 2027-01-09 | 11:10 AM | 30 | $300 No Limit Hold'em 1E $100K GTD (1Day) | 13 |
| 46 | 2027-01-09 | 5:10 PM | 30 | $300 No Limit Hold'em 1F $100K GTD (1Day) | 14 |
| 47 | 2027-01-10 | 10:10 AM | 31 | $400 No Limit Hold'em Seniors $20K GTD (1Day) - Must be 50+ years of age to participate | 10 |
| 48 | 2027-01-10 | 12:00 PM | 30 | $300 No Limit Hold'em Day 2 Restart | 13 |
| 49 | 2027-01-10 | 5:10 PM | 32 | $200 No Limit Hold'em Bounty $8K GTD (1Day) | 2 |

Row count: 49. Series window as served: 2026-12-24 to 2027-01-10.
