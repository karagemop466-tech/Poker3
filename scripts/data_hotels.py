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
VENETIAN_HOTEL_TERMS = "https://www.venetianlasvegas.com/legal/hotel-terms-and-conditions.html"
WYNN_ROOMS = "https://www.wynnlasvegas.com/rooms-and-suites"
WYNN_TERMS = "https://www.wynnlasvegas.com/terms-and-conditions/850070"
BELLAGIO_HOTEL = "https://bellagio.mgmresorts.com/en/hotel.html"
BELLAGIO_TERMS = "https://bellagio.mgmresorts.com/en/terms-and-conditions.html"
MGM_HOTEL = "https://mgmgrand.mgmresorts.com/en/hotel.html"
CAESARS_HOTEL = "https://www.caesars.com/caesars-palace/hotels"
HORSESHOE_HOTEL = "https://www.caesars.com/horseshoe-las-vegas/hotels"
ARIA_HOTEL = "https://aria.mgmresorts.com/en/hotel.html"
# Hotel Reservation Terms and Conditions pages, reached via the MGM Resorts
# corporate terms index (https://www.mgmresorts.com/en/terms-and-conditions.html)
# and cited by the MGM Grand FAQ for the resort-fee question.
MGM_TERMS = "https://mgmgrand.mgmresorts.com/en/terms-and-conditions.html"
ARIA_TERMS = "https://aria.mgmresorts.com/en/terms-and-conditions.html"

TAX_RATE = 13.38  # Clark County room tax, printed in the Venetian hotel terms

# The official booking engine, opened with the dates and party size in the URL.
VENETIAN_QUOTE_URL = ("https://www.venetianlasvegas.com/booking?adults[]=2&arrival_date=2026-11-17"
                      "&children[]=0&departure_date=2026-11-19&view=calendar")
VENETIAN_CALENDAR_NOV_URL = ("https://www.venetianlasvegas.com/booking?adults[]=2&arrival_date=2026-11-17"
                             "&children[]=0&departure_date=2026-11-19&view=calendar")
VENETIAN_CALENDAR_TRIP_URL = ("https://www.venetianlasvegas.com/booking?adults[]=2&arrival_date=2026-11-25"
                              "&children[]=0&departure_date=2026-12-03&view=calendar")

# The one dated official checkout total found on 2026-11-16, read straight off the
# official booking engine.  Every line is printed on the page.
VENETIAN_QUOTE = dict(
    property="The Venetian Resort - venetian Newly Remodeled Luxury King suite",
    checkIn="2026-11-17", checkOut="2026-11-19", guests=2, nights=2,
    offer="Book Direct: Up to 25% Off",
    suiteDetail="Approximately 650 square feet, king bed, living room, Roman tub",
    nightOne=dict(date="2026-11-17", rate=824.25, resortFee=55.00),
    nightTwo=dict(date="2026-11-18", rate=164.25, resortFee=55.00),
    taxes=146.98, total=1245.48, averageRate=549.25,
    # (rate + $55 resort fee) x 1.1338, rounded to cents per night, as printed.
    # $996.89 + $248.59 = $1,245.48, which is the venue's printed total exactly.
    # An earlier version used 996.91 / 248.61 and a note excusing a 4-cent gap;
    # that gap was arithmetic error in this repository, not the venue's rounding.
    derivedNightly=[996.89, 248.59], derivedTotal=1245.48,
    note=("The two derived nightly figures, (rate + $55 resort fee) x 1.1338 rounded to cents, add to $1,245.48, "
          "the printed total exactly."),
    source=VENETIAN_QUOTE_URL, observedOn="2026-11-16")

# Calendar cells published by the same booking engine for November 2026.  The page
# states: "Pricing shown is best available suite and rate, includes daily resort fee,
# excludes taxes."  They are observations, not quotes.
VENETIAN_CALENDAR_NOV = [
    ("2026-11-17", 855), ("2026-11-18", ""), ("2026-11-19", ""), ("2026-11-20", 488),
    ("2026-11-21", 1055), ("2026-11-22", 1055), ("2026-11-23", 165), ("2026-11-24", 165),
    ("2026-11-25", 185), ("2026-11-26", 190), ("2026-11-27", 210), ("2026-11-28", 905),
    ("2026-11-29", 340), ("2026-11-30", 165),
]

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
        taxNote="Clark County Room Tax of 13.38% applies to the daily rate; the resort fee is 'plus applicable tax'.",
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
        quote=VENETIAN_QUOTE,
        bookingUrl=VENETIAN_QUOTE_URL,
        calendarUrl=VENETIAN_CALENDAR_TRIP_URL,
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
        taxNote="Clark County Room Tax of 13.38% applies to the daily rate; the resort fee is 'plus applicable tax'.",
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
    ),
    dict(
        id="wynn", name="Wynn Las Vegas", venue="Wynn poker room (located in Encore at Wynn Las Vegas)",
        property="Wynn Las Vegas", rooms="Wynn Resort King, Wynn Resort Two Queens, Panoramic View rooms, Tower Suites",
        baseRate="", baseRateFloor="", baseRateCeiling="",
        baseRateNote=("The official rooms page lists room categories and a booking link but publishes no room price. No "
                      "date-specific quote is published. The poker-room page links a 'Reserve your stay' contact for "
                      "poker players, which was not published as a price."),
        resortFee=55, resortFeeNote="A daily resort fee of $55 plus tax is added to the room account for each room night.",
        taxRate="", taxNote=("The reviewed Wynn terms publish 'plus tax' without a percentage; the Clark County room tax "
                             "rate of 13.38% is published in the Venetian hotel terms."),
        parking=("Self parking is complimentary for registered guests. Non-registered guests pay $25 per day with the first "
                 "three hours free; valet $40 per day. Complimentary self-parking is extended to Wynn Poker Room guests."),
        parkingSource=WYNN_TERMS,
        cancellation=("Cancellations must be received at least 48 hours prior to the arrival date or the deposit is "
                      "forfeited; early departures are charged the room rate and tax for the night."),
        cancellationSource=WYNN_TERMS,
        incidental="A credit card authorisation for room, resort fees and tax plus $150 a night for incidentals is required at check-in.",
        checkInOut="",
        qualification="",
        source=WYNN_ROOMS, feeSource=WYNN_TERMS, taxSource=WYNN_TERMS,
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
        resortFee=50, resortFeeNote=("The MGM Grand Hotel Reservation Terms and Conditions state: 'A daily resort fee of "
                                     "$50.00 plus applicable tax will be applied to all reservations.' The fee is waived for "
                                     "eligible MGM Rewards Gold+ members."),
        taxRate="", taxNote=("The same terms state that 'Lodging taxes apply to the basic room rate, any resort fee, additional "
                             "per occupant charges, upgrades, as well as any other charges as required by applicable law.' The "
                             "percentage itself is not published on the reviewed pages, so no true nightly total is computed."),
        parking="", parkingSource="",
        cancellation=("The first night's deposit is fully refundable with timely notice to Room Reservations (877.880.0880) at "
                      "least 72 hours prior to arrival; later cancellations and no-shows forfeit the first night's deposit."),
        cancellationSource=MGM_TERMS,
        incidental="A $100 per day incidental authorization is placed at check-in for room-charging privileges.",
        checkInOut="Check-in 3:00 PM; check-out 11:00 AM.",
        qualification="",
        source=MGM_HOTEL, feeSource=MGM_TERMS, taxSource=MGM_TERMS,
        verifiedOn="2026-11-17",
        qualityNote="Not scored.",
        status=("Fee, cancellation and incidental terms verified on the official MGM Grand terms page on 2026-11-17. Room rate "
                "and tax percentage are still unpublished, so the true nightly cost stays blank."),
        walkNote="Poker room is inside the property; Google Maps walking route to The Venetian measures 35 minutes.",
    ),
    dict(
        id="caesars", name="Caesars Palace", venue="Caesars Palace poker room (Appian Way)", property="Caesars Palace",
        rooms="", baseRate="", baseRateFloor="", baseRateCeiling="",
        baseRateNote="No room price is published on the official pages reviewed.",
        resortFee="", resortFeeNote="Not verified: the Caesars Palace hotel fee and tax terms were not captured in this pass.",
        taxRate="", taxNote="Not verified in this pass.",
        parking="", parkingSource="",
        cancellation="", cancellationSource="",
        incidental="", checkInOut="", qualification="",
        source=CAESARS_HOTEL, feeSource="", taxSource="",
        qualityNote="Not scored.",
        status="Open item: hotel cost components are not yet verified for this property.",
        walkNote="Poker room is inside the property; Google Maps walking route to The Venetian measures 12 minutes.",
    ),
    dict(
        id="horseshoe", name="Horseshoe Las Vegas", venue="Horseshoe Hall of Fame poker room", property="Horseshoe Las Vegas",
        rooms="", baseRate="", baseRateFloor="", baseRateCeiling="",
        baseRateNote="No room price is published on the official pages reviewed.",
        resortFee="", resortFeeNote="Not verified: the Horseshoe hotel fee and tax terms were not captured in this pass.",
        taxRate="", taxNote="Not verified in this pass.",
        parking="", parkingSource="",
        cancellation="", cancellationSource="",
        incidental="", checkInOut="", qualification="",
        source=HORSESHOE_HOTEL, feeSource="", taxSource="",
        qualityNote="Not scored.",
        status="Open item: hotel cost components are not yet verified for this property.",
        walkNote="Poker room is inside the property; Google Maps walking route to The Venetian measures 16 minutes.",
    ),
    dict(
        id="aria", name="ARIA Resort & Casino", venue="ARIA poker room", property="ARIA Resort & Casino",
        rooms="", baseRate="", baseRateFloor="", baseRateCeiling="",
        baseRateNote="No room price is published on the official pages reviewed.",
        resortFee=55, resortFeeNote=("The ARIA Hotel Reservation Terms and Conditions state: 'A daily resort fee of $55.00 plus "
                                     "applicable tax will be applied to all reservations.' The fee is waived for eligible MGM "
                                     "Rewards Gold+ members."),
        taxRate="", taxNote=("The same terms state that lodging taxes apply to the basic room rate, any resort fee and other "
                             "charges as required by applicable law. The percentage itself is not published on the reviewed "
                             "pages, so no true nightly total is computed."),
        parking="", parkingSource="",
        cancellation=("The first night's deposit is fully refundable with timely notice to Room Reservations (866.359.7757) at "
                      "least 72 hours prior to arrival; later cancellations and no-shows forfeit the first night's deposit."),
        cancellationSource=ARIA_TERMS,
        incidental=("Credit card authorization at check-in covers room, tax and resort fees plus a per-day incidental amount of "
                    "$150 for Deluxe Rooms, $250 for Tower Suites, $350 for Sky Suites and $500 for Villas."),
        checkInOut="Check-in 3:00 PM; check-out 11:00 AM.",
        qualification="",
        source=ARIA_HOTEL, feeSource=ARIA_TERMS, taxSource=ARIA_TERMS,
        verifiedOn="2026-11-17",
        qualityNote="Not scored.",
        status=("Fee, cancellation and incidental terms verified on the official ARIA terms page on 2026-11-17. Room rate and "
                "tax percentage are still unpublished, so the true nightly cost stays blank."),
        walkNote="Google Maps walking route to The Venetian measures 31 minutes, which is outside the 30-minute limit.",
    ),
]

# Dated rate log. New observations are appended, never overwritten.
RATE_LOG = [
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
    dict(hotel="venetian", observedOn="2026-11-16", baseRate="",
         publishedStartingRates="calendar cells for Nov. 17-30: " + ", ".join(
             f"{d[5:]} ${v}" if v else f"{d[5:]} no price" for d, v in VENETIAN_CALENDAR_NOV),
         resortFee="included in the calendar cell", tax="excluded from the calendar cell",
         trueNightlyLow="", trueNightlyHigh="",
         quoteType="Booking calendar cells (not quotes)",
         note=("The calendar states: 'Pricing shown is best available suite and rate, includes daily resort fee, excludes "
               "taxes.' An earlier observation of the same calendar on the same day recorded $605 for Nov. 17, so these "
               "cells move within a day. The recommended trip window, Nov. 25 to Dec. 2, published no price at all."),
         source=VENETIAN_CALENDAR_NOV_URL, feeSource=VENETIAN_RESORT_FEE, taxSource=VENETIAN_HOTEL_TERMS),
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
    dict(hotel="mgm", observedOn="2026-11-17", baseRate="", publishedStartingRates="",
         resortFee="50.00 plus applicable tax", tax="percentage not published",
         trueNightlyLow="", trueNightlyHigh="",
         quoteType="Published fee terms (no room rate)",
         note=("MGM Grand Hotel Reservation Terms and Conditions: 'A daily resort fee of $50.00 plus applicable tax will be "
               "applied to all reservations.' Lodging taxes apply to the basic room rate and any resort fee; the tax "
               "percentage is not published, so no true nightly total is computed."),
         source=MGM_TERMS, feeSource=MGM_TERMS, taxSource=MGM_TERMS),
    dict(hotel="aria", observedOn="2026-11-17", baseRate="", publishedStartingRates="",
         resortFee="55.00 plus applicable tax", tax="percentage not published",
         trueNightlyLow="", trueNightlyHigh="",
         quoteType="Published fee terms (no room rate)",
         note=("ARIA Hotel Reservation Terms and Conditions: 'A daily resort fee of $55.00 plus applicable tax will be applied "
               "to all reservations.' Lodging taxes apply to the basic room rate and any resort fee; the tax percentage is not "
               "published, so no true nightly total is computed."),
         source=ARIA_TERMS, feeSource=ARIA_TERMS, taxSource=ARIA_TERMS),
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
    dict(hotel="wynn", venue="venetian", minutes=13, miles="0.6",
         note="Maps walking estimate; a 14-minute alternative via Las Vegas Blvd S is also shown.",
         via="Wynn Main Gate Dr", source="https://www.wynnlasvegas.com/casino/poker",
         mapsOrigin="Wynn+Las+Vegas,+3131+Las+Vegas+Blvd+S,+Las+Vegas,+NV+89109",
         mapsDestination="The+Venetian+Resort,+Las+Vegas,+NV"),
    dict(hotel="horseshoe", venue="venetian", minutes=16, miles="0.7",
         note="Maps walking estimate; a 17-minute alternative via Las Vegas Blvd S is also shown.",
         via="Linq Ln", source="https://www.caesars.com/las-vegas/explore/casino/poker-tournaments-las-vegas-strip",
         mapsOrigin="Horseshoe+Las+Vegas+Hotel+%26+Casino,+3645+W+Flamingo+Rd,+Las+Vegas,+NV+89169",
         mapsDestination="The+Venetian+Resort,+Las+Vegas,+NV"),
    dict(hotel="bellagio", venue="venetian", minutes=21, miles="0.9",
         note="Maps walking estimate; a 24-minute alternative is also shown.", via="Las Vegas Blvd S",
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
]
