import type { ZoneQualityComponent, ZoneResearchResult } from "../../types/scanner";

export const zoneQualityComponentNames: Record<string, string> = {
    base_quality: "Base Quality",
    departure_quality: "Departure Quality",
    legout_dominance: "Leg-Out Dominance",
    structural_clearance: "Structural Clearance",
    lifecycle_quality: "Lifecycle Quality",
    authenticity_quality: "Authenticity Quality",
};

export const zoneQualityComponentHelp: Record<string, string> = {
    base_quality: "Measures how compact and balanced the Base formation is.",
    departure_quality: "Measures the strength and decisiveness of price leaving the zone.",
    legout_dominance: "Compares the strength of the departure with the arrival into the zone.",
    structural_clearance: "Measures how decisively price cleared the required formation structure.",
    lifecycle_quality: "Measures the current condition of the zone using canonical lifecycle evidence.",
    authenticity_quality: "Uses canonical authenticity evidence to assess formation integrity.",
};

export const zoneQualityReasonText: Record<string, string> = {
    LOW_BASE_BODY_RATIO: "Compact base",
    HIGHER_BASE_BODY_RATIO: "Base candles were less compact",
    WEAK_DEPARTURE: "Weak departure",
    STRONG_DEPARTURE: "Strong departure",
    VERY_STRONG_DEPARTURE: "Very strong departure",
    EXPLOSIVE_LEG_OUT: "Explosive departure",
    SIGNIFICANT_GAP: "Significant departure gap",
    HIGH_DISPLACEMENT: "Strong price displacement",
    LEG_OUT_DOMINATES: "Leg-Out strongly dominated Leg-In",
    LIMITED_LEG_OUT_DOMINANCE: "Limited Leg-Out dominance",
    DECISIVE_STRUCTURAL_CLEARANCE: "Decisive structural clearance",
    MARGINAL_STRUCTURAL_CLEARANCE: "Limited structural clearance",
    LIFECYCLE_FRESH: "Fresh zone",
    LIFECYCLE_APPROACHING: "Price is approaching the zone",
    LIFECYCLE_REACTING: "Price is reacting from the zone",
    LIFECYCLE_TESTED: "Zone has been tested",
    LIFECYCLE_RETESTED: "Zone has been retested",
    LIFECYCLE_INVALIDATED: "Zone is invalidated",
    AUTHENTIC_FORMATION: "Authentic formation",
    NON_AUTHENTIC_FORMATION: "Formation is not authentic",
    AUTHENTICITY_UNAVAILABLE: "Authenticity evidence unavailable",
    FORMATION_EVIDENCE_UNAVAILABLE: "Canonical formation evidence unavailable",
};

export function formatZoneQuality(value: number): string {
    return value.toFixed(1);
}

export function formatZoneQualityLabel(label?: string | null): string {
    if (!label) return "Weak";
    return label.charAt(0).toUpperCase() + label.slice(1).toLowerCase();
}

export function canonicalQualityComponents(result: ZoneResearchResult): ZoneQualityComponent[] {
    return result.zone_quality_component_details ?? [];
}

export function qualityReasonDescriptions(result: ZoneResearchResult): string[] {
    return (result.zone_quality_reason_codes ?? [])
        .map((code) => zoneQualityReasonText[code])
        .filter((text): text is string => Boolean(text));
}
