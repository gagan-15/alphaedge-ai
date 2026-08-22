# Milestone 8 - Historical Trade Planning Replay

> Research infrastructure only. Canonical Trade Planning V1 is not active.

## Dataset

- Symbols requested: 28
- Successful symbol/timeframe series: 28
- Failed series: 0
- Reconstructed canonical zones: 311
- Date range: 2021-08-20 00:00:00 to 2026-08-21 00:00:00
- Provider: YahooProvider
- Tick size: unavailable from the current provider contract; no universal tick was assumed.

## Coverage

- Timeframes: {'1W': 311}
- Zone types: {'DEMAND': 187, 'SUPPLY': 124}
- Patterns: {'RBR': 114, 'DBR': 73, 'RBD': 49, 'DBD': 75}

## Entry x stop results

| Timeframe | Entry | Stop | Zones | Fill % | Target first % | Stop first % | Median R:R | Median MAE/ATR | Median MFE/ATR |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| 1W | DISTAL | ATR14_10 | 254 | 52.36 | 5.00 | 95.00 | 27.9145 | 2.2081 | 2.0519 |
| 1W | DISTAL | ATR14_15 | 254 | 52.36 | 7.32 | 92.68 | 18.6097 | 2.2081 | 2.0519 |
| 1W | DISTAL | ATR14_20 | 254 | 52.36 | 9.76 | 90.24 | 13.9573 | 2.2081 | 2.0519 |
| 1W | DISTAL | ATR14_25 | 254 | 52.36 | 14.29 | 85.71 | 11.1658 | 2.2081 | 2.0519 |
| 1W | DISTAL | ATR14_30 | 254 | 52.36 | 15.00 | 85.00 | 9.3048 | 2.2081 | 2.0519 |
| 1W | DISTAL | ATR14_5 | 254 | 52.36 | 2.50 | 97.50 | 55.829 | 2.2081 | 2.0519 |
| 1W | DISTAL | HYBRID_MAX_ZW_ATR_10 | 254 | 52.36 | 5.00 | 95.00 | 25.0106 | 2.2081 | 2.0519 |
| 1W | DISTAL | HYBRID_MAX_ZW_ATR_15 | 254 | 52.36 | 7.32 | 92.68 | 16.6738 | 2.2081 | 2.0519 |
| 1W | DISTAL | HYBRID_MAX_ZW_ATR_20 | 254 | 52.36 | 9.76 | 90.24 | 12.5053 | 2.2081 | 2.0519 |
| 1W | DISTAL | HYBRID_MAX_ZW_ATR_25 | 254 | 52.36 | 14.63 | 85.37 | 10.0043 | 2.2081 | 2.0519 |
| 1W | DISTAL | HYBRID_MAX_ZW_ATR_30 | 254 | 52.36 | 15.00 | 85.00 | 8.3369 | 2.2081 | 2.0519 |
| 1W | DISTAL | HYBRID_MAX_ZW_ATR_5 | 254 | 52.36 | 2.50 | 97.50 | 50.0213 | 2.2081 | 2.0519 |
| 1W | DISTAL | ZONE_WIDTH_10 | 311 | 52.73 | 4.76 | 95.24 | 40.5958 | 2.2081 | 2.0519 |
| 1W | DISTAL | ZONE_WIDTH_15 | 311 | 52.73 | 4.76 | 95.24 | 27.0638 | 2.2081 | 2.0519 |
| 1W | DISTAL | ZONE_WIDTH_20 | 311 | 52.73 | 4.76 | 95.24 | 20.2979 | 2.2081 | 2.0519 |
| 1W | DISTAL | ZONE_WIDTH_25 | 311 | 52.73 | 4.88 | 95.12 | 16.2383 | 2.2081 | 2.0519 |
| 1W | DISTAL | ZONE_WIDTH_30 | 311 | 52.73 | 5.00 | 95.00 | 13.5319 | 2.2081 | 2.0519 |
| 1W | DISTAL | ZONE_WIDTH_5 | 311 | 52.73 | 0.00 | 100.00 | 81.1915 | 2.2081 | 2.0519 |
| 1W | MIDPOINT | ATR14_10 | 254 | 59.45 | 28.26 | 71.74 | 5.2857 | 2.078 | 2.3098 |
| 1W | MIDPOINT | ATR14_15 | 254 | 59.45 | 28.26 | 71.74 | 4.7419 | 2.078 | 2.3098 |
| 1W | MIDPOINT | ATR14_20 | 254 | 59.45 | 30.43 | 69.57 | 4.285 | 2.078 | 2.3098 |
| 1W | MIDPOINT | ATR14_25 | 254 | 59.45 | 31.91 | 68.09 | 3.9542 | 2.078 | 2.3098 |
| 1W | MIDPOINT | ATR14_30 | 254 | 59.45 | 33.33 | 66.67 | 3.6508 | 2.078 | 2.3098 |
| 1W | MIDPOINT | ATR14_5 | 254 | 59.45 | 26.09 | 73.91 | 6.1104 | 2.078 | 2.3098 |
| 1W | MIDPOINT | HYBRID_MAX_ZW_ATR_10 | 254 | 59.45 | 28.26 | 71.74 | 5.2857 | 2.078 | 2.3098 |
| 1W | MIDPOINT | HYBRID_MAX_ZW_ATR_15 | 254 | 59.45 | 28.26 | 71.74 | 4.7419 | 2.078 | 2.3098 |
| 1W | MIDPOINT | HYBRID_MAX_ZW_ATR_20 | 254 | 59.45 | 30.43 | 69.57 | 4.285 | 2.078 | 2.3098 |
| 1W | MIDPOINT | HYBRID_MAX_ZW_ATR_25 | 254 | 59.45 | 32.61 | 67.39 | 3.9542 | 2.078 | 2.3098 |
| 1W | MIDPOINT | HYBRID_MAX_ZW_ATR_30 | 254 | 59.45 | 33.33 | 66.67 | 3.6508 | 2.078 | 2.3098 |
| 1W | MIDPOINT | HYBRID_MAX_ZW_ATR_5 | 254 | 59.45 | 26.09 | 73.91 | 6.1104 | 2.078 | 2.3098 |
| 1W | MIDPOINT | ZONE_WIDTH_10 | 311 | 60.13 | 27.08 | 72.92 | 5.9326 | 2.078 | 2.3098 |
| 1W | MIDPOINT | ZONE_WIDTH_15 | 311 | 60.13 | 27.08 | 72.92 | 5.4763 | 2.078 | 2.3098 |
| 1W | MIDPOINT | ZONE_WIDTH_20 | 311 | 60.13 | 27.08 | 72.92 | 5.0851 | 2.078 | 2.3098 |
| 1W | MIDPOINT | ZONE_WIDTH_25 | 311 | 60.13 | 27.66 | 72.34 | 4.7461 | 2.078 | 2.3098 |
| 1W | MIDPOINT | ZONE_WIDTH_30 | 311 | 60.13 | 28.26 | 71.74 | 4.4495 | 2.078 | 2.3098 |
| 1W | MIDPOINT | ZONE_WIDTH_5 | 311 | 60.13 | 23.40 | 76.60 | 6.472 | 2.078 | 2.3098 |
| 1W | PROXIMAL | ATR14_10 | 254 | 69.29 | 49.06 | 50.94 | 2.6478 | 1.9175 | 2.5603 |
| 1W | PROXIMAL | ATR14_15 | 254 | 69.29 | 49.06 | 50.94 | 2.422 | 1.9175 | 2.5603 |
| 1W | PROXIMAL | ATR14_20 | 254 | 69.29 | 50.94 | 49.06 | 2.2883 | 1.9175 | 2.5603 |
| 1W | PROXIMAL | ATR14_25 | 254 | 69.29 | 51.85 | 48.15 | 2.1365 | 1.9175 | 2.5603 |
| 1W | PROXIMAL | ATR14_30 | 254 | 69.29 | 53.85 | 46.15 | 2.0317 | 1.9175 | 2.5603 |
| 1W | PROXIMAL | ATR14_5 | 254 | 69.29 | 47.17 | 52.83 | 2.8267 | 1.9175 | 2.5603 |
| 1W | PROXIMAL | HYBRID_MAX_ZW_ATR_10 | 254 | 69.29 | 49.06 | 50.94 | 2.6478 | 1.9175 | 2.5603 |
| 1W | PROXIMAL | HYBRID_MAX_ZW_ATR_15 | 254 | 69.29 | 49.06 | 50.94 | 2.422 | 1.9175 | 2.5603 |
| 1W | PROXIMAL | HYBRID_MAX_ZW_ATR_20 | 254 | 69.29 | 50.94 | 49.06 | 2.2883 | 1.9175 | 2.5603 |
| 1W | PROXIMAL | HYBRID_MAX_ZW_ATR_25 | 254 | 69.29 | 52.83 | 47.17 | 2.1365 | 1.9175 | 2.5603 |
| 1W | PROXIMAL | HYBRID_MAX_ZW_ATR_30 | 254 | 69.29 | 53.85 | 46.15 | 2.0283 | 1.9175 | 2.5603 |
| 1W | PROXIMAL | HYBRID_MAX_ZW_ATR_5 | 254 | 69.29 | 47.17 | 52.83 | 2.8267 | 1.9175 | 2.5603 |
| 1W | PROXIMAL | ZONE_WIDTH_10 | 311 | 70.74 | 47.27 | 52.73 | 2.7814 | 1.9175 | 2.5603 |
| 1W | PROXIMAL | ZONE_WIDTH_15 | 311 | 70.74 | 47.27 | 52.73 | 2.6605 | 1.9175 | 2.5603 |
| 1W | PROXIMAL | ZONE_WIDTH_20 | 311 | 70.74 | 47.27 | 52.73 | 2.5496 | 1.9175 | 2.5603 |
| 1W | PROXIMAL | ZONE_WIDTH_25 | 311 | 70.74 | 48.15 | 51.85 | 2.4477 | 1.9175 | 2.5603 |
| 1W | PROXIMAL | ZONE_WIDTH_30 | 311 | 70.74 | 49.06 | 50.94 | 2.3535 | 1.9175 | 2.5603 |
| 1W | PROXIMAL | ZONE_WIDTH_5 | 311 | 70.74 | 44.44 | 55.56 | 2.9139 | 1.9175 | 2.5603 |

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
