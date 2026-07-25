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

    zone_type: str | None = None

    proximal_price: float | None = None

    distal_price: float | None = None

    zone_score: float | None = None

    distance_percent: float | None = None

    zone_fresh: bool | None = None

    touch_count: int | None = None

    base_index: int | None = None

    timeframe: str | None = None
    pattern_type: str | None = None


class ScannerResponse(APIResponseModel):
    """
    Complete scanner API response.
    """

    total_scanned: int

    total_matches: int

    results: tuple[ScannerResultResponse, ...]


class ZoneExplanationFactorResponse(APIResponseModel):
    """One available zone explanation factor."""

    key: str
    title: str
    score: float
    sentiment: str
    summary: str
    recommendation: str
    weight: float


class ZoneExplanationResponse(APIResponseModel):
    """Trader-readable explanation of rule-based zone quality."""

    overall_score: float
    rating: int
    label: str
    summary: str
    positive_factors: tuple[ZoneExplanationFactorResponse, ...]
    negative_factors: tuple[ZoneExplanationFactorResponse, ...]
    educational_insight: str


class ZoneResearchResultResponse(APIResponseModel):
    """Detected zone context without execution claims."""

    symbol: str
    zone_type: str
    pattern_type: str | None = None
    proximal_price: float
    distal_price: float
    distance_percent: float
    zone_score: float
    score_kind: str = "RULE_BASED_QUALITY"
    freshness_score: float
    strength_score: float
    touch_score: float
    merge_score: float
    is_fresh: bool
    touch_count: int
    merged_count: int
    evidence: tuple[str, ...]
    explanation: ZoneExplanationResponse
    current_price: float
    timeframe: str
    base_index: int
    base_date: str
    status: str


class ZoneResearchResponse(APIResponseModel):
    """Research zones across the configured scanner universe."""

    total_scanned: int
    total_zones: int
    delayed: bool = True
    results: tuple[ZoneResearchResultResponse, ...]
