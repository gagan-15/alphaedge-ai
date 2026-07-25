import axios from "axios";

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
    baseURL: "http://127.0.0.1:8000/market",
    timeout: 15000,
});

export async function getMarketCandles(
    symbol: string,
    period = "1y",
    interval = "1d",
): Promise<CandleSeriesResult> {
    const response = await marketApi.get<CandleSeriesResult>("/candles", {
        params: { symbol, period, interval },
    });
    return response.data;
}
