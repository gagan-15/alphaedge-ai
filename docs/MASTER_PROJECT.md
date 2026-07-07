# Engineering Rules

1. Architecture before coding.
2. Explain every line of code.
3. Keep modules small and reusable.
4. No duplicate logic.
5. Validation, Logging, and Unit Tests are mandatory.
6. Think scalability before implementation.
7. AI assists decisions but never replaces rule-based logic.
8. Every sprint ends with:
   - Tests passing
   - Documentation updated
   - Git commit
   - Git push

# AlphaEdge AI - Master Project Document

> **Project Status:** Active Development
> **Project Owner:** Gagan Devali
> **Technical Partner:** ChatGPT
> **Current Version:** v0.1.5

---

# Project Metrics

Current Version: v0.1.5

Total Sprints Completed: 17

Python Files: 22

Services: 2
MarketDataService
IndicatorService

Providers: 1

Validators: 2
MarketDataValidator
IndicatorValidator

Indicators: 13

BaseIndicator
SMAIndicator
EMAIndicator
RSIIndicator
MACDIndicator
ATRIndicator
BollingerBandsIndicator
VolumeSMAIndicator
RelativeVolumeIndicator
VolumeConfirmationIndicator
VWAPIndicator
OBVIndicator
CMFIndicator
MFIIndicator
Configuration Modules: 1

Entry Points: 1

Tests: 28 Passing

Git Commits: 12

# Vision

Build the world's most intelligent AI-assisted trading platform.

AlphaEdge AI aims to become a complete Trading Intelligence Platform that helps traders make better decisions using data, technical analysis, AI, market news, risk management, and explainable insights.

The platform will always be:

* Data First
* AI Assisted (Not AI Dependent)
* Modular
* Scalable
* Explainable
* Enterprise Ready

---

# Long-Term Goal

Build a commercial SaaS platform capable of serving thousands of users with features that equal or exceed today's leading trading platforms in usability, intelligence, customization, and decision support.

---

# Overall Project Progress

███████░░░░░░░░░░░░ 24%

Core Platform

████████████░░░░░░ 45%

Commercial Readiness

██░░░░░░░░░░░░░░░░ 9%


# Current Milestone

✓ Market Data Engine
✓ Validation Framework
✓ Indicator Foundation
✓ Momentum Indicators
✓ Volatility Indicators
✓ Volume Indicators (Core)

Next Milestone

Rule Engine


Version History

v0.0.1  Project Foundation
v0.0.2  Market Data Engine
v0.0.3  Validation & Logging
v0.0.4  Indicator Foundation (SMA, EMA)
v0.0.5  RSI Engine
v0.0.6  MACD Engine
v0.0.7  ATR Engine
v0.0.8  Bollinger Bands Engine
v0.0.9  Volume Indicator Engine
v0.1.0  Relative Volume Engine
v0.1.1  Volume Confirmation Engine
v0.1.2  VWAP Indicator Engine
v0.1.3 — OBV Indicator Engine
v0.1.4 — Chaikin Money Flow (CMF) Indicator Engine
v0.1.5 — Money Flow Index (MFI) Indicator Engine

# Sprint History

| Sprint | Status | Description |
|---------|--------|-------------|
| Sprint 1 | ✅ | Project Foundation |
| Sprint 2.1 | ✅ | Market Data Engine |
| Sprint 2.2 | ✅ | Configuration Engine |
| Sprint 2.3 | ✅ | Market Data Validation Engine |
| Sprint 2.4 | ✅ | Logging Engine |
| Sprint 2.5 | ✅  | Indicator Foundation |
| Sprint 2.6 | ✅ | RSI Engine |
| Sprint 2.7 | ✅ | MACD Engine |
| Sprint 2.8 | ✅ | ATR Engine |
| Sprint 2.9 | ✅ | Bollinger Bands Engine |
| Sprint 2.10 | ✅ | Volume Indicator Engine
| Sprint 2.11 | ✅ | Relative Volume Engine |
| Sprint 2.12 | ✅ | Volume Confirmation Engine |
| Sprint 2.13 | ✅ | VWAP Indicator Engine |
| Sprint 2.14 | ✅ | On-Balance Volume (OBV) Indicator Engine |
| Sprint 2.15 | ✅ | Chaikin Money Flow (CMF) Indicator Engine |
| Sprint 2.16 | ✅ | Money Flow Index (MFI) Indicator Engine |

# Current Sprint

Sprint 2.17 – Average Directional Index (ADX) Indicator Engine

# Sprint Completion Checklist

✅ Architecture
✅ Code
✅ Validation
✅ Logging
✅ Tests
✅ Documentation
⏳ Git Commit
⏳ Git Push

## Objective

Build the Average Directional Index (ADX) Indicator Engine.

Objectives

• Learn ADX
• Build ADX Indicator
• Understand Trend Strength
• Add Validation
• Add Logging
• Add Unit Tests

---

# Current Project Status

## Completed

* Development Environment Setup
* Python Virtual Environment
* VS Code Configuration
* Required Python Packages Installed
* Git Initialized
* GitHub Repository Connected
* Initial Git Commit
* Professional Project Folder Structure
* Documentation Structure Created
* Architecture Planned
- Yahoo Finance Provider
- Market Data Service
- Application Entry Point
- Live Market Data Download
- Market Data Cleaning
• Market Data Validation Engine
• Exception Handling
• Data Validation Framework
• Empty Data Validation
• Required Column Validation
• Missing Value Validation
• Duplicate Date Validation
• Sorted Date Validation
• Indicator Foundation
• Base Indicator
• SMA Indicator
• EMA Indicator
• Indicator Service
• Indicator Validator
• Indicator Logging
• Indicator Unit Tests
• RSI Indicator
• RSI Validation
• RSI Logging
• RSI Unit Tests
• Indicator Service RSI Integration
• MACD Indicator
• Signal Line
• Histogram
• MACD Validation
• MACD Logging
• MACD Unit Tests
• Indicator Service MACD Integration
• ATR Indicator
• ATR Validation
• ATR Unit Tests
• Indicator Service ATR Integration
• Bollinger Bands Indicator
• Middle Band
• Upper Band
• Lower Band
• Bollinger Bands Validation
• Bollinger Bands Unit Tests
• Indicator Service Bollinger Integration
• Volume SMA Indicator
• Volume SMA Validation
• Volume SMA Logging
• Volume SMA Unit Tests
• Indicator Service Volume SMA Integration
• Relative Volume Indicator
• Relative Volume Validation
• Relative Volume Logging
• Relative Volume Unit Tests
• Indicator Service Relative Volume Integration
• Volume Confirmation Indicator
• Volume Confirmation Validation
• Volume Confirmation Logging
• Volume Confirmation Unit Tests
• Indicator Service Volume Confirmation Integration
• VWAP Indicator
• VWAP Validation
• VWAP Logging
• VWAP Unit Tests
• Indicator Service VWAP Integration
• OBV Indicator
• OBV Validation
• OBV Logging
• OBV Unit Tests
• Indicator Service OBV Integration

---

# In Progress

* Average Directional Index (ADX) Indicator Engine

---

# Core Runtime Architecture

BaseIndicator
      │
      ├── SMA
      ├── EMA
      ├── RSI
      ├── MACD
      ├── ATR
      ├── Bollinger Bands
      ├── Volume SMA
      ├── Relative Volume
      ├── Volume Confirmation
      ├── VWAP
      ├── OBV
      ├── CMF
      └── MFI  

# Pending Modules

* Rule Engine
* Screener Engine
* Demand & Supply Engine
* Risk Engine
* Backtesting Engine
* News Engine
* Portfolio Engine
* Alert Engine
* AI Engine
* Dashboard
* Deployment

---

# Technology Stack

## Backend

* Python
* FastAPI

## Frontend

* React (Future)

## Database

* PostgreSQL (Planned)

## Charts

* To Be Finalized

## AI

* Planned
* AI will enhance decisions but never replace rule-based analysis.

---

# Engineering Principles

* Data First
* AI Optional
* Plugin Architecture
* Modular Design
* Clean Architecture
* Enterprise Standards
* No Vendor Lock-In
* Explainable AI
* Configuration Driven
* Test Driven (where practical)

---

# Current Folder Structure

AlphaEdgeAI/

├── backend/
│   ├── config/
│   ├── data_providers/
│   ├── services/
│   ├── validators/
│   ├── engines/
│   ├── indicators/
│   ├── strategies/
│   ├── models/
│   ├── utils/
│   └── main.py
│
├── tests/
├── docs/
├── data/
├── logs/
├── scripts/
├── requirements.txt
└── README.md
└── main.py

---

# GitHub Repository

https://github.com/gagan-15/alphaedge-ai

---

# Latest Commit

Sprint 2.16: Build Money Flow Index (MFI) Indicator Engine

---

# Immediate Next Task

Average Directional Index (ADX) Indicator Engine

---

# Development Workflow

For every feature:

1. Requirement
2. Architecture
3. Implementation
4. Explain Every Line
5. Validation
6. Logging
7. IndicatorService Integration
8. Unit Tests
9. Run pytest
10. Update MASTER_PROJECT.md
11. Git Commit
12. Git Push

---

# Learning Objective

This project is intended to teach:

* Python
* Object-Oriented Programming
* FastAPI
* Software Architecture
* Design Patterns
* AI Engineering
* Database Design
* React
* Cloud Deployment
* Enterprise Software Development

Every line of code will be explained before moving to the next step.

---

# Important Agreement

This project will be developed one sprint at a time.

No unnecessary architecture changes.

No unnecessary folders.

Every module must be:

* Modular
* Reusable
* Scalable
* Testable
* Easy to extend

Future additions (new indicators, AI models, timeframes, markets, strategies, news providers, brokers, etc.) should require minimal changes to existing code.

---

# Resume Instructions

Continue AlphaEdge AI.

Current Version: v0.1.5

Sprint 2.17 – Average Directional Index (ADX) Indicator Engine

Follow MASTER_PROJECT.md.

This document is the single source of truth.

---

# Project Motto

> Every line of code should make AlphaEdge AI easier to extend, easier to understand, and easier to trust.

# Upcoming Sprint

Sprint 2.17 – Average Directional Index (ADX) Indicator Engine

Objectives

• Learn ADX
• Build ADX Indicator
• Understand Trend Strength
• Add Validation
• Add Logging
• Add Unit Tests



# Future Features

□ Multi-timeframe Screener
□ AI Confidence Score
□ Institutional Order Blocks
□ Heatmap
□ Sector Rotation
□ Portfolio Tracker
□ Telegram Alerts
□ Mobile App
□ Options Chain Analysis
□ News Sentiment
□ Voice Assistant
□ Web Dashboard
□ Broker Integration
□ Portfolio Analytics
□ Multi Provider Support

# How to add a new indicator

1. Create indicator file
2. Inherit BaseIndicator
3. Implement calculate()
4. Add validation
5. Add logging
6. Integrate with IndicatorService
7. Create unit test
8. Run pytest
9. Update MASTER_PROJECT.md
10. Git Commit
11. Git Push
12. Sprint Closed

# Architecture Decisions

AD-001
AI is an enhancement, not the core decision maker.

AD-002
Every external API must have its own Provider.

AD-003
No business logic inside main.py.

AD-004
No hardcoded values. Use configuration.

AD-005
Each engine has a single responsibility.

AD-006
Every feature must be testable.

AD-007

All downloaded market data must pass through the Validation Engine before being used anywhere in AlphaEdge AI.

AD-008

Every indicator must inherit from BaseIndicator.

AD-009

Every indicator must include validation, logging and unit tests before being considered complete.

AD-010

MACDIndicator reuses EMAIndicator instead of duplicating EMA calculation logic.

Reason:
Avoid duplicate code and maintain a single source of truth for EMA calculations.

AD-011

Indicators should reuse existing indicators whenever doing so avoids duplicate logic and preserves a single source of truth.

AD-012

VWAP is implemented as an independent indicator because its calculation is based directly on price and volume data and does not reuse other indicators.

AD-013

OBV is implemented as a stateful indicator because each OBV value depends on the previous OBV value.


# Development Rules

DR-001 – Completed Sprints Are Read-Only

Rule:

Once a sprint is marked ✅ Complete, its implementation is considered frozen.

It will only be modified if:

A verified bug is found.
A security issue exists.
The project owner (Gagan) approves the change.

Reason:

Keeps completed work stable and prevents accidental regressions.

DR-002 – Verify Existing Code Before Reuse ⭐

Rule:

Before reusing any module from a previous sprint, inspect its actual implementation.

Do not assume:

constructor parameters
method names
return types
input parameters
class design

Reason:

Today's EMAIndicator() issue happened because I assumed its interface instead of verifying it.

DR-003 – Existing Code Is the Source of Truth

Rule:

When continuing AlphaEdge AI, the existing implementation always takes precedence over assumptions or generic examples.

New code must adapt to the existing architecture.

Reason:

Keeps the project internally consistent.

DR-004 – No Breaking Changes Without Approval

Rule:

If a previous module needs to change:

Explain why.
Explain the impact.
Explain the benefits.
Wait for approval.

Only then make the change.

DR-005 – Dependency Verification Checklist

Before coding any new module, verify:

Required classes
Public methods
Constructor signatures
Return types
Existing tests

Only then begin implementation.

DR-006 – Tests Before Architecture Changes

If a design assumption is uncertain:

Check the implementation.
Write/update tests.
Then implement.

Never redesign based on assumptions.

DR-007 – Preserve Sprint Independence

Each sprint should integrate with previous sprints without requiring previous completed code to change, whenever reasonably possible.

This keeps every completed sprint self-contained and reliable.


DR-008 – ChatGPT Verification Rule

Rule:

Before generating code that depends on a previous sprint, ChatGPT must verify the dependent module if it has not been shown in the current chat.

If verification is not possible, ChatGPT must ask for the relevant file instead of assuming its implementation.

Reason:

Prevents mistakes like today's EMAIndicator constructor mismatch.

DR-009 – Test Before Closing Sprint

A sprint cannot be marked complete until:

• All unit tests pass.
• Previous sprint tests continue to pass.
• MASTER_PROJECT.md is updated.
• Git commit is created.
• Git push is completed.

DR-010 – Simplicity First

Code should always be written in the simplest
possible way while maintaining enterprise-grade
performance, scalability and maintainability.

Avoid unnecessary complexity, clever tricks,
over-engineering and premature optimization.

The goal is that a new developer joining the
project should be able to understand the code
with minimal effort.

Prefer readable code over clever code.

Only introduce advanced techniques when there is
a measurable engineering benefit.