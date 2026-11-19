# Trip-window fresh re-read — 2026-11-19 (session arena/a33db3c1-poker3)

Verbatim captures of the official sources behind the fixed trip window **2026-11-23 → 2026-11-30**,
re-read line by line on **2026-11-19**. Every value below was compared with `site/data.json` and
matched with **no change**. The machine-checkable record is `research/reread_2026-11-19.json`;
`tests/test_reread_2026_11_19.py` fails if the published rows drift from it.

## Sources re-read (official)

| Source | URL |
|---|---|
| Venetian DeepStack Extravaganza IV schedule page | https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html |
| Venetian structure sheets 1, 2, 3, 5, 6, 7, 8, 11, 22, 26, 30 | https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_<N>.pdf |
| Wynn WPT World Championship schedule PDF | https://cdn.wynnresorts.com/image/upload/v1757097329/visitwynn_pdfs_files/Poker/WPT/WPT_World_Championship_Schedule.pdf |
| Wynn WPT World Championship structures PDF | https://cdn.wynnresorts.com/image/upload/v1750864036/visitwynn_pdfs_files/Poker/WPT/WPT_World_Championship_Structures.pdf |
| Venetian 2026 poker suite-rates page | https://www.venetianlasvegas.com/resort/casino/poker/suite-rates.html |
| Venetian resort-fee page | https://www.venetianlasvegas.com/resort/resort-fee.html |
| Venetian poker-room page | https://www.venetianlasvegas.com/resort/casino/poker.html |
| Venetian booking engine (trip window) | https://www.venetianlasvegas.com/booking?adults[]=2&arrival_date=2026-11-23&children[]=0&departure_date=2026-11-30&view=calendar |

## Venetian DeepStack IV — trip-window schedule rows (as printed, 2026-11-19)

| Date | Time | # | Event | Sheet |
|---|---|---|---|---|
| Mon Nov 23 | 11:10 AM | 7 | $400 No Limit Hold'em 1A $75K GTD | 2 |
| Mon Nov 23 | 5:10 PM | 8 | $200 No Limit Hold'em $8K GTD (1Day) - Progressive Knock-Out Bounty (PKO) | 30 |
| Tue Nov 24 | 11:10 AM | 7 | $400 No Limit Hold'em 1B $75K GTD | 2 |
| Tue Nov 24 | 5:10 PM | 9 | $200 No Limit Hold'em Bounty $8K GTD (1Day) | 1 |
| Wed Nov 25 | 11:00 AM | 7 | $400 No Limit Hold'em Day 2 Restart | 2 |
| Wed Nov 25 | 11:10 AM | 10 | $400 No Limit Hold'em $15K GTD (1Day) | 6 |
| Wed Nov 25 | 5:10 PM | 11 | $200 No Limit Hold'em Bounty $8K GTD (1Day) | 1 |
| Thu Nov 26 | 11:10 AM | 12 | $300 No Limit Hold'em $10K GTD (1Day) | 5 |
| Thu Nov 26 | 5:10 PM | 13 | $200 No Limit Hold'em Bounty $8K GTD (1Day) | 1 |
| Fri Nov 27 | 11:10 AM | 14 | $600 No Limit Hold'em $30K GTD (1Day) | 7 |
| Fri Nov 27 | 5:10 PM | 15 | $200 No Limit Hold'em Bounty $8K GTD (1Day) | 1 |
| Sat Nov 28 | 11:10 AM | 16 | $600 No Limit Hold'em Bounty $30K GTD (1Day) - $200 bounties to start & $500 bounties in the money | 11 |
| Sat Nov 28 | 12:10 PM | 17 | $400 Pot Limit Omaha Bounty $15K GTD (1Day) | 26 |
| Sat Nov 28 | 5:10 PM | 18 | $200 NLH PokerAtlas Valuetown Bounty $20K GTD (1Day) - POKERATLAS PRO MEMBER $20 RAKE DISCOUNT | 8 |
| Sun Nov 29 | 11:10 AM | 19 | $400 No Limit Hold'em 1A $75K GTD | 3 |
| Sun Nov 29 | 12:10 PM | 20 | $300 Pot Limit Omaha $10K GTD (1Day) - Double Board Bomb Pot | 22 |
| Sun Nov 29 | 5:10 PM | 21 | $200 No Limit Hold'em Bounty $8K GTD (1Day) | 1 |
| Mon Nov 30 | 11:10 AM | 19 | $400 No Limit Hold'em 1B $75K GTD | 3 |
| Mon Nov 30 | 5:10 PM | 22 | $200 No Limit Hold'em Bounty $8K GTD (1Day) | 1 |

## Wynn WPT World Championship — trip-window schedule rows (as printed, 2026-11-19)

| Date | Time | Event | Buy-in | Guarantee | Chips | Levels |
|---|---|---|---|---|---|---|
| Nov 27 Fri | 11 a.m. | No Limit Hold'em Day 1A | $600 | $400,000 | 40,000 | 30/40 |
| Nov 27 Fri | 12 p.m. | TORSE | $600 | — | 35,000 | 30 |
| Nov 27 Fri | 1 p.m. | PLO | $400 | — | 30,000 | 30 |
| Nov 27 Fri | 5 p.m. | No Limit Hold'em Day 1B | $600 | $400,000 | 40,000 | 30/40 |
| Nov 28 Sat | 11 a.m. | No Limit Hold'em Day 1C | $600 | $400,000 | 40,000 | 30/40 |
| Nov 28 Sat | 12 p.m. | Mixed Triple Draw (A-5, 2-7, BadugI) | $600 | — | 35,000 | 30 |
| Nov 28 Sat | 5 p.m. | No Limit Hold'em Day 1D | $600 | $400,000 | 40,000 | 30/40 |
| Nov 29 Sun | 11 a.m. | No Limit Hold'em Day 1E | $600 | $400,000 | 40,000 | 30/40 |
| Nov 29 Sun | 6 p.m. | No Limit Hold'em Day 1F | $600 | $400,000 | 40,000 | 20/40 |
| Nov 30 Mon | 11 a.m. | No Limit Hold'em Day 1A | $800 | $1,000,000 | 40,000 | 30/40 |
| Nov 30 Mon | 12 p.m. | Limit Omaha 8 | $600 | — | 35,000 | 30 |
| Nov 30 Mon | 1 p.m. | No Limit Hold'em Day 2 | $800 | $1,000,000 | 40,000 | 30/40 |
| Nov 30 Mon | 5 p.m. | No Limit Hold'em Day 1B | $800 | $1,000,000 | 40,000 | 30/40 |

(The PDF prints "BadugI" with a capital I on the Nov 28 row; the published row spells it "Badugi".
This is a rendering difference of the same event, not a data error — recorded for manual review.)

## Structure-sheet facts read verbatim (2026-11-19)

| Sheet | Event(s) | Start chips | Level | Late registration | Fee | Guarantee |
|---|---|---|---|---|---|---|
| 1 | 9, 11, 13, 15, 21, 22, 23, 25, 60, 61, 62, 64 | 25,000 | 30 min | 8 levels + Break (9:40 PM) | $40 of $200 | $8,000 |
| 2 | 7 | 40,000 | 40 min | 9 levels + Break (5:55 PM) | $70 of $400 | $75,000 |
| 3 | 19 | 40,000 | 40 min | 9 levels + Break (5:55 PM) | $70 of $400 | $75,000 |
| 5 | 2, 12 | 40,000 | 30 min | 10 levels + Break (~ 4:55 PM) | $58 of $300 | $10,000 |
| 6 | 10 | 40,000 | 30 min | 10 levels + Break (~ 4:55 PM) | $65 of $400 | $15,000 |
| 7 | 14, 28, 63 | 40,000 | 30 min | 10 levels + Break (~ 4:55 PM) | $90 of $600 | $30,000 (#14/#63), $40,000 (#28) |
| 8 | 18, 58 | 25,000 | 30 min | 8 levels + Break (9:40 PM) | $40 of $200 | $20,000 |
| 11 | 16, 30, 54 | 40,000 | 30 min | 10 levels + Break (4:55 PM) | $90 of $600 | $30,000 (#16) |
| 22 | 20 | 30,000 | 30 min | 8 levels + break (~ 4:40 PM) | $58 of $300 | $10,000 |
| 26 | 17 | 30,000 | 30 min | 8 levels + break (~ 4:40 PM) | $60 of $400 | $15,000 |
| 30 | 8 | 25,000 | 30 min | 8 levels + Break (9:40 PM) | $40 of $200 | $8,000 |

No sheet prints a maximum-entry-per-player cap, an explicit "freezeout" label, a rebuy or an add-on
provision (sheet 8 prints a PokerAtlas PRO $20 rake discount on the initial buy-in only). This
re-confirms flag **F31**: sheet-screened single-entry candidates are not written-confirmed.

## Hotel and policy pages (read 2026-11-19)

- **Suite rates** (`suite-rates.html`): "rates will start as low as $119 and $209", "There is a $55
  resort fee per night stayed", code **EPOKR25**, "six hours of active live cash gameplay or buy in
  to a $300 or higher tournament for each night stayed", 150-day horizon. Matches the published
  hotel facts.
- **Resort fee** (`resort-fee.html`): "Rates include a daily Resort Fee of $55 plus tax per night,
  payable upon check-in." Matches.
- **Poker-room page** (`poker.html`): "The Palazzo, level 2, Grand Canal Shoppes", "Open 24 Hours",
  complimentary self-parking for registered guests. Matches — resolves **F92**.
- **Booking engine** (trip window, 23–30 Nov): returned the reservation shell only
  ("Your Venice meets Vegas getaway is loading") and **no checkout total**. Consistent with **F88**:
  the engine does not serve a stable static price to a static reader, so the dated $4,010.55 total
  stands on its 2026-11-17 read and must be re-read at the moment of booking.

## Outcome

- 32 trip-window rows (19 Venetian + 13 Wynn) re-read and matched exactly; `lastChecked` and
  `lastVerified` advanced to **2026-11-19** on those rows and on the Venetian/Palazzo hotel rows and
  the re-read sources.
- No tournament, hotel, rate, guarantee or rule value was changed.
- **F92** resolved (poker-room page re-read, no value moved).
- **F88** re-attempted (engine still returns no total to a static reader); the caution stands.
