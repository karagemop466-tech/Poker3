#!/usr/bin/env python3
"""Rebuild the canonical site snapshot from reviewed local source extracts.

No network access is performed. The Venetian schedule rows come from the checked-in
verbatim extraction/parser output; source silence remains unverified, never eligible.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
AS_OF = "2026-11-16"
VEN_PAGE = "https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html"
VEN_PDF = "https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_{}.pdf"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def money(value):
    return f"${int(value):,}" if isinstance(value, (int, float)) and value is not None else ""


def source(sid: str, name: str, url: str, kind: str = "official source", monitor: bool = True):
    return {"id": sid, "name": name, "url": url, "kind": kind, "checked": AS_OF, "monitor": monitor}


def evidence(status: str, url: str, excerpt: str = "", note: str = ""):
    return {"status": status, "source": url, "excerpt": excerpt, "retrievedAt": AS_OF, "note": note}


def structure_for(row: dict) -> str | None:
    number = str(row["event_no"])
    name = row["name"].upper()
    flight = re.search(r"\b1([A-F])\b", name)
    day = flight.group(1) if flight else ""
    fixed = {
        "2": 5, "3": 18, "4": 18, "5": 18, "6": 29, "7": 2, "8": 30,
        "9": 1, "10": 6, "11": 1, "12": 5, "13": 1, "14": 7, "15": 1,
        "16": 11, "17": 26, "18": 8, "19": 3, "20": 22, "21": 1, "22": 1,
        "23": 1, "24": 17, "25": 1, "27": 28, "28": 7, "29": 15, "30": 11,
        "31": 15, "32": 17, "33": 19, "34": 15, "35": 31, "36": 16, "37": 19,
        "38": 15, "39": 32, "40": 27, "41": 24, "42": 15, "43": 33, "44": 24,
        "45": 25, "46": 25, "48": 25, "49": 20, "50": 15, "51": 15, "52": 34,
        "53": 15, "54": 11, "55": 15, "57": 23, "58": 8, "59": 4, "60": 1,
        "61": 1, "62": 1, "63": 7, "64": 1,
    }
    if number == "1":
        sheet = 10 if day in ("A", "C") else 9
    elif number == "26":
        sheet = 14 if day == "F" else (13 if day in ("B", "D") else 12)
    elif number == "47":
        sheet = 37 if day == "B" else 21
    elif number == "56":
        sheet = 36 if day in ("B", "D") else 35
    else:
        sheet = fixed.get(number)
    return VEN_PDF.format(sheet) if sheet else None


def tags_for(name: str) -> list[str]:
    text = name.lower()
    tags = []
    flight = re.search(r"\b1([a-f])\b", text)
    if flight:
        tags.append("multi-flight")
    if "bount" in text or "pko" in text:
        tags.append("bounty")
    if "satellite" in text:
        tags.append("satellite")
    if "seniors" in text or "50+" in text:
        tags.append("age-restricted")
    if "ladies" in text or "lips" in text:
        tags.append("women-only-or-lips")
    if "tag team" in text:
        tags.append("team-format")
    if "pokeratlas pro" in text or "rake discount" in text:
        tags.append("conditional-rake-discount")
    if "(1day)" in text:
        tags.append("one-day-format")
    return tags


def build_venetian(row: dict) -> dict:
    name = row["name"].strip()
    structure_url = structure_for(row)
    basis = structure_url or VEN_PAGE
    tags = tags_for(name)
    flight = re.search(r"\b1([A-F])\b", name, re.I)
    fmt = f"Multi-flight · Day 1{flight.group(1).upper()}" if flight else ("Satellite" if "satellite" in name.lower() else ("One day" if "(1DAY)" in name.upper() else "Scheduled start"))
    single_text = "The official schedule/structure does not establish one total entry per player."
    rules = {
        "singleEntry": evidence("unknown", basis, "", single_text),
        "reEntry": evidence("not-stated", basis, "", "No event-specific re-entry statement was confirmed in this snapshot."),
        "rebuy": evidence("not-stated", basis, "", "No event-specific rebuy statement was confirmed in this snapshot."),
        "addOn": evidence("not-stated", basis, "", "No event-specific add-on statement was confirmed in this snapshot."),
        "paidChipAdvantage": evidence("not-stated", basis, "", "No event-specific paid-chip-advantage statement was confirmed in this snapshot."),
        "flights": evidence("multiple" if flight else "single-listed-start", VEN_PAGE, name, "Flight label is printed; it does not establish a total event-entry cap." if flight else "One schedule row does not establish a one-entry limit."),
        "bounty": evidence("yes" if "bount" in name.lower() or "pko" in name.lower() else "no", VEN_PAGE, name, "Bounty/PKO appears in the official event name." if "bount" in name.lower() or "pko" in name.lower() else "No bounty label appears in the official event name."),
    }
    if "satellite" in name.lower():
        rules["satellite"] = evidence("yes", VEN_PAGE, name, "The official event is a satellite; it is kept separate from cash-guarantee comparisons.")
    buy_in = row.get("buy_in")
    guarantee_text = row.get("guarantee_text") or ""
    event_id = f"venetian-{row['date']}-{row['event_no']}-{re.sub(r'[^0-9]', '', row['time'])}"
    date_status = "printed" if row.get("date_source") == "printed" else "inferred-from-row-order"
    source_ids = ["venetian-series"]
    if structure_url:
        match = re.search(r"structure_(\d+)", structure_url)
        if match:
            source_ids.append(f"venetian-structure-{match.group(1)}")
    if date_status != "printed":
        date_note = row.get("date_source", "Date inferred from schedule row order.")
    else:
        date_note = "Date printed in the official schedule."
    fee_excerpt = f"Event #{row['event_no']}: {name} · {row['time']} · {money(buy_in)}"
    guarantee_status = "confirmed" if row.get("guarantee") else ("seat-award" if "seat" in guarantee_text.lower() else "not-published")
    return {
        "id": event_id,
        "date": row["date"],
        "dateISO": row["date"],
        "dateEvidence": evidence(date_status, VEN_PAGE, row.get("weekday_printed") or "", date_note),
        "time": row["time"],
        "registrationCloses": row.get("reg_closes") or "",
        "eventNumber": row["event_no"],
        "venue": "The Venetian",
        "venueId": "venetian",
        "event": name,
        "buyIn": money(buy_in),
        "entryFeeUsd": buy_in,
        "entryFeeConfirmed": buy_in is not None,
        "entryFeeEvidence": evidence("confirmed" if buy_in is not None else "unverified", VEN_PAGE, fee_excerpt, "Published headline entry amount, not a verified cap on total spend."),
        "guarantee": guarantee_text,
        "guaranteeUsd": row.get("guarantee"),
        "guaranteeConfirmed": bool(row.get("guarantee")),
        "guaranteeBasis": "published total guarantee; bounty allocation may be included" if row.get("guarantee") and "bount" in name.lower() else ("seat-award, not a cash guarantee" if guarantee_status == "seat-award" else ("published tournament guarantee" if row.get("guarantee") else "not published")),
        "guaranteeEvidence": evidence(guarantee_status, VEN_PAGE, guarantee_text, "Numeric guarantee is a published event figure; no cash-pool inference is made." if row.get("guarantee") else ("Schedule lists a seat award, not a cash guarantee." if guarantee_status == "seat-award" else "No numeric guarantee is printed for this row.")),
        "format": fmt,
        "tags": tags,
        "bucket": "review",
        "strictStatus": "unverified",
        "entryStatus": "Not verified as one entry total with no re-entry, rebuy, add-on, or paid chip advantage.",
        "rules": rules,
        "schedule": VEN_PAGE,
        "scheduleLabel": "Official Venetian schedule",
        "structure": structure_url or "",
        "confirmSource": VEN_PAGE,
        "sourceIds": source_ids,
        "chips": row.get("chips"),
        "levels": row.get("levels") or "",
        "lastChecked": AS_OF,
        "ratioEligible": False,
    }


def main() -> None:
    data = load(SITE / "data.json")
    parsed = load(ROOT / "data/venetian_flights.json")
    sources = data.get("officialSources", [])
    for item in sources:
        item.setdefault("checked", AS_OF)
        item.setdefault("monitor", True)
        if item["id"] == "wynn-expired-offer":
            item["name"] = "Wynn expired 2025 promotional terms (historical; not current fee evidence)"
            item["kind"] = "historical expired promotion"
            item["monitor"] = False
        if "booking search" in item.get("kind", ""):
            item["monitor"] = False
    def ensure(sid, name, url, kind="official source", monitor=True):
        match = next((s for s in sources if s.get("url") == url), None)
        if match:
            match["monitor"] = bool(match.get("monitor", True) and monitor)
            return match["id"]
        sources.append(source(sid, name, url, kind, monitor))
        return sid
    ensure("venetian-series", "Venetian DeepStack Extravaganza IV schedule", VEN_PAGE, "official tournament schedule")
    for number in range(1, 38):
        url = VEN_PDF.format(number)
        ensure(f"venetian-structure-{number}", f"Venetian official structure sheet #{number}", url, "official structure PDF")
    extra_sources = [
        ("wynn-daily-structures", "Wynn daily tournament structures and terms", "https://cdn.wynnresorts.com/image/upload/v1752011191/visitwynn_pdfs_files/Poker/Daily%20Tournaments/Poker-All_Daily_Structures.pdf", "official structure PDF", True),
        ("wynn-wpt-schedule", "Wynn WPT festival schedule", "https://cdn.wynnresorts.com/image/upload/v1757097329/visitwynn_pdfs_files/Poker/WPT/WPT_World_Championship_Schedule.pdf", "official schedule PDF", True),
        ("wynn-wpt-structures", "Wynn WPT structure sheets and terms", "https://cdn.wynnresorts.com/image/upload/v1750864036/visitwynn_pdfs_files/Poker/WPT/WPT_World_Championship_Structures.pdf", "official structure PDF", True),
        ("wpt-press", "WPT festival announcement and featured-event terms", "https://www.worldpokertour.com/article/wpt-world-championship-at-wynn-las-vegas-set-for-season-24-finale-with-over-85-events-and-20m-in-gte/", "official event terms", True),
        ("wpt-festival-schedule", "WPT official festival schedule PDF", "https://wptmedia-mig.s3.amazonaws.com/wp-content/uploads/2026/09/WPT-World-Championship-Festival-Schedule-Season-24.pdf", "official schedule PDF", True),
        ("wynn-resort-info", "Wynn current resort fee and hotel information", "https://www.wynnlasvegas.com/about-us/resort-information", "official hotel terms", True),
        ("venetian-poker-parking", "Venetian Poker Room parking fees and play-based parking terms", "https://www.venetianlasvegas.com/resort/casino/poker/player-parking.html", "official parking terms", True),
        ("mgm-parking", "MGM Resorts hotel-guest parking terms", "https://www.mgmresorts.com/en/things-to-do/parking.html", "official parking terms", True),
        ("bellagio-terms", "Bellagio hotel terms, resort fee and cancellation", "https://bellagio.mgmresorts.com/en/terms-and-conditions.html", "official hotel terms", True),
        ("aria-terms", "ARIA hotel terms, resort fee and cancellation", "https://aria.mgmresorts.com/en/terms-and-conditions.html", "official hotel terms", True),
        ("mgm-grand-terms", "MGM Grand hotel terms, resort fee and cancellation", "https://mgmgrand.mgmresorts.com/en/terms-and-conditions.html", "official hotel terms", True),
        ("treasure-island-cancellation", "Treasure Island official cancellation terms", "https://treasureisland.com/hotel/best-rate-guarantee", "official hotel terms", True),
        ("treasure-island-faq", "Treasure Island official hotel parking FAQ", "https://treasureisland.com/hotel-faqs", "official hotel FAQ", True),
        ("horseshoe-hotel", "Horseshoe Las Vegas hotel and cancellation summary", "https://www.caesars.com/horseshoe-las-vegas/hotel", "official hotel page", True),
    ]
    for record in extra_sources:
        ensure(*record)

    non_venetian = [r for r in data["tournaments"] if r.get("venueId") != "venetian" and r.get("venue") != "The Venetian"]
    venetian = [build_venetian(row) for row in parsed]
    rows = sorted(non_venetian + venetian, key=lambda r: (r.get("dateISO") or "9999", r.get("time") or "", r.get("venue", ""), r.get("id", "")))
    # Give every old row a stable metadata envelope and refresh the source-index references.
    source_ids = {s["url"]: s["id"] for s in sources}
    for row in rows:
        row.setdefault("strictStatus", "unverified")
        row.setdefault("tags", [])
        row.setdefault("dateISO", row.get("date", "") if re.fullmatch(r"20\d\d-\d\d-\d\d", str(row.get("date", ""))) else "")
        row.setdefault("venueId", "other")
        row.setdefault("lastChecked", AS_OF)
        row.setdefault("rules", {})
        row["sourceIds"] = list(dict.fromkeys(row.get("sourceIds", []) + [source_ids[url] for url in (row.get("schedule"), row.get("structure"), row.get("confirmSource")) if url and url in source_ids] + [source_ids[x["source"]] for x in list(row["rules"].values()) + [row.get("entryFeeEvidence", {}), row.get("guaranteeEvidence", {})] if x.get("source") in source_ids]))
        row["ratioEligible"] = False
        if row.get("venueId") == "venetian":
            row["strictStatus"] = "unverified"
            row["bucket"] = "review"
            row["entryFeeConfirmed"] = row.get("entryFeeUsd") is not None
            row["guaranteeConfirmed"] = row.get("guaranteeUsd") is not None
            row["ratioEligible"] = False
        elif row.get("rules", {}).get("singleEntry", {}).get("status") == "confirmed":
            allowed = all(row["rules"].get(key, {}).get("status") in ("not-allowed", "not-allowed-per-flight") for key in ("reEntry", "rebuy")) and all(row["rules"].get(key, {}).get("status") in ("not-allowed", "none") for key in ("addOn", "paidChipAdvantage"))
            row["strictStatus"] = "verified" if allowed else "unverified"
        elif row.get("bucket") == "conflict":
            row["strictStatus"] = "conflict"
        elif any(row.get("rules", {}).get(key, {}).get("status") in ("allowed", "available") for key in ("reEntry", "rebuy", "addOn", "paidChipAdvantage")):
            row["strictStatus"] = "rejected"
        else:
            row["strictStatus"] = "unverified"

    # Hotel rows keep room price and totals blank; only published fee and policy facts are populated.
    hotel_records = {h["id"]: h for h in data["hotels"]}
    fee_source = {
        "venetian": "https://www.venetianlasvegas.com/resort/resort-fee.html",
        "palazzo": "https://www.venetianlasvegas.com/resort/resort-fee.html",
        "wynn": "https://www.wynnlasvegas.com/about-us/resort-information",
        "bellagio": "https://bellagio.mgmresorts.com/en/terms-and-conditions.html",
        "aria": "https://aria.mgmresorts.com/en/terms-and-conditions.html",
        "mgm-grand": "https://mgmgrand.mgmresorts.com/en/terms-and-conditions.html",
        "treasure-island": "https://treasureisland.com/hotel/deluxe-rooms",
        "horseshoe": "https://www.caesars.com/horseshoe-las-vegas/hotel",
    }
    policies = {
        "venetian": (55, 55, 13.38, None, "13.38% Clark County room tax applies to room rate; resort fee is plus applicable tax.", "Hotel self-parking: $20 per day; actual use optional.", "Date/rate-specific cancellation terms not confirmed in reviewed source."),
        "palazzo": (55, 55, 13.38, None, "13.38% Clark County room tax applies to room rate; resort fee is plus applicable tax.", "Hotel self-parking: $20 per day; actual use optional.", "Date/rate-specific cancellation terms not confirmed in reviewed source."),
        "wynn": (55, 55, None, None, "Room tax rate not recorded in reviewed current terms.", "Self-parking for registered guests included in resort fee for up to two vehicles; offer terms can vary.", "Use cancellation terms attached to the exact booked rate; a valid sample quote was not returned."),
        "bellagio": (55, 55, None, 50, "Lodging tax applies to room rate, resort fee, and extra-occupant charges; rate not recorded.", "MGM registered hotel-guest self parking: $20 per 24 hours; terms/events may change rates.", "First-night deposit refundable with cancellation at least 72 hours before arrival unless offer differs."),
        "aria": (55, 55, None, 50, "Lodging tax applies to room rate, resort fee, and extra-occupant charges; rate not recorded.", "MGM registered hotel-guest self parking: $20 per 24 hours; terms/events may change rates.", "First-night deposit refundable with cancellation at least 72 hours before arrival unless offer differs."),
        "mgm-grand": (50, 50, None, 40, "Lodging tax applies to room rate, resort fee, and extra-occupant charges; rate not recorded.", "MGM registered hotel-guest self parking: $20 per 24 hours; terms/events may change rates.", "First-night deposit refundable with cancellation at least 72 hours before arrival unless offer differs."),
        "treasure-island": (49.95, 49.95, None, None, "Tax rate not recorded in reviewed official terms; qualifying offers may make resort fee optional.", "Registered hotel guests receive free self and valet parking.", "First-night room-and-tax deposit refundable only if cancelled more than 72 hours before 3 p.m. on arrival; exclusions apply."),
        "horseshoe": (None, None, None, None, "No current resort-fee amount or tax treatment verified in the reviewed official terms.", "Self-parking and valet are available; guest charge not verified.", "Official page advertises free cancellation at least 48 hours before check-in; rate terms control."),
    }
    for hotel in data["hotels"]:
        old = hotel_records.get(hotel["id"], hotel)
        fee, fee_usd, tax, extra, tax_notes, parking, cancel = policies[hotel["id"]]
        hotel.update(old)
        hotel["baseRate"] = ""
        hotel["trueNightly"] = ""
        hotel["checkoutTotalUsd"] = None
        hotel["nightlyAverageUsd"] = None
        hotel["resortFeeUsdPerNight"] = fee_usd
        hotel["resortFeeTaxRateKnown"] = tax is not None
        hotel["roomTaxRateKnown"] = tax is not None
        hotel["roomTaxRatePercent"] = tax
        hotel["resortFeeTaxRatePercent"] = tax
        hotel["extraOccupantUsdPerPersonNight"] = extra
        parking_rates = {"venetian": 20, "palazzo": 20, "wynn": None, "bellagio": 20, "aria": 20, "mgm-grand": 20, "treasure-island": 0, "horseshoe": None}
        hotel["parkingUsdPerVehicleNight"] = parking_rates[hotel["id"]]
        hotel["parkingIncludedVehicleLimit"] = 2 if hotel["id"] == "wynn" else 0
        parking_sources = {
            "venetian": "https://www.venetianlasvegas.com/resort/casino/poker/player-parking.html",
            "palazzo": "https://www.venetianlasvegas.com/resort/casino/poker/player-parking.html",
            "wynn": "https://www.wynnlasvegas.com/about-us/resort-information",
            "bellagio": "https://www.mgmresorts.com/en/things-to-do/parking.html",
            "aria": "https://www.mgmresorts.com/en/things-to-do/parking.html",
            "mgm-grand": "https://www.mgmresorts.com/en/things-to-do/parking.html",
            "treasure-island": "https://treasureisland.com/hotel-faqs",
            "horseshoe": "https://www.caesars.com/horseshoe-las-vegas/hotel",
        }
        hotel["parkingSource"] = parking_sources[hotel["id"]]
        hotel["parkingPolicyNote"] = "Poker-room players with 3+ hours of tournament or cash play may receive complimentary self-parking for that day; confirm qualification with a supervisor." if hotel["id"] in ("venetian", "palazzo") else ""
        hotel["resortFeePolicy"] = "May be optional under a specific qualifying offer; confirm the booked rate." if hotel["id"] == "treasure-island" else ("Not verified from reviewed official terms." if fee is None else "Published per-night fee; tax and any offer-specific waiver must be confirmed.")
        hotel["extraOccupantPolicy"] = "Published per-person, per-night fee applies above two occupants per room." if extra is not None else ("Additional occupancy terms not verified; enter an official rate if the stay exceeds two occupants per room." if hotel["id"] != "wynn" else "Room-type / occupancy terms vary; confirm the booked offer.")
        hotel["resortFee"] = f"${fee:,.2f}/night + tax" if fee is not None else "Not verified"
        hotel["taxes"] = tax_notes
        hotel["parking"] = parking
        hotel["cancellation"] = cancel
        hotel["source"] = old.get("source") or "https://www.venetianlasvegas.com/resort/casino/poker/suite-rates.html"
        hotel["feeSource"] = fee_source[hotel["id"]]
        hotel["taxSource"] = fee_source[hotel["id"]]
        hotel["lastChecked"] = AS_OF
        hotel["status"] = "No comparable date-matched checkout total; do not rank."
        hotel["qualityNote"] = hotel.get("qualityNote") or "Not scored: no like-for-like official quality measure was verified."

    data["schemaVersion"] = 2
    data["asOf"] = AS_OF
    data["scope"] = "Full 83-row Venetian DeepStack Extravaganza IV schedule extraction through Dec. 23, 2026, plus selected Wynn/WPT, Wynn recurring, Bellagio and ARIA leads. This is not a complete Las Vegas inventory. Entry-rule silence is never freezeout proof."
    data["scheduleCoverage"] = {"venueId": "venetian", "listedRows": len(venetian), "eventNumbers": len({r["eventNumber"] for r in venetian}), "firstDate": min(r["dateISO"] for r in venetian), "lastDate": max(r["dateISO"] for r in venetian), "inferredDateRows": sum(r["dateEvidence"]["status"] != "printed" for r in venetian), "sourceId": "venetian-series"}
    data["sampleStay"] = {"arrival": "2026-12-10", "departure": "2026-12-14", "nights": 4, "occupancy": {"rooms": 1, "adults": 2, "children": 0}, "userProvided": False, "label": "Working research sample only; not travel dates supplied by the user."}
    data["tournaments"] = rows
    data["officialSources"] = sources
    flags = data.get("flags", [])
    if not any(flag.get("id") == "wynn-expired-offer" for flag in flags):
        flags.append({"id": "wynn-expired-offer", "severity": "medium", "title": "Wynn historical $50 fee offer is expired", "finding": "A Wynn offer/terms page reviewed for the earlier fee discrepancy was limited to a 2025 stay period. It is retained as historical context only; the current resort-information source states $55 plus tax. The fee on a future booking is controlled by the exact room offer.", "nextStep": "Use the resort fee and parking terms attached to the actual dated reservation; do not use the expired offer as a current rate.", "sourceIds": ["wynn-resort-info", "wynn-expired-offer"]})
    if not any(flag.get("id") == "venetian-date-inference" for flag in flags):
        flags.append({"id": "venetian-date-inference", "severity": "low", "title": "Some Venetian parsed dates rely on omitted-date row order", "finding": "Thirteen extracted schedule rows have a date reconstructed from the preceding printed date and the sequence of start times. Those rows are marked individually; the official schedule page is linked for direct confirmation.", "nextStep": "Recheck each marked row against the live official schedule before relying on a travel or registration date.", "sourceIds": ["venetian-series"]})
    data["flags"] = flags
    (SITE / "data.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    logs = []
    log_results = {
        "venetian": ("placeholder", "Official Dec. 10–14 calendar showed $XXX placeholders; no usable room quote.", "Calendar indicates resort fee included and tax excluded."),
        "palazzo": ("placeholder", "Shared Venetian/Palazzo calendar showed placeholders; no tower-specific quote.", "Calendar indicates resort fee included and tax excluded."),
        "wynn": ("date-mismatch", "The response displayed Nov. 16–17, not the requested Dec. 10–14 stay; displayed price excluded.", "No valid date-matched rate-plan cancellation terms captured."),
        "bellagio": ("not-quoted", "No date-matched direct checkout total captured.", "First-night deposit terms are subject to the exact offer."),
        "aria": ("not-quoted", "No date-matched direct checkout total captured.", "First-night deposit terms are subject to the exact offer."),
        "mgm-grand": ("not-quoted", "No date-matched direct checkout total captured.", "First-night deposit terms are subject to the exact offer."),
        "treasure-island": ("not-quoted", "Promotional starting price is not a quote for the exact four-night stay.", "Offer-specific cancellation terms may differ from the general 72-hour policy."),
        "horseshoe": ("booking-error", "Dated Caesars search returned a technical-difficulties message and zero rooms.", "Hotel page says free cancellation 48 hours before check-in; rate-specific terms control."),
    }
    for h in data["hotels"]:
        status, result, cancellation = log_results[h["id"]]
        fee = h.get("resortFeeUsdPerNight")
        logs.append({"id": h["rateLogId"], "hotelId": h["id"], "hotel": h["name"], "arrival": "2026-12-10", "departure": "2026-12-14", "nights": 4, "occupancy": {"rooms": 1, "adults": 2, "children": 0}, "roomType": "", "searchedAt": AS_OF, "timePrecision": "Date recorded; exact time not recorded.", "source": h.get("bookingSource") or h["source"], "status": status, "result": result, "roomSubtotalUsd": None, "roomTaxUsd": None, "resortFeeUsdPerNight": fee, "resortFeeTotalBeforeTaxUsd": round(fee * 4, 2) if fee is not None else None, "resortFeeTaxUsd": None, "parkingTotalUsd": None, "otherMandatoryFeesUsd": None, "checkoutTotalUsd": None, "nightlyAverageUsd": None, "allInComparable": False, "cancellationTerms": cancellation, "notes": "Research sample only, not user-provided travel dates. No missing price, tax or total is estimated."})
    logs_path = SITE / "data/hotel-rate-logs.json"
    logs_path.parent.mkdir(parents=True, exist_ok=True)
    logs_path.write_text(json.dumps({"schemaVersion": 1, "asOf": AS_OF, "sampleStay": data["sampleStay"], "logs": logs}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    monitor_path = SITE / "data/source-monitor.json"
    if not monitor_path.exists():
        monitor_path.write_text(json.dumps({"schemaVersion": 1, "lastRun": None, "changedCount": 0, "failureCount": 0, "changes": [], "failures": [], "sources": {}}, indent=2) + "\n", encoding="utf-8")
    print(f"Rebuilt {len(rows)} events ({len(venetian)} Venetian starts), {len(sources)} official sources, and {len(logs)} hotel rate-search records.")
    print(f"Date coverage: {data['scheduleCoverage']['firstDate']}–{data['scheduleCoverage']['lastDate']}; inferred Venetian dates: {data['scheduleCoverage']['inferredDateRows']}; strict passes: {sum(r['strictStatus'] == 'verified' for r in rows)}")


if __name__ == "__main__":
    main()
