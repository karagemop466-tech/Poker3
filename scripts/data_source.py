"""Assembles site/data.json from the source modules.

Run:  python3 scripts/data_source.py
"""
import datetime
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import data_venetian as V  # noqa: E402
import data_venues as N  # noqa: E402
import data_hotels as H  # noqa: E402

ASOF = "2026-11-16"
RECHECKED = "2026-11-17"
# Third live pass: the official schedule pages and hotel terms were read again on 2026-11-19
# (session arena/9b858e66-poker3, through the platform page reader - the build sandbox's own
# egress to the venue hosts still fails, flag F40).  It is kept as its own date so a row can
# say which pass last read it instead of inheriting a blanket "today".
LAST_PASS_2026_11_19 = "2026-11-19"
RECHECK_FROM, RECHECK_TO = "2026-11-16", "2026-12-23"
DSE_NOV_URL = "https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html"
TODAY = LAST_PASS_2026_11_19
# Quoted from the official poker-suite rate page (re-read 2026-11-16, cited on every hotel row).
RATE_QUALIFICATION_TEXT = ("six hours of active live cash gameplay or buy in to a $300 or higher tournament for each "
                           "night stayed")          # snapshot date of the live re-check; drives past / today / upcoming
CHECKED_TODAY = RECHECKED     # rows whose official page was re-read on TODAY

# Live re-read of the 13 trip-window rows and their seven structure sheets (2026-11-17).
# The record is the single source for those dates; tests/test_reread_2026_11_17.py checks
# the published rows against it.
REREAD = json.loads((ROOT / "research" / "reread_2026-11-17.json").read_text(encoding="utf-8"))
REREAD_DATE = REREAD["retrievedOn"]
REREAD_ROWS = {(r["date"], r["event"]) for r in REREAD["rows"]}
REREAD_SHEETS = set(REREAD["sheets"].keys())
WPT_REREAD = REREAD["wpt"]
WPT_ROWS = {r["id"]: r for r in WPT_REREAD["rows"]}

# ---------------------------------------------------------------------------
# Live re-verification record (session arena/52e02b46-poker3, 2026-11-17).
#
# On 2026-11-17 every official page and PDF behind the rows below was fetched
# again and read.  ASOF stays 2026-11-16 because that is the date the underlying
# values were originally transcribed; VERIFIED_ON records the later date on which
# a person re-read the same source and found it unchanged.  The two dates are
# kept apart on purpose so "when was this value read" and "when was it last
# confirmed still true" never get conflated.
# ---------------------------------------------------------------------------
from trip_cost import published_model  # noqa: E402  (same directory as this module)

VERIFIED_ON = "2026-11-17"

VERIFIED_SOURCES_2026_11_17 = [
    dict(
        name="DeepStack Extravaganza IV official series schedule PDF (Nov 16 - Dec 23, 2026)",
        url="https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/dse-nov-2026-schedule.pdf",
        type="official schedule PDF",
        checked=VERIFIED_ON,
        what="All 44 published rows between 2026-11-16 and 2026-12-06 were compared with this PDF on date, start time, "
             "REG CLOSES, guarantee, starting chips and level length. 44 of 44 agree. The transcription is kept in "
             "site/data/venetian_pdf_rows.json and re-checked by scripts/verify_transcription.py.",
    ),
    dict(
        name="Venetian poker-room suite rates and 2026 play requirements",
        url="https://www.venetianlasvegas.com/resort/casino/poker/suite-rates.html",
        type="official rate page",
        checked=VERIFIED_ON,
        what="$119 / $209 starting rates, the $55 resort fee per night, single/double occupancy in a Luxury King Suite, and "
             "the six-hours-of-live-cash-play-or-$300-tournament-entry requirement per night stayed.",
    ),
    dict(
        name="Venetian resort fee page",
        url="https://www.venetianlasvegas.com/resort/resort-fee.html",
        type="official fee page",
        checked=VERIFIED_ON,
        what="A daily Resort Fee of $55 plus tax per night, payable upon check-in.",
    ),
    dict(
        name="Venetian hotel terms: 13.38% Clark County room tax, parking, check-in and incidentals",
        url="https://www.venetianlasvegas.com/legal/hotel-terms-and-conditions.html",
        type="official terms",
        checked=VERIFIED_ON,
        what="Daily rates exclude the 13.38% Clark County Room Tax; registered-guest self-parking is $20/day seven days a "
             "week, valet $40/day; $150 per night incidental authorisation; check-in 3:00 PM to 11:59 PM, check-out 11:00 AM.",
    ),
    dict(
        name="Bellagio hotel terms: $55 resort fee, 72-hour cancellation, taxes on the fee",
        url="https://bellagio.mgmresorts.com/en/terms-and-conditions.html",
        type="official terms",
        checked=VERIFIED_ON,
        what="A daily resort fee of $55.00 plus applicable tax; lodging taxes apply to the basic room rate and to the resort "
             "fee; first night refundable with 72 hours notice; $150 per day incidental authorisation.",
    ),
    dict(
        name="Wynn general hotel terms: $55 resort fee, 48-hour cancellation, parking",
        url="https://www.wynnlasvegas.com/terms-and-conditions/850070",
        type="official terms",
        checked=VERIFIED_ON,
        what="A daily resort fee of $55 plus tax; cancellations at least 48 hours before arrival or the deposit is "
             "forfeited; self-parking complimentary for registered guests, $25/day for non-registered guests, valet $40/day; "
             "check-in after 3 p.m., check-out before 12 p.m.",
    ),
    dict(
        name="Wynn WPT World Championship schedule PDF (Nov 27 - Dec 21, 2026)",
        url="https://cdn.wynnresorts.com/image/upload/v1757097329/visitwynn_pdfs_files/Poker/WPT/WPT_World_Championship_Schedule.pdf",
        type="official schedule PDF",
        checked=VERIFIED_ON,
        what="Buy-in, guarantee, starting chips and level length for every WPT row already published, plus the note that "
             "registration for each event opens four hours before the scheduled start.",
    ),
    dict(
        name="Bellagio Saturday NLH structure PDF",
        url="https://assets.contentstack.io/v3/assets/bltc6ce635bc4868eb2/blt6d47974bf5a7d9b6/6af491a391a6e8e4230c9e07/mgm-bellagio-poker-saturdays-$1000-nlh.pdf",
        type="official structure PDF",
        checked=VERIFIED_ON,
        what="Re-read for flag F02: the header prints 'NLH $1100 BUY-IN', rule 07 prints 'Of the $600 Buy-in', and rule 09 "
             "sells a voluntary $40 staff gratuity that grants an extra 20,000 chips. $1,100, $600 and $1,040 (with the "
             "gratuity) are therefore three different amounts for the same event.",
    ),
]

# Facts confirmed live on 2026-11-17 that the earlier build left blank.
LIVE_FACTS_2026_11_17 = dict(
    verifiedOn=VERIFIED_ON,
    venetianParkingPerNight=20.0,
    venetianParkingSource="https://www.venetianlasvegas.com/legal/hotel-terms-and-conditions.html",
    venetianParkingExcerpt="The daily fee for registered hotel guests is $20/day, seven days a week.",
    venetianCheckInOut="Check-in 3:00 PM to 11:59 PM; check-out 11:00 AM.",
    venetianCancellation=("A deposit covering the suite, fee and tax is billed when the reservation is confirmed; prepaid "
                          "offers are non-cancellable and non-refundable; early checkout costs $100 plus tax; arriving after "
                          "11:59 PM without notice cancels the reservation and forfeits the first night."),
    wynnCheckInOut="Check-in after 3 p.m.; check-out before 12 p.m.",
    bellagioIncidental="$150 incidental authorisation per day at check-in.",
    bellagioCancellation=("The first night's deposit is refundable if Room Reservations receives notice at least 72 hours "
                          "before arrival; later cancellations and no-shows forfeit the first night."),
    wynnRegistrationNote="Registration for each WPT event opens four hours before the scheduled start (WPT general terms).",
    wynnRegistrationSource="https://cdn.wynnresorts.com/image/upload/v1750864036/visitwynn_pdfs_files/Poker/WPT/WPT_World_Championship_Structures.pdf",
    wynnFeeNote=("The WPT schedule PDF states that a complete listing of house and staff fees is on wynnpoker.com or the "
                 "event structure sheets; the schedule itself does not print the fee for each row."),
    bellagioSaturdayConflict=("Bellagio's Saturday page title says $1,000, the structure PDF header says $1,100 and rule 07 of "
                              "the same PDF says $600; rule 09 adds a voluntary $40 gratuity that buys 20,000 extra chips. The "
                              "event is excluded from the single-entry path for all three reasons."),
)

# Aliases used by the per-row re-read bookkeeping below. LAST_PASS is ASOF, so a row or
# source that was not re-read today keeps the base snapshot date. RECHECKED_TODAY is the
# scheduleUrl fragment of the rows that scripts/verify_live_official.py compares line by
# line against a fresh capture of the official page.
LAST_PASS = ASOF
RECHECKED_TODAY = "dse-nov-2026"

# --------------------------------------------------------------- time helpers
_CLOCK = re.compile(r"(\d{1,2}):(\d{2})\s*([ap])\.?m\.?", re.I)


def clock_minutes(text):
    """Return minutes past midnight for the first clock time in text, or None."""
    if not text:
        return None
    m = _CLOCK.search(text)
    if not m:
        return None
    hh, mm, ap = int(m.group(1)), int(m.group(2)), m.group(3).lower()
    if hh == 12:
        hh = 0
    if ap == "p":
        hh += 12
    return hh * 60 + mm


def fmt_clock(minutes):
    if minutes is None:
        return ""
    minutes = int(round(minutes))
    hh, mm = divmod(minutes % 1440, 60)
    ampm = "AM" if hh < 12 else "PM"
    hh12 = hh % 12 or 12
    return f"{hh12}:{mm:02d} {ampm}"


def late_cutoff_times(text):
    """Every clock time printed in a late-registration clause, in printed order."""
    out = []
    for m in _CLOCK.finditer(text or ""):
        hh, mm, ap = int(m.group(1)), int(m.group(2)), m.group(3).lower()
        if hh == 12:
            hh = 0
        if ap == "p":
            hh += 12
        out.append(hh * 60 + mm)
    return out


def select_cutoff(start_min, late_text):
    """Pick the printed cut-off that belongs to this row's start time.

    A few NYE sheets print one late-registration clause covering two different
    start flights, for example "6 levels + break (~5:25 PM or ~8:25 PM)".
    Taking the first clock time blindly puts a 5:25 PM cut-off on the 6:10 PM
    row, which closes registration before that event begins, and the estimate
    built on it is meaningless.

    Both times are printed on the sheet, so this disambiguates published values
    rather than inventing one: when more than one time is printed, the earliest
    one still falling after this row's start is the one that belongs to it. If
    no printed time falls after the start, the sheet cannot be matched to this
    row and no cut-off is published, so the row falls back to the documented
    six-hour planning assumption.
    """
    times = late_cutoff_times(late_text)
    if not times:
        return None
    if len(times) == 1 or start_min is None:
        return times[0]
    after = [t for t in times if t > start_min]
    return min(after) if after else None

# DeepStack Extravaganza IV rows whose late-registration cut-off is published as a
# clock time on the official series schedule PDF but not on their structure sheet.
#
# The series PDF is the only official place that prints REG CLOSES as a clock time,
# and it prints one per row. Sheet 25 ($260 Turbo Milestone Satellite) covers three
# rows that start at three different times, and the sheet itself says only "6 levels",
# so a single sheet-level value cannot carry the printed cut-off for all three.
# These are the values printed in the REG CLOSES column, applied per row.
DSE_REG_CLOSES = {
    ("2026-12-11", "45"): "6 levels (REG CLOSES 9:55 PM)",
    ("2026-12-12", "46"): "6 levels (REG CLOSES 10:55 AM)",
    ("2026-12-12", "48"): "6 levels (REG CLOSES 1:55 PM)",
}


def session_estimate(start_min, late_text, level_min):
    """Estimate a session length from printed data only.

    When the structure sheet prints the late-registration cut-off clock time, the
    session cannot end before that point, so the estimate is the cut-off plus two
    more levels (one level and one break).  With no printed cut-off time the
    documented six-hour planning assumption is used.
    """
    cutoff = select_cutoff(start_min, late_text)
    if cutoff is None or start_min is None:
        return 360, "", None
    if cutoff <= start_min:
        cutoff += 1440
    level = level_min if isinstance(level_min, int) and level_min else 30
    length = (cutoff - start_min) + (2 * level) + 15
    return length, fmt_clock(cutoff), cutoff


def is_continuation(name: str) -> bool:
    """True when a schedule row is a resumption of a field that has already closed.

    A "Day 2 Restart", a "Day 3" row or a "Final Table" row resumes a field that
    was seeded on an earlier day, so registration is closed and no official
    finish time is published for the row.

    A starting flight is NOT a continuation even when its payout clause mentions
    a later day: "$250 No Limit Hold'em 1A $75K GTD - Day 1 payouts with 5%
    advancing to Day 2" is flight 1A.  Only the part of the name before the
    first " - " separator is tested for a day number, so a trailing payout
    clause cannot turn a flight into a restart.  "(2Day)" is also not matched,
    because there is no word boundary between the digit and "Day".
    """
    n = (name or "").lower()
    if "restart" in n or "final table" in n:
        return True
    head = n.split(" - ", 1)[0]
    return bool(re.search(r"\bday\s*[2-9]\b", head))


VENUES = [
    dict(id="venetian", name="The Venetian Resort", pokerRoom="Venetian poker room",
         page="https://www.venetianlasvegas.com/resort/casino/poker.html",
         series="DeepStack Extravaganza IV (Nov 16 - Dec 23, 2026) and DeepStack Extravaganza NYE (Dec 24, 2026 - Jan 10, 2027)",
         schedule="https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html",
         hotels=["venetian", "palazzo"],
         note=("Poker room is on the resort property; the poker-suite rate applies to The Venetian and The Palazzo. "
               "The official series page states 'More than $3.6 Million in guaranteed tournament prize pools' for "
               "DeepStack Extravaganza IV.")),
    dict(id="wynn", name="Wynn Las Vegas", pokerRoom="Wynn poker room, located in Encore at Wynn Las Vegas",
         page="https://www.wynnlasvegas.com/casino/poker",
         series="WPT World Championship (Nov 27 - Dec 21, 2026), Wynn Signature Series (Jan 11-24, 2027), daily tournaments",
         schedule="https://cdn.wynnresorts.com/image/upload/v1757097329/visitwynn_pdfs_files/Poker/WPT/WPT_World_Championship_Schedule.pdf",
         hotels=["wynn", "encore"], note="Daily tournaments are suspended during Wynn Signature, Wynn Millions and Classic series."),
    dict(id="bellagio", name="Bellagio", pokerRoom="Bellagio poker room, northside of casino next to Sportsbook",
         page="https://bellagio.mgmresorts.com/en/casino/poker.html",
         series="Weekly Friday $600 NLH, Saturday NLH, Sunday $400 H.O.R.S.E., nightly PLO Double Board Bomb Pot",
         schedule="https://bellagio.mgmresorts.com/en/casino/poker.html",
         hotels=["bellagio"], note="Recurring weekly events; no date-specific schedule is published."),
    dict(id="mgm", name="MGM Grand", pokerRoom="MGM Grand poker room",
         page="https://mgmgrand.mgmresorts.com/en/casino/poker-tables.html",
         series="Daily No Limit Hold'em tournaments at 11:10 AM, 7:10 PM and 11:10 PM",
         schedule="https://assets.contentstack.io/v3/assets/bltc6ce635bc4868eb2/blt5f25277b8918da08/mgm-grand-casino-poker-tournament_schedule.pdf",
         hotels=["mgm"], note="The published weekly schedule sheet is headed 'August'."),
    dict(id="caesars", name="Caesars Palace", pokerRoom="Caesars Palace poker room",
         page="https://www.caesars.com/las-vegas/explore/casino/poker-tournaments-las-vegas-strip",
         series="Four daily No Limit Hold'em tournaments", schedule="https://www.caesars.com/las-vegas/explore/casino/poker-tournaments-las-vegas-strip",
         hotels=["caesars"], note="Buy-in, chips and guarantee are published on the official page; no structure sheet is linked."),
    dict(id="horseshoe", name="Horseshoe Las Vegas", pokerRoom="Horseshoe Hall of Fame poker room",
         page="https://www.caesars.com/las-vegas/explore/casino/poker-tournaments-las-vegas-strip",
         series="Six daily No Limit Hold'em tournaments", schedule="https://www.caesars.com/las-vegas/explore/casino/poker-tournaments-las-vegas-strip",
         hotels=["horseshoe"], note="Only the start times are published; buy-ins and guarantees are not."),
    dict(id="aria", name="ARIA Resort & Casino", pokerRoom="ARIA poker room",
         page="https://aria.mgmresorts.com/en/casino/poker.html",
         series="Daily and nightly cadence per an undated official guide",
         schedule="https://aria.mgmresorts.com/en/casino/poker.html",
         hotels=["aria"], note="The current page asks guests to call or check @ARIAPoker to confirm whether events are running."),
]

SOURCES = [
    dict(id="vl-dse-nov", name="Venetian DeepStack Extravaganza IV schedule and structure sheets (Nov 16 - Dec 23, 2026)",
         url="https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html",
         type="official schedule", checked=RECHECKED),
    dict(id="vl-dse-dec", name="Venetian DeepStack Extravaganza NYE schedule and structure sheets (Dec 24, 2026 - Jan 10, 2027)",
         url="https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-dec-2026.html",
         type="official schedule", checked=LAST_PASS),
    dict(id="clark-county-lodging-tax",
         name="Clark County Department of Business License - Combined Transient Lodging Tax rate schedule (Appendix III, General Information Guide for Transient Lodging Establishments)",
         url="https://www.clarkcountynv.gov/adobe/assets/urn:aaid:aem:689ef54f-ec0d-4bb6-b8ea-05a82887561f/original/as/genl-info-guide-for-tles-july-2021.pdf",
         type="government tax schedule", checked=RECHECKED),
    dict(id="clv-calendar", name="Caesars Palace official booking page: Hotel Policies > Fees block and Nov/Dec 2026 calendar",
         url="https://www.caesars.com/book/hotel-calendar?dateSearchFormat=flexible-dates&flexibleMonth=December&propCode=clv",
         type="official hotel page", checked=RECHECKED),
    dict(id="blv-calendar", name="Horseshoe Las Vegas official booking page: fee block and dated Nov/Dec 2026 rate cells",
         url="https://www.caesars.com/book/hotel-calendar?dateSearchFormat=flexible-dates&flexibleMonth=November&propCode=blv",
         type="official hotel page", checked=RECHECKED),
    dict(id="wynn-sig-struct", name="Wynn Signature Series structures file (read 2026-11-17: 'LAS VEGAS POKER - COMING SOON')",
         url="https://cdn.wynnresorts.com/image/upload/v1762299460/visitwynn_pdfs_files/Poker/Wynn%20Signature%20Series/Wynn_Signature_Series_Structures.pdf",
         type="official structures file", checked=RECHECKED),
    dict(id="vl-series", name="Venetian DeepStack Poker Series index (current, next and future series)",
         url="https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament.html",
         type="official index", checked=LAST_PASS),
    dict(id="vl-poker", name="Venetian poker room page", url="https://www.venetianlasvegas.com/resort/casino/poker.html",
         type="official room page", checked=LAST_PASS),
    dict(id="vl-suite-rates", name="Venetian poker-room suite rates and play requirements 2026",
         url="https://www.venetianlasvegas.com/resort/casino/poker/suite-rates.html", type="official rate page", checked=RECHECKED),
    dict(id="vl-resort-fee", name="Venetian resort fee page", url="https://www.venetianlasvegas.com/resort/resort-fee.html",
         type="official fee page", checked=RECHECKED),
    dict(id="vl-hotel-terms", name="Venetian hotel terms and conditions (tax, parking, cancellation)",
         url="https://www.venetianlasvegas.com/legal/hotel-terms-and-conditions.html", type="official terms", checked=RECHECKED),
    dict(id="wynn-poker", name="Wynn Las Vegas poker room page", url="https://www.wynnlasvegas.com/casino/poker",
         type="official room page", checked=LAST_PASS),
    dict(id="wynn-resort-info", name="Wynn Las Vegas Resort Policies (resort fee, check-in/out, reservation guarantee)",
         url="https://www.wynnlasvegas.com/about-us/resort-information", type="official terms", checked=RECHECKED),
    dict(id="wynn-parking", name="Wynn Las Vegas Parking Information (self-parking and valet fees)",
         url="https://www.wynnlasvegas.com/about-us/parking", type="official fee page", checked=RECHECKED),
    dict(id="wynn-daily-poster", name="Wynn daily tournament poster",
         url="https://cdn.wynnresorts.com/image/upload/v1752011166/visitwynn_pdfs_files/Poker/Daily%20Tournaments/poker-daily-tournament-poster.pdf",
         type="official schedule", checked=RECHECKED),
    dict(id="wynn-daily-struct", name="Wynn daily tournament terms and structures",
         url="https://cdn.wynnresorts.com/image/upload/v1752011191/visitwynn_pdfs_files/Poker/Daily%20Tournaments/Poker-All_Daily_Structures.pdf",
         type="official structures", checked=LAST_PASS),
    dict(id="wynn-wpt-sched", name="WPT World Championship schedule at Wynn Las Vegas (Nov 27 - Dec 21, 2026)",
         url="https://cdn.wynnresorts.com/image/upload/v1757097329/visitwynn_pdfs_files/Poker/WPT/WPT_World_Championship_Schedule.pdf",
         type="official schedule", checked=RECHECKED),
    dict(id="wynn-wpt-struct", name="WPT World Championship structures at Wynn Las Vegas",
         url="https://cdn.wynnresorts.com/image/upload/v1750864036/visitwynn_pdfs_files/Poker/WPT/WPT_World_Championship_Structures.pdf",
         type="official structures", checked=LAST_PASS),
    dict(id="wynn-sig-sched", name="Wynn Signature Series schedule (Jan 11-24, 2027)",
         url="https://cdn.wynnresorts.com/image/upload/v1753296112/visitwynn_pdfs_files/Poker/Wynn%20Signature%20Series/Wynn_Signature_Series_Schedule.pdf",
         type="official schedule", checked=LAST_PASS),
    dict(id="wynn-rooms", name="Wynn Las Vegas rooms and suites", url="https://www.wynnlasvegas.com/rooms-and-suites",
         type="official room page", checked=LAST_PASS),
    dict(id="wynn-terms", name="Wynn Las Vegas terms (resort fee, cancellation, parking)",
         url="https://www.wynnlasvegas.com/terms-and-conditions/850070", type="official terms", checked=LAST_PASS),
    dict(id="bell-poker", name="Bellagio poker room page", url="https://bellagio.mgmresorts.com/en/casino/poker.html",
         type="official room page", checked=RECHECKED),
    dict(id="bell-fri", name="Bellagio Friday $600 No Limit Hold'em structure",
         url="https://assets.contentstack.io/v3/assets/bltc6ce635bc4868eb2/blt9cf95b0e60ec253e/6af491a3a9851d75c40be840/mgm-bellagio-poker-fridays-$600-nlh.pdf",
         type="official structure", checked=LAST_PASS),
    dict(id="bell-sat", name="Bellagio Saturday No Limit Hold'em structure (buy-in conflict)",
         url="https://assets.contentstack.io/v3/assets/bltc6ce635bc4868eb2/blt6d47974bf5a7d9b6/6af491a391a6e8e4230c9e07/mgm-bellagio-poker-saturdays-$1000-nlh.pdf",
         type="official structure", checked=LAST_PASS),
    dict(id="bell-sun", name="Bellagio Sunday $400 H.O.R.S.E. structure",
         url="https://assets.contentstack.io/v3/assets/bltc6ce635bc4868eb2/blt07fcf1244a6da661/6af491a339e2b4f6b76a86ad/mgm-bellagio-poker-sundays-$400-horse.pdf",
         type="official structure", checked=LAST_PASS),
    dict(id="bell-hotel", name="Bellagio hotel rooms and suites", url="https://bellagio.mgmresorts.com/en/hotel.html",
         type="official room page", checked=LAST_PASS),
    dict(id="bell-terms", name="Bellagio hotel reservation terms (resort fee, cancellation, taxes)",
         url="https://bellagio.mgmresorts.com/en/terms-and-conditions.html", type="official terms", checked=LAST_PASS),
    dict(id="mandalay-poker", name="Mandalay Bay poker room page (hours, price range; no tournament schedule printed)",
         url="https://mandalaybay.mgmresorts.com/en/casino/poker-tables.html", type="official poker page", checked="2026-11-17"),
    dict(id="mgm-poker", name="MGM Grand poker room page", url="https://mgmgrand.mgmresorts.com/en/casino/poker-tables.html",
         type="official room page", checked=LAST_PASS),
    dict(id="mgm-sched", name="MGM Grand weekly tournament schedule sheet",
         url="https://assets.contentstack.io/v3/assets/bltc6ce635bc4868eb2/blt5f25277b8918da08/mgm-grand-casino-poker-tournament_schedule.pdf",
         type="official schedule", checked=LAST_PASS),
    dict(id="mgm-struct", name="MGM Grand $120 No Limit Hold'em structure",
         url="https://assets.contentstack.io/v3/assets/bltc6ce635bc4868eb2/bltb2a45da7e8ee5621/mgm-grand-casino-poker-120_nlh.pdf",
         type="official structure", checked=LAST_PASS),
    dict(id="caesars-poker", name="Caesars Palace and Horseshoe poker tournament page",
         url="https://www.caesars.com/las-vegas/explore/casino/poker-tournaments-las-vegas-strip",
         type="official room page", checked=LAST_PASS),
    dict(id="caesars-flyer", name="Caesars Palace daily No-Limit Hold'em tournament flyer 2026 (linked from the official Caesars Palace casino page, 'View Schedule')",
         url="https://www.caesars.com/content/dam/empire/clv/casino/poker/tournament-schedule/clv-poker-daily-nlh-tournament-flyer-2026.pdf",
         type="official tournament flyer", checked="2026-11-18"),
    dict(id="aria-poker", name="ARIA poker room page", url="https://aria.mgmresorts.com/en/casino/poker.html",
         type="official room page", checked=LAST_PASS),
    dict(id="aria-guide", name="ARIA official poker guide (undated)",
         url="https://aria.mgmresorts.com/content/dam/MGM/aria/casino/poker/aria-casino-poker-gentlemans-guide.pdf",
         type="official guide", checked=ASOF),
    # --- Added by the live re-verification of 2026-11-17 -------------------
    *[dict(name=v["name"], url=v["url"], type=v["type"], checked=v["checked"])
      for v in VERIFIED_SOURCES_2026_11_17],
    dict(name="Venetian DSE IV transcribed schedule rows (44 rows, line by line)",
         url="https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/dse-nov-2026-schedule.pdf",
         type="verified transcription", checked=VERIFIED_ON),
    dict(name="MGM Grand hotel reservation terms ($50 resort fee, 72-hour cancellation)",
         url="https://mgmgrand.mgmresorts.com/en/terms-and-conditions.html",
         type="official terms", checked=VERIFIED_ON),
    dict(name="ARIA hotel reservation terms ($55 resort fee, 72-hour cancellation)",
         url="https://aria.mgmresorts.com/en/terms-and-conditions.html",
         type="official terms", checked=VERIFIED_ON),
    dict(name="Wynn resort policies (live, non-offer page: $55 resort fee, check-in/out)",
         url="https://www.wynnlasvegas.com/about-us/resort-information",
         type="official terms", checked=VERIFIED_ON),

]

FLAGS = [
    dict(id="F01", area="Wynn WPT schedule", severity="High",
         title="The official WPT schedule PDF labels December 18 as both a Wednesday and a Friday",
         detail=("In the same PDF, 'Dec. 18 Wednesday' carries the No Limit Hold'em Day 1A and PLO rows while 'Dec. 18 Friday' "
                 "carries the WPT World Championship Day 4 rows. The rows also run out of order, with the December 17 block "
                 "printed after the December 18 Wednesday block, and no December 16 block appears anywhere in the PDF. "
                 "December 18, 2026 is a Friday. Flag F61 sets out the official evidence that the day number, not the weekday, "
                 "is the misprint and that these eight rows are very likely December 16. The schedule dates are reproduced "
                 "exactly as printed and the dispute is flagged rather than corrected, because the site does not silently "
                 "re-date a row on an inference."),
         source="https://cdn.wynnresorts.com/image/upload/v1757097329/visitwynn_pdfs_files/Poker/WPT/WPT_World_Championship_Schedule.pdf"),
    dict(id="F02", area="Bellagio", severity="High",
         title="Bellagio Saturday buy-in is printed three different ways on official sources",
         detail=("The poker-room page links the event as 'SATURDAYS | $1,000 NLH'; the structure PDF header reads 'NLH $1100 "
                 "BUY-IN'; rule 07 of the same PDF reads 'Of the $600 Buy-in, $510 goes to the Prize Pool, $50 is Admin Fees and "
                 "$40 is optional staff gratuity'. The row is therefore left blank for buy-in and guarantee and is not ranked."),
         source="https://assets.contentstack.io/v3/assets/bltc6ce635bc4868eb2/blt6d47974bf5a7d9b6/6af491a391a6e8e4230c9e07/mgm-bellagio-poker-saturdays-$1000-nlh.pdf"),
    dict(id="F03", area="Bellagio", severity="Medium",
         title="Bellagio tournament-resumption notice is undated and names July 26",
         detail=("The poker page still carries the notice 'Tournament play will resume on Saturday, July 26, beginning with the "
                 "$300 PLO Double Board Bomb Pot Tournament at 2 PM PT.' No year is printed, July 26, 2026 was a Sunday, and the "
                 "page highlights elsewhere say the PLO Double Bomb Pot runs nightly at 6 PM. The start time is therefore left "
                 "as the page highlight value and the notice is listed as a conflict."),
         source="https://bellagio.mgmresorts.com/en/casino/poker.html"),
    dict(id="F04", area="Venetian NYE", severity="Medium",
         title="Venetian NYE schedule prints 'Saturday, December 26, 2025' for three events",
         detail=("Events 5, 6 and 7 of the DeepStack Extravaganza NYE page are dated 'Saturday, December 26, 2025' even though "
                 "the series runs December 24, 2026 to January 10, 2027. The page also misspells 'Tuesaday'. The rows are kept "
                 "at 2026-12-26 and the printed label is flagged here."),
         source="https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-dec-2026.html"),
    dict(id="F05", area="Venetian DSE IV", severity="Low",
         title="Structure sheet 13 cross-references the wrong companion sheet",
         detail=("Sheet 12 covers 'Day A+C+E' and points to 'SEE OTHER STRUCTURE SHEET FOR DAYS B+D+F'. Sheet 13 covers 'Day B+D' "
                 "but points to 'SEE OTHER STRUCTURE SHEET FOR DAYS A+C+F', which should read A+C+E. Sheet 14 covers Day F and "
                 "points to A+B+C+D+E. The flight groups themselves agree with the schedule page; only the cross-reference is wrong."),
         source="https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_13.pdf"),
    dict(id="F06", area="Venetian NYE", severity="Medium",
         title="Two NYE events are labelled (1Day) but have a Day 2 restart on the same schedule page",
         detail=("Event 27 '$250 No Limit Hold'em 1A $75K GTD (1Day)' carries the note 'Day 1 Payouts with 5% advancing to Day 2' "
                 "and a Day 2 Restart on January 6, 2027. Event 30 '$300 No Limit Hold'em 1A $100K GTD (1Day)' has a Day 2 "
                 "Restart on January 10, 2027. Both are treated as multi-day."),
         source="https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-dec-2026.html"),
    dict(id="F07", area="MGM Grand", severity="Medium",
         title="MGM Grand weekly schedule sheet is headed 'August Tournament Schedule'",
         detail=("The PDF linked from the MGM Grand poker-room page is titled 'MGM Grand August Tournament Schedule' while the "
                 "room page itself is current. The daily slots and buy-ins are used as printed; the month label is flagged."),
         source="https://assets.contentstack.io/v3/assets/bltc6ce635bc4868eb2/blt5f25277b8918da08/mgm-grand-casino-poker-tournament_schedule.pdf"),
    dict(id="F08", area="MGM Grand", severity="Medium",
         title="MGM Grand $120 payout table does not line up with its own entry ranges",
         detail=("Rows such as '71-77' list eleven payout percentages and '64-70' list ten, which cannot both describe a "
                 "seven-entry range. The payout table is not used for any comparison on this site."),
         source="https://assets.contentstack.io/v3/assets/bltc6ce635bc4868eb2/bltb2a45da7e8ee5621/mgm-grand-casino-poker-120_nlh.pdf"),
    dict(id="F09", area="MGM Grand", severity="Low",
         title="The MGM Grand $120 structure PDF carries the title 'Max Stacks Tournament Series'",
         detail=("The document title on the PDF is 'Max Stacks Tournament Series' although its content is the $120 No Limit "
                 "Hold'em structure. Content matches the poker-room page; the title does not."),
         source="https://assets.contentstack.io/v3/assets/bltc6ce635bc4868eb2/bltb2a45da7e8ee5621/mgm-grand-casino-poker-120_nlh.pdf"),
    dict(id="F10", area="Venetian DSE IV", severity="Low",
         title="LIPS flat-fee wording on sheets 31, 32 and 33 is ambiguous",
         detail=("Sheet 33 reads '$80 of the $600 Buy-In is withheld for house fees (Rake + Staff). $10 of the $600 Buy In will be "
                 "withheld as a flat fee for ... Ladies International Poker Series (LIPS). Prize pool consists of $510 of every "
                 "$600 Buy In.' Read as two separate withholdings ($80 + $10 + $510) the total is $600; read as one, it is $590. "
                 "The figures are reported as printed with the ambiguity flagged."),
         source="https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_33.pdf"),
    dict(id="F11", area="Venetian NYE", severity="Low",
         title="The NYE series is fully read, but three of its sheets print multi-entry wording the schedule page omits",
         detail=("Resolved on 2026-11-17: the 15 DeepStack Extravaganza NYE structure sheets were read in full, so no NYE "
                 "row is marked 'structure sheet not read'. The sheets change the picture that the schedule page alone "
                 "gives. Sheet 2 ($200 Bounty) and sheet 9 ($200 Valuetown Bounty) both print a 'subsequent re-entry' "
                 "sentence, and sheet 15's $250 flight series says a player 'may play another flight', so those rows are "
                 "multi-entry and stay out of the single-entry path. Sheets 1, 3, 10, 11 and 12 print no re-entry, rebuy "
                 "or add-on clause and are recorded as single entry on the sheet. Sheets 6, 8, 13 and 14 print bagging "
                 "clauses and are counted as multi-flight. The remaining sheets are satellites or bounty events with "
                 "their own wording, quoted on each row."),
         source="https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-dec-2026.html"),
    dict(id="F12", area="Wynn WPT", severity="Medium",
         title="Thirteen WPT events now carry their printed rules; the $10,400 World Championship and the satellites still have no published section",
         detail=("The official structures PDF was read end to end on 2026-11-17 (all eight chunks) and every event "
                 "section it publishes is transcribed in "
                 "raw/wynn_wpt_world_championship_structures_2026-11-17.md. Thirty-five schedule rows now match a "
                 "section on date, start slot, buy-in and printed name: the $600 NLH $400K flights (Nov 27-29), the "
                 "$800 NLH $1M flights (Nov 30-Dec 2), the $1,600 NLH $1M flights (Dec 3-4), the $1,100 WPT Prime "
                 "flights (Dec 5-8), the $1,600 PLO Mystery Bounty flights (Dec 6), and the single-day TORSE, PLO, "
                 "Mixed Triple Draw, Limit Omaha 8, Limit Omaha 8/Stud 8, $1,100 PLO, HORSE and $600 NLH Turbo "
                 "events. Every one of those sections prints re-entry, so none of them is a single-entry event, and "
                 "none prints an add-on or rebuy provision. What remains unverified is listed here rather than "
                 "implied: the $10,400 WPT World Championship has no section at all; the Dec 18 $3,000 and $10,500 "
                 "events, the Super Gold Million Mystery Bounty, the Seniors and Ladies championships, the NLH "
                 "Mystery Bounty, the Wynn Mixed Championship, the TORSE and Limit Omaha 8 championships and every "
                 "Milestone Satellite have no section either. Day 2 and final-table rows keep 'not-verified' because "
                 "the document publishes entry rules for starting flights, not for restarts, and two of them (Nov 30 "
                 "1 p.m. and Dec 3 1 p.m.) carry the following event's buy-in columns in the schedule PDF (F34)."),
         source="https://cdn.wynnresorts.com/image/upload/v1750864036/visitwynn_pdfs_files/Poker/WPT/WPT_World_Championship_Structures.pdf"),
    dict(id="F13", area="ARIA", severity="Medium",
         title="The ARIA poker guide is undated and the current page asks guests to confirm by phone",
         detail=("The official guide states daily 1 PM and nightly 7 PM events but carries no date. The current poker page asks "
                 "guests to call or check @ARIAPoker for whether daily events are running, and publishes no buy-in, guarantee or "
                 "entry rules. The rows are kept as an undated cadence only."),
         source="https://aria.mgmresorts.com/en/casino/poker.html"),
    dict(id="F14", area="Hotels", severity="Medium",
         title="Wynn resort fee differs between published offer pages",
         detail=("The general Wynn terms used here state 'A daily resort fee of $55 plus tax'. An older, expired offer page "
                 "states $50 plus tax. The actual fee on a booked reservation controls; $55 plus tax is used and the discrepancy "
                 "is flagged rather than resolved."),
         source="https://www.wynnlasvegas.com/terms-and-conditions/850070"),
    dict(id="F15", area="Hotels", severity="High",
         title="RESOLVED 2026-11-17: a dated checkout total exists for the booked trip window ($4,010.55, 23-30 Nov 2026)",
         detail=("Superseded on the evening of 2026-11-17; the record is kept because it is the largest money gap the "
                 "dashboard carried. The booking engine printed an itemised total for the stay the trip is actually "
                 "booked for: 23-30 November 2026, seven nights, two adults, Newly Remodeled Luxury King under 'Book "
                 "Direct: Up to 25% Off', $4,010.55 with $473.30 of tax and nightly room rates of $164.25, $164.25, "
                 "$201.75, $231.75, $1,649.25, $554.25 and $186.75 before a $55 resort fee each night. Every night "
                 "reconciles to (rate + $55) x 1.1338 and the seven derived figures add to the printed total exactly. "
                 "The trip cost model now uses that total and publishes the $197.28 component floor beside it. For "
                 "completeness on the superseded dates: four stay windows inside the then-recommended 25 November - "
                 "2 December 2026 returned no suite and no price, and two earlier near-term stays are still in the rate "
                 "log as observations (17-19 November at $1,245.48 on 2026-11-16 and $1,015.89 on 2026-11-17, 20-22 "
                 "November at $2,504.00). What remains open is narrower and is carried by F66: the phone-only poker "
                 "rate (code EPOKR25) does not appear in the engine quote."),
         source="https://www.venetianlasvegas.com/booking?adults[]=2&arrival_date=2026-11-17&children[]=0&departure_date=2026-11-19&view=calendar"),
    dict(id="F28", area="Hotels", severity="High",
         title="The Venetian booking calendar disagrees with the quote, and its cells change with the query",
         detail=("The calendar cell for November 17 read $855 in the observation recorded on 2026-11-16, while the same "
                 "page's quote for the same night printed a $824.25 room rate, and an earlier observation of the same "
                 "calendar on the same day recorded $605. The calendar states that its prices are the best available suite "
                 "and rate, include the daily resort fee and exclude taxes. Calendar cells are logged as observations and "
                 "are never used in a total. On 2026-11-17 the same booking engine was fetched live for the superseded "
                 "25 November - 2 December window and showed no amount in any date cell; the engine was then opened for "
                 "the booked 23-30 November stay and printed an itemised $4,010.55 total (F15), while its calendar cells "
                 "for those nights were still different figures (F69). No calendar cell is ever recorded as a price."),
         source="https://www.venetianlasvegas.com/booking?adults[]=2&arrival_date=2026-11-17&children[]=0&departure_date=2026-11-19&view=calendar"),
    dict(id="F45", area="Sources", severity="Low",
         title="The official schedule PDF and the official schedule page print the event name differently",
         detail=("Both captures are official and they agree on date, time, event number and structure-sheet link for all "
                 "94 rows, but 83 of the 94 names are rendered differently: the PDF puts the guarantee in its own "
                 "GUARANTEE column, while the HTML page inlines '$XXK GTD' into the event name. Example: the PDF prints "
                 "'$200 NLH BOUNTY (1DAY)' with a separate $8,000 guarantee, and the page prints '$200 No Limit Hold'em "
                 "Bounty $8K GTD (1Day)'. The site's names follow the HTML page, which is the page every row links to."),
         source="https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html"),
    dict(id="F46", area="Sources", severity="Medium",
         title="The official schedule PDF prints decorative sponsor art in the DATE column on 20 rows",
         detail=("20 of the 94 rows on the official DeepStack Extravaganza IV schedule PDF carry no date at all: 6 read "
                 "'@PokerAtlas* TOUR', 6 read 'LIPS CHAMPIONSHIP CHAMPIES CHAMPIES CHAMPIES', 5 read "
                 "'LIPS FRIDAY, DECEMBER 11', 2 read '@PokerAtlas PRO' and 1 reads '@PokerAtlas* PRO'. Those rows cover "
                 "events 17, 18, 32-38, 41-46, 48, 50, 51 and 58. The dates on this site for those rows come from the "
                 "official schedule page, not from the PDF, and the two were cross-checked row by row."),
         source="https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html"),
    dict(id="F47", area="Hotels", severity="High",
         title="Booking-calendar cells are not prices: the same date prints a different figure per query",
         detail=("On 2026-11-17 the official Venetian booking calendar was read twice, with two different stay windows "
                 "open. November 16 printed $555 with the November 17-19 window open and $854 with the November 27-28 "
                 "window open; November 22 printed $165 against $230; November 27 printed $905 against $1,814. The page's "
                 "own footnote says the figure is the best available suite and rate, includes the daily resort fee and "
                 "excludes taxes, so the cell tracks the cheapest suite the engine can offer for that context rather than "
                 "a fixed nightly rate. No calendar cell is used anywhere on this site as a price; only the engine's "
                 "itemised quote panel is."),
         source="https://www.venetianlasvegas.com/booking?adults[]=2&arrival_date=2026-11-17&children[]=0&departure_date=2026-11-19&view=calendar"),
    dict(id="F16", area="Schedule", severity="High",
         title="No official schedule publishes tournament finish times",
         detail=("Venetian sheets publish start time, level length and late-registration cut-off but no finish time. The overlap "
                 "check therefore uses a stated planning assumption (a six-hour session plus a 30-minute transfer between venues) "
                 "and every conflict it reports is an estimate, not an official statement."),
         source="https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html"),
    dict(id="F17", area="Schedule", severity="High",
         title="The earliest verified official start is 9:00 AM (Horseshoe daily); no 8:00 AM start is published",
         detail=("Re-read on 2026-11-17 on the Caesars page: Horseshoe runs six daily No-Limit Hold'em games at 9 a.m., "
                 "11 a.m., 2 p.m., 5 p.m., 8 p.m. and 11 p.m., with no buy-in published. Caesars Palace runs four daily games "
                 "at 10 a.m., 2 p.m., 6 p.m. and 9 p.m. (the official flyer prints $100 buy-ins at 10 a.m. and 6 p.m. and $160 at 2 p.m. and 9 p.m., with an optional $50 add-on; read 2026-11-18, F90). On the Venetian schedule re-read on "
                 "2026-11-17 the earliest start is 9:10 AM, a $260 satellite on Dec 12. "
                 "Re-read live on 2026-11-19 from the official DSE IV schedule page (all four chunks): the 9:10 AM row is Saturday, "
                 "December 12, Event 46; the two 10:00 AM Venetian rows are Friday, December 11 (Event 39, Day 2 Restart) and Tuesday, "
                 "December 15 (Event 49, Day 2 Restart); the earliest opening event is 10:10 AM. Opening Venetian events start at "
                 "10:10 AM or later; the only 10:00 AM Venetian starts are restarts (Day 2 or Day 3). Inside the 23-29 November trip "
                 "window no opening event starts before 11:10 AM; the only earlier start there is the Day 2 restart at 11:00 AM on "
                 "25 November (read 2026-11-19). The Wynn daily starts at 12:00 PM. "
                 "Most Wynn WPT rows start at 11:00 AM. Its 10:00 AM rows are the Super Gold Million flights (Dec 10 and 11), one WPT "
                 "row on Dec 12 and a satellite on Dec 18, all from the WPT PDF read on 2026-11-16. An 'all day from 8:00 AM' plan cannot be built from official sources. The day plan starts at "
                 "the earliest verified start for each venue. Re-checked 2026-11-19: the 9:10 AM Venetian satellite and the "
                 "9:00 AM Horseshoe daily are still the two earliest printed starts, and neither supports an 8:00 AM plan."),
         source="https://www.caesars.com/las-vegas/explore/casino/poker-tournaments-las-vegas-strip"),
    dict(id="F18", area="Wynn", severity="Low",
         title="Wynn daily tournaments are suspended during Wynn Signature, Wynn Millions and Classic series",
         detail=("Stated on the official poker-room page. It matters for date selection: the daily $200 and $160 events cannot be "
                 "assumed to run during those windows."),
         source="https://www.wynnlasvegas.com/casino/poker"),
    dict(id="F19", area="Hotels", severity="Medium",
         title="Hotel cost comparison is limited to published per-night components",
         detail=("No reviewed property publishes parking cost inside the room folio, incidentals, or the tax rate as a single "
                 "checkout total, so the like-for-like comparison is built from the same published components for every property: "
                 "room rate, mandatory resort fee, tax, parking and cancellation deadline."),
         source="https://www.venetianlasvegas.com/legal/hotel-terms-and-conditions.html"),
    dict(id="F20", area="Horseshoe", severity="Medium",
         title="Horseshoe daily buy-ins, levels and guarantees are not published",
         detail=("The official Caesars page publishes six Horseshoe start times but states only that 'a mixture of buy-ins, levels "
                 "and guarantees caters to all participants'. Every Horseshoe monetary field is therefore blank."),
         source="https://www.caesars.com/las-vegas/explore/casino/poker-tournaments-las-vegas-strip"),
    dict(id="F21", area="Walking routes", severity="Low",
         title="Google Maps resolved 'Horseshoe Las Vegas' to Bally's on the first query",
         detail=("The first walking query using the property name alone was routed from Bally's Las Vegas. The figure shown for "
                 "Horseshoe was re-taken using the full street address and the result is labelled as such. Walking times are "
                 "Google Maps estimates captured on 2026-11-16, not venue-published figures."),
         source="https://www.google.com/maps/dir/?api=1&travelmode=walking"),
    dict(id="F26", area="Wynn Signature Series", severity="Medium",
         title="Several schedule rows on the Wynn Signature Series PDF carry an extra empty cell",
         detail=("The rows for '1/17 NLH TURBO', '1/18 NO LIMIT HOLD\'EM DAY 1A' and '1/18 NLH TURBO' have one more "
                 "cell than the table header, which shifts the guarantee column: the printed guarantee appears in the "
                 "entry column and the entry price appears in the chip column. The values are read in the order the "
                 "surrounding rows use, so the $10,000 and $100,000 figures are treated as the guarantee and $200 or "
                 "$400 as the entry. The guarantee for the milestone satellites is printed as '10 Seats'. "
                 "Re-read on 2026-11-17: the shift is still on the page, and the same pattern also moves the guarantee "
                 "out of its column on the 1/17 1 P.M. Day 2, 1/18 PLO, 1/19 TORSE, 1/20 MIXED TRIPLE DRAW, 1/21 TOE, "
                 "1/22 BIG O and 1/24 PLO DOUBLE BOARD BOMB POT rows, which print no guarantee cell. Those rows are "
                 "shown with a blank guarantee rather than a shifted figure."),
         source="https://cdn.wynnresorts.com/image/upload/v1753296112/visitwynn_pdfs_files/Poker/Wynn%20Signature%20Series/Wynn_Signature_Series_Schedule.pdf"),
    dict(id="F27", area="Venetian DSE IV", severity="Low",
         title="The official DSE schedule page misspells 'Limit' on four rows",
         detail=("The schedule page prints 'No LImit Hold\'em' with a capital letter i on the rows for event 2 "
                 "(November 18), event 6 (November 22), event 10 (November 25) and event 12 (November 26). The event "
                 "names on this site use the corrected spelling and every row links the page and the structure sheet, "
                 "so the printed label can be checked in one click."),
         source="https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html"),
    dict(id="F23", area="Wynn WPT", severity="Medium",
         title="The Ladies Championship entry fee is printed twice, differently",
         detail=("The WPT schedule prints the buy-in column as '$1,100' for 'Ladies NIH Championship (2 Day)' while the "
                 "footnote under the table reads 'The Tournament Entry for the Ladies Championship is $11,100. Ladies will "
                 "receive a discounted entry.' The event name is printed as 'NIH', which is a typo for No Limit Hold'em. "
                 "The row keeps the printed column value and the footnote is recorded with it; nothing is adjusted."),
         source="https://cdn.wynnresorts.com/image/upload/v1757097329/visitwynn_pdfs_files/Poker/WPT/WPT_World_Championship_Schedule.pdf"),
    dict(id="F24", area="Wynn WPT", severity="High",
         title="The '$1,000,000 Added' on the WPT World Championship is not available in Nevada",
         detail=("The schedule prints 'WPT World Championship Day 1A $1,000,000 Added' for $10,400, and the footnote "
                 "under the table states: '$1,000,000 will be added in cash prizes by ClubWPT Gold. ClubWPT Gold is not "
                 "available in Nevada.' The guarantee column for those rows is blank on the schedule. A Nevada player "
                 "therefore cannot count the added million, which is why no guarantee is shown for those rows."),
         source="https://cdn.wynnresorts.com/image/upload/v1757097329/visitwynn_pdfs_files/Poker/WPT/WPT_World_Championship_Schedule.pdf"),
    dict(id="F25", area="Wynn WPT", severity="Low",
         title="The five footnote markers on the WPT schedule PDF: what each one says, and the four **** rows it does not describe",
         detail=("Re-read with the whole schedule PDF on 2026-11-17 (both chunks) so the resolution is recorded rather than "
                 "called unclear. The markers, in the PDF's own order, read: (1) '*' - 'Winners will receive two (2) "
                 "prizes valued at $1,100 each. Prizes may be used separately or combined for a tournament entry.'; "
                 "(2) '**' - 'Winners will receive direct entry to the corresponding event(s) for which it was held.'; "
                 "(3) '***' - '$1,000,000 will be added in cash prizes by ClubWPT Gold. ClubWPT Gold is not available in "
                 "Nevada.'; (4) '****' - 'The Tournament Entry for the Ladies Championship is $11,100. Ladies will "
                 "receive a discounted entry.'; (5) '*****' - 'Players registered prior to the start of the event will "
                 "receive a discounted entry.'. Markers 1, 2, 3 and 5 are printed on rows the text describes and are "
                 "carried with those rows. Marker 4 is the unresolved one. The footnote describes one event - the "
                 "Ladies Championship, printed as 'Ladies NIH Championship' at $1,100 on Dec 13 - and the PDF prints "
                 "the marker on seven rows in total: that row plus six the footnote does not describe (PLO 6-Max "
                 "$10,500, the Milestone Satellite to the $25K NLH High Roller $3,000, the NLH High Roller $25,800, "
                 "NLH 6-Max $10,500, PLO $10,500 and NLH 8-Max $10,500). Nothing is adjusted on any of them and none is "
                 "treated as discounted; the printed buy-in is shown. If the marker means the same thing on all seven "
                 "rows then the six high-roller-style prices are not the amount payable and the site overstates them, "
                 "which is why this stays open rather than resolved. Marker 5 appears on no captured row. Confirm with "
                 "the Wynn poker room (702.770.7654, printed on the same PDF)."),
         source="https://cdn.wynnresorts.com/image/upload/v1757097329/visitwynn_pdfs_files/Poker/WPT/WPT_World_Championship_Schedule.pdf"),
    dict(id="F22", area="Venetian DSE IV", severity="Low",
         title="The RaceDay Stack sheets print no guarantee",
         detail=("Sheets 18 and 29 print the buy-in, rake and blind structure but no guarantee line, so events 3, 4, 5 and 6 carry "
                 "a blank guarantee and are not ranked by the guaranteed-pool-to-fee ratio."),
         source="https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_18.pdf"),
    dict(id="F29", area="Publishing", severity="High",
         title="The site root served a stale page that contradicted the dashboard, because two publishers wrote to the same URL",
         detail=("GitHub Pages was configured to deploy from the main branch root while pages.yml also deployed the site/ "
                 "artifact, so the URL /Poker3/ served whichever deployment finished last. At the time this was found the "
                 "root served an earlier-round page (46 Venetian rows, no verified hotel cost, 'no hotel ranking is shown'), "
                 "while /Poker3/site/ served the canonical 341-row dashboard. A visitor landing on the site root therefore saw "
                 "conclusions the live data contradicts. The root page is now a redirect and pages.yml redeploys after the "
                 "branch build; the underlying setting (Pages source = 'deploy from a branch') could not be changed by this "
                 "session's token, which is why the redirect exists as a second guarantee."),
         source="https://github.com/karagemop466-tech/Poker3/blob/main/site/poker3/index.html"),
    dict(id="F30", area="Monitoring", severity="High",
         title="No scheduled source re-check had produced a run yet, and the three monitors were not serialised against each other",
         detail=("At inspection time no run of checks.yml, monitor.yml or daily-check.yml existed, and site/checks.json, which "
                 "the sources page fetches, did not exist either, so the page reported 'No automated check file yet'. The "
                 "reason for the zero runs is timing, not deletion: all three workflows reached main at 00:44 UTC on "
                 "2026-11-17 and their crons were 12:13, 12:05 and 09:00 UTC, so the first scheduled time had not arrived. "
                 "The real defect is that monitor.yml and daily-check.yml had no concurrency group at all while checks.yml "
                 "used its own, so they could have collided once the crons fired; daily-check.yml additionally rewrote the "
                 "tree and force-rebased onto main, and monitor.yml pushed with '|| true', which hides a rejected push. They "
                 "are now one serialised job with a rebase-retry push. It is registered and active; its first run is the "
                 "12:13 UTC cron, and this page does not claim a run has been observed."),
         source="https://github.com/karagemop466-tech/Poker3/actions"),
    dict(id="F31", area="Venetian DSE IV", severity="High",
         title="The structure sheets do not confirm a one-entry-per-player maximum",
         detail=("The 52 Venetian rows classified as 'single entry on the sheet' have one printed buy-in and no re-entry, rebuy, add-on or second-flight provision in the reviewed sheet. However, the sheets do not state a maximum number of entries per player and do not explicitly call the event a freezeout. This is only a document-level screen, not written confirmation of the room's one-entry policy. Do not treat these candidates as strictly eligible or book around them until the venue confirms the maximum-entry, no-rebuy and no-add-on rules in writing. The source excerpt and date are attached to each row. "
                 "Re-read 2026-11-19: the live official DSE IV schedule (all four chunks) prints no 'one entry', 'freezeout' or re-entry label on any row; its only entry wording is 'Direct Entry to Event #47 / #39' (satellites) and rake-discount notes. "
                 "The venue does print one-entry wording on schedule rows in other series: the official DeepStack Extravaganza II page (April 2023, dse-apr-2023.html) prints 'One Entry Only with One Hour of Registration' on Event 13 (read live 2026-11-19). "
                 "So the venue's schedule vocabulary includes a one-entry label, and the 2026 series prints none on any row. That is still not a written maximum-entry rule for the 2026 series, so F31 remains open. The question to put to the venue is in research/reread_2026-11-19.md. "
                 "This pass also read four more official pages in full (the DSE IV schedule all four chunks, the DeepStack series landing page, the poker-room page and the poker-room parking page) and none carries entry-rule prose; the schedule PDF was not re-read. Closing this needs a written answer from the room (lv_cas_poker@venetianlasvegas.com, 702.414.7657), not another schedule read."),
         source="https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html"),
    dict(id="F95", area="Change monitoring", severity="Low",
         title="The 2026-11-18 monitor run flagged six changed official URLs; all six were re-read by hand on 2026-11-19 and no published value moved",
         detail=("site/checks.json records a run at 2026-11-19T05:33Z in which six of the fetched official URLs had a "
                 "different visible-text hash from the previous run: the Venetian DeepStack series landing page and five Wynn "
                 "pages (the poker room, Resort Policies, Parking, Rooms & Suites and the /terms-and-conditions/850070 terms "
                 "page). A hash change is a review signal, not a value change, so each was read in full through the page "
                 "reader on 2026-11-19 and compared with what the site publishes. Results: the Venetian landing page now "
                 "correctly names DeepStack Extravaganza IV as the Current Series (F82 resolved). The Wynn poker page still "
                 "prints the four-event daily slate, the $200,000 weekly guarantee, the Friday $40,000 rebuy and the 'suspended "
                 "during each Wynn Signature, Wynn Millions and Classic series' note, and still links the same schedule, "
                 "structures and Signature files. Resort Policies still prints a $55 plus tax daily resort fee, check-in 3 p.m. "
                 "and check-out 12 p.m. Parking still prints $25 per day for non-registered guests with the first three hours "
                 "complimentary, $40 valet, and complimentary self-parking for Wynn Poker Room guests. Rooms & Suites prints "
                 "room descriptions and no price. The terms page still prints the DEPOSIT POLICY, the 48-hour CANCELLATION "
                 "POLICY, the $55 plus tax resort fee for both room classes and the parking section. No tournament, fee, rate, "
                 "route or policy value on this site was changed by any of the six. Any future hash change is re-read the same "
                 "way before a value is touched."),
         source="https://www.wynnlasvegas.com/about-us/resort-information"),
    dict(id="F61", area="Wynn WPT schedule", severity="High",
         title="Eight WPT rows are probably two days late: the 'Dec. 18 Wednesday' block is very likely December 16",
         detail=("The official WPT schedule PDF prints one block labelled 'Dec. 18 Wednesday' and a second labelled "
                 "'Dec. 18 Friday' holding different events, and it prints no December 16 block at all. Four pieces of "
                 "official evidence say the Wednesday block is December 16. (1) It sits between the December 15 Tuesday "
                 "block and the December 17 Thursday block in print order, exactly where December 16 belongs. "
                 "(2) December 16, 2026 is a Wednesday, which is the weekday the block prints. (3) It carries WPT World "
                 "Championship Day 2, and that event's Day 1C is printed on December 15 while its Day 3 is printed on "
                 "December 17, so Day 2 has to fall between them. (4) The $1,100 No Limit Hold'em whose Day 1A and Day 1B "
                 "appear in the block has its 'No Limit Hold'em Day 2' printed inside the December 17 block. The day "
                 "number therefore looks like the misprint, not the weekday. The site keeps the date exactly as printed, "
                 "because re-dating a row on an inference is exactly what this project promises not to do, so these eight "
                 "rows remain dated 2026-12-18: that collides them with the genuine December 18 rows and leaves "
                 "2026-12-16 empty. Confirm against the room's own published calendar before planning around any of them. "
                 "Flag F01 recorded the PDF's self-contradiction and concluded the weekday was the error; this flag "
                 "records the evidence that reverses that conclusion, and F01 has been amended to point here."),
         source="https://cdn.wynnresorts.com/image/upload/v1757097329/visitwynn_pdfs_files/Poker/WPT/WPT_World_Championship_Schedule.pdf"),
    dict(id="F62", area="Wynn WPT schedule", severity="Low",
         title="Four WPT event names read differently from the printed text",
         detail=("The schedule PDF prints 'NIH Turbo', 'NIH $500 Bounty Turbo' and 'Milestone Satellite to $25K NIH High "
                 "Roller', and it prints 'Double Play Milestone Satellite1' with a trailing digit. The published rows read "
                 "'NLH Turbo', 'NLH $500 Bounty Turbo', 'Milestone Satellite to $25K NLH High Roller' and 'Double Play "
                 "Milestone Satellite'. NIH is almost certainly the PDF's own rendering of NLH, but NIH is what is "
                 "printed, so this is a normalisation rather than a transcription and it is recorded as one. Every other "
                 "cell on those four rows - date, start time, buy-in, guarantee, chips and level length - was re-checked "
                 "against the PDF on 2026-11-17 and agrees."),
         source="https://cdn.wynnresorts.com/image/upload/v1757097329/visitwynn_pdfs_files/Poker/WPT/WPT_World_Championship_Schedule.pdf"),
    dict(id="F63", area="Venetian DSE IV", severity="Low",
         title="Day 2 restart rows carry values that their own schedule row leaves blank",
         detail=("The official DeepStack Extravaganza IV series schedule PDF prints an empty GUARANTEE, CHIPS, LEVEL and "
                 "REG CLOSES cell for every Day 2 restart row, because those rows continue an event whose Day 1 row "
                 "already printed them. The published restart rows fill those cells with the values printed on that "
                 "event's own structure sheet, so the figures are official but they come from the sheet, not from the "
                 "restart row. A line-by-line re-check of all 94 rows against the PDF on 2026-11-17 found 43 such cells, "
                 "all on Day 2 restart rows, and no other disagreement anywhere in the series."),
         source="https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/dse-nov-2026-schedule.pdf"),
    dict(id="F64", area="Hotels", severity="Low",
         title="Two different official booking requests gave two different answers for the trip window",
         detail=("Asking the official Venetian booking engine for the trip window itself (arrival 2026-11-25, departure "
                 "2026-12-02) returned $XXX in every cell on the earlier read, so no checkout total was obtained for those "
                 "nights; a later read of 2026-11-23 to 2026-11-30 did return one ($4,010.55, F36). Asking the same "
                 "engine for a calendar view (arrival 2026-11-17) prints per-night cells for 17-30 November, including "
                 "$185 on 25 November, $190 on 26 November, $210 on 27 November, $905 on 28 November, $340 on "
                 "29 November and $165 on 30 November, and the calendar states those cells include the daily resort fee "
                 "and exclude taxes. A note carried by an earlier build of this site said the trip window published no "
                 "price at all, which those cells contradict; a later live re-read rewrote that note, and this flag keeps "
                 "the two requests distinct so the claim cannot return. The calendar cells are still not a quote, and "
                 "nothing here converts them into one: they are recorded so a reader can see that part of the window "
                 "does have published figures."),
         source="https://www.venetianlasvegas.com/booking?adults[]=2&arrival_date=2026-11-17&children[]=0&departure_date=2026-11-19&view=calendar"),
    dict(id="F65", area="Hotels", severity="Low",
         title="Printed Venetian tax for the 23-30 Nov quote is $0.02 above 13.38% of its pre-tax subtotal",
         detail=("Dated official booking-engine read on 2026-11-17 (2 adults, 23-30 Nov 2026, 7 nights): the printed "
                 "nightly rates total $3,152.25, the printed resort fees total $385.00, the pre-tax subtotal is $3,537.25, "
                 "and the printed tax is $473.30. 13.38% of $3,537.25 is $473.28. The page does not explain the $0.02 "
                 "difference. The record keeps the printed $473.30 and the printed $4,010.55 total, and does not adjust "
                 "either figure. Per-night true costs are derived as (rate + $55) x 1.1338 and sum to the printed total."),
         source="https://www.venetianlasvegas.com/booking?adults[]=2&arrival_date=2026-11-23&children[]=0&departure_date=2026-11-30&view=calendar"),
    dict(id="F32", area="Walking routes", severity="Medium",
         title="Walking-route estimates are point-in-time Google Maps readings",
         detail=("The hotel-by-venue matrix now holds all 56 pairs (8 hotel records × 7 venue records): 14 rows from the "
                 "2026-11-16 base pass plus 42 rows read on 2026-11-17 — 41 resort-to-resort readings added by that pass "
                 "and the Venetian-to-Bellagio row added by a concurrent pass with poker-room endpoints (27 min, see F67). "
                 "Cross-checks: every resort-to-resort pair measured agrees with its already-published reverse direction "
                 "within one minute, except Wynn-venue rows, where the new pass walked to Encore (where the poker room "
                 "actually is) while the stored wynn-origin rows start at Wynn Las Vegas. What remains flagged: every "
                 "figure is a reading of one moment — sidewalks, crossings and route recommendations change — endpoint "
                 "choice alone moves the answer by several minutes (F67), and no unofficial path is used. Re-measure the "
                 "specific pair on Google or Apple Maps before relying on it, and confirm the official property addresses. "
                 "The tournament table's 30-minute limit is opt-in, not a default, so it cannot hide rows before the reader "
                 "asks; it is measured from the hotel the reader selects, and a pair resolved only by the reverse of a "
                 "recorded row is labelled 'reverse of the recorded pair', because a reversed row is a property-to-property "
                 "figure whose far end is the resort address rather than the poker room."),
         source="https://www.google.com/maps/dir/?api=1&travelmode=walking"),
    dict(id="F88", area="Hotels", severity="Medium",
         title="The dated Venetian checkout total rests on one successful engine read; a second read the same evening returned no prices",
         detail=("The $4,010.55 all-in total for 23-30 November 2026 was printed by the official booking engine on 2026-11-17 and "
                 "re-read that evening at 21:5x UTC (see F15). A third read from this session at 22:33 UTC on the same URL returned "
                 "no price at all: every calendar cell rendered the placeholder '$XXX', the suite panel showed only 'Your Venice "
                 "meets Vegas getaway is loading', and no checkout summary was returned. That is the same rendering failure this "
                 "repository recorded for four other stay windows, so it is treated as evidence that the engine does not serve a "
                 "stable static price to every reader, not as evidence that the price moved. F78, published by a concurrent session, records a different failure of the same engine on the same night: the same trip-window query returned two different suites and totals about 20 minutes apart. Read the two together - the engine is not a stable source for a static reader. Consequence for a decision: the "
                 "published total is dated, reproducible from the recorded nightly figures and internally consistent "
                 "(every night reconciles to (rate + $55) x 1.1338 and the seven figures add to the printed total), but it must be "
                 "re-read at the moment of booking before any non-refundable payment. Nothing on the site was revalued on the "
                 "strength of the failed read. A fourth read on 2026-11-19 repeated the failure in the same way: the 23-30 "
                 "November booking URL returned the reservation shell and the rewards panel with no suite price and no "
                 "checkout total, so this pass adds no rate observation and the $4,010.55 record of 2026-11-17 stands as "
                 "the only dated total."),
         source="https://www.venetianlasvegas.com/booking?adults[]=2&arrival_date=2026-11-23&children[]=0&departure_date=2026-11-30&view=calendar"),
    dict(id="F89", area="Verification", severity="Low",
         title="Sources re-read on 2026-11-17 (22:3x UTC) that match the published rows, recorded so the re-check date is not lost",
         detail=("Re-read line by line from this session with no change found, and therefore no value edited: the Venetian "
                 "DeepStack IV schedule page (chunk 0 of 4, 16-28 November rows: event numbers, dates, start times, buy-ins, "
                 "guarantees and structure-sheet links all agree with site/data.json); the Venetian 2026 poker suite-rates page "
                 "('rates will start as low as $119 and $209', '$55 resort fee per night stayed', the six-hours-cash-or-$300-"
                 "tournament qualification, code EPOKR25, the 150-day horizon); the Wynn WPT World Championship structures PDF "
                 "(chunks 0, 1, 4 and 5 of 8: the general terms, and the $600 NLH, $600 Limit Omaha 8/Stud 8, $1,100 PLO, $1,600 "
                 "NLH, $600 HORSE and $1,100 Prime Championship sections, each fee split, registration clause and starting stack "
                 "quoting exactly as published, including the $1,100 section whose components add to $1,105 - F60); the Wynn resort "
                 "policies page ('a daily resort fee of $55 plus tax', check-in 3 p.m., check-out 12 p.m., self-parking for up to "
                 "two vehicles included in the fee); the Bellagio terms and conditions ('A daily resort fee of $55.00 plus "
                 "applicable tax', $50 plus tax per additional occupant, 72-hour cancellation window, $150 per day incidental "
                 "authorisation); and the Caesars Palace booking page ('$62.30 ($54.95 plus $7.35 tax)', 'Rates shown reflect the "
                 "lowest available rate and include applicable resort fees'). Caesars' printed fee-plus-tax figures divide to "
                 "13.375%, and Horseshoe's ($49.95 plus $6.68) to 13.373%, which corroborates the 13.38% Clark County room tax "
                 "used by the cost model from the properties' own pages rather than only from the Venetian's terms."),
         source="https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html"),
    dict(id="F33", area="Schedule overlap", severity="Medium",
         title="Day 2 restarts of earlier Venetian events overlap the trip-window primaries",
         detail=("Re-read on 2026-11-17 from the official schedule: Event #7 ($400 No Limit Hold'em flights) has a Day 2 Restart "
                 "at 11:00 AM on Wed Nov 25, the same morning as the 11:10 AM primary (#10). Event #19 ($400 flights) has a Day 2 "
                 "Restart at 11:00 AM on Wed Dec 2, and its 11:10 AM Day 1 flight on Sun Nov 29 is the same morning as the "
                 "12:10 PM primary (#20). A restart applies only to a player who bagged "
                 "chips in an earlier flight, so the day plan treats these as conditional and does not model them. Before "
                 "relying on a primary, check whether any earlier flight was played."),
         source="https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html"),
    dict(id="F34", area="Wynn WPT", severity="High",
         title="The WPT schedule and the WPT structure PDF give different dates for the same events",
         detail=("Read on 2026-11-17. The schedule PDF lists a 'No Limit Hold'em Day 2' for the $800 NLH on Mon Nov 30 at 1:00 PM, "
                 "but the structure PDF gives that event Day 1A at 11 a.m. on Mon Nov 30 and Day 2 at 1 p.m. on Thu Dec 3. The "
                 "schedule also lists a 'No Limit Hold'em (2 Day)' $1,600 on Dec 9 at 11 a.m., while the structure PDF gives "
                 "the $1,600 NLH Day 1A on Thu Dec 3 and Day 2 on Sat Dec 5. The rows are reproduced as printed and not "
                 "corrected. The $800 row is not matched to a structure section for that reason. Confirm the date with the "
                 "poker room before any decision that depends on it."),
         source="https://cdn.wynnresorts.com/image/upload/v1750864036/visitwynn_pdfs_files/Poker/WPT/WPT_World_Championship_Structures.pdf"),
    dict(id="F35", area="Hotel terms", severity="High",
         title="The Wynn terms page cited for the resort fee is an expired 2025 offer; the cancellation term lives elsewhere",
         detail=("The earlier build cited https://www.wynnlasvegas.com/terms-and-conditions/850070 for Wynn's $55 resort "
                 "fee, parking and 48-hour cancellation. That page is a DINING CREDIT offer whose own text says a stay "
                 "booked under it 'must be completed on or before September 30, 2025', so it cannot substantiate a "
                 "November 2026 trip. The fee was re-verified on 2026-11-17 from the live Resort Policies page, which "
                 "still prints $55 plus tax, check-in 3 p.m. and check-out 12 p.m.; that page does not print a "
                 "cancellation window. Corrected 2026-11-17 on a second live read: the 48-hour window is NOT confined "
                 "to offer terms. The live Terms page (the same /terms-and-conditions/850070 URL) carries a "
                 "'CANCELLATION POLICY' section whose body reads 'cancellations must be received at least 48 hours "
                 "prior to arrival date or deposit (if applicable) will be forfeited', plus an early-departure penalty "
                 "of the departing night's rate and tax. The hotel row now records that general 48-hour term with the "
                 "Terms URL as its source, and notes that the same page also prints offer-specific date exceptions "
                 "that were not read one by one."),
         source="https://www.wynnlasvegas.com/terms-and-conditions/850070"),
    dict(id="F36", area="Hotel cost", severity="Medium",
         title="RESOLVED 2026-11-17: the booking engine does print an itemised total for the trip window; the $XXX cells were a rendering artefact",
         detail=("Superseded on the evening of 2026-11-17. This flag was written against the superseded 25 November - "
                 "2 December window, where the date picker returned every cell reading $XXX because prices load by "
                 "script after first paint, so no dated total could be read for those dates. Reopening the engine for "
                 "the window the trip is booked for (23-30 November 2026) returned the itemised panel and the $4,010.55 "
                 "checkout total described in F15. The lesson is kept on the register rather than deleted: the calendar "
                 "cells and the itemised panel can disagree, so no calendar cell is ever used as a price (F69). The "
                 "published starting-rate floor ($197.28) is still shown beside the quote and is still labelled a "
                 "floor, never a quote."),
         source="https://www.venetianlasvegas.com/booking?adults[]=2&arrival_date=2026-11-23&children[]=0&departure_date=2026-11-30&view=calendar"),
    dict(id="F37", area="Hotel cost", severity="Low",
         title="Caesars Palace and Horseshoe resort fees are now confirmed; their room-tax percentage is not",
         detail=("Closed on 2026-11-17 for the fee. The official Caesars booking page for each property prints a Hotel "
                 "Policies > Fees block: Caesars Palace 'Resort fees: $62.30 ($54.95 plus $7.35 tax)' with a '$100 per "
                 "day' deposit, and Horseshoe Las Vegas 'Resort fees: $56.63 ($49.95 plus $6.68 tax)' with a '$50 per "
                 "day' deposit, a $75 pet fee and a $30-per-day rollaway. Both pages add that 'Rates shown reflect the "
                 "lowest available rate and include applicable resort fees' and that the fee is not assessed for Diamond "
                 "and Seven Stars guests. What remains open: neither page prints a room-tax percentage for the rate, and "
                 "neither publishes a self-parking amount, so a true nightly cost is still not computed from "
                 "property-published components. The third-party spread that blocked this row earlier ($42, $49.95, "
                 "$54.95, $55, $62.30) is resolved: the $54.95/$49.95 figures are the pre-tax fees and the $62.30/$56.63 "
                 "figures are the same fees with tax."),
         source="https://www.caesars.com/book/hotel-calendar?dateSearchFormat=flexible-dates&flexibleMonth=December&propCode=clv"),

    
    dict(id="F39", area="Hotel cost", severity="Medium",
         title="Room-tax % is still blank in the property-published column for Wynn, Caesars, Horseshoe, Bellagio, MGM Grand and ARIA; a county per-property reference now sits beside each",
         detail=("Checked 2026-11-17 (session arena/5b8ce14d-poker3). No property page read this session prints a room-tax percentage "
                 "for its room rate. Wynn's terms page prints a $55 resort fee 'plus tax' with no percentage. Caesars and Horseshoe "
                 "print only the tax amount on their resort fee ($7.35 on $54.95; $6.68 on $49.95; both 13.38% to the cent). "
                 "The Clark County General Information Guide for Transient Lodging (July 2021 edition) lists per-property rows "
                 "that include Wynn/Encore, Caesars Palace, Bellagio, MGM Grand, ARIA and Bally's at 13.38% (Primary Gaming "
                 "Corridor), and its Appendix III chart prints 13.38% for a resort hotel in SD & PGC. Horseshoe is not listed under "
                 "its own name; Bally's, at the same street address (3645 Las Vegas Blvd S), appears at 13.38%, but the former name "
                 "is not treated as Horseshoe's own licence, so Horseshoe stays open. Only part of the guide was read (chunks 0 and "
                 "3-11 of 12); the rows for Wynn, Bellagio, MGM Grand and Venetian were not all read to their licence numbers and are "
                 "not quoted here. The guide is dated July 2021; the county's guidance page lists an April 2021 rate table as "
                 "'Updated', and no 2026 rate table was found, so the listing must be re-confirmed. DECISION NEEDED: the taxRate "
                 "column is blank by policy (tests enforce 'a figure the property printed'); the county figure is shown only as a "
                 "reference beside it. Whether a government per-property listing may fill that column is a user decision (see "
                 "suggestions). True nightly cost still needs a dated base rate from each property, which none of these six has published."),
         source="https://www.clarkcountynv.gov/adobe/assets/urn:aaid:aem:689ef54f-ec0d-4bb6-b8ea-05a82887561f/original/as/genl-info-guide-for-tles-july-2021.pdf"),
    dict(id="F51", area="Hotel cost", severity="High",
         title="Two official Venetian pages disagree on whether the resort fee is added to the rate or included in it",
         detail=("Partly resolved on 2026-11-17 by reading the resort-fee page itself, which the earlier pass had not "
                 "quoted. The Venetian's own Resort Fee page states: 'Rates include a daily Resort Fee of $55 plus tax "
                 "per night, payable upon check-in.' That page governs the fee and it supports the arithmetic this site "
                 "uses: the poker-suite starting rates are quoted before the fee, the $55 is chargeable on top, and the "
                 "floor is therefore ($119 + $55) x 1.1338 = $197.28 rather than a double-count. Two things stay open. "
                 "First, the booking calendar footnote says the opposite - 'Pricing shown is best available suite and "
                 "rate, includes daily resort fee, excludes taxes' - so one official page states the fee is added to the "
                 "rate and another states it is already in it. Second, neither page says which convention the "
                 "phone-only poker rate (EPOKR25) uses. The published floor keeps the conservative reading (fee added, "
                 "+$55 a night, about $300 over seven nights); if the poker rate proves to be fee-inclusive, the true "
                 "floor is about $154 a night, roughly $43 lower. Only a dated checkout total for the poker rate settles "
                 "it. The same caution applies to the Horseshoe calendar cells, whose own page says they include the "
                 "resort fee."),
         source="https://www.venetianlasvegas.com/resort/resort-fee.html"),
    dict(id="F55", area="Hotel cost", severity="Medium",
         title="The Horseshoe rate calendar printed two different grids five minutes apart on the same day",
         detail=("Both readings are kept in the rate log. At 01:26 UTC the December 2026 grid printed Dec 1 $449, "
                 "Dec 4 $219, Dec 5 $369, Dec 6 $249, Dec 7 $229, Dec 8 $169, Dec 9 $149, Dec 10 $359, Dec 11 $479, "
                 "Dec 12 $429, Dec 13 $56, Dec 18 $63, Dec 19 $219, Dec 25 $129, Dec 27 $149, Dec 30 $209 and Dec 31 "
                 "$529. At 01:31 UTC the same page printed $379, $189, $313, $214, $198, $148, $132, $305, $404, $363, "
                 "$55, $61, $189, $115, $132, $181 and $445 for the same dates. A flexible-month calendar cell is a "
                 "moving observation, not a held price, and this site does not average or pick between them. Any trip "
                 "budget built from these cells must be re-read on the day of booking. The Caesars Palace calendar, read "
                 "the same way twice, returned no price cells at all. F47 records the same behaviour on the Venetian "
                 "calendar; this flag is the Caesars-page instance, which matters because the Horseshoe cells are the "
                 "only dated room rates any reviewed property publishes for the trip window."),
         source="https://www.caesars.com/book/hotel-calendar?dateSearchFormat=flexible-dates&flexibleMonth=December&propCode=blv"),
    dict(id="F56", area="Wynn Signature Series", severity="Medium",
         title="The official Wynn Signature Series structures file is still a 'coming soon' placeholder (re-read 2026-11-19), so 38 rows cannot be confirmed",
         detail=("Read on 2026-11-17. The URL the site cites for Wynn Signature Series structures "
                 "(Wynn_Signature_Series_Structures.pdf) now returns only 'LAS VEGAS POKER / COMING SOON'. The series "
                 "schedule PDF, read at the same time, prints the dates January 11-24, 2027 and tells guests to 'Scan the "
                 "QR code for event structures'. There is therefore no readable official structure sheet for these 38 "
                 "rows today, and their single-entry, re-entry and add-on status correctly stays 'not verified' rather "
                 "than being inferred from the schedule. The schedule does print buy-in, guarantee, chips and level "
                 "length for most rows, and those columns are shown. Re-read on 2026-11-19 through the page reader: "
                 "the file still returns only 'LAS VEGAS POKER / COMING SOON' and the Wynn poker page still links to "
                 "it as the structures file, so the gap has not moved."),
         source="https://cdn.wynnresorts.com/image/upload/v1762299460/visitwynn_pdfs_files/Poker/Wynn%20Signature%20Series/Wynn_Signature_Series_Structures.pdf"),

    dict(id="F54", area="Trip plan", severity="High",
         title="Two of the seven planned nights (23 and 24 November) do not satisfy the published condition for the $119 poker-suite rate",
         detail=("Corrected 2026-11-17. The earlier text of this flag named 30 November, 1 December and 2 December, which "
                 "belonged to the superseded 25 November - 2 December window and are not part of the booked stay; the "
                 "finding is unchanged in substance and only the dates were wrong. Derived from two published documents, "
                 "not inferred. The Venetian poker-suite rate page requires 'six hours of active live cash gameplay or "
                 "buy in to a $300 or higher tournament for each night stayed', and failure to qualify means the "
                 "prevailing rate is charged. The trip is 23-30 November 2026, so the seven nights that must qualify are "
                 "23, 24, 25, 26, 27, 28 and 29 November. The day plan places a $400, $300, $600, $600 and $300 primary "
                 "on 25, 26, 27, 28 and 29 November, which satisfy it, and a $200 primary on 23 and 24 November, which do "
                 "not; those two nights are therefore not covered by the published condition. The page does not say "
                 "whether an entry counts on the day it is paid or on every night of a multi-day event, so no re-pricing "
                 "amount is claimed - the room must be asked. One $300+ alternative is published on each of those two "
                 "dates: the $400 No Limit Hold'em 1A at 11:10 AM on 23 November and 1B at 11:10 AM on 24 November, both "
                 "multi-flight, so both sit outside the single-entry screen and would also require playing into a later "
                 "day. Choosing between a $200 buy-in with a possibly repriced room, a $400 multi-flight entry, or six "
                 "hours of live cash play is a decision this site shows but does not make."),
         source="https://www.venetianlasvegas.com/resort/casino/poker/suite-rates.html"),
    dict(id="F40", area="Monitoring", severity="Low",
         title="The build sandbox cannot reach the venue hosts; live reads were made by the page reader",
         detail=("Every official venue and property host refused or timed out from the build sandbox, so the fetches in "
                 "this pass were made by the assistant's page reader one URL at a time. This is recorded so a reader "
                 "understands why an automated checks run can report 'unreachable' for a URL that loads normally in a "
                 "browser."),
         source="https://github.com/karagemop466-tech/Poker3/actions/workflows/checks.yml"),
    dict(id="F41", area="DeepStack Extravaganza NYE schedule", severity="Low",
         title="The NYE schedule page prints the year 2025 on its December 26 rows",
         detail=("The official DeepStack Extravaganza NYE page is headed 'December 24, 2026 - January 10, 2027', but its "
                 "three December 26 rows read 'Saturday, December 26, 2025'. December 26 is a Saturday in 2026 (not in "
                 "2025, when it was a Friday), so the weekday is right and the year is the typo. The rows are listed with "
                 "the series dates and the printed year is flagged rather than corrected. All 15 NYE structure sheets "
                 "have since been read (see F11), so the printed year is the only open point on these rows."),
         source="https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-dec-2026.html"),
    # F43 rather than F38: main already defines F38 (and F17) for this exact finding.
    # Reusing the number would give two flags in one register the same id.
    dict(id="F43", area="Schedule", severity="Low",
         title="The Caesars page gives a general session length, not an event finish time",
         detail=("The official Caesars Palace poker-tournament page says 'Most sessions finish in four to six hours.' That is a "
                 "general statement about its tournaments, not a published finish time for any event. The six-hour planning "
                 "assumption for every room therefore remains an assumption."),
         source="https://www.caesars.com/las-vegas/explore/casino/poker-tournaments-las-vegas-strip"),
    dict(id="F48", area="Venetian DeepStack NYE", severity="Medium",
         title="Two NYE events share one 11:10 AM start on January 4, 2027",
         detail=("The official DeepStack Extravaganza NYE schedule page lists Event #20 ($1,600 MSPT Day 2 Restart) and "
                 "Event #27 ($250 No Limit Hold'em 1A $75K GTD) at 11:10 AM on the same day. Every other Day 2 or Day 3 "
                 "restart row in both Venetian series is published at 10:00, 11:00 AM or 12:00 PM, never at 11:10 AM, "
                 "while every 1A/1B/1C starting flight is published at 11:10 AM or 5:10 PM. The restart time therefore "
                 "looks like a transcription slip on the official page rather than a genuine 11:10 AM restart, but this "
                 "cannot be settled from the repository's copy, so the row is published exactly as the official page has "
                 "it and is not adjusted. Confirm against the official page before sequencing anything on that date."),
         source="https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-dec-2026.html"),
    dict(id="F49", area="Day 2 / final-table rows", severity="Medium",
         title="Resumption rows carry no late-registration cut-off and no estimated finish",
         detail=("45 rows are resumptions of a field that closed on an earlier day: Day 2, Day 3, Day 4 and Day 5 restarts "
                 "and streamed final tables at the Venetian and at Wynn. Earlier in this build those rows printed the "
                 "structure sheet's late-registration clause and the session length derived from it, but both belong to "
                 "the earlier day's flight, not to the restart: registration closed when that day ended, and no venue "
                 "publishes a restart finish time. On the LIPS streamed final table this produced a 7:00 PM start with a "
                 "'late registration until 4:55 PM' that closed three hours earlier, and an estimated finish at 6:30 PM "
                 "the following afternoon. Both fields are now blank on those rows, with the reason recorded on the row. "
                 "Four NYE rows that had been misclassified as restarts were also corrected: '$250 No Limit Hold'em "
                 "1A/1B/1C/1D $75K GTD - Day 1 payouts with 5% advancing to Day 2' are starting flights, not resumptions, "
                 "because their 'Day 2' mention sits in the trailing payout clause. Continuation detection is now one "
                 "shared rule instead of four separate regexes, two of which could not see a bare 'Final Table' row."),
         source="https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html"),
    dict(id="F50", area="Venetian DeepStack NYE", severity="Low",
         title="Three NYE sheets print one late-registration clause covering two start times",
         detail=("Sheets dse_dec_2026-structure_4, _5 and _15 print a single late-registration clause with two clock times, "
                 "for example '6 levels + break (~5:25 PM or ~8:25 PM)', because one sheet covers more than one start "
                 "flight. The builder previously took the first clock time on every row, which put a 5:25 PM cut-off on the "
                 "6:10 PM row and closed registration before that event began. The row now takes the earliest printed time "
                 "that still falls after its own start, so the 3:10 PM row keeps 5:25 PM and the 6:10 PM row takes 8:25 PM. "
                 "Both times are printed on the sheet, so this disambiguates published values rather than inventing one; "
                 "where no printed time falls after a row's start, no cut-off is published at all. Sheet _5 prints "
                 "'5:25 PM or 12:25 PM' and no row in this schedule would take the 12:25 PM figure, so confirm the "
                 "12:25 PM reading with the poker room."),
         source="https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-dec-2026.html"),
    dict(id="F52", area="Bellagio", severity="Low",
         title="The Bellagio Saturday structure sheet prints a blind level as 200-4300",
         detail=("The sheet linked from the Bellagio poker-room page prints the third blind level of the Saturday event as "
                 "'200-4300', which does not fit the level ladder used by the neighbouring levels. Re-read 2026-11-17; the "
                 "value is reported exactly as printed and no level data is derived from it."),
         source="https://assets.contentstack.io/v3/assets/bltc6ce635bc4868eb2/blt6d47974bf5a7d9b6/6af491a391a6e8e4230c9e07/mgm-bellagio-poker-saturdays-$1000-nlh.pdf"),
    dict(id="F53", area="Venetian NYE", severity="Low",
         title="NYE structure_14 header names only Day 1B & 1D although three flights link to it",
         detail=("The official NYE schedule links the 5:10 PM flights on January 7, 8 and 9, 2027 (Day 1B, 1D and 1F) to "
                 "dse_dec_2026-structure_14.pdf, but the sheet's flight header prints 'Day 1B & 1D @ 5:10 PM with Day 2 @ "
                 "12:00 PM' without Day 1F. The structure_14 rules are applied to all three linked rows and the header "
                 "mismatch is flagged here. Read 2026-11-17."),
         source="https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_dec_2026-structure_14.pdf"),
    dict(id="F57", area="Hotels", severity="High",
         title="30 November and 1 December 2026 print no figure in any reading, so a stay spanning them cannot be booked online",
         detail=("The official Venetian booking calendar was read on 2026-11-17 with two different stay windows open. "
                 "Every date in the captured range printed a figure in at least one of the two renderings except two: "
                 "30 November and 1 December were blank in both. An arrival date of 30 November returns the message "
                 "\u201cWe're sorry, but there is no availability for some of your selected dates. Please select different "
                 "dates to proceed.\u201d No rate, no suite and no checkout total can therefore be obtained online for a stay "
                 "that includes either night. This is why the recommended trip is 23 November to 30 November and not 25 "
                 "November to 2 December: the longer window spans two nights the engine will not price, so it cannot be "
                 "booked as one stay. This finding does not depend on treating a calendar cell as a price \u2014 F47 records "
                 "that the cells move with the query, and F28 that they disagree with the quote. It is narrower than "
                 "either: across two independent renderings these were the only two dates that printed no figure at all. "
                 "Confirm by phone on 866.255.8936 before booking either night."),
         source="https://www.venetianlasvegas.com/booking?adults[]=2&arrival_date=2026-11-30&children[]=0&departure_date=2026-12-02&view=calendar"),

    dict(id="F58", area="Venetian NYE", severity="Medium",
         title="NYE Event #29 CES-badge discount is $10 on the schedule page but $20 on the structure sheet",
         detail=("The official DeepStack Extravaganza NYE schedule row for Event #29 (Jan 6, 2027, 5:10 PM) prints "
                 "'Show Your CES Badge - $10 RAKE DISCOUNT', but the event's structure sheet (dse_dec_2026-structure_2.pdf) "
                 "prints: 'any player who shows their CES badge at the time of registration will receive a $20 discount on "
                 "house fees for a total buy in of $180 instead of $200'. Both are official; neither was adjusted. "
                 "Confirm the discount with the poker room before relying on it."),
         source="https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_dec_2026-structure_2.pdf"),
    dict(id="F59", area="Venetian NYE", severity="Medium",
         title="MSPT (Event #20) Day 2 restart is 11:10 AM on the schedule page but 11:00 AM on the structure sheet",
         detail=("The official NYE schedule prints the Event #20 Day 2 Restart on Jan 4, 2027 at 11:10 AM, while the "
                 "event's structure sheet (dse_dec_2026-structure_8.pdf) prints 'Day A+B+C @ 11:10 AM with Day 2 @ 11:00 AM'. "
                 "The stored row keeps the schedule time (11:10 AM) and the sheet excerpt is recorded on the row's rules. "
                 "F48 flags the same restart time from a different angle (two events share the 11:10 AM slot); the sheet "
                 "evidence here shows the printed restart is 11:00 AM. Confirm the restart time with the poker room."),
         source="https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_dec_2026-structure_8.pdf"),
    dict(id="F71", area="MGM Grand", severity="Medium",
         title="MGM Grand's official poker page and its official weekly schedule PDF print different start times",
         detail=("Both pages were re-read on 2026-11-17. The poker-room page states 'Daily Texas Hold'em Tournaments "
                 "11:00am, 7:00pm and 11:00pm'. The weekly schedule PDF linked from that same page prints 11:10am, "
                 "7:10pm and 11:10pm on all seven days. The published rows follow the PDF. The difference is ten "
                 "minutes, so it cannot change whether an event is reachable, but a player who arrives on the strength "
                 "of the HTML time would miss the first ten minutes. The PDF carries its own reason to distrust its "
                 "dates: it is titled 'MGM Grand August Tournament Schedule' (F07). Confirm the current slot with the "
                 "poker room before travelling."),
         source="https://mgmgrand.mgmresorts.com/en/casino/poker-tables.html"),
    dict(id="F72", area="MGM Grand", severity="Low",
         title="MGM Grand's only printed entry-policy statement for the $120 daily assumes five or more entries",
         detail=("Verified on 2026-11-17 from the footnote at the foot of the published weekly schedule PDF: 'Sunday "
                 "through Friday - Players with 5 entries or more in $120 Daily Tournaments will receive one (1) free "
                 "entry to the Saturday $150 NLH $2,000 Guarantee'. That sentence is the only entry-policy statement "
                 "the room publishes for these events and it assumes a player takes five or more entries, so the $120 "
                 "daily is recorded as a multi-entry format and kept out of the single-entry path. It is not a cap: no "
                 "maximum number of entries per player is printed anywhere on the sheet."),
         source="https://assets.contentstack.io/v3/assets/bltc6ce635bc4868eb2/blt5f25277b8918da08/mgm-grand-casino-poker-tournament_schedule.pdf"),
    dict(id="F73", area="Caesars Palace", severity="Medium",
         title="The Caesars Palace daily schedule is now read from its official flyer; the Horseshoe schedule is still published only inside a dated marketing article",
         detail=("Updated on 2026-11-18. The official Caesars Palace casino page links a 2026 daily No-Limit Hold'em flyer "
                 "('View Schedule'). That flyer prints the four Caesars Palace start times (10 AM, 2 PM, 6 PM, 9 PM), the "
                 "buy-in of each, the $1,000 guarantee, 20,000 chips, 20-minute levels, a $50 optional add-on at the first "
                 "break, re-entry within the first break, and registration closing at the start of level seven. The four "
                 "Caesars Palace rows now take the flyer as their source. The 17 July 2026 marketing article still says every "
                 "Caesars Palace event is $100; the flyer prices the 2 PM and 9 PM events at $160 (see F90). The Horseshoe "
                 "start times (9 AM, 11 AM, 2 PM, 5 PM, 8 PM, 11 PM) appear only in that article; its buy-ins are not printed "
                 "there, so the Horseshoe rows stay blank (F20)."),
         source="https://www.caesars.com/content/dam/empire/clv/casino/poker/tournament-schedule/clv-poker-daily-nlh-tournament-flyer-2026.pdf"),
    dict(id="F90", area="Caesars Palace", severity="Medium",
         title="The 2 PM and 9 PM Caesars Palace events are $160 buy-ins on the official flyer; the marketing article and the earlier rows say $100",
         detail=("Found on 2026-11-18. The official flyer lists the Caesars Palace daily No-Limit Hold'em events as 10 AM $100, "
                 "2 PM $160, 6 PM $100 and 9 PM $160, each with a $1,000 guarantee, and prices the $160 events at $115 to the "
                 "prize pool and $45 maintenance fee. The 17 July 2026 article says every event is $100, and the earlier rows "
                 "followed it. The rows are corrected to the flyer, which is the room's own schedule document. Both sources are "
                 "official-domain pages; the article is the less specific one. All four events stay in the multi-entry category "
                 "(re-entry within the first break and an optional $50 add-on), so the correction does not change the single-entry list. "
                 "Check the buy-in printed on the booking or sign-up sheet before paying."),
         source="https://www.caesars.com/content/dam/empire/clv/casino/poker/tournament-schedule/clv-poker-daily-nlh-tournament-flyer-2026.pdf"),
    dict(id="F91", area="Walking routes", severity="Low",
         title="The official Venetian poker page places the room at The Palazzo, level 2, Grand Canal Shoppes; the walking captures measure to the Venetian",
         detail=("Read on 2026-11-18 from the Venetian poker page: 'LOCATION: The Palazzo, level 2, Grand Canal Shoppes', with "
                 "directions from the Venetian lobby (escalator from the Waterfall Atrium) and from the Palazzo lobby (self-parking "
                 "elevators). The Google Maps walking captures on file (F84) and the 'Venetian' venue row use the resort address. "
                 "No minute value is changed by this flag. Before a walking-limit decision, re-measure to the room's own entrance on "
                 "level 2 of Grand Canal Shoppes."),
         source="https://www.venetianlasvegas.com/resort/casino/poker.html"),
    dict(id="F92", area="Change monitoring", severity="Low",
         title="Re-read 2026-11-19: the flagged Venetian poker-page change is the series banner rolling from WPT Fall Festival to DeepStack Extravaganza IV; no tournament, rate or policy value on the page changed",
         detail=("The scheduled re-check (site/checks.json, run 2026-11-18T20:24:36Z) recorded a visible-text change on "
                 "https://www.venetianlasvegas.com/resort/casino/poker.html. The saved daily text snapshots show what changed. "
                 "The 2026-11-17 snapshot reads 'Current Series: WPT Fall Festival October 28 - November 15, 2026 Nearly $4 Million'. "
                 "The 2026-11-18 and 2026-11-19 snapshots read 'Current Series: DeepStack Extravaganza IV November 16 - December 23, 2026 "
                 "More than $3.6 Million in guaranteed tournament prize pools'. That is the only text difference between those two days. "
                 "Manual re-read on 2026-11-19 (live read) shows the same DeepStack Extravaganza IV banner, the Palazzo level 2 location (F91), "
                 "'Open 24 Hours', the Player Suite rates link and the complimentary self-parking terms (three hours of play for non-registered guests). "
                 "Limit of this check: the monitor stores only a hash of the 20:24 UTC run, not its text, so the match is by content, "
                 "not proven byte for byte. Nothing on the page is a tournament value, so no row changed. The poker page still does not print "
                 "a dated room rate for a given night; the Venetian rate and fee flags (F51, F66, F69) are unchanged."),
         source="https://www.venetianlasvegas.com/resort/casino/poker.html"),
    dict(id="F93", area="Hotels", severity="High",
         title="Pre-payment reconfirmation on 2026-11-19: the Venetian booking engine still prints no checkout total for 23-30 November, so no current nightly price is on record",
         detail=("Re-read live on 2026-11-19 (UTC). The official booking link for 2 adults, arrival 23 Nov 2026, departure 30 Nov 2026 "
                 "returned only the page text 'Your Venice meets Vegas getaway is loading', with no rate, resort fee, tax or checkout "
                 "total, the same result as the 2026-11-17 and 2026-11-18 attempts recorded in research/reread_2026-11-19.md. The "
                 "$4,010.55 checkout total therefore remains the dated 2026-11-17 observation in the rate log, not a price for today. "
                 "The suite-rate page (re-read 2026-11-19, unchanged) still states that the $119 and $209 poker rates are booked by "
                 "telephone with code EPOKR25, require six hours of active live cash play or a buy-in to a $300-or-higher tournament for "
                 "each night, and carry a $55 resort fee per night stayed. Whether EPOKR25 applies to these dates is not confirmed (F66). "
                 "Before any nonrefundable payment, ask the poker room (702.414.7657, lv_cas_poker@venetianlasvegas.com, both printed on the "
                 "suite-rate page) for the all-in total in writing and record the answer with its date."),
         source="https://www.venetianlasvegas.com/resort/casino/poker/suite-rates.html"),
    dict(id="F94", area="Day plan", severity="High",
         title="On five of the seven trip days the published fallback was the same event the site publishes as an "
               "impossible sequence against that day's primary (found and fixed 2026-11-19)",
         detail=("Found on 2026-11-19 by comparing site/data.json against its own stated fallback rule. The rule said the "
                 "fallback 'starts after the primary's estimated finish plus a 30-minute transfer', but the builder selected "
                 "the next-ranked candidate without applying that test. On 25, 26, 27, 28 and 29 November 2026 the fallback "
                 "therefore started inside the primary's estimated session, and the same pair also appeared under "
                 "planConflicts as an 'impossible sequence' on the schedule page. One block said the pair cannot be played; "
                 "the other offered it as the plan. No official value was wrong and no tournament, fee, guarantee, hotel or "
                 "walking figure changed. The fix adds an explicit sequence status to every fallback: 'replaces the primary' "
                 "where it starts before the primary's estimated finish plus the transfer, and 'playable after the primary' "
                 "where it starts later, each with a plain-language note on the schedule page. The stated rule now matches "
                 "the code, and tests/test_fallback_sequencing.py fails if any fallback is again described as playable after "
                 "an event it overlaps. This does not resolve the underlying limit: no venue publishes finish times (F16), "
                 "so the replaced-or-after judgement still rests on an estimate."),
         source="https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html"),
    dict(id="F96", area="Integration spot check", severity="Info",
         title=("2026-11-19 spot check: F92 re-read and cleared, F31 and F16 reconfirmed, F56 still open, and the "
                "official booking engine still returns no checkout total"),
         detail=("An independent read of the official pages on 2026-11-19 by the integration session "
                 "(arena/3dae36ec-poker3), after the automated re-check could only hash page text. This is the same "
                 "engine read recorded as F93 above and adds only what F93 does not cover. "
                 "(1) F92 cleared: the Venetian poker-room page still places the room at The Palazzo, level 2, Grand "
                 "Canal Shoppes, open 24 hours, and its DeepStack Extravaganza IV block still reads 'November 16 - "
                 "December 23, 2026' and 'More than $3.6 Million in guaranteed tournament prize pools'. No published "
                 "value behind the 2026-11-18 wording change moved. "
                 "(2) F31 reconfirmed, not resolved: neither that page nor the DSE IV schedule page prints a maximum "
                 "number of entries per player, a rebuy clause, an add-on clause or freezeout wording. "
                 "(3) F16 reconfirmed: the DSE IV schedule page still prints no finish time. "
                 "(4) F56 still open: the official Wynn Signature Series structures link still resolves to a page "
                 "whose only text is 'LAS VEGAS / POKER / COMING SOON'. "
                 "(5) The Wynn WPT World Championship schedule PDF was re-read in both chunks and every official "
                 "row is already published: no row is missing and none was invented. "
                 "(6) The player-parking page and the Caesars/Horseshoe Strip article were re-read and every figure "
                 "the site publishes from them still matches verbatim, including the $20 registered-guest fee, the "
                 "three-hour waiver and the 9 a.m. earliest Horseshoe start behind F17. "
                 "(7) The DSE IV schedule page's 94 rows were transcribed again and matched the catalog on date, start "
                 "time and structure sheet; four paraphrased names were corrected to the page's own wording. "
                 "No value was changed or inferred by this read."),
         source="https://www.venetianlasvegas.com/resort/casino/poker/suite-rates.html"),
    dict(id="F74", area="Venetian DSE NYE", severity="Low",
         title="Eleven NYE rows carried a 'structure sheet not read' label after all 15 sheets had been read",
         detail=("Found and fixed on 2026-11-17. Eleven NYE rows sat in the category 'Unverified - structure sheet not "
                 "read' even though all 15 NYE sheets were read in full that day and each of those rows already "
                 "carried an excerpt quoted from its own sheet. Each row now takes the category its own sheet supports: "
                 "the sheet-screened candidate list where the sheet prints no re-entry clause, the extra-spend list "
                 "where it does. No money, date or time value changed. The error is published here because a wrong "
                 "label on a verified row is the failure this page exists to surface."),
         source="https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-dec-2026.html"),
    dict(id="F75", area="Venetian DSE NYE", severity="Medium",
         title="NYE Event #29 was listed as a single-entry candidate although its own sheet prints re-entry wording",
         detail=("Found by a new automated label check on 2026-11-17 and fixed. NYE Event #29 ($200 NLH Bounty, "
                 "Wednesday 2027-01-06 at 5:10 PM, CES-badge $10 rake discount) sat in the sheet-screened candidate "
                 "category while its own row already carried the structure-2 excerpt: 'The $20 discount can be applied "
                 "to the initial entry or any subsequent re-entry'. A sheet that contemplates a subsequent re-entry "
                 "cannot sit in the single-entry candidate list, so the row is now in the extra-spend category. No "
                 "money, date or time value changed. Structure 2 is shared by nine bounty events, so the same wording "
                 "governs all of them; the other eight were already correctly placed."),
         source="https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_dec_2026-structure_2.pdf"),
    dict(id="F76", area="Wynn WPT", severity="Low",
         title="Six WPT rows said 'entry rules not yet read' while quoting the entry rule from the sheet",
         detail=("Found and fixed on 2026-11-17. The six NLH flight rows whose structure sections were matched that "
                 "day carried both the registration clause quoted from the official structures PDF and the older note "
                 "'entry rules not yet read'. The note now states that the rules were read from the structure sheet. "
                 "No value changed; the contradiction was in the prose only."),
         source="https://cdn.wynnresorts.com/image/upload/v1750864036/visitwynn_pdfs_files/Poker/WPT/WPT_World_Championship_Structures.pdf"),
    dict(id="F78", area="Venetian booking engine", severity="Medium",
         title="The same trip-window query returned two different suites and totals within about 20 minutes",
         detail=("Observed on 2026-11-17, not inferred. The official booking engine was opened twice for the "
                 "identical query - 2 adults, arrival 2026-11-23, departure 2026-11-30, seven nights. The read at "
                 "about 21:54 UTC returned a venetian Newly Remodeled Luxury King suite with an estimated cost of "
                 "stay of $4,010.55 (nightly rates 164.25/164.25/201.75/231.75/1,649.25/554.25/186.75, taxes "
                 "$473.30). The read at about 22:15 UTC returned a palazzo Luxury King suite with an estimated "
                 "cost of stay of $3,823.46 (nightly rates 204.25/204.25/286.75/406.75/1,119.25/561.75/204.25, "
                 "taxes $451.21) - $187.09 less, with no change to the dates or the party size. Both quotes "
                 "reconcile exactly to (rate + $55 resort fee) x 1.1338, so neither is arithmetic error: the "
                 "engine's best-available offer moved between requests. Both are logged as dated observations in "
                 "the rate log and neither replaces the other. For a like-for-like comparison, record the suite "
                 "name, the read time and the itemised breakdown, and re-read the engine immediately before any "
                 "nonrefundable payment."),
         source="https://www.venetianlasvegas.com/booking?adults[]=2&arrival_date=2026-11-23&children[]=0&departure_date=2026-11-30&view=calendar"),
    dict(id="F60", area="Wynn WPT", severity="Medium",
         title="The $1,100 PLO structure sheet's printed buy-in components total $1,105, not $1,100",
         detail=("The WPT World Championship structure sheet for the $1,100 PLO (Tuesday Dec 1, 1 p.m.) prints the buy-in "
                 "split as a $975 prize pool with fees of $85 and $45. The printed components sum to $1,105, five dollars "
                 "more than the printed $1,100 buy-in on the schedule. The row reproduces the schedule buy-in and the rule "
                 "panel reproduces the split as printed; nothing is adjusted. Confirm the amounts with the poker room."),
         source="https://cdn.wynnresorts.com/image/upload/v1750864036/visitwynn_pdfs_files/Poker/WPT/WPT_World_Championship_Structures.pdf"),
    dict(id="F77", area="Wynn WPT", severity="High",
         title="Six published WPT fee splits and one registration clause were paraphrases, not the printable text",
         detail=("Corrected 2026-11-17 by reading the official structures PDF in full (all eight chunks). Five WPT rows "
                 "printed the fee split as '$525 of every $600 buy-in is the prize pool and $75 is withheld in fees'. "
                 "That sentence does not appear anywhere in the document. The document prints a single line for those "
                 "events: '$600 Buy-in = $510 (Tournament Prize Pool) + $65 (Tournament Fee) + $25 (Poker Staff Service "
                 "Charge)', and it prints '$400 Buy-in = $337 (Tournament Prize Pool) + $45 (Tournament Fee) + $18 "
                 "(Poker Staff Service Charge)' for the $400 PLO. The $1,100 PLO split was already correct. Separately, "
                 "the Prime Championship rows carried a quoted sentence ('A player may play a maximum of one (1) starting "
                 "flight...') and a 'first entry = $1,000 + $100' prize line that the document does not contain; the "
                 "document prints 'One (1) Entry and One (1) re-entry for each starting flight will be available until "
                 "the start of level 10 (approximately 6:45 p.m.)'. Every excerpt now quotes the document word for word, "
                 "the paraphrase is recorded here rather than deleted silently, and no money value, date or start time "
                 "changed: only the quoted text and the rule status did. No row became single entry."),
         source="https://cdn.wynnresorts.com/image/upload/v1750864036/visitwynn_pdfs_files/Poker/WPT/WPT_World_Championship_Structures.pdf"),
    dict(id="F69", area="Hotels", severity="Medium",
         title="The engine's calendar cells for 23-30 November are not the quote for the same nights",
         detail=("On 2026-11-17 the booking calendar printed $165, $165, $190, $210, $1,155, $425 and $180 for the nights of "
                 "23 to 29 November, under a footnote that says its prices include the daily resort fee. The itemised quote for "
                 "the same stay, read the same day, printed a room rate of $164.25, $164.25, $201.75, $231.75, $1,649.25, $554.25 "
                 "and $186.75 on those nights, plus a $55 resort fee on each night. Rate plus fee is higher than the cell on every "
                 "night (for example $165 against $219.25 on 23 November), so the calendar cell is not the price the engine charges. "
                 "The dashboard uses the itemised quote and never a calendar cell as a nightly price. Confirm the price for the "
                 "chosen dates on the booking screen or by phone (866.255.8936) before paying."),
         source="https://www.venetianlasvegas.com/booking?adults[]=2&arrival_date=2026-11-23&children[]=0&departure_date=2026-11-30&view=calendar"),
    dict(id="F66", area="Hotels", severity="High",
         title="The $119 poker rate is phone-only and does not appear in the booking-engine quote",
         detail=("The official poker-room rate page says poker suite rates 'start as low as $119 and $209 and can be higher'. "
                 "They are booked by calling 866.255.8936 with code EPOKR25 and require six hours of active live cash play, or a "
                 "buy-in to a $300-or-higher tournament, for each night stayed, completed before 2 a.m. on the last night; a night "
                 "that fails is re-priced at the prevailing rate. The 23-30 November engine quote of $4,010.55 ('Book Direct: Up to "
                 "25% Off') does not show the code. The $197.28 a night floor in the trip profile is computed from published "
                 "components and is not a quote. Ask the poker room whether EPOKR25 applies to these dates and what the all-in "
                 "total would be, then record the answer as a dated rate-log entry."),
         source="https://www.venetianlasvegas.com/resort/casino/poker/suite-rates.html"),
    dict(id="F67", area="Walking routes", severity="Medium",
         title="Venetian to Bellagio: an earlier 27-minute read conflicts with a second read of 21 minutes on the same day (see F84)",
         detail=("On 2026-11-17 the Google Maps walking card from 3355 S Las Vegas Blvd (The Venetian) to the Bellagio Poker Room, "
                 "3600 S Las Vegas Blvd, read 27 minutes for 1.1 miles via Las Vegas Blvd S. The driving card for the same pair read "
                 "8 minutes. The walking card does not print its mode label; the link requested travelmode=walking. The reverse pair, "
                 "Bellagio Hotel & Casino to The Venetian, read 21 minutes (0.9 mile) the same day, which matches the stored route. "
                 "The day plan uses only the venue-to-Venetian direction, so a Venetian-to-Bellagio transfer is understated by six "
                 "minutes. The 30-minute limit is still met (27 minutes). Re-read the pair on a second day before relying on either figure. "
                 "UPDATE 2026-11-17 (session d3a4c0f8): a second walking-mode read of the same pair returned 21 minutes (0.9 mile) via Las Vegas Blvd S "
                 "and 25 minutes (1.1 miles) via Las Vegas Blvd S and Bellagio Dr, and the stored value is now 21. The 27-minute card has no saved capture, "
                 "so the conflict stays open; see F84 for the raw record."),
         source="https://www.google.com/maps/dir/?api=1&origin=3355+S+Las+Vegas+Blvd,+Las+Vegas,+NV+89109&destination=Bellagio+Poker+Room,+3600+S+Las+Vegas+Blvd,+Las+Vegas,+NV+89109&travelmode=walking"),
    dict(id="F68", area="Publishing", severity="Low",
         title="RESOLVED 2026-11-17: stale hotel, rate and route files were feeding the sheet-verification page",
         detail=("site/data/hotels.json, site/data/rates.json and site/data/routes.json were dated 2026-11-16, were written by no script, "
                 "and were not read by any dashboard page — but scripts/build_addendum.py did read hotels.json, rates.json and "
                 "routes.json, and it generates site/sheets.html, which is a page in the site navigation. That page therefore "
                 "published 2026-11-16 data: 14 retired FL-prefixed flags instead of the live 72-item F register, 5 of the 8 "
                 "hotels, and 13 of the 15 walking routes with every walking time blank. The three files are deleted and "
                 "build_addendum.py now reads site/data.json and the two data modules only, so it cannot drift again. "
                 "site/data.json is the only current data file. Kept on the register as the record of the defect."),
         source="https://github.com/karagemop466-tech/Poker3/blob/main/scripts/build_addendum.py"),
    dict(id="F79", area="Strip poker rooms", severity="Medium",
         title="Planet Hollywood's poker room is no longer open (closed 31 January 2026), so it has no rows on this site",
         detail=("Re-read 2026-11-17 (session arena/5b8ce14d-poker3). The official Caesars poker-tournaments page (dated 17 July 2026) "
                 "names only Caesars Palace and Horseshoe Las Vegas as Caesars poker rooms with daily tournament schedules, and "
                 "Planet Hollywood's own poker page could not be read (HTTP 500 on 2026-11-17). The closure is a Caesars Entertainment "
                 "statement reported by the Las Vegas Review-Journal on 28 January 2026 (https://www.reviewjournal.com/business/casinos-gaming/"
                 "inside-gaming-strip-casino-to-close-poker-room-3612434/): the room would not operate after 31 January, and its operations "
                 "were consolidated into Caesars Palace and Horseshoe. Any Planet Hollywood tournament listing found online is therefore not used. "
                 "Flamingo is also absent from the official Caesars article; a third-party closure list dates its poker-room closure to "
                 "September 2021, which this site does not treat as verified."),
         source="https://www.caesars.com/las-vegas/explore/casino/poker-tournaments-las-vegas-strip"),
    dict(id="F80", area="Strip poker rooms", severity="Medium",
         title="Resorts World Las Vegas: no official poker schedule could be read, and third-party sources disagree on its tournaments",
         detail=("Checked 2026-11-17 (session arena/5b8ce14d-poker3). Official rwlasvegas.com pages read: the poker-invite e-mail page "
                 "(no schedule); /gaming/poker-room/poker-room-dining/ (dining only); /gaming/casino-events/ (promotions, no poker "
                 "tournament). /poker, /casino/poker/ and /poker-room/ returned no page. Third-party pages disagree on times and buy-ins "
                 "for Resorts World's tournaments (PokerNews 2024, Vegas Advantage 2025, CardPlayer, Bet-NV 2023, PokerAtlas, "
                 "Somuchpoker), and none is official, so no Resorts World row is published. Its poker room is a candidate to add "
                 "once its official poker page is reached. A press search result (casino.org / Vital Vegas, March 2026; article not fetched) reports "
                 "the resort saying the poker room will close on 30 March 2026. No official statement was retrieved in this pass, so the closure is unverified."),
         source="https://www.rwlasvegas.com/gaming/casino-events/"),
    dict(id="F81", area="Hotel cost", severity="Medium",
         title="MGM Resorts booking pages served the same price grid on two different property URLs",
         detail=("Read live on 2026-11-17 by session 58e42dbd. The MGM Grand room booking page, opened with the MGM King "
                 "picker and 2 guests, printed a November 2026 calendar: 22 Nov $84, 23 Nov $84, 24 Nov $84, 25 Nov "
                 "$84, 26 Nov $149, 27 Nov $349, 28 Nov $149, 29 Nov unavailable, 30 Nov $649. The Bellagio booking "
                 "page, opened in the same session on its own URL, printed a grid containing the same run of figures "
                 "(22-25 Nov $84, 26 Nov $149, 27 Nov $349, 28 Nov $149, 30 Nov $649) alongside Bellagio-only values "
                 "on other nights (17 Nov $309, 19 Nov $249). Both pages carry a resort picker and a shared cart, so "
                 "the most likely explanation is that the grid renders whichever property the booking session has "
                 "selected, not necessarily the URL's property. Consequence for this project: a cell from an MGM "
                 "Resorts booking URL cannot be attributed to a property without the property name printed beside it. "
                 "The MGM Grand cells are logged with the room type the page names in its own picker ('Price on "
                 "calendar for MGM King'); the Bellagio cells are deliberately NOT logged as a Bellagio rate and its "
                 "room rate stays blank. Anyone re-reading either page must confirm the selected property first. This "
                 "was renumbered twice as other sessions published their own flags on main while this branch was open, and "
                 "is now F81; flag ids are kept unique across the whole repository, not per session."),
         source="https://bellagio.mgmresorts.com/book-room?property=bellagio&resort=66964e2b-2550-4476-84c3-1a4c0c5c067f"),
    dict(id="F82", area="Venetian series pages", severity="Low",
         title="RESOLVED 2026-11-19: the DeepStack landing page again labels DeepStack Extravaganza IV as the Current Series",
         detail=("The official DeepStack Poker Series landing page was re-read on 2026-11-17 (session arena-1bbee97f), two days "
                 "after the festival's printed end date, and still heads its list with 'Current Series: WPT Fall Festival, "
                 "October 28 - November 15, 2026', while DeepStack Extravaganza IV (November 16 - December 23, 2026) is "
                 "labelled 'Next Series'. The series dates themselves agree with the DSE IV schedule page and the series is "
                 "live, so only the current/next label is stale. No published value depends on the label; recorded for manual "
                 "review so a reader does not conclude DSE IV has not started. Renumbered twice as other sessions published "
                 "F81 first: flag ids are kept unique across the whole repository. RESOLVED 2026-11-19: the landing page "
                 "was re-read live and now heads the list with 'Current Series: DeepStack Extravaganza IV, November 16 - "
                 "December 23, 2026', followed by 'Next Series: DeepStack Extravaganza NYE, December 24, 2026 - January 10, "
                 "2027' and 'DeepStack Showdown (January), January 11 - February 14, 2027'. The label and the schedule page "
                 "now agree, and no published value depended on it. Kept on the register as the record of the defect."),
         source="https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament.html"),
    dict(id="F83", area="Wynn", severity="Medium",
         title="Whether the Wynn daily slate runs on November 27-29 is not stated by any official page",
         detail=("The official Wynn poker page says the daily tournament slate 'runs twice a day during non-event timeframes' "
                 "and that 'the Daily Tournament schedule will be suspended during each Wynn Signature, Wynn Millions, and "
                 "Classic tournament series'. The WPT World Championship (November 27 - December 21, 2026) is a series that "
                 "starts on day 5 of the trip window, but it is not named in the suspension note and no official page states "
                 "whether the daily $200/$240 events run alongside it. Re-read 2026-11-17 (session arena-1bbee97f); the wording "
                 "was unchanged. Until the room confirms it, the day plan's Wynn daily rows for November 27-29 are conditional "
                 "and should not be counted on: the Venetian DSE IV events and the WPT $600/$800 flights are the verified "
                 "options on those days."),
         source="https://www.wynnlasvegas.com/casino/poker"),
    dict(id="F84", area="Walking routes", severity="Medium",
         title="Walking minutes are Google Maps directions read 2026-11-17 in walking mode; no venue publishes them",
         detail=("All eight hotels were read to the Venetian poker room. Records, exact queries, every route card and the mode marker are in "
                 "raw/google_maps_walk_2026-11-17.json, and tests/test_walk_captures_2026_11_17.py asserts each stored minute figure against it. "
                 "The first (recommended) card is the stored value; the other shown cards are in the note. Walking mode is identified by the page's "
                 "'mostly flat' line; a driving control for Venetian to Bellagio read 10 minutes by car against 21 on foot. The page was in a French "
                 "browser locale. Google Maps is a non-official measurement source and is labelled as such. The earlier 27-minute Venetian-to-Bellagio "
                 "card (F67) has no saved capture and is not reproduced."),
         source="https://www.google.com/maps/dir/?api=1&travelmode=walking&origin=The+Palazzo+Las+Vegas+NV&destination=The+Venetian+Resort+Las+Vegas+NV"),
    dict(id="F85", area="Mandalay Bay", severity="Medium",
         title="Mandalay Bay is open on its official page, which prints no tournament schedule",
         detail=("The official poker page (read 2026-11-17) prints Wednesday to Monday, 10 AM to 4 AM, closed Tuesdays, a $60–$1,000 price range, and "
                 "'Please Visit or Call Poker Room for Details' with reservations at 702.632.7790. Third-party listings show a $60 daily at 1 PM and a "
                 "$100 Saturday event at 8 PM; those are not official and are not used. The room is in the morning feed, and no Mandalay Bay event "
                 "enters the plan."),
         source="https://mandalaybay.mgmresorts.com/en/casino/poker-tables.html"),
    dict(id="F86", area="Hotels", severity="Medium",
         title="The poker-room parking waiver the venue prints for players is now carried by both Venetian rows, with the paid fee left in every total",
         detail=("Found on 2026-11-17 by re-reading the official poker-room pages (22:31Z), and reached independently on the same "
                 "day by the session that put the poker-room page on The Venetian row's citation. The finding is the asymmetry: "
                 "the Wynn row has carried a poker-room parking benefit for some time, while the Venetian and Palazzo rows "
                 "published only the paid self-parking figures. The resort's own page, "
                 "https://www.venetianlasvegas.com/resort/casino/poker/player-parking.html, prints both the rates ('The daily "
                 "fee for registered hotel guests is $20/day, seven days a week') and the waiver: 'Players in the poker room "
                 "who play three hours or more in tournament or cash games will receive complimentary self-parking for the day. "
                 "Players must visit a supervisor at the end of their session to confirm qualifications for complimentary "
                 "self-parking.' What this session adds on top of the citation: The Palazzo row now states the same policy "
                 "(cited to the same poker-room page, which prints both the guest rate and the waiver); both rows and the "
                 "trip-cost model carry the waiver as a dated, structured field with the verbatim text, the supervisor "
                 "condition, the Sapphire tier route and the reason it is not applied; the calculator prints the waiver beside "
                 "its parking field; and Q12 answers the question from the venue's page. NO TOTAL WAS CHANGED. The "
                 "paid $20 a night stays in the calculator and in every published trip total, because no official source "
                 "publishes a tournament finish time (F16) so the three-hour condition cannot be confirmed from a schedule, the "
                 "page requires a supervisor to confirm the session, and the same page warns 'Event parking rates may be in "
                 "effect' and that rates are 'subject to change'. What the page does not say - whether the waiver reaches an "
                 "overnight folio charge or only the exit gate - is left blank, not guessed. MGM Resorts' own parking pages "
                 "(MGM Grand, ARIA, Bellagio) could not be reached from this environment on 2026-11-17, so those three parking cells "
                 "stay empty rather than being filled from third-party write-ups; Caesars Palace and Horseshoe publish only "
                 "\"surcharge applies\" with no figure on the pages read. A guard, scripts/verify_entry_labels.py, now "
                 "fails the build if a waiver is quoted in the data but not in the table row, or netted into a total."),
         source="https://www.venetianlasvegas.com/resort/casino/poker/player-parking.html"),
    dict(id="F87", area="Venetian DSE IV", severity="Low",
         title="Three event names are re-cased against the schedule page, which prints those sub-lines in capital letters",
         detail=("Found by re-reading the official schedule page at 2026-11-17T22:29Z and comparing the published rows line by "
                 "line with the page text (24 rows, 16-28 November). 19 rows match character for character. Four differ only in "
                 "the source's own typo 'No LImit', which F27 already discloses. Three rows differ in letter case, all from one "
                 "shared sub-line, of which one is inside the 24 rows re-read this session and two are in the December and "
                 "NYE captures: event #18 "
                 "(Saturday 28 November, 5:10 PM, $200 NLH PokerAtlas Valuetown Bounty $20K GTD) prints its sub-line as "
                 "'POKERATLAS PRO MEMBER $20 RAKE DISCOUNT' on the page, while the site publishes 'PokerAtlas PRO member $20 "
                 "rake discount'. The same re-casing covers event #58 (19 December) and NYE event #25 (2 January), which share "
                 "that sub-line. No date, time, event number, buy-in, guarantee or structure-sheet link differs on any of the "
                 "three rows, so no money or schedule value is affected. It is published because the site's rule is that a name "
                 "is either the printed name or is marked as restyled, and this one was not marked. The choice is left to the "
                 "user: print the capitals, or keep the title case and leave this flag on the register."),
         source="https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html"),

]

QUESTIONS = [
    dict(id="Q01", question="What are the actual travel dates, and how many nights?",
         answer=("Superseded 2026-11-17: the trip is now 23 to 30 November 2026 (seven nights), because the engine prices that "
                 "window in full (F69, F66). Earlier: for planning purposes the dates were fixed at November 25 to December 2, 2026 because that "
                 "window contains the most sheet-screened candidates (not confirmed single-entry events) in the reviewed "
                 "snapshot. The official booking engine was opened on 2026-11-17 for four stay windows inside those dates "
                 "and returned no suite and no price for any of them. It does quote near-term stays: it priced November "
                 "17-19, 2026 for two adults at $1,245.48 on 2026-11-16 and at $1,015.89 on 2026-11-17, and November "
                 "20-22 at $2,504.00."),
         why="Needed", blocking="Yes - no hotel total can be confirmed without it",
         how="Open the booking link on the hotels page with the arrival and departure dates you want; the price is printed by the venue itself.",
         source="https://www.venetianlasvegas.com/booking?adults[]=2&arrival_date=2026-11-17&children[]=0&departure_date=2026-11-19&view=calendar"),
    dict(id="Q02", question="How many people are travelling, and is one room enough?",
         answer="The published rates are single or double occupancy. The Venetian adds $50 plus tax per additional guest 13 and older; Bellagio adds $50 plus tax per occupant above two.",
         why="Needed", blocking="Yes - occupancy changes the nightly total",
         how="Confirm the party size and the room type before comparing totals.",
         source="https://bellagio.mgmresorts.com/en/terms-and-conditions.html"),
    dict(id="Q03", question="What nightly budget and quality floor apply?",
         answer="Not supplied. No comparable official quality score exists for these rooms, so the site leaves the quality ranking blank rather than inventing one.",
         why="Needed", blocking="Yes - it decides which properties are shortlisted",
         how="Give a maximum true cost per night and the minimum standard you accept, then re-run the comparison with the published rate floors.",
         source="https://www.wynnlasvegas.com/rooms-and-suites"),
    dict(id="Q04", question="Is one total entry per player actually required, or only one entry per event?",
         answer="For 52 Venetian one-day candidates, the official sheets print one buy-in and no re-entry, rebuy, add-on or second-flight clause. They do not state a maximum number of entries per player or explicitly say 'single entry' or 'freezeout'. The site therefore calls these sheet-screened candidates only; written confirmation from the venue is still needed before treating them as eligible. Wynn, Bellagio, MGM Grand and Caesars rows with printed re-entry, rebuy or add-on clauses are isolated in the separate extra-spend section.",
         why="Needed", blocking="Yes - the maximum-entry policy is not published in the reviewed sheets",
         how="Ask the poker room to confirm in writing that a second buy-in is not accepted for a specific event if that matters for your decision.",
         source="https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_5.pdf"),
    dict(id="Q05", question="Which hotels actually publish a room price for the dates you want?",
         answer=(
                 "Only The Venetian, and only through its own booking engine rather than on the rate page. Re-read "
                 "on 2026-11-17, the engine printed $621.75 + $55 and $164.25 + $55 with $119.89 tax and a "
                 "$1,015.89 total for a 650 sq ft Luxury King suite on November 17-19, against $1,245.48 for the "
                 "same stay the day before, plus $2,504.00 for November 20-22. For the trip window itself it "
                 "returned no suite at all. The engine's calendar cells are not prices: read twice on the same day, "
                 "November 16 printed $555 with one stay window open and $854 with another, and November 27 printed "
                 "$905 against $1,814 (F47). The last sentence of this answer was superseded later on 2026-11-17: the "
                 "engine DID price the trip window (23-30 Nov 2026, $4,010.55 checkout total, logged in the rate log) "
                 "and, on a second read about 20 minutes later, a Palazzo Luxury King at $3,823.46 (F78). The rate page "
                 "still publishes only starting rates of $119 and $209, which are explicitly not date-specific, and "
                 "states that rates are provided up to 150 days out. Two other properties now have dated figures too, "
                 "both from their own booking pages on 2026-11-17: MGM Grand printed MGM King calendar cells (22-28 Nov "
                 "$84, $84, $84, $84, $149, $349, $149; 30 Nov $649) under a legend that says the cells include the "
                 "average daily resort fee and exclude taxes, and Horseshoe printed its own November and December "
                 "grids. A calendar cell is not a checkout total; only the Venetian has a printed, itemised checkout "
                 "total for the trip stay."),
         why="Needed", blocking="Yes for a confirmed total",
         how="Open the booking link with the exact dates, then log the printed total in the rate log with its timestamp.",
         source="https://www.venetianlasvegas.com/resort/casino/poker/suite-rates.html"),
    dict(id="Q06", question="Will the poker-suite rate be honoured if you play tournaments rather than cash games?",
         answer="Yes, in writing: the rate page requires 'six hours of active live cash gameplay or buy in to a $300 or higher tournament for each night stayed', met before 2 a.m. on the last night. A $100 or $200 tournament does not qualify; a $300 or higher entry does.",
         why="Needed", blocking="No",
         how="Plan at least one $300+ entry per night stayed, or accept the prevailing rate.",
         source="https://www.venetianlasvegas.com/resort/casino/poker/suite-rates.html"),
    dict(id="Q07", question="How long do the tournaments actually run, so two events can be sequenced?",
         answer="Not published. Sheets give start time, level length and the late-registration cut-off, but no finish time. The overlap check on this site uses a stated six-hour session assumption plus a 30-minute transfer, and labels every conflict as an estimate.",
         why="Needed", blocking="No, but it limits the day plan",
         how="Ask the poker room for expected finish times, or treat the plan as a template and confirm on the day.",
         source="https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html"),
    dict(id="Q08", question="What is the real walking time between each hotel and each poker room?",
         answer="The venues publish no walking times. On 2026-11-17 every hotel was read to the Venetian poker room in Google Maps walking mode (first route card): The Palazzo 4 minutes, Wynn 13, Bellagio 21, Caesars Palace 12, Horseshoe 16, MGM Grand 35 and ARIA 31 (ARIA's other shown routes run to 38). The Venetian itself is in-property. These are Google Maps measurements, not official venue times (F84). Other hotel-to-room pairs, and every pair that includes Mandalay Bay, are not checked (F32).",
         why="Needed", blocking="Yes - hotel-to-room pairs other than the Venetian are not checked",
         how="Use official property addresses to verify each hotel-to-room Google or Apple walking route; do not assume missing pairs are under 30 minutes.",
         source="https://www.google.com/maps/dir/?api=1&travelmode=walking"),
    dict(id="Q09", question="Which other Strip rooms should be added to the plan?",
         answer="Mandalay Bay was added on 2026-11-17: its official page is open Wednesday to Monday but prints no tournament schedule (F85). Resorts World and Planet Hollywood are reported closed in press only (F79, F80; unverified) and are listed on the Strip-room status table, not as candidates. Not checked: South Point, Golden Nugget, Circa, Excalibur, Luxor, Orleans, Red Rock, Palms, Westgate, Tropicana, Bally's, Flamingo, LINQ, Rio and M Resort.",
         why="Useful", blocking="No",
         how="Say which properties to add; each needs its own official page and structure sheets.",
         source="https://www.venetianlasvegas.com/resort/casino/poker.html"),
    dict(id="Q10", question="Do the December 17-23 and holiday-week events still run as published?",
         answer=("Re-read on 2026-11-17. Venetian DeepStack Extravaganza IV (the page covers Nov 16 to Dec 23, 2026): the 21 rows dated Nov 16 to Nov 27 match the page on date, start time, event name, buy-in, guarantee and structure-sheet link. The 73 rows dated Nov 28 to Dec 23 match on date, start time, event name, buy-in and guarantee; their structure links were not compared. Caesars Palace (four daily starts at 10 AM, 2 PM, 6 PM and 9 PM, $100 buy-in, $1,000 guarantee) and Horseshoe (six daily starts from 9 AM to 11 PM) match the page text. The page gives no Horseshoe buy-in or guarantee, so those cells stay blank. The Venetian resort fee is still $55 plus tax. The Wynn landing page confirms the WPT window and the Super Gold Million terms. The Bellagio landing page still carries a stale notice (flag F03). Not re-read by the 2026-11-17 pass that produced this answer: the Bellagio weekly PDFs, the Wynn daily and WPT PDFs and the DeepStack NYE schedule. They were read by the sessions recorded on the sources page, and each row shows its own read and verified dates."),
         why="Useful", blocking="No",
         how="Re-check the Flagged for review page and the change log before booking and again 48 hours before you travel.",
         source="https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html"),
    dict(id="Q11", question="What is the cancellation deadline at each property?",
         answer=("Published and different, all re-read live on 2026-11-17. Wynn: 'cancellations must be received at least "
                 "48 hours prior to arrival date or deposit (if applicable) will be forfeited', plus an early-departure "
                 "penalty, with offer-specific date exceptions on the same page (F35 corrected). Bellagio, MGM Grand and "
                 "ARIA: the first night's deposit is refundable if Room Reservations receives notice at least 72 hours "
                 "before arrival; later cancellations and no-shows forfeit it. Caesars Palace and Horseshoe: the property "
                 "pages advertise 'FREE 48-Hour Cancellation*' but do not print the terms behind the asterisk. Venetian: "
                 "a deposit is billed on confirmation, blackout dates apply, prepaid offers are non-refundable, and an "
                 "early checkout costs $100 plus tax."),
         why="Needed", blocking="No",
         how="Use the cancellation column in the hotel table when choosing where to hold the booking.",
         source="https://www.wynnlasvegas.com/terms-and-conditions/850070"),
    dict(id="Q12", question="What does parking cost, and does it change the true cost per night?",
         answer=("Venetian: $20 per day for registered hotel guests, $20 Monday-Thursday and $25 Friday-Sunday for non-hotel "
                 "guests, valet $40. The poker room's own parking page adds a waiver the hotel terms page does not print: "
                 "players who play three hours or more in tournament or cash games receive complimentary self-parking for "
                 "that day, confirmed with a supervisor at the end of the session (re-read 2026-11-17). A registered guest "
                 "staying on property and playing a six-hour session therefore may pay nothing for parking, which is why "
                 "the trip calculator keeps parking out of the core formula and shows it separately. Wynn: self-parking is "
                 "free for registered guests and $25 per day for others, valet $40, and complimentary self-parking extends "
                 "to Wynn poker-room guests. Bellagio, MGM Grand and ARIA publish no parking figure on their reservation "
                 "terms pages, so those cells stay blank rather than guessed."),
         why="Needed", blocking="No",
         how=("Parking stays in the trip total at $20 a night. If the room confirms three or more hours of play for a day, that "
              "night's self-parking is complimentary per the page, so set the parking field to 0 for those days rather than "
              "assuming the waiver in advance."),
         source="https://www.venetianlasvegas.com/resort/casino/poker/player-parking.html"),
    dict(id="Q13", question="Are you 21 or older with a Venetian Rewards card, and are you 50 or older for the Seniors events?",
         answer=("Each of the seven DeepStack Extravaganza IV sheets re-read on 2026-11-17 requires players to be 21+ and to hold a "
                 "Venetian Rewards card. The Dec 2 10:10 AM $600 No Limit Hold'em Seniors event (#24) is open only to players "
                 "50 or older. Sheet 17, read on 2026-11-16 and re-read line by line on 2026-11-17, prints 'MUST BE 50+ YEARS OF "
                 "AGE TO PARTICIPATE' and adds that a player who buys in under 50 is not entitled to prize money or a refund of "
                 "the buy-in, so the age limit is confirmed on the sheet and not only on the schedule. The day plan leaves "
                 "age-restricted events out, so the Dec 2 primary stays the 5:10 PM bounty and this Seniors event is listed "
                 "only as an alternative for a player who is 50+."),
         why="Needed", blocking="Yes - eligibility decides which of the trip-window events a player can enter",
         how="Confirm your age band and whether you hold a Venetian Rewards card. If you are 50+, the Dec 2 Seniors event (#24) is open to you: its sheet is read and its fee, guarantee, chips and late-registration cut-off are on the row.",
         source="https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_6.pdf"),
    dict(id="Q14", question="Does the 8 AM start the brief asks for exist anywhere on the Strip?",
         answer=("Not on any official source read for this build. The earliest verified start is Horseshoe's daily game at 9:00 AM "
                 "on the Caesars page (read 2026-11-17), which publishes no buy-in or structure. Caesars Palace starts at 10:00 AM. "
                 "The earliest Venetian start is 9:10 AM (a satellite on Dec 12), and the earliest non-satellite Venetian start is "
                 "10:10 AM. An all-day 8 AM plan therefore cannot be built from verified data; the day plan starts at the first "
                 "verified open event for each venue. For the trip window itself (23-29 November) no opening event starts before "
                 "11:10 AM; the only earlier start there is a Day 2 restart at 11:00 AM on 25 November (F17, read 2026-11-19)."),
         why="Needed", blocking="Yes - the all-day schedule in the brief cannot be produced without it",
         how="Ask Horseshoe for the buy-in, structure and single-entry rule of its 9:00 AM game; ask each room for its earliest daily start.",
         source="https://www.caesars.com/las-vegas/explore/casino/poker-tournaments-las-vegas-strip"),
    dict(id="Q15", question="What is the real checkout total for the trip dates?",
         answer=("Partly answered 2026-11-17. The official Venetian booking engine printed an itemised checkout total of $4,010.55 "
                 "for 2026-11-23 to 2026-11-30 (two adults, Luxury King suite, best available rate; $55 resort fee each night and $473.30 tax). "
                 "Earlier readings for 2026-11-25 to 2026-12-02 showed the placeholder '$XXX' in every calendar cell and no total (F57). "
                 "Re-read 2026-11-19: the same booking link still showed only a loading page with no total, so the $4,010.55 figure is "
                 "not a price for today (F93). No other property publishes a date-specific total in the data. "
                 "The phone-only poker rate is not in the quote (F66)."),
         why="Needed", blocking="Yes - the engine total is now known, but the poker-rate total the budget is built on is not",
         how="Open the booking engine in a browser, select the dates and two adults, and read the checkout total; or call the "
             "poker rate line on 866.255.8936 and ask for code EPOKR25 priced for those dates.",
         source="https://www.venetianlasvegas.com/resort/casino/poker/suite-rates.html"),
    dict(id="Q16", question="Do the poker hotel rates require play that the trip plan actually satisfies?",
         answer=("Yes, and it changes the risk. The Venetian poker rate requires six hours of active live cash play, or a "
                 "buy-in to a $300 or higher tournament, for each night stayed. Any night that misses the requirement is "
                 "repriced at the prevailing rate at checkout. Measured against the published plan on 2026-11-17: five "
                 "of the seven nights carry a $300 or higher primary (Nov 25 $400, Nov 26 $300, Nov 27 $600, Nov 28 "
                 "$600, Nov 29 $300) and two do not (Nov 23 and Nov 24, both $200). The seven nights are 23-29 "
                 "November because the trip ends with an 11:00 a.m. check-out on 30 November, which is a departure "
                 "day and not a night. Each day of the plan prints its own result. What the page does not say is whether one entry covers every night of a multi-day event, or only the night it is paid - "
                 "ask the room before treating the $119 floor as certain (F54)."),
         why="Needed", blocking="No, but it decides which events belong on which day",
         how="Confirm with the poker room that the tournament buy-in counts on the day it is paid, and whether a Day 2 "
             "return counts again.",
         source="https://www.venetianlasvegas.com/resort/casino/poker/suite-rates.html"),
    dict(id="Q17", question="Which hotel fees are still unverified, and does that break the comparison?",
         answer=("Corrected 2026-11-17: every one of the eight properties now has a verified resort fee. Caesars Palace "
                 "prints $54.95 plus $7.35 tax ($62.30 tax inclusive) and Horseshoe $49.95 plus $6.68 ($56.63), both on "
                 "their own booking pages; MGM Grand $50, Bellagio $55, ARIA $55, Wynn $55 and the Venetian $55 come from "
                 "each property's own reservation terms. What remains unverified is the ROOM-TAX PERCENTAGE: only the "
                 "Venetian prints 13.38%, so true-nightly figures stay blank at the other properties and the comparison is "
                 "incomplete rather than wrong (F39). The site leaves those cells blank and flags them."),
         why="Needed", blocking="No - the recommended property is fully verified",
         how="Read each property's own reservation terms page, or ask the front desk for the resort fee and tax in writing.",
         source="https://www.caesars.com/caesars-palace"),
    dict(id="Q18", question="What happens if a scheduled re-check reports a changed page?",
         answer=("Nothing changes automatically. scripts/verify_transcription.py stores a SHA-256 of each page and flags a change; "
                 "a person then re-reads the source before any value moves. This is deliberate: a venue can change a "
                 "guarantee, a fee or a start time without notice, and an automatic overwrite would publish an unread "
                 "number as if it had been verified."),
         why="Needed", blocking="No - it is a process question",
         how="Watch the Sources page; a changed URL is listed with its previous and current hash.",
         source="https://github.com/karagemop466-tech/Poker3/blob/main/scripts/verify_transcription.py"),

]

SUGGESTIONS = [
    dict(id="S01", title="Publish a nightly rate snapshot per property and week",
         detail=("Rooms are priced per night and the published rates are only available up to 150 days out. A weekly snapshot of the "
                 "official starting rate, the mandatory resort fee and the tax for each property would turn a blank column into a "
                 "comparable one and would let the rate log show movement."),
         impact="High", effort="Medium", decision="Needs a data source that the venue publishes without login"),
    dict(id="S02", title="Add a per-venue finish-time estimate that the poker room confirms",
         detail=("The overlap check is the weakest part of the plan because no venue publishes a finish time. A simple field on each "
                 "structure sheet, confirmed by the room, would make the day plan exact instead of assumed."),
         impact="High", effort="Low", decision="Ask each poker room; the Venetian publishes structure sheets it controls"),
    dict(id="S03", title="Read the remaining WPT event sections and the rest of the Strip schedule", status="Done for the WPT structures, 2026-11-17",
         detail=("Closed for the WPT structures: the official structures PDF was read in full (all eight chunks) on "
                 "2026-11-17 and every event section it publishes is transcribed in "
                 "raw/wynn_wpt_world_championship_structures_2026-11-17.md, with 35 rows now quoting their own section "
                 "(F12, F77). Reading it did NOT move any event into the single-entry filter, because every section "
                 "prints re-entry. Still open, and now precisely bounded: the $10,400 WPT World Championship, the Dec 18 "
                 "high-roller and $3,000 events, the Super Gold Million Mystery Bounty, the Seniors and Ladies "
                 "championships, the NLH Mystery Bounty, the Wynn Mixed Championship, the TORSE and Limit Omaha 8 "
                 "championships and every Milestone Satellite have no published section at all, so no amount of reading "
                 "this document settles them. 101 WPT rows stay unverified for that reason. The next step is to ask the "
                 "Wynn poker room for those sheets or to watch the same URL for a re-issue."),
         impact="High", effort="Medium", decision="Ask the Wynn poker room for the unpublished sections; no new source to find"),
    dict(id="S04", title="Add the missing Strip poker rooms",
         detail=("Mandalay Bay was added on 2026-11-17 (F85). Resorts World and Planet Hollywood are reported closed in press only (F79, F80; unverified). South Point, Golden Nugget, Circa, Excalibur, Luxor, Orleans, Red Rock, Palms, Westgate, Tropicana, "
                 "Bally's, Flamingo, LINQ, Rio and M Resort are all unverified. For a trip that aims to enter as many "
                 "tournaments as possible, the daily rooms in walking range are worth more than another marquee series."),
         impact="Medium", effort="Medium", decision="Which properties to prioritise"),
    dict(id="S05", title="Replace the estimated walking times with a venue-published figure",
         detail=("No venue publishes a walking time. Asking each property for the official route and time to its own poker room "
                 "would replace Google Maps estimates, which are model outputs that ignore indoor walkways and Strip traffic. "
                 "Until then the site only filters on measured pairs: as of 2026-11-17 the tournaments table's 30-minute limit "
                 "is opt-in, is measured from the hotel the reader selects, labels a figure used in the reverse of its recorded "
                 "direction, and counts the rows it hides as either over the limit or unmeasured."),
         impact="Medium", effort="Low", decision="Worth doing for the final shortlist"),
    dict(id="S06", title="Capture the hotel cost components for the remaining properties",
         detail=("STATUS UPDATED 2026-11-17. The fee half of this is closed: all eight properties now carry a resort fee taken "
                 "from the property's own page (Venetian, Palazzo, Wynn and Bellagio $55, MGM Grand $50, Caesars Palace $54.95, "
                 "Horseshoe $49.95, ARIA $55), and Caesars Palace and Horseshoe additionally print the tax on that fee, which "
                 "divides to 13.376% and 13.373% and corroborates the 13.38% the model applies. What still blocks a like-for-like "
                 "ranking is the room rate: no property except the Venetian publishes a dated price a static reader can reach, so "
                 "true cost per night exists only for the Venetian and the Palazzo. Parking is published for Venetian, Palazzo, "
                 "Wynn, Caesars and Horseshoe and not for MGM Grand, Bellagio or ARIA."),
         impact="Medium", effort="Low", decision="Straightforward research, no new source needed"),
    dict(id="S07", title="Add a bankroll-versus-prize view that states the assumption",
         detail=("The site deliberately shows guaranteed pool divided by entry fee as a descriptive ratio and never as a forecast. A "
                 "clearly labelled scenario panel could show how many buy-ins a fixed bankroll buys against a given guarantee, with "
                 "the assumption written next to the number."),
         impact="Medium", effort="Medium", decision="Whether to include any modelling at all"),
    dict(id="S08", title="Add a seat-availability check for the recommended day plan",
         detail=("The Venetian requires a Venetian Rewards card to play and the Wynn requires Wynn Rewards membership. A pre-trip "
                 "checklist for rewards enrolment, and a note about MGM Rewards for Bellagio and MGM Grand, would remove a common "
                 "day-of-trip failure."),
         impact="Medium", effort="Low", decision="Straightforward content addition"),
    dict(id="S09", title="Let the planner remember a trip profile",
         detail=("Dates, nightly budget, party size and the single-entry rule are the same four inputs on every page. Storing them in "
                 "the browser would let the date filter, the hotel comparison and the cost calculator agree with each other."),
         impact="Medium", effort="Low", decision="Local storage only, no account"),
    dict(id="S10", title="Publish the change-detection log as a first-class page",
         detail=("The scheduled checker already records a dated status and content hash for every official URL. Surfacing it on its "
                 "own page, with the rows that changed highlighted on the tournament tables, is what turns the site from a snapshot "
                 "into something you can trust on the morning you travel."),
         impact="High", effort="Low", decision="Already implemented in this pass - confirm the presentation"),
    dict(id="S11", title="Resolve the Bellagio Saturday buy-in conflict with the poker room",
         detail=("Three official sources print three different buy-ins for the same event. A single written answer from the room "
                 "would let the event be ranked instead of being left blank."),
         impact="Medium", effort="Low", decision="Send the conflict list to the room"),
    dict(id="S12", title="Retire the four superseded dashboards",
         detail=("The repository still holds five dashboards from earlier parallel sessions (root pages, docs/, verified/, planner/, "
                 "single-entry/). Only site/ is published by the Pages workflow, so the others are audit artefacts. Removing or "
                 "archiving them would stop them diverging from the live data."),
         impact="Low", effort="Low", decision="Keep as archive or delete"),

    dict(id="S13", title="Settle the missing facts before any booking decision",
         detail=("Six things are known and seven are not, and the difference decides the trip. Known from official "
                 "sources: every DeepStack IV and NYE structure sheet, every printed buy-in and fee, the Venetian resort "
                 "fee and 13.38% room tax, the Venetian $20 guest parking, and the cancellation rules for the Venetian, "
                 "Bellagio, MGM Grand, ARIA and Wynn. Not known: the real checkout total for the trip dates, the Wynn and "
                 "Caesars tax percentages, the Caesars and Horseshoe resort fees, any published tournament finish time, "
                 "the WPT event-level re-entry rules, whether the poker rate's play requirement counts a tournament "
                 "buy-in on the day it is paid, and whether any room opens before 09:10 AM. Each one has a question card "
                 "on the Questions page."),
         impact="High", effort="Low",
         decision="Answer the blocking questions on the Questions page, in the order they are listed"),
    dict(id="S14", title="Price the same seven-night stay in a browser, then log it",
         detail=("The booking engine renders its prices with script, so the three sources that can read a checkout total "
                 "are a real browser, the poker-rate phone line (866.255.8936, code EPOKR25) or the front desk. Whichever "
                 "answers, record the arrival date, departure date, occupancy, room type, nightly rate, resort fee, tax, "
                 "total and the timestamp as one new dated rate-log entry. That single row would replace the $197.28 "
                 "floor with a real number for the recommended dates."),
         impact="High", effort="Low",
         decision="One phone call or one browser session; no new source needed"),
    dict(id="S15", title="Ask the three rooms with unverified fees for the numbers in writing",
         detail=("Caesars Palace and Horseshoe publish room prices but no resort fee, and Wynn prints 'plus tax' without "
                 "a percentage. A written fee schedule from each property would let all eight properties be compared "
                 "like for like for the first time. Until then the comparison on the trip cost page shows those rows "
                 "blank on purpose."),
         impact="Medium", effort="Low",
         decision="Send the same three-question request to each property"),
    dict(id="S16", title="Count the levels to the money instead of assuming one session length",
         detail=("The day plan estimates a finish from the late-registration cut-off plus two levels, which is honest but "
                 "still an assumption. Every structure sheet prints the full blind schedule and the payout percentage, "
                 "so the levels to the money could be counted to produce a field-size-based finish range. That would turn "
                 "the overlap flags from estimates into arithmetic on published data."),
         impact="High", effort="Medium",
         decision="Whether to publish a modelled finish range or keep one stated assumption"),
    dict(id="S17", title="Confirm the WPT event-level re-entry rule for the three events inside the trip window", status="Done, 2026-11-17",
         detail=("Closed. The structures PDF was read in full and each of the three WPT rows inside the trip window that "
                 "has a published section now quotes it verbatim: the $600 TORSE on Nov 27 ('Unlimited re-entry will be "
                 "available until the start of level 9'), the $400 PLO on Nov 27 and the $600 Limit Omaha 8 on Nov 30 "
                 "(both 'Unlimited re-entry will be available until the start of level 9'). All three are multi-entry, "
                 "so none of them is a single-entry candidate. The 82 WPT rows still marked unverified are events the "
                 "document does not cover, not rows this pass failed to read (F12)."),
         impact="High", effort="Low", decision="No further action: the answer is that these events allow unlimited re-entry"),
    dict(id="S18", title="Re-quote the trip window every morning and log what the engine returns",
         detail=("Three dated quotes show the engine moves: the same November 17-19 stay printed $1,245.48 on "
                 "2026-11-16 and $1,015.89 on 2026-11-17. Four stay windows inside the trip window returned no suite at "
                 "all. A scheduled job that opens the seven per-night booking links each morning and appends whatever "
                 "the engine prints - a total, or 'no suite returned' - would turn the trip budget from a floor into a "
                 "tracked number without anyone having to remember to look."),
         impact="High", effort="Medium",
         decision="Automate the morning re-quote, or keep the per-night links manual"),
    dict(id="S19", title="Never treat a booking-calendar cell as a price",
         detail=("Read twice on the same day, the official calendar printed $555 and $854 for November 16 and $905 and "
                 "$1,814 for November 27 depending on which stay window was open. The cell tracks the cheapest suite the "
                 "engine can offer for that query, not a nightly rate. This is already enforced in the data - only the "
                 "itemised quote panel is used - but the comparison is worth keeping on the hotels page so a reader does "
                 "not copy a calendar figure into a budget."),
         impact="Medium", effort="Done", decision="Keep the comparison published - and since 2026-11-17 the calculator page "
                                                 "itself warns against pasting a calendar cell into the room-rate box, "
                                                 "quoting the two properties' own 'includes resort fee' sentences"),
    dict(id="S20", title="Ask the Venetian two questions in one call, then fix the rate basis once",
         detail=("Two open questions are answered by the same phone call to 866.255.8936 (code EPOKR25). (1) Is the "
                 "$119 / $209 poker rate quoted before or after the $55 resort fee? The Resort Fee page says the fee is "
                 "chargeable on top of the rate and the booking calendar says its prices include the fee, so the poker "
                 "rate itself decides whether the $197.28 floor overstates the nightly cost by about $43 (F51). (2) Does one $300 or higher entry cover every night of a "
                 "multi-day event, or only the night it is paid? The answer decides whether the 23 and 24 November "
                 "nights are repriced (F54). A dated checkout total for the booked 23-30 November stay is already "
                 "recorded ($4,010.55, F15), so quote the poker rate against that same stay to compare like for like."),
         impact="High", effort="Low",
         decision="One call settles the nightly budget basis, the qualification risk and the missing total"),
    dict(id="S21", title="Score each day on rate qualification as well as on guarantee",
         detail=("The day plan now prints, per day, whether the planned primary satisfies the published $300 condition "
                 "for the poker-suite rate. Two ways to act on it: (a) leave 23 and 24 November as $200 primaries and "
                 "budget those two nights at the prevailing rate, or (b) swap them for the published $400 No Limit "
                 "Hold'em 1A / 1B at 11:10 AM on each day, which qualifies but moves both days out of the single-entry "
                 "screen, because a flight shares a Day 2 with other flights. This site shows the trade-off and does not "
                 "choose it, because it depends on whether the traveller values the verified rate or the single-entry "
                 "format."),
         impact="Medium", effort="Low",
         decision="Add a 'qualifies for the poker rate' filter to the tournaments table (a $300+ buy-in filter on the "
                  "same rows already published)"),
    dict(id="S22", title="Keep monitoring the two Caesars booking pages for a dated rate",
         detail=("The Caesars property booking pages publish a fee block and, for Horseshoe, a full dated month of "
                 "lowest-available rates, in plain HTML rather than by script - unlike the Venetian engine, which prints "
                 "$XXX. Both pages are now in the monitored source list, so the 12:10 UTC re-check will see a Caesars "
                 "Palace calendar appear as soon as the property starts publishing one, and the rate log will keep both "
                 "readings when a cell moves (F55). No scraper is needed for these two properties."),
         impact="Medium", effort="Done in this pass",
         decision="No further work: the URLs are in site/data.json sources and are re-checked on schedule"),
]


SIG_MARK_NOTES = {
    "*": ("Prize footnote on the schedule: \"Winners will receive direct entry to the corresponding event(s) for which "
          "it was held.\" These are seat prizes, not cash."),
}

WPT_MARK_NOTES = {
    "*": ("Footnote 1 on the schedule PDF, printed beside this row: \"Winners will receive two (2) prizes valued at "
          "$1,100 each. Prizes may be used separately or combined for a tournament entry.\""),
    "**": ("Footnote 2 on the schedule PDF, printed beside this row: \"Winners will receive direct entry to the "
           "corresponding event(s) for which it was held.\" These are seat prizes, not cash."),
    "***": ("Footnote 3 on the schedule PDF, printed beside this row: \"$1,000,000 will be added in cash prizes by "
            "ClubWPT Gold. ClubWPT Gold is not available in Nevada.\" A Nevada player cannot count the added million, "
            "which is why this row shows no guarantee."),
    "****": ("Footnote 4 on the schedule PDF reads \"The Tournament Entry for the Ladies Championship is $11,100. "
             "Ladies will receive a discounted entry.\" The PDF prints this marker on seven rows, only one of which the "
             "footnote describes: the Ladies Championship itself ($1,100, Dec 13) and six more it says nothing about - "
             "PLO 6-Max ($10,500), the Milestone Satellite to the $25K NLH High Roller ($3,000), the NLH High Roller "
             "($25,800), NLH 6-Max ($10,500), PLO ($10,500) and NLH 8-Max ($10,500). The marker does not resolve "
             "against the footnote list, so the printed buy-in is shown unchanged and no entry is treated as "
             "discounted (F25). Confirm with the Wynn poker room before relying on any price on those rows."),
    "*****": ("Footnote 5 on the schedule PDF reads \"Players registered prior to the start of the event will "
              "receive a discounted entry.\" No published row in the captured schedule carries this marker."),
}


def _rules_for_sheet(sheet_no):
    s = V.SHEETS[sheet_no]
    url = f"{V.BASE}/dse_nov_2026-structure_{sheet_no}.pdf"
    base = dict(source=url, retrieved=V.RETRIEVED)
    fee_excerpt = (f"${s['rake']} of the ${s['buyIn']} Buy-In is withheld for house fees (Rake + Staff). "
                   f"The prize pool consists of ${s['pool']} of every ${s['buyIn']} Buy In.")
    if sheet_no in (31, 32, 33):
        fee_excerpt += " A separate flat fee is withheld for the Ladies International Poker Series."
    if s["entry"] == "none":
        single = dict(status="single-entry-on-sheet",
                      excerpt=(f"The sheet prints one ${s['buyIn']} buy-in, one start flight and one 'Starting Chips' figure. "
                               "No re-entry, rebuy, add-on or second-flight provision appears anywhere on the sheet. "
                               "The sheet does not state a per-player maximum-entry count or explicitly call the event a freezeout; venue confirmation is still required."), **base)
        reentry = dict(status="none-printed", excerpt="No re-entry provision appears on this structure sheet.", **base)
        addon = dict(status="none-printed", excerpt="No add-on provision appears on this structure sheet.", **base)
    elif s["entry"] == "multi-flight":
        single = dict(status="multiple-entries",
                      excerpt=("Each starting flight will play until we are down to approximately 12.5% of the field remaining. Day 2 "
                               "will resume combining all remaining players from the listed flights. Any player who bags chips for Day 2 "
                               "may not play a subsequent flight, so a player who does not bag may buy into another flight."),
                      **base)
        reentry = dict(status="separate-flights", excerpt="Separate starting flights (1A/1B/...) are published on the schedule page.", **base)
        addon = dict(status="none-printed", excerpt="No add-on provision appears on this structure sheet.", **base)
    elif s["entry"] == "multi-buyin":
        single = dict(status="multiple-entries", excerpt=s["entryExcerpt"], **base)
        reentry = dict(status="allowed", excerpt=s["entryExcerpt"], **base)
        addon = dict(status="none-printed", excerpt="No add-on provision appears on this structure sheet.", **base)
    elif s["entry"] == "satellite":
        single = dict(status="not-cash-tournament", excerpt="All tournament prizes are direct entry into the target event, not cash.", **base)
        reentry = dict(status="none-printed", excerpt="No re-entry provision appears on this structure sheet.", **base)
        addon = dict(status="none-printed", excerpt="No add-on provision appears on this structure sheet.", **base)
    else:  # special formats
        single = dict(status="special-format", excerpt=s.get("entryExcerpt", "This event uses a restricted or team format."), **base)
        reentry = dict(status="not-verified", excerpt="Not applicable to the published format.", **base)
        addon = dict(status="none-printed", excerpt="No add-on provision appears on this structure sheet.", **base)
    rules = dict(singleEntry=single, reEntry=reentry, addOn=addon,
                 fee=dict(status="confirmed", excerpt=fee_excerpt, **base))
    if "rebuy" in s:
        rules["rebuy"] = dict(status="allowed", excerpt=s["rebuy"], **base)
    return rules


def _event(eid, venue, date, time, name, buyIn, guarantee, rules, category, kind,
           sheet_url, schedule_url, structure_url=None, last_checked=LAST_PASS,
           note="", eligibility="", guarantee_note="", chips="", level_min="",
           late_reg="", entry_type="not-verified", fmt="", continuation=False, weekdays=None):
    buy = buyIn if isinstance(buyIn, str) else ("" if buyIn in (None, "-") else buyIn)
    gua = guarantee if isinstance(guarantee, str) else ("" if guarantee in (None, "-") else guarantee)
    start = clock_minutes(time)
    if continuation:
        # A restart row resumes a closed field.  The structure sheet's
        # late-registration clause and the session arithmetic derived from it
        # describe the earlier day's flight, not this row: registration closed
        # when that day ended, and no venue publishes a restart finish time.
        # Carrying either value across would print a late-registration cut-off
        # for an event nobody can register for, so both are left blank and the
        # reason is recorded on the row.
        length, cutoff, end = None, "", None
        note = (note + " " if note else "") + (
            "Resumption row: the structure sheet's late-registration clause"
            + (f" ({late_reg})" if late_reg else "")
            + " and the session length derived from it belong to the earlier day, so no late-registration cut-off"
              " and no estimated finish are published for this row.")
        late_reg = ""
    else:
        length, cutoff, _ = session_estimate(start, late_reg, level_min)
        end = None if start is None else start + length
    if not fmt:
        n = name.lower()
        if entry_type == "satellite":
            fmt = "satellite"
        elif entry_type == "multi-flight":
            fmt = "flight"
        elif "bounty" in n or "pko" in n or "big o" in n:
            fmt = "bounty"
        elif entry_type == "multi-buyin":
            fmt = "multi-buyin"
        elif entry_type == "special":
            fmt = "special"
        elif entry_type == "none":
            fmt = "freezeout"
        else:
            fmt = "other"
    return dict(
        id=eid, venue=venue, date=date, time=time, name=name,
        buyIn=buy, guarantee=gua,
        ratio=(round(gua / buy, 1) if isinstance(buy, (int, float)) and isinstance(gua, (int, float)) and buy else ""),
        guaranteeNote=guarantee_note, rules=rules, category=category, kind=kind,
        entryType=entry_type,
        singleEntry=(entry_type == "none"),
        format=fmt,
        chips=chips, levelMin=level_min, lateReg=late_reg, weekdays=weekdays or [],
        lateRegEnd=cutoff,
        sessionMin=length, endEstimate=fmt_clock(end), endEstimateMin=end,
        isContinuation=continuation,
        sheetUrl=sheet_url, scheduleUrl=schedule_url, structureUrl=structure_url or "",
        lastChecked=last_checked, lastVerified=VERIFIED_ON, note=note, eligibility=eligibility,
    )


CATEGORIES = {
    "single": {"label": "Sheet-screened candidates (entry cap unconfirmed)", "blurb":
               "The official structure sheet prints one buy-in and no re-entry, rebuy, add-on or second-flight clause, "
               "but does not state a maximum number of entries per player. These are candidates only until the venue confirms its written policy."},
    "unverified": {"label": "Unverified — structure sheet not read", "blurb":
                   "Published on an official schedule but its structure sheet has not been read, so no entry rule, "
                   "fee split or chip count is confirmed. These rows keep the unverified label on purpose and are "
                   "never counted as single-entry events."},
    "flight": {"label": "Multi-flight", "blurb":
               "The official schedule publishes separate start flights. A player who does not bag for Day 2 may buy into "
               "another flight, so more than one entry is possible."},
    "satellite": {"label": "Satellite (seat prizes, not cash)", "blurb":
                  "Prizes are entries into another event, not cash. Different maths: see the ratio note."},
    "bounty": {"label": "Bounty / PKO", "blurb":
               "Part of the guarantee is paid as bounties, so the printed guarantee is not a cash prize pool."},
    "extra": {"label": "Extra-spend formats (re-entry, rebuy, add-on, paid chip boost)", "blurb":
              "Isolated from the single-entry list. Each format gives a way to spend more than the printed buy-in."},
    "special": {"label": "Restricted or team format", "blurb":
                "Team, female-only or age-restricted formats. They are labelled so they are never mistaken for an open "
                "single-entry event."},
    "wpt": {"label": "Wynn tournament series", "blurb":
            "Rows from the official WPT World Championship and Wynn Signature Series schedule PDFs."},
    "recurring": {"label": "Recurring daily or weekly room tournaments", "blurb":
                  "A published cadence rather than a dated event."},
    "conflict": {"label": "Source conflict (not ranked)", "blurb":
                 "The official sources disagree, so the monetary fields are left blank."},
}

TRIP = {
    "start": "2026-11-23",
    "end": "2026-11-30",
    "playableEnd": "2026-11-29",
    "nights": 7,
    "days": 7,
    "hotel": "venetian",
    "alternativeHotel": "palazzo",
    "checkoutNote": (
        "Check-out is 11:00 a.m. on 2026-11-30, so 30 November is a departure day, not a playable day. The seven "
        "playable days are 23-29 November 2026. The Venetian does publish a 5:10 p.m. $200 bounty on 30 November, "
        "but it cannot be played after an 11:00 a.m. check-out unless the player pays for a late check-out, which "
        "the official terms say is subject to an additional fee."),
    "nightlyBudget": 197.28,
    "nightlyBudgetNote": (
        "Two figures, because they answer different questions. The floor is $197.28: ($119 published poker-suite "
        "starting rate + $55 mandatory resort fee) x 1.1338 Clark County room tax. It is a floor computed from published "
        "components, not a quote. The $119 rate is available only by phone under code EPOKR25 and only to a player who "
        "meets the daily play requirement (F66). The dated figure is $572.94 a night all-in: the official Venetian booking "
        "engine's checkout total of $4,010.55 for 23-30 November 2026 (2 adults, Luxury King, read 2026-11-17 after 21:54 UTC), divided by seven nights. That total already includes the $55 resort fee and the 13.38% tax."),
    "nightlyBudgetCeiling": 299.32,
    "nightlyObservedAverage": 572.94,
    "lodgingTotalBeforeTax": 3537.25,
    "lodgingTotalAllIn": 4010.55,
    "qualityFloor": (
        "Fixed by this session on an objective published-evidence test rather than an invented score: the property must "
        "publish its own poker-room rate, keep the poker room on site, and publish its resort fee, tax and cancellation "
        "terms. No comparable official quality score exists for these rooms, so the quality column stays blank (F19)."),
    "rationale": [
        ("2026-11-23 to 2026-11-30 (7 nights, 7 playable days - 30 November is an 11 a.m. checkout day) holds 12 "
         "sheet-screened candidates whose sheets omit extra-entry terms, at least one on each playable date. This is "
         "not proof of a one-entry-per-player cap. The window moved here from 25 November - 2 December because the "
         "official booking engine will not price a stay spanning 30 November and 1 December (F57)."),
        ("All 37 DeepStack Extravaganza IV structure sheets were read directly on 2026-11-16. The sheets are primary-source "
         "evidence for their printed terms, but they do not confirm a maximum number of entries per player; see F31."),
        ("The window stays inside DSE IV, the series whose 37 structure sheets were read first. The December 24, 2026 to "
         "January 10, 2027 DeepStack NYE series is fully published and all 15 of its sheets have been read; three of "
         "them print multi-entry wording, so those rows stay off the candidate list, and the whole series sits outside "
         "the trip window in any case (F11)."),
        ("It also sits before the $10,400 WPT World Championship buy-in tier on December 13, which would break the trip "
         "budget on a single entry."),
        ("The Wynn WPT schedule runs from November 27 inside the window, so three days carry additional published rows, "
         "all clearly marked as series rows with unverified entry rules (F12)."),
    ],
    "nightlyRisk": (
        "The night of Friday 27 November 2026, the night after Thanksgiving, is quoted at $1,649.25 room rate + $55 resort "
        "fee + tax = $1,932.28 all-in, against $248.59 all-in on 23 and 24 November. It is 48% of the whole $4,010.55 stay on "
        "its own. A player who can move the trip, or who is willing to change property for that one night, removes $1,683.69 "
        "of all-in cost compared with a $248.59 night. The phone-only poker rate ($119-$209 + $55) is the other lever, if the "
        "daily play requirement is met and the code applies to these dates (F66)."),
    "bankrollNote": ("Bankroll figure on the day-plan page is the sum of the recommended primary buy-ins plus a 25% "
                     "buffer. The buffer is not permission or a budget for rebuys or add-ons: no event is treated as a confirmed "
                     "one-entry event until the venue confirms the written rules (F31). It is a planning number, not "
                     "a forecast."),
    "lodgingEvidence": (
        "The official Venetian booking engine was opened on 2026-11-17 for several stay windows, with two adults. Four windows "
        "inside the originally considered 25 November - 2 December dates returned no suite or price: the seven-night stay and "
        "the November 30 single night rendered every calendar cell as the placeholder '$XXX', the November 25-27 stay did not "
        "finish loading, and the November 27-28 stay rendered the calendar with no suite panel. A further read the same day "
        "rendered 25 November through 1 December as 'Date Unavailable' (F57). The trip was therefore moved to 23-30 November, "
        "the seven-night window the engine prices on every night. A read on 2026-11-17 after 21:54 UTC priced that window in "
        "full: a checkout total of $4,010.55, with the nightly rate, the $55 resort fee and 13.38% tax itemised for each night. "
        "Those figures are the dated quote in the rate log and the basis of the observed nightly figure. The earlier $2,140 and "
        "$346.62 figures were the sum and average of calendar cells for the superseded window; the engine's own footnote says the "
        "cells are not the price, so they are withdrawn from the trip budget (F69). The engine quotes near-term stays too, and it "
        "priced the same 17-19 November stay twice on consecutive days ($1,245.48 on 2026-11-16 and $1,015.89 on 2026-11-17), so "
        "every figure here is dated and can move."),
}

PLAN_NOTES = {
    "primaryRule": ("Provisional primary candidate = the sheet-screened event on that date with the largest published guarantee, "
                    "among venues within a 30-minute walk of the recommended hotel, excluding age-restricted, female-only "
                    "and team formats. This is not confirmation of a one-entry-per-player cap; written venue rules are required."),
    "fallbackRule": ("Fallback = the next sheet-screened candidate on the same date, ranked after the primary, chosen as an "
                     "alternative to it and never in addition to it. It is labelled in one of two ways, and the label is "
                     "generated from the two published start times rather than asserted: 'playable after the primary' "
                     "when it starts at or after the primary's estimated finish plus a 30-minute transfer, and 'replaces "
                     "the primary' when it starts inside that session, in which case it can only be played if the player "
                     "is out of the primary in time to register. When no published event on the date starts late enough "
                     "to follow the primary, the plan names that out loud and marks the next-best row as a same-day "
                     "alternative rather than presenting an impossible sequence. Every fallback is conditional on "
                     "written confirmation of entry rules and fit."),
    "transfer": 30,
    "walkLimit": 30,
    "pokerRateRule": ("The hotel rate the budget is built on is conditional. Each night stayed needs either six hours "
                      "of active live cash play or a $300 or higher tournament buy-in, per the official poker-suite "
                      "rate page. Every day of the plan now carries a 'poker-rate condition' result against that rule; a "
                      "night marked as not satisfying it may be repriced at the prevailing rate at checkout (F54)."),
}

# Walking minutes from the recommended hotel (The Venetian / The Palazzo resort) to each
# poker room.  Google Maps walking estimates captured 2026-11-16; no venue publishes a time.
WALK = {"venetian": 0, "caesars": 12, "wynn": 13, "horseshoe": 16, "bellagio": 21, "mgm": 35, "aria": 31}

FEED_ROOMS = [
    dict(id="venetian", name="The Venetian poker room",
         schedule="https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html",
         extra=["https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-dec-2026.html",
                "https://www.venetianlasvegas.com/resort/casino/poker.html"]),
    dict(id="wynn", name="Wynn poker room",
         schedule="https://www.wynnlasvegas.com/casino/poker",
         extra=["https://cdn.wynnresorts.com/image/upload/v1752011166/visitwynn_pdfs_files/Poker/Daily%20Tournaments/poker-daily-tournament-poster.pdf",
                "https://cdn.wynnresorts.com/image/upload/v1757097329/visitwynn_pdfs_files/Poker/WPT/WPT_World_Championship_Schedule.pdf"]),
    dict(id="bellagio", name="Bellagio poker room",
         schedule="https://bellagio.mgmresorts.com/en/casino/poker.html",
         extra=["https://assets.contentstack.io/v3/assets/bltc6ce635bc4868eb2/blt9cf95b0e60ec253e/6af491a3a9851d75c40be840/mgm-bellagio-poker-fridays-$600-nlh.pdf"]),
    dict(id="mgm", name="MGM Grand poker room",
         schedule="https://mgmgrand.mgmresorts.com/en/casino/poker-tables.html",
         extra=["https://assets.contentstack.io/v3/assets/bltc6ce635bc4868eb2/bltb2a45da7e8ee5621/mgm-grand-casino-poker-120_nlh.pdf"]),
    dict(id="caesars", name="Caesars Palace and Horseshoe poker rooms",
         schedule="https://www.caesars.com/las-vegas/explore/casino/poker-tournaments-las-vegas-strip", extra=[]),
    dict(id="aria", name="ARIA poker room", schedule="https://aria.mgmresorts.com/en/casino/poker.html", extra=[]),
    dict(id="mandalay", name="Mandalay Bay poker room", schedule="https://mandalaybay.mgmresorts.com/en/casino/poker-tables.html", extra=[]),
]

# Strip poker-room census, read 2026-11-17. A room is 'open' only where an official page says so; a closure
# is recorded only with a dated company statement, and where the statement was seen second-hand (press) the row
# says so. Rows with no official page read are listed as 'on record', never as newly confirmed.
STRIP_ROOMS_READ = "2026-11-17"
STRIP_ROOMS = [
    dict(id="venetian", name="The Venetian", status="Open", statusBasis="Official poker page and DeepStack Extravaganza schedule re-read in the trip window",
         read=STRIP_ROOMS_READ, official="https://www.venetianlasvegas.com/resort/casino/poker.html", inFeed=True, flag="",
         evidence="venetianlasvegas.com poker page and dse-nov-2026 schedule"),
    dict(id="wynn", name="Wynn Las Vegas (Encore)", status="Open", statusBasis="Official poker page reachable; daily and WPT PDFs in the morning feed",
         read=STRIP_ROOMS_READ, official="https://www.wynnlasvegas.com/casino/poker", inFeed=True, flag="",
         evidence="wynnlasvegas.com/casino/poker; Wynn PDFs in the feed"),
    dict(id="bellagio", name="Bellagio", status="Open (on record)", statusBasis="Official poker page on record with weekly events; not re-read on 2026-11-17",
         read="2026-11-16", official="https://bellagio.mgmresorts.com/en/casino/poker.html", inFeed=True, flag="",
         evidence="bellagio.mgmresorts.com poker page (base read)"),
    dict(id="mgm", name="MGM Grand", status="Open (on record)", statusBasis="Official poker page on record with a daily schedule sheet; not re-read on 2026-11-17",
         read="2026-11-16", official="https://mgmgrand.mgmresorts.com/en/casino/poker-tables.html", inFeed=True, flag="",
         evidence="mgmgrand.mgmresorts.com poker page (base read)"),
    dict(id="caesars", name="Caesars Palace", status="Open (daily schedule read from official flyer)",
         statusBasis="Official Caesars Palace casino page (read 2026-11-18) says the poker room is open 24/7 with cash games and daily tournaments, and links the 2026 daily No-Limit Hold'em flyer, which prints four events (10 AM, 2 PM, 6 PM, 9 PM).",
         read="2026-11-18", official="https://www.caesars.com/caesars-palace/casino", inFeed=True, flag="F90",
         evidence="caesars.com/caesars-palace/casino; clv-poker-daily-nlh-tournament-flyer-2026.pdf"),
    dict(id="horseshoe", name="Horseshoe Las Vegas", status="Open (no schedule read)", statusBasis="Room name from the prior-session Horseshoe casino page (Hall of Fame Poker Room); not re-read 2026-11-17; no schedule read",
         read=STRIP_ROOMS_READ, official="https://www.caesars.com/las-vegas/explore/casino/poker-tournaments-las-vegas-strip", inFeed=True, flag="",
         evidence="caesars.com poker-tournaments-las-vegas-strip (shared with Caesars Palace)"),
    dict(id="aria", name="ARIA Resort & Casino", status="Open (events unconfirmed)", statusBasis="Official page asks guests to call or check @ARIAPoker to confirm events; not re-read on 2026-11-17",
         read="2026-11-16", official="https://aria.mgmresorts.com/en/casino/poker.html", inFeed=True, flag="",
         evidence="aria.mgmresorts.com poker page (base read)"),
    dict(id="mandalay", name="Mandalay Bay", status="Open Wed–Mon, 10 AM–4 AM; closed Tuesdays",
         statusBasis="Official poker page read 2026-11-17 prints these hours and a $60–$1,000 price range, and says 'Please Visit or Call Poker Room for Details'. No tournament schedule is printed.",
         read=STRIP_ROOMS_READ, official="https://mandalaybay.mgmresorts.com/en/casino/poker-tables.html", inFeed=True, flag="F85",
         evidence="mandalaybay.mgmresorts.com/en/casino/poker-tables.html"),
    dict(id="planet_hollywood", name="Planet Hollywood", status="Reported closed after 31 Jan 2026 (press; unverified)",
         statusBasis=("Press search result (Review-Journal; article not fetched) reports a Caesars Entertainment statement that the room closes after 31 January 2026. "
                      "The official statement and the Planet Hollywood poker page were not retrieved."),
         read=STRIP_ROOMS_READ, official="", inFeed=False, flag="F79",
         evidence="Press search result only (Review-Journal; article not fetched); no official page retrieved"),
    dict(id="resorts_world", name="Resorts World Las Vegas", status="Reported closed 30 Mar 2026 (press; unverified)",
         statusBasis=("Press search result (casino.org / Vital Vegas; article not fetched) reports a resort statement that the room closes on March 30. "
                      "The official rwlasvegas poker page was not retrieved (the address that resolved is a marketing e-mail)."),
         read=STRIP_ROOMS_READ, official="", inFeed=False, flag="F80",
         evidence="Press search result only (casino.org / Vital Vegas; article not fetched); no official page retrieved"),
]


def _plan_eligible(e):
    """Can this event appear in the provisional planning shortlist?

    Ranking needs a confirmed entry fee and guarantee, a one-buy-in sheet with
    no extra-entry clause printed, no age/gender/team restriction, and a venue
    inside the 30-minute walking limit. The structure sheet does not prove the
    venue's maximum-entry policy; every shortlist item remains conditional on
    written confirmation before registration or nonrefundable travel.
    """
    if e["entryType"] != "none":
        return False
    if e["isContinuation"]:
        return False
    if e["eligibility"]:
        return False
    if e["format"] in ("special", "satellite"):
        return False
    if e["venue"] not in WALK:
        return False
    if WALK[e["venue"]] > PLAN_NOTES["walkLimit"]:
        return False
    if not isinstance(e["buyIn"], (int, float)) or not e["buyIn"]:
        return False
    if not isinstance(e["guarantee"], (int, float)) or not e["guarantee"]:
        return False
    return True


def _pool_note(e):
    """Name what a printed guarantee counts, using only the sheet's own wording.

    Bounty and PKO sheets print 'prize pool + total bounties', so their guarantee is not a
    cash prize pool. The category stays 'single' - that label answers the entry question -
    and this note carries the bounty split so the ratio is never read as a cash-only pool.
    """
    kind = e.get("kind")
    if kind == "bounty":
        return "Includes total bounties, not a cash-only prize pool"
    if kind == "pko":
        return "Progressive knockout: part of the guarantee is paid as bounties"
    if kind == "satellite":
        return "Seat prizes, not cash"
    return ""


def _plan_rank(e):
    """Biggest published guarantee first, then shortest walk, then cheaper entry."""
    guarantee = e["guarantee"] if isinstance(e["guarantee"], (int, float)) else 0
    start = clock_minutes(e["time"]) or 0
    return (-guarantee, WALK[e["venue"]], e["buyIn"], start)


def _fallback_sequence(primary, alt):
    """Can the fallback be played after the primary, under the disclosed estimates?

    Returns (status, text). The status is "after" when the fallback starts at or
    after the primary's estimated finish plus the transfer allowance, otherwise
    "replaces". Both are honest readings of the same two printed clock times: a
    fallback that starts first is an alternative to the primary, never a second
    event on the same day.
    """
    if not primary or not alt:
        return "", ""
    p_start = clock_minutes(primary["time"])
    p_end = primary.get("endEstimateMin")
    a_start = clock_minutes(alt["time"])
    if p_start is None or a_start is None or p_end is None:
        return ("unknown",
                "Timing not compared: a start time or the primary's estimated finish is not published.")
    transfer = PLAN_NOTES["transfer"]
    if a_start >= p_end + transfer:
        return ("after",
                f"Playable after the primary: it starts at {alt['time']}, after the primary's estimated "
                f"{primary['endEstimate']} finish plus the {transfer}-minute transfer.")
    if a_start > p_start:
        return ("replaces",
                f"Replaces the primary, not a second entry: it starts at {alt['time']}, before the primary's "
                f"estimated {primary['endEstimate']} finish. It is only playable if the player is out of the primary "
                f"in time to register, and it closes at {alt.get('lateRegEnd') or 'an unpublished time'}.")
    return ("replaces",
            f"Replaces the primary, not a second entry: it starts at {alt['time']}, before the primary starts at "
            f"{primary['time']}.")


def _fallback_reason(primary, alt):
    if alt["entryType"] != "none":
        return ("Different format: this row is a multi-flight, satellite or series event, so it is listed as an "
                "alternative and not as a single-entry option.")
    if not isinstance(alt["guarantee"], (int, float)):
        return ("No published guarantee on the official sheet, so it is not ranked; shown as the alternative for this "
                "date.")
    if alt["guarantee"] < primary["guarantee"]:
        return (f"Smaller published guarantee (${alt['guarantee']:,} against ${primary['guarantee']:,}), so it is the "
                "conditional fallback rather than the primary.")
    if WALK.get(alt["venue"], 99) > WALK.get(primary["venue"], 0):
        return (f"Same published guarantee but {WALK.get(alt['venue'], '?')} minutes' walk from the recommended hotel "
                f"against {WALK.get(primary['venue'], 0)}.")
    return "Next sheet-screened candidate on this date; entry cap still needs written confirmation."


def _starts_after_primary_finish(primary, alt):
    """Does `alt` start after the primary's estimated finish plus the transfer?

    No venue publishes a finish time, so the primary's end is the session-length
    assumption. A candidate that starts before that end cannot be played after the
    primary, so it is not a fallback for the day - it is a same-day *alternative*.
    """
    start_alt = clock_minutes(alt["time"])
    start_primary = clock_minutes(primary["time"])
    end_primary = primary.get("endEstimateMin")
    if start_alt is None or start_primary is None or end_primary is None:
        return False
    return start_alt >= end_primary + PLAN_NOTES["transfer"]



def build_day_plan(events, start_date, end_date, recurring=()):
    """Build the one-primary-per-day plan plus the impossible-sequence flags."""
    by_date = {}
    for e in events:
        if e["date"] and start_date <= e["date"] <= end_date:
            by_date.setdefault(e["date"], []).append(e)
    plan = []
    conflicts = []
    for date in sorted(by_date):
        eligible = sorted([e for e in by_date[date] if _plan_eligible(e)], key=_plan_rank)
        primary = eligible[0] if eligible else None
        fallback = None
        fallback_alternative = None
        fallback_reason = ""
        if primary:
            rest = eligible[1:]
            # Fallback rule, applied literally: the fallback must start after the primary's
            # estimated finish plus the transfer. A row that starts inside the primary's
            # session is published separately as a same-day alternative, because calling it a
            # fallback would contradict the rule printed directly beneath the plan.
            if rest:
                after = [e for e in rest if _starts_after_primary_finish(primary, e)]
                if after:
                    fallback = after[0]
                    fallback_reason = _fallback_reason(primary, fallback)
                else:
                    fallback_alternative = rest[0]
                    fallback_reason = (
                        f"No published event on this date starts after the primary's estimated finish "
                        f"({primary['endEstimate']}) plus the {PLAN_NOTES['transfer']}-minute transfer. The next-best "
                        f"candidate, {rest[0]['name']} at {rest[0]['time']}, starts inside the primary's session and is "
                        f"therefore a same-day alternative, not a fallback: it can only be played if the player is out "
                        f"of the primary in time to register for it.")
            else:
                others = [e for e in by_date[date]
                          if e["id"] != primary["id"] and not e["isContinuation"]
                          and e["entryType"] == "none" and not e["eligibility"]]
                if others:
                    others.sort(key=lambda x: (not isinstance(x["guarantee"], (int, float)), x["time"]))
                    if _starts_after_primary_finish(primary, others[0]):
                        fallback = others[0]
                        fallback_reason = _fallback_reason(primary, fallback)
                    else:
                        fallback_alternative = others[0]
                        fallback_reason = (
                            f"The only other sheet-screened candidate on this date is {others[0]['name']} at "
                            f"{others[0]['time']}, which starts inside the primary's estimated session. It is a "
                            f"same-day alternative, not a fallback. {_fallback_reason(primary, others[0])}")
                else:
                    fallback_reason = ("No other sheet-screened candidate is published for this date. The multi-flight "
                                       "and series rows for this date are listed in the tournaments table.")
        else:
            fallback_reason = "No sheet-screened candidate with a published fee and guarantee on this date."
        for a in by_date[date]:
            if a["isContinuation"]:
                continue
            for b in by_date[date]:
                if b["isContinuation"] or a["id"] >= b["id"]:
                    continue
                if not (_plan_eligible(a) or _plan_eligible(b)):
                    continue
                sa, sb = clock_minutes(a["time"]) or 0, clock_minutes(b["time"]) or 0
                if sa == sb:
                    continue
                first, second = (a, b) if sa < sb else (b, a)
                end = first["endEstimateMin"]
                if end is None:
                    continue
                if sb < end + PLAN_NOTES["transfer"]:
                    conflicts.append(dict(
                        date=date, first=first["id"], second=second["id"],
                        firstName=first["name"], secondName=second["name"],
                        firstVenue=first["venue"], secondVenue=second["venue"],
                        firstStart=first["time"], secondStart=second["time"],
                        firstEnd=first["endEstimate"], secondVenueWalk=WALK.get(second["venue"], ""),
                        detail=(f"{first['name']} at {first['time']} is estimated to end at {first['endEstimate']}; "
                                f"{second['name']} starts at {second['time']}, which is inside the estimated session "
                                f"plus the 30-minute transfer.")))
        # One call, two readings: the other session's 'after/replaces' classification is
        # derived from the same two printed clock times as the selection above, so the label
        # on the page is generated rather than asserted.
        sequence_status, sequence_note = _fallback_sequence(primary, fallback) if fallback else ("", "")
        plan.append(dict(
            date=date,
            weekday=datetime.date.fromisoformat(date).strftime("%A"),
            recurring=[dict(id=e["id"], venue=e["venue"], name=e["name"], time=e["time"],
                            buyIn=e["buyIn"], guarantee=e["guarantee"], walk=WALK.get(e["venue"], ""),
                            category=e["category"], entryType=e["entryType"], format=e["format"])
                       for e in recurring
                       if datetime.date.fromisoformat(date).weekday() in (e.get("weekdays") or [])],
            primary=primary["id"] if primary else "",
            primaryName=primary["name"] if primary else "",
            primaryVenue=primary["venue"] if primary else "",
            primaryTime=primary["time"] if primary else "",
            primaryEnd=primary["endEstimate"] if primary else "",
            primaryBuyIn=primary["buyIn"] if primary else "",
            primaryGuarantee=primary["guarantee"] if primary else "",
            primaryWalk=WALK.get(primary["venue"], "") if primary else "",
            primaryLateReg=primary["lateReg"] if primary else "",
            primaryChips=primary["chips"] if primary else "",
            primaryFormat=primary["format"] if primary else "",
            primaryLateEnd=primary["lateRegEnd"] if primary else "",
            fallback=fallback["id"] if fallback else "",
            fallbackName=fallback["name"] if fallback else "",
            fallbackVenue=fallback["venue"] if fallback else "",
            fallbackTime=fallback["time"] if fallback else "",
            fallbackBuyIn=fallback["buyIn"] if fallback else "",
            fallbackGuarantee=fallback["guarantee"] if fallback else "",
            fallbackWalk=WALK.get(fallback["venue"], "") if fallback else "",
            fallbackFormat=fallback["format"] if fallback else "",
            fallbackReason=fallback_reason,
            fallbackSequence=sequence_status,
            fallbackSequenceNote=sequence_note,
            fallbackAlternativeId=fallback_alternative["id"] if fallback_alternative else "",
            fallbackAlternativeName=fallback_alternative["name"] if fallback_alternative else "",
            fallbackAlternativeTime=fallback_alternative["time"] if fallback_alternative else "",
            candidates=len(eligible),
            primaryGuaranteeNote=_pool_note(primary) if primary else "",
            fallbackGuaranteeNote=_pool_note(fallback) if fallback else "",
            # The Venetian poker-suite rate is conditional: the official rate page requires
            # "six hours of active live cash gameplay or buy in to a $300 or higher tournament
            # for each night stayed". A night whose only planned entry is under $300 is shown as
            # not satisfying the published condition, so the room may be repriced at checkout.
            pokerRateCondition=RATE_QUALIFICATION_TEXT,
            pokerRateSatisfied=bool(primary) and (primary.get("buyIn") or 0) >= 300,
            pokerRateBasis=(f"Planned primary entry ${primary['buyIn']} is at or above the $300 threshold published on the "
                            f"poker-suite rate page." if primary and (primary.get("buyIn") or 0) >= 300 else
                            (f"Planned primary entry ${primary['buyIn']} is below the $300 threshold published on the "
                             f"poker-suite rate page, so this night does not satisfy the condition as the plan stands."
                             if primary else "No primary event is planned for this date.")),
        ))
    return plan, conflicts



BOOKING_LINKS = [dict(
    hotel="venetian", property="The Venetian and The Palazzo (one booking engine)",
    stay="2026-11-23 to 2026-11-30 (7 nights, check-out 30 Nov), 2 adults, 0 children",
    url=H.VENETIAN_FIXED_STAY_BOOKING, checkedOn=CHECKED_TODAY,
    priceInStaticPage=("Yes. On 2026-11-17 (after 21:54 UTC) the engine printed an itemised checkout total of $4,010.55 for "
                       "this stay: nightly rates of $164.25 to $1,649.25 before a $55 resort fee per night, plus $473.30 tax. "
                       "The calendar cells on the same page are not the quote (F69). The phone-only poker rate is separate (F66)."),
    source=H.VENETIAN_FIXED_STAY_BOOKING,
    feeSource="https://www.venetianlasvegas.com/resort/resort-fee.html",
)]


def build():
    events = []

    # --- Venetian DSE IV -------------------------------------------------
    for date, time, no, name, sheet, guarantee, category in V.DSE_ROWS:
        s = V.SHEETS[sheet]
        url = f"{V.BASE}/dse_nov_2026-structure_{sheet}.pdf"
        cont = is_continuation(name)
        guarantee_value = guarantee
        guarantee_note = ""
        if not guarantee_value and s.get("kind") == "satellite" and s.get("guarantee"):
            guarantee_value = s["guarantee"]
            guarantee_note = "seat prizes, not cash"
        events.append(_event(
            f"vl-dse-{date}-{no}-{time.replace(':', '').replace(' ', '').lower()}",
            "venetian", date, time, name, s["buyIn"], guarantee_value, _rules_for_sheet(sheet),
            category, s["kind"], url, V.DSE, url,
            last_checked=REREAD_DATE if (date, no) in REREAD_ROWS else ASOF,
            note=s.get("note", "") + (s.get("entryExcerpt", "") if s.get("entryExcerpt") else ""),
            eligibility=s.get("eligibility", ""),
            guarantee_note=(guarantee_note or "multi-flight" if s["kind"] == "flight"
                            else guarantee_note
                            or ("includes bounties" if ("bounties" in s["guarantee"] or "Bounty" in name
                                                       or "PKO" in name or "Knock-Out" in name) else "")),
            chips=s.get("chips", ""), level_min=s.get("levelMin", ""),
            late_reg=DSE_REG_CLOSES.get((date, no), s.get("late", "")),
            entry_type=s["entry"], continuation=cont,
        ))

    # --- Venetian DSE NYE ------------------------------------------------
    # All 15 NYE structure sheets were read in full on 2026-11-17. Each row now
    # carries the facts printed on its own sheet, and the entry rule is taken
    # from the sheet's own wording: an explicit re-entry sentence makes the row
    # a multi-buy-in; a bagging sentence makes it a multi-flight; a sheet that
    # prints none of those gets the same "no re-entry printed" status as DSE IV.
    for date, time, no, name, sheet_file, guarantee, category in V.NYE_ROWS:
        url = f"{V.BASE}/{sheet_file}"
        n = int(re.search(r"structure_(\d+)\.pdf$", sheet_file).group(1))
        sh = V.NYE_SHEETS[n]
        entry = sh["entry"]
        # All 15 NYE sheets were read in full on 2026-11-17, so no NYE row is left
        # "unverified". The category answers the entry question and is derived from
        # the sheet's own wording below, so a stale literal can never disagree with
        # the rule text it is paired with.
        category = {"none": "single", "multi-flight": "flight",
                    "multi-buyin": "extra", "satellite": "satellite"}[entry]
        if entry == "none":
            se_status = "single-entry-on-sheet"
            se_excerpt = (f"The sheet prints one ${sh['buyIn']:,} buy-in, one start flight and one starting-chips figure "
                          f"({sh['chips']:,}). No re-entry, rebuy, add-on or second-flight provision appears anywhere on "
                          f"the sheet. The sheet does not state a per-player maximum-entry count or explicitly call the "
                          f"event a freezeout; venue confirmation is still required.")
            re_status, re_excerpt = "none-printed", "No re-entry provision appears on this structure sheet."
            ao_status, ao_excerpt = "none-printed", "No add-on provision appears on this structure sheet."
            etype = "none"
        elif entry == "multi-flight":
            se_status = "multiple-entries"
            se_excerpt = sh.get("entryExcerpt", "The sheet publishes separate starting flights.")
            re_status, re_excerpt = "separate-flights", "Separate starting flights are published on the schedule."
            ao_status, ao_excerpt = "none-printed", "No add-on provision appears on this structure sheet."
            etype = "multi-flight"
        elif entry == "multi-buyin":
            se_status = "multiple-entries"
            se_excerpt = sh.get("entryExcerpt", "The sheet allows more than one buy-in.")
            re_status, re_excerpt = "re-entry-allowed", sh.get("entryExcerpt", "")
            ao_status, ao_excerpt = "none-printed", "No add-on provision appears on this structure sheet."
            etype = "multi-buyin"
        else:
            se_status = "not-allowed"
            se_excerpt = ("Seat prize only: the sheet awards direct entry into another event, so there is no cash "
                          "prize pool and no freezeout entry rule to apply.")
            re_status, re_excerpt = "not-applicable", "Satellite: entry rules of the target event apply."
            ao_status, ao_excerpt = "none-printed", "No add-on provision appears on this structure sheet."
            etype = "satellite"
        rules = dict(
            singleEntry=dict(status=se_status, excerpt=se_excerpt, source=url, retrieved=VERIFIED_ON),
            reEntry=dict(status=re_status, excerpt=re_excerpt, source=url, retrieved=VERIFIED_ON),
            addOn=dict(status=ao_status, excerpt=ao_excerpt, source=url, retrieved=VERIFIED_ON),
            fee=dict(status="confirmed",
                     excerpt=(f"${sh['rake']} of the ${sh['buyIn']:,} buy-in is withheld for house fees (rake + staff); "
                              f"the prize pool consists of ${sh['pool']} of every ${sh['buyIn']:,} buy-in."),
                     source=url, retrieved=VERIFIED_ON),
        )
        cont = is_continuation(name)
        events.append(_event(
            f"vl-nye-{date}-{no}-{time.replace(':', '').replace(' ', '').lower()}",
            "venetian", date, time, name, sh["buyIn"], guarantee, rules, category, sh["kind"], url, V.NYE, url,
            note=("DeepStack Extravaganza NYE. Structure sheet read in full on 2026-11-17; the excerpt above is quoted "
                  "from it."),
            eligibility=sh.get("eligibility", ""),
            chips=sh["chips"], level_min=sh["levelMin"], late_reg=sh["late"],
            entry_type=etype, continuation=cont,
            guarantee_note=("includes bounties" if sh["kind"] == "bounty" else
                            ("seat prizes, not cash" if entry == "satellite" else
                             ("multi-flight" if entry == "multi-flight" else ""))),
        ))

    # --- Wynn daily ------------------------------------------------------
    # Most WYNN_DAILY names already print their day range (e.g. "$200 No Limit
    # Hold'em (Monday-Thursday)"). Appending the range again produced duplicated
    # labels such as "(Monday-Thursday) (Monday-Thursday)", so the suffix is only
    # added when the name does not already state the range.
    for i, d in enumerate(N.WYNN_DAILY):
        rules = {k: dict(v, source=d["source"], retrieved=ASOF) for k, v in d["rules"].items()}
        first_day = d["days"].split(",")[0].strip()
        if d["name"].endswith("Nightly") and d["days"].startswith("Nightly "):
            label = f"{d['name']} ({d['days'][len('Nightly '):]})"
        else:
            label = d["name"] if first_day in d["name"] else f"{d['name']} ({d['days']})"
        events.append(_event(
            f"wynn-daily-{i}", "wynn", "", d["time"], label,
            d["buyIn"], d["guarantee"], rules, d["category"], "daily",
            d["poster"], d["source"], d["source"],
            note=d.get("note", "") + f" Recurring {d['days'].lower()}.", last_checked=LAST_PASS,
            chips=d.get("chips", ""), level_min=d.get("levelMin", ""), late_reg=d.get("lateReg", ""),
            entry_type="multi-buyin", weekdays=d.get("weekdays", []),
        ))

    # --- Wynn WPT --------------------------------------------------------
    # The structures PDF was read in full (all eight chunks) on 2026-11-17. Every event
    # section it publishes is transcribed in raw/wynn_wpt_world_championship_structures_2026-11-17.md
    # and carried as WPT_SHEET_SECTIONS in scripts/data_venues.py. A row is matched to a
    # section only when its buy-in, its printed name and its exact date and start slot all
    # agree with that section's own printed day list, so no row inherits another event's
    # rules. Rows whose event has no section in the document keep the unverified label and
    # state that the document was read and does not cover them.
    #
    # No matched row becomes a single-entry candidate: every section prints re-entry, and
    # the Prime Championship prints "One (1) Entry and One (1) re-entry for each starting
    # flight", which is a per-flight cap and not a one-entry tournament.
    WPT_NO_SECTION = (
        "The official structures PDF was read in full on 2026-11-17 and publishes no section "
        "for this event, so no entry rule, fee split or stack is confirmed for it."
    )
    WPT_RESTART = (
        "This row resumes a field whose starting flights are published: the structures PDF "
        "gives the entry rules for the flights, not for the restart."
    )
    WPT_SATELLITE = (
        "The official structures PDF publishes no section for this satellite, so its prize "
        "structure and entry terms are unconfirmed."
    )
    for idx, line in enumerate(N.WYNN_WPT_ROWS.splitlines()):
        cells = line.split("|")
        date, time, name, buy_in, guarantee, chips, levels = cells[:7]
        marks = cells[7] if len(cells) > 7 else ""
        buy = "" if buy_in == "-" else int(buy_in)
        if guarantee == "-":
            gua = ""
        elif guarantee.replace(",", "").isdigit():
            gua = int(guarantee.replace(",", ""))
        else:
            gua = guarantee
        flight = bool(re.search(r"Day 1[A-F]\b", name))
        cat = "flight" if flight else ("satellite" if "Satellite" in name else "wpt")
        sec = N.wpt_section_for(date, time, name, buy_in if buy_in != "-" else "")
        continuation = is_continuation(name)
        # Reset per row: a value left over from the previous iteration would print one event's
        # registration cut-off on another event's row (caught by scripts/audit_951cd431.py).
        late_text = ""
        if sec:
            slot = N.wpt_slot(date, time)
            role = sec["dates"].get(slot, "")
            rules = {
                # The document prints re-entry in every section, so none of these rows can be
                # treated as single entry. The excerpt is the document's own sentence.
                "singleEntry": dict(status="multiple-entries", excerpt=sec["registration"],
                                    source=N.WYNN_WPT_STRUCT, retrieved=RECHECKED),
                "reEntry": dict(status="confirmed", excerpt=sec["registration"],
                                source=N.WYNN_WPT_STRUCT, retrieved=RECHECKED),
                "addOn": dict(status="none-printed",
                              excerpt=("The structure section for this event prints registration, stack, level "
                                       "length, breaks, table size and payouts, and no add-on or rebuy provision."),
                              source=N.WYNN_WPT_STRUCT, retrieved=RECHECKED),
                "fee": dict(status="confirmed", excerpt=sec["fee"],
                            source=N.WYNN_WPT_STRUCT, retrieved=RECHECKED),
            }
            note_bits = [
                f"Entry rules, fee split and starting stack read from this event's own section of the official "
                f"structures PDF ({sec['title']}; printed start slots: {sec['days_printed']}).",
                f"Printed stack: {sec['chips']} Printed levels: {sec['levels']}",
                (f"Section prints {sec['per_flight_cap']} — a per-flight cap, not a one-entry tournament, so this "
                 f"row stays out of the single-entry list." if sec.get("per_flight_cap") else
                 "The section prints unlimited re-entry, so this event is not a single-entry event."),
                WPT_MARK_NOTES.get(marks, ""),
            ]
            chips_value = int(chips) if chips not in ("-", "") else ""
            entry_type = "multi-flight" if flight else "multi-buyin"
            # The document prints the registration window in levels, and for two events also
            # as an approximate clock time. Only that printed clock time is carried as a
            # cut-off; a level count alone is displayed as text and never converted into a
            # time, so no session length or overlap flag is invented from it.
            approx = re.search(r"approximately ([0-9]{1,2}:[0-9]{2} [ap]\.m\.)", sec["registration"])
            if "level 9" in sec["registration"]:
                late_text = ("Level 9 (approximately %s)" % approx.group(1)
                             if approx else "Start of level 9")
            elif "level 10" in sec["registration"]:
                late_text = ("Level 10 (approximately %s)" % approx.group(1)
                             if approx else "Start of level 10")
            else:
                late_text = ""
        else:
            if continuation:
                reason, status_excerpt = WPT_RESTART, WPT_RESTART
            elif "Satellite" in name:
                reason, status_excerpt = WPT_SATELLITE, WPT_SATELLITE
            else:
                reason, status_excerpt = WPT_NO_SECTION, WPT_NO_SECTION
            rules = {
                "singleEntry": dict(status="not-verified", excerpt=status_excerpt,
                                    source=N.WYNN_WPT_STRUCT, retrieved=RECHECKED),
                "reEntry": dict(status="not-verified", excerpt=status_excerpt,
                                source=N.WYNN_WPT_STRUCT, retrieved=RECHECKED),
                "addOn": dict(status="not-verified", excerpt=status_excerpt,
                              source=N.WYNN_WPT_STRUCT, retrieved=RECHECKED),
                "fee": dict(status="confirmed" if buy_in != "-" else "not-verified",
                            excerpt=(f"Buy-in ${buy_in} and guarantee ${guarantee} are printed on the official "
                                     f"schedule PDF; no fee split is published for this event."
                                     if buy_in != "-" else
                                     "The schedule PDF prints no buy-in for this row, and the structures PDF "
                                     "publishes no section for it."),
                            source=N.WYNN_WPT_SCHED, retrieved=ASOF),
            }
            note_bits = [
                ("Multiple start flights are published for this event, so more than one entry is possible."
                 if flight else
                 ("Schedule row from the official WPT World Championship schedule PDF."
                  if not continuation else
                  "Schedule row from the official WPT World Championship schedule PDF; it resumes an earlier flight.")),
                reason, WPT_MARK_NOTES.get(marks, ""),
            ]
            chips_value = int(chips) if chips not in ("-", "") else ""
            entry_type = "multi-flight" if flight else "not-verified"
        events.append(_event(
            f"wynn-wpt-{date}-{idx:03d}-{time.replace(':', '').replace(' ', '').lower()}",
            "wynn", date, time, name, buy, gua, rules, cat, "wpt",
            N.WYNN_WPT_SCHED, N.WYNN_WPT_SCHED, N.WYNN_WPT_STRUCT,
            note=" ".join(x for x in note_bits if x).strip(),
            chips=chips_value, entry_type=entry_type,
            continuation=continuation, late_reg=late_text,
            level_min=(int(levels.split("/")[0]) if sec and levels not in ("-", "") else ""),
        ))

    # --- Wynn Signature Series ------------------------------------------
    # The official structures file cited below was re-read on 2026-11-17 and prints only
    # "LAS VEGAS POKER / COMING SOON"; the schedule tells guests to scan a QR code for structures.
    # Entry rules are therefore left not verified rather than inferred (F56).
    SIG_STRUCT_GAP = ("The official Wynn Signature Series structures file printed only 'LAS VEGAS POKER - COMING SOON' "
                      "when it was re-read on 2026-11-17, and the schedule PDF directs guests to scan a QR code for "
                      "event structures, so no entry rule is published in readable form for this event.")
    for idx, line in enumerate(N.WYNN_SIGNATURE_ROWS.splitlines()):
        cells = line.split("|")
        date, time, name, buy_in, guarantee, chips, levels = cells[:7]
        marks = cells[7] if len(cells) > 7 else ""
        buy = "" if buy_in == "-" else int(buy_in)
        if guarantee == "-":
            gua = ""
        elif guarantee.replace(",", "").isdigit():
            gua = int(guarantee.replace(",", ""))
        else:
            gua = guarantee
        flight = bool(re.search(r"Day 1[A-F]\b", name))
        cat = "flight" if flight else ("satellite" if "Satellite" in name else "wpt")
        rules = {
            "singleEntry": dict(status="not-verified",
                                excerpt=SIG_STRUCT_GAP, source=N.WYNN_SIG_STRUCT, retrieved=VERIFIED_ON),
            "reEntry": dict(status="not-verified", excerpt=SIG_STRUCT_GAP,
                            source=N.WYNN_SIG_STRUCT, retrieved=VERIFIED_ON),
            "addOn": dict(status="not-verified", excerpt=SIG_STRUCT_GAP,
                          source=N.WYNN_SIG_STRUCT, retrieved=VERIFIED_ON),
            "fee": dict(status="confirmed", excerpt=f"Buy-in ${buy_in} and guarantee ${guarantee} are printed on the official schedule PDF.",
                        source=N.WYNN_SIG_SCHED, retrieved=ASOF),
        }
        events.append(_event(
            f"wynn-sig-{date}-{idx:03d}-{time.replace(':', '').replace(' ', '').lower()}",
            "wynn", date, time, name, buy, gua, rules, cat, "wpt",
            N.WYNN_SIG_SCHED, N.WYNN_SIG_SCHED, N.WYNN_SIG_STRUCT,
            note=" ".join(x for x in [
                ("Multiple start flights are published for this event." if flight else
                 "Wynn Signature Series row from the official schedule PDF; entry rules not yet read."),
                SIG_MARK_NOTES.get(marks, "")] if x).strip(),
            chips=int(chips) if chips not in ("-", "") else "", entry_type=("multi-flight" if flight else "not-verified"),
            continuation=is_continuation(name),
        ))

    # --- Other venues ----------------------------------------------------
    def add_group(group, venue, prefix, last_checked=ASOF):
        for i, d in enumerate(group):
            rules = {k: dict(v, source=v.get("source", d["source"]), retrieved=v.get("retrieved", ASOF)) for k, v in d["rules"].items()}
            st = rules["singleEntry"]["status"]
            entry_type = ("none" if st == "single-entry-on-sheet"
                          else ("not-verified" if "not-verified" in st else "multi-buyin"))
            events.append(_event(
                f"{prefix}-{i}", d.get("venue", venue), "", d["time"],
                f"{d['name']} ({d['days']})" if d.get("days") else d["name"],
                d.get("buyIn", ""), d.get("guarantee", ""), rules,
                d.get("category", "recurring"), "recurring",
                d["source"], d["source"], d.get("page", d["source"]),
                note=d.get("note", ""), last_checked=last_checked,
                chips=d.get("chips", ""), level_min=d.get("levelMin", ""),
                late_reg=d.get("lateReg", ""), entry_type=entry_type,
                weekdays=d.get("weekdays", []),
            ))

    add_group(N.BELLAGIO_EVENTS, "bellagio", "bell")
    add_group(N.MGM_EVENTS, "mgm", "mgm")
    add_group(N.CAESARS_EVENTS, "caesars", "caes", last_checked="2026-11-18")  # flyer read 2026-11-18
    add_group(N.HORSESHOE_EVENTS, "horseshoe", "horse", last_checked=CHECKED_TODAY)
    add_group(N.ARIA_EVENTS, "aria", "aria")

    hotels = []
    for h in H.HOTELS:
        row = dict(h)
        low = high = ""
        if h.get("baseRateFloor") and h.get("resortFee") and h.get("taxRate"):
            low = round((h["baseRateFloor"] + h["resortFee"]) * (1 + h["taxRate"] / 100), 2)
            high = round((h["baseRateCeiling"] + h["resortFee"]) * (1 + h["taxRate"] / 100), 2)
        row["trueNightlyLow"] = low
        row["trueNightlyHigh"] = high
        # lastChecked is per row and records only properties whose page this build actually re-read.
        # 2026-11-17 re-reads (session 58e42dbd, live): Venetian + Palazzo poker-suite rates, resort fee and
        # hotel terms; Wynn Resort Policies + Terms; Bellagio poker page and hotel reservation terms;
        # MGM Grand poker page, hotel page and hotel reservation terms; ARIA poker page and reservation terms;
        # Caesars Palace / Horseshoe tournament page. 2026-11-16 is the earlier capture date.
        _reread_today = ("venetian", "palazzo", "caesars", "horseshoe", "wynn", "bellagio", "mgm", "aria")
        # Where a property prints its resort fee and the tax on that fee as two dollar amounts, the
        # implied percentage is arithmetic on its own page, not an assumption borrowed from another
        # property's terms.  It corroborates the 13.38% the cost model applies; it does not replace
        # taxRate, which stays blank until the property prints a room-tax percentage for the rate.
        paid = h.get("printedFeeAndTax")
        if paid:
            implied = round(paid["tax"] / paid["fee"] * 100, 3)
            row["printedFeeAndTax"] = dict(paid, taxPctImplied=implied,
                                           agreesWithModelTaxPct=abs(implied - 13.38) < 0.02)
        row["lastChecked"] = (CHECKED_TODAY if h["id"] in _reread_today else ASOF)
        row["lastVerified"] = VERIFIED_ON
        # Facts confirmed live on 2026-11-17 that the earlier build left blank.
        if h.get("id") in ("venetian", "palazzo"):
            row["parking"] = row.get("parking") or ""
            row["parkingPerNight"] = LIVE_FACTS_2026_11_17["venetianParkingPerNight"]
            row["parkingNote"] = LIVE_FACTS_2026_11_17["venetianParkingExcerpt"]
            row["checkInOut"] = LIVE_FACTS_2026_11_17["venetianCheckInOut"]
            row["cancellationDetail"] = LIVE_FACTS_2026_11_17["venetianCancellation"]
            row["cancellationDetailSource"] = LIVE_FACTS_2026_11_17["venetianParkingSource"]
        if h.get("id") == "wynn":
            row["checkInOut"] = LIVE_FACTS_2026_11_17["wynnCheckInOut"]
            row["registrationNote"] = LIVE_FACTS_2026_11_17["wynnRegistrationNote"]
            row["registrationSource"] = LIVE_FACTS_2026_11_17["wynnRegistrationSource"]
            row["feeDetailNote"] = LIVE_FACTS_2026_11_17["wynnFeeNote"]
        if h.get("id") == "bellagio":
            row["incidental"] = LIVE_FACTS_2026_11_17["bellagioIncidental"]
            row["cancellationDetail"] = LIVE_FACTS_2026_11_17["bellagioCancellation"]
            row["cancellationDetailSource"] = row.get("cancellationSource", "")
        row["trueNightlyLow"] = row["trueNightlyLow"]
        # The Venetian and Palazzo rows were re-queried on the official booking engine on
        # 2026-11-17, so their lastChecked moves to that date; every other property keeps
        # the base snapshot date because its page was not opened today.
        if h["id"] in ("venetian", "palazzo"):
            row["lastChecked"] = VERIFIED_ON
        hotels.append(row)

    routes = []
    for r in H.ROUTES:
        row = dict(r)
        row["mapsUrl"] = H.MAPS.format(o=r["mapsOrigin"], d=r["mapsDestination"])
        # Each route row carries its own measurement date: the 2026-11-17 full-matrix pass
        # writes measuredOn, the poker-room-endpoint read writes lastReadOn, and base-pass
        # rows keep the base snapshot date.
        row["lastChecked"] = r.get("measuredOn") or r.get("lastReadOn") or ASOF
        row["walkSourceType"] = (f"Google Maps walking directions (walking mode), read {r['lastReadOn']}"
                                 if r.get("walkCapture") else "Google Maps walking estimate, not re-read 2026-11-17")
        routes.append(row)

    # Live re-check of the official DeepStack Extravaganza IV page, 2026-11-17. Two windows, because the two
    # checks compared different things: rows dated 2026-11-16 to 2026-11-27 (chunk 0 of the page) were matched on
    # date, start time, event name, buy-in, guarantee and structure-sheet link; rows dated 2026-11-28 to 2026-12-23
    # (chunks 1 to 3) were matched on date, start time, event name, buy-in and guarantee only, and their structure
    # links were not compared.
    n_first = n_second = 0
    for e in events:
        if e["venue"] == "venetian" and e["date"] and RECHECK_FROM <= e["date"] <= RECHECK_TO:
            e["lastChecked"] = RECHECKED
            if e["date"] < "2026-11-28":
                e["recheck"] = dict(date=RECHECKED, source=DSE_NOV_URL,
                                    result="matched on date, start time and structure link")
                n_first += 1
            else:
                e["recheck"] = dict(date=RECHECKED, source=DSE_NOV_URL,
                                    result=("matched on date, start time, event name, buy-in and guarantee; "
                                            "structure links not compared"))
                n_second += 1
    assert n_first == 21 and n_second == 73, f"re-check windows: expected 21 and 73, got {n_first} and {n_second}"

    # Wynn WPT: every row whose own section of the structures PDF prints its rules.
    #
    # The match is made by N.wpt_section_for() on date + start slot + buy-in + printed name,
    # so a row can only take the clause that its own section prints. The earlier version of
    # this block matched six rows by id against a hand-kept list whose excerpts were
    # paraphrases rather than the printed text; the excerpts now come from the document
    # (raw/wynn_wpt_world_championship_structures_2026-11-17.md) and flag F77 records the
    # correction.
    n_wpt_sections = 0
    for ev in events:
        if ev["venue"] != "wynn" or not ev["id"].startswith("wynn-wpt-"):
            continue
        sec = N.wpt_section_for(ev["date"], ev["time"], ev["name"], ev["buyIn"])
        if not sec:
            continue
        src = N.WYNN_WPT_STRUCT
        on = RECHECKED
        ev["rules"]["singleEntry"] = dict(status="multiple-entries", excerpt=sec["registration"], source=src, retrieved=on)
        ev["rules"]["reEntry"] = dict(status="confirmed", excerpt=sec["registration"], source=src, retrieved=on)
        ev["rules"]["addOn"] = dict(
            status="none-printed",
            excerpt=("The structure section for this event prints registration, stack, level length, breaks, table "
                     "size and payouts, and no add-on or rebuy provision."),
            source=src, retrieved=on)
        ev["rules"]["fee"] = dict(status="confirmed", excerpt=sec["fee"], source=src, retrieved=on)
        ev["lastChecked"] = on
        ev["note"] = (f"Official structures PDF, read in full 2026-11-17. Section: {sec['title']}. "
                      f"Printed start slots: {sec['days_printed']}. Fee split and registration quoted verbatim above.")
        n_wpt_sections += 1
    assert n_wpt_sections == 35, f"expected 35 WPT rows matched to their own printed section, got {n_wpt_sections}"


    # Live re-check, 2026-11-17 (session c1655bf5): the official WPT World Championship schedule PDF
    # was re-fetched independently and every published Wynn row across the range that PDF covers,
    # 2026-11-25 to 2026-12-02, was matched on date, start time, buy-in and guarantee: 19 rows. This
    # complements the structure-level REREAD above (which covers the rows whose structure section that
    # PDF prints) by also recording the rows the REREAD does not list.
    #
    # The range is deliberately the PDF's own coverage and NOT the trip window. The trip moved to
    # 2026-11-23..2026-11-30 (flag F51: 30 Nov and 1 Dec print no price, so a stay cannot span them),
    # and scoping this re-check to the trip window would have silently withdrawn the re-check
    # evidence from the 1 and 2 December rows, which were read just as carefully as the others.
    # Evidence of a read belongs to the rows that were read, not to the window we happen to advise.
    WPT_SCHEDULE_URL = ("https://cdn.wynnresorts.com/image/upload/v1757097329/visitwynn_pdfs_files/"
                        "Poker/WPT/WPT_World_Championship_Schedule.pdf")
    WPT_REREAD_FROM, WPT_REREAD_TO = "2026-11-25", "2026-12-02"
    n2 = 0
    for e in events:
        if e["venue"] == "wynn" and e["date"] and WPT_REREAD_FROM <= e["date"] <= WPT_REREAD_TO:
            e["lastChecked"] = RECHECKED
            e["recheck"] = dict(date=RECHECKED, source=WPT_SCHEDULE_URL,
                                result="matched on date, start time, buy-in and guarantee")
            n2 += 1
    assert n2 == 19, (
        f"expected 19 re-checked Wynn rows across {WPT_REREAD_FROM}..{WPT_REREAD_TO}, got {n2}. "
        "This range is the coverage of the official WPT schedule PDF, not the trip window; if the PDF "
        "changes, re-read it and update both together.")

    # lastChecked is per row, not per build. Every row on the official DSE IV schedule page
    # was re-read against that page on 2026-11-17 (scripts/verify_live_official.py compares
    # all 94 of them line by line), so those rows carry the later date. Every other row keeps
    # the date of the pass that last read it, including the rows the block above re-read.
    for e in events:
        if RECHECKED_TODAY in (e.get("scheduleUrl") or ""):
            e["lastChecked"] = RECHECKED

    # ------------------------------------------------------------------ third live pass, 2026-11-19
    # Read live on 2026-11-19 through the platform page reader (the build sandbox cannot open
    # these hosts itself; F40).  The rows below were compared field by field with what the
    # official pages printed, the comparison is asserted by
    # scripts/verify_live_2026_11_19.py against raw/dse_schedule_live_2026_11_19_9b858e66.md,
    # and NO value changed.  Only the read date moves.
    #
    #   dse-nov-2026.html  chunk 0-3  -> 29 rows (the 24-row trip window 23 Nov - 2 Dec, the
    #                                    09:10 satellite that settles the 8 a.m. question, and
    #                                    the NYE rows that print the year 2025) all agreed on
    #                                    date, start time, event number, printed buy-in and
    #                                    structure-sheet link.
    #   dse-dec-2026.html  chunk 0    -> the 2025 year typo is still printed (F04/F41).
    #   Venetian suite rates, resort fee and hotel terms -> $119/$209 starting rates, $55 resort
    #                                    fee plus tax, 13.38% Clark County room tax, $20/day guest
    #                                    self-parking, 3:00 p.m. check-in, 11:00 a.m. check-out,
    #                                    $150 incidental and the $100 early-checkout charge all
    #                                    reprinted unchanged.  The booking engine again returned
    #                                    a reservation shell with no checkout total (F15 stays
    #                                    resolved by the 2026-11-17 read; this pass adds none).
    #   Wynn poker page, Resort Policies and Parking -> daily slate, $55 + tax resort fee,
    #                                     check-in 3 p.m./check-out 12 p.m., $25 non-guest self
    #                                    parking and $40 valet unchanged.
    #   Bellagio poker page and reservation terms -> the same three weekly PDFs, the same undated
    #                                    "July 26" resumption notice (F03), $55 + tax resort fee,
    #                                    72-hour cancellation unchanged.
    #   Wynn Signature Series structures PDF -> still the "COMING SOON" placeholder (F56).
    LIVE_2026_11_19 = "2026-11-19"
    n_third = 0
    for e in events:
        if (e["venue"] == "venetian" and e["date"] and
                ("2026-11-23" <= e["date"] <= "2026-12-02" or e["id"] == "vl-dse-2026-12-12-46-910am")):
            e["lastChecked"] = LIVE_2026_11_19
            e["recheck"] = dict(date=LIVE_2026_11_19, source=DSE_NOV_URL,
                                result=("matched the live official page on date, start time, event number, printed "
                                        "buy-in and structure-sheet link; no value changed"))
            n_third += 1
    assert n_third == 25, f"2026-11-19 live pass: expected 25 rows, got {n_third}"

    SOURCES_2026_11_19 = {
        DSE_NOV_URL,
        "https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-dec-2026.html",
        "https://www.venetianlasvegas.com/resort/casino/poker/suite-rates.html",
        "https://www.venetianlasvegas.com/resort/resort-fee.html",
        "https://www.venetianlasvegas.com/legal/hotel-terms-and-conditions.html",
        "https://www.venetianlasvegas.com/resort/casino/poker.html",
        "https://www.venetianlasvegas.com/resort/casino/poker/player-parking.html",
        "https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament.html",
        "https://www.wynnlasvegas.com/casino/poker",
        "https://www.wynnlasvegas.com/about-us/resort-information",
        "https://www.wynnlasvegas.com/about-us/parking",
        "https://www.wynnlasvegas.com/terms-and-conditions/850070",
        "https://www.wynnlasvegas.com/rooms-and-suites",
        "https://bellagio.mgmresorts.com/en/casino/poker.html",
        "https://bellagio.mgmresorts.com/en/terms-and-conditions.html",
        "https://cdn.wynnresorts.com/image/upload/v1762299460/visitwynn_pdfs_files/Poker/"
        "Wynn%20Signature%20Series/Wynn_Signature_Series_Structures.pdf",
    }
    for src in SOURCES:
        if src["url"] in SOURCES_2026_11_19:
            src["checked"] = LIVE_2026_11_19
    for h in hotels:
        # Only the properties whose own terms were opened again on 2026-11-19.
        if h.get("id") in ("venetian", "palazzo", "wynn", "bellagio"):
            h["lastChecked"] = LIVE_2026_11_19
            h["lastVerified"] = LIVE_2026_11_19

    # Second 2026-11-17 re-read pass (session arena-196dc009): schedule pages and
    # hotel terms fetched again that day and compared with the published rows.
    # Advance a date only where the URL behind it was re-read; everything else
    # keeps ASOF / VERIFIED_ON / LAST_PASS as set above.
    RECHECKED_URLS = {
        "https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html",
        "https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-dec-2026.html",
        "https://www.venetianlasvegas.com/resort/casino/poker/suite-rates.html",
        "https://www.venetianlasvegas.com/resort/resort-fee.html",
        "https://www.venetianlasvegas.com/legal/hotel-terms-and-conditions.html",
        "https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_dec_2026-structure_13.pdf",
        "https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_dec_2026-structure_14.pdf",
        "https://www.caesars.com/las-vegas/explore/casino/poker-tournaments-las-vegas-strip",
        "https://www.wynnlasvegas.com/casino/poker",
        "https://cdn.wynnresorts.com/image/upload/v1752011166/visitwynn_pdfs_files/Poker/Daily%20Tournaments/poker-daily-tournament-poster.pdf",
        "https://cdn.wynnresorts.com/image/upload/v1752011191/visitwynn_pdfs_files/Poker/Daily%20Tournaments/Poker-All_Daily_Structures.pdf",
        "https://cdn.wynnresorts.com/image/upload/v1757097329/visitwynn_pdfs_files/Poker/WPT/WPT_World_Championship_Schedule.pdf",
        "https://www.wynnlasvegas.com/terms-and-conditions/850070",
        "https://bellagio.mgmresorts.com/en/casino/poker.html",
        "https://assets.contentstack.io/v3/assets/bltc6ce635bc4868eb2/bltb202e65a90a1327d/85a065bdcab3b356884f4873f3ad8042/mgm-bellagio-poker-fridays-$600-nlh.pdf",
        "https://assets.contentstack.io/v3/assets/bltc6ce635bc4868eb2/blt9cf95b0e60ec253e/6af491a3a9851d75c40be840/mgm-bellagio-poker-fridays-$600-nlh.pdf",
        "https://assets.contentstack.io/v3/assets/bltc6ce635bc4868eb2/blt6d47974bf5a7d9b6/6af491a391a6e8e4230c9e07/mgm-bellagio-poker-saturdays-$1000-nlh.pdf",
        "https://assets.contentstack.io/v3/assets/bltc6ce635bc4868eb2/blte904386f4117e230202cb512347e3b85/mgm-bellagio-poker-sundays-$400-horse.pdf",
        "https://assets.contentstack.io/v3/assets/bltc6ce635bc4868eb2/blt07fcf1244a6da661/6af491a339e2b4f6b76a86ad/mgm-bellagio-poker-sundays-$400-horse.pdf",
        "https://bellagio.mgmresorts.com/en/terms-and-conditions.html",
        "https://assets.contentstack.io/v3/assets/bltc6ce635bc4868eb2/blt5f25277b8918da08/mgm-grand-casino-poker-tournament_schedule.pdf",
        "https://aria.mgmresorts.com/en/casino/poker.html",
    }
    for src in SOURCES:
        if src["url"] in RECHECKED_URLS:
            src["checked"] = RECHECKED
    for e in events:
        if e["scheduleUrl"] in RECHECKED_URLS or e["sheetUrl"] in RECHECKED_URLS:
            e["lastChecked"] = RECHECKED
        for body in e["rules"].values():
            if body.get("source") in RECHECKED_URLS:
                body["retrieved"] = RECHECKED
    for h in hotels:
        if h.get("id") in ("venetian", "palazzo", "wynn", "bellagio"):
            h["lastChecked"] = RECHECKED

    recurring_events = [e for e in events if not e["date"] and e.get("weekdays")]
    plan, conflicts = build_day_plan(events, TRIP["start"], TRIP.get("playableEnd", TRIP["end"]), recurring_events)
    bankroll = sum(p["primaryBuyIn"] for p in plan if isinstance(p["primaryBuyIn"], (int, float)))
    TRIP["primaryBuyIns"] = bankroll
    TRIP["bankrollWithBuffer"] = round(bankroll * 1.25)
    n_days = len(plan)
    TRIP["bankrollNote"] = (f"The {n_days} recommended primary entries total ${bankroll:,} in buy-ins. With a 25% "
                            f"buffer for one rebuy or an add-on where a room allows it, plan on "
                            f"${round(bankroll * 1.25):,}. It is a planning number, not a forecast.")

    # The poker-suite rate holds only if a daily requirement is met. Say which nights the recommended
    # entries already satisfy, so the gap is visible rather than discovered at check-out.
    _qual, _gap = [], []
    for day in plan:
        pr = day.get("primary")
        pid = pr if isinstance(pr, str) else (pr or {}).get("id")
        e = next((x for x in events if x["id"] == pid), None)
        if not e:
            continue
        fee = e.get("buyIn")
        if isinstance(fee, (int, float)) and fee >= 300:
            _qual.append(f"{day['date']} (${fee:,})")
        else:
            _gap.append(f"{day['date']} (${fee:,})" if fee else f"{day['date']} (no fee printed)")
    TRIP["pokerRateQualification"] = (
        "The Venetian poker-suite rate is held only if, for each night stayed, the player completes six hours of "
        "active live cash play or buys in to a $300 or higher tournament, before 2 a.m. on the last night. "
        + (f"The recommended entries already meet the tournament test on {len(_qual)} of the {n_days} nights: "
           f"{', '.join(_qual)}. " if _qual else "")
        + (f"They do not meet it on {', '.join(_gap)}, where the primary event is under $300, so those nights depend "
           f"on the six-hour cash-play test or on paying the prevailing rate. " if _gap else "")
        + "For every night the requirement is missed the rate is adjusted to the prevailing rate, which the booking "
          "calendar prices at $165 to $905 across these dates.")

    structure_sheets = []
    for n in sorted(V.SHEETS):
        structure_sheets.append(dict(
            venue="venetian", series="DeepStack Extravaganza IV", sheet=n,
            url=f"{V.BASE}/dse_nov_2026-structure_{n}.pdf",
            readOn=V.RETRIEVED, read=True,
            reReadOn=REREAD_DATE if str(n) in REREAD_SHEETS else None,
            note="Read directly; excerpt recorded on the tournament row and in research/structure_notes.md."))
    for date, time, no, name, sheet_file, guarantee, category in V.NYE_ROWS:
        url = f"{V.BASE}/{sheet_file}"
        if not any(s["url"] == url for s in structure_sheets):
            structure_sheets.append(dict(
                venue="venetian", series="DeepStack Extravaganza NYE", sheet=sheet_file,
                url=url, readOn=VERIFIED_ON, read=True,
                note="Read in full on 2026-11-17; fee, chips, level length, late-registration cut-off and the entry "
                     "wording are transcribed on the row and quoted in its rule panel."))

    # The dated rate log is append-only. Every observation is kept, including
    # superseded ones, so a fee can be shown to have changed instead of being
    # silently overwritten. Duplicate observations of the same hotel and date
    # (one per component pass) are merged, never dropped.
    rate_log = sorted(H.RATE_LOG, key=lambda r: (r["observedOn"], r["hotel"]))
    for r in rate_log:
        r.setdefault("quoteType", "Observation")

    for e in events:
        if not e["date"]:
            e["status"] = "recurring"
        elif e["date"] < TODAY:
            e["status"] = "past"
        elif e["date"] == TODAY:
            e["status"] = "today"
        else:
            e["status"] = "upcoming"

    data = dict(
        asOf=TODAY,
        today=TODAY,
        bookingLinks=BOOKING_LINKS,
        scope=("Las Vegas Strip poker tournaments and Strip lodging, built only from official venue and property pages. "
               "Snapshot date 2026-11-19. The schedule pages behind the trip window were re-read that day (29 rows compared "
               "line by line, no value changed) and the Venetian, Wynn and Bellagio hotel terms pages again; every row carries "
               "the date it was last read, and a row not re-read keeps an earlier date rather than inheriting today's."),
        policy=("Every row links the official page it came from. A value that could not be confirmed from an official source is "
                "left blank and listed on the Flagged for review page. Walking minutes are Google Maps walking estimates and are "
                "labelled as such. The guaranteed-pool-to-fee ratio is descriptive only and is not a forecast."),
        sessionLengthAssumption=("No venue publishes a finish time. The schedule planner assumes a six-hour session plus a "
                                 "30-minute transfer between venues, so every conflict it reports is an estimate."),
        categories=CATEGORIES,
        venues=VENUES, events=events, hotels=hotels, rateLog=rate_log, routes=routes,
        sources=SOURCES, flags=FLAGS, questions=QUESTIONS, suggestions=SUGGESTIONS,
        trip=TRIP,
        dayPlan=plan, planConflicts=conflicts, planNotes=PLAN_NOTES,
        structureSheets=structure_sheets,
        feed=FEED_ROOMS,
        stripRooms=STRIP_ROOMS,
        verifiedOn=VERIFIED_ON,
        liveFacts=LIVE_FACTS_2026_11_17,
        # entries x buy-in + nights x (rate + resort fee) x (1 + tax), computed
        # from the seven primary entries and the seven recommended nights. The
        # tournament total is the exact sum of the chosen buy-ins (bankroll),
        # not entries x a rounded mean, so no phantom cent appears.
        tripCostModel=with_live_quote(published_model(len([p for p in plan if p.get("primary")]), _avg_primary_buyin(plan), TRIP["nights"], buy_in_exact=bankroll)),
    )
    return data


PER_NIGHT_NOTE = "Re-read live from the official Venetian booking engine on 2026-11-17 for the exact trip window (2 adults, 7 nights). The per-night true costs are derived as (rate + $55) x 1.1338 and sum to the printed total. The engine's own 'Average Rate' line prints $505.32, which equals the average of (rate + $55 resort fee), confirming that its average-rate figure includes the resort fee. Printed tax is $0.02 above 13.38% of the printed pre-tax subtotal; the page does not explain the difference and the printed figures are kept as printed (flag F65). This is a dated observation, not a booking price: the engine's rates move between reads, and the poker-suite rate page adds a play-qualification condition and the EPOKR25 code."


def with_live_quote(model):
    """Adds the dated official quote for the trip stay beside the published-floor model.

    The quote is the booking engine's checkout total for all nights, with the resort fee and tax included,
    read on 2026-11-17. The tournament total and parking are the same as in the floor model.
    """
    q = H.VENETIAN_QUOTE_TRIP
    rates = [r for _, r in q["nightly"]]
    nights = len(rates)
    model["liveQuote"] = dict(
        quoteDate=q["observedOn"], checkIn=q["checkIn"], checkOut=q["checkOut"], nights=nights,
        roomRatesTotal=round(sum(rates), 2), resortFeeTotal=round(q["resortFeePerNight"] * nights, 2),
        taxTotal=q["taxes"], checkoutTotal=q["total"],
        nightlyAllInAverage=round(q["total"] / nights, 2),
        tournamentTotal=model["tournamentTotal"], parkingTotal=model["parkingTotal"],
        tripTotal=round(model["tournamentTotal"] + q["total"] + model["parkingTotal"], 2),
        basis=("Dated official booking-engine checkout total for two adults in a Luxury King suite, read 2026-11-17 after 21:54 UTC. It is the engine's best available rate, not the phone-only poker rate (F66), and it is one read, "
               "not a guarantee."),
        sources=dict(quote=q["source"], resortFee=H.VENETIAN_RESORT_FEE, tax=H.VENETIAN_HOTEL_TERMS),
        # The per-night breakdown of the same quote. It was added to site/data.json by hand in 5a9269d, which
        # made the committed file differ from what this builder writes (see the reproducibility check).
        perNight=dict(
            property=q["property"], guests=q["guests"], offer=q["offer"],
            nightlyRates=[r for _, r in q["nightly"]], resortFeePerNight=q["resortFeePerNight"],
            nightlyTrueCostDerived=q["derivedNightly"], printedTaxes=q["taxes"], printedTotal=q["total"],
            printedAverageRate=q["averageRate"], observedOn=q["observedOn"], source=q["source"],
            note=PER_NIGHT_NOTE,
        ),
    )
    # Per-night breakdown of the same quote. Every value is read from the quote record; the per-night true
    # cost is derived as (rate + resort fee) x 1.1338 and rounded to the cent.
    model["liveQuote"]["perNight"] = dict(
        property=q["property"], guests=q["guests"], offer=q["offer"],
        nightlyRates=rates, resortFeePerNight=q["resortFeePerNight"],
        nightlyTrueCostDerived=[round((r + q["resortFeePerNight"]) * 1.1338, 2) for r in rates],
        printedTaxes=q["taxes"], printedTotal=q["total"], printedAverageRate=q["averageRate"],
        observedOn=q["observedOn"], source=q["source"],
        note=("Re-read live from the official Venetian booking engine on 2026-11-17 for the exact trip window (2 adults, "
              "7 nights). The per-night true costs are derived as (rate + $55) x 1.1338 and sum to the printed total. "
              "The engine's own 'Average Rate' line prints $505.32, which equals the average of (rate + $55 resort fee), "
              "confirming that its average-rate figure includes the resort fee. Printed tax is $0.02 above 13.38% of the "
              "printed pre-tax subtotal; the page does not explain the difference and the printed figures are kept as "
              "printed (flag F65). This is a dated observation, not a booking price: the engine's rates move between "
              "reads, and the poker-suite rate page adds a play-qualification condition and the EPOKR25 code."),
    )
    return model


def _avg_primary_buyin(plan):
    """Average buy-in of the recommended primary events.

    Every primary is a different price, so the calculator is published with the
    average of the seven chosen entries. The sum is in TRIP["primaryBuyIns"], so a
    reader can check the average against it.
    """
    buys = [p["primaryBuyIn"] for p in plan if isinstance(p.get("primaryBuyIn"), (int, float))]
    return round(sum(buys) / len(buys), 2) if buys else 0



def main():
    out = ROOT / "site" / "data.json"
    data = build()
    out.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    # The sheet-verification page links the machine-readable sheet extracts. The
    # source of truth lives at data/sheet_extracts.jsonl, outside the published
    # directory, and the Pages artifact publishes only site/. Mirror it so the
    # link resolves under the artifact publisher and under the root publisher.
    src = ROOT / "data" / "sheet_extracts.jsonl"
    if src.exists():
        dst = ROOT / "site" / "data" / "sheet_extracts.jsonl"
        dst.parent.mkdir(parents=True, exist_ok=True)
        if not dst.exists() or dst.read_bytes() != src.read_bytes():
            dst.write_bytes(src.read_bytes())
    cats = {}
    for e in data["events"]:
        cats[e["category"]] = cats.get(e["category"], 0) + 1
    print(f"wrote {out} with {len(data['events'])} events, {len(data['hotels'])} hotels, "
          f"{len(data['routes'])} routes, {len(data['sources'])} sources")
    print("categories:", cats)
    print("venues:", sorted({e["venue"] for e in data["events"]}))


if __name__ == "__main__":
    main()
