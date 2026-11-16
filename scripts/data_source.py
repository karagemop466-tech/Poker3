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


def session_estimate(start_min, late_text, level_min):
    """Estimate a session length from printed data only.

    When the structure sheet prints the late-registration cut-off clock time, the
    session cannot end before that point, so the estimate is the cut-off plus two
    more levels (one level and one break).  With no printed cut-off time the
    documented six-hour planning assumption is used.
    """
    cutoff = clock_minutes(late_text)
    if cutoff is None or start_min is None:
        return 360, "", None
    if cutoff <= start_min:
        cutoff += 1440
    level = level_min if isinstance(level_min, int) and level_min else 30
    length = (cutoff - start_min) + (2 * level) + 15
    return length, fmt_clock(cutoff), cutoff

VENUES = [
    dict(id="venetian", name="The Venetian Resort", pokerRoom="Venetian poker room",
         page="https://www.venetianlasvegas.com/resort/casino/poker.html",
         series="DeepStack Extravaganza IV (Nov 16 - Dec 23, 2026) and DeepStack Extravaganza NYE (Dec 24, 2026 - Jan 10, 2027)",
         schedule="https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html",
         hotels=["venetian", "palazzo"], note="Poker room is on the resort property; the poker-suite rate applies to The Venetian and The Palazzo."),
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
         type="official schedule", checked=ASOF),
    dict(id="vl-dse-dec", name="Venetian DeepStack Extravaganza NYE schedule and structure sheets (Dec 24, 2026 - Jan 10, 2027)",
         url="https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-dec-2026.html",
         type="official schedule", checked=ASOF),
    dict(id="vl-series", name="Venetian DeepStack Poker Series index (current, next and future series)",
         url="https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament.html",
         type="official index", checked=ASOF),
    dict(id="vl-poker", name="Venetian poker room page", url="https://www.venetianlasvegas.com/resort/casino/poker.html",
         type="official room page", checked=ASOF),
    dict(id="vl-suite-rates", name="Venetian poker-room suite rates and play requirements 2026",
         url="https://www.venetianlasvegas.com/resort/casino/poker/suite-rates.html", type="official rate page", checked=ASOF),
    dict(id="vl-resort-fee", name="Venetian resort fee page", url="https://www.venetianlasvegas.com/resort/resort-fee.html",
         type="official fee page", checked=ASOF),
    dict(id="vl-hotel-terms", name="Venetian hotel terms and conditions (tax, parking, cancellation)",
         url="https://www.venetianlasvegas.com/legal/hotel-terms-and-conditions.html", type="official terms", checked=ASOF),
    dict(id="wynn-poker", name="Wynn Las Vegas poker room page", url="https://www.wynnlasvegas.com/casino/poker",
         type="official room page", checked=ASOF),
    dict(id="wynn-daily-poster", name="Wynn daily tournament poster",
         url="https://cdn.wynnresorts.com/image/upload/v1752011166/visitwynn_pdfs_files/Poker/Daily%20Tournaments/poker-daily-tournament-poster.pdf",
         type="official schedule", checked=ASOF),
    dict(id="wynn-daily-struct", name="Wynn daily tournament terms and structures",
         url="https://cdn.wynnresorts.com/image/upload/v1752011191/visitwynn_pdfs_files/Poker/Daily%20Tournaments/Poker-All_Daily_Structures.pdf",
         type="official structures", checked=ASOF),
    dict(id="wynn-wpt-sched", name="WPT World Championship schedule at Wynn Las Vegas (Nov 27 - Dec 21, 2026)",
         url="https://cdn.wynnresorts.com/image/upload/v1757097329/visitwynn_pdfs_files/Poker/WPT/WPT_World_Championship_Schedule.pdf",
         type="official schedule", checked=ASOF),
    dict(id="wynn-wpt-struct", name="WPT World Championship structures at Wynn Las Vegas",
         url="https://cdn.wynnresorts.com/image/upload/v1750864036/visitwynn_pdfs_files/Poker/WPT/WPT_World_Championship_Structures.pdf",
         type="official structures", checked=ASOF),
    dict(id="wynn-sig-sched", name="Wynn Signature Series schedule (Jan 11-24, 2027)",
         url="https://cdn.wynnresorts.com/image/upload/v1753296112/visitwynn_pdfs_files/Poker/Wynn%20Signature%20Series/Wynn_Signature_Series_Schedule.pdf",
         type="official schedule", checked=ASOF),
    dict(id="wynn-rooms", name="Wynn Las Vegas rooms and suites", url="https://www.wynnlasvegas.com/rooms-and-suites",
         type="official room page", checked=ASOF),
    dict(id="wynn-terms", name="Wynn Las Vegas terms (resort fee, cancellation, parking)",
         url="https://www.wynnlasvegas.com/terms-and-conditions/850070", type="official terms", checked=ASOF),
    dict(id="bell-poker", name="Bellagio poker room page", url="https://bellagio.mgmresorts.com/en/casino/poker.html",
         type="official room page", checked=ASOF),
    dict(id="bell-fri", name="Bellagio Friday $600 No Limit Hold'em structure",
         url="https://assets.contentstack.io/v3/assets/bltc6ce635bc4868eb2/blt9cf95b0e60ec253e/6af491a3a9851d75c40be840/mgm-bellagio-poker-fridays-$600-nlh.pdf",
         type="official structure", checked=ASOF),
    dict(id="bell-sat", name="Bellagio Saturday No Limit Hold'em structure (buy-in conflict)",
         url="https://assets.contentstack.io/v3/assets/bltc6ce635bc4868eb2/blt6d47974bf5a7d9b6/6af491a391a6e8e4230c9e07/mgm-bellagio-poker-saturdays-$1000-nlh.pdf",
         type="official structure", checked=ASOF),
    dict(id="bell-sun", name="Bellagio Sunday $400 H.O.R.S.E. structure",
         url="https://assets.contentstack.io/v3/assets/bltc6ce635bc4868eb2/blt07fcf1244a6da661/6af491a339e2b4f6b76a86ad/mgm-bellagio-poker-sundays-$400-horse.pdf",
         type="official structure", checked=ASOF),
    dict(id="bell-hotel", name="Bellagio hotel rooms and suites", url="https://bellagio.mgmresorts.com/en/hotel.html",
         type="official room page", checked=ASOF),
    dict(id="bell-terms", name="Bellagio hotel reservation terms (resort fee, cancellation, taxes)",
         url="https://bellagio.mgmresorts.com/en/terms-and-conditions.html", type="official terms", checked=ASOF),
    dict(id="mgm-poker", name="MGM Grand poker room page", url="https://mgmgrand.mgmresorts.com/en/casino/poker-tables.html",
         type="official room page", checked=ASOF),
    dict(id="mgm-sched", name="MGM Grand weekly tournament schedule sheet",
         url="https://assets.contentstack.io/v3/assets/bltc6ce635bc4868eb2/blt5f25277b8918da08/mgm-grand-casino-poker-tournament_schedule.pdf",
         type="official schedule", checked=ASOF),
    dict(id="mgm-struct", name="MGM Grand $120 No Limit Hold'em structure",
         url="https://assets.contentstack.io/v3/assets/bltc6ce635bc4868eb2/bltb2a45da7e8ee5621/mgm-grand-casino-poker-120_nlh.pdf",
         type="official structure", checked=ASOF),
    dict(id="caesars-poker", name="Caesars Palace and Horseshoe poker tournament page",
         url="https://www.caesars.com/las-vegas/explore/casino/poker-tournaments-las-vegas-strip",
         type="official room page", checked=ASOF),
    dict(id="aria-poker", name="ARIA poker room page", url="https://aria.mgmresorts.com/en/casino/poker.html",
         type="official room page", checked=ASOF),
    dict(id="aria-guide", name="ARIA official poker guide (undated)",
         url="https://aria.mgmresorts.com/content/dam/MGM/aria/casino/poker/aria-casino-poker-gentlemans-guide.pdf",
         type="official guide", checked=ASOF),
]

FLAGS = [
    dict(id="F01", area="Wynn WPT schedule", severity="High",
         title="The official WPT schedule PDF labels December 18 as both a Wednesday and a Friday",
         detail=("In the same PDF, 'Dec. 18 Wednesday' carries the No Limit Hold'em Day 1A and PLO rows while 'Dec. 18 Friday' "
                 "carries the WPT World Championship Day 4 rows. The rows also run out of order, with the December 17 block "
                 "printed after the December 18 Wednesday block. December 18, 2026 is a Friday, so the 'Wednesday' label is the "
                 "error. The schedule dates are reproduced exactly as printed and the weekday label is flagged rather than corrected."),
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
    dict(id="F11", area="Venetian NYE", severity="Medium",
         title="The 15 DeepStack Extravaganza NYE structure sheets were not read in this pass",
         detail=("The NYE rows come from the official schedule page, so dates, times, buy-ins and guarantees are official, but the "
                 "entry rules behind them (re-entry, add-on, multi-flight wording) have not been read. Those rows are marked "
                 "'structure sheet not read' and are excluded from the single-entry filter."),
         source="https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-dec-2026.html"),
    dict(id="F12", area="Wynn WPT", severity="Medium",
         title="WPT World Championship structure sheets were not read in this pass",
         detail=("The WPT schedule PDF publishes buy-in, guarantee, chips and level length but not the entry rules. The structure "
                 "PDF is an eight-chunk document that was not read end to end, so re-entry and add-on terms for WPT rows are "
                 "marked unverified and those rows are excluded from the single-entry filter."),
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
         title="No property publishes a date-specific checkout total, so no true nightly total is confirmed",
         detail=("Only per-night components are published: room rate, resort fee and tax. The Venetian publishes starting poker "
                 "suite rates of $119 and $209 that are not date-specific and are not mapped to a property. The calculator therefore "
                 "shows a floor computed from published components and labels it as a floor, not a quote."),
         source="https://www.venetianlasvegas.com/resort/casino/poker/suite-rates.html"),
    dict(id="F16", area="Schedule", severity="High",
         title="No official schedule publishes tournament finish times",
         detail=("Venetian sheets publish start time, level length and late-registration cut-off but no finish time. The overlap "
                 "check therefore uses a stated planning assumption (a six-hour session plus a 30-minute transfer between venues) "
                 "and every conflict it reports is an estimate, not an official statement."),
         source="https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html"),
    dict(id="F17", area="Schedule", severity="High",
         title="No verified start time earlier than 9:10 AM exists in the reviewed official schedules",
         detail=("The earliest verified starts are the Venetian RaceDay Stack at 10:10 AM, the Venetian seniors and tag-team events "
                 "at 10:10 AM, Horseshoe at 9:00 AM and Caesars Palace at 10:00 AM, the Wynn daily at 12:00 PM and the Wynn WPT "
                 "at 11:00 AM. An 'all day from 8:00 AM' plan cannot be built from official sources. The day plan therefore starts "
                 "at the earliest verified start for each venue."),
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
    dict(id="F22", area="Venetian DSE IV", severity="Low",
         title="The RaceDay Stack sheets print no guarantee",
         detail=("Sheets 18 and 29 print the buy-in, rake and blind structure but no guarantee line, so events 3, 4, 5 and 6 carry "
                 "a blank guarantee and are not ranked by the guaranteed-pool-to-fee ratio."),
         source="https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_18.pdf"),
]

QUESTIONS = [
    dict(id="Q01", question="What are the actual travel dates, and how many nights?",
         answer="Not supplied and not inferable from official sources. Every rate is date-, occupancy- and availability-dependent, so no date-specific quote can be requested or compared until dates exist.",
         why="Needed", blocking="Yes - no hotel total can be confirmed without it",
         how="Pick the arrival and departure dates, then request a quote from each property's own booking channel.",
         source="https://www.venetianlasvegas.com/resort/casino/poker/suite-rates.html"),
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
         answer="For the Venetian one-day events the official sheets print one buy-in, one start flight and no re-entry, rebuy, add-on or second-flight clause. The sheets never use the words 'single entry' or 'freezeout', so the site labels this as 'single entry on the official sheet' and shows the excerpt. For Wynn, Bellagio, MGM Grand and Caesars the sheets print re-entry, rebuy or add-on clauses, so those events are placed in the separate extra-spend section.",
         why="Needed", blocking="No - the rule set is documented on every row",
         how="Ask the poker room to confirm in writing that a second buy-in is not accepted for a specific event if that matters for your decision.",
         source="https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_5.pdf"),
    dict(id="Q05", question="Which hotels actually publish a room price for the dates you want?",
         answer="None of the reviewed properties publishes a price on the page itself. The Venetian publishes starting poker-suite rates of $119 and $209 that are explicitly not date-specific, and it states that future rates are only provided up to 150 days out.",
         why="Needed", blocking="Yes for a confirmed total",
         how="Request a written quote per property for the exact dates, and log it in the rate log on this site with the quote timestamp.",
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
    dict(id="Q08", question="What is the real walking time between the chosen hotel and each poker room?",
         answer="The venues publish no walking times. Google Maps walking estimates captured on 2026-11-16 are used and labelled as estimates: Caesars Palace to the Venetian 12 minutes, Wynn to the Venetian 13, Horseshoe 16, Bellagio 21, ARIA 31, MGM Grand 35. The Wynn poker room is in Encore, a 10-minute walk from the Wynn hotel.",
         why="Needed", blocking="No - the 30-minute filter is applied to the estimates",
         how="Re-check the live Maps route on the morning of each tournament; Strip crossings add time that the estimate does not include.",
         source="https://www.wynnlasvegas.com/casino/poker"),
    dict(id="Q09", question="Which other Strip rooms should be added to the plan?",
         answer="Not covered. This pass verified The Venetian, Wynn, Bellagio, MGM Grand, Caesars Palace, Horseshoe and ARIA. South Point, Golden Nugget, Resorts World, Circa, Excalibur, Luxor, Orleans, Red Rock, Palms, Westgate, Tropicana, Bally's, Flamingo, LINQ, Planet Hollywood, Rio and M Resort were not checked.",
         why="Useful", blocking="No",
         how="Say which properties to add; each needs its own official page and structure sheets.",
         source="https://www.venetianlasvegas.com/resort/casino/poker.html"),
    dict(id="Q10", question="Do the December 17-23 and holiday-week events still run as published?",
         answer="The schedule pages are current as published on 2026-11-16, and this site re-checks every source URL on a schedule. Any source that changes is flagged on the change log.",
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
]


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
                               "No re-entry, rebuy, add-on or second-flight provision appears anywhere on the sheet."), **base)
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
           sheet_url, schedule_url, structure_url=None, last_checked=ASOF,
           note="", eligibility="", guarantee_note="", chips="", level_min="",
           late_reg="", entry_type="not-verified", fmt="", continuation=False, weekdays=None):
    buy = buyIn if isinstance(buyIn, str) else ("" if buyIn in (None, "-") else buyIn)
    gua = guarantee if isinstance(guarantee, str) else ("" if guarantee in (None, "-") else guarantee)
    start = clock_minutes(time)
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
        lastChecked=last_checked, note=note, eligibility=eligibility,
    )


CATEGORIES = {
    "single": {"label": "Single entry (verified on the official sheet)", "blurb":
               "The official structure sheet prints one buy-in, one start flight and no re-entry, rebuy, add-on or "
               "second-flight clause."},
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
    "start": "2026-11-25",
    "end": "2026-12-02",
    "nights": 7,
    "days": 8,
    "hotel": "venetian",
    "alternativeHotel": "palazzo",
    "nightlyBudget": 197.28,
    "nightlyBudgetNote": (
        "Fixed by this session at the lowest published true nightly cost of the recommended property: "
        "($119 published poker-suite starting rate + $55 mandatory resort fee) x 1.1338 Clark County room tax = $197.28. "
        "It is a floor computed from published components, not a quote."),
    "nightlyBudgetCeiling": 299.32,
    "qualityFloor": (
        "Fixed by this session on an objective published-evidence test rather than an invented score: the property must "
        "publish its own poker-room rate, keep the poker room on site, and publish its resort fee, tax and cancellation "
        "terms. No comparable official quality score exists for these rooms, so the quality column stays blank (F19)."),
    "rationale": [
        ("2026-11-25 to 2026-12-02 (7 nights, 8 days) holds the largest number of single-entry events verified on an "
         "official structure sheet: 14, and every one of the eight days has at least one."),
        ("All 37 DeepStack Extravaganza IV structure sheets were read directly on 2026-11-16, so the single-entry "
         "classification on these dates comes from a primary source rather than from the schedule title."),
        ("The window stays inside DSE IV. The December 24 to January 10 DeepStack NYE dates are published on the "
         "official schedule page, but the 15 NYE structure sheets were not read, so those rows cannot enter the "
         "single-entry list yet (F11)."),
        ("It also sits before the $10,400 WPT World Championship buy-in tier on December 13, which would break the trip "
         "budget on a single entry."),
        ("The Wynn WPT schedule runs from November 27 inside the window, so three days carry additional published rows, "
         "all clearly marked as series rows with unverified entry rules (F12)."),
    ],
    "bankrollNote": ("Bankroll figure on the day-plan page is the sum of the eight recommended primary buy-ins plus a 25% "
                     "buffer for one rebuy or an add-on if a room allows it. It is a planning number, not a forecast."),
}

PLAN_NOTES = {
    "primaryRule": ("Primary event = the verified single-entry event on that date with the largest published guarantee, "
                    "among venues within a 30-minute walk of the recommended hotel, excluding age-restricted, "
                    "female-only and team formats."),
    "fallbackRule": ("Fallback = the next verified single-entry event that starts after the primary's estimated finish "
                     "plus a 30-minute transfer. When nothing fits, the fallback is the best alternative that date with "
                     "the reason it was not chosen."),
    "transfer": 30,
    "walkLimit": 30,
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
    """Can this event be a recommended primary entry for a general traveller?

    Ranking needs a confirmed entry fee and a confirmed guarantee, a verified
    single-entry sheet, no age/gender/team restriction, and a venue inside the
    30-minute walking limit from the recommended hotel.
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
    return "Next best published single-entry event on this date."


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
                    fallback_reason = ("No other verified single-entry event is published for this date. The multi-flight "
                                       "and series rows for this date are listed in the tournaments table.")
        else:
            fallback_reason = "No verified single-entry event with a published fee and guarantee on this date."
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
        ))
    return plan, conflicts



def build():
    events = []

    # --- Venetian DSE IV -------------------------------------------------
    for date, time, no, name, sheet, guarantee, category in V.DSE_ROWS:
        s = V.SHEETS[sheet]
        url = f"{V.BASE}/dse_nov_2026-structure_{sheet}.pdf"
        cont = bool(re.search(r"day [23]\b", name.lower()))
        events.append(_event(
            f"vl-dse-{date}-{no}-{time.replace(':', '').replace(' ', '').lower()}",
            "venetian", date, time, name, s["buyIn"], guarantee, _rules_for_sheet(sheet),
            category, s["kind"], url, V.DSE, url,
            note=s.get("note", "") + (s.get("entryExcerpt", "") if s.get("entryExcerpt") else ""),
            eligibility=s.get("eligibility", ""),
            guarantee_note="multi-flight" if s["kind"] == "flight" else ("includes bounties" if "bounties" in s["guarantee"] else ""),
            chips=s.get("chips", ""), level_min=s.get("levelMin", ""), late_reg=s.get("late", ""),
            entry_type=s["entry"], continuation=cont,
        ))

    # --- Venetian DSE NYE ------------------------------------------------
    for date, time, no, name, sheet_file, guarantee, category in V.NYE_ROWS:
        url = f"{V.BASE}/{sheet_file}"
        rules = {
            "singleEntry": dict(status="not-verified", excerpt="The NYE structure sheet has not been read in this pass, so no entry rule is confirmed.", source=url, retrieved=ASOF),
            "reEntry": dict(status="not-verified", excerpt="The NYE structure sheet has not been read in this pass.", source=url, retrieved=ASOF),
            "addOn": dict(status="not-verified", excerpt="The NYE structure sheet has not been read in this pass.", source=url, retrieved=ASOF),
            "fee": dict(status="confirmed", excerpt="The buy-in is printed in the official schedule event name.", source=V.NYE, retrieved=ASOF),
        }
        cont = bool(re.search(r"day [23]\b", name.lower()))
        events.append(_event(
            f"vl-nye-{date}-{no}-{time.replace(':', '').replace(' ', '').lower()}",
            "venetian", date, time, name, "", guarantee, rules, category, "single", url, V.NYE, url,
            note="DeepStack Extravaganza NYE. Structure sheet not read in this pass (see F11).",
            continuation=cont,
        ))

    # --- Wynn daily ------------------------------------------------------
    for i, d in enumerate(N.WYNN_DAILY):
        rules = {k: dict(v, source=d["source"], retrieved=ASOF) for k, v in d["rules"].items()}
        events.append(_event(
            f"wynn-daily-{i}", "wynn", "", d["time"], f"{d['name']} ({d['days']})",
            d["buyIn"], d["guarantee"], rules, d["category"], "daily",
            d["poster"], d["source"], d["source"],
            note=d.get("note", "") + f" Recurring {d['days'].lower()}.", last_checked=ASOF,
            chips=d.get("chips", ""), level_min=d.get("levelMin", ""), late_reg=d.get("lateReg", ""),
            entry_type="multi-buyin", weekdays=d.get("weekdays", []),
        ))

    # --- Wynn WPT --------------------------------------------------------
    for idx, line in enumerate(N.WYNN_WPT_ROWS.splitlines()):
        date, time, name, buy_in, guarantee, chips, levels = line.split("|")
        buy = "" if buy_in == "-" else int(buy_in)
        gua = "" if guarantee == "-" else int(guarantee)
        flight = bool(re.search(r"Day 1[A-F]\b", name))
        cat = "flight" if flight else ("satellite" if "Satellite" in name else "wpt")
        rules = {
            "singleEntry": dict(status="not-verified",
                                excerpt="The WPT structure sheets have not been read in this pass, so no entry rule is confirmed for this event.",
                                source=N.WYNN_WPT_STRUCT, retrieved=ASOF),
            "reEntry": dict(status="not-verified", excerpt="The WPT structure sheets have not been read in this pass.",
                            source=N.WYNN_WPT_STRUCT, retrieved=ASOF),
            "addOn": dict(status="not-verified", excerpt="The WPT structure sheets have not been read in this pass.",
                          source=N.WYNN_WPT_STRUCT, retrieved=ASOF),
            "fee": dict(status="confirmed", excerpt=f"Buy-in ${buy_in} and guarantee ${guarantee} are printed on the official schedule PDF.",
                        source=N.WYNN_WPT_SCHED, retrieved=ASOF),
        }
        events.append(_event(
            f"wynn-wpt-{date}-{idx:03d}-{time.replace(':', '').replace(' ', '').lower()}",
            "wynn", date, time, name, buy, gua, rules, cat, "wpt",
            N.WYNN_WPT_SCHED, N.WYNN_WPT_SCHED, N.WYNN_WPT_STRUCT,
            note=("Multiple start flights are published for this event, so more than one entry is possible." if flight else
                  "Schedule row from the official WPT World Championship schedule PDF; entry rules not yet read."),
            chips=int(chips) if chips not in ("-", "") else "", entry_type=("multi-flight" if flight else "not-verified"),
            continuation=bool(re.search(r"day [2345]\b|final table", name.lower())),
        ))

    # --- Wynn Signature Series ------------------------------------------
    for idx, line in enumerate(N.WYNN_SIGNATURE_ROWS.splitlines()):
        date, time, name, buy_in, guarantee, chips, levels = line.split("|")
        buy = "" if buy_in == "-" else int(buy_in)
        gua = "" if guarantee == "-" else int(guarantee)
        flight = bool(re.search(r"Day 1[A-F]\b", name))
        cat = "flight" if flight else ("satellite" if "Satellite" in name else "wpt")
        rules = {
            "singleEntry": dict(status="not-verified",
                                excerpt="The Wynn Signature Series structure sheets have not been read in this pass.",
                                source=N.WYNN_SIG_STRUCT, retrieved=ASOF),
            "reEntry": dict(status="not-verified", excerpt="The Wynn Signature Series structure sheets have not been read in this pass.",
                            source=N.WYNN_SIG_STRUCT, retrieved=ASOF),
            "addOn": dict(status="not-verified", excerpt="The Wynn Signature Series structure sheets have not been read in this pass.",
                          source=N.WYNN_SIG_STRUCT, retrieved=ASOF),
            "fee": dict(status="confirmed", excerpt=f"Buy-in ${buy_in} and guarantee ${guarantee} are printed on the official schedule PDF.",
                        source=N.WYNN_SIG_SCHED, retrieved=ASOF),
        }
        events.append(_event(
            f"wynn-sig-{date}-{idx:03d}-{time.replace(':', '').replace(' ', '').lower()}",
            "wynn", date, time, name, buy, gua, rules, cat, "wpt",
            N.WYNN_SIG_SCHED, N.WYNN_SIG_SCHED, N.WYNN_SIG_STRUCT,
            note=("Multiple start flights are published for this event." if flight else
                  "Wynn Signature Series row from the official schedule PDF; entry rules not yet read."),
            chips=int(chips) if chips not in ("-", "") else "", entry_type=("multi-flight" if flight else "not-verified"),
            continuation=bool(re.search(r"day [2345]\b|final table", name.lower())),
        ))

    # --- Other venues ----------------------------------------------------
    def add_group(group, venue, prefix):
        for i, d in enumerate(group):
            rules = {k: dict(v, source=d["source"], retrieved=ASOF) for k, v in d["rules"].items()}
            st = rules["singleEntry"]["status"]
            entry_type = ("none" if st == "single-entry-on-sheet"
                          else ("not-verified" if "not-verified" in st else "multi-buyin"))
            events.append(_event(
                f"{prefix}-{i}", d.get("venue", venue), "", d["time"],
                f"{d['name']} ({d['days']})" if d.get("days") else d["name"],
                d.get("buyIn", ""), d.get("guarantee", ""), rules,
                d.get("category", "recurring"), "recurring",
                d["source"], d["source"], d.get("page", d["source"]),
                note=d.get("note", ""),
                chips=d.get("chips", ""), level_min=d.get("levelMin", ""),
                late_reg=d.get("lateReg", ""), entry_type=entry_type,
                weekdays=d.get("weekdays", []),
            ))

    add_group(N.BELLAGIO_EVENTS, "bellagio", "bell")
    add_group(N.MGM_EVENTS, "mgm", "mgm")
    add_group(N.CAESARS_EVENTS, "caesars", "caes")
    add_group(N.HORSESHOE_EVENTS, "horseshoe", "horse")
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
        row["lastChecked"] = ASOF
        hotels.append(row)

    routes = []
    for r in H.ROUTES:
        row = dict(r)
        row["mapsUrl"] = H.MAPS.format(o=r["mapsOrigin"], d=r["mapsDestination"])
        row["lastChecked"] = ASOF
        row["walkSourceType"] = "Google Maps walking estimate"
        routes.append(row)

    recurring_events = [e for e in events if not e["date"] and e.get("weekdays")]
    plan, conflicts = build_day_plan(events, TRIP["start"], TRIP["end"], recurring_events)
    bankroll = sum(p["primaryBuyIn"] for p in plan if isinstance(p["primaryBuyIn"], (int, float)))
    TRIP["primaryBuyIns"] = bankroll
    TRIP["bankrollWithBuffer"] = round(bankroll * 1.25)
    TRIP["bankrollNote"] = (f"The eight recommended primary entries total ${bankroll:,} in buy-ins. With a 25% buffer "
                            f"for one rebuy or add-on where a room allows it, plan on ${round(bankroll * 1.25):,}.")

    structure_sheets = []
    for n in sorted(V.SHEETS):
        structure_sheets.append(dict(
            venue="venetian", series="DeepStack Extravaganza IV", sheet=n,
            url=f"{V.BASE}/dse_nov_2026-structure_{n}.pdf",
            readOn=V.RETRIEVED, read=True,
            note="Read directly; excerpt recorded on the tournament row and in research/structure_notes.md."))
    for date, time, no, name, sheet_file, guarantee, category in V.NYE_ROWS:
        url = f"{V.BASE}/{sheet_file}"
        if not any(s["url"] == url for s in structure_sheets):
            structure_sheets.append(dict(
                venue="venetian", series="DeepStack Extravaganza NYE", sheet=sheet_file,
                url=url, readOn="", read=False,
                note="Not read in this pass; the row carries schedule-level facts only (F11)."))

    data = dict(
        asOf=ASOF,
        scope=("Las Vegas Strip poker tournaments and Strip lodging, built only from official venue and property pages. "
               "Snapshot date 2026-11-16."),
        policy=("Every row links the official page it came from. A value that could not be confirmed from an official source is "
                "left blank and listed on the Flagged for review page. Walking minutes are Google Maps walking estimates and are "
                "labelled as such. The guaranteed-pool-to-fee ratio is descriptive only and is not a forecast."),
        sessionLengthAssumption=("No venue publishes a finish time. The schedule planner assumes a six-hour session plus a "
                                 "30-minute transfer between venues, so every conflict it reports is an estimate."),
        categories=CATEGORIES,
        venues=VENUES, events=events, hotels=hotels, rateLog=H.RATE_LOG, routes=routes,
        sources=SOURCES, flags=FLAGS, questions=QUESTIONS, suggestions=SUGGESTIONS,
        trip=TRIP,
        dayPlan=plan, planConflicts=conflicts, planNotes=PLAN_NOTES,
        structureSheets=structure_sheets,
        feed=FEED_ROOMS,
    )
    return data



def main():
    out = ROOT / "site" / "data.json"
    data = build()
    out.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    cats = {}
    for e in data["events"]:
        cats[e["category"]] = cats.get(e["category"], 0) + 1
    print(f"wrote {out} with {len(data['events'])} events, {len(data['hotels'])} hotels, "
          f"{len(data['routes'])} routes, {len(data['sources'])} sources")
    print("categories:", cats)
    print("venues:", sorted({e["venue"] for e in data["events"]}))


if __name__ == "__main__":
    main()
