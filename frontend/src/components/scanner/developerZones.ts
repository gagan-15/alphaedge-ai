import type { ZoneCandidateDiagnostic, ZoneResearchResult, ZoneRuleDiagnostic } from "../../types/scanner";
import { zoneSequenceLabel } from "./zoneLabels";

export type DeveloperZoneStatus = "Accepted" | "Rejected" | "Invalidated";

export interface DeveloperChartZone {
    zoneId: string;
    zoneType: "DEMAND" | "SUPPLY";
    proximalPrice: number;
    distalPrice: number;
    baseIndex: number;
    pattern?: string;
    zoneStatus: DeveloperZoneStatus;
    zoneScore?: number;
    rejectionReasons?: string[];
    ruleResults?: ZoneRuleDiagnostic[];
    baseStartDate?: string;
    baseEndDate?: string;
    selected?: boolean;
}

export function diagnosticDeveloperZones(
    candidates: ZoneCandidateDiagnostic[],
    selectedZone?: ZoneResearchResult,
): DeveloperChartZone[] {
    let demand = 0;
    let supply = 0;
    return candidates.flatMap((candidate) => {
        if (candidate.zone_type !== "DEMAND" && candidate.zone_type !== "SUPPLY") {
            return [];
        }
        const isDemand = candidate.zone_type === "DEMAND";
        const sequence = isDemand ? ++demand : ++supply;
        const selected = Boolean(
            selectedZone
            && candidate.status === "accepted"
            && Math.abs(candidate.proximal - selectedZone.proximal_price) < .01
            && Math.abs(candidate.distal - selectedZone.distal_price) < .01
        );
        return [{
            zoneId: `${isDemand ? "DZ" : "SZ"}-C${sequence}`,
            zoneType: candidate.zone_type,
            proximalPrice: candidate.proximal,
            distalPrice: candidate.distal,
            baseIndex: candidate.base_start_index,
            pattern: candidate.pattern ?? undefined,
            zoneStatus: candidate.status === "accepted"
                ? "Accepted"
                : candidate.status === "invalidated" ? "Invalidated" : "Rejected",
            zoneScore: candidate.score ?? undefined,
            rejectionReasons: candidate.rejection_reasons,
            ruleResults: candidate.rule_results,
            baseStartDate: candidate.base_start_date,
            baseEndDate: candidate.base_end_date,
            selected,
        }];
    });
}

export function acceptedDeveloperZones(
    zones: ZoneResearchResult[],
    selectedZoneId?: string,
): DeveloperChartZone[] {
    return zones.map((zone, index) => {
        const zoneId = zoneSequenceLabel(zones, index);
        return {
            zoneId,
            zoneType: zone.zone_type === "DEMAND" ? "DEMAND" : "SUPPLY",
            proximalPrice: zone.proximal_price,
            distalPrice: zone.distal_price,
            baseIndex: zone.base_index,
            pattern: zone.pattern_type ?? undefined,
            zoneStatus: "Accepted",
            zoneScore: zone.zone_score,
            rejectionReasons: [],
            selected: !selectedZoneId || zoneId === selectedZoneId,
        };
    });
}
