# AlphaEdge AI - Developer Guide

> **Purpose**
>
> This document defines the engineering standards, development workflow, coding conventions, and architectural rules used throughout AlphaEdge AI.
>
> Every new feature, sprint, bug fix, and enhancement must follow this guide.

---

# 1. Development Philosophy

AlphaEdge AI is designed as an enterprise-grade AI-assisted trading platform.

Every implementation must be:

- Modular
- Reusable
- Scalable
- Testable
- Easy to Understand
- Enterprise Ready

The project always prefers:

- Simplicity over cleverness
- Readability over shortcuts
- Architecture over quick fixes
- Rule-Based Decisions over AI guesses

---

# 2. Engineering Rules

Every sprint follows these rules.

1. Architecture before coding.

2. Explain the design before implementation.

3. Keep modules small and reusable.

4. No duplicate logic.

5. Validation, Logging and Unit Tests are mandatory.

6. Think scalability before implementation.

7. AI assists decisions but never replaces rule-based logic.

8. Every sprint ends with:

- Tests Passing
- Documentation Updated
- Git Commit
- Git Push

---

# 3. Standard Development Workflow

Every new sprint follows this sequence.

1. Revision Question
2. Brief Concept Explanation
3. Architecture Planning
4. Complete File Implementation
5. Code Review
6. Validation
7. Logging
8. Integration
9. Unit Tests
10. Run Pytest
11. Update Documentation
12. Git Commit
13. Git Push

---

# 4. Coding Standards

## Naming

Classes

Example

MarketDataService

IndicatorValidator

EMAIndicator

Variables

Use meaningful names.

Example

market_data

close_prices

volume_average

Never use names like

x

temp

abc

except inside very small loops.

---

## Functions

Every function should do one job.

Bad

calculateEverything()

Good

calculate_rsi()

calculate_ema()

validate_data()

---

## Comments

Use comments to explain

WHY

instead of

WHAT

Bad

# Increment i

i += 1

Good

# Skip invalid candles

---

## Docstrings

Every public class and function must have:

Purpose

Arguments

Returns

Raises (if applicable)

---

# 5. Validation Rules

Every module that accepts external input must validate it.

Validation includes

- Empty data
- Required columns
- Invalid parameters
- Minimum rows
- Data type validation

Never trust external input.

---

# 6. Logging Rules

Every major module must log

Start

Completion

Errors

Do not use print() for production logic.

Always use the centralized logger.

---

# 7. Unit Testing Rules

Every sprint must include tests.

Typical tests include

- Successful calculation

- Invalid input

- Missing columns

- Wrong parameters

- Service integration

A sprint is not complete until

pytest passes.

---

# 8. Indicator Development Checklist

Every indicator must follow:

□ Create Indicator

□ Inherit BaseIndicator

□ Implement calculate()

□ Add Validation

□ Add Logging

□ Integrate with IndicatorService

□ Create Unit Tests

□ Run Pytest

□ Update Documentation

□ Git Commit

□ Git Push

---

# 9. Architecture Rules

Follow Single Responsibility Principle.

Never duplicate business logic.

Reuse existing modules whenever possible.

Keep completed sprints read-only.

Prefer composition over duplication.

Configuration is preferred over hardcoding.

---

# 10. Development Rules

## DR-001

Completed sprints are read-only unless a verified bug is found.

---

## DR-002

Verify existing code before reuse.

Never assume

- Constructor parameters
- Method names
- Return values

Always inspect the implementation.

---

## DR-003

Existing implementation is the source of truth.

New code adapts to existing architecture.

---

## DR-004

Breaking changes require approval.

Explain

- Why
- Benefits
- Impact

before changing completed work.

---

## DR-005

Verify dependencies before coding.

Check

- Classes
- Constructors
- Methods
- Tests

---

## DR-006

Write tests before architecture changes.

---

## DR-007

Preserve sprint independence.

---

## DR-008

If dependency cannot be verified,

request the file.

Never guess.

---

## DR-009

A sprint closes only after

- Tests pass
- Documentation updated
- Git Commit
- Git Push

---

## DR-010

Keep solutions simple.

Avoid unnecessary abstraction.

Avoid premature optimization.

Readable code always wins.

---

# 11. Documentation Rules

MASTER_PROJECT.md

Current project status only.

DeveloperGuide.md

Development standards.

Architecture.md

Architecture and design decisions.

SprintHistory.md

Completed sprint history.

Roadmap.md

Future work.

---

# 12. AI Collaboration Rules

ChatGPT assists development.

ChatGPT does not invent missing project details.

When previous implementation is required,

verify it first.

Never modify completed sprints without approval.

Always optimize for maintainability.

---

# Developer Motto

> Build software that another engineer can understand in one day and confidently extend for years.