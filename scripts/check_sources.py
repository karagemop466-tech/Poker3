#!/usr/bin/env python3
"""Scheduled re-check of every official URL behind the dashboard.

Run from the repository root:

    python3 scripts/check_sources.py

It fetches each official URL, stores a SHA-256 of the response body and compares
it with the hash recorded in site/checks.json.  A URL whose body changed is
flagged, and the flags are published on the sources page.

The script never changes a tournament value by itself.  A changed page means a
human has to look at the official source again before any number moves, so the
script only records the change and the reason.

Network access is required.  It is designed to run in GitHub Actions; it is
safe to run anywhere with outbound HTTPS.
"""
from __future__ import annotations

import argparse
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
CHECKS = SITE / "checks.json"

HASH_BASIS = ("visible text (HTML tags, scripts and styles removed); the raw-byte hash is kept per URL as hash")
PDF_HASH_BASIS = "PDF raw bytes SHA-256 (conservative review signal, not extracted text)"
USER_AGENT = "Poker3SourceChecker/1.0 (+https://karagemop466-tech.github.io/Poker3/)"
TIMEOUT = 30


def official_targets(data: dict) -> list[dict]:
    """Every official URL the dashboard depends on, with a readable label."""
    out: dict[str, dict] = {}

    def add(url: str, label: str) -> None:
        if url and url.startswith("https://") and url not in out:
            out[url] = {"url": url, "label": label}

    for s in data.get("sources", []):
        add(s["url"], s["name"])
    for sheet in data.get("structureSheets", []):
        add(sheet["url"], f"{sheet['series']} structure sheet {sheet['sheet']}")
    for room in data.get("feed", []):
        add(room["schedule"], f"{room['name']} schedule page")
        for extra in room.get("extra", []):
            add(extra, f"{room['name']} extra source")
    for e in data.get("events", []):
        add(e.get("scheduleUrl", ""), f"Schedule for {e['name']}")
        add(e.get("structureUrl", ""), f"Structure sheet for {e['name']}")
        for rule_name, rule in (e.get("rules") or {}).items():
            if isinstance(rule, dict):
                add(rule.get("source", ""), f"{e['name']} {rule_name} rule")
    for h in data.get("hotels", []):
        for field, label in (
            ("source", "room source"), ("feeSource", "fee terms"), ("taxSource", "tax terms"),
            ("feeSourceAlt", "alternate fee terms"), ("parkingSource", "parking terms"),
            ("cancellationSource", "cancellation terms"), ("bookingUrl", "booking page"),
            ("calendarUrl", "booking calendar"),
        ):
            add(h.get(field, ""), f"{h['name']} {label}")
        quote = h.get("quote") or {}
        add(quote.get("source", ""), f"{h['name']} dated quote")
    for row in data.get("rateLog", []):
        add(row.get("source", ""), f"{row.get('hotel', 'Hotel')} rate observation")
        add(row.get("feeSource", ""), f"{row.get('hotel', 'Hotel')} fee source")
        add(row.get("taxSource", ""), f"{row.get('hotel', 'Hotel')} tax source")
    for route in data.get("routes", []):
        add(route.get("source", ""), f"{route.get('hotel', '')} to {route.get('venue', '')} official address")
    return list(out.values())


def fetch(url: str) -> tuple[int, str, bytes]:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    context = ssl.create_default_context()
    with urllib.request.urlopen(request, timeout=TIMEOUT, context=context) as response:
        return response.status, response.headers.get("Content-Type", ""), response.read()


# HTML scripts/nonces are noise, so HTML is compared on normalized text. PDF
# text normally lives inside compressed streams: stripping streams silently hid
# changes to fees and rules. Compare *all* PDF bytes instead. This deliberately
# over-flags metadata-only changes, which require review but never mutate values.
_SCRIPT_STYLE = re.compile(r"<(script|style|noscript|svg)\b[^>]*>.*?</\1>", re.IGNORECASE | re.DOTALL)
_TAG = re.compile(r"<[^>]+>")
_WS = re.compile(r"\s+")
_ENTITY = {"&nbsp;": " ", "&amp;": "&", "&lt;": "<", "&gt;": ">", "&quot;": '"', "&#39;": "'"}


def is_pdf(body: bytes, content_type: str) -> bool:
    """Accept either a PDF MIME type or its signature (including generic MIME)."""
    return "pdf" in (content_type or "").lower() or body.startswith(b"%PDF")


def comparison_basis(body: bytes, content_type: str) -> str:
    return PDF_HASH_BASIS if is_pdf(body, content_type) else HASH_BASIS


def visible_text(body: bytes, content_type: str) -> str:
    """Normalize HTML text; PDF extraction is deliberately not claimed here."""
    if is_pdf(body, content_type):
        return ""
    html = body.decode("utf-8", errors="ignore")
    html = _SCRIPT_STYLE.sub(" ", html)
    html = _TAG.sub(" ", html)
    for entity, plain in _ENTITY.items():
        html = html.replace(entity, plain)
    return _WS.sub(" ", html).strip().lower()


def content_hash(body: bytes, content_type: str) -> str:
    comparable = body if is_pdf(body, content_type) else visible_text(body, content_type).encode("utf-8")
    return hashlib.sha256(comparable).hexdigest()


# Hosts whose edges return 403/302/timeout to a datacenter runner while serving a normal
# browser. Re-read by hand on 2026-11-17: all 17 affected URLs were reachable and every
# published value behind them was corroborated. A block is an observation about the
# runner, not evidence that a page is gone, so it is recorded separately from a failure.
BOT_BLOCKED_HOSTS = ("caesars.com", "mgmresorts.com")


def classify_outcome(status: str) -> str:
    """Name what actually happened to a request, so a block is not reported as a failure."""
    if status.startswith("HTTP 2"):
        return "fetched"
    if status in ("HTTP 403", "HTTP 401", "HTTP 429"):
        return "blocked"
    if status.startswith("HTTP 3"):
        return "redirected"
    if status == "unreachable":
        return "unreachable"
    return "error"


def compare_check(old: dict | None, status: str, digest: str | None,
                  hash_basis: str = HASH_BASIS) -> dict:
    """Compare like hash bases; a byte change in a PDF is not proof of wording."""
    available = status.startswith("HTTP 2")
    old = old or {}
    prior_raw = old.get("hash")
    prior_text = old.get("textHash") if old.get("hashBasis") == hash_basis else None
    # Earlier runs already stored the complete raw-body digest alongside their
    # flawed PDF text digest. Reuse that valid raw baseline, not the discarded-
    # stream hash: the first fixed run must not miss a changed PDF or reset it.
    prior_hash = prior_raw if hash_basis == PDF_HASH_BASIS else prior_text
    basis_reset = bool(available and prior_raw and not prior_hash)
    changed = bool(available and prior_hash and digest and prior_hash != digest)
    return {
        "changed": changed,
        "wordingChanged": changed and hash_basis == HASH_BASIS,
        "unavailable": not available,
        "baseline": bool(available and not prior_hash),
        "basisReset": basis_reset,
        "previousHash": prior_hash or None,
        "previousTextHash": prior_text if hash_basis == HASH_BASIS else None,
        "previousChecked": old.get("checked", "") or None,
        "statusChanged": bool(old and old.get("status") != status),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Re-check every official URL used by the dashboard.")
    parser.add_argument("--only", default="", help="only check URLs whose label contains this text")
    parser.add_argument("--dry-run", action="store_true", help="do not write site/checks.json")
    args = parser.parse_args()

    data = json.loads(DATA.read_text(encoding="utf-8"))
    previous = {}
    if CHECKS.exists():
        try:
            previous = {u["url"]: u for u in json.loads(CHECKS.read_text(encoding="utf-8")).get("urls", [])}
        except (ValueError, KeyError):
            previous = {}

    targets = official_targets(data)
    if args.only:
        needle = args.only.lower()
        targets = [t for t in targets if needle in t["label"].lower() or needle in t["url"].lower()]

    now = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()
    rows = []
    changed = []
    for target in targets:
        url = target["url"]
        row = {"url": url, "label": target["label"], "checked": now}
        old = previous.get(url)
        try:
            status, ctype, body = fetch(url)
            row["status"] = f"HTTP {status}"
            row["hash"] = hashlib.sha256(body).hexdigest()
            row["bytes"] = len(body)
            row["textHash"] = content_hash(body, ctype)
            row["hashBasis"] = comparison_basis(body, ctype)
            row["comparisonKind"] = "pdf-bytes" if is_pdf(body, ctype) else "html-text"
            if not is_pdf(body, ctype):
                row["textChars"] = len(visible_text(body, ctype))
        except urllib.error.HTTPError as exc:
            row["status"] = f"HTTP {exc.code}"
            row["error"] = str(exc)
        except Exception as exc:  # noqa: BLE001 - the checker must survive one bad URL
            row["status"] = "unreachable"
            row["error"] = f"{type(exc).__name__}: {exc}"

        row["outcome"] = classify_outcome(row["status"])
        row["botBlocked"] = row["outcome"] in ("blocked", "redirected") and any(
            h in row["url"] for h in BOT_BLOCKED_HOSTS)
        row.update(compare_check(old, row["status"], row.get("textHash"),
                                 row.get("hashBasis", HASH_BASIS)))
        # Only comparable, identical HTML text hashes justify calling raw changes
        # noise. A PDF-byte difference is always a review signal, never rawOnly.
        row["rawOnly"] = bool(row.get("hashBasis") == HASH_BASIS
                              and row.get("previousTextHash") == row.get("textHash")
                              and row.get("hash") and (old or {}).get("hash")
                              and row["hash"] != old["hash"] and not row.get("changed"))
        if row["changed"]:
            changed.append(row)
        rows.append(row)
        state = "CHANGED" if row["changed"] else "UNAVAILABLE" if row["unavailable"] else "BASELINE" if row["baseline"] else "unchanged"
        print(f"{row['status']:>14}  {state:>11}  {url}")

    # The sources page reads summary.generatedAt/mode, so publish the same shape the
    # page renders. A later verify_transcription.py run adds the "transcription" key
    # to this same file instead of replacing it.
    fetched = sum(1 for r in rows if str(r.get("status", "")).startswith("HTTP 2"))
    payload = {
        "generatedAt": now,
        "mode": "live fetch",
        "summary": {
            "urls": len(rows),
            "fetched": fetched,
            "changed": len(changed),
            # A URL the runner could not read is recorded honestly: "blocked" when the edge
            # refused a datacenter client (bot protection), "unavailable" for a real error.
            # "failed" is kept as the legacy alias for the total of the two, so existing
            # readers keep working, but the checks page labels them separately.
            "blocked": sum(1 for r in rows if r.get("outcome") in ("blocked", "redirected")),
            "unavailable": sum(1 for r in rows if r.get("outcome") in ("unreachable", "error")),
            "failed": sum(1 for r in rows if r.get("unavailable")),
        },
        "urls": rows,
        "changedCount": len(changed),
        "changed": [r["url"] for r in changed],
        "hashBasis": "Per URL: normalized HTML text or complete PDF bytes; see each row's hashBasis",
        "note": ("Automated re-check of every official URL behind this dashboard. HTML changes compare normalized text. "
                 "PDF changes compare all bytes, including compressed streams; a PDF flag may be metadata-only and "
                 "does not prove a wording or value change. A human must re-read the source before any value is changed. "
                 "Only an HTML raw-body difference with identical comparable text is recorded as noise. "
                 "A 'blocked' row means the venue's edge refused this datacenter runner (HTTP 403/401/429 or a bot "
                 "redirect); it does not mean the page is gone. Those URLs are covered by a manual read, and the last "
                 "manual result is on the Sources page."),
    }
    if CHECKS.exists():
        try:
            previous_payload = json.loads(CHECKS.read_text(encoding="utf-8"))
        except ValueError:
            previous_payload = {}
        if previous_payload.get("transcription"):
            payload["transcription"] = previous_payload["transcription"]
    if not args.dry_run:
        CHECKS.write_text(json.dumps(payload, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"\nwrote {CHECKS} with {len(rows)} URLs, {len(changed)} changed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
