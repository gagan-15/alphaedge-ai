# Zone Freshness Engine

## Purpose

Determine how fresh a detected Demand/Supply Zone remains after it has been created.

The engine evaluates whether price has revisited the zone and whether the zone is still considered valid.

---

# Responsibilities

The Zone Freshness Engine is responsible for:

- Counting zone retests.
- Measuring zone penetration.
- Determining whether a zone has been broken.
- Producing a freshness result.

The engine is NOT responsible for:

- Zone Detection
- Zone Strength
- BOS Detection
- CHoCH Detection
- Zone Scoring
- Trade Decision

---

# Input

- Detected Zone
- Market Data after the zone was created

---

# Output

- Freshness Status
- Touch Count
- Penetration Percentage
- Broken Status

---

# Out of Scope

The following are intentionally excluded from Sprint 2.27:

- Freshness Score
- Trade Score
- AI Explanation
- Zone Ranking

---

# Freshness Rules

## Rule 1

If price has never revisited the zone:

Status = Fresh

---

## Rule 2

If price revisits the zone but does not break it:

Status = Tested

---

## Rule 3

If price deeply penetrates the zone but remains valid:

Status = Weak

---

## Rule 4

If price completely breaks the zone:

Status = Broken


# Assumptions

- The input zone has already been validated by the Zone Detection Engine.
- Market data is assumed to be valid.
- The engine analyzes only price action after the zone is created.


# Open Design Questions

3. Does a candle body entering the zone count as a touch?

4. How is penetration percentage calculated?

5. When is a zone considered broken?

6. Should every touch have equal weight?

7. Should a rejection after a touch influence freshness?

The following rules must be finalized before implementation:

# Touch Definition (Draft)

A touch occurs when price enters the zone after the zone has been created.

The following scenarios must be evaluated before implementation:

# Wick Touch

Decision: Pending

# Body Touch

Decision: Pending

# Partial Penetration

Decision: Pending

# Full Penetration

Decision: Pending

# Multiple touches within the same move

Decision: Pending


Question:

Should a candle wick entering a zone be considered a valid touch?

Options:

- Yes
- No
- Depends on penetration

Reason:

To be finalized before implementation.


## Penetration Percentage

Decision: Pending

Purpose:

Measure how deeply price entered the zone during each retest.

Questions:

- Where does penetration start?
- Where does penetration end?
- Should penetration be measured using the wick or candle body?
- Should the maximum penetration or closing penetration be used?
- Should multiple penetrations be stored?

---

# Validation Rules

The Zone Freshness Engine must validate:

- Zone is valid.
- Zone boundaries are valid.
- Market data is not empty.
- Market data exists after zone creation.

---

# Error Handling

The engine shall return appropriate validation errors when:

- Zone is invalid.
- Zone boundaries are invalid.
- Market data is missing.
- Market data contains insufficient candles.

---