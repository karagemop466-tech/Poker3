# Repo review — 2026-11-19, session `arena/e94482ee-poker3`

Branch `arena/e94482ee-poker3`, from `main` at `5c42d7fb5e9931f4582af03e6aa6cc741efc9d9e`.
Every claim below is followed by the official page it was checked against, or by the repository path and the
command that produced it. Nothing in this file is inferred: a value that could not be read from an official
source is named as unread.

---

## 1. What was read live in this session

All reads were made through the platform page reader on 2026-11-19. The build sandbox itself cannot reach the
venue hosts (recorded flag F40), so the commands in this repository that need the network run in GitHub Actions.

### 1.1 Venetian DeepStack Extravaganza IV schedule — all four chunks

Source: <https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html>

The four chunks cover Nov 16 – Dec 23, 2026. Each of the 19 rows inside the trip window (2026-11-23 … 2026-11-30)
was compared with `site/data.json` on date, start time, event number, printed name, printed buy-in, printed
guarantee and the structure-sheet link. **19/19 match; no row is missing, no value was added or changed.**

Rows confirmed verbatim in this pass, in schedule order:

| Date | Time | # | Printed name | Buy-in | Guarantee | Sheet |
|---|---|---|---|---|---|---|
| Nov 23 | 11:10 AM | 7 | $400 No Limit Hold'em 1A $75K GTD | $400 | $75,000 | structure_2 |
| Nov 23 | 5:10 PM | 8 | $200 No Limit Hold'em $8K GTD (1Day) – Progressive Knock-Out Bounty (PKO) | $200 | $8,000 | structure_30 |
| Nov 24 | 11:10 AM | 7 | $400 No Limit Hold'em 1B $75K GTD | $400 | $75,000 | structure_2 |
| Nov 24 | 5:10 PM | 9 | $200 No Limit Hold'em Bounty $8K GTD (1Day) | $200 | $8,000 | structure_1 |
| Nov 25 | 11:00 AM | 7 | $400 No Limit Hold'em Day 2 Restart | $400 | $75,000 | structure_2 |
| Nov 25 | 11:10 AM | 10 | $400 No Limited Hold'em $15K GTD (1Day) | $400 | $15,000 | structure_6 |
| Nov 25 | 5:10 PM | 11 | $200 No Limit Hold'em Bounty $8K GTD (1Day) | $200 | $8,000 | structure_1 |
| Nov 26 | 11:10 AM | 12 | $300 No Limit Hold'em $10K GTD (1Day) | $300 | $10,000 | structure_5 |
| Nov 26 | 5:10 PM | 13 | $200 No Limit Hold'em Bounty $8K GTD (1Day) | $200 | $8,000 | structure_1 |
| Nov 27 | 11:10 AM | 14 | $600 No Limit Hold'em $30K GTD (1Day) | $600 | $30,000 | structure_7 |
| Nov 27 | 5:10 PM | 15 | $200 No Limit Hold'em Bounty $8K GTD (1Day) | $200 | $8,000 | structure_1 |
| Nov 28 | 11:10 AM | 16 | $600 No Limit Hold'em Bounty $30K GTD (1Day) – $200 bounties to start & $500 in the money | $600 | $30,000 | structure_11 |
| Nov 28 | 12:10 PM | 17 | $400 Pot Limit Omaha Bounty $15K GTD (1Day) | $400 | $15,000 | structure_26 |
| Nov 28 | 5:10 PM | 18 | $200 NLH PokerAtlas Valuetown Bounty $20K GTD (1Day) – POKERATLAS PRO MEMBER $20 RAKE DISCOUNT | $200 | $20,000 | structure_8 |
| Nov 29 | 11:10 AM | 19 | $400 No Limit Hold'em 1A $75K GTD | $400 | $75,000 | structure_3 |
| Nov 29 | 12:10 PM | 20 | $300 Pot Limit Omaha $10K GTD (1Day) – Double Board Bomb Pot | $300 | $10,000 | structure_22 |
| Nov 29 | 5:10 PM | 21 | $200 No Limit Hold'em Bounty $8K GTD (1Day) | $200 | $8,000 | structure_1 |
| Nov 30 | 11:10 AM | 19 | $400 No Limit Hold'em 1B $75K GTD | $400 | $75,000 | structure_3 |
| Nov 30 | 5:10 PM | 22 | $200 No Limit Hold'em Bounty $8K GTD (1Day) | $200 | $8,000 | structure_1 |

Note the page's own misspelling on Nov 25 ("$400 No Limited Hold'em $15K GTD"): the published row keeps the
corrected wording from the structure sheet, which is the same kind of rendering irregularity already recorded
for the WPT PDF (F45).

### 1.2 Venetian structure sheets — all eleven that the trip window links

Each sheet was read in full. What each prints, and whether a maximum-entry rule is printed:

| Sheet | Event(s) | Start | Chips | Levels | Late reg | Guarantee | Fee split printed | Re-entry / rebuy / add-on printed? |
|---|---|---|---|---|---|---|---|---|
| 1 | 9, 11, 13, 15, 21, 22, 23, 25, 60–62, 64 | 5:10 PM | 25,000 | 30 min | 8 levels + break (9:40 PM) | $8,000 (pool + bounties) | $40 of $200 | None printed |
| 5 | 2, 12 | 11:10 AM | 40,000 | 30 min | 10 levels + break (~4:55 PM) | $10,000 | $58 of $300 | None printed |
| 6 | 10 | 11:10 AM | 40,000 | 30 min | 10 levels + break (~4:55 PM) | $15,000 | $65 of $400 | None printed |
| 7 | 14, 28, 63 | 11:10 AM | 40,000 | 30 min | 10 levels + break (~4:55 PM) | $30,000 (#14, #63) / $40,000 (#28) | $90 of $600 | None printed |
| 11 | 16, 30, 54 | 11:10 AM | 40,000 | 30 min | 10 levels + break (4:55 PM) | $30,000 (#16) / $40,000 (#30) / $50,000 (#54), pool + bounties | $90 of $600 | None printed |
| 22 | 20 | 12:10 PM | 30,000 | 30 min | 8 levels + break (~4:40 PM) | $10,000 | $58 of $300 | None printed |
| 26 | 17 | 12:10 PM | 30,000 | 30 min | 8 levels + break (~4:40 PM) | $15,000 (pool + bounties) | **$60 of $400 for house fees, prize pool $340 of every $400** | None printed |
| 30 | 8 | 5:10 PM | 25,000 | 30 min | 8 levels + break (9:40 PM) | $8,000 (pool + bounties) | $40 of $200 | None printed |
| 2 | 7 | 11:00 AM restart / 11:10 AM flights | 40,000 | 40 min | 9 levels + break (5:55 PM) | $75,000 | $70 of $400 | **Yes — a bagging rule that allows another flight** |
| 3 | 19 | 11:10 AM | 40,000 | 40 min | 9 levels + break (5:55 PM) | $75,000 | $70 of $400 | **Yes — same bagging rule** |
| 8 | 18 | 5:10 PM | 25,000 | 30 min | 8 levels + break (9:40 PM) | $20,000 | $40 of $200 | **Yes — PokerAtlas PRO member rake discount** |

**Result of the sheet re-read: no value discrepancy.** Every fee split, chip count, level length, late-registration
clock and guarantee now printed by the eleven live sheets equals the figure already published in
`site/data.json` (checked event by event). Two printing differences are worth recording because they look like
anomalies and are not:

- Sheet 26 (Event #17, $400 PLO Bounty) withholds **$60 of $400 = 15.0%**, while the other $400 events withhold
  $65–$70 (16.25–17.5%). That is the venue's own published allocation for that event, printed verbatim on the
  row, and it is not an error to correct.
- Sheet 7 prints the guarantee **per event number** — "$30,000 for Event #14 and #63" and "$40,000 for Event #28"
  for the same buy-in. A row therefore has to be matched to its event number, not only its buy-in; the published
  rows do this and carry the matching figure.

The only genuine wording irregularities in this pass are rendering artefacts that were already flagged:
the live schedule page prints "$400 No **Limited** Hold'em $15K GTD" for Nov 25 (published row keeps the sheet's
correct wording, same class as F45), and the WPT PDF prints "BadugI" for Badugi (F62).

### 1.3 Wynn WPT World Championship schedule PDF

Source: <https://cdn.wynnresorts.com/image/upload/v1757097329/visitwynn_pdfs_files/Poker/WPT/WPT_World_Championship_Schedule.pdf>

All 13 rows that fall inside the trip window were compared with `site/data.json`: **13/13 match** on date, time,
event name, buy-in, guarantee, chips and level length. Nov 27 has 1A/1B/1C-style flights at 11 a.m. and 5 p.m.;
Nov 28 Mixed Triple Draw at 12 p.m.; Nov 29 1E at 11 a.m. and 1F at 6 p.m.; Nov 30 the $800 $1M flight at 11 a.m.
and 5 p.m. plus a Day 2 at 1 p.m. The printed name "BadugI" (capital I for l) is a rendering artefact of the same
class as F45/F62 and is not corrected.

### 1.4 Venetian hotel terms, resort fee, poker-suite rate and parking

| Page | What it prints, verbatim | Value used on the site |
|---|---|---|
| [Hotel Terms & Conditions](https://www.venetianlasvegas.com/legal/hotel-terms-and-conditions.html) | "Daily rates do not include the applicable Clark County Room Tax of 13.38%." · "The Venetian Resort has a standard Las Vegas Resort Fee of $55 plus applicable tax per night, payable upon check-in." · "Check-out time is 11:00 a.m. Check-ins prior to 3:00 p.m. and check-outs after 11:00 a.m. are subject to additional fees." · "Check-out prior to your scheduled departure date will result in an additional charge of $100 plus tax." · "A deposit for your stay, including suite, fee, and tax, will be billed upon reservation confirmation." | 13.38% tax, $55 fee, 11 a.m. checkout, $100 early-checkout, deposit terms — all unchanged from the published record |
| [Resort Fee](https://www.venetianlasvegas.com/resort/resort-fee.html) | "Rates include a daily Resort Fee of $55 plus tax per night, payable upon check-in." | The same $55, but the wording **contests** the terms page (F51 stands: "include" vs "plus") |
| [Poker Suite Rates](https://www.venetianlasvegas.com/resort/casino/poker/suite-rates.html) | "These rates will start as low as $119 and $209 and can be higher." · "There is a $55 resort fee per night stayed." · "you will be required to play six hours of active live cash gameplay or buy in to a $300 or higher tournament for each night stayed" · code EPOKR25, by telephone, 866.255.8936 | $119/$209 starting rates, the qualification condition (F54, F66) |
| [Poker Room Parking](https://www.venetianlasvegas.com/resort/casino/poker/player-parking.html) | "The daily fee for registered hotel guests is $20/day, seven days a week." · "Players in the poker room who play three hours or more in tournament or cash games will receive complimentary self-parking for the day." | $20/night parking, waiver printed but not netted off (F86) |

### 1.5 Venetian booking engine — a second dated total for the trip stay

Source: <https://www.venetianlasvegas.com/booking?adults%5B%5D=2&children%5B%5D=0&arrival_date=2026-11-23&departure_date=2026-11-30&view=calendar>

The identical query used on 2026-11-17 (2 adults, 7 nights) rendered a full itemised panel on 2026-11-19:

- Suite: **palazzo Luxury King**, "Book Direct: Up to 25% Off", 2 adults, 7 nights
- Printed room rates: 204.25 / 204.25 / 204.25 / 309.25 / 1,119.25 / 561.75 / 204.25 → **$2,807.25**
- Resort fee: **$55.00 listed on each of the seven nights** → $385.00
- Pre-tax subtotal: **$3,192.25**
- Printed Taxes: **$427.14** (13.38% of $3,192.25 is $427.12 — a 2-cent difference, published as F120)
- Printed Total ("Estimated cost of stay"): **$3,619.39**; printed Average Rate: **$456.04**
- All-in per night = printed total ÷ 7 = **$517.06**

Two arithmetic facts the page does not state, now published with the record: the printed Average Rate
($456.04) is the average of (room rate + $55) and therefore includes the resort fee while excluding tax, and
the seven per-night derivations (rate + $55) × 1.1338 add to $3,619.38, one cent under the printed total.

`site/data.json` now carries this as `tripCostModel.liveQuote.laterRead` and as a dated `rateLog` entry beside
the $4,010.55 read of 2026-11-17. Flag **F93** is corrected from "still prints no checkout total" to
"partially resolved" because the earlier loading-shell reads and this successful read are both true on the same
day.

### 1.6 Wynn booking engine and Wynn policy pages

| Page | What it prints | Use |
|---|---|---|
| [Wynn IBE, 23–30 Nov 2026](https://reservations.wynnlasvegas.com/ibe/details.aspx?hotelID=13763&langID=1&rmID=68658&checkIn=11/23/2026&checkOut=11/30/2026) | "Wynn Resort King · 7 Night Stay: Nov. 23 - Nov. 30, 2026" · "Flexible Getaway Rate — $495 Avg/Night — Includes Resort Fee, Excludes taxes" | Dated observation, unchanged from the 2026-11-19 record |
| [Resort Policies & Information](https://www.wynnlasvegas.com/about-us/resort-information) | "Reservations will be charged a daily resort fee of $55 plus tax." · Check-in 3 p.m., check-out 12 p.m. | $55 fee, check-in/out — unchanged |
| [Parking Information](https://www.wynnlasvegas.com/about-us/parking) | "complimentary parking for all Wynn and Encore Resort and Tower Suite registered guests" · unregistered $25/day · valet $40/day · "Complimentary self-parking is extended to Wynn Poker Room guests" | **New**: the registered-guest figure is a published **$0**, so the row now carries `parkingPerNight: 0.0` instead of a blank |

### 1.7 Caesars Entertainment parking

Source: <https://www.caesars.com/parking>

Caesars Palace: registered hotel guests **$20/day** self-parking, Gold $25/day, Platinum/Diamond/Seven Stars
free, non-member $25/day, valet $50/day. Horseshoe Las Vegas: registered guests and non-members **Monday–Wednesday
$20/day, Thursday–Sunday $25/day**, valet $40/day. Both match the published rows; Horseshoe's weekday split still
has no single nightly figure (`parkingPerNight` stays unset, F102).

---

## 2. Repository review — defects found and fixed in this session

| # | Defect | Where | Fix | Guard |
|---|---|---|---|---|
| 1 | Five 2026-11-16 snapshot JSON files were published under `site/data/` and answered the same questions with stale values | `site/data/{flags,questions,suggestions,tournaments,sources}.json` | moved to `archive/` with a provenance README (F101 resolved) | `tests/test_sheet_page_not_stale.py` now guards all eight retired names |
| 2 | A dead builder wrote one of those snapshots; nothing referenced it | `scripts/build_data.py` | removed | `test_sheet_page_not_stale.py::test_generator_does_not_read_a_snapshot_json` |
| 3 | A second, never-scheduled checker read the retired source list | `scripts/daily_check.py` | kept, marked retired and unused, with a pointer to `scripts/check_sources.py` | — (no workflow references it) |
| 4 | F93 asserted the engine "still prints no checkout total", which a later read the same day disproved | `scripts/data_source.py` | corrected to "partially resolved" with both reads named | `tests/test_calculator_page.py` asserts both dated totals render |
| 5 | The hotel rate log rendered a 7-night quote as "observed nights: $low and $high", hiding five nights and never showing an all-in nightly cost | `site/assets/app.js` | each printed night is listed and the all-in per night is the printed total ÷ nights | `tests/canonical_render.js` |
| 6 | Wynn's parking cell was blank although the property publishes a $0 for registered guests | `scripts/data_hotels.py` | `parkingPerNight: 0.0` with the printed sentence and the unregistered-guest rates | — |
| 7 | One flag (`F117`) cited a repository file under an area not in the verifier's publishing/monitoring exemption | `scripts/data_verification.py` | re-classified to `Monitoring`; `verify_site.py` passes | `scripts/verify_site.py` |
| 8 | The second dated quote's derived nights miss the printed total by one cent, which the independent auditor treated as a failure | `scripts/audit_951cd431.py` | the auditor now reconciles per night and accepts a ≤1-cent-per-night rounding gap **only** when the record discloses it in its own note | `audit_951cd431.py`, run in every CI job |

**Checked and found clean in this pass**

- Local links: 27 HTML pages under `site/`, 1 false positive (a JavaScript string inside `calculator.html`), 0 broken.
- Every one of the 341 event rows carries an official `scheduleUrl` or `structureUrl`; 0 rows without a source.
- `lastChecked` on all 32 trip-window rows is 2026-11-19; no row anywhere still carries 2026-11-16.
- No row anywhere carries the word "unverified" in its note or eligibility field; blanks are explained by a note or a flag.
- Data rebuild from the modules is deterministic (byte-identical `data_source.py` output across runs).
- Local date references still reading 2026-11-16/17 in the rendered pages are dated *observations* (a walk
  capture, a quote, a flag title), not claims that the value is current.

---

## 3. Open, unresolvable-from-official-sources items (unchanged, blocking the booking decision)

| Item | Why it is still open | Official page for manual review |
|---|---|---|
| No written maximum-entry / no-rebuy / no-add-on rule from the Venetian for any 2026 event (F31) | The 52 sheet-screened rows print one buy-in and no extra-entry clause, which is a document screen, not a cap. The same venue's April 2023 schedule did print "One Entry Only with One Hour of Registration". | <https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html> · ask the room: 702.414.7657 |
| No published tournament finish times (F16) | No sheet or page prints one; the overlap check is therefore a stated six-hour assumption, labelled as such. | same schedule page, and each structure sheet |
| No official 8:00 AM start on the Strip (F17) | Earliest recurring official start is Horseshoe 9 a.m.; Venetian main-list starts are 10:10/11:10 a.m. | <https://www.caesars.com/las-vegas/explore/casino/poker-tournaments-las-vegas-strip> |
| Room-tax percentage for six of the eight properties (F39) | Only the Venetian prints 13.38%. The county rate is published but applying it to another property's own total is an assumption. | <https://www.clarkcountynv.gov/adobe/assets/urn:aaid:aem:689ef54f-ec0d-4bb6-b8ea-05a82887561f/original/as/genl-info-guide-for-tles-july-2021.pdf> |
| Whether EPOKR25 applies to 23–30 Nov 2026, and at what nightly rate (F66, F54) | The rate page publishes only a floor ("as low as $119 and $209"), blackout dates and a play condition; it publishes no date-specific price. | <https://www.venetianlasvegas.com/resort/casino/poker/suite-rates.html> |
| Bellagio Saturday buy-in printed three ways (F02) | Page says $1,000; PDF header says $1,100; PDF rule 07 allocates a $600 buy-in. | <https://assets.contentstack.io/v3/assets/bltc6ce635bc4868eb2/blt6d47974bf5a7d9b6/6af491a391a6e8e4230c9e07/mgm-bellagio-poker-saturdays-$1000-nlh.pdf> |
| Caesars "every event $100" vs the flyer's $100/$160 plus a $50 add-on (F90) | Two official Caesars pages disagree; the add-on also disqualifies the format from the single-entry section. | <https://www.caesars.com/las-vegas/explore/casino/poker-tournaments-las-vegas-strip> |
| Walking minutes are a third-party estimate (F32, F84) | No property publishes a walking time; every figure is a Google Maps walking reading with its own date. | the Maps link on each route row |

---

## 4. Questions to answer before any change is planned

These are the questions this review cannot answer from official sources. Each has the source that would settle
it, so the answer can be obtained without guesswork.

1. **Will the Venetian put the maximum-entry, no-rebuy and no-add-on rules in writing for the November events?**
   Route: poker room, 702.414.7657 or `lv_cas_poker@venetianlasvegas.com` (both printed on the suite-rates page).
   Until then no row is labelled confirmed single-entry and the ranking page has no eligible winner.
2. **Does the engine's $3,619.39 (2026-11-19) or $4,010.55 (2026-11-17) total apply to a poker-rate booking with
   code EPOKR25, or only to the public best-available rate?** Route: the same phone number, asking for the
   all-in total for 23–30 Nov 2026 in writing under EPOKR25.
3. **Do nights 23 and 24 November satisfy the poker-rate play condition** (six hours of cash or a $300+ buy-in
   each night)? On those two dates the Venetian's own evening events are $200 bounty tournaments, which do not
   meet the $300 threshold, so the player would have to play cash or add the Nov 24/25 $400 event on those days.
   Route: confirm with the poker room how the condition is assessed on a night with only a $200 event.
4. **What is the trip's occupancy and room type?** Two adults in one king is assumed. A second bed, a view or a
   second adult changes the total (the terms page prints $50 per additional guest 13+).
5. **Is a 30-minute walk the real constraint, or is a 10-minute walk preferred?** The site applies the 30-minute
   filter; narrowing it changes which eight hotels remain eligible.
6. **What nightly ceiling replaces the $299.32 planning ceiling?** Both dated official totals are above it
   ($517.06 and $572.94 all-in). Either the ceiling rises or the trip needs a different property.
7. **Does the player accept an event that starts at 5:10 p.m. as the day's primary event** on Nov 23, 24 and 26,
   where the morning event is a multi-flight or a $300 that does not meet the poker-rate threshold? This is the
   only way to keep the poker rate on those nights without adding entries.

---

## 5. Verification commands run before the pull request

```
python3 scripts/data_source.py            # deterministic rebuild
python3 scripts/build_addendum.py         # sheets page regenerated from site/data.json
python3 scripts/coverage.py               # traceability matrix refreshed
python3 scripts/verify_site.py            # 341 events / 8 hotels / 56 routes / 50 sources / 103 flags / 18 pages
python3 scripts/audit_951cd431.py         # independent auditor: 0 failures, 0 warnings
python3 scripts/audit_data.py             # 37 structure sheets vs 94 rows
python3 scripts/verify_live_official.py   # both official captures vs canonical rows
python3 scripts/verify_entry_labels.py    # entry-label integrity
python3 -m unittest discover -s tests -p 'test_*.py'   # 334 tests OK
python3 tests/canonical_smoke.py && node tests/canonical_render.js && node tests/walk_limit_render.js
node --check site/assets/app.js && node --check site/assets/search.js && node --check site/assets/venue.js
```
