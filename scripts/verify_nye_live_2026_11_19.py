#!/usr/bin/env python3
"""Verify every published DeepStack NYE row against the 2026-11-19 live capture.

Run from the repository root:

    python3 scripts/verify_nye_live_2026_11_19.py

The capture is `raw/venetian_dse_nye_live_2026-11-19_7d96049f.md`, a dated transcription of the
visible text of https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-dec-2026.html
read on 2026-11-19. That page is the only official source for the 49 Venetian New Year's Eve rows in
`site/data.json`, and those rows were the last group in the catalog still stamped with the 2026-11-17
read date.

Fields compared, because they are the fields the page itself prints:

    date, start time, event number, event name, printed buy-in, printed guarantee, structure-sheet number

Rows are matched on the page's own identity — date + start time + Event # — so a re-ordered or
duplicated schedule row is caught instead of silently re-aligned.

A resumption row ("Day 2 Restart", "Day 3 Restart") prints no guarantee of its own, and a satellite
prints none at all. A guarantee the page cannot supply is never inferred: the resumption rows are
checked against the guarantee printed on the same Event # in this same capture, and a satellite with
no printed guarantee must have a blank one in the catalog.

This script never edits data. It fails loudly when a published row disagrees with the dated capture,
so the catalog and its evidence cannot drift apart.

Note on the year: three December 26 rows print "2025" on the official page. The capture records the
series-correct 2026-12-26 in its Date column and explains why (the row's own weekday label "Saturday"
matches 2026-12-26, not 2025-12-26). The printed-year defect is flagged on the site as F04/F41; it is
not silently corrected in the data.
"""
from __future__ import annotations

import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
CAPTURE = ROOT / "raw" / "venetian_dse_nye_live_2026-11-19_7d96049f.md"
DATA = ROOT / "site" / "data.json"
PAGE_URL = ("https://www.venetianlasvegas.com/resort/casino/poker/"
            "deepstack-extravaganza-poker-tournament/dse-dec-2026.html")

ROW = re.compile(
    r"^\|\s*(\d+)\s*\|\s*(\d{4}-\d{2}-\d{2})\s*\|\s*([^|]+?)\s*\|\s*(\d+)\s*\|\s*([^|]+?)\s*\|\s*(\d+)\s*\|\s*$"
)
RESTART = re.compile(r"Day \d Restart", re.I)


def norm(s: str) -> str:
    """Fold only what the reader and the catalog style differently, never a value.

    The official page puts the subtitle after a `<br>`, spells "Event # 08" with a space and
    capitalises inconsistently ("RAKE DISCOUNT" against the catalog's "rake discount"). The catalog
    writes the same subtitle with commas. Folding case, whitespace and punctuation keeps every digit
    and word intact, so a real change to a name, an amount or an event number still fails.
    """
    s = s.replace("<br>", " ").replace("&amp;", "&")
    return re.sub(r"[^0-9a-z$%]+", "", s.lower(), flags=re.I)


def printed_amount(text: str, guarantee: bool = False) -> int | None:
    """Read a printed dollar amount out of the event name.

    The page prints no buy-in column and no guarantee column, so the buy-in is the first ``$n`` the
    name begins with and the guarantee is the ``$nK GTD`` token inside it. Both are quoted numbers,
    never computed; when the token is absent the answer is None and the field stays blank.
    """
    if guarantee:
        m = re.search(r"\$([\d,]+)\s*(K|Mill|Million)?\s*GTD", text, re.I)
    else:
        m = re.match(r"\$([\d,]+)", text.strip())
    if not m:
        return None
    value = int(m.group(1).replace(",", ""))
    unit = (m.group(2) or "").lower() if m.re.groups >= 2 else ""
    if unit.startswith("k"):
        value *= 1000
    elif unit.startswith("mill"):
        value *= 1_000_000
    return value


def read_capture(path: pathlib.Path = CAPTURE) -> list[dict]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        m = ROW.match(line.strip())
        if m:
            rows.append(dict(n=int(m.group(1)), date=m.group(2), time=m.group(3).strip(),
                             event=int(m.group(4)), name=m.group(5).strip(), sheet=int(m.group(6))))
    return rows


def published() -> list[dict]:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    out = []
    for e in data["events"]:
        if e.get("scheduleUrl") != PAGE_URL:
            continue
        m = re.search(r"-(\d+)-(\d{3,4})(am|pm)$", e["id"])
        out.append(dict(id=e["id"], date=e["date"], time=e["time"], name=e["name"],
                        buyIn=e.get("buyIn"), guarantee=e.get("guarantee"),
                        sheetUrl=e.get("sheetUrl") or "", category=e.get("category"),
                        isContinuation=bool(e.get("isContinuation")),
                        event=int(m.group(1)) if m else None,
                        lastChecked=e.get("lastChecked"), lastVerified=e.get("lastVerified")))
    return out


def key(row: dict) -> tuple:
    """The page's own identity for a row: its date, its start time and its Event # column."""
    return (row["date"], row["time"].upper(), row["event"])


def main() -> int:
    cap = read_capture()
    pub = published()
    problems: list[str] = []

    if len(cap) != 49:
        problems.append(f"capture has {len(cap)} rows, expected the 49 the page printed")
    if len(pub) != len(cap):
        problems.append(f"catalog has {len(pub)} DeepStack NYE rows, capture has {len(cap)}")

    index: dict[tuple, list[dict]] = {}
    for p in pub:
        index.setdefault(key(p), []).append(p)
    for k, rows in index.items():
        if len(rows) > 1:
            problems.append(f"catalog holds {len(rows)} rows for {k}; the page prints one")

    seen = []
    inherited = 0
    no_guarantee = 0
    # A resumption row carries its event's guarantee: the guarantee printed on the starting flights
    # of the same Event # in this same capture. Built from the non-resumption rows only.
    by_event: dict[int, set] = {}
    for c in cap:
        if not RESTART.search(c["name"]):
            g = printed_amount(c["name"], guarantee=True)
            if g is not None:
                by_event.setdefault(c["event"], set()).add(g)

    for c in cap:
        rows = index.get(key(c), [])
        if not rows:
            problems.append(f"capture row {c['n']} ({c['date']} {c['time']} event {c['event']}) "
                            "has no matching catalog row")
            continue
        p = rows[0]
        seen.append(p["id"])
        if f"structure_{c['sheet']}.pdf" not in p["sheetUrl"]:
            problems.append(f"row {c['n']}: sheet {p['sheetUrl']} != capture structure_{c['sheet']}.pdf")
        if norm(c["name"]) != norm(p["name"]):
            problems.append(f"row {c['n']}: name\n    catalog: {p['name']}\n    capture: {c['name']}")
        fee = printed_amount(c["name"])
        if fee is None or fee != p["buyIn"]:
            problems.append(f"row {c['n']}: buy-in {p['buyIn']} != printed {fee}")
        gtd = printed_amount(c["name"], guarantee=True)
        pub_g = p["guarantee"] if isinstance(p["guarantee"], int) else None
        if gtd is not None:
            if gtd != pub_g:
                problems.append(f"row {c['n']}: guarantee {pub_g} != printed {gtd}")
        elif RESTART.search(c["name"]):
            parents = by_event.get(c["event"], set())
            if not parents:
                problems.append(f"row {c['n']}: resumption row has no event #{c['event']} guarantee in "
                                "this capture to check against")
            elif pub_g not in parents:
                problems.append(f"row {c['n']}: resumption guarantee {pub_g} is not the guarantee "
                                f"printed on event #{c['event']} flights {sorted(parents)}")
            elif not p["isContinuation"]:
                problems.append(f"row {c['n']}: the page prints a Day-N restart but catalog row "
                                f"{p['id']} is not marked as a continuation")
            else:
                inherited += 1
        elif pub_g is not None:
            problems.append(f"row {c['n']}: catalog prints a ${pub_g:,} guarantee the page does not print")
        else:
            no_guarantee += 1

    missing = [p["id"] for p in pub if p["id"] not in set(seen)]
    if missing:
        problems.append(f"catalog rows not printed by the capture: {missing}")

    for msg in problems:
        print("FAIL:", msg)
    if problems:
        return 1
    print(f"verified all {len(cap)} published DeepStack NYE rows against the 2026-11-19 live capture "
          f"(date, start time, event number, printed name, printed buy-in, printed guarantee and "
          f"structure-sheet link); {inherited} resumption rows carry their event's printed guarantee, "
          f"{no_guarantee} satellite rows print no guarantee and carry none")
    return 0


if __name__ == "__main__":
    sys.exit(main())
