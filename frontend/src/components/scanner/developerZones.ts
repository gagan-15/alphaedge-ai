import type { ZoneResearchResult } from "../../types/scanner";
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
    selected?: boolean;
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

