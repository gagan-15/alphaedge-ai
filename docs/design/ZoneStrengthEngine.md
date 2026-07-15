# Zone Strength Engine

## Purpose

Evaluate how strongly price departed from a detected Demand or Supply Zone.

---

# Responsibilities

The Zone Strength Engine is responsible for:

- Measuring departure distance.
- Measuring departure speed.
- Measuring departure candle quality.
- Measuring volume confirmation when available.
- Producing a strength result.

The engine is NOT responsible for:

- Zone Detection
- Zone Freshness
- BOS Detection
- CHoCH Detection
- Multi-Timeframe Analysis
- Zone Scoring
- Trade Decision

---

# Input

- Detected Zone
- Market data surrounding and following the zone
- Departure information when available

---

# Output

- Strength Status
- Departure Distance
- Departure Candle Count
- Departure Speed
- Volume Confirmation
- Gap Presence

---

# Strength Factors

## Departure Distance

How far price moved away from the zone relative to the zone height.

## Departure Speed

How quickly price moved away from the zone.

## Candle Quality

Evaluate:

- Candle body size
- Wick size
- Candle direction
- Consecutive departure candles

## Volume Confirmation

Determine whether departure volume is stronger than normal volume.

## Gap Presence

Determine whether price created an imbalance or gap while leaving the zone.

---

# Strength Status

Possible statuses:

- Weak
- Moderate
- Strong
- Very Strong

---

# Assumptions

- The zone has already been detected and validated.
- Market data has already passed the Validation Engine.
- Strength is evaluated independently from freshness.
- No final zone score is calculated in this sprint.

---

# Out of Scope

- Freshness
- BOS
- CHoCH
- Multi-Timeframe Confluence
- Zone Ranking
- Trade Score
- AI Explanation

---

# Validation Rules

The engine must validate:

- Zone is not null.
- Zone boundaries are valid.
- Market data is not empty.
- Zone creation index is valid.
- Required OHLC columns exist.
- Volume is optional unless volume analysis is enabled.

---

# Architecture Decisions

1. Zone Strength is evaluated independently from freshness.
2. The engine measures raw strength evidence only.
3. Final zone scoring belongs to the Zone Scoring Engine.
4. Volume analysis is optional when volume data is unavailable.
5. All thresholds must come from configuration.
6. The engine must support both Demand and Supply zones.
7. The engine must remain timeframe-independent.

---

# Architecture Status

Frozen