"""Trip cost, computed from published parts and nothing else.

    trip cost = entries x buy-in  +  nights x true cost of a night

The true cost of a night is the published room rate plus the mandatory resort
fee plus tax on both.  Every component keeps the official page it came from, so
a reader can re-derive the total by hand.

This module is the single place the arithmetic is defined; the site's
calculator reads the numbers it publishes in ``site/data.json`` under
``tripCostModel`` so the browser and the tests cannot drift apart.
"""
from __future__ import annotations

import math


def _optional_number(value, *, integer=False):
    """Parse a non-negative published/input number; blanks and invalid values stay unknown."""
    if value is None or (isinstance(value, str) and not value.strip()) or isinstance(value, bool):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError):
        return None
    if not math.isfinite(number) or number < 0:
        return None
    if integer:
        if not number.is_integer():
            return None
        return int(number)
    return number


def true_nightly(rate, resort_fee, tax_pct):
    """Rate + mandatory resort fee + tax on both, rounded to the cent.

    Tax is applied to the room rate and the resort fee, because every property
    terms page reviewed says the fee is "plus applicable tax" and Bellagio's
    terms add that lodging taxes apply to the resort fee as well. A missing,
    invalid or negative component is unknown, not zero; explicit zero is valid.
    """
    rate = _optional_number(rate)
    resort_fee = _optional_number(resort_fee)
    tax_pct = _optional_number(tax_pct)
    if any(value is None for value in (rate, resort_fee, tax_pct)):
        return None
    return round((rate + resort_fee) * (1 + tax_pct / 100), 2)


def trip_cost(entries, buy_in, nights, rate, resort_fee, tax_pct,
              parking_per_night=None, extra_nights_at=None, buy_in_exact=None):
    """Return the published-parts trip total with its breakdown.

    ``extra_nights_at`` lets a caller price the same stay at a second published
    rate (for example the $209 Palazzo starting rate) without inventing a
    blended average. Missing or invalid inputs remain unknown; explicit zero is
    allowed. ``tripTotal`` is the all-in total including parking, so it remains
    unknown when any required component is unknown.
    """
    entries = _optional_number(entries, integer=True)
    buy_in = _optional_number(buy_in)
    nights = _optional_number(nights, integer=True)
    rate = _optional_number(rate)
    resort_fee = _optional_number(resort_fee)
    tax_pct = _optional_number(tax_pct)
    parking = _optional_number(parking_per_night)
    exact_buy_in = _optional_number(buy_in_exact)

    # The seven chosen primaries are $200, $200, $400, $300, $600, $600 and $300, which
    # sum to exactly $2,600. Their mean is $371.428571..., so multiplying the rounded
    # mean by seven prints a phantom cent ($2,600.01). When the caller can supply the
    # exact sum, use it, and publish the integer average beside it so a reader checking
    # 7 x $371.43 is not left thinking the page made an arithmetic error.
    if exact_buy_in is not None:
        tournament_total = round(exact_buy_in, 2)
    elif entries is not None and buy_in is not None:
        tournament_total = round(entries * buy_in, 2)
    else:
        tournament_total = None
    nightly = true_nightly(rate, resort_fee, tax_pct)
    lodging_total = (round(nights * nightly, 2)
                     if nights is not None and nightly is not None else None)
    parking_total = (round(nights * parking, 2)
                     if nights is not None and parking is not None else None)
    grand = (round(tournament_total + lodging_total + parking_total, 2)
             if all(value is not None for value in (tournament_total, lodging_total, parking_total)) else None)

    out = {
        "entries": entries,
        "buyIn": buy_in,
        "tournamentTotal": tournament_total,
        "nights": nights,
        "roomRatePerNight": rate,
        "resortFeePerNight": resort_fee,
        "taxPct": tax_pct,
        "trueCostPerNight": nightly,
        "lodgingTotal": lodging_total,
        "parkingPerNight": parking,
        "parkingTotal": parking_total,
        "tripTotal": grand,
        "formula": "entries x buy-in + nights x (room rate + resort fee) x (1 + tax)",
    }
    if extra_nights_at is not None and not (isinstance(extra_nights_at, str) and not extra_nights_at.strip()):
        alt_rate = _optional_number(extra_nights_at)
        alt = true_nightly(alt_rate, resort_fee, tax_pct) if alt_rate is not None else None
        out["alternateRatePerNight"] = alt_rate
        out["alternateTrueCostPerNight"] = alt
        out["alternateTripTotal"] = (round(tournament_total + nights * alt + parking_total, 2)
                                     if all(value is not None for value in
                                            (tournament_total, nights, alt, parking_total)) else None)
    return out


# --------------------------------------------------------------------------
# Verified input set.  Every figure below is read from an official page; the
# source is recorded beside it and re-checked by scripts/verify_site.py.
# --------------------------------------------------------------------------
VERIFIED_INPUTS = {
    "hotel": "The Venetian / The Palazzo poker suite rate",
    "resortFeePerNight": 55.0,
    "resortFeeSource": "https://www.venetianlasvegas.com/resort/resort-fee.html",
    "taxPct": 13.38,
    "taxSource": "https://www.venetianlasvegas.com/legal/hotel-terms-and-conditions.html",
    "taxExcerpt": "Daily rates do not include the applicable Clark County Room Tax of 13.38%.",
    "startingRateLow": 119.0,
    "startingRateHigh": 209.0,
    "startingRateSource": "https://www.venetianlasvegas.com/resort/casino/poker/suite-rates.html",
    "startingRateExcerpt": "These rates will start as low as $119 and $209 and can be higher.",
    "parkingPerNight": 20.0,
    # The excerpt below is verbatim from the poker room's own parking page, so that page is the
    # citation for the fee as well; the hotel terms page carries the same $20 figure in its own
    # wording and is cited by the hotel rows for it.
    "parkingSource": "https://www.venetianlasvegas.com/resort/casino/poker/player-parking.html",
    "parkingExcerpt": "The daily fee for registered hotel guests is $20/day, seven days a week.",
    # The poker room's own parking page prints a conditional waiver of that fee for
    # players.  It is published beside the figure and deliberately NOT netted off it:
    # no official source publishes a finish time, so a three-hour session cannot be
    # confirmed for a named event, and the page requires a supervisor to validate it.
    "parkingWaiverSource": "https://www.venetianlasvegas.com/resort/casino/poker/player-parking.html",
    "parkingWaiverExcerpt": ("Players in the poker room who play three hours or more in tournament or cash games will "
                            "receive complimentary self-parking for the day. Players must visit a supervisor at the end "
                            "of their session to confirm qualifications for complimentary self-parking."),
    "parkingWaiverRetrieved": "2026-11-17",
    "cancellation": "A deposit covering suite, fee and tax is billed on confirmation. Prepaid offers are non-cancellable "
                    "and non-refundable. Early checkout costs $100 plus tax. No date-specific cancellation deadline was "
                    "published for a flexible booking on the reviewed pages.",
    "cancellationSource": "https://www.venetianlasvegas.com/legal/hotel-terms-and-conditions.html",
    "qualification": "Six hours of active live cash play, or a buy-in to a $300 or higher tournament, for each night stayed. "
                     "The rate is adjusted to the prevailing rate for any night the requirement is missed.",
    "qualificationSource": "https://www.venetianlasvegas.com/resort/casino/poker/suite-rates.html",
}


def published_model(entries, buy_in, nights, buy_in_exact=None):
    """The model the dashboard publishes, built only from VERIFIED_INPUTS."""
    v = VERIFIED_INPUTS
    low = trip_cost(entries, buy_in, nights, v["startingRateLow"], v["resortFeePerNight"],
                    v["taxPct"], v["parkingPerNight"], extra_nights_at=v["startingRateHigh"],
                    buy_in_exact=buy_in_exact)
    exact_buy_in = _optional_number(buy_in_exact)
    if exact_buy_in is not None:
        low["primaryBuyInSum"] = round(exact_buy_in, 2)
        low["buyInNote"] = ("The published average is the exact mean of the chosen primaries, rounded to the cent "
                            "(sum $2,600.00 / 7 = $371.428571...). The tournament total uses the exact sum, so "
                            "7 x $371.43 lists as $2,600.00 rather than as a phantom $2,600.01.")
    low.update({
        "basis": "Published starting rate (a floor, not a quote)",
        "hotel": v["hotel"],
        "sources": {
            "startingRate": v["startingRateSource"],
            "resortFee": v["resortFeeSource"],
            "tax": v["taxSource"],
            "parking": v["parkingSource"],
            "cancellation": v["cancellationSource"],
            "qualification": v["qualificationSource"],
        },
        "excerpts": {
            "startingRate": v["startingRateExcerpt"],
            "tax": v["taxExcerpt"],
            "parking": v["parkingExcerpt"],
            "qualification": v["qualification"],
        },
        "parkingWaiver": {
            "status": "published-conditional",
            "excerpt": v["parkingWaiverExcerpt"],
            "source": v["parkingWaiverSource"],
            "retrieved": v["parkingWaiverRetrieved"],
            "appliedToTotals": False,
            "note": ("The $20 per night parking line above is the registered-guest self-parking fee. The resort's own "
                     "poker-room parking page prints a waiver of it for players who play three hours or more, confirmed "
                     "by a supervisor at the end of the session. The waiver is not netted off this total: no official "
                     "source publishes a finish time for any event (F16), so the three-hour condition cannot be "
                     "confirmed from a schedule, and a rate the venue reserves the right to change is not a saving to "
                     "bank. Set the parking field to 0 in the calculator only once the room has confirmed it for you."),
        },
        "cancellation": v["cancellation"],
        "note": ("Computed from the published starting rate, the published $55 resort fee and the published "
                 "13.38% Clark County room tax. It is a floor for the property, not a quote for any date. The official "
                 "booking engine quoted a dated checkout total for the 23-30 Nov 2026 trip window on 2026-11-17; that "
                 "quote is in liveQuote and is not this floor. The parking line is the registered-guest fee; the venue "
                 "publishes a conditional waiver of it for players (see parkingWaiver), which is not netted off."),
    })
    return low
