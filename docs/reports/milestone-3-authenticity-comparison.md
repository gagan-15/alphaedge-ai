# Milestone 3 - Canonical Authenticity Comparison

## Scope

The frozen comparison corpus contains five isolated, deterministic scenarios:
an original zone, a reaction relationship, a tick-normalized duplicate, a
nested relationship and a partial overlap. The engine classifies existing
zones without changing formation, boundaries, lifecycle, quality, confidence,
ranking or recommendation output.

## Before and after

| Scenario | Zones Before | Zones After | Authentic | Reaction | Duplicate | Nested | Overlapping | Good Closing |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Original | 1 | 1 | 1 | 0 | 0 | 0 | 0 | 0 |
| Reaction | 2 | 2 | 1 | 1 | 0 | 0 | 0 | 1 |
| Duplicate | 2 | 2 | 1 | 0 | 1 | 0 | 0 | 0 |
| Nested | 2 | 2 | 1 | 0 | 0 | 1 | 0 | 0 |
| Partial overlap | 2 | 2 | 1 | 0 | 0 | 0 | 1 | 0 |
| **Total** | **9** | **9** | **5** | **1** | **1** | **1** | **1** | **1** |

## Classification changes

- Zones removed or merged: 0
- Zones retaining their existing formation and boundaries: 9
- Zones receiving `AUTHENTIC`: 5
- Zones receiving `NON_AUTHENTIC`: 4
- Zones whose authenticity changed from previously unclassified: 9
- Reaction zones detected: 1
- Duplicate occurrences detected: 1
- Nested child zones detected: 1
- Partially overlapping later zones detected: 1
- Good Closing zones: 1

## Identity and relationship checks

- Duplicate identity requires the same symbol, timeframe, pattern, canonical
  origin and tick-normalized canonical boundaries.
- Duplicate occurrences share one `zone_id` but retain distinct occurrence IDs.
- Reaction records retain the parent ID, penetration depth, timestamp and
  wick/body source.
- Nested parent and child zones both remain present and are not merged.
- Partial overlaps retain both zones and store the smaller-zone overlap ratio.
- Good Closing is stored as evidence and does not change a non-authentic result.

## Regression result

The complete backend regression suite passed. Frontend lint and production
build also passed. No production UI, scanner ranking, alert, lifecycle, quality,
confidence or recommendation code was changed.
