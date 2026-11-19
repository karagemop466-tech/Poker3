# PDF source-monitor audit — 2026-11-19 UTC

Owner: `arena/09d32ea7-poker3`. This is a repository-code audit, **not** a new live source read or verification of a tournament, hotel rate, route, or policy.

## Finding and primary evidence

The [pre-fix checker at the session's base commit](https://github.com/karagemop466-tech/Poker3/blob/e79f5a62c41ef164882f1c9d299659964a62e69a/scripts/check_sources.py) implements its PDF `visible_text` branch by decoding the bytes as Latin-1 and deleting `stream.*?endstream`. It does not invoke a PDF text extractor. Text stored in a compressed content stream is therefore not part of its `textHash`. Its old regression test explicitly required two different stream bodies to hash identically.

This can miss changes inside a PDF stream, even if the changed item is a buy-in, guarantee, start time or entry rule. It does **not** establish that any official sheet actually changed. Existing dated manual read records are not invalidated by this code finding, but an automated historical `changed: false` or `wordingChanged: false` result is not independent evidence of unchanged PDF text.

## Repair

[Corrected checker](https://github.com/karagemop466-tech/Poker3/blob/main/scripts/check_sources.py):

- Identify PDFs by case-insensitive content type or `%PDF` signature, including a generic or absent content type.
- Compare SHA-256 of **all PDF response bytes**, without stripping, decoding, lowercasing or normalizing any bytes.
- Use the existing `hash` (already a raw-byte digest) as the PDF baseline, including for old records. Thus the first corrected run detects a changed document without comparing incompatible hash bases or blindly resetting the baseline.
- Mark PDF-byte changes `changed: true`, `wordingChanged: false`. A byte difference can be metadata only; it does not prove changed wording or any specific value. Never classify PDF-byte changes as `rawOnly` noise.
- Keep normalized HTML-text comparison unchanged. Identical comparable HTML text with different script/nonces can still be classified as raw-only noise.
- Publish per-row `hashBasis` and `comparisonKind`. For schema/UI compatibility, `textHash` holds the comparison digest, which for a PDF is the full-byte digest, **not extracted text**. Do not publish a PDF `textChars` count.
- Keep official-source data and manual verification dates untouched. The checker never promotes a field to verified.

No new extraction dependency is needed in Actions or locally. Full-byte comparison is deliberately conservative: it may cause more review alerts, but cannot silently discard a change in a compressed PDF stream.

## Reproduction and validation

`tests/test_pdf_monitor.py` constructs **synthetic** zlib/FlateDecode PDF content-stream fixtures. These are software test inputs, not source evidence for any event. Changing `Buy-in $300` to `Buy-in $400` leaves the two fixture byte lengths equal but changes the full PDF hash. Both fixtures would lose the changed content under the old stream-removal algorithm.

Coverage includes:

1. Compressed content changes with equal response length.
2. PDF signature detection with normal, generic, uppercase and absent MIME types.
3. Reuse of legacy raw-byte hashes for both changed and unchanged PDFs.
4. A true first baseline, without false change claims.
5. An unavailable PDF, without a false content-change claim.
6. Conservative alerting on metadata-only byte changes.
7. The complete recorder path, with a mocked PDF change and HTML script-only noise: published `changed` list/count, comparison method, absent fake text count and preserved transcription record.

`tests/test_check_sources.py` also replaces the incorrect stream-insensitivity expectation with a regression requiring changed PDF streams to move the hash.

Commands (offline; validate implementation and recorded evidence, not live official availability):

```sh
python3 -m venv .venv
.venv/bin/pip install PyYAML==6.0.3
.venv/bin/python -m unittest discover -s tests -p 'test_*.py'
python3 scripts/verify_site.py
python3 scripts/audit_951cd431.py
python3 scripts/verify_live_official.py
python3 scripts/audit_data.py
python3 scripts/verify_entry_labels.py
python3 scripts/verify_transcription.py --dry-run
python3 tests/canonical_smoke.py
node tests/canonical_render.js
node tests/walk_limit_render.js
python3 tests/smoke.py
```

## Limitations and publication

- The sandbox permits outbound connections only to GitHub and package hosts. No new official casino/hotel fetch or current-price confirmation was attempted or claimed here. Scheduled Actions runners perform the next live fetch after merge.
- Raw-byte hashes detect document differences, not which field changed. A PDF alert remains a request to re-read the official linked source.
- An unavailable request is not proof of an unchanged document. Read the per-source manual verification date and current fetch status separately.
- This repair does not supply the still-missing written one-entry/no-rebuy/no-add-on confirmations, comparable checkout totals for all hotels, or verified event finish times. Those remain review items on the existing dashboard.
- The operational finding is disclosed on [Flagged for Review](https://karagemop466-tech.github.io/Poker3/flagged.html#pdf-monitor-review) and next to the automated results on [Sources](https://karagemop466-tech.github.io/Poker3/sources.html). Old source-check observations are not retrospectively rewritten as fresh reads.
