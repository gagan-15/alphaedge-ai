# AlphaEdge AI - Coding Standards

> **Purpose**
>
> This document defines the coding standards followed throughout AlphaEdge AI.
>
> All backend, frontend, documentation, and test code must comply with these standards.

---

# 1. General Principles

Every line of code should be:

- Readable
- Maintainable
- Testable
- Reusable
- Consistent
- Enterprise Ready

Always prefer:

- Simplicity over cleverness
- Explicit code over implicit behaviour
- Composition over duplication
- Readability over short code

---

# 2. File Organization

Every source file should contain sections in this order:

1. File Header
2. Imports
3. Constants
4. Types / Interfaces
5. Classes / Functions
6. Export

---

# 3. File Header

Every source file begins with:

```python
"""
Module description.

Sprint:
    x.xx - Sprint Name
"""
```

Example:

```python
"""
Risk Management Engine.

Sprint:
    2.38 - Risk Management Engine
"""
```

---

# 4. Import Ordering

Imports must always be grouped.

Python

```python
# Standard Library

# Third-party

# Local Application
```

TypeScript

```typescript
// React

// Third-party

// Material UI

// Local imports
```

Never mix import groups.

---

# 5. Naming Conventions

## Classes

Use PascalCase.

Examples

MarketDataService

RiskManagementEngine

DashboardResult

---

## Functions

Use snake_case in Python.

Use camelCase in TypeScript.

Examples

calculate_rsi()

validate_data()

getDashboard()

---

## Variables

Use meaningful names.

Good

market_data

closing_prices

availableCapital

Bad

temp

abc

x

---

## Constants

Python

UPPER_CASE

TypeScript

UPPER_CASE

---

# 6. Functions

Each function should perform one responsibility.

Prefer small reusable functions.

Avoid deeply nested logic.

---

# 7. Comments

Comments explain WHY.

Not WHAT.

Bad

```python
i += 1
```

Good

```python
# Skip invalid candles
```

---

# 8. Docstrings

Every public function should include:

- Purpose
- Arguments
- Returns
- Raises (when applicable)

---

# 9. Formatting

Python

- Black formatting
- Four spaces
- Maximum readability

TypeScript

- Prettier formatting
- Consistent indentation
- Semicolons enabled

---

# 10. React Standards

Pages

- Orchestrate components
- Load API data

Components

- Presentation only
- No business logic

Layouts

- Reusable
- Shared application shell

API Layer

- Handles backend communication
- No UI rendering

---

# 11. FastAPI Standards

Routes

- Thin controllers

Services

- Business orchestration

Engines

- Calculations

Models

- Data contracts

Validators

- External validation

---

# 12. Error Handling

Never ignore exceptions.

Catch only when meaningful.

Always log unexpected errors.

Return standardized responses.

---

# 13. Testing

Every completed sprint requires:

- Unit Tests
- Regression Tests
- Pytest Passing

No sprint closes without passing tests.

---

# 14. Git Standards

Commit message format:

```
Sprint X.XX - Feature Name
```

Examples

```
Sprint 2.60 - Professional Application Shell

Sprint 2.61 - Signals Panel
```

Every completed sprint must be:

- Committed
- Pushed

---

# 15. Documentation

Whenever implementation changes:

Update:

- MASTER_PROJECT.md
- SprintHistory.md
- Roadmap.md
- Architecture.md
- API.md (if required)

Documentation is part of the sprint.

---

# 16. Code Review Checklist

Before merging:

- Architecture verified
- Naming verified
- Formatting verified
- Imports ordered
- No duplicate logic
- Tests passing
- Documentation updated

---

# Coding Motto

> Write code that another engineer can understand in one day and confidently maintain for years.