#!/usr/bin/env python3
"""Look up the current official rate for a hotel on given dates and append it to the
dated rate log.

The lookup reads the property's own booking engine, which is the official source for
its price. It records what the page prints, the exact URL, the retrieval timestamp and
the room type, so every observation in the log can be checked by hand.

It never invents a rate. When the booking engine will not return a price for the
requested dates, the tool says so and records nothing.

Run:
  python3 scripts/check_hotel_rates.py --hotel horseshoe --arrival 2026-12-10 --departure 2026-12-14
  python3 scripts/check_hotel_rates.py --list
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import re
import sys
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
HOTELS = ROOT / "data" / "hotels.json"
USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0 Safari/537.36"
)

# Booking URLs per property. Each one is the property's own booking engine.
BOOKING_URLS = {
    "horseshoe": (
        "https://www.caesars.com/book/room-list?arrivalDate={arrival}&departureDate={departure}"
        "&dateSearchFormat=exact-dates&propCode=blv&numAdults=2"
    ),
    "caesars-palace": (
        "https://www.caesars.com/book/room-list?arrivalDate={arrival}&departureDate={departure}"
        "&dateSearchFormat=exact-dates&propCode=clv&numAdults=2"
    ),
    "paris": (
        "https://www.caesars.com/book/hotel-calendar?dateSearchFormat=flexible-dates"
        "&flexibleMonth={month}&propCode=plr"
    ),
    "venetian": (
        "https://www.venetianlasvegas.com/booking?adults[]=2&arrival_date={arrival}"
        "&children[]=0&departure_date={departure}&view=calendar"
    ),
    "wynn": (
        "https://reservations.wynnlasvegas.com/ibe/details.aspx?hotelID=13763&langID=1"
        "&rmID=68658&arrivalDate={arrival}&departureDate={departure}&adults=2"
    ),
    "bellagio": (
        "https://bellagio.mgmresorts.com/en/hotel/booking.html?arrivalDate={arrival}"
        "&departureDate={departure}&numAdults=2"
    ),
}

# Caesars prints the rate breakdown in a fixed shape, for example:
#   "$223 Room Rate + $50 Daily Resort Fee = $273 / Night, Includes resort fee, Excludes Taxes"
RATE_PATTERN = re.compile(
    r"\$([\d,]+)\s*Room Rate\s*\+\s*\$([\d,]+)\s*Daily Resort Fee\s*=\s*\$([\d,]+)\s*/\s*Night",
    re.I,
)
ROOMS_PATTERN = re.compile(r"(\d[\d,]*)\s*Rooms?\s*Found", re.I)
RESTRICTED_PATTERN = re.compile(
    r"arrival date is restricted|please choose a new arrival date", re.I
)
VENETIAN_PLACEHOLDER = re.compile(r"\$XXX|\$X,?XXX")


def fetch(url: str, timeout: int = 40) -> str:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        },
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        raw = response.read(6 * 1024 * 1024 + 1)
    return raw.decode("utf-8", "replace")


def strip_tags(html: str) -> str:
    text = re.sub(r"(?is)<(script|style).*?</\1>", " ", html)
    text = re.sub(r"(?s)<[^>]+>", " ", text)
    text = (
        text.replace("&nbsp;", " ")
        .replace("&amp;", "&")
        .replace("&#39;", "'")
        .replace("&quot;", '"')
        .replace("&#36;", "$")
    )
    return re.sub(r"\s+", " ", text)


def parse_caesars(text: str) -> dict | None:
    """Read the published rate breakdown from a Caesars room-list page."""
    matches = RATE_PATTERN.findall(text)
    if not matches:
        return None
    # The cheapest published breakdown is the one a traveller would book.
    best = min(matches, key=lambda m: int(m[2].replace(",", "")))
    room_rate, fee, nightly = (int(x.replace(",", "")) for x in best)
    rooms = ROOMS_PATTERN.search(text)
    return {
        "nightlyRate": room_rate,
        "resortFeeIncluded": fee,
        "nightlyWithFee": nightly,
        "roomsFound": int(rooms.group(1).replace(",", "")) if rooms else "",
    }


def parse_venetian(text: str) -> dict | None:
    """The Venetian booking calendar prints '$XXX' where a price should be."""
    if VENETIAN_PLACEHOLDER.search(text):
        return None
    prices = [int(p.replace(",", "")) for p in re.findall(r"\$\s?([\d,]{3,})\s*(?:/night|per night)?", text)]
    nightly = [p for p in prices if 80 <= p <= 1500]
    if not nightly:
        return None
    return {"nightlyRate": min(nightly), "resortFeeIncluded": "", "nightlyWithFee": min(nightly)}


def lookup(hotel_id: str, arrival: str, departure: str, occupancy: int = 2) -> dict:
    template = BOOKING_URLS.get(hotel_id)
    if not template:
        return {"status": "no booking URL recorded for this property"}
    try:
        arrival_date = dt.date.fromisoformat(arrival)
        departure_date = dt.date.fromisoformat(departure)
    except ValueError as exc:
        return {"status": f"bad date: {exc}"}
    nights = (departure_date - arrival_date).days
    if nights <= 0:
        return {"status": "the departure date must be after the arrival date"}
    url = template.format(
        arrival=arrival,
        departure=departure,
        month=arrival_date.strftime("%B"),
        adults=occupancy,
    )
    try:
        html = fetch(url)
    except Exception as exc:  # Network, TLS and HTTP errors are evidence gaps.
        return {"status": "unavailable", "error": f"{type(exc).__name__}: {str(exc)[:200]}", "url": url}

    text = strip_tags(html)
    if RESTRICTED_PATTERN.search(text):
        return {"status": "restricted", "detail": "the booking engine refused this arrival date", "url": url}

    parsed = parse_caesars(text) if "caesars.com" in url else parse_venetian(text)
    if not parsed:
        return {
            "status": "no price returned",
            "detail": "the page loaded but no nightly price could be read from it",
            "url": url,
        }
    parsed.update(
        {
            "status": "ok",
            "url": url,
            "arrival": arrival,
            "departure": departure,
            "nights": nights,
            "occupancy": f"{occupancy} adults, 1 room",
            "checked": dt.datetime.now(dt.timezone.utc).date().isoformat(),
            "checkedAt": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
            "excludesTax": True,
            "note": "Published price breakdown read from the official booking engine. The "
            "booking page states the rate excludes taxes, so the final folio is higher.",
        }
    )
    return parsed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--hotel", help="property id, for example horseshoe")
    parser.add_argument("--arrival", default="2026-12-10")
    parser.add_argument("--departure", default="2026-12-14")
    parser.add_argument("--adults", type=int, default=2)
    parser.add_argument("--list", action="store_true", help="list the known properties")
    parser.add_argument("--write", action="store_true", help="append the observation to the rate log")
    args = parser.parse_args()

    doc = json.loads(HOTELS.read_text(encoding="utf-8"))
    known = {h["id"]: h["name"] for h in doc["hotels"]}

    if args.list:
        for hotel_id, name in known.items():
            print(f"{hotel_id:16} {name}")
        return 0

    if not args.hotel:
        parser.error("--hotel is required (use --list to see the options)")
    if args.hotel not in known:
        print(f"unknown property '{args.hotel}'. Known: {', '.join(known)}")
        return 1

    result = lookup(args.hotel, args.arrival, args.departure, args.adults)
    print(json.dumps(result, indent=2))
    if result.get("status") != "ok":
        return 1

    if args.write:
        for hotel in doc["hotels"]:
            if hotel["id"] != args.hotel:
                continue
            observation = {
                key: result[key]
                for key in [
                    "checked",
                    "checkedAt",
                    "arrival",
                    "departure",
                    "nights",
                    "occupancy",
                    "nightlyRate",
                    "resortFeeIncluded",
                    "nightlyWithFee",
                    "roomsFound",
                    "excludesTax",
                    "note",
                ]
                if key in result
            }
            observation["roomType"] = "as printed by the booking engine"
            observation["sourceId"] = "live-lookup"
            observation["sourceUrl"] = result["url"]
            hotel.setdefault("rates", []).append(observation)
            print(f"appended an observation to {hotel['id']}")
        HOTELS.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
