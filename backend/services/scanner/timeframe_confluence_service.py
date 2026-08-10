"""Cached higher-timeframe zone confluence analysis."""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from backend.config.timeframe_hierarchy import get_timeframe_hierarchy
from backend.engines.demand_supply_engine.zone_detection_engine import (
    ZoneDetectionEngine,
)
from backend.engines.zone_scoring_engine.zone_scoring_engine import ZoneScoringEngine
from backend.services.market_data.market_data_service import MarketDataService
from backend.services.market_data.timeframe_service import aggregate_timeframe

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
            min(execution_upper, higher_upper)
            - max(execution_lower, higher_lower),
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
            return "HTF_CONTEXT_UNAVAILABLE"
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
                f"{name} {zone_name} overlaps the selected zone by "
                f"{overlap:.1f}%."
            )
        if zone_type == execution_type:
            return (
                f"{name} {zone_name} is {distance:.1f}% away, so support "
                "is limited."
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
        higher_frames = self.higher_timeframes(execution_timeframe)
        hierarchy = get_timeframe_hierarchy(execution_timeframe)
        execution_lower = min(proximal_price, distal_price)
        execution_upper = max(proximal_price, distal_price)
        validated_data = self._market.get_stock_data_segments(
            symbol, period="10y", interval="1d"
        )
        segments = validated_data.segments
        current_price = float(segments[-1]["Close"].iloc[-1])
        results: list[dict[str, Any]] = []
        for timeframe in higher_frames:
            zones = []
            for segment in segments:
                framed = aggregate_timeframe(segment, timeframe)
                if not framed.empty:
                    zones.extend(self._detector.detect_zones(framed))
            if not zones:
                results.append(
                    {
                        "timeframe": timeframe,
                        "timeframe_name": TIMEFRAME_NAMES[timeframe],
                        "status": "NOT_CONFIRMED",
                        "zone": None,
                        "relationship": "NO_OVERLAP",
                        "compatibility": "NO_HTF_CONTEXT",
                        "reason_code": "HTF_CONTEXT_UNAVAILABLE",
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
                            selected.upper_price
                            if selected.zone_type.value == "DEMAND"
                            else selected.lower_price,
                            2,
                        ),
                        "distal_price": round(
                            selected.lower_price
                            if selected.zone_type.value == "DEMAND"
                            else selected.upper_price,
                            2,
                        ),
                        "quality": round(score, 1),
                        "overlap_percent": round(overlap, 1),
                        "distance_percent": round(distance, 2),
                        "freshness": (
                            "Fresh" if selected.is_fresh else "Retested"
                        ),
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
                count_score
                + average_overlap * 0.4
                + average_quality * 0.2,
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
            "location_timeframe": hierarchy.location,
            "trend_timeframe": hierarchy.trend,
            "trend_state": "UNAVAILABLE",
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
        }
