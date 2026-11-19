# Independent 2026-11-19 re-verification — session `arena/03d48a10-poker3`

Every value below was read from the official page named beside it **on 2026-11-19 UTC** by this session, using the
platform fetch tool. No third-party calendar, aggregator or press report was used to substantiate a value. Where an
official page did not print a value, the row records that it did not, and the dashboard's blank is left blank.

Sources are quoted verbatim where the quote is the evidence. Retrieval date for every row in this record:
**2026-11-19**.

---

## 1. The Venetian — DeepStack Extravaganza IV schedule

URL: <https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html>
Read: all four chunks in full (Nov 16 – Dec 23, 2026).

Comparison method: the official page was read independently, then its rows inside the trip window were matched
against `site/data.json` on **date, start time, printed buy-in and event description**, one row at a time.

| Official row (2026-11-19 read) | Start | Site row | Result |
|---|---|---|---|
| #7 $400 No Limit Hold'em 1A $75K GTD | 11:10 AM Nov 23 | `vl-dse-2026-11-23-7-1110am`, $400 | match |
| #8 $200 No Limit Hold'em $8K GTD (1Day) — Progressive Knock-Out | 5:10 PM Nov 23 | `…-8-510pm`, $200 / $8,000 | match |
| #7 $400 No Limit Hold'em 1B $75K GTD | 11:10 AM Nov 24 | $400 | match |
| #9 $200 No Limit Hold'em Bounty $8K GTD (1Day) | 5:10 PM Nov 24 | $200 / $8,000 | match |
| #7 $400 No Limit Hold'em Day 2 Restart | 11:00 AM Nov 25 | $400, no guarantee printed | match |
| #10 $400 No Limit Hold'em $15K GTD (1Day) | 11:10 AM Nov 25 | $400 / $15,000 | match |
| #11 $200 No Limit Hold'em Bounty $8K GTD (1Day) | 5:10 PM Nov 25 | $200 / $8,000 | match |
| #12 $300 No Limit Hold'em $10K GTD (1Day) | 11:10 AM Nov 26 | $300 / $10,000 | match |
| #13 $200 No Limit Hold'em Bounty $8K GTD (1Day) | 5:10 PM Nov 26 | $200 / $8,000 | match |
| #14 $600 No Limit Hold'em $30K GTD (1Day) | 11:10 AM Nov 27 | $600 / $30,000 | match |
| #15 $200 No Limit Hold'em Bounty $8K GTD (1Day) | 5:10 PM Nov 27 | $200 / $8,000 | match |
| #16 $600 No Limit Hold'em Bounty $30K GTD (1Day) | 11:10 AM Nov 28 | $600 / $30,000 | match |
| #17 $400 Pot Limit Omaha Bounty $15K GTD (1Day) | 12:10 PM Nov 28 | $400 / $15,000 | match |
| #18 $200 NLH PokerAtlas Valuetown Bounty $20K GTD (1Day) | 5:10 PM Nov 28 | $200 / $20,000 | match |
| #19 $400 No Limit Hold'em 1A $75K GTD | 11:10 AM Nov 29 | $400 / $75,000 | match |
| #20 $300 Pot Limit Omaha $10K GTD (1Day) — Double Board Bomb Pot | 12:10 PM Nov 29 | $300 / $10,000 | match |
| #21 $200 No Limit Hold'em Bounty $8K GTD (1Day) | 5:10 PM Nov 29 | $200 / $8,000 | match |
| #19 $400 No Limit Hold'em 1B $75K GTD | 11:10 AM Nov 30 | $400 / $75,000 | match |
| #22 $200 No Limit Hold'em Bounty $8K GTD (1Day) | 5:10 PM Nov 30 | $200 / $8,000 | match |
| #19 $400 No Limit Hold'em 1C $75K GTD | 11:10 AM Dec 1 | $400 / $75,000 | match |
| #23 $200 No Limit Hold'em Bounty $8K GTD (1Day) | 5:10 PM Dec 1 | $200 / $8,000 | match |
| #24 $600 No Limit Hold'em Seniors $40K GTD (1Day) — must be 50+ | 10:10 AM Dec 2 | $600 / $40,000, restricted | match |
| #19 $400 No Limit Hold'em Day 2 Restart | 11:00 AM Dec 2 | $400, no guarantee | match |
| #25 $200 No Limit Hold'em Bounty $8K GTD (1Day) | 5:10 PM Dec 2 | $200 / $8,000 | match |

**Result: 24 official rows, 24 site rows, 24 matches, 0 missing, 0 invented.**

Two values are worth recording because they are easy to get wrong and the dashboard gets them right:

- **Nov 25 carries two rows with different numbers** — #7 at 11:00 AM (a Day 2 restart) and #10 at 11:10 AM (a new
  event). They start ten minutes apart; neither is a typo, and neither can be played alongside the other.
- **Nov 23–25 and Nov 29–Dec 2 share event number #7/#19** across their starting flights (1A / 1B / 1C). The printed
  buy-in is the same; the guarantee is one pool shared by all flights, not a guarantee per flight. The dashboard's
  flight category says exactly this.

### The earliest official start in the reviewed set

The earliest start time anywhere in the DeepStack Extravaganza IV schedule is **10:10 AM** (Nov 19, 20, 21 RaceDay
Stack; Dec 2 and Dec 8 Seniors; Dec 9 LIPS satellite; Dec 10, 12 main events). There is **no 8:00 AM start** on this
schedule. The user's brief asks for an all-day plan beginning at 8 AM; no official source reviewed supports an 8 AM
tournament start, so the plan cannot be built from published values. This confirms the existing flag F17 rather than
changing it.

---

## 2. The Venetian — hotel components

All four pages were re-read on 2026-11-19.

| Value used by the dashboard | Excerpt read today | Source |
|---|---|---|
| Resort fee $55 + tax | "Rates include a daily Resort Fee of $55 plus tax per night, payable upon check-in." | <https://www.venetianlasvegas.com/resort/resort-fee.html> |
| $55 resort fee (second wording) | "The Venetian Resort has a standard Las Vegas Resort Fee of $55 plus applicable tax per night, payable upon check-in." | <https://www.venetianlasvegas.com/legal/hotel-terms-and-conditions.html> |
| Clark County room tax 13.38% | "Daily rates do not include the applicable Clark County Room Tax of 13.38%. Starting rates are based on double occupancy." | <https://www.venetianlasvegas.com/legal/hotel-terms-and-conditions.html> |
| Poker suite starting rates | "These rates will start as low as $119 and $209 and can be higher. Future rates are only provided out to a maximum of 150 days from the current date." | <https://www.venetianlasvegas.com/resort/casino/poker/suite-rates.html> |
| Poker-rate qualification | "you will be required to play six hours of active live cash gameplay or buy in to a $300 or higher tournament for each night stayed … prior to 2 a.m. the last night stayed" | <https://www.venetianlasvegas.com/resort/casino/poker/suite-rates.html> |
| Rate adjustment on failure | "For any nights you fail to complete these requirements, your nightly suite rate will be adjusted to the prevailing rate, and you will not receive the poker suite rate discount." | <https://www.venetianlasvegas.com/resort/casino/poker/suite-rates.html> |
| Registered-guest parking $20/day | "The daily fee for registered hotel guests is $20/day, seven days a week. For non-hotel guests, the fee is $20/day Monday – Thursday, and $25/day Friday – Sunday. Valet parking is $40/day." | <https://www.venetianlasvegas.com/resort/casino/poker/player-parking.html> and the hotel terms page |
| Poker-player parking waiver | "Players in the poker room who play three hours or more in tournament or cash games will receive complimentary self-parking for the day. Players must visit a supervisor at the end of their session to confirm qualifications…" | <https://www.venetianlasvegas.com/resort/casino/poker/player-parking.html> |
| Early-checkout charge | "Check-out prior to your scheduled departure date will result in an additional charge of $100 plus tax." | <https://www.venetianlasvegas.com/legal/hotel-terms-and-conditions.html> |
| Incidental deposit | "A credit card incidental deposit of $150 per night is required upon check-in for suite charging privileges for non-Signature Suites." | <https://www.venetianlasvegas.com/legal/hotel-terms-and-conditions.html> |
| Deposit on confirmation | "A deposit for your stay, including suite, fee, and tax, will be billed upon reservation confirmation." | <https://www.venetianlasvegas.com/legal/hotel-terms-and-conditions.html> |

**Arithmetic re-derived by hand, 2026-11-19:**

```
true cost / night at the published floor = ($119 + $55) x 1.1338 = $197.28   (matches tripCostModel.trueCostPerNight)
true cost / night at the high rate       = ($209 + $55) x 1.1338 = $299.32   (matches alternateTrueCostPerNight)
7 nights x $197.28                       = $1,380.96                        (matches lodgingTotal)
7 entries, exact sum $200+$200+$400+$300+$600+$600+$300 = $2,600.00          (matches tournamentTotal)
$2,600.00 + $1,380.96 + (7 x $20)        = $4,120.96                        (matches tripTotal)
```

**Irregularity confirmed, not new (F51).** The two official pages describe the $55 fee differently. The Resort Fee page
says "Rates include a daily Resort Fee of $55 plus tax per night"; the booking calendar says its prices already include
the fee. One wording implies the fee is inside the quoted rate, the other implies it is added. The dashboard keeps the
conservative reading (fee added) and publishes the alternative. This is correctly flagged; it is not resolved by
reading the two pages again, and this session does not resolve it.

**No date-specific total is available today.** The booking engine deep link
<https://www.venetianlasvegas.com/booking?adults%5B%5D=2&arrival_date=2026-11-23&children%5B%5D=0&departure_date=2026-11-30&view=calendar>
did not return a price in this session's read, consistent with the dashboard's recorded 2026-11-19 result (F93). The
latest dated checkout total remains the 2026-11-17 read of **$4,010.55**, which is published as a dated log entry with
its own date, not as a current price.

---

## 3. Wynn Las Vegas

Read on 2026-11-19.

| Value used by the dashboard | Excerpt read today | Source |
|---|---|---|
| Resort fee $55 + tax (Wynn rooms) | "Reservations will be charged a daily resort fee of $55 plus tax." | <https://www.wynnlasvegas.com/about-us/resort-information> |
| Resort fee $55 + tax (Tower Suites) | "TOWER SUITES RESORT FEE INFORMATION — Reservations will be charged a daily resort fee of $55 plus tax." | same page |
| Check-in / check-out | "Check In: 3 p.m.  Check Out: 12 p.m." | same page |
| Guarantee policy | "A valid credit card is required to confirm your reservation. One night's room rate and tax will be charged at time of booking." | same page |
| Daily tournaments | "Monday–Thursday • $200 NLH • 12 p.m.", "Friday • $240 NLH Rebuy • 12 p.m.", "Saturday • $200 NLH • 12 p.m.", "Sunday • $200 NLH • 12 p.m.", "NIGHTLY $10,000 Guarantee • $160 NLH • 6 p.m." | <https://cdn.wynnresorts.com/image/upload/v1752011166/visitwynn_pdfs_files/Poker/Daily%20Tournaments/poker-daily-tournament-poster.pdf> |
| Daily slate suspension | "Please note that the Daily Tournament schedule will be suspended during each Wynn Signature, Wynn Millions, and Classic tournament series." | <https://www.wynnlasvegas.com/casino/poker> |
| WPT dates | "WPT WORLD CHAMPIONSHIP — November 27–December 21" | same page |
| Signature Series dates | "WYNN SIGNATURE SERIES — January 11–24. 2027" | same page |
| Poker room location | Casino page FAQ heading "Where is the poker room located?" (answer collapsed in the fetched text); the dashboard's stated location "located in Encore at Wynn Las Vegas" is **not** re-confirmed by today's read | same page |

**Result: every Wynn daily-poster value the dashboard publishes matches the official poster exactly** — 4 rows, 4
matches, including the Friday $240 rebuy format, which the dashboard keeps in the extra-spend section rather than the
single-entry path.

**Signature Series structures — checked, still unpublished.** The poker page today links a structures document the
dashboard did not previously cite:
<https://cdn.wynnresorts.com/image/upload/v1762299460/visitwynn_pdfs_files/Poker/Wynn%20Signature%20Series/Wynn_Signature_Series_Structures.pdf>.
Its entire readable content is:

> LAS VEGAS / POKER / COMING SOON

That confirms, rather than contradicts, the dashboard's position that the Signature Series structure sheets are not
published. The 22 Signature Series rows therefore stay labelled as unverified on entry rules. **This is the one place
this session found a source the dashboard should cite**, and it has been added to the source list.

---

## 4. Bellagio

Read on 2026-11-19: the poker page and the Friday $600 PDF.

| Value | Excerpt read today | Source |
|---|---|---|
| Friday $600 NLH structure | "NLH $600 BUY-IN — Fridays \| 11:00 a.m." | <https://assets.contentstack.io/v3/assets/bltc6ce635bc4868eb2/blt9cf95b0e60ec253e/6af491a3a9851d75c40be840/mgm-bellagio-poker-fridays-$600-nlh.pdf> |
| Fee split | "The $600 Buy-In is allocated as follows: $510 to Prize Pool; $50 House Fee; $40 Voluntary Staff Gratuity." | same PDF |
| Re-entry | "Players may buy-in and re-enter through the end of level 8 (Including Break)." | same PDF |
| Optional gratuity adds chips | "The voluntary staff gratuity will grant players an extra 15,000 chips." | same PDF |
| Starting stack | "Players will start with 30,000 tournament chips, including the optional Staff Gratuity. (15,000 + 15,000)" | same PDF |
| Weekly links | "FRIDAYS \| $600 NLH", "SATURDAYS \| $1,000 NLH", "SUNDAYS \| $400 H.O.R.S.E" | <https://bellagio.mgmresorts.com/en/casino/poker.html> |
| PLO Double Bomb Pot | "PLO Double Bomb Pot: … join the action nightly at 6 PM." | same page |
| Undated resumption notice | "Tournament play will resume on Saturday, July 26, beginning with the $300 PLO Double Board Bomb Pot Tournament at 2 PM PT." — **no year printed** | same page |

**Result: the Friday $600 row matches the source, and it is correctly excluded from the single-entry path.** The
published structure allows re-entry through level 8 and an optional $40 gratuity that buys 15,000 extra chips. Both are
ways to spend more money for an advantage, so the row belongs in the separate section, which is where it is.

**F02 (Bellagio Saturday) re-confirmed as an open conflict.** The page heading says "$1,000 NLH"; the linked PDF's
header says "$1100 BUY-IN" and its fee allocation says "Of the $600 Buy-in". Three different numbers on one event. The
dashboard leaves the buy-in blank and flags it rather than choosing. That is the correct treatment and this session did
not change it.

**F03 (undated notice) re-confirmed.** The notice still names "July 26" with no year, and the page's own highlight says
the PLO bomb pot runs nightly at 6 PM, while the notice says 2 PM. July 26, 2026 was a Sunday, not a Saturday. The
notice cannot be used for a date, so it is not.

---

## 5. Caesars Palace and Horseshoe — the article that backs the daily rows

URL: <https://www.caesars.com/las-vegas/explore/casino/poker-tournaments-las-vegas-strip>
Read: chunks 0–1, on 2026-11-19. This is a **Caesars-published editorial article dated July 17, 2026**, not a
machine-generated schedule page. That distinction matters and is recorded here because the dashboard's rows depend on it.

| Value the dashboard publishes | Excerpt read today |
|---|---|
| Caesars Palace start times | "you will find four No-Limit Hold'em tournaments each day at 10 a.m., 2 p.m., 6 p.m. and 9 p.m." |
| Caesars Palace buy-in | "Every event carries a $100 buy-in, starts you with 20,000 chips, and features a $1,000 guaranteed prize pool." |
| Caesars Palace add-on | "a $50 add-on at the first break gives you an extra 15,000 chips if you want a deeper run" |
| Horseshoe start times | "The times at 9 a.m., 11 a.m., 2 p.m., 5 p.m., 8 p.m. and 11 p.m." |

**Irregularity confirmed (F90, correctly flagged).** The article says *every* Caesars Palace event is a $100 buy-in. The
dashboard publishes $100 at 10 a.m. and 6 p.m. and **$160 at 2 p.m. and 9 p.m.**, from a flyer. Two official Caesars
sources therefore describe the same room's buy-ins differently. The dashboard does not flatten them into one figure.

**A second, unreported suppression risk.** The article says Caesars Palace runs a **$50 add-on** that buys 15,000 more
chips. That is exactly the "gain an advantage by spending more" format the brief asks to be kept separate. The
dashboard's four Caesars rows carry `entryType: multi-buyin`, so they are already outside the single-entry path, and the
column note names the add-on. Verified as correct.

---

## 6. MGM Grand

URL: <https://assets.contentstack.io/v3/assets/bltc6ce635bc4868eb2/blt5f25277b8918da08/mgm-grand-casino-poker-tournament_schedule.pdf>
Read: full document, 2026-11-19.

| Value | Excerpt read today |
|---|---|
| Title | "MGM Grand August Tournament Schedule" — the month label is still **August**, no year printed |
| Start times | 11:10am, 7:10pm, 11:10pm on all seven days |
| Saturday | "$150 NLH - $2,000" |
| Chips / levels | "25K Chips / 15 Min" (Saturday 11:10am: "25K Chips / 20 Min") |
| Entry policy | "**Sunday through Friday** - Players with 5 entries or more in $120 Daily Tournaments will receive one (1) free entry to the Saturday $150 NLH $2,000 Guarantee" |

**Result: every published MGM value matches, and the one printed entry-policy sentence is properly recorded.** That
sentence is the closest thing this room publishes to an entry rule, and it **assumes five or more entries** in the $120
daily. It therefore cannot support a single-entry claim for the $120 rows. The dashboard publishes it verbatim under F72
and keeps those rows out of the single-entry path.

**F07 re-confirmed.** The month heading still says August. The daily slots and buy-ins are used as printed and the month
label is flagged; nothing in this read dates the schedule.

---

## 7. Summary of this verification pass

| Area | Rows / facts compared | Matches | Changes made |
|---|---|---|---|
| Venetian DSE IV trip window | 24 rows | 24 | none |
| Venetian hotel components | 10 facts + 4 arithmetic identities | 10 / 4 | none |
| Wynn daily poster | 4 rows | 4 | added 1 source URL (Signature structures, still "COMING SOON") |
| Wynn resort policy | 5 facts | 5 | none |
| Bellagio Friday structure | 7 facts | 7 | none |
| Caesars / Horseshoe article | 4 facts | 4 | none |
| MGM Grand schedule | 6 facts | 6 | none |
| **Total** | **64** | **64** | 1 source added, 0 values changed |

No published value changed as a result of this pass. Seven irregularities were re-confirmed against live official pages
(F02, F03, F07, F17, F31, F51, F72, F90, F93) and none was resolved, because none can be resolved by reading the same
pages again — each needs either a venue statement or a fresh dated quote.

### What this pass could not do

- **No date-specific Venetian total.** The booking engine returned no price today, as recorded in F93.
- **No 8 AM start.** The earliest reviewed start is 10:10 AM (F17).
- **No finish times.** No venue publishes one (F16). Every "estimated finish" on the site is derived and labelled.
- **No written maximum-entry rule.** No reviewed sheet, page or term states one for any candidate (F31).
- **No Wynn room-tax percentage.** Wynn prints "$55 plus tax" and no percentage, so no Wynn all-in nightly total is
  computable from published components (F39).
- **No walking time published by any venue.** Every walking figure is a Google Maps estimate with its own capture date.
