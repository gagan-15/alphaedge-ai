# Milestones 1.2 and 1.3 Formation Comparison

> Historical comparison report. The current frozen production methodology is
> [Canonical Formation V1](../canonical_formation_v1.md).

## Scope

This report compares the frozen pre-migration detector with the canonical
candle-classification and zone-formation engine on the same deterministic
seven-case OHLC corpus. It measures formation only. Boundary, lifecycle,
quality, confidence, recommendation, ranking, and UI behavior are excluded.

## Zone Output

| Measure | Before | After | Change |
| --- | ---: | ---: | ---: |
| Total zones | 6 | 6 | 0 |
| New zones | 0 | 1 | +1 |
| Removed zones | 0 | 1 | +1 intentional removal |

New zone:

- `four_base_very_strong_gap`: DBR with four base candles. The canonical
  engine accepts it because the departure is classified Very Strong.

Removed zone:

- `boundary_50_percent`: the former detector treated an exact 50% body ratio
  as a base. The canonical engine classifies it as a Boundary Candle, so it
  cannot form a base.

## Pattern Distribution

| Pattern | Before | After |
| --- | ---: | ---: |
| DBR | 3 | 3 |
| RBR | 1 | 1 |
| RBD | 1 | 1 |
| DBD | 1 | 1 |

The aggregate distribution is unchanged, although one DBR was replaced by a
different, canonically valid DBR.

## Accepted Base Candle Count Distribution

| Base candles | Before | After |
| --- | ---: | ---: |
| 1 | 6 | 5 |
| 2 | 0 | 0 |
| 3 | 0 | 0 |
| 4 | 0 | 1 |
| 5 | 0 | 0 |

The comparison corpus also contains one two-candle base candidate whose
Leg-Out is invalid. It is evaluated but does not produce a zone.

## Leg Validation Statistics

Canonical candidate evaluation across the corpus:

| Validation | Valid | Invalid |
| --- | ---: | ---: |
| Leg-In | 7 | 0 |
| Leg-Out | 6 | 1 |

Accepted canonical departure strengths:

| Strength | Count |
| --- | ---: |
| Weak | 1 |
| Strong | 4 |
| Very Strong | 1 |

The legacy detector did not expose canonical multi-candle Leg-In/Leg-Out or
Weak/Strong/Very Strong classifications, so those legacy sub-counts are not
reported as if they were equivalent measurements.

## Regression Findings

- No unintended regression was found in the automated suite.
- Exact-50% base removal is an approved methodology change.
- Conditional four/five-candle base support is an approved methodology
  change and is guarded by the Very Strong departure requirement.
- Wick-to-wick zone boundaries remain unchanged and are protected by a
  regression test.
- Lifecycle, zone quality, trade confidence, recommendations, scanner
  ranking, and UI were not changed.

## Verification

- Backend lint: passed.
- Backend tests: 368 passed.
- Frontend lint and production build: passed.
- The comparison dataset and expected delta are stored in
  `tests/fixtures/canonical_formation_cases.py`.
