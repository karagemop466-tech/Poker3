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
RECHECK_FROM, RECHECK_TO = "2026-11-16", "2026-12-23"
DSE_NOV_URL = "https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html"
TODAY = "2026-11-17"
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
    dict(id="caesars", name="Caesars Palace", pokerRoom="Caesars Palace poker room, Appian Way",
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
         title="The WPT structure PDF's trip-window NLH sections are read; later-series sections and the $10,400 event are still unmatched",
         detail=("Read end to end on 2026-11-17 (all eight chunks). Twelve trip-window flight rows now carry verified "
                 "rules quoted from the PDF: the six $600 NLH $400K flights (Nov 27-29) and the six $800 NLH $1M "
                 "flights (Nov 30-Dec 2). Both sections print 'Unlimited re-entry for each starting flight will be "
                 "available until the start of level 9', so those events are multi-entry and stay out of the "
                 "single-entry filter; neither section prints an add-on provision. The Day 2 rows stay "
                 "'not-verified' on purpose: the schedule PDF prints them with the FOLLOWING event's buy-in columns "
                 "(Nov 30 1 p.m. 'Day 2' of the $600 event carries $800/$1M, and Dec 3 1 p.m. 'Day 2' of the $800 "
                 "event carries $1,600/$1M), so rules are not attached across conflicting evidence. The $10,400 WPT "
                 "World Championship has no section in the structures PDF. Non-NLH WPT rows outside the read "
                 "sections keep 'not-verified' status."),
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
         title="Dated checkout totals exist for near-term stays, but none for the recommended trip window",
         detail=("The Venetian booking engine has now printed three dated totals. November 17-19, 2026 with two adults: "
                 "$824.25 + $55, $164.25 + $55, $146.98 tax, $1,245.48 total on 2026-11-16, and the same stay at "
                 "$621.75 + $55, $164.25 + $55, $119.89 tax, $1,015.89 total on 2026-11-17. November 20-22, 2026: "
                 "$899.25 + $55, $1,199.25 + $55, $295.50 tax, $2,504.00 total. On 2026-11-17 four stay windows inside "
                 "the recommended trip window of November 25 to December 2, 2026 were opened and none returned a suite or "
                 "a price, so the nightly budget stays at the floor computed from the published starting rates of $119 "
                 "and $209 and is labelled a floor, not a quote."),
         source="https://www.venetianlasvegas.com/booking?adults[]=2&arrival_date=2026-11-17&children[]=0&departure_date=2026-11-19&view=calendar"),
    dict(id="F28", area="Hotels", severity="High",
         title="The Venetian booking calendar disagrees with the quote, and its cells change with the query",
         detail=("The calendar cell for November 17 read $855 in the observation recorded on 2026-11-16, while the same "
                 "page's quote for the same night printed a $824.25 room rate, and an earlier observation of the same "
                 "calendar on the same day recorded $605. The calendar states that its prices are the best available suite "
                 "and rate, include the daily resort fee and exclude taxes. Calendar cells are logged as observations and "
                 "are never used in a total. On 2026-11-17 the same booking engine, fetched live for Nov 25 to Dec 2, "
                 "showed no amount in any date cell, so the trip window is still unpriced and no cell was recorded."),
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
                 "at 10 a.m., 2 p.m., 6 p.m. and 9 p.m. ($100 buy-in, $50 add-on). On the Venetian schedule re-read on "
                 "2026-11-17 the earliest start is 9:10 AM, a $260 satellite on Dec 12. Opening Venetian events start at "
                 "10:10 AM or later; the only 10:00 AM Venetian starts are restarts (Day 2 or Day 3). The Wynn daily starts at 12:00 PM. "
                 "Most Wynn WPT rows start at 11:00 AM. Its 10:00 AM rows are the Super Gold Million flights (Dec 10 and 11), one WPT "
                 "row on Dec 12 and a satellite on Dec 18, all from the WPT PDF read on 2026-11-16. An 'all day from 8:00 AM' plan cannot be built from official sources. The day plan starts at "
                 "the earliest verified start for each venue."),
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
         title="Discounted-entry footnote markers do not resolve cleanly against the footnote list",
         detail=("The schedule prints '*', '**', '***', '****' and '*****' markers. Several rows, including the $10,500 "
                 "PLO 6-Max and the $25,800 NLH High Roller, carry a four-marker footnote, while the footnote list "
                 "describes the Ladies Championship entry under four markers and the general discounted entry under "
                 "five. The marker is reproduced with its row and the footnote text is quoted, but the published entry "
                 "is not adjusted."),
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
         detail=("The 52 Venetian rows classified as 'single entry on the sheet' have one printed buy-in and no re-entry, rebuy, add-on or second-flight provision in the reviewed sheet. However, the sheets do not state a maximum number of entries per player and do not explicitly call the event a freezeout. This is only a document-level screen, not written confirmation of the room's one-entry policy. Do not treat these candidates as strictly eligible or book around them until the venue confirms the maximum-entry, no-rebuy and no-add-on rules in writing. The source excerpt and date are attached to each row."),
         source="https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html"),
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
                 "2026-12-02) returns $XXX in every cell, so no checkout total exists for those nights. Asking the same "
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
         detail=("Dated official booking-engine read on 2026-11-17 at 21:54 UTC (2 adults, 23-30 Nov 2026, 7 nights): the printed "
                 "nightly rates total $3,152.25, the printed resort fees total $385.00, the pre-tax subtotal is $3,537.25, "
                 "and the printed tax is $473.30. 13.38% of $3,537.25 is $473.28. The page does not explain the $0.02 "
                 "difference. The record keeps the printed $473.30 and the printed $4,010.55 total, and does not adjust "
                 "either figure. Per-night true costs are derived as (rate + $55) x 1.1338 and sum to the printed total. "
                 "The later same-day reading of the identical query did not reproduce the difference: its printed tax of "
                 "$451.21 equals the sum of the per-night rounded taxes exactly (see F78)."),
         source="https://www.venetianlasvegas.com/booking?adults[]=2&arrival_date=2026-11-23&children[]=0&departure_date=2026-11-30&view=calendar"),
    dict(id="F32", area="Walking routes", severity="Medium",
         title="The 30-minute walking check does not cover every hotel–venue pair",
         detail=("The current 14 route rows cover routes from the recommended Venetian resort hotel to the listed poker rooms, plus selected on-site pairs. The requested full hotel-by-venue matrix would contain 56 pairs (8 hotel records × 7 venue records); the remaining pairs have no checked walking time here and are not assumed to meet the 30-minute limit. The existing schedule filter applies only to the recommended Venetian resort route estimates. Check the official property addresses and each Google/Apple walking route before comparing other hotel choices."),
         source="https://www.google.com/maps/dir/?api=1&travelmode=walking"),
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
         title="The Wynn terms page used as the fee source is an expired 2025 offer",
         detail=("The earlier build cited https://www.wynnlasvegas.com/terms-and-conditions/850070 for Wynn's $55 resort "
                 "fee, parking and 48-hour cancellation. That page is a DINING CREDIT offer whose own text says a stay "
                 "booked under it 'must be completed on or before September 30, 2025', so it cannot substantiate a "
                 "November 2026 trip. The fee was re-verified on 2026-11-17 from the live Resort Policies page, which "
                 "still prints $55 plus tax, check-in 3 p.m. and check-out 12 p.m. The 48-hour cancellation window appears "
                 "only in offer terms, so Wynn has no verified flexible-booking cancellation deadline and is shown blank."),
         source="https://www.wynnlasvegas.com/about-us/resort-information"),
    dict(id="F36", area="Hotel cost", severity="Medium",
         title="The booking engine prints $XXX for the recommended trip dates, so no checkout total exists for them",
         detail=("The Venetian booking engine was opened for 2026-11-25 to 2026-12-02 with two adults. It returned the "
                 "date picker with every cell reading $XXX, because prices are loaded by script after the page renders. "
                 "No dated checkout total can therefore be read for the trip window without a browser session. The site "
                 "keeps the published starting-rate floor ($197.28) and labels it a floor, never a quote."),
         source="https://www.venetianlasvegas.com/booking?adults[]=2&arrival_date=2026-11-25&children[]=0&departure_date=2026-12-02&view=calendar"),
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
         title="Wynn, Caesars Palace and Horseshoe print no room-tax percentage, so their true nightly cost stays open",
         detail=("Wynn publishes 'plus tax' on the resort fee and on the room rate but no percentage (page re-read "
                 "2026-11-17: 'Reservations will be charged a daily resort fee of $55 plus tax'). Caesars Palace and "
                 "Horseshoe print only the tax amount charged on their fee. The Clark County Department of Business "
                 "License Combined Transient Lodging Tax schedule (Appendix III of the General Information Guide for "
                 "Transient Lodging Establishments) lists every resort hotel in the Primary Gaming Corridor at 13.38% "
                 "- MGM Grand, Luxor, Paris, New York-New York, Sahara and Rio were read line by line on 2026-11-17 "
                 "(session 688eb797) - and the City of Las Vegas room-tax packet prints the same 13.38%/13.00% split "
                 "(https://files.lasvegasnevada.gov/business-licensing/RoomTaxPacket.pdf); 13.38% is also the figure "
                 "the Venetian prints in its own hotel terms. This site does not substitute a government schedule into "
                 "a property-published column: the row shows the reference beside a blank property figure. Closing it "
                 "needs a dated checkout total from each property."),
         source="https://www.wynnlasvegas.com/about-us/resort-information"),
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
         title="The official Wynn Signature Series structures file is a 'coming soon' placeholder, so 38 rows cannot be confirmed",
         detail=("Read on 2026-11-17. The URL the site cites for Wynn Signature Series structures "
                 "(Wynn_Signature_Series_Structures.pdf) now returns only 'LAS VEGAS POKER / COMING SOON'. The series "
                 "schedule PDF, read at the same time, prints the dates January 11-24, 2027 and tells guests to 'Scan the "
                 "QR code for event structures'. There is therefore no readable official structure sheet for these 38 "
                 "rows today, and their single-entry, re-entry and add-on status correctly stays 'not verified' rather "
                 "than being inferred from the schedule. The schedule does print buy-in, guarantee, chips and level "
                 "length for most rows, and those columns are shown."),
         source="https://cdn.wynnresorts.com/image/upload/v1762299460/visitwynn_pdfs_files/Poker/Wynn%20Signature%20Series/Wynn_Signature_Series_Structures.pdf"),

    dict(id="F54", area="Trip plan", severity="High",
         title="Two of the seven planned nights do not satisfy the published condition for the $119 poker-suite rate",
         detail=("Derived on 2026-11-17 from two published documents, not inferred. The Venetian poker-suite rate page "
                 "requires 'six hours of active live cash gameplay or buy in to a $300 or higher tournament for each "
                 "night stayed', and failure to qualify means the prevailing rate is charged. The recommended plan "
                 "places a $400, $300, $600, $600 and $300 primary on Nov 25, 26, 27, 28 and 29, which satisfy it, and a "
                 "$200 primary on Nov 30 and Dec 1, which do not; the nights of those two days are therefore not covered "
                 "by the published condition. The Dec 2 $200 entry falls on the departure day, so it is not a night that "
                 "needs qualifying. The page does not say whether an entry counts on the day it is paid or on every night "
                 "of a multi-day event, so no re-pricing amount is claimed - the room must be asked. Two $300+ "
                 "alternatives are published on those dates (the $400 No Limit Hold'em 1B at 11:10 AM on Nov 30 and 1C at "
                 "11:10 AM on Dec 1, both multi-flight, so they sit outside the single-entry screen; on Dec 2 the only "
                 "$300+ single-day event is the $600 Seniors, which is age-restricted to 50+). Choosing between a $200 "
                 "buy-in and a possibly repriced room is a decision this site shows but does not make."),
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
         title="The Caesars Palace and Horseshoe daily schedules are published only inside a dated marketing article",
         detail=("Re-read on 2026-11-17. The page that publishes every Caesars Palace and Horseshoe start time is an "
                 "editorial page, bylined 'James Billington' and dated July 17, 2026, not a tournament page, and it "
                 "carries no structure-sheet link. The four Caesars Palace values it prints ($100 buy-in, 20,000 "
                 "chips, $1,000 guarantee, 20-minute levels, plus a $50 add-on at the first break for 15,000 extra "
                 "chips) are recorded on the four rows with that article as their source. The Horseshoe rows stay blank "
                 "because the article publishes only 'a mixture of buy-ins, levels and guarantees' (F20). A schedule "
                 "that exists in a four-month-old article is not something to rely on before a nonrefundable booking."),
         source="https://www.caesars.com/las-vegas/explore/casino/poker-tournaments-las-vegas-strip"),
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
    dict(id="F60", area="Wynn WPT", severity="Medium",
         title="The $1,100 PLO structure sheet's printed buy-in components total $1,105, not $1,100",
         detail=("The WPT World Championship structure sheet for the $1,100 PLO (Tuesday Dec 1, 1 p.m.) prints the buy-in "
                 "split as a $975 prize pool with fees of $85 and $45. The printed components sum to $1,105, five dollars "
                 "more than the printed $1,100 buy-in on the schedule. The row reproduces the schedule buy-in and the rule "
                 "panel reproduces the split as printed; nothing is adjusted. Confirm the amounts with the poker room."),
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
                 "that fails is re-priced at the prevailing rate. Neither 23-30 November engine quote ($4,010.55 at 21:54 UTC or "
                 "$3,823.46 at about 22:07 UTC, both 'Book Direct: Up to 25% Off') shows the code. The $197.28 a night floor in the trip profile is computed from published "
                 "components and is not a quote. Ask the poker room whether EPOKR25 applies to these dates and what the all-in "
                 "total would be, then record the answer as a dated rate-log entry."),
         source="https://www.venetianlasvegas.com/resort/casino/poker/suite-rates.html"),
    dict(id="F67", area="Walking routes", severity="Medium",
         title="Venetian to Bellagio Poker Room walks 27 minutes; the planner's Bellagio-to-Venetian figure is 21 minutes",
         detail=("On 2026-11-17 the Google Maps walking card from 3355 S Las Vegas Blvd (The Venetian) to the Bellagio Poker Room, "
                 "3600 S Las Vegas Blvd, read 27 minutes for 1.1 miles via Las Vegas Blvd S. The driving card for the same pair read "
                 "8 minutes. The walking card does not print its mode label; the link requested travelmode=walking. The reverse pair, "
                 "Bellagio Hotel & Casino to The Venetian, read 21 minutes (0.9 mile) the same day, which matches the stored route. "
                 "The day plan uses only the venue-to-Venetian direction, so a Venetian-to-Bellagio transfer is understated by six "
                 "minutes. The 30-minute limit is still met (27 minutes). Re-read the pair on a second day before relying on either figure."),
         source="https://www.google.com/maps/dir/?api=1&origin=3355+S+Las+Vegas+Blvd,+Las+Vegas,+NV+89109&destination=Bellagio+Poker+Room,+3600+S+Las+Vegas+Blvd,+Las+Vegas,+NV+89109&travelmode=walking"),
    dict(id="F68", area="Publishing", severity="Low",
         title="Legacy hotel, rate and route files in site/data/ are stale and are written by no script",
         detail=("site/data/hotels.json, site/data/rates.json and site/data/routes.json are dated 2026-11-16, are written by no script "
                 "in scripts/, and are not linked or read by any dashboard page. They still show the 25 November - 2 December window, "
                 "the calendar-based $2,140 figure and blank walking minutes. They are left in place so nothing else breaks; they "
                 "should be removed or regenerated in a separate change. site/data.json is the only current source."),
         source="https://github.com/karagemop466-tech/Poker3/tree/main/site/data"),
    dict(id="F77", area="Change monitoring", severity="High",
         title="The automated re-check cannot see a price change on the booking pages, because it never fetches the price",
         detail=("Found on 2026-11-17. The scheduled recorder fetches each official URL and compares the visible text of the "
                 "response with the stored text hash. The five Venetian booking-engine URLs (17-19 Nov, 20-22 Nov, 23-30 Nov, "
                 "25 Nov-2 Dec and 27-28 Nov) all return a byte-identical response of 142,771 bytes whose visible text is 1,779 "
                 "characters, and all five carry the same text hash. The page renders its prices client-side, so the response body "
                 "does not depend on the dates in the query at all. The recorder therefore reports 'changed: false' for these URLs "
                 "forever, whether the price moved or not, and it also recorded one of them as a first-time baseline rather than a "
                 "comparison. A price change on the page that carries the hotel budget is therefore invisible to the monitor. "
                 "The fix is to compare a rendered read of each booking URL against a stored rendered read, not a raw fetch. Until "
                 "that is built, the dated rate log is the only record of what the engine actually printed, and every price on this "
                 "site must be read by hand and logged with its timestamp."),
         source="https://www.venetianlasvegas.com/booking?adults[]=2&arrival_date=2026-11-23&children[]=0&departure_date=2026-11-30&view=calendar"),
    dict(id="F78", area="Hotels", severity="Medium",
         title="The same official booking query returned two different prices thirteen minutes apart",
         detail=("On 2026-11-17 the identical booking-engine URL for 23-30 November 2026 (two adults, seven nights) was read twice "
                 "in different sandboxes. The 21:54 UTC read printed an 'Estimated cost of stay' of $4,010.55 for the venetian "
                 "Newly Remodeled Luxury King, with nightly rates 164.25 / 164.25 / 201.75 / 231.75 / 1,649.25 / 554.25 / 186.75, "
                 "a $55.00 resort fee each night and taxes of $473.30. The read at about 22:07 UTC printed $3,823.46 for the palazzo "
                 "Luxury King, with nightly rates 204.25 / 204.25 / 286.75 / 406.75 / 1,119.25 / 561.75 / 204.25, the same $55.00 "
                 "resort fee each night and taxes of $451.21. Two reads minutes apart in one session agreed on the second figure. "
                 "Both totals reconcile exactly against (rate + $55) x 1.1338, so neither is an arithmetic error; the engine's "
                 "best-available rate and the tower it offers both moved. The later reading is published as the current figure and "
                 "the earlier one is kept in the dated rate log, because the site's policy is a dated log rather than one number. "
                 "A reader must treat the engine's price as a reading, not as a fixed rate, and confirm it on the booking screen "
                 "before paying."),
         source="https://www.venetianlasvegas.com/booking?adults[]=2&arrival_date=2026-11-23&children[]=0&departure_date=2026-11-30&view=calendar"),

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
                 "same stay the day before, plus $2,504.00 for November 20-22. For the trip window itself the engine "
                 "printed a full itemised total twice on 2026-11-17: $4,010.55 at 21:54 UTC and $3,823.46 at about "
                 "22:07 UTC, both for seven nights, two adults, a $55 resort fee each night and tax (F78). The "
                 "engine's calendar cells are not prices: read twice on the same day, "
                 "November 16 printed $555 with one stay window open and $854 with another, and November 27 printed "
                 "$905 against $1,814 (F47). The rate page publishes only starting rates of $119 and $209, which are "
                 "explicitly not date-specific, and states that rates are provided up to 150 days out."),
         why="Needed", blocking="Yes for a confirmed total",
         how="Open the booking link with the exact dates, then log the printed total in the rate log with its timestamp.",
         source="https://www.venetianlasvegas.com/booking?adults[]=2&arrival_date=2026-11-23&children[]=0&departure_date=2026-11-30&view=calendar"),
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
         answer="The venues publish no walking times. Google Maps estimates captured on 2026-11-16 cover the recommended Venetian resort hotel to the listed rooms and selected on-site pairs only; the full 8-hotel × 7-venue matrix is incomplete (F32). The recommended-hotel estimates are: Caesars Palace 12 minutes, Wynn 13, Horseshoe 16, Bellagio 21, ARIA 31 and MGM Grand 35. The Wynn poker room is in Encore, a 10-minute estimate from the Wynn hotel. These are estimates, not verified venue times.",
         why="Needed", blocking="Yes - only the recommended hotel's route set is checked",
         how="Use official property addresses to verify each hotel-to-room Google or Apple walking route; do not assume missing pairs are under 30 minutes.",
         source="https://www.google.com/maps/dir/?api=1&travelmode=walking"),
    dict(id="Q09", question="Which other Strip rooms should be added to the plan?",
         answer="Not covered. This pass verified The Venetian, Wynn, Bellagio, MGM Grand, Caesars Palace, Horseshoe and ARIA. South Point, Golden Nugget, Resorts World, Circa, Excalibur, Luxor, Orleans, Red Rock, Palms, Westgate, Tropicana, Bally's, Flamingo, LINQ, Planet Hollywood, Rio and M Resort were not checked.",
         why="Useful", blocking="No",
         how="Say which properties to add; each needs its own official page and structure sheets.",
         source="https://www.venetianlasvegas.com/resort/casino/poker.html"),
    dict(id="Q10", question="Do the December 17-23 and holiday-week events still run as published?",
         answer=("Re-read on 2026-11-17. Venetian DeepStack Extravaganza IV (the page covers Nov 16 to Dec 23, 2026): the 21 rows dated Nov 16 to Nov 27 match the page on date, start time, event name, buy-in, guarantee and structure-sheet link. The 73 rows dated Nov 28 to Dec 23 match on date, start time, event name, buy-in and guarantee; their structure links were not compared. Caesars Palace (four daily starts at 10 AM, 2 PM, 6 PM and 9 PM, $100 buy-in, $1,000 guarantee) and Horseshoe (six daily starts from 9 AM to 11 PM) match the page text. The page gives no Horseshoe buy-in or guarantee, so those cells stay blank. The Venetian resort fee is still $55 plus tax. The Wynn landing page confirms the WPT window and the Super Gold Million terms. The Bellagio landing page still carries a stale notice (flag F03). Not re-read by the 2026-11-17 pass that produced this answer: the Bellagio weekly PDFs, the Wynn daily and WPT PDFs and the DeepStack NYE schedule. They were read by the sessions recorded on the sources page, and each row shows its own read and verified dates."),
         why="Useful", blocking="No",
         how="Re-check the Flagged for review page and the change log before booking and again 48 hours before you travel.",
         source="https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html"),
    dict(id="Q11", question="What is the cancellation deadline at each property?",
         answer="Published and different: Wynn requires 48 hours before arrival, Bellagio 72 hours before arrival, and the Venetian bills a deposit on confirmation with blackout dates and non-refundable prepaid offers; an early checkout costs $100 plus tax.",
         why="Needed", blocking="No",
         how="Use the cancellation column in the hotel table when choosing where to hold the booking.",
         source="https://www.wynnlasvegas.com/terms-and-conditions/850070"),
    dict(id="Q12", question="What does parking cost, and does it change the true cost per night?",
         answer="Venetian: $20 per day for registered hotel guests, $20 Monday-Thursday and $25 Friday-Sunday for non-hotel guests, valet $40. Wynn: self-parking is free for registered guests and $25 per day for others, valet $40, and complimentary self-parking extends to Wynn poker-room guests. Bellagio parking was not captured in this pass.",
         why="Needed", blocking="No",
         how="Include parking in the trip total if you will not stay on property every night.",
         source="https://www.venetianlasvegas.com/legal/hotel-terms-and-conditions.html"),
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
                 "verified open event for each venue."),
         why="Needed", blocking="Yes - the all-day schedule in the brief cannot be produced without it",
         how="Ask Horseshoe for the buy-in, structure and single-entry rule of its 9:00 AM game; ask each room for its earliest daily start.",
         source="https://www.caesars.com/las-vegas/explore/casino/poker-tournaments-las-vegas-strip"),
    dict(id="Q15", question="What is the real checkout total for the trip dates?",
         answer=("Answered for The Venetian on 2026-11-17. The official booking engine printed an itemised checkout total for "
                 "2026-11-23 to 2026-11-30 twice on that day: $4,010.55 at 21:54 UTC (venetian Newly Remodeled Luxury King, "
                 "$55 resort fee each night, $473.30 tax) and $3,823.46 at about 22:07 UTC (palazzo Luxury King, $55 resort fee "
                 "each night, $451.21 tax). The later reading is the published figure and the earlier one is kept beside it in the "
                 "dated rate log; the engine's best-available price for the same stay moved $187.09 in about thirteen minutes "
                 "(F78). Earlier readings for the superseded 2026-11-25 to 2026-12-02 window printed $XXX. No other property "
                 "publishes a date-specific total in the data. The phone-only poker rate is not in the quote (F66)."),
         why="Needed", blocking="Yes - the budget is a floor until a quote is read, and the quote itself moves between reads",
         how="Open the booking engine in a browser, select the dates and two adults, and read the checkout total; or call the "
             "poker rate line on 866.255.8936 and ask for code EPOKR25 priced for those dates.",
         source="https://www.venetianlasvegas.com/booking?adults[]=2&arrival_date=2026-11-23&children[]=0&departure_date=2026-11-30&view=calendar"),
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
         answer=("Caesars Palace and Horseshoe publish no resort fee on their official pages, and Wynn prints 'plus tax' "
                 "without a percentage. MGM Grand ($50), Bellagio ($55), ARIA ($55) and the Venetian ($55) are verified. "
                 "Any hotel comparison that includes the unverified properties is therefore incomplete, not wrong; the "
                 "site leaves those cells blank and flags them."),
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
    dict(id="S03", title="Read the remaining DeepStack NYE and WPT structure sheets",
         detail=("Fifteen NYE sheets and the eight-chunk WPT structure PDF are still unread. Reading them would move the holiday "
                 "window and the WPT week from 'schedule confirmed, rules unverified' to fully verified and would let those events "
                 "into the single-entry filter."),
         impact="High", effort="Medium", decision="Straightforward research, no new source needed"),
    dict(id="S04", title="Add the missing Strip poker rooms",
         detail=("South Point, Golden Nugget, Resorts World, Circa, Excalibur, Luxor, Orleans, Red Rock, Palms, Westgate, Tropicana, "
                 "Bally's, Flamingo, LINQ, Planet Hollywood, Rio and M Resort are all unverified. For a trip that aims to enter as many "
                 "tournaments as possible, the daily rooms in walking range are worth more than another marquee series."),
         impact="Medium", effort="Medium", decision="Which properties to prioritise"),
    dict(id="S05", title="Replace the estimated walking times with a venue-published figure",
         detail=("No venue publishes a walking time. Asking each property for the official route and time to its own poker room "
                 "would replace Google Maps estimates, which are model outputs that ignore indoor walkways and Strip traffic."),
         impact="Medium", effort="Low", decision="Worth doing for the final shortlist"),
    dict(id="S06", title="Capture the hotel cost components for the remaining properties",
         detail=("MGM Grand, Caesars Palace, Horseshoe and ARIA have no verified resort fee, tax or parking in the current data, so "
                 "they cannot be compared like for like. One pass over each property's terms page closes that gap."),
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
    dict(id="S17", title="Confirm the WPT event-level re-entry rule for the three events inside the trip window",
         detail=("The WPT structures PDF opens with general terms and then publishes a sheet per event. Only the general "
                 "terms have been read, and they publish no re-entry clause, so each WPT row says 'not verified' rather "
                 "than being dropped or promoted. Reading the three event sheets that fall between 2026-11-25 and "
                 "2026-12-02 would settle it."),
         impact="High", effort="Low",
         decision="Read three PDFs; no new source needed"),
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
         impact="Medium", effort="Done", decision="Keep the comparison published"),
    dict(id="S20", title="Ask the Venetian two questions in one call, then fix the rate basis once",
         detail=("Two open questions are answered by the same phone call to 866.255.8936 (code EPOKR25). (1) Is the "
                 "$119 / $209 poker rate quoted before or after the $55 resort fee? The Resort Fee page says the fee is "
                 "chargeable on top of the rate and the booking calendar says its prices include the fee, so the poker "
                 "rate itself decides whether the $197.28 floor overstates the nightly cost by about $43 (F51). (2) Does one $300 or higher entry cover every night of a "
                 "multi-day event, or only the night it is paid? The answer decides whether the Nov 30 and Dec 1 nights "
                 "are repriced (F54). Ask both while a dated checkout total for 2026-11-25 to 2026-12-02 is also "
                 "requested (F15, F36), which is the only figure that replaces the floor with a real number."),
         impact="High", effort="Low",
         decision="One call settles the nightly budget basis, the qualification risk and the missing total"),
    dict(id="S21", title="Score each day on rate qualification as well as on guarantee",
         detail=("The day plan now prints, per day, whether the planned primary satisfies the published $300 condition "
                 "for the poker-suite rate. Two ways to act on it: (a) leave Nov 30 and Dec 1 as $200 primaries and "
                 "budget those two nights at the prevailing rate, or (b) swap them for the published $400 multi-flight "
                 "(11:10 AM on each day), which qualifies but moves both days out of the single-entry screen, because a "
                 "flight shares a Day 2 with other flights. This site shows the trade-off and does not choose it, "
                 "because it depends on whether the traveller values the verified rate or the single-entry format."),
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
    "*": ("Prize footnote on the schedule: \"Winners will receive two (2) prizes valued at $1,100 each. Prizes may be "
          "used separately or combined for a tournament entry.\""),
    "**": ("Prize footnote on the schedule: \"Winners will receive direct entry to the corresponding event(s) for which "
           "it was held.\" These are seat prizes, not cash."),
    "***": ("The schedule prints \"$1,000,000 Added\" with the footnote \"$1,000,000 will be added in cash prizes by "
            "ClubWPT Gold. ClubWPT Gold is not available in Nevada.\""),
    "****": ("The schedule prints a discounted-entry marker on this row: \"The Tournament Entry for the Ladies "
             "Championship is $11,100. Ladies will receive a discounted entry.\" and \"Players registered prior to the "
             "start of the event will receive a discounted entry.\" The marker on this row does not resolve cleanly "
             "against the footnote list, so the printed entry is shown and nothing is adjusted."),
    "*****": ("The schedule prints a discounted-entry marker on this row: \"Players registered prior to the start of "
              "the event will receive a discounted entry.\""),
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
        "meets the daily play requirement (F66). The dated figure is $546.21 a night all-in: the official Venetian booking "
        "engine's checkout total of $3,823.46 for 23-30 November 2026 (2 adults, palazzo Luxury King, read 2026-11-17 at about 22:07 UTC), divided by seven nights. That total already includes the $55 resort fee and the 13.38% tax. The identical query read thirteen minutes earlier printed $4,010.55, so both readings are kept in the dated rate log (F78)."),
    "nightlyBudgetCeiling": 299.32,
    "nightlyObservedAverage": 546.21,
    "lodgingTotalBeforeTax": 3372.25,
    "lodgingTotalAllIn": 3823.46,
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
        "The night of Friday 27 November 2026, the night after Thanksgiving, is quoted at $1,119.25 room rate + $55 resort "
        "fee + tax = $1,331.36 all-in, against $293.94 all-in on 23, 24 and 29 November. It is 35% of the whole $3,823.46 stay on "
        "its own. A player who can move the trip, or who is willing to change property for that one night, removes $1,037.42 "
        "of all-in cost compared with a $293.94 night. The phone-only poker rate ($119-$209 + $55) is the other lever, if the "
        "daily play requirement is met and the code applies to these dates (F66). The earlier same-day reading of this same "
        "stay quoted that night at $1,932.28 against a $248.59 night, so the risk figure itself moves (F78)."),
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
        "the seven-night window the engine prices on every night. Two reads of that window on 2026-11-17 priced it in "
        "full: $4,010.55 at 21:54 UTC and $3,823.46 at about 22:07 UTC, each with the nightly rate, the $55 resort fee and "
        "13.38% tax itemised for each night. The later reading is the current figure and the earlier one is kept beside it "
        "in the dated rate log, because the engine's price for a stay moves between reads (F78). The earlier $2,140 and "
        "$346.62 figures were the sum and average of calendar cells for the superseded window; the engine's own footnote says the "
        "cells are not the price, so they are withdrawn from the trip budget (F69). The engine quotes near-term stays too, and it "
        "priced the same 17-19 November stay twice on consecutive days ($1,245.48 on 2026-11-16 and $1,015.89 on 2026-11-17), so "
        "every figure here is dated and can move."),
}

PLAN_NOTES = {
    "primaryRule": ("Provisional primary candidate = the sheet-screened event on that date with the largest published guarantee, "
                    "among venues within a 30-minute walk of the recommended hotel, excluding age-restricted, female-only "
                    "and team formats. This is not confirmation of a one-entry-per-player cap; written venue rules are required."),
    "fallbackRule": ("Fallback = the next sheet-screened candidate that starts after the primary's estimated finish plus a "
                     "30-minute transfer. The fallback is conditional on written confirmation of entry rules and fit."),
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
        fallback_reason = ""
        if primary:
            rest = [e for e in eligible[1:]]
            if rest:
                fallback = rest[0]
                fallback_reason = _fallback_reason(primary, fallback)
            else:
                others = [e for e in by_date[date]
                          if e["id"] != primary["id"] and not e["isContinuation"]
                          and e["entryType"] == "none" and not e["eligibility"]]
                if others:
                    others.sort(key=lambda x: (not isinstance(x["guarantee"], (int, float)), x["time"]))
                    fallback = others[0]
                    fallback_reason = _fallback_reason(primary, fallback)
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
    priceInStaticPage=("Yes. On 2026-11-17 the engine printed an itemised checkout total for this stay twice: $4,010.55 at "
                       "21:54 UTC (nightly rates of $164.25 to $1,649.25 before a $55 resort fee per night, plus $473.30 tax) "
                       "and $3,823.46 at about 22:07 UTC (nightly rates of $204.25 to $1,119.25 before a $55 resort fee per "
                       "night, plus $451.21 tax). Both are kept in the dated rate log (F78). "
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
                          f"the sheet.")
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
    # The two multi-flight NLH events whose flights fall inside the trip window were matched to
    # their own sections of the official structures PDF on 2026-11-17 (session 688eb797, chunks 1
    # and 3). Both sections print the same registration clause, so their flight rows and Day 2 rows
    # carry verified rules instead of the generic "not read" text. Everything else stays not-verified.
    WPT_NLH_SECTIONS = {
        # $600 NLH $400,000 GTD, November 27-30, 2026 (1A-1F on Nov 27-29; Day 2 Mon Nov 30 1 p.m.)
        "600": dict(
            fee_excerpt=("Entry Fee: $600 Buy-in = $510 (Tournament Prize Pool) + $65 (Tournament Fee) "
                         "+ $25 (Poker Staff Service Charge)"),
            re_excerpt=("Registration: Unlimited re-entry for each starting flight will be available until the "
                        "start of level 9. A player who advances to Day 2 is prohibited from entering a subsequent "
                        "starting flight."),
            flight=lambda date, name: ("2026-11-27" <= date <= "2026-11-29"
                                       and name.startswith("No Limit Hold'em Day 1")),
            day2=None,
        ),
        # $800 NLH $1,000,000 GTD, November 30 - December 4, 2026 (1A-1F on Nov 30 - Dec 2; Day 2 Thu Dec 3 1 p.m.)
        "800": dict(
            fee_excerpt=("Entry Fee: $800 Buy-in = $695 (Tournament Prize Pool) + $72 (Tournament Fee) "
                         "+ $33 (Poker Staff Service Charge)"),
            re_excerpt=("Registration: Unlimited re-entry for each starting flight will be available until the "
                        "start of level 9. A player who advances to Day 2 is prohibited from entering a subsequent "
                        "starting flight."),
            flight=lambda date, name: ("2026-11-30" <= date <= "2026-12-02"
                                       and name.startswith("No Limit Hold'em Day 1")),
            day2=None,
        ),
    }

    def _wpt_section_for(date, name, buy):
        for key, sec in WPT_NLH_SECTIONS.items():
            if sec["flight"](date, name):
                return sec
        return None

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
        sec = _wpt_section_for(date, name, buy)
        if sec:
            re_note = ("Structure section for this event read in the official structures PDF on 2026-11-17 "
                       "(session 688eb797); the registration clause above is quoted from it.")
            rules = {
                "singleEntry": dict(status="multiple-entries", excerpt=sec["re_excerpt"],
                                    source=N.WYNN_WPT_STRUCT, retrieved=RECHECKED),
                "reEntry": dict(status="confirmed", excerpt=sec["re_excerpt"],
                                source=N.WYNN_WPT_STRUCT, retrieved=RECHECKED),
                "addOn": dict(status="none-printed",
                              excerpt="No add-on provision appears in this event's structure section.",
                              source=N.WYNN_WPT_STRUCT, retrieved=RECHECKED),
                "fee": dict(status="confirmed", excerpt=sec["fee_excerpt"],
                            source=N.WYNN_WPT_STRUCT, retrieved=RECHECKED),
            }
        else:
            re_note = ""
            rules = {
                "singleEntry": dict(status="not-verified",
                                    excerpt="This event's structure section has not been matched, so no entry rule is confirmed for this event.",
                                    source=N.WYNN_WPT_STRUCT, retrieved=ASOF),
                "reEntry": dict(status="not-verified", excerpt="This event's structure section has not been matched.",
                                source=N.WYNN_WPT_STRUCT, retrieved=ASOF),
                "addOn": dict(status="not-verified", excerpt="This event's structure section has not been matched.",
                              source=N.WYNN_WPT_STRUCT, retrieved=ASOF),
                "fee": dict(status="confirmed", excerpt=f"Buy-in ${buy_in} and guarantee ${guarantee} are printed on the official schedule PDF.",
                            source=N.WYNN_WPT_SCHED, retrieved=ASOF),
            }
        events.append(_event(
            f"wynn-wpt-{date}-{idx:03d}-{time.replace(':', '').replace(' ', '').lower()}",
            "wynn", date, time, name, buy, gua, rules, cat, "wpt",
            N.WYNN_WPT_SCHED, N.WYNN_WPT_SCHED, N.WYNN_WPT_STRUCT,
            note=" ".join(x for x in [
                ("Multiple start flights are published for this event, so more than one entry is possible." if flight else
                 ("Schedule row from the official WPT World Championship schedule PDF; entry rules not yet read." if not sec
                  else "Schedule row from the official WPT World Championship schedule PDF.")),
                re_note, WPT_MARK_NOTES.get(marks, "")] if x).strip(),
            chips=int(chips) if chips not in ("-", "") else "", entry_type=("multi-flight" if flight else "not-verified"),
            continuation=is_continuation(name),
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
            rules = {k: dict(v, source=v.get("source", d["source"]), retrieved=ASOF) for k, v in d["rules"].items()}
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
    add_group(N.CAESARS_EVENTS, "caesars", "caes", last_checked=CHECKED_TODAY)
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
        row["lastChecked"] = (CHECKED_TODAY if h["id"] in ("venetian", "palazzo", "caesars", "horseshoe") else ASOF)
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
        # Walking times were measured on the base pass and were not re-measured today.
        row["lastChecked"] = r.get("lastReadOn", ASOF)
        row["walkSourceType"] = "Google Maps walking estimate"
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

    # Wynn WPT: the trip-window rows whose section the structure PDF prints (2026-11-17 read).
    for ev in events:
        rec = WPT_ROWS.get(ev["id"])
        if not rec:
            continue
        src = WPT_REREAD["sheetUrl"]
        ev["rules"]["reEntry"] = dict(status="re-entry-printed", excerpt=rec["excerpt"], source=src,
                                      retrieved=WPT_REREAD["retrievedOn"])
        ev["rules"]["singleEntry"] = dict(status="multiple-entries", excerpt=rec["excerpt"], source=src,
                                          retrieved=WPT_REREAD["retrievedOn"])
        ev["lastChecked"] = WPT_REREAD["retrievedOn"]
        # The note said "entry rules not yet read" while the rules above now quote the sheet's
        # own registration clause. Leaving both produced a row that contradicted itself, so the
        # stale clause is replaced by the read date rather than stacked underneath it (defect
        # fixed 2026-11-17; see COORDINATION.md).
        ev["note"] = (ev.get("note", "")
                      .replace("entry rules not yet read.", "entry rules read from the official structure sheet.")
                      + f" Official structure sheet ({rec['section']}): {rec['excerpt']}").strip()

# Fee splits and registration clauses for the WPT rows the structure PDF names
    # explicitly (PDF read 2026-11-17). The six split rows are the ones the PDF
    # matches to a printed start time, so the split certainly belongs to that row.
    WPT_FEE_SPLITS = {
        "wynn-wpt-2026-11-27-001-1200pm": ("$525 of every $600 buy-in is the prize pool and $75 is withheld in fees."),
        "wynn-wpt-2026-11-27-002-100pm": ("$350 of every $400 buy-in is the prize pool and $50 is withheld in fees."),
        "wynn-wpt-2026-11-28-005-1200pm": ("$525 of every $600 buy-in is the prize pool and $75 is withheld in fees."),
        "wynn-wpt-2026-11-30-010-1200pm": ("$525 of every $600 buy-in is the prize pool and $75 is withheld in fees."),
        "wynn-wpt-2026-12-01-014-1200pm": ("$525 of every $600 buy-in is the prize pool and $75 is withheld in fees."),
        "wynn-wpt-2026-12-01-015-100pm": (
            "The sheet prints the $1,100 buy-in split as a $975 prize pool with fees of $85 and $45; the printed "
            "components total $1,105, which does not equal the printed $1,100 buy-in. Flagged F60; the split is "
            "reproduced as printed and nothing is adjusted."),
    }
    for ev in events:
        excerpt = WPT_FEE_SPLITS.get(ev["id"])
        if excerpt:
            ev["rules"]["fee"] = dict(status="fee-split-printed", excerpt=excerpt,
                                      source=WPT_REREAD["sheetUrl"], retrieved=WPT_REREAD["retrievedOn"])
        if (ev.get("venue") == "wynn" and ev.get("name", "").startswith("WPT Prime Championship")
                and "Day 1" in ev.get("name", "")):
            ev["rules"]["reEntry"] = dict(
                status="re-entry-printed",
                excerpt=("Registration: \"Unlimited re-entry for each starting flight will be available until the start "
                         "of level 10.\" The printed prize line reads \"$1,100 (1st Entry = $1,000 + $100; Re-Entry = "
                         "$1,000 + $100)\", and the sheet prints: \"A player may play a maximum of one (1) starting "
                         "flight. Players that bag in a flight may not play another flight. Players eliminated in a "
                         "starting flight may re-enter that starting flight until the start of level 10.\""),
                source=WPT_REREAD["sheetUrl"], retrieved=WPT_REREAD["retrievedOn"])
            ev["rules"]["singleEntry"] = dict(
                status="one-flight-cap",
                excerpt="A player may play a maximum of one (1) starting flight; bagged players may not play another flight.",
                source=WPT_REREAD["sheetUrl"], retrieved=WPT_REREAD["retrievedOn"])
        if ev.get("venue") == "wynn" and ev.get("buyIn") == 10400 and "World Championship" in ev.get("name", ""):
            ev["rules"]["fee"] = dict(
                status="fee-split-printed",
                excerpt=("The printed prize line reads \"$10,400 (1st Entry = $10,000 + $400; Re-Entry = $10,000 + "
                         "$400)\"; the sheet prints that $10,400 is withheld from first prize and the winner receives "
                         "entry into the 2027 WPT World Championship."),
                source=WPT_REREAD["sheetUrl"], retrieved=WPT_REREAD["retrievedOn"])
            ev["note"] = (ev.get("note", "") + " The printed components of the first prize are a seat in the 2027 WPT "
                                               "World Championship; the cash shown is after the $10,400 withholding. "
                                               "This event's re-entry clause sits in the level-10 registration family; "
                                               "its exact wording was not transcribed in this pass and the row's "
                                               "re-entry rule stays unverified.").strip()


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
               "Snapshot date 2026-11-17. Rows re-read that day carry 2026-11-17 as their last-checked date; every other row keeps the date it was last read."),
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
        verifiedOn=VERIFIED_ON,
        liveFacts=LIVE_FACTS_2026_11_17,
        # entries x buy-in + nights x (rate + resort fee) x (1 + tax), computed
        # from the eight primary entries and the seven recommended nights.
        tripCostModel=with_live_quote(published_model(len([p for p in plan if p.get("primary")]), _avg_primary_buyin(plan), TRIP["nights"])),
    )
    return data


def with_live_quote(model):
    """Adds the dated official quote for the trip stay beside the published-floor model.

    The quote is the booking engine's checkout total for all nights, with the resort fee and tax included,
    read on 2026-11-17. The tournament total and parking are the same as in the floor model.

    The engine's price for a stay moves between reads: the identical query printed $4,010.55 at 21:54 UTC and
    $3,823.46 at about 22:07 UTC. Both are kept. The later reading is published as the current figure and the
    earlier one is carried beside it as `earlierSameDayReading`, so the movement is visible instead of hidden.
    """
    q = H.VENETIAN_QUOTE_TRIP
    rates = [r for _, r in q["nightly"]]
    nights = len(rates)
    earlier = H.VENETIAN_QUOTE_TRIP_PRIOR
    model["liveQuote"] = dict(
        quoteDate=q["observedOn"], checkIn=q["checkIn"], checkOut=q["checkOut"], nights=nights,
        roomRatesTotal=round(sum(rates), 2), resortFeeTotal=round(q["resortFeePerNight"] * nights, 2),
        taxTotal=q["taxes"], checkoutTotal=q["total"],
        nightlyAllInAverage=round(q["total"] / nights, 2),
        tournamentTotal=model["tournamentTotal"], parkingTotal=model["parkingTotal"],
        tripTotal=round(model["tournamentTotal"] + q["total"] + model["parkingTotal"], 2),
        basis=("Dated official booking-engine checkout total for two adults in a Luxury King suite, read 2026-11-17 "
               "at about 22:07 UTC. It is the engine's best available rate, not the phone-only poker rate (F66), and "
               "it is one read, not a guarantee."),
        earlierSameDayReading=dict(
            checkoutTotal=earlier["total"], taxTotal=earlier["taxes"],
            nightlyAllInAverage=round(earlier["total"] / nights, 2),
            roomRatesTotal=round(sum(r for _, r in earlier["nightly"]), 2),
            nightlyRates=[r for _, r in earlier["nightly"]],
            derivedNightly=earlier["derivedNightly"],
            property=earlier["property"], averageRate=earlier["averageRate"],
            note=("The identical official query, read earlier on 2026-11-17, printed $4,010.55 instead of "
                  "$3,823.46 and offered the venetian Luxury King rather than the palazzo Luxury King. The engine's "
                  "price for the same stay moved by $187.09 within about thirteen minutes. Both readings are kept "
                  "because the site's policy is a dated log, not a single number; see flag F78."),
        ),
        sources=dict(quote=q["source"], resortFee=H.VENETIAN_RESORT_FEE, tax=H.VENETIAN_HOTEL_TERMS),
    )
    return model


def _avg_primary_buyin(plan):
    """Average buy-in of the recommended primary events.

    Every primary is a different price, so the calculator is published with the
    average of the eight chosen entries. The sum is in TRIP["primaryBuyIns"], so a
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
