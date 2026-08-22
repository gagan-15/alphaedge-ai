"""
Scanner API Response Models.

Sprint:
    2.64 - Scanner Results Foundation
"""

from backend.api.models.dashboard_response import (
    APIResponseModel,
)
from backend.config.canonical_methodology import SCANNER_METHODOLOGY_CACHE_VERSION


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
    gap_type: str | None = None


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
    """Explanation of AlphaEdge Zone Quality from canonical evidence."""

    overall_score: float
    rating: int
    label: str
    summary: str
    positive_factors: tuple[ZoneExplanationFactorResponse, ...]
    negative_factors: tuple[ZoneExplanationFactorResponse, ...]
    educational_insight: str


class ZoneQualityComponentResponse(APIResponseModel):
    """One serialized AlphaEdge Canonical Zone Quality component."""

    key: str
    score: float
    maximum_score: float
    evidence: tuple[str, ...] = ()
    reason_codes: tuple[str, ...] = ()


class CanonicalTradeConfidenceResponse(APIResponseModel):
    """Canonical Trade Confidence serialized with a scanner row."""

    score: float
    label: str
    zone_quality_score: float
    zone_quality_contribution: float
    location_contribution: float
    trend_contribution: float
    location_alignment: str
    trend_alignment: str
    combined_context: str
    htf_overlap_type: str
    htf_direction_compatibility: str
    data_sufficiency: str
    reason_codes: tuple[str, ...] = ()
    evidence: tuple[str, ...] = ()
    shadow_mode: bool = False


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
    raw_zone_score: float
    quality_cap: float
    zone_quality_label: str | None = None
    zone_quality_components: dict[str, float] = {}
    zone_quality_component_details: tuple[ZoneQualityComponentResponse, ...] = ()
    zone_quality_reason_codes: tuple[str, ...] = ()
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
    reaction_percent: float | None = None
    reaction_started: str | None = None
    reaction_ended: str | None = None
    reaction_duration_candles: int | None = None
    zone_id: str | None = None
    lifecycle_status: str | None = None
    authenticity_status: str | None = None
    authenticity_reason_code: str | None = None
    authenticity_reason: str | None = None
    test_count: int | None = None
    reaction_status: str | None = None
    reaction_percentage: float | None = None
    max_penetration_percent: float | None = None
    current_penetration_percent: float | None = None
    good_closing: bool | None = None
    parent_zone_id: str | None = None
    is_nested: bool = False
    is_duplicate: bool = False
    overlap_percent: float | None = None
    dashboard_qualified: bool = False
    qualification_reason_codes: tuple[str, ...] = ()
    departure_quality: str | None = None
    canonical_formation_departure: str | None = None
    dashboard_qualification_departure: str | None = None
    base_quality: str | None = None
    formation_quality: str | None = None
    departure_displacement: float | None = None
    departure_zone_width_ratio: float | None = None
    base_candle_count: int | None = None
    base_compactness: str | None = None
    base_compactness_reason: str | None = None
    trade_confidence: CanonicalTradeConfidenceResponse | None = None


class ZoneStateCountResponse(APIResponseModel):
    """Lifecycle and authenticity counts for one zone direction."""

    total: int = 0
    fresh: int = 0
    reacting: int = 0
    tested: int = 0
    retested: int = 0
    invalidated: int = 0
    authentic: int = 0
    non_authentic: int = 0


class ZoneLifecycleSummaryResponse(APIResponseModel):
    """Dashboard-ready counts produced from canonical engine records."""

    demand: ZoneStateCountResponse
    supply: ZoneStateCountResponse


class ZoneResearchResponse(APIResponseModel):
    """Research zones across the configured scanner universe."""

    total_scanned: int
    total_zones: int
    delayed: bool = True
    timeframe: str = "1D"
    results: tuple[ZoneResearchResultResponse, ...]
    historical_results: tuple[ZoneResearchResultResponse, ...] = ()
    universe: str = "nse500"
    status: str = "completed"
    total_symbols: int = 0
    processed_symbols: int = 0
    failed_symbols: int = 0
    last_completed_at: str | None = None
    data_status: str = "delayed"
    lifecycle_summary: ZoneLifecycleSummaryResponse | None = None
    canonical_zone_count: int = 0
    formation_qualified_count: int = 0
    dashboard_qualified_count: int = 0
    dashboard_rejected_count: int = 0
    qualification_rejection_counts: dict[str, int] = {}
    methodology_version: str = SCANNER_METHODOLOGY_CACHE_VERSION


class ZoneRuleDiagnosticResponse(APIResponseModel):
    """One production-rule result for a developer candidate."""

    key: str
    label: str
    passed: bool
    actual: str | float | int | bool | None = None
    required: str | float | int | bool | None = None


class ZoneCandidateDiagnosticResponse(APIResponseModel):
    """Developer-only lifecycle record for one evaluated candidate."""

    candidate_id: str
    symbol: str
    timeframe: str
    pattern: str | None = None
    base_start_index: int
    base_end_index: int
    base_start_date: str
    base_end_date: str
    proximal: float
    distal: float
    zone_type: str | None = None
    status: str
    score: float | None = None
    rejection_reasons: tuple[str, ...]
    rule_results: tuple[ZoneRuleDiagnosticResponse, ...]


class ZoneDiagnosticsResponse(APIResponseModel):
    """Separate developer payload; never included in normal scanner results."""

    symbol: str
    timeframe: str
    candidates: tuple[ZoneCandidateDiagnosticResponse, ...]
