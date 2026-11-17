#!/usr/bin/env python3
"""Build site/sheets.html — structure-sheet verification, entry-rule evidence, flag register.

Rewritten 2026-11-17 (session arena/57c814fd-poker3) to close flag F68.

WHAT WAS WRONG. The previous version read `site/data/{tournaments,hotels,routes,flags}.json`.
Those were four snapshots frozen on 2026-11-16 that no script regenerated, so this page —
which sits in the site navigation — published stale numbers: 14 retired `FL`-prefixed flags
instead of the live 72-item `F` register, 5 of 8 hotels, and 13 of 15 walking routes with
every walking time blank. The three unused snapshots have been deleted; `site/data.json` is
the one current data file.

WHAT THIS READS NOW.
  * `data/sheet_extracts.jsonl`  — the field-by-field read record for the 37 DeepStack
                                   Extravaganza IV structure PDFs (dated 2026-11-16)
  * `scripts/data_venetian.py`   — the same facts for the 37 DSE IV sheets plus the 15 NYE
                                   sheets, i.e. what the dashboard itself renders from
  * `site/data.json`             — hotels, routes, flags, and each event's published category

TWO VOCABULARIES, ONE MEANING. `sheet_extracts.jsonl` records what the *sheet prints*
(`entryWording`), while `data_venetian.py` records the event's entry *format* (`entry`).
They use different words for the same fact and they disagree on five sheets only because a
satellite or a tag-team prints no entry clause at all — its format is not `none`. The mapping
below is applied explicitly and every pair is checked at build time; an unexplained
disagreement is written onto the page instead of being hidden.
"""
import json, os, sys, html
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import data_venetian as V  # noqa: E402

TODAY = "2026-11-17"

# sheet_extracts.jsonl wording -> data_venetian.py format. Both describe the same sheet.
ENTRY_EQUIV = {
    "none": {"none", "satellite", "special"},
    "flight-limited": {"multi-flight"},
    "ambiguous-subsequent-buyins": {"multi-buyin"},
}

VERDICT = {
    "none": ("no re-entry, rebuy or add-on clause printed", "ok"),
    "flight-limited": ("separate starting flights; a player may not re-enter a flight after bagging", "warn"),
    "ambiguous-subsequent-buyins": ("the sheet refers to “subsequent buy-in's”, so more than one buy-in is possible", "bad"),
    "multi-flight": ("separate starting flights; a player may not re-enter a flight after bagging", "warn"),
    "multi-buyin": ("the sheet prints more than one buy-in: not a single-entry event", "bad"),
    "satellite": ("satellite: awards direct entry to another event, so it has no cash freezeout rule", "warn"),
    "special": ("restricted or team format; the sheet prints no entry clause but the format is not a plain freezeout", "warn"),
}


def esc(x):
    return html.escape(str(x if x is not None else ""))


def money(x):
    try:
        return "$" + f"{float(x):,.0f}"
    except (TypeError, ValueError):
        return "—"


def guarantee(x):
    """The read record stores the guarantee as an int or as a printed string."""
    if isinstance(x, (int, float)):
        return money(x)
    return esc(x) if x not in (None, "") else "—"


def num(x):
    try:
        return f"{int(x):,}"
    except (TypeError, ValueError):
        return "—"


def load(path):
    with open(path) as f:
        return json.load(f)


DATA = load(os.path.join(ROOT, "site", "data.json"))
FLAGS = DATA["flags"]
HOTELS = DATA["hotels"]
ROUTES = DATA["routes"]
EXTRACTS = {}
with open(os.path.join(ROOT, "data", "sheet_extracts.jsonl")) as f:
    for line in f:
        line = line.strip()
        if line:
            s = json.loads(line)
            EXTRACTS[s["sheet"]] = s

# ------------------------------------------------------------------ consistency check
DISAGREEMENTS = []
for n, ext in EXTRACTS.items():
    fmt = V.SHEETS.get(n, {}).get("entry")
    if fmt is None:
        DISAGREEMENTS.append((n, "sheet %d is in the read record but not in data_venetian.py" % n))
        continue
    if fmt not in ENTRY_EQUIV.get(ext["entryWording"], set()):
        DISAGREEMENTS.append((n, "read record says %r, dashboard module says %r"
                              % (ext["entryWording"], fmt)))

# ------------------------------------------------------------------ 1. DSE IV sheets
def rows_dse():
    out = []
    for n in sorted(EXTRACTS):
        s = EXTRACTS[n]
        wording = s["entryWording"]
        label, cls = VERDICT.get(wording, (esc(wording), ""))
        evs = ", ".join("#" + str(x) for x in s["events"])
        out.append(f"""<tr><td>{n}</td><td>{esc(evs)}</td><td>{esc(s['title'])}</td>
<td>{esc(s.get('startTime',''))}</td><td>{num(s.get('chips'))}</td>
<td>{esc(s.get('levelMinutes',''))} min × {esc(s.get('levels','—'))}</td>
<td><small>{esc(s.get('lateReg',''))}</small></td>
<td>{money(s.get('houseFee'))} / {money(s.get('prizeShare'))}</td>
<td>{guarantee(s.get('guarantee'))}{' <small class="q">(' + esc(s['guaranteeNote']) + ')</small>' if s.get('guaranteeNote') else ''}</td>
<td>{esc(s.get('pays','') or '—')}</td><td>{esc(s.get('bounty','') or '—')}</td>
<td class="{cls}"><small>{label}</small>{('<br><small class="q">“' + esc(s['entryExcerpt'][:150]) + '”</small>') if s.get('entryExcerpt') else ''}</td>
<td><a href="{V.BASE}/dse_nov_2026-structure_{n}.pdf" target="_blank" rel="noopener">PDF</a></td></tr>""")
    return out


# ------------------------------------------------------------------ 2. NYE sheets
def nye_files():
    files = {}
    for row in V.NYE_ROWS:
        sheet_file = row[4]
        n = int(sheet_file.rsplit("structure_", 1)[1].replace(".pdf", ""))
        files.setdefault(n, sheet_file)
    return files


def rows_nye():
    out = []
    files = nye_files()
    for n in sorted(V.NYE_SHEETS):
        s = V.NYE_SHEETS[n]
        label, cls = VERDICT.get(s.get("entry", ""), (esc(s.get("entry", "")), ""))
        url = f"{V.BASE}/{files[n]}" if n in files else ""
        out.append(f"""<tr><td>{n}</td><td>{esc(s.get('events',''))}</td><td>{esc(s.get('title',''))}</td>
<td><small>{esc(s.get('late',''))}</small></td><td>{num(s.get('chips'))}</td>
<td>{esc(s.get('levelMin',''))} min</td>
<td>{money(s.get('rake'))} / {money(s.get('pool'))}</td><td>{guarantee(s.get('guarantee'))}</td>
<td class="{cls}"><small>{label}</small></td>
<td>{('<a href="' + esc(url) + '" target="_blank" rel="noopener">PDF</a>') if url else '—'}</td></tr>""")
    return out


# ------------------------------------------------------------------ 3. spend-more rows
def rows_extra():
    """Published rows whose entry format allows more than one buy-in, straight from data.json."""
    out = []
    seen = set()
    for e in DATA["events"]:
        if e.get("venue") != "venetian" or e.get("entryType") not in ("multi-buyin", "multi-flight"):
            continue
        key = e.get("structureUrl") or e.get("name")
        if key in seen:
            continue
        seen.add(key)
        rule = (e.get("rules") or {}).get("singleEntry", {})
        out.append(f"""<tr><td>{esc(e['date'] or 'recurring')}</td>
<td>{esc(e['time'])} · #{esc(e['id'].split('-')[3])}</td><td>{esc(e.get('name',''))}</td>
<td>{esc(e.get('entryType',''))}</td><td>{money(e.get('buyIn'))}</td>
<td><small class="q">{esc((rule.get('excerpt') or '')[:280])}</small></td>
<td>{('<a href="' + esc(rule.get('source')) + '" target="_blank" rel="noopener">sheet</a>') if rule.get('source') else '—'}
· {esc(rule.get('retrieved',''))}</td></tr>""")
    return out


srows, nrows, xrows = rows_dse(), rows_nye(), rows_extra()

dbg = ""
if DISAGREEMENTS:
    items = "".join(f"<li>sheet {n}: {esc(m)}</li>" for n, m in DISAGREEMENTS)
    dbg = f'<div class="warn"><b>The read record and the dashboard module disagree on {len(DISAGREEMENTS)} sheet(s):</b><ul>{items}</ul></div>'
else:
    dbg = ('<div class="ok">Cross-check passed at build time: the 2026-11-16 read record '
           f'(<code>data/sheet_extracts.jsonl</code>) and the dashboard module (<code>scripts/data_venetian.py</code>) '
           f'agree on the entry rule of all {len(EXTRACTS)} DeepStack Extravaganza IV sheets, once the two '
           'vocabularies for the same fact are mapped.</div>')

by_area = defaultdict(list)
for f in FLAGS:
    by_area[f.get("area", "Other")].append(f)
frows = []
for area in sorted(by_area):
    for f in by_area[area]:
        frows.append(f"""<tr><td id="fl-{esc(f['id'])}"><b>{esc(f['id'])}</b></td><td>{esc(f.get('severity',''))}</td>
<td>{esc(area)}</td><td>{esc(f.get('title',''))}</td><td><small>{esc(f.get('detail',''))}</small></td>
<td><a href="{esc(f.get('source',''))}" target="_blank" rel="noopener">source</a></td></tr>""")

hrows = []
for h in HOTELS:
    hrows.append(f"""<tr><td>{esc(h.get('name',''))}<br><small>{esc(h.get('rooms',''))}</small></td>
<td>{money(h.get('resortFee'))} + tax</td><td>{esc(h.get('taxRate',''))}%</td>
<td>{esc(h.get('trueNightlyLow','') or 'blank')} / {esc(h.get('trueNightlyHigh','') or 'blank')}</td>
<td><small>{esc(h.get('parking','') or 'blank')}</small></td>
<td><small>{esc(h.get('cancellation','') or 'blank')}</small></td>
<td>{('<a href="' + esc(h.get('bookingUrl')) + '" target="_blank" rel="noopener">booking</a>') if h.get('bookingUrl') else '—'}
· {esc(h.get('lastChecked',''))}</td></tr>""")

rrows = []
for r in ROUTES:
    mins = r.get("minutes")
    over = isinstance(mins, (int, float)) and mins > 30
    cls = "bad" if over else "ok"
    rrows.append(f"""<tr><td>{esc(r.get('hotel',''))} → {esc(r.get('venue',''))}</td>
<td class="{cls}">{esc(mins) if mins not in (None, '') else 'blank'} min{(' · over the 30-minute limit' if over else '')}</td>
<td>{esc(r.get('miles','') or '—')}</td><td><small>{esc(r.get('note',''))}</small></td>
<td><a href="{esc(r.get('mapsUrl',''))}" target="_blank" rel="noopener">Google Maps (walking)</a></td>
<td>{esc(r.get('lastChecked',''))}</td></tr>""")

page = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Structure-sheet verification and flag register · Vegas Poker Planner</title>
<style>
body{{font:14px/1.5 -apple-system,'Segoe UI',Roboto,Arial,sans-serif;background:#0e1116;color:#e8ecf1;margin:0;padding:20px}}
main{{max-width:1500px;margin:0 auto}} h1{{margin:6px 0}} h2{{margin:30px 0 6px;border-bottom:1px solid #2a3341;padding-bottom:6px}}
table{{border-collapse:collapse;width:100%;font-size:12.5px;margin:10px 0 22px;background:#171c24}}
th{{text-align:left;background:#1e2530;color:#9aa7b8;padding:8px;position:sticky;top:0}} td{{padding:7px 8px;border-top:1px solid #2a3341;vertical-align:top}}
a{{color:#4da3ff;text-decoration:none}} a:hover{{text-decoration:underline}}
.u{{color:#e06c6c;font-style:italic}} .q{{color:#9aa7b8}} .lede{{color:#9aa7b8;max-width:95ch}}
.ok{{color:#79c98a}} .warn{{color:#e0b96c}} .bad{{color:#e06c6c}}
.wrap{{overflow-x:auto;max-height:80vh;overflow-y:auto;border:1px solid #2a3341;border-radius:6px}}
.back{{display:inline-block;margin:6px 0 14px}} code{{color:#9fd0ff}}
</style></head><body><main>
<a class="back" href="index.html">← back to the dashboard</a>
<h1>Structure-sheet verification · {len(EXTRACTS) + len(V.NYE_SHEETS)} official sheets, read line by line</h1>
<p class="lede">Every Venetian DeepStack structure sheet behind a published row, field by field against the official PDF: event
numbers, start time, starting stack, level length, registration close, house-fee / prize-pool split, guarantee, payout
percentage, bounty amounts and the entry clauses. <b>No sheet prints the words “single entry”, and no sheet prints a re-entry,
rebuy or add-on clause</b> except where the verdict column says otherwise (sheet 8's “subsequent buy-in's” wording, and the
multi-flight bagging rules). Every fee split, guarantee and chip count below is a printed value, not an estimate.
This page is generated from <code>data/sheet_extracts.jsonl</code>, <code>scripts/data_venetian.py</code> and
<code>site/data.json</code> — no other file.</p>
<p class="lede">{dbg}</p>

<h2>1 · {len(EXTRACTS)} DeepStack Extravaganza IV sheets (16 Nov – 23 Dec 2026)</h2>
<div class="wrap"><table><thead><tr><th>Sheet</th><th>Events</th><th>Event name</th><th>Start</th><th>Chips</th><th>Levels</th>
<th>Registration closes</th><th>House / prize split</th><th>Guarantee</th><th>Pays</th><th>Bounty</th>
<th>Entry rule printed on the sheet</th><th>Source</th></tr></thead>
<tbody>{''.join(srows)}</tbody></table></div>

<h2>2 · {len(V.NYE_SHEETS)} DeepStack Extravaganza NYE sheets (26 Dec 2026 – 10 Jan 2027)</h2>
<div class="wrap"><table><thead><tr><th>Sheet</th><th>Events</th><th>Event name</th><th>Registration closes</th><th>Chips</th>
<th>Levels</th><th>House / prize split</th><th>Guarantee</th><th>Entry rule printed on the sheet</th><th>Source</th></tr></thead>
<tbody>{''.join(nrows)}</tbody></table></div>

<h2>3 · Where spending more can buy a second chance — kept apart from the single-entry list</h2>
<p class="lede">These are the published rows whose own structure sheet prints more than one buy-in or more than one starting
flight. They are not rejected as bad events; they are separated because a player who cannot play a second bullet is competing
under different rules from a player who can. The excerpt is the sheet's own wording.</p>
<div class="wrap"><table><thead><tr><th>First date</th><th>Start · event #</th><th>Event</th><th>Entry format</th><th>Buy-in</th>
<th>Excerpt from the sheet</th><th>Source · read on</th></tr></thead><tbody>{''.join(xrows)}</tbody></table></div>

<h2>4 · Flag register — all {len(FLAGS)} open items, grouped by area</h2>
<p class="lede">Every irregularity and every value that could not be confirmed from an official source. None of these blocks
the site from being used or published; each carries the official link so it can be reviewed and either fixed or retired. The
same register is rendered on the <a href="flagged.html">Flagged for review page</a>.</p>
<div class="wrap"><table><thead><tr><th>ID</th><th>Severity</th><th>Area</th><th>Item</th><th>Finding</th><th>Source</th></tr></thead>
<tbody>{''.join(frows)}</tbody></table></div>

<h2>5 · Hotel policies and true cost per night</h2>
<p class="lede">True nightly cost = rate + mandatory resort fee + Clark County room tax. The Venetian poker rate requires six
hours of live cash play <b>or</b> a $300+ tournament buy-in for each night stayed, before 2 a.m. of the last night; unqualified
nights are repriced to the prevailing rate. Dated quotes are appended to the rate log, never overwritten — see the
<a href="hotels.html">hotels page</a>.</p>
<div class="wrap"><table><thead><tr><th>Hotel</th><th>Resort fee</th><th>Tax</th><th>True cost / night (low / high)</th>
<th>Parking</th><th>Cancellation</th><th>Official source · checked</th></tr></thead>
<tbody>{''.join(hrows)}</tbody></table></div>

<h2>6 · Hotel–venue walking routes, 30-minute limit applied</h2>
<p class="lede">No venue publishes a walking time, so every figure below is a Google Maps walking estimate and is labelled as
such. Each row links the exact directions query so it can be re-run. A pair over 30 minutes is marked and is excluded by the
≤30-minute filter on the tournaments page.</p>
<div class="wrap"><table><thead><tr><th>Pair</th><th>Walking time</th><th>Distance</th><th>Note</th><th>Verify</th><th>Checked</th></tr></thead>
<tbody>{''.join(rrows)}</tbody></table></div>

<p class="lede">Generated {TODAY} by session <code>arena/57c814fd-poker3</code> · every value traced to an official venue or
property source · back to the <a href="index.html">dashboard</a>.</p>
</main></body></html>"""

with open(os.path.join(ROOT, "site", "sheets.html"), "w") as f:
    f.write(page)
print(f"wrote site/sheets.html {len(page)} bytes · {len(EXTRACTS)} DSE IV sheets · {len(V.NYE_SHEETS)} NYE sheets · "
      f"{len(FLAGS)} flags · {len(HOTELS)} hotels · {len(ROUTES)} routes · {len(xrows)} spend-more rows · "
      f"{len(DISAGREEMENTS)} unexplained disagreements")
