"""Cached higher-timeframe zone confluence analysis."""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from backend.services.scanner.canonical_trend_service import (
    CanonicalTrendService,
)
from backend.engines.demand_supply_engine.zone_detection_engine import (
    ZoneDetectionEngine,
)
from backend.engines.zone_scoring_engine.zone_scoring_engine import ZoneScoringEngine
from backend.engines.trend_engine.canonical_trend_engine import CanonicalTrendEngine
from backend.services.market_data.market_data_service import MarketDataService
from backend.services.market_data.timeframe_service import aggregate_timeframe
from backend.services.market_data.timeframe_service import INTRADAY_SOURCES
from backend.services.scanner.zone_lifecycle_ui_service import ZoneLifecycleUiService

TIMEFRAME_ORDER = ("1D", "1W", "1M", "3M", "6M", "1Y")
TIMEFRAME_NAMES = {
    "1D": "Daily",
    "1W": "Weekly",
    "1M": "Monthly",
    "3M": "Quarterly",
    "6M": "Half-Yearly",
    "1Y": "Yearly",
}


class TimeframeConfluenceService:
    """Compare one execution zone only with genuinely higher timeframes."""

    def __init__(self) -> None:
        self._market = MarketDataService()
        self._detector = ZoneDetectionEngine()
        self._scoring = ZoneScoringEngine()
        self._trend = CanonicalTrendService(self._market)
        self._lifecycle = ZoneLifecycleUiService()

    @staticmethod
    def higher_timeframes(execution_timeframe: str) -> tuple[str, ...]:
        if execution_timeframe not in TIMEFRAME_ORDER:
            return ()
        index = TIMEFRAME_ORDER.index(execution_timeframe)
        return TIMEFRAME_ORDER[index + 1 :]

    @staticmethod
    def overlap_percent(
        execution_lower: float,
        execution_upper: float,
        higher_lower: float,
        higher_upper: float,
    ) -> float:
        width = max(execution_upper - execution_lower, 1e-9)
        intersection = max(
            0.0,
            min(execution_upper, higher_upper) - max(execution_lower, higher_lower),
        )
        return min(100.0, intersection / width * 100.0)

    @staticmethod
    def overlap_relationship(
        execution_lower: float,
        execution_upper: float,
        higher_lower: float,
        higher_upper: float,
        tick_size: float = 0.05,
    ) -> str:
        """Describe price-area geometry without changing a zone decision."""
        tolerance = max(float(tick_size), 0.0)
        if (
            higher_lower <= execution_lower + tolerance
            and higher_upper >= execution_upper - tolerance
        ):
            return "FULL_OVERLAP"
        intersection = min(execution_upper, higher_upper) - max(
            execution_lower, higher_lower
        )
        if intersection > tolerance:
            return "PARTIAL_OVERLAP"
        gap = max(higher_lower - execution_upper, execution_lower - higher_upper, 0.0)
        return "TOUCHING" if gap <= tolerance else "NO_OVERLAP"

    @staticmethod
    def distance_percent(
        execution_lower: float,
        execution_upper: float,
        higher_lower: float,
        higher_upper: float,
        current_price: float,
    ) -> float:
        if higher_upper < execution_lower:
            distance = execution_lower - higher_upper
        elif higher_lower > execution_upper:
            distance = higher_lower - execution_upper
        else:
            distance = 0.0
        return distance / max(current_price, 1e-9) * 100.0

    @staticmethod
    def status(
        same_type: bool,
        overlap: float,
        distance: float,
    ) -> str:
        if same_type and overlap >= 50:
            return "CONFIRMED"
        if same_type and (overlap > 0 or distance <= 5):
            return "PARTIAL"
        return "NOT_CONFIRMED"

    @staticmethod
    def compatibility(zone_type: str, higher_zone_type: str | None) -> str:
        if higher_zone_type is None:
            return "NO_HTF_CONTEXT"
        return "ALIGNED" if zone_type == higher_zone_type else "OPPOSING"

    @staticmethod
    def reason_code(relationship: str, compatibility: str) -> str:
        if compatibility == "NO_HTF_CONTEXT":
            return "HTF_NO_ACTIVE_ZONE"
        if relationship == "NO_OVERLAP":
            return "HTF_NO_OVERLAP"
        return f"HTF_{relationship}_{compatibility}"

    @staticmethod
    def _explanation(
        timeframe: str,
        zone_type: str,
        execution_type: str,
        overlap: float,
        distance: float,
    ) -> str:
        name = TIMEFRAME_NAMES[timeframe]
        zone_name = zone_type.lower()
        if zone_type == execution_type and overlap >= 99:
            return f"{name} {zone_name} fully contains the selected zone."
        if zone_type == execution_type and overlap > 0:
            return (
                f"{name} {zone_name} overlaps the selected zone by " f"{overlap:.1f}%."
            )
        if zone_type == execution_type:
            return (
                f"{name} {zone_name} is {distance:.1f}% away, so support " "is limited."
            )
        return (
            f"{name} {zone_name} points in the opposite direction and "
            "does not confirm this setup."
        )

    @lru_cache(maxsize=128)
    def build(
        self,
        symbol: str,
        execution_timeframe: str,
        zone_type: str,
        proximal_price: float,
        distal_price: float,
        refresh_key: str = "",
    ) -> dict[str, Any]:
        del refresh_key  # It intentionally remains part of the cache key.
        workflow, trend = self._trend.analyze(symbol, execution_timeframe)
        higher_frames = (workflow.location,) if workflow.location else ()
        execution_lower = min(proximal_price, distal_price)
        execution_upper = max(proximal_price, distal_price)
        source_period, source_interval = self._source_for_location(
            workflow.location
        )
        try:
            validated_data = self._market.get_stock_data_segments(
                symbol, period=source_period, interval=source_interval
            )
        except Exception:
            return self._unavailable_response(
                symbol=symbol,
                execution_timeframe=execution_timeframe,
                zone_type=zone_type,
                proximal_price=proximal_price,
                distal_price=distal_price,
                workflow=workflow,
                trend=trend,
                reason_code="HTF_DATA_UNAVAILABLE",
                explanation="Monthly market data could not be loaded.",
            )
        segments = validated_data.segments
        current_price = float(segments[-1]["Close"].iloc[-1])
        results: list[dict[str, Any]] = []
        for timeframe in higher_frames:
            zones = []
            detected_count = 0
            completed_count = 0
            for segment in segments:
                framed = aggregate_timeframe(segment, timeframe)
                framed = CanonicalTrendEngine.completed_candles(
                    framed, timeframe
                )
                completed_count += len(framed)
                if not framed.empty:
                    try:
                        detected = self._detector.detect_zones(framed)
                    except Exception:
                        return self._unavailable_response(
                            symbol=symbol,
                            execution_timeframe=execution_timeframe,
                            zone_type=zone_type,
                            proximal_price=proximal_price,
                            distal_price=distal_price,
                            workflow=workflow,
                            trend=trend,
                            reason_code="HTF_ANALYSIS_FAILED",
                            explanation="Monthly zone analysis could not be completed.",
                        )
                    detected_count += len(detected)
                    metadata = self._lifecycle.evaluate(
                        detected,
                        framed,
                        symbol=symbol,
                        timeframe=timeframe,
                        current_price=float(framed["Close"].iloc[-1]),
                    )
                    zones.extend(
                        zone
                        for zone in detected
                        if metadata[zone.created_index].dashboard_lifecycle_eligible
                    )
            if not zones:
                reason_code = (
                    "HTF_INSUFFICIENT_HISTORY"
                    if completed_count < 3
                    else "HTF_NO_ACTIVE_ZONE"
                    if detected_count
                    else "HTF_NO_CANONICAL_ZONE"
                )
                results.append(
                    {
                        "timeframe": timeframe,
                        "timeframe_name": TIMEFRAME_NAMES[timeframe],
                        "status": "NOT_CONFIRMED",
                        "zone": None,
                        "relationship": "NO_OVERLAP",
                        "compatibility": "NO_HTF_CONTEXT",
                        "reason_code": reason_code,
                        "selection_reason": (
                            "No canonical zone exists on this timeframe."
                        ),
                        "explanation": (
                            f"No validated {TIMEFRAME_NAMES[timeframe].lower()} "
                            "zone was found in the available history."
                        ),
                    }
                )
                continue
            candidates = []
            for zone in zones:
                overlap = self.overlap_percent(
                    execution_lower,
                    execution_upper,
                    zone.lower_price,
                    zone.upper_price,
                )
                distance = self.distance_percent(
                    execution_lower,
                    execution_upper,
                    zone.lower_price,
                    zone.upper_price,
                    current_price,
                )
                candidates.append((zone, overlap, distance))
            selected, overlap, distance = max(
                candidates,
                key=lambda item: (
                    item[1],
                    -item[2],
                    item[0].created_index,
                    item[0].zone_type.value,
                ),
            )
            score = self._scoring.score([selected]).scored_zones[0].total_score
            same_type = selected.zone_type.value == zone_type
            compatibility = self.compatibility(zone_type, selected.zone_type.value)
            relationship = self.overlap_relationship(
                execution_lower,
                execution_upper,
                selected.lower_price,
                selected.upper_price,
            )
            reason_code = self.reason_code(relationship, compatibility)
            zone_id = (
                f"{symbol}:{timeframe}:{selected.zone_type.value}:"
                f"{selected.pattern_type or 'UNKNOWN'}:{selected.created_index}"
            )
            results.append(
                {
                    "timeframe": timeframe,
                    "timeframe_name": TIMEFRAME_NAMES[timeframe],
                    "status": self.status(same_type, overlap, distance),
                    "relationship": relationship,
                    "compatibility": compatibility,
                    "reason_code": reason_code,
                    "selection_reason": (
                        "Selected by highest execution-zone overlap, then shortest "
                        "distance, then newest canonical formation."
                    ),
                    "zone": {
                        "zone_id": zone_id,
                        "zone_type": selected.zone_type.value,
                        "lower_price": round(selected.lower_price, 2),
                        "upper_price": round(selected.upper_price, 2),
                        "proximal_price": round(
                            (
                                selected.upper_price
                                if selected.zone_type.value == "DEMAND"
                                else selected.lower_price
                            ),
                            2,
                        ),
                        "distal_price": round(
                            (
                                selected.lower_price
                                if selected.zone_type.value == "DEMAND"
                                else selected.upper_price
                            ),
                            2,
                        ),
                        "quality": round(score, 1),
                        "overlap_percent": round(overlap, 1),
                        "distance_percent": round(distance, 2),
                        "freshness": ("Fresh" if selected.is_fresh else "Retested"),
                        "retests": selected.touch_count,
                        "relationship": relationship,
                        "direction": compatibility,
                        "reason_code": reason_code,
                    },
                    "explanation": self._explanation(
                        timeframe,
                        selected.zone_type.value,
                        zone_type,
                        overlap,
                        distance,
                    ),
                }
            )
        confirmed = [item for item in results if item["status"] == "CONFIRMED"]
        zones_with_data = [item for item in results if item["zone"]]
        average_overlap = (
            sum(item["zone"]["overlap_percent"] for item in zones_with_data)
            / len(zones_with_data)
            if zones_with_data
            else 0.0
        )
        average_quality = (
            sum(item["zone"]["quality"] for item in confirmed) / len(confirmed)
            if confirmed
            else 0.0
        )
        count_score = len(confirmed) / max(len(results), 1) * 40
        confluence_score = round(
            min(
                100.0,
                count_score + average_overlap * 0.4 + average_quality * 0.2,
            ),
            1,
        )
        strength = (
            "Strong"
            if confluence_score >= 70
            else "Moderate" if confluence_score >= 40 else "Weak"
        )
        if confirmed:
            names = " and ".join(item["timeframe_name"] for item in confirmed)
            summary = (
                f"The selected {zone_type.lower()} zone is supported by "
                f"{names}. Similar price areas appear on higher timeframes."
            )
        else:
            summary = (
                f"The selected {zone_type.lower()} zone has no confirmed "
                "higher-timeframe support. It relies on the execution chart."
            )
        return {
            "symbol": symbol,
            "execution_timeframe": execution_timeframe,
            "location_timeframe": workflow.location,
            "trend_timeframe": workflow.trend,
            "workflow_source": workflow.source.value,
            "trend_state": trend.trend_state.value,
            "trend_alignment": self._trend.alignment(
                zone_type, trend.trend_state
            ).value,
            "canonical_trend": trend.as_dict(),
            "combined_context": self._combined_context(
                trend.trend_state.value,
                self._trend.alignment(zone_type, trend.trend_state).value,
                results,
            ),
            "execution_zone": {
                "zone_type": zone_type,
                "proximal_price": proximal_price,
                "distal_price": distal_price,
            },
            "higher_timeframes": results,
            "confluence_score": confluence_score,
            "strength": strength,
            "summary": summary,
            "source": "Yahoo Finance delayed OHLCV",
            "canonical_analysis": {
                "symbol": symbol,
                "execution_timeframe": execution_timeframe,
                "trend_timeframe": workflow.trend,
                "location_timeframe": workflow.location,
                "canonical_trend": trend.as_dict(),
                "trend_alignment": self._trend.alignment(
                    zone_type, trend.trend_state
                ).value,
                "htf_location": results[0] if results else None,
                "location_relationship": (
                    results[0]["relationship"] if results else "NO_OVERLAP"
                ),
                "location_compatibility": (
                    results[0]["compatibility"]
                    if results else "NO_HTF_CONTEXT"
                ),
                "reason_codes": [
                    *[code.value for code in trend.reason_codes],
                    *[item["reason_code"] for item in results],
                ],
                "data_sufficient": trend.data_sufficient
                and all(item["reason_code"] not in {
                    "HTF_DATA_UNAVAILABLE",
                    "HTF_INSUFFICIENT_HISTORY",
                    "HTF_ANALYSIS_FAILED",
                } for item in results),
            },
        }

    @staticmethod
    def _source_for_location(timeframe: str | None) -> tuple[str, str]:
        if timeframe in INTRADAY_SOURCES:
            return INTRADAY_SOURCES[timeframe]
        if timeframe == "1W":
            return "10y", "1wk"
        if timeframe == "1M":
            return "10y", "1mo"
        return "10y", "1d"

    @staticmethod
    def _combined_context(
        trend_state: str,
        trend_alignment: str,
        results: list[dict[str, Any]],
    ) -> dict[str, str]:
        location = results[0] if results else None
        return {
            "trend_state": trend_state,
            "trend_alignment": trend_alignment,
            "location_relationship": (
                location["relationship"] if location else "NO_OVERLAP"
            ),
            "location_compatibility": (
                location["compatibility"] if location else "NO_HTF_CONTEXT"
            ),
            "location_reason_code": (
                location["reason_code"] if location else "HTF_NO_ACTIVE_ZONE"
            ),
        }

    @classmethod
    def _unavailable_response(
        cls,
        *,
        symbol: str,
        execution_timeframe: str,
        zone_type: str,
        proximal_price: float,
        distal_price: float,
        workflow: Any,
        trend: Any,
        reason_code: str,
        explanation: str,
    ) -> dict[str, Any]:
        item = {
            "timeframe": workflow.location,
            "timeframe_name": TIMEFRAME_NAMES.get(workflow.location, "Location"),
            "status": "NOT_CONFIRMED",
            "zone": None,
            "relationship": "NO_OVERLAP",
            "compatibility": "NO_HTF_CONTEXT",
            "reason_code": reason_code,
            "selection_reason": "No higher-timeframe zone was selected.",
            "explanation": explanation,
        }
        alignment = CanonicalTrendEngine.alignment(
            zone_type, trend.trend_state
        ).value
        return {
            "symbol": symbol,
            "execution_timeframe": execution_timeframe,
            "location_timeframe": workflow.location,
            "trend_timeframe": workflow.trend,
            "workflow_source": workflow.source.value,
            "trend_state": trend.trend_state.value,
            "trend_alignment": alignment,
            "canonical_trend": trend.as_dict(),
            "execution_zone": {
                "zone_type": zone_type,
                "proximal_price": proximal_price,
                "distal_price": distal_price,
            },
            "higher_timeframes": [item],
            "combined_context": cls._combined_context(
                trend.trend_state.value, alignment, [item]
            ),
            "canonical_analysis": {
                "symbol": symbol,
                "execution_timeframe": execution_timeframe,
                "trend_timeframe": workflow.trend,
                "location_timeframe": workflow.location,
                "canonical_trend": trend.as_dict(),
                "trend_alignment": alignment,
                "htf_location": item,
                "location_relationship": "NO_OVERLAP",
                "location_compatibility": "NO_HTF_CONTEXT",
                "reason_codes": [
                    *[code.value for code in trend.reason_codes], reason_code
                ],
                "data_sufficient": False,
            },
            "confluence_score": 0.0,
            "strength": "Weak",
            "summary": explanation,
            "source": "Yahoo Finance delayed OHLCV",
        }
