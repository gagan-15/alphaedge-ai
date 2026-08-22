# Milestone 11B - Large-Scale Entry Confirmation Validation

> **Frozen status:** Research approved and closed. No production Entry
> Confirmation rule is approved. See
> `docs/milestone-11-entry-confirmation-research.md`.

## 1. Dataset size and coverage

This is research only. No Entry Confirmation methodology was activated.

- Universe selection: first 100 symbols from the maintained NSE 500 universe,
  in deterministic constituent order; no symbol was cherry-picked.
- Successfully processed: 100/100; provider failures: 0.
- Historical source: provider-backed five-year Daily candles, split at canonical
  data breaks, with Weekly bars aggregated from those Daily candles.
- Daily: 523 valid segments, 109,661 candles, 5,243 interacted zones.
- Weekly: 523 valid segments, 23,488 candles, 955 interacted zones.
- Total: 133,149 candles and 6,198 point-in-time interactions.
- Demand: 2,979; Supply: 3,219.
- DBR: 1,508; RBR: 1,471; RBD: 930; DBD: 2,289.

The frozen Historical Evidence V1 artifact was not changed or used as an input.
It does not retain the interaction OHLC sequence required by this study.

## 2. Exclusions and failures

There were no symbol failures. Invalid market-data candles remained canonical
data-break boundaries. No interpolation or fabricated candle was used.

Five-year 15m, 75m and 125m evidence was not available from the current provider
at trustworthy coverage. Intraday and Daily-to-lower-timeframe conclusions are
therefore unresolved, not extrapolated.

## 3. Baseline results

All 6,198 interacted valid zones form the baseline:

| Outcome from interaction | Result |
| --- | ---: |
| >=1 zone width (ZW) | 4,782 / 6,198 = 77.15% |
| >=2 ZW | 2,972 / 6,198 = 47.95% |
| >=3 ZW | 1,947 / 6,198 = 31.41% |
| No structural failure in the bounded horizon | 1,248 / 6,198 = 20.14% |
| Median favorable excursion | 1.9317 ZW |

The baseline >=2 ZW 95% Wilson interval is 46.71%-49.20%.

## 4. Tiered confirmation results

The tiers are validation labels, not an activated methodology or score.

| State | Exact research definition | N / coverage | >=2 ZW after confirmation | Median post-confirmation MFE |
| --- | --- | ---: | ---: | ---: |
| Tier 1 | causal close recovery | 4,097 / 66.10% | 1,804 / 4,097 = 44.03% | 1.7037 ZW |
| Tier 2 `REACTION_DETECTED` | close recovery plus one independent response observation | 3,670 / 59.21% | 1,539 / 3,670 = 41.93% | 1.5428 ZW |
| Tier 3 `STRUCTURAL_CONFIRMATION` | causal micro-level close break plus 1 ZW displacement | 1,340 / 21.62% | 673 / 1,340 = 50.22% | 2.0091 ZW |

Tier 1 and Tier 2 did not improve the post-confirmation >=2 ZW rate over the
interaction baseline. Tier 3 improved it by only 2.27 percentage points while
retaining 21.62% of interactions.

## 5. Post-confirmation outcomes and uncertainty

| Cohort | >=2 ZW | 95% Wilson interval | Absolute difference vs baseline |
| --- | ---: | ---: | ---: |
| Baseline | 47.95% | 46.71%-49.20% | - |
| Tier 1 | 44.03% | 42.51%-45.55% | -3.92 pp |
| Tier 2 | 41.93% | 40.35%-43.54% | -6.02 pp |
| Tier 3 | 50.22% | 47.55%-52.90% | +2.27 pp |

The Tier 3 and baseline intervals overlap materially. This is not reliable proof
of incremental predictive value.

## 6. Delay and opportunity cost

| Tier | Median delay | P75 | P90 | Median move completed before confirmation |
| --- | ---: | ---: | ---: | ---: |
| Tier 1 | 0 candles | 0 | 1 | 1.4000 ZW |
| Tier 2 | 1 candle | 1 | 2 | 1.4427 ZW |
| Tier 3 | 4 candles | 7 | 12 | 2.9196 ZW |

Tier 3 generally arrived after almost three zone widths of movement. Sensitivity
to a late threshold should be studied later; no arbitrary cutoff was selected.

## 7. False positives

- Tier 1: 1,262 confirmations had less than 1 ZW subsequent reaction; 2,869
  later encountered structural failure in the bounded horizon.
- Tier 2: 1,354 had less than 1 ZW subsequent reaction; 2,458 later failed.
- Tier 3: 370 had less than 1 ZW subsequent reaction; 384 later failed.

Recurring causes were late recognition, confirmation after much of the move,
and later zone invalidation. Same-candle ordering makes many early cases unsafe.

## 8. False negatives

Among baseline >=2 ZW reactions, confirmation never appeared for:

- Tier 1: 554 / 2,972 = 18.64%.
- Tier 2: 759 / 2,972 = 25.54%.
- Tier 3: 1,742 / 2,972 = 58.61%.

Missed structures include immediate explosive moves, gaps, shallow touches and
one-candle reversals. Tier 3 misses most historically strong reactions.

## 9. Demand and Supply

| Side | Baseline >=2 ZW | Tier 1 post | Tier 2 post | Tier 3 post |
| --- | ---: | ---: | ---: | ---: |
| Demand (2,979) | 51.39% | 46.92% | 45.15% | 57.76% |
| Supply (3,219) | 44.77% | 41.26% | 38.96% | 42.69% |

Tier 3 helps Demand descriptively but not Supply. A symmetric production rule
is not supported.

## 10. Pattern results

| Pattern | N | Baseline >=2 ZW | Tier 1 | Tier 2 | Tier 3 |
| --- | ---: | ---: | ---: | ---: | ---: |
| DBR | 1,508 | 48.94% | 44.83% | 43.15% | 53.12% |
| RBR | 1,471 | 53.91% | 49.09% | 47.29% | 62.46% |
| RBD | 930 | 42.37% | 38.77% | 37.39% | 36.89% |
| DBD | 2,289 | 45.74% | 42.30% | 39.63% | 45.26% |

Structural confirmation separates RBR but fails to add value for RBD and DBD.

## 11. Timeframe results

| Timeframe | N | Baseline >=2 ZW | Tier 1 | Tier 2 | Tier 3 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Daily | 5,243 | 48.25% | 44.57% | 42.61% | 50.13% |
| Weekly | 955 | 46.28% | 41.18% | 38.30% | 50.70% |

Daily has adequate descriptive sample size, but the candidate architecture is
not sufficiently stable. Weekly remains smaller and does not justify freezing.
15m/75m/125m remain unresolved.

## 12. Same-timeframe versus lower-timeframe

This run validates same-timeframe features only. Weekly-to-Daily and
Daily-to-intraday mapping cannot be reconstructed safely from the stored records.
Lower-timeframe confirmation is not supported by current evidence.

## 13. Zone Quality relationship

Exact point-in-time Zone Quality was not joined to these newly reconstructed
interactions. Independence beyond Zone Quality is unresolved. Zone Quality was
not modified or used to create confirmation.

## 14. Trade Confidence relationship

Exact point-in-time Trade Confidence was not available for every reconstructed
interaction. No claim of incremental information beyond the frozen 40/35/25
Trade Confidence formula is made. Trade Confidence was unchanged.

## 15. Robustness analysis

- Symbols with >=10 observations: Tier 1 = 95, Tier 2 = 93, Tier 3 = 80.
- Median per-symbol post-confirmation >=2 ZW: Tier 1 43.75%, Tier 2 41.18%,
  Tier 3 50.00%.
- Tier 3 per-symbol range was 16.67%-92.31%, demonstrating instability.
- Period baseline/Tier 3: 2021-22 48.54%/47.68%; 2023-24 49.53%/54.22%;
  2025-26 45.50%/47.12%.

The apparent structural benefit is period- and symbol-sensitive.

## 16. Same-candle ambiguity

- Tier 1: 3,283 / 4,097 = 80.13%.
- Tier 2: 1,688 / 3,670 = 46.00%.
- Tier 3: 79 / 1,340 = 5.90%.

Ambiguous cases were not assumed to have favorable ordering. Current OHLC cannot
reliably order touch, reaction and failure within the candle.

## 17. Look-ahead validation

The replay creates canonical zones from Formation V1.1, begins monitoring only
after `leg_out_end_index`, uses fixed boundaries already known then, and scans
confirmation features forward one candle at a time. Micro structure uses only
the three pre-interaction bars and a causally observed close. Outcome bars do
not select confirmation. Future lifecycle state, future zones and Historical
Evidence are not inputs.

Focused tests lock event timing, explicit coverage loss and causal micro-level
construction.

## 18. Representative cases

Examples are identified by immutable research zone ID because this first
large-scale artifact did not persist display boundaries. Exact boundary display
is therefore a documented evidence gap, not reconstructed approximately.

| Type | Example | Interaction | Evidence and subsequent outcome |
| --- | --- | --- | --- |
| Demand useful | ADANIPOWER 1D DBR `ADANIPOWER-1D-101` | 2025-08-28 | structural at +3 candles; 52.61 ZW afterward; no bounded failure |
| Demand false | BRIGADE/other sampled structural cases | stored in analysis artifact | structural state followed by <1 ZW in sampled false-confirmation cohort |
| Demand missed | ATGL 1D DBR `ATGL-1D-88` | 2024-06-04 | no candidate state; large same-candle move/failure ambiguity |
| Demand none | AADHARHFC 1D RBR `AADHARHFC-1D-81` | 2024-10-04 | no confirmation; same-candle failure |
| Supply useful | ADANIPORTS 1D DBD `ADANIPORTS-1D-351` | 2023-01-20 | structural at +1 candle; 31.56 ZW afterward; no bounded failure |
| Supply false | AADHARHFC 1D RBD `AADHARHFC-1D-94` | 2024-10-08 | structural at +10; only 0.40 ZW afterward |
| Supply missed | sampled immediate/gap cases in analysis artifact | exact records retained | strong move without Tier 2/3; sequencing may be ambiguous |
| Supply none | AADHARHFC 1D DBD `AADHARHFC-1D-70` | 2024-09-03 | no confirmation; immediate structural failure |

## 19. Statistical conclusion

Percentages were calculated on post-confirmation movement only. Wilson intervals
show that Tier 3's small overall difference is not decisive. Large per-symbol
variation, side asymmetry and period variation prevent a reliable promotion.

## 20. Recommended candidate methodology

Do not submit a production methodology yet. Retain the research state model:

`NOT_INTERACTED -> INTERACTING -> REACTION_DETECTED -> STRUCTURAL_CONFIRMATION`

with `FAILED`, `AMBIGUOUS` and `INSUFFICIENT_DATA` outcomes. Continue treating
close recovery as early evidence, not confirmation. Do not create a score.

## 21. Final decision

- Confirmation adds descriptive evidence only at the structural tier.
- Tier 3 has the best quality/delay balance among tested candidates, but its
  coverage is only 21.62%, median delay is four bars, and 58.61% of strong
  reactions never reach it.
- A single candle is not enough because 80.13% of Tier 1 is same-candle ambiguous.
- Structural confirmation is not generally worth waiting for yet.
- Results are not stable across Supply, patterns, symbols or periods.
- Daily is researched but not ready for production; Weekly is not sufficiently
  validated; intraday and lower-timeframe confirmation are unresolved.
- Evidence is **not sufficient** to propose Canonical Entry Confirmation V1.

## 22. Validation

Required focused, leakage, deterministic and full regression results are listed
in the completion response after execution.

## 23. Files changed

Research-only files are listed in the completion response. Production engines,
API behavior, frontend and UI were not changed.

## 24. Guardrail confirmation

No Formation, boundary, lifecycle, authenticity, Zone Quality, HTF, Trend,
Trade Confidence, ranking, Dashboard qualification, Trade Planning or Historical
Evidence methodology changed. Entry Confirmation V1 was not implemented and
Milestone 11C was not started.
