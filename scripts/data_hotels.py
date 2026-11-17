"""Hotel, rate-log and walking-route data.

Every value was read from an official property page on 2026-11-16.  Walking
minutes are Google Maps walking estimates captured on the same date (the
"Maps estimate" label is used everywhere they appear); the venues themselves
publish no walking times.  Rates are kept as a dated log, never as a single
value: see RATE_LOG.
"""

RETRIEVED = "2026-11-16"

VENETIAN_SUITE_RATES = "https://www.venetianlasvegas.com/resort/casino/poker/suite-rates.html"
VENETIAN_RESORT_FEE = "https://www.venetianlasvegas.com/resort/resort-fee.html"
# Per-date official booking link for the trip stay (2 adults, Nov 23 to Nov 30, 2026: seven nights, check-out
# 30 Nov). The engine priced this window in full on 2026-11-17 (see VENETIAN_QUOTE_TRIP). The earlier Nov 25 -
# Dec 2 window is kept as VENETIAN_OLD_WINDOW_BOOKING for the log only. This module never stores a price from a link.
VENETIAN_FIXED_STAY_BOOKING = ("https://www.venetianlasvegas.com/booking?adults[]=2&arrival_date=2026-11-23"
                               "&children[]=0&departure_date=2026-11-30&view=calendar")
VENETIAN_OLD_WINDOW_BOOKING = ("https://www.venetianlasvegas.com/booking?adults[]=2&arrival_date=2026-11-25"
                               "&children[]=0&departure_date=2026-12-02&view=calendar")
VENETIAN_HOTEL_TERMS = "https://www.venetianlasvegas.com/legal/hotel-terms-and-conditions.html"
WYNN_ROOMS = "https://www.wynnlasvegas.com/rooms-and-suites"
# The page the earlier build cited (terms-and-conditions/850070) is an expired
# 2025 DINING CREDIT offer: its own text says a stay "must be completed on or
# before September 30, 2025".  The live, non-offer policy page below is therefore
# used instead; the expired page is kept only as a cross-check and is flagged.
WYNN_TERMS = "https://www.wynnlasvegas.com/about-us/resort-information"
WYNN_PARKING = "https://www.wynnlasvegas.com/about-us/parking"
WYNN_EXPIRED_OFFER = "https://www.wynnlasvegas.com/terms-and-conditions/850070"
MGM_TERMS = "https://mgmgrand.mgmresorts.com/en/terms-and-conditions.html"
ARIA_TERMS = "https://aria.mgmresorts.com/en/terms-and-conditions.html"
BELLAGIO_HOTEL = "https://bellagio.mgmresorts.com/en/hotel.html"
BELLAGIO_TERMS = "https://bellagio.mgmresorts.com/en/terms-and-conditions.html"
MGM_HOTEL = "https://mgmgrand.mgmresorts.com/en/hotel.html"
CAESARS_HOTEL = "https://www.caesars.com/caesars-palace/hotels"
HORSESHOE_HOTEL = "https://www.caesars.com/horseshoe-las-vegas/hotels"
ARIA_HOTEL = "https://aria.mgmresorts.com/en/hotel.html"

TAX_RATE = 13.38  # Clark County room tax, printed in the Venetian hotel terms

# --- Caesars Entertainment properties: read from the properties' own pages on 2026-11-17 ---
# The official Caesars booking page publishes a "Hotel Policies > Fees" block for each property
# even when the rate grid is empty.  That block is the fee source for Caesars Palace and
# Horseshoe Las Vegas; the room-tax percentage is still not printed, so `taxRate` stays blank.
CAESARS_CALENDAR = ("https://www.caesars.com/book/hotel-calendar?dateSearchFormat=flexible-dates"
                    "&flexibleMonth=December&propCode=clv")
HORSESHOE_CALENDAR_NOV = ("https://www.caesars.com/book/hotel-calendar?dateSearchFormat=flexible-dates"
                          "&flexibleMonth=November&propCode=blv")
HORSESHOE_CALENDAR_DEC = ("https://www.caesars.com/book/hotel-calendar?dateSearchFormat=flexible-dates"
                          "&flexibleMonth=December&propCode=blv")
CAESARS_BOOKING_HOMEPAGE = "https://www.caesars.com/caesars-palace/hotel"
# The county/city room-tax schedule, used only as a labelled reference where a property prints
# "plus tax" without a percentage.  It is published by the City of Las Vegas for establishments
# it licences; the Strip resorts sit in unincorporated Clark County, so this repository does NOT
# substitute the figure into a property-published column.
ROOM_TAX_REFERENCE = "https://www.clarkcountynv.gov/adobe/assets/urn:aaid:aem:689ef54f-ec0d-4bb6-b8ea-05a82887561f/original/as/genl-info-guide-for-tles-july-2021.pdf"
ROOM_TAX_REFERENCE_NOTE = ("13.38% is the combined transient lodging tax rate published for properties inside the "
                           "Primary Gaming Corridor (13.00% outside it). Government sources read 2026-11-17: the Clark "
                           "County Department of Business License schedule (Appendix III) lists the corridor resort "
                           "hotels at 13.38% line by line; the City of Las Vegas room-tax packet "
                           "(https://files.lasvegasnevada.gov/business-licensing/RoomTaxPacket.pdf) prints the same "
                           "split. The rate is a reference beside the property's own figure, never a substitute for it.")

# Dated calendar cells read off the official Horseshoe booking page at 01:26 UTC and again at
# 01:31 UTC on 2026-11-17.  The page states: "Rates shown reflect the lowest available rate and
# include applicable resort fees."  They are observations of a moving calendar, not quotes.
HORSESHOE_CALENDAR_NOV_CELLS = [
    ("2026-11-16", 55), ("2026-11-17", 72), ("2026-11-18", 99), ("2026-11-19", 99),
    ("2026-11-20", 181), ("2026-11-21", 247), ("2026-11-22", 55), ("2026-11-23", 55),
    ("2026-11-24", 55), ("2026-11-25", 55), ("2026-11-26", 55), ("2026-11-27", 181),
    ("2026-11-28", 115), ("2026-11-29", 272), ("2026-11-30", 470),
]
HORSESHOE_CALENDAR_DEC_CELLS = [
    ("2026-12-01", 379), ("2026-12-02", "Sold Out"), ("2026-12-03", "Sold Out"),
    ("2026-12-04", 189), ("2026-12-05", 313), ("2026-12-06", 214), ("2026-12-07", 198),
    ("2026-12-08", 148), ("2026-12-09", 132), ("2026-12-10", 305), ("2026-12-11", 404),
    ("2026-12-12", 363), ("2026-12-13", 55), ("2026-12-14", 55), ("2026-12-15", 55),
    ("2026-12-16", 55), ("2026-12-17", 55), ("2026-12-18", 61), ("2026-12-19", 189),
    ("2026-12-20", 55), ("2026-12-21", 55), ("2026-12-22", 55), ("2026-12-23", 55),
    ("2026-12-24", 55), ("2026-12-25", 115), ("2026-12-26", 115), ("2026-12-27", 132),
    ("2026-12-28", 115), ("2026-12-29", 115), ("2026-12-30", 181), ("2026-12-31", 445),
]
# The first reading of the same December page, 01:26 UTC, before the 01:31 UTC values above.
HORSESHOE_CALENDAR_DEC_FIRST_READ = {
    "2026-12-01": 449, "2026-12-04": 219, "2026-12-05": 369, "2026-12-06": 249,
    "2026-12-07": 229, "2026-12-08": 169, "2026-12-09": 149, "2026-12-10": 359,
    "2026-12-11": 479, "2026-12-12": 429, "2026-12-13": 56, "2026-12-18": 63,
    "2026-12-19": 219, "2026-12-25": 129, "2026-12-27": 149, "2026-12-30": 209,
    "2026-12-31": 529,
}


def _cells(pairs):
    return ", ".join(f"{d[5:]} ${v}" if isinstance(v, int) else f"{d[5:]} {v}" for d, v in pairs)

# The official booking engine, opened with the dates and party size in the URL.
VENETIAN_QUOTE_URL = ("https://www.venetianlasvegas.com/booking?adults[]=2&arrival_date=2026-11-17"
                      "&children[]=0&departure_date=2026-11-19&view=calendar")
VENETIAN_CALENDAR_NOV_URL = ("https://www.venetianlasvegas.com/booking?adults[]=2&arrival_date=2026-11-17"
                             "&children[]=0&departure_date=2026-11-19&view=calendar")
VENETIAN_CALENDAR_TRIP_URL = ("https://www.venetianlasvegas.com/booking?adults[]=2&arrival_date=2026-11-23"
                              "&children[]=0&departure_date=2026-11-30&view=calendar")

def next_day(iso_date: str) -> str:
    """The following calendar day, used to turn a stay night into a one-night booking URL."""
    from datetime import date, timedelta
    y, m, d = (int(x) for x in iso_date.split("-"))
    return (date(y, m, d) + timedelta(days=1)).isoformat()


def venetian_stay_url(check_in: str, check_out: str, adults: int = 2) -> str:
    """The official booking engine, opened with the stay dates and party size in the URL.

    This URL pattern was opened successfully on 2026-11-17 for five different stay windows;
    each returned the engine's own calendar and, where a suite was available, its own
    itemised quote panel.
    """
    return (f"https://www.venetianlasvegas.com/booking?adults[]={adults}&arrival_date={check_in}"
            f"&children[]=0&departure_date={check_out}&view=calendar")


# The dated official checkout totals read straight off the official booking engine.
# Every line below is printed on the page.  They are kept as a log, never overwritten:
# the same stay printed a different price on two consecutive days.

VENETIAN_QUOTE = dict(
    property="The Venetian Resort - venetian Newly Remodeled Luxury King suite",
    checkIn="2026-11-17", checkOut="2026-11-19", guests=2, nights=2,
    offer="Book Direct: Up to 25% Off",
    suiteDetail="Approximately 650 square feet, king bed, living room, Roman tub",
    nightOne=dict(date="2026-11-17", rate=621.75, resortFee=55.00),
    nightTwo=dict(date="2026-11-18", rate=164.25, resortFee=55.00),
    taxes=119.89, total=1015.89, averageRate=448.00,
    derivedNightly=[767.30, 248.59], derivedTotal=1015.89,
    note=("Read straight off the official booking engine on 2026-11-17. Each derived nightly figure is "
          "(rate + $55 resort fee) x 1.1338 rounded to the cent: $767.30 and $248.59, which add to $1,015.89, the "
          "printed total exactly. The same rounding reconciles the 2026-11-16 observation of this stay to its printed "
          "total as well, so the 13.38% Clark County room tax is confirmed from an official source to be charged on "
          "the rate and the resort fee together."),
    source=VENETIAN_QUOTE_URL, observedOn="2026-11-17")

# The same quote one day earlier, kept because a rate log is a dated series, not a single value.
# The night of Nov 17 fell from $824.25 to $621.75 in under 24 hours while the Nov 18 night did not move.
VENETIAN_QUOTE_PRIOR = dict(
    property="The Venetian Resort - venetian Newly Remodeled Luxury King suite",
    checkIn="2026-11-17", checkOut="2026-11-19", guests=2, nights=2,
    offer="Book Direct: Up to 25% Off",
    nightOne=dict(date="2026-11-17", rate=824.25, resortFee=55.00),
    nightTwo=dict(date="2026-11-18", rate=164.25, resortFee=55.00),
    taxes=146.98, total=1245.48, averageRate=549.25,
    # (rate + $55 resort fee) x 1.1338, rounded to cents per night, as printed.
    # $996.89 + $248.59 = $1,245.48, which is the venue's printed total exactly.
    # An earlier version used 996.91 / 248.61 and a note excusing a 4-cent gap;
    # that gap was arithmetic error in this repository, not the venue's rounding.
    # Two sessions found this independently; both agree on 996.89 / 248.59.
    derivedNightly=[996.89, 248.59], derivedTotal=1245.48,
    note=("The two derived nightly figures, (rate + $55 resort fee) x 1.1338 rounded to cents, add to $1,245.48, the "
          "printed total exactly, so the 13.38% tax applies to the rate and to the resort fee together. This stay was "
          "quoted again on 2026-11-17 at a lower price; see the next log entry."),
    source=VENETIAN_QUOTE_URL, observedOn="2026-11-16")

# The same stay, re-read from the same official booking engine one day later.
VENETIAN_QUOTE_2026_11_17 = dict(
    property="The Venetian Resort - venetian Newly Remodeled Luxury King suite",
    checkIn="2026-11-17", checkOut="2026-11-19", guests=2, nights=2,
    offer="Book Direct: Up to 25% Off",
    suiteDetail="Approximately 650 square feet, king bed, living room, Roman tub",
    nightOne=dict(date="2026-11-17", rate=621.75, resortFee=55.00),
    nightTwo=dict(date="2026-11-18", rate=164.25, resortFee=55.00),
    taxes=119.89, total=1015.89, averageRate=448.00,
    derivedNightly=[767.30, 248.59], derivedTotal=1015.89,
    note=("Re-read from the same official booking engine on 2026-11-17. The first night fell from $824.25 to $621.75 "
          "while the second night was unchanged at $164.25, so the checkout total fell from $1,245.48 to $1,015.89. "
          "The engine's own 'Average Rate' line prints $448.00, which equals the average of (rate + $55 resort fee) "
          "for the two nights, confirming that its average-rate figure includes the resort fee."),
    source=VENETIAN_QUOTE_URL, observedOn="2026-11-17")

# A second stay window quoted by the same engine on the same day, for a different suite type.
VENETIAN_QUOTE_NOV_20 = dict(
    property="The Venetian Resort - venetian Newly Remodeled Luxury Two Queen suite",
    checkIn="2026-11-20", checkOut="2026-11-22", guests=2, nights=2,
    offer="Book Direct: Up to 25% Off",
    suiteDetail="Approximately 750 square feet, two queen beds, living room, Roman tub",
    nightOne=dict(date="2026-11-20", rate=899.25, resortFee=55.00),
    nightTwo=dict(date="2026-11-21", rate=1199.25, resortFee=55.00),
    taxes=295.50, total=2504.00, averageRate=1104.25,
    derivedNightly=[1081.93, 1422.07], derivedTotal=2504.00,
    note=("Quoted by the official booking engine on 2026-11-17 for the same party size. The derived nightly figures, "
          "(rate + $55) x 1.1338, add to $2,504.00 and match the printed total exactly. This is the third independent "
          "quote whose arithmetic confirms the true-cost formula; the engine picks the suite type, so the King and the "
          "Two Queen quotes are not directly comparable on price."),
    source=venetian_stay_url("2026-11-20", "2026-11-22"), observedOn="2026-11-17")

# The trip stay, 23 to 30 November 2026 (seven nights, check-out 11:00 a.m. on 30 November), quoted by the official
# booking engine on 2026-11-17 after 21:54 UTC (sandbox clock). Every figure is printed on the page. The per-night
# all-in figures are derived as (rate + $55 resort fee) x 1.1338, rounded to the cent, and they add to the printed
# checkout total exactly. This is the first dated checkout total for the trip window itself.
VENETIAN_QUOTE_TRIP = dict(
    property="The Venetian Resort - venetian Newly Remodeled Luxury King suite",
    checkIn="2026-11-23", checkOut="2026-11-30", guests=2, nights=7,
    offer="Book Direct: Up to 25% Off",
    suiteDetail="Approximately 650 square feet, king bed, living room, Roman tub",
    nightly=[("2026-11-23", 164.25), ("2026-11-24", 164.25), ("2026-11-25", 201.75), ("2026-11-26", 231.75),
             ("2026-11-27", 1649.25), ("2026-11-28", 554.25), ("2026-11-29", 186.75)],
    resortFeePerNight=55.00,
    taxes=473.30, total=4010.55, averageRate=505.32,
    derivedNightly=[248.59, 248.59, 291.10, 325.12, 1932.28, 690.77, 274.10], derivedTotal=4010.55,
    note=("Re-read from the official booking engine on 2026-11-17 after 21:54 UTC. The engine's Average Rate of $505.32 "
          "is the average of (rate + $55 resort fee) over the seven nights. The printed taxes of $473.30 equal the sum of "
          "13.38% of (rate + resort fee) on each night, rounded to the cent per night. This is the engine's best available "
          "rate for a Luxury King suite. It is not the phone-only poker rate (code EPOKR25; see F66)."),
    source=VENETIAN_CALENDAR_TRIP_URL, observedOn="2026-11-17")

VENETIAN_QUOTES = [VENETIAN_QUOTE, VENETIAN_QUOTE_2026_11_17, VENETIAN_QUOTE_NOV_20, VENETIAN_QUOTE_TRIP]

# Stay windows the engine was opened for on 2026-11-17 that returned no suite and no price.
# Each is a dated observation of the official engine, not an inference.
VENETIAN_NO_QUOTE_WINDOWS = [
    dict(checkIn="2026-11-25", checkOut="2026-12-02", nights=7,
         result="No suite panel and no price. Every calendar cell rendered as the placeholder '$XXX', and the seven "
                "trip nights rendered with no figure at all.",
         url=venetian_stay_url("2026-11-25", "2026-12-02")),
    dict(checkIn="2026-11-25", checkOut="2026-11-27", nights=2,
         result="The booking page did not finish loading; no date selector, no calendar and no quote were returned.",
         url=venetian_stay_url("2026-11-25", "2026-11-27")),
    dict(checkIn="2026-11-27", checkOut="2026-11-28", nights=1,
         result="The calendar rendered but no suite panel was returned, so no rate and no total for that night.",
         url=venetian_stay_url("2026-11-27", "2026-11-28")),
    dict(checkIn="2026-11-30", checkOut="2026-12-01", nights=1,
         result="Every calendar cell rendered as the placeholder '$XXX' and no suite panel was returned.",
         url=venetian_stay_url("2026-11-30", "2026-12-01")),
]

# Calendar cells published by the same booking engine for November 2026.  The page
# states: "Pricing shown is best available suite and rate, includes daily resort fee,
# excludes taxes."  They are observations, not quotes.
# Read on 2026-11-17 from the booking calendar rendered for two independent arrival dates
# (Nov 17-19 and Nov 30-Dec 2). The two renderings agreed on every cell they both showed, so
# the row below is a reproducible observation rather than a single parse.
#
# CORRECTION 2026-11-17: the 2026-11-16 reading of this calendar was shifted one day later from
# Nov 26 onward. Its Nov 26-30 cells ($190, $210, $905, $340, $165) are in fact the cells for
# Nov 25-29. The shift hid two things: that Nov 27, 2026 is the $905 night after Thanksgiving,
# and that Nov 30 and Dec 1 publish no price at all. Recorded as flag F35.
VENETIAN_CALENDAR_NOV = [
    ("2026-11-16", 555), ("2026-11-17", 440), ("2026-11-18", 165), ("2026-11-19", 405),
    ("2026-11-20", 655), ("2026-11-21", 855), ("2026-11-22", 165), ("2026-11-23", 165),
    ("2026-11-24", 165), ("2026-11-25", 190), ("2026-11-26", 210), ("2026-11-27", 905),
    ("2026-11-28", 340), ("2026-11-29", 165), ("2026-11-30", ""), ("2026-12-01", ""),
]

# The same official calendar, re-read on 2026-11-17 with two different stay windows open.
# The cells do NOT hold a fixed per-night price: the value printed for a given date changes
# with the stay window that is selected.  Three examples, read on the same day:
#
#   date      | window Nov 17-19 open | window Nov 27-28 open
#   Nov 16    | $555                  | $854
#   Nov 22    | $165                  | $230
#   Nov 27    | $905                  | $1,814
#
# Because of that, no calendar cell is used anywhere on this site as evidence of a nightly
# rate.  Only the engine's itemised quote panel is treated as a price.  Recorded as F31.
VENETIAN_CALENDAR_2026_11_17 = dict(
    observedOn="2026-11-17",
    footnote=("Pricing shown is best available suite and rate, includes daily resort fee, excludes taxes."),
    windowA=dict(url=venetian_stay_url("2026-11-17", "2026-11-19"), label="stay window Nov 17-19 open",
                 cells=[("2026-11-16", 555), ("2026-11-17", "placeholder"), ("2026-11-18", "placeholder"),
                        ("2026-11-19", 405), ("2026-11-20", 655), ("2026-11-21", 855), ("2026-11-22", 165),
                        ("2026-11-23", 165), ("2026-11-24", 165), ("2026-11-25", 190), ("2026-11-26", 210),
                        ("2026-11-27", 905), ("2026-11-28", 340), ("2026-11-29", 165), ("2026-11-30", ""),
                        ("2026-12-01", ""), ("2026-12-02", 1405), ("2026-12-03", 805), ("2026-12-04", 505),
                        ("2026-12-05", 505)]),
    windowB=dict(url=venetian_stay_url("2026-11-27", "2026-11-28"), label="stay window Nov 27-28 open",
                 cells=[("2026-11-16", 854), ("2026-11-17", 670), ("2026-11-18", 230), ("2026-11-19", 614),
                        ("2026-11-20", 1014), ("2026-11-21", 855), ("2026-11-22", 230), ("2026-11-23", 230),
                        ("2026-11-24", 230), ("2026-11-25", 270), ("2026-11-26", 302), ("2026-11-27", 1814),
                        ("2026-11-28", 510), ("2026-11-29", 230), ("2026-11-30", ""), ("2026-12-01", ""),
                        ("2026-12-02", 1405), ("2026-12-03", 805), ("2026-12-04", 774), ("2026-12-05", 774)]))

# The seven nights of the recommended trip, each with its own official booking deep link.
TRIP_NIGHTS = ["2026-11-23", "2026-11-24", "2026-11-25", "2026-11-26", "2026-11-27", "2026-11-28", "2026-11-29"]

HOTELS = [
    dict(
        id="venetian", name="The Venetian Resort (poker suite rate)", venue="Venetian poker room",
        property="The Venetian", rooms="Luxury King Suite, single or double occupancy",
        baseRate="", baseRateFloor=119, baseRateCeiling=209,
        baseRateNote=("The official poker-room rate page states: 'These rates will start as low as $119 and $209 and can be "
                      "higher.' The page does not map each starting figure to a specific property and no date-specific "
                      "quote is published."),
        resortFee=55, resortFeeNote="$55 resort fee per night stayed, plus tax, payable upon check-in.",
        taxRate=TAX_RATE,
        taxNote=("Printed in the official Hotel Terms and Conditions, 'Taxes, Surcharges, and Resort Fee' section: 'Daily "
                 "rates do not include the applicable Clark County Room Tax of 13.38%.' and 'The Venetian Resort has a "
                 "standard Las Vegas Resort Fee of $55 plus applicable tax per night, payable upon check-in.' The same "
                 "page still opens its Resort Fee section with 'Rates include a daily Resort Fee of $55 plus tax per "
                 "night', and the booking calendar footnote says its prices 'include daily resort fee, excludes taxes', "
                 "so the two official pages describe the fee differently and the site uses the fee-on-top reading (F51)."),
        parking="$20 per day for registered hotel guests (seven days a week); $20 Monday-Thursday and $25 Friday-Sunday for non-hotel guests; valet $40 per day.",
        parkingSource=VENETIAN_HOTEL_TERMS,
        cancellation=("A deposit for the stay including suite, fee and tax is billed on reservation confirmation. Blackout "
                      "dates apply. Prepaid offers are non-cancellable and non-refundable. Early checkout before the "
                      "scheduled departure date costs $100 plus tax."),
        cancellationSource=VENETIAN_HOTEL_TERMS,
        incidental="$150 per night credit card incidental deposit for suite charging privileges (non-Signature Suites).",
        checkInOut="Check-in 3:00 PM to 11:59 PM; check-out 11:00 AM.",
        qualification=("Poker-suite rates require six hours of active live cash play, or a buy-in to a $300 or higher "
                        "tournament, for each night stayed, completed before 2 a.m. on the last night. Book with code "
                        "EPOKR25 on 866.255.8936. Failure to qualify means the prevailing rate is charged."),
        source=VENETIAN_SUITE_RATES, feeSource=VENETIAN_RESORT_FEE, taxSource=VENETIAN_HOTEL_TERMS,
        quote=VENETIAN_QUOTE_TRIP,
        quotes=VENETIAN_QUOTES,
        bookingUrl=VENETIAN_CALENDAR_TRIP_URL,
        calendarUrl=VENETIAN_CALENDAR_TRIP_URL,
        calendarObservation=VENETIAN_CALENDAR_2026_11_17,
        noQuoteWindows=VENETIAN_NO_QUOTE_WINDOWS,
        bookingLinks=[dict(label=f"{d} (1 night)", url=venetian_stay_url(d, next_day(d))) for d in TRIP_NIGHTS]
        + [dict(label="whole trip, 7 nights", url=VENETIAN_CALENDAR_TRIP_URL)],
        bookingLinksNote=(
            "Each link opens the official booking engine with that night's dates and two adults already filled in. "
            "On 2026-11-17 the engine returned an itemised checkout total for the 23-30 November trip stay ($4,010.55; "
            "see the rate log) and for near-term stays. The one-night links open the engine for a single night; the "
            "dated rate log is the record of what the engine printed, and the links are not a price."),
        qualityNote=("Not scored. No official quality metric was published for the suites in the reviewed material, so the "
                     "quality ranking is left blank rather than inferred."),
        status=("Best-value candidate for a Venetian-based trip: poker room on property, published starting rate, published "
                "fee and tax, and the only property with a dated official checkout total."),
        walkNote="The poker room is inside the resort that owns this hotel; the Google Maps walking route from The Palazzo to The Venetian measures 4 minutes.",
    ),
    dict(
        id="palazzo", name="The Palazzo (poker suite rate)", venue="Venetian poker room",
        property="The Palazzo", rooms="Luxury King Suite, single or double occupancy",
        baseRate="", baseRateFloor=119, baseRateCeiling=209,
        baseRateNote=("The official poker-room rate page states poker-suite rates apply to guests 'staying in either The "
                      "Venetian or The Palazzo', starting 'as low as $119 and $209'. Which figure belongs to which "
                      "property is not stated."),
        resortFee=55, resortFeeNote="$55 resort fee per night stayed, plus tax, payable upon check-in.",
        taxRate=TAX_RATE,
        taxNote=("Printed in the official Hotel Terms and Conditions, 'Taxes, Surcharges, and Resort Fee' section: 'Daily "
                 "rates do not include the applicable Clark County Room Tax of 13.38%.' and 'The Venetian Resort has a "
                 "standard Las Vegas Resort Fee of $55 plus applicable tax per night, payable upon check-in.' The same "
                 "page still opens its Resort Fee section with 'Rates include a daily Resort Fee of $55 plus tax per "
                 "night', and the booking calendar footnote says its prices 'include daily resort fee, excludes taxes', "
                 "so the two official pages describe the fee differently and the site uses the fee-on-top reading (F51)."),
        parking="$20 per day for registered hotel guests; valet $40 per day.",
        parkingSource=VENETIAN_HOTEL_TERMS,
        cancellation=("Deposit billed on confirmation; blackout dates apply; prepaid offers non-refundable; early checkout "
                      "$100 plus tax."),
        cancellationSource=VENETIAN_HOTEL_TERMS,
        incidental="$150 per night credit card incidental deposit.",
        checkInOut="Check-in 3:00 PM to 11:59 PM; check-out 11:00 AM.",
        qualification="Same six-hours-or-$300-tournament qualification as The Venetian, booked on 866.255.8936 with code EPOKR25.",
        source=VENETIAN_SUITE_RATES, feeSource=VENETIAN_RESORT_FEE, taxSource=VENETIAN_HOTEL_TERMS,
        qualityNote="Not scored. No official quality metric was published for the suites in the reviewed material.",
        status="Same resort as the Venetian poker room; walking route to The Venetian measured at 4 minutes.",
        walkNote="Google Maps walking estimate 4 minutes (0.2 mile) to The Venetian, where the poker room is located.",
        bookingLinks=[dict(label=f"{d} (1 night)", url=venetian_stay_url(d, next_day(d))) for d in TRIP_NIGHTS]
        + [dict(label="whole trip, 7 nights", url=VENETIAN_CALENDAR_TRIP_URL)],
        bookingLinksNote=(
            "The Palazzo is booked through the same official engine as The Venetian, so the same dated links apply. "
            "No per-property date-parameterised link was verified for The Palazzo specifically, so the engine's suite "
            "type for these links is whatever it offers, not a Palazzo-only quote."),
    ),
    dict(
        id="wynn", name="Wynn Las Vegas", venue="Wynn poker room (located in Encore at Wynn Las Vegas)",
        property="Wynn Las Vegas", rooms="Wynn Resort King, Wynn Resort Two Queens, Panoramic View rooms, Tower Suites",
        baseRate="", baseRateFloor="", baseRateCeiling="",
        baseRateNote=("The official rooms page lists room categories and a booking link but publishes no room price. No "
                      "date-specific quote is published. The poker-room page links a 'Reserve your stay' contact for "
                      "poker players, which was not published as a price."),
        resortFee=55,
        resortFeeNote=("Reservations are charged a daily resort fee of $55 plus tax for each room night, on both standard "
                       "rooms and Tower Suites."),
        taxRate="",
        taxNote=("Wynn prints 'plus tax' without a percentage. The 13.38% Clark County room tax is the rate printed in the "
                 "Venetian hotel terms; applying it to Wynn's own total is an assumption and is labelled as one."),
        parking=("Confirmed on the official Parking page: 'Self-parking garages at Wynn and Encore ... complimentary "
                 "parking for all Wynn and Encore Resort and Tower Suite registered guests'; 'The daily parking fee for "
                 "non-registered guests is $25 per day with the first three (3) hours complimentary'; 'Complimentary "
                 "self-parking is extended to Wynn Poker Room guests'; 'Valet parking is $40 per day up to 24 hours (no "
                 "grace period, no re-entry)'."),
        parkingSource=WYNN_PARKING,
        cancellation=("A deposit of one night's room rate and tax is charged at booking. The live policy page does not "
                      "print a cancellation window; the 48-hour window appears only in offer terms, so no Wynn "
                      "cancellation deadline is marked verified for a flexible 2026 booking."),
        cancellationSource=WYNN_TERMS,
        incidental=("A credit card authorised to cover room, resort fees and tax plus $150 a night for incidentals is "
                    "required at check-in."),
        checkInOut="Check-in 3 p.m.; check-out 12 p.m. (official resort policies page).",
        qualification="",
        source=WYNN_ROOMS, feeSource=WYNN_TERMS, taxSource=WYNN_TERMS,
        sourceNote=("The fee, parking and check-in times are read from the live Resort Policies page. The page the earlier "
                    "build cited (terms-and-conditions/850070) is an expired 2025 DINING CREDIT offer whose own text "
                    "requires a stay completed by September 30, 2025, so it cannot substantiate a 2026 trip."),
        qualityNote=("The rooms page states 'With 22 Five-Star awards across our hotels, spas and restaurants, Wynn Resorts "
                     "holds more Five-Star designations than any independent hotel company in the world' and links Forbes "
                     "Travel Guide. That is a publisher claim, not a comparable room-level score, so no numeric score is used."),
        status="Strongest published fee transparency of the Strip properties reviewed, but no published room price.",
        walkNote="The poker room is in Encore at Wynn Las Vegas; Google Maps walking estimate 10 minutes (0.4 mile).",
    ),
    dict(
        id="bellagio", name="Bellagio", venue="Bellagio poker room (northside of casino, next to Sportsbook)",
        property="Bellagio", rooms="Premier King, Premier Two Queen, Spa Premier, Fountain View, Resort Tower King and suites",
        baseRate="", baseRateFloor="", baseRateCeiling="",
        baseRateNote=("The official hotel page publishes room classes, square footage and a 'Check Rates' booking link but "
                      "no room price. No date-specific quote is published."),
        resortFee=55, resortFeeNote="A daily resort fee of $55.00 plus applicable tax applies to all reservations.",
        taxRate="",
        taxNote=("'Lodging taxes apply to the basic room rate, any resort fee, additional per occupant charges, upgrades, as "
                 "well as any other charges as required by applicable law.' The percentage is not printed on the page; the "
                 "Clark County rate of 13.38% is published in the Venetian hotel terms."),
        parking="",
        parkingSource=BELLAGIO_TERMS,
        cancellation=("The first night's deposit is fully refundable if cancellation is received at least 72 hours prior to "
                      "arrival. Cancelling later, or failing to show, forfeits the first night. Complimentary stays incur a "
                      "$165 mid-week or $200 weekend cancellation fee."),
        cancellationSource=BELLAGIO_TERMS,
        incidental="$150 incidental amount per day authorised at check-in.",
        checkInOut="",
        qualification="",
        source=BELLAGIO_HOTEL, feeSource=BELLAGIO_TERMS, taxSource=BELLAGIO_TERMS,
        qualityNote="Not scored. No official, comparable quality metric was published in the reviewed material.",
        status="On-property poker room with published weekly tournaments; no published room price.",
        walkNote="Poker room is inside the property; Google Maps walking route to The Venetian measures 21 minutes.",
    ),
    dict(
        id="mgm", name="MGM Grand", venue="MGM Grand poker room", property="MGM Grand",
        rooms="", baseRate="", baseRateFloor="", baseRateCeiling="",
        baseRateNote="No room price is published on the official pages reviewed.",
        resortFee=50,
        resortFeeNote=("A daily resort fee of $50.00 plus applicable tax applies to all reservations; waived for eligible "
                       "MGM Rewards Gold+ members."),
        taxRate="",
        taxNote=("'Lodging taxes apply to the basic room rate, any resort fee...' The percentage is not printed; the "
                 "Clark County 13.38% rate is printed in the Venetian hotel terms."),
        parking="", parkingSource="",
        cancellation=("The first night's deposit is fully refundable with notice at least 72 hours before arrival; later "
                      "cancellations and no-shows forfeit the first night."),
        cancellationSource=MGM_TERMS,
        incidental="$100 incidental authorisation per day at check-in.", checkInOut="Check-in 3:00 pm; check-out 11:00 am.",
        qualification="",
        source=MGM_HOTEL, feeSource=MGM_TERMS, taxSource=MGM_TERMS,
        qualityNote="Not scored.",
        status="Fee terms verified; no published room price, and the walking route to the Venetian is outside the limit.",
        walkNote="Poker room is inside the property; Google Maps walking route to The Venetian measures 35 minutes.",
    ),
    dict(
        id="caesars", name="Caesars Palace", venue="Caesars Palace poker room (Appian Way)", property="Caesars Palace",
        rooms="Colosseum, Augustus, Octavius, Julius, Forum and Palace towers",
        baseRate="", baseRateFloor="", baseRateCeiling="",
        baseRateNote=("No room price is published for the reviewed dates. The official booking page printed 'Searching "
                      "Rates' for the November and December 2026 flexible-month calendars on 2026-11-17 and returned no "
                      "price cells, so there is no dated rate to log for this property."),
        resortFee=54.95,
        resortFeeNote=("The official booking page prints, under Hotel Policies > Fees: 'Resort fees: $62.30 ($54.95 "
                       "plus $7.35 tax)' and 'Resort fees are not assessed for Diamond and Seven Stars guests.' The fee "
                       "covers WiFi for two devices with a premium-speed upgrade, all local calls and daily fitness "
                       "centre access for two."),
        taxRate="", taxNote=("The property page does not print a room-tax percentage for the rate. It prints only the tax "
                            "amount charged on the resort fee ($7.35 on $54.95)."),
        parking="Self parking: surcharge applies. Valet parking: surcharge applies. Both are complimentary for Caesars Rewards members at Platinum tier or higher; Nevada locals get the first 3 hours of self parking at no charge. No dollar amount is published on the page.",
        parkingSource=CAESARS_CALENDAR,
        cancellation=("The official property page advertises 'FREE 48-Hour Cancellation*' under 'Why Book With Us'; the "
                      "terms behind the asterisk are not printed on that page. The booking page adds that rates shown "
                      "include applicable resort fees and that pricing and availability may vary with length of stay."),
        cancellationSource=CAESARS_BOOKING_HOMEPAGE,
        incidental="$100 per day deposit; a credit card is required at check-in for incidental charges; cash is not accepted for deposits or room charges.",
        checkInOut="Check-in starts at 4 PM; check-out is 11 AM; minimum check-in age is 21.",
        qualification="",
        source=CAESARS_HOTEL, feeSource=CAESARS_CALENDAR, taxSource=CAESARS_CALENDAR,
        taxReference=ROOM_TAX_REFERENCE_NOTE, taxReferenceSource=ROOM_TAX_REFERENCE,
        qualityNote=("Not scored. No official quality metric is published. Facts published by the property for 2026 "
                     "stays: 3,976 rooms, 11 restaurants, full-service spa, pool complex; 21+ check-in."),
        status=("Resort fee, deposit, parking policy and check-in/check-out are confirmed from the property's own "
                "booking page on 2026-11-17. The room rate and the room-tax percentage are still not published, so no "
                "true nightly cost can be computed from property-published components."),
        walkNote="Poker room is inside the property; Google Maps walking route to The Venetian measures 12 minutes.",
    ),
    dict(
        id="horseshoe", name="Horseshoe Las Vegas", venue="Horseshoe Hall of Fame poker room", property="Horseshoe Las Vegas",
        rooms="2,056 rooms", baseRate="", baseRateFloor="", baseRateCeiling="",
        baseRateNote=("No date-specific checkout total is published. The official booking calendar does publish a dated "
                      "lowest-available rate for every day of November and December 2026, and those cells are recorded in "
                      "the rate log — but the page states the cells 'include applicable resort fees' and are not a quote."),
        resortFee=49.95,
        resortFeeNote=("The official booking page prints, under Hotel Policies > Fees: 'Resort fees: $56.63 ($49.95 plus "
                       "$6.68 tax)' and 'Resort fees are not assessed for Diamond and Seven Stars guests.' The fee "
                       "covers WiFi for two devices with a premium-speed upgrade, all local calls and daily fitness "
                       "centre access for two. The rooms page states 'Wifi included in Resort Fee'."),
        taxRate="", taxNote=("The property page does not print a room-tax percentage for the rate. It prints only the tax "
                             "amount charged on the resort fee ($6.68 on $49.95)."),
        parking="Self parking: surcharge applies. Valet parking: surcharge applies. Both are complimentary for Caesars Rewards members at Platinum tier or higher; Nevada locals get the first 3 hours of self parking at no charge. No dollar amount is published on the page.",
        parkingSource=HORSESHOE_CALENDAR_NOV,
        cancellation=("The official property page advertises 'FREE 48-Hour Cancellation*' under 'Why Book With Us'; the "
                      "terms behind the asterisk are not printed on that page. The booking page adds: 'Rates shown "
                      "reflect the lowest available rate and include applicable resort fees.'"),
        cancellationSource=CAESARS_BOOKING_HOMEPAGE,
        incidental="$50 per day deposit; a credit card is required at check-in for incidental charges. Pet fee $75; rollaway bed $30 per day; $50 plus tax no-show fee on complimentary rooms.",
        checkInOut="Check-in starts at 4 PM; check-out is 11 AM; minimum check-in age is 21.",
        qualification="",
        source=HORSESHOE_HOTEL, feeSource=HORSESHOE_CALENDAR_NOV, taxSource=HORSESHOE_CALENDAR_NOV,
        taxReference=ROOM_TAX_REFERENCE_NOTE, taxReferenceSource=ROOM_TAX_REFERENCE,
        qualityNote=("Not scored. No official quality metric is published. Facts published by the property for 2026 "
                     "stays: 2,056 rooms, 10 restaurants, outdoor seasonal pool, 21+ check-in."),
        status=("The only reviewed property whose official calendar publishes a dated lowest-available rate per night "
                "for the trip window (see the rate log, 2026-11-17). Those cells already include the $49.95 resort fee, "
                "so the fee must not be added again; the room tax is not printed, so no true nightly cost is computed."),
        walkNote="Poker room is inside the property; Google Maps walking route to The Venetian measures 16 minutes.",
    ),
    dict(
        id="aria", name="ARIA Resort & Casino", venue="ARIA poker room", property="ARIA Resort & Casino",
        rooms="", baseRate="", baseRateFloor="", baseRateCeiling="",
        baseRateNote="No room price is published on the official pages reviewed.",
        resortFee=55,
        resortFeeNote=("A daily resort fee of $55.00 plus applicable tax applies to all reservations; waived for eligible "
                       "MGM Rewards Gold+ members."),
        taxRate="",
        taxNote=("Lodging taxes apply to the basic room rate and to any resort fee. The percentage is not printed; the "
                 "13.38% Clark County rate is printed in the Venetian hotel terms."),
        parking="", parkingSource="",
        cancellation=("The first night's deposit is fully refundable with notice at least 72 hours before arrival; later "
                      "cancellations and no-shows forfeit the first night."),
        cancellationSource=ARIA_TERMS,
        incidental=("$150 per day incidental authorisation for Deluxe Rooms, $250 Tower Suites, $350 Sky Suites, $500 "
                    "Villas."),
        checkInOut="Check-in 3:00 pm; check-out 11:00 am.", qualification="",
        source=ARIA_HOTEL, feeSource=ARIA_TERMS, taxSource=ARIA_TERMS,
        qualityNote="Not scored.",
        status="Fee terms verified; the walking route to the Venetian is outside the limit, and no dated poker schedule was confirmed.",
        walkNote="Google Maps walking route to The Venetian measures 31 minutes, which is outside the 30-minute limit.",
    ),
]

# Dated rate log. New observations are appended, never overwritten.
RATE_LOG = [
    # Recommended trip window, read from the official booking engine (session fe903bcb, 2026-11-17 UTC).
    # The engine printed a best-available "Newly Remodeled Luxury King" quote for 7 nights, 2 adults.
    # Every money figure below is printed on the page; the per-night true cost is derived (see note).
    dict(hotel="venetian", observedOn="2026-11-17", baseRate="",
         publishedStartingRates="164.25 (Nov 23), 164.25 (Nov 24), 201.75 (Nov 25), 231.75 (Nov 26), "
                                "1,649.25 (Nov 27), 554.25 (Nov 28), 186.75 (Nov 29) per night, rate before resort fee",
         resortFee="55.00 per night",
         tax="473.30 printed (7 nights)",
         # Derived = (printed rate + printed $55 resort fee) x 1.1338, one value per night.
         trueNightlyLow="248.59", trueNightlyHigh="1932.28",
         # Printed per-night room rates (23-29 Nov) and the derived all-in night costs, in stay order.
         nightlyRates=[164.25, 164.25, 201.75, 231.75, 1649.25, 554.25, 186.75],
         nightlyTrueCost=[248.59, 248.59, 291.10, 325.12, 1932.28, 690.77, 274.10],
         quoteType=("Dated official checkout total (2 adults, 7 nights, 23-30 Nov 2026, best available "
                    "Luxury King suite) - read 2026-11-17"),
         note=("Printed on the page: the engine's 'Estimated cost of stay' of $4,010.55 (average rate $505.32 per "
               "night, all-in before tax). Its breakdown lists the seven nightly rates above, a $55.00 resort fee on "
               "each night ($385.00 total) and taxes of $473.30. Seven derived per-night true costs add to $4,010.55 "
               "exactly. Tax check: 13.38% of the printed pre-tax subtotal of $3,537.25 is $473.28, so the printed "
               "$473.30 differs by $0.02; the page gives no reason, and the figure is recorded as printed "
               "(flagged). The 27 Nov night ($1,649.25) is the engine's own price for that night and is not a "
               "reference rate. This is a non-poker-suite, best-available quote; the $119/$209 poker suite rate "
               "needs the poker-play conditions on the official rate page and is not applied here. Reads on the same "
               "day for other windows differed (see the rows below), so this quote is one dated observation."),
         source="https://www.venetianlasvegas.com/booking?adults[]=2&arrival_date=2026-11-23&children[]=0&departure_date=2026-11-30&view=calendar",
         feeSource=VENETIAN_RESORT_FEE, taxSource=VENETIAN_HOTEL_TERMS),
    dict(hotel="venetian", observedOn="2026-11-17", baseRate="",
         publishedStartingRates="621.75 (Nov 17) and 164.25 (Nov 18) per night",
         resortFee="55.00 per night", tax="119.89 printed",
         # Low/high are the two NIGHTS in this dated quote, not a price range:
         # 18 Nov came to $248.59 all-in and 17 Nov to $767.30.
         trueNightlyLow="248.59", trueNightlyHigh="767.30",
         quoteType="Dated official checkout total (2 adults, 2 nights) - re-read",
         note=("The same booking engine, the same stay and the same two adults printed a lower price one day after the "
               "previous observation: Nov 17 fell from $824.25 to $621.75 while Nov 18 stayed at $164.25, taking the "
               "checkout total from $1,245.48 to $1,015.89. Derived nightly figures are (rate + $55) x 1.1338 and add "
               "to $1,015.89, matching the printed total. This is why the site keeps a log instead of one number."),
         source=VENETIAN_QUOTE_URL, feeSource=VENETIAN_RESORT_FEE, taxSource=VENETIAN_HOTEL_TERMS),
    dict(hotel="venetian", observedOn="2026-11-17", baseRate="",
         publishedStartingRates="899.25 (Nov 20) and 1,199.25 (Nov 21) per night",
         resortFee="55.00 per night", tax="295.50 printed",
         trueNightlyLow="1081.93", trueNightlyHigh="1422.07",
         quoteType="Dated official checkout total (2 adults, 2 nights, second window)",
         note=("A second stay window quoted by the same engine on the same day, for a 750 sq ft Newly Remodeled Luxury "
               "Two Queen suite rather than the 650 sq ft King. Derived nightly figures are (rate + $55) x 1.1338 and "
               "add to $2,504.00, matching the printed total exactly. The engine chooses the suite, so this is not "
               "comparable with the King quote on price - only on arithmetic."),
         source=venetian_stay_url("2026-11-20", "2026-11-22"),
         feeSource=VENETIAN_RESORT_FEE, taxSource=VENETIAN_HOTEL_TERMS),
    dict(hotel="venetian", observedOn="2026-11-17", baseRate="",
         publishedStartingRates="",
         resortFee="55.00 per night", tax="13.38%",
         trueNightlyLow="", trueNightlyHigh="",
         quoteType="No quote returned for the superseded 25 Nov - 2 Dec window",
         note=("The engine was opened four times on 2026-11-17 for stays in the superseded 25 Nov - 2 Dec window "
               "(the trip was later moved to 23-30 Nov, which the engine prices in full; see the 23-30 Nov entry): "
               "Nov 25 to Dec 2 (7 nights) returned every calendar cell as the placeholder '$XXX' and no suite; "
               "Nov 25 to Nov 27 did not finish loading; Nov 27 to Nov 28 rendered the calendar but no suite; and "
               "Nov 30 to Dec 1 rendered every cell as '$XXX' and no suite. No rate, no tax and no total is published "
               "for that window only; the 23-30 Nov window was re-read later and is priced."),
         source=VENETIAN_OLD_WINDOW_BOOKING, feeSource=VENETIAN_RESORT_FEE, taxSource=VENETIAN_HOTEL_TERMS),
    dict(hotel="venetian", observedOn="2026-11-17", baseRate="",
         publishedStartingRates=("calendar cells with the Nov 17-19 window open: "
                                 + ", ".join(f"{d[5:]} ${v}" if v != "" else f"{d[5:]} no price"
                                             for d, v in VENETIAN_CALENDAR_2026_11_17["windowA"]["cells"])),
         resortFee="included in the calendar cell", tax="excluded from the calendar cell",
         trueNightlyLow="", trueNightlyHigh="",
         quoteType="Booking calendar cells (context-dependent, not a price)",
         note=("The calendar's own footnote reads: 'Pricing shown is best available suite and rate, includes daily "
               "resort fee, excludes taxes.' The value printed for a date changes with the stay window that is open: "
               "read on the same day, Nov 16 showed $555 with the Nov 17-19 window open and $854 with the Nov 27-28 "
               "window open, Nov 22 showed $165 against $230, and Nov 27 showed $905 against $1,814. Because the cells "
               "move with the query, no calendar cell on this site is used as a nightly rate (F31)."),
         source=VENETIAN_CALENDAR_2026_11_17["windowA"]["url"],
         feeSource=VENETIAN_RESORT_FEE, taxSource=VENETIAN_HOTEL_TERMS),
    dict(hotel="venetian", observedOn="2026-11-17", baseRate="",
         publishedStartingRates=("calendar cells with the Nov 27-28 window open: "
                                 + ", ".join(f"{d[5:]} ${v}" if v != "" else f"{d[5:]} no price"
                                             for d, v in VENETIAN_CALENDAR_2026_11_17["windowB"]["cells"])),
         resortFee="included in the calendar cell", tax="excluded from the calendar cell",
         trueNightlyLow="", trueNightlyHigh="",
         quoteType="Booking calendar cells (context-dependent, not a price) - second window",
         note=("Second reading of the same official calendar on 2026-11-17, kept beside the first reading so the two "
               "can be compared cell by cell. Nov 30 and Dec 1 printed no price in either reading."),
         source=VENETIAN_CALENDAR_2026_11_17["windowB"]["url"],
         feeSource=VENETIAN_RESORT_FEE, taxSource=VENETIAN_HOTEL_TERMS),
    dict(hotel="venetian", observedOn="2026-11-16", baseRate="",
         publishedStartingRates="824.25 and 164.25 per night for Nov. 17-19, 2026",
         resortFee="55.00 per night", tax="146.98 printed",
         # Low/high are the two observed NIGHTS in this one dated quote, not a
         # price range: 17 Nov came to $996.89 all-in and 18 Nov to $248.59.
         trueNightlyLow="248.59", trueNightlyHigh="996.89",
         quoteType="Dated official checkout total (2 adults, 2 nights)",
         note=("The official booking engine printed $824.25 + $55 and $164.25 + $55, taxes $146.98 and a total of "
               "$1,245.48 for a 650 sq ft Newly Remodeled Luxury King suite. Derived nightly figures are "
               "(rate + $55) x 1.1338 and add to $1,245.48, the printed total exactly."),
         source=VENETIAN_QUOTE_URL, feeSource=VENETIAN_RESORT_FEE, taxSource=VENETIAN_HOTEL_TERMS),
    dict(hotel="venetian", observedOn="2026-11-16", baseRate="", publishedStartingRates="119 and 209",
         resortFee="55 plus tax", tax="13.38%", trueNightlyLow="197.28", trueNightlyHigh="299.32",
         quoteType="Published starting rate (not date-specific, not mapped to a property)",
         note="Floor figures are arithmetic on published numbers: (rate + 55) x 1.1338. Not a quote.",
         source=VENETIAN_SUITE_RATES, feeSource=VENETIAN_RESORT_FEE, taxSource=VENETIAN_HOTEL_TERMS),
    dict(hotel="palazzo", observedOn="2026-11-16", baseRate="", publishedStartingRates="119 and 209",
         resortFee="55 plus tax", tax="13.38%", trueNightlyLow="197.28", trueNightlyHigh="299.32",
         quoteType="Published starting rate (not date-specific, not mapped to a property)",
         note="Same published poker-suite rate page covers The Venetian and The Palazzo.",
         source=VENETIAN_SUITE_RATES, feeSource=VENETIAN_RESORT_FEE, taxSource=VENETIAN_HOTEL_TERMS),
    dict(hotel="wynn", observedOn="2026-11-16", baseRate="", publishedStartingRates="",
         resortFee="55 plus tax", tax="", trueNightlyLow="", trueNightlyHigh="",
         quoteType="No published rate", note="Room categories published without prices.",
         source=WYNN_ROOMS, feeSource=WYNN_TERMS, taxSource=WYNN_TERMS),
    dict(hotel="bellagio", observedOn="2026-11-16", baseRate="", publishedStartingRates="",
         resortFee="55 plus tax", tax="", trueNightlyLow="", trueNightlyHigh="",
         quoteType="No published rate", note="Room classes published without prices.",
         source=BELLAGIO_HOTEL, feeSource=BELLAGIO_TERMS, taxSource=BELLAGIO_TERMS),
    dict(hotel="mgm", observedOn="2026-11-17", baseRate="",
         publishedStartingRates="No room price published on the official hotel page",
         resortFee="50.00 per night plus applicable tax",
         quoteType="Fee verified, no published room rate",
         note=("Resort fee read from the MGM Grand official hotel reservation terms: 'A daily resort fee of $50.00 plus "
               "applicable tax will be applied to all reservations.' Room rate still blank: no official date-specific "
               "price was published."),
         source=MGM_HOTEL, feeSource=MGM_TERMS, taxSource=MGM_TERMS),
    dict(hotel="aria", observedOn="2026-11-17", baseRate="",
         publishedStartingRates="No room price published on the official hotel page",
         resortFee="55.00 per night plus applicable tax",
         quoteType="Fee verified, no published room rate",
         note=("Resort fee read from the ARIA official hotel reservation terms: 'A daily resort fee of $55.00 plus "
               "applicable tax will be applied to all reservations.' Room rate still blank."),
         source=ARIA_HOTEL, feeSource=ARIA_TERMS, taxSource=ARIA_TERMS),
    dict(hotel="wynn", observedOn="2026-11-17", baseRate="",
         publishedStartingRates="No room price published on the official rooms page",
         resortFee="55.00 per night plus tax (re-confirmed on the live Resort Policies page)",
         quoteType="Fee re-confirmed, no published room rate",
         note=("Re-read on 2026-11-17 on the live Resort Policies page. The 2025 DINING CREDIT terms page cited by the "
               "earlier build (850070) is an expired offer and is no longer used as the fee source."),
         source=WYNN_ROOMS, feeSource=WYNN_TERMS, taxSource=WYNN_TERMS),
    dict(hotel="mgm", observedOn="2026-11-16", baseRate="", publishedStartingRates="",
         resortFee="", tax="", trueNightlyLow="", trueNightlyHigh="",
         quoteType="Not verified in this pass", note="Hotel fee and tax terms still to be captured.",
         source=MGM_HOTEL, feeSource="", taxSource=""),
    dict(hotel="caesars", observedOn="2026-11-16", baseRate="", publishedStartingRates="",
         resortFee="", tax="", trueNightlyLow="", trueNightlyHigh="",
         quoteType="Not verified in this pass", note="Hotel fee and tax terms still to be captured.",
         source=CAESARS_HOTEL, feeSource="", taxSource=""),
    dict(hotel="horseshoe", observedOn="2026-11-16", baseRate="", publishedStartingRates="",
         resortFee="", tax="", trueNightlyLow="", trueNightlyHigh="",
         quoteType="Not verified in this pass", note="Hotel fee and tax terms still to be captured.",
         source=HORSESHOE_HOTEL, feeSource="", taxSource=""),
    dict(hotel="aria", observedOn="2026-11-16", baseRate="", publishedStartingRates="",
         resortFee="", tax="", trueNightlyLow="", trueNightlyHigh="",
         quoteType="Not verified in this pass", note="Hotel fee and tax terms still to be captured.",
         source=ARIA_HOTEL, feeSource="", taxSource=""),
    dict(hotel="venetian", observedOn="2026-11-17", baseRate="", publishedStartingRates="",
         resortFee="55.00 per night plus tax (resort-fee page re-read 2026-11-17)",
         tax="13.38% Clark County room tax (hotel terms not re-read on 2026-11-17)",
         trueNightlyLow="", trueNightlyHigh="",
         quoteType="Booking-engine calendar, no price captured",
         note=("Static read of the booking page for Nov 25 to Dec 2, 2026 (2 adults): every calendar cell showed $XXX. "
               "No nightly rate is recorded for these dates. The page says its prices include the daily resort fee and "
               "exclude taxes."),
         source=VENETIAN_FIXED_STAY_BOOKING, feeSource=VENETIAN_RESORT_FEE, taxSource=VENETIAN_HOTEL_TERMS),
    # --- Caesars Entertainment properties, read from their own booking page 2026-11-17 ---
    dict(hotel="horseshoe", observedOn="2026-11-17", baseRate="",
         publishedStartingRates="calendar cells for Nov. 16-30: " + _cells(HORSESHOE_CALENDAR_NOV_CELLS),
         resortFee="49.95 plus 6.68 tax ($56.63 tax inclusive), already inside the calendar cell",
         tax="not printed for the room rate",
         trueNightlyLow="", trueNightlyHigh="",
         quoteType="Official booking-calendar cells (lowest available, resort-fee inclusive; not a quote)",
         note=("Read at 01:31 UTC on the property's own booking page. The page states: 'Rates shown reflect the lowest "
               "available rate and include applicable resort fees.' The recommended trip nights (Nov 25 to Dec 1) sum to "
               "$1,527.00 for a room, fee included, tax excluded: 55 + 55 + 181 + 115 + 272 + 470 + 379. No checkout "
               "total is published for a dated stay."),
         source=HORSESHOE_CALENDAR_NOV, feeSource=HORSESHOE_CALENDAR_NOV, taxSource=HORSESHOE_CALENDAR_NOV),
    dict(hotel="horseshoe", observedOn="2026-11-17", baseRate="",
         publishedStartingRates="calendar cells for Dec. 1-31: " + _cells(HORSESHOE_CALENDAR_DEC_CELLS),
         resortFee="49.95 plus 6.68 tax, already inside the calendar cell",
         tax="not printed for the room rate",
         trueNightlyLow="", trueNightlyHigh="",
         quoteType="Official booking-calendar cells (second reading of the same page, 01:31 UTC)",
         note=("The same December page had printed a different grid five minutes earlier at 01:26 UTC: Dec 1 $449, "
               "Dec 4 $219, Dec 5 $369, Dec 6 $249, Dec 7 $229, Dec 8 $169, Dec 9 $149, Dec 10 $359, Dec 11 $479, "
               "Dec 12 $429, Dec 13 $56, Dec 18 $63, Dec 19 $219, Dec 25 $129, Dec 27 $149, Dec 30 $209, Dec 31 $529. "
               "Both readings are kept. A calendar cell is not a price held for a guest, and this repository does not "
               "choose between them."),
         source=HORSESHOE_CALENDAR_DEC, feeSource=HORSESHOE_CALENDAR_DEC, taxSource=HORSESHOE_CALENDAR_DEC),
    dict(hotel="caesars", observedOn="2026-11-17", baseRate="",
         publishedStartingRates="",
         resortFee="54.95 plus 7.35 tax, printed as $62.30 tax inclusive",
         tax="not printed for the room rate",
         trueNightlyLow="", trueNightlyHigh="",
         quoteType="No rate published; calendar returned no price cells",
         note=("The November and December 2026 flexible-month calendars for Caesars Palace were opened twice on "
               "2026-11-17 and both times showed 'Searching Rates' with a reservation-system error and no price cells. "
               "The fee block on the same page did print, and is recorded on the hotel row."),
         source=CAESARS_CALENDAR, feeSource=CAESARS_CALENDAR, taxSource=CAESARS_CALENDAR),
    dict(hotel="venetian", observedOn="2026-11-17", baseRate="",
         publishedStartingRates="",
         resortFee="55.00 per night (resort-fee page re-read 2026-11-17, session 688eb797)",
         tax="13.38% Clark County room tax (hotel terms re-read 2026-11-17, session 688eb797)",
         trueNightlyLow="", trueNightlyHigh="",
         quoteType="Booking-engine calendar, stay unavailable (fifth independent read)",
         note=("Read with the 25 November - 2 December 2026 window open (2 adults) on 2026-11-17 ~01:40 UTC by session "
               "688eb797. The calendar rendered 25, 26, 27, 28, 29 and 30 November and 1 December as 'Date Unavailable' "
               "with no price cell at all, and '$XXX' placeholders from 2 December onward. This is the strongest form "
               "of the no-availability finding (F57) and the reason the recommended trip is 23 - 30 November. The "
               "footnote was re-confirmed verbatim: 'Pricing shown is best available suite and rate, includes daily "
               "resort fee, excludes taxes.' No rate was inferred from any cell."),
         source=VENETIAN_QUOTE_URL, feeSource=VENETIAN_RESORT_FEE, taxSource=VENETIAN_HOTEL_TERMS),
]

MAPS = "https://www.google.com/maps/dir/?api=1&travelmode=walking&origin={o}&destination={d}"

ROUTES = [
    dict(hotel="venetian", venue="venetian", minutes=0, miles="",
         note="Poker room is inside the hotel's own resort; indoor walk, no street crossing.",
         via="", source="https://www.venetianlasvegas.com/resort/casino/poker.html",
         mapsOrigin="The+Venetian+Resort,+Las+Vegas,+NV", mapsDestination="The+Venetian+Resort,+Las+Vegas,+NV"),
    dict(hotel="palazzo", venue="venetian", minutes=4, miles="0.2",
         note="Maps walking estimate between the two connected resort properties.",
         via="unnamed resort paths", source="https://www.venetianlasvegas.com/resort/casino/poker/suite-rates.html",
         mapsOrigin="The+Palazzo+Las+Vegas,+Las+Vegas,+NV", mapsDestination="The+Venetian+Resort,+Las+Vegas,+NV"),
    dict(hotel="wynn", venue="wynn", minutes=10, miles="0.4",
         note="The official Wynn poker page states the poker room is 'located in Encore at Wynn Las Vegas'.",
         via="Las Vegas Blvd S", source="https://www.wynnlasvegas.com/casino/poker",
         mapsOrigin="Wynn+Las+Vegas,+3131+Las+Vegas+Blvd+S,+Las+Vegas,+NV+89109",
         mapsDestination="Encore+Las+Vegas,+3131+Las+Vegas+Blvd+S,+Las+Vegas,+NV+89109"),
    dict(hotel="bellagio", venue="bellagio", minutes=0, miles="",
         note="Poker room is inside the hotel (northside of casino, next to Sportsbook).",
         via="", source="https://bellagio.mgmresorts.com/en/casino/poker.html",
         mapsOrigin="Bellagio+Hotel+%26+Casino,+Las+Vegas,+NV", mapsDestination="Bellagio+Hotel+%26+Casino,+Las+Vegas,+NV"),
    dict(hotel="mgm", venue="mgm", minutes=0, miles="",
         note="Poker room is inside the hotel.",
         via="", source="https://mgmgrand.mgmresorts.com/en/casino/poker-tables.html",
         mapsOrigin="MGM+Grand+Hotel+%26+Casino,+Las+Vegas,+NV", mapsDestination="MGM+Grand+Hotel+%26+Casino,+Las+Vegas,+NV"),
    dict(hotel="caesars", venue="caesars", minutes=0, miles="",
         note="Poker room is inside the hotel, along the Appian Way promenade.",
         via="", source="https://www.caesars.com/las-vegas/explore/casino/poker-tournaments-las-vegas-strip",
         mapsOrigin="Caesars+Palace+Las+Vegas,+3570+Las+Vegas+Blvd+S,+Las+Vegas,+NV",
         mapsDestination="Caesars+Palace+Las+Vegas,+3570+Las+Vegas+Blvd+S,+Las+Vegas,+NV"),
    dict(hotel="horseshoe", venue="horseshoe", minutes=0, miles="",
         note="Poker room is inside the hotel, in a quieter section of the casino.",
         via="", source="https://www.caesars.com/las-vegas/explore/casino/poker-tournaments-las-vegas-strip",
         mapsOrigin="Horseshoe+Las+Vegas+Hotel+%26+Casino,+3645+W+Flamingo+Rd,+Las+Vegas,+NV+89169",
         mapsDestination="Horseshoe+Las+Vegas+Hotel+%26+Casino,+3645+W+Flamingo+Rd,+Las+Vegas,+NV+89169"),
    dict(hotel="aria", venue="aria", minutes=0, miles="",
         note="Poker room is inside the hotel.",
         via="", source="https://aria.mgmresorts.com/en/casino/poker.html",
         mapsOrigin="ARIA+Resort+%26+Casino,+Las+Vegas,+NV", mapsDestination="ARIA+Resort+%26+Casino,+Las+Vegas,+NV"),
    # cross-property routes to the Venetian poker room (the main venue)
    dict(hotel="caesars", venue="venetian", minutes=12, miles="0.5",
         note="Maps walking estimate, Las Vegas Blvd S.", via="Las Vegas Blvd S",
         source="https://www.caesars.com/las-vegas/explore/casino/poker-tournaments-las-vegas-strip",
         mapsOrigin="Caesars+Palace+Las+Vegas,+3570+Las+Vegas+Blvd+S,+Las+Vegas,+NV",
         mapsDestination="The+Venetian+Resort,+Las+Vegas,+NV"),
    dict(hotel="wynn", venue="venetian", minutes=13, miles="0.6", lastReadOn="2026-11-17",
         note="Maps walking estimate, re-read 2026-11-17 (13 min, 0.6 mile); a 14-minute alternative via Las Vegas Blvd S is also shown.",
         via="Wynn Main Gate Dr", source="https://www.wynnlasvegas.com/casino/poker",
         mapsOrigin="Wynn+Las+Vegas,+3131+Las+Vegas+Blvd+S,+Las+Vegas,+NV+89109",
         mapsDestination="The+Venetian+Resort,+Las+Vegas,+NV"),
    dict(hotel="horseshoe", venue="venetian", minutes=16, miles="0.7",
         note="Maps walking estimate; a 17-minute alternative via Las Vegas Blvd S is also shown.",
         via="Linq Ln", source="https://www.caesars.com/las-vegas/explore/casino/poker-tournaments-las-vegas-strip",
         mapsOrigin="Horseshoe+Las+Vegas+Hotel+%26+Casino,+3645+W+Flamingo+Rd,+Las+Vegas,+NV+89169",
         mapsDestination="The+Venetian+Resort,+Las+Vegas,+NV"),
    dict(hotel="bellagio", venue="venetian", minutes=21, miles="0.9", lastReadOn="2026-11-17",
         note="Maps walking estimate, re-read 2026-11-17 (21 min, 0.9 mile); a 24-minute alternative is also shown.", via="Las Vegas Blvd S",
         source="https://bellagio.mgmresorts.com/en/casino/poker.html",
         mapsOrigin="Bellagio+Hotel+%26+Casino,+Las+Vegas,+NV", mapsDestination="The+Venetian+Resort,+Las+Vegas,+NV"),
    dict(hotel="mgm", venue="venetian", minutes=35, miles="1.6",
         note="Maps walking estimate; outside the 30-minute limit for a day of tournament hopping.",
         via="Las Vegas Blvd S", source="https://mgmgrand.mgmresorts.com/en/casino/poker-tables.html",
         mapsOrigin="MGM+Grand+Hotel+%26+Casino,+Las+Vegas,+NV", mapsDestination="The+Venetian+Resort,+Las+Vegas,+NV"),
    dict(hotel="aria", venue="venetian", minutes=31, miles="1.4",
         note="Maps walking estimate; outside the 30-minute limit.", via="Las Vegas Blvd S",
         source="https://aria.mgmresorts.com/en/casino/poker.html",
         mapsOrigin="ARIA+Resort+%26+Casino,+Las+Vegas,+NV", mapsDestination="The+Venetian+Resort,+Las+Vegas,+NV"),
    # Venetian hotel -> Bellagio Poker Room, the reverse direction is not in the day plan (see F67).
    dict(hotel="venetian", venue="bellagio", minutes=27, miles="1.1", lastReadOn="2026-11-17",
         note=("Google Maps walking card, read 2026-11-17 (single read): 27 min, 1.1 miles via Las Vegas Blvd S. The driving "
               "card for the same pair read 8 min. The walking card does not print its mode label; the link requested "
               "travelmode=walking. Not re-read on a second day."),
         via="Las Vegas Blvd S", source="https://bellagio.mgmresorts.com/en/casino/poker.html",
         mapsOrigin="3355+S+Las+Vegas+Blvd,+Las+Vegas,+NV+89109",
         mapsDestination="Bellagio+Poker+Room,+3600+S+Las+Vegas+Blvd,+Las+Vegas,+NV+89109"),
]
