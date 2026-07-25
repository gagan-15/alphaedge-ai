# AlphaEdge AI UI and Feature Parity Audit

Updated: 26 July 2026

## Target

The supplied reference images define one consistent research platform:

- modern dark desktop shell with a compact sidebar and top header;
- shared index strip and bottom delayed-market ticker;
- dense, aligned panels that fit at 100% browser zoom;
- research and education only, with no broker connection or order execution;
- clear delayed/demo labels and source timestamps;
- consistent empty, loading and error states.

Visual similarity alone is not completion. A screen is complete only when its important
controls work, its source is identified, and demo values cannot be mistaken for live data.

## Current status

| Screen | Current state | Main gaps |
| --- | --- | --- |
| Dashboard | Partial | Layout is simpler than the reference; some panels use fixed demo values; shared ticker exists only here; gauges, breadth and movers need source-backed data. |
| Market Overview | Early partial | Missing multi-index performance chart, breadth donut, detailed movers and proper sector comparison. |
| Scanner | Partial | General filters and zone results exist, but universe is only four symbols; daily zones use heuristic scoring; filters and zone-chart detail need production validation. |
| Signals | Partial | Signal rows load, but reference-style tabs, reason columns, scenarios, invalidation and richer confidence explanations are incomplete. |
| Market Breadth | Early partial | Static summary and bars only; no sourced advance-decline series, 52-week statistics or complete sector breadth. |
| News & Events | Early partial | Static outlook; no news provider, tabs, source links, timestamps or sentiment pipeline. |
| Backtesting | Prototype | Button changes the UI, but no historical strategy engine, equity curve, costs, benchmark comparison or downloadable result. |
| Portfolio | Prototype | Illustrative values; holdings workflow and persistence need completion. |
| Risk Management | Partial | Basic risk view exists; position sizing and validation need a complete calculator workflow. |
| Alerts | Partial | Local persistence and delayed checks exist; create/edit/pause/delete flow and notification delivery need completion. |
| Economic Calendar | Prototype | Static event rows; filters, sourced events, forecast/previous values and timezone handling are missing. |
| Option Chain | Prototype | Static sample chain; expiry selection and exchange-licensed derivatives data are not connected. |
| Calculators | Early partial | Position-size calculator works; the other calculator buttons are placeholders. |

## Data truth

- Dashboard candles can use the backend's delayed Yahoo Finance feed.
- Zone Intelligence currently scans INFY, TCS, HDFCBANK and RELIANCE on the daily timeframe.
- Zone scores are heuristic research scores, not validated probabilities.
- Market breadth, sector performance, FII/DII flow, option-chain rows, calendar events,
  several dashboard metrics and news text include static demo values.
- Nothing should be labelled **live** unless a licensed live source is connected and its
  timestamp and health are visible. The free build should use **Delayed** or **Demo** labels.

## Build order

1. Shared shell parity: header, sidebar, page width, typography, cards, delayed ticker,
   loading/error/empty states and 100% zoom alignment.
2. Dashboard and Market Overview: reusable sourced index cards, chart panels, movers,
   breadth and sector modules.
3. Scanner and Signals: larger universe, working filters, clear zones, full pattern and
   scoring details, explainable scenarios and invalidation.
4. Breadth, News and Calendar: source-backed datasets with timestamps and links.
5. Backtesting, Risk, Alerts and Calculators: complete interactive workflows and persistence.
6. Option Chain: keep demo-labelled until a lawful data source is connected.
7. Responsive QA, accessibility, tests, documentation and release checks for every route.

## Completion rule

Each screen must pass:

1. reference-image visual review at 100% zoom;
2. desktop and responsive layout checks;
3. control and navigation tests;
4. API success, loading, empty and failure-state tests;
5. data-source, timestamp and demo/delayed labels;
6. research-only disclaimer and no broker execution;
7. lint, build and automated tests.

## Zone score policy

The scanner must not present a rule score as the probability that a zone will hold.
The current Zone Intelligence score is therefore named **Quality**, not Confidence.
Its visible breakdown is:

- freshness: 30 points when no later retest is observed;
- departure strength: up to 35 points, measured from the move away relative to zone width;
- retest/touch quality: up to 20 points, reduced by later touches;
- merge/confluence: up to 15 points when independently detected zones are merged.

This is a transparent ranking score. It is not yet a calibrated prediction. A future
probability may be shown only after walk-forward validation over a larger Nifty universe
and multiple timeframes, with sample size, success definition, calibration error and
out-of-sample performance published beside it.

The roadmap additionally requires multi-timeframe zones, BOS/CHOCH, leg-in and leg-out
validation, freshness, merging and ranking. These requirements are not all complete in
the current scanner and remain release gates.

## Dynamic Zone Explanation

Zone explanations are assembled from independent factor modules. Each available factor
returns a title, normalized score, positive or negative status, plain-language summary,
recommendation and weight. The UI renders only returned factors, so unfinished analysis
such as volume, liquidity sweep or higher-timeframe alignment is never shown as a
placeholder.

The first supported factors are freshness, measured departure strength, later
intersections/retests and overlapping-zone confluence. Planned modules include base
quality, leg-in, leg-out, BOS, CHOCH, trend, higher-timeframe alignment, EMA alignment,
volume, risk/reward, zone width, liquidity sweep, momentum and validated institutional
activity evidence.

The scanner now supports delayed Daily, Weekly, Monthly, Quarterly, Half-yearly and
Yearly zone requests by aggregating daily OHLCV candles. Timeframe tabs and the toolbar
reload the selected aggregation and retain a count after each timeframe has been opened.
NSE is connected; BSE remains visibly unavailable rather than displaying NSE results
under an incorrect market label.

Dashboard quick research prompts now return explicit local research guidance. They do
not call a generative AI service yet. All five secondary calculator buttons now open
working mathematical tools: risk/reward, SIP illustration, gross result, weighted
average price and Fibonacci retracement levels.

Expanded zone charts now request the same timeframe used for zone detection. Monthly
zones display monthly candles, weekly zones display weekly candles, and the same rule
applies through yearly charts. The zone is rendered as one colored band beginning at its
formation candle; duplicate full-chart proximal and distal price lines were removed.

Shared workspace parity work now uses a 224-pixel desktop sidebar, 70-pixel header,
aligned page gutters, a correctly offset delayed ticker, larger AlphaEdge branding and
consistent blue/violet interaction accents. The Dashboard uses aligned index cards with
sparklines, a large interactive chart, a signal column, and a combined AI insight,
market-breadth and sentiment column.

Market Overview now includes an aligned five-index strip, working comparison-range
controls, a four-index performance visualization, breadth donut with participation
counts, a movers table and positive/negative sector bars. Unlicensed breadth and index
summary values remain explicitly labelled as delayed development data.

Scanner filters now work for market selection, timeframe, minimum rule quality, demand
or supply type, DBR/RBR/RBD/DBD pattern, zone status and maximum proximity. The visual
workspace was checked with delayed results loaded and the table remains aligned at
100-percent browser zoom.

Zone ranking categories are Elite (90–100), Strong (75–89), Moderate (60–74), Weak
(40–59) and Rejected (below 40). Rejected zones are hidden by default and can be enabled
from the minimum-quality control. Departure strength now requires follow-through closes
and applies a penalty when price immediately reverses into the zone; a brief maximum
excursion alone cannot earn an explosive-departure score.

Market Breadth now has working range controls, an advance–decline visualization, sector
participation bars and 52-week high/low summaries. News & Events now has working
Overview, Technical, Sentiment and Scenarios tabs plus an event monitor. Both screens
show explicit demo/provider limitations instead of implying that static values are live.

Backtesting now has working strategy, period and cost controls, recalculates an
illustrative historical result, and clearly separates research output from verified
live performance. Risk Management now calculates capital at risk, position size,
exposure and risk/reward from user inputs. Alerts can be created, checked against
delayed prices, paused, resumed and deleted, with local persistence and no implied
broker execution.
