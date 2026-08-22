# Milestone 8 - Historical Trade Planning Replay

> Research infrastructure only. Canonical Trade Planning V1 is not active.

## Dataset

- Symbols requested: 28
- Successful symbol/timeframe series: 28
- Failed series: 0
- Reconstructed canonical zones: 675
- Date range: 2021-08-17 00:00:00 to 2026-08-17 00:00:00
- Provider: YahooProvider
- Tick size: unavailable from the current provider contract; no universal tick was assumed.

## Coverage

- Timeframes: {'1D': 675}
- Zone types: {'DEMAND': 345, 'SUPPLY': 330}
- Patterns: {'RBR': 178, 'RBD': 105, 'DBD': 225, 'DBR': 167}

## Entry x stop results

| Timeframe | Entry | Stop | Zones | Fill % | Target first % | Stop first % | Median R:R | Median MAE/ATR | Median MFE/ATR |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| 1D | DISTAL | ATR14_10 | 580 | 64.66 | 3.25 | 96.75 | 36.6441 | 2.903 | 2.5352 |
| 1D | DISTAL | ATR14_15 | 580 | 64.66 | 3.87 | 96.13 | 24.4294 | 2.903 | 2.5352 |
| 1D | DISTAL | ATR14_20 | 580 | 64.66 | 5.19 | 94.81 | 18.322 | 2.903 | 2.5352 |
| 1D | DISTAL | ATR14_25 | 580 | 64.66 | 6.49 | 93.51 | 14.6576 | 2.903 | 2.5352 |
| 1D | DISTAL | ATR14_30 | 580 | 64.66 | 7.14 | 92.86 | 12.2147 | 2.903 | 2.5352 |
| 1D | DISTAL | ATR14_5 | 580 | 64.66 | 2.58 | 97.42 | 73.2881 | 2.903 | 2.5352 |
| 1D | DISTAL | HYBRID_MAX_ZW_ATR_10 | 580 | 64.66 | 3.25 | 96.75 | 34.0124 | 2.903 | 2.5352 |
| 1D | DISTAL | HYBRID_MAX_ZW_ATR_15 | 580 | 64.66 | 4.52 | 95.48 | 22.6749 | 2.903 | 2.5352 |
| 1D | DISTAL | HYBRID_MAX_ZW_ATR_20 | 580 | 64.66 | 5.19 | 94.81 | 17.0062 | 2.903 | 2.5352 |
| 1D | DISTAL | HYBRID_MAX_ZW_ATR_25 | 580 | 64.66 | 6.49 | 93.51 | 13.605 | 2.903 | 2.5352 |
| 1D | DISTAL | HYBRID_MAX_ZW_ATR_30 | 580 | 64.66 | 8.44 | 91.56 | 11.3375 | 2.903 | 2.5352 |
| 1D | DISTAL | HYBRID_MAX_ZW_ATR_5 | 580 | 64.66 | 2.58 | 97.42 | 68.0248 | 2.903 | 2.5352 |
| 1D | DISTAL | ZONE_WIDTH_10 | 675 | 64.74 | 2.56 | 97.44 | 55.266 | 2.903 | 2.5352 |
| 1D | DISTAL | ZONE_WIDTH_15 | 675 | 64.74 | 3.85 | 96.15 | 36.844 | 2.903 | 2.5352 |
| 1D | DISTAL | ZONE_WIDTH_20 | 675 | 64.74 | 4.49 | 95.51 | 27.633 | 2.903 | 2.5352 |
| 1D | DISTAL | ZONE_WIDTH_25 | 675 | 64.74 | 5.81 | 94.19 | 22.1064 | 2.903 | 2.5352 |
| 1D | DISTAL | ZONE_WIDTH_30 | 675 | 64.74 | 7.10 | 92.90 | 18.422 | 2.903 | 2.5352 |
| 1D | DISTAL | ZONE_WIDTH_5 | 675 | 64.74 | 1.28 | 98.72 | 110.5321 | 2.903 | 2.5352 |
| 1D | MIDPOINT | ATR14_10 | 580 | 70.00 | 13.21 | 86.79 | 7.7693 | 2.7774 | 2.5021 |
| 1D | MIDPOINT | ATR14_15 | 580 | 70.00 | 13.84 | 86.16 | 7.0205 | 2.7774 | 2.5021 |
| 1D | MIDPOINT | ATR14_20 | 580 | 70.00 | 15.19 | 84.81 | 6.3803 | 2.7774 | 2.5021 |
| 1D | MIDPOINT | ATR14_25 | 580 | 70.00 | 16.46 | 83.54 | 5.7011 | 2.7774 | 2.5021 |
| 1D | MIDPOINT | ATR14_30 | 580 | 70.00 | 17.09 | 82.91 | 5.2716 | 2.7774 | 2.5021 |
| 1D | MIDPOINT | ATR14_5 | 580 | 70.00 | 12.50 | 87.50 | 8.7251 | 2.7774 | 2.5021 |
| 1D | MIDPOINT | HYBRID_MAX_ZW_ATR_10 | 580 | 70.00 | 13.21 | 86.79 | 7.7693 | 2.7774 | 2.5021 |
| 1D | MIDPOINT | HYBRID_MAX_ZW_ATR_15 | 580 | 70.00 | 14.47 | 85.53 | 7.0205 | 2.7774 | 2.5021 |
| 1D | MIDPOINT | HYBRID_MAX_ZW_ATR_20 | 580 | 70.00 | 15.19 | 84.81 | 6.3647 | 2.7774 | 2.5021 |
| 1D | MIDPOINT | HYBRID_MAX_ZW_ATR_25 | 580 | 70.00 | 16.46 | 83.54 | 5.6477 | 2.7774 | 2.5021 |
| 1D | MIDPOINT | HYBRID_MAX_ZW_ATR_30 | 580 | 70.00 | 18.35 | 81.65 | 5.117 | 2.7774 | 2.5021 |
| 1D | MIDPOINT | HYBRID_MAX_ZW_ATR_5 | 580 | 70.00 | 12.50 | 87.50 | 8.7251 | 2.7774 | 2.5021 |
| 1D | MIDPOINT | ZONE_WIDTH_10 | 675 | 70.07 | 12.42 | 87.58 | 8.3777 | 2.7774 | 2.5021 |
| 1D | MIDPOINT | ZONE_WIDTH_15 | 675 | 70.07 | 13.66 | 86.34 | 7.7332 | 2.7774 | 2.5021 |
| 1D | MIDPOINT | ZONE_WIDTH_20 | 675 | 70.07 | 14.29 | 85.71 | 7.1809 | 2.7774 | 2.5021 |
| 1D | MIDPOINT | ZONE_WIDTH_25 | 675 | 70.07 | 15.72 | 84.28 | 6.7021 | 2.7774 | 2.5021 |
| 1D | MIDPOINT | ZONE_WIDTH_30 | 675 | 70.07 | 16.98 | 83.02 | 6.2833 | 2.7774 | 2.5021 |
| 1D | MIDPOINT | ZONE_WIDTH_5 | 675 | 70.07 | 11.18 | 88.82 | 9.1393 | 2.7774 | 2.5021 |
| 1D | PROXIMAL | ATR14_10 | 580 | 74.48 | 19.63 | 80.37 | 3.9182 | 2.6765 | 2.5514 |
| 1D | PROXIMAL | ATR14_15 | 580 | 74.48 | 20.25 | 79.75 | 3.688 | 2.6765 | 2.5514 |
| 1D | PROXIMAL | ATR14_20 | 580 | 74.48 | 21.60 | 78.40 | 3.4904 | 2.6765 | 2.5514 |
| 1D | PROXIMAL | ATR14_25 | 580 | 74.48 | 22.22 | 77.78 | 3.3154 | 2.6765 | 2.5514 |
| 1D | PROXIMAL | ATR14_30 | 580 | 74.48 | 22.84 | 77.16 | 3.1548 | 2.6765 | 2.5514 |
| 1D | PROXIMAL | ATR14_5 | 580 | 74.48 | 18.90 | 81.10 | 4.1564 | 2.6765 | 2.5514 |
| 1D | PROXIMAL | HYBRID_MAX_ZW_ATR_10 | 580 | 74.48 | 19.63 | 80.37 | 3.9182 | 2.6765 | 2.5514 |
| 1D | PROXIMAL | HYBRID_MAX_ZW_ATR_15 | 580 | 74.48 | 20.86 | 79.14 | 3.688 | 2.6765 | 2.5514 |
| 1D | PROXIMAL | HYBRID_MAX_ZW_ATR_20 | 580 | 74.48 | 21.60 | 78.40 | 3.4904 | 2.6765 | 2.5514 |
| 1D | PROXIMAL | HYBRID_MAX_ZW_ATR_25 | 580 | 74.48 | 22.22 | 77.78 | 3.3154 | 2.6765 | 2.5514 |
| 1D | PROXIMAL | HYBRID_MAX_ZW_ATR_30 | 580 | 74.48 | 24.07 | 75.93 | 3.1548 | 2.6765 | 2.5514 |
| 1D | PROXIMAL | HYBRID_MAX_ZW_ATR_5 | 580 | 74.48 | 18.90 | 81.10 | 4.1381 | 2.6765 | 2.5514 |
| 1D | PROXIMAL | ZONE_WIDTH_10 | 675 | 75.11 | 19.88 | 80.12 | 4.1151 | 2.6765 | 2.5514 |
| 1D | PROXIMAL | ZONE_WIDTH_15 | 675 | 75.11 | 21.08 | 78.92 | 3.9362 | 2.6765 | 2.5514 |
| 1D | PROXIMAL | ZONE_WIDTH_20 | 675 | 75.11 | 21.69 | 78.31 | 3.7722 | 2.6765 | 2.5514 |
| 1D | PROXIMAL | ZONE_WIDTH_25 | 675 | 75.11 | 22.56 | 77.44 | 3.6213 | 2.6765 | 2.5514 |
| 1D | PROXIMAL | ZONE_WIDTH_30 | 675 | 75.11 | 23.78 | 76.22 | 3.482 | 2.6765 | 2.5514 |
| 1D | PROXIMAL | ZONE_WIDTH_5 | 675 | 75.11 | 19.28 | 80.72 | 4.3111 | 2.6765 | 2.5514 |

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
