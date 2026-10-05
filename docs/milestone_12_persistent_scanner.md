# Milestone 12 - Persistent Scanner Architecture

## Freeze status

**OPEN - HIGHER-TIMEFRAME MATERIALIZATION ACCEPTANCE IN PROGRESS**

- Frozen architecture version: `persistent-all-nse-scanner-v1`
- Base/Daily storage compatibility: `milestone-12.2-resumable`
- Derived EOD materialization compatibility:
  `milestone-12.3-derived-core-timeframes`
- Default production universe: `allnse`
- Current official NSE Main Equity instruments: 2,559
- Canonical methodology remains independently frozen and unchanged.

The previous freeze was reopened after higher-timeframe runtime acceptance
failed. Milestone 12 currently preserves persistent OHLCV, completed scanner snapshots,
per-symbol methodology/data-revision checkpoints, resumable leased jobs,
incremental refresh, atomic last-known-good publication, and isolated
universe/timeframe materializations. READY reads remain database/cache reads;
refresh work remains bounded and asynchronous. It is not frozen again until
All-NSE Daily, Weekly, Monthly, Quarterly, Half-yearly and Yearly switching is
validated from READY persisted materializations.

## Canonical persisted Daily source

- Source semantics version: `yahoo-adjusted-daily-v1`
- Intended historical period: the existing higher-timeframe path's `10y`
- Provider adjustment: Yahoo `auto_adjust=True`, now explicit rather than
  inherited from a library default. Splits and dividend adjustments therefore
  follow Yahoo's adjusted OHLC series; reported volume is persisted as supplied.
- Session timestamps are normalized by the existing provider/store boundary.
- Malformed rows are rejected. Valid zero-range rows remain explicit data-break
  boundaries. No missing session is invented or interpolated.
- Full-history completion is checkpointed per symbol and semantics version.

Weekly, Monthly, Quarterly, Half-yearly and Yearly candles are derived only
from that persisted Daily source. Aggregation is first Open, maximum High,
minimum Low, last Close and summed Volume. Buckets are Friday-ended weeks and
Indian-market calendar month/quarter/half-year/year periods over the actual
sessions present in the source. Exchange holidays therefore introduce no fake
rows. The incomplete current bucket remains included, matching the pre-existing
local aggregation behavior and protected by regression tests.

The query contract is filters first, then global allow-listed numerical sort,
deterministic tie-breaking by contextual rank and stable zone identity, and
pagination last. An explicit user sort is presentation ordering only. With no
explicit sort, the frozen contextual ranking remains authoritative. A sort
change resets the client to page 1, and server-paginated rows are never locally
re-sorted.

The Stock Details data path remains tied to persisted provider candles and the
same frozen canonical zone identity used by scanner snapshots.

## Current implementation

The canonical scanner remains the only calculation path. Milestone 12 wraps its
unchanged `ZoneResearchResponse` in a versioned persistent snapshot store.
SQLite is used for the local product because it provides restart persistence,
atomic transactions, WAL concurrent reads, deterministic setup, and no paid or
external service. The repository boundary permits a future PostgreSQL adapter
for multi-instance deployment without changing canonical engines.

## Read and publication flow

1. Read the compatible in-memory response when present.
2. Otherwise read the latest `COMPLETE` compatible SQLite snapshot.
3. Serve that last-known-good response immediately.
4. Refresh in the bounded background executor.
5. Write a `BUILDING` snapshot, run the existing scanner, and atomically update
   it to `COMPLETE` only after the full response exists.
6. A failure records `FAILED`; it never replaces the prior complete snapshot.
7. Refresh jobs are durable (`QUEUED`, `RUNNING`, `COMPLETE`, `FAILED`, or
   `RETRYABLE`). Creating a replacement job safely retires interrupted work for
   that exact universe/timeframe/methodology key. Merely opening the database
   from another process never mutates a live job.

Compatibility is keyed by universe, timeframe, custom-symbol identity,
scanner storage version, and frozen methodology version (`formation-1.1`).

## Instrument identity and supported scope

Configured universes are mirrored into an instrument master with stable IDs of
the form `NSE:<exchange symbol>`. Exchange identity is retained. BSE and combined
India deduplication are not activated because the current provider/universe
files do not supply verified BSE listings and ISIN mappings. Commodity futures
and spot instruments remain explicitly unavailable. The largest trustworthy
configured universe is currently `allnse` with 2,390 symbols; the schema itself
has no 500-symbol limit and is suitable for synthetic 5,000+ query-load tests.

## Runtime data

The local runtime database is created at
`backend/data/scanner/alphaedge-scanner.sqlite3` and is ignored by Git. Override
it with `SCANNER_DATABASE_PATH`. It is separate from both the application/auth
database and frozen Historical Evidence SQLite artifact.

Provider OHLCV is persisted in `scanner_candles`, keyed by stable instrument,
base timeframe, and timestamp. Once bootstrapped, the provider is asked only
for a correction overlap plus new candles. Merges deterministically distinguish
inserted, corrected, unchanged, and rejected rows; every merge is recorded in
`scanner_candle_merge_audit`. Valid zero-range rows remain stored as explicit
`DATA_BREAK` boundaries and are never interpolated.

Queryable zone rows are stored in `scanner_result_rows`, separate from the
exact immutable response payload. Indexed filters, allow-listed ordering, and
stable server pagination therefore do not require sending every result to a
browser. Materialization state is stored as `READY`, `BUILDING`, `STALE`,
`FAILED`, or `UNAVAILABLE`.

## API

- `GET /scanner/capabilities` reports configured universes, counts, timeframe
  materialization state, and honest exchange/security coverage. NSE Main Equity
  is sourced from the official NSE EQ/BE/BZ file. NSE SME, NSE ETFs, BSE Main,
  BSE SME, and BSE ETFs remain explicitly unavailable or provider-dependent
  until independently validated sources and mappings are connected.
- Instrument-master synchronization is non-blocking, atomically preserves the
  last-known-good membership, and uses a persistent lease so multiple API
  workers cannot publish overlapping refreshes. Stable identity uses
  exchange + ISIN, with exchange-symbol aliases retained across symbol changes.
- The legacy API universe id `allnse` is displayed honestly as **NSE Main
  Equity**. It must not be described as all Indian securities or as NSE+BSE.
  The response also includes operational storage and methodology versions.
- `GET /scanner/snapshot-status` reports complete/building/failed snapshot counts.
- `GET /scanner/persisted-zones` provides database filtering, sorting, and
  deterministic pagination over the latest compatible complete snapshot.
- `GET /scanner/zones` remains backward compatible. It now reads the latest
  durable compatible snapshot before starting background refresh.

## Final validation evidence (2026-08-23)

- The real configured All-NSE Daily background bootstrap completed 2,389 of
  2,390 symbols, isolated KALYANI as invalid provider data, persisted 676,406
  candles, and published 256 qualifying zones in 2,670.9 seconds. This is the
  initial/full background bootstrap cost, not interactive Dashboard latency.
- The first realistic subsequent overlap refresh downloaded recent provider
  data in bounded batches. It inserted 556 candles, corrected 35, matched
  54,634 unchanged rows, rejected two invalid rows, and produced 257 zones
  without replacing the prior COMPLETE snapshot while BUILDING. A repeat
  refresh inserted zero, corrected 14 provider rows, matched 55,854 unchanged
  rows, rejected two invalid rows, and completed in 237.2 seconds.
- Per-symbol checkpoints are keyed by stable instrument, timeframe, frozen
  methodology, and candle revision. An actual All-NSE checkpoint reconstruction
  resumed 2,389 unchanged symbols, retried only KALYANI, and reproduced the
  persisted canonical payload exactly. A restart parity regression separately
  proves interrupted and uninterrupted merges are identical.
- READY read measurements distinguish a cold first database read from warm
  application-cache reads. All-NSE Dashboard was 44.62 ms cold and 3.40 ms
  warm p50; pagination was 76.54 ms cold and 40.36 ms warm p50; filtered/sorted
  pagination was 62.86 ms cold and 41.29 ms warm p50. All requests succeeded.
- READY switching did not launch a market scan: NSE 500 Daily measured 30.95 ms
  cold / 19.36 ms warm p50, and Nifty 50 Weekly measured 10.27 ms cold /
  9.98 ms warm p50.
- The Dashboard first reads summary metadata without full results and obtains
  the visible page through `/scanner/persisted-zones`. Filters, sorting, and
  pagination are server-side; the browser does not download the full All-NSE
  result set.
- The runtime database is 189,308,928 bytes (180.5 MiB), containing 676,962
  candles after incremental refresh. The final completed controlled All-NSE
  workload used one scanner process and at most six canonical symbol workers.
  Native working-set memory was 137.82 MiB baseline, 287.82 MiB peak, and
  232.75 MiB final; CPU time was 251.59 seconds over 239.6 seconds wall time
  (105.0% of one core, 8.75% of the 12-core host). Two threads remained after
  completion (main plus the bounded application executor); no per-symbol worker
  or connection leak was observed.
- Synthetic infrastructure tests cover more than 5,000 result rows. This proves
  storage/query scale only and is not represented as 5,000 provider-backed
  Indian instruments.

## Final freeze validation (2026-08-24)

- All-NSE Daily global Trade Confidence descending and ascending API pages
  exactly matched independent SQLite ordering across all 269 persisted rows.
- All-NSE Daily global Zone Quality descending and ascending pages exactly
  matched SQLite ordering. Descending boundaries were 90.3 at the end of page
  1, 90.2 at the start of page 2, 88.3 at the end of page 2, and 88.1 at the
  start of page 3.
- Trade Confidence descending continued from 71.22 at the end of page 2 to
  70.98 at the start of page 3.
- Demand plus minimum-quality filtering produced 177 rows and preserved global
  Trade Confidence ordering before pagination.
- Distance sorting, stable totals, deterministic ties, and complete page
  concatenation without duplicate or missing zone identities are regression
  locked.
- NSE 500 sorting remained isolated to its 64-row Daily snapshot. Weekly reads
  selected only the Weekly materialization and returned zero Daily leakage.
- Restart/checkpoint parity, interrupted-job retry, last-known-good publication,
  and READY-read-without-scan behavior remain regression locked.

## Instrument-master reconciliation (2026-08-26)

- Official source: NSE `EQUITY_L.csv`; checksum
  `ff8ef8d24d063d0b1ba145060eea9545050b50594462d1e16a404e21bd090f26`.
- Validated membership: 2,559 active securities: EQ 2,291, BE 240, BZ 28.
- The prior 2,390-symbol bootstrap was replaced atomically; three stale
  instruments were deactivated without deleting stable identity or history.
- `TMPV` is present as `NSE:TMPV`, ISIN `INE155A01022`, provider identifier
  `TMPV.NS`. A real Daily provider-backed scan processed it successfully and
  found two canonical zones, neither of which qualified for the Dashboard.
- Existing completed snapshots remain available while the 169 newly covered
  net instruments are incrementally persisted and scanned. Snapshot publication
  remains all-or-nothing, so partial refresh results never replace READY data.
- Persisted-read benchmark after synchronization: Dashboard summary 33.41 ms
  warm p50; unfiltered page 122.86 ms; filtered/sorted page 117.38 ms; all
  measured requests completed successfully.

## Coverage and operational limits

- Real current membership coverage is 2,559 NSE Main Equity securities. The
  older 2,389/2,390 completed scan remains the last-known-good snapshot until
  the incremental 2,559-symbol materialization is atomically published.
- BSE and verified cross-exchange ISIN deduplication remain unavailable and
  provider-dependent. A future production provider must supply an NSE/BSE
  instrument master, stable exchange identifiers, ISIN, reliable historical
  and intraday OHLCV, bulk downloads, corporate-action handling, and documented
  production rate limits.
- A READY timeframe is served from persistence. An unmaterialized timeframe is
  honestly reported as BUILDING, STALE, or UNAVAILABLE; no data is fabricated.
- SQLite is correct for one local backend process. Multi-instance production
  requires PostgreSQL and a distributed lease implementation. The current job
  lease and checkpoint model safely supports local backend restart/resume.
- Refresh is asynchronous and request-triggered. A separate always-on scheduler
  may be added operationally later without changing canonical scanning.
