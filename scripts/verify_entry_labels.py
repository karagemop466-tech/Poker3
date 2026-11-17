#!/usr/bin/env python3
"""Label-integrity check: no published label may claim more than its own excerpt says.

This exists because the repository has already been bitten twice by the same class of
defect: a row was placed in the single-entry candidate list, or given a status, while the
excerpt quoted underneath it said something weaker or the opposite (F75: a NYE row quoted
"the initial entry or any subsequent re-entry" and still sat in the candidate list; F76: WPT
rows said "entry rules not yet read" while quoting the entry rule).  A third instance
appeared on the hotel side (F86): the recommended hotel published a paid parking figure
while omitting the waiver the venue prints for poker-room players, so its row was not
like-for-like with the Wynn row, which carried its own benefit.

The checks are deliberately syntactic.  They compare a label with the text quoted beneath
it and with the document that text was taken from; they never decide whether a venue's rule
is good or bad, and they never fill in a value.  Anything they cannot support is left blank
and flagged, which is the rule the whole site follows.

Run:  python3 scripts/verify_entry_labels.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from verify_site import official  # the repository's own official-host test  # noqa: E402

DATA = ROOT / "site" / "data.json"
CAPTURE = ROOT / "raw" / "venetian_player_parking_2026-11-17_4fbf8168.md"

RULE_KEYS = ("singleEntry", "reEntry", "addOn", "rebuy", "fee")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

# The one label in the register that is a *screen*, not a confirmation.
SCREEN = "single-entry-on-sheet"
# Statuses that report the absence of a provision, or that refuse to say.  None of them
# may carry an excerpt that affirmatively sells an extra entry.
NOTHING_PRINTED = {"none-printed", "not-applicable", "not-verified", "separate-flights",
                   "source-conflict", "one-flight-cap", ""}

# What a written per-player entry cap has to look like before the site may say "confirmed".
CAP_LANGUAGE = re.compile(
    r"(?:one|1)\s+(?:total\s+)?entr(?:y|ies)\s+per\s+(?:player|person)"
    r"|maximum\s+of\s+(?:one|1)\s+(?:total\s+)?entr"
    r"|single\s+entr(?:y|ies)\s+per\s+player"
    r"|\bno\s+re-?bui(?:y|s)\b|\bno\s+re-?entr(?:y|ies)\b"
    r"|\bno\s+add-?ons?\b|\bfreeze-?out\b",
    re.I,
)
# Wording that offers the player another entry, i.e. "gain an advantage by spending more".
AFFIRMATIVE_SPEND = re.compile(
    r"(?:unlimited|any|multiple|each|additional|further|one\s+more)\s+(?:re-?entr|rebuy|re-?buy)"
    r"|may\s+re-?enter|\bre-?entry\s+(?:is|will\s+be|are)\s+(?:available|allowed|permitted)"
    r"|subsequent\s+(?:re-?entr|entry|flight|buy-?in)|add-?on\s+(?:is|will\s+be|are)\s+(?:available|offered|permitted)"
    r"|may\s+buy\s+into\s+another|buy-?in(?:s)?\s+(?:again|per\s+day|for\s+each)|bag(?:s|ged)?\s+in?\s+chips"
    r"|\bapplied\s+to\s+the\s+initial\s+entry\b",
    re.I,
)
NEGATION = re.compile(r"\b(?:no|not|none|without|neither|never|absent)\b", re.I)


def sentences(text: str):
    for part in re.split(r"(?<=[.;])\s+", text or ""):
        if part.strip():
            yield part.strip()


def affirmatively_offers_extra_entry(text: str) -> bool:
    """True if some sentence grants an extra entry, rebate of fees for it, or a bag.

    Sentence-level, so "No re-entry, rebuy or add-on clause appears on the sheet" does not
    read as a grant, while "Unlimited re-entry … will be available until level 9" does.
    """
    for sentence in sentences(text):
        if AFFIRMATIVE_SPEND.search(sentence) and not NEGATION.search(sentence):
            return True
    return False


def main() -> int:
    errors: list[str] = []
    data = json.loads(DATA.read_text(encoding="utf-8"))
    events = data["events"]

    screened = confirmed = 0
    for e in events:
        eid = e.get("id", "?")
        rules = e.get("rules") or {}

        # 1. Every rule block stands on its own source: status, a quote, an official URL, a date.
        for key in RULE_KEYS:
            block = rules.get(key)
            if block is None:
                continue
            if not isinstance(block, dict):
                fail(f"{eid}: rule '{key}' is not an object", errors)
                continue
            if not str(block.get("status", "")).strip():
                fail(f"{eid}: rule '{key}' has no status", errors)
            if not str(block.get("excerpt", "")).strip():
                fail(f"{eid}: rule '{key}' has status '{block.get('status')}' but no quoted excerpt", errors)
            src = block.get("source", "")
            if not official(src):
                fail(f"{eid}: rule '{key}' source is missing or not an official URL: {src!r}", errors)
            if not DATE_RE.match(str(block.get("retrieved", ""))):
                fail(f"{eid}: rule '{key}' has no retrieval date (YYYY-MM-DD): {block.get('retrieved')!r}", errors)

        single = rules.get("singleEntry") or {}
        status = single.get("status", "")

        # 2. "Confirmed" is the only label that means the venue put a cap in writing.  It has
        #    to be earned: maxEntries == 1 and the quoted text must actually state a cap.
        if status == "confirmed":
            confirmed += 1
            excerpt = single.get("excerpt", "")
            if not CAP_LANGUAGE.search(excerpt):
                fail(f"{eid}: labelled 'confirmed' but its excerpt does not state a per-player "
                     f"entry cap, no-rebuy or freezeout rule", errors)
            if single.get("maxEntries") != 1:
                fail(f"{eid}: labelled 'confirmed' without maxEntries == 1", errors)
            if not e.get("singleEntry"):
                fail(f"{eid}: status 'confirmed' but the row's candidate flag is not set", errors)

        # 3. The candidate boolean must agree with the screen.  A row that the sheet rules out
        #    cannot be a candidate, and a candidate cannot be anything but the screened label.
        if e.get("singleEntry") and status != SCREEN and status != "confirmed":
            fail(f"{eid}: candidate flag set while singleEntry status is '{status}'", errors)

        # 4. A screened row may not carry an affirmative spend provision anywhere on the row.
        #    This is the F75 shape exactly: the sheet quoted "any subsequent re-entry" while the
        #    row sat in the candidate list.
        if status == SCREEN:
            screened += 1
            for key in ("singleEntry", "reEntry", "addOn", "rebuy"):
                block = rules.get(key) or {}
                if affirmatively_offers_extra_entry(block.get("excerpt", "")):
                    fail(f"{eid}: {SCREEN} candidate, but rules.{key} excerpt grants an extra "
                         f"entry: {block.get('excerpt', '')[:120]!r}", errors)
            other = {k: (rules.get(k) or {}).get("status") for k in ("reEntry", "addOn", "rebuy")}
            for key, st in other.items():
                if st and st not in NOTHING_PRINTED:
                    fail(f"{eid}: {SCREEN} candidate, but rules.{key} asserts a provision "
                         f"(status '{st}')", errors)
            # 5. A screened row has to disclose that the cap is still unknown, so a reader
            #    cannot mistake the screen for a confirmation.
            if not re.search(r"maximum|does not state|unconfirm|not explicitly|freezeout",
                             single.get("excerpt", ""), re.I):
                fail(f"{eid}: {SCREEN} candidate whose excerpt does not say the entry cap is "
                     f"unconfirmed", errors)

    # 6. Hotels: where a property prints a waiver of its parking fee for poker-room players,
    #    the row must carry it, quote it verbatim from the capture, and must not fold it into
    #    a published total.  The Venetian, Palazzo and Wynn rows are compared like-for-like.
    capture_text = CAPTURE.read_text(encoding="utf-8") if CAPTURE.exists() else ""

    def normalise(t: str) -> str:
        """Collapse the capture to plain prose so a quote can be matched to its document.

        The capture stores the page text in markdown blockquotes with hard wraps; the
        comparison must not be an artefact of that formatting.
        """
        lines = [re.sub(r"^\s*>+\s?", "", ln) for ln in (t or "").splitlines()]
        return re.sub(r"\s+", " ", " ".join(lines)).strip()

    capture_norm = normalise(capture_text)
    waiver_bearing = []
    for h in data["hotels"]:
        waiver = h.get("parkingWaiver")
        hid = h.get("id", "?")
        if not waiver:
            continue
        waiver_bearing.append(hid)
        if not normalise(waiver.get("excerpt", "")):
            fail(f"hotel {hid}: parkingWaiver carries no excerpt", errors)
        elif capture_text and normalise(waiver["excerpt"]) not in capture_norm:
            fail(f"hotel {hid}: parkingWaiver excerpt is not a verbatim substring of the official "
                 f"capture in {CAPTURE.name}", errors)
        if not official(waiver.get("source", "")):
            fail(f"hotel {hid}: parkingWaiver source is missing or not official", errors)
        if not DATE_RE.match(str(waiver.get("retrieved", ""))):
            fail(f"hotel {hid}: parkingWaiver has no retrieval date", errors)
        if waiver.get("appliedToTotals"):
            fail(f"hotel {hid}: parkingWaiver appliedToTotals must be False while finish times are "
                 f"unpublished (F16)", errors)
        # Every fragment the row puts in quotation marks has to be in the capture, verbatim.
        # Opening quote not preceded by a word character (so an apostrophe cannot start a
        # quote), closing quote not followed by one.
        quoted = re.findall(r"(?<![\w'])'([^']{25,}?)'(?![\w'])", str(waiver.get("conditions", "")))
        for frag in quoted:
            if normalise(frag) not in capture_norm:
                fail(f"hotel {hid}: quoted parking condition is not in the official capture: {frag[:70]!r}", errors)

        if not str(waiver.get("whyNotApplied", "")).strip():
            fail(f"hotel {hid}: parkingWaiver is not applied to totals but says nothing about why", errors)
        if "three hours or more" not in (h.get("parking") or ""):
            fail(f"hotel {hid}: the table row still does not disclose the player parking waiver "
                 f"it publishes in parkingWaiver", errors)

    for hid in ("venetian", "palazzo"):
        if hid not in waiver_bearing:
            fail(f"hotel {hid}: the resort prints a poker-room parking waiver; the row must carry it (F86)",
                 errors)

    # 7. The trip-cost model keeps the paid parking line; the waiver sits beside it.
    model = data.get("tripCostModel") or {}
    if model:
        if model.get("parkingPerNight") != 20.0:
            fail("tripCostModel: the paid parking line changed value; this check exists to notice "
                 "that, so update the site's copy and the flag in the same commit", errors)
        walk = model.get("parkingWaiver") or {}
        if not walk:
            fail("tripCostModel: the parking line is published without the venue's printed waiver beside it",
                 errors)
        else:
            if walk.get("appliedToTotals"):
                fail("tripCostModel: parking waiver must not be netted off the total", errors)
            if not official(walk.get("source", "")):
                fail("tripCostModel: parking waiver source is missing or not official", errors)
            total = round(model["tournamentTotal"] + model["lodgingTotal"] + model["parkingTotal"], 2)
            if total != model["tripTotal"]:
                fail(f"tripCostModel: trip total {model['tripTotal']} != {total} recomputed from its parts",
                     errors)

    print(f"entry-label check: {len(events)} events · {screened} {SCREEN} candidates · "
          f"{confirmed} written-cap confirmations · hotels carrying a parking waiver: "
          f"{', '.join(sorted(waiver_bearing)) or 'none'}")
    if errors:
        print(f"\n{len(errors)} problem(s):")
        for err in errors:
            print(" -", err)
        return 1
    print("entry-label integrity passed")
    return 0


def fail(message: str, sink: list[str]) -> None:
    sink.append(message)


if __name__ == "__main__":
    sys.exit(main())
