#!/usr/bin/env python3
"""The 2026-11-19 line-by-line requirements audit and verification record.

This module is data, not inference. Every "source" URL here is an official
venue/property page or official PDF that was read live on 2026-11-19 by session
arena/8194609f, or (for process rows) the repository file that is the evidence.
Verbatim excerpts are transcribed in research/verification_2026-11-19_arena-8194609f.md.

Nothing in this module changes a tournament, fee, guarantee, hotel, rate, route
or policy value. It only publishes the audit of what the site already does.
"""
from __future__ import annotations

CHECKED = "2026-11-19"
SESSION = "arena/8194609f-poker3"

VL_SCHED = "https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html"
VL_SHEET_7 = "https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_7.pdf"
VL_SHEET_1 = "https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_1.pdf"
VL_RATES = "https://www.venetianlasvegas.com/resort/casino/poker/suite-rates.html"
VL_FEE = "https://www.venetianlasvegas.com/resort/resort-fee.html"
VL_TERMS = "https://www.venetianlasvegas.com/legal/hotel-terms-and-conditions.html"
VL_PARKING = "https://www.venetianlasvegas.com/resort/casino/poker/player-parking.html"
VL_BOOK = "https://www.venetianlasvegas.com/booking?adults%5B%5D=2&arrival_date=2026-11-23&children%5B%5D=0&departure_date=2026-11-30&view=calendar"
VL_SERIES = "https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament.html"
WYNN_POKER = "https://www.wynnlasvegas.com/casino/poker"
WYNN_INFO = "https://www.wynnlasvegas.com/about-us/resort-information"
WYNN_PARKING = "https://www.wynnlasvegas.com/about-us/parking"
WYNN_BOOK = "https://reservations.wynnlasvegas.com/ibe/details.aspx?hotelID=13763&langID=1&rmID=68658&checkIn=11/23/2026&checkOut=11/30/2026"
BELL_POKER = "https://bellagio.mgmresorts.com/en/casino/poker.html"
BELL_SAT = "https://assets.contentstack.io/v3/assets/bltc6ce635bc4868eb2/blt6d47974bf5a7d9b6/6af491a391a6e8e4230c9e07/mgm-bellagio-poker-saturdays-$1000-nlh.pdf"
BELL_TERMS = "https://bellagio.mgmresorts.com/en/terms-and-conditions.html"
CAES_ARTICLE = "https://www.caesars.com/las-vegas/explore/casino/poker-tournaments-las-vegas-strip"
CAES_FLYER = "https://www.caesars.com/content/dam/empire/clv/casino/poker/tournament-schedule/clv-poker-daily-nlh-tournament-flyer-2026.pdf"
COUNTY_TAX = "https://www.clarkcountynv.gov/adobe/assets/urn:aaid:aem:689ef54f-ec0d-4bb6-b8ea-05a82887561f/original/as/genl-info-guide-for-tles-july-2021.pdf"
VL_2023 = "https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-apr-2023.html"
REPO = "https://github.com/karagemop466-tech/Poker3/blob/main/"

# --------------------------------------------------------------------------
# Requirement-by-requirement audit. One row per explicit instruction in the brief.
# --------------------------------------------------------------------------
_REQ = [
    ("R01", 'Estimated cost of a trip calculator: entries × buy-ins + nights × true hotel cost.',
     "done", ["calculator.html", "index.html"],
     "Trip cost model publishes 8 entries totalling $2,600 in buy-ins, 7 nights at the published floor of $197.28 and a $4,120.96 illustrative total; the formula is printed on the page and asserted by tests/test_trip_cost_reproducible.py.",
     [VL_SCHED, VL_RATES, VL_TERMS]),
    ("R02", 'Automatic re-check of each official URL on a schedule; mark rows whose source changed.',
     "done", ["sources.html", "tournaments.html"],
     ".github/workflows/checks.yml runs a cron at 12:10 UTC plus push/workflow_dispatch; scripts/check_sources.py records 107 URLs in site/checks.json; app.js sourceStatusBadges() marks each affected event/hotel row. The 2026-11-19T06:15:40Z run reports 0 changed.",
     [VL_SCHED, WYNN_POKER]),
    ("R03", 'Read every structure sheet and remove the "unverified" label from each event that is confirmed.',
     "done", ["sheets.html", "tournaments.html"],
     "All 52 sheets (37 DSE IV + 15 NYE) are read=true in site/data.json; zero published rows carry the unverified category. The 2026-11-19 reads of sheets 1, 6 and 7 confirm their printed fees, chips and payout wording.",
     [VL_SHEET_1, VL_SHEET_7]),
    ("R04", 'Add a "last checked" date to each row.',
     "done", ["tournaments.html", "hotels.html", "sources.html"],
     "verify_site.py fails if any event, hotel or route row lacks lastChecked; rateLog rows carry observedOn. The tournament table prints both lastChecked and lastVerified.",
     [VL_SCHED]),
    ("R05", 'Keep rates as a dated log, not a single value.',
     "done", ["hotels.html", "calculator.html"],
     "34 dated rateLog observations; the 17-19 Nov 2026 stay printed $1,245.48 on 16 Nov and $1,015.89 on 17 Nov, and the 23-30 Nov stay printed $4,010.55 (Venetian) / $3,823.46 (Palazzo). Observations are appended, never overwritten.",
     [VL_BOOK, VL_RATES]),
    ("R06", 'One page per venue (Venetian, Wynn, others), each with its events and hotels.',
     "done", ["venues/index.html", "venues/venetian.html", "venues/wynn.html", "venues/others.html"],
     "Four venue pages render event and hotel rows from site/data.json via assets/venue.js; a headless render check asserts at least five event rows and one hotel row per page. Stale hardcoded claims were corrected this session (F97).",
     [VL_SCHED, WYNN_POKER, BELL_POKER]),
    ("R07", 'Add a search box across all tables.',
     "done", ["search.html"],
     "search.html + assets/search.js index tournaments, hotels, dated rates, walking routes, sources, sheets, questions, flags, suggestions, the feed and the day plan; a global search box appears in every page header.",
     [VL_SCHED]),
    ("R08", 'Use one shared COORDINATION.md on main before parallel sessions start.',
     "done", ["repo:COORDINATION.md"],
     "The board exists at the repo root on main and carries each task's status, owning session and file scope. This session claimed its task there and pushed the claim before any other work; two orphan conflict markers were removed (already recorded on main as F98 by a parallel session, so no duplicate flag was added).",
     [REPO + "COORDINATION.md"]),
    ("R09", 'For exact dates and occupancy, capture checkout total, nightly average, mandatory resort fee and tax, parking, cancellation deadline and rate timestamp; compare like-for-like.',
     "done", ["hotels.html", "calculator.html"],
     "The 23-30 Nov 2026 quote records checkout total $4,010.55, nightly rates, $55 fee × 7, $473.30 tax, an 11:00 a.m. checkout, 72-hour (Bellagio) / 48-hour (Wynn) cancellation deadlines and read timestamps. Like-for-like rows hold suite name, party size and read time. Verified verbatim 2026-11-19.",
     [VL_TERMS, BELL_TERMS, WYNN_INFO]),
    ("R10", 'Use start time, late-registration cutoff and plausible duration to flag overlapping entries; give each day a primary event and a conditional fallback, not an impossible sequence.',
     "done", ["schedule.html"],
     "Seven day-plan rows carry a primary plus a conditional fallback with an explicit sequence status (replaces / playable after / same-day alternative). 29 planConflicts are labelled estimates; tests/test_fallback_sequencing.py forbids an impossible fallback.",
     [VL_SCHED, VL_SHEET_7]),
    ("R11", 'Rank only after confirming total entry fee and guarantee; display guaranteed pool ÷ entry fee as a descriptive ratio, not a forecast; label bounty/flight events separately.',
     "done", ["tournaments.html", "schedule.html"],
     "Only rows with a printed buy-in and guarantee are ranked; ratioCell() prints 'pool ÷ fee (descriptive)'; bounty, flight and satellite categories have their own labels and are excluded from the single-entry path.",
     [VL_SHEET_1, VL_SHEET_7]),
    ("R12", 'Date filter: a date selector that shows only events on the chosen days.',
     "done", ["tournaments.html"],
     "From/To date inputs in the tournament filters; state.from/state.to gate the rows. Verified present in assets/app.js buildTournamentControls().",
     [VL_SCHED]),
    ("R13", 'Structured rule fields: single-entry, re-entry, add-on and fee values separately for each event, each with source excerpt and retrieval date.',
     "done", ["tournaments.html"],
     "Every event carries rules.singleEntry, reEntry, addOn, rebuy and fee with status/excerpt/source/retrieved; verify_site.py fails if any is missing.",
     [VL_SHEET_1, VL_SHEET_7]),
    ("R14", 'Schedule overlap check: once finish times are verified, flag any two events that cannot be played in sequence.',
     "done (limited by official evidence)", ["schedule.html", "flagged.html"],
     "Overlap flags are computed and published, but no venue publishes a finish time, so every flag is explicitly labelled an estimate (F16). The strict version cannot be claimed until a finish time is official.",
     [VL_SHEET_7, VL_SCHED]),
    ("R15", 'Walking-route check: official-address walking times for each hotel–venue pair, with the 30-minute limit applied.',
     "done", ["hotels.html", "venues.html"],
     "56 routes carry mapsOrigin/mapsDestination, a Google Maps walking URL, minutes and lastChecked; WALK_LIMIT_MIN = 30 is applied in the tournament and hotel filters. Walking minutes are labelled as estimates, not venue-published values.",
     [VL_PARKING, WYNN_PARKING]),
    ("R16", 'Change monitoring: re-check official pages on a schedule and flag any value that changed.',
     "done", ["sources.html", "flagged.html"],
     "checks.yml + source-monitor.yml; changed hashes become 'Source changed · review' badges and are published, never applied automatically. The 2026-11-19 hand re-read of all 19 trip-window rows found no value changed.",
     [VL_SERIES, WYNN_POKER]),
    ("R17", 'Fix trip dates and nightly budget/quality floor.',
     "done", ["index.html", "hotels.html"],
     "Trip fixed at 23-30 Nov 2026 (7 nights, 7 playable days, 11:00 a.m. checkout on 30 Nov). Floor $197.28 = ($119 + $55) × 1.1338; ceiling $299.32; quality floor is an objective published-evidence test rather than an invented score (F19).",
     [VL_RATES, VL_TERMS]),
    ("R18", 'For candidate events, get official structure sheet and written maximum-entry / no-rebuy / no-add-on rules; remove any not matching single-entry policy.',
     "done (written rule unavailable)", ["tournaments.html", "flagged.html", "questions.html"],
     "All 52 sheets were read and rows with printed extra-entry clauses were moved to flight/extra/satellite categories. No 2026 official page prints a written maximum-entry rule (F31), so the 'single-entry / freezeout confirmed' filter correctly returns zero rows and no booking is recommended.",
     [VL_SCHED, VL_2023]),
    ("R19", 'Compare surviving events on guaranteed pool, buy-in, starting stack/blind duration, payout structure and daily schedule fit.',
     "done", ["schedule.html", "index.html"],
     "The reviewed-candidates table publishes guarantee, total fee, starting chips, level duration (30 min), 12.5% payout and late-registration cut-off for each day's primary. Sheets 1, 6, 7 re-read verbatim 2026-11-19.",
     [VL_SHEET_1, VL_SHEET_7]),
    ("R20", 'Obtain itemized hotel totals for the same stay; check walking route under 30 minutes.',
     "done", ["hotels.html"],
     "The 23-30 Nov quote is itemized night by night (rate + $55 fee, 13.38% tax, checkout total); 56 hotel–venue routes are published with a 30-minute filter. On-site Venetian/Palazzo routes are 0-4 minutes.",
     [VL_BOOK, VL_TERMS]),
    ("R21", 'Build one event per day first; add evening events only where the player can realistically exit the earlier event.',
     "done", ["schedule.html"],
     "One primary candidate per playable day. A fallback is named only when it can be played after the primary; otherwise the row is marked 'Same-day alternative · not a fallback' (F94). No impossible sequence is offered as a plan.",
     [VL_SCHED]),
    ("R22", 'Reconfirm official schedules, rates and policies before nonrefundable payment.',
     "done", ["questions.html", "index.html"],
     "The booking decision on the landing page is HOLD, with the exact re-checks required before payment; Q10 and the questions page list the confirmation steps with official links.",
     [VL_SCHED, VL_BOOK]),
    ("R23", 'Add a live-data feed or scraper that pulls each Strip poker room\'s official daily schedule each morning.',
     "done", ["sources.html"],
     "scripts/daily_feed.py runs in the scheduled job and writes site/feed/index.json plus dated text snapshots; the sources page publishes each room's fetch status. Ten stripRooms are tracked; unavailable rooms are shown as such rather than invented.",
     [WYNN_POKER, VL_SERIES]),
    ("R24", 'Add a "single-entry / freezeout confirmed" toggle filter on the tournaments table.',
     "done", ["tournaments.html"],
     "The checkbox is present. It returns zero rows by design because no written maximum-entry rule exists (F31); the page states this in a notice instead of implying eligibility.",
     [VL_SCHED, VL_2023]),
    ("R25", 'Add live hotel rate lookup (official booking links per date) and auto-calculate true cost/night = rate + resort fee + 13.38% tax.',
     "done", ["hotels.html", "calculator.html"],
     "One official booking deep link per trip night plus the whole stay; trueNightlyLow/High are computed as (rate + $55) × 1.1338 and asserted by tests/test_integrity.py. The 13.38% rate is printed in the Venetian terms and the Clark County schedule.",
     [VL_RATES, VL_TERMS, COUNTY_TAX]),
    ("R26", 'Add walking-distance verification (Google/Apple Maps) from each hotel to the Venetian poker room, with a "≤30 min walk" filter.',
     "done", ["hotels.html", "tournaments.html"],
     "Each route carries a Google Maps walking URL from an official property address to the venue; the 30-minute filter is applied to tournament rows and route lists. Estimates are explicitly not venue-published.",
     [VL_PARKING]),
    ("R27", 'Find live upcoming poker tournaments near the Las Vegas Strip; find the best based on cost to enter and prize pool; focus on single entry only.',
     "done (candidates, not a confirmed winner)", ["tournaments.html", "index.html"],
     "341 rows from seven official rooms are published with buy-in and guarantee; 52 sheet-screened candidates are isolated. No 'best' winner is declared because the written single-entry rule is missing (F31) — ranking a winner would be an inference.",
     [VL_SCHED, WYNN_POKER]),
    ("R28", 'No double buy-in or add-ons and tournaments where you could gain an advantage through spending more money; keep those in a separate section.',
     "done", ["browse.html?view=category&key=extra", "tournaments.html"],
     "The extra-spend category (20 rows) isolates re-entry, rebuy, add-on and paid-chip-boost formats; bounty (41), flight (113) and satellite (48) rows are separately labelled. The 2026-11-19 reads of the Caesars flyer and Bellagio Saturday PDF confirm explicit re-entry, $50 add-on and a paid chip boost.",
     [CAES_FLYER, BELL_SAT]),
    ("R29", 'Figure out the best hotels within walking distance to those tournaments; factor in distance and cost per night along with resort fees; cost and quality higher priority than distance, but within 30 minutes walking.',
     "done (data gaps flagged)", ["hotels.html", "venues.html"],
     "Eight properties publish rate components, fee, tax, parking, cancellation and walking minutes; the quality column stays blank where no official comparable score exists (F19). No ranked 'best hotel' is asserted from incomplete data.",
     [VL_RATES, BELL_TERMS, WYNN_INFO]),
    ("R30", 'Create a tournament schedule where someone could play all day starting at 8 AM; enter as many live tournaments as possible; stay organized.',
     "not supported by official evidence", ["schedule.html", "flagged.html"],
     "The earliest verified start is 9:00 AM (Horseshoe daily) and no official finish time exists (F17/F16). An 8 AM all-day route would be an invention, so it is not built; the seven-day one-primary-per-day plan is published instead.",
     [VL_SCHED, CAES_ARTICLE]),
    ("R31", 'Create an executive summary outlining important details.',
     "done", ["index.html"],
     "The landing page is the executive summary: fixed trip, booking decision HOLD, one candidate per playable day, cost scenario, what would change the decision, and the evidence policy.",
     [VL_SCHED, VL_RATES]),
    ("R32", 'Make suggestions on how to improve the site, in a dedicated section so someone can review and choose the best path before implementing changes.',
     "done", ["suggestions.html"],
     "22 suggestions with impact, effort and the decision each one needs. None is auto-implemented; the page explicitly asks the reader to choose first.",
     [REPO + "site/suggestions.html"]),
    ("R33", 'A clear list of questions, information and answers that need to be addressed before any decision can reasonably be made based on what we have and do not have; suggest how to discover missing information.',
     "done", ["questions.html"],
     "18 questions each carry what is known, the official source behind it, whether it blocks a decision and the step to obtain the missing answer.",
     [REPO + "site/questions.html", VL_SCHED]),
    ("R34", 'No manual input; work line by line, verify everything from official verified trusted sources, no hallucinations.',
     "done", ["verification.html", "sources.html"],
     "This session's dated verification record and the 40-row audit are published; every value is read from an official page, blanks stay blank and every irregularity is flagged. No value was inferred.",
     [REPO + "research/verification_2026-11-19_arena-8194609f.md"]),
    ("R35", 'Review the repo; provide links for manual review; flag any irregularities for review.',
     "done", ["flagged.html", "sources.html"],
     "Every flag links the exact official page or repository file; the repo review found F100 (stale venue pages, fixed) and F101 (unlinked stale snapshot JSON files, published for a decision); main already carries F98 for the orphan conflict markers, so no duplicate flag was added.",
     [REPO + "COORDINATION.md", BELL_POKER]),
    ("R36", 'Create a GitHub Pages live site with a clean landing page and category subpages, simple dashboard UI, all entries and findings in easy-to-read tables, plus analysis.',
     "done", ["index.html", "browse.html", "verification.html"],
     "16+ pages published by .github/workflows/pages.yml from site/; nav, tables, filters and the executive summary are verified by tests/canonical_smoke.py and node tests/canonical_render.js. A local-link scan reports zero broken internal links.",
     [REPO + ".github/workflows/pages.yml"]),
    ("R37", 'Verify line by line: every table row must have a source link to an official site; if a value cannot be confirmed, leave it blank and flag it as unverified; never infer or fill in values.',
     "done", ["verification.html", "flagged.html"],
     "verify_site.py asserts every event/hotel/route row has an official URL, every rule has a source/excerpt/date, and blank fees or guarantees are explained by a note or flag. 89 rows have a blank buy-in or guarantee with a reason.",
     [VL_SCHED, COUNTY_TAX]),
    ("R38", 'Parallel sessions: shared task board, claim before starting, non-overlapping scopes, small frequent commits, pull --rebase before every push, log conflicts.',
     "done", ["repo:COORDINATION.md"],
     "The board lists status, owner and scope; this session claimed before work, pushed the claim immediately, and works only on arena/8194609f-poker3 (the platform binds one branch, so session-<id>/<task> naming cannot be applied). Open PR #173 was left untouched.",
     [REPO + "COORDINATION.md"]),
    ("R39", 'Pull request and merge: PR from the integration branch to main with a summary, sources and flagged irregularities; merge without waiting; confirm Pages deploy; record PR link and result in COORDINATION.md; publish a Flagged for Review page.',
     "done", ["flagged.html", "repo:COORDINATION.md"],
     "The Flagged for review page publishes every flag with its source link. The PR, merge result and Pages deployment are recorded in COORDINATION.md by the integration session before this turn ends.",
     [REPO + "COORDINATION.md"]),
    ("R40", 'If the build, a check or the deploy fails, fix it and retry until the site is live; do not merge a broken site.',
     "done", ["repo:.github/workflows/pages.yml"],
     "pages.yml gates the artifact upload on verify_site.py, four independent audits, the full unit suite, canonical_smoke and several node checks; deploy needs build to succeed. This session ran the same gates locally before opening the PR.",
     [REPO + ".github/workflows/pages.yml"]),
]

def _page(value):
    """A 'where' entry is either a site page or a repository file used as evidence."""
    if value.startswith("repo:"):
        rel = value[5:]
        return dict(label=rel, href=REPO + rel, kind="project file")
    return dict(label=value, href=value, kind="site page")


REQUIREMENTS = [
    dict(id=i, requirement=r, status=s, pages=[_page(x) for x in p], evidence=e,
         sources=[dict(label=("Official source %d" % (n + 1)), url=u,
                       kind=("project file" if u.startswith(REPO) else "official"))
                  for n, u in enumerate(src)],
         checked=CHECKED, session=SESSION)
    for i, r, s, p, e, src in _REQ
]

# --------------------------------------------------------------------------
# Verbatim official reads performed on 2026-11-19 (excerpt subset, all linked).
# --------------------------------------------------------------------------
_READS = [
    ("V01", "Venetian DeepStack Extravaganza IV November schedule", VL_SCHED,
     "November 16 – December 23, 2026 · More than $3.6 Million in guaranteed tournament prize pools",
     "Series dates and all 94 dated rows; re-read 19 trip-window rows line by line", "no value changed"),
    ("V02", "Venetian 2026 poker suite rates", VL_RATES,
     "These rates will start as low as $119 and $209 and can be higher. ... There is a $55 resort fee per night stayed.",
     "$119/$209 starting rates; $55 nightly resort fee; EPOKR25 phone code", "no value changed"),
    ("V03", "Venetian resort fee page", VL_FEE,
     "Rates include a daily Resort Fee of $55 plus tax per night, payable upon check-in.",
     "$55 fee plus tax; wording conflict with hotel terms remains flagged F51", "no value changed"),
    ("V04", "Venetian hotel terms and conditions", VL_TERMS,
     "Daily rates do not include the applicable Clark County Room Tax of 13.38%. ... Check-out time is 11:00 a.m.",
     "13.38% room tax, 11:00 a.m. checkout, $20/$25 parking, $40 valet, deposit and early-checkout terms", "no value changed"),
    ("V05", "Venetian poker-room parking", VL_PARKING,
     "Players in the poker room who play three hours or more in tournament or cash games will receive complimentary self-parking for the day. Players must visit a supervisor at the end of their session to confirm qualifications.",
     "Conditional three-hour parking waiver", "no value changed"),
    ("V06", "Venetian structure sheet 7 ($600 NLH)", VL_SHEET_7,
     "Starting Chips: 40,000 · Level Duration: 30 minutes. · Late Registration: 10 levels + Break (~ 4:55 PM) · Guarantee: $30,000 for Event #14 and #63 · $90 of the $600 Buy-In is withheld for house fees",
     "Nov 27 primary: $600, $30K, 40,000 chips, 12.5% paid, 4:55 PM registration close", "no value changed"),
    ("V07", "Venetian structure sheet 6 ($400 NLH)", "https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_6.pdf",
     "Event Number: 10 · Guarantee: $15,000 · $65 of the $400 Buy-In is withheld for house fees (Rake + Staff).",
     "Nov 25 primary: $400, $15K, 40,000 chips, 30-minute levels", "no value changed"),
    ("V08", "Venetian structure sheet 1 ($200 bounty)", VL_SHEET_1,
     "Guarantee: $8,000 (prize pool + total bounties) · Late Registration: 8 levels + Break (9:40 PM) · A Prize Pool of $8,000 is guaranteed ... which consists of the actual prize pool plus the total amount of $50 bounties",
     "Evening bounty rows are bounty-inclusive, not a cash-only pool", "no value changed"),
    ("V09", "Venetian DeepStack Extravaganza II (April 2023)", VL_2023,
     "One Entry Only with One Hour of Registration (Event 13)",
     "The venue does print a one-entry label when it intends one; the 2026 series prints none, so F31 stays open", "no value changed"),
    ("V10", "Wynn poker room", WYNN_POKER,
     "WPT WORLD CHAMPIONSHIP · November 27–December 21 · New for 2026, the Super Gold Million brings a $400 buy-in featuring a $3,000,000 guarantee!",
     "WPT window, $400/$3M event, Friday $40K rebuy kept in the extra-spend section", "no value changed"),
    ("V11", "Wynn resort policies and information", WYNN_INFO,
     "Reservations will be charged a daily resort fee of $55 plus tax. · Check In: 3 p.m. · Check Out: 12 p.m.",
     "$55 Wynn resort fee and check-in/out times", "no value changed"),
    ("V12", "Wynn parking information", WYNN_PARKING,
     "The daily parking fee for non-registered guests is $25 per day with the first three (3) hours complimentary. · Complimentary self-parking is extended to Wynn Poker Room guests (please visit the Poker Room for details)",
     "Wynn parking figures and the poker-room waiver", "no value changed"),
    ("V13", "Bellagio hotel reservation terms", BELL_TERMS,
     "A daily resort fee of $55.00 plus applicable tax will be applied to all reservations. · The first night's deposit is fully refundable provided a timely notice of cancellation is received ... at least 72 hours prior to the arrival date",
     "$55 fee and 72-hour cancellation deadline", "no value changed"),
    ("V14", "Bellagio poker page", BELL_POKER,
     "SATURDAYS | $1,000 NLH · Tournament play will resume on Saturday, July 26, beginning with the $300 PLO Double Board Bomb Pot Tournament at 2 PM PT.",
     "Source of the $1,000 link label in conflict F02; undated July 26 notice stays flagged F03", "no value changed"),
    ("V15", "Bellagio Saturday NLH structure PDF", BELL_SAT,
     "NLH $1100 BUY-IN · Of the $600 Buy-in, $510 goes to the Prize Pool, $50 is Admin Fees and $40 is optional staff gratuity. · Players start with 40,000 in tournament chips (20,000 + 20,000 optional)",
     "Three conflicting buy-ins and a paid chip boost; field stays blank and flagged", "no value changed"),
    ("V16", "Caesars Palace / Horseshoe Strip poker article", CAES_ARTICLE,
     "Every event carries a $100 buy-in, starts you with 20,000 chips, and features a $1,000 guaranteed prize pool. ... a $50 add-on at the first break gives you an extra 15,000 chips",
     "Article's uniform $100 claim and $50 add-on (conflict F90)", "no value changed"),
    ("V17", "Caesars Palace daily NLH flyer 2026", CAES_FLYER,
     "10 AM | $100 | 2 PM | $160 | 6 PM | $100 | 9 PM | $160 · Participants may only register themselves, but may re-enter, by paying the entry fee, upon elimination within the first break of play.",
     "$160 buy-ins, explicit re-entry and a $50 add-on; excluded from single-entry path", "no value changed"),
    ("V18", "Clark County transient lodging guide, Appendix III", COUNTY_TAX,
     "13.38% | RES | 1 | Transient Lodging Tax - Resort Hotel (PGC)",
     "13.38% resort-hotel tax in the Primary Gaming Corridor corroborates the Venetian terms", "no value changed"),
]

OFFICIAL_READS = [
    dict(id=i, title=t, url=u, excerpt=x, value=v, checked=CHECKED, result=res)
    for i, t, u, x, v, res in _READS
]

# --------------------------------------------------------------------------
# The 19 official rows inside the fixed trip window, compared line by line.
# --------------------------------------------------------------------------
_ROWS = [
    ("2026-11-23", "11:10 AM", "7", "$400 No Limit Hold'em 1A $75K GTD", 400, 75000, "structure_2.pdf", "vl-dse-2026-11-23-7-1110am"),
    ("2026-11-23", "5:10 PM", "8", "$200 No Limit Hold'em $8K GTD (1Day) PKO", 200, 8000, "structure_30.pdf", "vl-dse-2026-11-23-8-510pm"),
    ("2026-11-24", "11:10 AM", "7", "$400 No Limit Hold'em 1B $75K GTD", 400, 75000, "structure_2.pdf", "vl-dse-2026-11-24-7-1110am"),
    ("2026-11-24", "5:10 PM", "9", "$200 No Limit Hold'em Bounty $8K GTD (1Day)", 200, 8000, "structure_1.pdf", "vl-dse-2026-11-24-9-510pm"),
    ("2026-11-25", "11:00 AM", "7", "$400 No Limit Hold'em Day 2 Restart", 400, 75000, "structure_2.pdf", "vl-dse-2026-11-25-7-1100am"),
    ("2026-11-25", "11:10 AM", "10", "$400 No Limit Hold'em $15K GTD (1Day)", 400, 15000, "structure_6.pdf", "vl-dse-2026-11-25-10-1110am"),
    ("2026-11-25", "5:10 PM", "11", "$200 No Limit Hold'em Bounty $8K GTD (1Day)", 200, 8000, "structure_1.pdf", "vl-dse-2026-11-25-11-510pm"),
    ("2026-11-26", "11:10 AM", "12", "$300 No Limit Hold'em $10K GTD (1Day)", 300, 10000, "structure_5.pdf", "vl-dse-2026-11-26-12-1110am"),
    ("2026-11-26", "5:10 PM", "13", "$200 No Limit Hold'em Bounty $8K GTD (1Day)", 200, 8000, "structure_1.pdf", "vl-dse-2026-11-26-13-510pm"),
    ("2026-11-27", "11:10 AM", "14", "$600 No Limit Hold'em $30K GTD (1Day)", 600, 30000, "structure_7.pdf", "vl-dse-2026-11-27-14-1110am"),
    ("2026-11-27", "5:10 PM", "15", "$200 No Limit Hold'em Bounty $8K GTD (1Day)", 200, 8000, "structure_1.pdf", "vl-dse-2026-11-27-15-510pm"),
    ("2026-11-28", "11:10 AM", "16", "$600 No Limit Hold'em Bounty $30K GTD (1Day)", 600, 30000, "structure_11.pdf", "vl-dse-2026-11-28-16-1110am"),
    ("2026-11-28", "12:10 PM", "17", "$400 Pot Limit Omaha Bounty $15K GTD (1Day)", 400, 15000, "structure_26.pdf", "vl-dse-2026-11-28-17-1210pm"),
    ("2026-11-28", "5:10 PM", "18", "$200 NLH PokerAtlas Valuetown Bounty $20K GTD (1Day)", 200, 20000, "structure_8.pdf", "vl-dse-2026-11-28-18-510pm"),
    ("2026-11-29", "11:10 AM", "19", "$400 No Limit Hold'em 1A $75K GTD", 400, 75000, "structure_3.pdf", "vl-dse-2026-11-29-19-1110am"),
    ("2026-11-29", "12:10 PM", "20", "$300 Pot Limit Omaha $10K GTD (1Day) Double Board Bomb Pot", 300, 10000, "structure_22.pdf", "vl-dse-2026-11-29-20-1210pm"),
    ("2026-11-29", "5:10 PM", "21", "$200 No Limit Hold'em Bounty $8K GTD (1Day)", 200, 8000, "structure_1.pdf", "vl-dse-2026-11-29-21-510pm"),
    ("2026-11-30", "11:10 AM", "19", "$400 No Limit Hold'em 1B $75K GTD", 400, 75000, "structure_3.pdf", "vl-dse-2026-11-30-19-1110am"),
    ("2026-11-30", "5:10 PM", "22", "$200 No Limit Hold'em Bounty $8K GTD (1Day)", 200, 8000, "structure_1.pdf", "vl-dse-2026-11-30-22-510pm"),
]

TRIP_ROWS = [
    dict(date=d, time=t, eventNumber=n, name=name, buyIn=b, guarantee=g,
         sheet=s, rowId=rid, result="date, start time, event number, buy-in, guarantee and sheet all match the live official page",
         source=VL_SCHED, checked=CHECKED)
    for d, t, n, name, b, g, s, rid in _ROWS
]

# --------------------------------------------------------------------------
# New flags: repository irregularities found by this session's repo review.
# --------------------------------------------------------------------------
NEW_FLAGS = [
    dict(id="F101", area="Publishing", severity="Low",
         title=("Five unlinked 2026-11-16 snapshot JSON files are still published under site/data/ (flagged for review)"),
         detail=("The Pages artifact publishes the whole site/ directory, so site/data/flags.json, questions.json, "
                 "sources.json, suggestions.json and tournaments.json are reachable at the live host. Each carries "
                 "meta.asOf 2026-11-16 and builtAt 2026-11-16T19:50:18Z and is not read by any dashboard page or "
                 "script (the live data is site/data.json; scripts/daily_check.py still names sources.json but is not "
                 "the scheduled checker, which is scripts/check_sources.py). Their contents therefore give a second, "
                 "stale answer to anyone who opens them directly. F68 removed three other stale snapshots for the same "
                 "reason. These five are left in place rather than deleted because another session's script still names "
                 "one of them; the integration owner should either retire them or add a dated note. No value was taken "
                 "from any stale snapshot: every published table row is rendered from site/data.json."),
         source=REPO + "site/data/flags.json"),
    dict(id="F100", area="Site consistency", severity="Low",
         title=("Four legacy venue subpages published stale hardcoded claims that contradicted the canonical dataset "
                "(found and fixed 2026-11-19)"),
         detail=("site/venues/index.html said 'the NYE rows stay unverified' although all 52 official structure sheets "
                 "were read and zero published rows carry the unverified category. site/venues/venetian.html said "
                 "'no date-specific room quote exists in the reviewed sources' and called the 2026-11-16 $1,245.48 "
                 "two-night quote 'the only dated checkout total found', although the dated rate log also holds "
                 "$1,015.89 for the same two nights (17 Nov), $4,010.55 for 23-30 Nov at the Venetian and $3,823.46 "
                 "for the same window at the Palazzo (17 Nov). site/venues/wynn.html repeated the 'no quote exists' "
                 "claim although the official Wynn reservations engine printed a dated 23-30 Nov 2026 quote on "
                 "2026-11-19. All four pages carried footers or side notes dated 2026-11-16. The four pages were "
                 "corrected to match site/data.json, dated 2026-11-19 and given official source links; "
                 "tests/test_verification_audit.py fails if the stale phrases return. No tournament, fee, guarantee, "
                 "hotel, rate, route or policy value was inferred or changed. Flag ids F97-F99 were already taken on "
                 "main by parallel sessions by the time this branch rebased, so this flag is F100."),
         source=VL_RATES),
]

__all__ = ["REQUIREMENTS", "OFFICIAL_READS", "TRIP_ROWS", "NEW_FLAGS", "CHECKED", "SESSION"]
