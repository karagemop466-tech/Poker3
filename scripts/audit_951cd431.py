#!/usr/bin/env python3
"""Independent line-by-line audit for session arena/951cd431-poker3.

Re-derives every number a reader acts on straight from site/data.json and the
verbatim official copies in raw/.  Deliberately does NOT import the site's own
builder modules, so a defect in the builder cannot hide itself here.
"""
import json, re, sys, datetime, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
D = json.load(open(ROOT / 'site' / 'data.json'))

MON = {m: i + 1 for i, m in enumerate(
    ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August',
     'September', 'October', 'November', 'December'])}
WD = {w: i for i, w in enumerate(
    ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])}

def num(v):
    """Coerce a stored value to float, or None when blank/not numeric."""
    if v is None: return None
    if isinstance(v, (int, float)): return float(v)
    s = str(v).strip().replace(',', '').replace('$', '')
    if not s: return None
    try: return float(s)
    except ValueError: return None

def tomin(t):
    if not t: return None
    m = re.match(r'^(\d{1,2}):(\d{2})\s*([AP])M$', str(t).strip().upper().replace('.', ''))
    if not m: return None
    h = int(m.group(1)) % 12
    if m.group(3) == 'P': h += 12
    return h * 60 + int(m.group(2))

def fmt(x):
    if x is None: return ''
    x = int(round(x)) % 1440
    h, mi = divmod(x, 60)
    return f"{h % 12 or 12}:{mi:02d} {'AM' if h < 12 else 'PM'}"

fails, warns = [], []
def fail(msg): fails.append(msg)
def warn(msg): warns.append(msg)

# ---------------------------------------------------------------- 1. events
ev = D['events']
for e in ev:
    eid = e.get('id', '?')
    if not e.get('lastChecked'): fail(f'{eid}: no lastChecked date')
    if not e.get('source') and not (e.get('rules') or {}).get('singleEntry', {}).get('source'):
        fail(f'{eid}: no source link')
    g, b, r = num(e.get('guarantee')), num(e.get('buyIn')), num(e.get('ratio'))
    if g and b:
        exp = round(g / b, 1)
        if r is None or abs(r - exp) > 0.051:
            fail(f'{eid}: ratio {r} != guarantee {g} / buyIn {b} = {exp}')
    elif r is not None:
        fail(f'{eid}: ratio {r} printed with no guarantee or no buy-in')
    st, sm, ee = tomin(e.get('time')), num(e.get('sessionMin')), e.get('endEstimate')
    if st is not None and sm is not None and ee:
        exp = fmt(st + sm)
        if ee.strip().upper().replace('.', '') != exp.upper().replace('.', ''):
            fail(f'{eid}: endEstimate {ee} != start {e["time"]} + {sm:.0f} min = {exp}')
    if st is None and e.get('time'):
        warn(f'{eid}: unparsable start time {e["time"]!r}')
    lr = tomin(e.get('lateRegEnd'))
    if lr is not None and st is not None:
        delta = (lr - st) % 1440
        if not (0 < delta <= 12 * 60):
            fail(f'{eid}: lateRegEnd {e["lateRegEnd"]} is not 0-12h after start {e["time"]}')
    if e.get('date'):
        try: datetime.date.fromisoformat(e['date'])
        except ValueError: fail(f'{eid}: bad date {e["date"]!r}')

# ------------------------------------------------- 2. Venetian DSE IV vs raw
raw = (ROOT / 'raw' / 'dse_nov_2026_structures_page.md').read_text()
official = []
for line in raw.splitlines():
    m = re.match(r'^\|\s*(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday), '
                 r'([A-Z][a-z]+) (\d+), 2026\s*\|\s*([\d:]+ [AP]M)\s*\|\s*(\d+)\s*\|'
                 r'\s*(.*?)\s*\|\s*\[([^\]]+)\]\(([^)]+)\)\s*\|$', line)
    if m:
        official.append(dict(wd=m.group(1), mon=m.group(2), day=int(m.group(3)),
                             time=m.group(4), ev=int(m.group(5)), name=m.group(6),
                             sheet=m.group(7), url=m.group(8)))
pub = {}
for e in ev:
    if e.get('venue') == 'venetian':
        k = (e.get('date'), tomin(e.get('time')))
        pub.setdefault(k, []).append(e)
for r in official:
    dt = datetime.date(2026, MON[r['mon']], r['day'])
    if dt.weekday() != WD[r['wd']]:
        fail(f'official raw copy: {r["wd"]} {r["mon"]} {r["day"]} is not that weekday')
    k = (dt.isoformat(), tomin(r['time']))
    if k not in pub:
        fail(f'DSE IV row missing from data.json: {k[0]} {r["time"]} ev#{r["ev"]}')
        continue
    e = pub[k][0]
    mb = re.match(r'\$(\d[\d,]*)', r['name'])
    if mb and num(e.get('buyIn')) != float(mb.group(1).replace(',', '')):
        fail(f'DSE IV buy-in mismatch {k[0]} {r["time"]}: data {e["buyIn"]} vs official {mb.group(1)}')
    if r['url'] not in json.dumps(e.get('rules', {})) and r['url'] != e.get('source'):
        warn(f'DSE IV {k[0]} {r["time"]}: structure-sheet URL {r["sheet"]} not attached to the row')
# Known, published irregularity F33: the official NYE page lists two events at
# 11:10 AM on 2027-01-04. It is recorded on the Flagged page rather than
# silently corrected, because the repository's copy cannot settle it. The audit
# asserts the flag still exists, so fixing the data without retiring the flag -
# or the reverse - is caught here.
KNOWN_DUPLICATE = (('2027-01-04', 670),
                   ('vl-nye-2027-01-04-20-1110am', 'vl-nye-2027-01-04-27-1110am'))
KNOWN_DUPLICATE_NEEDLE = 'January 4, 2027'
flag_ids = {f.get('id') for f in D['flags']}
for k, v in sorted(pub.items()):
    if len(v) > 1:
        ids = tuple(sorted(x['id'] for x in v))
        if k == KNOWN_DUPLICATE[0] and ids == KNOWN_DUPLICATE[1]:
            # Look the flag up by what it says, not by its number: parallel
            # sessions renumber flags as they land, so a hardcoded id would
            # silently start matching somebody else's flag.
            matches = [f['id'] for f in D['flags']
                       if KNOWN_DUPLICATE_NEEDLE in (f.get('title') or '') + (f.get('detail') or '')]
            if len(matches) != 1:
                fail(f'the known duplicate NYE start time must be recorded by exactly one flag '
                     f'mentioning {KNOWN_DUPLICATE_NEEDLE!r}; found {matches}')
                known_flag = None
            else:
                known_flag = matches[0]
                print(f'known irregularity (published as {known_flag}): {k[0]} {fmt(k[1])} '
                      f'has two official rows: {ids}')
        else:
            fail(f'duplicate Venetian (date,time) key {k}: {ids}')
DSE_OFFICIAL = len(official)

# ------------------------------------------------------------- 3. hotels
for h in D['hotels']:
    hid = h['id']
    if not h.get('source'): fail(f'hotel {hid}: no source link')
    if not h.get('lastChecked'): fail(f'hotel {hid}: no lastChecked')
    fee, tax = num(h.get('resortFee')), num(h.get('taxRate'))
    floor = num(h.get('baseRateFloor'))
    if floor is not None and fee is not None and tax is not None:
        exp = round((floor + fee) * (1 + tax / 100), 2)
        claim = num(h.get('trueNightlyLow'))
        if claim is not None and abs(claim - exp) > 0.011:
            fail(f'hotel {hid}: trueNightlyLow {claim} != (floor {floor} + fee {fee}) x (1 + {tax}%) = {exp}')
        ceil = num(h.get('baseRateCeiling'))
        claim_hi = num(h.get('trueNightlyHigh'))
        if None not in (ceil, claim_hi) and abs(claim_hi - round((ceil + fee) * (1 + tax / 100), 2)) > 0.011:
            fail(f'hotel {hid}: trueNightlyHigh {claim_hi} != (ceiling {ceil} + fee {fee}) x (1 + {tax}%) = '
                 f'{round((ceil + fee) * (1 + tax / 100), 2)}')
    if floor is None and not h.get('baseRateNote'):
        fail(f'hotel {hid}: no published rate and no note explaining the blank')
    if fee is None and not h.get('resortFeeNote'):
        fail(f'hotel {hid}: no resort fee and no note explaining the blank')

# --------------------------------------------------------- 4. rate log
for r in D['rateLog']:
    low, high, tax = num(r.get('trueNightlyLow')), num(r.get('trueNightlyHigh')), num(r.get('tax'))
    nights = num(r.get('nights')) or 2
    tot = num(r.get('total'))
    if None not in (low, high) and tot is not None:
        exp = round(low + high, 2)
        if abs(tot - exp) > 0.011:
            fail(f'rate log {r.get("hotel")} {r.get("observedOn")}: nights {low}+{high} = {exp} != total {tot}')
    for nite in (low, high):
        pass
    if not r.get('source'): fail(f'rate log {r.get("hotel")}: no source link')
    if not r.get('observedOn'): fail(f'rate log {r.get("hotel")}: no observedOn date')
# Every dated official checkout total must reconcile to a figure printed in its
# own note. The note carries several dollar amounts (the per-night rates, the
# resort fee, the tax, the total), so the check is that the two derived nights
# add to one of the amounts the record itself prints. Not one fixed number: the
# repository holds several dated quotes for different stays and suites.
MONEY = re.compile(r'\$([0-9][0-9,]*(?:\.[0-9]{2})?)')
for r in D['rateLog']:
    if 'checkout total' not in (r.get('quoteType') or '').lower():
        continue
    low, high = num(r.get('trueNightlyLow')), num(r.get('trueNightlyHigh'))
    if low is None or high is None:
        fail(f'rate log {r.get("hotel")} {r.get("observedOn")}: a dated checkout total with no derived nights')
        continue
    printed = {round(float(m.replace(',', '')), 2) for m in MONEY.findall(r.get('note') or '')}
    if r.get('nightlyTrueCost'):
        # Multi-night quote (the 7-night fixed-stay read): each night is re-derived from its printed rate and
        # the hotel's printed resort fee, the nights must sum to the printed total, and low/high are the min/max night.
        nts = [float(x) for x in r['nightlyTrueCost']]
        rates = [float(x) for x in (r.get('nightlyRates') or [])]
        fee_n = next((num(hh.get('resortFee')) for hh in D['hotels'] if hh['id'] == r.get('hotel')), None)
        if len(rates) != len(nts) or fee_n is None:
            fail(f'rate log {r.get("hotel")} {r.get("observedOn")}: nightlyRates/nightlyTrueCost do not line up')
            continue
        for i, (rt, nt) in enumerate(zip(rates, nts), 1):
            if abs(round((rt + fee_n) * 1.1338, 2) - nt) > 0.011:
                fail(f'rate log {r.get("hotel")} {r.get("observedOn")}: night {i} {nt} != ({rt} + {fee_n}) x 1.1338')
        if abs(min(nts) - low) > 0.011 or abs(max(nts) - high) > 0.011:
            fail(f'rate log {r.get("hotel")} {r.get("observedOn")}: trueNightlyLow/High are not the min/max night')
        got = round(sum(nts), 2)
    else:
        got = round(low + high, 2)
    if not any(abs(got - p) <= 0.011 for p in printed):
        fail(f'rate log {r.get("hotel")} {r.get("observedOn")}: the two derived nights {low} + {high} = {got} '
             f'do not appear among the figures the record prints ({sorted(printed)})')
    fee = next((num(hh.get('resortFee')) for hh in D['hotels'] if hh['id'] == r.get('hotel')), None)
    for label, nite in (('first', low), ('second', high)):
        # nightly = (room rate + resort fee) x (1 + 13.38% Clark County room tax)
        implied = round(nite / 1.1338 - (fee or 0), 2)
        if implied <= 0:
            fail(f'rate log {r.get("hotel")} {r.get("observedOn")}: {label} night {nite} implies a '
                 f'non-positive room rate of {implied}')

# -------------------------------------------------------- 5. routes <= 30
for r in D['routes']:
    if not r.get('source'): fail(f'route {r.get("hotel")}->{r.get("venue")}: no source link')
    if not r.get('lastChecked'): fail(f'route {r.get("hotel")}->{r.get("venue")}: no lastChecked')
    m = num(r.get('minutes'))
    if m is None: fail(f'route {r.get("hotel")}->{r.get("venue")}: no walking minutes')
    elif m > 30:
        # Over the limit is a legitimate published observation, not a defect, but
        # every such row must say so on the page rather than silently fail a filter.
        if 'walk' not in json.dumps(r).lower():
            warn(f'route {r.get("hotel")}->{r.get("venue")}: {m:.0f} min exceeds the limit with no note')
    if 'google' not in (r.get('walkSourceType') or '').lower():
        fail(f'route {r.get("hotel")}->{r.get("venue")}: walking-time source type is not disclosed')

# ---------------------------------------------------- 6. trip / day plan
t = D['trip']
floor, fee, tax = num(t.get('nightlyBudget')), 119, 13.38
if floor is not None:
    exp = round((119 + 55) * 1.1338, 2)
    if abs(floor - exp) > 0.011:
        fail(f'trip nightlyBudget {floor} != (119 + 55) x 1.1338 = {exp}')
start = datetime.date.fromisoformat(t['start']); end = datetime.date.fromisoformat(t['end'])
if (end - start).days != t['nights']:
    fail(f'trip: nights {t["nights"]} != {end} - {start} = {(end - start).days}')
if len(D['dayPlan']) != t['days']:
    fail(f'trip: days {t["days"]} != dayPlan rows {len(D["dayPlan"])}')
seen = set()
for day in D['dayPlan']:
    if day['date'] in seen: fail(f'dayPlan: duplicate date {day["date"]}')
    seen.add(day['date'])
    if not (start <= datetime.date.fromisoformat(day['date']) <= end):
        fail(f'dayPlan date {day["date"]} outside the trip window')
    for key in ('primary', 'fallback'):
        eid = day.get(key)
        if eid and isinstance(eid, str):
            row = next((x for x in ev if x.get('id') == eid), None)
            if row is None:
                fail(f'dayPlan {day["date"]}: {key} id {eid} is not a known event')
            elif row.get('date') != day['date']:
                fail(f'dayPlan {day["date"]}: {key} event {eid} is dated {row.get("date")}')
    pt, pe = tomin(day.get('primaryTime')), tomin(day.get('primaryEnd'))
    if pt is not None and pe is not None and not (0 < (pe - pt) % 1440 <= 20 * 60):
        fail(f'dayPlan {day["date"]}: primaryEnd {day["primaryEnd"]} is not after primaryTime {day["primaryTime"]}')

# ---------------------------------------------- 7. sources / flags / sheets
for s in D['sources']:
    if not s.get('url'): fail(f'source {s.get("id", "?")}: no url')
    if not (s.get('lastChecked') or s.get('checked')): fail(f'source {s.get("id", "?")}: no last-checked date')
for f in D['flags']:
    if not f.get('id'): fail('flag without an id')
ids = [f['id'] for f in D['flags']]
if len(ids) != len(set(ids)): fail('duplicate flag ids')
for q in D['questions']:
    if not q.get('id'): fail('question without an id')
for s in D['suggestions']:
    if not s.get('id'): fail('suggestion without an id')

# ------------------------------------------------------------- 8. result
print(f'events: {len(ev)}  (Venetian DSE IV official rows in raw/: {DSE_OFFICIAL})')
print(f'hotels: {len(D["hotels"])}  routes: {len(D["routes"])}  sources: {len(D["sources"])}  flags: {len(D["flags"])}')
print(f'rate-log records: {len(D["rateLog"])}   day-plan days: {len(D["dayPlan"])}   sheets: {len(D["structureSheets"])}')
for w in warns[:40]: print('WARN ', w)
if warns: print(f'  ({len(warns)} warnings)')
for f in fails[:60]: print('FAIL ', f)
print(f'\n{len(fails)} failures, {len(warns)} warnings')
sys.exit(1 if fails else 0)
