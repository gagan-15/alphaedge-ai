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
    proximal_price: number;
    distal_price: number;
    distance_percent: number;
    zone_score: number;
    score_kind: "RULE_BASED_QUALITY";
    freshness_score: number;
    strength_score: number;
    touch_score: number;
    merge_score: number;
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
    results: ZoneResearchResult[];
}
