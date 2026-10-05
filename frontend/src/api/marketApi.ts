import axios from "axios";
import { API_BASE_URL } from "./config";

export interface MarketCandle {
    time: string;
    open: number;
    high: number;
    low: number;
    close: number;
    volume: number;
}

export interface CandleSeriesResult {
    symbol: string;
    period: string;
    interval: string;
    source: string;
    delayed: boolean;
    candles: MarketCandle[];
}

const marketApi = axios.create({
    baseURL: `${API_BASE_URL}/market`,
    timeout: 15000,
});

const candleCache = new Map<string, Promise<CandleSeriesResult>>();

export async function getMarketCandles(
    symbol: string,
    period = "1y",
    interval = "1d",
    timeframe = "1D",
    signal?: AbortSignal,
    instrumentId?: string | null,
    formationDate?: string | null,
): Promise<CandleSeriesResult> {
    const key = `${symbol}:${period}:${interval}:${timeframe}:${instrumentId ?? ""}:${formationDate ?? ""}`;
    // Background scanner enrichment is cancellable. Do not place those
    // requests in the shared cache because an opened chart must never wait on
    // an obsolete background request from a previous symbol or timeframe.
    if (signal) {
        const response = await marketApi.get<CandleSeriesResult>("/candles", {
            params: { symbol, period, interval, timeframe, instrument_id: instrumentId, formation_date: formationDate },
            signal,
        });
        return response.data;
    }
    const cached = candleCache.get(key);
    if (cached) return cached;
    const request = marketApi.get<CandleSeriesResult>("/candles", {
        params: { symbol, period, interval, timeframe, instrument_id: instrumentId, formation_date: formationDate },
    }).then((response) => response.data);
    candleCache.set(key, request);
    try {
        return await request;
    } finally {
        // Coalesce only simultaneous requests. Candle history is mutable after
        // a successful Dhan incremental update, so keeping this promise for
        // the browser session would leave an opened/reopened chart stale even
        // though the persisted chart API already contains newer sessions.
        if (candleCache.get(key) === request) candleCache.delete(key);
    }
}
