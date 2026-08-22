# Milestone 8 - Historical Trade Planning Replay

> Research infrastructure only. Canonical Trade Planning V1 is not active.

## Dataset

- Symbols requested: 28
- Successful symbol/timeframe series: 28
- Failed series: 0
- Reconstructed canonical zones: 312
- Date range: 2021-08-20 00:00:00 to 2026-08-21 00:00:00
- Provider: YahooProvider
- Tick size: unavailable from the current provider contract; no universal tick was assumed.

## Coverage

- Timeframes: {'1W': 312}
- Zone types: {'DEMAND': 185, 'SUPPLY': 127}
- Patterns: {'DBR': 75, 'RBD': 53, 'RBR': 110, 'DBD': 74}

## Entry x stop results

| Timeframe | Entry | Stop | Zones | Fill % | Target first % | Stop first % | Median R:R | Median MAE/ATR | Median MFE/ATR |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| 1W | PROXIMAL | RESEARCH_ONLY_NOT_CANONICAL_STOP | 312 | 71.79 | 41.38 | 58.62 | 2.99 | 2.0293 | 2.4163 |

## Look-ahead protection

- Every accepted zone is re-detected on an OHLCV prefix ending at its Leg-Out planning candle.
- Wilder ATR(14) is calculated on that prefix only: first ATR is the mean of 14 True Ranges; later values use Wilder smoothing `(prior ATR * 13 + TR) / 14`.
- Opposing zones are limited to the same symbol, timeframe, and prefix snapshot.
- Targets must be directionally ahead, lifecycle-active, and Authentic at planning time.
- Future candles are read only after the snapshot is frozen and only for outcome measurement.
- If stop and target are both touched in one candle, the outcome is recorded as ambiguous rather than guessed.

## Data limitations

- Instrument-specific tick-size metadata unavailable; no tick component was added to hybrid stop candidates.

## Decision status

No production Entry, Protective Stop, or numerical constants were selected automatically. Review the row-level JSON and sensitivity table before approving a policy.
