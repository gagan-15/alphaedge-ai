import type { StockDetailsBackendAnalysis } from "../../api/scannerApi";
import type { ZoneResearchResult } from "../../types/scanner";
import type { StockZoneAnalysis } from "./stockZoneAnalysis";
import { buildTradeConfidence, type TradeConfidenceResult } from "./tradeConfidence";

export const LEGACY_AI_SCORE_AUDIT_ONLY = "LEGACY_AI_SCORE_AUDIT_ONLY" as const;

export interface LegacyAiScoreAuditRecord {
    kind: typeof LEGACY_AI_SCORE_AUDIT_ONLY;
    zoneIdentity: string;
    score: number;
    result: TradeConfidenceResult;
}

export function canonicalZoneIdentity(result: ZoneResearchResult): string {
    return [
        result.symbol.trim().toUpperCase(),
        result.timeframe.trim().toUpperCase(),
        result.zone_type.trim().toUpperCase(),
        (result.pattern_type ?? "UNKNOWN").trim().toUpperCase(),
        result.proximal_price.toFixed(8),
        result.distal_price.toFixed(8),
        result.base_date,
        result.zone_id ?? result.base_index,
    ].join(":");
}

/** Audit wrapper only; the legacy evaluator and all of its weights stay unchanged. */
export function captureLegacyAiScore(
    result: ZoneResearchResult,
    analysis: StockZoneAnalysis | null,
    backend: StockDetailsBackendAnalysis | null,
): LegacyAiScoreAuditRecord {
    const legacy = buildTradeConfidence(result, analysis, backend);
    return {
        kind: LEGACY_AI_SCORE_AUDIT_ONLY,
        zoneIdentity: canonicalZoneIdentity(result),
        score: legacy.score,
        result: legacy,
    };
}
