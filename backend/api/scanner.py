"""
Scanner API.

Sprint:
    2.64 - Scanner Results Foundation
"""

from fastapi import APIRouter

from backend.api.models.scanner_response import (
    ScannerResponse,
    ScannerResultResponse,
)
from backend.models.market_scanner.market_scanner_result import (
    MarketScannerResult,
)
from backend.services.scanner.scanner_service import (
    ScannerService,
)

scanner_router = APIRouter(
    prefix="/scanner",
    tags=["Scanner"],
)

_scanner_service = ScannerService()


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
