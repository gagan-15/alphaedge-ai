/**
 * Scanner API.
 *
 * Sprint:
 *     2.64 - Scanner Results Foundation
 */

import axios from "axios";
import { API_BASE_URL } from "./config";

import type {
    ScannerResponse,
    TimeframeConfluenceResponse,
    ZoneResearchResponse,
    ZoneResearchResult,
    ZoneDiagnosticsResponse,
    PersistedZonePage,
    ScannerCapabilities,
} from "../types/scanner";
import type { MarketUniverse } from "../market-universe/MarketUniverseState";

const api = axios.create({
    baseURL: API_BASE_URL,
    timeout: 60000,
});

const researchZoneRequests = new Map<string, Promise<ZoneResearchResponse>>();

export interface InstrumentSearchResult {
    instrument_id: string;
    exchange: string;
    exchange_symbol: string;
    display_symbol: string;
    instrument_name: string;
    isin: string;
    series: string;
    is_active: number;
    provider_identifier: string;
}

export interface DhanRuntimeStatus {
    provider: "dhan";
    data_status: "READY" | "UPDATING" | "CANCELLING" | "CANCELLED" | "FAILED";
    auth_status?: "AUTH_VALID" | "AUTH_RENEWED" | "AUTH_REGENERATED" | "AUTH_REQUIRED";
    last_successful_update: string | null;
    latest_trading_date: string | null;
    last_update: {
        status: string;
        stage?: string;
        error?: string | null;
        instruments_checked?: number;
        instruments_changed?: number;
        instruments_failed?: number;
        progress_completed?: number;
        progress_total?: number;
        affected_timeframes?: string;
        started_at?: string | null;
        completed_at?: string | null;
        run_id?: number;
    };
    snapshots: Record<string, {
        snapshot_id: number;
        status: "READY" | "BUILDING" | "FAILED";
        completed_at: string | null;
        result_count: number;
    }>;
}

export async function getDhanRuntimeStatus(): Promise<DhanRuntimeStatus> {
    const response = await api.get<DhanRuntimeStatus>("/scanner/dhan-runtime-status");
    return response.data;
}

export async function startDhanIncrementalUpdate(): Promise<{ status: string; message: string }> {
    const response = await api.post<{ status: string; message: string }>(
        "/scanner/dhan-incremental-update",
        undefined,
        { headers: { "X-AlphaEdge-Update-Intent": "explicit-user" } },
    );
    return response.data;
}

export async function cancelDhanIncrementalUpdate(runId: number): Promise<{ status: string; run_id: number; message: string }> {
    const response = await api.post<{ status: string; run_id: number; message: string }>(
        `/scanner/dhan-incremental-update/${runId}/cancel`,
        undefined,
        { headers: { "X-AlphaEdge-Update-Intent": "explicit-user" } },
    );
    return response.data;
}

export async function searchInstruments(
    query: string,
    signal?: AbortSignal,
): Promise<InstrumentSearchResult[]> {
    if (!query.trim()) return [];
    const response = await api.get<{ results: InstrumentSearchResult[] }>(
        "/scanner/instruments/search",
        { params: { q: query.trim(), limit: 8 }, signal },
    );
    return response.data.results;
}

export async function getScanner(
    universe: MarketUniverse = "allindia",
    symbols: string[] = [],
): Promise<ScannerResponse> {
    try {
        const response = await api.get<ScannerResponse>(
            "/scanner/",
            { params: { universe, symbols } },
        );

        return response.data;
    } catch (error) {
        console.error(
            "Failed to fetch scanner data.",
            error,
        );

        throw error;
    }
}

export async function getScannerCapabilities(
    universe: MarketUniverse = "allindia",
): Promise<ScannerCapabilities> {
    const response = await api.get<ScannerCapabilities>("/scanner/capabilities", {
        params: { universe },
    });
    return response.data;
}

export async function getPersistedZonePage(params: {
    timeframe: string;
    universe: MarketUniverse;
    symbols?: string[];
    zoneType?: string;
    pattern?: string;
    minimumQuality?: number;
    status?: string;
    maxDistance?: number;
    symbol?: string;
    sort?: string;
    descending?: boolean;
    page?: number;
    pageSize?: number;
}): Promise<PersistedZonePage> {
    const response = await api.get<PersistedZonePage>("/scanner/persisted-zones", {
        params: {
            timeframe: params.timeframe,
            universe: params.universe,
            symbols: params.symbols,
            zone_type: params.zoneType,
            pattern: params.pattern,
            min_zone_quality: params.minimumQuality,
            status: params.status,
            max_distance: params.maxDistance,
            symbol: params.symbol,
            sort: params.sort,
            descending: params.descending,
            page: params.page ?? 1,
            page_size: params.pageSize ?? 14,
        },
    });
    return response.data;
}

export async function getResearchZones(
    timeframe = "DAILY",
    universe: MarketUniverse = "allindia",
    symbols: string[] = [],
    includeResults = true,
): Promise<ZoneResearchResponse> {
    const requestKey = `${timeframe}:${universe}:${symbols.join(",")}:${includeResults}`;
    const active = researchZoneRequests.get(requestKey);
    if (active) return active;
    const request = api.get<ZoneResearchResponse>("/scanner/zones", {
        params: { timeframe, universe, symbols, include_results: includeResults },
    }).then((response) => response.data).finally(() => {
        researchZoneRequests.delete(requestKey);
    });
    researchZoneRequests.set(requestKey, request);
    return request;
}

export interface ComparisonPeriod {
    stock_return?: number;
    benchmark_return?: number;
    difference?: number;
    status: string;
}

export interface StockDetailsBackendAnalysis {
    symbol: string;
    selected_zone: {
        symbol: string;
        zone_type: string;
        proximal_price: number;
        distal_price: number;
        timeframe: string;
    };
    source: string;
    nifty_comparison: Record<string, ComparisonPeriod>;
    sector: {
        name: string;
        benchmark: string | null;
        status?: string;
        comparison?: Record<string, ComparisonPeriod>;
        sector_vs_nifty?: Record<string, ComparisonPeriod>;
    };
    multi_timeframe: {
        status: string;
        frames: Array<{ timeframe: string; trend: string; ema_alignment: string; confirmation: string }>;
    };
    trade_plan: {
        selected_zone_id: string;
        symbol: string;
        timeframe: string;
        snapshot_id: string;
        methodology_version: string;
        zone_type: string;
        status: "COMPLETE_STRUCTURAL" | "PARTIAL" | "UNAVAILABLE";
        interaction_range: [number, number] | null;
        planned_entry_reference: number | null;
        structural_invalidation: number | null;
        target: number | null;
        target_zone_id: string | null;
        available_room: number | null;
        structural_reward_per_share: number | null;
        distance_entry_to_structural_invalidation: number | null;
        protective_stop: number | null;
        protective_stop_status: "POLICY_NOT_DEFINED";
        risk_per_share: number | null;
        risk_reward: number | null;
        /** Deprecated compatibility field; canonical structural plans omit it. */
        risk_reward_ratio?: number | null;
        reason_codes: string[];
        research_only: boolean;
    };
}

export async function getStockDetailsAnalysis(result: {
    symbol: string;
    zone_type: string;
    proximal_price: number;
    distal_price: number;
    timeframe: string;
}, signal?: AbortSignal): Promise<StockDetailsBackendAnalysis> {
    const response = await api.get<StockDetailsBackendAnalysis>(`/scanner/zones/${encodeURIComponent(result.symbol)}/analysis`, {
        params: {
            zone_type: result.zone_type,
            proximal_price: result.proximal_price,
            distal_price: result.distal_price,
            timeframe: result.timeframe,
        },
        signal,
    });
    return response.data;
}

export async function getTimeframeConfluence(
    result: ZoneResearchResult,
): Promise<TimeframeConfluenceResponse> {
    const response = await api.get<TimeframeConfluenceResponse>(
        `/scanner/zones/${encodeURIComponent(result.symbol)}/confluence`,
        {
            params: {
                execution_timeframe: result.timeframe,
                zone_type: result.zone_type,
                proximal_price: result.proximal_price,
                distal_price: result.distal_price,
                refresh_key: result.base_date,
                zone_quality_score: result.zone_score,
            },
        },
    );
    return response.data;
}

const diagnosticTimeframeNames: Record<string, string> = {
    "5m": "MINUTE_5",
    "15m": "MINUTE_15",
    "75m": "MINUTE_75",
    "125m": "MINUTE_125",
    "1H": "HOUR_1",
    "2H": "HOUR_2",
    "4H": "HOUR_4",
    "6H": "HOUR_6",
    "1D": "DAILY",
    "1W": "WEEKLY",
    "1M": "MONTHLY",
    "3M": "QUARTERLY",
    "6M": "HALFYEARLY",
    "1Y": "YEARLY",
};

export async function getZoneDiagnostics(
    symbol: string,
    timeframe: string,
): Promise<ZoneDiagnosticsResponse> {
    const response = await api.get<ZoneDiagnosticsResponse>(
        `/scanner/zones/${encodeURIComponent(symbol)}/diagnostics`,
        { params: { timeframe: diagnosticTimeframeNames[timeframe] ?? "DAILY" } },
    );
    return response.data;
}
