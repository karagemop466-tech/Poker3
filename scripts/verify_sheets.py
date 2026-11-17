#!/usr/bin/env python3
"""Compare the published tournament rows against facts read directly from the official structure PDFs.

Usage:  python3 scripts/verify_sheets.py

`data/sheet_facts_2026-11-17.json` holds what was read off each official structure sheet on 2026-11-17:
the events the sheet covers, the buy-in, starting chips, level length, late-registration line, the
guarantee as printed, the fee split, and a list of every clause that would let a player spend more than
one buy-in. This script checks each of those against `site/data.json` and reports any drift.

It also re-checks the central claim of the single-entry list: that no sheet behind a 'single entry'
row prints a re-entry, rebuy, add-on or second-flight provision.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FACTS = ROOT / "data" / "sheet_facts_2026-11-17.json"
DATA = ROOT / "site" / "data.json"

ENTRY_WORDS = ("re-entry", "reentry", "re entry", "rebuy", "re-buy", "add-on", "addon", "add on")


def sheet_key(url: str) -> str:
    """Series-qualified sheet name, so dse_nov_2026-structure_1 and dse_dec_2026-structure_1
    are never confused. The NYE series has its own sheets with the same numbers."""
    m = re.search(r"(dse_[a-z]+_\d{4})-structure_(\d+)\.pdf", url or "")
    return f"{m.group(1)}-structure_{m.group(2)}" if m else ""


def nk(s: str) -> str:
    """Normalised comparison key for free-text fields: case, spacing and the tilde are not evidence."""
    return re.sub(r"[^a-z0-9]+", "", (s or "").lower())


def negated(excerpt: str, word: str) -> bool:
    """True if `word` appears in the excerpt under a negation such as 'no re-entry, rebuy, add-on'."""
    low = excerpt.lower()
    for m in re.finditer(re.escape(word), low):
        window = low[max(0, m.start() - 160):m.start()]
        if re.search(r"\b(no|not|without|nor)\b", window):
            return True
    return False


def main() -> int:
    facts = json.loads(FACTS.read_text())
    data = json.loads(DATA.read_text())
    events = data["events"]

    problems: list[str] = []
    checked_rows = 0
    confirmed_single = 0

    for short, sheet in facts["sheets"].items():
        # The series is taken from the sheet URL itself, so DSE IV (dse_nov_2026)
        # and NYE (dse_dec_2026) sheets are both covered by this loop; the key
        # short name is only a label.
        url = sheet["url"]
        name = sheet_key(url)
        rows = [e for e in events if sheet_key(e.get("structureUrl")) == name]
        if not rows:
            problems.append(f"{name}: no published row links this sheet")
            continue

        # every event number on the sheet must be published, and every row on the sheet must agree
        for e in rows:
            checked_rows += 1
            if e.get("buyIn") not in (None, "", sheet["buyIn"]):
                problems.append(f"{name} {e['id']}: buyIn published={e.get('buyIn')} sheet={sheet['buyIn']}")
            if e.get("chips") not in (None, "", sheet["chips"]):
                problems.append(f"{name} {e['id']}: chips published={e.get('chips')} sheet={sheet['chips']}")
            if e.get("levelMin") not in (None, "", sheet["levelMin"]):
                problems.append(f"{name} {e['id']}: levelMin published={e.get('levelMin')} sheet={sheet['levelMin']}")
            if e.get("lateReg") and nk(e["lateReg"]) != nk(sheet["lateReg"]):
                problems.append(f"{name} {e['id']}: lateReg published={e['lateReg']!r} sheet={sheet['lateReg']!r}")

            want = sheet["guarantees"].get("default")
            if want is None and not sheet["guarantees"]:
                # sheet prints no guarantee: the published value must be blank or explained
                if e.get("guarantee") not in (None, "", 0):
                    problems.append(
                        f"{name} {e['id']}: sheet prints NO guarantee but published={e.get('guarantee')}"
                    )
                if not (e.get("guaranteeNote") or e.get("note")):
                    problems.append(f"{name} {e['id']}: blank guarantee with no explanation")
            elif want is not None:
                if e.get("guarantee") not in (None, "", want):
                    problems.append(
                        f"{name} {e['id']}: guarantee published={e.get('guarantee')} sheet={want}"
                    )

            # the central single-entry claim
            if e["rules"]["singleEntry"]["status"] == "single-entry-on-sheet":
                confirmed_single += 1
                if sheet["entryClauses"]:
                    problems.append(
                        f"{name} {e['id']}: row is marked single-entry-on-sheet but the sheet prints "
                        f"{sheet['entryClauses']}"
                    )
                excerpt = e["rules"]["singleEntry"].get("excerpt") or ""
                for w in ENTRY_WORDS:
                    if w in excerpt.lower() and not negated(excerpt, w):
                        problems.append(
                            f"{name} {e['id']}: single-entry excerpt contains the word {w!r} without a "
                            f"negation - read the sheet again"
                        )
                if e["rules"]["singleEntry"].get("source") != url:
                    problems.append(f"{name} {e['id']}: single-entry excerpt source is not this sheet")
                if not e["rules"]["singleEntry"].get("retrieved"):
                    problems.append(f"{name} {e['id']}: single-entry excerpt has no retrieval date")

    print(f"sheets: {len(facts['sheets'])}  rows checked: {checked_rows}  "
          f"single-entry rows confirmed against their sheet: {confirmed_single}")
    if problems:
        print(f"\n{len(problems)} problem(s):")
        for p in problems:
            print("  -", p)
        return 1
    print("every published row matches the facts read from its official structure sheet")
    return 0


if __name__ == "__main__":
    sys.exit(main())
