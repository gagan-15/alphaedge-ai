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
Market Structure Engine
        │
        ▼
Zone Merge Engine
        │
        ▼
Zone Scoring Engine
        │
        ▼
Zone Ranking Engine
        │
        ▼
Trade Setup Engine
        │
        ▼
Entry Confirmation Engine
        │
        ▼
Risk Management Engine
        │
        ▼
Screener Engine
        │
        ▼
Market Scanner Engine
        │
        ▼
Backtesting Engine
        │
        ▼
AI Explanation Engine
        │
        ▼
Portfolio Engine
        │
        ▼
Alert Engine
        │
        ▼
Dashboard Engine
        │
        ▼
Dashboard Service
        │
        ▼
FastAPI
        │
        ▼
REST API
    ↓
React API Layer
    ↓
App
    ↓
AppLayout
    ↓
Header + Sidebar
    ↓
Dashboard Page
    ↓
Dashboard Components
    ↓
TradingView Widget (Temporary)

---

Demand & Supply and Market Structure Engine

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
Zone Freshness Engine
      │
      ▼
Zone Strength Engine
      │
      ▼
Swing Detector
      │
      ▼
Break of Structure Engine
      │
      ▼
Validated Market Structure

# 4. Core Modules

Current

- Market Data Engine
- Validation Engine
- Indicator Engine
- Rule Engine
- Demand & Supply Engine
- Zone Detection Engine
- Zone Freshness Engine
- Zone Strength Engine
- Swing Detector
- Break of Structure Engine
- Risk Management Engine
- Market Scanner Engine
- Backtesting Engine
- BacktestResult
- AI Explanation Engine
- AIExplanationResult
- AIExplanationDecision
- Portfolio Engine
- PortfolioResult
- React Application Shell
- Header
- Sidebar
- Dashboard Layout
- Material UI Theme

Upcoming

Alert Engine

Dashboard

Broker Integration

Watchlist Engine

Strategy Repository

---

# 5. Folder Structure

```
AlphaEdgeAI/

backend/
    api/
    config/
    services/
    engines/
    models/
    validators/
    providers/
    indicators/
    utils/

frontend/
    src/
        api/
        assets/
        components/
            dashboard/
            header/
            sidebar/
        layouts/
        pages/
        theme/
        types/
        hooks/
```

---

# 6. Technology Stack

Backend

- Python
- FastAPI

Frontend

- React 19
- TypeScript
- Material UI
- Axios
- Vite
- TradingView Widget (Temporary)

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

State management is separated from analytics.

Core engines maintain domain state.

Analytics engines derive metrics from that state.

This separation keeps responsibilities clear,
reduces coupling, and allows analytics to evolve
without changing the underlying domain models.

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

## AD-017 – Role-Based Multi-Timeframe Architecture

AlphaEdge AI separates analysis into three independent roles:

Location – Finds where high-quality trading opportunities exist.
Trend – Validates whether market structure supports trading at that location.
Execution – Determines the precise entry timing.

The timeframes assigned to these roles are configurable. All future engines (Freshness, Strength, BOS, CHoCH, Scoring, Ranking, Screener, Alerts, and AI Explanation) operate on these roles rather than hardcoded timeframes.

---

## AD-018

Zone quality evaluation is performed as independent stages.

Zone Detection Engine
        ↓
Zone Freshness Engine
        ↓
Zone Strength Engine

Each engine has a single responsibility.

BOS builds upon confirmed swing structure, while future engines such as CHoCH, Zone Scoring, and Zone Ranking will consume existing zone-quality and market-structure outputs without duplicating calculations.

---

## AD-019 – Break of Structure Architecture

Break of Structure analysis is implemented using independent and reusable components.

Market Data
        ↓
Swing Detector
        ↓
BOS Detector
        ↓
BOS Engine
        ↓
BOS Result

The Swing Detector identifies confirmed swing highs and swing lows.

The BOS Detector evaluates whether a confirmed swing level has been broken.

The BOS Engine orchestrates validation, swing detection, BOS detection and result construction.

Each component has one responsibility.

The Swing Detector and BOS results may be reused by future engines such as:

- Change of Character
- Market Structure Classification
- Multi-Timeframe Structure
- Zone Scoring
- Zone Ranking
- Trade Setup Engine

BOS detection remains rule-based, configurable and explainable.

---

## AD-020 – Configurable Structure Confirmation

Break of Structure confirmation is configuration-driven.

Supported confirmation sources:

- Close
- High
- Low

Supported break buffers:

- Percentage
- Points

The default confirmation source is Close.

Wick-based confirmation is available only when explicitly configured.

---

## AD-021 – Risk Management Architecture

Risk Management is implemented as an independent engine that
operates only after Entry Confirmation.

Pipeline

Entry Confirmation
        ↓
Risk Management Engine
        ↓
Approved Trade

The engine is responsible for:

- Position sizing
- Capital allocation
- Risk/reward validation
- Trade approval

Future engines such as Screener, Backtesting, Portfolio,
Broker Integration and Alerts consume the approved trade
without duplicating risk calculations.

This keeps risk evaluation centralized, reusable and
consistent across the platform.

---

## AD-022 – Screener Architecture

The Screener Engine is responsible for transforming approved
trading opportunities into a collection of screened results.

Pipeline

Approved Trade
        ↓
Screened Opportunity
        ↓
Screener Engine
        ↓
Screener Result

Responsibilities

- Filter rejected opportunities
- Respect maximum configured results
- Return a collection of screened opportunities

The Screener Engine does not:

- Download market data
- Calculate indicators
- Evaluate trading rules
- Perform risk management

Those responsibilities remain in their dedicated engines.

This keeps the Screener Engine focused on orchestration and
screening while maintaining a stable interface for future
consumers such as the Dashboard, Alerts, Portfolio, Mobile App,
Desktop App, and AI Explanation Engine.

---

## AD-023 – Market Scanner Architecture

The Market Scanner Engine coordinates the scanning of a stock
universe using the existing AlphaEdge AI trading pipeline.

Pipeline

Stock Universe
        ↓
Market Scanner Engine
        ↓
Trading Pipeline
        ↓
Screener Engine
        ↓
MarketScannerResult

Responsibilities

- Coordinate symbol scanning
- Enforce maximum symbol limits
- Produce standardized scanning results
- Integrate with the Screener Engine

The Market Scanner Engine does not:

- Download market data
- Calculate indicators
- Evaluate trading rules
- Perform risk management
- Rank opportunities

These responsibilities remain in their dedicated engines and
services.

This architecture keeps the Market Scanner focused on orchestration
while allowing future support for multiple data providers, exchanges,
parallel execution, caching, and scheduling without changing the
public interface.

---
## AD-024 – Backtesting Architecture

The Backtesting Engine evaluates historical trading outcomes
and produces standardized performance metrics.

Pipeline

Trade Results
      ↓
Backtesting Engine
      ↓
Backtest Result

Responsibilities

- Evaluate completed trades
- Calculate total trades
- Calculate winning trades
- Calculate losing trades
- Calculate win rate
- Produce a standardized BacktestResult

The Backtesting Engine does not:

- Generate trade signals
- Download market data
- Evaluate indicators
- Execute orders
- Perform portfolio management

These responsibilities remain within their dedicated engines.

Future metrics such as Profit Factor, Maximum Drawdown,
Sharpe Ratio, Sortino Ratio, CAGR, Equity Curve,
Expectancy, and Monte Carlo simulation will extend
BacktestResult without changing the public engine interface.

---

## AD-025 – AI Explanation Architecture

The AI Explanation Engine converts structured trading
evidence into deterministic, reusable explanations.

Pipeline

Backtest Result
        ↓
AI Explanation Engine
        ↓
AIExplanationResult

Responsibilities

- Explain BUY, SELL, HOLD and WAIT decisions
- Assemble structured explanation reasons
- Apply explanation configuration
- Produce reusable AIExplanationResult

The AI Explanation Engine does not:

- Execute AI models
- Call LLM providers
- Generate conversational responses
- Perform market analysis
- Make trading decisions

These responsibilities remain outside the engine.

Future Generative AI integrations will consume
AIExplanationResult without changing the public
engine interface.

---

## AD-026 – Portfolio Architecture

The Portfolio Engine maintains the current portfolio
state for AlphaEdge AI.

Pipeline

AIExplanationResult
        ↓
Portfolio Engine
        ↓
PortfolioResult

Responsibilities

- Track total positions
- Track invested capital
- Track available capital
- Track total capital
- Produce PortfolioResult

The Portfolio Engine does not:

- Calculate profit and loss
- Calculate portfolio exposure
- Calculate drawdown
- Calculate Sharpe Ratio
- Execute trades
- Synchronize broker accounts

These responsibilities belong to future
Portfolio Analytics and Broker Integration
modules.

The Portfolio Engine is intentionally designed
as a state management engine rather than an
analytics engine.

---

## AD-027 – Alert Architecture

AlertEngine creates standardized alerts.

It never sends emails,
Telegram,
WhatsApp,
Push notifications.

Delivery belongs to adapters.

---

## AD-028 – Frontend Architecture

The React frontend follows a presentation-only architecture.

Pages
      ↓
Components
      ↓
API Layer
      ↓
REST API

Business logic is never implemented inside React components.

Trading calculations, validation, portfolio logic, scanner logic, AI explanation, and market analysis remain exclusively within backend services and engines.

This separation allows independent evolution of the user interface while preserving a stable backend architecture.

---

## AD-029 – Backend Layering

Backend requests always follow:

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

Each layer has one responsibility.

No layer may bypass another without explicit architectural approval.

---

## AD-030 – React Application Shell

The frontend follows a reusable application shell architecture.

Pipeline

App
    ↓
AppLayout
    ↓
Header + Sidebar
    ↓
Pages
    ↓
Dashboard Components
    ↓
API Layer
    ↓
REST API

Responsibilities

- App initializes the application.
- AppLayout manages the overall page layout.
- Header provides global actions and branding.
- Sidebar manages navigation.
- Pages orchestrate screen composition.
- Components remain presentation-only.
- API Layer communicates with the backend.

Business logic remains exclusively within backend services and engines.

This architecture allows additional pages such as Signals, Scanner, Portfolio, Risk Dashboard, Watchlist and AI Assistant to reuse the same application shell without modification.

--

## Current Scanner Integration

The current Scanner Results flow follows:

Scanner API
    ↓
Scanner Service
    ↓
Entry Confirmation Engine
    ↓
Risk Management Engine
    ↓
Market Scanner Engine
    ↓
Scanner API Response Mapper
    ↓
React Scanner API Layer
    ↓
Scanner Page and Components

The Scanner Service analyzes each configured symbol independently. A provider
or analysis failure for one symbol is logged and does not stop the remaining
scan.

The Market Opportunity Service connects validated market data, demand-zone
detection, zone scoring and ranking, trade setup, entry confirmation, risk
management, screening, and scanning.

The current scanner supports long opportunities from fresh demand zones near
the current price. Short opportunities remain disabled until short-trade
position sizing and risk calculations are implemented.

The API response mapper is kept at the API boundary so domain models do not
contain FastAPI route logic.

---

## AD-031 - Replaceable Market Data Providers

External market data access follows:

MarketDataService
    â†“
BaseMarketDataProvider
    â†“
Provider Adapter

`BaseMarketDataProvider` defines the normalized historical OHLCV contract.
`YahooProvider` is the current development adapter.

Application services depend on the provider contract rather than a vendor.
This allows future NSE-compatible, broker, licensed data, cached, and test
providers to be introduced without changing trading engines.

All provider output must pass through `MarketDataValidator` before it reaches
indicators, scanners, backtests, or other trading intelligence engines.

Provider implementations own vendor-specific symbol and response handling.
Application services own orchestration and validation. Trading engines remain
independent from network access.

---

## AD-032 - Responsive Dark Trading Shell

The React application uses one shared dark trading shell for every page.

The Material UI theme owns colors, typography, card borders, navigation
states, and common component styling. AppLayout owns responsive page spacing.
Header owns global search and account actions. Sidebar owns navigation only.

The expanded sidebar is used on large screens. A compact icon sidebar is used
on smaller screens so the application remains usable without changing page
components.

Dashboard pages and reusable cards must use theme values instead of hardcoded
light backgrounds. This keeps the full product visually consistent and allows
future dashboard panels to match the approved AlphaEdge AI design.

---

## AD-033 - Research-Only Product Boundary

AlphaEdge AI is a market research and educational analytics platform.

The platform does not execute orders, connect to brokers, manage user money,
promise returns, or present results as guaranteed outcomes.

Internal engines may use deterministic BUY, SELL, HOLD, and WAIT values for
calculation compatibility. User-facing surfaces translate these values into
Bullish Setup, Bearish Setup, and Watch.

User-facing trade-plan fields use Possible Entry, Invalidation Level, Scenario
Target, Conditions Matched, and Risk Check. Historical performance always
states that past results do not guarantee future performance.

Research disclaimers are displayed throughout the private application. Legal
and compliance review remains required before charging for stock-specific
research or adding any regulated service.

---

## AD-034 - Authentication Security Foundation

Authentication uses Argon2 password hashing, short-lived signed access tokens,
and separate refresh tokens.

Refresh tokens include unique identifiers so rotation, session revocation, and
logout can be implemented without changing token contracts. Refresh tokens
will be stored in Secure, HttpOnly cookies. Access tokens will not be stored in
browser local storage.

Authentication secrets and token lifetimes come from environment variables.
Weak secrets and invalid lifetimes are rejected before token services start.

PostgreSQL owns production user and session data. Automated tests use isolated
test storage and never depend on the production database.

---

## AD-035 - Minimum User Data

Registration stores only full name, email, country, password hash, adult
confirmation, Terms acceptance time, risk-disclosure acceptance time, account
state, email-verification state, and audit timestamps.

The platform does not collect PAN, Aadhaar, bank, broker, or payment
information in the current product scope.

Production account data uses PostgreSQL and versioned Alembic migrations.
Registration normalizes email and country values, rejects duplicate accounts,
and requires all safety consent before creating a user.

---

## AD-036 - Revocable Multi-Device Sessions

Each successful login creates a separate AuthSession for one device. Only the
refresh token identifier is stored; the full refresh token is never stored in
the database.

Refresh rotates the token and revokes the previous session. Logout revokes one
device, while logout-all revokes every active session owned by the user.

Unverified, inactive, expired, and revoked sessions cannot create new access
tokens. Access tokens remain short lived and refresh tokens remain isolated in
Secure, HttpOnly, SameSite cookies.

---

## AD-037 - Local Email Verification

Development verification uses secure one-time tokens. Only token hashes are
stored. Tokens expire, cannot be reused, and verification links are written
only to local backend logs. Public API responses never expose tokens or reveal
whether an email account exists.

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
