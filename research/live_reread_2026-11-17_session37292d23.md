# Live re-check record — session arena/37292d23-poker3, 2026-11-17 (UTC)

Scope: tasks R1 and R3 of this session's claim in COORDINATION.md. Every page below was
read live with the platform page reader (the sandbox cannot reach venue hosts over curl,
flag F40). Retrieval timestamps are approximate to the minute of the fetch.

## Part 1 — the two pages the scheduled monitor flagged as CHANGED (site/checks.json, run 2026-11-17T20:48:34Z)

### 1a. DeepStack Extravaganza NYE schedule page — CHANGED

URL: https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-dec-2026.html
Retrieved: 2026-11-17 ~22:00 UTC.

- Full transcription stored: `raw/dse_dec_2026_schedule_2026-11-17_37292d23.md` (49 rows).
- New comparator: `scripts/verify_nye_live.py` — result **49/49 printed rows agree with the
  published rows** on date, start time, event number, buy-in, printed guarantee, structure
  sheet number and full event name. Zero orphans in either direction.
- Five restart rows carry a guarantee the printed schedule row leaves blank; all five are
  disclosed by published flag F63, which the comparator requires.
- The printed `Saturday, December 26, 2025` rows (3) and the `Tuesaday` typo rows (2) are
  transcribed exactly as printed; flags F04/F41 cover the year typo.
- **One real drift found and corrected:** the published Seniors row (2027-01-10, event 31)
  ended at "Must be 50+ years of age" while the live page prints "Must be 50+ years of age
  to participate". The row name in `scripts/data_venetian.py` was corrected and
  `site/data.json` regenerated (byte-identical rebuild verified).
- No other published value on this page differs from the live text.
- The exact text delta behind the hash change cannot be reconstructed: the monitor stores
  only hashes, never a text snapshot. This is recorded as suggestion S-new (store a snapshot
  on change) rather than guessed.

### 1b. Venetian poker suite rates page — CHANGED

URL: https://www.venetianlasvegas.com/resort/casino/poker/suite-rates.html
Retrieved: 2026-11-17 ~21:57 UTC.

- Verbatim body stored: `raw/suite_rates_2026-11-17_37292d23.md`.
- Every published claim that cites this page was checked against the live text:
  - "These rates will start as low as $119 and $209 and can be higher." — verbatim match.
  - "six hours of active live cash gameplay or buy in to a $300 or higher tournament for
    each night stayed" — verbatim match.
  - "prior to 2 a.m. the last night stayed" → published "before 2 a.m. on the last night" — match.
  - "$55 resort fee per night stayed" — verbatim match.
  - "cannot be combined with any other promotional rates" — verbatim match.
  - "maximum of 150 days from the current date" — verbatim match.
  - booking code EPOKR25, phone 866.255.8936, poker room 702.414.7657 — verbatim match.
  - prevailing-rate repricing for any unqualified night — verbatim match.
- **No published value differs. No row required a change.**
- As with 1a, the hash delta is not reconstructable from hashes alone.

## Part 2 — re-read of the 17 URLs the GitHub runner could not reach on the same run

All 17 re-read with the page reader on 2026-11-17 ~21:57–22:15 UTC. Result per URL:

| # | URL | Runner result | Page-reader result | What it means for the published data |
|---|-----|---------------|--------------------|--------------------------------------|
| 1 | bellagio.mgmresorts.com/en/casino/poker.html | timeout | read OK | Weekly links (Fri $600, Sat $1,000, Sun $400 H.O.R.S.E.), the undated "July 26" resume notice (F03) and the three-way Saturday buy-in conflict (F02) are all still printed exactly as published. |
| 2 | bellagio.mgmresorts.com/en/hotel.html | timeout | read OK | Room catalogue, "Check Rates" links, no prices rendered statically. No published value affected. |
| 3 | bellagio.mgmresorts.com/en/terms-and-conditions.html | timeout | read OK | Resort fee "$55.00 plus applicable tax", the 72-hour cancellation window, the $165 mid-week / $200 weekend fee and the $150/day incidental hold are all printed on the page — consistent with the published Bellagio row. |
| 4 | mgmgrand.mgmresorts.com/en/casino/poker-tables.html | timeout | read OK | "Daily Texas Hold'em Tournaments 11:00am, 7:00pm and 11:00pm"; room open 24 hours; weekly schedule + structure links present. |
| 5 | mgmgrand.mgmresorts.com/en/hotel.html | timeout | read OK | Room catalogue, no prices rendered. No published value affected. |
| 6 | mgmgrand.mgmresorts.com/en/terms-and-conditions.html | timeout | read OK | Resort fee "$50.00 plus applicable tax", check-in 3:00 PM / check-out 11:00 AM, the $100/day incidental hold, the cancellation paragraph with the $110 mid-week / $155 weekend fee — consistent with the published MGM Grand row. |
| 7 | aria.mgmresorts.com/en/casino/poker.html | timeout | read OK | Still asks guests to confirm by phone / @ARIAPoker (F13 unchanged); no schedule times printed; room-rate phone 702.590.7232. |
| 8 | aria.mgmresorts.com/en/hotel.html | timeout | read OK | Room catalogue, no prices rendered. No published value affected. |
| 9 | aria.mgmresorts.com/en/terms-and-conditions.html | timeout | read OK | Resort fee "$55.00 plus applicable tax", check-in 3:00 PM / check-out 11:00 AM, the cancellation paragraph with the $165 mid-week / $200 weekend fee — consistent with the published ARIA row. |
| 10 | aria .../aria-casino-poker-gentlemans-guide.pdf | timeout | read OK (resolves to assets.contentstack.io) | Etiquette/terminology booklet only; no tournament data. |
| 11 | caesars.com/las-vegas/explore/casino/poker-tournaments-las-vegas-strip | 302 loop | read OK | Article dated July 17, 2026. Confirms Caesars Palace room 16 tables, open 24/7 with a "daily tournament slate"; Horseshoe Hall of Fame room open around the clock. Publishes no schedule, no buy-ins — nothing to add to event rows. |
| 12 | caesars.com/book/hotel-calendar?...Month=November&propCode=blv | 302 loop | read OK | No rate cells ("technical difficulties" banner); policy block confirms Resort fees "$56.63 ($49.95 plus $6.68 tax)", deposit $50/day — matches F37/Horseshoe row. |
| 13 | caesars.com/book/hotel-calendar?...Month=December&propCode=blv | 302 loop | read OK | Same banner, no cells; same fee policy block as #12. |
| 14 | caesars.com/book/hotel-calendar?...Month=December&propCode=clv | 403 | read OK | No rate cells (matches F15: Caesars Palace prints no cells); policy confirms "$62.30 ($54.95 plus $7.35 tax)", deposit $100/day — matches F37/Caesars Palace row. |
| 15 | caesars.com/caesars-palace/hotels | 302 loop | read OK (redirects to /caesars-palace) | Promo hero "Rooms from $186 $139" (Cyber Monday Early Access, terms apply) — a promotional lead-in price, not date-specific; recorded as an observation only, never as a rate (rule S19). "FREE 48-Hour Cancellation*" still advertised. |
| 16 | caesars.com/caesars-palace/hotel | 403 | read OK | "FREE 48-Hour Cancellation*" still advertised under Why Book With Us; widget default dates Jan 1–3 2027; no dated rate. Matches the published cancellation text. |
| 17 | caesars.com/horseshoe-las-vegas/hotels | 302 loop | read OK (redirects to /horseshoe-las-vegas) | Promo hero "Rooms from $61 $56" + "Free cancellation up to 48 hours before check-in" printed in the hero — the 48-hour window is now printed on the Horseshoe page itself, not only the asterisked badge. Promotional lead-in price, not date-specific; observation only. |

Summary: 17/17 re-read. Every published fee, cancellation and schedule value that these
URLs back is confirmed unchanged. Two cosmetic observations (Caesars promo hero prices)
are recorded here and in the rate-log note below; they are not rates and were not added
to any table as prices.

## Part 3 — R3 rate-log freshness (narrowed)

Session arena/fe903bcb already landed the dated Venetian quote for the fixed trip window
(PR #87) while this session was running; this session therefore adds **no** trip-window
quote. The only rate-reading observations from this session are the two Caesars promo hero
prices above, logged as observations in COORDINATION.md rather than as new rate-log rows,
because a lead-in "from" price is not date-specific and must not sit beside dated readings.

## Verification run after the changes in this note

- `python3 scripts/data_source.py` twice → byte-identical site/data.json.
- `python3 scripts/verify_nye_live.py` → 49/49, exit 0.
- `python3 -m unittest discover -s tests` → 102 tests OK (after adding this session's work;
  see COORDINATION.md for the final count).
- `python3 scripts/verify_site.py` → verification passed.
- `python3 scripts/verify_dse_full.py`, `scripts/verify_transcription.py`, smoke scripts → run at integration.
