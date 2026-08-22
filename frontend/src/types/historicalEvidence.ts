export const HISTORICAL_EVIDENCE_VERSION = "milestone-9c.1";

export interface EvidenceMetric {
    numerator: number;
    denominator: number;
    percent: number | null;
}

export interface HistoricalEvidenceMetadata {
    historical_evidence_version: string;
    methodology_fingerprint: string;
    methodology?: Record<string, unknown>;
    dataset_period: { start: string; end: string };
    record_count: number;
    trade_confidence_counts: Record<string, number>;
    supported_timeframes?: string[];
    source_universe?: string;
}

export interface HistoricalEvidenceSummary {
    historical_evidence_version: string;
    methodology_fingerprint: string;
    historical_zones: number;
    interacted_zones: number;
    interaction_rate: EvidenceMetric;
    reaction_1_zone_width: EvidenceMetric;
    reaction_2_zone_width: EvidenceMetric;
    reaction_3_zone_width: EvidenceMetric;
    reaction_5_zone_width: EvidenceMetric;
    structural_survival: EvidenceMetric;
    structural_target_availability: EvidenceMetric;
    structural_target_achievement: EvidenceMetric;
    median_mfe_zone_width: number | null;
    median_mae_zone_width: number | null;
    reliability: string;
    empty_cohort: boolean;
}

export interface HistoricalEvidenceZone {
    zone_id: string;
    symbol: string;
    timeframe: string;
    pattern: string;
    zone_type: string;
    planning_timestamp: string;
    planning_year: number;
    zone_low: number;
    zone_high: number;
    lifecycle_status: string;
    authenticity_status: string;
    interacted: number;
    mfe_zone_width: number | null;
    mae_zone_width: number | null;
    zone_quality_score: number | null;
    zone_quality_label: string | null;
    trade_confidence_score: number | null;
    trade_confidence_label: string | null;
}

export interface HistoricalEvidenceZonesPage {
    historical_evidence_version: string;
    methodology_fingerprint: string;
    total: number;
    page: number;
    page_size: number;
    total_pages: number;
    items: HistoricalEvidenceZone[];
}

export interface HistoricalEvidenceFilters {
    timeframe: string;
    zoneType: string;
    pattern: string;
    zoneQuality: string;
    tradeConfidence: string;
    year: string;
    symbol: string;
    interactionStatus: string;
}

export interface ComparableZoneInputs {
    zone_id: string;
    timeframe: string;
    zone_type: string;
    pattern: string;
    zone_quality_label: string;
    trade_confidence_label: string;
    current_methodology_version: string;
}

export interface ComparableHistoricalEvidence {
    status: "AVAILABLE" | "UNSUPPORTED_TIMEFRAME" | "NO_COMPARABLE_HISTORICAL_EVIDENCE";
    historical_evidence_version: string;
    methodology_fingerprint: string;
    current_zone: ComparableZoneInputs;
    selected_match_level: 1 | 2 | 3 | null;
    exact_level_1: { historical_zones: number; interacted_zones: number } | null;
    selected_cohort: { historical_zones: number; interacted_zones: number } | null;
    reliability: string;
    applied_cohort_definition: Record<string, string> | null;
    summary_metrics: HistoricalEvidenceSummary | null;
    explanation: string;
}
