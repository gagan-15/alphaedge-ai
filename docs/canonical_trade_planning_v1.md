# AlphaEdge Canonical Trade Planning V1

Status: **FROZEN production methodology**

Version: `Canonical Trade Planning V1` (`1`)

Freeze approved: 2026-08-18

This methodology must not be tuned or modified without explicit approval.

Canonical Trade Planning V1 consumes the exact selected canonical zone and
same-snapshot canonical opposing zones. It does not redetect or reconstruct a
zone from a later market-data snapshot.

## Frozen structural rules

- Demand entry reference: proximal (upper) boundary.
- Supply entry reference: proximal (lower) boundary.
- The full zone is named the interaction range, not an entry range.
- Structural invalidation is the distal boundary.
- The target is the nearest directionally-ahead, authentic, lifecycle-active
  opposing canonical zone proximal boundary on the same symbol, timeframe and
  snapshot.
- No target produces a `PARTIAL` plan. No 1R, 2R or 3R target is manufactured.
- A target produces structural available room and structural reward per share.

## Execution policy separation

V1 does not define a universal protective stop. `protective_stop`,
`risk_per_share` and `risk_reward` remain null. Structural invalidation must not
be presented as an execution-ready stop. A future Execution/Risk Policy layer
may define protective-order placement without changing this structural plan.

## Legacy path

`TradeSetupEngine` remains available for the existing Signals compatibility
path. It is deprecated for canonical Stock Details planning and does not control
the Canonical Trade Planning V1 response.

The research replay remains separate. Its candidate stop policies and frozen
evaluation horizons are research evidence, not production execution policy.

## Frozen research policy

- When a future target and execution stop are touched in the same OHLC candle
  and lower-timeframe ordering is unavailable, the result is `UNKNOWN`.
- Replay evaluation horizons remain 15m=80 candles, 75m=48, 125m=48,
  Daily=80 and Weekly=52. Expiry of a replay horizon does not invalidate a
  live zone.

## Regression locks

The following must not change as part of Trade Planning work:

- Canonical Formation V1.1 and Leg-In/Base/Leg-Out evidence
- canonical zone boundaries
- lifecycle and authenticity methodology
- Zone Quality
- higher-timeframe location and Canonical Trend
- Trade Confidence and contextual ranking
- primary-zone selection and Dashboard qualification
- recommendations and existing Signals compatibility behavior

Canonical Trade Planning V1 must continue to preserve the selected zone ID,
symbol, timeframe, snapshot and methodology version. It must reject stale or
out-of-sync inputs and must never manufacture a protective stop, risk per share,
R:R, or 1R/2R/3R target.
