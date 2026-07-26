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

`Working` means the visible local workflow responds correctly. It does not mean that
the underlying data is licensed, live or production validated.

| Screen | Controls/workflow | Data state | Main production gap |
| --- | --- | --- | --- |
| Landing | Working | Product copy only | Final visual and accessibility QA |
| Login, registration, verification | Working in local/demo mode; API path exists | Local demo or configured account API | Production database, email delivery, rate limits and deployment security |
| Dashboard | Working core layout, chart ranges and local quick prompts | Mixed delayed and demo | Source every market panel; closer reference-density polish |
| Market Overview | Working 1D/1W/1M/3M/1Y controls and responsive panels | Demo comparison series | Licensed index, breadth and sector feeds |
| Scanner / Zone Intelligence | Working filters, multi-timeframe requests, grouped symbols and full-screen chart workspace | Delayed source where available; heuristic zone rules | Larger universe, feed reliability, walk-forward validation and calibrated quality policy |
| Signals | Working filters and refresh | Derived from current scanner service | Production signal lifecycle, historical validation and notification delivery |
| Holdings | Working local add/remove/persistence | Local entries plus delayed lookup | Broker-grade reconciliation is intentionally out of scope |
| Watchlist | Working local add/remove/persistence | Local entries plus delayed lookup | Larger symbol master and reliable licensed quote feed |
| Market Breadth | Working 1D/1W/1M/3M controls | Demo-labelled | Sourced advance/decline, highs/lows and sector constituents |
| News & Events | Working research tabs | Demo/provider-unconnected | Licensed news, citations, timestamps and sentiment pipeline |
| Strategies | Working create, enable, pause and delete | Browser-local templates | Production rule execution and versioned persistence |
| AI Assistant | Working local prompt templates | Transparent rule-based guidance | Optional production AI provider, evaluation and source grounding |
| Backtesting | Working input controls and illustrative recalculation | Illustrative only | Timestamped historical engine, benchmark, costs, slippage and walk-forward tests |
| Risk Management | Working calculations | User-entered values | Validation rules, saved plans and portfolio-level exposure |
| Alerts | Working create, check, pause, resume and delete | Browser-local; delayed check | Background scheduler and Telegram/email/in-app delivery |
| Economic Calendar | Working country, impact and Today/Upcoming filters | Demo-labelled | Approved event feed and reliable timezone handling |
| Option Chain | Working underlying, expiry and strike controls | Demo-labelled | Authorized NSE derivatives feed and exchange timestamps |
| Calculators | All six tools working | Mathematical inputs only | Input validation, fees/taxes where relevant and saved scenarios |
| Reports | Working JSON download | Browser-local workspace snapshot | PDF/CSV formats, server history and signed audit trail |
| Settings | Working save/reset and scanner defaults | Browser-local preferences | Account sync; desktop/background notification implementation |

## Audit conclusion

The product is a functional local research prototype, not a complete real-time product.
The largest remaining work is not another visual card: it is lawful market data,
production authentication/infrastructure, validated zone research, a real backtest
engine, background alerts and complete cross-device QA. Demo panels stay visibly
labelled and must never be represented as accurate live market data.

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

Economic Calendar now has working country, impact and date-window controls with a
clear demo-feed label. Option Chain now recalculates visible strikes when the
underlying or strike count changes and marks the illustrative ATM row. Calculators
now use one consistent workspace with working position-size, risk/reward, profit,
average-price, SIP and Fibonacci tools.

Zone detection now rejects setups where the first leg-out body is not at least
10 percent stronger than the incoming leg body, or where the three-candle
directional follow-through does not exceed the incoming leg. This prevents a
small bounce followed by immediate failure from being presented as a strong zone.
The comparison is pattern-independent and applies to DBR, RBR, RBD and DBD zones.

Strategies now supports creating, enabling, pausing and deleting locally stored
rule templates. AI Assistant now provides working, transparent rule-based research
responses and explicitly states that no generative provider is connected. Portfolio
and Watchlist retain local persistence and use the existing delayed candle service;
neither screen implies a broker connection.

The multi-timeframe scanner now enforces the leg-out rule inside the actual
`DepartureDetector` used by `/scanner/zones`, not only the legacy detector.
Scanner timeframe tabs show the visible filtered count on the active tab and no
longer retain stale totals beside previously opened timeframes.

Market Overview now uses a dedicated responsive screen with compact index cards,
labelled chart axes, normalized multi-index lines, a breadth donut, a movers table
and sector participation bars. The former oversized placeholder chart is no longer
routed into the application.

Market Overview range controls now alter the normalized series and x-axis labels
for 1D, 1W, 1M, 3M and 1Y. They no longer act as selection-only buttons over a
static chart.

Breached zones are excluded from scanner results. A demand zone is invalid after
a later candle closes below its distal (lower) boundary; a supply zone is invalid
after a later candle closes above its distal (upper) boundary. Wicks alone remain
classified as tests or liquidity probes, while confirmed close breaches remove
the zone.

Active scanner results now exclude zones that were tested before the latest
candle and already produced a reaction. A first touch occurring on the current
candle remains visible as `IN ZONE`; completed reactions are reserved for a
future historical-validation view instead of being presented as new opportunities.

Zone quality now uses mandatory departure gates. Freshness, zero touches and merge
confluence cannot lift a structurally weak departure into a moderate or strong
rating. Departure below 40 percent of its available points is capped as Rejected;
below 60 percent is capped as Weak; below 75 percent cannot exceed Moderate; and
below 90 percent cannot reach Elite.

Departure detection also requires at least two closes beyond the base boundary,
a sustained final close in the departure direction, and movement of at least
1.5 times the full zone width. Overlapping or hesitant candles are rejected even
when the first departure candle is larger than the incoming leg.

The scanner supports 5m, 15m, 75m, 125m, 1H, 2H, 4H and 6H intraday
research timeframes through a compact dropdown. Intraday requests use intraday
source candles and custom aggregation where needed; intraday candles are never
manufactured from daily data.

Selecting a scanner row now opens a full-screen AlphaEdge research workspace
instead of expanding the chart inside the table. The workspace includes the
interactive candlestick chart, highlighted zone, crosshair, pan, wheel zoom,
fit control, two-point price/percentage measurement and the complete evidence
and recommendation panel. It does not copy TradingView branding or order tools.

Gap-up and gap-down departures are supported and visibly marked in scanner
results. A gap qualifies only when the departure candle does not overlap the
previous candle range, closes beyond the base boundary and receives directional
follow-through. A gap by itself cannot make a zone valid.

Scanner rows are grouped by symbol, so a stock appears only once per selected
timeframe. Opening that row plots every active demand and supply zone for the
symbol on one full-screen chart and lists each zone's pattern, boundaries, status,
base date and quality beside the chart.

Market Overview layout phase two establishes a reusable institutional information
hierarchy without adding unvalidated calculations or feeds. The existing route and
global navigation remain unchanged. The page now reserves ordered sections for an
AI market summary, four decision KPIs, participation chart, sector rotation and
breadth, institutional flow/VIX/sentiment, opportunities/alerts and a final daily
verdict. Desktop uses a 12-column grid, tablet collapses to two columns and mobile
keeps the same information order in one column.

Market Overview widget phase replaces every reserved slot without moving the layout.
It includes an expandable transparent-logic summary, animated health and confidence
gauges, regime/bias/risk interpretation, six genuinely different participation
timeframe datasets, overlay controls, a sector table/heatmap switch, detailed breadth
metrics, institutional flow, VIX, sentiment, opportunities, alerts and a daily verdict.
Tooltips and reusable loading/empty-state components are included. Values remain
explicit development data until approved market, breadth, flow and volatility feeds
are connected; the summary is deterministic demo logic and is not represented as AI.

The AI Market Summary alone was then upgraded into an executive interpretation panel.
Its headline, narrative, status chips, research focus and confidence-factor breakdown
are derived from a reusable typed input object rather than fixed page copy. It includes
animated confidence, chip tooltips, expandable score contributions, professional
loading/empty states and a working scanner hand-off. The displayed model remains
transparent demonstration logic until a validated intelligence service is connected.

All Market Overview user-facing copy now follows the plain-language rule. Technical
terms are removed where possible and immediately explained when they are necessary.
Labels describe what users can understand and do, such as "Stocks Going Up and Down,"
"Large Investor Activity" and "Look for Buying Opportunities." Tooltips explain moving
averages, exchange price limits, market participation and expected price swings in one
short sentence.

The AI summary score is now named Overall Market Score and is shown as a plain
`91 / 100` health reading. The visible explanation is limited to four short sentences.
Seven chips use beginner-friendly names, and the research strip includes a simple
"What should I do today?" checklist. The Why action opens a side panel with five
plain-English reasons and never exposes a technical formula.

Only the Market Participation Trend widget was then upgraded. Its 1D, 1W, 1M, 3M,
6M and 1Y views use separate intraday, daily, weekly or monthly-density datasets.
The chart includes simple positive/zero/negative axes, current/high/low and hover
markers, event markers, Nifty and Bank Nifty comparison lines, quick statistics,
plain-English strengthening/weakening detection, keyboard navigation, loading and
empty states, fullscreen, CSV export and a link to detailed market data.

Market Overview now has a reusable 440-pixel Customize Drawer connected to the
existing Customize action. It provides five presets, per-widget visibility, a saved
default timeframe and stock group, chart preferences, simple/professional language,
density and number-format choices. Presets and widget visibility preview immediately;
Cancel restores the saved view, all-widget hiding is blocked, and Save persists a
versioned preference model under the current local user key. Data and widget business
logic remain unchanged.

Customize Drawer functionality is now connected end to end. Presets configure their
timeframe, language, density, comparison lines and visible widgets; every manual change
switches the preset to Custom. Live preview updates the participation chart, AI summary,
verdict, health, trend, demo stock universe, explanations, tooltips, density and number
format. AI Summary cannot be hidden, at least one analysis widget must remain, Reset
requires confirmation, and Save is enabled only while an "Unsaved Changes" state exists.
The local schema is version 2 and retains a service boundary for future account storage.

The Scanner full-screen research chart now uses its existing right-side panel as a
decision workspace. It explains the rule-based quality score, gives a cautious research
recommendation, shows the available zone evidence, failed or unconfirmed checks, zone
freshness, retests and departure strength, and provides working local watchlist, alert
and share actions. Missing trade-plan, trend, momentum, sector, relative-performance,
historical and risk fields are labelled as unavailable rather than being invented.
Validated backend services are required before entry, stop, target, probability or
historical-success values can be shown.
