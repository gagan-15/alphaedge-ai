"""
Scanner API.

Sprint:
    2.64 - Scanner Results Foundation
"""

from concurrent.futures import Future, ThreadPoolExecutor
import os
from dataclasses import replace
from datetime import UTC, datetime
from threading import RLock
from time import monotonic, perf_counter, sleep
from typing import Literal
from uuid import uuid4

from fastapi import APIRouter, Header, HTTPException, Query
from pandas import DataFrame

from backend.core.logger import logger
from backend.api.models.scanner_response import (
    ScannerResponse,
    ScannerResultResponse,
    CanonicalTradeConfidenceResponse,
    ZoneExplanationFactorResponse,
    ZoneExplanationResponse,
    ZoneQualityComponentResponse,
    ZoneResearchResponse,
    ZoneResearchResultResponse,
    ZoneLifecycleSummaryResponse,
    ZoneStateCountResponse,
    ZoneCandidateDiagnosticResponse,
    ZoneDiagnosticsResponse,
    ZoneRuleDiagnosticResponse,
)
from backend.config.scanner_config import ScannerConfig
from backend.config.canonical_methodology import SCANNER_METHODOLOGY_CACHE_VERSION
from backend.engines.demand_supply_engine.zone_detection_engine import (
    ZoneDetectionEngine,
)
from backend.engines.zone_scoring_engine.zone_scoring_engine import (
    ZoneScoringEngine,
)
from backend.models.market_scanner.market_scanner_result import (
    MarketScannerResult,
)
from backend.models.zone import Zone, ZoneType
from backend.models.zone_scoring.canonical_zone_quality import ZoneQualityContext
from backend.models.canonical_zone_analysis import CanonicalZoneAnalysis
from backend.engines.trade_confidence_engine import CanonicalTradeConfidenceEngine
from backend.services.scanner.scanner_service import (
    ScannerService,
)
from backend.services.scanner.dashboard_zone_qualification_service import (
    DashboardZoneQualificationService,
)
from backend.services.scanner.stock_details_analysis_service import (
    StockDetailsAnalysisService,
)
from backend.services.scanner.timeframe_confluence_service import (
    TimeframeConfluenceService,
)
from backend.services.scanner.zone_lifecycle_ui_service import (
    ZoneLifecycleUiService,
)
from backend.services.scanner.zone_result_enrichment_service import (
    ZoneResultEnrichmentService,
)
from backend.services.zone_explanation_service import ZoneExplanationService
from backend.services.market_data.market_data_service import MarketDataService
from backend.services.market_data.timeframe_service import (
    TIMEFRAME_RULES,
    aggregate_timeframe,
)
from backend.services.market_data.canonical_source_semantics import (
    DAILY_HISTORY_PERIOD,
    DAILY_SOURCE_INTERVAL,
    DAILY_SOURCE_SEMANTICS_VERSION,
)
from backend.services.market_data.dhan_shadow_store import DhanShadowStore
from backend.services.market_data.dhan_quote_service import DhanQuoteService
from backend.services.market_data.dhan_incremental_update_service import (
    DhanIncrementalUpdateService,
)
from backend.services.market_data.dhan_authentication_service import (
    DhanAuthenticationService,
)
from backend.config.market_data_providers import MARKET_DATA_PROVIDER
from backend.services.scanner.universe_service import (
    UniverseName,
    UniverseService,
)
from backend.services.scanner.persistent_scanner_store import (
    PersistentScannerStore,
    DERIVED_EOD_STORAGE_VERSION,
    SCANNER_ARCHITECTURE_VERSION,
    SCANNER_STORAGE_VERSION,
)
from backend.services.scanner.instrument_master_service import (
    ALL_SUPPORTED_INDIAN_EQUITY_UNIVERSE,
    InstrumentMasterService,
)

scanner_router = APIRouter(
    prefix="/scanner",
    tags=["Scanner"],
)

_scanner_service = ScannerService()
_zone_market_data = MarketDataService()
_zone_engine = ZoneDetectionEngine()
_zone_scoring_engine = ZoneScoringEngine()
_zone_config = ScannerConfig()
_stock_details_analysis = StockDetailsAnalysisService()
_timeframe_confluence = TimeframeConfluenceService()
_trade_confidence = CanonicalTradeConfidenceEngine()
_zone_lifecycle_ui = ZoneLifecycleUiService()
_dashboard_qualification = DashboardZoneQualificationService()
_zone_result_enrichment = ZoneResultEnrichmentService()
_universe_service = UniverseService()
_persistent_scanner_store = PersistentScannerStore()
_dhan_shadow_store = DhanShadowStore()
_dhan_quote_service = DhanQuoteService()
_dhan_update_executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="dhan-incremental-update")
_dhan_update_future: Future[object] | None = None
_dhan_update_lock = RLock()
_instrument_master = InstrumentMasterService(_persistent_scanner_store.path)
_zone_scan_executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="zone-scan")
_core_preparation_executor = ThreadPoolExecutor(
    max_workers=1, thread_name_prefix="core-timeframe-preparation"
)
_zone_scan_cache: dict[str, tuple[float, ZoneResearchResponse]] = {}
_zone_scan_jobs: dict[str, Future[ZoneResearchResponse]] = {}
_zone_scan_progress: dict[str, tuple[int, int]] = {}
_zone_scan_lock = RLock()
# A complete large-universe scan is expensive. Keep the last completed result
# available long enough that normal page navigation does not continuously start
# another NSE 500 scan.
_zone_scan_ttl_seconds = 1800.0
_CORE_DERIVED_TIMEFRAMES: tuple[str, ...] = (
    "WEEKLY", "MONTHLY", "QUARTERLY", "HALFYEARLY", "YEARLY",
)
_CORE_EOD_TIMEFRAMES: tuple[str, ...] = (
    "DAILY", *_CORE_DERIVED_TIMEFRAMES,
)
_INTRADAY_TIMEFRAMES: tuple[str, ...] = (
    "MINUTE_5", "MINUTE_15", "MINUTE_75", "MINUTE_125",
    "HOUR_1", "HOUR_2", "HOUR_4", "HOUR_6",
)
_core_preparation_future: Future[None] | None = None
_PRIMARY_PERSISTED_UNIVERSE = ALL_SUPPORTED_INDIAN_EQUITY_UNIVERSE
_DHAN_DASHBOARD_UNIVERSES = (
    "nifty50", "nifty100", "nifty200", "nse500", "fno",
    "nse_main", "nse_sme", "allnse", "bse_main", "bse_sme",
    "allbse", "allindia",
)
_DHAN_DASHBOARD_SORT_ALIASES = {
    "distance_percent": "distance",
    "zone_score": "zone_quality",
}


def _normalize_dhan_dashboard_sort(sort: str) -> str:
    """Accept table-column aliases without widening the persisted sort allow-list."""
    return _DHAN_DASHBOARD_SORT_ALIASES.get(sort, sort)


def _dhan_index_constituents() -> dict[str, list[str]]:
    """Intersect configured index/F&O membership with current Dhan identities."""
    return {
        name: _universe_service.get_symbols(name)  # type: ignore[arg-type]
        for name in ("nifty50", "nifty100", "nifty200", "nse500", "fno")
    }


def _snapshot_storage_version(timeframe: str) -> str:
    return (
        DERIVED_EOD_STORAGE_VERSION
        if timeframe in _CORE_DERIVED_TIMEFRAMES
        else SCANNER_STORAGE_VERSION
    )


def _price_dependent_status(result: ZoneResearchResultResponse, price: float) -> tuple[float, str]:
    """Recalculate display-only distance/status without altering zone evidence."""
    proximal, distal = float(result.proximal_price), float(result.distal_price)
    upper, lower = max(proximal, distal), min(proximal, distal)
    if result.status == "INVALIDATED":
        return 0.0, "INVALIDATED"
    if result.lifecycle_status == "REACTING" or result.status == "REACTING":
        return round(abs(price - proximal) / max(price, 1e-9) * 100, 2), "REACTING"
    if lower <= price <= upper:
        return 0.0, "IN ZONE"
    distance = ((price - upper) if price > upper else (lower - price)) / max(price, 1e-9) * 100
    return round(distance, 2), "APPROACHING" if distance <= 5 else "FAR"


def _overlay_dhan_current_prices(rows: list[str]) -> list[dict[str, object]]:
    """Overlay exact Dhan LTPs on response rows; persisted snapshot stays immutable."""
    results = [ZoneResearchResultResponse.model_validate_json(row) for row in rows]
    instrument_ids = sorted({item.instrument_id for item in results if item.instrument_id})
    instruments = _dhan_shadow_store.instruments_by_ids(instrument_ids)
    live_quotes = _dhan_quote_service.quotes_for(instruments)
    persisted_closes = _dhan_shadow_store.latest_daily_closes(instrument_ids)
    rendered: list[dict[str, object]] = []
    for item in results:
        quote = live_quotes.get(item.instrument_id or "")
        fallback = persisted_closes.get(item.instrument_id or "")
        if quote is not None:
            price, source, as_of = quote.price, "LIVE_QUOTE", quote.as_of
        elif fallback is not None:
            price, source, as_of = fallback[0], "PERSISTED_DHAN_CLOSE", fallback[1]
        else:
            price, source, as_of = item.current_price, "PERSISTED_DHAN_CLOSE", item.price_as_of
        distance, status = _price_dependent_status(item, price)
        rendered.append(item.model_copy(update={
            "current_price": float(price), "distance_percent": distance, "status": status,
            "price_source": source, "price_as_of": as_of,
        }).model_dump())
    return rendered


def _filter_dhan_response_time_rows(
    rows: list[dict[str, object]], *, status: str | None, max_distance: float | None,
) -> list[dict[str, object]]:
    """Apply filters to the exact current values returned to the Dashboard."""
    expected_status = {"WATCH": "FAR"}.get((status or "").upper(), (status or "").upper())
    matched: list[dict[str, object]] = []
    for item in rows:
        if expected_status and str(item.get("status", "")).upper() != expected_status:
            continue
        try:
            distance = float(item.get("distance_percent"))
        except (TypeError, ValueError):
            continue
        if max_distance is not None and distance > max_distance:
            continue
        matched.append(item)
    return matched


def _sort_dhan_response_time_rows(
    rows: list[dict[str, object]], *, field: str, descending: bool,
) -> list[dict[str, object]]:
    """Deterministically sort after the live/persisted price overlay."""
    def numeric(item: dict[str, object], key: str) -> tuple[int, float]:
        try:
            value = item.get(key)
            return (0, float(value)) if value is not None else (1, 0.0)
        except (TypeError, ValueError):
            return (1, 0.0)

    def trade_confidence(item: dict[str, object]) -> tuple[int, float]:
        confidence = item.get("trade_confidence")
        if not isinstance(confidence, dict):
            return (1, 0.0)
        try:
            return (0, float(confidence.get("score")))
        except (TypeError, ValueError):
            return (1, 0.0)

    def identity(item: dict[str, object]) -> tuple[str, str]:
        return str(item.get("symbol", "")), str(item.get("zone_id", ""))

    if field == "contextual_rank":
        return sorted(rows, key=lambda item: (
            *numeric(item, "distance_percent"),
            -numeric(item, "zone_score")[1],
            *identity(item),
        ))
    if field == "symbol":
        return sorted(rows, key=lambda item: (*identity(item),), reverse=descending)
    value_getter = {
        "distance": lambda item: numeric(item, "distance_percent"),
        "current_price": lambda item: numeric(item, "current_price"),
        "zone_quality": lambda item: numeric(item, "zone_score"),
        "trade_confidence": trade_confidence,
    }.get(field)
    if value_getter is None:
        raise ValueError("Unsupported sort.")
    return sorted(rows, key=lambda item: (
        value_getter(item)[0],
        -value_getter(item)[1] if descending else value_getter(item)[1],
        *identity(item),
    ))


def _seed_instrument_master() -> None:
    """Mirror configured NSE universes into the durable instrument master."""

    names = ["nifty50", "nifty100", "nifty200", "nse500", "fno"]
    if not _instrument_master.has_current_master():
        names.append("allnse")
    for name in names:
        try:
            _persistent_scanner_store.seed_universe(
                name,
                _universe_service.get_symbols(name),
                source=f"AlphaEdge configured {name} universe",
            )
        except Exception:
            logger.exception("Instrument-master seed failed for %s.", name)


_seed_instrument_master()


def _serialize_trade_confidence(confidence: object) -> CanonicalTradeConfidenceResponse:
    """Serialize the promoted canonical model without changing its values."""

    return CanonicalTradeConfidenceResponse(
        score=confidence.total_score,
        label=confidence.label.value,
        zone_quality_score=confidence.zone_quality_score,
        zone_quality_contribution=confidence.zone_quality_contribution,
        location_contribution=confidence.location_contribution,
        trend_contribution=confidence.trend_contribution,
        location_alignment=confidence.location_alignment,
        trend_alignment=confidence.trend_alignment,
        combined_context=confidence.combined_context,
        htf_overlap_type=confidence.htf_overlap_type,
        htf_direction_compatibility=confidence.htf_direction_compatibility,
        data_sufficiency=confidence.data_sufficiency.value,
        reason_codes=confidence.reason_codes,
        evidence=confidence.evidence,
        shadow_mode=False,
    )


def _canonical_trade_confidence_for_row(
    item: ZoneResearchResultResponse,
    *,
    refresh_key: str,
) -> CanonicalTradeConfidenceResponse:
    """Compose shadow Trade Confidence from the same canonical context endpoint uses."""

    payload = _timeframe_confluence.build(
        item.symbol,
        item.timeframe,
        item.zone_type,
        item.proximal_price,
        item.distal_price,
        refresh_key,
    )
    canonical = payload["canonical_analysis"]
    analysis = CanonicalZoneAnalysis(
        zone_id=item.zone_id or refresh_key,
        symbol=item.symbol,
        timeframe=item.timeframe,
        zone_type=item.zone_type,
        pattern=item.pattern_type,
        proximal=item.proximal_price,
        distal=item.distal_price,
        formation_evidence=None,
        lifecycle=None,
        authenticity=None,
        zone_quality=item.zone_score,
        canonical_trend=canonical.get("canonical_trend"),
        htf_context=canonical.get("htf_location"),
        alignment=str(canonical.get("trend_alignment", "UNKNOWN")),
        significant_gap=False,
        gap_measurement=None,
        trend_timeframe=canonical.get("trend_timeframe"),
        location_timeframe=canonical.get("location_timeframe"),
        trend_alignment=str(canonical.get("trend_alignment", "UNKNOWN")),
        location_relationship=str(
            canonical.get("location_relationship", "NO_OVERLAP")
        ),
        location_compatibility=str(
            canonical.get("location_compatibility", "NO_HTF_CONTEXT")
        ),
        combined_context=payload.get("combined_context"),
        data_sufficient=bool(canonical.get("data_sufficient", False)),
        reason_codes=tuple(canonical.get("reason_codes", ())),
    )
    return _serialize_trade_confidence(_trade_confidence.evaluate(analysis))


ZoneTimeframe = Literal[
    "MINUTE_5",
    "MINUTE_15",
    "MINUTE_75",
    "MINUTE_125",
    "HOUR_1",
    "HOUR_2",
    "HOUR_4",
    "HOUR_6",
    "DAILY",
    "WEEKLY",
    "MONTHLY",
    "QUARTERLY",
    "HALFYEARLY",
    "YEARLY",
]

_TIMEFRAME_LABELS = {
    "MINUTE_5": "5m",
    "MINUTE_15": "15m",
    "MINUTE_75": "75m",
    "MINUTE_125": "125m",
    "HOUR_1": "1H",
    "HOUR_2": "2H",
    "HOUR_4": "4H",
    "HOUR_6": "6H",
    "DAILY": "1D",
    "WEEKLY": "1W",
    "MONTHLY": "1M",
    "QUARTERLY": "3M",
    "HALFYEARLY": "6M",
    "YEARLY": "1Y",
}

_INTRADAY_SOURCE = {
    "MINUTE_5": ("1mo", "5m"),
    "MINUTE_15": ("1mo", "15m"),
    "MINUTE_75": ("1mo", "15m"),
    "MINUTE_125": ("1mo", "5m"),
    "HOUR_1": ("1mo", "1h"),
    "HOUR_2": ("1mo", "1h"),
    "HOUR_4": ("1mo", "1h"),
    "HOUR_6": ("1mo", "1h"),
}


def _timeframe_data(data: DataFrame, timeframe: str) -> DataFrame:
    """Aggregate daily OHLCV candles into the selected research timeframe."""

    return aggregate_timeframe(data, _TIMEFRAME_LABELS[timeframe])


def _canonical_gap_type(zone: Zone) -> str | None:
    """Serialize immutable gap evidence produced by canonical formation."""

    evidence = zone.formation_evidence
    if evidence is None or not evidence.significant_gap:
        return None
    return "GAP UP" if evidence.leg_in_direction.value == "BULLISH" else "GAP DOWN"


# Deprecated compatibility helpers. Production and Developer Mode must not call
# these; canonical engines are the only source for application lifecycle data.
def _measure_zone(zone: Zone, data: DataFrame) -> Zone:
    width = max(zone.upper_price - zone.lower_price, 1e-9)
    start = min(zone.created_index + 1, len(data))
    end = min(start + 3, len(data))
    departure = data.iloc[start:end]
    if departure.empty:
        multiple = follow = 0.0
        penalty = 1.0
    elif zone.zone_type == ZoneType.DEMAND:
        multiple = max(0.0, (float(departure["High"].max()) - zone.upper_price) / width)
        follow = float((departure["Close"] > zone.upper_price).sum()) / len(departure)
        penalty = (
            0.45 if float(departure["Close"].iloc[-1]) <= zone.upper_price else 1.0
        )
    else:
        multiple = max(0.0, (zone.lower_price - float(departure["Low"].min())) / width)
        follow = float((departure["Close"] < zone.lower_price).sum()) / len(departure)
        penalty = (
            0.45 if float(departure["Close"].iloc[-1]) >= zone.lower_price else 1.0
        )
    later = data.iloc[end:]
    touches = int(
        ((later["Low"] <= zone.upper_price) & (later["High"] >= zone.lower_price)).sum()
    )
    return replace(
        zone,
        strength=round(min(35.0, multiple / 3.0 * 35.0) * follow * penalty, 2),
        is_fresh=touches == 0,
        touch_count=touches,
    )


def _is_zone_invalidated(zone: Zone, data: DataFrame) -> bool:
    closes = data.iloc[min(zone.created_index + 2, len(data)) :]["Close"]
    if closes.empty:
        return False
    return (
        bool((closes < zone.lower_price).any())
        if zone.zone_type == ZoneType.DEMAND
        else bool((closes > zone.upper_price).any())
    )


def _has_completed_test(zone: Zone, data: DataFrame) -> bool:
    candles = data.iloc[min(zone.created_index + 4, len(data)) : -1]
    return (
        False
        if candles.empty
        else bool(
            (
                (candles["Low"] <= zone.upper_price)
                & (candles["High"] >= zone.lower_price)
            ).any()
        )
    )


def _departure_gap(zone: Zone, data: DataFrame) -> str | None:
    index = zone.created_index + 1
    if index >= len(data):
        return None
    previous, departure = data.iloc[index - 1], data.iloc[index]
    if float(departure["Low"]) > float(previous["High"]):
        return "GAP UP"
    if float(departure["High"]) < float(previous["Low"]):
        return "GAP DOWN"
    return None


def _reaction_state(
    zone: Zone, data: DataFrame, completion_percent: float
) -> dict[str, object]:
    later = data.iloc[min(zone.created_index + 4, len(data)) :]
    if len(later) < 2:
        return {"active": False}
    demand = zone.zone_type == ZoneType.DEMAND
    touched = False
    previous_close: float | None = None
    start_position: int | None = None
    started = None
    for position, (index, candle) in enumerate(later.iterrows()):
        low, high, close = (
            float(candle["Low"]),
            float(candle["High"]),
            float(candle["Close"]),
        )
        entered = low <= zone.upper_price and high >= zone.lower_price
        touched = touched or entered
        crossed = touched and (
            (
                demand
                and close > zone.upper_price
                and (
                    entered
                    or previous_close is not None
                    and previous_close <= zone.upper_price
                )
            )
            or (
                not demand
                and close < zone.lower_price
                and (
                    entered
                    or previous_close is not None
                    and previous_close >= zone.lower_price
                )
            )
        )
        if crossed:
            start_position, started = position, index
            break
        previous_close = close
    if start_position is None:
        return {"active": False}
    proximal = zone.upper_price if demand else zone.lower_price
    latest = float(data["Close"].iloc[-1])
    percent = (
        (latest - proximal) / proximal * 100
        if demand
        else (proximal - latest) / proximal * 100
    )
    completion_price = proximal * (
        1 + completion_percent / 100 if demand else 1 - completion_percent / 100
    )
    reaction = later.iloc[start_position:]
    mask = (
        reaction["Close"] >= completion_price
        if demand
        else reaction["Close"] <= completion_price
    )
    positions = [index for index, complete in enumerate(mask.tolist()) if complete]
    completed = bool(positions)
    end_position = positions[0] if completed else None
    ended = reaction.index[end_position] if end_position is not None else None
    return {
        "active": not completed and percent >= 0,
        "percent": round(percent, 2),
        "started": (
            started.isoformat() if hasattr(started, "isoformat") else str(started)
        ),
        "ended": (
            ended.isoformat()
            if ended is not None and hasattr(ended, "isoformat")
            else str(ended) if ended is not None else None
        ),
        "duration": end_position + 1 if end_position is not None else len(reaction),
    }


def build_scanner_response(
    scanner: MarketScannerResult,
) -> ScannerResponse:
    """
    Convert a domain scanner result into an API response.
    """

    results = tuple(
        ScannerResultResponse(
            symbol=opportunity.symbol,
            entry_price=(
                opportunity.risk_management_result.entry_confirmation.trade_setup.entry_price  # noqa: E501
            ),
            stop_loss=(
                opportunity.risk_management_result.entry_confirmation.trade_setup.stop_loss  # noqa: E501
            ),
            target_price=(
                opportunity.risk_management_result.entry_confirmation.trade_setup.target_price  # noqa: E501
            ),
            risk_reward_ratio=(
                opportunity.risk_management_result.entry_confirmation.trade_setup.risk_reward_ratio  # noqa: E501
            ),
            confirmation_score=(
                opportunity.risk_management_result.entry_confirmation.confirmation_score
            ),
            volume_confirmed=(
                opportunity.risk_management_result.entry_confirmation.volume_confirmed
            ),
            trend_confirmed=(
                opportunity.risk_management_result.entry_confirmation.trend_confirmed
            ),
            momentum_confirmed=(
                opportunity.risk_management_result.entry_confirmation.momentum_confirmed
            ),
            confirmed=(opportunity.risk_management_result.entry_confirmation.confirmed),
            approved=(opportunity.risk_management_result.approved),
            rejection_reason=(opportunity.risk_management_result.rejection_reason),
            zone_type=opportunity.zone_type,
            proximal_price=opportunity.proximal_price,
            distal_price=opportunity.distal_price,
            zone_score=opportunity.zone_score,
            distance_percent=opportunity.distance_percent,
            zone_fresh=opportunity.zone_fresh,
            touch_count=opportunity.touch_count,
            base_index=opportunity.base_index,
            timeframe=opportunity.timeframe,
            pattern_type=opportunity.pattern_type,
        )
        for opportunity in scanner.screener_result.opportunities
    )

    return ScannerResponse(
        total_scanned=scanner.scanned_symbols,
        total_matches=len(results),
        results=results,
    )


@scanner_router.get(
    "/",
    response_model=ScannerResponse,
)
def get_scanner(
    universe: UniverseName = Query(default="allnse"),
    symbols: list[str] | None = Query(default=None),
) -> ScannerResponse:
    """
    Return the current scanner data.
    """

    return build_scanner_response(
        _scanner_service.get_scanner(universe, symbols),
    )


def _scan_research_zones(
    timeframe: ZoneTimeframe,
    universe: UniverseName,
    symbols: list[str] | None,
    progress_key: str | None = None,
    durable_job_id: int | None = None,
) -> ZoneResearchResponse:
    """Return recent demand and supply zones for research exploration."""

    scan_started = perf_counter()
    results: list[ZoneResearchResultResponse] = []
    historical_results: list[ZoneResearchResultResponse] = []
    dashboard_base_preferences: dict[tuple[str, int], int] = {}
    summary_keys = (
        "total",
        "fresh",
        "reacting",
        "tested",
        "retested",
        "invalidated",
        "authentic",
        "non_authentic",
    )
    summary = {
        "DEMAND": {key: 0 for key in summary_keys},
        "SUPPLY": {key: 0 for key in summary_keys},
    }
    scanned = 0
    canonical_zone_count = 0
    formation_qualified_count = 0
    dashboard_qualified_count = 0
    qualification_rejection_counts: dict[str, int] = {}
    universe_symbols = _universe_service.get_symbols(universe, symbols)
    source_period, source_interval = _INTRADAY_SOURCE.get(
        timeframe,
        (
            "10y" if timeframe != "DAILY" else _zone_config.period,
            _zone_config.interval,
        ),
    )

    zero_range_skipped = 0
    zones_ended_at_data_break = 0

    def load_symbol(
        symbol: str,
    ) -> tuple[tuple[DataFrame, ...], int] | None:
        for attempt in range(2):
            try:
                validated = _zone_market_data.get_stock_data_segments(
                    symbol=symbol,
                    period=source_period,
                    interval=source_interval,
                )
                segments = tuple(
                    framed
                    for segment in validated.segments
                    if not (framed := _timeframe_data(segment, timeframe)).empty
                )
                if not segments:
                    raise ValueError("No valid market-data segments remain.")
                if progress_key:
                    with _zone_scan_lock:
                        processed, failed = _zone_scan_progress.get(
                            progress_key,
                            (0, 0),
                        )
                        _zone_scan_progress[progress_key] = (
                            processed + 1,
                            failed,
                        )
                return segments, validated.skipped_zero_range_count
            except Exception:
                if attempt == 0:
                    sleep(0.25)
        if progress_key:
            with _zone_scan_lock:
                processed, failed = _zone_scan_progress.get(progress_key, (0, 0))
                _zone_scan_progress[progress_key] = (processed, failed + 1)
        return None

    with ThreadPoolExecutor(
        max_workers=min(
            _zone_config.scan_concurrency,
            max(1, len(universe_symbols)),
        ),
        thread_name_prefix="alphaedge-zone-data",
    ) as executor:
        loaded_data = list(executor.map(load_symbol, universe_symbols))
    load_completed = perf_counter()

    load_failures_seen = 0
    for position, (symbol, loaded) in enumerate(
        zip(universe_symbols, loaded_data, strict=True),
        start=1,
    ):
        if loaded is None:
            load_failures_seen += 1
            if durable_job_id is not None and (
                position % 10 == 0 or position == len(universe_symbols)
            ):
                _persistent_scanner_store.update_job(
                    durable_job_id,
                    "RUNNING",
                    processed=position,
                    failed=load_failures_seen,
                )
            continue
        try:
            scanned += 1
            segments, skipped_count = loaded
            zero_range_skipped += skipped_count

            # A data break terminates projection from older segments. We still
            # evaluate them so valid formation can continue on both sides, but
            # only zones from the latest continuous segment can be active.
            for historical_segment in segments[:-1]:
                zones_ended_at_data_break += len(
                    _zone_engine.detect_zones(historical_segment)
                )

            data = segments[-1]
            current_price = float(data["Close"].iloc[-1])
            zones = _zone_engine.detect_zones(data)
            canonical_zone_count += len(zones)
            qualifications = {
                zone.created_index: _dashboard_qualification.qualify(
                    zone,
                    _TIMEFRAME_LABELS[timeframe],
                )
                for zone in zones
            }
            formation_qualified_count += sum(
                item.dashboard_qualified for item in qualifications.values()
            )
            for qualification in qualifications.values():
                if qualification.dashboard_qualified:
                    continue
                for reason in qualification.qualification_reason_codes:
                    if reason in {
                        "WEAK_DEPARTURE",
                        "BASE_TOO_LONG_FOR_PRIMARY_DASHBOARD",
                        "MULTI_BASE_EXECUTION_ZONE",
                        "INSUFFICIENT_DISPLACEMENT",
                        "POOR_DIRECTIONAL_CLOSE",
                        "MALFORMED_OR_INCOMPLETE_EVIDENCE",
                        "DRIFTING_DEPARTURE",
                        "NO_EXPLOSIVE_OR_STRONG_SEQUENCE",
                        "CLOSING_RULE_FAILED",
                    }:
                        qualification_rejection_counts[reason] = (
                            qualification_rejection_counts.get(reason, 0) + 1
                        )
            canonical_metadata = _zone_lifecycle_ui.evaluate(
                zones,
                data,
                symbol=symbol,
                timeframe=_TIMEFRAME_LABELS[timeframe],
                current_price=current_price,
            )
            # Canonical detection and persisted-zone rehydration intentionally
            # converge here.  The reusable service owns all downstream
            # lifecycle, qualification, Zone Quality and response enrichment.
            enriched_batch = _zone_result_enrichment.enrich(
                zones=zones,
                data=data,
                symbol=symbol,
                timeframe=_TIMEFRAME_LABELS[timeframe],
                current_price=current_price,
            )
            formation_qualified_count += enriched_batch.formation_qualified_count
            dashboard_qualified_count += enriched_batch.dashboard_qualified_count
            for reason, count in enriched_batch.qualification_rejection_counts.items():
                qualification_rejection_counts[reason] = (
                    qualification_rejection_counts.get(reason, 0) + count
                )
            results.extend(enriched_batch.active)
            historical_results.extend(enriched_batch.historical)
            dashboard_base_preferences.update(
                {(symbol, index): rank for index, rank in enriched_batch.base_preferences.items()}
            )
            # The retained block below is summary compatibility code.  It must
            # not create a second response-enrichment path.
            response_enrichment_zones = zones
            zones = []
            for detected_zone in zones:
                metadata = canonical_metadata.get(detected_zone.created_index)
                if metadata is None:
                    continue
                counts = summary[detected_zone.zone_type.value]
                counts["total"] += 1
                if metadata.test_count == 0 and metadata.lifecycle_status not in (
                    "INVALIDATED",
                    "REMOVED",
                ):
                    counts["fresh"] += 1
                if metadata.lifecycle_status == "REACTING":
                    counts["reacting"] += 1
                if metadata.test_count == 1:
                    counts["tested"] += 1
                if metadata.test_count >= 2:
                    counts["retested"] += 1
                if metadata.lifecycle_status in ("INVALIDATED", "REMOVED"):
                    counts["invalidated"] += 1
                if metadata.authenticity_status == "AUTHENTIC":
                    counts["authentic"] += 1
                else:
                    counts["non_authentic"] += 1
                qualification = qualifications[detected_zone.created_index]
                if qualification.dashboard_qualified:
                    if metadata.dashboard_lifecycle_eligible:
                        dashboard_qualified_count += 1
                    else:
                        reason = metadata.dashboard_lifecycle_reason_code
                        qualification_rejection_counts[reason] = (
                            qualification_rejection_counts.get(reason, 0) + 1
                        )
            formation_dashboard_zones = [
                item
                for item in sorted(
                    zones,
                    key=lambda zone: zone.created_index,
                    reverse=True,
                )
                if qualifications[item.created_index].dashboard_qualified
            ]
            dashboard_zones = [
                item
                for item in formation_dashboard_zones
                if canonical_metadata[item.created_index].dashboard_lifecycle_eligible
            ][:4]
            historical_dashboard_zones = [
                item
                for item in formation_dashboard_zones[:4]
                if canonical_metadata[item.created_index].is_invalidated
                and item not in dashboard_zones
            ]
            for detected_zone in dashboard_zones + historical_dashboard_zones:
                qualification = qualifications[detected_zone.created_index]
                zone = detected_zone
                metadata = canonical_metadata.get(detected_zone.created_index)
                invalidated = bool(metadata and metadata.is_invalidated)
                if invalidated:
                    status = "INVALIDATED"
                    distance = 0.0
                elif metadata and metadata.dashboard_lifecycle_reason_code == (
                    "LIFECYCLE_REACTING"
                ):
                    status = "REACTING"
                    proximal = (
                        zone.upper_price
                        if zone.zone_type == ZoneType.DEMAND
                        else zone.lower_price
                    )
                    distance = abs(current_price - proximal) / current_price * 100
                elif zone.lower_price <= current_price <= zone.upper_price:
                    distance = 0.0
                    status = "IN ZONE"
                elif current_price > zone.upper_price:
                    distance = (current_price - zone.upper_price) / current_price * 100
                    status = "APPROACHING" if distance <= 5 else "WATCH"
                else:
                    distance = (zone.lower_price - current_price) / current_price * 100
                    status = "APPROACHING" if distance <= 5 else "WATCH"

                quality_context = ZoneQualityContext(
                    lifecycle_status=(metadata.lifecycle_status if metadata else None),
                    is_fresh=(metadata.is_fresh if metadata else None),
                    penetration_percent=(
                        metadata.current_penetration_percent if metadata else None
                    ),
                    max_penetration_percent=(
                        metadata.max_penetration_percent if metadata else None
                    ),
                    authenticity_status=(
                        metadata.authenticity_status if metadata else None
                    ),
                )
                zone_score = _zone_scoring_engine.score(
                    [zone], {zone.created_index: quality_context}
                ).scored_zones[0]
                explanation = ZoneExplanationService.build(zone, zone_score)
                gap_type = _canonical_gap_type(zone)
                demand = zone.zone_type.value == "DEMAND"
                evidence = (
                    (
                        "Fresh: price has not retested the zone after formation."
                        if metadata and metadata.is_fresh
                        else (
                            f"Tested: {metadata.test_count if metadata else 0} "
                            "distinct post-formation visit(s) "
                            "reduce quality."
                        )
                    ),
                    (
                        "Departure quality contribution: "
                        f"{zone_score.departure_quality_score:.1f}/30."
                    ),
                    (
                        "Leg-Out dominance contribution: "
                        f"{zone_score.legout_dominance_score:.1f}/15."
                    ),
                    (
                        "Structural clearance contribution: "
                        f"{zone_score.structural_clearance_score:.1f}/15."
                    ),
                    (
                        "This quality score is rule-based and is not a "
                        "probability that the zone will hold."
                    ),
                    (
                        f"Departure includes a confirmed {gap_type.lower()}."
                        if gap_type
                        else "No non-overlapping departure gap was detected."
                    ),
                )
                response = ZoneResearchResultResponse(
                    symbol=symbol,
                    zone_type=zone.zone_type.value,
                    pattern_type=zone.pattern_type,
                    gap_type=gap_type,
                    proximal_price=zone.upper_price if demand else zone.lower_price,
                    distal_price=zone.lower_price if demand else zone.upper_price,
                    distance_percent=round(distance, 2),
                    zone_score=round(zone_score.total_score, 1),
                    freshness_score=round(zone_score.freshness_score, 1),
                    strength_score=round(zone_score.strength_score, 1),
                    touch_score=round(zone_score.touch_score, 1),
                    merge_score=round(zone_score.merge_bonus, 1),
                    raw_zone_score=round(zone_score.raw_score, 1),
                    quality_cap=round(zone_score.quality_cap, 1),
                    zone_quality_label=zone_score.label,
                    zone_quality_components={
                        component.key: round(component.score, 2)
                        for component in zone_score.components
                    },
                    zone_quality_component_details=tuple(
                        ZoneQualityComponentResponse(
                            key=component.key,
                            score=round(component.score, 2),
                            maximum_score=round(component.maximum_score, 2),
                            evidence=component.evidence,
                            reason_codes=component.reason_codes,
                        )
                        for component in zone_score.components
                    ),
                    zone_quality_reason_codes=zone_score.reason_codes,
                    is_fresh=(metadata.is_fresh if metadata else False),
                    touch_count=(metadata.test_count if metadata else 0),
                    merged_count=zone.merged_count,
                    evidence=evidence,
                    explanation=ZoneExplanationResponse(
                        overall_score=explanation.overall_score,
                        rating=explanation.rating,
                        label=explanation.label,
                        summary=explanation.summary,
                        positive_factors=tuple(
                            ZoneExplanationFactorResponse(
                                key=factor.key,
                                title=factor.title,
                                score=factor.score,
                                sentiment=factor.sentiment,
                                summary=factor.summary,
                                recommendation=factor.recommendation,
                                weight=factor.weight,
                            )
                            for factor in explanation.positive_factors
                        ),
                        negative_factors=tuple(
                            ZoneExplanationFactorResponse(
                                key=factor.key,
                                title=factor.title,
                                score=factor.score,
                                sentiment=factor.sentiment,
                                summary=factor.summary,
                                recommendation=factor.recommendation,
                                weight=factor.weight,
                            )
                            for factor in explanation.negative_factors
                        ),
                        educational_insight=(explanation.educational_insight),
                    ),
                    current_price=current_price,
                    timeframe=_TIMEFRAME_LABELS[timeframe],
                    base_index=zone.created_index,
                    base_date=data.index[zone.created_index].date().isoformat(),
                    status=status,
                    reaction_percent=(
                        metadata.reaction_percentage if metadata else None
                    ),
                    reaction_started=None,
                    reaction_ended=None,
                    reaction_duration_candles=None,
                    zone_id=metadata.zone_id if metadata else None,
                    lifecycle_status=(metadata.lifecycle_status if metadata else None),
                    authenticity_status=(
                        metadata.authenticity_status if metadata else None
                    ),
                    authenticity_reason_code=(
                        metadata.authenticity_reason_code if metadata else None
                    ),
                    authenticity_reason=(
                        metadata.authenticity_reason if metadata else None
                    ),
                    test_count=(metadata.test_count if metadata else zone.touch_count),
                    reaction_status=(metadata.reaction_status if metadata else None),
                    reaction_percentage=(
                        metadata.reaction_percentage if metadata else None
                    ),
                    max_penetration_percent=(
                        metadata.max_penetration_percent if metadata else None
                    ),
                    current_penetration_percent=(
                        metadata.current_penetration_percent if metadata else None
                    ),
                    good_closing=(metadata.good_closing if metadata else None),
                    parent_zone_id=(metadata.parent_zone_id if metadata else None),
                    is_nested=(metadata.is_nested if metadata else False),
                    is_duplicate=(metadata.is_duplicate if metadata else False),
                    overlap_percent=(metadata.overlap_percent if metadata else None),
                    dashboard_qualified=(
                        metadata.dashboard_lifecycle_eligible if metadata else False
                    ),
                    qualification_reason_codes=(
                        qualification.qualification_reason_codes
                        + (metadata.dashboard_lifecycle_reason_code,)
                        if metadata
                        else qualification.qualification_reason_codes
                    ),
                    departure_quality=qualification.departure_quality,
                    canonical_formation_departure=(
                        zone.formation_evidence.departure_strength.value
                        if zone.formation_evidence
                        else None
                    ),
                    dashboard_qualification_departure=qualification.departure_quality,
                    base_quality=qualification.base_quality,
                    formation_quality=qualification.formation_quality,
                    departure_displacement=(qualification.departure_displacement),
                    departure_zone_width_ratio=(
                        qualification.departure_zone_width_ratio
                    ),
                    base_candle_count=qualification.base_candle_count,
                    base_compactness=qualification.base_compactness,
                    base_compactness_reason=(qualification.base_compactness_reason),
                )
                dashboard_base_preferences[(symbol, zone.created_index)] = (
                    qualification.base_preference_rank
                )
                if invalidated:
                    historical_results.append(response)
                else:
                    results.append(response)
            # Summary-only accounting still needs the original directional
            # canonical zones; response rows were built above by the shared
            # enrichment service.
            for detected_zone in response_enrichment_zones:
                metadata = canonical_metadata.get(detected_zone.created_index)
                if metadata is None:
                    continue
                counts = summary[detected_zone.zone_type.value]
                counts["total"] += 1
                if metadata.test_count == 0 and metadata.lifecycle_status not in ("INVALIDATED", "REMOVED"):
                    counts["fresh"] += 1
                if metadata.lifecycle_status == "REACTING":
                    counts["reacting"] += 1
                if metadata.test_count == 1:
                    counts["tested"] += 1
                if metadata.test_count >= 2:
                    counts["retested"] += 1
                if metadata.lifecycle_status in ("INVALIDATED", "REMOVED"):
                    counts["invalidated"] += 1
                if metadata.authenticity_status == "AUTHENTIC":
                    counts["authentic"] += 1
                else:
                    counts["non_authentic"] += 1
        except Exception:
            pass
        if durable_job_id is not None and (
            position % 10 == 0 or position == len(universe_symbols)
        ):
            _persistent_scanner_store.update_job(
                durable_job_id,
                "RUNNING",
                processed=position,
                failed=load_failures_seen,
            )

    def dashboard_sort_key(
        item: ZoneResearchResultResponse,
    ) -> tuple[float, float, int]:
        return (
            item.distance_percent,
            -item.zone_score,
            dashboard_base_preferences.get((item.symbol, item.base_index), 99),
        )

    results.sort(key=dashboard_sort_key)
    historical_results.sort(key=dashboard_sort_key)
    analysis_completed = perf_counter()
    # Enrich the completed scanner batch with promoted canonical Trade Confidence
    # here so the browser never launches one context request per table row.
    # A shared refresh key ties all values to this completed market snapshot;
    # MarketDataService reuses OHLC datasets for zones sharing a symbol/frame.
    confidence_snapshot = datetime.now(UTC).isoformat()

    def enrich_symbol_rows(
        rows: list[tuple[int, ZoneResearchResultResponse]],
    ) -> list[tuple[int, ZoneResearchResultResponse]]:
        enriched: list[tuple[int, ZoneResearchResultResponse]] = []
        for index, item in rows:
            try:
                confidence = _canonical_trade_confidence_for_row(
                    item,
                    refresh_key=confidence_snapshot,
                )
            except Exception:
                logger.exception(
                    "Shadow Trade Confidence enrichment failed for %s %s.",
                    item.symbol,
                    item.zone_id or item.base_index,
                )
                confidence = None
            enriched.append(
                (index, item.model_copy(update={"trade_confidence": confidence}))
            )
        return enriched

    rows_by_symbol: dict[str, list[tuple[int, ZoneResearchResultResponse]]] = {}
    for index, item in enumerate(results):
        rows_by_symbol.setdefault(item.symbol, []).append((index, item))
    enriched_rows: list[ZoneResearchResultResponse | None] = [None] * len(results)
    if rows_by_symbol:
        with ThreadPoolExecutor(
            max_workers=min(8, len(rows_by_symbol)),
            thread_name_prefix="trade-confidence",
        ) as confidence_executor:
            futures = [
                confidence_executor.submit(enrich_symbol_rows, rows)
                for rows in rows_by_symbol.values()
            ]
            for future in futures:
                for index, item in future.result():
                    enriched_rows[index] = item
        results = [item for item in enriched_rows if item is not None]
    enrichment_completed = perf_counter()
    logger.info(
        "Zone scan phase timing: symbols=%s load_seconds=%.3f "
        "analysis_seconds=%.3f confidence_seconds=%.3f total_seconds=%.3f.",
        len(universe_symbols),
        load_completed - scan_started,
        analysis_completed - load_completed,
        enrichment_completed - analysis_completed,
        enrichment_completed - scan_started,
    )
    logger.info(
        "Zone scan continuity summary: symbols=%s scanned=%s failed=%s "
        "zones=%s zero_range_skipped=%s zones_ended_at_data_break=%s "
        "invalid_candle_candidates_evaluated=0.",
        len(universe_symbols),
        scanned,
        len(universe_symbols) - scanned,
        len(results),
        zero_range_skipped,
        zones_ended_at_data_break,
    )
    return ZoneResearchResponse(
        total_scanned=scanned,
        total_zones=len(results),
        timeframe=_TIMEFRAME_LABELS[timeframe],
        results=tuple(results),
        historical_results=tuple(historical_results),
        universe=universe,
        status="completed",
        total_symbols=len(universe_symbols),
        processed_symbols=scanned,
        failed_symbols=len(universe_symbols) - scanned,
        last_completed_at=datetime.now(UTC).isoformat(),
        data_status="delayed",
        lifecycle_summary=ZoneLifecycleSummaryResponse(
            demand=ZoneStateCountResponse(**summary["DEMAND"]),
            supply=ZoneStateCountResponse(**summary["SUPPLY"]),
        ),
        canonical_zone_count=canonical_zone_count,
        formation_qualified_count=formation_qualified_count,
        dashboard_qualified_count=dashboard_qualified_count,
        dashboard_rejected_count=(canonical_zone_count - dashboard_qualified_count),
        qualification_rejection_counts=qualification_rejection_counts,
    )


def _zone_scan_key(
    timeframe: str,
    universe: str,
    symbols: list[str] | None,
) -> str:
    return (
        f"{timeframe}:{universe}:{','.join(sorted(symbols or []))}:"
        f"{SCANNER_METHODOLOGY_CACHE_VERSION}:v7d-batch-trade-confidence"
    )


def _store_zone_scan(key: str, future: Future[ZoneResearchResponse]) -> None:
    with _zone_scan_lock:
        _zone_scan_jobs.pop(key, None)
        _zone_scan_progress.pop(key, None)
        try:
            _zone_scan_cache[key] = (monotonic(), future.result())
        except Exception:
            return


def _run_persistent_zone_scan(
    timeframe: str,
    universe: str,
    symbols: list[str] | None,
    key: str,
    job_id: int,
    *,
    refresh_market_data: bool = True,
) -> ZoneResearchResponse:
    """Run the unchanged canonical scan and atomically publish its exact payload."""

    universe_symbols = _universe_service.get_symbols(universe, symbols)
    lease_owner = f"scanner-{uuid4()}"
    if not _persistent_scanner_store.claim_job(job_id, lease_owner):
        raise RuntimeError("Scanner refresh is already owned by another worker.")
    snapshot_id = _persistent_scanner_store.begin_snapshot(
        universe=universe,
        timeframe=timeframe,
        methodology_version=SCANNER_METHODOLOGY_CACHE_VERSION,
        symbols=symbols,
        total_symbols=len(universe_symbols),
        storage_version=_snapshot_storage_version(timeframe),
    )
    try:
        response = _scan_research_zones_resumable(
            timeframe, universe, symbols, key, durable_job_id=job_id,
            lease_owner=lease_owner,
            refresh_market_data=refresh_market_data,
        )
        _persistent_scanner_store.publish(snapshot_id, response)
        _persistent_scanner_store.update_job(
            job_id,
            "COMPLETE",
            processed=response.processed_symbols,
            failed=response.failed_symbols,
            owner=lease_owner,
        )
        _persistent_scanner_store.release_job_lease(job_id, lease_owner)
        if timeframe == "DAILY" and universe == "allnse":
            _persistent_scanner_store.mark_materializations_stale(
                "allnse", _CORE_DERIVED_TIMEFRAMES
            )
            start_core_timeframe_preparation()
        return response
    except Exception as error:
        _persistent_scanner_store.fail(snapshot_id, str(error))
        _persistent_scanner_store.update_job(
            job_id,
            "RETRYABLE",
            error=str(error),
            owner=lease_owner,
        )
        _persistent_scanner_store.release_job_lease(job_id, lease_owner)
        raise


def _merge_symbol_responses(
    *,
    timeframe: ZoneTimeframe,
    universe: UniverseName,
    expected_symbols: int,
    responses: list[ZoneResearchResponse],
    failed: int,
) -> ZoneResearchResponse:
    """Assemble exact completed symbol checkpoints into one publishable snapshot."""

    results = [item for response in responses for item in response.results]
    historical = [
        item for response in responses for item in response.historical_results
    ]
    # Canonical contextual ranking is already embedded in each row. Preserve the
    # existing Dashboard ordering semantics used before persistent pagination.

    def sort_key(item: ZoneResearchResultResponse) -> tuple[float, float, str]:
        return (item.distance_percent, -item.zone_score, item.zone_id or "")
    results.sort(key=sort_key)
    historical.sort(key=sort_key)
    summary_keys = (
        "total", "fresh", "reacting", "tested", "retested", "invalidated",
        "authentic", "non_authentic",
    )
    summary = {
        direction: {key: 0 for key in summary_keys}
        for direction in ("demand", "supply")
    }
    rejection_counts: dict[str, int] = {}
    for response in responses:
        if response.lifecycle_summary:
            for direction in ("demand", "supply"):
                values = getattr(response.lifecycle_summary, direction)
                for field in summary_keys:
                    summary[direction][field] += int(getattr(values, field))
        for reason, count in response.qualification_rejection_counts.items():
            rejection_counts[reason] = rejection_counts.get(reason, 0) + count
    now = datetime.now(UTC).isoformat()
    return ZoneResearchResponse(
        total_scanned=sum(item.total_scanned for item in responses),
        total_zones=len(results),
        timeframe=_TIMEFRAME_LABELS[timeframe],
        results=tuple(results),
        historical_results=tuple(historical),
        universe=universe,
        status="completed",
        total_symbols=expected_symbols,
        processed_symbols=len(responses),
        failed_symbols=failed,
        last_completed_at=now,
        data_status="delayed",
        lifecycle_summary=ZoneLifecycleSummaryResponse(
            demand=ZoneStateCountResponse(**summary["demand"]),
            supply=ZoneStateCountResponse(**summary["supply"]),
        ),
        canonical_zone_count=sum(item.canonical_zone_count for item in responses),
        formation_qualified_count=sum(
            item.formation_qualified_count for item in responses
        ),
        dashboard_qualified_count=sum(
            item.dashboard_qualified_count for item in responses
        ),
        dashboard_rejected_count=sum(
            item.dashboard_rejected_count for item in responses
        ),
        qualification_rejection_counts=rejection_counts,
    )


def _scan_research_zones_resumable(
    timeframe: ZoneTimeframe,
    universe: UniverseName,
    symbols: list[str] | None,
    progress_key: str | None,
    durable_job_id: int,
    lease_owner: str,
    refresh_market_data: bool = True,
) -> ZoneResearchResponse:
    """Checkpoint canonical output per symbol and resume unchanged revisions."""

    universe_symbols = _universe_service.get_symbols(universe, symbols)
    derived_from_daily = timeframe in _CORE_DERIVED_TIMEFRAMES
    source_period, source_interval = _INTRADAY_SOURCE.get(
        timeframe,
        (
            DAILY_HISTORY_PERIOD if derived_from_daily else _zone_config.period,
            DAILY_SOURCE_INTERVAL if derived_from_daily else _zone_config.interval,
        ),
    )
    completed: list[ZoneResearchResponse] = []
    terminal_failures = 0
    retryable_failures = 0
    resumed = 0

    # Yahoo multi-ticker requests materially reduce both bootstrap and refresh
    # round trips. Existing instruments receive a bounded correction overlap;
    # new instruments retain the full canonical source period. The durable
    # merge revision then determines which symbol checkpoints need recalculation.
    missing = {
        symbol for symbol in universe_symbols
        if not _zone_market_data.has_persisted_data(symbol, source_interval)
    }
    provider_batches = (
        ()
        if derived_from_daily or not refresh_market_data
        else range(0, len(universe_symbols), 50)
    )
    for start in provider_batches:
        batch = universe_symbols[start:start + 50]
        batch_period = source_period
        if source_interval == "1d" and not any(symbol in missing for symbol in batch):
            batch_period = "1mo"
        try:
            _zone_market_data.prefetch_stock_data_batch(
                batch, period=batch_period, interval=source_interval
            )
        except Exception:
            logger.exception(
                "Provider batch refresh failed for %s..%s; using durable candles.",
                start, start + len(batch),
            )

    def process(symbol: str) -> tuple[ZoneResearchResponse | None, bool, bool]:
        revision = ""
        try:
            # The bounded bootstrap above owns provider I/O. Canonical work reads
            # the durable snapshot so a large-universe build cannot regress into
            # thousands of serial provider refreshes.
            _zone_market_data.load_persisted_segments(
                symbol=symbol, period=source_period, interval=source_interval
            )
            revision = (
                _zone_market_data.persisted_revision(symbol, source_interval)
                or "volatile"
            )
            cached = _persistent_scanner_store.symbol_checkpoint(
                instrument_id=f"NSE:{symbol}",
                timeframe=timeframe,
                methodology_version=SCANNER_METHODOLOGY_CACHE_VERSION,
                market_data_revision=revision,
            )
            if cached is not None:
                return cached, True, False
            response = _scan_research_zones(timeframe, "custom", [symbol])
            _persistent_scanner_store.save_symbol_checkpoint(
                instrument_id=f"NSE:{symbol}", timeframe=timeframe,
                methodology_version=SCANNER_METHODOLOGY_CACHE_VERSION,
                market_data_revision=revision, response=response,
            )
            return response, False, False
        except Exception as error:
            message = str(error).lower()
            retryable = not (
                "no valid candles" in message
                or "no valid market-data segments" in message
                or "insufficient history" in message
            )
            _persistent_scanner_store.fail_symbol_checkpoint(
                instrument_id=f"NSE:{symbol}", timeframe=timeframe,
                methodology_version=SCANNER_METHODOLOGY_CACHE_VERSION,
                market_data_revision=revision or "unavailable", error=str(error),
                retryable=retryable,
            )
            logger.exception("Resumable scanner failed for %s %s.", symbol, timeframe)
            return None, False, retryable
        finally:
            _zone_market_data.release_symbol_cache(symbol)

    workers = min(max(1, _zone_config.scan_concurrency), 8, len(universe_symbols))
    with ThreadPoolExecutor(
        max_workers=workers,
        thread_name_prefix="canonical-symbol",
    ) as executor:
        for position, (response, was_resumed, retryable) in enumerate(
            executor.map(process, universe_symbols), start=1
        ):
            if response is None:
                if retryable:
                    retryable_failures += 1
                else:
                    terminal_failures += 1
            else:
                completed.append(response)
                resumed += int(was_resumed)
            _persistent_scanner_store.update_job(
                durable_job_id, "RUNNING", processed=position,
                failed=terminal_failures + retryable_failures,
                owner=lease_owner,
            )
            if position % 10 == 0 or position == len(universe_symbols):
                if not _persistent_scanner_store.heartbeat_job(
                    durable_job_id, lease_owner
                ):
                    raise RuntimeError("Scanner worker lease was lost.")
            if progress_key:
                with _zone_scan_lock:
                    _zone_scan_progress[progress_key] = (
                        position,
                        terminal_failures + retryable_failures,
                    )
    logger.info(
        "Resumable scan checkpoint summary: universe=%s timeframe=%s "
        "completed=%s resumed=%s failed=%s.",
        universe, timeframe, len(completed), resumed,
        terminal_failures + retryable_failures,
    )
    if retryable_failures:
        raise RuntimeError(
            "Scanner build remains incomplete: "
            f"{retryable_failures} symbol(s) are retryable."
        )
    return _merge_symbol_responses(
        timeframe=timeframe, universe=universe,
        expected_symbols=len(universe_symbols), responses=completed,
        failed=terminal_failures,
    )


def _prepare_allnse_core_timeframes() -> None:
    """Bootstrap and materialize the broadest verified equity universe."""

    universe = _PRIMARY_PERSISTED_UNIVERSE
    symbols = _universe_service.get_symbols(universe)
    for attempt in range(3):
        for start in range(0, len(symbols), 50):
            batch = symbols[start:start + 50]
            try:
                _zone_market_data.bootstrap_daily_history_batch(
                    batch,
                    period=DAILY_HISTORY_PERIOD,
                    semantics_version=DAILY_SOURCE_SEMANTICS_VERSION,
                    final_attempt=attempt == 2,
                )
            except Exception:
                logger.exception(
                    "Daily source bootstrap failed for All NSE batch %s..%s.",
                    start, start + len(batch),
                )
    progress = _zone_market_data.daily_bootstrap_progress(
        period=DAILY_HISTORY_PERIOD,
        semantics_version=DAILY_SOURCE_SEMANTICS_VERSION,
        universe=universe,
    )
    resolved = progress.get("COMPLETE", 0) + progress.get("FAILED", 0)
    if resolved < len(symbols):
        logger.warning(
            "Core timeframe preparation paused: Daily source %s/%s complete.",
            progress.get("COMPLETE", 0), len(symbols),
        )
        return
    daily_revision = (
        _zone_market_data.persisted_universe_revision(DAILY_SOURCE_INTERVAL)
        or "unavailable"
    )

    def materialize(timeframe: str) -> None:
        state = _persistent_scanner_store.materialization_states(universe).get(
            timeframe
        )
        compatible = _persistent_scanner_store.latest_complete(
            universe=universe, timeframe=timeframe,
            methodology_version=SCANNER_METHODOLOGY_CACHE_VERSION,
            symbols=None,
            storage_version=_snapshot_storage_version(timeframe),
        )
        if compatible is not None and state == "READY":
            return
        key = _zone_scan_key(timeframe, universe, None)
        job_id = _persistent_scanner_store.create_job(
            universe, timeframe, SCANNER_METHODOLOGY_CACHE_VERSION,
            len(symbols),
            source_revision=(
                f"{DAILY_SOURCE_SEMANTICS_VERSION}:{daily_revision}"
            ),
        )
        try:
            response = _run_persistent_zone_scan(
                timeframe, universe, None, key, job_id,
                refresh_market_data=False,
            )
            with _zone_scan_lock:
                _zone_scan_cache[key] = (monotonic(), response)
        except Exception:
            logger.exception("Background %s materialization failed.", timeframe)

    # SQLite publishes one immutable snapshot at a time. A single worker avoids
    # cross-materialization write contention while symbol checkpoints preserve
    # restart/resume behavior.
    with ThreadPoolExecutor(
        max_workers=1, thread_name_prefix="core-eod-materialization"
    ) as executor:
        list(executor.map(materialize, _CORE_EOD_TIMEFRAMES))


def start_core_timeframe_preparation() -> None:
    """Recover interrupted jobs and launch one bounded coordinator."""

    global _core_preparation_future
    recovered = _persistent_scanner_store.recover_expired_jobs()
    if recovered:
        logger.info("Recovered %s expired scanner job(s).", recovered)
    if os.getenv("ALPHAEDGE_BACKGROUND_PREPARATION", "1") == "0":
        return
    if os.getenv("PYTEST_CURRENT_TEST"):
        return
    with _zone_scan_lock:
        if _core_preparation_future and not _core_preparation_future.done():
            return
        _core_preparation_future = _core_preparation_executor.submit(
            _prepare_allnse_core_timeframes
        )


@scanner_router.get("/instruments/search")
def search_instruments(
    q: str = Query(..., min_length=1, max_length=80),
    limit: int = Query(default=10, ge=1, le=25),
) -> dict[str, object]:
    """Search active instruments independently of scanner-zone results."""

    return {
        "query": q,
        "results": (
            _dhan_shadow_store.search_current_instruments(q, limit)
            if MARKET_DATA_PROVIDER == "dhan"
            else _instrument_master.search(q, limit)
        ),
    }


@scanner_router.get("/instruments/metadata")
def get_instrument_master_metadata() -> dict[str, object]:
    """Expose the broadest verified, provider-addressable equity master."""

    symbols = _universe_service.get_symbols(_PRIMARY_PERSISTED_UNIVERSE)
    return {
        "universe": _PRIMARY_PERSISTED_UNIVERSE,
        "display_name": "All Supported Indian Equity",
        "scope": "NSE Main and NSE SME; BSE requires a licensed provider master",
        "active_count": len(symbols),
        "provider_coverage": _instrument_master.provider_coverage_summary(
            _PRIMARY_PERSISTED_UNIVERSE
        ),
        "latest_sync": _instrument_master.latest_sync(
            _PRIMARY_PERSISTED_UNIVERSE
        ),
        "sme_included": bool(
            _instrument_master.active_symbols("nse_sme")
        ),
        "etf_included": False,
        "coverage": _instrument_master.coverage_capabilities(),
    }


@scanner_router.post("/instruments/synchronize")
def synchronize_instrument_master() -> dict[str, object]:
    """Atomically refresh NSE Main Equity while preserving last-known-good data."""

    try:
        return _instrument_master.synchronize_from_nse()
    except Exception as error:
        logger.exception("NSE Main Equity synchronization failed.")
        raise HTTPException(
            status_code=503,
            detail=(
                "Instrument-master synchronization failed; the last-known-good "
                "master remains active."
            ),
        ) from error


@scanner_router.get("/capabilities")
def get_scanner_capabilities(
    universe: UniverseName = Query(default="allnse"),
) -> dict[str, object]:
    """Report only universes/timeframes backed by current configuration."""

    if MARKET_DATA_PROVIDER == "dhan":
        counts = _dhan_shadow_store.current_master_universe_counts(
            _dhan_index_constituents()
        )
        return {
            "architecture_version": SCANNER_ARCHITECTURE_VERSION,
            "storage_version": SCANNER_STORAGE_VERSION,
            "derived_eod_storage_version": DERIVED_EOD_STORAGE_VERSION,
            "methodology_version": SCANNER_METHODOLOGY_CACHE_VERSION,
            "universes": [
                {
                    "id": name,
                    "instrument_count": counts[name],
                    "state": "READY" if counts[name] else "UNAVAILABLE",
                }
                for name in _DHAN_DASHBOARD_UNIVERSES
            ],
            "timeframes": [
                {
                    "id": key,
                    "label": label,
                    "state": (
                        "READY"
                        if _dhan_shadow_store.latest_ready_dashboard_result_snapshot(
                            "dhan_all_supported_indian_equity", _TIMEFRAME_LABELS[key]
                        ) is not None
                        else "UNAVAILABLE"
                    ),
                    "category": (
                        "CORE_MATERIALIZED"
                        if key in {"DAILY", *_CORE_DERIVED_TIMEFRAMES}
                        else "INTRADAY_PROVIDER_DEPENDENT"
                    ),
                }
                for key, label in _TIMEFRAME_LABELS.items()
            ],
            "instrument_classes": {
                "nse_equities": "SUPPORTED",
                "bse_equities": "SUPPORTED",
                "indices": "Dhan-master intersected",
                "etfs": "EXCLUDED",
                "commodity_futures": "UNAVAILABLE",
                "commodity_spot": "UNAVAILABLE",
            },
            "market_coverage": [],
        }

    counts = _persistent_scanner_store.instrument_counts()
    default_states = _persistent_scanner_store.materialization_states(universe)
    market_coverage = _instrument_master.coverage_capabilities()
    coverage_states = {str(item["id"]): str(item["state"]) for item in market_coverage}
    timeframe_capabilities: list[dict[str, str]] = []
    for key, label in _TIMEFRAME_LABELS.items():
        state = default_states.get(key, "UNAVAILABLE")
        if universe == _PRIMARY_PERSISTED_UNIVERSE and key in _INTRADAY_TIMEFRAMES:
            # Yahoo's short rolling intraday history and retail throttling do
            # not qualify as trustworthy broad-market persisted coverage.
            state = "UNAVAILABLE"
        if (
            universe in {"allnse", _PRIMARY_PERSISTED_UNIVERSE}
            and key in _CORE_EOD_TIMEFRAMES
            and _persistent_scanner_store.latest_complete(
                universe=universe,
                timeframe=key,
                methodology_version=SCANNER_METHODOLOGY_CACHE_VERSION,
                symbols=None,
                storage_version=_snapshot_storage_version(key),
            ) is None
        ):
            state = "BUILDING"
        timeframe_capabilities.append({
            "id": key,
            "label": label,
            "state": state,
            "category": (
                "CORE_MATERIALIZED"
                if key in {"DAILY", *_CORE_DERIVED_TIMEFRAMES}
                else "INTRADAY_PROVIDER_DEPENDENT"
            ),
        })
    return {
        "architecture_version": SCANNER_ARCHITECTURE_VERSION,
        "storage_version": SCANNER_STORAGE_VERSION,
        "derived_eod_storage_version": DERIVED_EOD_STORAGE_VERSION,
        "methodology_version": SCANNER_METHODOLOGY_CACHE_VERSION,
        "universes": [
            {
                "id": name,
                "instrument_count": counts.get(name, 0),
                "state": (
                    coverage_states.get(name, "READY")
                ),
            }
            for name in (
                "nifty50", "nifty100", "nifty200", "nse500", "fno",
                "allnse", "nse_sme", "allindia",
            )
        ],
        "timeframes": timeframe_capabilities,
        "instrument_classes": {
            "nse_equities": "SUPPORTED",
            "fno_underlyings": "SUPPORTED",
            "bse_equities": "UNAVAILABLE",
            "indices": "LIMITED",
            "etfs": "PROVIDER_DEPENDENT",
            "commodity_futures": "UNAVAILABLE",
            "commodity_spot": "UNAVAILABLE",
        },
        "market_coverage": market_coverage,
    }


@scanner_router.get("/snapshot-status")
def get_scanner_snapshot_status() -> dict[str, object]:
    """Expose operational state without invoking market-data or canonical engines."""

    source_progress = _zone_market_data.daily_bootstrap_progress(
        period=DAILY_HISTORY_PERIOD,
        semantics_version=DAILY_SOURCE_SEMANTICS_VERSION,
        universe=_PRIMARY_PERSISTED_UNIVERSE,
    )
    return {
        "architecture_version": SCANNER_ARCHITECTURE_VERSION,
        "storage_version": SCANNER_STORAGE_VERSION,
        "derived_eod_storage_version": DERIVED_EOD_STORAGE_VERSION,
        "methodology_version": SCANNER_METHODOLOGY_CACHE_VERSION,
        "snapshots": _persistent_scanner_store.status_counts(),
        "active_jobs": len(_zone_scan_jobs),
        "jobs": _persistent_scanner_store.latest_jobs(),
        "daily_source": {
            "semantics_version": DAILY_SOURCE_SEMANTICS_VERSION,
            "period": DAILY_HISTORY_PERIOD,
            "progress": source_progress,
        },
    }


@scanner_router.get("/dhan-runtime-status")
def get_dhan_runtime_status() -> dict[str, object]:
    """Operational status only; this endpoint never triggers scanning or downloads."""
    update = _dhan_shadow_store.incremental_update_status()
    run_status = str(update.get("status", "READY"))
    snapshots = _dhan_shadow_store.dashboard_snapshot_statuses(
        "dhan_all_supported_indian_equity"
    )
    has_ready_snapshot = any(
        str(snapshot.get("status")) == "READY"
        for snapshot in snapshots.values()
    )
    in_process_starting = _dhan_update_future is not None and not _dhan_update_future.done()
    if run_status in {"RUNNING", "CANCELLING"} and not in_process_starting:
        from backend.services.market_data.update_process_lock import update_process_is_active
        if not update_process_is_active(_dhan_shadow_store.path):
            # Report interrupted work without mutating state on a read request.
            update = {**update, "status": "FAILED", "stage": "Update interrupted",
                      "error": "INTERRUPTED_STALE_RUN"}
            run_status = "FAILED"
    if in_process_starting and run_status != "RUNNING":
        update = {**update, "status": "RUNNING", "stage": "Checking Dhan..."}
        run_status = "RUNNING"
    # A cancelled/failed refresh must never make existing atomic READY data
    # appear unavailable.  Only a live worker reports UPDATING.
    data_status = (
        "CANCELLING"
        if run_status == "CANCELLING"
        else "UPDATING"
        if run_status == "RUNNING"
        else "READY"
        if has_ready_snapshot
        else "FAILED"
    )
    return {
        "provider": "dhan",
        "data_status": data_status,
        "auth_status": DhanAuthenticationService.last_known_status(),
        "last_successful_update": (
            update.get("completed_at")
            if run_status == "READY"
            else _dhan_shadow_store.latest_successful_incremental_update_at()
        ),
        "latest_trading_date": update.get("latest_trading_date"),
        "last_update": update,
        "snapshots": snapshots,
    }


@scanner_router.post("/dhan-incremental-update/{run_id}/cancel")
def cancel_dhan_incremental_update(
    run_id: int,
    x_alphaedge_update_intent: str | None = Header(default=None),
) -> dict[str, object]:
    """Request graceful cancellation for the exact current explicit run."""
    if x_alphaedge_update_intent != "explicit-user":
        raise HTTPException(status_code=400, detail="Dhan cancellation requires an explicit user action.")
    active = _dhan_shadow_store.incremental_update_status()
    if int(active.get("run_id") or -1) != run_id:
        raise HTTPException(status_code=409, detail="This Dhan update is no longer active.")
    if str(active.get("status")) not in {"RUNNING", "CANCELLING"}:
        raise HTTPException(status_code=409, detail="This Dhan update cannot be cancelled.")
    if not _dhan_shadow_store.request_incremental_update_cancellation(run_id):
        raise HTTPException(status_code=409, detail="This Dhan update cannot be cancelled.")
    return {"status": "CANCELLING", "run_id": run_id, "message": "Cancelling update..."}


@scanner_router.post("/dhan-incremental-update")
def start_dhan_incremental_update(
    x_alphaedge_update_intent: str | None = Header(default=None),
) -> dict[str, object]:
    """Start an explicitly requested Dashboard Dhan update exactly once."""
    global _dhan_update_future
    if x_alphaedge_update_intent != "explicit-user":
        raise HTTPException(
            status_code=400,
            detail="Dhan updates require an explicit user action.",
        )
    if MARKET_DATA_PROVIDER != "dhan":
        raise HTTPException(status_code=409, detail="Dhan production provider is not active.")
    with _dhan_update_lock:
        active = _dhan_shadow_store.incremental_update_status()
        from backend.services.market_data.update_process_lock import update_process_is_active
        if (
            str(active.get("status")) in {"RUNNING", "CANCELLING"}
            and update_process_is_active(_dhan_shadow_store.path)
        ):
            return {
                "status": str(active["status"]),
                "run_id": active.get("run_id"),
                "message": str(active.get("stage") or "Dhan update is already running."),
            }
        if _dhan_update_future is not None and not _dhan_update_future.done():
            return {"status": "RUNNING", "message": "Checking Dhan..."}
        _dhan_update_future = _dhan_update_executor.submit(DhanIncrementalUpdateService().run)
        return {"status": "RUNNING", "message": "Checking Dhan..."}


@scanner_router.get("/persisted-zones")
def get_persisted_zone_page(
    timeframe: ZoneTimeframe = Query(default="DAILY"),
    universe: UniverseName = Query(default="allnse"),
    symbols: list[str] | None = Query(default=None),
    zone_type: str | None = Query(default=None),
    pattern: str | None = Query(default=None),
    min_zone_quality: float | None = Query(default=None, ge=0, le=100),
    min_trade_confidence: float | None = Query(default=None, ge=0, le=100),
    lifecycle: str | None = Query(default=None),
    status: str | None = Query(default=None),
    symbol: str | None = Query(default=None),
    max_distance: float | None = Query(default=None, ge=0),
    sort: str = Query(default="contextual_rank"),
    descending: bool = Query(default=False),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=500),
) -> dict[str, object]:
    """Query a completed snapshot with indexed filters and stable pagination."""

    # Dhan is source-isolated: a requested Dhan Dashboard never falls through
    # to Yahoo if its persisted result snapshot is not ready.
    if MARKET_DATA_PROVIDER == "dhan":
        dhan_timeframe = _TIMEFRAME_LABELS[timeframe]
        # Table-column names are intentionally UI-friendly; normalize them at
        # the Dhan persistence boundary rather than treating a valid sort as a
        # timeframe/materialization error.
        dhan_sort = _normalize_dhan_dashboard_sort(sort)
        snapshot = _dhan_shadow_store.latest_ready_dashboard_result_snapshot(
            "dhan_all_supported_indian_equity", dhan_timeframe
        )
        if snapshot is None:
            return {
                "state": "BUILDING", "provider": "dhan",
                "selected_timeframe": timeframe, "selected_universe": universe,
                "total": 0, "page": page, "page_size": page_size, "results": [],
                "processed_symbols": 0, "total_symbols": 0, "failed_symbols": 0,
            }
        try:
            constituents = _dhan_index_constituents()
            price_dependent_query = status is not None or max_distance is not None or dhan_sort in {
                "distance", "current_price",
            }
            total, rows = _dhan_shadow_store.query_dashboard_result_rows(
                int(snapshot["snapshot_id"]), zone_type=zone_type, pattern=pattern,
                min_zone_quality=min_zone_quality, min_trade_confidence=min_trade_confidence,
                status=None if price_dependent_query else status,
                symbol=symbol, max_distance=None if price_dependent_query else max_distance,
                sort=dhan_sort,
                descending=descending, page=page, page_size=page_size,
                universe=universe, universe_symbols=constituents.get(universe, ()),
            )
        except ValueError as error:
            raise HTTPException(status_code=422, detail=str(error)) from error
        # Price-dependent filters and sorts use the same response-time values
        # as the rendered table: overlay first, then global filter/sort/page.
        if price_dependent_query and total:
            _, all_rows = _dhan_shadow_store.query_dashboard_result_rows(
                int(snapshot["snapshot_id"]), zone_type=zone_type, pattern=pattern,
                min_zone_quality=min_zone_quality, min_trade_confidence=min_trade_confidence,
                status=None, symbol=symbol, max_distance=None, sort="symbol",
                descending=False, page=1, page_size=total,
                universe=universe, universe_symbols=constituents.get(universe, ()),
            )
            response_time_rows = _filter_dhan_response_time_rows(
                _overlay_dhan_current_prices(all_rows), status=status,
                max_distance=max_distance,
            )
            globally_sorted = _sort_dhan_response_time_rows(
                response_time_rows, field=dhan_sort, descending=descending,
            )
            total = len(globally_sorted)
            start = (page - 1) * page_size
            rendered_results = globally_sorted[start:start + page_size]
        else:
            rendered_results = _overlay_dhan_current_prices(rows)
        return {
            "state": "READY", "provider": "dhan", "selected_timeframe": timeframe,
            "selected_universe": universe, "snapshot_id": int(snapshot["snapshot_id"]),
            "last_completed_at": snapshot["completed_at"],
            "methodology_version": SCANNER_METHODOLOGY_CACHE_VERSION,
            "total": total, "page": page, "page_size": page_size,
            "results": rendered_results,
        }

    snapshot = _persistent_scanner_store.latest_complete(
        universe=universe,
        timeframe=timeframe,
        methodology_version=SCANNER_METHODOLOGY_CACHE_VERSION,
        symbols=symbols,
        storage_version=_snapshot_storage_version(timeframe),
    )
    materialization_state = _persistent_scanner_store.materialization_states(
        universe
    ).get(timeframe, "UNAVAILABLE")
    if snapshot is None:
        progress = _persistent_scanner_store.materialization_progress(
            universe, timeframe
        )
        if timeframe in _CORE_EOD_TIMEFRAMES:
            source = _zone_market_data.daily_bootstrap_progress(
                period=DAILY_HISTORY_PERIOD,
                semantics_version=DAILY_SOURCE_SEMANTICS_VERSION,
                universe=universe,
            )
            expected_source = len(_universe_service.get_symbols(universe, symbols))
            source_resolved = source.get("COMPLETE", 0) + source.get("FAILED", 0)
            if source_resolved < expected_source:
                progress = {
                    "total_instruments": expected_source,
                    "processed_instruments": source.get("COMPLETE", 0),
                    "failed_instruments": source.get("FAILED", 0)
                    + source.get("RETRYABLE", 0),
                }
        return {
            "state": (
                "BUILDING"
                if timeframe in _CORE_EOD_TIMEFRAMES
                else materialization_state
            ),
            "selected_timeframe": timeframe,
            "selected_universe": universe,
            "total": 0,
            "page": page,
            "page_size": page_size,
            "results": [],
            "processed_symbols": int(
                (progress or {}).get("processed_instruments", 0)
            ),
            "total_symbols": int(
                (progress or {}).get("total_instruments", 0)
            ),
            "failed_symbols": int(
                (progress or {}).get("failed_instruments", 0)
            ),
        }
    try:
        total, rows = _persistent_scanner_store.query_results(
            snapshot.snapshot_id,
            timeframe=_TIMEFRAME_LABELS[timeframe],
            zone_type=zone_type,
            pattern=pattern,
            min_zone_quality=min_zone_quality,
            min_trade_confidence=min_trade_confidence,
            lifecycle=lifecycle,
            status=status,
            symbol=symbol,
            max_distance=max_distance,
            sort=sort,
            descending=descending,
            page=page,
            page_size=page_size,
        )
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    return {
        "state": (
            "STALE" if materialization_state == "BUILDING"
            else materialization_state
            if materialization_state in {"STALE", "FAILED"}
            else "READY"
        ),
        "selected_timeframe": timeframe,
        "selected_universe": universe,
        "refresh_state": (
            "BUILDING" if materialization_state == "BUILDING" else None
        ),
        "snapshot_id": snapshot.snapshot_id,
        "last_completed_at": snapshot.completed_at,
        "methodology_version": SCANNER_METHODOLOGY_CACHE_VERSION,
        "total": total,
        "page": page,
        "page_size": page_size,
        "results": [
            ZoneResearchResultResponse.model_validate_json(row).model_dump()
            for row in rows
        ],
    }


@scanner_router.get("/zones", response_model=ZoneResearchResponse)
def get_research_zones(
    timeframe: ZoneTimeframe = Query(default="DAILY"),
    universe: UniverseName = Query(default="allnse"),
    symbols: list[str] | None = Query(default=None),
    include_results: bool = Query(default=True),
) -> ZoneResearchResponse:
    """Return cached results immediately and refresh scans in background."""

    universe_symbols = _universe_service.get_symbols(universe, symbols)
    key = _zone_scan_key(timeframe, universe, symbols)
    with _zone_scan_lock:
        cached_entry = _zone_scan_cache.get(key)
        if cached_entry is None:
            persisted = _persistent_scanner_store.latest_complete(
                universe=universe,
                timeframe=timeframe,
                methodology_version=SCANNER_METHODOLOGY_CACHE_VERSION,
                symbols=symbols,
                storage_version=_snapshot_storage_version(timeframe),
            )
            if persisted is not None:
                completed_at = datetime.fromisoformat(persisted.completed_at)
                if completed_at.tzinfo is None:
                    completed_at = completed_at.replace(tzinfo=UTC)
                persisted_age = max(
                    0.0,
                    (datetime.now(UTC) - completed_at).total_seconds(),
                )
                # Preserve wall-clock freshness across a process restart while
                # continuing to use monotonic time for this process.
                cached_entry = (monotonic() - persisted_age, persisted.response)
                _zone_scan_cache[key] = cached_entry
        job = _zone_scan_jobs.get(key)
        stale = (
            not cached_entry or monotonic() - cached_entry[0] >= _zone_scan_ttl_seconds
        )
        source_ready = True
        if timeframe in _CORE_DERIVED_TIMEFRAMES:
            source_progress = _zone_market_data.daily_bootstrap_progress(
                period=DAILY_HISTORY_PERIOD,
                semantics_version=DAILY_SOURCE_SEMANTICS_VERSION,
                universe=universe,
            )
            source_ready = source_progress.get("COMPLETE", 0) >= len(
                universe_symbols
            )
        if stale and job is None and source_ready:
            _zone_scan_progress[key] = (0, 0)
            job_id = _persistent_scanner_store.create_job(
                universe,
                timeframe,
                SCANNER_METHODOLOGY_CACHE_VERSION,
                len(universe_symbols),
                source_revision=(
                    f"{DAILY_SOURCE_SEMANTICS_VERSION}:{DAILY_HISTORY_PERIOD}"
                    if timeframe in _CORE_DERIVED_TIMEFRAMES
                    else "provider-refresh"
                ),
            )
            job = _zone_scan_executor.submit(
                _run_persistent_zone_scan,
                timeframe,
                universe,
                symbols,
                key,
                job_id,
            )
            _zone_scan_jobs[key] = job
            job.add_done_callback(
                lambda completed, cache_key=key: _store_zone_scan(
                    cache_key,
                    completed,
                )
            )
        if cached_entry:
            cached = cached_entry[1]
            processed, failed = (
                _zone_scan_progress.get(
                    key,
                    (cached.processed_symbols, cached.failed_symbols),
                )
                if job is not None
                else (cached.processed_symbols, cached.failed_symbols)
            )
            # Loading all symbol datasets is not scan completion: canonical
            # analysis, enrichment and cache publication still follow.  Never
            # display the misleading "500 / 500, refreshing" state.
            if job is not None and processed >= len(universe_symbols):
                processed = max(0, len(universe_symbols) - 1)
            response = cached.model_copy(
                update={
                    "status": "refreshing" if stale else "completed",
                    "data_status": "cached" if stale else cached.data_status,
                    "processed_symbols": processed,
                    "failed_symbols": failed,
                }
            )
            if not include_results:
                response = response.model_copy(
                    update={"results": (), "historical_results": ()}
                )
            return response
        processed, failed = _zone_scan_progress.get(key, (0, 0))
        if job is not None and processed >= len(universe_symbols):
            processed = max(0, len(universe_symbols) - 1)
        return ZoneResearchResponse(
            total_scanned=0,
            total_zones=0,
            timeframe=_TIMEFRAME_LABELS[timeframe],
            results=(),
            universe=universe,
            status="refreshing",
            total_symbols=len(universe_symbols),
            processed_symbols=processed,
            failed_symbols=failed,
            last_completed_at=None,
            data_status="refreshing",
        )


@scanner_router.get(
    "/zones/{symbol}/diagnostics",
    response_model=ZoneDiagnosticsResponse,
    include_in_schema=False,
)
def get_zone_diagnostics(
    symbol: str,
    timeframe: ZoneTimeframe = Query(default="DAILY"),
) -> ZoneDiagnosticsResponse:
    """Return developer-only candidate diagnostics for one symbol."""

    normalized = symbol.strip().upper()
    if normalized not in _universe_service.get_symbols("allnse"):
        raise HTTPException(
            status_code=404, detail="Symbol is not in the scanner universe."
        )
    source_period, source_interval = _INTRADAY_SOURCE.get(
        timeframe,
        (
            "10y" if timeframe != "DAILY" else _zone_config.period,
            _zone_config.interval,
        ),
    )
    validated = _zone_market_data.get_stock_data_segments(
        symbol=normalized,
        period=source_period,
        interval=source_interval,
    )
    segments = tuple(
        framed
        for segment in validated.segments
        if not (framed := _timeframe_data(segment, timeframe)).empty
    )
    if not segments:
        raise HTTPException(
            status_code=503,
            detail="No valid market-data segment is available for diagnostics.",
        )
    # Match production active-zone semantics: a data break terminates older
    # projection, so diagnostics inspect the latest valid continuous segment.
    data = segments[-1]
    accepted, candidates = _zone_engine.detect_zones_with_diagnostics(data)
    accepted_by_index = {zone.created_index: zone for zone in accepted}
    current_price = float(data["Close"].iloc[-1])
    canonical_metadata = _zone_lifecycle_ui.evaluate(
        accepted,
        data,
        symbol=normalized,
        timeframe=_TIMEFRAME_LABELS[timeframe],
        current_price=current_price,
    )
    response: list[ZoneCandidateDiagnosticResponse] = []
    for candidate in candidates:
        start = int(candidate["base_start_index"])
        end = int(candidate["base_end_index"])
        status = str(candidate["status"])
        reasons = list(candidate["rejection_reasons"])
        rules = list(candidate["rule_results"])
        score = candidate["score"]
        zone = accepted_by_index.get(end)
        if zone is not None:
            metadata = canonical_metadata[zone.created_index]
            score = round(
                _zone_scoring_engine.score(
                    [zone],
                    {
                        zone.created_index: ZoneQualityContext(
                            lifecycle_status=metadata.lifecycle_status,
                            is_fresh=metadata.is_fresh,
                            penetration_percent=metadata.current_penetration_percent,
                            max_penetration_percent=metadata.max_penetration_percent,
                            authenticity_status=metadata.authenticity_status,
                        )
                    },
                )
                .scored_zones[0]
                .total_score,
                1,
            )
            invalidated = metadata.is_invalidated
            completed_test = metadata.test_count > 0
            rules.extend(
                [
                    {
                        "key": "freshness",
                        "label": "Zone remains fresh",
                        "passed": metadata.is_fresh,
                        "actual": metadata.test_count,
                        "required": 0,
                    },
                    {
                        "key": "retest_count",
                        "label": "Retest count",
                        "passed": metadata.test_count == 0,
                        "actual": metadata.test_count,
                        "required": 0,
                    },
                    {
                        "key": "invalidation",
                        "label": "Canonical lifecycle remains active",
                        "passed": not invalidated,
                        "actual": "Invalidated" if invalidated else "Intact",
                        "required": "Intact",
                    },
                    {
                        "key": "completed_test",
                        "label": "Zone has not already completed a test",
                        "passed": not completed_test,
                        "actual": "Tested" if completed_test else "Untested",
                        "required": "Untested",
                    },
                ]
            )
            if invalidated:
                status = "invalidated"
                reasons.append("Canonical lifecycle invalidated this zone.")
            elif completed_test:
                status = "rejected"
                reasons.append(
                    "The zone already completed a test before the current candle."
                )
        response.append(
            ZoneCandidateDiagnosticResponse(
                candidate_id=str(candidate["candidate_id"]),
                symbol=normalized,
                timeframe=_TIMEFRAME_LABELS[timeframe],
                pattern=(
                    str(candidate["pattern"])
                    if candidate["pattern"] is not None
                    else None
                ),
                base_start_index=start,
                base_end_index=end,
                base_start_date=data.index[start].date().isoformat(),
                base_end_date=data.index[end].date().isoformat(),
                proximal=float(candidate["proximal"]),
                distal=float(candidate["distal"]),
                zone_type=(
                    str(candidate["zone_type"])
                    if candidate["zone_type"] is not None
                    else None
                ),
                status=status,
                score=float(score) if score is not None else None,
                rejection_reasons=tuple(reasons),
                rule_results=tuple(
                    ZoneRuleDiagnosticResponse(**rule) for rule in rules
                ),
            )
        )
    return ZoneDiagnosticsResponse(
        symbol=normalized,
        timeframe=_TIMEFRAME_LABELS[timeframe],
        candidates=tuple(response),
    )


@scanner_router.get("/zones/{symbol}/analysis")
def get_stock_details_analysis(
    symbol: str,
    zone_type: Literal["DEMAND", "SUPPLY"] = Query(...),
    proximal_price: float = Query(..., gt=0),
    distal_price: float = Query(..., gt=0),
    timeframe: str = Query(...),
) -> dict[str, object]:
    """Return delayed-data benchmark, timeframe and trade-plan research."""

    normalized = symbol.strip().upper()
    if normalized not in _universe_service.get_symbols("allnse"):
        raise HTTPException(
            status_code=404, detail="Symbol is not in the scanner universe."
        )
    try:
        if timeframe not in TIMEFRAME_RULES:
            raise HTTPException(status_code=400, detail="Unsupported timeframe.")
        return _stock_details_analysis.build(
            normalized,
            zone_type,
            proximal_price,
            distal_price,
            timeframe,
        )
    except (ValueError, LookupError) as error:
        raise HTTPException(
            status_code=404, detail="The selected zone could not be rebuilt."
        ) from error


@scanner_router.get("/zones/{symbol}/confluence")
def get_timeframe_confluence(
    symbol: str,
    execution_timeframe: str = Query(...),
    zone_type: Literal["DEMAND", "SUPPLY"] = Query(...),
    proximal_price: float = Query(..., gt=0),
    distal_price: float = Query(..., gt=0),
    refresh_key: str = Query(""),
    zone_quality_score: float = Query(0.0, ge=0, le=100),
) -> dict[str, object]:
    """Return cached zones only from timeframes above the execution chart."""

    normalized = symbol.strip().upper()
    if normalized not in _universe_service.get_symbols("allnse"):
        raise HTTPException(
            status_code=404,
            detail="Symbol is not in the scanner universe.",
        )
    try:
        payload = dict(
            _timeframe_confluence.build(
                normalized,
                execution_timeframe,
                zone_type,
                proximal_price,
                distal_price,
                refresh_key,
            )
        )
        endpoint_row = ZoneResearchResultResponse.model_construct(
            symbol=normalized,
            timeframe=execution_timeframe,
            zone_type=zone_type,
            proximal_price=proximal_price,
            distal_price=distal_price,
            zone_score=zone_quality_score,
            zone_id=refresh_key or f"{normalized}:{execution_timeframe}",
            pattern_type=None,
        )
        payload["trade_confidence"] = _canonical_trade_confidence_for_row(
            endpoint_row,
            refresh_key=refresh_key,
        ).model_dump()
        return payload
    except Exception as error:
        raise HTTPException(
            status_code=503,
            detail="Higher-timeframe confluence is temporarily unavailable.",
        ) from error
