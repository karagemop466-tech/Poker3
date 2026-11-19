# Line-by-line verification · 2026-11-19 · session `arena/8194609f-poker3`

**Method.** Every URL below was fetched and read live on 2026-11-19 UTC through the platform fetch tool.
Only official venue/property pages and official PDFs are used as evidence for a value. Third-party pages are
never used to fill a value. A value that an official page does not print stays blank and is flagged. No value
in `site/data.json` was changed by automation; this session's reads are a re-verification of published values.
The scheduled re-check record (`site/checks.json`, generated 2026-11-19T06:15:40+00:00) reports 107 URLs,
85 fetched, 0 changed, 8 bot-blocked, 14 unavailable, 22 failed — those unreachable URLs were read by hand by
earlier sessions and are still flagged on the Flagged for review page.

**Result.** No published tournament, fee, guarantee, hotel, rate, route or policy value changed. Two repository
irregularities were found and fixed (see §4). Four legacy venue subpages carried stale hardcoded statements that
contradicted the canonical data; they were corrected (see §4, flag F100). A third irregularity (five unlinked
stale snapshot JSON files still published under `site/data/`) is flagged as F101 rather than deleted, because another
session's script still names one of them. The orphan conflict markers were already recorded as F98 by a parallel
session on main by the time this branch rebased, so no duplicate flag was added here.

---

## 1. Official sources read this session (verbatim excerpts)

| # | Official source (URL) | Verbatim text read 2026-11-19 | Value it confirms | Published field |
|---|---|---|---|---|
| 1 | [Venetian DeepStack Extravaganza IV November schedule](https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html) (all 4 chunks) | "**November 16 – December 23, 2026**"; "More than $3.6 Million in guaranteed tournament prize pools"; 94 dated rows, e.g. "Friday, November 27, 2026 \| 11:10 AM \| 14 \| $600 No Limit Hold'em $30K GTD (1Day)" | Series dates, all 94 rows, start times, buy-ins, guarantees, structure-sheet links | `events` (Venetian DSE IV) |
| 2 | [Venetian 2026 poker suite rates](https://www.venetianlasvegas.com/resort/casino/poker/suite-rates.html) | "These rates will start as low as $119 and $209 and can be higher." / "There is a $55 resort fee per night stayed." / "During your stay, you will be required to play six hours of active live cash gameplay or buy in to a $300 or higher tournament for each night stayed. ... These requirements must be met prior to 2 a.m. the last night stayed." / "calling 866.255.8936 and mentioning code EPOKR25" | $119/$209 starting rates, $55 fee, play qualification, EPOKR25 | `hotels[venetian].baseRateFloor/baseRateCeiling`, `rateLog` |
| 3 | [Venetian resort fee page](https://www.venetianlasvegas.com/resort/resort-fee.html) | "Rates include a daily Resort Fee of $55 plus tax per night, payable upon check-in." | $55 resort fee, plus tax | `hotels[venetian].resortFee` (conflict with terms wording = F51) |
| 4 | [Venetian hotel terms](https://www.venetianlasvegas.com/legal/hotel-terms-and-conditions.html) (both chunks) | "Daily rates do not include the applicable Clark County Room Tax of 13.38%." / "The Venetian Resort has a standard Las Vegas Resort Fee of $55 plus applicable tax per night, payable upon check-in." / "Check-out time is 11:00 a.m." / "The daily fee for registered hotel guests is $20/day, seven days a week. For non-hotel guests, the fee is $20, Monday – Thursday, and $25/day Friday – Sunday. Valet parking is $40/day." / "Check-out prior to your scheduled departure date will result in an additional charge of $100 plus tax." | 13.38% tax, $55 fee, 11:00 checkout, parking, early-checkout fee, cancellation/deposit terms | `hotels[venetian].taxRate`, `parking`, `cancellation` |
| 5 | [Venetian poker-room parking](https://www.venetianlasvegas.com/resort/casino/poker/player-parking.html) | "Players in the poker room who play three hours or more in tournament or cash games will receive complimentary self-parking for the day. Players must visit a supervisor at the end of their session to confirm qualifications for complimentary self-parking." | Conditional 3-hour parking waiver | `hotels[venetian].parkingWaiver` |
| 6 | [Venetian structure sheet 7](https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_7.pdf) | "**Start Time:** 11:10 AM"; "**Starting Chips:** 40,000"; "**Level Duration:** 30 minutes."; "**Late Registration:** 10 levels + Break (~ 4:55 PM)"; "**Guarantee:** $30,000 for Event #14 and #63"; "$90 of the $600 Buy-In is withheld for house fees (Rake + Staff). The prize pool consists of $510 of every $600 Buy In."; "This event pays 12.5% of the field" | Nov 27 primary: $600, $30K, 40,000 chips, 30-min levels, 4:55 PM reg close, 12.5% paid | `events[vl-dse-2026-11-27-14-1110am]` |
| 7 | [Venetian structure sheet 6](https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_6.pdf) | "## Event Number: 10"; "**Start Time:** 11:10 AM"; "**Starting Chips:** 40,000"; "**Guarantee:** $15,000"; "**Late Registration:** 10 levels + Break (~ 4:55 PM)"; "$65 of the $400 Buy-In is withheld for house fees (Rake + Staff)." | Nov 25 primary: $400, $15K, 40,000 chips, 30-min levels | `events[vl-dse-2026-11-25-10-1110am]` |
| 8 | [Venetian structure sheet 1](https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_1.pdf) | "**Start Time:** 5:10 PM"; "**Starting Chips:** 25,000"; "**Late Registration:** 8 levels + Break (9:40 PM)"; "**Guarantee:** $8,000 (prize pool + total bounties)"; "$40 of the $200 Buy-In is withheld for house fees"; "Players receive $50 bounty for each player they eliminate"; "A Prize Pool of $8,000 is guaranteed by the Venetian Poker Room which consists of the actual prize pool plus the total amount of $50 bounties" | Evening bounty rows, bounty-inclusive guarantee, 9:40 PM reg close | `events` sheet-1 rows; bounty label |
| 9 | [Venetian DeepStack Extravaganza II (April 2023)](https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-apr-2023.html) | Event 13: "$400 NLH MonsterStack ThrowBack $20K GTD (1Day)**One Entry Only with One Hour of Registration**" | The venue's schedule vocabulary *does* include a one-entry label when it intends one; the 2026 series prints none on any row → F31 stays open | flag F31 |
| 10 | [Wynn poker room](https://www.wynnlasvegas.com/casino/poker) | "### WPT WORLD CHAMPIONSHIP ### November 27–December 21"; "New for 2026, the Super Gold Million brings a $400 buy-in featuring a $3,000,000 guarantee!"; "WYNN SIGNATURE SERIES ### January 11–24. 2027"; "Tournaments include the $40,000 guaranteed NLH Rebuy on Friday and a $10,000 guaranteed event every evening at 6 p.m." | Series windows, $400/$3M, Friday rebuy (extra-spend), daily $10K 6 p.m. | Wynn rows; `extra` category |
| 11 | [Wynn resort policies](https://www.wynnlasvegas.com/about-us/resort-information) | "Check In: 3 p.m." / "Check Out: 12 p.m." / "Reservations will be charged a daily resort fee of $55 plus tax." | $55 fee, check-in/out | `hotels[wynn].resortFee`, `cancellation` context |
| 12 | [Wynn parking](https://www.wynnlasvegas.com/about-us/parking) | "The daily parking fee for non-registered guests is $25 per day with the first three (3) hours complimentary."; "Complimentary self-parking is extended to Wynn Poker Room guests (please visit the Poker Room for details)"; "Valet parking is $40 per day up to 24 hours" | Wynn parking figures | `hotels[wynn].parking` |
| 13 | [Bellagio hotel reservation terms](https://bellagio.mgmresorts.com/en/terms-and-conditions.html) | "A daily resort fee of $55.00 plus applicable tax will be applied to all reservations."; "The first night's deposit is fully refundable provided a timely notice of cancellation is received by Room Reservations at 888.987.6667 at least 72 hours prior to the arrival date" | $55 fee, 72-hour cancellation | `hotels[bellagio]` |
| 14 | [Bellagio poker page](https://bellagio.mgmresorts.com/en/casino/poker.html) | "SATURDAYS \| $1,000 NLH" (link labelled $1,000) | Source of the Saturday link label in conflict F02 | flag F02 |
| 15 | [Bellagio Saturday NLH structure PDF](https://assets.contentstack.io/v3/assets/bltc6ce635bc4868eb2/blt6d47974bf5a7d9b6/6af491a391a6e8e4230c9e07/mgm-bellagio-poker-saturdays-$1000-nlh.pdf) | "## NLH $1100 BUY-IN"; "7. Of the $600 Buy-in, $510 goes to the Prize Pool, $50 is Admin Fees and $40 is optional staff gratuity."; "1. Players start with 40,000 in tournament chips (20,000 + 20,000 optional)." | Three conflicting buy-ins ($1,000 page / $1,100 header / $600 body); optional paid chip boost → excluded from single-entry path | flag F02, `extra` |
| 16 | [Caesars Palace / Horseshoe Strip poker article](https://www.caesars.com/las-vegas/explore/casino/poker-tournaments-las-vegas-strip) | "You will find four No-Limit Hold'em tournaments each day at 10 a.m., 2 p.m., 6 p.m. and 9 p.m. Every event carries a $100 buy-in, starts you with 20,000 chips, and features a $1,000 guaranteed prize pool. ... a $50 add-on at the first break gives you an extra 15,000 chips" | Article's "every event $100" + $50 add-on | flag F90 |
| 17 | [Caesars Palace daily NLH flyer 2026](https://www.caesars.com/content/dam/empire/clv/casino/poker/tournament-schedule/clv-poker-daily-nlh-tournament-flyer-2026.pdf) | Table: "10 AM \| $100", "2 PM \| $160", "6 PM \| $100", "9 PM \| $160", each "Add-On Optional $50"; "Participants may only register themselves, but may re-enter, by paying the entry fee, upon elimination within the first break of play." | $160 buy-ins, explicit re-entry, $50 add-on → extra-spend section | flag F90, Caesars rows |
| 18 | [Clark County transient lodging guide](https://www.clarkcountynv.gov/adobe/assets/urn:aaid:aem:689ef54f-ec0d-4bb6-b8ea-05a82887561f/original/as/genl-info-guide-for-tles-july-2021.pdf) (Appendix III, chunks 7 and 9) | e.g. "\| 1000172.RES-001 \| Luxor Hotel And Casino \| ... \| 13.38% \| RES \| 1 \| Transient Lodging Tax - Resort Hotel (PGC) \|"; "\| 1000109.RES-001 \| Rio Suite Hotel & Casino \| ... \| 13.38% \| RES \| 1 \| ... \|" | 13.38% resort-hotel rate in the Primary Gaming Corridor (corroborates Venetian terms) | `hotels[*].taxRate` |
| 19 | [Venetian DSE IV series index](https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament.html) | Series banner rolls to DeepStack Extravaganza IV (prior session F92 re-read; no value changed) | F92 resolution | flag F92 |

---

## 2. Trip-window rows: live official page vs published dataset

Nineteen rows fall in 23–30 November 2026 on the live official November schedule. Each was compared on
**date, start time, event number, printed buy-in, printed guarantee and structure-sheet filename**. All 19
agree; no row is missing and none is invented. Source for every row:
[official DSE IV November schedule](https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html).

| Date | Time | Event # | Official name (abbreviated) | Buy-in | Guarantee | Sheet | Published row | Result |
|---|---|---|---|---|---|---|---|---|
| 2026-11-23 | 11:10 AM | 7 | $400 NLH 1A $75K GTD | $400 | $75,000 | structure_2 | `vl-dse-2026-11-23-7-1110am` | match |
| 2026-11-23 | 5:10 PM | 8 | $200 NLH $8K GTD PKO | $200 | $8,000 | structure_30 | `vl-dse-2026-11-23-8-510pm` | match |
| 2026-11-24 | 11:10 AM | 7 | $400 NLH 1B $75K GTD | $400 | $75,000 | structure_2 | `vl-dse-2026-11-24-7-1110am` | match |
| 2026-11-24 | 5:10 PM | 9 | $200 NLH Bounty $8K GTD | $200 | $8,000 | structure_1 | `vl-dse-2026-11-24-9-510pm` | match |
| 2026-11-25 | 11:00 AM | 7 | $400 NLH Day 2 Restart | $400 | $75,000 | structure_2 | `vl-dse-2026-11-25-7-1100am` | match |
| 2026-11-25 | 11:10 AM | 10 | $400 NLH $15K GTD | $400 | $15,000 | structure_6 | `vl-dse-2026-11-25-10-1110am` | match |
| 2026-11-25 | 5:10 PM | 11 | $200 NLH Bounty $8K GTD | $200 | $8,000 | structure_1 | `vl-dse-2026-11-25-11-510pm` | match |
| 2026-11-26 | 11:10 AM | 12 | $300 NLH $10K GTD | $300 | $10,000 | structure_5 | `vl-dse-2026-11-26-12-1110am` | match |
| 2026-11-26 | 5:10 PM | 13 | $200 NLH Bounty $8K GTD | $200 | $8,000 | structure_1 | `vl-dse-2026-11-26-13-510pm` | match |
| 2026-11-27 | 11:10 AM | 14 | $600 NLH $30K GTD | $600 | $30,000 | structure_7 | `vl-dse-2026-11-27-14-1110am` | match |
| 2026-11-27 | 5:10 PM | 15 | $200 NLH Bounty $8K GTD | $200 | $8,000 | structure_1 | `vl-dse-2026-11-27-15-510pm` | match |
| 2026-11-28 | 11:10 AM | 16 | $600 NLH Bounty $30K GTD | $600 | $30,000 | structure_11 | `vl-dse-2026-11-28-16-1110am` | match |
| 2026-11-28 | 12:10 PM | 17 | $400 PLO Bounty $15K GTD | $400 | $15,000 | structure_26 | `vl-dse-2026-11-28-17-1210pm` | match |
| 2026-11-28 | 5:10 PM | 18 | $200 NLH PokerAtlas Valuetown Bounty $20K GTD | $200 | $20,000 | structure_8 | `vl-dse-2026-11-28-18-510pm` | match |
| 2026-11-29 | 11:10 AM | 19 | $400 NLH 1A $75K GTD | $400 | $75,000 | structure_3 | `vl-dse-2026-11-29-19-1110am` | match |
| 2026-11-29 | 12:10 PM | 20 | $300 PLO $10K GTD Double Board Bomb Pot | $300 | $10,000 | structure_22 | `vl-dse-2026-11-29-20-1210pm` | match |
| 2026-11-29 | 5:10 PM | 21 | $200 NLH Bounty $8K GTD | $200 | $8,000 | structure_1 | `vl-dse-2026-11-29-21-510pm` | match |
| 2026-11-30 | 11:10 AM | 19 | $400 NLH 1B $75K GTD | $400 | $75,000 | structure_3 | `vl-dse-2026-11-30-19-1110am` | match |
| 2026-11-30 | 5:10 PM | 22 | $200 NLH Bounty $8K GTD | $200 | $8,000 | structure_1 | `vl-dse-2026-11-30-22-510pm` | match |

**Live page also confirms what is *not* printed:** no "one entry", "freezeout", "maximum entries", re-entry
clause or finish time on any 2026 row. The 8 AM all-day route therefore remains unsupported (F17/F31/F16).
The 30 November 11:00 a.m. checkout (official terms, read #4 above) means that day is a departure day.

---

## 3. Requirement audit

A machine-readable, 40-row line-by-line audit of **every requirement in the brief** — with the page that
implements it, the evidence, and the official source links — is published at
[`site/verification.html`](../site/verification.html) and stored in `site/data.json` under
`verification`, `verificationReads` and `verificationRows` (built by `scripts/data_verification.py`).
Every audit row carries at least one link; process rows link the repository file that is the evidence.

Verification performed on the integrated site before publication:

- `python3 scripts/verify_site.py` — every event/hotel/route row has a `lastChecked` date and an official
  source link; every rule record has an excerpt, source and retrieval date; blank fees/guarantees are explained.
- `python3 -m unittest discover -s tests -p 'test_*.py'` — full regression suite.
- `python3 scripts/audit_951cd431.py`, `audit_data.py`, `verify_live_official.py`, `verify_entry_labels.py`,
  `verify_transcription.py --dry-run` — independent re-derivation and label checks.
- `python3 tests/canonical_smoke.py`, `node tests/canonical_render.js`, `node tests/walk_limit_render.js`,
  `node --check` on all JS assets — render and syntax checks.
- A local-link scan over all `site/**/*.html` — zero broken internal links.
- `python3 scripts/data_source.py` followed by `git diff --exit-code -- site/data.json` — byte-identical rebuild.

---

## 4. Irregularities found and what was done

| ID | Irregularity | Evidence / manual-review link | Action |
|---|---|---|---|
| F100 | Four legacy venue subpages (`site/venues/index.html`, `venetian.html`, `wynn.html`, `others.html`) published stale hardcoded claims that contradict the canonical data: "the NYE rows stay unverified" (there are zero unverified rows and all 52 sheets were read), "no date-specific room quote exists" (dated checkout totals exist for both Venetian and Wynn), "the only dated checkout total found is ... $1,245.48" (superseded by $1,015.89 and the 23–30 Nov $4,010.55 / $3,823.46 quotes), and footers/side notes dated 2026-11-16. | [Venetian suite rates](https://www.venetianlasvegas.com/resort/casino/poker/suite-rates.html), [Venetian booking engine for the trip window](https://www.venetianlasvegas.com/booking?adults%5B%5D=2&arrival_date=2026-11-23&children%5B%5D=0&departure_date=2026-11-30&view=calendar), [Wynn reservations engine](https://reservations.wynnlasvegas.com/ibe/details.aspx?hotelID=13763&langID=1&rmID=68658&checkIn=11/23/2026&checkOut=11/30/2026), [repo file](https://github.com/karagemop466-tech/Poker3/blob/main/site/venues/venetian.html) | Corrected the four pages to match `site/data.json`, added official source links, dated them 2026-11-19. A unit test now fails if the stale phrases return. |
| F98 | `COORDINATION.md` contained two orphan git conflict-marker lines (`>>>>>>> 609f1ce …` and `>>>>>>> c14bb08 …`) left in the file by a prior rebase. They were inert in Markdown but would mislead a reader and could break a tooling diff. | [COORDINATION.md](https://github.com/karagemop466-tech/Poker3/blob/main/COORDINATION.md) | Marker lines removed in the claim commit; every session's text was kept verbatim. |
| F101 | Five unlinked 2026-11-16 snapshot JSON files (`site/data/flags.json`, `questions.json`, `sources.json`, `suggestions.json`, `tournaments.json`) are still published by the Pages artifact and give a second, stale answer if opened directly. No dashboard page reads them; `scripts/daily_check.py` still names `sources.json` but is not the scheduled checker. | [site/data/flags.json](https://github.com/karagemop466-tech/Poker3/blob/main/site/data/flags.json) | Flagged for review rather than deleted, so another session's script is not broken. The integration owner should retire them or add a dated note. |
| F02 | Bellagio Saturday buy-in is printed three ways across official sources: the poker page links "$1,000 NLH", the linked PDF header reads "$1100 BUY-IN" and its fee allocation says "$600 Buy-in". | [Bellagio poker](https://bellagio.mgmresorts.com/en/casino/poker.html), [Saturday PDF](https://assets.contentstack.io/v3/assets/bltc6ce635bc4868eb2/blt6d47974bf5a7d9b6/6af491a391a6e8e4230c9e07/mgm-bellagio-poker-saturdays-$1000-nlh.pdf) | Re-confirmed 2026-11-19; monetary field stays blank and flagged. |
| F90 | Caesars article says "Every event carries a $100 buy-in"; the official flyer prints $160 at 2 p.m. and 9 p.m. and an explicit re-entry clause plus a $50 add-on. | [Article](https://www.caesars.com/las-vegas/explore/casino/poker-tournaments-las-vegas-strip), [flyer](https://www.caesars.com/content/dam/empire/clv/casino/poker/tournament-schedule/clv-poker-daily-nlh-tournament-flyer-2026.pdf) | Re-confirmed 2026-11-19; Caesars rows stay in the extra-spend section, never the single-entry path. |
| F51 | Two official Venetian pages describe the $55 resort fee differently ("Rates include a daily Resort Fee of $55 plus tax" vs "Daily rates do not include ... Room Tax of 13.38%" and "standard Las Vegas Resort Fee of $55 plus applicable tax"). | [Resort fee page](https://www.venetianlasvegas.com/resort/resort-fee.html), [hotel terms](https://www.venetianlasvegas.com/legal/hotel-terms-and-conditions.html) | Re-confirmed 2026-11-19; site uses the fee-on-top reading and keeps the conflict flagged. |
| F31 | No 2026 official page prints a maximum number of entries per player, while the same venue's April 2023 schedule does print "One Entry Only with One Hour of Registration". | [2026 DSE IV schedule](https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html), [2023 DSE II schedule](https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-apr-2023.html) | Re-confirmed 2026-11-19; "single-entry / freezeout confirmed" filter correctly shows zero rows until written confirmation exists. |
| F17 / F16 | No official 8 AM start; no official finish time. | [2026 DSE IV schedule](https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html), [sheets 1/6/7](https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_7.pdf) | All-day-from-8-AM route not built; overlap flags are labelled estimates. |

---

## 5. Links for manual review

- Live dashboard: <https://karagemop466-tech.github.io/Poker3/>
- Flagged for review: <https://karagemop466-tech.github.io/Poker3/flagged.html>
- Verification & requirements audit: <https://karagemop466-tech.github.io/Poker3/verification.html>
- Official source log: <https://karagemop466-tech.github.io/Poker3/sources.html>
- Shared task board: [COORDINATION.md](https://github.com/karagemop466-tech/Poker3/blob/main/COORDINATION.md)
- Automated re-check record: [`site/checks.json`](../site/checks.json) (107 URLs, last run 2026-11-19T06:15:40Z)
- Morning-room-feed record: [`site/feed/index.json`](../site/feed/index.json)
