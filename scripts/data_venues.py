"""Non-Venetian venue data, read from official venue sources on 2026-11-16.

Format for the compact table rows: date|time|name|buyIn|guarantee|chips|levels
`buyIn` and `guarantee` are plain numbers, "-" means the value is not printed.
"""

import re

RETRIEVED = "2026-11-16"

WYNN_POKER = "https://www.wynnlasvegas.com/casino/poker"
WYNN_DAILY_POSTER = "https://cdn.wynnresorts.com/image/upload/v1752011166/visitwynn_pdfs_files/Poker/Daily%20Tournaments/poker-daily-tournament-poster.pdf"
WYNN_DAILY_STRUCT = "https://cdn.wynnresorts.com/image/upload/v1752011191/visitwynn_pdfs_files/Poker/Daily%20Tournaments/Poker-All_Daily_Structures.pdf"
WYNN_WPT_SCHED = "https://cdn.wynnresorts.com/image/upload/v1757097329/visitwynn_pdfs_files/Poker/WPT/WPT_World_Championship_Schedule.pdf"
WYNN_WPT_STRUCT = "https://cdn.wynnresorts.com/image/upload/v1750864036/visitwynn_pdfs_files/Poker/WPT/WPT_World_Championship_Structures.pdf"
WYNN_SIG_SCHED = "https://cdn.wynnresorts.com/image/upload/v1753296112/visitwynn_pdfs_files/Poker/Wynn%20Signature%20Series/Wynn_Signature_Series_Schedule.pdf"
WYNN_SIG_STRUCT = "https://cdn.wynnresorts.com/image/upload/v1762299460/visitwynn_pdfs_files/Poker/Wynn%20Signature%20Series/Wynn_Signature_Series_Structures.pdf"

BELLAGIO_POKER = "https://bellagio.mgmresorts.com/en/casino/poker.html"
BELLAGIO_FRI = "https://assets.contentstack.io/v3/assets/bltc6ce635bc4868eb2/blt9cf95b0e60ec253e/6af491a3a9851d75c40be840/mgm-bellagio-poker-fridays-$600-nlh.pdf"
BELLAGIO_SAT = "https://assets.contentstack.io/v3/assets/bltc6ce635bc4868eb2/blt6d47974bf5a7d9b6/6af491a391a6e8e4230c9e07/mgm-bellagio-poker-saturdays-$1000-nlh.pdf"
BELLAGIO_SUN = "https://assets.contentstack.io/v3/assets/bltc6ce635bc4868eb2/blt07fcf1244a6da661/6af491a339e2b4f6b76a86ad/mgm-bellagio-poker-sundays-$400-horse.pdf"

MGM_POKER = "https://mgmgrand.mgmresorts.com/en/casino/poker-tables.html"
MGM_SCHED = "https://assets.contentstack.io/v3/assets/bltc6ce635bc4868eb2/blt5f25277b8918da08/mgm-grand-casino-poker-tournament_schedule.pdf"
MGM_STRUCT = "https://assets.contentstack.io/v3/assets/bltc6ce635bc4868eb2/bltb2a45da7e8ee5621/mgm-grand-casino-poker-120_nlh.pdf"

CAESARS_POKER = "https://www.caesars.com/las-vegas/explore/casino/poker-tournaments-las-vegas-strip"
# Official Caesars Palace daily No-Limit Hold'em flyer, linked from caesars.com/caesars-palace/casino ("View Schedule").
# Read 2026-11-18: it prints the four start times, buy-ins, fees, re-entry, add-on and guarantee.
CAESARS_FLYER = "https://www.caesars.com/content/dam/empire/clv/casino/poker/tournament-schedule/clv-poker-daily-nlh-tournament-flyer-2026.pdf"
ARIA_POKER = "https://aria.mgmresorts.com/en/casino/poker.html"
ARIA_GUIDE = "https://aria.mgmresorts.com/content/dam/MGM/aria/casino/poker/aria-casino-poker-gentlemans-guide.pdf"

# ---------------------------------------------------------------- Wynn daily
# Recurring daily tournaments. Structure PDF is the rule source.
WYNN_DAILY = [
    dict(name="$200 No Limit Hold'em", days="Monday-Thursday", time="12:00 PM", weekdays=[0,1,2,3],
         buyIn=200, guarantee=10000, chips=25000, levelMin=30, lateReg="Registration and re-entries until the start of level 9 (approximately 4:30 p.m.)",
         source=WYNN_DAILY_STRUCT, poster=WYNN_DAILY_POSTER, category="extra",
         rules=dict(
             singleEntry=dict(status="multiple-entries", excerpt="The Tournament entry fee, as well as the re-entry fee, is $200 (the 'Entry Fee')."),
             reEntry=dict(status="allowed", excerpt="Registration and re-entries will be available until the start of level 9 (approximately 4:30 p.m.)."),
             addOn=dict(status="none-printed", excerpt="No add-on provision appears on this structure sheet."),
             fee=dict(status="confirmed", excerpt="The $200 Entry Fee will be distributed as follows: $26 for the Tournament fee, $12 for the poker staff service charge, and $162 for the Tournament prize pool.")),
         note="The daily slate is suspended during each Wynn Signature, Wynn Millions and Classic tournament series (per the official poker-room page)."),
    dict(name="$240 No Limit Hold'em Rebuy & Add-on", days="Friday", time="12:00 PM", weekdays=[4],
         buyIn=240, guarantee=40000, chips=25000, levelMin=30, lateReg="Registration, rebuys and add-ons until the start of level 9 (approximately 4:30 p.m.)",
         source=WYNN_DAILY_STRUCT, poster=WYNN_DAILY_POSTER, category="extra",
         rules=dict(
             singleEntry=dict(status="multiple-entries", excerpt="Re-entry is NOT allowed, but unlimited rebuys are: 'All rebuys must be done immediately from the player's original seat.'"),
             reEntry=dict(status="not-allowed", excerpt="Re-entry is NOT allowed."),
             addOn=dict(status="allowed", excerpt="One (1) $100 add-on for 15,000 tournament chips is available any time until the end of registration."),
             rebuy=dict(status="allowed", excerpt="Unlimited $200 rebuys for 25,000 tournament chips are available any time a player is at 15,000 chips or less."),
             fee=dict(status="confirmed", excerpt="The Tournament entry fee is $240, of which $35 will be withheld for the Tournament fee and $15 as a service charge for poker staff. $190 of each Entry Fee and rebuy will fund the Tournament prize pool.")),
         note="A rebuy-heavy event: spending more buys a second shot at the same prize pool."),
    dict(name="$200 No Limit Hold'em", days="Saturday, Sunday", time="12:00 PM", weekdays=[5,6],
         buyIn=200, guarantee=25000, chips=25000, levelMin=30, lateReg="Registration, re-entries, and one (1) add-on per entry until the start of level 11 (approximately 5:30 p.m.)",
         source=WYNN_DAILY_STRUCT, poster=WYNN_DAILY_POSTER, category="extra",
         rules=dict(
             singleEntry=dict(status="multiple-entries", excerpt="The Tournament entry fee, as well as the re-entry fee, is $200 (the 'Entry Fee')."),
             reEntry=dict(status="allowed", excerpt="Registration, re-entries, and one (1) add-on per entry will be available until the start of level 11 (approximately 5:30 p.m.)."),
             addOn=dict(status="allowed", excerpt="One (1) $100 add-on for 25,000 tournament chips is available any time until the end of registration."),
             fee=dict(status="confirmed", excerpt="The $200 Entry Fee will be distributed as follows: $26 for the Tournament fee, $12 for the poker staff service charge, and $162 for the Tournament prize pool."))),
    dict(name="$160 No Limit Hold'em Nightly", days="Monday-Sunday", time="6:00 PM", weekdays=[0,1,2,3,4,5,6],
         buyIn=160, guarantee=10000, chips=25000, levelMin=20, lateReg="Registration, re-entries, and one (1) add-on per entry until the start of level 9 (approximately 9:00 p.m.)",
         source=WYNN_DAILY_STRUCT, poster=WYNN_DAILY_POSTER, category="extra",
         rules=dict(
             singleEntry=dict(status="multiple-entries", excerpt="The Tournament entry fee, as well as the re-entry fee, is $160 (the 'Entry Fee')."),
             reEntry=dict(status="allowed", excerpt="Registration, re-entries, and one (1) add-on per entry will be available until the start of level 9 (approximately 9:00 p.m.)."),
             addOn=dict(status="allowed", excerpt="One (1) $100 add-on for 25,000 tournament chips is available any time until the end of registration."),
             fee=dict(status="confirmed", excerpt="The $160 Entry Fee will be distributed as follows: $20 for the Tournament fee, $10 for the poker staff service charge, and $130 for the Tournament prize pool."))),
]

# ------------------------------------------------------- Wynn WPT Championship
# Rows exactly as printed on the official schedule PDF, including the December 18
# weekday conflict (the PDF labels two different days "Dec. 18").
# Transcript of the official WPT World Championship schedule PDF: one line per
# printed row, fields  date | start | event | buy-in | guarantee | chips | levels | marks.
# '-' means the official cell is empty.
#
# Re-checked line by line against raw/wynn_wpt_world_championship_schedule.md on
# 2026-11-17 by scripts/verify_wpt_full.py, which reports 136/136 rows matched and
# names every difference. Seven guarantee cells were corrected in that pass: a
# satellite's seat guarantee had been carried onto the non-satellite rows that share
# its date and start time (rows 59, 60, 76, 116, 117 of this block), and two
# satellites had lost the seat guarantee the PDF prints on their own row (rows 84, 96).
WYNN_WPT_ROWS = """
2026-11-27|11:00 AM|No Limit Hold'em Day 1A|600|400000|40000|30/40
2026-11-27|12:00 PM|TORSE|600|-|35000|30
2026-11-27|1:00 PM|PLO|400|-|30000|30
2026-11-27|5:00 PM|No Limit Hold'em Day 1B|600|400000|40000|30/40
2026-11-28|11:00 AM|No Limit Hold'em Day 1C|600|400000|40000|30/40
2026-11-28|12:00 PM|Mixed Triple Draw (A-5, 2-7, Badugi)|600|-|35000|30
2026-11-28|5:00 PM|No Limit Hold'em Day 1D|600|400000|40000|30/40
2026-11-29|11:00 AM|No Limit Hold'em Day 1E|600|400000|40000|30/40
2026-11-29|6:00 PM|No Limit Hold'em Day 1F|600|400000|40000|20/40
2026-11-30|11:00 AM|No Limit Hold'em Day 1A|800|1000000|40000|30/40
2026-11-30|12:00 PM|Limit Omaha 8|600|-|35000|30
2026-11-30|1:00 PM|No Limit Hold'em Day 2|800|1000000|40000|30/40
2026-11-30|5:00 PM|No Limit Hold'em Day 1B|800|1000000|40000|30/40
2026-12-01|11:00 AM|No Limit Hold'em Day 1C|800|1000000|40000|30/40
2026-12-01|12:00 PM|Limit Omaha 8/5/stud 8|600|-|35000|30
2026-12-01|1:00 PM|PLO|1100|-|30000|30
2026-12-01|5:00 PM|No Limit Hold'em Day 1D|800|1000000|40000|30/40
2026-12-02|11:00 AM|No Limit Hold'em Day 1E|800|1000000|40000|30/40
2026-12-02|6:00 PM|No Limit Hold'em Day 1F|800|1000000|40000|20/40
2026-12-03|11:00 AM|No Limit Hold'em Day 1A|1600|1000000|40000|40
2026-12-03|1:00 PM|No Limit Hold'em Day 2|1600|1000000|40000|40
2026-12-03|7:00 PM|Double Play Milestone Satellite (2 X $1,100 ticket)|400|25 Prizes|20000|20|*
2026-12-04|11:00 AM|No Limit Hold'em Day 1B|1600|1000000|40000|40
2026-12-04|12:00 PM|HORSE|600|-|35000|30
2026-12-04|1:00 PM|No Limit Hold'em Final Table|-|-|-|-
2026-12-04|7:00 PM|Double Play Milestone Satellite (2 X $1,100 ticket)|400|25 Prizes|20000|20|*
2026-12-05|11:00 AM|No Limit Hold'em Day 2|1100|5000000|40000|40/60
2026-12-05|11:00 AM|WPT Prime Championship Day 1A|1100|5000000|40000|40/60
2026-12-05|9:00 PM|NLH Turbo|600|50000|30000|20
2026-12-06|11:00 AM|WPT Prime Championship Day 1B|1100|5000000|40000|40/60
2026-12-06|11:00 AM|PLO Mystery Bounty Day 1A|1600|500000|40000|40
2026-12-06|12:00 PM|Milestone Satellite to $1,100 Prime Championship|200|50 Seats|20000|20|**
2026-12-06|6:00 PM|PLO Mystery Bounty Day 1B|1600|500000|40000|20/40
2026-12-06|7:00 PM|Double Play Milestone Satellite (2 X $1,100 ticket)|400|25 Prizes|20000|20|*
2026-12-06|9:00 PM|NLH Turbo|600|50000|30000|20
2026-12-07|11:00 AM|WPT Prime Championship Day 1C|1100|5000000|40000|40/60
2026-12-07|11:00 AM|HORSE (2 Day)|1100|-|40000|40
2026-12-07|12:00 PM|PLO Mystery Bounty Day 2|-|-|-|-
2026-12-07|1:00 PM|PLO $500 Bounty|1600|100000|30000|30
2026-12-07|7:00 PM|Milestone Satellite Package to Prime and World Championship|1600|25 Prizes|20000|25|**
2026-12-07|9:00 PM|NLH Turbo|600|50000|30000|20
2026-12-08|11:00 AM|WPT Prime Championship Day 1D|1100|5000000|40000|40/60
2026-12-08|7:00 PM|Milestone Satellite to $10,400 World Championship|1100|25 Seats|20000|25|**
2026-12-08|9:00 PM|NLH Turbo|600|50000|30000|20
2026-12-09|11:00 AM|No Limit Hold'em (2 Day)|1600|1000000|40000|40
2026-12-09|12:00 PM|WPT Prime Championship Day 2|-|-|-|-
2026-12-09|1:00 PM|PLO $1,000 Bounty|3000|250000|30000|30
2026-12-09|1:00 PM|Limit Omaha 8|800|-|35000|30
2026-12-09|2:00 PM|Milestone Satellite to $10,400 World Championship|1100|25 Seats|20000|25|**
2026-12-09|7:00 PM|Milestone Satellite to $10,400 World Championship|1100|25 Seats|20000|25|**
2026-12-09|9:00 PM|NLH Turbo|600|50000|30000|20
2026-12-10|10:00 AM|Super Gold Million Mystery Bounty Day 1A|400|3000000|30000|30/40
2026-12-10|12:00 PM|WPT Prime Championship Day 3|-|-|-|-
2026-12-10|6:00 PM|Super Gold Million Mystery Bounty Day 1B|400|3000000|30000|20/40
2026-12-11|10:00 AM|Super Gold Million Mystery Bounty Day 1C|400|3000000|30000|30/40
2026-12-11|12:00 PM|WPT Prime Championship Day 4|-|-|-|-
2026-12-11|6:00 PM|Super Gold Million Mystery Bounty Day 1D|400|3000000|30000|20/40
2026-12-12|10:00 AM|No Limit Hold'em|800|100000|30000|30
2026-12-12|1:00 PM|PLO|3000|250000|30000|30
2026-12-12|2:00 PM|WPT Prime Championship Final Table|-|-|-|-
2026-12-12|2:00 PM|Super Gold Million Mystery Bounty Day 2|-|-|-|-
2026-12-12|2:00 PM|Milestone Satellite to $10,400 World Championship 1A/8|1100|75 Seats|20000|25|**
2026-12-12|4:00 PM|Milestone Satellite to $10,400 Ladies NLH Championship|200|10 Seats|20000|20|**
2026-12-12|7:00 PM|Milestone Satellite to $10,400 World Championship 1A/8|1100|25 Seats|20000|25|**
2026-12-12|9:00 PM|NLH Turbo|600|50000|30000|20
2026-12-13|11:00 AM|WPT World Championship Day 1A $1,000,000 Added|10400|-|100000|60/90|***
2026-12-13|11:00 AM|Ladies NIH Championship (2 Day)|1100|250000|40000|40|****|***
2026-12-13|11:00 AM|TORSE (2 Day)|1100|-|40000|40
2026-12-13|11:00 AM|No Limit Hold'em Day 1A|800|500000|40000|40
2026-12-13|12:00 PM|PLO Day 1A|1600|1000000|40000|40
2026-12-13|12:00 PM|Milestone Satellite to $10,400 World Championship 1B|1100|25 Seats|20000|25|**
2026-12-13|1:00 PM|Super Gold Million Mystery Bounty Day 3|-|-|-|-
2026-12-13|6:00 PM|Milestone Satellite to $10,400 World Championship 1B/C|1100|25 Seats|20000|25|**
2026-12-14|11:00 AM|WPT World Championship Day 1B $1,000,000 Added|10400|-|100000|60/90|***
2026-12-14|11:00 AM|No Limit Hold'em Day 1B|800|500000|40000|40
2026-12-14|12:00 PM|PLO Day 1B|1600|1000000|40000|40
2026-12-14|12:00 PM|Mixed Triple Draw (A-5, 2-7, Badugi) (2 Day)|1100|-|40000|40
2026-12-14|12:00 PM|Milestone Satellite to $10,400 World Championship 1C|1100|25 Seats|20000|25|**
2026-12-14|2:00 PM|Super Gold Million Mystery Bounty Final Table|-|-|-|-
2026-12-14|6:00 PM|Milestone Satellite to $10,400 World Championship 1C|1100|25 Seats|20000|25|**
2026-12-14|7:00 PM|PLO Turbo|1100|100000|30000|20
2026-12-14|9:00 PM|NLH Turbo|600|50000|30000|20
2026-12-15|11:00 AM|WPT World Championship Day 1C $1,000,000 Added|10400|-|100000|60/90|***
2026-12-15|11:00 AM|No Limit Hold'em Day 2|-|-|-|-
2026-12-15|11:00 AM|Milestone Satellite to $10,400 World Championship 1C/Day 2|1100|10 Seats|20000|25|**
2026-12-15|12:00 PM|PLO Day 2|-|-|-|-
2026-12-15|12:00 PM|Big O|1100|-|30000|30
2026-12-15|1:00 PM|PLO Progressive Bounty (PKO)|3000|250000|30000|30
2026-12-15|6:00 PM|Milestone Satellite to $10,400 World Championship Day 2|1100|10 Seats|20000|25|**
2026-12-15|7:00 PM|NLH $500 Bounty Turbo|1600|100000|30000|20
2026-12-18|11:00 AM|No Limit Hold'em Day 1A|1100|1000000|40000|40
2026-12-18|12:00 PM|WPT World Championship Day 2 (Registration open until the start of Day 2)|-|-|-|-
2026-12-18|12:00 PM|PLO Double Board Bomb Pot|800|-|30000|30
2026-12-18|1:00 PM|PLO 6-Max|10500|-|100000|30/40|****
2026-12-18|1:00 PM|HORSE|800|-|35000|30
2026-12-18|6:00 PM|Milestone Satellite to $25K NLH High Roller|3000|-|20000|25|****
2026-12-18|6:00 PM|Milestone Satellite to $3,000 NLH|400|25 Seats|20000|20|**
2026-12-18|7:00 PM|No Limit Hold'em Day 1B|1100|1000000|40000|20/40
2026-12-17|11:00 AM|Seniors NLH Championship (3 Day)|1100|500000|40000|40
2026-12-17|11:00 AM|Wynn Mixed Championship (2 Day)|1600|-|40000|40/60
2026-12-17|12:00 PM|WPT World Championship Day 3|-|-|-|-
2026-12-17|12:00 PM|No Limit Hold'em Day 2|-|-|-|-
2026-12-17|12:00 PM|No Limit Hold'em Day 1A|3000|2000000|40000|40
2026-12-17|1:00 PM|NLH High Roller (2 Day)|25800|-|200000|40/60|****
2026-12-17|2:00 PM|Milestone Satellite to $3,000 NLH|400|25 Seats|20000|20|**
2026-12-17|7:00 PM|Milestone Satellite to $3,000 NLH|400|25 Seats|20000|20|**
2026-12-18|10:00 AM|Milestone Satellite to $3,000 NLH|400|10 Seats|20000|15|**
2026-12-18|12:00 PM|WPT World Championship Day 4|-|-|-|-
2026-12-18|12:00 PM|No Limit Hold'em Day 1B|3000|2000000|40000|40
2026-12-18|12:00 PM|Limit Omaha 8 Championship (2 Day)|1600|-|40000|40/60
2026-12-18|12:00 PM|No Limit Hold'em|600|100000|30000|30
2026-12-18|1:00 PM|NLH 6-Max|10500|-|100000|30/40|****
2026-12-18|2:00 PM|Milestone Satellite to $5,000 Seniors High Roller|600|10 Seats|20000|20|**
2026-12-18|6:00 PM|NLH Turbo|1100|100000|30000|20
2026-12-19|11:00 AM|Seniors High Roller (3 Day)|5000|250000|50000|60
2026-12-19|11:00 AM|NLH Mystery Bounty Day 1A|1600|1000000|40000|40
2026-12-19|12:00 PM|WPT World Championship Day 5|-|-|-|-
2026-12-19|12:00 PM|No Limit Hold'em Day 2|-|-|-|-
2026-12-19|12:00 PM|Milestone Satellite to $1,600 Mystery Bounty|300|10 Seats|20000|20|**
2026-12-19|1:00 PM|PLO|10500|-|100000|30/40|****
2026-12-19|1:00 PM|NLH 6-Max|3000|500000|30000|30
2026-12-19|1:00 PM|TORSE Championship (2 Day)|1600|-|40000|40/60
2026-12-19|5:00 PM|Milestone Satellite to $1,600 Mystery Bounty|300|10 Seats|20000|20|**
2026-12-19|6:00 PM|NLH 6-Max Turbo|600|50000|30000|20
2026-12-19|7:00 PM|NLH Mystery Bounty Day 1B|1600|1000000|40000|20/40
2026-12-20|11:00 AM|NLH Mystery Bounty Day 1C|1600|1000000|40000|40
2026-12-20|12:00 PM|No Limit Hold'em Final Table|-|-|-|-
2026-12-20|12:00 PM|No Limit Hold'em|600|50000|30000|30
2026-12-20|1:00 PM|NLH 8-Max|10500|-|100000|30/40|****
2026-12-20|1:00 PM|Mixed Triple Draw (A-5, 2-7, Badugi)|600|-|35000|30
2026-12-20|2:00 PM|WPT World Championship Final Table|-|-|-|-
2026-12-20|6:00 PM|5-Card PLO Turbo|600|50000|30000|20
2026-12-20|7:00 PM|NLH Mystery Bounty Day 1D|1600|1000000|40000|20/40
2026-12-21|12:00 PM|No Limit Hold'em|1100|100000|30000|30
2026-12-21|1:00 PM|NLH Mystery Bounty Day 2|-|-|-|-
2026-12-21|8:00 PM|NLH Turbo|600|50000|30000|20
""".strip()

# ------------------------------------- WPT World Championship structures PDF
# Read in full (all eight chunks) on 2026-11-17.  Every string below is copied
# from the document, and raw/wynn_wpt_world_championship_structures_2026-11-17.md
# is the verbatim capture it was copied from.
#
# `dates` is the list of printed start slots the section's own Terms and
# Conditions block names.  A schedule row is matched to a section ONLY when its
# date AND start time AND buy-in all appear in that list, so a row cannot inherit
# another event's rules by sharing a name.  The page reader renders 11 a.m. as
# "11 a.m."; the schedule transcript stores "11:00 AM", so both sides are
# normalised through the same helper before comparison.
#
# Keys are (buy-in, printed event name as it appears on the schedule transcript).
# The document prints "$600 NLH Turbo" while the schedule prints "NLH Turbo", and
# "Mixed Triple Draw (A-5, 2-7, Badugi)" is printed identically on both, so the
# mapping below is by the schedule's own name.
WPT_SHEET_SECTIONS = {
    ("600", "No Limit Hold'em Day 1"): dict(  # matches Day 1A..Day 1F
        title="$600 No Limit Hold'em $400,000 Guarantee (November 27-30, 2026)",
        dates={
            "2026-11-27 11:00": "Day 1A", "2026-11-27 17:00": "Day 1B",
            "2026-11-28 11:00": "Day 1C", "2026-11-28 17:00": "Day 1D",
            "2026-11-29 11:00": "Day 1E", "2026-11-29 18:00": "Day 1F",
        },
        days_printed="1A Fri Nov 27 11 a.m. / 1B Fri Nov 27 5 p.m. / 1C Sat Nov 28 11 a.m. / "
                     "1D Sat Nov 28 5 p.m. / 1E Sun Nov 29 11 a.m. / 1F Sun Nov 29 6 p.m. / "
                     "Day 2 Mon Nov 30 1 p.m.",
        fee="$600 Buy-in = $510 (Tournament Prize Pool) + $65 (Tournament Fee) + $25 (Poker Staff Service Charge)",
        registration="Unlimited re-entry for each starting flight will be available until the start of level 9. "
                     "A player who advances to Day 2 is prohibited from entering a subsequent starting flight.",
        chips="Players will start with 40,000 in tournament chips.",
        levels="Day 1A-E: 30 minutes per level until 12.5% or less of the field remains. Day 1F: 20 minutes per level.",
    ),
    ("600", "TORSE"): dict(
        title="$600 TORSE (November 27, 2026)",
        dates={"2026-11-27 12:00": ""},
        days_printed="Friday, November 27, 2026, at 12 p.m.",
        fee="$600 Buy-in = $510 (Tournament Prize Pool) + $65 (Tournament Fee) + $25 (Poker Staff Service Charge)",
        registration="Unlimited re-entry will be available until the start of level 9",
        chips="Players will start with 35,000 in tournament chips.",
        levels="30 minutes per level until a winner is declared.",
    ),
    ("400", "PLO"): dict(
        title="$400 PLO (November 27, 2026)",
        dates={"2026-11-27 13:00": ""},
        days_printed="Friday, November 27, 2026, at 1 p.m.",
        fee="$400 Buy-in = $337 (Tournament Prize Pool) + $45 (Tournament Fee) + $18 (Poker Staff Service Charge)",
        registration="Unlimited re-entry will be available until the start of level 9 (approximately 5:30 p.m.).",
        chips="Players will start with 30,000 in tournament chips.",
        levels="30 minutes per level until a winner is declared.",
    ),
    ("600", "Mixed Triple Draw (A-5, 2-7, Badugi)"): dict(
        title="$600 Mixed Triple Draw (A-5, 2-7, Badugi) (November 28 and December 20, 2026)",
        dates={"2026-11-28 12:00": "", "2026-12-20 13:00": ""},
        days_printed="Saturday, November 28, 2026, at 12 p.m. / Sunday, December 20, 2026, at 1 p.m.",
        fee="$600 Buy-in = $510 (Tournament Prize Pool) + $65 (Tournament Fee) + $25 (Poker Staff Service Charge)",
        registration="Unlimited re-entry will be available until the start of level 9.",
        chips="Players will start with 35,000 in tournament chips.",
        levels="30 minutes per level until a winner is declared.",
    ),
    ("800", "No Limit Hold'em Day 1"): dict(  # matches Day 1A..Day 1F
        title="$800 No Limit Hold'em $1,000,000 Guarantee (November 30 - December 4, 2026)",
        dates={
            "2026-11-30 11:00": "Day 1A", "2026-11-30 17:00": "Day 1B",
            "2026-12-01 11:00": "Day 1C", "2026-12-01 17:00": "Day 1D",
            "2026-12-02 11:00": "Day 1E", "2026-12-02 18:00": "Day 1F",
        },
        days_printed="1A Mon Nov 30 11 a.m. / 1B Mon Nov 30 5 p.m. / 1C Tue Dec 1 11 a.m. / "
                     "1D Tue Dec 1 5 p.m. / 1E Wed Dec 2 11 a.m. / 1F Wed Dec 2 6 p.m. / "
                     "Day 2 Thu Dec 3 1 p.m. / Final Table Fri Dec 4 1 p.m.",
        fee="$800 Buy-in = $695 (Tournament Prize Pool) + $72 (Tournament Fee) + $33 (Poker Staff Service Charge)",
        registration="Unlimited re-entry for each starting flight will be available until the start of level 9. "
                     "A player who advances to Day 2 is prohibited from entering a subsequent starting flight.",
        chips="Players will start with 40,000 in tournament chips.",
        levels="Day 1A-1E: 30 minutes per level until 12.5% or less of the field remains. Day 1F: 20 minutes per level.",
    ),
    ("600", "Limit Omaha 8"): dict(
        title="$600 Limit Omaha 8 (November 30, 2026)",
        dates={"2026-11-30 12:00": ""},
        days_printed="Monday, November 30, 2026, at 12 p.m.",
        fee="$600 Buy-in = $510 (Tournament Prize Pool) + $65 (Tournament Fee) + $25 (Poker Staff Service Charge)",
        registration="Unlimited re-entry will be available until the start of level 9",
        chips="Players will start with 35,000 in tournament chips.",
        levels="30 minutes per level until a winner is declared.",
    ),
    ("600", "Limit Omaha 8/5/stud 8"): dict(
        title="$600 Limit Omaha 8/Stud 8 (December 1, 2026)",
        dates={"2026-12-01 12:00": ""},
        days_printed="Tuesday, December 1, 2026, at 12 p.m.",
        fee="$600 Buy-in = $510 (Tournament Prize Pool) + $65 (Tournament Fee) + $25 (Poker Staff Service Charge)",
        registration="Unlimited re-entry will be available until the start of level 9",
        chips="Players will start with 35,000 in tournament chips.",
        levels="30 minutes per level until a winner is declared.",
    ),
    ("1100", "PLO"): dict(
        title="$1,100 PLO (December 1, 2026)",
        dates={"2026-12-01 13:00": ""},
        days_printed="Tuesday, December 1, 2026, at 1 p.m.",
        # The printed components sum to $1,105 against the printed $1,100 buy-in (flag F60).
        fee="$1,100 Buy-in = $975 (Tournament Prize Pool) + $85 (Tournament Fee) + $45 (Poker Staff Service Charge)",
        registration="Unlimited re-entry will be available until the start of level 9 (approximately 5:30 p.m.).",
        chips="Players will start with 30,000 in tournament chips.",
        levels="30 minutes per level until a winner is declared.",
    ),
    ("1600", "No Limit Hold'em Day 1"): dict(  # matches Day 1A and Day 1B only
        title="$1,600 No Limit Hold'em $1,000,000 Guarantee (December 3-5, 2026)",
        dates={"2026-12-03 11:00": "Day 1A", "2026-12-04 11:00": "Day 1B"},
        days_printed="Day 1A Thu Dec 3 11 a.m. / Day 1B Fri Dec 4 11 a.m. / Day 2 Sat Dec 5 11 a.m.",
        fee="$1,600 Buy-in = $1,430 (Tournament Prize Pool) + $120 (Tournament Fee) + $50 (Poker Staff Service Charge)",
        registration="Unlimited re-entry for each starting flight will be available until the start of level 10. "
                     "A player who advances to Day 2 is prohibited from entering a subsequent starting flight.",
        chips="Players will start with 40,000 in tournament chips.",
        levels="Day 1: 40 minutes per level until 12.5% or less of the field remains.",
    ),
    ("600", "HORSE"): dict(
        title="$600 HORSE (December 4, 2026)",
        dates={"2026-12-04 12:00": ""},
        days_printed="Friday, December 4, 2026 at 12 p.m.",
        fee="$600 Buy-in = $510 (Tournament Prize Pool) + $65 (Tournament Fee) + $25 (Poker Staff Service Charge)",
        registration="Unlimited re-entry will be available until the start of level 9 (approximately 4:30 p.m.).",
        chips="Players will start with 35,000 in tournament chips.",
        levels="30 minutes per level until a winner is declared.",
    ),
    ("600", "NLH Turbo"): dict(
        title="$600 NLH Turbo $50,000 Guarantee (eight printed dates)",
        dates={
            "2026-12-05 21:00": "", "2026-12-06 21:00": "", "2026-12-07 21:00": "",
            "2026-12-08 21:00": "", "2026-12-09 21:00": "", "2026-12-12 21:00": "",
            "2026-12-14 21:00": "", "2026-12-21 18:00": "",
        },
        days_printed="Sat Dec 5 9 p.m. / Sun Dec 6 9 p.m. / Mon Dec 7 9 p.m. / Tue Dec 8 9 p.m. / "
                     "Wed Dec 9 9 p.m. / Sat Dec 12 9 p.m. / Mon Dec 14 9 p.m. / Mon Dec 21 6 p.m.",
        fee="$600 Buy-in = $515 (Tournament Prize Pool) + $60 (Tournament Fee) + $25 (Poker Staff Service Charge)",
        registration="Unlimited re-entry will be available until the start of level 9.",
        chips="Players will start with 30,000 in tournament chips.",
        levels="20 minutes per level until a winner is declared.",
    ),
    ("1600", "PLO Mystery Bounty"): dict(  # the schedule prints this as "PLO $500 Bounty"
        title="$1,600 PLO Mystery Bounty $500,000 Guarantee (December 6-7, 2026)",
        dates={"2026-12-06 11:00": "Day 1A", "2026-12-06 18:00": "Day 1B"},
        days_printed="Day 1A Sun Dec 6 11 a.m. / Day 1B Sun Dec 6 6 p.m. / Day 2 Mon Dec 7 12 p.m.",
        fee="$1,600 Buy-in = $930 (Tournament Prize Pool) + $500 (Mystery Bounty Prize Pool) + "
            "$120 (Tournament Fee) + $50 (Poker Staff Service Charge)",
        registration="Unlimited re-entry for each starting flight will be available until the start of level 10. "
                     "A player who advances to Day 2 is prohibited from entering a subsequent starting flight.",
        chips="Players will start with 40,000 in tournament chips.",
        levels="Day 1A: 40 minutes per level. Day 1B: 20 minutes per level.",
    ),
    # The only section in the document that prints an explicit per-flight entry cap.
    ("1100", "WPT Prime Championship Day 1"): dict(  # matches Day 1A..Day 1D
        title="$1,100 WPT Prime Championship $5,000,000 Guarantee (December 5-12, 2026)",
        dates={
            "2026-12-05 11:00": "Day 1A", "2026-12-06 11:00": "Day 1B",
            "2026-12-07 11:00": "Day 1C", "2026-12-08 11:00": "Day 1D",
        },
        days_printed="1A Sat Dec 5 11 a.m. / 1B Sun Dec 6 11 a.m. / 1C Mon Dec 7 11 a.m. / "
                     "1D Tue Dec 8 11 a.m. / Day 2 Wed Dec 9 12 p.m. / Day 3 Thu Dec 10 12 p.m. / "
                     "Day 4 Fri Dec 11 12 p.m. / Final Table Sat Dec 12 2 p.m.",
        fee="$1,100 Buy-in = $970 (Tournament Prize Pool) + $90 (Tournament Fee) + $40 (Poker Staff Service Charge)",
        registration="One (1) Entry and One (1) re-entry for each starting flight will be available until the start "
                     "of level 10 (approximately 6:45 p.m.). A player who advances to Day 2 is prohibited from "
                     "entering a subsequent starting flight.",
        chips="Players will start with 40,000 in tournament chips.",
        levels="Day 1: 40 minutes per level until 12.5% or less of the field remains.",
        # Printed in the document; NOT a one-entry tournament, so the row stays out of the
        # single-entry filter. This phrase is quoted verbatim in the rule panel.
        per_flight_cap="One (1) Entry and One (1) re-entry for each starting flight",
    ),
}

# ------------------------------------------------------ Wynn Signature Series
WYNN_SIGNATURE_ROWS = """
2027-01-11|12:00 PM|No Limit Hold'em Day 1A|400|150000|40000|30/40
2027-01-11|5:00 PM|No Limit Hold'em Day 1B|400|150000|40000|30/40
2027-01-12|12:00 PM|No Limit Hold'em Day 1C|400|150000|40000|30/40
2027-01-12|5:00 PM|No Limit Hold'em Day 1D|400|150000|40000|30/40
2027-01-13|12:00 PM|No Limit Hold'em Day 1E|400|150000|40000|30/40
2027-01-13|5:00 PM|No Limit Hold'em Day 1F|400|150000|40000|30/40
2027-01-14|11:00 AM|No Limit Hold'em Day 1A|600|250000|40000|40
2027-01-14|1:00 PM|No Limit Hold'em Day 2|-|-|-|-
2027-01-14|6:00 PM|Milestone Satellite to $600 NLH|125|10 Seats|20000|20
2027-01-15|11:00 AM|No Limit Hold'em Day 1B|600|250000|40000|40
2027-01-15|6:00 PM|NLH Turbo|200|10000|25000|20
2027-01-16|11:00 AM|No Limit Hold'em Day 1C|600|250000|40000|40
2027-01-16|6:00 PM|No Limit Hold'em Day 1D|600|250000|40000|20/40
2027-01-17|12:00 PM|No Limit Hold'em|400|30000|30000|30
2027-01-17|1:00 PM|No Limit Hold'em Day 2|-|-|-|-
2027-01-17|6:00 PM|NLH Turbo|200|10000|25000|20
2027-01-18|11:00 AM|No Limit Hold'em Day 1A|400|100000|40000|40
2027-01-18|1:00 PM|PLO|400|-|30000|30
2027-01-18|6:00 PM|NLH Turbo|200|10000|25000|20
2027-01-19|11:00 AM|No Limit Hold'em Day 1B|400|100000|40000|40
2027-01-19|1:00 PM|TORSE|400|-|35000|30
2027-01-19|6:00 PM|NLH Turbo|200|10000|25000|20
2027-01-20|11:00 AM|No Limit Hold'em Day 1C|400|100000|40000|40
2027-01-20|1:00 PM|Mixed Triple Draw (A-5, 2-7, Badugi)|400|-|35000|30
2027-01-20|6:00 PM|NLH Turbo|200|10000|25000|20
2027-01-21|11:00 AM|No Limit Hold'em Day 1A|800|300000|40000|40
2027-01-21|12:00 PM|No Limit Hold'em Day 2|-|-|-|-
2027-01-21|1:00 PM|TOE|400|-|35000|30
2027-01-21|6:00 PM|Milestone Satellite to $800 NLH|160|10 Seats|20000|20
2027-01-22|11:00 AM|No Limit Hold'em Day 1B|800|300000|40000|40
2027-01-22|1:00 PM|Big O|400|-|30000|30
2027-01-22|6:00 PM|Milestone Satellite to $800 NLH|160|10 Seats|20000|20
2027-01-23|11:00 AM|No Limit Hold'em Day 1C|800|300000|40000|40
2027-01-23|6:00 PM|No Limit Hold'em Day 1D|800|300000|40000|20/40
2027-01-24|12:00 PM|Seniors NLH 50+|400|30000|30000|30
2027-01-24|1:00 PM|No Limit Hold'em Day 2|-|-|-|-
2027-01-24|1:00 PM|PLO Double Board Bomb Pot|400|-|30000|30
2027-01-24|6:00 PM|NLH Turbo|200|10000|25000|20
""".strip()

# ------------------------------------------------------------------ Bellagio
BELLAGIO_EVENTS = [
    dict(name="$600 No Limit Hold'em", days="Fridays", time="11:00 AM", weekdays=[4], buyIn=600, guarantee="",
         chips=30000, levelMin=30, source=BELLAGIO_FRI, page=BELLAGIO_POKER, category="extra",
         lateReg="Registration and re-entry through the end of level 8 (including break). Level length 30 minutes.",
         rules=dict(
             singleEntry=dict(status="multiple-entries", excerpt="Players may buy-in and re-enter through the end of level 8 (Including Break)."),
             reEntry=dict(status="allowed", excerpt="Players may buy-in and re-enter through the end of level 8 (Including Break)."),
             addOn=dict(status="paid-chip-gratuity", excerpt="There is a voluntary Staff gratuity of $40, at registration only. The voluntary staff gratuity will grant players an extra 15,000 chips."),
             fee=dict(status="confirmed", excerpt="The $600 Buy-In is allocated as follows: $510 to Prize Pool; $50 House Fee; $40 Voluntary Staff Gratuity.")),
         note="The optional $40 staff gratuity buys 15,000 extra chips, so paying more raises your stack. No guarantee is printed on the sheet."),
    dict(name="$1,000 / $1,100 No Limit Hold'em (multi-flight)", days="Saturdays", time="11:00 AM", weekdays=[5],
         buyIn="", guarantee="", chips=40000, levelMin=30, source=BELLAGIO_SAT, page=BELLAGIO_POKER,
         category="conflict", lateReg="Registration will be open until the start of Level 10. (Approximately 5:15pm for Flights 1A, 1B, 4:15pm for 1C and 9:30pm for Flight D).",
         rules=dict(
             singleEntry=dict(status="source-conflict", excerpt="The PDF header reads 'NLH $1100 BUY-IN', the poker-room page link reads '$1,000 NLH', and rule 07 reads 'Of the $600 Buy-in, $510 goes to the Prize Pool, $50 is Admin Fees and $40 is optional staff gratuity.'"),
             reEntry=dict(status="not-verified", excerpt="No re-entry clause appears on the sheet; the entry fee itself is in conflict, so the event is not ranked."),
             addOn=dict(status="paid-chip-gratuity", excerpt="There is a voluntary staff gratuity of $40, at registration only. The voluntary staff gratuity will grant players an extra 20,000 chips."),
             fee=dict(status="source-conflict", excerpt="Buy-in printed as $1,100 in the sheet header, $1,000 in the page link, and $600 in rule 07.")),
         note="Not ranked: the official sources disagree on the buy-in. The sheet also references a 'Combined Final Day 2 (9/13/26)' date."),
    dict(name="$400 H.O.R.S.E.", days="Sundays", time="11:00 AM", weekdays=[6], buyIn=400, guarantee="",
         chips=30000, levelMin=30, source=BELLAGIO_SUN, page=BELLAGIO_POKER, category="extra",
         lateReg="Registration and re-entry through the end of level 8 (including break). Level length 30 minutes.",
         rules=dict(
             singleEntry=dict(status="multiple-entries", excerpt="Players may buy-in and re-enter through the end of level 8 (Including Break)."),
             reEntry=dict(status="allowed", excerpt="Players may buy-in and re-enter through the end of level 8 (Including Break)."),
             addOn=dict(status="paid-chip-gratuity", excerpt="A voluntary Staff gratuity of $25, at registration only, will grant players an additional 15,000 in starting chips."),
             fee=dict(status="confirmed", excerpt="The $400 Buy-In is allocated as follows: $340 to Prize Pool; $35 House Fee; $25 Voluntary Staff Gratuity.")),
         note="Payout structure is approximately 12.5% of the field. No guarantee is printed on the sheet."),
    dict(name="$300 Pot Limit Omaha Double Board Bomb Pot", days="Nightly (per poker-room page)", time="6:00 PM", weekdays=[0,1,2,3,4,5,6],
         buyIn=300, guarantee="", chips="", levelMin="", source=BELLAGIO_POKER, page=BELLAGIO_POKER,
         category="recurring", lateReg="",
         rules=dict(
             singleEntry=dict(status="not-verified", excerpt="The poker-room page lists 'PLO Double Bomb Pot ... nightly at 6 PM' without a structure sheet, so entry terms are not published in the reviewed material."),
             reEntry=dict(status="not-verified", excerpt="No structure sheet was located for this event in the reviewed material."),
             addOn=dict(status="not-verified", excerpt="No structure sheet was located for this event in the reviewed material."),
             fee=dict(status="partial", excerpt="The $300 buy-in appears only in the page notice 'Tournament play will resume on Saturday, July 26, beginning with the $300 PLO Double Board Bomb Pot Tournament at 2 PM PT.'")),
         note="Start-time conflict: the page highlights say 6 PM nightly, the page notice says 2 PM PT. The 'July 26' notice carries no year."),
]

# ---------------------------------------------------------------- MGM Grand
MGM_EVENTS = [
    dict(name="$120 No Limit Hold'em", days="Sunday-Friday", time="11:10 AM", weekdays=[0,1,2,3,4,6], buyIn=120, guarantee="",
         chips=25000, levelMin=15, source=MGM_SCHED, page=MGM_POKER, category="recurring",
         lateReg="Registration is open until Level 8. Level length 15 minutes.",
         rules=dict(
             singleEntry=dict(status="multiple-entries", excerpt="Sunday through Friday - All players with 5 entries into daily tournaments will receive one (1) free entry into the Saturday $150 NLH - $2,000 Guarantee."),
             reEntry=dict(status="implied-multiple", excerpt="The same promotion counts five entries into the daily tournaments, so repeated entries are expected and rewarded."),
             addOn=dict(status="paid-chip-gratuity", excerpt="Each initial $120 buy-in is allocated as follows: $92 to Prize Pool, $13 House Fee and a onetime, voluntary gratuity of $11 which grants players an extra 10,000 chips.", source=MGM_STRUCT),
             fee=dict(status="confirmed", excerpt="Each initial $120 buy-in is allocated as follows: $92 to Prize Pool, $13 House Fee and a onetime, voluntary gratuity of $11 which grants players an extra 10,000 chips. $4 will fund Tournament Promotions.", source=MGM_STRUCT)),
         note="The published weekly schedule PDF is headed 'MGM Grand August Tournament Schedule', so the month on the sheet is not current."),
    dict(name="$120 No Limit Hold'em", days="Monday-Sunday", time="7:10 PM", weekdays=[0,1,2,3,4,5,6], buyIn=120, guarantee="",
         chips=25000, levelMin=15, source=MGM_SCHED, page=MGM_POKER, category="recurring",
         lateReg="Registration is open until Level 8. Level length 15 minutes.",
         rules=dict(
             singleEntry=dict(status="multiple-entries", excerpt="Sunday through Friday - All players with 5 entries into daily tournaments will receive one (1) free entry into the Saturday $150 NLH - $2,000 Guarantee."),
             reEntry=dict(status="implied-multiple", excerpt="The promotion counts five entries into the daily tournaments."),
             addOn=dict(status="paid-chip-gratuity", excerpt="A onetime, voluntary gratuity of $11 which grants players an extra 10,000 chips.", source=MGM_STRUCT),
             fee=dict(status="confirmed", excerpt="Each initial $120 buy-in is allocated as follows: $92 to Prize Pool, $13 House Fee and a onetime, voluntary gratuity of $11 which grants players an extra 10,000 chips.", source=MGM_STRUCT)),
         note="Registration is open until Level 8 per the $120 structure sheet."),
    dict(name="$120 No Limit Hold'em", days="Monday-Sunday", time="11:10 PM", weekdays=[0,1,2,3,4,5,6], buyIn=120, guarantee="",
         chips=25000, levelMin=15, source=MGM_SCHED, page=MGM_POKER, category="recurring",
         lateReg="Registration is open until Level 8. Level length 15 minutes.",
         rules=dict(
             singleEntry=dict(status="multiple-entries", excerpt="Sunday through Friday - All players with 5 entries into daily tournaments will receive one (1) free entry into the Saturday $150 NLH - $2,000 Guarantee."),
             reEntry=dict(status="implied-multiple", excerpt="The promotion counts five entries into the daily tournaments."),
             addOn=dict(status="paid-chip-gratuity", excerpt="A onetime, voluntary gratuity of $11 which grants players an extra 10,000 chips.", source=MGM_STRUCT),
             fee=dict(status="confirmed", excerpt="Each initial $120 buy-in is allocated as follows: $92 to Prize Pool, $13 House Fee and a onetime, voluntary gratuity of $11 which grants players an extra 10,000 chips.", source=MGM_STRUCT)),
         note="No guarantee is printed on the $120 sheet."),
    dict(name="$150 No Limit Hold'em $2,000 Guarantee", days="Saturday", time="11:10 AM", weekdays=[5], buyIn=150,
         guarantee=2000, chips=25000, levelMin=20, source=MGM_SCHED, page=MGM_POKER, category="recurring",
         lateReg="",
         rules=dict(
             singleEntry=dict(status="multiple-entries", excerpt="Sunday through Friday - All players with 5 entries into daily tournaments will receive one (1) free entry into the Saturday $150 NLH - $2,000 Guarantee."),
             reEntry=dict(status="implied-multiple", excerpt="The prize is earned by taking five entries in the daily tournaments."),
             addOn=dict(status="paid-chip-gratuity", excerpt="The $120 daily structure sheet provides a $11 optional gratuity for 10,000 extra chips; the $150 structure was not published on the poker-room page.", source=MGM_STRUCT),
             fee=dict(status="not-verified", excerpt="The $150 structure sheet was not published on the MGM Grand poker-room page.", source=MGM_POKER)),
         note="20-minute levels on Saturday per the published weekly schedule."),
]

# ------------------------------------------------- Caesars / Horseshoe / ARIA
CAESARS_EVENTS = [
    dict(name="No Limit Hold'em", days="Daily", weekdays=[0,1,2,3,4,5,6], time="10:00 AM", buyIn=100, guarantee=1000, chips=20000,
         levelMin=20, source=CAESARS_FLYER, page=CAESARS_POKER, category="extra", venue="caesars", lateReg="",
         rules=dict(
             singleEntry=dict(status="multiple-entries", excerpt="Participants may only register themselves, but may re-enter, by paying the entry fee, upon elimination within the first break of play.", source=CAESARS_FLYER, retrieved="2026-11-18"),
             reEntry=dict(status="allowed", excerpt="Participants may only register themselves, but may re-enter, by paying the entry fee, upon elimination within the first break of play.", source=CAESARS_FLYER, retrieved="2026-11-18"),
             addOn=dict(status="allowed", excerpt="All Tournaments feature a $50 add-on for 15,000 tournament chips that can only be taken at the first break.", source=CAESARS_FLYER, retrieved="2026-11-18"),
             fee=dict(status="confirmed", excerpt="Of the $100 buy in, $70 goes to the prize pool and $30 is held by Caesars Palace as a maintenance fee.", source=CAESARS_FLYER, retrieved="2026-11-18")),
         note="Official flyer: registration closes at the start of level seven (no clock time printed). The marketing article of 17 July 2026 says every event is $100; the flyer prices the 2 PM and 9 PM events at $160."),
    dict(name="No Limit Hold'em", days="Daily", weekdays=[0,1,2,3,4,5,6], time="2:00 PM", buyIn=160, guarantee=1000, chips=20000,
         levelMin=20, source=CAESARS_FLYER, page=CAESARS_POKER, category="extra", venue="caesars", lateReg="",
         rules=dict(
             singleEntry=dict(status="multiple-entries", excerpt="Participants may only register themselves, but may re-enter, by paying the entry fee, upon elimination within the first break of play.", source=CAESARS_FLYER, retrieved="2026-11-18"),
             reEntry=dict(status="allowed", excerpt="Participants may only register themselves, but may re-enter, by paying the entry fee, upon elimination within the first break of play.", source=CAESARS_FLYER, retrieved="2026-11-18"),
             addOn=dict(status="allowed", excerpt="All Tournaments feature a $50 add-on for 15,000 tournament chips that can only be taken at the first break.", source=CAESARS_FLYER, retrieved="2026-11-18"),
             fee=dict(status="confirmed", excerpt="Of the $160 buy in, $115 goes to the prize pool and $45 is held by Caesars Palace as a maintenance fee.", source=CAESARS_FLYER, retrieved="2026-11-18")),
         note="Official flyer: registration closes at the start of level seven (no clock time printed). The marketing article of 17 July 2026 says every event is $100; the flyer prices the 2 PM and 9 PM events at $160."),
    dict(name="No Limit Hold'em", days="Daily", weekdays=[0,1,2,3,4,5,6], time="6:00 PM", buyIn=100, guarantee=1000, chips=20000,
         levelMin=20, source=CAESARS_FLYER, page=CAESARS_POKER, category="extra", venue="caesars", lateReg="",
         rules=dict(
             singleEntry=dict(status="multiple-entries", excerpt="Participants may only register themselves, but may re-enter, by paying the entry fee, upon elimination within the first break of play.", source=CAESARS_FLYER, retrieved="2026-11-18"),
             reEntry=dict(status="allowed", excerpt="Participants may only register themselves, but may re-enter, by paying the entry fee, upon elimination within the first break of play.", source=CAESARS_FLYER, retrieved="2026-11-18"),
             addOn=dict(status="allowed", excerpt="All Tournaments feature a $50 add-on for 15,000 tournament chips that can only be taken at the first break.", source=CAESARS_FLYER, retrieved="2026-11-18"),
             fee=dict(status="confirmed", excerpt="Of the $100 buy in, $70 goes to the prize pool and $30 is held by Caesars Palace as a maintenance fee.", source=CAESARS_FLYER, retrieved="2026-11-18")),
         note="Official flyer: registration closes at the start of level seven (no clock time printed). The marketing article of 17 July 2026 says every event is $100; the flyer prices the 2 PM and 9 PM events at $160."),
    dict(name="No Limit Hold'em", days="Daily", weekdays=[0,1,2,3,4,5,6], time="9:00 PM", buyIn=160, guarantee=1000, chips=20000,
         levelMin=20, source=CAESARS_FLYER, page=CAESARS_POKER, category="extra", venue="caesars", lateReg="",
         rules=dict(
             singleEntry=dict(status="multiple-entries", excerpt="Participants may only register themselves, but may re-enter, by paying the entry fee, upon elimination within the first break of play.", source=CAESARS_FLYER, retrieved="2026-11-18"),
             reEntry=dict(status="allowed", excerpt="Participants may only register themselves, but may re-enter, by paying the entry fee, upon elimination within the first break of play.", source=CAESARS_FLYER, retrieved="2026-11-18"),
             addOn=dict(status="allowed", excerpt="All Tournaments feature a $50 add-on for 15,000 tournament chips that can only be taken at the first break.", source=CAESARS_FLYER, retrieved="2026-11-18"),
             fee=dict(status="confirmed", excerpt="Of the $160 buy in, $115 goes to the prize pool and $45 is held by Caesars Palace as a maintenance fee.", source=CAESARS_FLYER, retrieved="2026-11-18")),
         note="Official flyer: registration closes at the start of level seven (no clock time printed). The marketing article of 17 July 2026 says every event is $100; the flyer prices the 2 PM and 9 PM events at $160."),
]

HORSESHOE_EVENTS = [
    dict(name="No Limit Hold'em daily tournament", days="Daily", weekdays=[0, 1, 2, 3, 4, 5, 6], time="9:00 AM",
         buyIn="", guarantee="", chips="", levelMin="", source=CAESARS_POKER, page=CAESARS_POKER,
         category="recurring", venue="horseshoe", lateReg="",
         rules=dict(
             singleEntry=dict(status="not-verified", excerpt="The official Caesars page states that Horseshoe runs six daily No-Limit Hold'em games at 9 a.m., 11 a.m., 2 p.m., 5 p.m., 8 p.m. and 11 p.m., but publishes no buy-in, structure or entry terms for them."),
             reEntry=dict(status="not-verified", excerpt="No entry terms are published on the official page."),
             addOn=dict(status="not-verified", excerpt="No entry terms are published on the official page."),
             fee=dict(status="not-verified", excerpt="No buy-in is published on the official page.")),
         note="Buy-in, level structure and guarantee are not published for this slot."),


    dict(name="No Limit Hold'em daily tournament", days="Daily", weekdays=[0, 1, 2, 3, 4, 5, 6], time="11:00 AM",
         buyIn="", guarantee="", chips="", levelMin="", source=CAESARS_POKER, page=CAESARS_POKER,
         category="recurring", venue="horseshoe", lateReg="",
         rules=dict(
             singleEntry=dict(status="not-verified", excerpt="The official Caesars page lists this Horseshoe start time but publishes no buy-in, structure or entry terms for it."),
             reEntry=dict(status="not-verified", excerpt="No entry terms are published on the official page."),
             addOn=dict(status="not-verified", excerpt="No entry terms are published on the official page."),
             fee=dict(status="not-verified", excerpt="No buy-in is published on the official page.")),
         note="Buy-in, level structure and guarantee are not published for this slot."),


    dict(name="No Limit Hold'em daily tournament", days="Daily", weekdays=[0, 1, 2, 3, 4, 5, 6], time="2:00 PM",
         buyIn="", guarantee="", chips="", levelMin="", source=CAESARS_POKER, page=CAESARS_POKER,
         category="recurring", venue="horseshoe", lateReg="",
         rules=dict(
             singleEntry=dict(status="not-verified", excerpt="The official Caesars page lists this Horseshoe start time but publishes no buy-in, structure or entry terms for it."),
             reEntry=dict(status="not-verified", excerpt="No entry terms are published on the official page."),
             addOn=dict(status="not-verified", excerpt="No entry terms are published on the official page."),
             fee=dict(status="not-verified", excerpt="No buy-in is published on the official page.")),
         note="Buy-in, level structure and guarantee are not published for this slot."),


    dict(name="No Limit Hold'em daily tournament", days="Daily", weekdays=[0, 1, 2, 3, 4, 5, 6], time="5:00 PM",
         buyIn="", guarantee="", chips="", levelMin="", source=CAESARS_POKER, page=CAESARS_POKER,
         category="recurring", venue="horseshoe", lateReg="",
         rules=dict(
             singleEntry=dict(status="not-verified", excerpt="The official Caesars page lists this Horseshoe start time but publishes no buy-in, structure or entry terms for it."),
             reEntry=dict(status="not-verified", excerpt="No entry terms are published on the official page."),
             addOn=dict(status="not-verified", excerpt="No entry terms are published on the official page."),
             fee=dict(status="not-verified", excerpt="No buy-in is published on the official page.")),
         note="Buy-in, level structure and guarantee are not published for this slot."),


    dict(name="No Limit Hold'em daily tournament", days="Daily", weekdays=[0, 1, 2, 3, 4, 5, 6], time="8:00 PM",
         buyIn="", guarantee="", chips="", levelMin="", source=CAESARS_POKER, page=CAESARS_POKER,
         category="recurring", venue="horseshoe", lateReg="",
         rules=dict(
             singleEntry=dict(status="not-verified", excerpt="The official Caesars page lists this Horseshoe start time but publishes no buy-in, structure or entry terms for it."),
             reEntry=dict(status="not-verified", excerpt="No entry terms are published on the official page."),
             addOn=dict(status="not-verified", excerpt="No entry terms are published on the official page."),
             fee=dict(status="not-verified", excerpt="No buy-in is published on the official page.")),
         note="Buy-in, level structure and guarantee are not published for this slot."),


    dict(name="No Limit Hold'em daily tournament", days="Daily", weekdays=[0, 1, 2, 3, 4, 5, 6], time="11:00 PM",
         buyIn="", guarantee="", chips="", levelMin="", source=CAESARS_POKER, page=CAESARS_POKER,
         category="recurring", venue="horseshoe", lateReg="",
         rules=dict(
             singleEntry=dict(status="not-verified", excerpt="The official Caesars page lists this Horseshoe start time but publishes no buy-in, structure or entry terms for it."),
             reEntry=dict(status="not-verified", excerpt="No entry terms are published on the official page."),
             addOn=dict(status="not-verified", excerpt="No entry terms are published on the official page."),
             fee=dict(status="not-verified", excerpt="No buy-in is published on the official page.")),
         note="Buy-in, level structure and guarantee are not published for this slot."),
]

ARIA_EVENTS = [
    dict(name="ARIA daily poker tournament", days="Daily (per undated official guide)", time="1:00 PM", weekdays=[0,1,2,3,4,5,6],
         buyIn="", guarantee="", chips="", levelMin="", source=ARIA_GUIDE, page=ARIA_POKER,
         category="recurring", venue="aria", lateReg="",
         rules=dict(
             singleEntry=dict(status="not-verified", excerpt="The official guide is undated and the current poker page asks guests to call or check @ARIAPoker to confirm whether daily events are running."),
             reEntry=dict(status="not-verified", excerpt="No entry terms are published in the reviewed material."),
             addOn=dict(status="not-verified", excerpt="No entry terms are published in the reviewed material."),
             fee=dict(status="not-verified", excerpt="No buy-in is published in the reviewed material.")),
         note="Undated cadence only. No date-specific event, buy-in or guarantee is published."),
    dict(name="ARIA nightly poker tournament", days="Nightly (per undated official guide)", time="7:00 PM", weekdays=[0,1,2,3,4,5,6],
         buyIn="", guarantee="", chips="", levelMin="", source=ARIA_GUIDE, page=ARIA_POKER,
         category="recurring", venue="aria", lateReg="",
         rules=dict(
             singleEntry=dict(status="not-verified", excerpt="The official guide is undated and the current poker page asks guests to call or check @ARIAPoker to confirm whether daily events are running."),
             reEntry=dict(status="not-verified", excerpt="No entry terms are published in the reviewed material."),
             addOn=dict(status="not-verified", excerpt="No entry terms are published in the reviewed material."),
             fee=dict(status="not-verified", excerpt="No buy-in is published in the reviewed material.")),
         note="Undated cadence only."),
]


def wpt_slot(date: str, time: str) -> str:
    """Normalise a schedule row's date and start time to a 'YYYY-MM-DD HH:MM' 24-hour slot.

    The structures document prints 11 a.m. / 1 p.m. and the schedule transcript
    stores 11:00 AM / 1:00 PM, so both sides are compared as 24-hour clock slots.
    """
    clock, meridiem = time.strip().split()
    hh, mm = (int(x) for x in clock.split(":"))
    hh = hh % 12 + (12 if meridiem.upper() == "PM" else 0)
    return f"{date} {hh:02d}:{mm:02d}"


def wpt_section_for(date: str, time: str, name: str, buy_in):
    """The structures section a WPT schedule row belongs to, or None.

    A row matches only when its buy-in, its printed name and its exact date and
    start slot all agree with the section, so no row can inherit another event's
    entry rules by sharing part of a name.  Day 2, Day 3, final table and
    satellite rows never match: those sections print no restart rules.
    """
    if buy_in in ("", "-", None):
        return None
    slot = wpt_slot(date, time)
    buy = str(buy_in)
    flight = re.search(r" Day 1([A-F])$", name)
    base = name[: flight.start()] if flight else name
    for (sec_buy, sec_name), sec in WPT_SHEET_SECTIONS.items():
        if sec_buy != buy:
            continue
        if sec_name != base and not (flight and sec_name == base + " Day 1"):
            continue
        if slot in sec["dates"]:
            return sec
    return None
