/**
 * Scanner Types.
 *
 * Sprint:
 *     2.64 - Scanner Results Foundation
 */

export interface ScannerResult {
    symbol: string;

    entry_price: number;

    stop_loss: number;

    target_price: number;

    risk_reward_ratio: number;

    confirmation_score: number;

    volume_confirmed: boolean;

    trend_confirmed: boolean;

    momentum_confirmed: boolean;

    confirmed: boolean;

    approved: boolean;

    rejection_reason: string | null;

    zone_type: string | null;
    proximal_price: number | null;
    distal_price: number | null;
    zone_score: number | null;
    distance_percent: number | null;
    zone_fresh: boolean | null;
    touch_count: number | null;
    base_index: number | null;
    timeframe: string | null;
    pattern_type: string | null;
    gap_type: string | null;
}

export interface ScannerResponse {
    total_scanned: number;

    total_matches: number;

    results: ScannerResult[];
}

export interface ZoneResearchResult {
    symbol: string;
    zone_type: string;
    pattern_type: string | null;
    gap_type: string | null;
    proximal_price: number;
    distal_price: number;
    distance_percent: number;
    zone_score: number;
    score_kind: "RULE_BASED_QUALITY";
    freshness_score: number;
    strength_score: number;
    touch_score: number;
    merge_score: number;
    raw_zone_score?: number;
    quality_cap?: number;
    zone_quality_label?: string | null;
    zone_quality_components?: Record<string, number>;
    zone_quality_component_details?: ZoneQualityComponent[];
    zone_quality_reason_codes?: string[];
    is_fresh: boolean;
    touch_count: number;
    merged_count: number;
    evidence: string[];
    explanation: ZoneExplanation;
    current_price: number;
    timeframe: string;
    base_index: number;
    base_date: string;
    status: string;
    reaction_percent?: number | null;
    reaction_started?: string | null;
    reaction_ended?: string | null;
    reaction_duration_candles?: number | null;
    zone_id?: string | null;
    lifecycle_status?: string | null;
    authenticity_status?: "AUTHENTIC" | "NON_AUTHENTIC" | null;
    authenticity_reason_code?: string | null;
    authenticity_reason?: string | null;
    test_count?: number | null;
    reaction_status?: "REACTING" | "NOT_REACTING" | null;
    reaction_percentage?: number | null;
    max_penetration_percent?: number | null;
    current_penetration_percent?: number | null;
    good_closing?: boolean | null;
    parent_zone_id?: string | null;
    is_nested?: boolean;
    is_duplicate?: boolean;
    overlap_percent?: number | null;
    dashboard_qualified?: boolean;
    qualification_reason_codes?: string[];
    departure_quality?: "EXPLOSIVE" | "STRONG" | "ACCEPTABLE" | "WEAK" | string;
    canonical_formation_departure?: "WEAK" | "STRONG" | "VERY_STRONG" | string | null;
    dashboard_qualification_departure?: "EXPLOSIVE" | "STRONG" | "ACCEPTABLE" | "WEAK" | string | null;
    base_quality?: string | null;
    formation_quality?: string | null;
    departure_displacement?: number | null;
    departure_zone_width_ratio?: number | null;
    base_candle_count?: number | null;
    base_compactness?: "EXCELLENT" | "STRONG" | "ACCEPTABLE" | "NOT_PRIMARY" | string;
    base_compactness_reason?: string | null;
    trade_confidence?: CanonicalTradeConfidence | null;
}

export interface CanonicalTradeConfidence {
    score: number;
    label: "VERY_HIGH" | "HIGH" | "MODERATE" | "LOW" | "CONFLICTED" | "INSUFFICIENT_CONTEXT";
    zone_quality_score: number;
    zone_quality_contribution: number;
    location_contribution: number;
    trend_contribution: number;
    location_alignment: string;
    trend_alignment: string;
    combined_context: string;
    htf_overlap_type: string;
    htf_direction_compatibility: string;
    data_sufficiency: "AVAILABLE" | "PARTIAL" | "INSUFFICIENT";
    reason_codes: string[];
    evidence: string[];
    shadow_mode: boolean;
}

export interface ZoneQualityComponent {
    key: string;
    score: number;
    maximum_score: number;
    evidence: string[];
    reason_codes: string[];
}

export interface ZoneStateCount {
    total: number;
    fresh: number;
    reacting: number;
    tested: number;
    retested: number;
    invalidated: number;
    authentic: number;
    non_authentic: number;
}

export interface ZoneLifecycleSummary {
    demand: ZoneStateCount;
    supply: ZoneStateCount;
}

export interface ZoneExplanationFactor {
    key: string;
    title: string;
    score: number;
    sentiment: "POSITIVE" | "NEGATIVE";
    summary: string;
    recommendation: string;
    weight: number;
}

export interface ZoneExplanation {
    overall_score: number;
    rating: number;
    label: string;
    summary: string;
    positive_factors: ZoneExplanationFactor[];
    negative_factors: ZoneExplanationFactor[];
    educational_insight: string;
}

export interface ZoneResearchResponse {
    total_scanned: number;
    total_zones: number;
    delayed: boolean;
    timeframe: string;
    results: ZoneResearchResult[];
    historical_results?: ZoneResearchResult[];
    universe: string;
    status: "completed" | "refreshing" | "queued" | "failed";
    total_symbols: number;
    processed_symbols: number;
    failed_symbols: number;
    last_completed_at: string | null;
    data_status: "delayed" | "cached" | "refreshing";
    lifecycle_summary?: ZoneLifecycleSummary | null;
    canonical_zone_count?: number;
    dashboard_qualified_count?: number;
    dashboard_rejected_count?: number;
    qualification_rejection_counts?: Record<string, number>;
    methodology_version: string;
}

export interface ZoneRuleDiagnostic {
    key: string;
    label: string;
    passed: boolean;
    actual: string | number | boolean | null;
    required: string | number | boolean | null;
}

export interface ZoneCandidateDiagnostic {
    candidate_id: string;
    symbol: string;
    timeframe: string;
    pattern: string | null;
    base_start_index: number;
    base_end_index: number;
    base_start_date: string;
    base_end_date: string;
    proximal: number;
    distal: number;
    zone_type: string | null;
    status: "accepted" | "rejected" | "invalidated";
    score: number | null;
    rejection_reasons: string[];
    rule_results: ZoneRuleDiagnostic[];
}

export interface ZoneDiagnosticsResponse {
    symbol: string;
    timeframe: string;
    candidates: ZoneCandidateDiagnostic[];
}

export interface ConfluenceZone {
    zone_id: string;
    zone_type: string;
    lower_price: number;
    upper_price: number;
    proximal_price: number;
    distal_price: number;
    quality: number;
    overlap_percent: number;
    distance_percent: number;
    freshness: string;
    retests: number;
    relationship: "FULL_OVERLAP" | "PARTIAL_OVERLAP" | "TOUCHING" | "NO_OVERLAP";
    direction: "ALIGNED" | "OPPOSING";
    reason_code: string;
}

export interface ConfluenceTimeframe {
    timeframe: string;
    timeframe_name: string;
    status: "CONFIRMED" | "PARTIAL" | "NOT_CONFIRMED";
    zone: ConfluenceZone | null;
    explanation: string;
    relationship: "FULL_OVERLAP" | "PARTIAL_OVERLAP" | "TOUCHING" | "NO_OVERLAP";
    compatibility: "ALIGNED" | "OPPOSING" | "NO_HTF_CONTEXT";
    reason_code: string;
    selection_reason: string;
}

export interface TimeframeConfluenceResponse {
    symbol: string;
    execution_timeframe: string;
    location_timeframe: string | null;
    trend_timeframe: string | null;
    trend_state: string;
    trend_alignment: "ALIGNED" | "OPPOSING" | "NEUTRAL" | "UNKNOWN";
    workflow_source: "EXPLICIT_GTF_MAPPING" | "ALPHAEDGE_DERIVED" | "NO_CANONICAL_GTF_WORKFLOW";
    canonical_trend: {
        symbol: string;
        trend_timeframe: string | null;
        trend_state: "UPTREND" | "DOWNTREND" | "SIDEWAYS" | "UNAVAILABLE";
        sma50_current: number | null;
        sma50_seven_bars_ago: number | null;
        sma_colour: "GREEN" | "RED" | "NEUTRAL" | "UNAVAILABLE";
        atr14: number | null;
        normalized_slope: number | null;
        trend_angle_degrees: number | null;
        evaluation_timestamp: string | null;
        data_sufficient: boolean;
        reason_codes: string[];
    };
    combined_context: {
        trend_state: string;
        trend_alignment: "ALIGNED" | "OPPOSING" | "NEUTRAL" | "UNKNOWN";
        location_relationship: "FULL_OVERLAP" | "PARTIAL_OVERLAP" | "TOUCHING" | "NO_OVERLAP";
        location_compatibility: "ALIGNED" | "OPPOSING" | "NO_HTF_CONTEXT";
        location_reason_code: string;
    };
    canonical_analysis: {
        symbol: string;
        execution_timeframe: string;
        trend_timeframe: string | null;
        location_timeframe: string | null;
        canonical_trend: TimeframeConfluenceResponse["canonical_trend"];
        trend_alignment: "ALIGNED" | "OPPOSING" | "NEUTRAL" | "UNKNOWN";
        htf_location: ConfluenceTimeframe | null;
        location_relationship: "FULL_OVERLAP" | "PARTIAL_OVERLAP" | "TOUCHING" | "NO_OVERLAP";
        location_compatibility: "ALIGNED" | "OPPOSING" | "NO_HTF_CONTEXT";
        reason_codes: string[];
        data_sufficient: boolean;
    };
    trade_confidence: CanonicalTradeConfidence;
    execution_zone: {
        zone_type: string;
        proximal_price: number;
        distal_price: number;
    };
    higher_timeframes: ConfluenceTimeframe[];
    confluence_score: number;
    strength: "Weak" | "Moderate" | "Strong";
    summary: string;
    source: string;
}

export interface ConfluenceChartOverlay {
    timeframe: string;
    timeframeName: string;
    zoneType: string;
    proximalPrice: number;
    distalPrice: number;
    quality: number;
    overlapPercent: number;
    distancePercent: number;
    freshness: string;
    retests: number;
    relationship: "FULL_OVERLAP" | "PARTIAL_OVERLAP" | "TOUCHING" | "NO_OVERLAP";
    direction: "ALIGNED" | "OPPOSING";
    reasonCode: string;
    zoneId: string;
}
