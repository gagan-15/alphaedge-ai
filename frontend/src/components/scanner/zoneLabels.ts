import type { ZoneResearchResult } from "../../types/scanner";
import { zoneIdFor } from "../../services/zoneSelectionService";

export function zoneSequenceLabel(zones: ZoneResearchResult[], index: number) {
    return zoneIdFor(zones, zones[index]);
}
