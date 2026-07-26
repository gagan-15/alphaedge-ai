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
): Promise<CandleSeriesResult> {
    const key = `${symbol}:${period}:${interval}:${timeframe}`;
    const cached = candleCache.get(key);
    if (cached) return cached;
    const request = marketApi.get<CandleSeriesResult>("/candles", {
        params: { symbol, period, interval, timeframe },
    }).then((response) => response.data).catch((error) => {
        candleCache.delete(key);
        throw error;
    });
    candleCache.set(key, request);
    return request;
}
