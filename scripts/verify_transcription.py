#!/usr/bin/env python3
"""Cross-check the transcribed official series table against the published rows.

Run from the repository root:

    python3 scripts/verify_transcription.py            # check, write the record
    python3 scripts/verify_transcription.py --quiet    # exit code only

`site/data/venetian_pdf_rows.json` is a hand transcription of the official DeepStack
Extravaganza IV series PDF (`dse-nov-2026-schedule.pdf`), which is the only official
place that prints the REG CLOSES clock time. This script compares that transcription
with `site/data.json` row by row: date, start time, late-registration cut-off,
guarantee, chip count and level length must all agree, and every transcribed row must
still exist in the published data.

It writes its result to `site/checks.json` under the `transcription` key and never
edits a tournament value: a mismatch is a false or drifted published row that a person
must fix at the source module. A match is positive evidence that the page a reader is
looking at still says what the official PDF said on the day it was read.

It needs no network access, so it also runs in the scheduled job and in the sandbox.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
DATA = SITE / "data.json"
CHECKS = SITE / "checks.json"
TRANSCRIPTION = SITE / "data" / "venetian_pdf_rows.json"


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


# --------------------------------------------------------------------------
# Transcription check: the official series PDF, as transcribed by a person,
# against the published rows.
# --------------------------------------------------------------------------
def check_transcription(data: dict) -> dict:
    if not TRANSCRIPTION.exists():
        return {
            "status": "missing",
            "checked": utc_now(),
            "note": "No transcription file was found, so no row was cross-checked "
                    "against the official series PDF in this run.",
            "rows": [], "mismatches": [], "missingInData": [], "extraInData": 0,
        }

    doc = json.loads(TRANSCRIPTION.read_text(encoding="utf-8"))
    events = {e["id"]: e for e in data.get("events", [])}
    rows, mismatches, missing = [], [], []

    for row in doc["rows"]:
        eid = row.get("eventId", "")
        target = events.get(eid)
        problems = []
        if target is None:
            missing.append({"eventId": eid, "reason": "transcribed row is not in site/data.json"})
        else:
            def cmp(field: str, data_field: str, fmt=str):
                want, got = row.get(field, ""), target.get(data_field, "")
                if want in ("", None):
                    return
                if fmt(want) != fmt(got):
                    problems.append(
                        {"field": field, "published": got, "official": want}
                    )

            cmp("date", "date")
            cmp("time", "time")

            def money(v):
                if v in ("", None):
                    return ""
                return int(round(float(str(v).replace(",", "").replace("$", ""))))

            cmp("guarantee", "guarantee", money)
            cmp("chips", "chips", lambda v: int(str(v).replace(",", "")) if str(v) else "")
            cmp("levelMin", "levelMin", lambda v: int(str(v)) if str(v) not in ("", "None") else "")
            cmp("regCloses", "lateRegEnd")

        entry = {
            "eventId": eid,
            "date": row.get("date", ""),
            "event": row.get("event", ""),
            "name": row.get("name", ""),
            "time": row.get("time", ""),
            "regCloses": row.get("regCloses", ""),
            "guarantee": row.get("guarantee", ""),
            "chips": row.get("chips", ""),
            "levelMin": row.get("levelMin", ""),
            "inData": target is not None,
        }
        if problems:
            entry["mismatch"] = problems
            mismatches.append(entry)
        rows.append(entry)

    transcribed_ids = {r.get("eventId") for r in doc["rows"]}
    extra = [eid for eid in events if
             str(events[eid].get("venue")) == "venetian"
             and doc.get("series")
             and str(events[eid].get("date", "")).startswith("2026-11")
             and events[eid]["date"] <= doc.get("through", "")
             and eid not in transcribed_ids]

    return {
        "status": "checked" if not mismatches and not missing else "mismatch",
        "checked": utc_now(),
        "source": doc.get("source", ""),
        "sourceHash": doc.get("sourceHashRecorded", ""),
        "range": f"{doc.get('from', '')} → {doc.get('through', '')}",
        "rowsTranscribed": len(doc["rows"]),
        "rowsMatched": len(doc["rows"]) - len(mismatches) - len(missing),
        "mismatches": mismatches,
        "missingInData": missing,
        "rowsInDataNotTranscribed": len([e for e in extra if e]),
        "note": doc.get("note", ""),
        "rows": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Cross-check the transcription against the published rows.")
    parser.add_argument("--quiet", action="store_true", help="do not print the per-row summary")
    parser.add_argument("--dry-run", action="store_true", help="do not write site/checks.json")
    args = parser.parse_args()

    data = json.loads(DATA.read_text(encoding="utf-8"))
    result = check_transcription(data)
    if not args.quiet:
        print(f"transcription: {result['status']} — {result['rowsMatched']}/{result['rowsTranscribed']} rows match")
        for bad in result["mismatches"]:
            print(f"  MISMATCH {bad['eventId']} {bad.get('name', '')}: {bad['mismatch']}")
        for missing in result["missingInData"]:
            print(f"  MISSING  {missing['eventId']}: {missing['reason']}")

    if not args.dry_run:
        record = {}
        if CHECKS.exists():
            try:
                record = json.loads(CHECKS.read_text(encoding="utf-8"))
            except ValueError:
                record = {}
        record["transcription"] = result
        CHECKS.write_text(json.dumps(record, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        if not args.quiet:
            print(f"wrote the transcription record into {CHECKS}")
    return 0 if result["status"] == "checked" else 1


if __name__ == "__main__":
    sys.exit(main())
