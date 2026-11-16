#!/usr/bin/env python3
"""Generate the published site (site/) from scripts/site_data.py.

Handoff copy (session aa084881). Writes ROOT/data.json and the rendered pages to ROOT/out/ (not committed).
Derived values are labelled in the page text: ratios (guarantee / buy-in), the Venetian
true nightly cost (rate + resort fee, then x (1 + 13.38%) as printed in the official tax
rule), and the schedule order/overlap flags (6-hour planning assumption).
"""
import datetime as dt
import html
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))  # handoff copy: sources live next to this file
import site_data as D  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent
SITE = ROOT / "out"  # rendered pages are NOT committed; regenerate with this script
ASSUMED_DURATION_MIN = 360  # planning assumption only; no official duration is published (F10)
TAX = D.VENETIAN_QUOTE["taxRate"]
TODAY = D.CHECKED


def esc(v):
    return html.escape("" if v is None else str(v), quote=True)


def money(v):
    if v is None:
        return ""
    return f"${v:,.0f}" if float(v).is_integer() else f"${v:,.2f}"


def mins(t):
    t = t.strip().upper()
    if t == "NOT CONFIRMED":
        return None
    clock, ap = t.split()
    h, m = (int(x) for x in clock.split(":")) if ":" in clock else (int(clock), 0)
    h = h % 12 + (12 if ap.startswith("P") else 0)
    return h * 60 + m


def ratio(gtd, buyin):
    if gtd is None or not buyin:
        return None
    return round(gtd / buyin, 1)


def eligibility_for(ev, name):
    """Only eligibility that the official table or sheet prints. Blank otherwise."""
    if "Seniors" in name:
        return "50+ only (per schedule)"
    if ev == "27":
        return "21+ and Venetian Rewards card (sheet 28)"
    return ""


def build_rows():
    rows = []
    for ev, d, wd, tm, name, buy, gtd, sheet, late, fee, pool in D.DSE_MAIN:
        rows.append(dict(id=ev, date=d, weekday=wd, time=tm, name=name, category="main", buyIn=buy, guarantee=gtd,
                         houseFee=fee, prizePool=pool, sheet=sheet, lateReg=late or "",
                         structureUrl=D.SHEET.format(sheet), scheduleUrl=D.DSE_PAGE,
                         note=D.SHEETS_READ.get(sheet, ""), flags=[], lastChecked=TODAY,
                         eligibility=eligibility_for(ev, name)))
    for ev, d, wd, tm, name, buy, gtd, sheet, late, fee, pool, note, flags in D.DSE_BOUNTY:
        rows.append(dict(id=ev, date=d, weekday=wd, time=tm, name=name, category="bounty", buyIn=buy, guarantee=gtd,
                         houseFee=fee, prizePool=pool, sheet=sheet, lateReg=late or "",
                         structureUrl=D.SHEET.format(sheet), scheduleUrl=D.DSE_PAGE, note=note,
                         flags=flags, lastChecked=TODAY, eligibility=eligibility_for(ev, name)))
    for ev, d, wd, tm, name, buy, gtd, sheet, late, fee, pool in D.DSE_UNCLEAR:
        rows.append(dict(id=ev, date=d, weekday=wd, time=tm, name=name, category="unclear", buyIn=buy, guarantee=gtd,
                         houseFee=fee, prizePool=pool, sheet=sheet, lateReg="",
                         structureUrl=D.SHEET.format(sheet), scheduleUrl=D.DSE_PAGE,
                         note=D.SHEETS_READ.get(sheet, ""), flags=["F04"], lastChecked=TODAY, eligibility=""))
    for ev, first, last, times, name, reason, flags in D.DSE_EXCLUDED:
        rows.append(dict(id=ev, date=first, dateTo=last, weekday="", time=times, name=name, category="excluded",
                         buyIn=None, guarantee=None, houseFee=None, prizePool=None, sheet=None, lateReg="",
                         structureUrl="", scheduleUrl=D.DSE_PAGE, note=reason, flags=flags, lastChecked=TODAY,
                         eligibility=eligibility_for(ev, name)))
    for r in rows:
        r.setdefault("dateTo", r["date"])
        r["ratio"] = ratio(r.get("guarantee"), r.get("buyIn"))
    # ranks: main and bounty only, after buy-in and guarantee are both confirmed (F-note on page)
    for cat in ("main", "bounty"):
        ranked = sorted([r for r in rows if r["category"] == cat and r["guarantee"] and r["buyIn"]],
                        key=lambda r: (-r["guarantee"], r["buyIn"], mins(r["time"]) or 0))
        for i, r in enumerate(ranked, 1):
            r["rank"] = i
    return rows


def venetian_nightly():
    q = D.VENETIAN_QUOTE
    out = []
    for d, rate in q["nights"]:
        base = rate + q["resortFeePerNight"]
        true = round(base * (1 + TAX), 2)
        out.append(dict(date=d, rate=rate, resortFee=q["resortFeePerNight"], tax=round(base * TAX, 2), trueNightly=true))
    total_true = round(sum(n["trueNightly"] for n in out), 2)
    avg = round(q["checkoutTotal"] / len(q["nights"]), 2)
    return out, total_true, avg


def hotel_rows():
    nights, sum_true, avg = venetian_nightly()
    q = D.VENETIAN_QUOTE
    return [
        dict(id="H-VEN", property="The Venetian Resort", room=q["property"], pokerRoom="The Venetian (DeepStack IV host)",
             quoteDate=q["checked"], sample="Nov 17-19, 2026 (2 nights, 2 adults)", nights=nights,
             checkoutTotal=q["checkoutTotal"], taxPrinted=q["taxPrinted"], trueNightly=avg,
             trueNightlyBasis="Derived: official checkout total / 2 nights. Rate + $55 resort fee, tax 13.38%.",
             resortFee="$55 per night, plus tax (official terms)", parking="$20/day for registered guests (official terms); non-hotel parking $20 Mon-Thu, $25 Fri-Sun; valet $40/day",
             cancelDeadline="", rateTimestamp=f"{TODAY} (retrieved; time of day not shown)",
             walkingMinutes="", sources=[q["source"], D.VEN_FEE, D.VEN_TERMS], flags=["F12", "F17", "F18"],
             status="Only dated official total in this site. Calendar cells (F12) and suite rates (F16) are not used."),
        dict(id="H-PAL", property="The Palazzo", room="", pokerRoom="The Venetian (DeepStack IV host)", quoteDate="",
             sample="No Palazzo quote captured", nights=[], checkoutTotal=None, taxPrinted=None, trueNightly=None,
             trueNightlyBasis="", resortFee="", parking="", cancelDeadline="", rateTimestamp="", walkingMinutes="",
             sources=[D.VEN_SUITE], flags=["F16", "F18"], status="Suite page lists 'as low as $119 and $209' for The Venetian or The Palazzo; not mapped to a property."),
        dict(id="H-WYN", property="Wynn Las Vegas", room="", pokerRoom="Wynn Poker Room (WPT in Encore, per Wynn WPT terms)",
             quoteDate="", sample="None captured", nights=[], checkoutTotal=None, taxPrinted=None, trueNightly=None,
             trueNightlyBasis="", resortFee="", parking="", cancelDeadline="", rateTimestamp="", walkingMinutes="",
             sources=[D.WYNN_TERMS, D.WYNN_POKER], flags=["F24", "F18"], status="Only an expired offer's terms are on record (F24). No current rate or fee."),
        dict(id="H-BEL", property="Bellagio", room="", pokerRoom="Bellagio Poker Room (on property)", quoteDate="",
             sample="None captured", nights=[], checkoutTotal=None, taxPrinted=None, trueNightly=None,
             trueNightlyBasis="", resortFee="", parking="", cancelDeadline="", rateTimestamp="", walkingMinutes="",
             sources=[D.BEL_POKER], flags=["F31", "F18"], status="No official rate or resort fee retrieved."),
        dict(id="H-ARIA", property="ARIA Resort & Casino", room="", pokerRoom="ARIA poker room (on property)", quoteDate="",
             sample="None captured", nights=[], checkoutTotal=None, taxPrinted=None, trueNightly=None,
             trueNightlyBasis="", resortFee="", parking="", cancelDeadline="", rateTimestamp="", walkingMinutes="",
             sources=[D.ARIA_POKER], flags=["F29", "F18"], status="Page offers 'exclusive room rates' by phone or email; no value printed."),
    ], sum_true, avg


def schedule(rows):
    single = [r for r in rows if r["category"] in ("main", "bounty")]
    days = []
    start = dt.date(2026, 11, 16)
    for i in range(38):
        d = (start + dt.timedelta(days=i)).isoformat()
        day = sorted([r for r in single if r["date"] == d], key=lambda r: mins(r["time"]))
        ordered = sorted(day, key=lambda r: (-(r["guarantee"] or -1), mins(r["time"])))
        primary = ordered[0] if ordered else None
        fallback = ordered[1] if len(ordered) > 1 else None
        overlaps = []
        for a, b in zip(day, day[1:]):
            if mins(b["time"]) - mins(a["time"]) < ASSUMED_DURATION_MIN:
                overlaps.append(f"#{a['id']} {a['time']} and #{b['id']} {b['time']} start {mins(b['time'])-mins(a['time'])} min apart (< 6 h planning assumption)")
        days.append(dict(date=d, weekday=dt.date.fromisoformat(d).strftime("%A"), events=[r["id"] for r in day],
                         primary=primary["id"] if primary else None, fallback=fallback["id"] if fallback else None,
                         overlaps=overlaps))
    return days


def links(urls, label=None):
    out = []
    for i, u in enumerate(urls):
        if u:
            out.append(f'<a href="{esc(u)}" rel="noopener">{esc(label or "Official source")} {i+1 if len(urls)>1 else ""}</a>'.replace(" >", ">").replace("  ", " ").strip())
    return " · ".join(out)


def tag_flags(ids):
    return " ".join(f'<a class="tag" href="{{P}}flagged.html#{esc(f)}">{esc(f)}</a>' for f in ids)


def th(cols):
    return "<thead><tr>" + "".join(f"<th>{esc(c)}</th>" for c in cols) + "</tr></thead>"


def tbl(tid, cols, body_rows, empty="No rows."):
    if not body_rows:
        return f'<p class="empty">{esc(empty)}</p>'
    return (f'<div class="tablewrap"><table id="{tid}" class="searchable">{th(cols)}<tbody>'
            + "".join(body_rows) + "</tbody></table></div>")


def toolbar(tid, date_field=True, main_only=None):
    parts = [f'<div class="toolbar"><label>Search <input type="search" data-search="{tid}" placeholder="Search table"></label>']
    if date_field:
        parts.append(f'<label>Date <input type="date" data-date="{tid}" min="2026-11-16" max="2026-12-23"></label>')
    if main_only:
        parts.append(f'<label class="toggle"><input type="checkbox" data-mainonly="{tid}"> Single-entry main list only</label>')
    parts.append("</div>")
    return "".join(parts)


def row_main(r, P):
    gtd = money(r["guarantee"]) if r["guarantee"] else ""
    rk = r.get("rank", "")
    flagsh = tag_flags(r["flags"])
    src = links([r["scheduleUrl"], r["structureUrl"]]).replace("Official source 1", "Schedule").replace("Official source 2", "Structure sheet")
    return (f'<tr data-cat="{esc(r["category"])}" data-date="{esc(r["date"])}">'
            f'<td>{esc(rk)}</td><td>{esc(r["date"])}<br><small>{esc(r["weekday"])} · {esc(r["time"])}</small></td>'
            f'<td>{esc(r["id"])}</td><td>{esc(r["name"])}{("<br><small>"+esc(r["note"])+"</small>") if r["note"] else ""}</td>'
            f'<td>{money(r["buyIn"])}</td><td>{gtd}</td><td>{esc(r["ratio"] if r["ratio"] is not None else "")}</td>'
            f'<td>{money(r["houseFee"]) if r["houseFee"] is not None else ""}</td><td>{money(r["prizePool"]) if r["prizePool"] is not None else ""}</td>'
            f'<td>{esc(r["lateReg"])}</td><td>{esc(r["eligibility"])}</td><td>{src}</td>'
            f'<td>{esc(r["lastChecked"])}</td><td>{flagsh}</td></tr>').replace("{P}", P)


def page(title, body, P, active, extra_head=""):
    nav = [("index.html", "Home"), ("tournaments.html", "Tournaments"), ("excluded.html", "Excluded"),
           ("schedule.html", "Schedule"), ("trip.html", "Trip calculator"), ("hotels.html", "Hotels"),
           ("venues.html", "Venues"), ("flagged.html", "Flagged for Review"), ("questions.html", "Questions"),
           ("suggestions.html", "Suggestions"), ("monitor.html", "Source monitor")]
    navh = "".join(f'<a href="{P}{h}"{" class=active" if h == active else ""}>{esc(t)}</a>' for h, t in nav)
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)} · Las Vegas Strip poker trip</title>
<link rel="stylesheet" href="{P}assets/site.css">{extra_head}</head>
<body>
<header class="top"><a class="brand" href="{P}index.html">Las Vegas Strip poker trip</a>
<nav aria-label="Main">{navh}</nav></header>
<main>
<h1>{esc(title)}</h1>
{body}
</main>
<footer>Data checked {TODAY} (Las Vegas). Every row links an official source. Blank = not verified; not filled in. Calculations are labelled. Unverified items: <a href="{P}flagged.html">Flagged for Review</a>.</footer>
<script src="{P}assets/app.js" defer></script>
</body></html>
"""


def pages(rows, hotels, sum_true, avg, days):
    P = ""
    out = {}
    main = sorted([r for r in rows if r["category"] == "main"], key=lambda r: (r.get("rank", 999), r["date"]))
    bounty = sorted([r for r in rows if r["category"] == "bounty"], key=lambda r: (r.get("rank", 999), r["date"]))
    unclear = [r for r in rows if r["category"] == "unclear"]
    excluded = [r for r in rows if r["category"] == "excluded"]
    nomain = len(main)
    # ---- index ----
    cards = [("tournaments.html", "Tournaments", f"{nomain} main-list rows (no re-entry/add-on wording on sheet) and {len(bounty)} bounty rows."),
             ("excluded.html", "Excluded", f"{len(excluded)} flight, restart, satellite and team rows, plus Wynn WPT and Bellagio entries kept out."),
             ("schedule.html", "Schedule", "Day-by-day schedule with primary and fallback events, and overlap flags. Earliest verified start is 10:10 AM."),
             ("trip.html", "Trip calculator", "Entries x buy-in, plus nights x true nightly hotel cost (only the dated Venetian quote is used)."),
             ("hotels.html", "Hotels", "Checkout totals, resort fee, tax, parking and rate timestamps. Blank where not verified."),
             ("venues.html", "Venues", "Official pages for each Strip room, and what could not be verified."),
             ("flagged.html", "Flagged for Review", f"{len(D.FLAGS)} irregularities and open items, each with its source."),
             ("questions.html", "Questions", "Missing information and who to ask."),
             ("suggestions.html", "Suggestions", "Options for review before any change is made."),
             ("poker3/", "Companion dashboard", "Earlier companion dashboard from session 779af4ba. Not edited in this session."),
             ("monitor.html", "Source monitor", "Change checks on the official URLs used here. First live baseline is pending (see page).")]
    cardh = "".join(f'<a class="card" href="{h}"><b>{esc(t)}</b><span>{esc(d)}</span></a>' for h, t, d in cards)
    summary = """<section class="summary"><h2>Executive summary</h2><ul>
<li><b>Only one dated hotel total is verified:</b> The Venetian, Nov 17-19, 2026 (2 adults): $1,245.48 checkout total including $110 resort fees and $146.98 tax (official quote). Per night, true cost averages $622.74 (derived). The booking calendar disagrees with the quote (F12). No other hotel has a verified rate.</li>
<li><b>The DeepStack Extravaganza IV (Venetian, Nov 16-Dec 23)</b> is the only Strip series with a full official table in this session. It has 12 single-start freezeout rows, 32 single-start bounty rows, 3 unclear-format RaceDay rows, and 17 flight, restart, two-day, satellite, or team rows kept out.</li>
<li><b>Single-entry is not printed anywhere.</b> Main-list rows say 'no re-entry or add-on wording on sheet'. This is flagged as F01 and needs written confirmation.</li>
<li><b>Ranking</b> uses the printed guarantee after confirming the total buy-in. The ratio (guarantee / buy-in) is descriptive only, not a forecast. One main-list event (#6) prints no guarantee and is not ranked.</li>
<li><b>Wynn WPT (Nov 27-Dec 21) and Bellagio</b> have official schedules, but formats and rules were not fully read. Bellagio Friday allows re-entry and Saturday is multi-flight, so both are excluded. Wynn's Friday daily is a rebuy.</li>
<li><b>Not verified:</b> walking times, the 8:00 AM all-day plan (earliest verified start is 10:10 AM), finish times, cancellation deadlines, and current Wynn or Bellagio fees. Each is blank and flagged.</li>
</ul></section>"""
    out["index.html"] = page("Las Vegas Strip poker trip", summary + f'<section class="cards">{cardh}</section>', P, "index.html")

    # ---- tournaments ----
    main_cols = ["Rank", "Date / time", "Event", "Name (as printed)", "Buy-in (total)", "Guaranteed", "GTD ÷ buy-in (descriptive)", "House fee (sheet)", "Pool (sheet)", "Late-reg", "Eligibility", "Official source", "Last checked", "Flags"]
    tb = toolbar("t-main", main_only=True) + "<div class='sec' data-sec='main'><h2>Main list: single-start 1-day events</h2><p class='note'>Freezeout formats. No re-entry, rebuy or add-on wording on the structure sheet read. Single-entry is not printed (F01). Ranked by guarantee after buy-in is confirmed.</p>"
    tb += tbl("t-main", main_cols, [row_main(r, P) for r in main], "No main rows.") + "</div>"
    tb += "<div class='sec' data-sec='bounty'><h2>Bounty and knockout events (separate)</h2><p class='note'>Bounty and PKO events are labelled separately and are ranked only within this section.</p>"
    tb += toolbar("t-bounty")
    tb += tbl("t-bounty", main_cols, [row_main(r, P) for r in bounty]) + "</div>"
    tb += "<div class='sec' data-sec='unclear'><h2>Format unclear (not ranked)</h2>" + toolbar("t-unclear") + tbl("t-unclear", main_cols, [row_main(r, P) for r in unclear]) + "</div>"
    out["tournaments.html"] = page("Single-entry tournaments", tb, P, "tournaments.html")

    # ---- excluded ----
    ex_cols = ["Event", "Dates (first - last)", "Times printed", "Name", "Why excluded", "Official source", "Last checked", "Flags"]
    body = "<p class='note'>Kept out of the main list and schedule. Each row links the official table.</p>"
    body += "<h2>Flights, restarts, two-day, satellites and team rows (Venetian)</h2>"
    body += toolbar("t-excl")
    ex_rows = []
    for r in excluded:
        ex_rows.append(f'<tr data-cat="excluded" data-date="{esc(r["date"])}"><td>{esc(r["id"])}</td><td>{esc(r["date"])} to {esc(r["dateTo"])}</td>'
                       f'<td>{esc(r["time"])}</td><td>{esc(r["name"])}</td><td>{esc(r["note"])}</td>'
                       f'<td><a href="{esc(r["scheduleUrl"])}">Schedule</a></td><td>{esc(r["lastChecked"])}</td><td>{tag_flags(r["flags"]).replace("{P}", P)}</td></tr>')
    body += tbl("t-excl", ex_cols, ex_rows)
    body += "<h2>Advantage, rebuy, re-entry and buy-in conflicts</h2><p class='note'>Shown here as separate sections, per the scope rule.</p>"
    bel_rows = []
    for day, tm, p_buy, pdf_buy, gtd, status, src, flags in D.BELLAGIO:
        bel_rows.append(f'<tr data-cat="excluded"><td>Bellagio {esc(day)}</td><td>{esc(tm)}</td><td>{money(p_buy)} (page)</td><td>{money(pdf_buy) if pdf_buy else "blank"}</td>'
                        f'<td>{esc(status)}</td><td><a href="{esc(src)}">Official PDF</a></td><td>{esc(TODAY)}</td><td>{tag_flags(flags).replace("{P}", P)}</td></tr>')
    body += "<h3>Bellagio weekly events</h3>" + tbl("t-bel", ["Event", "Time", "Buy-in (page)", "Buy-in (PDF)", "Status", "Official source", "Last checked", "Flags"], bel_rows)
    dl = []
    for day, tm, label, buy, gtd, note, src in D.WYNN_DAILY:
        dl.append(f'<tr data-cat="excluded"><td>Wynn {esc(day)}</td><td>{esc(tm)}</td><td>{esc(label)} ({money(buy)})</td><td>{money(gtd)}</td><td>{esc(note)}</td><td><a href="{esc(src)}">Official poster</a></td><td>{esc(TODAY)}</td><td>{tag_flags(["F28"]).replace("{P}", P)}</td></tr>')
    body += "<h3>Wynn daily tournaments (poster)</h3>" + tbl("t-wdaily", ["Day", "Time", "Event (buy-in)", "Guarantee", "Status", "Official source", "Last checked", "Flags"], dl)
    wl = []
    for win, ev, buy, gtd, note, src in D.WYNN_WPT:
        wl.append(f'<tr data-cat="excluded"><td>{esc(win)}</td><td>{esc(ev)}</td><td>{money(buy)}</td><td>{money(gtd) if gtd else ""}</td><td>{esc(note)}</td><td><a href="{esc(src)}">Official schedule</a></td><td>{esc(TODAY)}</td><td>{tag_flags(["F25"]).replace("{P}", P)}</td></tr>')
    body += "<h3>Wynn WPT World Championship (formats not verified)</h3>" + tbl("t-wpt", ["Window", "Event", "Buy-in", "Guarantee", "Status", "Official source", "Last checked", "Flags"], wl)
    out["excluded.html"] = page("Excluded and unverified events", body, P, "excluded.html")

    # ---- schedule ----
    sched_rows = []
    byid = {r["id"] + r["category"]: r for r in rows}
    for d in days:
        evs = [r for r in rows if r["date"] == d["date"] and r["category"] in ("main", "bounty")]
        evs.sort(key=lambda r: mins(r["time"]))
        listing = "<br>".join(f'#{esc(r["id"])} {esc(r["time"])} · {esc(r["name"][:70])}' for r in evs) or "No verified single-start event."
        prim = next((r for r in rows if r["id"] == str(d["primary"]) and r["date"] == d["date"] and r["category"] in ("main", "bounty")), None) if d["primary"] else None
        fb = next((r for r in rows if r["id"] == str(d["fallback"]) and r["date"] == d["date"] and r["category"] in ("main", "bounty")), None) if d["fallback"] else None
        ptxt = f'#{esc(prim["id"])} {esc(prim["time"])} ({money(prim["guarantee"]) if prim["guarantee"] else "GTD not printed"})' if prim else "None"
        ftxt = f'#{esc(fb["id"])} {esc(fb["time"])} ({money(fb["guarantee"]) if fb["guarantee"] else "GTD not printed"})' if fb else "None verified"
        ov = "<br>".join(esc(x) for x in d["overlaps"]) or ""
        sched_rows.append(f'<tr data-cat="schedule" data-date="{esc(d["date"])}"><td>{esc(d["date"])}<br><small>{esc(d["weekday"])}</small></td>'
                          f'<td>{listing}</td><td>{ptxt}</td><td>{ftxt}</td><td>{ov}</td>'
                          f'<td><a href="{esc(D.DSE_PAGE)}">Venetian schedule</a></td></tr>')
    sb = ("<p class='note'><b>8:00-10:00 AM: no verified tournament start.</b> The earliest official start is 10:10 AM. "
          "Primary = largest printed guarantee that day (planning rule, not a forecast). Fallback = next largest. "
          "Overlap = two starts less than 6 hours apart (planning assumption, F10). Late-registration cutoffs are printed only for 9:40 PM events (F09). "
          "Days with only flights or RaceDay show no primary (see Excluded).</p>")
    sb += toolbar("t-sched")
    sb += tbl("t-sched", ["Date", "Single-start events (time order)", "Primary", "Fallback", "Overlap flags", "Official source"], sched_rows)
    out["schedule.html"] = page("Daily schedule (Nov 16 to Dec 23, 2026)", sb, P, "schedule.html")

    # ---- trip calculator ----
    calc_rows = []
    for r in main + bounty:
        calc_rows.append(f'<tr data-cat="calc"><td>{esc(r["id"])}</td><td>{esc(r["date"])}</td><td>{esc(r["name"][:80])}</td>'
                         f'<td class="num" data-buyin="{r["buyIn"]}">{money(r["buyIn"])}</td>'
                         f'<td><input type="number" min="0" step="1" data-entries value="" aria-label="Entries for #{esc(r["id"])}"></td>'
                         f'<td><a href="{esc(r["scheduleUrl"])}">Schedule</a></td></tr>')
    cb = ("<p class='note'>Enter your own counts. Nothing is prefilled. Entry cost = entries × printed total buy-in. "
          "Hotel cost = nights × true nightly cost. The only dated hotel total on this site is the Venetian Nov 17-19 quote; "
          "its average is derived as (rate + $55 resort fee) × (1 + 13.38%) per night (F12, F16).</p>")
    cb += ('<section class="calc"><label>Nights <input type="number" min="0" step="1" id="nights" value=""></label>'
           f'<label>Hotel: <select id="hotel"><option value="">Choose a hotel</option><option value="{avg}">The Venetian, Nov 17-19 quote (derived average {money(avg)} per night)</option>'
           '<option value="custom">Enter a verified value</option></select></label>'
           '<label>Nightly true cost (custom, verified only) <input type="number" min="0" step="0.01" id="custom-night" value=""></label>'
           '<output id="calc-out" aria-live="polite">Enter values to compute.</output></section>')
    cb += toolbar("t-calc", date_field=False)
    cb += tbl("t-calc", ["Event", "Date", "Name", "Total buy-in", "Entries", "Official source"], calc_rows)
    out["trip.html"] = page("Trip cost calculator", cb, P, "trip.html")

    # ---- hotels ----
    hcols = ["Property", "Poker room", "Sample (dated)", "Checkout total", "Tax (official)", "True nightly", "Resort fee", "Parking", "Cancel by", "Rate timestamp", "Walk (min)", "Official source", "Flags"]
    hb = "<p class='note'>Only the Venetian has a dated official total. True nightly = (rate + resort fee) × 1.1338, derived from the official quote. Blank = not verified.</p>"
    hrows = []
    for h in hotels:
        srcs = " · ".join(f'<a href="{esc(u)}">Source {i+1}</a>' for i, u in enumerate(h["sources"]))
        hrows.append(f'<tr data-cat="hotel"><td>{esc(h["property"])}<br><small>{esc(h["room"])}</small></td><td>{esc(h["pokerRoom"])}</td>'
                     f'<td>{esc(h["sample"])}</td><td>{money(h["checkoutTotal"]) if h["checkoutTotal"] else ""}</td>'
                     f'<td>{money(h["taxPrinted"]) if h["taxPrinted"] else ""}</td><td>{money(h["trueNightly"]) if h["trueNightly"] else ""}</td>'
                     f'<td>{esc(h["resortFee"])}</td><td>{esc(h["parking"])}</td><td>{esc(h["cancelDeadline"])}</td>'
                     f'<td>{esc(h["rateTimestamp"])}</td><td>{esc(h["walkingMinutes"])}</td><td>{srcs}</td><td>{tag_flags(h["flags"]).replace("{P}", P)}</td></tr>')
    hb += tbl("t-hotels", hcols, hrows)
    hb += ("<h2>Venetian nightly breakdown (derived from the official quote)</h2>"
           "<div class='tablewrap'><table id='t-nights' class='searchable'>" + th(["Night", "Quoted rate", "Resort fee", "Tax (13.38%)", "True nightly", "Note", "Official source"]) + "<tbody>"
           + "".join(f"<tr data-cat='night'><td>{esc(n['date'])}</td><td>{money(n['rate'])}</td><td>{money(n['resortFee'])}</td><td>{money(n['tax'])}</td><td>{money(n['trueNightly'])}</td><td>Derived; rounding ±$0.01 vs the printed total</td><td><a href='{esc(D.VEN_QUOTE)}'>Official quote</a></td></tr>" for n in hotels[0]["nights"])
           + f"</tbody></table></div><p class='note'>Sum of derived true nightly = {money(sum_true)}; official checkout total = {money(D.VENETIAN_QUOTE['checkoutTotal'])} (rounding difference shown in the Flags).</p>")
    hb += "<h2>Dated booking-calendar log (not quotes; F17)</h2>" + toolbar("t-rates")
    rl = []
    for d, price, basis, src in D.RATE_LOG:
        rl.append(f'<tr data-cat="rate" data-date="{esc(d)}"><td>{esc(d)}</td><td>{money(price) if price else "no price shown"}</td><td>{esc(basis)}</td><td>{esc(TODAY)}</td><td><a href="{esc(src)}">Booking calendar</a></td><td>{tag_flags(["F12","F17"]).replace("{P}", P)}</td></tr>')
    hb += tbl("t-rates", ["Date", "Calendar cell", "Basis", "Last checked", "Official source", "Flags"], rl)
    out["hotels.html"] = page("Hotels and true nightly cost", hb, P, "hotels.html")

    # ---- venues index + subpages ----
    vrows = [
        ("venues/venetian.html", "The Venetian", "DeepStack Extravaganza IV host. Official table read in full.", D.DSE_PAGE),
        ("venues/wynn.html", "Wynn Las Vegas", "WPT World Championship (Nov 27-Dec 21), daily poster. Formats not reviewed.", D.WYNN_POKER),
        ("venues/bellagio.html", "Bellagio", "Friday $600, Saturday, Sunday H.O.R.S.E. Mostly excluded.", D.BEL_POKER),
        ("venues/aria.html", "ARIA", "Poker page offers rate contacts. No schedule printed.", D.ARIA_POKER),
    ]
    vb = "<p class='note'>Strip rooms with an official source are below. Caesars, MGM Grand, Golden Nugget, Resorts World and Circa did not yield a verified schedule (F30).</p>"
    vb += "<div class='cards'>" + "".join(f'<a class="card" href="{h}"><b>{esc(t)}</b><span>{esc(d)}</span><small>Official: {esc(u)}</small></a>' for h, t, d, u in vrows) + "</div>"
    out["venues.html"] = page("Venues", vb, P, "venues.html")
    v_ven = (f"<p>Official table: <a href='{esc(D.DSE_PAGE)}'>DeepStack Extravaganza IV</a> (Nov 16 - Dec 23, 2026). "
             f"Series overview: <a href='{esc(D.DSE_SERIES)}'>series page</a>. Suite rates: <a href='{esc(D.VEN_SUITE)}'>poker suite page</a> (F16). "
             f"Resort fee <a href='{esc(D.VEN_FEE)}'>$55 + tax per night</a>; terms <a href='{esc(D.VEN_TERMS)}'>hotel terms</a>.</p>"
             "<h2>Events</h2><p>See <a href='../tournaments.html'>Tournaments</a>, <a href='../schedule.html'>Schedule</a> and <a href='../excluded.html'>Excluded</a>.</p>"
             "<h2>Not verified</h2><p>Walking time to the poker room (same property, minutes not published, F18). Finish times (F10). Cancellation rule (F18).</p>")
    out["venues/venetian.html"] = page("The Venetian", v_ven, "../", "venues.html")
    wpt_rows = "".join(f'<tr><td>{esc(a)}</td><td>{esc(b)}</td><td>{money(c)}</td><td>{money(d) if d else ""}</td><td>{esc(e)}</td><td><a href="{esc(f)}">Official</a></td></tr>' for a, b, c, d, e, f in D.WYNN_WPT)
    v_wyn = (f"<p>Official: <a href='{esc(D.WYNN_POKER)}'>Wynn poker room</a>. WPT World Championship (Nov 27 - Dec 21, 2026). Daily poster and rules below.</p>"
             "<h2>WPT World Championship (windows as printed)</h2>"
             "<div class='tablewrap'><table><thead><tr><th>Window</th><th>Event</th><th>Buy-in</th><th>Guarantee</th><th>Note</th><th>Source</th></tr></thead><tbody>" + wpt_rows + "</tbody></table></div>"
             f"<p>Structures (chunk 0 read): <a href='{esc(D.WYNN_STRUCT)}'>WPT structures PDF</a>. Dec 18 weekday conflict (F26). WPT PLO sum conflict (F27). Terms page 850070 covers an expired offer (F24).</p>"
             "<h2>Daily poster</h2><p>Recurring; rebuy on Friday (F28). <a href='" + esc(D.WYNN_DAILY_STRUCT) + "'>Daily structures PDF</a>.</p>")
    out["venues/wynn.html"] = page("Wynn Las Vegas", v_wyn, "../", "venues.html")
    v_bel = ("<p>Official: <a href='" + esc(D.BEL_POKER) + "'>Bellagio poker page</a>. Host: 702.693.7291. Call-ahead waitlist.</p>"
             "<table><thead><tr><th>Day</th><th>Time</th><th>Buy-in (page)</th><th>Buy-in (PDF)</th><th>Status</th><th>Source</th></tr></thead><tbody>"
             + "".join(f'<tr><td>{esc(d)}</td><td>{esc(t)}</td><td>{money(p)}</td><td>{money(q) if q else "blank"}</td><td>{esc(s)}</td><td><a href="{esc(src)}">PDF</a></td></tr>' for d, t, p, q, g, s, src, f in D.BELLAGIO)
             + "</tbody></table><p>Flags: F19 (Saturday buy-in conflict), F20 (Friday re-entry), F21, F22, F23 (stale 'July 26' notice), F31 (fee claim).</p>")
    out["venues/bellagio.html"] = page("Bellagio", v_bel, "../", "venues.html")
    v_aria = (f"<p>Official: <a href='{esc(D.ARIA_POKER)}'>ARIA poker page</a>. The page offers exclusive poker-player room rates by phone (702.590.7232) and email (PokerRoomRates@aria.com). "
              "No schedule, no buy-in and no rate is printed. Nothing is listed (F29). Call to confirm whether daily tournaments run as scheduled.</p>")
    out["venues/aria.html"] = page("ARIA", v_aria, "../", "venues.html")

    # ---- flagged ----
    fl = []
    for fid, (sev, title, detail, srcs) in D.FLAGS.items():
        sl = " · ".join(f'<a href="{esc(u)}">Source {i+1}</a>' for i, u in enumerate(srcs)) or "No official source (not verifiable)"
        fl.append(f'<tr id="{esc(fid)}"><td>{esc(fid)}</td><td>{esc(sev)}</td><td>{esc(title)}</td><td>{esc(detail)}</td><td>{sl}</td></tr>')
    fb = ("<p class='note'>Every irregularity and open item. Blank values on other pages are blank because of these flags. "
          "Nothing here is filled in by inference.</p>") + toolbar("t-flags", date_field=False) + tbl("t-flags", ["ID", "Severity", "Issue", "Detail", "Official source"], fl)
    out["flagged.html"] = page("Flagged for Review", fb, P, "flagged.html")

    # ---- questions ----
    qs = [
        ("Can the Venetian poker room confirm in writing which DeepStack events are single-entry (no re-entry, no add-on)?", "Venetian poker room. Until then the main list says only that no re-entry or add-on wording is on the sheet (F01)."),
        ("What is the cancellation deadline on the Venetian Nov 17-19 quote?", "Venetian reservations. Not on the captured page (F18)."),
        ("Which Venetian nightly rate is correct for Nov 17 and 18: the quote ($824.25 / $164.25) or the calendar ($605 / $165)?", "Venetian booking. Quote used; calendar logged (F12)."),
        ("What is the current Wynn resort fee and cancellation rule for a stay in Dec 2026?", "Wynn reservations. Only an expired offer is on record (F24)."),
        ("What are the Wynn WPT format and re-entry rules for each row?", "Wynn poker room. Structures chunk 0 only (F25)."),
        ("Which Bellagio Saturday buy-in is correct: $1,000, $1,100 or $600?", "Bellagio poker host 702.693.7291 (F19)."),
        ("What are walking times from each hotel to each poker room?", "No official source. Not published by the properties checked (F18)."),
        ("What is the finish time and typical duration of each event?", "Venue poker room. Not published (F10)."),
        ("Do any Strip rooms other than Venetian, Wynn and Bellagio run a verified daily schedule?", "Caesars, MGM Grand, Golden Nugget, Resorts World and Circa did not yield one (F30)."),
        ("Is the PokerAtlas PRO discount a rake discount or a $20 cut to the first buy-in?", "Venetian poker room (F06, F13)."),
    ]
    qb = "<ol class='qa'>" + "".join(f"<li><p><b>{esc(q)}</b></p><p>{esc(a)}</p></li>" for q, a in qs) + "</ol>"
    out["questions.html"] = page("Questions: missing information", qb, P, "questions.html")

    # ---- suggestions ----
    sg = [
        "Add a Wynn stay-terms page check once a current offer is published, so Wynn fee and cancellation rows can be filled.",
        "Read the Bellagio Sunday H.O.R.S.E. structure and the remaining Wynn WPT structure chunks (1-7) before listing any WPT row as main.",
        "Extend the daily monitor (scripts/check_sources.py) to this site's official URL list (site/data/sources.json). This is a cross-session request in COORDINATION.md; not done here.",
        "Add a day-by-day walking-time table only after an official source publishes walking times or a route is supplied by the user.",
        "Add the other Strip room pages (Caesars, MGM Grand, Golden Nugget, Resorts World, Circa) only if an official schedule URL becomes available.",
    ]
    sb2 = "<p class='note'>For user review. None of these is implemented; each needs a decision first.</p><ul>" + "".join(f"<li>{esc(s)}</li>" for s in sg) + "</ul>"
    out["suggestions.html"] = page("Suggestions for review", sb2, P, "suggestions.html")

    # ---- monitor ----
    mrows = "".join(f'<tr><td>{esc(n)}</td><td><a href="{esc(u)}">{esc(u)}</a></td><td>{esc(TODAY)}</td></tr>' for _, n, u in D.MONITOR_SOURCES)
    mb = ("<p class='note'><b>Status: first live baseline not yet run.</b> The sandbox cannot reach venue sites, so no result is shown here. "
          "The existing daily monitor (scripts/check_sources.py, workflow source-monitor.yml) checks only site/poker3/data/research.json on main. "
          "Pointing it at site/data/sources.json needs a cross-session change to that workflow (logged in COORDINATION.md). Until then, results are not claimed.</p>"
          "<h2>Official URLs listed for re-check</h2><div class='tablewrap'><table><thead><tr><th>Source</th><th>URL</th><th>Last checked</th></tr></thead><tbody>" + mrows + "</tbody></table></div>")
    out["monitor.html"] = page("Source monitor", mb, P, "monitor.html")
    return out


def main():
    rows = build_rows()
    hotels, sum_true, avg = hotel_rows()
    days = schedule(rows)
    pages_out = pages(rows, hotels, sum_true, avg, days)
    data = dict(asOf=TODAY, tournaments=[dict(r) for r in rows], hotels=hotels,
                venetianNights=venetian_nightly()[0], rateLog=[dict(date=d, cell=p, basis=b, source=s, lastChecked=TODAY) for d, p, b, s in D.RATE_LOG],
                wynnWpt=[dict(window=a, event=b, buyIn=c, guarantee=d, note=e, source=f) for a, b, c, d, e, f in D.WYNN_WPT],
                wynnDaily=[dict(day=a, time=b, event=c, buyIn=d, guarantee=e, note=f, source=g) for a, b, c, d, e, f, g in D.WYNN_DAILY],
                bellagio=[dict(day=a, time=b, buyInPage=c, buyInPdf=d, status=f, source=g, flags=h) for a, b, c, d, e, f, g, h in D.BELLAGIO],
                schedule=days, flags={k: dict(severity=v[0], title=v[1], detail=v[2], sources=v[3]) for k, v in D.FLAGS.items()},
                sources=[dict(id=i, name=n, url=u, kind="official") for i, n, u in D.MONITOR_SOURCES])
    SITE.mkdir(parents=True, exist_ok=True)
    (ROOT / "data.json").write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (SITE / "sources.json").write_text(json.dumps({"note": "Official URLs for scripts/check_sources.py (kind=official).", "sources": data["sources"]}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (SITE / "venues").mkdir(parents=True, exist_ok=True)
    for rel, text in pages_out.items():
        (SITE / rel).write_text(text, encoding="utf-8")
    print(f"wrote {len(pages_out)} pages, {len(rows)} event rows, {len(D.FLAGS)} flags")


if __name__ == "__main__":
    main()
