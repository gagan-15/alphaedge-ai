"""Market-data adapter for the canonical GTF Trend Engine."""

from __future__ import annotations

from backend.config.gtf_workflow_roles import (
    TimeframeWorkflow,
    resolve_gtf_workflow,
)
from backend.engines.trend_engine.canonical_trend_engine import (
    CanonicalTrendEngine,
)
from backend.models.canonical_trend import (
    CanonicalTrendResult,
    CanonicalTrendState,
    TrendAlignment,
    TrendReasonCode,
)
from backend.services.market_data.market_data_service import MarketDataService
from backend.services.market_data.timeframe_service import (
    INTRADAY_SOURCES,
    aggregate_timeframe,
)


class CanonicalTrendService:
    """Load the role-aware Trend timeframe and preserve engine evidence."""

    def __init__(self, market_data: MarketDataService | None = None) -> None:
        self._market = market_data or MarketDataService()
        self._engine = CanonicalTrendEngine()

    def analyze(
        self,
        symbol: str,
        execution_timeframe: str,
    ) -> tuple[TimeframeWorkflow, CanonicalTrendResult]:
        """Return the resolved workflow and canonical Trend result."""

        workflow = resolve_gtf_workflow(execution_timeframe)
        if workflow.trend is None:
            return workflow, self._engine.unavailable(
                symbol,
                None,
                TrendReasonCode.NO_CANONICAL_TREND_TIMEFRAME,
            )
        period, interval = self._source_for(workflow.trend)
        try:
            validated = self._market.get_stock_data_segments(
                symbol,
                period=period,
                interval=interval,
            )
            framed_segments = tuple(
                aggregate_timeframe(segment, workflow.trend)
                for segment in validated.segments
                if not segment.empty
            )
            return workflow, self._engine.evaluate_segments(
                symbol,
                workflow.trend,
                framed_segments,
            )
        except Exception:
            return workflow, self._engine.unavailable(
                symbol,
                workflow.trend,
                TrendReasonCode.MARKET_DATA_UNAVAILABLE,
            )

    def alignment(
        self, zone_type: str, trend_state: CanonicalTrendState
    ) -> TrendAlignment:
        """Expose the canonical alignment decision without duplicating it."""

        return self._engine.alignment(zone_type, trend_state)

    @staticmethod
    def _source_for(timeframe: str) -> tuple[str, str]:
        if timeframe in INTRADAY_SOURCES:
            return INTRADAY_SOURCES[timeframe]
        if timeframe == "1D":
            return "1y", "1d"
        if timeframe == "1W":
            # Prefer the provider's native weekly history. Building Weekly
            # candles from segmented Daily data can discard otherwise valid
            # history after a Daily-only data break.
            return "10y", "1wk"
        if timeframe == "1M":
            return "10y", "1mo"
        return "10y", "1d"
