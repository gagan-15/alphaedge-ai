import type { CanonicalTradeConfidence, ZoneResearchResult } from "../../types/scanner";

const labelText: Record<CanonicalTradeConfidence["label"], string> = {
    VERY_HIGH: "Very High", HIGH: "High", MODERATE: "Moderate", LOW: "Low",
    CONFLICTED: "Conflicted", INSUFFICIENT_CONTEXT: "Insufficient Context",
};

export function tradeConfidenceBucket(value: CanonicalTradeConfidence | null | undefined): number {
    if (!value || value.data_sufficiency === "INSUFFICIENT" || value.label === "INSUFFICIENT_CONTEXT") return 7;
    if (value.label === "CONFLICTED") return 6;
    if (value.label === "LOW") return 5;
    if (value.data_sufficiency === "PARTIAL") return value.label === "MODERATE" ? 4 : 3;
    if (value.label === "VERY_HIGH") return 0;
    if (value.label === "HIGH") return 1;
    return 2;
}

export function stableZoneIdentity(zone: ZoneResearchResult): string {
    return zone.zone_id ?? [zone.symbol, zone.timeframe, zone.zone_type, zone.pattern_type ?? "", zone.base_index, zone.proximal_price, zone.distal_price].join(":");
}

export function compareCanonicalTradeConfidence(left: ZoneResearchResult, right: ZoneResearchResult): number {
    return tradeConfidenceBucket(left.trade_confidence) - tradeConfidenceBucket(right.trade_confidence)
        || (right.trade_confidence?.score ?? -1) - (left.trade_confidence?.score ?? -1)
        || right.zone_score - left.zone_score
        || (left.distance_percent ?? Number.POSITIVE_INFINITY) - (right.distance_percent ?? Number.POSITIVE_INFINITY)
        || stableZoneIdentity(left).localeCompare(stableZoneIdentity(right));
}

export function tradeConfidenceDisplay(value: CanonicalTradeConfidence | null | undefined) {
    if (!value || value.data_sufficiency === "INSUFFICIENT" || value.label === "INSUFFICIENT_CONTEXT") return { score: "—", label: "Insufficient Context" };
    return { score: value.score.toFixed(1), label: labelText[value.label] };
}

export function tradeConfidenceExplanation(value: CanonicalTradeConfidence | null | undefined): string {
    if (!value || value.data_sufficiency === "INSUFFICIENT" || value.label === "INSUFFICIENT_CONTEXT") return "Insufficient higher-timeframe context to assess confidence.";
    if (value.label === "CONFLICTED") return "Conflicting higher-timeframe or trend evidence.";
    if (value.data_sufficiency === "PARTIAL") return "Some higher-timeframe context is unavailable.";
    if (value.label === "VERY_HIGH") return "Strong zone with strong higher-timeframe and trend support.";
    if (value.label === "HIGH") return "Strong contextual support.";
    if (value.label === "MODERATE") return "Mixed or neutral contextual support.";
    return "Current higher-timeframe and trend support is weak.";
}
