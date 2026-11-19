# Independent re-verification of the trip-window official sources — 2026-11-19

Session: `arena/cce0b8d3-poker3`. Branch: `arena/cce0b8d3-poker3`. Read date: **2026-11-19 (UTC)**.
Method: the platform page reader on the live official pages only. No third-party source was used and no value was
inferred. The machine-readable record is `research/verification_2026-11-19_arena-cce0b8d3.json`; the regression
guard is `tests/test_verification_2026-11-19_cce0b8d3.py`.

## Sources read (official, for manual review)

| Source | URL | Read |
|---|---|---|
| Venetian DeepStack Extravaganza IV schedule (all four chunks) | https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html | 2026-11-19 |
| Venetian structure sheets 1, 5, 6, 7, 11, 22, 30 | `https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_<N>.pdf` | 2026-11-19 |
| Wynn WPT World Championship schedule PDF | https://cdn.wynnresorts.com/image/upload/v1757097329/visitwynn_pdfs_files/Poker/WPT/WPT_World_Championship_Schedule.pdf | 2026-11-19 |
| Wynn poker room page | https://www.wynnlasvegas.com/casino/poker | 2026-11-19 |
| Wynn resort policies | https://www.wynnlasvegas.com/about-us/resort-information | 2026-11-19 |
| Venetian poker-suite rate page | https://www.venetianlasvegas.com/resort/casino/poker/suite-rates.html | 2026-11-19 |
| Venetian resort-fee page | https://www.venetianlasvegas.com/resort/resort-fee.html | 2026-11-19 |
| Venetian hotel terms and conditions (both chunks) | https://www.venetianlasvegas.com/legal/hotel-terms-and-conditions.html | 2026-11-19 |
| Venetian booking engine, 23-30 Nov 2026, 2 adults | https://www.venetianlasvegas.com/booking?adults[]=2&arrival_date=2026-11-23&children[]=0&departure_date=2026-11-30&view=calendar | 2026-11-19 |
| Wynn Signature Series structures PDF | https://cdn.wynnresorts.com/image/upload/v1762299460/visitwynn_pdfs_files/Poker/Wynn%20Signature%20Series/Wynn_Signature_Series_Structures.pdf | 2026-11-19 |

## Result

**0 value differences.** All 19 published Venetian trip-window rows, all 13 published Wynn WPT trip-window rows and
all seven primary structure sheets match the live official text. No tournament, fee, guarantee, chip, level,
late-registration, hotel or policy value was changed by this pass.

### Venetian DSE IV schedule, 23-30 November 2026 (19 rows)

Every row matches the published row on date, start time, event name and structure-sheet link:

| Date | Start | # | Event | Sheet |
|---|---|---|---|---|
| Nov 23 | 11:10 AM | 7 | $400 No Limit Hold'em 1A $75K GTD | 2 |
| Nov 23 | 5:10 PM | 8 | $200 No Limit Hold'em $8K GTD (1Day) — Progressive Knock-Out Bounty (PKO) | 30 |
| Nov 24 | 11:10 AM | 7 | $400 No Limit Hold'em 1B $75K GTD | 2 |
| Nov 24 | 5:10 PM | 9 | $200 No Limit Hold'em Bounty $8K GTD (1Day) | 1 |
| Nov 25 | 11:00 AM | 7 | $400 No Limit Hold'em Day 2 Restart | 2 |
| Nov 25 | 11:10 AM | 10 | $400 No LImit Hold'em $15K GTD (1Day) | 6 |
| Nov 25 | 5:10 PM | 11 | $200 No Limit Hold'em Bounty $8K GTD (1Day) | 1 |
| Nov 26 | 11:10 AM | 12 | $300 No LImit Hold'em $10K GTD (1Day) | 5 |
| Nov 26 | 5:10 PM | 13 | $200 No Limit Hold'em Bounty $8K GTD (1Day) | 1 |
| Nov 27 | 11:10 AM | 14 | $600 No Limit Hold'em $30K GTD (1Day) | 7 |
| Nov 27 | 5:10 PM | 15 | $200 No Limit Hold'em Bounty $8K GTD (1Day) | 1 |
| Nov 28 | 11:10 AM | 16 | $600 No Limit Hold'em Bounty $30K GTD (1Day) — $200 bounties to start & $500 bounties in the money | 11 |
| Nov 28 | 12:10 PM | 17 | $400 Pot Limit Omaha Bounty $15K GTD (1Day) | 26 |
| Nov 28 | 5:10 PM | 18 | $200 NLH PokerAtlas Valuetown Bounty $20K GTD (1Day) — PokerAtlas PRO member $20 rake discount | 8 |
| Nov 29 | 11:10 AM | 19 | $400 No Limit Hold'em 1A $75K GTD | 3 |
| Nov 29 | 12:10 PM | 20 | $300 Pot Limit Omaha $10K GTD (1Day) — Double Board Bomb Pot | 22 |
| Nov 29 | 5:10 PM | 21 | $200 No Limit Hold'em Bounty $8K GTD (1Day) | 1 |
| Nov 30 | 11:10 AM | 19 | $400 No Limit Hold'em 1B $75K GTD | 3 |
| Nov 30 | 5:10 PM | 22 | $200 No Limit Hold'em Bounty $8K GTD (1Day) | 1 |

### Wynn WPT World Championship, 27-30 November 2026 (13 rows)

Every row matches the live schedule PDF on date, start time, event name, buy-in, guarantee and chips. The PDF prints
`BadugI` with a capital I on 28 November; the published row spells `Badugi`. That is a rendering difference only,
already recorded as flag F45, not a data error.

### Structure sheets (7)

| Sheet | Event(s) | Start | Chips | Level | Late registration | Guarantee | Fee |
|---|---|---|---|---|---|---|---|
| 30 | 8 | 5:10 PM | 25,000 | 30 min | 8 levels + break (9:40 PM) | $8,000 incl. bounties | $40 of $200 |
| 1 | 9, 11, 13, 15, 21, 22, 23, 25, 60, 61, 62, 64 | 5:10 PM | 25,000 | 30 min | 8 levels + break (9:40 PM) | $8,000 incl. bounties | $40 of $200 |
| 6 | 10 | 11:10 AM | 40,000 | 30 min | 10 levels + break (~4:55 PM) | $15,000 | $65 of $400 |
| 5 | 2, 12 | 11:10 AM | 40,000 | 30 min | 10 levels + break (~4:55 PM) | $10,000 | $58 of $300 |
| 7 | 14, 28, 63 | 11:10 AM | 40,000 | 30 min | 10 levels + break (~4:55 PM) | $30,000 (#14, #63); $40,000 (#28) | $90 of $600 |
| 11 | 16, 30, 54 | 11:10 AM | 40,000 | 30 min | 10 levels + break (4:55 PM) | $30,000 (#16); $40,000 (#30); $50,000 (#54) | $90 of $600 |
| 22 | 20 | 12:10 PM | 30,000 | 30 min | 8 levels + break (~4:40 PM) | $10,000 | $58 of $300 |

### Hotel facts

- **Venetian.** The poker-suite rate page still reads "These rates will start as low as $119 and $209 and can be
  higher", with a $55 resort fee per night stayed, phone booking under code EPOKR25, and the six-hours-of-live-cash
  or $300+ tournament qualification per night. The resort-fee page reads "Rates include a daily Resort Fee of $55 plus
  tax per night, payable upon check-in". The hotel terms print the 13.38% Clark County Room Tax, check-in 3:00 p.m. to
  11:59 p.m., check-out 11:00 a.m., a deposit billed on confirmation, prepaid offers non-cancellable and
  non-refundable, and a $100 plus tax early-checkout charge. All match the published hotel row.
- **Wynn.** The resort-policy page reads check-in 3 p.m., check-out 12 p.m., a daily resort fee of $55 plus tax, and
  one night's room rate and tax charged at booking. All match the published Wynn row.

## Irregularities / open items (do not block)

- **F93 stands.** The official Venetian booking engine again returned only the reservation shell ("Your Venice meets
  Vegas getaway is loading") for 23-30 November 2026, with no rate, resort fee, tax or checkout total. The dated
  2026-11-17 checkout total of $4,010.55 remains the latest on record.
- **F56 stands.** The Wynn Signature Series structures file still returns only "LAS VEGAS POKER / COMING SOON".
- **F45 re-confirmed.** The live Wynn PDF prints `BadugI` (capital I) on the 28 November Mixed Triple Draw row.
- **Two static-page statements corrected in this session.** `site/venues/venetian.html` said all 52 sheets were read
  on 2026-11-16; the 37 DSE IV sheets were read that day and the 15 NYE sheets on 2026-11-17.
  `site/venues/index.html` said "the NYE rows stay unverified"; the NYE rows are not all unverified — seven are
  sheet-screened candidates, and the unverified rows are the Wynn Signature rows whose structures file is still
  "coming soon".
