# AlphaEdge AI - API Documentation

> **Purpose**
>
> This document defines all public REST APIs exposed by the AlphaEdge AI backend.
>
> Only implemented APIs are documented here.
> Planned APIs are listed separately.

---

# Current Status

## Backend

## ✅ FastAPI Implemented

## Frontend

✅ React Dashboard Connected

## Dashboard Consumer

✅ React Dashboard

## API Documentation

✅ Swagger UI Available

## OpenAPI

✅ Available

## Authentication

⬜ JWT (Planned)

---

# Base URL

Development

```
http://127.0.0.1:8000
```

Swagger UI

```
http://127.0.0.1:8000/docs
```

OpenAPI

```
http://127.0.0.1:8000/openapi.json
```

---

# Implemented APIs

## Registration API

### Endpoint

```text
POST /auth/register
```

### Purpose

Creates a minimum-data AlphaEdge AI account. Registration requires acceptance
of the Terms, market-risk disclosure, and adult confirmation.

Stored account data is limited to full name, email, country, password hash,
consent timestamps, account state, and audit timestamps. Plain passwords are
never stored.

New accounts remain unverified until the future local email-verification flow
is completed.

---

## Login API

```text
POST /auth/login
```

Creates one revocable device session after email and password verification.
The response contains a short access token. The refresh token is stored in a
Secure, HttpOnly cookie and is not exposed to frontend JavaScript.

## Refresh API

```text
POST /auth/refresh
```

Rotates the current refresh token. The old device session is revoked and a new
session and token pair are created.

## Logout APIs

```text
POST /auth/logout
POST /auth/logout-all
```

Logout revokes the current device. Logout-all revokes every active device
session for the account.

## Email Verification APIs

```text
POST /auth/email-verification/request
POST /auth/email-verification/verify
```

Development verification links are written only to local backend logs. Tokens
are one-time, expire, and are stored only as hashes.

---

## Health API

### Endpoint

```
GET /health/
```

### Purpose

Verify that the AlphaEdge AI backend is running.

### Response

```json
{
    "status": "healthy"
}
```

---

## Dashboard API

### Endpoint

```
GET /dashboard/
```

### Purpose

Returns the complete dashboard data required by the React Dashboard.

The response aggregates data from multiple backend engines through the Dashboard Service and Dashboard Engine.

Current modules include:

- Market Overview
- Portfolio Summary
- Signals
- Alerts
- Scanner
- Backtest Summary
- AI Explanation

### Architecture

Dashboard API
        │
        ▼
Dashboard Service
        │
        ▼
Dashboard Engine
        │
        ▼
Domain Models
        │
        ▼
JSON Response

### Response Structure

- Market
- Portfolio
- Signals
- Alerts
- Scanner
- Backtest
- AI Explanation

Example

```json
{

    "market": {
        "nifty": {},
        "sensex": {},
        "bank_nifty": {},
        "india_vix": {}
    },

    "portfolio": {
        "total_positions": 3,
        "invested_capital": 25000,
        "available_capital": 75000,
        "total_capital": 100000
    },
    "signals": [
        {
            "symbol": "INFY",
            "action": "BUY",
            "price": 1642.5,
            "confidence": 95.0
        }
    ],
    "alerts": [
        {
            "title": "BUY",
            "message": "INFY BUY",
            "priority": "HIGH",
            "requires_action": true
        }
    ],
    "scanner": {
        "scanned_symbols": 100,
        "screener_result": {
            "opportunities": []
        }
    },
    "backtest": {
        "total_trades": 100,
        "winning_trades": 70,
        "losing_trades": 30,
        "win_rate": 70.0
    },
    "ai_explanation": {
        "decision": "BUY",
        "reasons": [
            "Weekly Demand Zone"
        ],
        "confidence_score": 92.0,
        "summary": "Weekly Demand Zone"
    }
}
```

---

# Scanner API

## Endpoint

```text
GET /scanner/
```

## Purpose

Returns scanner results for the React Scanner page.

The current implementation downloads and validates market data for configured
symbols. It detects nearby fresh demand zones, scores and ranks them, builds
trade setups, checks volume, trend, and momentum, and applies risk management
before returning approved opportunities.

The current scanner supports long opportunities only. One symbol failure does
not stop the remaining scan.

## Response

```json
{
    "total_scanned": 4,
    "total_matches": 2,
    "results": [
        {
            "symbol": "INFY",
            "entry_price": 1642.5,
            "stop_loss": 1602.5,
            "target_price": 1722.5,
            "risk_reward_ratio": 2.0,
            "confirmation_score": 92.0,
            "volume_confirmed": true,
            "trend_confirmed": true,
            "momentum_confirmed": true,
            "confirmed": true,
            "approved": true,
            "rejection_reason": null
        }
    ]
}
```

---

# Planned APIs

- Market API
- Signals API
- Portfolio API
- Risk API
- Watchlist API
- News API
- AI Assistant API
- Authentication API
- User API

---

# Technology

Backend

Python

FastAPI

Pydantic

Frontend

React 19

TypeScript

Axios

Material UI

Documentation

Swagger UI

OpenAPI

---

# Notes

- All APIs return JSON.
- Swagger documentation is automatically generated by FastAPI.
- Business logic resides within Services and Engines.
- API endpoints remain thin controllers.

# API Design Principles

All public APIs follow these principles:

- Thin Controllers
- Business Logic inside Services
- Engines perform calculations
- Models define contracts
- Validators validate external input
- JSON-only responses
- Stateless REST APIs
- OpenAPI compliant

# Future Evolution

The current REST APIs are designed as the single integration layer for:

- React Web Application
- Mobile Application
- Desktop Application
- AI Assistant
- Broker Integrations
- Third-Party Integrations
- Future Public APIs

All future clients must consume the backend through the public REST API rather than accessing business logic directly.
