# Milestone 12 - Dhan Shadow Integration

Status: **OPEN - SHADOW ONLY**

Yahoo remains AlphaEdge's production market-data provider. Dhan is an isolated,
read-only shadow source and must not be returned by ordinary Dashboard or Stock
Details requests.

## Source semantics

- Provider: `dhan`
- Semantics version: `dhan-raw-ohlcv-v1`
- Listing identity: `<exchange>:<Dhan security ID>`
- NSE and BSE listings remain separate even when they share an ISIN.
- Dhan candles are stored in `backend/data/shadow/dhan-shadow.sqlite3`, never in
  the Yahoo production candle or scanner tables.
- Stored metadata includes exchange, security ID, timeframe, source interval,
  raw/unadjusted semantics, candle revision, and retrieval time.
- Credentials are environment-only and are never persisted or exposed.

## Shadow universes

- `dhan_nse_main`
- `dhan_nse_sme`
- `dhan_bse_main`
- `dhan_bse_sme`
- `dhan_all_supported_indian_equity`

Membership is derived from the synchronized Dhan master. Counts are not
hardcoded. ETFs, REITs, InvITs, debt, preference instruments, warrants, and
other non-equity instruments are excluded by the master classifier.

## Materialization policy

Daily history is checkpointed per listing and is resumable. Refreshes request
only a correction overlap and newer sessions. Weekly, Monthly, Quarterly,
Half-yearly, and Yearly candles are deterministically aggregated from Dhan
Daily candles. The 75-minute and 125-minute shadow candles are anchored at
09:15 Asia/Kolkata and never cross sessions.

No production policy is approved for residual 1H/2H/4H/6H session candles.
Options requiring future approval include keeping the short final bucket,
merging it into the preceding bucket, or using exchange-session-aligned custom
buckets. None is activated by this milestone.

## Known blockers

- Dhan raw candles and Yahoo auto-adjusted candles have materially different
  source semantics; differences are source-data differences, not methodology
  regressions.
- TMPV security ID 3456 currently returns history beginning in 2003, preceding
  the present company identity. Symbol/predecessor/corporate-action semantics
  require a general identity policy before production use.
- BSE Main addressability/no-data behavior requires broader investigation.
- Full-universe resource, canonical enrichment, atomic snapshot, and global
  shadow result-query benchmarks remain incomplete.
- Technical API capability does not establish commercial redistribution rights.

No canonical analytical methodology is changed by this integration.
