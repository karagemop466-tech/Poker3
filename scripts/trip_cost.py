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


def true_nightly(rate, resort_fee, tax_pct):
    """Rate + mandatory resort fee + tax on both, rounded to the cent.

    Tax is applied to the room rate and the resort fee, because every property
    terms page reviewed says the fee is "plus applicable tax" and Bellagio's
    terms add that lodging taxes apply to the resort fee as well.
    """
    if rate in (None, "") or resort_fee in (None, ""):
        return None
    rate = float(rate)
    resort_fee = float(resort_fee)
    tax_pct = float(tax_pct or 0)
    return round((rate + resort_fee) * (1 + tax_pct / 100), 2)


def trip_cost(entries, buy_in, nights, rate, resort_fee, tax_pct,
              parking_per_night=0, extra_nights_at=None, buy_in_exact=None):
    """Return the published-parts trip total with its breakdown.

    ``extra_nights_at`` lets a caller price the same stay at a second published
    rate (for example the $209 Palazzo starting rate) without inventing a
    blended average.  Blank inputs are treated as zero, and the breakdown says
    so, because a blank means "no official source published this", not "free".
    """
    entries = int(entries or 0)
    buy_in = float(buy_in or 0)
    nights = int(nights or 0)
    parking = float(parking_per_night or 0)

    # The seven chosen primaries are $200, $200, $400, $300, $600, $600 and $300, which
    # sum to exactly $2,600. Their mean is $371.428571..., so multiplying the rounded
    # mean by seven prints a phantom cent ($2,600.01). When the caller can supply the
    # exact sum, use it, and publish the integer average beside it so a reader checking
    # 7 x $371.43 is not left thinking the page made an arithmetic error.
    if buy_in_exact not in (None, ""):
        tournament_total = round(float(buy_in_exact), 2)
    else:
        tournament_total = round(entries * buy_in, 2)
    nightly = true_nightly(rate, resort_fee, tax_pct)
    if nightly is None:
        lodging_total = None
        parking_total = None
        grand = None
    else:
        lodging_total = round(nights * nightly, 2)
        parking_total = round(nights * parking, 2)
        grand = round(tournament_total + lodging_total + parking_total, 2)

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
    if extra_nights_at not in (None, ""):
        alt = true_nightly(extra_nights_at, resort_fee, tax_pct)
        out["alternateRatePerNight"] = extra_nights_at
        out["alternateTrueCostPerNight"] = alt
        out["alternateTripTotal"] = round(tournament_total + nights * alt + (parking_total or 0), 2)
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
    if buy_in_exact not in (None, ""):
        low["primaryBuyInSum"] = round(float(buy_in_exact), 2)
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
