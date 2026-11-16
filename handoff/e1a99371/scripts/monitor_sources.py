#!/usr/bin/env python3
"""Re-fetch every official source URL and record what changed.

Writes:
  monitor/state.json              {url: {hash, firstSeen, lastSeen, lastChanged}}
  monitor/snapshots/<hash>.txt    the text captured for each distinct version
  monitor/report.md               a human-readable diff report, committed

A changed page is a prompt to re-verify by hand, never an automatic overwrite:
the site's data module is only ever edited by a person who has read the new
version of the page.
"""

from __future__ import annotations

import hashlib
import json
import pathlib
import sys
import urllib.request
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parents[1]
MON = ROOT / "monitor"
SNAPS = MON / "snapshots"
STATE = MON / "state.json"
REPORT = MON / "report.md"

TIMEOUT = 45
USER_AGENT = "Mozilla/5.0 (compatible; PokerTripPlanner-SourceMonitor/1.0)"


def fetch(url: str) -> tuple[int, str]:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        raw = resp.read()
    return resp.status, raw.decode("utf-8", errors="replace")


def strip_html(text: str) -> str:
    """Very small normaliser: drop scripts, styles and tags, collapse space."""
    import re

    text = re.sub(r"<script[^>]*>.*?</script>", " ", text, flags=re.S | re.I)
    text = re.sub(r"<style[^>]*>.*?</style>", " ", text, flags=re.S | re.I)
    text = re.sub(r"<!--.*?-->", " ", text, flags=re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"&nbsp;", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def load_sources() -> list[dict]:
    sys.path.insert(0, str(ROOT / "scripts"))
    import poker_data as D  # noqa: E402

    rows = [{"id": s["id"], "label": s["label"], "url": s["url"]} for s in D.SOURCES]

    # Every structure sheet is monitored too, since those carry the rules.
    for n in sorted(D.SHEETS):
        rows.append({
            "id": f"S04-{n}",
            "label": f"DSE IV structure sheet {n} - {D.SHEETS[n]['title']}",
            "url": D.sheet(n),
        })
    return rows


def main() -> int:
    SNAPS.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    state = {}
    if STATE.exists():
        try:
            state = json.loads(STATE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            state = {}

    sources = load_sources()
    changed, failed, unchanged = [], [], []

    for src in sources:
        url = src["url"]
        try:
            status, text = fetch(url)
        except Exception as exc:  # network, DNS, TLS, timeout
            failed.append((src, f"{type(exc).__name__}: {exc}"))
            continue

        body = strip_html(text)
        digest = hashlib.sha256(body.encode("utf-8")).hexdigest()

        (SNAPS / f"{digest}.txt").write_text(body, encoding="utf-8")

        prev = state.get(url)
        if prev is None:
            state[url] = {
                "id": src["id"],
                "label": src["label"],
                "hash": digest,
                "firstSeen": now,
                "lastSeen": now,
                "lastChanged": now,
                "changed": False,
            }
            unchanged.append(src)
        elif prev["hash"] != digest:
            state[url] = {
                "id": src["id"],
                "label": src["label"],
                "hash": digest,
                "firstSeen": prev.get("firstSeen", now),
                "lastSeen": now,
                "lastChanged": now,
                "previousHash": prev["hash"],
                "changed": True,
            }
            changed.append((src, prev["hash"], digest))
        else:
            prev["lastSeen"] = now
            prev["changed"] = False
            unchanged.append(src)

    STATE.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# Source monitoring report",
        "",
        f"Run: {now}",
        f"URLs checked: {len(sources)}",
        f"Changed since last run: {len(changed)}",
        f"Unreachable: {len(failed)}",
        "",
        "A changed page means the stored snapshot differs from the previous one. It is a prompt to",
        "re-read the page by hand - it never edits the site data automatically.",
        "",
        "`monitor/snapshots/` holds the captured text for each distinct version and is not committed;",
        "`monitor/state.json` holds the hash for each URL and is the durable change signal.",
        "",
    ]

    if changed:
        lines += ["## Changed", ""]
        for src, old, new in changed:
            lines.append(
                f"- **{src['id']}** {src['label']}  \n"
                f"  {src['url']}  \n"
                f"  `{old[:12]}` -> `{new[:12]}` (snapshots in `monitor/snapshots/`)"
            )
        lines.append("")

    if failed:
        lines += ["## Unreachable", ""]
        for src, err in failed:
            lines.append(f"- **{src['id']}** {src['label']} - {err}  \n  {src['url']}")
        lines.append("")

    if not changed and not failed:
        lines += ["No page changed and every page was reachable.", ""]

    lines += [
        "## Unchanged",
        "",
        f"{len(unchanged)} URL(s) matched the stored snapshot.",
        "",
    ]

    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"{len(sources)} URLs checked: {len(changed)} changed, "
          f"{len(failed)} unreachable, {len(unchanged)} unchanged.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
