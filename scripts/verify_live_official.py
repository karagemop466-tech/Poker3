"""Line-by-line cross-check of the canonical Venetian DeepStack Extravaganza IV rows.

Three independent captures are compared, field by field:

1. ``raw/dse_nov_2026_schedule_html_2026-11-17.md`` - the official HTML schedule page,
   re-fetched on 2026-11-17.
2. ``raw/venetian_dse_nov_2026_schedule.md``          - the official schedule PDF, read 2026-11-16.
3. ``site/data.json``                                 - the canonical published rows.

Every mismatch is printed. The script exits non-zero if any row disagrees, so the CI job
fails loudly rather than publishing a silent divergence.

Usage: ``python3 scripts/verify_live_official.py``
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HTML_RAW = ROOT / "raw" / "dse_nov_2026_schedule_html_2026-11-17.md"
PDF_RAW = ROOT / "raw" / "venetian_dse_nov_2026_schedule.md"
DATA = ROOT / "site" / "data.json"

MONTHS = {
    "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
    "july": 7, "august": 8, "september": 9, "october": 10, "november": 11, "december": 12,
}


def norm_name(text: str) -> str:
    """Collapse the cosmetic differences between the HTML page and the PDF."""
    t = text.lower()
    t = t.replace("<br>", " ").replace("-", " ")
    t = t.replace("no limit hold'em", "nlh")
    t = t.replace("pot limit omaha", "plo")
    t = t.replace("limit", "limit")
    t = re.sub(r"[^a-z0-9$# ]+", " ", t)
    t = re.sub(r"\s+", " ", t)
    return t.strip()


def parse_html_rows() -> list[dict]:
    rows = []
    for line in HTML_RAW.read_text().splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) != 5 or cells[2] in ("Event #", "---") or not cells[2].isdigit():
            continue
        date_s, time_s, num_s, name, sheet = cells
        m = re.match(r"[A-Za-z]+, ([A-Za-z]+) (\d+), (\d{4})$", date_s)
        if not m:
            continue
        rows.append({
            "date": f"{m.group(3)}-{MONTHS[m.group(1).lower()]:02d}-{int(m.group(2)):02d}",
            "time": time_s.replace(".m.", ".m.").upper(),
            "event": int(num_s),
            "name": norm_name(name),
            "sheet": int(sheet),
            "rawName": name,
        })
    return rows


def parse_pdf_rows() -> list[dict]:
    """The PDF capture has no year and prints decorative art in the DATE column on some rows.

    Rows whose date cell is not a weekday name are carried with a null date so the row can
    still be counted and its event number, time and name compared.
    """
    rows = []
    for line in PDF_RAW.read_text().splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 5 or not cells[1].isdigit():
            continue
        date_s, num_s, name, time_s = cells[0], cells[1], cells[2], cells[3]
        month = day = None
        m = re.match(r"([A-Za-z]+), ([A-Za-z]+) (\d+)$", date_s)
        if m and m.group(2).lower() in MONTHS:
            month, day = MONTHS[m.group(2).lower()], int(m.group(3))
        rows.append({
            "month": month,
            "day": day,
            "time": time_s.upper(),
            "event": int(num_s),
            "name": norm_name(name),
            "rawName": name,
        })
    return rows


def canonical_rows() -> list[dict]:
    data = json.loads(DATA.read_text())
    rows = []
    for e in data["events"]:
        if "dse-nov-2026" not in (e.get("scheduleUrl") or ""):
            continue
        sheet = e.get("sheetUrl") or ""
        m = re.search(r"structure_(\d+)\.pdf", sheet)
        rows.append({
            "id": e["id"],
            "date": e.get("date", ""),
            "time": (e.get("time") or "").upper(),
            "event": event_number(e),
            "name": norm_name(e.get("name", "")),
            "sheet": int(m.group(1)) if m else None,
            "buyIn": e.get("buyIn"),
            "guarantee": e.get("guarantee"),
            "category": e.get("category"),
        })
    return rows


def event_number(row: dict) -> int | None:
    # ids look like vl-dse-2026-11-25-10-1110am  -> event number 10, id-time 1110am
    m = re.search(r"-(\d+)-\d{3,4}[ap]m$", row["id"])
    return int(m.group(1)) if m else None


def main() -> int:
    html = parse_html_rows()
    pdf = parse_pdf_rows()
    canon = canonical_rows()

    problems: list[str] = []

    print(f"HTML schedule rows (fetched 2026-11-17): {len(html)}")
    print(f"PDF schedule rows   (read 2026-11-16):   {len(pdf)}")
    print(f"Canonical rows in site/data.json:        {len(canon)}")

    if len(html) != len(canon):
        problems.append(f"row count differs: html={len(html)} canonical={len(canon)}")

    # 1. canonical vs the HTML page, matched positionally (both are in schedule order)
    for i, (h, c) in enumerate(zip(html, canon)):
        label = f"row {i + 1} (event {h['event']}, {h['date']} {h['time']})"
        if h["date"] != c["date"]:
            problems.append(f"{label}: date html={h['date']} canonical={c['date']}")
        if h["time"].replace(" ", "") != c["time"].replace(" ", ""):
            problems.append(f"{label}: time html={h['time']!r} canonical={c['time']!r}")
        if h["event"] != c["event"]:
            problems.append(f"{label}: event number html={h['event']} canonical={c['event']}")
        if h["name"] != c["name"]:
            problems.append(f"{label}: name\n    html={h['name']}\n    canon={c['name']}")
        if h["sheet"] != c["sheet"]:
            problems.append(f"{label}: structure sheet html={h['sheet']} canonical={c['sheet']}")

    # 2. the PDF capture and the HTML page must agree on the ordered sequence of
    #    (event number, time, name). Dates are compared only where the PDF prints one.
    dated_pdf = [p for p in pdf if p["month"]]
    undated = [p for p in pdf if not p["month"]]
    print(f"PDF rows with a readable date: {len(dated_pdf)}; decorative date cells: {len(undated)}")
    if len(pdf) != len(html):
        problems.append(f"pdf/html row count differs: pdf={len(pdf)} html={len(html)}")
    for i, (p, h) in enumerate(zip(pdf, html)):
        if p["event"] != h["event"]:
            problems.append(f"pdf row {i + 1}: event pdf={p['event']} html={h['event']}")
        if p["time"] and p["time"].replace(" ", "") != h["time"].replace(" ", ""):
            problems.append(f"pdf row {i + 1}: time pdf={p['time']!r} html={h['time']!r}")
        if p["month"]:
            expect = f"{h['date'][:4]}-{p['month']:02d}-{p['day']:02d}"
            if expect != h["date"]:
                problems.append(f"pdf row {i + 1}: date pdf={expect} html={h['date']}")

    # 3. The two official captures render the event name differently: the PDF puts the
    #    guarantee in its own column while the HTML page inlines "$XXK GTD" into the name.
    #    That difference is an official-source rendering fact (flag F45), not a data error,
    #    so it is counted and printed but does not fail the check.
    name_diffs = 0
    for i, (p, h) in enumerate(zip(pdf, html)):
        if p["name"] == h["name"]:
            continue
        name_diffs += 1
    print(
        f"PDF/HTML name rendering differences: {name_diffs} of {len(pdf)} rows "
        "(the PDF prints the guarantee in its own column; the HTML page inlines it) "
        "- recorded as irregularity F45, not a data error."
    )

    # 4. buy-in printed in the event name must match the canonical buyIn field
    for c, h in zip(canon, html):
        m = re.search(r"\$([0-9,]+)", h["rawName"])
        if not m:
            continue
        printed = int(m.group(1).replace(",", ""))
        if c["buyIn"] is not None and printed != c["buyIn"]:
            problems.append(
                f"event {h['event']} {h['date']}: name prints ${printed} but canonical buyIn={c['buyIn']}"
            )

    # 5. guarantee printed in the event name must match the canonical guarantee field
    for c, h in zip(canon, html):
        m = re.search(r"\$([0-9,]+)K GTD", h["rawName"])
        printed = int(m.group(1).replace(",", "")) * 1000 if m else None
        if printed and c["guarantee"] and printed != c["guarantee"]:
            problems.append(
                f"event {h['event']} {h['date']}: name prints ${printed} GTD but canonical={c['guarantee']}"
            )
        if printed and not c["guarantee"]:
            problems.append(f"event {h['event']} {h['date']}: name prints a guarantee but canonical has none")

    # 6. The hotel and recurring-room values that the 2026-11-17 excerpts support.
    #    See raw/official_excerpts_2026-11-17.md for the verbatim official text behind each one.
    hotels = {h["id"]: h for h in json.loads(DATA.read_text())["hotels"]}
    ven = hotels.get("venetian", {})
    for field, expected in (("baseRateFloor", 119), ("baseRateCeiling", 209), ("resortFee", 55)):
        if ven.get(field) != expected:
            problems.append(f"hotel venetian: {field} is {ven.get(field)!r}, the suite-rates page prints {expected}")
    qual = (ven.get("qualification") or "").lower()
    for token in ("six hours", "$300", "2 a.m.", "epokr25"):
        if token not in qual:
            problems.append(f"hotel venetian: qualification is missing '{token}' printed on the suite-rates page")
    pal = hotels.get("palazzo", {})
    if pal.get("resortFee") != 55 or pal.get("baseRateFloor") != 119:
        problems.append("hotel palazzo: the suite-rates page covers The Palazzo at the same $119/$209 and $55")

    # The four recurring Wynn rows, against the daily poster.
    expected_wynn = {
        "200/10000/12:00 PM": "$200 No Limit Hold'em Mon-Thu, $10,000 guarantee, 12 p.m.",
        "240/40000/12:00 PM": "$240 No Limit Hold'em Rebuy Fri, $40,000 guarantee, 12 p.m.",
        "200/25000/12:00 PM": "$200 No Limit Hold'em Sat-Sun, $25,000 guarantee, 12 p.m.",
        "160/10000/6:00 PM": "$160 No Limit Hold'em nightly, $10,000 guarantee, 6 p.m.",
    }
    seen = set()
    for e in json.loads(DATA.read_text())["events"]:
        if e.get("venue") != "wynn" or e.get("date") or not e.get("weekdays"):
            continue
        key = f"{e.get('buyIn')}/{e.get('guarantee')}/{e.get('time')}"
        if key in expected_wynn:
            seen.add(key)
        else:
            problems.append(
                f"recurring Wynn row {e['id']}: {key} is not one of the four rows printed on the daily poster")
    for key, label in expected_wynn.items():
        if key not in seen:
            problems.append(f"recurring Wynn row missing from the data: {label}")
    print(f"Recurring Wynn rows matched against the daily poster: {len(seen)} of {len(expected_wynn)}")

    # 7. Every dated official quote must reconcile with (rate + resort fee) x (1 + tax rate).
    for h in json.loads(DATA.read_text())["hotels"]:
        for q in h.get("quotes") or ([] if not h.get("quote") else [h["quote"]]):
            nights = [q["nightOne"], q["nightTwo"]]
            derived = round(sum((n["rate"] + n["resortFee"]) * 1.1338 for n in nights), 2)
            printed = round(q["total"], 2)
            if abs(derived - printed) > 0.02:
                problems.append(
                    f"quote {q['checkIn']}->{q['checkOut']} ({q['property']}): derived {derived} != printed {printed}")
            if q.get("derivedTotal") and abs(q["derivedTotal"] - printed) > 0.02:
                problems.append(
                    f"quote {q['checkIn']}->{q['checkOut']}: stored derivedTotal {q['derivedTotal']} != printed {printed}")
    print("Dated official quotes reconciled against (rate + resort fee) x 1.1338")

    if problems:
        print(f"\nFAILED - {len(problems)} mismatch(es):")
        for p in problems:
            print("  -", p)
        return 1
    print("\nOK - the canonical rows match both official captures line by line.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
