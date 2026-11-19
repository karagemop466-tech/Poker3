# Repository review and blank-field completion — 2026-11-19 UTC

Session `arena/f5ac4318-poker3`, branched from `main` at `e79f5a6`.
Every line below was read from the page named beside it on **2026-11-19** through the platform's page reader.
No value was inferred. Where a page printed nothing, the field stays blank and the blank is named in the record.

---

## 1. Repository review

### 1.1 Two unresolved conflict markers had been published in `COORDINATION.md`

`main` at `e79f5a6` carried these two lines (the only conflict markers anywhere in the repository — a scan of every
.md`, `.py`, `.html`, `.json` and `.yml` file returned exactly these two):

> `>>>>>>> 609f1ce (coord: claim 2026-11-19 re-read + integration task (arena-23505d42))`
> `>>>>>>> c14bb08 (coord: record reconciled result (parallel-read agreement with 827185f7; F95/F92/F93 terms))`

Both arrived in merge commit `e79f5a6` (PR #179):

```
$ git log --oneline -S ">>>>>>> 609f1ce" -- COORDINATION.md
e79f5a6 Merge pull request #179 from karagemop466-tech/arena/23505d42-poker3
$ git log --oneline -S ">>>>>>> c14bb08" -- COORDINATION.md
e79f5a6 Merge pull request #179 from karagemop466-tech/arena/23505d42-poker3
```

**Whether any session record was lost.** Checked before deleting anything, against both parents of that merge:

```
parents: c5b511a3905edd3c93bb1938c0feba1ef717ed95 ee26288d7a41bb97a3f18f29dc75d12a09aba273
P1 c5b511a3  lines: 4031  missing from merged: 0
P2 ee26288d  lines: 4037  missing from merged: 0
```

Every non-blank line of both parents is present in the merged file, so nothing was dropped: these were trailing
markers with no `<<<<<<<` or `=======` partner. Both lines were removed from `main` on 2026-11-19 by PR #181 (session `96ff450a`), which records the same finding
("two orphaned rebase markers were removed, without removing any session text"). This session's scan after rebasing
onto that `main` returns zero markers, and the only remaining copy of the text is this quotation. Published as flag
**F98** (area *Publishing*, because the evidence is the repository itself).

### 1.2 The stale `parkingSource` on the Bellagio row

The Bellagio hotel row carried `parkingSource = https://bellagio.mgmresorts.com/en/terms-and-conditions.html` with a
blank `parking` field. That page (read in full on 2026-11-17 and again in chunk 0 on 2026-11-19) prints the resort fee,
tax rule, deposit, incidental hold and cancellation window, and **no parking figure**. A source that does not
substantiate the field it is cited for is misleading, so the row now cites the page that does print the figure.

---

## 2. Official pages read on 2026-11-19

### 2.1 MGM Resorts parking page — `https://www.mgmresorts.com/en/things-to-do/parking.html`

This is the page behind all three property-level parking URLs. Fetched directly:

| URL guessed from the property site | What it actually served |
|---|---|
| `https://bellagio.mgmresorts.com/en/amenities/parking.html` | `https://www.mgmresorts.com/en/things-to-do/parking.html` |
| `https://aria.mgmresorts.com/en/amenities/parking.html` | `https://www.mgmresorts.com/en/things-to-do/parking.html` |
| `https://mgmgrand.mgmresorts.com/en/amenities/parking.html` | `https://www.mgmresorts.com/en/things-to-do/parking.html` |

Verbatim, under **Parking Rates → Self Parking Rates**, for "Bellagio, ARIA, Vdara, The Cosmopolitan of Las Vegas,
MGM Grand, Mandalay Bay, W Las Vegas, Park MGM, The Reserve at Park MGM, New York-New York, Luxor, and Excalibur":

```
| Parking Duration                                                   | Mon - Thurs (Weekdays) | Fri - Sun (Weekends) |
| Over 0 to 24 hours                                                 | $20                    | $25                  |
| Over 24 hoursdaily rate for each additional day or fraction thereof| $20                    | $25                  |
| Registered Hotel Guest                                             | $20                    | $20                  |
```

Under **Valet Parking Daily Rates** for the same properties:

```
- Mon - Thurs (Weekdays): $40
- Fri - Sun (Weekends): $40
```

Other verbatim lines used:

- "Self-parking is complimentary for MGM Rewards Members with current level of Pearl, Gold, Platinum and NOIR."
- "For Nevada residents: receive first 3 hours of Self-Park at no charge, except during special events."
- "Prices may be higher during special events. Parking fees are subject to change and parking is subject to availability."
- "Terms and conditions vary for registered hotel guests vs. others (e.g. Weekend rates do not apply to registered hotel guests)."

**What this fills.** The Bellagio, MGM Grand and ARIA rows had a blank parking field. They now carry the printed
registered-guest figure: **$20 a day self-parking on weekdays and weekends, $40 a day valet**, with
`parkingPerNight = 20.0` so the parking line of a trip cost is no longer blank for an MGM property. What stays open is
recorded as flag **F99**: no property-level table exists any more, so a property-specific difference cannot be checked,
and the page reserves the right to charge more on event days.

### 2.2 ARIA hotel reservation terms — `https://aria.mgmresorts.com/en/terms-and-conditions.html`

Verbatim, and every figure unchanged from the published values:

- "A daily resort fee of $55.00 plus applicable tax will be applied to all reservations."
- "Check in time is 3:00 pm and check out time is 11:00 am."
- "There is an additional charge of $50 plus tax per occupant, per night, above 2 occupants per room."
- "a per day incidental amount of $150 for Deluxe Rooms, $250 for Tower Suites, $350 for Sky Suites and $500 for Villas"
- "The first night's deposit is fully refundable provided a timely notice of cancellation is received by Room
  Reservations at 866.359.7757 at least 72 hours prior to the arrival date"
- "Lodging taxes apply to the basic room rate, any resort fee, additional per occupant charges, upgrades" — still no
  percentage printed, so `taxRate` stays blank.

### 2.3 MGM Grand hotel reservation terms — `https://mgmgrand.mgmresorts.com/en/terms-and-conditions.html`

Verbatim, unchanged:

- "A daily resort fee of $50.00 plus applicable tax will be applied to all reservations."
- "Check in time is 3:00 pm and check out time is 11:00 am."
- "There is an additional charge of $40 plus tax per occupant, per night, above 2 occupants per room."
- "a $100 incidental amount per day"
- "The first night's deposit is fully refundable provided a timely notice of cancellation is received by Room
  Reservations at 877.880.0880 at least 72 hours prior to the arrival date"

### 2.4 What these reads change

| Row | Field | Before | After |
|---|---|---|---|
| `bellagio` | `parking`, `parkingSource` | blank; source was the terms page, which prints no parking | $20/day self, $40 valet; source is the parking page |
| `mgm` | `parking`, `parkingSource`, `parkingPerNight` | blank | same figure; `parkingPerNight = 20.0` |
| `aria` | `parking`, `parkingSource`, `parkingPerNight` | blank | same figure; `parkingPerNight = 20.0` |
| the three rows | `lastChecked` / `lastVerified` | 2026-11-17 | 2026-11-19 (the pages above were read on that date) |
| hotel `status` text | — | said the fee terms were verified and said nothing about parking | now names the parking figure and its source date |

No tournament, rate, guarantee, rule or walking-time value was changed. The Venetian, Palazzo, Wynn, Caesars Palace
and Horseshoe rows were not touched: their pages were not re-read by this session.

---

## 3. Checks that were re-confirmed, not changed

- **Earliest published start (flag F17).** Re-derived from the published rows: the earliest recurring official start is
  Horseshoe **9:00 AM**, then Caesars Palace 10:00 AM, Bellagio and Horseshoe 11:00 AM, MGM Grand 11:10 AM, Wynn
  12:00 PM. No room in the reviewed set publishes an 8:00 AM tournament, so the "all day from 8 AM" plan still starts
  at 9:00 AM and F17 stays open. No value moved.
- **Tax.** No property printed a room-tax percentage on 2026-11-19 either; `taxRate` therefore stays blank for Wynn,
  Bellagio, MGM Grand, ARIA, Caesars Palace and Horseshoe, with the 13.38% county figure shown only as a labelled
  reference. `scripts/audit_data.py` and `tests/test_hotel_costs_and_qualification.py` enforce this.

---

## 4. Verification run in this session

```
python3 scripts/data_source.py         -> site/data.json: 341 events, 8 hotels, 56 routes, 49 sources
python3 scripts/build_addendum.py      -> site/sheets.html: 94 flags, 8 hotels, 56 routes, 0 unexplained disagreements
python3 scripts/verify_site.py         -> events 341 / hotels 8 / routes 56 / sources 49 / flags 94 / plan days 7 / pages 16 — passed
python3 -m unittest discover -s tests  -> 260 tests OK
```

The `sheets.html` page is generated and embeds the flag register, so it was rebuilt after the two new flags; a test
(`tests/test_sheet_page_not_stale.py::test_every_flag_is_rendered`) fails if it is left stale.

---

## 5. Open items this session did not close

- **F99** — MGM publishes one corporate parking table instead of per-property tables, so no property-specific
  difference can be verified.
- **F17** — no 8:00 AM start is published by any reviewed room.
- **F19** — no official per-room quality score, so the quality column stays blank; the hotel ranking is on published
  cost components and walking time only.
- **F31 / F16 / F39 / F56 / F93 / F94 / F96** — unchanged and still open on the Flagged for review page.
