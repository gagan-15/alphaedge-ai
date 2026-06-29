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
> **Current Version:** v0.0.4

---

# Project Metrics

Current Version: v0.0.4

Total Sprints Completed: 6

Python Files: 12

Services: 2
MarketDataService
IndicatorService

Providers: 1

Validators: 2
MarketDataValidator
IndicatorValidator

Indicators: 3
BaseIndicator
SMAIndicator
EMAIndicator

Configuration Modules: 1

Entry Points: 1

Tests: 2

Git Commits: 5

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

██████░░░░░░░░░░░░ 18%

Core Platform

██████████░░░░░░░░ 35%

Commercial Readiness

█░░░░░░░░░░░░░░░░░ 5%


Version History

v0.0.1  Project Foundation
v0.0.2  Market Data Engine
v0.0.3  Validation & Logging
v0.0.4  Indicator Foundation (SMA, EMA)

# Sprint History

| Sprint | Status | Description |
|---------|--------|-------------|
| Sprint 1 | ✅ | Project Foundation |
| Sprint 2.1 | ✅ | Market Data Engine |
| Sprint 2.2 | ✅ | Configuration Engine |
| Sprint 2.3 | ✅ | Market Data Validation Engine |
| Sprint 2.4 | ✅ | Logging Engine |
| Sprint 2.5 | ✅  | Indicator Foundation |
| Sprint 2.6 | 🔄  | RSI Engine|

# Current Sprint

Current Sprint: Sprint 2.6 – RSI Engine.

## Objective

Build the Relative Strength Index (RSI) Engine.

Objectives

• Build RSI Indicator

• Learn Wilder's RSI Formula

• Integrate RSI with Indicator Service

• Add Validation

• Add Logging

• Add Unit Tests

• Prepare for Rule Engine integration
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

---

# In Progress

* RSI Engine

---

# Current Architecture

   Application
      │
      ▼
main.py
      │
      ├───────────────┐
      ▼               ▼
MarketDataService   IndicatorService
      │               │
      ▼               ├──────────────┐
MarketDataValidator   ▼              ▼
      │          SMAIndicator   EMAIndicator
      ▼               │              │
YahooProvider         └──────┬───────┘
      │                      ▼
      ▼              IndicatorValidator
Yahoo Finance API

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

backend/

├── config/

├── data_providers/

├── services/

├── validators/

├── engines/

├── indicators/

├── strategies/

├── models/

├── utils/

└── main.py

---

# GitHub Repository

https://github.com/gagan-15/alphaedge-ai

---

# Latest Commit

Sprint 2.5: Build Indicator Foundation with SMA, EMA, validation, logging and tests

---

# Immediate Next Task

RSI Engine

---

# Development Workflow

For every feature:

1. Requirement
2. Architecture
3. Implementation
4. Explanation (every line)
5. Testing
6. Git Commit
7. GitHub Push
8. Documentation Update

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

Whenever continuing this project in a new chat, start with:

Continue AlphaEdge AI.
Current Version: v0.0.4

Current Sprint: Sprint 2.4 – Logging Engine.

Follow MASTER_PROJECT.md.

This document is the single source of truth for the project.

---

# Project Motto

> Every line of code should make AlphaEdge AI easier to extend, easier to understand, and easier to trust.

# Upcoming Sprint

Sprint 2.7 – MACD Engine

Objectives

• Build MACD Indicator

• Fast EMA

• Slow EMA

• Signal Line

• Histogram

• Logging

• Validation

• Unit Tests



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