# Milestone 7F - Canonical Trade Confidence Promotion

## Product ownership

The user-facing confidence model is AlphaEdge Canonical Trade Confidence:

- 40% AlphaEdge Canonical Zone Quality
- 35% canonical higher-timeframe location
- 25% Canonical Trend

Zone Quality remains a separate measure of how well the zone itself was formed.
Trade Confidence describes the available market context and is not a BUY, SELL,
or entry instruction.

## Ranking

Dashboard ordering and primary-zone selection share one contextual comparator.
It orders available Very High, High, and Moderate context first; then partial
High and Moderate context; then Low, Conflicted, and Insufficient Context.
Within a bucket it uses Trade Confidence, Zone Quality, distance, and stable zone
identity in that order.

## Retired runtime path

The browser no longer requests candles and Stock Details for every scanner row
to calculate the legacy AI Score. The historical evaluator remains audit-only
under `scripts/audit` and does not execute in normal Dashboard or Stock Details
rendering.

## Future evidence ownership

- Future market/context engines own sector strength, relative strength versus
  Nifty, market breadth, and validated institutional or sentiment evidence.
- Future Entry/Execution owns RSI where appropriate, volume confirmation, and
  confirmation candles.
- Trade Planning owns entry, stop, target, risk/reward, position sizing, and
  current-price suitability.

None of these inputs are part of the frozen 40/35/25 Trade Confidence formula.
