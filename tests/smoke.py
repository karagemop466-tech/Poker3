#!/usr/bin/env python3
"""Dependency-free smoke checks for the Poker3 static site."""
from __future__ import annotations

import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site/poker3"


class LocalAssetParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.paths: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_map = dict(attrs)
        for key in ("href", "src"):
            value = attrs_map.get(key)
            if not value or value.startswith(("#", "//", "mailto:", "tel:", "data:")):
                continue
            if urlparse(value).scheme:
                continue
            self.paths.append(value.split("#", 1)[0].split("?", 1)[0])


def main() -> None:
    data_path = SITE / "data/research.json"
    data = json.loads(data_path.read_text(encoding="utf-8"))
    assert data["meta"]["asOf"] == "2026-11-16"
    assert data["meta"]["sampleStay"]["arrival"] == "2026-12-10"
    assert data["meta"]["sampleStay"]["departure"] == "2026-12-14"

    source_ids = {source["id"] for source in data["sources"]}
    assert len(source_ids) == len(data["sources"]), "source IDs must be unique"
    for source in data["sources"]:
        assert source["url"].startswith("https://"), source["id"]
    for collection in ("events", "rooms", "hotels", "flags"):
        for item in data[collection]:
            for source_id in item.get("sourceIds", []):
                assert source_id in source_ids, f"missing {source_id} in {collection}"
    for route in data["routes"]:
        assert route.get("sourceId") in source_ids, f"missing route source for {route.get('from')} → {route.get('to')}"

    assert data["events"], "event snapshot must not be empty"
    assert all(event["strictStatus"] in {"verified", "rejected", "unverified"} for event in data["events"])
    assert sum(event["strictStatus"] == "verified" for event in data["events"]) == 0
    assert any("up to three entries" in event["reason"] for event in data["events"])
    assert any("unlimited re-entry" in event["reason"] for event in data["events"])

    pages = [
        "index.html", "schedule.html", "plan.html", "rooms.html", "stay.html",
        "routes.html", "review.html", "methodology.html",
    ]
    for page in pages:
        path = SITE / page
        assert path.is_file(), f"missing page: {page}"
        parser = LocalAssetParser()
        parser.feed(path.read_text(encoding="utf-8"))
        for local in parser.paths:
            if local:
                assert (path.parent / local).is_file(), f"{page} points to missing local path: {local}"
        assert 'id="main-content"' in path.read_text(encoding="utf-8")

    js = (SITE / "assets/app.js").read_text(encoding="utf-8")
    assert "fetch(dataUrl" in js
    assert not re.search(r"https?://(?:localhost|127\.0\.0\.1)", js), "browser code must not call localhost"
    assert (SITE / "assets/app.css").is_file()
    assert (SITE / "index.html").is_file()
    assert 'href="site/poker3/"' in (ROOT / "index.html").read_text(encoding="utf-8"), "legacy root homepage must link to the companion"
    assert 'href="poker3/"' in (ROOT / "site/index.html").read_text(encoding="utf-8"), "Actions-published homepage must link to the companion"
    print(
        f"OK · {len(pages)} pages · {len(data['events'])} selected event starts · "
        f"{len(data['rooms'])} rooms · {len(data['hotels'])} hotels · "
        f"{len(data['sources'])} source records · 0 strict-entry passes"
    )


if __name__ == "__main__":
    main()
