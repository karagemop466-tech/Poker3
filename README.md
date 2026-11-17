# Vegas Poker Planner

Source-first Las Vegas Strip poker trip planner. The canonical GitHub Pages dashboard is in [`site/`](site/) and is
the only directory published by the Pages workflow.

**Published URL.** `https://karagemop466-tech.github.io/Poker3/` serves `site/`. The repository root's
`index.html` is a redirect into `site/`, because the Pages source is still the legacy `main /` setting
(the token used by the integration session cannot change it: `PUT /pages` returns 403) and GitHub's own
branch build would otherwise republish whatever sits at the root after every push. `.github/workflows/pages.yml`
re-deploys the `site/` artifact after that branch build finishes, so the serving copy is the verified
dashboard either way. See flag F29 on the Flagged for review page.

| Page | What it does |
|---|---|
| `site/index.html` | Executive summary: the fixed trip, the primary event per day, and what is and is not confirmed. |
| `site/tournaments.html` | Every published tournament row, with date, venue, category, written single-entry confirmation and sheet-candidate filters, plus per-row rules. |
| `site/search.html` | Global search across tournaments, hotel rows, dated rates, walking routes, sources, questions and review flags. |
| `site/venues.html` | One page per Strip poker room, each with its events and its hotels (`browse.html?view=venue&key=…`). |
| `site/calculator.html` | *Estimated cost of a trip* = entries × buy-ins + nights × true hotel cost, computed from the published components, with a like-for-like comparison of the eight entries and seven nights at each published rate. |
| `site/browse.html` | Venue and category subpages, so a bounty event is never mixed in with a plain freezeout. |
| `site/schedule.html` | A provisional sheet-screened candidate per day, conditional fallback, recurring room events and estimated overlap flags; none is strict-entry confirmed. |
| `site/hotels.html` | Published rate components, the mandatory resort fee, tax, true cost per night, parking, cancellation deadlines, walking times, one official booking deep link per trip night, the dated quote log and the dated rate log. |
| `site/questions.html` | The information still needed before booking, each with the official source behind the answer. |
| `site/suggestions.html` | Proposed improvements with impact, effort and the decision each one needs. |
| `site/flagged.html` | Every irregularity and unverified value, each with a link for manual review (31 items). |
| `site/sources.html` | The official source log, every structure sheet with its read status, the morning feed sources and the automated re-check results. |

## Evidence policy

Only official venue and property pages and official PDFs substantiate a value. A structure sheet that prints one buy-in,
one start flight and no re-entry, rebuy, add-on or second-flight clause is **sheet-screened only**: it does not prove a
maximum number of entries per player, so no candidate is treated as strictly eligible until the venue confirms the
one-entry, no-rebuy and no-add-on rules in writing (flag F31). Each row carries the exact excerpt, source and retrieval
date. A row with a blank fee or guarantee is always explained by a note or a flag. Guaranteed-pool ÷ entry-fee is
descriptive, never a forecast. Walking minutes are Google Maps estimates, because no venue publishes a walking time.

Values were first read on **2026-11-16**; every official page and PDF was re-read and re-confirmed on **2026-11-17**.
Both dates are carried on every row: `lastChecked` is when the value was read, `lastVerified` is when it was last
confirmed still true. All 52 structure sheets (37 DeepStack Extravaganza IV + 15 DeepStack NYE) have been read in full.

## Data pipeline

```sh
python3 scripts/data_source.py        # rebuilds site/data.json from the source modules
```

| Module | Contents |
|---|---|
| `scripts/data_venetian.py` | The 64 official DeepStack Extravaganza IV rows, the NYE rows, and the facts read from all 37 DSE IV structure PDFs. |
| `scripts/data_venues.py` | Wynn daily, WPT and Signature Series rows, Bellagio, MGM Grand, Caesars Palace, Horseshoe and ARIA room events. |
| `scripts/data_hotels.py` | Hotel components, the dated rate log and the walking-route estimates. |
| `scripts/data_source.py` | Assembles `site/data.json`, the fixed trip profile, the day plan and the conflict flags. |

`research/structure_notes.md` records the read log for all 37 DSE IV structure PDFs. The 15 NYE sheets were read on
2026-11-17 and their facts live in `NYE_SHEETS` in `scripts/data_venetian.py`; three of them print an explicit re-entry
sentence and are therefore *not* labelled single entry.

`site/data/venetian_pdf_rows.json` is a hand transcription of the official series PDF for the rows inside the trip
window (44 rows). `scripts/verify_transcription.py` compares it with `site/data.json` on every run and a unit test fails if any
date, start time, registration cut-off, guarantee, chip count or level length drifts.

`research/reread_2026-11-17.json` is the live re-read of the 13 trip-window rows (Nov 25 – Dec 2, 2026) and the seven structure sheets behind them, dated 2026-11-17. `tests/test_reread_2026_11_17.py` fails if the published rows drift from it.

## The 2026-11-17 re-verification pass

Every DeepStack Extravaganza IV row was re-read against a fresh capture of the official schedule page
(`raw/dse_nov_2026_schedule_html_2026-11-17.md`) and cross-checked against the official schedule PDF
(`raw/venetian_dse_nov_2026_schedule.md`). All 94 rows agree on date, time, event number, event name, structure-sheet
link, printed buy-in and printed guarantee. Eleven canonical names were truncated relative to the page and were
corrected; the rest already matched.

The official booking engine was re-opened on the same day. It priced the same November 17-19 stay at **$1,015.89**,
against **$1,245.48** the day before, and quoted November 20-22 at **$2,504.00**. All three reconcile exactly with
`(rate + $55 resort fee) x 1.1338`, confirming that the 13.38% Clark County room tax applies to the rate and to the
resort fee together. Four stay windows inside the recommended trip dates returned no suite and no price.

Two official-source irregularities came out of the pass and are published on the Flagged page: the schedule PDF prints
decorative sponsor art instead of a date on 20 rows (F46), and the booking calendar's cells change value with the stay
window that is open, so no calendar cell is ever used as a price (F47).

`raw/official_excerpts_2026-11-17.md` holds the verbatim official text behind the hotel and Wynn daily-tournament
values, and `scripts/verify_live_official.py` asserts them on every CI run.
>>>>>>> a1af876 (Sync the narrative with the 2026-11-17 findings)

## Scheduled checks

`.github/workflows/checks.yml` is the single scheduled job that reviews official sources at 12:10 UTC
(04:10 PST / 05:10 PDT, the morning pull) and can be dispatched by hand. It also carries a push trigger on its own
file and on the two recorder scripts, so a change to the monitoring setup runs the job immediately instead of waiting
for the cron (a change to one workflow file cannot trigger a different workflow — the earlier attempt routed this
through `source-monitor.yml`, which only starts the poker3 companion monitor). It runs two recorders in order:

- `scripts/check_sources.py` fetches every official URL behind the dashboard, stores a SHA-256 of the response, and flags
  any source whose body changed. A URL it cannot reach is recorded as `unavailable`, never as "changed".
- `scripts/verify_transcription.py` re-checks the 44 transcribed series-PDF rows against the published data and writes the
  result beside the URL record.

Neither script changes a tournament value on its own: a changed page is re-read by a human first. Both results are
published as `site/checks.json` and shown on the sources page, and the URL recorder creates the file if it does not exist,
so a single unreachable PDF can never abort the run.
- `scripts/daily_feed.py` pulls the schedule page of each Strip poker room and writes a dated snapshot under
  `site/feed/`, so a morning run can be compared with the previous morning instead of replacing it.
- The job then rebases onto `origin/main` and pushes, retrying up to five times, so a race with another scheduled
  run cannot lose the record.

It replaces three overlapping committers (`monitor.yml`, `daily-check.yml` and an earlier version of this one) that
ran on separate crons under separate concurrency groups and overwrote each other; none of the three had ever produced
a run. `source-monitor.yml` shares the same concurrency group so the two jobs are serialised. Flag F30 records this.

Unit tests in `tests/test_integrity.py` assert the arithmetic a reader acts on — the dated quote's two nights
reconciling to the printed total, the `$197.28` nightly floor, `ratio = guarantee / buy-in` on every row, a
`lastChecked` date on every row — and `verify.yml` runs them, so a later edit cannot quietly reintroduce a wrong
number.

## Run locally

```sh
python3 -m http.server 8000 --directory site
```

Then open `http://localhost:8000`.

## Verification

```sh
python3 scripts/verify_live_official.py  # canonical rows vs the official schedule page and schedule PDF,
                                        #   the hotel values vs the official excerpts, and the quote arithmetic
python3 scripts/audit_data.py            # every structure-sheet value vs the read log
python3 scripts/verify_site.py           # official-source, blank-value and link checks over site/data.json
python3 tests/canonical_smoke.py       # page structure plus a headless render check of every page
node --check site/assets/app.js
python3 -m json.tool site/data.json
```

`.github/workflows/verify.yml` runs all of these on every pull request and push to `main`.

## Prior-session artefacts

The repository also keeps earlier dashboards from merged parallel sessions: `docs/`, `verified/`, `planner/`,
`single-entry/`, the root-level pages, and `site/poker3/`. They are prior research artefacts with their own unresolved
rows and flags. They are not the canonical site and are not used as evidence for `site/data.json` unless re-checked
against the venue source. `site/poker3/` is still published at `/poker3/` because it lives inside the Pages artifact;
its conclusions predate this build and are more conservative, so treat it as an archive rather than as current data.

See [`COORDINATION.md`](COORDINATION.md) for ownership, the official source register, the integration history, the
verification record and the open review flags.

### Prior-session artefacts kept in the repository

`site/poker3/` adds a separate, source-linked Las Vegas field guide with tournament filters, a cautious date planner, room schedules, a sample hotel/fee comparison, route estimates, and a flagged-review register. The current live Pages setting still reports legacy `main`-root publishing, so the verified public path is [`/site/poker3/`](https://karagemop466-tech.github.io/Poker3/site/poker3/); the canonical dashboard at `/` is preserved. The existing Actions workflow uploads `site/`, where the same companion is available at `/poker3/` if Pages is switched to that source. The Dec. 10–14, 2026 two-adult hotel window is a research sample, not user-provided travel dates, and no strict-entry event is verified.

Run `python3 tests/smoke.py` to validate this companion. When serving the repository's `site/` directory locally, open `http://localhost:8000/poker3/`.

## Strip planner pages (session e125b4a2)

`planner/` holds this session's pages: landing page, Venetian DeepStack Extravaganza IV single-entry table with per-row official source links, re-entry table, hotels, schedule, executive summary, suggestions, Q&A, and flagged-for-review. Research tables behind them are in `data/tournaments.md`, `data/hotels.md`, `data/schedule.md`, and `pages/*.md`. These files are **not** published by `.github/workflows/pages.yml`, which deploys only `site/`. Publishing `planner/` would need a user decision.

## Single-entry site (session arena/d205f8ec-poker3)

`single-entry/` holds the single-entry Strip tournament planner: 1-day main list (53 rows; 47 cash events plus 5 satellites and 1 two-day event, each labelled), excluded events, hotel true-cost formula, schedule, questions, suggestions and flagged-for-review. Start at `single-entry/index.html`. Every row links an official Venetian source; all 22 main-list structure sheets were read in full. Single entry is not printed on those sheets, so the page says "no re-entry or add-on wording", not "single entry confirmed". This folder is **not** published by `.github/workflows/pages.yml` (which deploys only `site/`). Publishing it needs a user decision.

## Handoff folder from session aa084881

`handoff/aa084881/` holds a verified dataset and generator that were deliberately kept out of the published site:
`site_data.py` (every value with its official URL), `build_site.py`, `verify_site.py`, a generated `data.json` and a
README describing what can be imported. The dated Venetian booking-engine quote it recorded (November 17-19, 2026,
two adults, $1,245.48 including $146.98 of tax) was re-read and imported into the canonical rate log by the
integration session; the rest of the handoff is kept for audit.
