# Independent fresh line-by-line verification — session `arena/4475a074-poker3`

**Date:** 2026-11-19 UTC. **Method:** live `fetch_page` reads of the official venue/property pages and
structure PDFs behind the fixed trip window (2026-11-23 → 2026-11-30). Every value below was read from the
official source in this session and compared against the published `site/data.json`. **No value was inferred;
no blank was filled in.** Result: **all compared values match the official source verbatim; no drift and no
new irregularity was found.**

## 1. Trip-window schedule (all 19 Venetian DSE IV rows)

Source: [DSE IV schedule](https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html)
(page read in full, four chunks, 2026-11-19). Series line printed: "November 16 – December 23, 2026 … More than
$3.6 Million in guaranteed tournament prize pools."

Comparison fields per row: **date, start time, event number, event name, printed buy-in, printed guarantee,
structure-sheet link.** All 19 rows inside 2026-11-23 → 2026-11-30 match. None missing, none invented.

| Date | Time | Ev# | Published event name | Buy-in | GTD | Sheet | Match |
|---|---|---|---|---|---|---|---|
| 2026-11-23 | 11:10 AM | 7 | $400 NLH 1A $75K GTD | 400 | 75000 | structure_2.pdf | ✓ |
| 2026-11-23 | 5:10 PM | 8 | $200 NLH $8K GTD (1Day) - PKO | 200 | 8000 | structure_30.pdf | ✓ |
| 2026-11-24 | 11:10 AM | 7 | $400 NLH 1B $75K GTD | 400 | 75000 | structure_2.pdf | ✓ |
| 2026-11-24 | 5:10 PM | 9 | $200 NLH Bounty $8K GTD (1Day) | 200 | 8000 | structure_1.pdf | ✓ |
| 2026-11-25 | 11:00 AM | 7 | $400 NLH Day 2 Restart | 400 | 75000 | structure_2.pdf | ✓ |
| 2026-11-25 | 11:10 AM | 10 | $400 NLH $15K GTD (1Day) | 400 | 15000 | structure_6.pdf | ✓ |
| 2026-11-25 | 5:10 PM | 11 | $200 NLH Bounty $8K GTD (1Day) | 200 | 8000 | structure_1.pdf | ✓ |
| 2026-11-26 | 11:10 AM | 12 | $300 NLH $10K GTD (1Day) | 300 | 10000 | structure_5.pdf | ✓ |
| 2026-11-26 | 5:10 PM | 13 | $200 NLH Bounty $8K GTD (1Day) | 200 | 8000 | structure_1.pdf | ✓ |
| 2026-11-27 | 11:10 AM | 14 | $600 NLH $30K GTD (1Day) | 600 | 30000 | structure_7.pdf | ✓ |
| 2026-11-27 | 5:10 PM | 15 | $200 NLH Bounty $8K GTD (1Day) | 200 | 8000 | structure_1.pdf | ✓ |
| 2026-11-28 | 11:10 AM | 16 | $600 NLH Bounty $30K GTD (1Day) | 600 | 30000 | structure_11.pdf | ✓ |
| 2026-11-28 | 12:10 PM | 17 | $400 PLO Bounty $15K GTD (1Day) | 400 | 15000 | structure_26.pdf | ✓ |
| 2026-11-28 | 5:10 PM | 18 | $200 NLH PokerAtlas Valuetown Bounty $20K (1Day) | 200 | 20000 | structure_8.pdf | ✓ |
| 2026-11-29 | 11:10 AM | 19 | $400 NLH 1A $75K GTD | 400 | 75000 | structure_3.pdf | ✓ |
| 2026-11-29 | 12:10 PM | 20 | $300 PLO $10K GTD (1Day) - Double Board Bomb Pot | 300 | 10000 | structure_22.pdf | ✓ |
| 2026-11-29 | 5:10 PM | 21 | $200 NLH Bounty $8K GTD (1Day) | 200 | 8000 | structure_1.pdf | ✓ |
| 2026-11-30 | 11:10 AM | 19 | $400 NLH 1B $75K GTD | 400 | 75000 | structure_3.pdf | ✓ |
| 2026-11-30 | 5:10 PM | 22 | $200 NLH Bounty $8K GTD (1Day) | 200 | 8000 | structure_1.pdf | ✓ |

The page prints the PokerAtlas row as "POKERATLAS PRO MEMBER $20 RAKE DISCOUNT"; the published row carries the
same fact and is classified `extra` (PokerAtlas PRO discount), consistent with the single-entry policy.

## 2. Core money values (hotel / cost model)

| Value | Published | Official source (read 2026-11-19) | Verbatim | Match |
|---|---|---|---|---|
| Poker-suite starting rate | $119 / $209 | [suite-rates](https://www.venetianlasvegas.com/resort/casino/poker/suite-rates.html) | "These rates will start as low as $119 and $209 and can be higher." | ✓ |
| 150-day horizon | yes | suite-rates | "Future rates are only provided out to a maximum of 150 days from the current date." | ✓ |
| Qualification | 6 h cash / $300+ tourney, before 2 a.m. | suite-rates | "you will be required to play six hours of active live cash gameplay or buy in to a $300 or higher tournament for each night stayed … prior to 2 a.m. the last night stayed." | ✓ |
| Rate code | EPOKR25 | suite-rates | "book your suite … by calling 866.255.8936 and mentioning code EPOKR25." | ✓ |
| Resort fee | $55/night + tax | [resort-fee](https://www.venetianlasvegas.com/resort/resort-fee.html) | "Rates include a daily Resort Fee of $55 plus tax per night, payable upon check-in." | ✓ |
| Room tax | 13.38% | [hotel terms](https://www.venetianlasvegas.com/legal/hotel-terms-and-conditions.html) | "Daily rates do not include the applicable Clark County Room Tax of 13.38%." | ✓ |
| Guest self-parking | $20/day | player-parking / hotel terms | "The daily fee for registered hotel guests is $20/day, seven days a week." | ✓ |
| Non-guest / valet | $20-$25 / $40 | player-parking / hotel terms | "For non-hotel guests, the fee is $20/day Monday – Thursday, and $25/day Friday – Sunday. Valet parking is $40/day." | ✓ |
| 3-hour parking waiver | conditional, not netted | [player-parking](https://www.venetianlasvegas.com/resort/casino/poker/player-parking.html) | "Players in the poker room who play three hours or more in tournament or cash games will receive complimentary self-parking for the day." | ✓ |
| Wynn resort fee | $55/night + tax | [Wynn resort info](https://www.wynnlasvegas.com/about-us/resort-information) | "Reservations will be charged a daily resort fee of $55 plus tax." (self-parking complimentary, included) | ✓ |

## 3. Structure sheets (spot-read in full)

- **structure_1.pdf** — $200 NLH Bounty (1Day). Start 5:10 PM; 25,000 chips; 30-min levels; Late Registration
  8 levels + Break (9:40 PM); Guarantee $8,000 (prize pool + total bounties); "$40 of the $200 Buy-In is withheld
  for house fees … prize pool consists of $160 of every $200 Buy In"; pays 12.5% of field; $50 bounty. **Matches
  the published Nov 24/25/26/27/29/30 $200 Bounty rows** (chips 25000, levelMin 30, lateReg 9:40 PM, GTD 8000). ✓
- **structure_6.pdf** — $400 NLH (1Day), Event 10. Start 11:10 AM; 40,000 chips; 30-min levels; Late Registration
  10 levels + Break (~4:55 PM); Guarantee $15,000; "$65 of the $400 Buy-In is withheld … prize pool consists of
  $335 of every $400 Buy In"; pays 12.5%. **Matches the published Nov 25 $400 $15K GTD row** (chips 40000,
  levelMin 30, lateReg 4:55 PM, GTD 15000). ✓

The sheets print one buy-in, one start flight and no re-entry/rebuy/add-on/second-flight clause — i.e. they are
**sheet-screened**, not a written per-player maximum-entry confirmation (flag F31 stands; no sheet prints
"single entry"/"freezeout" wording).

## 4. Trip-cost arithmetic (recomputed by hand)

- trueCostPerNight = (119 + 55) × 1.1338 = 197.2812 → **$197.28** ✓
- lodgingTotal = 7 × 197.28 = **$1,380.96** ✓; parkingTotal = 7 × 20 = **$140.00** ✓
- tripTotal = 2600 + 1380.96 + 140 = **$4,120.96** ✓
- alternateTrueCostPerNight = (209 + 55) × 1.1338 = **$299.32** ✓; alternateTripTotal = **$4,835.24** ✓
- liveQuote (2026-11-17): 3152.25 + 385.00 + 473.30 = **$4,010.55** ✓; per-night (164.25+55)×1.1338 = **$248.59**,
  (1649.25+55)×1.1338 = **$1,932.28** ✓ — all reconcile with the printed checkout total.

## 5. Conclusion

The fresh 2026-11-19 read of the official schedule, the two hotel policy pages, the parking page, the Wynn resort
policy page and two structure PDFs agrees with every published value behind the trip window. **No published value
changed, no new irregularity was found, and no unverified value was inferred.** The 40-row requirements audit in
`site/data.json` (rendered at `site/verification.html`) remains accurate. Items official evidence cannot support
(written maximum-entry rule, verified finish times, an 8 a.m. all-day route, a ranked "best" winner/hotel) stay
marked as such rather than being filled in.
