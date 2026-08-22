# Milestone 2 - Canonical Boundary Comparison

## Scope

This comparison uses the frozen deterministic formation corpus from Milestone
1.2/1.3. Formation, pattern, created index and accepted-zone count are unchanged.
`Before` is the former Wick-to-Wick production boundary. `After` is the selected
canonical boundary. All comparison cases use the synthetic symbol named in the
table and the 1D timeframe.

## Changed zones

| Symbol | Timeframe | Pattern | Old Proximal | New Proximal | Old Distal | New Distal | Selected | Wick-to-Wick alternate | Reason |
|---|---:|---|---:|---:|---:|---:|---|---|---|
| SYNTH-DBR | 1D | DBR | 94.00 | 93.00 | 91.00 | 91.00 | Standard Body-to-Wick | 94.00-91.00 | Proximal moved from highest base wick to highest base body. |
| SYNTH-RBR | 1D | RBR | 92.00 | 90.50 | 89.00 | 89.00 | Standard Body-to-Wick | 92.00-89.00 | Proximal moved from highest base wick to highest base body. |
| SYNTH-RBD | 1D | RBD | 98.00 | 99.50 | 101.00 | 101.00 | Standard Body-to-Wick | 98.00-101.00 | Proximal moved from lowest base wick to lowest base body. |
| SYNTH-DBD | 1D | DBD | 92.00 | 93.00 | 95.00 | 95.00 | Standard Body-to-Wick | 92.00-95.00 | Proximal moved from lowest base wick to lowest base body. |
| SYNTH-WEAK-DBR | 1D | DBR | 97.00 | 96.00 | 94.00 | 94.00 | Standard Body-to-Wick | 97.00-94.00 | Proximal moved from highest base wick to highest base body. |
| SYNTH-EXTENDED-DBR | 1D | DBR | 96.00 | 95.00 | 93.00 | 93.00 | Standard Body-to-Wick | 96.00-93.00 | Proximal moved from highest base wick to highest base body. |

## Exceptional marking verification

Exceptional boundaries were verified independently for the approved pattern
and source combinations:

- DBR: overlapping Leg-In and overlapping Leg-Out.
- RBR: overlapping Leg-Out.
- RBD: overlapping Leg-In and overlapping Leg-Out.
- DBD: overlapping Leg-Out.

The standard Body-to-Wick boundary remains stored when an exceptional distal is
selected. The Wick-to-Wick representation also remains stored as an alternate.

## Counts

- Accepted zones before: 6
- Accepted zones after: 6
- Zone identities changed: 0
- Zones with changed selected boundaries: 6
- Standard Body-to-Wick selected: 6
- Exceptional selected in the frozen comparison corpus: 0
- Exceptional boundary unit scenarios passed: 4
- Wick-to-Wick alternate boundaries stored: 6
- Zones added or removed by boundary calculation: 0

## Regression result

The complete backend suite passed. The boundary migration changed coordinates
only. No formation, lifecycle, quality, confidence, ranking or UI logic changed.
