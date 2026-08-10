"""
Scanner API.

Sprint:
    2.64 - Scanner Results Foundation
"""

from dataclasses import replace
from concurrent.futures import Future, ThreadPoolExecutor
from datetime import UTC, datetime
from threading import RLock
from time import monotonic, sleep
from typing import Literal

from fastapi import APIRouter, HTTPException, Query
from pandas import DataFrame

from backend.core.logger import logger
from backend.api.models.scanner_response import (
    ScannerResponse,
    ScannerResultResponse,
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
from backend.services.zone_explanation_service import ZoneExplanationService
from backend.services.market_data.market_data_service import MarketDataService
from backend.services.market_data.timeframe_service import (
    TIMEFRAME_RULES,
    aggregate_timeframe,
)
from backend.services.scanner.universe_service import (
    UniverseName,
    UniverseService,
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
_zone_lifecycle_ui = ZoneLifecycleUiService()
_dashboard_qualification = DashboardZoneQualificationService()
_universe_service = UniverseService()
_zone_scan_executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="zone-scan")
_zone_scan_cache: dict[str, tuple[float, ZoneResearchResponse]] = {}
_zone_scan_jobs: dict[str, Future[ZoneResearchResponse]] = {}
_zone_scan_progress: dict[str, tuple[int, int]] = {}
_zone_scan_lock = RLock()
# A complete large-universe scan is expensive. Keep the last completed result
# available long enough that normal page navigation does not continuously start
# another NSE 500 scan.
_zone_scan_ttl_seconds = 1800.0

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


def _measure_zone(zone: Zone, data: DataFrame) -> Zone:
    """Add observable freshness, retest and departure measurements."""

    zone_width = max(zone.upper_price - zone.lower_price, 1e-9)
    departure_start = min(zone.created_index + 1, len(data))
    departure_end = min(departure_start + 3, len(data))
    departure = data.iloc[departure_start:departure_end]

    if departure.empty:
        departure_multiple = 0.0
        follow_through_ratio = 0.0
        reversal_penalty = 1.0
    elif zone.zone_type == ZoneType.DEMAND:
        departure_multiple = max(
            0.0,
            (float(departure["High"].max()) - zone.upper_price) / zone_width,
        )
        follow_through_ratio = float(
            (departure["Close"] > zone.upper_price).sum()
        ) / len(departure)
        reversal_penalty = (
            0.45 if float(departure["Close"].iloc[-1]) <= zone.upper_price else 1.0
        )
    else:
        departure_multiple = max(
            0.0,
            (zone.lower_price - float(departure["Low"].min())) / zone_width,
        )
        follow_through_ratio = float(
            (departure["Close"] < zone.lower_price).sum()
        ) / len(departure)
        reversal_penalty = (
            0.45 if float(departure["Close"].iloc[-1]) >= zone.lower_price else 1.0
        )

    later = data.iloc[departure_end:]
    touches = int(
        ((later["Low"] <= zone.upper_price) & (later["High"] >= zone.lower_price)).sum()
    )
    departure_strength = (
        min(
            35.0,
            departure_multiple / 3.0 * 35.0,
        )
        * follow_through_ratio
        * reversal_penalty
    )

    return replace(
        zone,
        strength=round(departure_strength, 2),
        is_fresh=touches == 0,
        touch_count=touches,
    )


def _is_zone_invalidated(zone: Zone, data: DataFrame) -> bool:
    """Return True when a later candle closes beyond the distal boundary."""

    first_review_index = min(zone.created_index + 2, len(data))
    later_closes = data.iloc[first_review_index:]["Close"]
    if later_closes.empty:
        return False

    if zone.zone_type == ZoneType.DEMAND:
        return bool((later_closes < zone.lower_price).any())

    return bool((later_closes > zone.upper_price).any())


def _has_completed_test(zone: Zone, data: DataFrame) -> bool:
    """Return True when price tested the zone before the current candle."""

    departure_end = min(zone.created_index + 4, len(data))
    prior_candles = data.iloc[departure_end:-1]
    if prior_candles.empty:
        return False

    overlaps = (prior_candles["Low"] <= zone.upper_price) & (
        prior_candles["High"] >= zone.lower_price
    )
    return bool(overlaps.any())


def _reaction_state(
    zone: Zone,
    data: DataFrame,
    completion_percent: float,
) -> dict[str, object]:
    """Describe a confirmed reaction without changing zone detection.

    A reaction begins only after a post-departure candle has entered the zone
    and a later close crosses back through the proximal boundary in the
    expected direction. It ends at the configured move beyond proximal.
    """

    departure_end = min(zone.created_index + 4, len(data))
    later = data.iloc[departure_end:]
    if len(later) < 2:
        return {"active": False}

    demand = zone.zone_type == ZoneType.DEMAND
    touched = False
    start_position: int | None = None
    previous_close: float | None = None
    for position, (index, candle) in enumerate(later.iterrows()):
        low = float(candle["Low"])
        high = float(candle["High"])
        close = float(candle["Close"])
        entered_on_candle = low <= zone.upper_price and high >= zone.lower_price
        touched = touched or entered_on_candle
        crossed = touched and (
            (
                demand
                and close > zone.upper_price
                and (
                    entered_on_candle
                    or (
                        previous_close is not None
                        and previous_close <= zone.upper_price
                    )
                )
            )
            or (
                not demand
                and close < zone.lower_price
                and (
                    entered_on_candle
                    or (
                        previous_close is not None
                        and previous_close >= zone.lower_price
                    )
                )
            )
        )
        if crossed:
            start_position = position
            started = index
            break
        previous_close = close

    if start_position is None:
        return {"active": False}

    proximal = zone.upper_price if demand else zone.lower_price
    latest = float(data["Close"].iloc[-1])
    reaction_percent = (
        (latest - proximal) / proximal * 100
        if demand
        else (proximal - latest) / proximal * 100
    )
    completion_price = proximal * (
        1 + completion_percent / 100 if demand else 1 - completion_percent / 100
    )
    reaction_candles = later.iloc[start_position:]
    completed_mask = (
        reaction_candles["Close"] >= completion_price
        if demand
        else reaction_candles["Close"] <= completion_price
    )
    completion_positions = [
        position
        for position, completed in enumerate(completed_mask.tolist())
        if completed
    ]
    completed = bool(completion_positions)
    end_position = completion_positions[0] if completed else None
    ended_index = (
        reaction_candles.index[end_position] if end_position is not None else None
    )
    duration = end_position + 1 if end_position is not None else len(reaction_candles)
    return {
        "active": not completed and reaction_percent >= 0,
        "percent": round(reaction_percent, 2),
        "started": (
            started.isoformat() if hasattr(started, "isoformat") else str(started)
        ),
        "ended": (
            ended_index.isoformat()
            if ended_index is not None and hasattr(ended_index, "isoformat")
            else str(ended_index) if ended_index is not None else None
        ),
        "duration": duration,
    }


def _departure_gap(zone: Zone, data: DataFrame) -> str | None:
    """Classify a true non-overlapping gap on the departure candle."""

    departure_index = zone.created_index + 1
    if departure_index >= len(data):
        return None
    previous = data.iloc[departure_index - 1]
    departure = data.iloc[departure_index]
    if float(departure["Low"]) > float(previous["High"]):
        return "GAP UP"
    if float(departure["High"]) < float(previous["Low"]):
        return "GAP DOWN"
    return None


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
    universe: UniverseName = Query(default="nse500"),
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
) -> ZoneResearchResponse:
    """Return recent demand and supply zones for research exploration."""

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

    for symbol, loaded in zip(universe_symbols, loaded_data, strict=True):
        if loaded is None:
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
                zone = _measure_zone(detected_zone, data)
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
                gap_type = _departure_gap(zone, data)
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
                        metadata.dashboard_lifecycle_eligible
                        if metadata
                        else False
                    ),
                    qualification_reason_codes=(
                        qualification.qualification_reason_codes
                        + (
                            metadata.dashboard_lifecycle_reason_code,
                        )
                        if metadata
                        else qualification.qualification_reason_codes
                    ),
                    departure_quality=qualification.departure_quality,
                    base_quality=qualification.base_quality,
                    formation_quality=qualification.formation_quality,
                    departure_displacement=(qualification.departure_displacement),
                    departure_zone_width_ratio=(
                        qualification.departure_zone_width_ratio
                    ),
                    base_candle_count=qualification.base_candle_count,
                    base_compactness=qualification.base_compactness,
                    base_compactness_reason=(
                        qualification.base_compactness_reason
                    ),
                )
                dashboard_base_preferences[(symbol, zone.created_index)] = (
                    qualification.base_preference_rank
                )
                if invalidated:
                    historical_results.append(response)
                else:
                    results.append(response)
        except Exception:
            continue

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
        "v7-canonical-zone-quality"
    )


def _store_zone_scan(key: str, future: Future[ZoneResearchResponse]) -> None:
    with _zone_scan_lock:
        _zone_scan_jobs.pop(key, None)
        _zone_scan_progress.pop(key, None)
        try:
            _zone_scan_cache[key] = (monotonic(), future.result())
        except Exception:
            return


@scanner_router.get("/zones", response_model=ZoneResearchResponse)
def get_research_zones(
    timeframe: ZoneTimeframe = Query(default="DAILY"),
    universe: UniverseName = Query(default="nse500"),
    symbols: list[str] | None = Query(default=None),
) -> ZoneResearchResponse:
    """Return cached results immediately and refresh scans in background."""

    universe_symbols = _universe_service.get_symbols(universe, symbols)
    key = _zone_scan_key(timeframe, universe, symbols)
    with _zone_scan_lock:
        cached_entry = _zone_scan_cache.get(key)
        job = _zone_scan_jobs.get(key)
        stale = (
            not cached_entry or monotonic() - cached_entry[0] >= _zone_scan_ttl_seconds
        )
        if stale and job is None:
            _zone_scan_progress[key] = (0, 0)
            job = _zone_scan_executor.submit(
                _scan_research_zones,
                timeframe,
                universe,
                symbols,
                key,
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
            return cached.model_copy(
                update={
                    "status": "refreshing" if stale else "completed",
                    "data_status": "cached" if stale else cached.data_status,
                    "processed_symbols": processed,
                    "failed_symbols": failed,
                }
            )
        processed, failed = _zone_scan_progress.get(key, (0, 0))
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
    data = _zone_market_data.get_stock_data(
        symbol=normalized,
        period=source_period,
        interval=source_interval,
    )
    data = _timeframe_data(data, timeframe)
    accepted, candidates = _zone_engine.detect_zones_with_diagnostics(data)
    accepted_by_index = {zone.created_index: zone for zone in accepted}
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
            measured = _measure_zone(zone, data)
            score = round(
                _zone_scoring_engine.score([measured]).scored_zones[0].total_score,
                1,
            )
            invalidated = _is_zone_invalidated(measured, data)
            completed_test = _has_completed_test(measured, data)
            rules.extend(
                [
                    {
                        "key": "freshness",
                        "label": "Zone remains fresh",
                        "passed": measured.is_fresh,
                        "actual": measured.touch_count,
                        "required": 0,
                    },
                    {
                        "key": "retest_count",
                        "label": "Retest count",
                        "passed": measured.touch_count == 0,
                        "actual": measured.touch_count,
                        "required": 0,
                    },
                    {
                        "key": "invalidation",
                        "label": "No close beyond distal boundary",
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
                reasons.append("A later candle closed beyond the distal boundary.")
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
) -> dict[str, object]:
    """Return cached zones only from timeframes above the execution chart."""

    normalized = symbol.strip().upper()
    if normalized not in _universe_service.get_symbols("allnse"):
        raise HTTPException(
            status_code=404,
            detail="Symbol is not in the scanner universe.",
        )
    try:
        return _timeframe_confluence.build(
            normalized,
            execution_timeframe,
            zone_type,
            proximal_price,
            distal_price,
            refresh_key,
        )
    except Exception as error:
        raise HTTPException(
            status_code=503,
            detail="Higher-timeframe confluence is temporarily unavailable.",
        ) from error
