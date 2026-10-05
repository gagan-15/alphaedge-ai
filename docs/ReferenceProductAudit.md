# Reference Product Audit

## Purpose

This document records product patterns observed from a user-authorized,
read-only review of a comparable Indian-market zone research tool. It does not
copy branding, private account data, proprietary code, paid data or exact
content.

## Strong Product Patterns

### Scanner Workspace

- Dense, sortable table is the main working surface.
- Timeframe tabs show Daily, Weekly, Monthly, Quarterly, Half-yearly and Yearly
  result counts.
- Filters cover proximity, zone type and pattern.
- Rows expose symbol, company, demand/supply type, pattern, status,
  proximal/distal levels, departure quality, quality score, delayed price,
  distance, sector and base date.
- Watchlist and chart actions are available from each row.

### Multi-Timeframe Analysis

- A separate MTF view summarizes which timeframes align for each symbol.
- Overlap is highlighted separately from ordinary alignment.
- The compact columns are symbol, company, delayed price, sector, aligned
  timeframes and overlap state.

### Sector Rotation

- Sector states use Leading, Improving, Weakening and Lagging quadrants.
- Relative strength is compared with a benchmark.
- Short-window acceleration is shown alongside one- and three-month strength.
- Demand and supply zone counts provide context.
- Reader-facing actions must be changed for AlphaEdge to neutral research
  language such as Strengthening, Weakening, Watch and Review Risk.

### Alerts and Search

- Command search supports symbols, zones and sectors.
- Alert preferences include in-app notification, optional sound and
  watchlist-only or all-symbol scope.
- The product clearly states that browser-tab alerts only work while the tab is
  open and refreshing.

### Onboarding and Safety

- A guided product tour introduces the interface step by step.
- A visible education-only disclaimer remains on the product surface.
- Risk language is shown before access, not hidden in settings.
- Local-device settings are explicitly labelled.

## AlphaEdge Implementation Order

1. Extend scanner response with zone metadata and sortable filters.
2. Add timeframe result tabs backed by real analysis.
3. Add MTF confluence service and compact table.
4. Add sector-relative-strength service using a benchmark.
5. Add command search across symbols and routes.
6. Add guided onboarding.
7. Add in-app alert polling with an honest tab-open limitation.
8. Add Telegram delivery only after secure configuration and testing.

## Safety Differences

AlphaEdge remains a research-intelligence platform. It will not place orders,
connect to a broker in the current product phase, promise returns, or label
technical outputs as guaranteed trade instructions.
