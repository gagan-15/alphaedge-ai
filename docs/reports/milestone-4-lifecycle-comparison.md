# Milestone 4 - Canonical Lifecycle Comparison

## Scope

The frozen comparison corpus contains six deterministic zones covering Fresh,
Tested, Retested, Reacting, Invalidated and manually Removed outcomes. Formation,
boundaries, authenticity, quality, confidence, ranking and recommendations are
unchanged. Historical records remain available after invalidation or removal.

## Before and after

| Metric | Before lifecycle evaluation | After lifecycle evaluation |
|---|---:|---:|
| Zones | 6 | 6 |
| Fresh zones | Unclassified | 1 |
| Tested zones | Unclassified | 5 |
| Retested zones | Unclassified | 1 |
| Active Reacting zones | Unclassified | 1 |
| Invalidated zones | Unclassified | 1 |
| Removed from active engine | Unclassified | 2 |
| Average maximum penetration | Unclassified | 36.6667% |
| Maximum penetration | Unclassified | 100.0000% |

The removed count contains one automatically removed invalidated zone and one
manual removal. Neither historical record was deleted.

## Canonical behavior verified

- Freshness begins at activation and ends on the first post-formation wick tag.
- Exact Proximal contact counts as the first test at 0% penetration.
- Consecutive candles in one continuous interaction remain one visit.
- A second distinct visit becomes a retest.
- Current and maximum penetration are stored separately and clamped to 0-100%.
- Any trade beyond Distal records failure evidence and invalidates immediately.
- Invalidation automatically removes the zone from active recommendations.
- Manual removal retains all visits and interactions.
- Projection records end at invalidation, removal or the end of available data.
- Reacting begins after entry and a confirmed cross back beyond Proximal.
- Reacting completes after travel of at least 5% of zone width beyond Proximal.

## Regression result

The complete backend regression suite passed. Backend lint, frontend lint and
the frontend production build also passed. No non-lifecycle engine or UI file
was changed.
