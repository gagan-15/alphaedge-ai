/**
 * Scanner API.
 *
 * Sprint:
 *     2.64 - Scanner Results Foundation
 */

import axios from "axios";
import { API_BASE_URL } from "./config";

import type { ScannerResponse, ZoneResearchResponse } from "../types/scanner";

const api = axios.create({
    baseURL: API_BASE_URL,
    timeout: 60000,
});

const researchZoneRequests = new Map<string, Promise<ZoneResearchResponse>>();

export async function getScanner(): Promise<ScannerResponse> {
    try {
        const response = await api.get<ScannerResponse>(
            "/scanner/",
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

export async function getResearchZones(timeframe = "DAILY"): Promise<ZoneResearchResponse> {
    const active = researchZoneRequests.get(timeframe);
    if (active) return active;
    const request = api.get<ZoneResearchResponse>("/scanner/zones", {
        params: { timeframe },
    }).then((response) => response.data).finally(() => {
        researchZoneRequests.delete(timeframe);
    });
    researchZoneRequests.set(timeframe, request);
    return request;
}

export interface ComparisonPeriod {
    stock_return?: number;
    benchmark_return?: number;
    difference?: number;
    status: string;
}

export interface StockDetailsBackendAnalysis {
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
        entry_range: [number, number];
        illustrative_entry: number;
        invalidation_stop: number;
        stop_buffer_rule: string;
        target: number | null;
        target_basis: string;
        risk_per_share: number;
        reward_per_share: number | null;
        risk_reward_ratio: number | null;
        distance_to_entry_percent: number;
        research_only: boolean;
    };
}

export async function getStockDetailsAnalysis(symbol: string, zoneType: string, baseIndex: number): Promise<StockDetailsBackendAnalysis> {
    const response = await api.get<StockDetailsBackendAnalysis>(`/scanner/zones/${encodeURIComponent(symbol)}/analysis`, {
        params: { zone_type: zoneType, base_index: baseIndex },
    });
    return response.data;
}
