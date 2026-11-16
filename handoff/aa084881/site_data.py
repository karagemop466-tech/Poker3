"""Source data for the consolidated Las Vegas poker-trip site (session aa084881).

Rules:
- A value is recorded only when an official page or PDF was read for it (see `source`).
- Unknown values are None (rendered blank) and carry a flag ID from FLAGS.
- Derived numbers (ratios, true nightly cost, schedule order) are computed in build_site.py and labelled there.
Checked: 2026-11-16 (Las Vegas date).
"""

CHECKED = "2026-11-16"

# ---- Official URLs (every one was read or linked from an official page on CHECKED) ----
DSE_PAGE = "https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html"
DSE_SERIES = "https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament.html"
SHEET = "https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_{}.pdf"
VEN_SUITE = "https://www.venetianlasvegas.com/resort/casino/poker/suite-rates.html"
VEN_FEE = "https://www.venetianlasvegas.com/resort/resort-fee.html"
VEN_TERMS = "https://www.venetianlasvegas.com/legal/hotel-terms-and-conditions.html"
VEN_QUOTE = "https://www.venetianlasvegas.com/booking?adults[]=2&arrival_date=2026-11-17&children[]=0&departure_date=2026-11-19&view=calendar"
VEN_CAL_DEC = "https://www.venetianlasvegas.com/booking?adults[]=2&arrival_date=2026-12-10&children[]=0&departure_date=2026-12-12&view=calendar"
WYNN_POKER = "https://www.wynnlasvegas.com/casino/poker"
WYNN_SCHED = "https://cdn.wynnresorts.com/image/upload/v1757097329/visitwynn_pdfs_files/Poker/WPT/WPT_World_Championship_Schedule.pdf"
WYNN_STRUCT = "https://cdn.wynnresorts.com/image/upload/v1750864036/visitwynn_pdfs_files/Poker/WPT/WPT_World_Championship_Structures.pdf"
WYNN_POSTER = "https://cdn.wynnresorts.com/image/upload/v1752011166/visitwynn_pdfs_files/Poker/Daily%20Tournaments/poker-daily-tournament-poster.pdf"
WYNN_DAILY_STRUCT = "https://cdn.wynnresorts.com/image/upload/v1752011191/visitwynn_pdfs_files/Poker/Daily%20Tournaments/Poker-All_Daily_Structures.pdf"
WYNN_TERMS = "https://www.wynnlasvegas.com/terms-and-conditions/850070"
BEL_POKER = "https://bellagio.mgmresorts.com/en/casino/poker.html"
BEL_FRI = "https://assets.contentstack.io/v3/assets/bltc6ce635bc4868eb2/blt9cf95b0e60ec253e/6af491a3a9851d75c40be840/mgm-bellagio-poker-fridays-$600-nlh.pdf"
BEL_SAT = "https://assets.contentstack.io/v3/assets/bltc6ce635bc4868eb2/blt6d47974bf5a7d9b6/6af491a391a6e8e4230c9e07/mgm-bellagio-poker-saturdays-$1000-nlh.pdf"
BEL_SUN = "https://assets.contentstack.io/v3/assets/bltc6ce635bc4868eb2/blt07fcf1244a6da661/6af491a339e2b4f6b76a86ad/mgm-bellagio-poker-sundays-$400-horse.pdf"
ARIA_POKER = "https://aria.mgmresorts.com/en/casino/poker.html"
CAESARS_PAGE = "https://www.caesars.com/caesars-palace/things-to-do/poker"
MGM_PAGE = "https://mgmgrand.com/en/casino/poker.html"
GN_PAGE = "https://www.goldennugget.com/las-vegas/casino/poker"
RW_PAGE = "https://www.rwlasvegas.com/casino/poker"
CIRCA_PAGE = "https://www.circalasvegas.com/casino/poker"

# ---- Venetian DeepStack Extravaganza IV (official table, read in full on CHECKED) ----
# Each row: (event, date ISO, weekday, time as printed, name as printed, buy-in, guarantee, sheet, late-reg, house fee, pool)
# Sheet fee/pool values are from structure sheets read on CHECKED (see flags F05/F09 for the unprinted ones).
DSE_MAIN = [
    ("2", "2026-11-18", "Wednesday", "11:10 AM", "$300 No Limit Hold'em $10K GTD (1Day)", 300, 10000, 5, None, 58, 242),
    ("6", "2026-11-22", "Sunday", "11:10 AM", "$200 No Limit Hold'em (1Day)", 200, None, 29, None, 40, 160),
    ("10", "2026-11-25", "Wednesday", "11:10 AM", "$400 No Limit Hold'em $15K GTD (1Day)", 400, 15000, 6, None, 65, 335),
    ("12", "2026-11-26", "Thursday", "11:10 AM", "$300 No Limit Hold'em $10K GTD (1Day)", 300, 10000, 5, None, 58, 242),
    ("14", "2026-11-27", "Friday", "11:10 AM", "$600 No Limit Hold'em $30K GTD (1Day)", 600, 30000, 7, None, 90, 510),
    ("20", "2026-11-29", "Sunday", "12:10 PM", "$300 Pot Limit Omaha $10K GTD (1Day) - Double Board Bomb Pot", 300, 10000, 22, None, 58, 242),
    ("24", "2026-12-02", "Wednesday", "10:10 AM", "$600 No Limit Hold'em Seniors $40K GTD (1Day) - must be 50+", 600, 40000, 17, None, 90, 510),
    ("27", "2026-12-03", "Thursday", "12:10 PM", "$600 BIG O $25K GTD (1Day)", 600, 25000, 28, None, 90, 510),
    ("28", "2026-12-06", "Sunday", "11:10 AM", "$600 No Limit Hold'em $40K GTD (1Day)", 600, 40000, 7, None, 90, 510),
    ("32", "2026-12-08", "Tuesday", "10:10 AM", "$600 No Limit Hold'em Seniors $40K GTD (1Day) - must be 50+", 600, 40000, 17, None, 90, 510),
    ("57", "2026-12-17", "Thursday", "12:10 PM", "$600 Pot Limit Omaha $25K GTD (1Day) - Double Board Bomb Pot", 600, 25000, 23, None, 90, 510),
    ("63", "2026-12-23", "Wednesday", "11:10 AM", "$600 No Limit Hold'em $30K GTD (1Day)", 600, 30000, 7, None, 90, 510),
]
# Bounty / knockout events, single start (kept out of the freezeout list as requested)
DSE_BOUNTY = [
    ("8", "2026-11-23", "Monday", "5:10 PM", "$200 No Limit Hold'em $8K GTD (1Day) - Progressive Knock-Out Bounty (PKO)", 200, 8000, 30, None, 40, 160, "PKO, $50 starting bounty (sheet 30)", []),
    ("9", "2026-11-24", "Tuesday", "5:10 PM", "$200 No Limit Hold'em Bounty $8K GTD (1Day)", 200, 8000, 1, "9:40 PM", 40, 160, "$50 bounty (sheet 1)", []),
    ("11", "2026-11-25", "Wednesday", "5:10 PM", "$200 No Limit Hold'em Bounty $8K GTD (1Day)", 200, 8000, 1, "9:40 PM", 40, 160, "$50 bounty (sheet 1)", []),
    ("13", "2026-11-26", "Thursday", "5:10 PM", "$200 No Limit Hold'em Bounty $8K GTD (1Day)", 200, 8000, 1, "9:40 PM", 40, 160, "$50 bounty (sheet 1)", []),
    ("15", "2026-11-27", "Friday", "5:10 PM", "$200 No Limit Hold'em Bounty $8K GTD (1Day)", 200, 8000, 1, "9:40 PM", 40, 160, "$50 bounty (sheet 1)", []),
    ("16", "2026-11-28", "Saturday", "11:10 AM", "$600 No Limit Hold'em Bounty $30K GTD (1Day) - $200 bounties to start, $500 in the money", 600, 30000, 11, None, 90, 510, "$200 rising to $500 (sheet 11)", []),
    ("17", "2026-11-28", "Saturday", "12:10 PM", "$400 Pot Limit Omaha Bounty $15K GTD (1Day)", 400, 15000, 26, None, 60, 340, "$100 bounty (sheet 26)", []),
    ("18", "2026-11-28", "Saturday", "5:10 PM", "$200 No Limit Hold'em PokerAtlas Valuetown Bounty $20K GTD (1Day) - PokerAtlas PRO member $20 rake discount", 200, 20000, 8, "9:40 PM", 40, 160, "$50 bounty (sheet 8)", ["F13", "F14"]),
    ("21", "2026-11-29", "Sunday", "5:10 PM", "$200 No Limit Hold'em Bounty $8K GTD (1Day)", 200, 8000, 1, "9:40 PM", 40, 160, "$50 bounty (sheet 1)", []),
    ("22", "2026-11-30", "Monday", "5:10 PM", "$200 No Limit Hold'em Bounty $8K GTD (1Day)", 200, 8000, 1, "9:40 PM", 40, 160, "$50 bounty (sheet 1)", []),
    ("23", "2026-12-01", "Tuesday", "5:10 PM", "$200 No Limit Hold'em Bounty $8K GTD (1Day)", 200, 8000, 1, "9:40 PM", 40, 160, "$50 bounty (sheet 1)", []),
    ("25", "2026-12-02", "Wednesday", "5:10 PM", "$200 No Limit Hold'em Bounty $8K GTD (1Day)", 200, 8000, 1, "9:40 PM", 40, 160, "$50 bounty (sheet 1)", []),
    ("29", "2026-12-06", "Sunday", "5:10 PM", "$300 No Limit Hold'em Bounty $15K GTD (1Day)", 300, 15000, 15, None, 50, 250, "$100 bounty (sheet 15)", []),
    ("30", "2026-12-07", "Monday", "11:10 AM", "$600 No Limit Hold'em Bounty $40K GTD (1Day) - $200 bounties to start, $500 in the money", 600, 40000, 11, None, 90, 510, "$200 rising to $500 (sheet 11)", []),
    ("31", "2026-12-07", "Monday", "5:10 PM", "$300 No Limit Hold'em Bounty $15K GTD (1Day)", 300, 15000, 15, None, 50, 250, "$100 bounty (sheet 15)", []),
    ("34", "2026-12-08", "Tuesday", "5:10 PM", "$300 No Limit Hold'em Bounty $15K GTD (1Day)", 300, 15000, 15, None, 50, 250, "$100 bounty (sheet 15)", []),
    ("36", "2026-12-09", "Wednesday", "11:10 AM", "$800 No Limit Hold'em Bounty $75K GTD (1Day) - $200 bounties to start, $500 in the money", 800, 75000, 16, None, 100, 700, "$200 rising to $500 (sheet 16)", []),
    ("38", "2026-12-09", "Wednesday", "5:10 PM", "$300 No Limit Hold'em Bounty $15K GTD (1Day)", 300, 15000, 15, None, 50, 250, "$100 bounty (sheet 15)", []),
    ("40", "2026-12-10", "Thursday", "12:10 PM", "$600 Pot Limit Omaha Bounty $25K GTD (1Day)", 600, 25000, 27, None, 90, 510, "$200 bounty (sheet 27)", []),
    ("42", "2026-12-10", "Thursday", "5:10 PM", "$300 No Limit Hold'em Bounty $15K GTD (1Day)", 300, 15000, 15, None, 50, 250, "$100 bounty (sheet 15)", []),
    ("43", "2026-12-11", "Friday", "11:10 AM", "$600 No Limit Hold'em LIPS Kings and Queens Bounty $30K GTD (1Day) - open to all players", 600, 30000, 33, None, 80, 510, "$200 bounty; $80 fee + $10 LIPS inside the $600 (sheet 33)", ["F15"]),
    ("50", "2026-12-13", "Sunday", "5:10 PM", "$300 No Limit Hold'em Bounty $15K GTD (1Day)", 300, 15000, 15, None, 50, 250, "$100 bounty (sheet 15)", []),
    ("51", "2026-12-14", "Monday", "5:10 PM", "$300 No Limit Hold'em Bounty $15K GTD (1Day)", 300, 15000, 15, None, 50, 250, "$100 bounty (sheet 15)", []),
    ("52", "2026-12-15", "Tuesday", "11:10 AM", "$1,100 No Limit Hold'em $75K GTD (1Day) - Progressive Knock-Out Bounty (PKO)", 1100, 75000, 34, None, 130, 970, "PKO, $200 starting bounty (sheet 34)", []),
    ("53", "2026-12-15", "Tuesday", "5:10 PM", "$300 No Limit Hold'em Bounty $15K GTD (1Day)", 300, 15000, 15, None, 50, 250, "$100 bounty (sheet 15)", []),
    ("54", "2026-12-16", "Wednesday", "11:10 AM", "$600 No Limit Hold'em Bounty $50K GTD (1Day) - $200 bounties to start, $500 in the money", 600, 50000, 11, None, 90, 510, "$200 rising to $500 (sheet 11)", []),
    ("55", "2026-12-16", "Wednesday", "5:10 PM", "$300 No Limit Hold'em Bounty $15K GTD (1Day)", 300, 15000, 15, None, 50, 250, "$100 bounty (sheet 15)", []),
    ("58", "2026-12-19", "Saturday", "5:10 PM", "$200 No Limit Hold'em PokerAtlas Valuetown Bounty $20K GTD (1Day) - PokerAtlas PRO member $20 rake discount", 200, 20000, 8, "9:40 PM", 40, 160, "$50 bounty (sheet 8)", ["F13", "F14"]),
    ("60", "2026-12-20", "Sunday", "5:10 PM", "$200 No Limit Hold'em Bounty $8K GTD (1Day)", 200, 8000, 1, "9:40 PM", 40, 160, "$50 bounty (sheet 1)", []),
    ("61", "2026-12-21", "Monday", "5:10 PM", "$200 No Limit Hold'em Bounty $8K GTD (1Day)", 200, 8000, 1, "9:40 PM", 40, 160, "$50 bounty (sheet 1)", []),
    ("62", "2026-12-22", "Tuesday", "5:10 PM", "$200 No Limit Hold'em Bounty $8K GTD (1Day)", 200, 8000, 1, "9:40 PM", 40, 160, "$50 bounty (sheet 1)", []),
    ("64", "2026-12-23", "Wednesday", "5:10 PM", "$200 No Limit Hold'em Bounty $8K GTD (1Day)", 200, 8000, 1, "9:40 PM", 40, 160, "$50 bounty (sheet 1)", []),
]
# Format not clear from the printed title and sheet (RaceDay). No guarantee printed. Not in schedule primary/fallback.
DSE_UNCLEAR = [
    ("3", "2026-11-19", "Thursday", "10:10 AM", "$200 No Limit Hold'em RaceDay Stack (1Day) - race to finish before the Race", 200, None, 18, None, 35, 165),
    ("4", "2026-11-20", "Friday", "10:10 AM", "$200 No Limit Hold'em RaceDay Stack (1Day) - race to finish before the Race", 200, None, 18, None, 35, 165),
    ("5", "2026-11-21", "Saturday", "10:10 AM", "$200 No Limit Hold'em RaceDay Stack (1Day) - race to finish before the Race", 200, None, 18, None, 35, 165),
]
# Flight, restart, team, satellite and two-day rows. Dates are the first and last date printed for that event number.
# (event, first date, last date, times printed, name, reason, flags)
DSE_EXCLUDED = [
    ("1", "2026-11-16", "2026-11-18", "11:10 AM, 5:10 PM (flights 1A-1D); Day 2 Restart 12:00 PM Nov 18", "$300 No Limit Hold'em $75K GTD (flights 1A-1D + restart)", "Multi-flight: several entries and a restart", ["F02"]),
    ("7", "2026-11-23", "2026-11-25", "11:10 AM (1A, 1B); Day 2 Restart 11:00 AM Nov 25", "$400 No Limit Hold'em $75K GTD (flights 1A-1B + restart)", "Multi-flight: several entries and a restart", ["F02"]),
    ("19", "2026-11-29", "2026-12-02", "11:10 AM (1A-1C); Day 2 Restart 11:00 AM Dec 2", "$400 No Limit Hold'em $75K GTD (flights 1A-1C + restart)", "Multi-flight: several entries and a restart", ["F02"]),
    ("26", "2026-12-03", "2026-12-06", "11:10 AM, 5:10 PM (flights 1A-1F); Day 2 Restart 12:00 PM Dec 6", "$800 No Limit Hold'em $500K GTD (flights 1A-1F + restart)", "Multi-flight: several entries and a restart", ["F02"]),
    ("35", "2026-12-09", "2026-12-09", "10:10 AM", "$600 NLH LIPS Poker Jingle Tag Team $10K GTD", "Tag-team entry (Female/Female or Female/Male)", []),
    ("39", "2026-12-10", "2026-12-11", "10:10 AM (2-day); Day 2 Restart 10:00 AM Dec 11; Final Table 7:00 PM Dec 11", "$800 No Limit Hold'em LIPS Ladies $40K GTD (2-day)", "Two-day event with restart; streamed final", ["F02"]),
    ("47", "2026-12-12", "2026-12-14", "10:10 AM (1A), 6:10 PM (1B); restarts 1:00 PM Dec 13 and 11:00 AM Dec 14", "$2,200 No Limit Hold'em $1 Mill GTD (flights 1A-1B + restarts)", "Multi-flight: several entries and restarts", ["F02"]),
    ("49", "2026-12-13", "2026-12-15", "10:10 AM (1A, 1B); Day 2 Restart 10:00 AM Dec 15", "$1,100 No Limit Hold'em Seniors $300K GTD (flights 1A-1B + restart)", "Multi-flight; 50+ only", ["F02", "F05"]),
    ("56", "2026-12-17", "2026-12-20", "10:10 AM, 6:10 PM (flights 1A-1E); Day 2 Restart 11:00 AM Dec 20", "$1,100 No Limit Hold'em $500K GTD (flights 1A-1E + restart)", "Multi-flight: several entries and a restart; rake discount for early entries", ["F02", "F07"]),
    ("59", "2026-12-20", "2026-12-23", "11:10 AM (1A-1C); Day 2 Restart 11:00 AM Dec 23", "$600 No Limit Hold'em $150K GTD (flights 1A-1C + restart)", "Multi-flight: several entries and a restart; rake discount for early entries", ["F02", "F07"]),
    ("33", "2026-12-08", "2026-12-08", "4:10 PM", "$100 NLH LIPS Ladies Milestone Satellite", "Satellite (awards direct entry to #39)", []),
    ("37", "2026-12-09", "2026-12-09", "4:10 PM", "$100 NLH LIPS Ladies Milestone Satellite", "Satellite (awards direct entry to #39)", []),
    ("41", "2026-12-10", "2026-12-10", "4:10 PM", "$260 NLH Milestone Satellite", "Satellite (awards direct entry to #47)", []),
    ("44", "2026-12-11", "2026-12-11", "4:10 PM", "$260 NLH Milestone Satellite", "Satellite (awards direct entry to #47)", []),
    ("45", "2026-12-11", "2026-12-11", "8:10 PM", "$260 NLH Turbo Milestone Satellite", "Satellite (awards direct entry to #47)", []),
    ("46", "2026-12-12", "2026-12-12", "9:10 AM", "$260 NLH Turbo Milestone Satellite", "Satellite (awards direct entry to #47)", []),
    ("48", "2026-12-12", "2026-12-12", "12:10 PM", "$260 NLH Turbo Milestone Satellite", "Satellite (awards direct entry to #47)", []),
]

# ---- Venetian structure-sheet values used above (as read on CHECKED) ----
# (sheet, buy-in, guarantee, house fee, pool, bounty or notes)
SHEETS_READ = {
    1: "$200 NLH Bounty, GTD $8K, fee $40, pool $160, $50 bounty",
    5: "$300 NLH, GTD $10K, fee $58, pool $242",
    6: "$400 NLH, GTD $15K, fee $65, pool $335",
    7: "$600 NLH, GTD $30K (events 14, 63) and $40K (event 28), fee $90, pool $510",
    8: "$200 NLH Valuetown Bounty, GTD $20K, fee $40, pool $160, $50 bounty; PokerAtlas PRO wording (see F13)",
    11: "$600 NLH Bounty, GTD $30K/$40K/$50K (events 16/30/54), fee $90, pool $510, $200 bounty rising to $500",
    15: "$300 NLH Bounty, GTD $15K, fee $50, pool $250, $100 bounty",
    16: "$800 NLH Bounty, GTD $75K, fee $100, pool $700, $200 bounty rising to $500",
    17: "$600 NLH Seniors 50+, GTD $40K, fee $90, pool $510",
    18: "$200 NLH RaceDay Stack, no GTD printed, fee $35, pool $165",
    22: "$300 PLO Double Board Bomb Pot, GTD $10K, fee $58, pool $242, eight-handed",
    23: "$600 PLO Double Board Bomb Pot, GTD $25K, fee $90, pool $510, eight-handed",
    26: "$400 PLO Bounty, GTD $15K, fee $60, pool $340, $100 bounty, eight-handed",
    27: "$600 PLO Bounty, GTD $25K, fee $90, pool $510, $200 bounty, eight-handed",
    28: "$600 BIG O (1Day), GTD $25K, fee $90, pool $510, eight-handed; 21+ and Venetian Rewards card",
    29: "$200 NLH (1Day), no GTD printed, fee $40, pool $160",
    30: "$200 NLH PKO, GTD $8K, fee $40, pool $160, $50 bounty start",
    33: "$600 NLH LIPS Kings and Queens Bounty, GTD $30K, fee $80 + $10 LIPS, pool $510, $200 bounty",
    34: "$1,100 NLH PKO, GTD $75K, fee $130, pool $970, $200 bounty start",
}

# ---- Other official rooms ----
WYNN_WPT = [
    # (window as printed, event, buy-in, guarantee, notes, source)
    ("Nov 27-29, 2026", "$600 NLH Day 1 flights", 600, 400000, "Multi-flight (Day 1A-1F); format not reviewed", WYNN_SCHED),
    ("Nov 30-Dec 2, 2026", "$800 NLH Day 1 flights", 800, 1000000, "Multi-flight; format not reviewed", WYNN_SCHED),
    ("Dec 3-4, 2026", "$1,600 NLH Day 1 flights", 1600, 1000000, "Multi-flight; format not reviewed", WYNN_SCHED),
    ("Dec 5-12, 2026", "$1,100 NLH Day 2 / WPT Prime Championship", 1100, 5000000, "Multi-day; format not reviewed", WYNN_SCHED),
    ("Dec 13-15, 2026", "$10,400 WPT World Championship Day 1A/1B/1C", 10400, None, "$1M added by ClubWPT Gold, not available in Nevada (guarantee not confirmed on sheet)", WYNN_SCHED),
    ("Dec 10-12, 2026", "Super Gold Million $400 Mystery Bounty", 400, 3000000, "Bounty; labelled separately", WYNN_POKER),
    ("Dec 17-18, 2026", "$3,000 NLH Day 1A/1B", 3000, 2000000, "Multi-flight; format not reviewed", WYNN_SCHED),
    ("Dec 17, 2026", "$25,800 NLH High Roller (2 Day)", 25800, None, "Two-day; guarantee not confirmed", WYNN_SCHED),
    ("Dec 17-18, 2026", "$1,100 NLH Day 1A/1B", 1100, 1000000, "Multi-flight; format not reviewed", WYNN_SCHED),
    ("Dec 18, 2026", "$600 NLH", 600, 100000, "Date printed as 'Dec. 18'; see F19", WYNN_SCHED),
    ("Dec 18-20, 2026", "$10,500 six-max / PLO / 8-max", 10500, None, "Format not reviewed", WYNN_SCHED),
    ("Dec 20, 2026", "$600 NLH Turbo", 600, 50000, "Turbo; format not reviewed", WYNN_SCHED),
]
WYNN_DAILY = [
    ("Monday-Thursday", "12 p.m.", "Daily NLH $200", 200, 10000, "Undated recurring poster; rules not reviewed", WYNN_POSTER),
    ("Friday", "12 p.m.", "Daily NLH REBUY $240", 240, 40000, "Rebuy: excluded from the single-entry list", WYNN_POSTER),
    ("Saturday", "12 p.m.", "Daily NLH $200", 200, 25000, "Undated recurring poster; rules not reviewed", WYNN_POSTER),
    ("Sunday", "12 p.m.", "Daily NLH $200", 200, 25000, "Undated recurring poster; rules not reviewed", WYNN_POSTER),
    ("Nightly", "6 p.m.", "NLH $160", 160, 10000, "Undated recurring poster; rules not reviewed", WYNN_POSTER),
]
BELLAGIO = [
    # (day, time, buy-in per page, buy-in per PDF, guarantee, status, source, flags)
    ("Friday", "11:00 a.m.", 600, 600, None, "Excluded: re-entry allowed through level 8; $40 gratuity buys extra chips", BEL_FRI, ["F20"]),
    ("Saturday", "11:00 a.m.", 1000, 1100, None, "Excluded: multi-flight (1A-1D) plus combined Day 2; buy-in conflict", BEL_SAT, ["F19", "F21"]),
    ("Sunday", "not confirmed", 400, None, None, "Excluded until the structure is read; H.O.R.S.E. format", BEL_SUN, ["F22"]),
]

# ---- Hotel and rate evidence ----
VENETIAN_QUOTE = {
    "property": "The Venetian Resort, Newly Remodeled Luxury King suite (2 adults)",
    "checked": CHECKED,
    "nights": [("2026-11-17", 824.25), ("2026-11-18", 164.25)],
    "resortFeePerNight": 55.00,
    "taxRate": 0.1338,
    "checkoutTotal": 1245.48,
    "taxPrinted": 146.98,
    "source": VEN_QUOTE,
}
# Booking calendar cells (lowest suite price shown for the date, which includes the resort fee and excludes tax).
# Not quotes: they are logged to show the conflict with the Nov 17-19 quote (F12).
RATE_LOG = [
    ("2026-11-17", 605, "calendar cell, 2 adults", VEN_QUOTE),
    ("2026-11-18", 165, "calendar cell, 2 adults", VEN_QUOTE),
    ("2026-12-10", None, "no price shown", VEN_CAL_DEC),
    ("2026-12-11", None, "no price shown", VEN_CAL_DEC),
    ("2026-12-12", None, "no price shown", VEN_CAL_DEC),
    ("2026-12-13", 255, "calendar cell, 2 adults", VEN_CAL_DEC),
    ("2026-12-14", 165, "calendar cell, 2 adults", VEN_CAL_DEC),
    ("2026-12-15", 165, "calendar cell, 2 adults", VEN_CAL_DEC),
    ("2026-12-16", 165, "calendar cell, 2 adults", VEN_CAL_DEC),
    ("2026-12-17", 165, "calendar cell, 2 adults", VEN_CAL_DEC),
    ("2026-12-18", 235, "calendar cell, 2 adults", VEN_CAL_DEC),
    ("2026-12-19", 405, "calendar cell, 2 adults", VEN_CAL_DEC),
]

# ---- Source list for scheduled re-checks (fed to scripts/check_sources.py via site/data/sources.json) ----
MONITOR_SOURCES = [
    ("ven-dse-table", "Venetian DeepStack IV schedule", DSE_PAGE),
    ("ven-dse-series", "Venetian DeepStack series overview", DSE_SERIES),
    ("ven-sheet-1", "DSE structure sheet 1", SHEET.format(1)),
    ("ven-sheet-5", "DSE structure sheet 5", SHEET.format(5)),
    ("ven-sheet-7", "DSE structure sheet 7", SHEET.format(7)),
    ("ven-sheet-15", "DSE structure sheet 15", SHEET.format(15)),
    ("ven-suite", "Venetian poker suite rates", VEN_SUITE),
    ("ven-fee", "Venetian resort fee", VEN_FEE),
    ("ven-terms", "Venetian hotel terms", VEN_TERMS),
    ("wynn-poker", "Wynn poker room", WYNN_POKER),
    ("wynn-wpt-sched", "Wynn WPT schedule PDF", WYNN_SCHED),
    ("wynn-poster", "Wynn daily poster PDF", WYNN_POSTER),
    ("bel-poker", "Bellagio poker page", BEL_POKER),
    ("bel-fri", "Bellagio Friday PDF", BEL_FRI),
    ("bel-sat", "Bellagio Saturday PDF", BEL_SAT),
    ("bel-sun", "Bellagio Sunday PDF", BEL_SUN),
    ("aria-poker", "ARIA poker page", ARIA_POKER),
]

# ---- Flag register ----
FLAGS = {
 "F01": ("High", "Single-entry status is not printed on any sheet read",
   "The 19 structure sheets read contain no re-entry, rebuy, or add-on wording, but none states single entry. Main-list rows say 'no re-entry/add-on wording on sheet'. Confirm in writing with the Venetian poker room.", [DSE_PAGE, SHEET.format(5)]),
 "F02": ("Medium", "Event numbers are reused across flights, restarts and Day 2 rows",
   "The official table repeats event numbers (for example 1, 7, 19, 26, 47, 56, 59). Multi-row events are grouped under one number and excluded.", [DSE_PAGE]),
 "F03": ("Medium", "Event 6 prints no guarantee",
   "Event 6 ($200 NLH, 1Day) has no GTD on the table or sheet 29. It is listed but not ranked.", [DSE_PAGE, SHEET.format(29)]),
 "F04": ("Medium", "RaceDay events 3, 4, 5 have an unclear format and no guarantee",
   "Title reads 'race to finish before the Race'. Sheet 18 prints no guarantee. Kept out of the main list and schedule.", [DSE_PAGE, SHEET.format(18)]),
 "F05": ("Low", "50+ eligibility on events 24, 32 and 49",
   "The schedule states 'must be 50+ years of age to participate'. These rows are eligibility-restricted, not general.", [DSE_PAGE, SHEET.format(17)]),
 "F06": ("Medium", "Bounty events may carry a 'rake discount'",
   "The schedule says PokerAtlas PRO members get a $20 rake discount. The sheet notes differ on the mechanism, so the discount is not applied to any ratio.", [DSE_PAGE, SHEET.format(8)]),
 "F07": ("Low", "Early-entry rake discounts on events 56 and 59",
   "Printed as '$40 rake discount for entries before 10:10 a.m.' and '$20 rake discount before 11:10 a.m.'. These are flight events and are excluded.", [DSE_PAGE]),
 "F08": ("Medium", "Structure sheet links differ by row",
   "The same event number links to different sheets on different dates (for example 1A and 1B). Each row's own link is used.", [DSE_PAGE]),
 "F09": ("Medium", "Late-registration cutoffs are printed for only two sheets",
   "Only sheets 1 and 8 print a 9:40 PM late-registration cutoff. Other rows are blank. No cutoff is computed from level lengths.", [SHEET.format(1), SHEET.format(8)]),
 "F10": ("High", "Finish times and plausible durations are not published",
   "Overlap flags use a planning assumption of 6 hours between starts. This is not an official duration (see schedule page).", [DSE_PAGE]),
 "F11": ("High", "No official tournament starts before 10:10 AM",
   "The earliest start on the Venetian table is 10:10 AM (events 32, 24, 3, 4, 5, 39, 47, 49, 56). The 8:00 AM all-day plan cannot be built from verified data.", [DSE_PAGE]),
 "F12": ("High", "Venetian calendar and the Nov 17-19 quote disagree",
   "Calendar cell Nov 17 = $605 and Nov 18 = $165. Quote nights are $824.25 and $164.25. The quote is used for the true-cost calculation. The calendar is logged only.", [VEN_QUOTE]),
 "F13": ("Low", "PokerAtlas PRO wording differs between schedule and sheet",
   "Schedule: '$20 rake discount'. Sheet 8 (earlier read): '$20 off initial buy-in ($180)'. Membership cost is not verified. Standard buy-in is used.", [DSE_PAGE, SHEET.format(8)]),
 "F14": ("Low", "Standard buy-in used for the PokerAtlas PRO discount events",
   "Events 18 and 58 are listed at $200. The discount is not applied.", [DSE_PAGE]),
 "F15": ("Low", "LIPS events add a fee on top of the buy-in",
   "Sheet 33 prints a $80 fee and a $10 LIPS fee within the $600 buy-in ($510 pool). The $600 total is used as printed.", [SHEET.format(33)]),
 "F16": ("High", "Venetian poker-suite rates are conditional and not mapped to a property",
   "'Start as low as $119 and $209' requires 6 hours of live cash play or a $300+ buy-in each night. Not used in the true-cost calculation.", [VEN_SUITE]),
 "F17": ("Medium", "Venetian calendar cells are not quotes",
   "Cells show the lowest suite price per date, including the resort fee and excluding tax. Dec 10-12 show no price. Not used in any total.", [VEN_CAL_DEC]),
 "F18": ("High", "Cancellation deadline and walking time not captured for Venetian quote",
   "No cancellation deadline on the captured quote page. No official walking time for any hotel. Both left blank.", [VEN_QUOTE]),
 "F19": ("High", "Bellagio Saturday buy-in conflict",
   "Page button reads $1,000; PDF header reads $1,100 (from earlier read); rule body reads $600 buy-in with $510 pool, $50 house, $40 gratuity. Excluded as multi-flight.", [BEL_POKER, BEL_SAT]),
 "F20": ("High", "Bellagio Friday allows re-entry and sells extra chips",
   "Re-entry through the end of level 8. A $40 voluntary gratuity buys chips. Excluded from the single-entry list.", [BEL_FRI]),
 "F21": ("Medium", "Bellagio Saturday is multi-flight",
   "Flights 1A-1D and a combined Day 2; registration to level 10. Excluded.", [BEL_SAT]),
 "F22": ("Medium", "Bellagio Sunday H.O.R.S.E. structure not read",
   "Excluded until the structure is read.", [BEL_SUN]),
 "F23": ("Low", "Bellagio page carries a stale 'resume Saturday, July 26' notice",
   "July 26, 2026 is a Sunday, and the notice is undated. Not treated as current.", [BEL_POKER]),
 "F24": ("High", "Wynn fee and cancellation terms come from an expired offer",
   "Wynn terms page 850070 covers an offer that ended Sept 30, 2025. No current Wynn fee, rate, or cancellation rule is verified.", [WYNN_TERMS]),
 "F25": ("High", "Wynn WPT formats not reviewed beyond structures chunk 0",
   "Most WPT rows are flights, satellites, or multi-day. None is listed as single-entry. Excluded from the main list.", [WYNN_SCHED, WYNN_STRUCT]),
 "F26": ("Medium", "Wynn WPT schedule prints Dec 18 with two weekdays",
   "Rows say Dec 18 is 'Wednesday' in one place and 'Friday' in another. Dec 18, 2026 is a Friday. Unresolved.", [WYNN_SCHED]),
 "F27": ("Low", "WPT $1,100 PLO breakdown sums to $1,105",
   "Earlier read of the structures PDF. Not used in any calculation.", [WYNN_STRUCT]),
 "F28": ("Medium", "Wynn daily Friday is a rebuy, and daily suspension does not name WPT",
   "Poster prints 'NLH REBUY $240' on Friday. The Wynn page says daily events are suspended during Signature, Millions and Classic series. WPT is not named, so it is unclear whether daily events run during WPT.", [WYNN_POSTER, WYNN_POKER]),
 "F29": ("High", "ARIA prints no tournament schedule or room rates",
   "The page offers 'exclusive room rates' by phone (702.590.7232) and email. No value is printed.", [ARIA_POKER]),
 "F30": ("High", "Five Strip poker pages gave no verified schedule",
   "Caesars page is general; MGM Grand page returned 'Page not found'; Golden Nugget page is blank; Resorts World page is an email template; Circa returns 404. These rooms are not listed.", [CAESARS_PAGE, MGM_PAGE, GN_PAGE, RW_PAGE, CIRCA_PAGE]),
 "F31": ("Medium", "Third-party claim of a $55 Bellagio resort fee is not verified here",
   "Coordination entries from other sessions say Bellagio terms confirm a $55 + tax fee. No Bellagio fee source was read in this session. Left blank.", [BEL_POKER]),
 "F32": ("High", "Monitor baseline not yet run",
   "The sandbox cannot reach venue sites. The daily monitor needs its first run in CI (see monitor page).", [DSE_PAGE]),
}
