# Milestone 5 - AlphaEdge Canonical Zone Quality Engine

## Purpose

The **AlphaEdge Canonical Zone Quality Score** measures how well the zone itself
was formed. It does not measure
the chance of profit and does not include market direction, distance, targets,
risk/reward, higher-timeframe alignment, user preferences, AI Score, or Trade
Confidence.

## Methodology ownership

The score must not be described as an explicit GTF score. Its methodology is:

1. GTF-derived formation philosophy and canonical evidence, including Base,
   departure, freshness/lifecycle, closing/structure, and authenticity facts.
2. AlphaEdge deterministic normalization and bounded component weights.
3. AlphaEdge Canonical Zone Quality Score on a 0-100 scale.

GTF does not define the exact 0-100 weights or normalization formulas below.
Those are deterministic AlphaEdge software decisions. Any separate explicit GTF
Trade Score remains a different concept and is not replaced by this engine.

## Previous behavior

The legacy score added freshness (30), measured departure strength (35), touch
points (20), and a merge bonus (15). A fresh, untouched zone with maximum
departure and no merge therefore repeatedly scored 85. It did not use the
preserved canonical base, Leg-In, Leg-Out, closing, lifecycle, or authenticity
evidence in a sufficiently detailed way.

## Canonical weights

| Component | Maximum |
|---|---:|
| Base quality | 15 |
| Departure quality | 30 |
| Leg-Out versus Leg-In dominance | 15 |
| Structural clearance | 15 |
| Lifecycle quality | 15 |
| Authenticity quality | 10 |
| Total | 100 |

## Normalization

- Base quality: 75% body compactness and 25% range compactness. Body
  compactness is `1 - clamp(mean body ratio / 0.5)`. Range compactness is
  `1 - clamp(mean range-to-median / 1.5)`. If canonical range-to-median is not
  available, only that sub-factor receives a neutral 0.5 value.
- Departure quality: equal bounded contributions from explosive-candle ratio,
  exciting-candle ratio, mean body ratio, range relative to median,
  displacement relative to zone width, and canonical departure class.
- Dominance: `clamp((Leg-Out body / Leg-In body - 0.5) / 2.5)`.
- Clearance: directional close clearance divided by zone width, capped at two
  zone widths.
- Lifecycle: Fresh 100%; Reacting/Testing 90% down to 55% according to canonical
  penetration; Tested 50%; Retested/Mitigated 25%; Invalidated/Removed 0%.
- Authenticity: Authentic 100%; Non-Authentic 30%; unavailable 50% and explicitly
  marked `AUTHENTICITY_UNAVAILABLE`.

All ratios are clamped before weighting. Extreme candles cannot force the total
above 100. The engine returns the total, established AlphaEdge quality label,
component scores, evidence facts, and deterministic reason codes.

The existing public label convention is preserved: Excellent (90+), Strong
(80-89), Good (70-79), Average (60-69), and Weak (below 60).

## Separation of responsibilities

- Formation remains the only source of Leg-In, Base, Leg-Out, gap and closing
  evidence.
- Lifecycle and authenticity remain their own canonical engines.
- Dashboard qualification still decides whether a zone appears.
- AlphaEdge Canonical Zone Quality only describes strength and does not filter
  Dashboard results.
- HTF and Trade Confidence are not AlphaEdge Canonical Zone Quality inputs.

## NSE 500 Daily runtime audit (2026-08-10)

- Symbols processed: 500 of 500; failures: 0
- Canonical zones: 862
- Formation-qualified zones: 79
- Lifecycle-qualified Dashboard zones: 47
- Score range: 53.8 to 93.5
- Mean: 76.37; median: 77.5
- Buckets: 90-100: 5; 80-89: 13; 70-79: 17; 60-69: 7; below 60: 5
- Distinct scores: 45 across 47 zones
- Most common score: 75.8 (2 zones)
- Zones scoring exactly 85: 0

The previous repeated-85 symptom is removed through evidence differentiation;
no random variation is used.
