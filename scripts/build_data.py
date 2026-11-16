#!/usr/bin/env python3
"""Build site/data/*.json from official-source extracts.

Inputs (all in-repo):
  data/venetian_flights.json     - Venetian DSE IV flights parsed from the official schedule PDF
  data/venetian_restarts.json    - Day-2/Day-3 restart rows from the same PDF
  data/sheet_extracts.jsonl      - per-sheet facts read from the 37 official structure PDFs (2026-11-16)
  encoded constants below        - Wynn / Bellagio / ARIA / hotel facts checked 2026-11-16

Outputs: site/data/{tournaments,hotels,rates,routes,sources,flags,questions,suggestions,dayplan}.json
Every row carries source URL(s) and a lastChecked date. Unknown values are null / "" and flagged.
"""
import json, re, os
from datetime import date, datetime, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TODAY = "2026-11-16"

def load(name):
    with open(os.path.join(ROOT, name)) as f:
        return json.load(f)

def load_sheets():
    out = {}
    with open(os.path.join(ROOT, "data", "sheet_extracts.jsonl")) as f:
        for line in f:
            line = line.strip()
            if line:
                s = json.loads(line)
                out[s["sheet"]] = s
    return out

VEN_DSE_HTML = "https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html"
VEN_DSE_PDF = "https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/dse-nov-2026-schedule.pdf"
def sheet_url(n):
    return ("https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/"
            f"dse_nov_2026-structure_{n}.pdf")

# Structure-sheet mapping read from the official DSE IV web schedule on 2026-11-16.
# event_no -> {flight_key: sheet_number}; flight_key matches the 1A/1B/... suffix or "" for single-start.
SHEET_MAP = {
    "1": {"1A": 10, "1B": 9, "1C": 10, "1D": 9},
    "2": {"": 5}, "3": {"": 18}, "4": {"": 18}, "5": {"": 18}, "6": {"": 29},
    "7": {"1A": 2, "1B": 2},
    "8": {"": 30},
    "9": {"": 1}, "10": {"": 6}, "11": {"": 1}, "12": {"": 5}, "13": {"": 1},
    "14": {"": 7}, "15": {"": 1}, "16": {"": 11}, "17": {"": 26}, "18": {"": 8},
    "19": {"1A": 3, "1B": 3, "1C": 3},
    "20": {"": 22}, "21": {"": 1}, "22": {"": 1}, "23": {"": 1}, "24": {"": 17}, "25": {"": 1},
    "26": {"1A": 12, "1B": 13, "1C": 12, "1D": 13, "1E": 12, "1F": 14},
    "27": {"": 28}, "28": {"": 7}, "29": {"": 15}, "30": {"": 11}, "31": {"": 15},
    "32": {"": 17}, "33": {"": 19}, "34": {"": 15}, "35": {"": 31}, "36": {"": 16},
    "37": {"": 19}, "38": {"": 15},
    "39": {"": 32},
    "40": {"": 27}, "41": {"": 24}, "42": {"": 15}, "43": {"": 33}, "44": {"": 24},
    "45": {"": 25}, "46": {"": 25},
    "47": {"1A": 21, "1B": 37},
    "48": {"": 25},
    "49": {"1A": 20, "1B": 20},
    "50": {"": 15}, "51": {"": 15}, "52": {"": 34}, "53": {"": 15}, "54": {"": 11},
    "55": {"": 15},
    "56": {"1A": 35, "1B": 36, "1C": 35, "1D": 36, "1E": 35},
    "57": {"": 23}, "58": {"": 8},
    "59": {"1A": 4, "1B": 4, "1C": 4},
    "60": {"": 1}, "61": {"": 1}, "62": {"": 1}, "63": {"": 7}, "64": {"": 1},
}

MULTI_FLIGHT = {"1", "7", "19", "26", "47", "49", "56", "59"}          # multiple entries possible across flights
SAT_EVENTS = {"33", "37", "41", "44", "45", "46", "48"}                 # satellites
SENIOR_EVENTS = {"24", "32", "49"}
LADIES_EVENTS = {"33", "35", "37", "39", "43"}
TAG_TEAM_EVENTS = {"35"}
AMBIGUOUS_EVENTS = {"18", "58"}   # sheet 8 discount clause references "subsequent buy-ins"

def flight_key(name):
    m = re.search(r"\b(1[A-F])\b", name.upper().replace("DAY ", "DAY "))
    m2 = re.search(r"\b(?:1|DAY)\s*([A-F])\b", name.upper())
    m3 = re.search(r"\b1([A-F])\b", name.upper())
    if m3:
        return "1" + m3.group(1)
    return ""

def money(x):
    if x is None:
        return None
    return int(round(float(x)))

def parse_time(t):
    """'11:10 AM' -> minutes since midnight."""
    if not t:
        return None
    m = re.match(r"(\d{1,2}):(\d{2})\s*(AM|PM)", t.strip(), re.I)
    if not m:
        return None
    h, mm, ap = int(m.group(1)), int(m.group(2)), m.group(3).upper()
    if ap == "PM" and h != 12:
        h += 12
    if ap == "AM" and h == 12:
        h = 0
    return h * 60 + mm

def fmt_time(mins):
    if mins is None:
        return None
    ap = "AM" if mins < 720 else "PM"
    h = mins // 60 % 12 or 12
    return f"{h}:{mins % 60:02d} {ap}"

def build_venetian(sheets):
    rows = []
    flights = load("data/venetian_flights.json")
    restarts = load("data/venetian_restarts.json")

    def sheet_for(ev_no, name):
        key = flight_key(name)
        smap = SHEET_MAP.get(str(ev_no), {})
        if key in smap:
            return smap[key]
        if "" in smap:
            return smap[""]
        return None

    for r in flights:
        ev = str(r["event_no"])
        name = r["name"]
        key = flight_key(name)
        sheet_no = sheet_for(ev, name)
        sh = sheets.get(sheet_no)
        buy_in = money(r.get("buy_in"))
        guarantee = money(r.get("guarantee"))
        is_sat = bool(r.get("satellite")) or ev in SAT_EVENTS
        is_flight = ev in MULTI_FLIGHT and key != ""

        # classification
        if is_sat:
            bucket = "satellite"
        elif ev in MULTI_FLIGHT:
            bucket = "spend-more"          # multiple entries possible across flights
        elif ev in TAG_TEAM_EVENTS:
            bucket = "review"              # team format; one entry per team, needs player-policy review
        elif ev in AMBIGUOUS_EVENTS:
            bucket = "review"              # sheet references "subsequent buy-ins"
        else:
            bucket = "single-path"

        # structured entry-rule fields (from the official sheet; absence of a clause is reported as such)
        entry = {
            "singleEntryPrinted": "no",
            "reentry": "no clause printed" if sh and sh.get("entryWording") == "none" else "",
            "rebuy": "no clause printed" if sh and sh.get("entryWording") == "none" else "",
            "addon": "no clause printed" if sh and sh.get("entryWording") == "none" else "",
            "excerpt": (sh or {}).get("entryExcerpt", ""),
            "sheetUrl": sheet_url(sheet_no) if sheet_no else "",
            "retrieved": TODAY if sh else "",
        }
        if sh and sh.get("entryWording") == "flight-limited":
            entry["reentry"] = "per flight until bagged (multi-flight event)"
            entry["rebuy"] = "no clause printed"
            entry["addon"] = "no clause printed"
        if ev in AMBIGUOUS_EVENTS:
            entry["reentry"] = "ambiguous: sheet references 'subsequent buy-ins'"
        if ev in TAG_TEAM_EVENTS:
            entry["singleEntryPrinted"] = "no (one entry per team)"

        # fee split
        house_fee = (sh or {}).get("houseFee")
        prize_share = (sh or {}).get("prizeShare")
        staff_fee = 0
        lips_fee = None
        if sheet_no in (31, 32, 33):
            lips_fee = 10 if sheet_no in (31, 33) else 20

        ratio = round(guarantee / buy_in, 1) if guarantee and buy_in else None

        # bounty guarantees include total bounties (verified per sheet wording) — label separately
        guarantee_note = (sh or {}).get("guaranteeNote", "")
        if sheet_no in (1, 8, 11, 15, 16, 26, 27, 30, 33, 34) and guarantee and not guarantee_note:
            guarantee_note = "Bounty guarantee = prize pool + total bounties (per sheet wording)"

        # duration estimate from the sheet (levels x length + breaks) — labelled as an estimate
        est_hours = None
        late_reg_min = None
        if sh:
            lvl = sh.get("levelMinutes") or 30
            lvls = sh.get("levels") or 28
            brk = (sh.get("breaks15") or 0) * 15
            extra = 0
            if sh.get("levelNote"):
                extra = 0  # RaceDay 20/15 handled below
            est_min = lvls * lvl + brk
            if sheet_no == 18:  # 20/15-minute RaceDay structure
                est_min = 6 * 20 + 22 * 15 + brk
            est_hours = round(est_min / 60, 1)
            lr = sh.get("lateReg", "")
            m = re.search(r"\((?:~\s*)?(\d{1,2}:\d{2}\s*[AP]M)", lr)
            if m:
                late_reg_min = parse_time(m.group(1).replace(" ", " ", 1))

        status = "verified" if sh else "unverified"
        label = {
            "single-path": "Sheet reviewed — no re-entry/rebuy/add-on wording printed",
            "spend-more": "Multi-flight — multiple entries possible across flights",
            "satellite": "Satellite — awards seats, not cash",
            "review": "Review — ambiguous or special entry policy",
        }[bucket]

        rows.append({
            "id": f"dse-{ev}-{key or 'main'}-{r['date']}",
            "series": "Venetian DeepStack Extravaganza IV",
            "venue": "venetian",
            "venueName": "The Venetian Poker Room",
            "date": r["date"],
            "weekday": r.get("weekday", ""),
            "time": r.get("time", ""),
            "timeMin": parse_time(r.get("time", "")),
            "eventNo": ev,
            "flight": key,
            "name": name.title().replace("Nlh", "NLH").replace("Plo", "PLO"),
            "rawName": name,
            "game": "PLO" if "PLO" in name.upper() or "OMAHA" in name.upper() else "NLH",
            "buyIn": buy_in,
            "houseFee": house_fee,
            "staffFee": staff_fee,
            "lipsFee": lips_fee,
            "prizeShare": prize_share,
            "guarantee": guarantee,
            "guaranteeNote": guarantee_note,
            "ratio": ratio,
            "bounty": (sh or {}).get("bounty") or "",
            "chips": r.get("chips") or (sh or {}).get("chips"),
            "levelMinutes": (sh or {}).get("levelMinutes"),
            "levelNote": (sh or {}).get("levelNote", ""),
            "levels": (sh or {}).get("levels"),
            "lateReg": (sh or {}).get("lateReg", ""),
            "lateRegTime": fmt_time(late_reg_min),
            "lateRegMin": late_reg_min,
            "estDurationHours": est_hours,
            "pays": (sh or {}).get("pays", ""),
            "entry": entry,
            "bucket": bucket,
            "bucketLabel": label,
            "restricted": ("50+ only" if ev in SENIOR_EVENTS else
                           "Female players only" if ev in LADIES_EVENTS and ev not in ("43",) else
                           "Tag team" if ev in TAG_TEAM_EVENTS else ""),
            "kind": "flight" if is_flight else ("satellite" if is_sat else "one-day"),
            "scheduleSource": VEN_DSE_HTML,
            "structureSource": sheet_url(sheet_no) if sheet_no else "",
            "lastChecked": TODAY,
            "status": status,
            "notes": [],
        })

    # restarts (Day 2 / Day 3 / Final Table rows)
    for ridx, r in enumerate(restarts):
        ev = str(r["event_no"])
        rname = (r.get("name") or "restart").lower().replace(" ", "-").replace("/", "-")[:24]
        rows.append({
            "id": f"dse-{ev}-{rname}-{r['date']}-{ridx}",
            "series": "Venetian DeepStack Extravaganza IV",
            "venue": "venetian",
            "venueName": "The Venetian Poker Room",
            "date": r["date"],
            "weekday": r.get("weekday", ""),
            "time": r.get("time", ""),
            "timeMin": parse_time(r.get("time", "")),
            "eventNo": ev,
            "flight": "restart",
            "name": (r.get("name") or "").title().replace("Nlh", "NLH").replace("Day 2", "Day 2"),
            "rawName": r.get("name", ""),
            "game": "NLH",
            "buyIn": None,
            "houseFee": None,
            "staffFee": None,
            "lipsFee": None,
            "prizeShare": None,
            "guarantee": None,
            "guaranteeNote": "",
            "ratio": None,
            "bounty": "",
            "chips": None,
            "levelMinutes": None,
            "levelNote": "",
            "levels": None,
            "lateReg": "",
            "lateRegTime": None,
            "lateRegMin": None,
            "estDurationHours": None,
            "pays": "",
            "entry": {"singleEntryPrinted": "n/a", "reentry": "n/a (restart)", "rebuy": "n/a", "addon": "n/a",
                      "excerpt": "Restart for players who bagged chips; no new entries.",
                      "sheetUrl": "", "retrieved": TODAY},
            "bucket": "restart",
            "bucketLabel": "Day restart — no new entries",
            "restricted": "",
            "kind": "restart",
            "scheduleSource": VEN_DSE_HTML,
            "structureSource": "",
            "lastChecked": TODAY,
            "status": "verified",
            "notes": [],
        })
    return rows


# ---------------------------------------------------------------- Wynn data (checked 2026-11-16)
WYNN_POSTER = "https://cdn.wynnresorts.com/image/upload/v1752011166/visitwynn_pdfs_files/Poker/Daily%20Tournaments/poker-daily-tournament-poster.pdf"
WYNN_DAILY_STRUCT = "https://cdn.wynnresorts.com/image/upload/v1752011191/visitwynn_pdfs_files/Poker/Daily%20Tournaments/Poker-All_Daily_Structures.pdf"
WYNN_WPT_SCHED = "https://cdn.wynnresorts.com/image/upload/v1757097329/visitwynn_pdfs_files/Poker/WPT/WPT_World_Championship_Schedule.pdf"
WYNN_WPT_STRUCT = "https://cdn.wynnresorts.com/image/upload/v1750864036/visitwynn_pdfs_files/Poker/WPT/WPT_World_Championship_Structures.pdf"
WYNN_POKER = "https://www.wynnlasvegas.com/casino/poker"

def build_wynn():
    rows = []
    def row(**kw):
        base = dict(series="Wynn daily tournaments", venue="wynn", venueName="Wynn Poker Room (Encore)",
                    weekday="", timeMin=parse_time(kw.get("time", "")), levelNote="", pays="",
                    lateRegMin=None, lateRegTime="", estDurationHours=None, restricted="",
                    scheduleSource=WYNN_POSTER, lastChecked=TODAY, status="verified", notes=[])
        base.update(kw)
        rows.append(base)

    # Daily tournaments — all confirmed re-entry (and add-ons on most) from the official structures PDF.
    row(id="wynn-daily-mon-thu", date="Monday–Thursday (recurring)", time="12:00 PM",
        eventNo="", flight="", name="Daily $200 NLH $10K GTD", game="NLH", buyIn=200,
        houseFee=26, staffFee=12, lipsFee=None, prizeShare=162, guarantee=10000,
        guaranteeNote="", ratio=50.0, bounty="", chips=25000, levelMinutes=30, levels=28,
        lateReg="Registration and re-entries until start of level 9 (~4:30 PM)", lateRegTime="4:30 PM",
        entry={"singleEntryPrinted": "no", "reentry": "YES — entry fee, as well as the re-entry fee, is $200",
               "rebuy": "no clause printed", "addon": "no clause printed",
               "excerpt": "The Tournament entry fee, as well as the re-entry fee, is $200 ... Registration and re-entries will be available until the start of level 9 (approximately 4:30 p.m.).",
               "sheetUrl": WYNN_DAILY_STRUCT, "retrieved": TODAY},
        bucket="spend-more", bucketLabel="Re-entry allowed (official terms)",
        kind="one-day", structureSource=WYNN_DAILY_STRUCT,
        notes=["Suspended during Wynn Signature, Wynn Millions and Classic series (official)."])

    row(id="wynn-daily-fri", date="Friday (recurring)", time="12:00 PM",
        eventNo="", flight="", name="Daily $240 NLH Rebuy & Add-on $40K GTD", game="NLH", buyIn=240,
        houseFee=35, staffFee=15, lipsFee=None, prizeShare=190, guarantee=40000,
        guaranteeNote="", ratio=166.7, bounty="", chips=25000, levelMinutes=30, levels=28,
        lateReg="Registration, rebuys and add-ons until start of level 9 (~4:30 PM)",
        lateRegTime="4:30 PM",
        entry={"singleEntryPrinted": "no",
               "reentry": "Re-entry is NOT allowed (explicit)",
               "rebuy": "YES — unlimited $200 rebuys for 25,000 chips at 15,000 or less",
               "addon": "YES — one $100 add-on for 15,000 chips",
               "excerpt": "Registration, rebuys and add-ons will be available until the start of level 9 (approximately 4:30 p.m.). Re-entry is NOT allowed. ... Unlimited $200 rebuys for 25,000 tournament chips are available any time a player is at 15,000 chips or less. One (1) $100 add-on for 15,000 tournament chips is available any time until the end of registration.",
               "sheetUrl": WYNN_DAILY_STRUCT, "retrieved": TODAY},
        bucket="spend-more", bucketLabel="Rebuys + add-on (official terms)",
        kind="one-day", structureSource=WYNN_DAILY_STRUCT)

    row(id="wynn-daily-sat", date="Saturday (recurring)", time="12:00 PM",
        eventNo="", flight="", name="Daily $200 NLH $25K GTD", game="NLH", buyIn=200,
        houseFee=26, staffFee=12, lipsFee=None, prizeShare=162, guarantee=25000,
        guaranteeNote="", ratio=125.0, bounty="", chips=25000, levelMinutes=30, levels=28,
        lateReg="Registration, re-entries, and one add-on per entry until start of level 11 (~5:30 PM)",
        lateRegTime="5:30 PM",
        entry={"singleEntryPrinted": "no", "reentry": "YES — entry fee, as well as the re-entry fee, is $200",
               "rebuy": "no clause printed",
               "addon": "YES — one $100 add-on per entry for 25,000 chips",
               "excerpt": "Registration, re-entries, and one (1) add-on per entry will be available until the start of level 11 (approximately 5:30 p.m.).",
               "sheetUrl": WYNN_DAILY_STRUCT, "retrieved": TODAY},
        bucket="spend-more", bucketLabel="Re-entry + add-on (official terms)",
        kind="one-day", structureSource=WYNN_DAILY_STRUCT)

    row(id="wynn-daily-sun", date="Sunday (recurring)", time="12:00 PM",
        eventNo="", flight="", name="Daily $200 NLH $25K GTD", game="NLH", buyIn=200,
        houseFee=26, staffFee=12, lipsFee=None, prizeShare=162, guarantee=25000,
        guaranteeNote="", ratio=125.0, bounty="", chips=25000, levelMinutes=30, levels=28,
        lateReg="Registration, re-entries, and one add-on per entry until start of level 11 (~5:30 PM)",
        lateRegTime="5:30 PM",
        entry={"singleEntryPrinted": "no", "reentry": "YES — entry fee, as well as the re-entry fee, is $200",
               "rebuy": "no clause printed",
               "addon": "YES — one $100 add-on per entry for 25,000 chips",
               "excerpt": "Registration, re-entries, and one (1) add-on per entry will be available until the start of level 11 (approximately 5:30 p.m.).",
               "sheetUrl": WYNN_DAILY_STRUCT, "retrieved": TODAY},
        bucket="spend-more", bucketLabel="Re-entry + add-on (official terms)",
        kind="one-day", structureSource=WYNN_DAILY_STRUCT)

    row(id="wynn-nightly", date="Nightly Monday–Sunday (recurring)", time="6:00 PM",
        eventNo="", flight="", name="Nightly $160 NLH $10K GTD", game="NLH", buyIn=160,
        houseFee=20, staffFee=10, lipsFee=None, prizeShare=130, guarantee=10000,
        guaranteeNote="", ratio=62.5, bounty="", chips=25000, levelMinutes=20, levels=30,
        lateReg="Registration, re-entries, and one add-on per entry until start of level 9 (~9:00 PM)",
        lateRegTime="9:00 PM",
        entry={"singleEntryPrinted": "no", "reentry": "YES — entry fee, as well as the re-entry fee, is $160",
               "rebuy": "no clause printed",
               "addon": "YES — one $100 add-on per entry for 25,000 chips",
               "excerpt": "Registration, re-entries, and one (1) add-on per entry will be available until the start of level 9 (approximately 9:00 p.m.).",
               "sheetUrl": WYNN_DAILY_STRUCT, "retrieved": TODAY},
        bucket="spend-more", bucketLabel="Re-entry + add-on (official terms)",
        kind="one-day", structureSource=WYNN_DAILY_STRUCT)

    # WPT World Championship festival (Nov 27 – Dec 21, 2026) — verified samples of the official structures doc.
    wpt = [
        dict(id="wpt-600-nlh", date="Nov 27–30, 2026", time="11:00 AM / 5:00 PM flights",
             name="$600 NLH $400K GTD (6 flights)", buyIn=600, houseFee=65, staffFee=25, prizeShare=510,
             guarantee=400000, ratio=666.7, chips=40000,
             entryRe="YES — unlimited re-entry per starting flight until start of level 9",
             excerpt="Unlimited re-entry for each starting flight will be available until the start of level 9."),
        dict(id="wpt-600-torse", date="Nov 27, 2026", time="12:00 PM",
             name="$600 TORSE (mixed)", buyIn=600, houseFee=65, staffFee=25, prizeShare=510,
             guarantee=None, ratio=None, chips=35000,
             entryRe="YES — unlimited re-entry until start of level 9",
             excerpt="Unlimited re-entry will be available until the start of level 9."),
        dict(id="wpt-400-plo", date="Nov 27, 2026", time="1:00 PM",
             name="$400 PLO", buyIn=400, houseFee=45, staffFee=18, prizeShare=337,
             guarantee=None, ratio=None, chips=30000,
             entryRe="YES — unlimited re-entry until start of level 9 (~5:30 PM)",
             excerpt="Unlimited re-entry will be available until the start of level 9 (approximately 5:30 p.m.)."),
        dict(id="wpt-600-mtd", date="Nov 28 & Dec 20, 2026", time="12:00 PM / 1:00 PM",
             name="$600 Mixed Triple Draw (A-5, 2-7, Badugi)", buyIn=600, houseFee=65, staffFee=25, prizeShare=510,
             guarantee=None, ratio=None, chips=35000,
             entryRe="YES — unlimited re-entry until start of level 9",
             excerpt="Unlimited re-entry will be available until the start of level 9."),
        dict(id="wpt-800-nlh", date="Nov 30–Dec 4, 2026", time="11:00 AM / 5:00 PM flights",
             name="$800 NLH $1M GTD (6 flights)", buyIn=800, houseFee=72, staffFee=33, prizeShare=695,
             guarantee=1000000, ratio=1250.0, chips=40000,
             entryRe="YES — unlimited re-entry per starting flight until start of level 9",
             excerpt="Unlimited re-entry for each starting flight will be available until the start of level 9."),
        dict(id="wpt-600-o8", date="Nov 30, 2026", time="12:00 PM",
             name="$600 Limit Omaha 8", buyIn=600, houseFee=65, staffFee=25, prizeShare=510,
             guarantee=None, ratio=None, chips=35000,
             entryRe="YES — unlimited re-entry until start of level 9",
             excerpt="Unlimited re-entry will be available until the start of level 9."),
        dict(id="wpt-600-o8s8", date="Dec 1, 2026", time="12:00 PM",
             name="$600 Limit Omaha 8 / Stud 8", buyIn=600, houseFee=65, staffFee=25, prizeShare=510,
             guarantee=None, ratio=None, chips=35000,
             entryRe="YES — unlimited re-entry until start of level 9",
             excerpt="Unlimited re-entry will be available until the start of level 9."),
        dict(id="wpt-1100-plo", date="Dec 1, 2026", time="1:00 PM",
             name="$1,100 PLO", buyIn=1100, houseFee=85, staffFee=45, prizeShare=975,
             guarantee=None, ratio=None, chips=30000,
             entryRe="YES — unlimited re-entry until start of level 9 (~5:30 PM)",
             excerpt="Unlimited re-entry will be available until the start of level 9 (approximately 5:30 p.m.)."),
        dict(id="wpt-1600-nlh", date="Dec 3–5, 2026", time="11:00 AM flights",
             name="$1,600 NLH $1M GTD (2 flights)", buyIn=1600, houseFee=120, staffFee=50, prizeShare=1430,
             guarantee=1000000, ratio=625.0, chips=40000,
             entryRe="YES — unlimited re-entry per starting flight until start of level 10",
             excerpt="Unlimited re-entry for each starting flight will be available until the start of level 10."),
        dict(id="wpt-600-horse", date="Dec 4, 2026", time="12:00 PM",
             name="$600 HORSE", buyIn=600, houseFee=65, staffFee=25, prizeShare=510,
             guarantee=None, ratio=None, chips=35000,
             entryRe="YES — unlimited re-entry until start of level 9 (~4:30 PM)",
             excerpt="Unlimited re-entry will be available until the start of level 9 (approximately 4:30 p.m.)."),
        dict(id="wpt-prime", date="Dec 5–12, 2026", time="11:00 AM flights",
             name="$1,100 WPT Prime Championship $5M GTD (4 flights)", buyIn=1100, houseFee=90, staffFee=40, prizeShare=970,
             guarantee=5000000, ratio=4545.5, chips=40000,
             entryRe="YES — one entry and one re-entry per starting flight until start of level 10 (~6:45 PM)",
             excerpt="One (1) Entry and One (1) re-entry for each starting flight will be available until the start of level 10 (approximately 6:45 p.m.). $10,400 will be withheld from the prize pool and issued to first place in the form of an entry to the December 2027 WPT World Championship."),
        dict(id="wpt-600-turbo", date="Dec 5–9, 12, 14 & 21, 2026", time="9:00 PM (Dec 21: 6:00 PM)",
             name="$600 NLH Turbo $50K GTD", buyIn=600, houseFee=60, staffFee=25, prizeShare=515,
             guarantee=50000, ratio=83.3, chips=30000,
             entryRe="YES — unlimited re-entry until start of level 9",
             excerpt="Unlimited re-entry will be available until the start of level 9."),
        dict(id="wpt-1600-plo-mb", date="Dec 6–7, 2026", time="11:00 AM / 6:00 PM flights",
             name="$1,600 PLO Mystery Bounty $500K GTD (2 flights)", buyIn=1600, houseFee=120, staffFee=50, prizeShare=930,
             guarantee=5000000 and 500000, ratio=312.5, chips=40000,
             entryRe="YES — unlimited re-entry per starting flight until start of level 10",
             excerpt="Unlimited re-entry for each starting flight will be available until the start of level 10. $1,600 Buy-in = $930 (Tournament Prize Pool) + $500 (Mystery Bounty Prize Pool) + $120 (Tournament Fee) + $50 (Poker Staff Service Charge)."),
    ]
    for e in wpt:
        row(id=e["id"], date=e["date"], time=e["time"], eventNo="", flight="",
            name=e["name"], game="NLH" if "NLH" in e["name"] or "Prime" in e["name"] or "Championship" in e["name"] else "Mixed/PLO",
            buyIn=e["buyIn"], houseFee=e["houseFee"], staffFee=e["staffFee"], lipsFee=None,
            prizeShare=e["prizeShare"], guarantee=e["guarantee"], guaranteeNote="",
            ratio=e["ratio"], bounty="Mystery Bounty" if "Mystery" in e["name"] else "",
            chips=e["chips"], levelMinutes=40 if "Prime" in e["name"] else 30,
            lateReg="see excerpt", lateRegTime=None,
            entry={"singleEntryPrinted": "no", "reentry": e["entryRe"], "rebuy": "no clause printed",
                   "addon": "no clause printed", "excerpt": e["excerpt"],
                   "sheetUrl": WYNN_WPT_STRUCT, "retrieved": TODAY},
            bucket="spend-more", bucketLabel="WPT festival — re-entry (official terms)",
            kind="festival", structureSource=WYNN_WPT_STRUCT, scheduleSource=WYNN_WPT_SCHED,
            notes=["WPT World Championship festival, Nov 27–Dec 21, 2026."])

    # Unextracted WPT headline events — flagged, entry terms blank on purpose.
    for e in [
        dict(id="wpt-super-gold", date="Dec 10–14, 2026", name="Super Gold Million $400 $3M GTD", buyIn=400, guarantee=3000000),
        dict(id="wpt-world-champ", date="Dec 13–20, 2026", name="WPT World Championship $10,400", buyIn=10400, guarantee=None),
    ]:
        row(id=e["id"], date=e["date"], time="", eventNo="", flight="", name=e["name"], game="NLH",
            buyIn=e["buyIn"], houseFee=None, staffFee=None, lipsFee=None, prizeShare=None,
            guarantee=e["guarantee"], guaranteeNote="", ratio=None, bounty="", chips=None,
            levelMinutes=None, lateReg="", lateRegTime=None,
            entry={"singleEntryPrinted": "not captured", "reentry": "", "rebuy": "", "addon": "",
                   "excerpt": "Entry terms are in the official structures document beyond the 30-page fetch limit used for this research pass; blank until re-verified.",
                   "sheetUrl": WYNN_WPT_STRUCT, "retrieved": ""},
            bucket="review", bucketLabel="Review — entry terms not captured this pass",
            kind="festival", structureSource=WYNN_WPT_STRUCT, scheduleSource=WYNN_WPT_SCHED,
            notes=["Announced on the official Wynn poker page (Super Gold Million $400 buy-in, $3,000,000 guarantee)."])
    return rows


def build_bellagio():
    B_PAGE = "https://bellagio.mgmresorts.com/en/casino/poker.html"
    B_FRI = "https://assets.contentstack.io/v3/assets/bltc6ce635bc4868eb2/blt9cf95b0e60ec253e/6af491a3a9851d75c40be840/mgm-bellagio-poker-fridays-$600-nlh.pdf"
    B_SAT = "https://assets.contentstack.io/v3/assets/bltc6ce635bc4868eb2/blt6d47974bf5a7d9b6/6af491a391a6e8e4230c9e07/mgm-bellagio-poker-saturdays-$1000-nlh.pdf"
    B_SUN = "https://assets.contentstack.io/v3/assets/bltc6ce635bc4868eb2/blt07fcf1244a6da661/6af491a339e2b4f6b76a86ad/mgm-bellagio-poker-sundays-$400-horse.pdf"
    rows = [
        dict(id="bellagio-fri", series="Bellagio weekly tournaments", venue="bellagio", venueName="Bellagio Poker Room",
             date="Fridays (recurring)", weekday="", time="11:00 AM", timeMin=parse_time("11:00 AM"),
             eventNo="", flight="", name="$600 NLH (weekly)", game="NLH", buyIn=600,
             houseFee=50, staffFee=40, lipsFee=None, prizeShare=510, guarantee=None,
             guaranteeNote="no guarantee printed", ratio=None, bounty="",
             chips=15000, levelMinutes=30, levelNote="optional $40 staff gratuity adds 15,000 chips",
             levels=28, lateReg="Buy-in and re-entry through the end of level 8 (including break)",
             lateRegTime=None, lateRegMin=None, estDurationHours=None, pays="",
             entry={"singleEntryPrinted": "no", "reentry": "YES — buy-in and re-enter through end of level 8",
                    "rebuy": "no clause printed", "addon": "paid chip boost: $40 voluntary staff gratuity adds 15,000 chips",
                    "excerpt": "Players may buy-in and re-enter through the end of level 8 (Including Break). ... The voluntary staff gratuity will grant players an extra 15,000 chips.",
                    "sheetUrl": B_FRI, "retrieved": TODAY},
             bucket="spend-more", bucketLabel="Re-entry + paid chip boost (official terms)",
             restricted="", kind="one-day", scheduleSource=B_PAGE, structureSource=B_FRI,
             lastChecked=TODAY, status="verified", notes=[]),
        dict(id="bellagio-sat", series="Bellagio weekly tournaments", venue="bellagio", venueName="Bellagio Poker Room",
             date="Saturdays (recurring)", weekday="", time="11:00 AM", timeMin=parse_time("11:00 AM"),
             eventNo="", flight="", name="NLH (weekly) — BUY-IN CONFLICT: link says $1,000, PDF header says $1,100, PDF breakdown says $600",
             game="NLH", buyIn=None,
             houseFee=50, staffFee=40, lipsFee=None, prizeShare=510, guarantee=50000,
             guaranteeNote="Bellagio guarantees the total combined prize pool will be at least $50,000",
             ratio=None, bounty="",
             chips=20000, levelMinutes=30, levelNote="optional $40 staff gratuity adds 20,000 chips",
             levels=28, lateReg="Registration open until the start of Level 10 (flights 1A–1D)",
             lateRegTime=None, lateRegMin=None, estDurationHours=None, pays="",
             entry={"singleEntryPrinted": "no", "reentry": "flights 1A–1D with combined Day 2 (multi-entry)",
                    "rebuy": "no clause printed", "addon": "paid chip boost: $40 voluntary staff gratuity adds 20,000 chips",
                    "excerpt": "Registration will be open until the start of Level 10 ... Each Flight would play until the money (12.5%). ... Of the $600 Buy-in, $510 goes to the Prize Pool, $50 is Admin Fees and $40 is optional staff gratuity.",
                    "sheetUrl": B_SAT, "retrieved": TODAY},
             bucket="spend-more", bucketLabel="Multi-flight + paid chip boost — buy-in conflict flagged",
             restricted="", kind="flight", scheduleSource=B_PAGE, structureSource=B_SAT,
             lastChecked=TODAY, status="unverified",
             notes=["Buy-in conflict: page link '$1,000 NLH', PDF header '$1100 BUY-IN', PDF rule 07 'Of the $600 Buy-in'. Buy-in left blank.",
                    "PDF rule 04 references 'Combined Final Day 2 (9/13/26)' — date looks stale; flagged."]),
        dict(id="bellagio-sun", series="Bellagio weekly tournaments", venue="bellagio", venueName="Bellagio Poker Room",
             date="Sundays (recurring)", weekday="", time="11:00 AM", timeMin=parse_time("11:00 AM"),
             eventNo="", flight="", name="$400 H.O.R.S.E. (weekly)", game="Mixed", buyIn=400,
             houseFee=35, staffFee=25, lipsFee=None, prizeShare=340, guarantee=None,
             guaranteeNote="no guarantee printed", ratio=None, bounty="",
             chips=15000, levelMinutes=30, levelNote="optional $25 staff gratuity adds 15,000 chips",
             levels=26, lateReg="Buy-in and re-enter through the end of level 8 (including break)",
             lateRegTime=None, lateRegMin=None, estDurationHours=None, pays="~12.5% of field",
             entry={"singleEntryPrinted": "no", "reentry": "YES — buy-in and re-enter through end of level 8",
                    "rebuy": "no clause printed", "addon": "paid chip boost: $25 voluntary staff gratuity adds 15,000 chips",
                    "excerpt": "Players may buy-in and re-enter through the end of level 8 (Including Break). ... will grant players an additional 15,000 in starting chips.",
                    "sheetUrl": B_SUN, "retrieved": TODAY},
             bucket="spend-more", bucketLabel="Re-entry + paid chip boost (official terms)",
             restricted="", kind="one-day", scheduleSource=B_PAGE, structureSource=B_SUN,
             lastChecked=TODAY, status="verified", notes=[]),
    ]
    return rows


def build_aria():
    A_PAGE = "https://aria.mgmresorts.com/en/casino/poker.html"
    A_GUIDE = "https://aria.mgmresorts.com/content/dam/MGM/aria/casino/poker/aria-casino-poker-gentlemans-guide.pdf"
    rows = []
    for t, tid in (("1:00 PM", "aria-day"), ("7:00 PM", "aria-night")):
        rows.append(dict(id=tid, series="ARIA daily/nightly cadence (official guide, undated)",
                         venue="aria", venueName="ARIA Poker Room",
                         date="Undated cadence — call room to confirm", weekday="", time=t,
                         timeMin=parse_time(t), eventNo="", flight="",
                         name="ARIA daily / nightly tournament cadence", game="NLH",
                         buyIn=None, houseFee=None, staffFee=None, lipsFee=None, prizeShare=None,
                         guarantee=None, guaranteeNote="", ratio=None, bounty="", chips=None,
                         levelMinutes=None, levelNote="", levels=None,
                         lateReg="", lateRegTime=None, lateRegMin=None, estDurationHours=None, pays="",
                         entry={"singleEntryPrinted": "not published", "reentry": "", "rebuy": "", "addon": "",
                                "excerpt": "The current official poker page asks guests to call the room or check @ARIAPoker to confirm whether daily tournaments are running; the official guide with 1 PM / 7 PM times is undated.",
                                "sheetUrl": A_GUIDE, "retrieved": TODAY},
                         bucket="review", bucketLabel="Review — undated cadence, not a confirmed event",
                         restricted="", kind="cadence", scheduleSource=A_PAGE, structureSource=A_GUIDE,
                         lastChecked=TODAY, status="unverified",
                         notes=["Official page: 'call the Poker Room or check out our Twitter account, @ARIAPoker, for the most recent information on whether our Daily Tournaments are running as scheduled'."]))
    return rows


def build_other_rooms():
    """Rooms with official pages that mention tournaments but no retrievable dated schedule."""
    rows = []
    rows.append(dict(id="horseshoe-daily", series="Horseshoe daily tournaments", venue="horseshoe",
                     venueName="Horseshoe Las Vegas — Hall of Fame Poker Room",
                     date="Daily (recurring)", weekday="", time="", timeMin=None,
                     eventNo="", flight="", name="6 daily tournament times (details not published on page)",
                     game="NLH", buyIn=None, houseFee=None, staffFee=None, lipsFee=None,
                     prizeShare=None, guarantee=None, guaranteeNote="", ratio=None, bounty="",
                     chips=None, levelMinutes=None, levelNote="", levels=None,
                     lateReg="", lateRegTime=None, lateRegMin=None, estDurationHours=None, pays="",
                     entry={"singleEntryPrinted": "not published", "reentry": "", "rebuy": "", "addon": "",
                            "excerpt": "Hall of Fame Poker Room ... Test your luck with 6 exciting tournament times daily.",
                            "sheetUrl": "", "retrieved": TODAY},
                     bucket="review", bucketLabel="Review — 6 daily tournaments confirmed; times/buy-ins not published",
                     restricted="", kind="cadence",
                     scheduleSource="https://www.caesars.com/horseshoe-las-vegas/casino/poker",
                     structureSource="", lastChecked=TODAY, status="unverified",
                     notes=["20 tables; NLH, LHE, PLO, O8 cash games. Tournament times and buy-ins are not on the official page."]))
    return rows


# ---------------------------------------------------------------- hotels (checked 2026-11-16)
VEN_FEE = "https://www.venetianlasvegas.com/resort/resort-fee.html"
VEN_TERMS = "https://www.venetianlasvegas.com/legal/hotel-terms-and-conditions.html"
VEN_POKER_RATES = "https://www.venetianlasvegas.com/resort/casino/poker/suite-rates.html"
WYNN_TERMS = "https://www.wynnlasvegas.com/terms-and-conditions/850070"
BEL_TERMS = "https://bellagio.mgmresorts.com/en/terms-and-conditions.html"
BEL_HOTEL = "https://bellagio.mgmresorts.com/en/hotel.html"
ARIA_POKER = "https://aria.mgmresorts.com/en/casino/poker.html"

def build_hotels():
    def hotel(**kw):
        base = dict(lastChecked=TODAY, taxRateNote="Clark County room tax 13.38% on the daily rate; tax also applies to the resort fee per Bellagio terms and Venetian terms say the fee is 'plus applicable tax'.", checkoutTotal=None, nightlyAvg=None, rateTimestamp="", cancellationDeadline="", qualityNote="")
        base.update(kw)
        return base
    return [
        hotel(id="venetian", name="The Venetian Resort", address="3355 S Las Vegas Blvd, Las Vegas, NV 89109",
              venue="venetian", resortFee=55.0, resortFeeNote="$55 plus applicable tax per night (official)",
              resortFeeSource=VEN_FEE, taxRate=0.1338, taxSource=VEN_TERMS,
              parking="Registered hotel guests $20/day; non-guests $20 Mon–Thu / $25 Fri–Sun; valet $40/day; Venetian Rewards Sapphire+ self-parking free (official terms)",
              parkingSource=VEN_TERMS,
              cancellation="Prepaid offers non-cancellable/non-refundable; deposit (suite + fee + tax) billed at booking; early departure charge $100 plus tax (official terms)",
              cancellationSource=VEN_TERMS,
              baseRate=None,
              rateNote="2026 poker suite rates start as low as $119 and $209 (Luxury King Suite, single/double, qualifying poker play: 6 hours cash game or a $300+ tournament buy-in per night). The page does not map rates to dates or towers; date-specific rate remains blank. Book code EPOKR25 via 866.255.8936.",
              rateSource=VEN_POKER_RATES,
              bookingUrl="https://www.venetianlasvegas.com/booking?adults[]=2&arrival_date=2026-11-17&children[]=0&departure_date=2026-11-19&view=calendar",
              trueNightlyFormula="(rate + 55 + tax(13.38% on rate + fee)) — computed by the calculator when a dated rate is entered"),
        hotel(id="palazzo", name="The Palazzo at The Venetian Resort", address="3325 S Las Vegas Blvd, Las Vegas, NV 89109",
              venue="venetian", resortFee=55.0, resortFeeNote="$55 plus applicable tax per night (official)",
              resortFeeSource=VEN_FEE, taxRate=0.1338, taxSource=VEN_TERMS,
              parking="Same policy as The Venetian (shared resort; official terms)",
              parkingSource=VEN_TERMS,
              cancellation="Same terms as The Venetian (official terms)",
              cancellationSource=VEN_TERMS,
              baseRate=None,
              rateNote="Shares the 2026 poker suite offer with The Venetian ('as low as $119 and $209'); property-specific rate not published. Blank until a dated quote exists.",
              rateSource=VEN_POKER_RATES,
              bookingUrl="https://www.venetianlasvegas.com/booking?adults[]=2&arrival_date=2026-11-17&children[]=0&departure_date=2026-11-19&view=calendar",
              trueNightlyFormula="(rate + 55 + tax(13.38% on rate + fee))"),
        hotel(id="wynn", name="Wynn Las Vegas / Encore", address="3131 S Las Vegas Blvd, Las Vegas, NV 89109",
              venue="wynn", resortFee=55.0, resortFeeNote="$55 plus tax per night (both Resort and Tower Suite rooms; official terms)",
              resortFeeSource=WYNN_TERMS, taxRate=0.1338,
              taxSource="https://www.venetianlasvegas.com/legal/hotel-terms-and-conditions.html",
              parking="Self-parking complimentary for registered guests; $25/day for non-registered (first 3 hours free); complimentary for Wynn Poker Room guests (ask the room); valet $40/day; Tower Suites guests free valet (official terms)",
              parkingSource=WYNN_TERMS,
              cancellation="Cancellations at least 48 hours prior to arrival or the deposit is forfeited; early departure penalty equals that night's room rate and tax (official terms)",
              cancellationSource=WYNN_TERMS,
              baseRate=None,
              rateNote="No date-specific room rate published on reviewed official pages. The terms page reviewed (850070) carries an offer whose stay window ended Sept 30, 2025 — its $55 + tax fee and parking/cancellation terms are the latest published on the reviewed Wynn terms URL, but confirm on the actual booking.",
              rateSource=WYNN_TERMS,
              bookingUrl="https://www.wynnlasvegas.com/rooms-and-suites",
              trueNightlyFormula="(rate + 55 + tax(13.38% on rate + fee))"),
        hotel(id="bellagio", name="Bellagio", address="3600 S Las Vegas Blvd, Las Vegas, NV 89109",
              venue="bellagio", resortFee=55.0, resortFeeNote="$55.00 plus applicable tax per night; waived for eligible MGM Rewards Gold+ (official terms)",
              resortFeeSource=BEL_TERMS, taxRate=0.1338,
              taxSource=BEL_TERMS,
              parking="Not published in the reviewed terms — check MGM parking policy at booking",
              parkingSource="",
              cancellation="First night's deposit fully refundable if cancelled at least 72 hours before arrival; late cancellation or no-show forfeits the first night (comp stays: $165 midweek / $200 weekend fee) (official terms)",
              cancellationSource=BEL_TERMS,
              baseRate=None,
              rateNote="Date-specific room rates not published on the official room page (date-based rate checker only). $50 + tax per night per occupant above 2. Incidental authorization $150/day.",
              rateSource=BEL_HOTEL,
              bookingUrl="https://bellagio.mgmresorts.com/en/hotel.html",
              trueNightlyFormula="(rate + 55 + tax(13.38% on rate + fee))"),
        hotel(id="aria", name="ARIA Resort & Casino", address="3730 S Las Vegas Blvd, Las Vegas, NV 89109",
              venue="aria", resortFee=None,
              resortFeeNote="Not verified this pass — blank on purpose",
              resortFeeSource="", taxRate=0.1338,
              taxSource=BEL_TERMS,
              parking="Not verified this pass",
              parkingSource="",
              cancellation="Not verified this pass",
              cancellationSource="",
              baseRate=None,
              rateNote="Official poker page advertises 'Exclusive room rates for qualifying poker players' — call 702.590.7232 or PokerRoomRates@aria.com; no published rate captured.",
              rateSource=ARIA_POKER,
              bookingUrl="https://aria.mgmresorts.com/en/hotel.html",
              trueNightlyFormula="(rate + resort fee + tax) — resort fee unverified"),
    ]


def build_rates():
    """Dated rate log. One entry per observation; never overwritten."""
    return [
        {"id": "rate-ven-2026-11-16", "hotel": "venetian", "observed": TODAY,
         "stayStart": "", "stayEnd": "", "room": "Luxury King Suite (Poker Suite Rate, code EPOKR25)",
         "rate": 119.0, "rateLabel": "from $119 (starting rate, date not mapped)",
         "resortFee": 55.0, "currency": "USD",
         "source": VEN_POKER_RATES,
         "note": "Published starting rate 'as low as $119 and $209' across The Venetian and The Palazzo; not mapped to dates, towers or occupancy beyond single/double. Requires 6 hours cash play or a $300+ tournament buy-in per night; otherwise adjusted to prevailing rate."},
        {"id": "rate-ven-209-2026-11-16", "hotel": "venetian", "observed": TODAY,
         "stayStart": "", "stayEnd": "", "room": "Luxury King Suite (Poker Suite Rate — upper starting rate)",
         "rate": 209.0, "rateLabel": "from $209 (starting rate, date not mapped)",
         "resortFee": 55.0, "currency": "USD",
         "source": VEN_POKER_RATES,
         "note": "Second published starting rate on the same official page; which property/date each applies to is not stated."},
        {"id": "rate-wynn-fee-2026-11-16", "hotel": "wynn", "observed": TODAY,
         "stayStart": "", "stayEnd": "", "room": "Resort King / Two Queens (fee only)",
         "rate": None, "rateLabel": "room rate not published",
         "resortFee": 55.0, "currency": "USD",
         "source": WYNN_TERMS,
         "note": "Resort fee $55 plus tax confirmed on reviewed Wynn terms page. No dated room rate captured."},
        {"id": "rate-bel-fee-2026-11-16", "hotel": "bellagio", "observed": TODAY,
         "stayStart": "", "stayEnd": "", "room": "Resort room (fee only)",
         "rate": None, "rateLabel": "room rate not published",
         "resortFee": 55.0, "currency": "USD",
         "source": BEL_TERMS,
         "note": "Resort fee $55.00 plus applicable tax confirmed in Bellagio reservation terms. Lodging taxes apply to the basic room rate and the resort fee. No dated room rate captured."},
    ]


def build_routes():
    """Hotel–venue walking pairs. Official addresses; walking times only with provenance."""
    G = "https://www.google.com/maps/dir/?api=1&origin={o}&destination={d}&travelmode=walking"
    def addr(a):
        return a.replace(" ", "+")
    pairs = [
        ("venetian", "venetian", "on-site"),
        ("palazzo", "venetian", "on-site"),
        ("wynn", "wynn", "on-site"),
        ("bellagio", "bellagio", "on-site"),
        ("aria", "aria", "on-site"),
        ("venetian", "wynn", "estimate"), ("palazzo", "wynn", "estimate"),
        ("wynn", "venetian", "estimate"),
        ("bellagio", "venetian", "estimate"), ("aria", "venetian", "estimate"),
        ("bellagio", "wynn", "estimate"), ("aria", "wynn", "estimate"),
        ("bellagio", "aria", "estimate"),
    ]
    HOTEL_ADDR = {h["id"]: h["address"] for h in build_hotels()}
    HOTEL_ADDR["venetian_poker"] = "3355 S Las Vegas Blvd, Las Vegas, NV 89109"
    VENUE_ADDR = {
        "venetian": "The Venetian Poker Room, 3355 S Las Vegas Blvd, Las Vegas, NV 89109",
        "wynn": "Wynn Poker Room (Encore), 3131 S Las Vegas Blvd, Las Vegas, NV 89109",
        "bellagio": "Bellagio Poker Room, 3600 S Las Vegas Blvd, Las Vegas, NV 89109",
        "aria": "ARIA Poker Room, 3730 S Las Vegas Blvd, Las Vegas, NV 89109",
    }
    HNAMES = {"venetian": "The Venetian Resort", "palazzo": "The Palazzo", "wynn": "Wynn Las Vegas / Encore",
              "bellagio": "Bellagio", "aria": "ARIA Resort & Casino"}
    VNAMES = {"venetian": "The Venetian Poker Room", "wynn": "Wynn Poker Room (Encore)",
              "bellagio": "Bellagio Poker Room", "aria": "ARIA Poker Room"}
    out = []
    for h, v, kind in pairs:
        out.append({
            "id": f"route-{h}-{v}",
            "hotel": h, "hotelName": HNAMES[h], "hotelAddress": HOTEL_ADDR.get(h, ""),
            "venue": v, "venueName": VNAMES[v], "venueAddress": VENUE_ADDR[v],
            "walkingMinutes": None,
            "walkingVerified": False,
            "walkingNote": ("Same resort property — walking distance inside the resort; exact route time not published by the venue."
                            if kind == "on-site" else
                            "Walking time not verified from an official or map source in this pass; verify via the map link before relying on the 30-minute limit."),
            "estimateMinutes": None,
            "estimateSource": "",
            "within30": None,
            "mapLink": G.format(o=addr(HOTEL_ADDR.get(h, "")), d=addr(VENUE_ADDR[v])),
            "lastChecked": TODAY,
        })
    return out


def build_sources():
    S = lambda i, n, u, daily=False: {"id": i, "name": n, "url": u, "kind": "official", "checked": TODAY, "dailyFeed": daily}
    return [
        S("ven-dse-html", "Venetian DeepStack Extravaganza IV schedule (web)", VEN_DSE_HTML, True),
        S("ven-dse-pdf", "Venetian DSE IV schedule (official PDF)", VEN_DSE_PDF, True),
        S("ven-suite", "Venetian 2026 poker suite rates", VEN_POKER_RATES),
        S("ven-fee", "Venetian resort fee", VEN_FEE),
        S("ven-terms", "Venetian hotel terms and taxes", VEN_TERMS),
        S("wynn-poker", "Wynn poker room, WPT and daily schedules", WYNN_POKER, True),
        S("wynn-poster", "Wynn daily tournament poster (PDF)", WYNN_POSTER, True),
        S("wynn-daily-struct", "Wynn daily tournament structures and terms (PDF)", WYNN_DAILY_STRUCT),
        S("wynn-wpt-sched", "WPT World Championship schedule (PDF)", WYNN_WPT_SCHED, True),
        S("wynn-wpt-struct", "WPT World Championship structures and terms (PDF)", WYNN_WPT_STRUCT),
        S("wynn-terms", "Wynn reservation terms (resort fee, parking, cancellation)", WYNN_TERMS),
        S("bel-poker", "Bellagio poker page (weekly links)", "https://bellagio.mgmresorts.com/en/casino/poker.html", True),
        S("bel-fri", "Bellagio Friday $600 NLH structure (PDF)",
          "https://assets.contentstack.io/v3/assets/bltc6ce635bc4868eb2/blt9cf95b0e60ec253e/6af491a3a9851d75c40be840/mgm-bellagio-poker-fridays-$600-nlh.pdf"),
        S("bel-sat", "Bellagio Saturday NLH structure (PDF, buy-in conflict)",
          "https://assets.contentstack.io/v3/assets/bltc6ce635bc4868eb2/blt6d47974bf5a7d9b6/6af491a391a6e8e4230c9e07/mgm-bellagio-poker-saturdays-$1000-nlh.pdf"),
        S("bel-sun", "Bellagio Sunday $400 H.O.R.S.E. structure (PDF)",
          "https://assets.contentstack.io/v3/assets/bltc6ce635bc4868eb2/blt07fcf1244a6da661/6af491a339e2b4f6b76a86ad/mgm-bellagio-poker-sundays-$400-horse.pdf"),
        S("bel-terms", "Bellagio reservation terms (resort fee, tax, cancellation)", BEL_TERMS),
        S("aria-poker", "ARIA poker page (call to confirm daily tournaments)", "https://aria.mgmresorts.com/en/casino/poker.html", True),
        S("aria-guide", "ARIA poker guide (undated daily/nightly cadence)",
          "https://aria.mgmresorts.com/content/dam/MGM/aria/casino/poker/aria-casino-poker-gentlemans-guide.pdf"),
        S("horseshoe-poker", "Horseshoe Las Vegas casino page (Hall of Fame Poker Room, 6 daily tournaments)",
          "https://www.caesars.com/horseshoe-las-vegas/casino/poker", True),
    ]


def build_flags():
    return [
        {"id": "FL01", "title": "Bellagio Saturday NLH buy-in conflict (three values)", "level": "high",
         "finding": "The poker page link says '$1,000 NLH' (filename saturdays-$1000-nlh.pdf), the PDF header says 'NLH $1100 BUY-IN', and PDF rule 07 says 'Of the $600 Buy-in, $510 goes to the Prize Pool...'.",
         "next": "Call the Bellagio poker room (702.693.7291) before planning around this event. Buy-in is left blank.",
         "source": "https://assets.contentstack.io/v3/assets/bltc6ce635bc4868eb2/blt6d47974bf5a7d9b6/6af491a391a6e8e4230c9e07/mgm-bellagio-poker-saturdays-$1000-nlh.pdf"},
        {"id": "FL02", "title": "WPT $1,100 PLO fee breakdown sums to $1,105", "level": "high",
         "finding": "Official structures doc: '$1,100 Buy-in = $975 (Tournament Prize Pool) + $85 (Tournament Fee) + $45 (Poker Staff Service Charge)' — components total $1,105, not $1,100.",
         "next": "Confirm the actual charged amount with the Wynn poker room before entering.",
         "source": "https://cdn.wynnresorts.com/image/upload/v1750864036/visitwynn_pdfs_files/Poker/WPT/WPT_World_Championship_Structures.pdf"},
        {"id": "FL03", "title": "Venetian sheet 8 (Events #18/#58) references 'subsequent buy-ins'", "level": "medium",
         "finding": "The PokerAtlas PRO discount clause reads 'All subsequent buy in's after the initial buy in will be $200', implying more than one buy-in may be possible, although no explicit re-entry clause is printed on the sheet.",
         "next": "Ask the Venetian poker room whether #18/#58 are one-entry freezeouts. Held in Review until confirmed.",
         "source": "https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_8.pdf"},
        {"id": "FL04", "title": "Wynn terms page carries an expired offer window", "level": "low",
         "finding": "Terms page 850070 includes a stay-completed-by September 30, 2025 offer alongside the $55 + tax resort fee, parking and cancellation terms used here.",
         "next": "Confirm fee, parking and cancellation terms on the live booking before nonrefundable payment.",
         "source": "https://www.wynnlasvegas.com/terms-and-conditions/850070"},
        {"id": "FL05", "title": "Bellagio 'tournament play will resume Saturday, July 26' notice is undated", "level": "medium",
         "finding": "The official poker page carries a resume notice naming July 26 with no year; July 26, 2026 is a Sunday. Current operation of the weekly schedule must be confirmed by phone.",
         "next": "Call 702.693.7291 to confirm the weekly tournaments are running on your dates.",
         "source": "https://bellagio.mgmresorts.com/en/casino/poker.html"},
        {"id": "FL06", "title": "ARIA daily/nightly tournament cadence is undated", "level": "medium",
         "finding": "The official guide (1 PM / 7 PM) is undated; the current official page says to call the room or check @ARIAPoker to confirm whether daily tournaments are running.",
         "next": "Call 702.590.7232 (or check @ARIAPoker) before counting ARIA events in a plan.",
         "source": "https://aria.mgmresorts.com/en/casino/poker.html"},
        {"id": "FL07", "title": "WPT Super Gold Million and $10,400 World Championship entry terms not captured", "level": "medium",
         "finding": "The official structures PDF is longer than the 30-page fetch limit used in this research pass; those events' registration clauses were not returned. Their entry fields are blank on purpose.",
         "next": "Open the official structures PDF manually and read the two events' Registration sections; then update tournaments.json.",
         "source": "https://cdn.wynnresorts.com/image/upload/v1750864036/visitwynn_pdfs_files/Poker/WPT/WPT_World_Championship_Structures.pdf"},
        {"id": "FL08", "title": "Walking times not verified", "level": "high",
         "finding": "No official venue publishes door-to-door walking times, and no map service result could be captured in this pass. Every hotel–venue pair carries a Google Maps walking link for manual verification; walkingMinutes is blank on all rows.",
         "next": "Open each map link (walking mode) and record the time; the 30-minute filter will then apply to verified values.",
         "source": "https://www.google.com/maps"},
        {"id": "FL09", "title": "Date-specific hotel rates not published; checkout totals blank", "level": "high",
         "finding": "Venetian/Palazzo publish poker-suite starting rates ($119/$209) not mapped to dates; Wynn, Bellagio and ARIA publish no static rate. All checkoutTotal / nightlyAvg fields are blank; the trip calculator computes them once a dated rate is entered.",
         "next": "Fix trip dates (Workflow step 1), then pull each hotel's official booking link for those dates and log the dated quote in the rate log.",
         "source": "https://www.venetianlasvegas.com/resort/casino/poker/suite-rates.html"},
        {"id": "FL10", "title": "Bellagio Saturday PDF references a stale Day 2 date", "level": "low",
         "finding": "PDF rule 04 says 'Combined Final Day 2 (9/13/26) will begin at 12pm' inside a weekly tournament sheet; the date appears stale and the sheet also references Flights 1A–1D.",
         "next": "Ask the room for the current Saturday structure.",
         "source": "https://assets.contentstack.io/v3/assets/bltc6ce635bc4868eb2/blt6d47974bf5a7d9b6/6af491a391a6e8e4230c9e07/mgm-bellagio-poker-saturdays-$1000-nlh.pdf"},
        {"id": "FL11", "title": "Golden Nugget / Resorts World / Circa / MGM Grand poker pages not retrievable", "level": "medium",
         "finding": "Golden Nugget returned empty content, Resorts World redirected to an email template, Circa failed to load, and the MGM Grand poker URL 404s. No rows were added for these rooms.",
         "next": "Retry these official pages (or call the rooms) and add dated schedule rows when retrieved; the daily-check workflow will also retry them.",
         "source": "https://www.goldennugget.com/las-vegas/casino/poker/"},
        {"id": "FL12", "title": "No verified 8:00 AM tournament start", "level": "medium",
         "finding": "The earliest verified start across all checked official schedules is 9:10 AM (Venetian satellite #46, Dec 12) and 10:10 AM for regular events; no official schedule shows an 8:00 AM start in this window.",
         "next": "If an 8 AM start is required, ask Horseshoe (6 daily tournaments, times unpublished) or Golden Nugget whether an early daily runs.",
         "source": "https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html"},
        {"id": "FL13", "title": "Single-entry is never printed as a policy", "level": "high",
         "finding": "No Venetian structure sheet prints 'single entry', 'freezeout', or a maximum-entries rule. Main-list rows are confirmed for date/time/buy-in/fee-split/guarantee and carry no re-entry/rebuy/add-on clause, but a one-entry limit is not stated in writing.",
         "next": "Get written confirmation of one-entry-total / no-rebuy / no-add-on from tournament staff before treating any event as a strict freezeout.",
         "source": "https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_5.pdf"},
        {"id": "FL14", "title": "Est. finish times are structure-derived estimates", "level": "low",
         "finding": "Duration estimates multiply printed level counts by level lengths plus printed breaks. Real events can end earlier (players bust) or later (final-table dynamics, TD discretion). Overlap flags use these estimates and are advisory only.",
         "next": "Treat overlap flags as planning guidance; the poker room controls actual timing.",
         "source": "https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_5.pdf"},
    ]


def build_questions():
    return [
        {"id": "Q01", "answer": '', "q": "What are the exact trip dates and nightly budget/quality floor?",
         "why": "Workflow step 1. Rates are date-specific; without dates no checkout total can be confirmed (FL09).",
         "how": "Provide arrival/departure dates and a max true nightly cost. The calculator and rate log then compare like-for-like.", "status": "open"},
        {"id": "Q02", "answer": 'Verified across all 37 Venetian structure sheets (2026-11-16): no sheet prints "single entry", a maximum-entry limit, or any re-entry/rebuy/add-on clause. Wynn and Bellagio sheets DO print re-entry clauses, so the distinction is real and documented. A strict freezeout rule still needs written room confirmation before relying on it.', "q": "Is a one-entry-total freezeout policy required, or is 'no clause printed' acceptable?",
         "why": "No official sheet prints a single-entry rule (FL13). Strict policy would remove every event from the list until rooms confirm in writing.",
         "how": "Decide the policy; the single-entry toggle filter can enforce either stance.", "status": "open"},
        {"id": "Q03", "answer": 'No official venue publishes door-to-door walking times. Google Maps walking-direction links per hotel–venue pair are provided on the Routes page for verification; recorded values will populate the 30-minute filter.', "q": "What walking time is acceptable as 'verified' — and from which map service?",
         "why": "WalkingMinutes are blank (FL08). The 30-minute limit cannot be applied until values with provenance exist.",
         "how": "Verify each route via the provided Google Maps walking links (or Apple Maps) and record minutes + date checked.", "status": "open"},
        {"id": "Q04", "answer": '', "q": "Which hotel quality ranking should be used?",
         "why": "No common official quality metric (star rating) is published by the resorts; quality is currently descriptive only.",
         "how": "Pick a criterion (e.g., published room class, user preference, third-party rating with source) and it will be added as a sortable column.", "status": "open"},
        {"id": "Q05", "answer": "Open — requires a phone call to 702.693.7291. The official page's resume notice is undated (FL05).", "q": "Are the Bellagio weekly tournaments actually running on the trip dates?",
         "why": "The official page carries an undated resume notice (FL05).",
         "how": "Call 702.693.7291; record the answer with date and staff name in the questions log.", "status": "open"},
        {"id": "Q06", "answer": 'Answered from the official suite-rate page: a $300+ tournament buy-in per night qualifies (6 hours live cash is the alternative). Most DeepStack buy-ins are ≥$300; on $200-event days (bounty family, RaceDay, Valuetown) the cash-play requirement applies instead. Unplayed nights are repriced to the prevailing rate at checkout.', "q": "Does the player qualify for the Venetian poker suite rate play requirement?",
         "why": "$119/$209 rates require 6 hours cash play or a $300+ tournament buy-in per night; otherwise the rate adjusts to prevailing.",
         "how": "Confirm the planned schedule meets the requirement per night (the DeepStack buy-ins mostly satisfy the $300+ rule on those days).", "status": "open"},
        {"id": "Q07", "answer": 'Open — three conflicting official values ($1,000 page link / $1,100 PDF header / $600 PDF breakdown). Room call required (FL01).', "q": "What is the real buy-in for the Bellagio Saturday NLH?",
         "why": "Three conflicting official values ($1,000 / $1,100 / $600) (FL01).",
         "how": "Phone the room; log the answer.", "status": "open"},
        {"id": "Q08", "answer": '', "q": "Is parking needed (rental car) and which hotel's parking policy applies?",
         "why": "Parking fees are verified per hotel but blank for ARIA; costs affect true nightly cost.",
         "how": "Decide transport; add parking to the trip calculator if needed.", "status": "open"},
    ]


def build_suggestions():
    return [
        {"id": "S01", "title": "Wire the daily-check workflow output into row badges",
         "detail": "The daily-check job already stores URL hashes and change dates. Next: surface 'source changed since verification' badges per row by joining changes.json to row source IDs.",
         "impact": "high", "effort": "low", "status": "proposed"},
        {"id": "S02", "title": "Add phone-confirmation log fields",
         "detail": "Questions Q02/Q05/Q07 need answers that only the poker rooms can give. Add a small dated call-log table (date, room, staff, question, answer) linked from each flagged row.",
         "impact": "high", "effort": "low", "status": "proposed"},
        {"id": "S03", "title": "Capture Super Gold Million and WPT World Championship terms manually",
         "detail": "Read the tail of the official structures PDF (beyond the 30-page fetch limit) and fill the two review rows (FL07).",
         "impact": "medium", "effort": "low", "status": "proposed"},
        {"id": "S04", "title": "Add per-night rate snapshots from official booking engines",
         "detail": "The booking deep links exist per hotel. A weekly job (or manual pass) can record dated quotes per stay window in rates.json so 'like-for-like' totals build up over time.",
         "impact": "high", "effort": "medium", "status": "proposed"},
        {"id": "S05", "title": "Verified walking-time table",
         "detail": "Walk each route (or use Google/Apple Maps walking directions) and fill walkingMinutes with the date and service used; the ≤30-minute filter becomes fully functional.",
         "impact": "high", "effort": "medium", "status": "proposed"},
        {"id": "S06", "title": "Evening-event feasibility planner",
         "detail": "Once finish-time estimates are trusted, auto-generate primary + fallback pairs per day and mark days where an evening event is realistically reachable after the earlier bust-out.",
         "impact": "medium", "effort": "medium", "status": "proposed"},
        {"id": "S07", "title": "Consolidate the archived research sites",
         "detail": "docs/, planner/, single-entry/, verified/ and the root HTML files are prior research artifacts. Keep one canonical site (site/) and move archives under archive/ after the user confirms (R2 from earlier sessions).",
         "impact": "medium", "effort": "low", "status": "needs decision"},
        {"id": "S08", "title": "Add ICS export of the day plan",
         "detail": "Let the user export the primary/fallback schedule to a calendar file for the chosen trip window.",
         "impact": "low", "effort": "low", "status": "proposed"},
    ]


def build_dayplan(tourneys):
    """Primary + fallback per date, with overlap flags based on start/late-reg/duration estimates."""
    by_date = {}
    for t in tourneys:
        if t["bucket"] not in ("single-path", "review") or t["kind"] in ("restart", "satellite", "cadence", "festival"):
            continue
        if not re.match(r"\d{4}-\d{2}-\d{2}$", t["date"] or ""):
            continue
        by_date.setdefault(t["date"], []).append(t)

    plan = []
    for d in sorted(by_date):
        evs = sorted(by_date[d], key=lambda x: (x.get("timeMin") or 0))
        for e in evs:
            conflicts = []
            if e.get("lateRegMin") and e.get("timeMin") is not None:
                for o in evs:
                    if o is e or o.get("timeMin") is None:
                        continue
                    # overlap: o starts before e's late reg closes and o plausibly runs into e's late-reg window
                    o_end = None
                    if o.get("estDurationHours"):
                        o_end = o["timeMin"] + int(o["estDurationHours"] * 60)
                    if o["timeMin"] < (e.get("lateRegMin") or 0) and (o_end is None or o_end > e["timeMin"]):
                        conflicts.append(o["id"])
            e["overlapWith"] = conflicts
        singles = [e for e in evs if e["bucket"] == "single-path"]
        ranked = sorted(singles, key=lambda x: (-(x.get("ratio") or 0)))
        plan.append({
            "date": d,
            "weekday": evs[0].get("weekday", ""),
            "primary": ranked[0]["id"] if ranked else (evs[0]["id"] if evs else None),
            "fallback": ranked[1]["id"] if len(ranked) > 1 else None,
            "events": [e["id"] for e in evs],
            "note": "" if ranked else "No sheet-confirmed single-path event on this date; primary is the earliest listed event.",
        })
    return plan


def main():
    sheets = load_sheets()
    tourneys = build_venetian(sheets) + build_wynn() + build_bellagio() + build_aria() + build_other_rooms()
    for t in tourneys:
        t.setdefault("overlapWith", [])
    dayplan = build_dayplan(tourneys)
    data = {
        "meta": {
            "asOf": TODAY,
            "builtAt": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "policy": "Only venue-controlled pages and official PDFs substantiate values. Unknown values are blank and flagged. A guarantee is not a forecast of actual payouts. Ratio = guaranteed pool ÷ buy-in, descriptive only.",
            "formula": "Trip cost = entries × buy-ins + nights × true hotel cost; true nightly = rate + resort fee + 13.38% tax (tax applies to rate and resort fee per Bellagio terms; Venetian terms state 13.38% Clark County room tax and 'plus applicable tax' on the fee).",
        },
        "tournaments": tourneys,
        "hotels": build_hotels(),
        "rates": build_rates(),
        "routes": build_routes(),
        "sources": build_sources(),
        "flags": build_flags(),
        "questions": build_questions(),
        "suggestions": build_suggestions(),
        "dayplan": dayplan,
    }
    outdir = os.path.join(ROOT, "site", "data")
    os.makedirs(outdir, exist_ok=True)
    with open(os.path.join(outdir, "tournaments.json"), "w") as f:
        json.dump({"meta": data["meta"], "tournaments": tourneys, "dayplan": dayplan}, f, indent=1)
    for key in ("hotels", "rates", "routes", "sources", "flags", "questions", "suggestions"):
        with open(os.path.join(outdir, key + ".json"), "w") as f:
            json.dump({"meta": data["meta"], key: data[key]}, f, indent=1)
    # summary counts
    counts = {}
    for t in tourneys:
        counts[t["bucket"]] = counts.get(t["bucket"], 0) + 1
    print("tournaments:", len(tourneys), counts)
    print("dayplan days:", len(dayplan))
    print("wrote site/data/*.json")

if __name__ == "__main__":
    main()
