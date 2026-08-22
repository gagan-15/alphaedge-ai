# Canonical Formation V1.1 - Frozen

Status: **Current production methodology**  
Frozen: **2026-08-13**

Canonical Formation V1.1 includes the approved candle classification, Base,
Leg-In, Leg-Out, pattern, and boundary behavior together with the conservative
Leg-In structural gate.

## Frozen Leg-In structural gate

A formation is rejected only when all three evidence groups agree:

1. Directional displacement is at most `0.25` zone widths and directional
   efficiency is at most `0.10`.
2. Pre-Leg-In occupancy is at least `0.90`.
3. At least one additional congestion confirmation exists:
   - adjacent body overlap is at least `0.50`;
   - at least `2` direction changes;
   - the approach stopped for `SECOND_PAUSE_OR_CONGESTION`; or
   - directional efficiency is at most `0.05`.

The canonical rejection state is
`LEG_IN_STRUCTURE_INVALID_CLEAR_CONGESTION`. Its detailed reason codes and
the broader structural evidence remain attached to diagnostics.

One-candle and multi-candle Leg-Ins remain valid when this combined rejection
rule does not apply. No single weak metric, wick overlap, shadow state, or
missing history rejects a formation by itself.

## V1.1 extreme pre-Base congestion branch

V1.1 preserves the complete V1 rule above and adds one conservative rejection
branch. `LEG_IN_EXTREME_PRE_BASE_CONGESTION` applies only when every condition
below is true:

- pre-Leg-In occupancy is exactly `1.00`;
- adjacent candle-body overlap is exactly `1.00`;
- the structural walk stops at `SECOND_PAUSE_OR_CONGESTION`;
- the approach contains at least `1` direction change;
- directional efficiency is at most `0.46`; and
- directional displacement is at most `0.50` zone widths.

This branch does not reject from wick overlap, occupancy, body overlap, or the
`CONGESTED` diagnostic state alone.

## Freeze protection

Do not tune Formation, Base, Leg-Out, boundaries, or Leg-In without explicit
product approval. Preserve:

- the thresholds and combined gate above;
- its deterministic reason codes;
- the frozen multi-timeframe fixtures;
- the removed-zone comparison report;
- SONACOMS, BLS, SCHNEIDER, AMBER, ATHERENERG, and NESTLEIND rejection tests;
  and
- AUBANK, CHOICEIN, MAXHEALTH, and HINDALCO survivor tests.

The frozen comparison report is stored at
`tests/fixtures/leg_in_structural/leg_in_formation_v1_1_report.json`. The V1
report remains preserved for historical comparison.

Trade Confidence and legacy AI Score promotion remain separate, parked work.
