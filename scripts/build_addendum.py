#!/usr/bin/env python3
"""Build site/sheets.html — the structure-sheet verification addendum.

Self-contained page (inline styles) so it never depends on, or overwrites, the
canonical site pages owned by the integration session. Renders:
  1. all 37 Venetian DSE IV structure sheets (fee split, stack, levels, late-reg,
     pays %, bounty, entry-clause verdict) with per-sheet official links
  2. entry-rule excerpts verified this session (Wynn dailies, WPT, Bellagio)
  3. fee-split anomalies and flags with source links
  4. verified hotel policies and the poker-suite qualification rule
  5. hotel–venue official addresses + Google Maps walking links (30-min filter)
Input: data/sheet_extracts.jsonl + site/data/*.json (built by scripts/build_data.py).
"""
import json, os, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "site", "data")

def esc(x):
    return html.escape(str(x if x is not None else ""))

def load(name):
    with open(os.path.join(DATA, name)) as f:
        return json.load(f)

def sheet_url(n):
    return ("https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/"
            f"dse_nov_2026-structure_{n}.pdf")

sheets = []
with open(os.path.join(ROOT, "data", "sheet_extracts.jsonl")) as f:
    for line in f:
        line = line.strip()
        if line:
            sheets.append(json.loads(line))
sheets.sort(key=lambda s: s["sheet"])

T = load("tournaments.json")["tournaments"]
FLAGS = load("flags.json")["flags"]
HOTELS = load("hotels.json")["hotels"]
ROUTES = load("routes.json")["routes"]

def money(x):
    return ("$" + f"{float(x):,.0f}") if x not in (None, "") else '<span class="u">blank</span>'

# ---- 1. sheet matrix
srows = []
for s in sheets:
    ev = ", ".join("#" + str(e) for e in s["events"])
    fee = " / ".join(x for x in [
        (money(s["houseFee"]) + " house") if s.get("houseFee") is not None else "",
        (money(s["prizeShare"]) + " prize") if s.get("prizeShare") is not None else "",
    ] if x)
    entry = {"none": "no re-entry/rebuy/add-on clause printed",
             "flight-limited": "multi-flight: may not re-enter a flight after bagging",
             "ambiguous-subsequent-buyins": "AMBIGUOUS: sheet refers to 'subsequent buy-ins' (FL03)"}.get(
                 s.get("entryWording"), esc(s.get("entryWording", "")))
    srows.append(f"""<tr><td>{s['sheet']}</td><td>{ev}</td><td>{esc(s['title'])}</td>
<td>{esc(s.get('startTime',''))}</td><td>{esc(s.get('chips',''))}</td>
<td>{esc(s.get('levelMinutes',''))} min × {esc(s.get('levels',''))}</td>
<td>{fee}</td><td>{money(s.get('guarantee'))}</td><td>{esc(s.get('pays',''))}</td>
<td>{esc(s.get('bounty','') or '—')}</td>
<td><small>{entry}</small><br><small class="q">“{esc((s.get('entryExcerpt') or '—')[:180])}”</small></td>
<td><a href="{sheet_url(s['sheet'])}" target="_blank" rel="noopener">sheet PDF</a></td></tr>""")

# ---- 2. entry-clause excerpts (non-Venetian verified rows)
erows = []
seen = set()
for t in T:
    if t["venue"] == "venetian":
        continue
    e = t.get("entry", {})
    key = (t["venueName"], t["name"])
    if key in seen:
        continue
    seen.add(key)
    erows.append(f"""<tr><td>{esc(t['venueName'])}</td><td>{esc(t['name'])}<br><small>{esc(t['date'])} · {esc(t.get('time',''))}</small></td>
<td>{esc(e.get('reentry',''))}</td><td>{esc(e.get('rebuy','') or '—')}</td><td>{esc(e.get('addon','') or '—')}</td>
<td><small class="q">“{esc((e.get('excerpt') or '')[:260])}”</small></td>
<td>{('<a href="'+esc(e.get('sheetUrl'))+'" target="_blank" rel="noopener">official doc</a>') if e.get('sheetUrl') else '<span class="u">—</span>'} · {esc(e.get('retrieved',''))}</td></tr>""")

# ---- 3. flags
frows = []
for f in FLAGS:
    frows.append(f"""<tr><td id="fl-{esc(f['id'])}">{esc(f['id'])}</td><td>{esc(f['title'])}</td>
<td>{esc(f['level'])}</td><td>{esc(f['finding'])}</td><td>{esc(f['next'])}</td>
<td><a href="{esc(f['source'])}" target="_blank" rel="noopener">source</a></td></tr>""")

# ---- 4. hotels
hrows = []
for h in HOTELS:
    hrows.append(f"""<tr><td>{esc(h['name'])}<br><small>{esc(h['address'])}</small></td>
<td>{money(h.get('resortFee'))} + tax</td><td>13.38% Clark County room tax (tax applies to rate and resort fee)</td>
<td><small>{esc(h.get('parking') or 'blank')}</small></td><td><small>{esc(h.get('cancellation') or 'blank')}</small></td>
<td><small>{esc(h.get('rateNote') or '')}</small></td>
<td>{('<a href="'+esc(h.get('bookingUrl'))+'" target="_blank" rel="noopener">booking</a>') if h.get('bookingUrl') else ''} · {esc(h.get('lastChecked',''))}</td></tr>""")

# ---- 5. routes
rrows = []
for r in ROUTES:
    rrows.append(f"""<tr><td>{esc(r['hotelName'])} → {esc(r['venueName'])}</td>
<td><small>{esc(r['hotelAddress'])}</small></td><td><small>{esc(r['venueAddress'])}</small></td>
<td>{esc(r['walkingNote'])}</td>
<td><a href="{esc(r['mapLink'])}" target="_blank" rel="noopener">Google Maps (walking)</a></td>
<td>{esc(r['lastChecked'])}</td></tr>""")

page = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Structure-sheet verification · Vegas Poker Planner</title>
<style>
body{{font:14px/1.5 -apple-system,'Segoe UI',Roboto,Arial,sans-serif;background:#0e1116;color:#e8ecf1;margin:0;padding:20px}}
main{{max-width:1240px;margin:0 auto}} h1{{margin:6px 0}} h2{{margin:26px 0 6px;border-bottom:1px solid #2a3341;padding-bottom:6px}}
table{{border-collapse:collapse;width:100%;font-size:12.5px;margin:10px 0 22px;background:#171c24}}
th{{text-align:left;background:#1e2530;color:#9aa7b8;padding:8px}} td{{padding:7px 8px;border-top:1px solid #2a3341;vertical-align:top}}
a{{color:#4da3ff;text-decoration:none}} a:hover{{text-decoration:underline}}
.u{{color:#e06c6c;font-style:italic}} .q{{color:#9aa7b8}} .lede{{color:#9aa7b8;max-width:90ch}}
.wrap{{overflow-x:auto}} .back{{display:inline-block;margin:6px 0 14px}}
</style></head><body><main>
<a class="back" href="index.html">← back to the dashboard</a>
<h1>Structure-sheet verification — all 37 official sheets, read line by line</h1>
<p class="lede">Every Venetian DeepStack Extravaganza IV structure sheet (dse_nov_2026-structure_1..37.pdf), retrieved 2026-11-16,
verified field by field: event numbers, start time, starting stack, level length, level count, house-fee / prize-pool split,
guarantee, payout percentage, bounty amounts, and entry clauses. <b>No sheet prints the words “single entry”, and no sheet prints a
re-entry, rebuy or add-on clause</b> (except sheet 8's ambiguous “subsequent buy-ins” reference and the multi-flight bagging rules).
Buy-in totals, fee splits and guarantees below are printed values, not estimates. Machine-readable copy:
<a href="data/tournaments.json">data/tournaments.json</a> and <a href="../data/sheet_extracts.jsonl">data/sheet_extracts.jsonl</a>.</p>

<h2>1 · Sheet matrix (1–37)</h2>
<div class="wrap"><table><thead><tr><th>Sheet</th><th>Events</th><th>Event name</th><th>Start</th><th>Stack</th><th>Levels</th>
<th>Fee split (house / prize)</th><th>Guarantee</th><th>Pays</th><th>Bounty</th><th>Entry clauses on the sheet (with excerpt)</th><th>Source</th></tr></thead>
<tbody>{''.join(srows)}</tbody></table></div>

<h2>2 · Entry-rule excerpts verified at Wynn and Bellagio (spend-more formats)</h2>
<p class="lede">These are the exact clauses that disqualify each event from the single-entry path. Full row set:
<a href="data/tournaments.json">data/tournaments.json</a>.</p>
<div class="wrap"><table><thead><tr><th>Room</th><th>Event</th><th>Re-entry</th><th>Rebuy</th><th>Add-on / paid chips</th><th>Official excerpt</th><th>Source</th></tr></thead>
<tbody>{''.join(erows)}</tbody></table></div>

<h2>3 · Irregularities and flags (do not block; all link their official source)</h2>
<div class="wrap"><table><thead><tr><th>ID</th><th>Item</th><th>Level</th><th>Finding</th><th>What to do</th><th>Source</th></tr></thead>
<tbody>{''.join(frows)}</tbody></table></div>

<h2>4 · Hotel policies verified from official terms (2026-11-16)</h2>
<p class="lede">True nightly cost = rate + resort fee + 13.38% tax. Venetian poker-suite qualification (official page): six hours of live cash
play <i>or</i> a $300+ tournament buy-in for each night stayed, before 2 a.m. of the last night; unqualified nights are repriced to the
prevailing rate. Dated rates are logged, never overwritten — see the canonical <a href="hotels.html">hotels page</a> for the rate log.</p>
<div class="wrap"><table><thead><tr><th>Hotel / official address</th><th>Resort fee</th><th>Tax</th><th>Parking</th><th>Cancellation</th><th>Rate note</th><th>Sources</th></tr></thead>
<tbody>{''.join(hrows)}</tbody></table></div>

<h2>5 · Hotel–venue walking routes — official addresses + verification links</h2>
<p class="lede">No venue publishes walking times; nothing is guessed. Each pair carries its official addresses and a Google Maps walking
link; the 30-minute limit applies to verified values (<span class="u">FL08</span>).</p>
<div class="wrap"><table><thead><tr><th>Pair</th><th>Hotel address</th><th>Room address</th><th>Walking time</th><th>Verify</th><th>Checked</th></tr></thead>
<tbody>{''.join(rrows)}</tbody></table></div>

<p class="lede">Session arena/ef37b79e-poker3 · verified 2026-11-16 against official venue PDFs and pages only ·
back to the <a href="index.html">dashboard</a>.</p>
</main></body></html>"""

with open(os.path.join(ROOT, "site", "sheets.html"), "w") as f:
    f.write(page)
print("wrote site/sheets.html", len(page), "bytes;", len(sheets), "sheets")
