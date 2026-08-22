# Milestone 8 - Final Trade Planning Calibration Study

> Research only. Canonical Trade Planning V1 remains inactive.

## Evidence and scope

- Replay generated: 2026-08-17T16:35:40.803399+05:30
- Symbols: 28 (RELIANCE, TCS, HDFCBANK, INFY, ICICIBANK, SBIN, HINDALCO, AUBANK, MAXHEALTH, SUNPHARMA, MARUTI, ITC, 360ONE, ALKEM, BAJFINANCE, BSOFT, COHANCE, EIHOTEL, GLAXO, INDUSINDBK, JSWENERGY, LLOYDSME, MRPL, OIL, PREMIERENE, TATACHEM, TVSMOTOR, ZYDUSWELL)
- Series succeeded/failed: 140 / 0
- Prefix-reconstructed zones: 1560
- Provider: YahooProvider
- Date range: 2021-08-17 00:00:00 to 2026-08-21 00:00:00
- Symbols were the original accepted 12 plus a deterministic, evenly spaced NSE 500 expansion; no outcome-based symbol selection was used.
- Subgroups below 30 zones are marked LIMITED and are not used for firm conclusions.

## Proximal entry validation

Overall fill: 1168 / 1560 (74.87%). Median candles to fill: 4.0.

| Entry | Sample | Filled | Fill % | Median candles |
|---|---:|---:|---:|---:|
| PROXIMAL | 1560 | 1168 | 74.87 | 4.0 |
| MIDPOINT | 1560 | 1073 | 68.78 | 6 |
| DISTAL | 1560 | 985 | 63.14 | 8 |

### By timeframe

| timeframe | sample_size | evidence | fill_rate_percent | median_candles_to_fill | target_before_invalidation_percent | invalidation_before_target_percent | no_valid_target_percent | median_mae_zone_width | median_mfe_zone_width |
|---|---|---|---|---|---|---|---|---|---|
| 125m | 117 | SUFFICIENT | 64.1 | 3 | 1.71 | 8.55 | 51.28 | 2.6368 | 3.1 |
| 15m | 271 | SUFFICIENT | 82.29 | 4 | 8.12 | 24.72 | 45.39 | 8.7781 | 10.6889 |
| 1D | 675 | SUFFICIENT | 74.96 | 4.0 | 4.44 | 20.15 | 48.3 | 5.7842 | 5.335 |
| 1W | 311 | SUFFICIENT | 70.74 | 3.0 | 7.72 | 9.65 | 50.48 | 3.1568 | 4.2087 |
| 75m | 186 | SUFFICIENT | 77.42 | 5.0 | 5.38 | 16.13 | 53.23 | 3.7133 | 4.474 |

### By zone type

| zone_type | sample_size | evidence | fill_rate_percent | median_candles_to_fill | target_before_invalidation_percent | invalidation_before_target_percent | no_valid_target_percent |
|---|---|---|---|---|---|---|---|
| DEMAND | 828 | SUFFICIENT | 71.74 | 4.0 | 4.83 | 12.2 | 53.02 |
| SUPPLY | 732 | SUFFICIENT | 78.42 | 3.0 | 6.56 | 23.5 | 44.54 |

### By pattern

| pattern | sample_size | evidence | fill_rate_percent | median_candles_to_fill | target_before_invalidation_percent | invalidation_before_target_percent | no_valid_target_percent |
|---|---|---|---|---|---|---|---|
| DBD | 469 | SUFFICIENT | 79.32 | 3.0 | 6.18 | 24.95 | 44.56 |
| DBR | 388 | SUFFICIENT | 71.39 | 4 | 5.67 | 12.63 | 51.55 |
| RBD | 263 | SUFFICIENT | 76.81 | 4.0 | 7.22 | 20.91 | 44.49 |
| RBR | 440 | SUFFICIENT | 72.05 | 4 | 4.09 | 11.82 | 54.32 |

## Robustness

Leave-one-symbol-out fill range: 74.37% to 75.35%.

### Period stability

| year | sample_size | evidence | fill_rate_percent |
|---|---|---|---|
| 2021 | 49 | SUFFICIENT | 93.88 |
| 2022 | 121 | SUFFICIENT | 85.95 |
| 2023 | 121 | SUFFICIENT | 82.64 |
| 2024 | 113 | SUFFICIENT | 78.76 |
| 2025 | 301 | SUFFICIENT | 70.76 |
| 2026 | 855 | SUFFICIENT | 72.05 |

## Same-candle ambiguity

OHLC cannot establish sequence when stop and target are both inside one candle. The canonical research recommendation is UNKNOWN / SAME_CANDLE_AMBIGUOUS; conservative and optimistic counts are sensitivity bounds only.

| stop_policy | eligible | ambiguous | ambiguous_percent | conservative_stop_first | optimistic_target_first | explicit_unknown |
|---|---|---|---|---|---|---|
| ATR14_10 | 395 | 11 | 2.78 | 273 | 106 | 11 |
| ATR14_15 | 395 | 10 | 2.53 | 272 | 106 | 10 |
| ATR14_20 | 395 | 10 | 2.53 | 268 | 109 | 10 |
| ATR14_5 | 395 | 12 | 3.04 | 278 | 103 | 12 |
| HYBRID_MAX_ZW_ATR_10 | 395 | 11 | 2.78 | 273 | 106 | 11 |
| HYBRID_MAX_ZW_ATR_15 | 395 | 10 | 2.53 | 271 | 107 | 10 |
| HYBRID_MAX_ZW_ATR_20 | 395 | 10 | 2.53 | 268 | 109 | 10 |
| HYBRID_MAX_ZW_ATR_5 | 395 | 12 | 3.04 | 278 | 103 | 12 |
| ZONE_WIDTH_10 | 403 | 15 | 3.72 | 284 | 108 | 15 |
| ZONE_WIDTH_15 | 403 | 12 | 2.98 | 278 | 110 | 12 |
| ZONE_WIDTH_20 | 403 | 11 | 2.73 | 276 | 111 | 11 |
| ZONE_WIDTH_5 | 403 | 17 | 4.22 | 288 | 107 | 17 |

## Protective-stop calibration

The detailed JSON contains every timeframe x stop candidate. No candidate is selected by win rate. 'Marginal' means the stop was exceeded by no more than 5% of zone width before a later target; it is descriptive, not a proposed rule.

| stop_policy | filled | valid_target_filled | target_before_stop | stop_before_target | ambiguous | median_risk_per_share | median_structural_rr | marginal_stop_then_target_percent | wider_than_needed_ex_post_percent |
|---|---|---|---|---|---|---|---|---|---|
| ATR14_10 | 1001 | 395 | 95 | 262 | 11 | 12.2826 | 4.1029 | 0.92 | 41.94 |
| ATR14_15 | 1001 | 395 | 96 | 262 | 10 | 13.177 | 3.8362 | 1.38 | 43.78 |
| ATR14_20 | 1001 | 395 | 99 | 258 | 10 | 14.1451 | 3.6081 | 0.46 | 44.24 |
| ATR14_5 | 1001 | 395 | 91 | 266 | 12 | 11.4537 | 4.3915 | 0.46 | 39.63 |
| HYBRID_MAX_ZW_ATR_10 | 1001 | 395 | 95 | 262 | 11 | 12.3501 | 4.1029 | 0.92 | 41.94 |
| HYBRID_MAX_ZW_ATR_15 | 1001 | 395 | 97 | 261 | 10 | 13.2752 | 3.8362 | 0.92 | 43.78 |
| HYBRID_MAX_ZW_ATR_20 | 1001 | 395 | 99 | 258 | 10 | 14.1601 | 3.5877 | 0.92 | 44.7 |
| HYBRID_MAX_ZW_ATR_5 | 1001 | 395 | 91 | 266 | 12 | 11.4697 | 4.3915 | 0.46 | 39.63 |
| ZONE_WIDTH_10 | 1168 | 403 | 93 | 269 | 15 | 11.6939 | 4.2857 | 2.22 | 40.0 |
| ZONE_WIDTH_15 | 1168 | 403 | 98 | 266 | 12 | 12.2255 | 4.0994 | 0.89 | 41.33 |
| ZONE_WIDTH_20 | 1168 | 403 | 100 | 265 | 11 | 12.757 | 3.9286 | 0.89 | 43.56 |
| ZONE_WIDTH_5 | 1168 | 403 | 90 | 271 | 17 | 11.1624 | 4.4898 | 1.33 | 39.11 |

## MAE beyond structural Distal

- Valid target-before-invalidation observations: 88
- Target reached only after structural failure: 120
- Structural-failure-before-target observations: 903
- Successful zone-width percentiles: {'p50': 0.0, 'p75': 0.0, 'p80': 0.0, 'p90': 0.0, 'p95': 0.0}
- Successful ATR percentiles: {'p50': 0.0, 'p75': 0.0, 'p80': 0.0, 'p90': 0.0, 'p95': 0.0}
- Later-recovery zone-width percentiles: {'p50': 3.7071, 'p75': 8.0056, 'p80': 8.8708, 'p90': 12.5005, 'p95': 20.1388}
- Later-recovery ATR percentiles: {'p50': 1.8941, 'p75': 3.7024, 'p80': 4.7644, 'p90': 5.8192, 'p95': 7.4203}
- Failed zone-width percentiles: {'p50': 5.8459, 'p75': 15.6441, 'p80': 20.4116, 'p90': 43.1767, 'p95': 64.875}
- Failed ATR percentiles: {'p50': 3.4805, 'p75': 8.0185, 'p80': 10.498, 'p90': 21.2757, 'p95': 29.2987}

## Target availability

- AUTHENTICITY_INELIGIBLE: 49 (3.14%)
- AVAILABLE: 536 (34.36%)
- DIRECTION_RESTRICTION: 268 (17.18%)
- LIFECYCLE_INELIGIBLE: 189 (12.12%)
- NO_OPPOSING_ZONE_AT_PLANNING: 247 (15.83%)
- OPPOSING_FORMED_LATER: 271 (17.37%)

## Replay horizon sensitivity

| timeframe | horizon_candles | filled_sample | resolved | resolved_percent | target_first | invalidation_first | ambiguous |
|---|---|---|---|---|---|---|---|
| 15m | 20 | 223 | 182 | 81.61 | 19 | 156 | 7 |
| 15m | 40 | 223 | 189 | 84.75 | 20 | 162 | 7 |
| 15m | 80 | 223 | 202 | 90.58 | 21 | 174 | 7 |
| 15m | 160 | 223 | 206 | 92.38 | 22 | 177 | 7 |
| 75m | 12 | 144 | 113 | 78.47 | 10 | 101 | 2 |
| 75m | 24 | 144 | 118 | 81.94 | 10 | 106 | 2 |
| 75m | 48 | 144 | 121 | 84.03 | 10 | 109 | 2 |
| 75m | 96 | 144 | 122 | 84.72 | 10 | 110 | 2 |
| 125m | 12 | 75 | 55 | 73.33 | 2 | 53 | 0 |
| 125m | 24 | 75 | 57 | 76.0 | 2 | 55 | 0 |
| 125m | 48 | 75 | 58 | 77.33 | 2 | 56 | 0 |
| 125m | 96 | 75 | 58 | 77.33 | 2 | 56 | 0 |
| 1D | 20 | 506 | 410 | 81.03 | 26 | 379 | 5 |
| 1D | 40 | 506 | 428 | 84.58 | 28 | 395 | 5 |
| 1D | 80 | 506 | 440 | 86.96 | 30 | 405 | 5 |
| 1D | 160 | 506 | 443 | 87.55 | 30 | 408 | 5 |
| 1W | 8 | 220 | 142 | 64.55 | 19 | 121 | 2 |
| 1W | 13 | 220 | 154 | 70.0 | 22 | 129 | 3 |
| 1W | 26 | 220 | 166 | 75.45 | 23 | 140 | 3 |
| 1W | 52 | 220 | 172 | 78.18 | 24 | 145 | 3 |

## Tick size

Official NSE master-data specifications include a per-security Tick Size field, so trustworthy metadata can be incorporated through a maintained NSE security-master ingestion path. The current YahooProvider contract does not expose it, and this study did not download or hard-code an unverified substitute. No universal Rs 0.05 assumption was made. Source: https://nsearchives.nseindia.com/web/sites/default/files/inline-files/NSE-Masters%20Data-v1.6.pdf

## Look-ahead validation

- Entry and boundaries come from the prefix-reconstructed selected zone.
- Wilder ATR(14) uses the planning prefix only.
- Opposing targets must exist in the same symbol/timeframe prefix snapshot.
- Lifecycle and authenticity are evaluated from that prefix snapshot.
- Future zones are used only to classify why a target was unavailable, never to create a plan target.
- Future candles affect outcomes only after planning coordinates are frozen.

## Final decision

**Entry:** Freeze Proximal as Canonical Entry V1 only if the owner accepts it as the interaction coordinate, not as a promised fill. It leads Midpoint and Distal overall and on every timeframe; leave-one-symbol-out fill varies by less than one percentage point.

**Protective Stop:** Do not freeze any tested buffer. The 5%-20% zone-width, ATR, and hybrid candidates change relatively few target-first outcomes, while every valid target-before-invalidation case has zero excursion beyond Distal by definition. No exact stop formula is supported.

**Target:** Retain the same-timeframe nearest active Authentic opposing canonical zone. Availability is limited and missing targets must not be manufactured.

**Horizon candidates for further validation:** 15m=80 candles, 75m=48, 125m=48, 1D=80, 1W=52. These are saturation-based research windows, not frozen production rules.

**Same-candle ambiguity:** Keep UNKNOWN / SAME_CANDLE_AMBIGUOUS as canonical research treatment. Use stop-first and target-first only as conservative/optimistic sensitivity bounds.

**Implementation readiness:** Canonical Trade Planning V1 is not safe to implement as a complete engine because Protective Stop and replay horizon remain unresolved. Proximal Entry and opposing-zone Target architecture have sufficient evidence for separate owner approval.
