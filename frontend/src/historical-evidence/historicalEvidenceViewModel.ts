import type { EvidenceMetric, HistoricalEvidenceFilters } from "../types/historicalEvidence";

export const DEFAULT_EVIDENCE_FILTERS: HistoricalEvidenceFilters = {
    timeframe: "",
    zoneType: "",
    pattern: "",
    zoneQuality: "",
    tradeConfidence: "",
    year: "",
    symbol: "",
    interactionStatus: "ALL",
};

export const ZONE_QUALITY_LABELS = ["ELITE", "STRONG", "GOOD", "AVERAGE", "MODERATE", "WEAK"];
export const TRADE_CONFIDENCE_LABELS = ["VERY_HIGH", "HIGH", "MODERATE", "LOW", "CONFLICTED", "INSUFFICIENT_CONTEXT"];

export function metricText(metric: EvidenceMetric) {
    if (metric.percent === null) return "Unavailable";
    return `${metric.percent.toFixed(2)}%`;
}

export function reliabilityLabel(value: string) {
    return value.toLowerCase().replaceAll("_", " ").replace(/^./, (letter) => letter.toUpperCase());
}

export function readFilters(searchParams: URLSearchParams): HistoricalEvidenceFilters {
    return {
        timeframe: searchParams.get("timeframe") ?? "",
        zoneType: searchParams.get("zone_type") ?? "",
        pattern: searchParams.get("pattern") ?? "",
        zoneQuality: searchParams.get("zone_quality") ?? "",
        tradeConfidence: searchParams.get("trade_confidence") ?? "",
        year: searchParams.get("year") ?? "",
        symbol: searchParams.get("symbol") ?? "",
        interactionStatus: searchParams.get("interaction_status") ?? "ALL",
    };
}

export function writeFilters(filters: HistoricalEvidenceFilters) {
    const params = new URLSearchParams();
    const mapping: Array<[keyof HistoricalEvidenceFilters, string]> = [
        ["timeframe", "timeframe"], ["zoneType", "zone_type"], ["pattern", "pattern"],
        ["zoneQuality", "zone_quality"], ["tradeConfidence", "trade_confidence"],
        ["year", "year"], ["symbol", "symbol"], ["interactionStatus", "interaction_status"],
    ];
    mapping.forEach(([key, query]) => {
        const value = filters[key];
        if (value && !(key === "interactionStatus" && value === "ALL")) params.set(query, value);
    });
    return params;
}
