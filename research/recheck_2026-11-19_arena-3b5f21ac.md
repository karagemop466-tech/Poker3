# Non-trip-window spot check — 2026-11-19 (session arena/3b5f21ac-poker3)

Every source below was fetched and read line by line on **2026-11-19 UTC** through the platform page
reader (the build sandbox's own egress to the venue hosts fails, flag F40). Scope: the open flags that
are **outside** the fixed trip-window re-read claimed by open PR #173 (`arena/a33db3c1-poker3`) and
outside the calculator scope claimed by open PR #184 (`arena/5cfdd619-poker3`). No published value
changed; the findings are recorded as flag-text updates and two new flags (F109, F110).

## Sources re-read (official)

| # | Source | URL |
|---|---|---|
| 1 | Wynn Signature Series structures PDF | https://cdn.wynnresorts.com/image/upload/v1762299460/visitwynn_pdfs_files/Poker/Wynn%20Signature%20Series/Wynn_Signature_Series_Structures.pdf |
| 2 | Wynn daily tournament poster PDF | https://cdn.wynnresorts.com/image/upload/v1752011166/visitwynn_pdfs_files/Poker/Daily%20Tournaments/poker-daily-tournament-poster.pdf |
| 3 | Wynn daily structures PDF (chunks 0–1) | https://cdn.wynnresorts.com/image/upload/v1752011191/visitwynn_pdfs_files/Poker/Daily%20Tournaments/Poker-All_Daily_Structures.pdf |
| 4 | Wynn poker room page | https://www.wynnlasvegas.com/casino/poker |
| 5 | Wynn terms page | https://www.wynnlasvegas.com/terms-and-conditions/850070 |
| 6 | Wynn resort policies page | https://www.wynnlasvegas.com/about-us/resort-information |
| 7 | Resorts World gaming page (both chunks) | https://www.rwlasvegas.com/gaming/ |
| 8 | Resorts World /poker-room/ request | https://www.rwlasvegas.com/poker-room/ |
| 9 | Resorts World casino-events page | https://www.rwlasvegas.com/gaming/casino-events/ |
| 10 | Caesars Strip poker article (chunks 0–1) | https://www.caesars.com/las-vegas/explore/casino/poker-tournaments-las-vegas-strip |
| 11 | Caesars Palace daily NLH flyer PDF | https://www.caesars.com/content/dam/empire/clv/casino/poker/tournament-schedule/clv-poker-daily-nlh-tournament-flyer-2026.pdf |
| 12 | Horseshoe casino page | https://www.caesars.com/horseshoe-las-vegas/casino |
| 13 | Planet Hollywood casino page | https://www.caesars.com/planet-hollywood/casino |
| 14 | Caesars help/FAQ request | https://www.caesars.com/help/faq |
| 15 | MGM Grand poker page | https://mgmgrand.mgmresorts.com/en/casino/poker-tables.html |
| 16 | MGM Grand weekly schedule PDF | https://assets.contentstack.io/v3/assets/bltc6ce635bc4868eb2/blt5f25277b8918da08/mgm-grand-casino-poker-tournament_schedule.pdf |
| 17 | MGM Grand $120 structure PDF | https://assets.contentstack.io/v3/assets/bltc6ce635bc4868eb2/bltb2a45da7e8ee5621/mgm-grand-casino-poker-120_nlh.pdf |
| 18 | MGM Grand terms page | https://mgmgrand.mgmresorts.com/en/terms-and-conditions.html |
| 19 | MGM Resorts parking page | https://www.mgmresorts.com/en/things-to-do/parking.html |
| 20 | Bellagio poker page | https://bellagio.mgmresorts.com/en/casino/poker.html |
| 21 | Bellagio Saturday PDF | https://assets.contentstack.io/v3/assets/bltc6ce635bc4868eb2/blt6d47974bf5a7d9b6/6af491a391a6e8e4230c9e07/mgm-bellagio-poker-saturdays-$1000-nlh.pdf |
| 22 | Bellagio Friday PDF | https://assets.contentstack.io/v3/assets/bltc6ce635bc4868eb2/blt9cf95b0e60ec253e/6af491a3a9851d75c40be840/mgm-bellagio-poker-fridays-$600-nlh.pdf |
| 23 | Bellagio Sunday PDF | https://assets.contentstack.io/v3/assets/bltc6ce635bc4868eb2/blt07fcf1244a6da661/6af491a339e2b4f6b76a86ad/mgm-bellagio-poker-sundays-$400-horse.pdf |
| 24 | ARIA poker page | https://aria.mgmresorts.com/en/casino/poker.html |

## Findings, source by source (verbatim excerpts)

1. **F56 reconfirmed — still open.** The Wynn Signature Series structures PDF prints exactly
   `LAS VEGAS` / `POKER` / `COMING SOON` (whole document). No structure sheet for the 38
   January 11–24, 2027 rows exists yet.

2. **F80/F103 reconfirmed — still open.** `rwlasvegas.com/gaming/` still carries a "Poker Room" card —
   "For individual games and tournament play, the poker room offers an elevated and technologically
   advanced gaming experience" — linking `https://www.rwlasvegas.com/poker-room/`, which still serves
   the gaming-page shell (identical content, no poker schedule). `rwlasvegas.com/gaming/casino-events/`
   lists only slot-type events ("November Mystery Point Multiplier", "$60,000 Tuesday Rodeo Roundup
   Tournament … $5,000 in weekly prizes", Genting Rewards programs) — no poker tournament.

3. **F20/F73/F90 reconfirmed — still open.** The 2026 Caesars Palace daily NLH flyer is unchanged:
   10 AM $100, 2 PM $160, 6 PM $100, 9 PM $160; each "20,000" chips, "20 Minutes" levels, "$1,000"
   guarantee, "$50" optional add-on; "Registration will close at the start of level seven"; "Of the $100
   buy in, $70 goes to the prize pool and $30 is held by Caesars Palace"; "Of the $160 buy in, $115 goes
   to the prize pool and $45 is held by Caesars Palace"; "Participants may only register themselves, but
   may re-enter, by paying the entry fee, upon elimination within the first break of play." The
   July 17, 2026 article still prints "Every event carries a $100 buy-in" for all four slots (conflict
   stands). The Horseshoe section still prints only the six start times ("9 a.m., 11 a.m., 2 p.m., 5 p.m.,
   8 p.m. and 11 p.m.") and "A mixture of buy-ins, levels and guarantees caters to all participants" —
   no figures. The Horseshoe casino page's Hall of Fame Poker Room block says "Test your luck with 6
   exciting tournament times daily" and publishes no schedule document.

4. **F71/F07/F09/F72 reconfirmed — still open.** MGM Grand poker page: "Daily Texas Hold'em
   Tournaments — 11:00am, 7:00pm and 11:00pm". Weekly schedule PDF (fresh read): headed "MGM Grand
   August Tournament Schedule"; prints 11:10am / 7:10pm / 11:10pm on all seven days; Saturday 11:10am
   is "$150 NLH - $2,000" with "25K Chips / 20 Min"; all other slots "$120 NLH", "25K Chips / 15 Min";
   footnote: "Sunday through Friday - Players with 5 entries or more in $120 Daily Tournaments will
   receive one (1) free entry to the Saturday $150 NLH $2,000 Guarantee". The $120 structure PDF's
   document title is still "Max Stacks Tournament Series".

5. **F02/F52 reconfirmed; F109 new.** The Bellagio Saturday sheet still prints the heading
   "NLH $1100 BUY-IN" against rule 07 "Of the $600 Buy-in, $510 goes to the Prize Pool, $50 is Admin
   Fees and $40 is optional staff gratuity", and the 3rd level still prints blinds "200-4300". **New
   finding:** the same sheet's general rules print a combined final "Day 2 (9/13/26)" (September 13,
   2026 — months before today), four Day-1 flights ("Flights 1A, 1B", "1C", "Flight D"), per-flight
   registration close times ("Approximately 5:15pm for Flights 1A, 1B, 4:15pm for 1C and 9:30pm for
   Flight D"), "Day 1D will have 25-minute levels", and "Each Flight would play until the money
   (12.5%)". The sheet is a stale copy of a past September multi-flight event, not the current weekly
   Saturday schedule; recorded as **F109**.

6. **F03 reconfirmed — still open.** The Bellagio poker page still prints "Tournament play will resume
   on Saturday, July 26, beginning with the $300 PLO Double Board Bomb Pot Tournament at 2 PM PT."
   (no year; the PLO Double Bomb Pot highlight still says "nightly at 6 PM").

7. **F13 reconfirmed — still open.** The ARIA poker page still publishes no tournament schedule and
   asks guests to "call the Poker Room or check out our Twitter account, @ARIAPoker, for the most
   recent information on whether our Daily Tournaments are running as scheduled!"

8. **F99 reconfirmed — unchanged.** The MGM Resorts parking page still prints the eleven-property
   self-parking table with "Registered Hotel Guest | $20 | $20" (Mon–Thu / Fri–Sun) and valet
   "$40 / $40" for "Bellagio, ARIA, Vdara, The Cosmopolitan of Las Vegas, MGM Grand, Mandalay Bay,
   W Las Vegas, Park MGM, The Reserve at Park MGM, New York-New York, and Luxor".

9. **F14/F39/F37 reconfirmed — still open (no property-published room-tax %).** Wynn terms page:
   "A daily resort fee of $55 plus tax will be added to your room account…" (no percentage; the page is
   still the expired 2025 offer, F35). Wynn resort-information page: "Reservations will be charged a
   daily resort fee of $55 plus tax." (twice: Resort Fee and Tower Suites Resort Fee). MGM Grand terms:
   "A daily resort fee of $50.00 plus applicable tax will be applied to all reservations… * Taxes.
   Estimated taxes are based on current tax rates which are subject to change as required by applicable
   law." — no percentage. `caesars.com/help/faq` redirects to the homepage; no FAQ text.

10. **F83 reconfirmed with additional sheet wording — still open.** The Wynn poker page note is
    unchanged ("…the Daily Tournament schedule will be suspended during each Wynn Signature, Wynn
    Millions, and Classic tournament series"). Additionally, each daily structure sheet's own terms say
    the tournament "may be suspended during Seniors Events, Classic Events, or other Tournament
    Series" (Monday–Thursday sheet rule 2; identical wording on the Friday and Sat/Sun sheets). No
    official page states whether the daily slate runs November 27–29, 2026 alongside the WPT World
    Championship.

11. **F105 reconfirmed verbatim — unchanged.** Friday $240 sheet rule 3 still prints "$190 of each
    Entry Fee and rebuy will fund the Tournament prize pool. $10 from each $200 rebuy and $5 from each
    $100 add-on with [sic] be withheld as a service charge for poker staff. $5 from each $200 rebuy and
    $5 from each add-on will be withheld as a tournament fee." — the $200 rebuy's printed components
    sum to $205.

12. **F79/F103 reconfirmed — still open.** The Planet Hollywood casino page still displays "23 Live
    Poker Tables" and "new live action poker room" marketing copy with no schedule, no structure sheet
    and no dedicated poker page.

13. **Bellagio Friday sheet re-read — unchanged.** "$600 Buy-In is allocated as follows: $510 to Prize
    Pool; $50 House Fee; $40 Voluntary Staff Gratuity"; 30,000 starting chips "(15,000 + 15,000)";
    "Players may buy-in and re-enter through the end of level 8 (Including Break)." Multi-entry, as
    published.

14. **Bellagio Sunday sheet re-read — unchanged.** "The $400 Buy-In is allocated as follows: $340 to
    Prize Pool; $35 House Fee; $25 Voluntary Staff Gratuity"; "Players may buy-in and re-enter through
    the end of level 8". Multi-entry, as published.

## Result

- **No published tournament, fee, guarantee, hotel, parking or policy value changed** on any of the 24
  sources re-read today.
- **New irregularity F109:** the official Bellagio "Saturdays | $1,000 NLH" sheet is a stale copy of a
  September 13, 2026 multi-flight event, compounding the F02 three-way buy-in conflict.
- **New spot-check record F110** itemizes the twelve reconfirmations above with fresh 2026-11-19 dates.
- F56, F80, F103, F20, F71, F07, F09, F02, F52, F03, F13, F14, F39, F37, F83, F105, F79 remain open,
  now each re-confirmed live on 2026-11-19 by this session.

## Caesars booking calendars (S22 monitoring, same session)

Both flexible-date booking calendars were requested again for November 2026 on 2026-11-19 UTC:

- Caesars Palace (propCode=clv): "Searching Rates" plus "Sorry! Our website is currently experiencing
  technical difficulties. Please try your search again or call us at 1-888-342-7724." — no rate cells.
- Horseshoe Las Vegas (propCode=blv): identical shell — no rate cells.

Both pages still print their fee blocks, and every figure matches the published data: Caesars Palace
"Resort fees: $62.30 ($54.95 plus $7.35 tax)", "Deposit: $100 per day"; Horseshoe "Resort fees: $56.63
($49.95 plus $6.68 tax)", "Pet fee: $75", "Deposit: $50 per day", "Rollaway bed fee: $30 per day", and
"Rates shown reflect the lowest available rate and include applicable resort fees."

Recorded as item (13) of flag F110. No dated rate is logged because the pages printed none.
