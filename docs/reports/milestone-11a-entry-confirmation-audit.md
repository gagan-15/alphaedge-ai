# Milestone 11A - Entry Confirmation Audit and Methodology Research

## Decision

Milestone 11A is research only. No production Entry Confirmation methodology is
activated. The evidence supports a tiered state model for a larger validation,
but it is not sufficient to freeze Canonical Entry Confirmation V1.

## Existing and legacy code audit

| Area | Current rule | Production reach | Finding |
| --- | --- | --- | --- |
| `EntryConfirmationEngine.confirm` | volume AND SMA trend AND RSI momentum AND score >= 70 | Reachable only through legacy `GET /scanner/` via `ScannerService` and `MarketOpportunityService` | Deterministic but not zone-reaction confirmation. It uses the latest bar and a legacy blended score. |
| `MarketOpportunityService._confirmation_score` | `0.4 * legacy zone score + 20 * each passed indicator`, capped at 100 | Legacy scanner endpoint and Signals page | Duplicate legacy concept. It affects `Signals.tsx`, not canonical `/scanner/zones`. |
| `TradeSetupEngine` | manufactures entry, stop and target from zone plus configured buffers | Legacy scanner chain | Superseded for Stock Details by Canonical Trade Planning V1; must not be reused for Entry Confirmation. |
| `RiskManagementEngine` | requires legacy confirmation and minimum R:R | Legacy scanner chain | Execution-era code; not canonical Entry Confirmation. |
| `SwingDetector` | two left and two right bars; swing known only after right bars close | BOS/CHoCH engines and tests | Deterministic and conceptually reusable only if confirmation time includes the right-bar delay. |
| `BOSDetector` | configured close/high/low breaks confirmed swing, no default buffer | Standalone BOS/CHoCH engines | Deterministic, but not connected to canonical scanner-zone confirmation. High/low modes are weaker; close mode is preferable for research. |
| `CHoCHDetector` | opposite BOS relative to supplied trend | Standalone legacy engine | Deterministic but only as sound as supplied trend and delayed swing evidence. |
| `ZoneLifecycleEngine` | touch, visit, penetration, reaction and invalidation | Canonical production | Reusable source for interaction state only. It must not be reimplemented. |
| Frontend `Signals.tsx` | displays volume/trend/momentum and legacy confirmation score | User visible | Legacy user-facing confirmation. It is not the promoted Trade Confidence and is separate from canonical zone reaction. |
| Frontend `tradeConfidence.ts` | local presentation checks including “confirmation status” | Stock Details presentation helper | Presentation-only legacy wording; not a backend confirmation engine. |
| Strategy/demo components | text such as “structure confirmation” | Static/demo UI | No deterministic production calculation. |

The production application currently has two scanner paths. `GET /scanner/` is
the legacy indicator/confirmation/risk chain. `GET /scanner/zones` is the
canonical zone research path used by the scanner-first Dashboard. No current
canonical Entry Confirmation engine exists.

### Look-ahead audit of existing code

- `SwingDetector` uses right-side bars. Its `confirmation_index` correctly
  records when the swing becomes knowable, but any consumer using the pivot
  index as the event time would leak future bars.
- `BOSDetector` starts after `confirmation_index`, so its normal event timing is
  causal.
- The legacy Entry Confirmation engine uses the last available candle, but it
  is not tied to a zone interaction timestamp and cannot be replayed as a
  point-in-time zone confirmation without reconstruction.
- Static frontend labels are not evidence and must not be treated as such.

## Layer separation

Formation answers whether the zone formed correctly. Zone Quality measures the
zone. HTF, Trend and Trade Confidence describe context. Historical Evidence is
read-only historical description. Lifecycle owns interaction. Entry
Confirmation must only describe observable reaction after interaction.
Execution remains outside Milestone 11A.

## Dataset and coverage

The frozen Historical Evidence V1 SQLite model contains 37,725 zones, but it
does not retain the OHLC candles around interaction. It therefore cannot be
used to reconstruct wick, close, engulfing or micro-structure evidence without
fabrication.

A separate bounded provider-backed research replay was run without changing
the frozen dataset:

- NSE 500 symbols requested: 30
- Provider failures: 0
- Daily: 158 valid segments, 30,842 candles, 1,462 interactions
- Weekly: 158 valid segments, 6,612 candles, 254 interactions
- Total point-in-time interactions: 1,716
- Demand: 827; Supply: 889
- Patterns: DBR 429, RBR 398, RBD 234, DBD 655
- History: available provider history within the five-year request, split at
  invalid zero-range candles
- 15m, 75m and 125m: not evaluated; provider retention and an immutable
  interaction-candle dataset were not sufficient
- Same-timeframe versus lower-timeframe mapping: unresolved

The study is broad enough to reject weak ideas, but not broad enough to define
production thresholds or claim independent predictive value.

## Interaction definition findings

Canonical Lifecycle should remain the source of truth:

- `NOT_INTERACTED`: no post-formation candle range overlaps the canonical zone.
- `INTERACTING`: candle range overlaps the zone; penetration is measured
  continuously from proximal (0%) to distal (100%).
- `CROSSED_DISTAL`: traded beyond distal; canonical lifecycle invalidation
  applies.
- `LEFT_ZONE`: price separates beyond proximal in the expected direction.

Labels such as APPROACHING or DEEP_IN_ZONE should remain presentation bands over
continuous distance/penetration, not new methodology in 11A. Same-candle touch
and recovery is explicitly ambiguous because OHLC does not prove the intrabar
order.

## Candidate feature comparison

Baseline for all 1,716 interactions: 828 reached at least 2 zone widths
(48.25%); 355 had no structural failure in the 20-bar research horizon
(20.69%). These are reaction observations, not win rates.

| Feature proxy | N | Coverage | >=2 ZW | Median delay | Finding |
| --- | ---: | ---: | ---: | ---: | --- |
| Wick rejection | 949 | 55.30% | 56.80% | 1 bar | Modest separation; 389 same-candle ambiguous cases. Not sufficient alone. |
| Close recovery beyond proximal | 1,142 | 66.55% | 58.93% | 0 bars | Useful early evidence, but 929 same-candle cases are sequence-ambiguous. |
| Body engulfing response | 400 | 23.31% | 74.50% | 4 bars | Stronger separation with large coverage and timing cost. |
| One-zone-width displacement | 645 | 37.59% | 85.74% | 1 bar | Strong separation, but partly definitional because one zone width has already occurred. Must measure remaining opportunity. |
| Failed continuation | 746 | 43.47% | 65.55% | 1 bar | Useful intermediate evidence and balanced coverage. |
| Three-bar micro-structure close break | 391 | 22.79% | 89.00% | 4 bars | Strongest broad proxy, but high delay and only a provisional swing definition. |
| Relative-volume expansion | 974 | 56.76% | 57.29% | 0 bars | Little incremental separation on its own; data is optional. |
| Directional gap response | 102 | 5.94% | 93.14% | 6 bars | Strong but rare and late; requires separate gap handling. |

Demand baseline >=2 ZW was 50.54%; Supply was 46.12%. Feature separation was
directionally similar. Daily baseline was 48.50%; Weekly was 46.85%. Daily and
Weekly proxy results were also broadly similar, but Weekly samples were much
smaller.

## Delay, false positives and false negatives

- Wick and close evidence are early, but same-candle ordering is often unknown.
- Engulfing and micro-structure evidence arrive around four bars later and
  retain only 23% of interactions.
- Gap evidence arrives around six bars later and retains only 6%.
- Micro structure misses approximately 77% of interactions, including immediate
  explosive reactions and shallow touches.
- Wick rejection remains vulnerable to a temporary bounce followed by distal
  failure. A representative Demand false signal was `360ONE 1D RBR`, interaction
  2021-12-03; wick evidence appeared but structural failure followed.
- Engulfing inside congestion and a close recovery without displacement remain
  likely false-positive structures.
- Exact movement already completed at confirmation, remaining structural-target
  room, and “too late” frequency were not safely reconstructed in this bounded
  output. A production proposal must not pretend proximal was executable after
  delayed confirmation.

## Representative cases

| Type | Case | Interaction | Evidence | Research outcome |
| --- | --- | --- | --- | --- |
| Demand clean | 360ONE 1D RBR | 2022-01-25 | displacement, wick rejection and later micro break | 9.77 ZW MFE; survived horizon |
| Demand weak/no evidence | 360ONE 1D DBR | 2025-08-28 | no studied feature | 0.44 ZW; distal failure |
| Demand false evidence | 360ONE 1D RBR | 2021-12-03 | wick rejection only | 1.83 ZW; later distal failure |
| Demand immediate | 360ONE 1D DBR | 2021-10-22 | same-candle displacement; sequence ambiguous | 15.07 ZW MFE; same-candle failure ambiguity |
| Supply clean | 3MINDIA 1D DBD | 2023-09-29 | displacement, wick rejection and micro break | 3.79 ZW MFE; survived horizon |
| Supply weak/no evidence | 360ONE 1D DBD | 2022-06-27 | no studied feature | 0.21 ZW; distal failure |
| Supply false evidence | 360ONE 1D DBD | 2022-03-17 | wick rejection only | 2.19 ZW; later distal failure |
| Supply immediate | 360ONE 1D DBD | 2022-11-15 | immediate displacement | 5.36 ZW MFE |

These are audit examples, not tuned fixtures.

## Architecture comparison

| Option | Strength | Main weakness | Recommendation |
| --- | --- | --- | --- |
| Single-candle rejection | early and simple | same-candle ambiguity and weak separation | Do not use alone. |
| Response displacement | objective | confirmation may consume the move | Retain as reaction evidence, not automatic execution. |
| Micro structure | strongest bounded separation | four-bar median delay, low coverage, swing-definition risk | Validate on a larger immutable candle dataset. |
| Combined binary rule | fewer false positives | brittle and loses many valid reactions | Do not freeze yet. |
| Tiered evidence/state model | explains progression without claiming certainty | needs larger causal validation | Recommended research direction. |

## Recommended candidate state model

1. `NOT_INTERACTED`: canonical Lifecycle reports no interaction.
2. `INTERACTING`: active canonical overlap with continuous penetration evidence.
3. `REACTION_DETECTED`: causal close recovery plus at least one independent
   response observation; same-candle cases remain `AMBIGUOUS` unless lower-TF
   data resolves order.
4. `STRUCTURAL_CONFIRMATION`: a causally known close breaks a deterministic
   pre-interaction micro level and meaningful response displacement is present.
5. `FAILED`: canonical distal invalidation.
6. `INSUFFICIENT_DATA`: missing bars, unreliable volume, unsupported mapping or
   unresolved intrabar order.

This is the candidate architecture for the next validation, not Canonical Entry
Confirmation V1. No 0-100 score is recommended.

## Timeframe decision table

| Zone timeframe | Evidence | Recommendation |
| --- | --- | --- |
| 15m | no immutable study coverage | unresolved |
| 75m | no immutable study coverage | unresolved |
| 125m | no immutable study coverage | unresolved |
| Daily | 1,462 interactions; same-TF proxies show separation | same-TF states can be studied; lower-TF mapping unresolved |
| Weekly | 254 interactions; broadly similar but smaller sample | same-TF evidence is exploratory; Daily confirmation mapping needs causal study |

## Relationship to frozen engines

The bounded records were not identical joins to the frozen 37,725-zone artifact,
so independent separation within Zone Quality and Trade Confidence bands was
not established. Historical Evidence was not used as a feature. Confirmation
must remain separate from Zone Quality, HTF, Trend, Trade Confidence, ranking,
qualification and Trade Planning.

## Answers to the approval questions

- Confirmation appears to add information beyond touch in this bounded sample,
  but independence is not proven.
- Micro-structure, displacement and engulfing proxies separated most; all cost
  coverage or timing.
- Candle rejection alone is insufficient.
- Micro structure may be useful, but its delay and provisional definition need
  larger causal validation.
- A timeframe hierarchy cannot yet be approved.
- Opportunity loss is material: stronger proxies retain only 23-38% of zones.
- Exact “too late” frequency remains unresolved.
- Demand and Supply behave similarly enough to keep symmetric research logic.
- Evidence does not cover all five timeframes.
- Incremental value beyond Zone Quality and Trade Confidence is unproven.
- False positives include transient bounces, congestion engulfing and recovery
  without displacement.
- False negatives include immediate reversal, gap-away, shallow touch and
  strong response without a textbook candle.
- Evidence is not sufficient to define Canonical Entry Confirmation V1.
- Next evidence required: immutable interaction-level OHLC for all supported
  timeframes, exact causal event prices, same/lower-timeframe alignment, target
  room at confirmation, and ZQ/TC-stratified out-of-sample evaluation.

## Production safety

Research imports remain one-way: production does not import the Milestone 11A
module or runner. No production engine, API, UI, methodology, rank, score,
qualification, historical dataset or execution behavior changed.
