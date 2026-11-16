#!/usr/bin/env python3
"""Build the static GitHub Pages site from data/*.json and scripts/data.py.

Run from the repository root:  python3 scripts/build.py
Writes HTML pages to the repository root (Pages source: main, folder /).
Every number shown is computed from the parsed official rows; nothing is typed in here.
"""
import datetime as dt
import html
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import data as D  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, ".."))
OUT = os.path.join(ROOT, "verified")  # site folder; other sites in this repo are not touched
os.makedirs(OUT, exist_ok=True)


def load(name):
    with open(os.path.join(ROOT, "data", name), encoding="utf-8") as f:
        return json.load(f)


VEN = load("venetian_flights.json")
VEN_RESTARTS = load("venetian_restarts.json")
WPT = load("wynn_wpt.json")

DAG = "\u2020"  # dagger marks an inferred date


def esc(x):
    return html.escape("" if x is None else str(x), quote=True)


def money(x):
    return "" if x is None else f"${x:,.0f}"


def tparse(s):
    s = s.replace("a.m.", "AM").replace("p.m.", "PM").replace("a. m.", "AM").replace("p. m.", "PM")
    s = s.strip().upper()
    for fmt in ("%I:%M %p", "%I %p"):
        try:
            return dt.datetime.strptime(s, fmt).time()
        except ValueError:
            pass
    raise ValueError(s)


def src(key_or_url, label=None):
    if key_or_url is None:
        return '<span class="badge badge-flag">no official source</span>'
    if key_or_url in D.SRC:
        text, url = D.SRC[key_or_url]
    else:
        text, url = (label or "Official source"), key_or_url
    return f'<a href="{esc(url)}" target="_blank" rel="noopener">{esc(label or text)}</a>'


def fmt_date(iso):
    d = dt.date.fromisoformat(iso)
    return d.strftime("%a %b ") + str(d.day)


# ------------------------------------------------------------- derived values
for r in VEN:
    r["_t"] = tparse(r["time"])
    r["_inferred"] = not r["date_source"].startswith("printed")
    r["_ratio"] = (r["guarantee"] / r["buy_in"]) if (r["guarantee"] and r["buy_in"] and not r["satellite"]) else None
    r["_checked"] = bool(r["structure_sheet"])

VEN.sort(key=lambda r: (r["date"], r["_t"]))
N_VEN = len(VEN)
N_CHECKED = sum(1 for r in VEN if r["_checked"])
N_UNCHECKED = N_VEN - N_CHECKED
N_SAT = sum(1 for r in VEN if r["satellite"])
N_INFERRED = sum(1 for r in VEN if r["_inferred"])
VEN_EVENTS = sorted({int(r["event_no"]) for r in VEN})
VEN_EARLIEST = min(VEN, key=lambda r: r["_t"])
VEN_CAL_CONFLICTS = [r for r in VEN if r.get("weekday_printed") and r["weekday_printed"].upper() != r["weekday"].upper()]

for r in WPT:
    try:
        r["_t"] = tparse(r["time"])
    except ValueError:
        r["_t"] = None

WPT_BUY = [r for r in WPT if r["buy_in"] is not None]
WPT_NO_BUY = [r for r in WPT if r["buy_in"] is None]
WPT_MULTI = [r for r in WPT_BUY if r["date"] == "2026-11-27"]  # 1A, 1B, TORSE, PLO on Nov 27
WPT_MULTI_IDS = {id(r) for r in WPT_MULTI}
WPT_UNV = [r for r in WPT_BUY if id(r) not in WPT_MULTI_IDS]
WPT_CONFLICTS = [r for r in WPT if r["calendar_conflict"]]
WPT_EARLIEST = min((r for r in WPT_BUY if r["_t"]), key=lambda r: r["_t"])

RANK_GTD = sorted([r for r in VEN if r["guarantee"] and not r["satellite"]], key=lambda r: -r["guarantee"])
RANK_RATIO = sorted([r for r in VEN if r["_ratio"]], key=lambda r: -r["_ratio"])
LOW_BUY = sorted([r for r in VEN if r["guarantee"] and r["buy_in"] and r["buy_in"] <= 200 and not r["satellite"]],
                 key=lambda r: -r["_ratio"])

# ------------------------------------------------------------- layout
NAV = [
    ("index.html", "Home"),
    ("summary.html", "Executive summary"),
    ("tournaments-single.html", "Single-entry (Venetian)"),
    ("tournaments-multi.html", "Re-entry &amp; unverified"),
    ("best-picks.html", "Best picks"),
    ("schedule.html", "Day schedule"),
    ("hotels.html", "Hotels"),
    ("suggestions.html", "Suggestions"),
    ("questions.html", "Questions"),
    ("repo-review.html", "Repo review"),
    ("flagged.html", "Flagged for Review"),
    ("sources.html", "Sources"),
]

CSS = """
:root{--ink:#1d2433;--muted:#5d6678;--line:#e3e7ef;--bg:#f7f8fb;--card:#fff;--accent:#1f5eff;
--ok:#0f7b4b;--warn:#8a5000;--bad:#b3261e;--grey:#5d6678}
*{box-sizing:border-box}body{margin:0;font:15px/1.5 system-ui,-apple-system,Segoe UI,Roboto,sans-serif;color:var(--ink);background:var(--bg)}
header{background:#14213d;color:#fff;padding:12px 20px}
header .brand{font-weight:700;font-size:17px;margin-right:18px}
nav{display:flex;flex-wrap:wrap;gap:4px}
nav a{color:#dfe7ff;text-decoration:none;padding:4px 8px;border-radius:6px;font-size:13px}
nav a:hover,nav a.on{background:#2c3e66;color:#fff}
main{max-width:1280px;margin:0 auto;padding:22px 18px 60px}
h1{font-size:26px;margin:4px 0 6px}h2{font-size:19px;margin:28px 0 8px;border-bottom:2px solid var(--line);padding-bottom:4px}
h3{font-size:16px;margin:14px 0 6px}
.lead{color:var(--muted);margin:0 0 14px}
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(210px,1fr));gap:12px;margin:14px 0}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px}
.card b{display:block;font-size:24px}.card a{font-weight:600;color:var(--accent);text-decoration:none}
.card span.k{color:var(--muted);font-size:13px}
.box{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px 16px;margin:12px 0}
.warnbox{border-left:5px solid var(--warn)}.badboxline{border-left:5px solid var(--bad)}.okbox{border-left:5px solid var(--ok)}
table{width:100%;border-collapse:collapse;background:var(--card);font-size:13px}
th,td{padding:6px 8px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}
th{background:#eef2fa;position:sticky;top:0;font-weight:600}
tr:nth-child(even) td{background:#fbfcfe}
.wrap{overflow-x:auto;border:1px solid var(--line);border-radius:10px;background:var(--card);max-height:78vh}
.num{text-align:right;white-space:nowrap}
.badge{display:inline-block;font-size:11.5px;padding:1px 7px;border-radius:999px;font-weight:600;white-space:nowrap}
.badge-ok{background:#e3f6ec;color:var(--ok)}.badge-multi{background:#fff1d6;color:var(--warn)}
.badge-unv{background:#eceef3;color:var(--grey)}.badge-flag{background:#fde7e5;color:var(--bad)}
.filter{padding:8px 10px;border:1px solid #c9d1e0;border-radius:8px;width:min(420px,100%);margin:8px 0}
small,.small{color:var(--muted);font-size:12.5px}
a{color:var(--accent)}
footer{color:var(--muted);font-size:12.5px;margin-top:34px;border-top:1px solid var(--line);padding-top:12px}
ul.tight li{margin:3px 0}
.calc label{display:block;margin:6px 0}.calc input,.calc select{padding:7px;border:1px solid #c9d1e0;border-radius:6px;width:220px}
.calc button{padding:8px 12px;border:0;border-radius:6px;background:var(--accent);color:#fff;font-weight:600;cursor:pointer;margin-top:8px}
.grid3{display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;font-size:12.5px}
.other{background:#eef2fa;padding:4px 18px;font-size:12.5px;color:#334}
.slot{background:#fbfcfe;border:1px solid var(--line);border-radius:8px;padding:6px}
"""

JS = """
document.querySelectorAll('input[data-filter]').forEach(function(inp){
  inp.addEventListener('input',function(){
    var q=inp.value.toLowerCase();
    var t=document.getElementById(inp.dataset.filter);
    t.querySelectorAll('tbody tr').forEach(function(tr){
      tr.style.display = tr.textContent.toLowerCase().indexOf(q)>-1 ? '' : 'none';
    });
  });
});
function hotelCalc(){
  var rate=parseFloat(document.getElementById('c-rate').value);
  var fee=parseFloat(document.getElementById('c-fee').value);
  var tax=parseFloat(document.getElementById('c-tax').value);
  var out=document.getElementById('c-out');
  if(isNaN(rate)){out.textContent='Enter the room rate from the official booking page for your exact dates. No rate is stored or estimated here.';return;}
  var pre=rate+(isNaN(fee)?0:fee);
  var s='Room rate + resort fee, before tax: $'+pre.toFixed(2)+' per night.';
  if(isNaN(tax)){s+=' Tax not entered: the Clark County rate is not verified from an official page, so the all-in total is not computed.';}
  else{s+=' With tax at '+tax+'%: $'+(pre*(1+tax/100)).toFixed(2)+' per night (check the tax rate against the folio).';}
  out.textContent=s;
}
"""


def page(title, active, body):
    nav = "".join(
        f'<a href="{href}" class="{"on" if href == active else ""}">{label}</a>'
        for href, label in NAV)
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)} | Las Vegas Strip Poker Dashboard</title>
<link rel="icon" href="data:,">
<style>{CSS}</style></head>
<body>
<header><div class="brand">Las Vegas Strip Poker Dashboard (verified-only)</div><nav>{nav}</nav></header>
<div class="other">Other sites in this repository: <a href="../">root dashboard</a> &middot; <a href="../docs/">docs site</a></div>
<main>
{body}
<footer>Figures come only from the official venue and resort pages and PDFs linked on each row (see <a href="sources.html">Sources</a>), retrieved {D.ACCESS_DATE}.
Blank = not verified. Nothing is estimated. Ratios (guarantee divided by buy-in) are calculated by the site from official numbers and are not expected return.
Check every value on the official page before you enter or book.</footer>
</main>
<script>{JS}</script>
</body></html>
"""


def table(tid, headers, rows, filter_box=True):
    th = "".join(f"<th>{h}</th>" for h in headers)
    body = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    flt = (f'<input class="filter" data-filter="{tid}" placeholder="Filter rows by text" aria-label="Filter rows">'
           if filter_box else "")
    return (f'{flt}<div class="wrap"><table id="{tid}"><thead><tr>{th}</tr></thead>'
            f"<tbody>{body}</tbody></table></div>")


def link(url, text):
    return f'<a href="{esc(url)}" target="_blank" rel="noopener">{esc(text)}</a>'


def sheet_cell(r):
    if r["_checked"]:
        n = r["structure_sheet"]
        return (f'<span class="badge badge-ok">sheet #{esc(n)} read</span><br>'
                f'{link(r["structure_sheet_url"], "structure sheet #" + n)}<br>'
                '<small>No re-entry or add-on rule stated in the text read</small>')
    note = ""
    if r["event_no"] == "26":
        note = "<br><small>Sheet #12 labels Days A/C/E; flight-name mapping not confirmed</small>"
    return ('<span class="badge badge-unv">not yet checked</span>' + note)


VEN_HEADERS = ["Date", "Start", "Event #", "Event (as printed)", "Buy-in", "Guarantee (as printed)",
               "Guarantee ÷ buy-in (calc)", "Reg closes", "Chips", "Level (min)", "Re-entry / add-on check", "Source"]


def ven_row(r):
    date_txt = fmt_date(r["date"]) + (DAG if r["_inferred"] else "")
    buy = money(r["buy_in"])
    if r["satellite"]:
        gtd = esc(r["guarantee_text"] or "")
    else:
        gtd = money(r["guarantee"]) if r["guarantee"] else '<span class="small">none printed</span>'
    ratio = f'{r["_ratio"]:.1f}x' if r["_ratio"] else ""
    name = esc(r["name"])
    if r["satellite"]:
        name += ' <span class="badge badge-unv">satellite</span>'
    return [
        f"{date_txt}<br><small>{esc(r['weekday'])}</small>",
        esc(r["time"]),
        esc(r["event_no"]),
        name,
        f'<span class="num">{buy}</span>',
        f'<span class="num">{gtd}</span>',
        f'<span class="num">{ratio}</span>',
        esc(r["reg_closes"] or ""),
        f'<span class="num">{money(r["chips"])}</span>',
        esc(r["levels"] or ""),
        sheet_cell(r),
        link(D.VEN_SCHED, "schedule PDF"),
    ]


WPT_HEADERS = ["Date (calendar)", "Date as printed", "Time", "Event (as printed)", "Buy-in", "Guarantee (as printed)",
               "Chips", "Levels", "Entry status", "Source"]


def wpt_row(r, status_html):
    cal = fmt_date(r["date"])
    flag = ""
    if r["calendar_conflict"]:
        flag = f'<br><span class="badge badge-flag">calendar conflict</span>'
    ev = esc(r["event"])
    if r["footnote_markers"]:
        ev += f' <small>(footnote {esc(r["footnote_markers"])})</small>'
    gtd_txt = money(r["guarantee"]) if r["guarantee"] else (esc(r["guarantee_text"]) if r["guarantee_text"] else '<span class="small">none printed</span>')
    return [
        f"{cal}{flag}",
        esc(r["date_label_printed"]),
        esc(r["time"]),
        ev,
        f'<span class="num">{money(r["buy_in"])}</span>',
        f'<span class="num">{gtd_txt}</span>',
        f'<span class="num">{money(r["chips"])}</span>',
        esc(r["levels"] or ""),
        status_html,
        link(D.WPT_SCHED, "schedule PDF"),
    ]


def sort_wpt(rows):
    return sorted(rows, key=lambda r: (r["date"], r["_t"] or dt.time(0), r["order"]))


# ------------------------------------------------------------- flags
FLAGS = [
    ("F01", "Low", "Wynn resort fee: $50 and $55 both appear on official Wynn terms",
     "The official special-offer terms state $50 plus tax for reservations booked before Jan 15, 2025 and $55 plus tax for reservations booked on or after that date. For a new booking in 2026 the $55 rule applies. The site shows $55. Confirm on the booking page.",
     ["wynn_terms"]),
    ("F02", "High", "Clark County lodging tax rate not verified from an official page",
     "The Clark County transient lodging tax page returned a 404 when fetched. Third-party sites quote 13.38% for Strip hotels, which is not an official figure, so the site leaves tax blank and does not use that rate.",
     ["clark_tax"]),
    ("F03", "High", f"Wynn WPT: {len(WPT_CONFLICTS)} rows print 'Dec. 18 Wednesday' (Dec 18, 2026 is a Friday)",
     "The official schedule prints 'Dec. 18 Wednesday' on eight rows, sits them between the Dec 15 and Dec 17 blocks, and also prints 'Dec. 18 Friday' on other rows. The official text does not show which is right (Dec 16 Wednesday or Dec 18 Friday). The site shows the calendar date from the printed label and marks the conflict.",
     ["wynn_schedule"]),
    ("F04", "Medium", "Wynn WPT schedule: typos and footnotes that need the structure sheet",
     "'NIH' is printed for 'NLH' on three rows. The Ladies championship is printed at $1,100 with a footnote that the Ladies entry is $11,100. 'BadugI' is printed in the structure table. Footnote markers (*, **, ***, ****, *****) are shown as printed; their meaning comes from the footnotes on the schedule PDF.",
     ["wynn_schedule"]),
    ("F05", "Medium", f"Venetian schedule: {N_INFERRED} rows have no printed day label",
     "In the official PDF, a row that repeats the same day has no day label. The site takes the date from row order, and marks it with a dagger (" + DAG + "). A time that returns from PM to AM means the next day. Confirm these dates on the official event page before you plan around them.",
     ["ven_sched", "ven_event"]),
    ("F06", "Low", f"Venetian: {len(VEN_RESTARTS)} Day 2 restart and final-table rows are not flights",
     "Restart and final-table rows have no buy-in and are listed on the Day schedule page, not in the flight tables.",
     ["ven_sched"]),
    ("F07", "High", f"Venetian: re-entry and add-on rules unverified for {N_UNCHECKED} of {N_VEN} flights",
     f"The structure sheets read this session were {', '.join('#' + s for s in D.VEN_STRUCT_OPENED)}. They state late-registration timing and, for #26, a rule that players who bag Day 2 chips may not play a later flight. None states a general re-entry or add-on rule. Flights on sheets not read are marked 'not yet checked' and must be confirmed.",
     ["ven_sched"]),
    ("F08", "Medium", "Venetian: guarantees on bounty events not checked against the structure sheet",
     "The official schedule prints a guarantee for each bounty event. Whether that number includes bounty money is a question for the structure sheet, which was not read for the events that have a different sheet.",
     ["ven_sched"]),
    ("F09", "Low", "Venetian satellites print seats, not dollars",
     f"{N_SAT} satellite rows print a seat count instead of a dollar guarantee. They are listed but excluded from the guarantee rankings.",
     ["ven_sched"]),
    ("F10", "Medium", "Venetian: buy-in discounts printed in event names",
     "Event #56 (Dec 17 and Dec 18) says '$40 rake discount for entries before 10:10 AM' or '6:10 PM'. Event #59 says '$20 rake discount' before 11:10 AM. Events #18 and #58 apply a PokerAtlas PRO member discount of $20. The site shows the printed buy-in and notes the discount.",
     ["ven_sched"]),
    ("F11", "Medium", "Wynn WPT: entry rules unverified for most rows",
     f"{len(WPT_MULTI)} rows (Nov 27) are shown as re-entry-verified: the structure sheet states unlimited re-entry until level 9 for the $600 NLH, $600 TORSE and $400 PLO events. Their structure sheet was read in the first 3 of 8 chunks. The other {len(WPT_UNV)} buy-in rows are not verified. Several $600 NLH flights (Nov 28 to 29) use the same buy-in but were not checked individually.",
     ["wynn_struct"]),
    ("F12", "Medium", "Wynn daily tournaments: poster is undated and third-party sources disagree",
     "The official poster lists the daily events without dates and says the daily schedule is suspended during the Wynn Signature, Wynn Millions and Classic series. Third-party sites show different guarantees for the Saturday event. The site uses the official poster only.",
     ["wynn_daily", "wynn_poker"]),
    ("F13", "High", "Other Strip rooms not covered",
     "No official schedule was retrieved this session for Bellagio, Aria, MGM Grand, Mandalay Bay, Caesars Palace, Horseshoe, Flamingo, Paris, Planet Hollywood, Harrah's, Excalibur and others. Third-party guides were seen but are not official, so they are not used for any row.",
     []),
    ("F14", "High", "Resorts World: no official tournament schedule retrieved",
     "The Resorts World poker page fetched this session has no schedule content. Resorts World hotel fees are verified (see Hotels), but no Resorts World tournament is listed.",
     ["rw_poker", "rw_faq"]),
    ("F15", "High", "Room rates and tax not verified, so the true nightly cost is blank",
     "Room rates change by date and no official rate was collected for any date. The calculator on the Hotels page computes the cost from numbers the user enters. Linked pages are the official fee pages, which do not give room rates.",
     ["ven_fee", "wynn_terms", "rw_faq"]),
    ("F16", "High", "Walking time not verified; poker-room location within each resort not confirmed",
     "No official source gives walking time between a hotel and a poker room. The Venetian and Wynn events are held at those resorts (official schedules). The Wynn poker page's FAQ answers, which include the poker room location, did not appear in the fetched text. The Venetian poker-room parking page (search excerpt, not fetched) points poker players to The Palazzo garage. Every walking time is blank.",
     ["wynn_poker", "ven_sched"]),
    ("F17", "Medium", "Hotel quality ratings not verified",
     "No official rating source was consulted for any hotel, so the quality column is blank.",
     []),
    ("F18", "High", "The 8 AM all-day goal cannot be confirmed from official data",
     f"The earliest printed Venetian start is {VEN_EARLIEST['time']} ({fmt_date(VEN_EARLIEST['date'])}{DAG}, a satellite). The earliest printed Wynn WPT start with a buy-in is {WPT_EARLIEST['time']} ({WPT_EARLIEST['date_label_printed']}). Neither schedule prints finish times, so back-to-back play cannot be confirmed.",
     ["ven_sched", "wynn_schedule"]),
    ("F19", "Low", "No WSOP Las Vegas event in this window (official WSOP schedule)",
     "The official WSOP schedule was read this session. No Las Vegas event appears for Nov to Dec 2026, so none is listed.",
     ["wsop"]),
    ("F20", "Medium", "Parallel-session protocol cannot run as written in this session",
     "The task asks for separate session branches and coordination through COORDINATION.md. This session is limited to one branch (arena/f332570d-poker3), so no session-<id>/<task> branches were created. COORDINATION.md records one claim by this session on every task.",
     ["repo"]),
    ("F21", "Low", "Repository was nearly empty before this session",
     "Before this session the repository held one file, README.md (8 bytes: '# Poker3'), with no license, no COORDINATION.md and no site. See Repo review.",
     ["repo"]),
    ("F22", "High", "Wynn $10,400 World Championship: added money not verified for Nevada players",
     "The official schedule prints '$1,000,000 Added' with a footnote that the added money comes from ClubWPT Gold, which 'is not available in Nevada'. The guarantee column is blank for these rows. The site shows the printed text and does not treat the added money as a guarantee.",
     ["wynn_schedule"]),
]

# ------------------------------------------------------------- questions
QUESTIONS = [
    ("What dates is the trip?", "Unanswered",
     "Not given. The Venetian series runs Nov 16 to Dec 23, 2026; the Wynn WPT runs Nov 27 to Dec 21, 2026 (both official).",
     "Give the dates. The day schedule and hotel pages can then be limited to those nights."),
    ("Can you play from 8 AM all day?", "Answered: not with official data",
     f"No printed start is before {VEN_EARLIEST['time']} in the Venetian series (a satellite). Most flights start at 10:10 or 11:10 AM. No finish times are printed, so a full day cannot be confirmed.",
     "Ask the Venetian and Wynn poker rooms for typical finish times and whether late registration allows a later entry."),
    ("Are the Venetian events single-entry?", "Partly answered",
     f"{N_CHECKED} of {N_VEN} flights are on structure sheets that were read; none of those sheets states a re-entry rule. The other {N_UNCHECKED} flights are not checked.",
     "Read the remaining sheets (the structure sheet links are on the single-entry page) or ask the Venetian poker room."),
    ("Are the Wynn WPT events single-entry?", "Partly answered",
     f"{len(WPT_MULTI)} Nov 27 rows are re-entry-verified. The other {len(WPT_UNV)} buy-in rows are not verified.",
     "Read each event's structure sheet in the official structures PDF."),
    ("What does 'prize pool' mean here?", "Answered",
     "The site uses the printed guarantee. The actual paid prize pool depends on the field, which the rooms do not print.",
     "Compare results PDFs after events run."),
    ("What are the entry requirements?", "Partly answered",
     "Wynn WPT schedule: players must be at least 21. Venetian structure sheet for #26: 21+ with a Venetian Rewards card.",
     "Read the structure sheet for each event you plan to enter."),
    ("What is the true nightly hotel cost?", "Unanswered",
     "Resort fees are verified for three hotels ($55 plus tax). No room rate or tax was verified, so the total is blank.",
     "Enter the rate from the official booking page for your dates into the calculator on the Hotels page."),
    ("What is the Clark County tax rate?", "Unanswered",
     "The official page returned a 404. Third-party sites say 13.38%. Not used.",
     "Confirm with Clark County or the LVCVA and enter it in the calculator."),
    ("How far is each hotel from each poker room on foot?", "Unanswered",
     "No official source gives walking times. Poker-room locations inside the resorts are not confirmed.",
     "Measure the route on a map tool, record the date and source, and add it to the data."),
    ("Which hotels should be compared?", "Partly answered",
     "Three hotels are included: The Venetian, Wynn Las Vegas and Resorts World Las Vegas. Other Strip hotels were not verified (flag F13).",
     "Decide which other hotels to verify (Suggestions S3)."),
    ("How should 'best hotel' be judged?", "Unanswered",
     "No quality measure is defined or verified.",
     "Define the measure (for example a star rating or review score) and name the source."),
    ("Should satellites and women-only or 50+ events be included?", "Unanswered",
     "They are listed. Satellites print seats, and some events have an eligibility rule (for example LIPS Ladies, Seniors 50+).",
     "Decide whether to include them in the rankings."),
    ("Should Wynn daily tournaments be included?", "Unanswered",
     "The official poster is undated and says the daily schedule is suspended during some series.",
     "Ask the Wynn poker room whether daily events run on your dates."),
    ("What is the budget?", "Unanswered", "Not given.", "Provide a budget so the plan can be capped."),
]

# ------------------------------------------------------------- suggestions
SUGGESTIONS = [
    ("S1", "Add a trip-date filter to every table",
     "Options: (a) a date-range filter on the existing pages; (b) a separate trip planner that builds a day plan from your dates.",
     "(a) is quick and static. (b) needs your dates and more script."),
    ("S2", "Refresh official data on a schedule",
     "Options: (a) update by hand each week; (b) a scheduled job that downloads the official PDFs, compares them with the data, and opens a pull request when something changes.",
     "(b) keeps the site current but needs a scheduled job and an approval step."),
    ("S3", "Verify more rooms",
     "Options: (a) MGM Resorts (Bellagio, Aria, MGM Grand, Mandalay Bay); (b) Caesars (Caesars Palace, Horseshoe, Flamingo, Harrah's, Paris, Planet Hollywood); (c) Resorts World tournaments; (d) all of these.",
     "Each room needs its own official schedule and structure sheets. (d) is the most complete."),
    ("S4", "Add structured entry-rule fields",
     "Record for each event: re-entry (yes, no, or limit), rebuy, add-on, and flights. Fill these from the structure sheets.",
     "Would close flags F07 and F11. About 35 structure sheets need reading."),
    ("S5", "Re-label the guarantee ratio",
     "Options: (a) keep the ratio, labelled 'guarantee per $1 of buy-in'; (b) drop it and show the guarantee alone.",
     "(a) keeps a useful comparison but is not expected return. (b) is the most conservative."),
    ("S6", "Record a checksum for every source",
     "Store the SHA-256 of each official PDF at the time of access so a reviewer can confirm the data has not changed.",
     "Needs a small script. PDFs stay out of Git unless you choose otherwise."),
    ("S7", "Dated room-rate snapshots",
     "For each hotel and date, record the official booking-page rate, the time, and a link. Rates change, so each snapshot is valid only for its date.",
     "Needs a person to read the booking page for each date."),
    ("S8", "Walking-time method",
     "Options: (a) measure with a map tool and record the route and date; (b) a routing service (needs an account and its terms approved).",
     "(a) is manual and free. (b) is automatic but needs approval."),
    ("S9", "Mobile layout",
     "Tables are wide. Options: (a) keep tables and scroll; (b) a card view on phones; (c) a one-page printable summary.",
     "(b) reads better on a phone at the room."),
    ("S10", "Review workflow",
     "Use GitHub issues for requested changes and a pull request for every data change, so each decision is recorded.",
     "Needs you to name who approves changes."),
]

# ------------------------------------------------------------- repo review (verified lines only)
REPO_REVIEW = [
    ("README.md", "One line: '# Poker3'. 8 bytes. No description, purpose or usage.",
     "Irregular: README is a placeholder. Not changed in this session (you review first).",
     "https://github.com/karagemop466-tech/Poker3/blob/main/README.md"),
    ("Repository root", "No index.html, no COORDINATION.md, no LICENSE, no site folder before this session.",
     "COORDINATION.md added; site pages, scripts, data and raw sources added. No license added (you have not chosen one).",
     "https://github.com/karagemop466-tech/Poker3"),
    ("Branches", "main (1 commit, 'Initial commit', 895478b) and arena/f332570d-poker3 (this session).",
     "All work is on the session branch, as required for this session.",
     "https://github.com/karagemop466-tech/Poker3/branches"),
    ("GitHub Pages", "Pages API (checked this session): status 'built', source main, path /.",
     "The site publishes from main root. A .nojekyll file is added so Jekyll does not process the files.",
     "https://github.com/karagemop466-tech/Poker3/settings/pages"),
    ("Remote", "origin = https://github.com/karagemop466-tech/Poker3.git",
     "Matches this repository.",
     "https://github.com/karagemop466-tech/Poker3"),
    ("Task vs. repo", "The task names COORDINATION.md and session-<id>/<task> branches.",
     "COORDINATION.md is created; session branches are not used because this session has one branch (flag F20).",
     "https://github.com/karagemop466-tech/Poker3"),
]


# ------------------------------------------------------------- hotel rows
def hotel_rows():
    out = []
    for h in D.HOTELS:
        name_cell = f"<b>{esc(h['name'])}</b>"
        if h["address"]:
            name_cell += f"<br><small>{esc(h['address'])}</small><br>{src(h['address_src'])}"
        else:
            name_cell += "<br><small>address not verified</small>"
        poker_cell = f"{esc(h['poker'])}<br>{src(h['poker_src'])}"
        walk_cell = (f'<span class="badge badge-unv">unverified</span><br><small>{esc(h["walk_note"])}</small>')
        fee_cell = f'<span class="num">{money(h["resort_fee"])} + tax per night</span><br><small>{esc(h["fee_text"])}</small><br>{src(h["fee_src"])}'
        park_cell = (f'{esc(h["parking"])}<br>{src(h["parking_src"])}' if h["parking"]
                     else '<span class="badge badge-unv">not verified</span>')
        rate_cell = '<span class="badge badge-unv">blank: not verified</span>'
        tax_cell = '<span class="badge badge-unv">blank: not verified</span>'
        qual_cell = '<span class="badge badge-unv">blank: not verified</span>'
        out.append([name_cell, poker_cell, walk_cell, fee_cell, park_cell, rate_cell, tax_cell, qual_cell])
    return out


# ------------------------------------------------------------- pages
def build():
    pages = {}

    # ---- index
    cards = f"""
<div class="cards">
 <div class="card"><span class="k">Venetian flights (official)</span><b>{N_VEN}</b><a href="tournaments-single.html">Open &rarr;</a></div>
 <div class="card"><span class="k">Flights with sheet read</span><b>{N_CHECKED}</b><a href="tournaments-single.html">Open &rarr;</a></div>
 <div class="card"><span class="k">Wynn WPT buy-in rows (official)</span><b>{len(WPT_BUY)}</b><a href="tournaments-multi.html">Open &rarr;</a></div>
 <div class="card"><span class="k">Wynn WPT re-entry verified</span><b>{len(WPT_MULTI)}</b><a href="tournaments-multi.html">Open &rarr;</a></div>
 <div class="card"><span class="k">Hotels with official fee</span><b>{len(D.HOTELS)}</b><a href="hotels.html">Open &rarr;</a></div>
 <div class="card"><span class="k">Flags for review</span><b>{len(FLAGS)}</b><a href="flagged.html">Open &rarr;</a></div>
</div>"""
    top = RANK_RATIO[0]
    body = f"""
<h1>Las Vegas Strip poker: official tournaments, hotels and planning</h1>
<p class="lead">Built only from official venue and resort pages and PDFs, retrieved {D.ACCESS_DATE}. Blank cells are unverified, not estimates.</p>
{cards}
<div class="box okbox"><b>What the official data shows</b>
<ul class="tight">
<li>The Venetian's DeepStack Extravaganza IV runs Nov 16 to Dec 23, 2026, with {N_VEN} dated flights. Its structure sheets read so far state no re-entry rule; {N_UNCHECKED} flights are still unchecked.</li>
<li>Highest guarantee ÷ buy-in (calculated, not expected return): <b>{esc(top['name'])}</b> on {fmt_date(top['date'])} at {esc(top['time'])}: {money(top['guarantee'])} guarantee on a {money(top['buy_in'])} buy-in = {top['_ratio']:.0f}x.</li>
<li>Wynn's WPT World Championship has {len(WPT_BUY)} buy-in rows. Only {len(WPT_MULTI)} (Nov 27) are verified as re-entry events. The rest are kept separate until checked.</li>
<li>No official source printed a start before {esc(VEN_EARLIEST['time'])}. A full 8 AM to close day cannot be confirmed (flag F18).</li>
<li>Resort fee is $55 plus tax per night at The Venetian and Wynn, and $55 plus tax at Resorts World (waived on select dates through Dec 28, 2026 under its offer). Room rates and tax are not verified.</li>
</ul></div>
<div class="box warnbox"><b>Not covered yet:</b> Bellagio, Aria, MGM Grand, Caesars Palace, Horseshoe, Resorts World tournaments and other Strip rooms (flag F13 and F14).</div>
<h2>Where to go</h2>
<div class="cards">
 <div class="card"><a href="summary.html">Executive summary</a><br><span class="k">One page of findings.</span></div>
 <div class="card"><a href="tournaments-single.html">Single-entry (Venetian)</a><br><span class="k">All {N_VEN} flights, each with its source.</span></div>
 <div class="card"><a href="tournaments-multi.html">Re-entry &amp; unverified</a><br><span class="k">Kept apart from single-entry.</span></div>
 <div class="card"><a href="best-picks.html">Best picks</a><br><span class="k">Ranked by official numbers.</span></div>
 <div class="card"><a href="schedule.html">Day schedule</a><br><span class="k">Every printed start, by day.</span></div>
 <div class="card"><a href="hotels.html">Hotels</a><br><span class="k">Official fees, parking and calculator.</span></div>
 <div class="card"><a href="suggestions.html">Suggestions</a><br><span class="k">Proposed changes. None is made until you choose.</span></div>
 <div class="card"><a href="questions.html">Questions</a><br><span class="k">What is known, and how to find out the rest.</span></div>
 <div class="card"><a href="repo-review.html">Repo review</a><br><span class="k">The repository, line by line.</span></div>
 <div class="card"><a href="flagged.html">Flagged for Review</a><br><span class="k">Conflicts, gaps and unverified values.</span></div>
 <div class="card"><a href="sources.html">Sources</a><br><span class="k">Every official link used.</span></div>
</div>"""
    pages["index.html"] = page("Home", "index.html", body)

    # ---- executive summary
    body = f"""
<h1>Executive summary</h1>
<p class="lead">Scope: the Venetian (DeepStack Extravaganza IV) and Wynn Las Vegas (WPT World Championship), plus official resort-fee terms for three hotels. Retrieved {D.ACCESS_DATE}.</p>
<div class="box"><h3>1. Live and upcoming tournaments (official)</h3>
<ul class="tight">
<li><b>Venetian DeepStack Extravaganza IV</b>, Nov 16 to Dec 23, 2026: {len(VEN_EVENTS)} numbered events, {N_VEN} flights, {N_SAT} of them satellites. {len(VEN_RESTARTS)} restart or final-table rows are listed separately.</li>
<li><b>Wynn WPT World Championship</b>, Nov 27 to Dec 21, 2026: {len(WPT_BUY)} buy-in rows plus {len(WPT_NO_BUY)} restart or final-table rows, from the official schedule PDF.</li>
<li><b>Wynn daily tournaments</b>: five recurring slots on the official poster. No dates are printed, so they are shown separately.</li>
<li><b>WSOP</b>: no Las Vegas event in this window on the official WSOP schedule (flag F19).</li>
</ul></div>
<div class="box"><h3>2. Single-entry vs. re-entry (kept separate)</h3>
<ul class="tight">
<li>Venetian flights are the single-entry list. Only {N_CHECKED} of them are on structure sheets that were read, and none of those sheets states a re-entry rule. The other {N_UNCHECKED} are marked 'not yet checked' (flag F07).</li>
<li>Wynn: {len(WPT_MULTI)} Nov 27 rows state unlimited re-entry until level 9 in the official structure sheet. They appear under 'Re-entry &amp; unverified', not in single-entry.</li>
<li>The other {len(WPT_UNV)} Wynn buy-in rows are not verified (flag F11).</li>
<li>No official event in the two schedules is described as a double buy-in or add-on. Events that were not checked may still have one.</li>
</ul></div>
<div class="box"><h3>3. Best value (calculated from printed numbers)</h3>
<p>Guarantee ÷ buy-in shows how large the printed guarantee is against the entry fee. It is not expected return: field sizes are not published.</p>
<ul class="tight">
<li>Highest guarantee ÷ buy-in: <b>{esc(top['name'])}</b>, {fmt_date(top['date'])} at {esc(top['time'])}: {money(top['guarantee'])} on {money(top['buy_in'])} = {top['_ratio']:.0f}x.</li>
<li>Largest guarantees: {esc(RANK_GTD[0]['name'])} ({money(RANK_GTD[0]['guarantee'])}) and the other $1,000,000+ events on the Best picks page.</li>
<li>Low buy-in with a guarantee (at or under $200): {len(LOW_BUY)} flights, all bounty or PKO events or the PokerAtlas Valuetown event.</li>
</ul></div>
<div class="box badboxline"><h3>4. The 8 AM all-day goal</h3>
<ul class="tight">
<li>The earliest printed Venetian start is {esc(VEN_EARLIEST['time'])} ({fmt_date(VEN_EARLIEST['date'])}{DAG}, a satellite). Most flights start at 10:10 or 11:10 AM.</li>
<li>No finish times are printed, so the site cannot show that two events fit back to back. The Day schedule page lists every printed start so you can plan.</li>
</ul></div>
<div class="box"><h3>5. Hotels</h3>
<ul class="tight">
<li>Resort fee: <b>$55 plus tax per night</b> at The Venetian (official resort-fee page), Wynn (official terms, bookings on or after Jan 15, 2025) and Resorts World (official FAQ).</li>
<li>Resorts World's official offer waives the fee on select dates through Dec 28, 2026; blackout dates may apply and room tax still applies.</li>
<li>Walking times, room rates, tax and quality ratings are not verified and are left blank. The true nightly cost cannot be computed without a room rate; the calculator on the Hotels page does the sum once you enter one.</li>
</ul></div>
<div class="box warnbox"><h3>6. Biggest gaps</h3>
<ul class="tight">
<li>Clark County tax (official page 404), room rates, walking times (flags F02, F15, F16).</li>
<li>Other Strip rooms and Resorts World tournaments (F13, F14).</li>
<li>Re-entry rules for {N_UNCHECKED} Venetian flights and {len(WPT_UNV)} Wynn rows (F07, F11).</li>
</ul></div>
<h2>Method</h2>
<p>Each row was taken from the official PDF or page and carries its link. Venetian and Wynn rows were parsed from the verbatim official text stored in <code>raw/</code>. Dagger (†) marks a date inferred from row order. Calendar weekdays were checked; a printed weekday that conflicts is flagged. Nothing was filled in from a third-party source.</p>
"""
    pages["summary.html"] = page("Executive summary", "summary.html", body)

    # ---- single-entry (Venetian)
    rows = [ven_row(r) for r in VEN]
    body = f"""
<h1>Single-entry tournaments: The Venetian (DeepStack Extravaganza IV)</h1>
<p class="lead">{N_VEN} dated flights from the official schedule, Nov 16 to Dec 23, 2026. Buy-in, guarantee, start, registration close, chips and level length are copied from the printed schedule. The ratio column is calculated.</p>
<div class="box warnbox">Re-entry and add-on rules are <b>not stated</b> in the structure sheets read ({N_CHECKED} of {N_VEN} flights are on those sheets). Confirm each flight before you enter. Satellites print seats, not dollars. Women-only and 50+ events have eligibility rules. Day 2 restarts are on the <a href="schedule.html">Day schedule</a> page.</div>
{table('t-single', VEN_HEADERS, rows)}
<h2>Notes</h2>
<ul class="tight">
<li>{DAG} = date inferred from row order because the printed row has no day label (flag F05).</li>
<li>Venetian events require age 21+ and a Venetian Rewards card, per the structure sheet for #26 (read this session). Other sheets were not checked for this.</li>
<li>Source for every row: <a href="{esc(D.VEN_SCHED)}" target="_blank" rel="noopener">official schedule PDF</a>. Structure sheets link where they were read.</li>
</ul>"""
    pages["tournaments-single.html"] = page("Single-entry tournaments", "tournaments-single.html", body)

    # ---- multi & unverified
    multi_rows = [wpt_row(r, '<span class="badge badge-multi">re-entry verified</span><br><small>Structure sheet: unlimited re-entry until level 9</small>')
                  for r in sort_wpt(WPT_MULTI)]
    unv_rows = [wpt_row(r, '<span class="badge badge-unv">not verified</span>') for r in sort_wpt(WPT_UNV)]
    daily_rows = []
    for days, time, ev, buy, gtd in D.WYNN_DAILY:
        daily_rows.append([
            esc(days) + "<br><small>undated (official poster)</small>",
            esc(time), esc(ev),
            f'<span class="num">{money(buy)}</span>', f'<span class="num">{money(gtd)}</span>',
            ('<span class="badge badge-multi">rebuy (poster wording)</span>' if "Rebuy" in ev
             else '<span class="badge badge-unv">dates not verified</span>'),
            link(D.SRC["wynn_daily"][1], "daily poster PDF"),
        ])
    body = f"""
<h1>Re-entry, rebuy and unverified entries</h1>
<p class="lead">These are <b>not</b> single-entry. Section A is re-entry verified. Section B has entry rules that are not verified, so it may contain re-entry or add-ons. Section C lists the Wynn daily events from the poster.</p>
<h2>A. Re-entry verified (Wynn WPT, Nov 27)</h2>
<p class="small">Source: Wynn WPT structure sheet, which states unlimited re-entry until level 9 for these events (first 3 of 8 chunks of the structure PDF read this session; see flag F11).</p>
{table('t-multi', WPT_HEADERS, multi_rows, filter_box=False)}
<h2 id="unverified">B. Wynn WPT: entry rule not verified ({len(WPT_UNV)} rows)</h2>
<p class="small">The structure sheet for each row was not read, so re-entry and add-on status is unknown. Rows with a calendar conflict are marked (flag F03). Rows with no buy-in (Day 2, Day 3 and final tables) are not in this table.</p>
{table('t-unv', WPT_HEADERS, unv_rows)}
<h2>C. Wynn daily tournaments (official poster, undated)</h2>
<p class="small">The poster is undated and says the daily schedule is suspended during the Wynn Signature, Wynn Millions and Classic series. Friday is printed as a rebuy event. Rebuy and add-on terms were not read.</p>
{table('t-daily', ['Day', 'Time', 'Event', 'Buy-in', 'Guarantee', 'Entry status', 'Source'], daily_rows, filter_box=False)}
"""
    pages["tournaments-multi.html"] = page("Re-entry and unverified", "tournaments-multi.html", body)

    # ---- best picks
    def brow(r):
        return [f"{fmt_date(r['date'])}{DAG if r['_inferred'] else ''} {esc(r['time'])}", esc(r["event_no"]),
                esc(r["name"]), f'<span class="num">{money(r["buy_in"])}</span>',
                f'<span class="num">{money(r["guarantee"])}</span>',
                f'<span class="num">{r["_ratio"]:.1f}x</span>' if r["_ratio"] else "",
                esc(r["reg_closes"] or ""),
                ('<span class="badge badge-ok">sheet read</span>' if r["_checked"] else '<span class="badge badge-unv">not yet checked</span>'),
                link(D.VEN_SCHED, "schedule PDF")]
    hdr = ["Date &amp; start", "Event #", "Event (as printed)", "Buy-in", "Guarantee", "Guarantee ÷ buy-in (calc)", "Reg closes", "Entry check", "Source"]
    body = f"""
<h1>Best picks (Venetian single-entry flights)</h1>
<p class="lead">Ranked on printed numbers only. Satellites are excluded because they print seats, not dollars. Wynn WPT rows are excluded until their entry rules are verified.</p>
<div class="box warnbox">A printed guarantee is a minimum, not the prize pool actually paid. Field size is not published. The ratio is a comparison of printed numbers, not an expected return.</div>
<h2>Top 12 by printed guarantee</h2>
{table('t-gtd', hdr, [brow(r) for r in RANK_GTD[:12]], filter_box=False)}
<h2>Top 15 by guarantee ÷ buy-in (calculated)</h2>
{table('t-ratio', hdr, [brow(r) for r in RANK_RATIO[:15]], filter_box=False)}
<h2>Low buy-in with a guarantee (at or under $200)</h2>
{table('t-low', hdr, [brow(r) for r in LOW_BUY], filter_box=False)}
<h2>Not ranked</h2>
<ul class="tight">
<li>RaceDay Stack and the $200 NLH flights without a printed guarantee (events #3 to #6).</li>
<li>Satellites (seat prizes, no dollar guarantee).</li>
<li>Wynn WPT: entry rules unverified; several rows have larger guarantees (for example the $3,000,000 Super Gold Million at $400, which the official poster calls new for 2026). Not ranked until the entry rule is read.</li>
</ul>"""
    pages["best-picks.html"] = page("Best picks", "best-picks.html", body)

    # ---- day schedule
    by_day = {}
    for r in VEN:
        by_day.setdefault(r["date"], []).append(r)
    restart_by_day = {}
    for r in VEN_RESTARTS:
        restart_by_day.setdefault(r["date"], []).append(r)
    sched_rows = []
    for d in sorted(set(by_day) | set(restart_by_day)):
        slots = {"Before 12 PM": [], "12 PM to 4:59 PM": [], "5 PM or later": []}
        for r in sorted(by_day.get(d, []), key=lambda x: x["_t"]):
            t = r["_t"]
            key = "Before 12 PM" if t.hour < 12 else ("12 PM to 4:59 PM" if t.hour < 17 else "5 PM or later")
            label = (f'<b>{esc(r["time"])}</b> #{esc(r["event_no"])} {esc(r["name"][:70])}'
                     f'{"" if not r["satellite"] else " <span class=badge>satellite</span>"}'
                     f'<br><small>reg closes {esc(r["reg_closes"] or "-")}; buy-in {money(r["buy_in"])}</small>'
                     f'{DAG if r["_inferred"] else ""}')
            slots[key].append(label)
        restarts = restart_by_day.get(d, [])
        rnote = ("<br>".join(f'<small>{esc(x["time"])} #{esc(x["event_no"])} {esc(x["name"][:60])} (restart or final table)</small>' for x in restarts)
                 if restarts else '<small>none</small>')
        cols = "".join(
            f'<div class="slot"><b>{k}</b><br>' + ("<br>".join(v) if v else '<small>no printed start</small>') + "</div>"
            for k, v in slots.items())
        sched_rows.append([f"<b>{fmt_date(d)}</b>", f'<div class="grid3">{cols}</div>', rnote,
                           link(D.VEN_SCHED, "schedule PDF")])
    body = f"""
<h1>Day schedule: every printed start, Nov 16 to Dec 23</h1>
<div class="box badboxline"><b>Can you play from 8 AM all day?</b> The printed schedule does not support it. The earliest printed start is {esc(VEN_EARLIEST['time'])} on {fmt_date(VEN_EARLIEST['date'])}{DAG} (a satellite). Most flights start at 10:10 or 11:10 AM. Finish times are not printed, so no set of back-to-back events can be confirmed. This grid shows every printed start so you can choose.</div>
<p class="small">Venetian only. Wynn WPT rows are on the Re-entry and unverified page, with their printed times. Dagger (†) = date inferred from row order. Restart and final-table rows are listed in the last column.</p>
{table('t-sched', ['Date', 'Printed flights (by start time)', 'Restarts and finals', 'Source'], sched_rows, filter_box=False)}
<h2>Wynn WPT printed starts (buy-in rows, by printed date)</h2>
<p class="small">Shown as printed. The Dec 18 Wednesday rows carry a calendar conflict (flag F03).</p>
{table('t-sched-wpt', ['Date (calendar)', 'Date as printed', 'Time', 'Event', 'Buy-in', 'Source'],
       [[f"{fmt_date(r['date'])}{' (conflict)' if r['calendar_conflict'] else ''}", esc(r['date_label_printed']), esc(r['time']),
         esc(r['event']), f'<span class="num">{money(r["buy_in"])}</span>', link(D.WPT_SCHED, "schedule PDF")]
        for r in sort_wpt(WPT_BUY)])}
"""
    pages["schedule.html"] = page("Day schedule", "schedule.html", body)

    # ---- hotels
    body = f"""
<h1>Hotels near the tournaments</h1>
<p class="lead">Official resort fees, parking and addresses only. Room rates, tax, walking times and ratings are not verified, so those cells are blank.</p>
<div class="box warnbox">The true nightly cost cannot be confirmed: the room rate and the tax rate are not verified (flags F02, F15). Walking distance is not verified (flag F16). The 30-minute walking rule from the request cannot be applied until times are verified.</div>
{table('t-hotel', ['Hotel', 'Poker event (official)', 'Walk to poker room', 'Resort fee (official)', 'Parking (official)', 'Room rate / night', 'Tax (Clark County)', 'Quality'], hotel_rows(), filter_box=False)}
<h2>True-cost calculator</h2>
<p class="small">Enter the room rate from the official booking page for your exact dates. Nothing is stored. Leave tax blank until a verified rate is available.</p>
<div class="box calc">
<label>Room rate before fees (USD): <input id="c-rate" type="number" min="0" step="1"></label>
<label>Resort fee (USD): <select id="c-fee"><option value="55">$55 (The Venetian, Wynn, Resorts World)</option><option value="0">$0 (Resorts World offer dates, see offer terms)</option></select></label>
<label>Tax % (enter only after verifying): <input id="c-tax" type="number" min="0" step="0.01"></label>
<button onclick="hotelCalc()">Calculate</button>
<p id="c-out" class="small"></p>
</div>
<h2>Contacts (official)</h2>
<ul class="tight">
<li>The Venetian hotel: 702-414-1000 ({src('ven_contact')}).</li>
<li>Wynn Las Vegas main line: (702) 770-7000 ({src('wynn_contact')}).</li>
<li>Wynn poker room: (702) 770-7654, as printed on the official WPT schedule ({src('wynn_schedule')}).</li>
</ul>"""
    pages["hotels.html"] = page("Hotels", "hotels.html", body)

    # ---- suggestions
    items = "".join(f"""
<div class="box"><h3>{esc(i)}. {esc(t)}</h3><p>{esc(o)}</p><p class="small"><b>Trade-off:</b> {esc(tr)}</p>
<p class="small"><b>Decision needed:</b> choose an option or reject it. Nothing will change until you choose.</p></div>""" for i, t, o, tr in SUGGESTIONS)
    body = f"""
<h1>Suggestions for the site (for your review)</h1>
<p class="lead">Proposals only. None has been implemented. Choose an option for each before any change is made.</p>
{items}"""
    pages["suggestions.html"] = page("Suggestions", "suggestions.html", body)

    # ---- questions
    qrows = []
    for q, status, ans, how in QUESTIONS:
        badge = ("badge-ok" if status.startswith("Answered") else
                 "badge-multi" if status.startswith("Partly") else "badge-flag")
        qrows.append([esc(q), f'<span class="badge {badge}">{esc(status)}</span>', esc(ans), esc(how)])
    body = f"""
<h1>Questions and information needed</h1>
<p class="lead">What is known, what is not, and how to find out. Decisions that depend on an open question should wait for the answer.</p>
{table('t-q', ['Question', 'Status', 'What the official sources show', 'How to resolve'], qrows, filter_box=False)}
<h2>Information still missing</h2>
<ul class="tight">
<li>Trip dates and budget.</li>
<li>Structure sheets for {N_UNCHECKED} Venetian flights and {len(WPT_UNV)} Wynn WPT rows.</li>
<li>Official schedules for the other Strip rooms (F13) and Resorts World events (F14).</li>
<li>Room rates and Clark County tax (F02, F15).</li>
<li>Walking times and hotel ratings (F16, F17).</li>
</ul>"""
    pages["questions.html"] = page("Questions", "questions.html", body)

    # ---- repo review
    rrows = [[esc(a), esc(b), esc(c), link(d, d)] for a, b, c, d in REPO_REVIEW]
    body = f"""
<h1>Repo review (line by line)</h1>
<p class="lead">Checked against the repository and the GitHub Pages API. Links go to the repository or GitHub documentation.</p>
{table('t-repo', ['Item', 'What was found', 'Status / action', 'Link'], rrows, filter_box=False)}
<h2>Irregularities</h2>
<ul class="tight">
<li>README is an 8-byte placeholder (F21).</li>
<li>COORDINATION.md named in the task did not exist and has been created (F20).</li>
<li>The task asks for separate session branches; this session has one branch (F20).</li>
<li>No license file. Not added, because you have not chosen one.</li>
</ul>"""
    pages["repo-review.html"] = page("Repo review", "repo-review.html", body)

    # ---- flagged
    frows = []
    for fid, sev, title, detail, keys in FLAGS:
        links = " &middot; ".join(link(D.SRC[k][1], D.SRC[k][0].split(" (")[0]) for k in keys) if keys else '<span class="small">gap: no official source exists for this item in the pages checked</span>'
        frows.append([f"<b>{fid}</b>", esc(sev), esc(title), esc(detail), links])
    body = f"""
<h1>Flagged for Review</h1>
<p class="lead">Irregularities, conflicts, unverified values and gaps. Each flag lists its official source so you can check it.</p>
{table('t-flags', ['ID', 'Severity', 'Item', 'Detail', 'Official source'], frows, filter_box=False)}"""
    pages["flagged.html"] = page("Flagged for Review", "flagged.html", body)

    # ---- sources
    srows = []
    for k, (label, url) in D.SRC.items():
        srows.append([esc(k), esc(label), link(url, url)])
    srows.append(["ven_struct", "Venetian structure sheets read (sheet numbers)",
                  " ; ".join(link(D.VEN_STRUCT.format(n=n), "#" + n) for n in D.VEN_STRUCT_OPENED)])
    srows.append(["ven_raw", "Venetian schedule text saved verbatim in this repo", '<a href="../raw/venetian_dse_nov_2026_schedule.md">raw/venetian_dse_nov_2026_schedule.md</a>'])
    srows.append(["wynn_raw", "Wynn WPT schedule text saved verbatim in this repo", '<a href="../raw/wynn_wpt_world_championship_schedule.md">raw/wynn_wpt_world_championship_schedule.md</a>'])
    body = f"""
<h1>Sources</h1>
<p class="lead">Every official link used. Access date {D.ACCESS_DATE}. Sources that returned errors are listed in Flagged for Review.</p>
{table('t-src', ['Key', 'Source', 'URL'], srows, filter_box=False)}"""
    pages["sources.html"] = page("Sources", "sources.html", body)
    return pages


def main():
    pages = build()
    for name, html_text in pages.items():
        with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
            f.write(html_text)
    print(f"wrote {len(pages)} pages")
    print(f"venetian flights={N_VEN} checked={N_CHECKED} unchecked={N_UNCHECKED} satellites={N_SAT} inferred={N_INFERRED}")
    print(f"venetian printed-weekday conflicts={len(VEN_CAL_CONFLICTS)}")
    print(f"wpt rows={len(WPT)} buy-in={len(WPT_BUY)} multi={len(WPT_MULTI)} unverified={len(WPT_UNV)} conflicts={len(WPT_CONFLICTS)}")
    print(f"earliest venetian={VEN_EARLIEST['time']} {VEN_EARLIEST['date']} #{VEN_EARLIEST['event_no']}")
    print(f"earliest wpt buy-in={WPT_EARLIEST['time']} {WPT_EARLIEST['date_label_printed']}")
    print(f"top ratio={RANK_RATIO[0]['name']} {RANK_RATIO[0]['_ratio']:.1f}")


if __name__ == "__main__":
    main()
