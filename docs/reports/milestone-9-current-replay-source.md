# Milestone 8 - Historical Trade Planning Replay

> Research infrastructure only. Canonical Trade Planning V1 is not active.

## Dataset

- Symbols requested: 28
- Successful symbol/timeframe series: 112
- Failed series: 28
- Reconstructed canonical zones: 890
- Date range: 2021-08-20 00:00:00 to 2026-08-21 00:00:00
- Provider: YahooProvider
- Tick size: unavailable from the current provider contract; no universal tick was assumed.

## Coverage

- Timeframes: {'15m': 275, '75m': 185, '125m': 118, '1W': 312}
- Zone types: {'DEMAND': 477, 'SUPPLY': 413}
- Patterns: {'DBR': 221, 'DBD': 245, 'RBR': 256, 'RBD': 168}

## Entry x stop results

| Timeframe | Entry | Stop | Zones | Fill % | Target first % | Stop first % | Median R:R | Median MAE/ATR | Median MFE/ATR |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| 125m | PROXIMAL | RESEARCH_ONLY_NOT_CANONICAL_STOP | 118 | 67.80 | 15.38 | 84.62 | 3.787 | 1.2894 | 1.7403 |
| 15m | PROXIMAL | RESEARCH_ONLY_NOT_CANONICAL_STOP | 275 | 82.91 | 24.44 | 75.56 | 9.1593 | 3.4999 | 4.3906 |
| 1W | PROXIMAL | RESEARCH_ONLY_NOT_CANONICAL_STOP | 312 | 72.12 | 42.37 | 57.63 | 2.9793 | 2.0558 | 2.3317 |
| 75m | PROXIMAL | RESEARCH_ONLY_NOT_CANONICAL_STOP | 185 | 77.84 | 23.08 | 76.92 | 5.1568 | 2.0807 | 2.3941 |

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
