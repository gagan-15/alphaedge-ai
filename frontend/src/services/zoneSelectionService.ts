import type { ZoneResearchResult } from "../types/scanner";

export function zoneIdentity(zone: ZoneResearchResult) {
    return [
        zone.symbol,
        zone.timeframe,
        zone.zone_type,
        zone.base_date,
        zone.proximal_price,
        zone.distal_price,
    ].join(":");
}

export function zoneIdMap(zones: ZoneResearchResult[]) {
    const mapping = new Map<string, string>();
    (["DEMAND", "SUPPLY"] as const).forEach((type) => {
        zones
            .filter((zone) => zone.zone_type === type)
            .sort((left, right) =>
                left.base_date.localeCompare(right.base_date)
                || left.proximal_price - right.proximal_price
            )
            .forEach((zone, index) => {
                mapping.set(zoneIdentity(zone), `${type === "DEMAND" ? "DZ" : "SZ"}${index + 1}`);
            });
    });
    return mapping;
}

export function zoneIdFor(zones: ZoneResearchResult[], zone: ZoneResearchResult) {
    return zoneIdMap(zones).get(zoneIdentity(zone)) ?? (zone.zone_type === "DEMAND" ? "DZ?" : "SZ?");
}

export function selectZoneById(zones: ZoneResearchResult[], selectedZoneId: string) {
    return zones.find((zone) => zoneIdFor(zones, zone) === selectedZoneId) ?? null;
}
