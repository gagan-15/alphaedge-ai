"""
Scanner API Response Models.

Sprint:
    2.64 - Scanner Results Foundation
"""

from backend.api.models.dashboard_response import (
    APIResponseModel,
)


class ScannerResultResponse(APIResponseModel):
    """
    Represents one screened trading opportunity.
    """

    symbol: str

    entry_price: float

    stop_loss: float

    target_price: float

    risk_reward_ratio: float

    confirmation_score: float

    volume_confirmed: bool

    trend_confirmed: bool

    momentum_confirmed: bool

    confirmed: bool

    approved: bool

    rejection_reason: str | None = None


class ScannerResponse(APIResponseModel):
    """
    Complete scanner API response.
    """

    total_scanned: int

    total_matches: int

    results: tuple[ScannerResultResponse, ...]
