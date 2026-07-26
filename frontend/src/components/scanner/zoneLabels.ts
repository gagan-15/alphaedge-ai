import type { ZoneResearchResult } from "../../types/scanner";

export function zoneSequenceLabel(zones: ZoneResearchResult[], index: number) {
    const zone = zones[index];
    const prefix = zone.zone_type === "DEMAND" ? "DZ" : "SZ";
    const sequence = zones
        .slice(0, index + 1)
        .filter((item) => item.zone_type === zone.zone_type)
        .length;
    return `${prefix}${sequence}`;
}
