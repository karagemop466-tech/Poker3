#!/usr/bin/env python3
"""Line-by-line audit of the canonical data against the read log.

research/structure_notes.md holds the table of every DSE IV structure PDF that
was opened, with the values that were read off each sheet.  This script parses
that table and compares it, row by row, with the values the canonical data
module carries.  A mismatch is a transcription error and has to be fixed in the
data module, not in the notes.

Run:  python3 scripts/audit_data.py
"""
from __future__ import annotations

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import data_venetian as V  # noqa: E402

NOTES = ROOT / "research" / "structure_notes.md"


def money(text: str):
    """Read a dollar or plain thousands-separated number from a table cell."""
    text = text.strip()
    m = re.match(r"^\$?([\d,]+)\s*(?:\D|$)", text)
    return int(m.group(1).replace(",", "")) if m else None


def guarantee_key(text: str) -> str:
    """Compare guarantees by amount and by whether bounties are included."""
    text = (text or "").strip()
    if not text or text.lower().startswith("not printed"):
        return ""
    amount = money(text)
    bounty = "bount" in text.lower()
    return f"{amount}|bounty={bounty}"


def parse_notes() -> dict[int, dict]:
    rows = {}
    for line in NOTES.read_text(encoding="utf-8").splitlines():
        if not line.startswith("| ") or line.startswith("|---"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 11 or not cells[0].isdigit():
            continue
        rows[int(cells[0])] = dict(
            title=cells[1], events=cells[2], buy_in=money(cells[3]), rake=money(cells[4]),
            pool=money(cells[5]), chips=money(cells[6]), level=cells[7], late=cells[8],
            guarantee=cells[9], rules=cells[10])
    return rows


def main() -> int:
    notes = parse_notes()
    if len(notes) != 37:
        print(f"expected 37 sheets in the read log, found {len(notes)}")
        return 1
    problems = []
    for sheet, n in sorted(notes.items()):
        s = V.SHEETS.get(sheet)
        if not s:
            problems.append(f"sheet {sheet}: missing from the data module")
            continue
        if s["buyIn"] != n["buy_in"]:
            problems.append(f"sheet {sheet}: buy-in {s['buyIn']} != read log {n['buy_in']}")
        if s["rake"] != n["rake"]:
            problems.append(f"sheet {sheet}: rake {s['rake']} != read log {n['rake']}")
        if s["pool"] != n["pool"]:
            problems.append(f"sheet {sheet}: prize pool {s['pool']} != read log {n['pool']}")
        extra = s.get("extraFee", 0)
        if s["rake"] + s["pool"] + extra != s["buyIn"]:
            problems.append(f"sheet {sheet}: rake + pool + flat fee {s['rake'] + s['pool'] + extra} "
                            f"!= buy-in {s['buyIn']}")
        if s["chips"] != n["chips"]:
            problems.append(f"sheet {sheet}: chips {s['chips']} != read log {n['chips']}")
        if s["levelMin"] != int(re.match(r"(\d+)", n["level"]).group(1)):
            problems.append(f"sheet {sheet}: level length {s['levelMin']} != read log {n['level']}")
        if s["late"] != n["late"]:
            problems.append(f"sheet {sheet}: late registration {s['late']!r} != read log {n['late']!r}")
        if guarantee_key(s["guarantee"]) != guarantee_key(n["guarantee"]):
            problems.append(f"sheet {sheet}: guarantee {s['guarantee']!r} != read log {n['guarantee']!r}")

    # every scheduled DSE row must point at a sheet that was read
    for date, time, no, name, sheet, guarantee, category in V.DSE_ROWS:
        if sheet not in V.SHEETS:
            problems.append(f"{date} event {no}: sheet {sheet} is not in the read log")
            continue
        s = V.SHEETS[sheet]
        if s["buyIn"] != money(name.split("No Limit")[0].split("PLO")[0].split("NLH")[0].strip()) and \
                not name.upper().startswith(("$" + str(s["buyIn"]))):
            problems.append(f"{date} event {no}: name {name!r} does not start with the sheet buy-in ${s['buyIn']}")
        if guarantee not in ("", s["guarantee"]) and str(guarantee) not in s["guarantee"].replace(",", ""):
            problems.append(f"{date} event {no}: guarantee {guarantee} not found on sheet {sheet} ({s['guarantee']})")
        if s["kind"] == "flight" and category != "flight":
            problems.append(f"{date} event {no}: multi-flight sheet categorised as {category!r}")
        if s["kind"] != "flight" and category == "flight":
            problems.append(f"{date} event {no}: non-flight sheet categorised as flight")

    print(f"audited {len(notes)} structure sheets against {len(V.DSE_ROWS)} scheduled DSE rows")
    if problems:
        print(f"\n{len(problems)} mismatch(es):")
        for p in problems:
            print(" -", p)
        return 1
    print("audit passed: every sheet value matches the read log")
    return 0


if __name__ == "__main__":
    sys.exit(main())
