# Milestone 10 — Historical Evidence (Frozen)

## Status

Milestone 10 is the frozen and closed production architecture for displaying historical
zone research. It is informational and read-only. It does not contribute to
zone detection, scores, ranking, qualification, recommendations, or trade
planning.

- Architecture version: `historical-evidence-v1`
- Dataset version: `milestone-9c.1`
- Freeze status: `CLOSED`

## Frozen dataset

- Historical evidence version: `milestone-9c.1`
- Methodology fingerprint:
  `034ebdd6c52e0c161fda7cde9be4157e9ad250786fe98c3b0f02bfbc5030d015`
- Population: 37,725 historical zones
- Research period: 2021-08-18 through 2026-08-18
- Universe: frozen NSE 500 research population
- Supported timeframes: Daily (`1D`) and Weekly (`1W`)

Trade Confidence distribution:

| Label | Historical zones |
| --- | ---: |
| VERY_HIGH | 0 |
| HIGH | 270 |
| MODERATE | 7,237 |
| LOW | 5,141 |
| CONFLICTED | 2,653 |
| INSUFFICIENT_CONTEXT | 22,424 |

The immutable SQLite artifact is built from the frozen Milestone 9C shards.
Source checksums are locked in
`backend/historical_evidence/constants.py`. Ordinary API requests query only
the SQLite read model; they do not load raw Milestone 9C JSON.

## Architecture

The product flow is strictly downstream:

`frozen Milestone 9C shards -> immutable SQLite artifact -> read-only repository -> service -> API -> UI`

The Historical Evidence package does not import or call market-data providers
or production canonical engines. The current zone is used only to define a
comparison cohort. It is never inserted into the frozen dataset.

Milestone 10F runtime behavior is also frozen: immutable read-only SQLite,
cached immutable metadata and cohort summaries, SQLite-native aggregation,
and no provider or canonical-engine work on Historical Evidence requests.

Available endpoints:

- `GET /historical-evidence/metadata`
- `GET /historical-evidence/summary`
- `GET /historical-evidence/zones`
- `GET /historical-evidence/comparable-zone`

Pagination and sorting are server-side and deterministic. Sort fields are
allow-listed by the repository.

## Metric definitions and denominators

- Historical Zones: every frozen historical zone in the selected cohort.
- Interacted Zones: historical zones with a recorded post-formation
  interaction.
- Interaction Rate: interacted zones / historical zones.
- At least 1, 2, 3, or 5 zone widths: qualifying historical reactions /
  interacted zones.
- Structural Survival: structurally surviving zones / interacted zones.
- Structural Target Availability: zones with an eligible opposing structural
  target / interacted zones.
- Structural Target Achievement: achieved structural targets / zones with an
  available structural target.
- Median MFE: median favorable excursion measured in canonical zone widths.
- Median MAE: median adverse excursion measured in canonical zone widths.

Every displayed percentage retains its numerator and denominator. Historical
reaction measurements are research observations, not trading outcome claims.
Historical behavior does not guarantee future results.

## Comparable cohort hierarchy

The backend resolves the hierarchy in one request:

1. Same timeframe, direction, pattern, Zone Quality label, and Trade
   Confidence label.
2. Same timeframe, direction, Zone Quality label, and Trade Confidence label.
   Pattern is broadened.
3. Same timeframe, direction, and Trade Confidence label. Zone Quality is
   broadened.

The first level with at least 30 interacted observations is selected. The
exact Level 1 historical and interacted counts are always disclosed. If all
levels contain fewer than 30 interacted observations, Level 3 is returned as
insufficient. The hierarchy never crosses timeframe, direction, or Trade
Confidence label and never substitutes HIGH for VERY_HIGH.

## Reliability

| Interacted observations | Reliability |
| ---: | --- |
| fewer than 30 | INSUFFICIENT |
| 30–99 | EXPLORATORY |
| 100–299 | MODERATE_EVIDENCE |
| 300 or more | STRONGER_EVIDENCE |

Reliability is calculated by the backend and displayed unchanged by the
frontend.

## Unsupported and empty states

- Intraday current zones: comparable large-scale evidence is unavailable;
  Daily or Weekly evidence is never substituted.
- VERY_HIGH: the frozen dataset contains zero observations; HIGH is never
  substituted.
- Empty Level 3 cohort: no comparable historical evidence is returned.
- Small Level 3 cohort: the cohort is returned with `INSUFFICIENT` reliability.
- Dataset version mismatch: HTTP 409.
- Current-methodology mismatch: HTTP 409 and no stale statistics are shown.

## Version and immutability safety

The API verifies `historical_evidence_version` before reading. Comparable-zone
requests also verify the current canonical Formation version against the
frozen dataset metadata. The SQLite connection uses read-only mode and its
artifact is reconciled against the frozen count and Trade Confidence
distribution.

## Frozen validation anchors

- HIGH, at least 2 zone widths: 177 / 189 = 93.65%
- MODERATE, at least 2 zone widths: 4,984 / 5,837 = 85.39%
- RELIANCE Level 1: 1,567 historical zones and 1,276 interacted zones
- RELIANCE Level 1, at least 2 zone widths: 1,102 / 1,276 = 86.36%
- RELIANCE Level 1, structural target achievement: 274 / 413 = 66.34%

These anchors are regression checks only. They must not be used as ranking
weights or presented as guaranteed future outcomes.

## Product separation and disclosures

Historical Evidence is informational research evidence only. It is not a win
probability and does not guarantee future performance. It does not affect:

- current-zone acceptance
- Zone Quality
- higher-timeframe location or Trend
- Trade Confidence
- contextual ranking or primary-zone selection
- Dashboard qualification
- Canonical Trade Planning V1

## Change control

The Milestone 10 architecture, dataset version, metric definitions,
denominators, fallback hierarchy, reliability bands, and disclosures are
frozen. Any future dataset or methodology must use a new explicit version and
must not silently replace `milestone-9c.1`.

Milestone 10 is closed. Milestone 11 is outside this freeze and has not started.
