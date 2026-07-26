import type { MarketCandle } from "../../api/marketApi";
import type { ZoneResearchResult } from "../../types/scanner";

export type CheckStatus = "PASS" | "FAIL" | "MIXED" | "UNAVAILABLE";
export interface AnalysisCheck {
    label: string;
    status: CheckStatus;
    value: string;
    threshold: string;
    reason: string;
    scoreEffect: string;
}

export interface StockZoneAnalysis {
    ema20: number | null;
    ema50: number | null;
    ema200: number | null;
    emaAlignment: string;
    rsi14: number | null;
    rsiDirection: string;
    atr14: number | null;
    currentVolume: number | null;
    averageVolume20: number | null;
    relativeVolume: number | null;
    volumeConfirmation: boolean | null;
    pressure: string;
    shortTrend: string;
    mediumTrend: string;
    longTrend: string;
    overallTrend: string;
    retests: number;
    firstRetest: string | null;
    latestRetest: string | null;
    maximumPenetration: number;
    broken: boolean;
    position: string;
    checks: AnalysisCheck[];
}

function finite(value: number | undefined | null): number | null {
    return value !== null && value !== undefined && Number.isFinite(value) ? value : null;
}

function ema(values: number[], period: number): number | null {
    if (values.length < period) return null;
    const multiplier = 2 / (period + 1);
    let value = values.slice(0, period).reduce((sum, item) => sum + item, 0) / period;
    for (const item of values.slice(period)) value = item * multiplier + value * (1 - multiplier);
    return finite(value);
}

function rsi(values: number[], period = 14): number | null {
    if (values.length <= period) return null;
    let gains = 0;
    let losses = 0;
    for (let index = values.length - period; index < values.length; index += 1) {
        const change = values[index] - values[index - 1];
        if (change >= 0) gains += change;
        else losses -= change;
    }
    if (losses === 0) return 100;
    return finite(100 - 100 / (1 + gains / losses));
}

function atr(candles: MarketCandle[], period = 14): number | null {
    if (candles.length <= period) return null;
    const ranges = candles.slice(-period).map((candle, index, recent) => {
        const previous = index === 0 ? candles[candles.length - period - 1].close : recent[index - 1].close;
        return Math.max(candle.high - candle.low, Math.abs(candle.high - previous), Math.abs(candle.low - previous));
    });
    return finite(ranges.reduce((sum, value) => sum + value, 0) / ranges.length);
}

function trend(closes: number[], lookback: number): string {
    if (closes.length <= lookback) return "Insufficient history";
    const change = (closes.at(-1)! - closes.at(-(lookback + 1))!) / closes.at(-(lookback + 1))! * 100;
    if (change > 2) return "Rising";
    if (change < -2) return "Falling";
    return "Sideways";
}

function check(label: string, status: CheckStatus, value: string, threshold: string, reason: string, scoreEffect = "Not included in the current zone-only score"): AnalysisCheck {
    return { label, status, value, threshold, reason, scoreEffect };
}

export function analyzeStockZone(result: ZoneResearchResult, candles: MarketCandle[]): StockZoneAnalysis {
    const valid = candles.filter((candle) => [candle.open, candle.high, candle.low, candle.close].every(Number.isFinite));
    const closes = valid.map((candle) => candle.close);
    const ema20 = ema(closes, 20);
    const ema50 = ema(closes, 50);
    const ema200 = ema(closes, 200);
    const rsi14 = rsi(closes);
    const priorRsi = rsi(closes.slice(0, -3));
    const atr14 = atr(valid);
    const volumeValues = valid.map((candle) => candle.volume).filter((value) => Number.isFinite(value) && value > 0);
    const currentVolume = finite(valid.at(-1)?.volume);
    const averageVolume20 = volumeValues.length >= 20 ? volumeValues.slice(-20).reduce((sum, value) => sum + value, 0) / 20 : null;
    const relativeVolume = currentVolume && averageVolume20 ? currentVolume / averageVolume20 : null;
    const demand = result.zone_type === "DEMAND";
    const lower = Math.min(result.distal_price, result.proximal_price);
    const upper = Math.max(result.distal_price, result.proximal_price);
    const width = upper - lower;
    // The detector's base index points at zone creation. The next three candles
    // form the departure window, so they cannot also be counted as retests.
    const afterBase = valid.slice(Math.min(result.base_index + 4, valid.length));
    const touches = afterBase.filter((candle) => candle.low <= upper && candle.high >= lower);
    const penetrations = touches.map((candle) => demand ? (upper - candle.low) / width * 100 : (candle.high - lower) / width * 100);
    const broken = afterBase.some((candle) => demand ? candle.close < lower : candle.close > upper);
    const latest = valid.at(-1)?.close ?? result.current_price;
    const distance = latest > upper ? (latest - upper) / latest * 100 : latest < lower ? (lower - latest) / latest * 100 : 0;
    const position = broken ? "Invalidated" : latest >= lower && latest <= upper ? "Inside zone" : distance <= 5 ? "Approaching" : "Too far";
    const emaAlignment = ema20 === null || ema50 === null ? "Insufficient history" :
        demand ? (ema20 > ema50 && (ema200 === null || ema50 > ema200) ? "Bullish" : "Mixed") :
            (ema20 < ema50 && (ema200 === null || ema50 < ema200) ? "Bearish" : "Mixed");
    const recent = valid.slice(-20);
    const upVolume = recent.filter((candle) => candle.close >= candle.open).reduce((sum, candle) => sum + Math.max(0, candle.volume), 0);
    const downVolume = recent.filter((candle) => candle.close < candle.open).reduce((sum, candle) => sum + Math.max(0, candle.volume), 0);
    const pressure = !volumeValues.length ? "Unavailable with the current data source" :
        upVolume > downVolume * 1.15 ? "Buyers stronger (price-and-volume estimate)" :
            downVolume > upVolume * 1.15 ? "Sellers stronger (price-and-volume estimate)" : "Balanced (price-and-volume estimate)";
    const shortTrend = trend(closes, 10);
    const mediumTrend = trend(closes, 30);
    const longTrend = trend(closes, 100);
    const trendVotes = [shortTrend, mediumTrend, longTrend];
    const overallTrend = trendVotes.filter((value) => value === "Rising").length >= 2 ? "Rising" :
        trendVotes.filter((value) => value === "Falling").length >= 2 ? "Falling" : "Mixed or sideways";
    const directionTrendPass = demand ? overallTrend === "Rising" : overallTrend === "Falling";
    const rsiPass = rsi14 !== null && (demand ? rsi14 >= 40 && rsi14 <= 70 : rsi14 >= 30 && rsi14 <= 60);
    const volumeConfirmation = relativeVolume === null ? null : relativeVolume >= 1.2;
    const checks: AnalysisCheck[] = [
        check("Fresh zone", result.is_fresh && touches.length === 0 ? "PASS" : "FAIL", `${touches.length} later wick intersection(s)`, "No later candle wick may enter the zone", touches.length ? "Quality reduced" : "Supports quality"),
        check("Strong departure", result.strength_score >= 24.5 ? "PASS" : "FAIL", `${result.strength_score.toFixed(1)} / 35`, "At least 24.5 / 35", result.strength_score >= 24.5 ? "Supports quality" : "Quality reduced"),
        check("Few retests", touches.length <= 1 ? "PASS" : "FAIL", `${touches.length} later wick intersection(s)`, "No more than one", touches.length <= 1 ? "Supports quality" : "Quality reduced"),
        check("Extra zone support", result.merge_score >= 7.5 ? "PASS" : result.merge_score > 0 ? "MIXED" : "FAIL", `${result.merge_score.toFixed(1)} / 15`, "At least 7.5 / 15", result.merge_score >= 7.5 ? "Supports quality" : "Limited support"),
        check("EMA alignment", ema20 === null || ema50 === null ? "UNAVAILABLE" : emaAlignment === "Mixed" ? "MIXED" : "PASS", emaAlignment, demand ? "EMA 20 above EMA 50 for demand" : "EMA 20 below EMA 50 for supply", "Context only"),
        check("Volume confirmation", volumeConfirmation === null ? "UNAVAILABLE" : volumeConfirmation ? "PASS" : "FAIL", relativeVolume === null ? "Volume unavailable from source" : `${relativeVolume.toFixed(2)}× 20-period average`, "At least 1.20×", "Context only"),
        check("RSI condition", rsi14 === null ? "UNAVAILABLE" : rsiPass ? "PASS" : "MIXED", rsi14 === null ? "Insufficient candle history" : rsi14.toFixed(1), demand ? "40 to 70 for demand context" : "30 to 60 for supply context", "Context only"),
        check("Trend confirmation", directionTrendPass ? "PASS" : overallTrend.includes("Mixed") ? "MIXED" : "FAIL", overallTrend, demand ? "Rising trend supports demand" : "Falling trend supports supply", "Context only"),
        check("Current-zone validity", broken ? "FAIL" : "PASS", position, "No candle close beyond the distal line", broken ? "Strong score must not be used" : "Zone remains active"),
        check("Sector strength", "UNAVAILABLE", "Sector benchmark not mapped", "Requires a maintained symbol-to-sector benchmark map", "Not scored"),
        check("Relative strength", "UNAVAILABLE", "Nifty comparison not loaded", "Requires aligned Nifty history", "Not scored"),
        check("Risk and reward", "UNAVAILABLE", "No validated opposing target zone", "Requires nearest opposing zone or confirmed structure target", "Not scored"),
        check("Multiple timeframes", "UNAVAILABLE", "Other timeframe analyses not loaded", "Requires aligned daily, weekly and monthly calculations", "Not scored"),
    ];
    return {
        ema20, ema50, ema200, emaAlignment, rsi14,
        rsiDirection: rsi14 === null || priorRsi === null ? "Insufficient history" : rsi14 > priorRsi ? "Rising" : rsi14 < priorRsi ? "Falling" : "Flat",
        atr14, currentVolume, averageVolume20, relativeVolume, volumeConfirmation, pressure,
        shortTrend, mediumTrend, longTrend, overallTrend,
        retests: touches.length,
        firstRetest: touches.at(0)?.time ?? null,
        latestRetest: touches.at(-1)?.time ?? null,
        maximumPenetration: penetrations.length ? Math.max(...penetrations) : 0,
        broken, position, checks,
    };
}
