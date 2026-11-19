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
# The poker room publishes its own parking page (read live 2026-11-17). It adds a player-specific waiver the
# hotel terms page does not print: three hours or more of tournament or cash play earns complimentary
# self-parking for that day. Used as the Venetian hotel row's parking source so the trip-cost parking
# assumption is not overstated.
VENETIAN_POKER_PARKING = "https://www.venetianlasvegas.com/resort/casino/poker/player-parking.html"
VENETIAN_PARKING_READ = "2026-11-17"
VENETIAN_PARKING_WAIVER = (
    "Players in the poker room who play three hours or more in tournament or cash games will receive "
    "complimentary self-parking for the day. Players must visit a supervisor at the end of their session to "
    "confirm qualifications for complimentary self-parking."
)
WYNN_ROOMS = "https://www.wynnlasvegas.com/rooms-and-suites"
# Official booking engine (SynXis IBE on the property's own reservations host).
# The date parameters are checkIn/checkOut as MM/DD/YYYY; read 2026-11-19, the page
# printed "7 Night Stay: Nov. 23 - Nov. 30, 2026" with dated rates for that window.
WYNN_IB_TRIP = ("https://reservations.wynnlasvegas.com/ibe/details.aspx?hotelID=13763&langID=1&rmID=68658"
                "&checkIn=11/23/2026&checkOut=11/30/2026")
# The page the earlier build cited (terms-and-conditions/850070) is an expired
# 2025 DINING CREDIT offer: its own text says a stay "must be completed on or
# before September 30, 2025".  The live, non-offer policy page below is therefore
# used instead; the expired page is kept only as a cross-check and is flagged.
WYNN_TERMS = "https://www.wynnlasvegas.com/about-us/resort-information"
WYNN_PARKING = "https://www.wynnlasvegas.com/about-us/parking"
# Cancellation policy. Re-read live on 2026-11-17 (after the last build): this
# page prints a CANCELLATION POLICY section headed by a deposit statement, and the
# 48-hour window is in that section's own body text, not only in a promotional
# offer's terms.  Flag F35 is corrected accordingly (see data_source.py).
WYNN_TERMS_CANCELLATION = "https://www.wynnlasvegas.com/terms-and-conditions/850070"
WYNN_EXPIRED_OFFER = "https://www.wynnlasvegas.com/terms-and-conditions/850070"
MGM_TERMS = "https://mgmgrand.mgmresorts.com/en/terms-and-conditions.html"
ARIA_TERMS = "https://aria.mgmresorts.com/en/terms-and-conditions.html"
# MGM Resorts parking: read 2026-11-19 (session arena/f5ac4318-poker3).  The three
# property-level parking pages that a reader would guess
# (bellagio|aria|mgmgrand.mgmresorts.com/en/amenities/parking.html) all serve this
# corporate page, so this is the page MGM actually publishes the rates on.  It prints one
# table for Bellagio, ARIA, Vdara, The Cosmopolitan, MGM Grand, Mandalay Bay, W Las Vegas,
# Park MGM, New York-New York, Luxor and Excalibur: self-parking over 0 to 24 hours $20
# weekday / $25 weekend, the same daily figure for each additional day, and a separate
# "Registered Hotel Guest $20 / $20" line; valet $40 a day weekday and weekend.
MGM_PARKING = "https://www.mgmresorts.com/en/things-to-do/parking.html"
MGM_PARKING_READ = "2026-11-19"
MGM_PARKING_NOTE = (
    "The official MGM Resorts parking page (read 2026-11-19) prints one table for Bellagio, ARIA, Vdara, The "
    "Cosmopolitan of Las Vegas, MGM Grand, Mandalay Bay, W Las Vegas, Park MGM, The Reserve at Park MGM, "
    "New York-New York, Luxor and Excalibur: self-parking over 0 to 24 hours $20 Monday-Thursday and $25 "
    "Friday-Sunday for non-guests, the same daily rate for each additional day, and a separate 'Registered "
    "Hotel Guest $20 / $20' line, so a registered guest pays $20 a day on both weekdays and weekends. Valet is "
    "$40 a day weekday and weekend. Self-parking is complimentary for MGM Rewards members at Pearl, Gold, "
    "Platinum and NOIR tier, and Nevada residents park free for the first three hours. The page adds: 'Prices "
    "may be higher during special events' and 'Parking fees are subject to change'. The property-level parking "
    "URL for this hotel (/en/amenities/parking.html) serves this same corporate page, so no property-specific "
    "table is published to cite.")
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
# Official Caesars Entertainment parking policy page (read 2026-11-19, chunks 0-1, session arena/e830d773-poker3).
# Prints property-by-property Las Vegas self-parking and valet dollar amounts that the flexible-dates booking
# calendar omits ("surcharge applies").
CAESARS_PARKING = "https://www.caesars.com/parking"
CAESARS_PARKING_READ = "2026-11-19"
CAESARS_PALACE_PARKING_NOTE = (
    "Confirmed on the official Caesars Entertainment Parking Policy page (read 2026-11-19): "
    "Self-Parking 'Registered Hotel Guests: $20/day', 'Gold: $25/day', 'Non-member: $25/day', "
    "'Platinum: Free', 'Diamond, Diamond Plus, Diamond Elite: Free', 'Seven Stars: Free', and "
    "'Las Vegas Locals: Complimentary Self-Parking through December 26 - No blackout dates. Valid Nevada "
    "driver's license required.' Valet: 'Gold: $50/day', 'Non-member/Registered Hotel Guests: $50/day', "
    "and 'Free' for Platinum, Diamond and Seven Stars. Registered hotel guests get in-and-out self-parking "
    "access across Caesars Entertainment Las Vegas self-parking facilities using their room key.")
HORSESHOE_PARKING_NOTE = (
    "Confirmed on the official Caesars Entertainment Parking Policy page (read 2026-11-19): "
    "Self-Parking 'Non-member/Registered Hotel Guests: Monday - Wednesday $20/day | Thursday - Sunday $25/day' "
    "(same for Gold; 'Free' for Platinum, Diamond, Diamond Plus, Diamond Elite and Seven Stars; "
    "'Las Vegas Locals: Complimentary Self-Parking through December 26 - No blackout dates. Valid Nevada "
    "driver's license required.'). Valet: 'Non-member/Registered Hotel Guests: $40/day (Rates may change for "
    "Special Events)' (same for Gold; 'Free' for Platinum, Diamond and Seven Stars). Because registered-guest "
    "self-parking splits by weekday ($20 Mon-Wed, $25 Thu-Sun; $160 across the 7-night 23-30 Nov 2026 stay), "
    "no single flat nightly constant is stored in parkingPerNight (flag F102).")
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

# Per-property lines from the same county table (Appendix III's per-property list, 2021 edition).
# Read line by line on 2026-11-17 (session arena/5b8ce14d-poker3). The county guide's own link text
# reads "Rates Effective 3-1-17 by Property", and the county guidance page links the rate table as
# "Transient Lodging Tax Rates Effective as of April 2021". Each line is a REFERENCE only: the
# property's own page prints no room-tax percentage, so `taxRate` stays blank (tests enforce this).
def county_reference(listing: str, extra: str = "") -> str:
    return ("County per-property table, " + listing + ": 13.38% for a resort hotel in the Primary Gaming Corridor (PGC). "
            "The guide's Appendix III chart prints 13.38% for 'Resort Hotel in SD & PGC'. Shown as a reference only; "
            "the property's own page prints no room-tax percentage."
            + (" " + extra if extra else ""))

WYNN_COUNTY_REF = county_reference("\"Wynn Las Vegas / Encore at Wynn Las Vegas\"")
BELLAGIO_COUNTY_REF = county_reference("\"Bellagio\"")
MGM_COUNTY_REF = county_reference("\"MGM Grand Hotel/Casino\"")
ARIA_COUNTY_REF = county_reference("\"Aria Resort & Casino\", 3730 Las Vegas Blvd S")
CAESARS_COUNTY_REF = county_reference(
    "\"Caesars Palace\", licence 1136233.RES-001 (the county table prints its address as \"35/0\"; not used)",
    "Caesars' own fee block prints $7.35 tax on its $54.95 fee; 13.38% of $54.95 is $7.35 to the cent, which "
    "agrees with the county figure but is not itself a printed percentage.")
HORSESHOE_COUNTY_REF = county_reference(
    "\"Bally's Las Vegas\", 3645 Las Vegas Blvd S (the Horseshoe page prints the same street address; the county "
    "table uses the former name, so this entry is not treated as Horseshoe's own licence)",
    "Horseshoe's own fee block prints $6.68 tax on its $49.95 fee; 13.38% of $49.95 is $6.68 to the cent.")

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

# Second dated checkout total for the SAME trip stay, printed by the official booking engine on 2026-11-19
# (session arena/e94482ee-poker3). Every money figure below is printed on the page; nothing is inferred.
# It is kept BESIDE the 2026-11-17 read, never in place of it, because the two reads differ on the suite,
# the nightly rates and the total (flag F78 records the earlier drift; F110 records this read).
# Arithmetic check on the printed figures:
#   nightly room rates         204.25 + 204.25 + 204.25 + 309.25 + 1119.25 + 561.75 + 204.25 = 2,807.25
#   resort fee                 7 x 55.00                                                   =   385.00
#   pre-tax subtotal           2,807.25 + 385.00                                            = 3,192.25
#   printed "Taxes"            427.14   (13.38% of 3,192.25 is 427.12, so the printed tax is 2 cents higher;
#                                         3,192.25 + 427.14 = 3,619.39 is the printed total exactly)
#   printed "Average Rate"     456.04   (= (2,807.25 + 385.00) / 7 = 456.036, the average rate INCLUDING the fee)
#   checkout total / 7         3,619.39 / 7 = 517.06  <- the all-in figure a traveller actually pays per night
# The page prints "includes daily resort fee, excludes taxes" on its calendar and lists the $55 fee as its own
# line, while the separate resort-fee terms page says "Rates include a daily Resort Fee of $55 plus tax per
# night" - the same contested wording already flagged as F51.
VENETIAN_QUOTE_TRIP_2026_11_19 = dict(
    property="The Palazzo - palazzo Luxury King suite",
    checkIn="2026-11-23", checkOut="2026-11-30", guests=2, nights=7,
    offer="Book Direct: Up to 25% Off",
    suiteDetail="Approximately 720 square feet, king bed, sunken living room, Roman tub",
    nightly=[("2026-11-23", 204.25), ("2026-11-24", 204.25), ("2026-11-25", 204.25), ("2026-11-26", 309.25),
             ("2026-11-27", 1119.25), ("2026-11-28", 561.75), ("2026-11-29", 204.25)],
    resortFeePerNight=55.00,
    taxes=427.14, total=3619.39, averageRate=456.04,
    derivedNightly=[293.94, 293.94, 293.94, 412.99, 1331.36, 699.27, 293.94], derivedTotal=3619.38,
    note=("Printed by the official booking engine on 2026-11-19 for the identical query as the 2026-11-17 read "
          "(2 adults, arrival 23 Nov 2026, departure 30 Nov 2026, 7 nights): a palazzo Luxury King suite, 'Estimated "
          "cost of stay' $3,619.39, nightly rates 204.25/204.25/204.25/309.25/1,119.25/561.75/204.25, a $55.00 resort "
          "fee listed on each of the seven nights, taxes $427.14 and an Average Rate line of $456.04. The 2026-11-17 "
          "read of the same query returned a venetian Newly Remodeled Luxury King at $4,010.55 (kept in the log). Both "
          "are dated observations; neither replaces the other and neither is a booking price. Arithmetic: the seven "
          "printed room rates sum to $2,807.25, the seven $55 fees to $385.00, so the pre-tax subtotal is $3,192.25; "
          "13.38% of that is $427.12, two cents below the printed $427.14, and $3,192.25 + $427.14 = $3,619.39, which is "
          "the printed total exactly. The printed Average Rate of $456.04 is the average of (room rate + $55) and "
          "therefore includes the resort fee, while the calendar footnote says its figures include the daily resort "
          "fee and exclude taxes - the same wording conflict as flag F51. The all-in cost per night for this quote is "
          "the printed total divided by seven, $517.06, and the seven per-night derivations above add to $3,619.38, "
          "one cent under the printed total. This is not the phone-only poker rate (code EPOKR25, flag F66) and the "
          "poker rate requires six hours of play or a $300+ tournament buy-in for each night stayed."),
    source=VENETIAN_CALENDAR_TRIP_URL, observedOn="2026-11-19")

VENETIAN_QUOTES = [VENETIAN_QUOTE, VENETIAN_QUOTE_2026_11_17, VENETIAN_QUOTE_NOV_20, VENETIAN_QUOTE_TRIP,
                   VENETIAN_QUOTE_TRIP_2026_11_19]

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
                 "rates do not include the applicable Clark County Room Tax of 13.38%.' The county per-property schedule prints the same "
                 "13.38% for a resort hotel in the Primary Gaming Corridor, and the resort fee is 'plus applicable tax' per night. The "
                 "same terms page still opens its Resort Fee section with 'Rates include a daily Resort Fee of $55 plus tax per night', "
                 "and the booking calendar footnote says its prices 'include daily resort fee, excludes taxes', so two official pages "
                 "describe the fee differently and the site uses the fee-on-top reading (F51)."),
        parking=("$20 per day for registered hotel guests (seven days a week); $20 Monday-Thursday and $25 Friday-Sunday "
                 "for non-hotel guests; valet $40 per day (hotel terms). The resort's own poker-room parking page repeats "
                 "those figures and adds a waiver: 'Players in the poker room who play three hours or more in tournament "
                 "or cash games will receive complimentary self-parking for the day.' Venetian Rewards Sapphire and above "
                 "park free; Nevada residents get three hours free; event parking rates may be in effect and rates are "
                 "'subject to change'."),
        # The paid figures are printed on this same page; the hotel terms page prints them too, and the
        # row cites the poker-room page because that is where the player waiver appears (main's test
        # test_every_hotel_fact_links_the_recorded_source pins the citation to this page).
        parkingSource=VENETIAN_POKER_PARKING,
        parkingWaiver=dict(
            status="published-conditional",
            excerpt=VENETIAN_PARKING_WAIVER,
            conditions=("Validated by a supervisor at the end of the session. The same page adds, in its own words, that "
                        "'Venetian Rewards Sapphire members and above receive complimentary self-parking' and that 'Event "
                        "parking rates may be in effect and are subject to change; check posted signage for additional "
                        "details.' It also gives Nevada residents three hours of complimentary self-parking by scanning a "
                        "valid Nevada driver's licence at a self-parking kiosk, not available while event parking rates are "
                        "in effect; that clause is paraphrased because the page's own punctuation could not be reproduced "
                        "byte for byte in this capture."),
            tierRoute=("75 cash-game hours or 15 tournaments in the past 12 months can be emailed to the address on the "
                       "page to be validated for Sapphire tier, which carries complimentary self-parking."),
            source=VENETIAN_POKER_PARKING,
            retrieved=VENETIAN_PARKING_READ,
            appliedToTotals=False,
            whyNotApplied=("The $20 per night stays in every published total. No official source publishes a tournament "
                           "finish time (F16), so a three-hour session cannot be confirmed for a named event, and the "
                           "page makes the waiver conditional on a supervisor confirming the session. The waiver is "
                           "published beside the figure, not folded into it."),
        ),
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
                 "rates do not include the applicable Clark County Room Tax of 13.38%.' The county per-property schedule prints the same "
                 "13.38% for a resort hotel in the Primary Gaming Corridor, and the resort fee is 'plus applicable tax' per night. The "
                 "same terms page still opens its Resort Fee section with 'Rates include a daily Resort Fee of $55 plus tax per night', "
                 "and the booking calendar footnote says its prices 'include daily resort fee, excludes taxes', so two official pages "
                 "describe the fee differently and the site uses the fee-on-top reading (F51). These are the resort-wide Venetian "
                 "terms: no Palazzo-specific fee or tax page was found, and the poker rate page covers 'either The Venetian or The "
                 "Palazzo', so the figures are shared rather than separately published."),
        parking=("$20 per day for registered hotel guests; $25 Friday-Sunday for non-hotel guests; valet $40 per day. "
                 "The poker room is in this building, and the row cites the resort's own poker-room parking page because "
                 "that is where the player waiver appears: 'Players in the poker room who play three hours or more in "
                 "tournament or cash games will receive complimentary self-parking for the day.' The same page prints the "
                 "paid guest rate; the hotel terms page carries the identical figures."),
        parkingSource=VENETIAN_POKER_PARKING,
        parkingWaiver=dict(
            status="published-conditional",
            excerpt=VENETIAN_PARKING_WAIVER,
            conditions=("The page is the resort's single poker-room parking page and does not separate The Venetian from "
                        "The Palazzo; the poker room itself is at The Palazzo, level 2 of Grand Canal Shoppes, per the "
                        "official poker-room page. Supervisor confirmation required."),
            source=VENETIAN_POKER_PARKING,
            retrieved=VENETIAN_PARKING_READ,
            appliedToTotals=False,
            whyNotApplied=("Same as The Venetian: the paid figure stays in the total because no official source publishes "
                           "a finish time (F16) and the waiver needs supervisor confirmation."),
        ),
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
        baseRateNote=("The official rooms page (re-read 2026-11-19) lists room categories and Book Now links and still "
                       "publishes no room price on the page itself. The property's own booking engine does print dated "
                       "rates: read 2026-11-19 for the trip window (Wynn Resort King, 7 nights, 23-30 Nov 2026) it printed "
                       "$495 avg/night (Flexible Getaway Rate) and $405 avg/night ('Your Fall to Have It All'), each "
                       "'Includes Resort Fee, Excludes taxes' - see the dated rate log. No checkout total and no tax "
                       "amount print for those quotes, so no true nightly cost is computed. The poker-room page links a "
                       "'Reserve your stay' contact for poker players, which was not published as a price."),
        resortFee=55,
        resortFeeNote=("Reservations are charged a daily resort fee of $55 plus tax for each room night, on both standard "
                       "rooms and Tower Suites."),
        taxRate="",
        taxNote=("Wynn prints 'plus tax' without a percentage. The 13.38% Clark County room tax is the rate printed in the "
                 "Venetian hotel terms; applying it to Wynn's own total is an assumption and is labelled as one."),
        taxReference=WYNN_COUNTY_REF, taxReferenceSource=ROOM_TAX_REFERENCE,
        parkingSource=WYNN_PARKING,
        # Re-read 2026-11-19: the official Parking page prints "complimentary parking for all Wynn and Encore Resort
        # and Tower Suite registered guests", so a registered guest pays $0 a night and is therefore a published
        # zero, not a blank. Unregistered guests ($25/day self, $40/day valet) are a different line and are kept in
        # the parking note; the trip cost model is a registered-guest stay.
        parkingPerNight=0.0,
        # A published zero must not render as a blank cell, so the row carries a parking string that prints it and
        # keeps the unregistered-guest rates in the same cell.
        parking=("$0 a night for a registered guest (official Parking page: self-parking garages are "
                 "'complimentary parking for all Wynn and Encore Resort and Tower Suite registered guests'). "
                 "Unregistered guests pay $25/day self-parking with the first three hours complimentary, and $40/day "
                 "valet; complimentary self-parking is also extended to Wynn Poker Room guests. Read 2026-11-19."),
        parkingPerNightNote=("$0 for a registered guest: the official Parking page says self-parking garages 'are ... "
                             "complimentary parking for all Wynn and Encore Resort and Tower Suite registered guests'. "
                             "Unregistered guests pay $25/day self-parking (first three hours free) and $40/day valet; "
                             "poker-room guests are also given complimentary self-parking. Read 2026-11-19."),
        cancellation=("A deposit of the first night's room rate and tax is charged at booking. The property's live "
                      "terms page prints a CANCELLATION POLICY section: \"cancellations must be received at least 48 "
                      "hours prior to arrival date or deposit (if applicable) will be forfeited\", and early departures "
                      "without notice cost \"the room rate and tax for the night on which the guest departed early\". "
                      "The same page carries offer-specific date exceptions, which were not read individually, so the "
                      "48-hour window is recorded as the general term only (re-read 2026-11-17, flag F35)."),
        cancellationSource=WYNN_TERMS_CANCELLATION,
        incidental=("A credit card authorised to cover room, resort fees and tax plus $150 a night for incidentals is "
                    "required at check-in."),
        checkInOut="Check-in 3 p.m.; check-out 12 p.m. (official resort policies page).",
        qualification="",
        source=WYNN_ROOMS, feeSource=WYNN_TERMS, taxSource=WYNN_TERMS,
        bookingUrl=WYNN_IB_TRIP,
        bookingLinks=[dict(label="whole trip, 7 nights (quote read 2026-11-19)", url=WYNN_IB_TRIP)],
        # The engine printed two dated average prices for the exact 7-night trip stay, each
        # described as "Includes Resort Fee, Excludes taxes". A true nightly cost can therefore
        # be derived for Wynn without inventing a rate: the average already contains the $55
        # resort fee, so only the Clark County room tax is added. It is labelled derived, not
        # quoted, because Wynn prints no tax amount and no checkout total of its own.
        derivedNightlyLow=459.19, derivedNightlyHigh=561.23,
        derivedNightlyNote=("Derived, not quoted. Wynn's own reservations engine printed, for the exact trip stay "
                            "(23-30 Nov 2026, 7 nights), '$405 avg/night' and '$495 avg/night', each marked "
                            "'Includes Resort Fee, Excludes taxes'. The resort fee is therefore already inside those "
                            "figures; adding the 13.38% Clark County room tax printed in The Venetian's hotel terms "
                            "gives $405 x 1.1338 = $459.19 and $495 x 1.1338 = $561.23 per night all-in. Wynn prints no "
                            "tax amount and no checkout total, so this is arithmetic on its own published figures and "
                            "is labelled as derived, not as a quote."),
        bookingLinksNote=(
            "This link opens the official Wynn reservations engine with the trip dates already selected "
            "(checkIn/checkOut are MM/DD/YYYY parameters). On 2026-11-19 that exact URL printed '7 Night Stay: "
            "Nov. 23 - Nov. 30, 2026' with dated rates ($495 and $405 avg/night, resort fee included, taxes "
            "excluded; see the rate log). The link is not a price: the engine reprices on every read."),
        sourceNote=("The fee, parking and check-in times are read from the live Resort Policies page. The page the earlier "
                    "build cited (terms-and-conditions/850070) is an expired 2025 DINING CREDIT offer whose own text "
                    "requires a stay completed by September 30, 2025, so it cannot substantiate a 2026 trip."),
        qualityNote=("The rooms page states 'With 22 Five-Star awards across our hotels, spas and restaurants, Wynn Resorts "
                     "holds more Five-Star designations than any independent hotel company in the world' and links Forbes "
                     "Travel Guide. That is a publisher claim, not a comparable room-level score, so no numeric score is used."),
        status=("Strongest published fee transparency of the Strip properties reviewed, and after 2026-11-19 the only "
                "property besides the Venetian with a dated official quote for the trip window (avg/night including the "
                "resort fee, taxes excluded). No checkout total and no room-tax percentage are printed, so no true "
                "nightly cost is computed."),
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
        taxReference=BELLAGIO_COUNTY_REF, taxReferenceSource=ROOM_TAX_REFERENCE,
        parking=MGM_PARKING_NOTE,
        parkingSource=MGM_PARKING,
        parkingPerNight=20.0,
        parkingNote=("Registered hotel guests pay $20 a day for self-parking on weekdays and weekends; valet is $40 a "
                     "day. Read from the MGM Resorts parking page on 2026-11-19. Self-parking is free for MGM Rewards "
                     "members at Pearl tier and above."),
        cancellation=("The first night's deposit is fully refundable if cancellation is received at least 72 hours prior to "
                      "arrival. Cancelling later, or failing to show, forfeits the first night. Complimentary stays incur a "
                      "$165 mid-week or $200 weekend cancellation fee."),
        cancellationSource=BELLAGIO_TERMS,
        incidental="$150 incidental amount per day authorised at check-in.",
        # The Bellagio hotel reservation terms page was read live on 2026-11-17 (2 chunks) and prints
        # the resort fee, taxes, deposit, incidental hold and cancellation window, but no check-in or
        # check-out clock time. Left as an explicit blank rather than copied from another MGM property.
        checkInOut="",
        checkInOutNote=("Not published on the Bellagio hotel reservation terms page, which was read in full on "
                        "2026-11-17: it prints the deposit, cancellation, tax and incidental terms but no check-in or "
                        "check-out time. Not inferred from MGM Grand or ARIA, which both print 3:00 pm / 11:00 am."),
        qualification="",
        source=BELLAGIO_HOTEL, feeSource=BELLAGIO_TERMS, taxSource=BELLAGIO_TERMS,
        qualityNote="Not scored. No official, comparable quality metric was published in the reviewed material.",
        status=("On-property poker room with published weekly tournaments; no published room price. Parking is published: "
                "$20 a day self-parking for registered hotel guests, $40 valet (MGM Resorts parking page, 2026-11-19)."),
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
        taxReference=MGM_COUNTY_REF, taxReferenceSource=ROOM_TAX_REFERENCE,
        parking=MGM_PARKING_NOTE, parkingSource=MGM_PARKING, parkingPerNight=20.0,
        parkingNote=("Registered hotel guests pay $20 a day for self-parking on weekdays and weekends; valet is $40 a "
                     "day. Read from the MGM Resorts parking page on 2026-11-19. Self-parking is free for MGM Rewards "
                     "members at Pearl tier and above."),
        cancellation=("The first night's deposit is fully refundable with notice at least 72 hours before arrival; later "
                      "cancellations and no-shows forfeit the first night."),
        cancellationSource=MGM_TERMS,
        incidental="$100 incidental authorisation per day at check-in.", checkInOut="Check-in 3:00 pm; check-out 11:00 am.",
        qualification="",
        source=MGM_HOTEL, feeSource=MGM_TERMS, taxSource=MGM_TERMS,
        qualityNote="Not scored.",
        status=("Fee and parking terms verified from the property's own pages; no published room price, and the walking "
                "route to the Venetian is outside the limit."),
        walkNote="Poker room is inside the property; Google Maps walking route to The Venetian measures 35 minutes.",
    ),
    dict(
        id="caesars", name="Caesars Palace", venue="Caesars Palace poker room", property="Caesars Palace",
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
        # Printed on the property's own booking page, re-read 2026-11-17 22:3x UTC. Kept as numbers so the
        # cost model's 13.38% can be checked against the property's own arithmetic, not only the Venetian's terms.
        printedFeeAndTax=dict(fee=54.95, tax=7.35, allIn=62.30, observedOn="2026-11-17",
                              excerpt="Resort fees: $62.30 ($54.95 plus $7.35 tax)",
                              source=CAESARS_CALENDAR),
        parking=CAESARS_PALACE_PARKING_NOTE,
        parkingSource=CAESARS_PARKING,
        parkingPerNight=20.0,
        parkingNote=("Registered hotel guests pay $20/day for self-parking ($25/day for non-members and Gold) and "
                     "$50/day for valet; complimentary for Caesars Rewards Platinum, Diamond and Seven Stars. Read "
                     "from https://www.caesars.com/parking on 2026-11-19."),
        cancellation=("The official property page advertises 'FREE 48-Hour Cancellation*' under 'Why Book With Us'; the "
                      "terms behind the asterisk are not printed on that page. The booking page adds that rates shown "
                      "include applicable resort fees and that pricing and availability may vary with length of stay."),
        cancellationSource=CAESARS_BOOKING_HOMEPAGE,
        incidental="$100 per day deposit; a credit card is required at check-in for incidental charges; cash is not accepted for deposits or room charges.",
        checkInOut="Check-in starts at 4 PM; check-out is 11 AM; minimum check-in age is 21.",
        qualification="",
        source=CAESARS_HOTEL, feeSource=CAESARS_CALENDAR, taxSource=CAESARS_CALENDAR,
        taxReference=CAESARS_COUNTY_REF, taxReferenceSource=ROOM_TAX_REFERENCE,
        qualityNote=("Not scored. No official quality metric is published. Facts published by the property for 2026 "
                     "stays: 3,976 rooms, 11 restaurants, full-service spa, pool complex; 21+ check-in."),
        status=("Resort fee, deposit and check-in/check-out confirmed from the property's own booking page (2026-11-17), "
                "and self-parking ($20/day registered hotel guests) and valet ($50/day) confirmed from the official "
                "Caesars Entertainment parking policy page (2026-11-19). The room rate and the room-tax percentage are "
                "still not published, so no true nightly cost can be computed from property-published components."),
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
        # Printed on the property's own booking page. Kept as numbers so the cost model's 13.38% can be checked against
        # the property's own arithmetic rather than only the Venetian's terms.
        printedFeeAndTax=dict(fee=49.95, tax=6.68, allIn=56.63, observedOn="2026-11-17",
                              excerpt="Resort fees: $56.63 ($49.95 plus $6.68 tax)",
                              source=HORSESHOE_CALENDAR_NOV),
        parking=HORSESHOE_PARKING_NOTE,
        parkingSource=CAESARS_PARKING,
        parkingNote=("Registered hotel guests pay $20/day Monday-Wednesday and $25/day Thursday-Sunday for self-parking "
                     "($160 across the 7-night 23-30 Nov 2026 stay) and $40/day for valet; complimentary for Caesars "
                     "Rewards Platinum, Diamond and Seven Stars. Read from https://www.caesars.com/parking on 2026-11-19."),
        cancellation=("The official property page advertises 'FREE 48-Hour Cancellation*' under 'Why Book With Us'; the "
                      "terms behind the asterisk are not printed on that page. The booking page adds: 'Rates shown "
                      "reflect the lowest available rate and include applicable resort fees.'"),
        cancellationSource=CAESARS_BOOKING_HOMEPAGE,
        incidental="$50 per day deposit; a credit card is required at check-in for incidental charges. Pet fee $75; rollaway bed $30 per day; $50 plus tax no-show fee on complimentary rooms.",
        checkInOut="Check-in starts at 4 PM; check-out is 11 AM; minimum check-in age is 21.",
        qualification="",
        source=HORSESHOE_HOTEL, feeSource=HORSESHOE_CALENDAR_NOV, taxSource=HORSESHOE_CALENDAR_NOV,
        taxReference=HORSESHOE_COUNTY_REF, taxReferenceSource=ROOM_TAX_REFERENCE,
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
        taxReference=ARIA_COUNTY_REF, taxReferenceSource=ROOM_TAX_REFERENCE,
        parking=MGM_PARKING_NOTE, parkingSource=MGM_PARKING, parkingPerNight=20.0,
        parkingNote=("Registered hotel guests pay $20 a day for self-parking on weekdays and weekends; valet is $40 a "
                     "day. Read from the MGM Resorts parking page on 2026-11-19. Self-parking is free for MGM Rewards "
                     "members at Pearl tier and above."),
        cancellation=("The first night's deposit is fully refundable with notice at least 72 hours before arrival; later "
                      "cancellations and no-shows forfeit the first night."),
        cancellationSource=ARIA_TERMS,
        incidental=("$150 per day incidental authorisation for Deluxe Rooms, $250 Tower Suites, $350 Sky Suites, $500 "
                    "Villas."),
        checkInOut="Check-in 3:00 pm; check-out 11:00 am.", qualification="",
        source=ARIA_HOTEL, feeSource=ARIA_TERMS, taxSource=ARIA_TERMS,
        qualityNote="Not scored.",
        status=("Fee and parking terms verified; the walking route to the Venetian is outside the limit, and no dated "
                "poker schedule was confirmed."),
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
    # Second read of the SAME trip window on the same day (session 7529044d, 2026-11-17 about 22:15 UTC,
    # about 20 minutes after the read above). The engine returned a different suite tower and a different
    # total for an identical query. Both are kept as dated observations; neither replaces the other (flag F78).
    dict(hotel="palazzo", observedOn="2026-11-17", baseRate="",
         publishedStartingRates="204.25 (Nov 23), 204.25 (Nov 24), 286.75 (Nov 25), 406.75 (Nov 26), "
                                "1,119.25 (Nov 27), 561.75 (Nov 28), 204.25 (Nov 29) per night, rate before resort fee",
         resortFee="55.00 per night",
         tax="451.21 printed (7 nights)",
         trueNightlyLow="293.94", trueNightlyHigh="1331.36",
         nightlyRates=[204.25, 204.25, 286.75, 406.75, 1119.25, 561.75, 204.25],
         nightlyTrueCost=[293.94, 293.94, 387.48, 523.53, 1331.36, 699.27, 293.94],
         quoteType=("Dated official checkout total (2 adults, 7 nights, 23-30 Nov 2026, best available "
                    "palazzo Luxury King suite) - read 2026-11-17 about 22:15 UTC"),
         note=("Second read of the identical query (2 adults, arrival 23 Nov, departure 30 Nov) about 20 minutes "
               "after the earlier read the same day: the engine returned a different suite tower - a palazzo "
               "Luxury King (about 720 sq ft) instead of the venetian Newly Remodeled Luxury King - and a lower "
               "total, $3,823.46 against $4,010.55, a difference of $187.09 with no change to dates or party size "
               "(flag F78). Printed on the page: estimated cost of stay $3,823.46, average rate $481.75, taxes "
               "$451.21, $55.00 resort fee on each of the seven nights. The seven derived per-night true costs "
               "(rate + $55) x 1.1338 are 293.94, 293.94, 387.48, 523.53, 1331.36, 699.27 and 293.94, which add "
               "to the printed $3,823.46 exactly, and 13.38% of the printed pre-tax subtotal of $3,372.25 is the "
               "printed $451.21. This is a dated observation of the engine's best-available offer, not a booking "
               "price; compare like-for-like by suite name and read time before budgeting (see the rate log and "
               "flag F78)."),
         source=VENETIAN_CALENDAR_TRIP_URL, feeSource=VENETIAN_RESORT_FEE, taxSource=VENETIAN_HOTEL_TERMS),
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
    # --- MGM Resorts property booking calendars, read live 2026-11-17 (session 58e42dbd) ---
    # Both reads are the *calendar* grid, not a checkout quote: the page prints, verbatim,
    # "Calendar pricing includes avg. daily resort fee (if applicable), excludes taxes.
    # Rates are based on the lowest rate available."  So a cell is a resort-fee-inclusive,
    # tax-exclusive nightly figure for the room type selected in the picker.  Nothing here is
    # converted into a quote and no tax is added, because the property prints no percentage.
    dict(hotel="mgm", observedOn="2026-11-17", baseRate="",
         publishedStartingRates=("MGM King calendar cells, November 2026: 11-18 $219; 11-22 $84, 11-23 $84, "
                                 "11-24 $84, 11-25 $84, 11-26 $149, 11-27 $349, 11-28 $149; 11-30 $649. "
                                 "December 2026: 12-01 $649, 12-02 $1,049, 12-03 $1,149, 12-04 $299, 12-05 $349, "
                                 "12-06 $429, 12-07 $210, 12-08 $210, 12-09 $91, 12-10 $229, 12-11 $579, "
                                 "12-12 $409"),
         resortFee="50.00 per night plus applicable tax (MGM Grand hotel reservation terms), already inside the calendar cell",
         tax="not printed: the calendar states it excludes taxes and the terms print no percentage",
         trueNightlyLow="", trueNightlyHigh="",
         quoteType=("Official booking-calendar cells (lowest available, resort-fee inclusive, tax exclusive; "
                    "not a quote)"),
         note=("Read on the MGM Grand room booking page with the MGM King picker selected and 2 guests. The page's own "
               "legend reads: 'Calendar pricing includes avg. daily resort fee (if applicable), excludes taxes. "
               "Rates are based on the lowest rate available. Rates and room availability may vary based on the "
               "actual length of your stay.' Six of the seven trip nights (23-29 Nov) printed a cell; 29 Nov printed "
               "as unavailable. No checkout total is printed for a dated stay without completing a reservation, so "
               "no true-nightly figure is derived. Tax stays blank because MGM Grand prints no room-tax percentage."),
         source="https://mgmgrand.mgmresorts.com/book-room?property=mgmgrand&room=23f5bef8-63ea-4ba9-a290-13b5a3056595"
                "&resort=66964e2b-2550-4476-84c3-1a4c0c5c067f",
         feeSource=MGM_TERMS, taxSource=MGM_TERMS),
    dict(hotel="bellagio", observedOn="2026-11-17", baseRate="",
         publishedStartingRates="",
         resortFee="55.00 per night plus applicable tax (Bellagio hotel reservation terms)",
         tax="not printed: Bellagio's terms print no room-tax percentage",
         trueNightlyLow="", trueNightlyHigh="",
         quoteType="No property-identified price captured; grid did not identify Bellagio in this read",
         note=("The Bellagio booking page was opened for 2 guests on 2026-11-17 and rendered a calendar grid, but the "
               "grid is NOT recorded as a Bellagio price. The identical grid appeared on the MGM Grand booking page "
               "in the same session (see flag F81 in the register): 22-28 November printed $84, $84, $84, $84, $149, $349, $149 and "
               "30 November printed $649, with 17 November $309 and 19 November $249 on the Bellagio URL. A page that "
               "can serve another property's grid is not evidence of this property's rate, so the Bellagio room rate "
               "stays blank and no nightly figure is derived from these cells."),
         source="https://bellagio.mgmresorts.com/book-room?property=bellagio"
                "&resort=66964e2b-2550-4476-84c3-1a4c0c5c067f",
         feeSource=BELLAGIO_TERMS, taxSource=BELLAGIO_TERMS),
    # ---- 2026-11-19 pass (session 827185f7): dated trip-window attempts at every remaining
    # property, plus the first dated Wynn engine quote. Appended; nothing above was edited. ----
    dict(hotel="wynn", observedOn="2026-11-19", baseRate="",
         publishedStartingRates=("Wynn Resort King, 7-night stay 23-30 Nov 2026, engine default occupancy: "
                                 "Flexible Getaway Rate $495 avg/night; 'Your Fall to Have It All' $405 avg/night "
                                 "- both printed 'Includes Resort Fee, Excludes taxes'"),
         resortFee="55.00 per night (printed on the same page: 'A daily resort fee of $55 plus tax will be added "
                   "to your room account for each ... room night')",
         tax="not printed for this quote: the engine states 'Excludes taxes' and Wynn publishes no room-tax "
             "percentage (F39)",
         trueNightlyLow="", trueNightlyHigh="",
         quoteType=("Dated official engine quote (Wynn Resort King, 7 nights, 23-30 Nov 2026) - read 2026-11-19"),
         note=("Read on the official Wynn reservations engine on 2026-11-19. The page heading prints '7 Night Stay: "
               "Nov. 23 - Nov. 30, 2026' for the Wynn Resort King (640 sq ft). Two public rates print for that exact "
               "window: Flexible Getaway at $495 avg/night and 'Your Fall to Have It All' at $405 avg/night (20% off, "
               "'book by November 24, 2026'; the offer page also lists 'Additional savings available: November "
               "22-26'). Both are footed 'Includes Resort Fee, Excludes taxes', so no checkout total and no tax "
               "amount print, and no true nightly figure is derived (Wynn prints no room-tax percentage, F39). "
               "Guarantee, both offers: 'A valid credit card is required to confirm your reservation. One night's "
               "room rate and tax will be charged at time of booking.' Cancellation for this window, both offers: "
               "'Cancel 72 hours prior to arrival to avoid penalty of one night's room rate and tax.' The same page "
               "prints an offer-specific restriction for stays 15-21 Nov 2026 (cancel 21 days prior; non-refundable "
               "if booked on or after 25 Oct 2026) - recorded as printed, it does not cover this window. The Wynn "
               "Rewards Exclusive Rate and The Wonder of Wynn print no price without sign-in. Occupancy caveat: the "
               "extracted page text does not expose the adults selector's selected value, so this is the engine's "
               "default occupancy for 1 room (the URL carries rooms=1); confirm the guest count in the cart before "
               "payment. Parking, printed on the page: self-parking complimentary to registered guests; valet "
               "complimentary to Tower Suites registered guests. Extra guests: 'for rooms with more than two guests "
               "a $50 per night per additional person fee is added'. Same day, the same engine with its default "
               "1-night window (18-19 Nov 2026) printed $654 avg/night Flexible and $564 Fall, so the quotes move "
               "with the stay window - which is why they are logged, not stored as one value."),
         source=WYNN_IB_TRIP, feeSource=WYNN_TERMS, taxSource=WYNN_TERMS),
    dict(hotel="wynn", observedOn="2026-11-19", baseRate="",
         publishedStartingRates=("Context read the same minutes: engine default 1-night stay 18-19 Nov 2026, "
                                 "Wynn Resort King - Flexible Getaway $654 avg/night, 'Your Fall to Have It All' "
                                 "$564 avg/night, both 'Includes Resort Fee, Excludes taxes'"),
         resortFee="55.00 per night (printed on the same page)",
         tax="not printed for this quote ('Excludes taxes'; Wynn prints no percentage - F39)",
         trueNightlyLow="", trueNightlyHigh="",
         quoteType="Dated official engine quote (default 1-night window 18-19 Nov 2026) - context read 2026-11-19",
         note=("The same engine URL without date parameters opens on its default window, '1 Night Stay: Nov. 18 - "
               "Nov. 19, 2026', and printed $654/$564 avg/night the same day the trip window printed $495/$405. "
               "Kept beside the trip-window entry so the window dependence is visible; neither replaces the other. "
               "For that default window the printed cancellation text was the offer's stay-restricted version "
               "(stays 15-21 Nov: cancel 21 days prior, non-refundable if booked on or after 25 Oct 2026)."),
         source="https://reservations.wynnlasvegas.com/ibe/details.aspx?hotelID=13763&langID=1&rmID=68658",
         feeSource=WYNN_TERMS, taxSource=WYNN_TERMS),
    dict(hotel="mgm", observedOn="2026-11-19", baseRate="",
         publishedStartingRates=("MGM King calendar cells, November 2026 (2 guests): 19-21 Nov printed '--'; "
                                 "22-25 $84, 26 $128, 27 $349, 28 $128, 29 $169, 30 $349. Trip nights 23-29 Nov: "
                                 "$84, $84, $84, $128, $349, $128, $169 - the seven cells sum to $1,026.00 "
                                 "before tax. December cells: 12-01 $548, 12-02 $1,049, 12-03 $1,149, 12-04 $299, "
                                 "12-05 $349, 12-06 $429, 12-07 $210, 12-08 $210, 12-09 $91, 12-10 $249, "
                                 "12-11 $579, 12-12 $449"),
         resortFee="50.00 per night plus applicable tax (MGM Grand hotel reservation terms), already inside the "
                   "calendar cell",
         tax="not printed: the calendar states it excludes taxes and the terms print no percentage",
         trueNightlyLow="", trueNightlyHigh="",
         quoteType=("Official booking-calendar cells (lowest available, resort-fee inclusive, tax exclusive; "
                    "not a quote) - re-read 2026-11-19"),
         note=("Second reading of the official MGM Grand room booking page, 2026-11-19, with the MGM King picker "
               "selected, guests=2 in the URL, and 'MGM Grand Las Vegas Selected' in the resort picker, so the grid "
               "is property-identified. Legend printed again: 'Calendar pricing includes avg. daily resort fee (if "
               "applicable), excludes taxes. Rates are based on the lowest rate available. Rates and room "
               "availability may vary based on the actual length of your stay.' Cells moved since 2026-11-17 and "
               "both readings are kept: 26 Nov $149 -> $128, 28 Nov $149 -> $128, 29 Nov unavailable -> $169, "
               "30 Nov $649 -> $349, 1 Dec $649 -> $548, 10 Dec $229 -> $249, 12 Dec $409 -> $449. All seven trip "
               "nights now print a cell (29 Nov was unavailable before). No checkout total is printed for a dated "
               "stay without completing a reservation, so no true-nightly figure is derived and the tax stays blank."),
         source="https://mgmgrand.mgmresorts.com/book-room?property=mgmgrand&room=23f5bef8-63ea-4ba9-a290-13b5a3056595"
                "&resort=66964e2b-2550-4476-84c3-1a4c0c5c067f",
         feeSource=MGM_TERMS, taxSource=MGM_TERMS),
    dict(hotel="bellagio", observedOn="2026-11-19", baseRate="",
         publishedStartingRates="",
         resortFee="55.00 per night plus applicable tax (Bellagio hotel reservation terms)",
         tax="not printed: Bellagio's terms print no room-tax percentage",
         trueNightlyLow="", trueNightlyHigh="",
         quoteType="No property-identified price captured; the redirected grid identifies MGM Grand in this read",
         note=("Read 2026-11-19 on the recorded Bellagio book-room URL. The URL redirected to the generic "
               "book-room/resort page with the property parameter dropped, no room picker ('Price on calendar "
               "for' absent), and 'MGM Grand Las Vegas Selected' in the resort picker. The grid shown (19 Nov $129, "
               "22-25 Nov $84, 26 Nov $128, 27 Nov $349, 28 Nov $128, 29 Nov $169, 30 Nov $349) is therefore not "
               "attributable to Bellagio and is not recorded as a Bellagio price - the same rule as flag F81. The "
               "Bellagio room rate stays blank and no nightly figure is derived."),
         source="https://bellagio.mgmresorts.com/book-room?property=bellagio"
                "&resort=66964e2b-2550-4476-84c3-1a4c0c5c067f",
         feeSource=BELLAGIO_TERMS, taxSource=BELLAGIO_TERMS),
    dict(hotel="aria", observedOn="2026-11-19", baseRate="",
         publishedStartingRates="",
         resortFee="55.00 per night plus applicable tax (ARIA hotel reservation terms)",
         tax="not printed: ARIA's terms print no room-tax percentage",
         trueNightlyLow="", trueNightlyHigh="",
         quoteType="No property-identified price captured; the redirected grid identifies MGM Grand in this read",
         note=("Read 2026-11-19 on the official ARIA host's book-room path (same engine pattern as MGM Grand). The "
               "URL redirected to the generic book-room/resort page with no property parameter and no room picker, "
               "and the resort picker shows 'MGM Grand Las Vegas Selected'. Per the F81 rule a grid that can serve "
               "another property's prices is not evidence of this property's rate, so the ARIA room rate stays "
               "blank and no nightly figure is derived."),
         source="https://aria.mgmresorts.com/book-room?property=aria"
                "&resort=66964e2b-2550-4476-84c3-1a4c0c5c067f",
         feeSource=ARIA_TERMS, taxSource=ARIA_TERMS),
    dict(hotel="horseshoe", observedOn="2026-11-19", baseRate="",
         publishedStartingRates="",
         resortFee="49.95 per night plus $6.68 tax = $56.63 (re-printed on the page in this read)",
         tax="not printed for room rates: the page prints only the tax charged on the resort fee ($6.68 on $49.95)",
         trueNightlyLow="", trueNightlyHigh="",
         quoteType="No rate grid returned in this read; policy values re-confirmed",
         note=("Read 2026-11-19 on the official Horseshoe booking calendar for November 2026. The rate grid did "
               "not load: the page printed 'Sorry! Our website is currently experiencing technical difficulties. "
               "Please try your search again...' and 'Searching Rates', so no dated rate was captured. Every "
               "policy value the site records from this page re-printed verbatim in the same read: 'Resort fees: "
               "$56.63 ($49.95 plus $6.68 tax)', 'Resort fees are not assessed for Diamond and Seven Stars "
               "guests.', 'Deposit: $50 per day', check-in 4 PM / check-out 11 AM / 21+, 'Rates shown reflect the "
               "lowest available rate and include applicable resort fees.', and 'Wifi included in Resort Fee'. "
               "The 2026-11-17 dated cells remain the latest printed rates for this property."),
         source=HORSESHOE_CALENDAR_NOV, feeSource=HORSESHOE_CALENDAR_NOV, taxSource=HORSESHOE_CALENDAR_NOV),
    dict(hotel="caesars", observedOn="2026-11-19", baseRate="",
         publishedStartingRates="",
         resortFee="54.95 per night plus $7.35 tax = $62.30 (re-printed on the page in this read)",
         tax="not printed for room rates: the page prints only the tax charged on the resort fee ($7.35 on $54.95)",
         trueNightlyLow="", trueNightlyHigh="",
         quoteType="No rate grid returned in this read; policy values re-confirmed",
         note=("Read 2026-11-19 on the official Caesars Palace booking calendar for December 2026. The rate grid "
               "did not load: 'Sorry! Our website is currently experiencing technical difficulties...' and "
               "'Searching Rates', no price cells - the same outcome as the 2026-11-17 read. Policy values "
               "re-printed verbatim: 'Resort fees: $62.30 ($54.95 plus $7.35 tax)', 'Resort fees are not assessed "
               "for Diamond and Seven Stars guests.', 'Deposit: $100 per day', check-in 4 PM / check-out 11 AM / "
               "21+, 3,976 rooms, 11 restaurants. No room rate is captured and none is inferred."),
         source=CAESARS_CALENDAR, feeSource=CAESARS_CALENDAR, taxSource=CAESARS_CALENDAR),
    dict(hotel="venetian", observedOn="2026-11-19", baseRate="",
         publishedStartingRates="",
         resortFee="55.00 per night (no fee figure printed in this read)",
         tax="not printed in this read",
         trueNightlyLow="", trueNightlyHigh="",
         quoteType="No quote returned for the trip window in this read (engine showed loading text)",
         note=("The official booking engine was opened twice on 2026-11-19 for the trip window (2 adults, arrival "
               "23 Nov, departure 30 Nov, view=calendar). Both reads returned 'Your Venice meets Vegas getaway is "
               "loading' plus the Venetian Rewards sign-up panel, with no calendar, no suite and no total. This is "
               "a failed render, not evidence of a sold-out stay or a price change: no figure was printed, so none "
               "is recorded. The printed totals from 2026-11-17 ($4,010.55 Venetian / $3,823.46 Palazzo) remain "
               "the latest dated checkout totals for this window, and a working render should be re-checked before "
               "nonrefundable payment."),
         source=VENETIAN_CALENDAR_TRIP_URL, feeSource=VENETIAN_RESORT_FEE, taxSource=VENETIAN_HOTEL_TERMS),
]

MAPS = "https://www.google.com/maps/dir/?api=1&travelmode=walking&origin={o}&destination={d}"

ROUTES = [
    # Walking routes to the Venetian poker room were re-read on 2026-11-17 in Google Maps walking mode.
    # Each row with a walkCapture key is asserted against raw/google_maps_walk_2026-11-17.json by
    # tests/test_walk_captures_2026_11_17.py. `minutes` is the first (recommended) route card; the
    # other shown routes are in `note`. Google Maps is not an official venue source (flag F77).
    dict(hotel="venetian", venue="venetian", minutes=0, miles="",
         note="Poker room is inside the hotel's own resort; indoor walk, no street crossing.",
         via="", source="https://www.venetianlasvegas.com/resort/casino/poker.html",
         mapsOrigin="The+Venetian+Resort,+Las+Vegas,+NV", mapsDestination="The+Venetian+Resort,+Las+Vegas,+NV"),
    dict(hotel="palazzo", venue="venetian", minutes=4, miles="0.2", lastReadOn="2026-11-17", walkCapture="palazzo-to-venetian",
         note="Google Maps walking directions read 2026-11-17: 4 min (0.2 mile) via unnamed roads; the poker room is in the same resort.",
         via="unnamed roads", source="https://www.venetianlasvegas.com/resort/casino/poker/suite-rates.html",
         mapsOrigin="The+Palazzo+Las+Vegas+NV", mapsDestination="The+Venetian+Resort+Las+Vegas+NV"),
    dict(hotel="wynn", venue="wynn", minutes=10, miles="0.4",
         note="The official Wynn poker page states the poker room is 'located in Encore at Wynn Las Vegas'. Google Maps walking estimate 10 minutes (0.4 mile); not re-read on 2026-11-17.",
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
         note="Room location inside the property is not stated on the source page (not re-read 2026-11-17 beyond the marketing article).",
         via="", source="https://www.caesars.com/las-vegas/explore/casino/poker-tournaments-las-vegas-strip",
         mapsOrigin="Caesars+Palace+Las+Vegas,+3570+Las+Vegas+Blvd+S,+Las+Vegas,+NV",
         mapsDestination="Caesars+Palace+Las+Vegas,+3570+Las+Vegas+Blvd+S,+Las+Vegas,+NV"),
    dict(hotel="horseshoe", venue="horseshoe", minutes=0, miles="",
         note="Room name (Hall of Fame) is from the prior-session Horseshoe casino page; location inside the property is not stated there.",
         via="", source="https://www.caesars.com/las-vegas/explore/casino/poker-tournaments-las-vegas-strip",
         mapsOrigin="Horseshoe+Las+Vegas+Hotel+%26+Casino,+3645+W+Flamingo+Rd,+Las+Vegas,+NV+89169",
         mapsDestination="Horseshoe+Las+Vegas+Hotel+%26+Casino,+3645+W+Flamingo+Rd,+Las+Vegas,+NV+89169"),
    dict(hotel="aria", venue="aria", minutes=0, miles="",
         note="Poker room is inside the hotel.",
         via="", source="https://aria.mgmresorts.com/en/casino/poker.html",
         mapsOrigin="ARIA+Resort+%26+Casino,+Las+Vegas,+NV", mapsDestination="ARIA+Resort+%26+Casino,+Las+Vegas,+NV"),
    # cross-property routes to the Venetian poker room (the main venue)
    dict(hotel="caesars", venue="venetian", minutes=12, miles="0.5", lastReadOn="2026-11-17", walkCapture="caesars-to-venetian",
         note="Google Maps walking directions read 2026-11-17: 12 min (0.5 mile) via Las Vegas Blvd S; a 12-minute alternative (0.6 mile) via S Siegfried And Roy Dr is also shown.",
         via="Las Vegas Blvd S", source="https://www.caesars.com/las-vegas/explore/casino/poker-tournaments-las-vegas-strip",
         mapsOrigin="Caesars+Palace+Las+Vegas+NV", mapsDestination="The+Venetian+Resort+Las+Vegas+NV"),
    dict(hotel="wynn", venue="venetian", minutes=13, miles="0.6", lastReadOn="2026-11-17", walkCapture="wynn-to-venetian",
         note="Google Maps walking directions read 2026-11-17: 13 min (0.6 mile) via Wynn Main Gate Dr; a 14-minute route (0.6 mile) via Las Vegas Blvd S and a 16-minute route (0.7 mile) via Sands Ave are also shown.",
         via="Wynn Main Gate Dr", source="https://www.wynnlasvegas.com/casino/poker",
         mapsOrigin="Wynn+Las+Vegas,+3131+Las+Vegas+Blvd+S,+Las+Vegas,+NV+89109", mapsDestination="The+Venetian+Resort,+Las+Vegas,+NV"),
    dict(hotel="horseshoe", venue="venetian", minutes=16, miles="0.7", lastReadOn="2026-11-17", walkCapture="horseshoe-to-venetian",
         note="Google Maps walking directions read 2026-11-17: 16 min (0.7 mile) via Linq Ln; a 16-minute route via Krueger Dr and a 17-minute route (0.8 mile) via Las Vegas Blvd S are also shown.",
         via="Linq Ln", source="https://www.caesars.com/las-vegas/explore/casino/poker-tournaments-las-vegas-strip",
         mapsOrigin="Horseshoe+Las+Vegas+NV", mapsDestination="The+Venetian+Resort+Las+Vegas+NV"),
    dict(hotel="bellagio", venue="venetian", minutes=21, miles="0.9", lastReadOn="2026-11-17", walkCapture="bellagio-to-venetian",
         note="Google Maps walking directions read 2026-11-17: 21 min (0.9 mile) via Las Vegas Blvd S; a 24-minute route (1.1 miles) via Bellagio Dr is also shown.",
         via="Las Vegas Blvd S", source="https://bellagio.mgmresorts.com/en/casino/poker.html",
         mapsOrigin="Bellagio+Hotel+%26+Casino+Las+Vegas+NV", mapsDestination="The+Venetian+Resort+Las+Vegas+NV"),
    dict(hotel="mgm", venue="venetian", minutes=35, miles="1.6", lastReadOn="2026-11-17", walkCapture="mgm-to-venetian",
         note="Google Maps walking directions read 2026-11-17: 35 min (1.6 miles) via Las Vegas Blvd S. Outside the 30-minute limit.",
         via="Las Vegas Blvd S", source="https://mgmgrand.mgmresorts.com/en/casino/poker-tables.html",
         mapsOrigin="MGM+Grand+Hotel+%26+Casino+Las+Vegas+NV", mapsDestination="The+Venetian+Resort+Las+Vegas+NV"),
    dict(hotel="aria", venue="venetian", minutes=31, miles="1.4", lastReadOn="2026-11-17", walkCapture="aria-to-venetian",
         note="Google Maps walking directions read 2026-11-17: 31 min (1.4 miles) via Las Vegas Blvd S; 32 min via The Cosmopolitan Service Rd and 38 min (1.7 miles) via Frank Sinatra Dr are also shown. Outside the 30-minute limit on every route shown.",
         via="Las Vegas Blvd S", source="https://aria.mgmresorts.com/en/casino/poker.html",
         mapsOrigin="ARIA+Resort+%26+Casino+Las+Vegas+NV", mapsDestination="The+Venetian+Resort+Las+Vegas+NV"),
    # Venetian hotel -> Bellagio Poker Room, the reverse direction is not in the day plan (see F67).
    dict(hotel="venetian", venue="bellagio", minutes=21, miles="0.9", lastReadOn="2026-11-17", walkCapture="venetian-to-bellagio",
         note=("Google Maps walking directions read 2026-11-17: 21 min (0.9 mile) via Las Vegas Blvd S; a 25-minute route "
               "(1.1 miles) via Las Vegas Blvd S and Bellagio Dr is also shown. The same pair is 10 minutes by car on the control read."),
         via="Las Vegas Blvd S", source="https://bellagio.mgmresorts.com/en/casino/poker.html",
         mapsOrigin="The+Venetian+Resort+Las+Vegas+NV", mapsDestination="Bellagio+Hotel+%26+Casino+Las+Vegas+NV"),
    dict(hotel="venetian", venue="wynn", minutes=19, miles="0.9",
         note="Maps walking estimate to Encore, where the Wynn poker room is located, via Las Vegas Blvd S.", via="Las Vegas Blvd S", source="https://www.venetianlasvegas.com/resort/casino/poker.html",
         mapsOrigin="The+Venetian+Resort,+Las+Vegas,+NV", mapsDestination="Encore+Las+Vegas,+3131+Las+Vegas+Blvd+S,+Las+Vegas,+NV+89109", measuredOn="2026-11-17"),
    dict(hotel="venetian", venue="mgm", minutes=36, miles="1.6",
         note="Maps walking estimate, Las Vegas Blvd S.", via="Las Vegas Blvd S", source="https://www.venetianlasvegas.com/resort/casino/poker.html",
         mapsOrigin="The+Venetian+Resort,+Las+Vegas,+NV", mapsDestination="MGM+Grand+Hotel+%26+Casino,+Las+Vegas,+NV", measuredOn="2026-11-17"),
    dict(hotel="venetian", venue="aria", minutes=32, miles="1.4",
         note="Maps walking estimate, Las Vegas Blvd S.", via="Las Vegas Blvd S", source="https://www.venetianlasvegas.com/resort/casino/poker.html",
         mapsOrigin="The+Venetian+Resort,+Las+Vegas,+NV", mapsDestination="ARIA+Resort+%26+Casino,+Las+Vegas,+NV", measuredOn="2026-11-17"),
    dict(hotel="venetian", venue="caesars", minutes=13, miles="0.5",
         note="Maps walking estimate, Las Vegas Blvd S.", via="Las Vegas Blvd S", source="https://www.venetianlasvegas.com/resort/casino/poker.html",
         mapsOrigin="The+Venetian+Resort,+Las+Vegas,+NV", mapsDestination="Caesars+Palace+Las+Vegas,+3570+Las+Vegas+Blvd+S,+Las+Vegas,+NV", measuredOn="2026-11-17"),
    dict(hotel="venetian", venue="horseshoe", minutes=16, miles="0.7",
         note="Maps walking estimate, Krueger Dr.", via="Krueger Dr", source="https://www.venetianlasvegas.com/resort/casino/poker.html",
         mapsOrigin="The+Venetian+Resort,+Las+Vegas,+NV", mapsDestination="Horseshoe+Las+Vegas+Hotel+%26+Casino,+3645+W+Flamingo+Rd,+Las+Vegas,+NV+89169", measuredOn="2026-11-17"),
    dict(hotel="palazzo", venue="wynn", minutes=13, miles="0.6",
         note="Maps walking estimate to Encore, where the Wynn poker room is located, via Las Vegas Blvd S.", via="Las Vegas Blvd S", source="https://www.venetianlasvegas.com/resort/casino/poker.html",
         mapsOrigin="The+Palazzo+Las+Vegas,+Las+Vegas,+NV", mapsDestination="Encore+Las+Vegas,+3131+Las+Vegas+Blvd+S,+Las+Vegas,+NV+89109", measuredOn="2026-11-17"),
    dict(hotel="palazzo", venue="bellagio", minutes=25, miles="1.1",
         note="Maps walking estimate, Las Vegas Blvd S.", via="Las Vegas Blvd S", source="https://www.venetianlasvegas.com/resort/casino/poker.html",
         mapsOrigin="The+Palazzo+Las+Vegas,+Las+Vegas,+NV", mapsDestination="Bellagio+Hotel+%26+Casino,+Las+Vegas,+NV", measuredOn="2026-11-17"),
    dict(hotel="palazzo", venue="mgm", minutes=39, miles="1.7",
         note="Maps walking estimate, Las Vegas Blvd S.", via="Las Vegas Blvd S", source="https://www.venetianlasvegas.com/resort/casino/poker.html",
         mapsOrigin="The+Palazzo+Las+Vegas,+Las+Vegas,+NV", mapsDestination="MGM+Grand+Hotel+%26+Casino,+Las+Vegas,+NV", measuredOn="2026-11-17"),
    dict(hotel="palazzo", venue="aria", minutes=35, miles="1.5",
         note="Maps walking estimate, Las Vegas Blvd S.", via="Las Vegas Blvd S", source="https://www.venetianlasvegas.com/resort/casino/poker.html",
         mapsOrigin="The+Palazzo+Las+Vegas,+Las+Vegas,+NV", mapsDestination="ARIA+Resort+%26+Casino,+Las+Vegas,+NV", measuredOn="2026-11-17"),
    dict(hotel="palazzo", venue="caesars", minutes=16, miles="0.7",
         note="Maps walking estimate, Las Vegas Blvd S.", via="Las Vegas Blvd S", source="https://www.venetianlasvegas.com/resort/casino/poker.html",
         mapsOrigin="The+Palazzo+Las+Vegas,+Las+Vegas,+NV", mapsDestination="Caesars+Palace+Las+Vegas,+3570+Las+Vegas+Blvd+S,+Las+Vegas,+NV", measuredOn="2026-11-17"),
    dict(hotel="palazzo", venue="horseshoe", minutes=21, miles="0.9",
         note="Maps walking estimate, Las Vegas Blvd S.", via="Las Vegas Blvd S", source="https://www.venetianlasvegas.com/resort/casino/poker.html",
         mapsOrigin="The+Palazzo+Las+Vegas,+Las+Vegas,+NV", mapsDestination="Horseshoe+Las+Vegas+Hotel+%26+Casino,+3645+W+Flamingo+Rd,+Las+Vegas,+NV+89169", measuredOn="2026-11-17"),
    dict(hotel="wynn", venue="bellagio", minutes=32, miles="1.4",
         note="Maps walking estimate, Las Vegas Blvd S.", via="Las Vegas Blvd S", source="https://www.wynnlasvegas.com/casino/poker",
         mapsOrigin="Wynn+Las+Vegas,+3131+Las+Vegas+Blvd+S,+Las+Vegas,+NV+89109", mapsDestination="Bellagio+Hotel+%26+Casino,+Las+Vegas,+NV", measuredOn="2026-11-17"),
    dict(hotel="wynn", venue="mgm", minutes=48, miles="2.1",
         note="Maps walking estimate, Las Vegas Blvd S.", via="Las Vegas Blvd S", source="https://www.wynnlasvegas.com/casino/poker",
         mapsOrigin="Wynn+Las+Vegas,+3131+Las+Vegas+Blvd+S,+Las+Vegas,+NV+89109", mapsDestination="MGM+Grand+Hotel+%26+Casino,+Las+Vegas,+NV", measuredOn="2026-11-17"),
    dict(hotel="wynn", venue="aria", minutes=44, miles="1.9",
         note="Maps walking estimate, Las Vegas Blvd S.", via="Las Vegas Blvd S", source="https://www.wynnlasvegas.com/casino/poker",
         mapsOrigin="Wynn+Las+Vegas,+3131+Las+Vegas+Blvd+S,+Las+Vegas,+NV+89109", mapsDestination="ARIA+Resort+%26+Casino,+Las+Vegas,+NV", measuredOn="2026-11-17"),
    dict(hotel="wynn", venue="caesars", minutes=23, miles="1.0",
         note="Maps walking estimate, Las Vegas Blvd S.", via="Las Vegas Blvd S", source="https://www.wynnlasvegas.com/casino/poker",
         mapsOrigin="Wynn+Las+Vegas,+3131+Las+Vegas+Blvd+S,+Las+Vegas,+NV+89109", mapsDestination="Caesars+Palace+Las+Vegas,+3570+Las+Vegas+Blvd+S,+Las+Vegas,+NV", measuredOn="2026-11-17"),
    dict(hotel="wynn", venue="horseshoe", minutes=29, miles="1.3",
         note="Maps walking estimate, Las Vegas Blvd S.", via="Las Vegas Blvd S", source="https://www.wynnlasvegas.com/casino/poker",
         mapsOrigin="Wynn+Las+Vegas,+3131+Las+Vegas+Blvd+S,+Las+Vegas,+NV+89109", mapsDestination="Horseshoe+Las+Vegas+Hotel+%26+Casino,+3645+W+Flamingo+Rd,+Las+Vegas,+NV+89169", measuredOn="2026-11-17"),
    dict(hotel="bellagio", venue="wynn", minutes=38, miles="1.7",
         note="Maps walking estimate to Encore, where the Wynn poker room is located, via Las Vegas Blvd S.", via="Las Vegas Blvd S", source="https://bellagio.mgmresorts.com/en/casino/poker.html",
         mapsOrigin="Bellagio+Hotel+%26+Casino,+Las+Vegas,+NV", mapsDestination="Encore+Las+Vegas,+3131+Las+Vegas+Blvd+S,+Las+Vegas,+NV+89109", measuredOn="2026-11-17"),
    dict(hotel="bellagio", venue="mgm", minutes=20, miles="0.9",
         note="Maps walking estimate, Bellagio Dr.", via="Bellagio Dr", source="https://bellagio.mgmresorts.com/en/casino/poker.html",
         mapsOrigin="Bellagio+Hotel+%26+Casino,+Las+Vegas,+NV", mapsDestination="MGM+Grand+Hotel+%26+Casino,+Las+Vegas,+NV", measuredOn="2026-11-17"),
    dict(hotel="bellagio", venue="aria", minutes=12, miles="0.5",
         note="Maps walking estimate, The Cosmopolitan Service Rd.", via="The Cosmopolitan Service Rd", source="https://bellagio.mgmresorts.com/en/casino/poker.html",
         mapsOrigin="Bellagio+Hotel+%26+Casino,+Las+Vegas,+NV", mapsDestination="ARIA+Resort+%26+Casino,+Las+Vegas,+NV", measuredOn="2026-11-17"),
    dict(hotel="bellagio", venue="caesars", minutes=12, miles="0.5",
         note="Maps walking estimate, Las Vegas Blvd Overpass.", via="Las Vegas Blvd Overpass", source="https://bellagio.mgmresorts.com/en/casino/poker.html",
         mapsOrigin="Bellagio+Hotel+%26+Casino,+Las+Vegas,+NV", mapsDestination="Caesars+Palace+Las+Vegas,+3570+Las+Vegas+Blvd+S,+Las+Vegas,+NV", measuredOn="2026-11-17"),
    dict(hotel="bellagio", venue="horseshoe", minutes=11, miles="0.5",
         note="Maps walking estimate, Bellagio Dr.", via="Bellagio Dr", source="https://bellagio.mgmresorts.com/en/casino/poker.html",
         mapsOrigin="Bellagio+Hotel+%26+Casino,+Las+Vegas,+NV", mapsDestination="Horseshoe+Las+Vegas+Hotel+%26+Casino,+3645+W+Flamingo+Rd,+Las+Vegas,+NV+89169", measuredOn="2026-11-17"),
    dict(hotel="mgm", venue="wynn", minutes=53, miles="2.3",
         note="Maps walking estimate to Encore, where the Wynn poker room is located, via Las Vegas Blvd S.", via="Las Vegas Blvd S", source="https://mgmgrand.mgmresorts.com/en/casino/poker-tables.html",
         mapsOrigin="MGM+Grand+Hotel+%26+Casino,+Las+Vegas,+NV", mapsDestination="Encore+Las+Vegas,+3131+Las+Vegas+Blvd+S,+Las+Vegas,+NV+89109", measuredOn="2026-11-17"),
    dict(hotel="mgm", venue="bellagio", minutes=20, miles="0.9",
         note="Maps walking estimate, Bellagio Dr.", via="Bellagio Dr", source="https://mgmgrand.mgmresorts.com/en/casino/poker-tables.html",
         mapsOrigin="MGM+Grand+Hotel+%26+Casino,+Las+Vegas,+NV", mapsDestination="Bellagio+Hotel+%26+Casino,+Las+Vegas,+NV", measuredOn="2026-11-17"),
    dict(hotel="mgm", venue="aria", minutes=16, miles="0.7",
         note="Maps walking estimate, W Aria Pl.", via="W Aria Pl", source="https://mgmgrand.mgmresorts.com/en/casino/poker-tables.html",
         mapsOrigin="MGM+Grand+Hotel+%26+Casino,+Las+Vegas,+NV", mapsDestination="ARIA+Resort+%26+Casino,+Las+Vegas,+NV", measuredOn="2026-11-17"),
    dict(hotel="mgm", venue="caesars", minutes=28, miles="1.2",
         note="Maps walking estimate, Las Vegas Blvd Overpass.", via="Las Vegas Blvd Overpass", source="https://mgmgrand.mgmresorts.com/en/casino/poker-tables.html",
         mapsOrigin="MGM+Grand+Hotel+%26+Casino,+Las+Vegas,+NV", mapsDestination="Caesars+Palace+Las+Vegas,+3570+Las+Vegas+Blvd+S,+Las+Vegas,+NV", measuredOn="2026-11-17"),
    dict(hotel="mgm", venue="horseshoe", minutes=22, miles="1.0",
         note="Maps walking estimate, Ballys Dr.", via="Ballys Dr", source="https://mgmgrand.mgmresorts.com/en/casino/poker-tables.html",
         mapsOrigin="MGM+Grand+Hotel+%26+Casino,+Las+Vegas,+NV", mapsDestination="Horseshoe+Las+Vegas+Hotel+%26+Casino,+3645+W+Flamingo+Rd,+Las+Vegas,+NV+89169", measuredOn="2026-11-17"),
    dict(hotel="caesars", venue="wynn", minutes=29, miles="1.3",
         note="Maps walking estimate to Encore, where the Wynn poker room is located, via Las Vegas Blvd S.", via="Las Vegas Blvd S", source="https://www.caesars.com/las-vegas/explore/casino/poker-tournaments-las-vegas-strip",
         mapsOrigin="Caesars+Palace+Las+Vegas,+3570+Las+Vegas+Blvd+S,+Las+Vegas,+NV", mapsDestination="Encore+Las+Vegas,+3131+Las+Vegas+Blvd+S,+Las+Vegas,+NV+89109", measuredOn="2026-11-17"),
    dict(hotel="caesars", venue="bellagio", minutes=12, miles="0.5",
         note="Maps walking estimate, Las Vegas Blvd Overpass.", via="Las Vegas Blvd Overpass", source="https://www.caesars.com/las-vegas/explore/casino/poker-tournaments-las-vegas-strip",
         mapsOrigin="Caesars+Palace+Las+Vegas,+3570+Las+Vegas+Blvd+S,+Las+Vegas,+NV", mapsDestination="Bellagio+Hotel+%26+Casino,+Las+Vegas,+NV", measuredOn="2026-11-17"),
    dict(hotel="caesars", venue="mgm", minutes=28, miles="1.2",
         note="Maps walking estimate, Las Vegas Blvd Overpass.", via="Las Vegas Blvd Overpass", source="https://www.caesars.com/las-vegas/explore/casino/poker-tournaments-las-vegas-strip",
         mapsOrigin="Caesars+Palace+Las+Vegas,+3570+Las+Vegas+Blvd+S,+Las+Vegas,+NV", mapsDestination="MGM+Grand+Hotel+%26+Casino,+Las+Vegas,+NV", measuredOn="2026-11-17"),
    dict(hotel="caesars", venue="aria", minutes=24, miles="1.0",
         note="Maps walking estimate, Las Vegas Blvd Overpass.", via="Las Vegas Blvd Overpass", source="https://www.caesars.com/las-vegas/explore/casino/poker-tournaments-las-vegas-strip",
         mapsOrigin="Caesars+Palace+Las+Vegas,+3570+Las+Vegas+Blvd+S,+Las+Vegas,+NV", mapsDestination="ARIA+Resort+%26+Casino,+Las+Vegas,+NV", measuredOn="2026-11-17"),
    dict(hotel="caesars", venue="horseshoe", minutes=10, miles="0.4",
         note="Maps walking estimate, Las Vegas Blvd Overpass.", via="Las Vegas Blvd Overpass", source="https://www.caesars.com/las-vegas/explore/casino/poker-tournaments-las-vegas-strip",
         mapsOrigin="Caesars+Palace+Las+Vegas,+3570+Las+Vegas+Blvd+S,+Las+Vegas,+NV", mapsDestination="Horseshoe+Las+Vegas+Hotel+%26+Casino,+3645+W+Flamingo+Rd,+Las+Vegas,+NV+89169", measuredOn="2026-11-17"),
    dict(hotel="horseshoe", venue="wynn", minutes=35, miles="1.5",
         note="Maps walking estimate to Encore, where the Wynn poker room is located, via Las Vegas Blvd S.", via="Las Vegas Blvd S", source="https://www.caesars.com/las-vegas/explore/casino/poker-tournaments-las-vegas-strip",
         mapsOrigin="Horseshoe+Las+Vegas+Hotel+%26+Casino,+3645+W+Flamingo+Rd,+Las+Vegas,+NV+89169", mapsDestination="Encore+Las+Vegas,+3131+Las+Vegas+Blvd+S,+Las+Vegas,+NV+89109", measuredOn="2026-11-17"),
    dict(hotel="horseshoe", venue="bellagio", minutes=11, miles="0.5",
         note="Maps walking estimate, Bellagio Dr.", via="Bellagio Dr", source="https://www.caesars.com/las-vegas/explore/casino/poker-tournaments-las-vegas-strip",
         mapsOrigin="Horseshoe+Las+Vegas+Hotel+%26+Casino,+3645+W+Flamingo+Rd,+Las+Vegas,+NV+89169", mapsDestination="Bellagio+Hotel+%26+Casino,+Las+Vegas,+NV", measuredOn="2026-11-17"),
    dict(hotel="horseshoe", venue="mgm", minutes=23, miles="1.0",
         note="Maps walking estimate, Ballys Dr.", via="Ballys Dr", source="https://www.caesars.com/las-vegas/explore/casino/poker-tournaments-las-vegas-strip",
         mapsOrigin="Horseshoe+Las+Vegas+Hotel+%26+Casino,+3645+W+Flamingo+Rd,+Las+Vegas,+NV+89169", mapsDestination="MGM+Grand+Hotel+%26+Casino,+Las+Vegas,+NV", measuredOn="2026-11-17"),
    dict(hotel="horseshoe", venue="aria", minutes=18, miles="0.8",
         note="Maps walking estimate, Ballys Dr.", via="Ballys Dr", source="https://www.caesars.com/las-vegas/explore/casino/poker-tournaments-las-vegas-strip",
         mapsOrigin="Horseshoe+Las+Vegas+Hotel+%26+Casino,+3645+W+Flamingo+Rd,+Las+Vegas,+NV+89169", mapsDestination="ARIA+Resort+%26+Casino,+Las+Vegas,+NV", measuredOn="2026-11-17"),
    dict(hotel="horseshoe", venue="caesars", minutes=10, miles="0.4",
         note="Maps walking estimate, Las Vegas Blvd Overpass.", via="Las Vegas Blvd Overpass", source="https://www.caesars.com/las-vegas/explore/casino/poker-tournaments-las-vegas-strip",
         mapsOrigin="Horseshoe+Las+Vegas+Hotel+%26+Casino,+3645+W+Flamingo+Rd,+Las+Vegas,+NV+89169", mapsDestination="Caesars+Palace+Las+Vegas,+3570+Las+Vegas+Blvd+S,+Las+Vegas,+NV", measuredOn="2026-11-17"),
    dict(hotel="aria", venue="wynn", minutes=48, miles="2.1",
         note="Maps walking estimate to Encore, where the Wynn poker room is located, via Las Vegas Blvd S.", via="Las Vegas Blvd S", source="https://aria.mgmresorts.com/en/casino/poker.html",
         mapsOrigin="ARIA+Resort+%26+Casino,+Las+Vegas,+NV", mapsDestination="Encore+Las+Vegas,+3131+Las+Vegas+Blvd+S,+Las+Vegas,+NV+89109", measuredOn="2026-11-17"),
    dict(hotel="aria", venue="bellagio", minutes=12, miles="0.5",
         note="Maps walking estimate, The Cosmopolitan Service Rd.", via="The Cosmopolitan Service Rd", source="https://aria.mgmresorts.com/en/casino/poker.html",
         mapsOrigin="ARIA+Resort+%26+Casino,+Las+Vegas,+NV", mapsDestination="Bellagio+Hotel+%26+Casino,+Las+Vegas,+NV", measuredOn="2026-11-17"),
    dict(hotel="aria", venue="mgm", minutes=15, miles="0.7",
         note="Maps walking estimate, W Aria Pl.", via="W Aria Pl", source="https://aria.mgmresorts.com/en/casino/poker.html",
         mapsOrigin="ARIA+Resort+%26+Casino,+Las+Vegas,+NV", mapsDestination="MGM+Grand+Hotel+%26+Casino,+Las+Vegas,+NV", measuredOn="2026-11-17"),
    dict(hotel="aria", venue="caesars", minutes=24, miles="1.0",
         note="Maps walking estimate, Las Vegas Blvd Overpass.", via="Las Vegas Blvd Overpass", source="https://aria.mgmresorts.com/en/casino/poker.html",
         mapsOrigin="ARIA+Resort+%26+Casino,+Las+Vegas,+NV", mapsDestination="Caesars+Palace+Las+Vegas,+3570+Las+Vegas+Blvd+S,+Las+Vegas,+NV", measuredOn="2026-11-17"),
    dict(hotel="aria", venue="horseshoe", minutes=18, miles="0.8",
         note="Maps walking estimate, Ballys Dr.", via="Ballys Dr", source="https://aria.mgmresorts.com/en/casino/poker.html",
         mapsOrigin="ARIA+Resort+%26+Casino,+Las+Vegas,+NV", mapsDestination="Horseshoe+Las+Vegas+Hotel+%26+Casino,+3645+W+Flamingo+Rd,+Las+Vegas,+NV+89169", measuredOn="2026-11-17"),
]
