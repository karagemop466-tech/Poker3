#!/usr/bin/env python3
"""Morning daily schedule feed for each Strip poker room.

Run from the repository root:

    python3 scripts/daily_feed.py

For each room with an official target it captures visible page text or a PDF
fingerprint and writes the request outcomes to site/feed/index.json. Dated
text snapshots allow comparing the same URL across runs.

The feed never invents tournament rows.  It records what the official page
contained on the morning it was fetched, which is what makes a change visible.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import pathlib
import re
import ssl
import sys
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
DATA = SITE / "data.json"
FEED = SITE / "feed"

USER_AGENT = "Poker3DailyFeed/1.0 (+https://karagemop466-tech.github.io/Poker3/)"
TIMEOUT = 30

# Additional schedule/rule documents already verified in the official source
# register. These are pointers into the catalog, not a second copy of the URLs.
ROOM_DOCUMENTS = {
    "wynn": ("wynn-sig-sched",),
    "bellagio": ("bell-sat", "bell-sun"),
    "mgm": ("mgm-sched",),
    "caesars": ("caesars-flyer",),
}


def room_targets(data: dict) -> list[dict]:
    sources = {row.get("id"): row.get("url") for row in data.get("sources", [])}
    census = {row["id"]: row for row in data.get("stripRooms", [])}
    targets = []
    for room in data.get("feed", []):
        room_id = room["id"]
        urls = [room["schedule"], *room.get("extra", [])]
        label = room["name"]
        if room_id == "caesars" and census.get("caesars", {}).get("official"):
            # The old combined target is a general article. Retain it for
            # Horseshoe but use the property and its flyer for Caesars Palace.
            if "horseshoe" in census:
                targets.append({"id": "horseshoe", "name": census["horseshoe"]["name"],
                                "urls": [room["schedule"]]})
            urls = [census["caesars"]["official"], *room.get("extra", [])]
            label = census["caesars"]["name"]
        urls.extend(sources.get(key) for key in ROOM_DOCUMENTS.get(room_id, ()))
        targets.append({"id": room_id, "name": label,
                        "urls": list(dict.fromkeys(url for url in urls if url))})
    return targets


# Times and dollar amounts that appear on a published poker schedule page.
TIME_RE = re.compile(r"\b(\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)?)\b")
MONEY_RE = re.compile(r"\$[\d,]+")


def fetch(url: str) -> tuple[int, str, bytes]:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    context = ssl.create_default_context()
    with urllib.request.urlopen(request, timeout=TIMEOUT, context=context) as response:
        return response.status, response.headers.get("Content-Type", ""), response.read()


def visible_text(body: bytes, content_type: str) -> str:
    if "pdf" in content_type.lower() or body.startswith(b"%PDF-"):
        # PDFs are fingerprinted, not transcribed by this job.
        return ""
    raw = body.decode("utf-8", errors="replace")
    raw = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", raw)
    text = re.sub(r"(?s)<[^>]+>", " ", raw)
    text = re.sub(r"&nbsp;?", " ", text)
    text = re.sub(r"&amp;", "&", text)
    return re.sub(r"\s+", " ", text).strip()


def main() -> int:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    rooms = room_targets(data)
    now = dt.datetime.now(dt.timezone.utc).replace(microsecond=0)
    stamp = now.strftime("%Y-%m-%d")
    FEED.mkdir(parents=True, exist_ok=True)

    summary = []
    for room in rooms:
        urls = room["urls"]
        entry = {"id": room["id"], "name": room["name"], "fetched": now.isoformat(), "pages": []}
        for url in urls:
            page = {"url": url}
            try:
                status, ctype, body = fetch(url)
                digest = hashlib.sha256(body).hexdigest()
                page["status"] = f"HTTP {status}"
                if not 200 <= status < 300:
                    page["outcome"] = "unavailable"
                    entry["pages"].append(page)
                    print(f"{page['status']:>14}  {url}")
                    continue
                text = visible_text(body, ctype)
                page["outcome"] = "text" if text else (
                    "pdf-fingerprint" if "pdf" in ctype.lower() or body.startswith(b"%PDF-") else "no-text"
                )
                page["hash"] = digest
                page["bytes"] = len(body)
                page["contentType"] = ctype
                if text:
                    page["textLength"] = len(text)
                    page["times"] = sorted(set(TIME_RE.findall(text)))[:60]
                    page["amounts"] = sorted(set(MONEY_RE.findall(text)))[:60]
                    # One room can publish more than one schedule page (the Venetian
                    # publishes the DSE IV page, the DSE NYE page and the poker-room
                    # page). Each page gets its own dated snapshot, keyed by a short
                    # digest of its URL, so the pages never overwrite one another and
                    # a morning run can be compared with the previous morning per page.
                    slug = hashlib.sha256(url.encode("utf-8")).hexdigest()[:8]
                    snapshot = FEED / f"{room['id']}-{stamp}-{slug}.txt"
                    snapshot.write_text(text, encoding="utf-8")
                    page["snapshot"] = f"feed/{room['id']}-{stamp}-{slug}.txt"
            except urllib.error.HTTPError as exc:
                page["status"] = f"HTTP {exc.code}"
                page["outcome"] = "unavailable"
                page["error"] = str(exc)
            except Exception as exc:  # noqa: BLE001 - one bad page must not stop the feed
                page["status"] = "unreachable"
                page["outcome"] = "unavailable"
                page["error"] = f"{type(exc).__name__}: {exc}"
            entry["pages"].append(page)
            print(f"{page['status']:>14}  {url}")
        summary.append(entry)

    index = {"generated": now.isoformat(), "date": stamp, "rooms": summary}
    (FEED / "index.json").write_text(json.dumps(index, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"\nwrote {FEED / 'index.json'} for {len(rooms)} poker rooms")
    return 0


if __name__ == "__main__":
    sys.exit(main())
