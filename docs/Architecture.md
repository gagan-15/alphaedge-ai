# AlphaEdge AI - Architecture

> **Purpose**
>
> This document defines the overall software architecture, design principles,
> architectural decisions, and technology choices used throughout AlphaEdge AI.
>
> This document changes only when the architecture itself changes.

---

# 1. Vision

AlphaEdge AI is an enterprise-grade AI-assisted Trading Intelligence Platform.

Its goal is to help traders make high-quality, explainable, and repeatable trading decisions using:

- Technical Indicators
- Rule Engine
- Demand & Supply Analysis
- Multi-Timeframe Analysis
- Risk Management
- AI-assisted Insights
- Explainable Decision Making

AI enhances decision making.

AI never replaces rule-based analysis.

---

# 2. Long-Term Goal

Build a commercial SaaS platform capable of serving thousands of users.

Future capabilities include:

- Stock Screening
- Portfolio Management
- Backtesting
- Strategy Builder
- AI Analysis
- Broker Integration
- Alerts
- Mobile Application
- Multi-user Cloud Platform

---

# 3. High-Level Architecture

Market Data
      │
      ▼
Validation Engine
      │
      ▼
Indicator Engine
      │
      ▼
Rule Engine
      │
      ▼
Demand & Supply Engine
      │
      ▼
Trading Signal

---

Demand & Supply Engine

Market Data
      │
      ▼
Base Detector
      │
      ▼
Departure Detector
      │
      ▼
Pattern Detector
      │
      ▼
Zone Detection Engine
      │
      ▼
Zone

# 4. Core Modules

Current

- Market Data Engine
- Validation Engine
- Indicator Engine
- Rule Engine
- Demand & Supply Engine

Upcoming

- Screener Engine
- Risk Management Engine
- AI Explanation Engine
- Backtesting Engine
- Portfolio Engine
- Alert Engine
---

# 5. Folder Structure

```
AlphaEdgeAI/

backend/
    config/
    data_providers/
    services/
    validators/
    indicators/
    engines/
    strategies/
    models/
    utils/
    api/
    database/

tests/

docs/

scripts/

logs/

data/
```

---

# 6. Technology Stack

Backend

- Python
- FastAPI

Frontend

- React

Database

- PostgreSQL

Testing

- pytest

Version Control

- Git

---

# 7. Software Design Principles

AlphaEdge AI follows:

- Clean Architecture
- SOLID Principles
- Single Responsibility Principle
- Modular Design
- Composition over Duplication
- Configuration Driven Development
- Testable Design
- Enterprise Coding Standards

---

# 8. Architecture Decisions

## AD-001

AI assists decisions.

AI never replaces rule-based logic.

---

## AD-002

Every external data source must have its own Provider.

---

## AD-003

No business logic inside main.py.

---

## AD-004

Configuration must replace hardcoded values whenever practical.

---

## AD-005

Each engine has one responsibility.

---

## AD-006

Every feature must be testable.

---

## AD-007

All downloaded market data passes through Validation Engine.

---

## AD-008

Every indicator inherits BaseIndicator.

---

## AD-009

Every indicator includes:

- Validation
- Logging
- Unit Tests

before completion.

---

## AD-010

Reuse existing modules instead of duplicating logic.

Example:

MACD reuses EMA calculations.

---

## AD-011

Prefer composition over inheritance whenever possible.

---

## AD-012

Indicators should remain independent.

The Rule Engine combines them.

---

## AD-013

Stateful indicators (for example OBV and Parabolic SAR) manage previous values internally.

---

## AD-014

The Rule Engine combines outputs from independent indicators to produce deterministic Buy, Sell and Hold decisions.

Indicators calculate.

Rule Engine interprets.

## AD-015

The Multi Rule Engine combines one or more Rule objects into a single consolidated Rule before the Rule Evaluator produces the final TradingSignal.

This separation keeps rule aggregation independent from rule evaluation and allows new trading rules to be added without modifying the evaluation workflow.

## AD-016

The Demand & Supply Engine is composed of independent detectors.

BaseDetector

↓

DepartureDetector

↓

PatternDetector

↓

ZoneDetectionEngine

Each detector has a single responsibility.

The ZoneDetectionEngine orchestrates the workflow without duplicating detection logic.

---

AD-017 – Role-Based Multi-Timeframe Architecture

AlphaEdge AI separates analysis into three independent roles:

Location – Finds where high-quality trading opportunities exist.
Trend – Validates whether market structure supports trading at that location.
Execution – Determines the precise entry timing.

The timeframes assigned to these roles are configurable. All future engines (Freshness, Strength, BOS, CHoCH, Scoring, Ranking, Screener, Alerts, and AI Explanation) operate on these roles rather than hardcoded timeframes.

---



# 9. Coding Philosophy

The architecture always prefers:

Simple

↓

Readable

↓

Reusable

↓

Scalable

↓

Optimized

Never optimize before it is necessary.

---

# 10. Documentation Structure

MASTER_PROJECT.md

Current project status.

DeveloperGuide.md

Development standards.

Architecture.md

Software architecture.

SprintHistory.md

Project history.

Roadmap.md

Future roadmap.

API.md

API documentation.

DatabaseDesign.md

Database design.

ProjectVision.md

Business vision.

---

# Architecture Motto

> Good architecture makes future features easier to build, not harder.