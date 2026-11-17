#!/usr/bin/env python3
"""Morning daily schedule feed for each Strip poker room.

Run from the repository root:

    python3 scripts/daily_feed.py

For every poker room in the canonical data it fetches the official schedule
page, stores a dated snapshot under site/feed/ and writes site/feed/index.json
with the summary.  The snapshot keeps the raw text and a content hash, so a
morning run can be compared with the previous morning instead of replacing it.

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

# Times and dollar amounts that appear on a published poker schedule page.
TIME_RE = re.compile(r"\b(\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)?)\b")
MONEY_RE = re.compile(r"\$[\d,]+")


def fetch(url: str) -> tuple[int, str, bytes]:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    context = ssl.create_default_context()
    with urllib.request.urlopen(request, timeout=TIMEOUT, context=context) as response:
        return response.status, response.headers.get("Content-Type", ""), response.read()


def visible_text(body: bytes, content_type: str) -> str:
    raw = body.decode("utf-8", errors="replace")
    if "pdf" in content_type.lower() or raw[:5] == "%PDF-":
        # A PDF's text is not extracted here; the hash still proves the file is
        # unchanged, and the page it is linked from is captured as well.
        return ""
    raw = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", raw)
    text = re.sub(r"(?s)<[^>]+>", " ", raw)
    text = re.sub(r"&nbsp;?", " ", text)
    text = re.sub(r"&amp;", "&", text)
    return re.sub(r"\s+", " ", text).strip()


def main() -> int:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    rooms = data.get("feed", [])
    now = dt.datetime.now(dt.timezone.utc).replace(microsecond=0)
    stamp = now.strftime("%Y-%m-%d")
    FEED.mkdir(parents=True, exist_ok=True)

    summary = []
    for room in rooms:
        urls = [room["schedule"]] + list(room.get("extra", []))
        entry = {"id": room["id"], "name": room["name"], "fetched": now.isoformat(), "pages": []}
        for url in urls:
            page = {"url": url}
            try:
                status, ctype, body = fetch(url)
                digest = hashlib.sha256(body).hexdigest()
                text = visible_text(body, ctype)
                page["status"] = f"HTTP {status}"
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
                page["error"] = str(exc)
            except Exception as exc:  # noqa: BLE001 - one bad page must not stop the feed
                page["status"] = "unreachable"
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
