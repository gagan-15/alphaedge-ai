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

1. Revision
2. Concept Explanation
3. Architecture
4. Implementation
5. Code Review
6. Validation
7. Integration
8. Unit Tests
9. Run Pytest
10. UI Review (Frontend Only)
11. Documentation
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

# React Development Standards

Every React component must follow these rules.

## Component Design

- One component, one responsibility.
- Keep components reusable.
- Prefer composition over duplication.
- Keep pages responsible for orchestration only.

## API Access

React components never call backend services directly.

Pages
↓

API Layer
↓

REST API

## Business Logic

Business logic belongs only in the backend.

React components should only:

- Display data
- Collect user input
- Trigger API requests
- Render UI

## Layout

The application shell follows:

App
↓

AppLayout
↓

Header + Sidebar
↓

Pages
↓

Components

This layout must remain reusable for future modules.

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


# 10. Sprint Completion Workflow

Before a sprint is considered complete, verify:

□ Code Review Completed

□ All Dependencies Verified

□ Architecture Matches Documentation

□ Unit Tests Passing

□ Frontend Tested (if applicable)

□ Documentation Synchronized

□ Git Commit

□ Git Push

Completed sprints become read-only after this checklist is finished.

_ _ _

# 11. Development Rules

## DR-001

Completed sprints are read-only.

Modifications are allowed only when:

- A verified bug exists.
- A documentation correction is required.
- A security issue must be fixed.

New features must always be implemented in new sprints.

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

Verify existing implementation before architecture changes.

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

## DR-011 – Future Compatibility

Every new module must be designed so that future features can be added with minimal changes to existing code. Prefer extension over modification whenever practical.

# 12. Documentation Rules

MASTER_PROJECT.md
Current Project Dashboard

DeveloperGuide.md
Development Standards

Architecture.md
Architecture Decisions

SprintHistory.md
Historical Record

Roadmap.md
Future Development

---

## DR-012 – Documentation Synchronization

Before closing a sprint, ensure the following documents are synchronized:

- MASTER_PROJECT.md
- SprintHistory.md
- Architecture.md
- Roadmap.md (if affected)

Project documentation must accurately reflect the implemented architecture before a sprint is considered complete.

---

## DR-013

Never redesign architecture after implementation begins.

Freeze the architecture before creating implementation files.

Architecture changes are allowed only before coding starts or when fixing a verified architectural defect.

---

## DR-014 – Test Synchronization

Unit tests must target the final approved public interface of the sprint.

If an implementation changes before sprint closure:

- Review all affected tests.
- Remove obsolete test assumptions.
- Verify tests against the final source code.
- Run the complete regression suite.

Tests must validate expected behaviour rather than internal implementation details whenever practical.

---

## DR-015 – Configuration Integrity

Every configuration field introduced by a sprint must be:

- Validated
- Used by production logic
- Covered by unit tests
- Documented

Unused or placeholder configuration fields are not allowed in completed sprints.

---

## DR-016 – Backend Layering

Every backend request must follow:

API
↓

Service
↓

Engine
↓

Models
↓

Validators
↓

Config

Business logic belongs only inside Services and Engines.

---

## DR-017 – Frontend Architecture

React components must remain presentation-only.

Pages
↓

Components
↓

API Layer
↓

REST API

No business logic inside React components.

---

## DR-018– Frontend Component Hierarchy

Frontend components must follow:

App
↓

AppLayout
↓

Pages
↓

Reusable Components

Reusable components must never contain page-specific business logic.

Pages orchestrate.

Components render.

API Layer communicates with the backend.

---

## DR-019– Verify Existing Implementation

Before implementing any sprint:

- Inspect existing files.
- Never assume constructors.
- Never assume APIs.
- Never assume folder structures.

Existing implementation is the source of truth.

---

# 13. AI Collaboration Rules

ChatGPT assists development.

ChatGPT does not invent missing project details.

When previous implementation is required,

verify it first.

Never modify completed sprints without approval.

Always optimize for maintainability.

---

# Developer Motto

> Build software that another engineer can understand in one day and confidently extend for years.

# Architecture Planning Rule

Before implementing any sprint, AlphaEdge AI must be planned with a minimum 5-sprint horizon.

For every sprint:

- Identify dependencies from previous sprints.
- Identify dependencies for the next five planned sprints.
- Avoid introducing designs that require rewriting completed modules.
- Treat completed sprint interfaces as stable contracts unless a verified bug requires a change.
- Architecture review is mandatory before implementation begins.

Goal:
Build a forward-compatible, extensible platform with minimal rework.


## Rule #14 — Legal First

Before implementing any feature:

1. Is it legal in India?
2. Does it require SEBI registration or another license?
3. Does it execute trades?
4. Does it manage money?
5. Does it provide regulated financial services?

If there is uncertainty, stop and review before implementation.