# Independent line-by-line verification record — 2026-11-19 (session `arena/80a6f5df-poker3`)

Branch: `arena/80a6f5df-poker3`, branched from `main` at `5c42d7fb5e9931f4582af03e6aa6cc741efc9d9e`.
Every value below was re-read by this session from the official page or PDF named beside it. Nothing is inferred, and
no published value was edited in this session.

## How this pass was run

The build sandbox has no direct egress to the venue hosts (`curl` to `www.venetianlasvegas.com` fails with
`SSL_ERROR_SYSCALL`), so every official read in this record was made through the platform page reader and is dated
2026-11-19. Where a published value is compared against a live read it is compared character for character against
the captured text, not from memory.

## 1. Venetian DSE IV schedule page — 94-row re-read

Source: <https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html>
(all four chunks read: 16 November – 23 December 2026).

The trip window (23–29 November 2026, the seven playable days) was transcribed from the live page and compared with
the 19 published rows in `site/data.json` on date, start time, printed buy-in, printed guarantee and structure-sheet
URL. **19 / 19 matched.** The comparison script and its output are reproducible:

```
trip-window rows matched against live official page text: 19/19
```

Rows verified: 23 Nov 11:10 AM #7 1A $400/$75K (sheet 2) and 5:10 PM #8 $200/$8K PKO (sheet 30); 24 Nov 11:10 AM
#7 1B and 5:10 PM #9 $200/$8K bounty (sheet 1); 25 Nov 11:00 AM #7 Day 2 restart, 11:10 AM #10 $400/$15K (sheet 6),
5:10 PM #11; 26 Nov #12 $300/$10K (sheet 5), #13; 27 Nov #14 $600/$30K (sheet 7), #15; 28 Nov #16 $600/$30K bounty
(sheet 11), 12:10 PM #17 $400 PLO (sheet 26), #18 $200/$20K PokerAtlas (sheet 8); 29 Nov #19 1A $400/$75K (sheet 3),
#20 $300 PLO (sheet 22), #21. Also checked: 30 November's #19 1B and #22, which the site correctly excludes from the
playable days because check-out is 11:00 a.m. that day.

## 2. Structure sheets behind the day plan — read in full

| Sheet | Event | What the official sheet prints | Matches the published row |
|---|---|---|---|
| [`structure_30.pdf`](https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_30.pdf) | #8, $200 PKO | Event 08, 5:10 PM, 25,000 chips, 30-min levels, late reg "8 levels + Break (9:40 PM)", "$8,000 (prize pool + total bounties)", rule 06 "$40 of the $200 Buy-In is withheld" | yes |
| [`structure_1.pdf`](https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_1.pdf) | #9, #11, #13, #15, #21, #22, #23, #25, #60–64 | Event Numbers 09, 11, 13, 15, 21, 22, 23, 25, 60, 61, 62, 64; 5:10 PM; 25,000 chips; 30-min levels; late reg 9:40 PM; $8,000 includes bounties; "$40 of the $200 Buy-In is withheld" | yes |
| [`structure_22.pdf`](https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_22.pdf) | #20, $300 PLO | Event 20, 12:10 PM, 30,000 chips, 30-min levels, late reg "8 levels + break (~ 4:40 PM)", $10,000 guarantee, "$58 of the $300 Buy-In is withheld" | yes |

The sheets print **no** finish time and **no** maximum number of entries per player, so flag F16 (no published finish
time) and F31 (no written one-entry maximum) are both **reconfirmed, not resolved**, on today's read.

## 3. Hotel components

| Value published | Official text read 2026-11-19 | Source |
|---|---|---|
| Poker-suite rate "as low as $119 and $209, can be higher" | verbatim: "These rates will start as low as $119 and $209 and can be higher. Future rates are only provided out to a maximum of 150 days from the current date. Rates are subject to qualifying poker play and availability based on hotel occupancy." | [suite-rates.html](https://www.venetianlasvegas.com/resort/casino/poker/suite-rates.html) |
| Resort fee $55 per night | verbatim: "There is a $55 resort fee per night stayed." (rate page) and "Rates include a daily Resort Fee of $55 plus tax per night, payable upon check-in." (resort-fee page) | [suite-rates.html](https://www.venetianlasvegas.com/resort/casino/poker/suite-rates.html), [resort-fee.html](https://www.venetianlasvegas.com/resort/resort-fee.html) |
| Clark County room tax 13.38% | verbatim: "Daily rates do not include the applicable Clark County Room Tax of 13.38%." | [hotel terms](https://www.venetianlasvegas.com/legal/hotel-terms-and-conditions.html) |
| Registered-guest self-parking $20/day; valet $40/day | verbatim: "The daily fee for registered hotel guests is $20/day, seven days a week. For non-hotel guests, the fee is $20/day Monday – Thursday, and $25/day Friday – Sunday. Valet parking is $40/day." | [player-parking.html](https://www.venetianlasvegas.com/resort/casino/poker/player-parking.html) |
| Parking waiver for three hours of play | verbatim: "Players in the poker room who play three hours or more in tournament or cash games will receive complimentary self-parking for the day." | [player-parking.html](https://www.venetianlasvegas.com/resort/casino/poker/player-parking.html) |
| Check-in 3:00 p.m.–11:59 p.m., check-out 11:00 a.m., late check-out billed | verbatim: "Check-in time is from 3:00 p.m. to 11:59 p.m. … Check-out time is 11:00 a.m. Check-ins prior to 3:00 p.m. and check-outs after 11:00 a.m. are subject to additional fees." | [hotel terms](https://www.venetianlasvegas.com/legal/hotel-terms-and-conditions.html) |
| Prepaid offers non-cancellable; $100 + tax early check-out | verbatim: "bookings made using a prepaid offer are non-cancellable and non-refundable" and "Check-out prior to your scheduled departure date will result in an additional charge of $100 plus tax." | [hotel terms](https://www.venetianlasvegas.com/legal/hotel-terms-and-conditions.html) |

The published floor arithmetic `($119 + $55) × 1.1338 = $197.28` reproduces exactly, and the published ceiling
`($209 + $55) × 1.1338 = $299.32` reproduces exactly. **No value changed.**

## 4. Poker-room location — confirmed, and an existing gap re-checked

The official poker page still prints "LOCATION: The Palazzo, level 2, Grand Canal Shoppes", "Open 24 Hours", the
"50 tables … 14,000 square feet … largest room on the Las Vegas Strip" sentence and the "complimentary self-parking
for non-registered guests who play three hours or more" line. The site's existing flag **F91** already records that
the walking minutes are measured to the resort, not to the room's own level-2 entrance. That flag stays open and no
minutes were changed here.

## 5. Wynn WPT World Championship schedule — second independent read

Source: [WPT_World_Championship_Schedule.pdf](https://cdn.wynnresorts.com/image/upload/v1757097329/visitwynn_pdfs_files/Poker/WPT/WPT_World_Championship_Schedule.pdf)
(chunks 0–1, 2026-11-19). Every trip-window row published from this PDF matches: 27 Nov 11 a.m. NLH Day 1A $600 /
$400,000 / 40,000 chips / 30-40 levels; 12 p.m. TORSE $600 / 35,000; 1 p.m. PLO $400 / 30,000; 5 p.m. Day 1B;
28 Nov 11 a.m. Day 1C, 12 p.m. Mixed Triple Draw, 5 p.m. Day 1D; 29 Nov 11 a.m. Day 1E (30/40) and 6 p.m. Day 1F
(20/40, the only turbo flight). The site already flags (F34, F61) that this schedule prints "Nov. 30 Monday … No Limit
Hold'em Day 2" at 1 p.m. on the same day as its own Day 1A, and "Dec. 5 Saturday … No Limit Hold'em Day 2" at 11 a.m.
beside the Prime Championship Day 1A; both reproductions are accurate to the document. **Confirmed as printed; the
schedule's internal impossibility is a venue irregularity, not a site error.**

## 6. Bellagio and MGM Grand structure documents — still not single-entry

- [Bellagio Friday $600 NLH](https://assets.contentstack.io/v3/assets/bltc6ce635bc4868eb2/blt9cf95b0e60ec253e/6af491a3a9851d75c40be840/mgm-bellagio-poker-fridays-$600-nlh.pdf)
  read live: rule 03 "Players may buy-in and re-enter through the end of level 8"; rule 05 "$510 to Prize Pool; $50
  House Fee; $40 Voluntary Staff Gratuity"; rules 06–07 "$40 … will grant players an extra 15,000 chips". That is a
  paid extra-chip path, so the Friday row correctly stays outside the single-entry list.
- [MGM Grand tournament schedule](https://assets.contentstack.io/v3/assets/bltc6ce635bc4868eb2/blt5f25277b8918da08/mgm-grand-casino-poker-tournament_schedule.pdf)
  read live: the sheet is titled "MGM Grand **August** Tournament Schedule" with no year, and prints "Players with 5
  entries or more in $120 Daily Tournaments will receive one (1) free entry". The published recurring rows are
  reproduced accurately and the sheet's own month mismatch is already carried as a flag.

## 7. Arithmetic and structure audit of the published data

| Check | Result |
|---|---|
| `ratio = guarantee ÷ buyIn` on every row that publishes both | consistent (80 exact, 34 deliberately blank because the printed "guarantee" is seats, not cash) |
| Rows missing a `lastChecked` date | 0 of 341 |
| Rows with no official source link at all | 0 of 341 |
| `lastChecked` distribution | 292 rows 2026-11-19, 49 rows 2026-11-17 (the WPT schedule rows, correctly kept at the earlier date) |
| Hotel `lastChecked` / `lastVerified` | all 8 properties 2026-11-19 |
| Dated rate-log observations | 34 records: 2026-11-16 (9), 2026-11-17 (17), 2026-11-19 (8) — a dated log, not one overwritten value |
| Flags with no URL anywhere | 0 of 101; duplicate flag ids: 0; flag ids cited on pages but undefined: 0 |
| Questions / rate-log / source-log rows without a source | 0 |
| Local links across all 27 `site/**/*.html` pages | 0 broken (164 local references checked) |
| `python3 scripts/data_source.py` rebuild | byte-identical to the committed `site/data.json` |

## 8. Gate results on this branch before the PR

- `scripts/verify_site.py`: **passed** — 341 events, 8 hotels, 56 routes, 50 sources, 101 flags, 7 plan days, 18 pages.
- `python3 -m unittest discover -s tests -p 'test_*.py'`: **334 tests OK** (PyYAML had to be installed into the sandbox
  for `test_workflows.py` / `test_pages_gate.py`; the Actions workflows already install it).
- `audit_951cd431.py` 0 failures / 0 warnings · `audit_data.py` · `verify_live_official.py` ·
  `verify_entry_labels.py` · `verify_transcription.py --dry-run` 44/44.
- `tests/canonical_smoke.py` (13 main + 5 detail pages), `node tests/canonical_render.js` (17 page renders),
  `node tests/walk_limit_render.js` (335 rows default, 329 with the ≤30-minute limit from The Venetian),
  `node --check` on all four JS assets.

## 9. Irregularities found by this pass

Three are new and are published as **F106, F107 and F108** in `scripts/data_source.py` (see the flag register and the
Flagged for review page). None of them changes a published tournament, fee, guarantee, rate, route or policy value:

- **F106** — the day plan's `primaryEnd` / `sessionMin` estimate is internally inconsistent with the stated method.
  The stated method is late-registration cut-off plus two 30-minute levels; for #9 on 24 November the published cut-off
  is 9:40 PM, which gives a 10:40 PM+ estimate, but the row publishes 10:55 PM and 345 minutes. For #10 on 25 November
  a 4:55 PM cut-off gives ~5:55 PM, but the row publishes 6:10 PM and 420 minutes. Four more rows repeat the pattern.
  Nothing official publishes a finish time (F16), so this is a consistency defect in a clearly-labelled estimate.
- **F107** — no reviewed official source prints a room-level **address with a street number or ZIP** for any of the
  eight properties; every hotel row is keyed to the property name only. The walking minutes (F84/F91) are therefore
  tied to a name-based Maps query, and the "official-address walking times" requirement cannot be fully evidenced.
- **F108** — `site/checks.json` (2026-11-19T07:34:30Z) records a content change on both Wynn booking-engine URLs
  (`reservations.wynnlasvegas.com/ibe/details.aspx…`) with text hashes that moved. No Wynn rate has ever been published
  for those URLs, so no row is wrong, but the changed page has not been re-read by a human and the Wynn hotel rows
  therefore remain a blank, flagged column.
