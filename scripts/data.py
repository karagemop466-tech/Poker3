"""Hand-entered reference data. Only values confirmed from fetched official pages.

Tournament rows are NOT entered here. They come from data/*.json, which
scripts/parse_official.py creates from the verbatim official text in raw/.

None = not verified from an official source. The site shows these as blank,
flagged "unverified". Nothing is estimated.
"""

ACCESS_DATE = "2026-11-16"

VEN_SCHED = "https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/dse-nov-2026-schedule.pdf"
VEN_EVENT_PAGE = "https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html"
VEN_STRUCT = "https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_{n}.pdf"
WPT_SCHED = "https://cdn.wynnresorts.com/image/upload/v1757097329/visitwynn_pdfs_files/Poker/WPT/WPT_World_Championship_Schedule.pdf"
WPT_STRUCT = "https://cdn.wynnresorts.com/image/upload/v1750864036/visitwynn_pdfs_files/Poker/WPT/WPT_World_Championship_Structures.pdf"
WYNN_DAILY_POSTER = "https://cdn.wynnresorts.com/image/upload/v1752011166/visitwynn_pdfs_files/Poker/Daily%20Tournaments/poker-daily-tournament-poster.pdf"

# Every key here is a source that was fetched during this session (or a page
# whose URL appeared in a fetched page's navigation, noted in the label).
SRC = {
    "ven_sched": ("Venetian official DeepStack Extravaganza IV schedule (PDF, fetched)", VEN_SCHED),
    "ven_event": ("Venetian official DSE IV event page (fetched)", VEN_EVENT_PAGE),
    "ven_fee": ("Venetian official resort fee page (fetched)", "https://www.venetianlasvegas.com/resort/resort-fee.html"),
    "ven_parking": ("Venetian official parking and transportation FAQ (fetched)", "https://www.venetianlasvegas.com/resort/maps-and-parking/parking-transportation-faqs.html"),
    "ven_contact": ("Venetian official contact page (fetched)", "https://www.venetianlasvegas.com/resort/contact.html"),
    "wynn_schedule": ("Wynn official WPT World Championship schedule (PDF, fetched)", WPT_SCHED),
    "wynn_struct": ("Wynn official WPT World Championship structures (PDF, first 3 of 8 chunks read)", WPT_STRUCT),
    "wynn_daily": ("Wynn official daily tournaments poster (PDF, fetched)", WYNN_DAILY_POSTER),
    "wynn_poker": ("Wynn official poker room page (fetched)", "https://www.wynnlasvegas.com/casino/poker"),
    "wynn_terms": ("Wynn official special-offer terms: resort fee $50 before Jan 15 2025, $55 on or after (fetched)", "https://www.wynnlasvegas.com/terms-and-conditions/849986"),
    "wynn_contact": ("Wynn official contact information (fetched in an earlier session)", "https://www.wynnlasvegas.com/about-us/contact-information"),
    "rw_faq": ("Resorts World Las Vegas official FAQ: resort fee $55 plus tax; self-parking $21 (fetched)", "https://www.rwlasvegas.com/faq/"),
    "rw_offer": ("Resorts World Las Vegas official 'All Resort, No Fees' offer terms (fetched)", "https://www.rwlasvegas.com/offers/all-resort-no-fees/"),
    "rw_poker": ("Resorts World Las Vegas official poker page (fetched; no schedule content)", "https://www.rwlasvegas.com/poker/"),
    "wsop": ("WSOP official tournament schedule (fetched)", "https://www.wsop.com/schedule/"),
    "repo": ("Repository karagemop466-tech/Poker3 on GitHub", "https://github.com/karagemop466-tech/Poker3"),
    "clark_tax": ("Clark County transient lodging tax page (returned 404 when fetched)", "https://www.clarkcountynv.gov/government/departments/finance/transient-lodging-tax.php"),
}

# Venetian structure sheets opened and read (see scripts/parse_official.py for event mapping).
VEN_STRUCT_OPENED = ["1", "2", "7", "10", "12", "18", "19"]

# ------------------------------------------------------------- Wynn daily (official poster, undated)
# (time, event, buy-in, guarantee). Poster has no calendar dates.
WYNN_DAILY = [
    ("Monday to Thursday", "12:00 PM", "No Limit Hold'em", 200, 10000),
    ("Friday", "12:00 PM", "No Limit Hold'em Rebuy", 240, 40000),
    ("Saturday", "12:00 PM", "No Limit Hold'em", 200, 25000),
    ("Sunday", "12:00 PM", "No Limit Hold'em", 200, 25000),
    ("Nightly", "6:00 PM", "No Limit Hold'em", 160, 10000),
]

# ------------------------------------------------------------- hotels (official values only)
HOTELS = [
    {
        "name": "The Venetian Resort Las Vegas",
        "address": "3355 Las Vegas Blvd S, Las Vegas, NV 89109",
        "address_src": "ven_contact",
        "poker": "DeepStack Extravaganza IV, listed on the Venetian's official site and schedule",
        "poker_src": "ven_sched",
        "walk": None,
        "walk_note": "Minutes to the poker room not measured. The poker-room location within the Venetian/Palazzo campus is not confirmed (see flag F16).",
        "walk_src": None,
        "resort_fee": 55,
        "fee_text": "$55 plus tax per night, payable upon check-in (official).",
        "fee_src": "ven_fee",
        "parking": "$20/day for registered hotel guests; $20 Mon to Thu and $25 Fri to Sun for non-guests (official FAQ)",
        "parking_src": "ven_parking",
    },
    {
        "name": "Wynn Las Vegas",
        "address": "3131 Las Vegas Blvd S, Las Vegas, NV 89109",
        "address_src": "wynn_contact",
        "poker": "WPT World Championship (Nov 27 to Dec 21, 2026), titled 'at Wynn Las Vegas' on the official poker page",
        "poker_src": "wynn_schedule",
        "walk": None,
        "walk_note": "Walking minutes not measured. The poker-room location FAQ answers on the official page were not visible in the fetched text (flag F16).",
        "walk_src": None,
        "resort_fee": 55,
        "fee_text": "$55 plus tax per room night for bookings on or after Jan 15, 2025 (official terms). The same terms page lists $50 for bookings made before that date, which does not apply to new bookings (flag F01).",
        "fee_src": "wynn_terms",
        "parking": None,
        "parking_src": None,
    },
    {
        "name": "Resorts World Las Vegas",
        "address": None,
        "address_src": None,
        "poker": "No official Resorts World tournament schedule retrieved (flag F14)",
        "poker_src": "rw_poker",
        "walk": None,
        "walk_note": "Not verified (no tournament venue data).",
        "walk_src": None,
        "resort_fee": 55,
        "fee_text": "$55 plus tax per night (official FAQ). Official offer: fee waived on select dates through Dec 28, 2026; blackout dates may apply; room tax still applies; $150 per room per night incidental deposit at check-in (official offer terms).",
        "fee_src": "rw_faq",
        "parking": "$21 per 24 hours self-parking; complimentary for Nevada plates and certain Genting Rewards tiers (official FAQ and offer page)",
        "parking_src": "rw_faq",
    },
]

OFFICIAL_CONTACTS = {
    "venetian_hotel": ("Venetian hotel", "702-414-1000", "ven_contact"),
    "wynn_main": ("Wynn Las Vegas main", "(702) 770-7000", "wynn_contact"),
    "wynn_poker": ("Wynn poker room (printed on official WPT schedule)", "(702) 770-7654", "wynn_schedule"),
}
