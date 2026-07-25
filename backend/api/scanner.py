"""
Scanner API.

Sprint:
    2.64 - Scanner Results Foundation
"""

from fastapi import APIRouter

from backend.api.models.scanner_response import (
    ScannerResponse,
    ScannerResultResponse,
    ZoneResearchResponse,
    ZoneResearchResultResponse,
)
from backend.config.scanner_config import ScannerConfig
from backend.engines.demand_supply_engine.zone_detection_engine import (
    ZoneDetectionEngine,
)
from backend.models.market_scanner.market_scanner_result import (
    MarketScannerResult,
)
from backend.services.scanner.scanner_service import (
    ScannerService,
)
from backend.services.market_data.market_data_service import MarketDataService

scanner_router = APIRouter(
    prefix="/scanner",
    tags=["Scanner"],
)

_scanner_service = ScannerService()
_zone_market_data = MarketDataService()
_zone_engine = ZoneDetectionEngine()
_zone_config = ScannerConfig()


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
                opportunity.risk_management_result
                .entry_confirmation.trade_setup.entry_price
            ),
            stop_loss=(
                opportunity.risk_management_result
                .entry_confirmation.trade_setup.stop_loss
            ),
            target_price=(
                opportunity.risk_management_result
                .entry_confirmation.trade_setup.target_price
            ),
            risk_reward_ratio=(
                opportunity.risk_management_result
                .entry_confirmation.trade_setup.risk_reward_ratio
            ),
            confirmation_score=(
                opportunity.risk_management_result
                .entry_confirmation.confirmation_score
            ),
            volume_confirmed=(
                opportunity.risk_management_result
                .entry_confirmation.volume_confirmed
            ),
            trend_confirmed=(
                opportunity.risk_management_result
                .entry_confirmation.trend_confirmed
            ),
            momentum_confirmed=(
                opportunity.risk_management_result
                .entry_confirmation.momentum_confirmed
            ),
            confirmed=(
                opportunity.risk_management_result
                .entry_confirmation.confirmed
            ),
            approved=(
                opportunity.risk_management_result.approved
            ),
            rejection_reason=(
                opportunity.risk_management_result
                .rejection_reason
            ),
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
def get_scanner() -> ScannerResponse:
    """
    Return the current scanner data.
    """

    return build_scanner_response(
        _scanner_service.get_scanner(),
    )


@scanner_router.get("/zones", response_model=ZoneResearchResponse)
def get_research_zones() -> ZoneResearchResponse:
    """Return recent demand and supply zones for research exploration."""

    results: list[ZoneResearchResultResponse] = []
    scanned = 0
    for symbol in _zone_config.symbols:
        try:
            data = _zone_market_data.get_stock_data(
                symbol=symbol,
                period=_zone_config.period,
                interval=_zone_config.interval,
            )
            scanned += 1
            current_price = float(data["Close"].iloc[-1])
            zones = _zone_engine.detect_zones(data)
            for zone in sorted(
                zones,
                key=lambda item: item.created_index,
                reverse=True,
            )[:4]:
                if zone.lower_price <= current_price <= zone.upper_price:
                    distance = 0.0
                    status = "IN ZONE"
                elif current_price > zone.upper_price:
                    distance = (current_price - zone.upper_price) / current_price * 100
                    status = "APPROACHING" if distance <= 5 else "WATCH"
                else:
                    distance = (zone.lower_price - current_price) / current_price * 100
                    status = "APPROACHING" if distance <= 5 else "WATCH"

                recency = zone.created_index / max(len(data) - 1, 1)
                score = min(95.0, 55.0 + recency * 35.0)
                demand = zone.zone_type.value == "DEMAND"
                results.append(
                    ZoneResearchResultResponse(
                        symbol=symbol,
                        zone_type=zone.zone_type.value,
                        pattern_type=zone.pattern_type,
                        proximal_price=zone.upper_price if demand else zone.lower_price,
                        distal_price=zone.lower_price if demand else zone.upper_price,
                        distance_percent=round(distance, 2),
                        zone_score=round(score, 1),
                        current_price=current_price,
                        timeframe=_zone_config.interval,
                        base_index=zone.created_index,
                        base_date=data.index[zone.created_index].date().isoformat(),
                        status=status,
                    )
                )
        except Exception:
            continue

    results.sort(key=lambda item: (item.distance_percent, -item.zone_score))
    return ZoneResearchResponse(
        total_scanned=scanned,
        total_zones=len(results),
        results=tuple(results),
    )
