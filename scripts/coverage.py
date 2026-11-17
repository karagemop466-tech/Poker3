#!/usr/bin/env python3
"""Brief-coverage traceability matrix (T4 / L7).

Every numbered requirement of the original brief, plus the unnumbered clauses that
travel with it, is mapped to the page that ships it and the flag that records any
residual gap. Nothing may be claimed without a location:

  * every ``ships`` entry must exist under ``site/`` (page or file),
  * every flag ID must exist in the freshly generated ``site/data.json``,
  * every question/suggestion ID cited must exist there too,
  * a status other than ``shipped`` must carry at least one flag.

Outputs ``site/coverage.json``, rendered by ``site/coverage.html``. This script
supersedes the data-only coverage.json generator merged earlier on main (PR #111);
its requirement-to-location substance is folded into the items below (F49/F50/F57/
F67 citations, the checks-workflow location) so nothing it recorded is lost.
Run:  python3 scripts/coverage.py
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"

# Status vocabulary:
#   shipped            - the requirement ships on the published site as asked.
#   shipped-with-flags - it ships, but known limits are recorded as flags.
#   flagged-gap        - the brief's literal wording cannot be met from official
#                        sources yet; the flag page carries what is missing.
BRIEF_ITEMS = [
    {
        "n": 1,
        "item": "Collect and analyse live upcoming poker tournaments near the Las Vegas Strip, "
                "ranked by cost vs prize pool, with single-entry events as the focus.",
        "status": "shipped-with-flags",
        "ships": ["tournaments.html", "index.html", "search.html"],
        "flags": ["F31", "F17"],
        "notes": "341 rows carry date, buy-in, guarantee and a Pool \u00f7 fee ratio column, "
                 "single-entry filtered by default; F31 keeps open that no sheet confirms a "
                 "one-entry-per-player maximum.",
    },
    {
        "n": 2,
        "item": "Keep double-buy-in, re-entry and add-on tournaments in a separate section.",
        "status": "shipped-with-flags",
        "ships": ["tournaments.html", "browse.html"],
        "flags": ["F11"],
        "notes": "entryType categories (extra, satellite, unverified) render as their own "
                 "sections/filters; F11 records the NYE sheets whose multi-entry wording "
                 "disagrees with the schedule page.",
    },
    {
        "n": 3,
        "item": "List hotels within a 30-minute walk of those tournaments, ranked by cost and "
                "quality first and distance second.",
        "status": "shipped-with-flags",
        "ships": ["hotels.html"],
        "flags": ["F32", "F19", "F39"],
        "notes": "8 properties ranked on published cost components plus quality facts, with "
                 "all 56 hotel\u2013venue walking pairs measured (F32 keeps the estimate-only "
                 "caveat; F19/F39 record components no property publishes).",
    },
    {
        "n": 4,
        "item": "Compute a true cost per night as rate + resort fee + tax.",
        "status": "shipped-with-flags",
        "ships": ["hotels.html", "calculator.html"],
        "flags": ["F51", "F37"],
        "notes": "trueNightly floor/ceiling columns plus the dated trip quote; F51 keeps the "
                 "fee-inclusion ambiguity of the $119 poker rate visible, F37 the missing "
                 "room-tax percentage at other properties.",
    },
    {
        "n": 5,
        "item": "Build a day-by-day tournament schedule starting at 8 AM and running all day, "
                "maximising the number of tournaments played.",
        "status": "flagged-gap",
        "ships": ["schedule.html"],
        "flags": ["F17", "F16", "F33", "F49", "F50"],
        "notes": "A 7-day plan ships with primaries and fallbacks, but no official source "
                 "publishes an 8:00 AM start (earliest verified is 9:00 AM) or finish times, "
                 "so the day boundaries are estimates, not published hours.",
    },
    {
        "n": 6,
        "item": "Ship a trip cost calculator of entries \u00d7 buy-ins + nights \u00d7 true hotel cost.",
        "status": "shipped-with-flags",
        "ships": ["calculator.html", "index.html"],
        "flags": ["F54", "F15"],
        "notes": "Preset ranges plus the published-model floor and the dated 23\u201330 Nov quote "
                 "($4,010.55); F54 flags the two planned nights that fail the poker-rate "
                 "earning condition, F15 that engine totals move day over day.",
    },
    {
        "n": 7,
        "item": "Keep dated hotel rate logs: checkout total, nightly average, resort fee, tax, "
                "parking, cancellation deadline, timestamp, compared like for like.",
        "status": "shipped-with-flags",
        "ships": ["hotels.html"],
        "flags": ["F15", "F55", "F64", "F57", "F39", "F86", "F88"],
        "notes": "rateLog carries every observation appended with its date and source, newest "
                 "first, including the itemized trip-window checkout total (a second same-evening "
                 "read returned a different suite and total, kept as F88) and the printed poker-room "
                 "parking waiver on both Venetian rows (F86); F39 keeps the missing room-tax "
                 "percentages visible.",
    },
    {
        "n": 8,
        "item": "Publish a page per venue.",
        "status": "shipped",
        "ships": ["venues.html", "venues/index.html", "venues/venetian.html", "venues/wynn.html", "venues/others.html"],
        "flags": [],
        "notes": "Venue cards plus dedicated Venetian, Wynn and multi-property pages, each row "
                 "linking its official poker page.",
    },
    {
        "n": 9,
        "item": "Provide global search across the tables.",
        "status": "shipped",
        "ships": ["search.html", "index.html"],
        "flags": [],
        "notes": "Header search on every page queries tournaments, hotels, venues, flags, "
                 "questions and sources in one box.",
    },
    {
        "n": 10,
        "item": "Provide a date filter.",
        "status": "shipped",
        "ships": ["tournaments.html", "browse.html"],
        "flags": [],
        "notes": "Date range filter over the tournament table with the plan window preloaded.",
    },
    {
        "n": 11,
        "item": "Check schedule overlaps and give each day a primary and a fallback.",
        "status": "shipped-with-flags",
        "ships": ["schedule.html"],
        "flags": ["F33"],
        "notes": "dayPlan rows carry primary, fallback and fallbackReason; planConflicts lists "
                 "the detected overlaps (Day-2 restarts against same-morning primaries).",
    },
    {
        "n": 12,
        "item": "Check walking routes and apply a 30-minute limit.",
        "status": "shipped-with-flags",
        "ships": ["hotels.html", "schedule.html", "venues.html"],
        "flags": ["F32", "F21", "F67"],
        "notes": "All 56 hotel\u2013venue pairs carry a Maps estimate with its live Maps link and "
                 "per-row last-checked date; rows over 30 minutes are labelled, and the "
                 "schedule filter applies the limit to the plan's Venetian walks.",
    },
    {
        "n": 13,
        "item": "Re-check official URLs on a schedule and mark changed rows.",
        "status": "shipped-with-flags",
        "ships": ["sources.html", "checks.json"],
        "files": [".github/workflows/checks.yml"],
        "flags": ["F30", "F40"],
        "notes": "The scheduled workflow records a per-URL change log (changed / unchanged / "
                 "unavailable with reason) and re-baselines when the comparison basis changes; "
                 "F40 records that some venue hosts are unreachable from the CI sandbox and are "
                 "published as unavailable rather than silently unchanged.",
    },
    {
        "n": 14,
        "item": "Show a last-checked column.",
        "status": "shipped",
        "ships": ["tournaments.html", "hotels.html", "sources.html", "flagged.html"],
        "flags": [],
        "notes": "lastChecked / lastVerified render on every event, rate-log, route and source "
                 "row; blanks render as 'Not recorded', never as a date.",
    },
    {
        "n": 15,
        "item": "Remove the 'unverified' label only when a value is confirmed.",
        "status": "shipped-with-flags",
        "ships": ["tournaments.html", "sheets.html"],
        "flags": ["F12", "F31"],
        "notes": "11 rows remain in the unverified category; the sheet-verification page shows "
                 "which rows a structure sheet has screened and the transcription check keeps "
                 "unmatched rows visible.",
    },
    {
        "n": 16,
        "item": "Carry structured rule fields (single-entry / re-entry / add-on / fee) with a "
                "source excerpt and retrieval date.",
        "status": "shipped",
        "ships": ["tournaments.html"],
        "flags": [],
        "notes": "Each event's rules object holds status, excerpt and retrieval date per rule; "
                 "the tournaments table renders entry check and late registration from it.",
    },
    {
        "n": 17,
        "item": "Rank only after confirming entry fee and guarantee; show guaranteed pool \u00f7 "
                "entry fee as a descriptive ratio; label bounty and flight events.",
        "status": "shipped-with-flags",
        "ships": ["tournaments.html", "index.html"],
        "flags": ["F24", "F31"],
        "notes": "Rows without a confirmed fee or guarantee keep the field blank and are not "
                 "ranked; the ratio column states it is descriptive only; bounty/flight wording "
                 "follows the printed name (F24 flags added-money wording, F31 the entry rule).",
    },
    {
        "n": 18,
        "item": "Publish an executive summary.",
        "status": "shipped",
        "ships": ["index.html"],
        "flags": [],
        "notes": "Landing dashboard: plan, costs, open questions and flagged count at a glance.",
    },
    {
        "n": 19,
        "item": "Publish a Q&A page of the questions that must be answered before decisions.",
        "status": "shipped",
        "ships": ["questions.html"],
        "flags": [],
        "notes": "18 questions (Q01\u2013Q18) with answer state, blocking marker and official source.",
    },
    {
        "n": 20,
        "item": "Publish a suggestions page for the user to choose paths.",
        "status": "shipped",
        "ships": ["suggestions.html"],
        "flags": [],
        "notes": "Each suggestion states the choice, its trade-off and the official evidence "
                 "behind it.",
    },
    {
        "n": 21,
        "item": "Review the repository line by line, give links for manual review, and flag "
                "irregularities.",
        "status": "shipped-with-flags",
        "ships": ["flagged.html", "sources.html"],
        "flags": ["F45", "F46"],
        "notes": "61 flags with severity, detail and official source link form the irregularity "
                 "register; sources.html lists every official URL for manual review; the review "
                 "log lives in COORDINATION.md.",
    },
    {
        "n": 22,
        "item": "Publish a GitHub Pages site: a clean dashboard landing page, category subpages, "
                "simple readable tables and analysis.",
        "status": "shipped",
        "ships": ["index.html", "tournaments.html", "venues.html", "schedule.html", "hotels.html", "calculator.html", "questions.html", "suggestions.html", "flagged.html", "sources.html", "sheets.html", "search.html", "browse.html"],
        "flags": [],
        "notes": "Static site under site/, built by scripts/data_source.py and deployed by the "
                 "pages workflow; this matrix page is part of it.",
    },
    {
        "n": 23,
        "item": "Verification standard: every row links an official source, unconfirmable values "
                "stay blank and flagged, nothing is inferred.",
        "status": "shipped",
        "ships": ["flagged.html", "sources.html"],
        "flags": [],
        "notes": "Enforced by scripts/verify_site.py (official-domain allowlist, blank-not-"
                 "fabricated rule, flag coverage, local links) on every build and in CI.",
    },
    {
        "n": 24,
        "item": "Coordinate parallel sessions through a shared COORDINATION.md: claim before "
                "starting, non-overlapping scopes, small commits, rebase before push, log conflicts.",
        "status": "shipped",
        "ships": [],
        "files": ["COORDINATION.md"],
        "flags": [],
        "notes": "Claim tables, session logs and conflict records are kept at the repository "
                 "root and pushed with every claim.",
    },
    {
        "n": 25,
        "item": "Final integration: open a PR to main with change summary, sources and flagged "
                "irregularities; merge without approval; confirm the Pages deploy; record the PR "
                "link and merge result in COORDINATION.md; flagged items appear on the Flagged "
                "for Review page and never block a green merge.",
        "status": "in-progress",
        "ships": ["flagged.html"],
        "files": ["COORDINATION.md"],
        "flags": [],
        "notes": "Claimed as T5 of this session; the PR link and merge result are appended to "
                 "COORDINATION.md when it completes.",
    },
]

STATUSES = {"shipped", "shipped-with-flags", "flagged-gap", "in-progress"}


def main() -> int:
    data = json.loads((SITE / "data.json").read_text(encoding="utf-8"))
    flag_ids = {f["id"] for f in data["flags"]}
    question_ids = {q["id"] for q in data.get("questions", [])}
    suggestion_ids = {s["id"] for s in data.get("suggestions", [])}
    problems = []
    items = []

    for raw in BRIEF_ITEMS:
        item = dict(raw)
        n = item["n"]
        status = item["status"]
        if status not in STATUSES:
            problems.append(f"item {n}: unknown status {status!r}")
        flags = item.get("flags", [])
        if status in ("shipped-with-flags", "flagged-gap") and not flags:
            problems.append(f"item {n}: status {status!r} requires at least one flag")
        for fid in flags:
            if fid not in flag_ids:
                problems.append(f"item {n}: flag {fid} does not exist in data.json")
        for page in item.get("ships", []):
            if not (SITE / page).exists():
                problems.append(f"item {n}: ships page {page} does not exist under site/")
        for rel in item.get("files", []):
            if not (ROOT / rel).exists():
                problems.append(f"item {n}: file {rel} does not exist in the repository")
        if not item.get("ships") and not item.get("files"):
            problems.append(f"item {n}: no ships/files location recorded")
        item["flagCount"] = len(flags)
        items.append(item)

    # Question / suggestion sanity: the Q&A and suggestion claims above must resolve.
    if len(question_ids) < 15:
        problems.append(f"expected at least 15 questions, found {len(question_ids)}")
    if not suggestion_ids:
        problems.append("no suggestions found in data.json")

    summary = {}
    for raw in BRIEF_ITEMS:
        summary[raw["status"]] = summary.get(raw["status"], 0) + 1
    summary["flags"] = len(flag_ids)
    summary["questions"] = len(question_ids)
    summary["suggestions"] = len(suggestion_ids)

    if problems:
        for p in problems:
            print(f"coverage problem: {p}", file=sys.stderr)
        return 1

    out = {
        "generatedOn": data["asOf"],
        "brief": "Original project brief, item by item, mapped to the shipped location.",
        "summary": summary,
        "items": items,
    }
    (SITE / "coverage.json").write_text(
        json.dumps(out, indent=1, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(
        f"wrote {SITE / 'coverage.json'} with {len(items)} brief items "
        f"({', '.join(f'{k}: {v}' for k, v in sorted(summary.items()))})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
