#!/usr/bin/env python3
"""Validation gate for the published site (runs in CI before every merge/deploy).

Checks:
  1. site/data/*.json parse and carry required fields (lastChecked, source links).
  2. All source links use https and known official domains.
  3. Verified tournament rows carry a buy-in (except restarts); ratios are consistent.
  4. Unknown values are blank/null (never fabricated: status 'verified' implies sheet fields exist).
  5. Generated HTML pages exist, nav links resolve, and every tournament row shows a source link.
  6. Flagged page contains every flag id from flags.json.
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "site", "data")
SITE = os.path.join(ROOT, "site")
errors, warns = [], []

OFFICIAL_DOMAINS = (
    "venetianlasvegas.com", "wynnlasvegas.com", "wynnpoker.com", "cdn.wynnresorts.com",
    "bellagio.mgmresorts.com", "mgmresorts.com", "aria.mgmresorts.com", "contentstack.io",
    "caesars.com", "pokertda.com", "google.com", "maps.google.com",
    "goldennugget.com", "rwlasvegas.com", "circleresorts.com", "saharalasvegas.com",
)

def err(m):
    errors.append(m)

def warn(m):
    warns.append(m)

def load(name):
    with open(os.path.join(DATA, name)) as f:
        return json.load(f)

def check_url(u, where):
    if not u:
        return
    if not u.startswith("https://"):
        err(f"{where}: non-https URL {u}")
        return
    host = re.sub(r"^https://(www\.)?", "", u).split("/")[0]
    if not any(host.endswith(d) for d in OFFICIAL_DOMAINS):
        err(f"{where}: non-official domain {u}")

def main():
    # --- data files parse
    files = ["tournaments.json", "hotels.json", "rates.json", "routes.json",
             "sources.json", "flags.json", "questions.json", "suggestions.json"]
    data = {}
    for fn in files:
        try:
            data[fn] = load(fn)
        except Exception as e:
            err(f"{fn}: does not parse: {e}")
    if errors:
        report()

    tourneys = data["tournaments.json"]["tournaments"]
    dayplan = data["tournaments.json"]["dayplan"]

    # --- tournaments
    ids = set()
    for t in tourneys:
        tid = t.get("id", "")
        where = f"tournament {tid or t.get('name')}"
        if not tid:
            err(where + ": missing id")
        if tid in ids:
            err(where + ": duplicate id")
        ids.add(tid)
        if not t.get("lastChecked"):
            err(where + ": missing lastChecked")
        if not t.get("scheduleSource"):
            err(where + ": missing scheduleSource")
        check_url(t.get("scheduleSource"), where)
        check_url(t.get("structureSource"), where)
        e = t.get("entry") or {}
        for k in ("singleEntryPrinted", "reentry", "rebuy", "addon"):
            if k not in e:
                err(where + f": entry.{k} missing")
        if t.get("status") == "verified" and t.get("bucket") not in ("restart",):
            if t.get("buyIn") in (None, "") and t.get("bucket") != "review":
                err(where + ": verified row with blank buy-in")
        if t.get("buyIn") and t.get("guarantee") and t.get("ratio"):
            expected = round(t["guarantee"] / t["buyIn"], 1)
            if abs(expected - t["ratio"]) > 0.3:
                err(where + f": ratio {t['ratio']} != guarantee/buyIn {expected}")
        # fabricated-value guard: verified rows must carry a fee split or an explicit blank flag
        if t.get("status") == "verified" and t.get("bucket") == "single-path":
            if t.get("houseFee") is None or t.get("prizeShare") is None:
                err(where + ": single-path verified row missing printed fee split")

    # --- day plan references
    for d in dayplan:
        for eid in d["events"]:
            if eid not in ids:
                err(f"dayplan {d['date']}: unknown event id {eid}")
        if d.get("primary") and d["primary"] not in ids:
            err(f"dayplan {d['date']}: unknown primary {d['primary']}")

    # --- hotels
    for h in data["hotels.json"]["hotels"]:
        where = "hotel " + h.get("id", "?")
        if not h.get("lastChecked"):
            err(where + ": missing lastChecked")
        if not h.get("address"):
            err(where + ": missing official address")
        for k in ("resortFeeSource", "taxSource", "bookingUrl", "rateSource"):
            check_url(h.get(k), where + f".{k}")
        if h.get("resortFee") not in (None, 55.0):
            warn(where + f": unexpected resort fee {h.get('resortFee')}")

    # --- rates / routes / flags
    for r in data["rates.json"]["rates"]:
        check_url(r.get("source"), "rate " + r.get("id", "?"))
        if not r.get("observed"):
            err("rate " + r.get("id", "?") + ": missing observation date")
    for r in data["routes.json"]["routes"]:
        if not r.get("hotelAddress") or not r.get("venueAddress"):
            err("route " + r.get("id", "?") + ": missing official address")
        check_url(r.get("mapLink"), "route " + r.get("id", "?"))
    for f in data["flags.json"]["flags"]:
        if not f.get("source"):
            err("flag " + f.get("id", "?") + ": missing source link")
        check_url(f.get("source"), "flag " + f.get("id", "?"))
    for s in data["sources.json"]["sources"]:
        check_url(s.get("url"), "source " + s.get("id", "?"))

    # --- generated pages
    pages = ["index.html", "tournaments.html", "schedule.html", "hotels.html", "routes.html",
             "calculator.html", "venues.html", "venue-venetian.html", "venue-wynn.html",
             "venue-bellagio.html", "venue-aria.html", "venue-others.html", "workflow.html",
             "monitoring.html", "sources.html", "questions.html", "suggestions.html", "flagged.html"]
    for p in pages:
        path = os.path.join(SITE, p)
        if not os.path.exists(path):
            err("missing page " + p)
            continue
        html = open(path).read()
        for m in re.findall(r'href="([^"#:]+\.html)"', html):
            if not os.path.exists(os.path.join(SITE, m)):
                err(f"{p}: broken local link {m}")

    # tournaments page must embed a source link per row
    tpage = open(os.path.join(SITE, "tournaments.html")).read()
    if tpage.count("target=\"_blank\"") < len([t for t in tourneys if t.get("scheduleSource")]):
        err("tournaments.html: fewer source links than tournament rows")

    # flagged page must contain every flag id
    fpage = open(os.path.join(SITE, "flagged.html")).read()
    for f in data["flags.json"]["flags"]:
        if f["id"] not in fpage:
            err("flagged.html: missing flag " + f["id"])

    # poker3 companion app still valid
    pj = os.path.join(SITE, "poker3", "data", "research.json")
    if os.path.exists(pj):
        try:
            json.load(open(pj))
        except Exception as e:
            err(f"poker3 research.json: {e}")
    report()

def report():
    print(f"verify_site: {len(errors)} errors, {len(warns)} warnings")
    for w in warns:
        print("WARN:", w)
    for e in errors:
        print("ERROR:", e)
    sys.exit(1 if errors else 0)

if __name__ == "__main__":
    main()
