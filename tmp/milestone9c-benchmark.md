# Milestone 8 - Historical Trade Planning Replay

> Research infrastructure only. Canonical Trade Planning V1 is not active.

## Dataset

- Symbols requested: 1
- Successful symbol/timeframe series: 2
- Failed series: 0
- Reconstructed canonical zones: 112
- Date range: 2021-08-18 00:00:00 to 2026-08-21 00:00:00
- Provider: YahooProvider
- Tick size: unavailable from the current provider contract; no universal tick was assumed.

## Coverage

- Timeframes: {'1D': 93, '1W': 19}
- Zone types: {'DEMAND': 64, 'SUPPLY': 48}
- Patterns: {'RBR': 30, 'DBR': 34, 'RBD': 19, 'DBD': 29}

## Entry x stop results

| Timeframe | Entry | Stop | Zones | Fill % | Target first % | Stop first % | Median R:R | Median MAE/ATR | Median MFE/ATR |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| 1D | PROXIMAL | RESEARCH_ONLY_NOT_CANONICAL_STOP | 93 | 90.32 | 12.00 | 88.00 | 3.5592 | 3.9315 | 3.7611 |
| 1W | PROXIMAL | RESEARCH_ONLY_NOT_CANONICAL_STOP | 19 | 84.21 | 33.33 | 66.67 | 4.1305 | 2.3308 | 2.4454 |

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
