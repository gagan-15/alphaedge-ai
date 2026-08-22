# Milestone 8 - Protective Stop Finalization Report

> Research only. Complete Canonical Trade Planning V1 remains inactive.

## Scope and controls

- Symbols: 28; successful series: 140/140
- Prefix-reconstructed zones: 1561
- Provider/date range: YahooProvider; 2021-08-17 00:00:00 to 2026-08-21 00:00:00
- Entry: frozen Proximal. Target: nearest eligible same-timeframe opposing canonical zone.
- Horizons: 15m=80, 75m=48, 125m=48, Daily=80, Weekly=52 candles.
- Same-candle stop/target sequence is UNKNOWN; no favorable ordering is assumed.

## Overall stop candidates

| stop_policy | eligible_trades | target_before_stop_percent | stop_before_target_percent | same_candle_ambiguous_percent | no_resolution_percent | median_risk | median_structural_rr | false_tight_stop_percent_of_target_reaching | mae_coverage_percent_of_target_reaching | excessively_wide_percent |
|---|---|---|---|---|---|---|---|---|---|---|
| ZONE_WIDTH_5 | 402 | 22.14 | 67.16 | 3.98 | 6.72 | 9.5449 | 4.4747 | 44.44 | 47.09 | None |
| ZONE_WIDTH_10 | 402 | 22.89 | 66.67 | 3.48 | 6.97 | 9.9994 | 4.2713 | 43.92 | 48.68 | 96.74 |
| ZONE_WIDTH_15 | 402 | 24.13 | 65.92 | 2.74 | 7.21 | 10.4539 | 4.0856 | 42.86 | 51.32 | 94.85 |
| ZONE_WIDTH_20 | 402 | 24.63 | 65.67 | 2.49 | 7.21 | 10.9085 | 3.9153 | 42.33 | 52.38 | 97.98 |
| ZONE_WIDTH_25 | 402 | 25.12 | 64.68 | 2.24 | 7.96 | 11.363 | 3.7587 | 41.8 | 53.44 | 98.02 |
| ZONE_WIDTH_30 | 402 | 25.62 | 63.93 | 2.24 | 8.21 | 11.8175 | 3.6141 | 40.74 | 54.5 | 98.06 |
| ATR14_5 | 394 | 22.84 | 67.26 | 2.79 | 7.11 | 9.933 | 4.3159 | 44.2 | 49.72 | None |
| ATR14_10 | 394 | 23.86 | 66.24 | 2.54 | 7.36 | 10.6464 | 4.0919 | 42.54 | 51.93 | 95.74 |
| ATR14_15 | 394 | 24.11 | 65.99 | 2.28 | 7.61 | 11.6314 | 3.7735 | 42.54 | 52.49 | 98.95 |
| ATR14_20 | 394 | 24.87 | 64.97 | 2.28 | 7.87 | 12.4728 | 3.5775 | 40.88 | 54.14 | 96.94 |
| ATR14_25 | 394 | 25.63 | 64.72 | 1.78 | 7.87 | 13.3675 | 3.4105 | 40.33 | 55.8 | 97.03 |
| ATR14_30 | 394 | 26.14 | 63.71 | 1.52 | 8.63 | 14.3593 | 3.2303 | 39.78 | 56.91 | 98.06 |
| HYBRID_MAX_ZW_ATR_5 | 394 | 22.84 | 67.26 | 2.79 | 7.11 | 9.933 | 4.3137 | 44.2 | 49.72 | None |
| HYBRID_MAX_ZW_ATR_10 | 394 | 23.86 | 66.24 | 2.54 | 7.36 | 10.6464 | 4.0919 | 42.54 | 51.93 | 95.74 |
| HYBRID_MAX_ZW_ATR_15 | 394 | 24.37 | 65.74 | 2.28 | 7.61 | 11.6314 | 3.7442 | 41.99 | 53.04 | 97.92 |
| HYBRID_MAX_ZW_ATR_20 | 394 | 24.87 | 64.97 | 2.28 | 7.87 | 12.5196 | 3.57 | 40.88 | 54.14 | 97.96 |
| HYBRID_MAX_ZW_ATR_25 | 394 | 25.89 | 64.47 | 1.52 | 8.12 | 13.461 | 3.4034 | 40.33 | 56.35 | 96.08 |
| HYBRID_MAX_ZW_ATR_30 | 394 | 26.9 | 63.2 | 1.27 | 8.63 | 14.3883 | 3.2159 | 38.67 | 58.56 | 96.23 |

## MAE beyond canonical Distal

### Target-reaching trades

`{'count': 189, 'beyond_distal_frequency_percent': 53.97, 'absolute_price': {'p50': 0.8999, 'p75': 14.05, 'p80': 19.8541, 'p85': 29.3, 'p90': 39.1866, 'p95': 62.6996, 'p97_5': 72.0173, 'p99': 149.0509}, 'zone_width_multiple': {'p50': 0.1428, 'p75': 1.9893, 'p80': 3.3316, 'p85': 4.6954, 'p90': 6.9603, 'p95': 11.0969, 'p97_5': 15.8106, 'p99': 24.2588}, 'wilder_atr14_multiple': {'p50': 0.0589, 'p75': 1.1028, 'p80': 1.6842, 'p85': 1.9591, 'p90': 2.4762, 'p95': 3.2887, 'p97_5': 3.9389, 'p99': 6.1076}}`

### Failed/invalidation trades

`{'count': 890, 'beyond_distal_frequency_percent': 100.0, 'absolute_price': {'p50': 39.4724, 'p75': 109.7582, 'p80': 135.0254, 'p85': 175.3047, 'p90': 241.7876, 'p95': 425.3042, 'p97_5': 666.9832, 'p99': 1028.4127}, 'zone_width_multiple': {'p50': 4.458, 'p75': 10.4208, 'p80': 11.8718, 'p85': 14.8081, 'p90': 20.7412, 'p95': 35.5932, 'p97_5': 50.275, 'p99': 64.7606}, 'wilder_atr14_multiple': {'p50': 2.568, 'p75': 5.16, 'p80': 6.1154, 'p85': 7.2352, 'p90': 9.4548, 'p95': 13.6381, 'p97_5': 19.1497, 'p99': 27.053}}`

## Robustness

Detailed JSON contains every stop by timeframe, Demand/Supply, pattern, symbol, year and empirical ATR/price volatility regime.

- Sector metadata coverage: 4 of 28 symbols. Unmapped symbols were not assigned invented sectors.
- Leave-one-symbol-out ranges are included for every candidate.
- Small groups are marked LIMITED and are not used for a firm decision.

## Final evidence decision

**1. Enough evidence to freeze Protective Stop V1? NO.** The target-reaching and failed distributions are separated in their centres, but overlap too widely for one defensible cutoff. Among target-reaching plans, 53.97% moved beyond Distal and the 75th percentile reached 1.9893 zone widths beyond it. A buffer large enough to retain most of those recoveries would materially expand risk and weaken structural meaning.

**2. Exact formula:** none is justified. Zone-width 5% to 30% raises target-before-stop from 22.14% to 25.62%, lowers stop-before-target from 67.16% to 63.93%, and lowers ambiguity from 3.98% to 2.24%, but median structural R:R falls from 4.4747 to 3.6141. ATR 5% to 30% gives similarly small outcome changes while median R:R falls from 4.3159 to 3.2303.

**3. Robustness:** no candidate behaves consistently enough across all five timeframes. The 125m eligible sample is only 14-15 plans per candidate; timeframe outcomes differ sharply; and maintained sector metadata covers only 4 of 28 symbols. Symbol, pattern, Demand/Supply, year, and empirical volatility breakdowns are retained in JSON, but they do not establish a stable universal threshold.

**4. Required next evidence:** a larger outcome-labelled dataset with reliable sector metadata, materially larger 125m coverage, and lower-timeframe sequencing for ambiguous candles. Validate candidate thresholds out of sample rather than selecting the best result from this grid.

**5. Trade Planning V1 readiness:** NOT SAFE to implement as a complete engine. Canonical Entry V1, structural invalidation, opposing-zone target architecture, ambiguity policy, and replay horizons remain approved; Protective Stop remains unresolved.
