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
    universe: string;
    status: "completed" | "refreshing" | "queued" | "failed";
    total_symbols: number;
    processed_symbols: number;
    failed_symbols: number;
    last_completed_at: string | null;
    data_status: "delayed" | "cached" | "refreshing";
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
}

export interface ConfluenceTimeframe {
    timeframe: string;
    timeframe_name: string;
    status: "CONFIRMED" | "PARTIAL" | "NOT_CONFIRMED";
    zone: ConfluenceZone | null;
    explanation: string;
}

export interface TimeframeConfluenceResponse {
    symbol: string;
    execution_timeframe: string;
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
}
