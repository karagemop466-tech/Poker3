# Official excerpts read on 2026-11-17

Verbatim text taken from official pages on 2026-11-17 while re-verifying the canonical data.
`scripts/verify_live_official.py` asserts that the canonical values in `site/data.json` are the
ones these excerpts support. Nothing here is paraphrased.

## 1. Venetian poker-suite rates

Source: https://www.venetianlasvegas.com/resort/casino/poker/suite-rates.html
Retrieved 2026-11-17 by fetch_page (1 chunk).

> We offer suite rates for poker players who are interested in staying in either The Venetian or The Palazzo. These
> rates will start as low as $119 and $209 and can be higher. Future rates are only provided out to a maximum of 150
> days from the current date. Rates are subject to qualifying poker play and availability based on hotel occupancy.
> Blackout dates may apply. Rates are based on single/double occupancy in a Luxury King Suite in The Venetian or The
> Palazzo. There is a $55 resort fee per night stayed.

> The poker rate cannot be combined with any other promotional rates. In order to qualify for these rates, the first
> step is to book your suite through The Venetian Resort Las Vegas by calling 866.255.8936 and mentioning code
> EPOKR25.

> During your stay, you will be required to play six hours of active live cash gameplay or buy in to a $300 or higher
> tournament for each night stayed. Poker play for any guests listed in your suite will also count toward these
> requirements. These requirements must be met prior to 2 a.m. the last night stayed. For any nights you fail to
> complete these requirements, your nightly suite rate will be adjusted to the prevailing rate, and you will not
> receive the poker suite rate discount.

Supports: `hotels[venetian].baseRateFloor = 119`, `baseRateCeiling = 209`, `resortFee = 55`,
`qualification` (six hours, $300 or higher, 2 a.m., code EPOKR25, 866.255.8936), and the same values on
`hotels[palazzo]`.

## 2. Wynn daily tournament poster

Source: https://cdn.wynnresorts.com/image/upload/v1752011166/visitwynn_pdfs_files/Poker/Daily%20Tournaments/poker-daily-tournament-poster.pdf
Retrieved 2026-11-17 by fetch_page (1 chunk).

> # DAILY TOURNAMENTS
>
> ## $10,000 GUARANTEE $40,000 GUARANTEE
>
> Monday-Thursday • $200 NLH • 12 p.m. Friday • $240 NLH Rebuy • 12 p.m.
>
> ## $25,000 GUARANTEE $25,000 GUARANTEE
>
> Saturday • $200 NLH • 12 p.m. Sunday • $200 NLH • 12 p.m.
>
> ## NIGHTLY
>
> $10,000 Guarantee • $160 NLH • 6 p.m.
>
> For information, please call (702) 770-7654 or visit wynnpoker.com

Note: the poster prints an en dash in "Monday-Thursday"; it is transcribed here with a hyphen.

Supports the four recurring Wynn rows: Mon-Thu $200 / $10,000 / 12:00 PM, Fri $240 rebuy / $40,000 / 12:00 PM,
Sat-Sun $200 / $25,000 / 12:00 PM, nightly $160 / $10,000 / 6:00 PM. All four sit in the extra-spend category
because the Friday event is a rebuy and the poster sends players to wynnpoker.com for the fee split.

## 3. Venetian booking engine, quoted 2026-11-17

Source: https://www.venetianlasvegas.com/booking?adults[]=2&arrival_date=2026-11-17&children[]=0&departure_date=2026-11-19&view=calendar

> ## venetian Newly Remodeled Luxury King
> Best Available Rate & Suite
> Estimated cost of stay: $1,015.89
> Guests: 2 Adults · Number of Nights: 2 · Check-in Date: November 17, 2026 · Check-out Date: November 19, 2026
> Offer: Book Direct: Up to 25% Off · Suite Type: venetian Newly Remodeled Luxury King
> Average Rate $448.00 · November 17 Rate $621.75 · Resort Fee $55.00 · November 18 Rate $164.25 · Resort Fee $55.00
> Taxes $119.89 · Total $1,015.89

Source: https://www.venetianlasvegas.com/booking?adults[]=2&arrival_date=2026-11-20&children[]=0&departure_date=2026-11-22&view=calendar

> ## venetian Newly Remodeled Luxury Two Queen
> Estimated cost of stay: $2,504.00
> Guests: 2 Adults · Number of Nights: 2 · Check-in Date: November 20, 2026 · Check-out Date: November 22, 2026
> Offer: Book Direct: Up to 25% Off · Suite Type: venetian Newly Remodeled Luxury Two Queen
> Average Rate $1,104.25 · November 20 Rate $899.25 · Resort Fee $55.00 · November 21 Rate $1,199.25 · Resort Fee $55.00
> Taxes $295.50 · Total $2,504.00

Arithmetic: (621.75 + 55 + 164.25 + 55) x 0.1338 = 119.88, printed 119.89 (one cent of rounding).
(899.25 + 55 + 1199.25 + 55) x 0.1338 = 295.50, printed 295.50. Both totals reconcile.

## 4. Stay windows that returned no price, 2026-11-17

| Stay window | What the official engine returned |
| --- | --- |
| Nov 25 - Dec 2, 2026 (7 nights) | Every calendar cell rendered as the placeholder "$XXX"; no suite panel. |
| Nov 25 - Nov 27, 2026 | The booking page did not finish loading; no date selector, calendar or quote. |
| Nov 27 - Nov 28, 2026 | Calendar rendered; no suite panel, so no rate for that night. |
| Nov 30 - Dec 1, 2026 | Every calendar cell rendered as "$XXX"; no suite panel. |
