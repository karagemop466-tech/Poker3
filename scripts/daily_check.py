#!/usr/bin/env python3
"""LEGACY / UNUSED. Retired on 2026-11-19; kept only for provenance. Do not schedule it.

The scheduled re-check is scripts/check_sources.py (workflow .github/workflows/checks.yml). The two
tools differ in what they read and where they write:

  * check_sources.py reads the live URL list out of site/data.json, writes site/checks.json, and
    compares HTML on visible text and PDFs on all response bytes (see research/pdf-monitor-2026-11-19.md).
  * this script read the retired 2026-11-16 snapshot site/data/sources.json, wrote
    site/data/changes.json and pruned a snapshots/ directory. It was never referenced by any workflow.

The snapshot it read has been moved to archive/daily_check_sources_2026-11-16.json so that the Pages
artifact no longer publishes a second, stale answer at the live host (flag F101, resolved by this
retirement). If this script is ever revived, point DATA at site/data.json first.

Original docstring follows. Runs on GitHub Actions (full network) every morning. For every URL in
site/data/sources.json:
  * fetch the page/PDF text, normalize it, hash it (sha256)
  * store a dated snapshot under snapshots/<YYYY-MM-DD>/<id>.txt (last 30 days kept)
  * compare with the previous hash in site/data/changes.json
  * mark rows whose source text changed since the last verification

Writes site/data/changes.json (consumed by scripts/build_site.py for monitoring badges)
and prints a short human summary. Exit code 0 always unless a fetch of ALL sources fails.
"""
import hashlib, json, os, re, sys, urllib.request, urllib.error
from datetime import datetime, timezone, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "site", "data")
SNAP = os.path.join(ROOT, "snapshots")
UA = {"User-Agent": "Mozilla/5.0 (compatible; VegasPokerPlanner/1.0; +github.com/karagemop466-tech/Poker3)"}
KEEP_DAYS = 30

def normalize(text):
    return re.sub(r"\s+", " ", text).strip()

def fetch(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=45) as r:
        raw = r.read()
    try:
        return normalize(raw.decode("utf-8", "replace"))
    except Exception:
        return normalize(str(hashlib.sha256(raw).hexdigest()))

def main():
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    with open(os.path.join(DATA, "sources.json")) as f:
        sources = json.load(f)["sources"]
    changes_path = os.path.join(DATA, "changes.json")
    prev = {}
    if os.path.exists(changes_path):
        with open(changes_path) as f:
            prev = {c["id"]: c for c in json.load(f).get("changes", [])}

    snap_dir = os.path.join(SNAP, today)
    os.makedirs(snap_dir, exist_ok=True)
    out, changed, failed = [], [], []
    for s in sources:
        cid = s["id"]
        try:
            text = fetch(s["url"])
            h = hashlib.sha256(text.encode("utf-8")).hexdigest()
            with open(os.path.join(snap_dir, cid + ".txt"), "w") as f:
                f.write(text[:200000])
            p = prev.get(cid, {})
            changed_now = bool(p.get("hash")) and p["hash"] != h
            first = not p.get("hash")
            out.append({
                "id": cid, "name": s["name"], "url": s["url"],
                "lastChecked": today,
                "hash": h,
                "lastChanged": today if (changed_now or first) else p.get("lastChanged", today),
                "changedSinceVerification": changed_now,
                "note": "first baseline" if first else ("source text changed" if changed_now else "no change"),
            })
            if changed_now:
                changed.append(cid)
        except Exception as e:
            failed.append((cid, str(e)[:120]))
            p = prev.get(cid, {})
            out.append({
                "id": cid, "name": s["name"], "url": s["url"],
                "lastChecked": p.get("lastChecked", ""),
                "hash": p.get("hash", ""),
                "lastChanged": p.get("lastChanged", ""),
                "changedSinceVerification": p.get("changedSinceVerification", False),
                "note": "fetch failed: " + str(e)[:120],
            })

    with open(changes_path, "w") as f:
        json.dump({"asOf": today,
                   "summary": {"checked": len(out), "changed": len(changed), "failed": len(failed)},
                   "changedIds": changed,
                   "changes": out}, f, indent=1)

    # prune old snapshots (keep KEEP_DAYS)
    if os.path.isdir(SNAP):
        cutoff = datetime.now(timezone.utc) - timedelta(days=KEEP_DAYS)
        for d in sorted(os.listdir(SNAP)):
            try:
                if datetime.strptime(d, "%Y-%m-%d") < cutoff:
                    dd = os.path.join(SNAP, d)
                    for fn in os.listdir(dd):
                        os.remove(os.path.join(dd, fn))
                    os.rmdir(dd)
            except ValueError:
                pass

    print(f"checked={len(out)} changed={len(changed)} failed={len(failed)}")
    for c in changed:
        print("CHANGED:", c)
    for cid, err in failed:
        print("FAILED:", cid, err)
    if len(failed) == len(sources):
        sys.exit(1)

if __name__ == "__main__":
    main()
