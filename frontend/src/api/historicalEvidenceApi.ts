import axios from "axios";

import { API_BASE_URL } from "./config";
import type {
    HistoricalEvidenceFilters,
    HistoricalEvidenceMetadata,
    HistoricalEvidenceSummary,
    HistoricalEvidenceZonesPage,
    ComparableHistoricalEvidence,
    ComparableZoneInputs,
} from "../types/historicalEvidence";
import { HISTORICAL_EVIDENCE_VERSION } from "../types/historicalEvidence";

const evidenceApi = axios.create({ baseURL: `${API_BASE_URL}/historical-evidence` });
const comparableRequests = new Map<string, Promise<ComparableHistoricalEvidence>>();

export function evidenceQuery(filters: HistoricalEvidenceFilters) {
    return {
        dataset_version: HISTORICAL_EVIDENCE_VERSION,
        timeframe: filters.timeframe || undefined,
        zone_type: filters.zoneType || undefined,
        pattern: filters.pattern || undefined,
        zone_quality_label: filters.zoneQuality || undefined,
        trade_confidence_label: filters.tradeConfidence || undefined,
        year: filters.year || undefined,
        symbol: filters.symbol.trim() || undefined,
        interaction_status: filters.interactionStatus || "ALL",
    };
}

export async function getHistoricalEvidenceMetadata() {
    const response = await evidenceApi.get<HistoricalEvidenceMetadata>("/metadata", {
        params: { dataset_version: HISTORICAL_EVIDENCE_VERSION },
    });
    return response.data;
}

export async function getHistoricalEvidenceSummary(filters: HistoricalEvidenceFilters) {
    const response = await evidenceApi.get<HistoricalEvidenceSummary>("/summary", {
        params: evidenceQuery(filters),
    });
    return response.data;
}

export async function getHistoricalEvidenceZones(
    filters: HistoricalEvidenceFilters,
    page: number,
    pageSize: number,
    sortBy: string,
    sortDirection: "asc" | "desc",
) {
    const response = await evidenceApi.get<HistoricalEvidenceZonesPage>("/zones", {
        params: {
            ...evidenceQuery(filters),
            page,
            page_size: pageSize,
            sort_by: sortBy,
            sort_direction: sortDirection,
        },
    });
    return response.data;
}

export function getComparableHistoricalEvidence(inputs: ComparableZoneInputs) {
    const key = JSON.stringify([HISTORICAL_EVIDENCE_VERSION, ...Object.values(inputs)]);
    const cached = comparableRequests.get(key);
    if (cached) return cached;
    const request = evidenceApi.get<ComparableHistoricalEvidence>("/comparable-zone", {
        params: {
            dataset_version: HISTORICAL_EVIDENCE_VERSION,
            zone_id: inputs.zone_id,
            timeframe: inputs.timeframe,
            zone_type: inputs.zone_type,
            pattern: inputs.pattern,
            zone_quality_label: inputs.zone_quality_label,
            trade_confidence_label: inputs.trade_confidence_label,
            current_methodology_version: inputs.current_methodology_version,
        },
    }).then((response) => response.data).catch((error) => {
        comparableRequests.delete(key);
        throw error;
    });
    comparableRequests.set(key, request);
    return request;
}

export function historicalEvidenceErrorMessage(error: unknown) {
    if (axios.isAxiosError(error)) {
        const detail = error.response?.data?.detail;
        if (typeof detail === "string") return detail;
        if (!error.response) return "Historical evidence could not be reached. Check that the backend is running.";
    }
    return "Historical evidence could not be loaded.";
}
