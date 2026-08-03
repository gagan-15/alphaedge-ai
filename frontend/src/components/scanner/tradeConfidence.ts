import type { StockDetailsBackendAnalysis } from "../../api/scannerApi";
import type { ZoneResearchResult } from "../../types/scanner";
import type { StockZoneAnalysis } from "./stockZoneAnalysis";

export type ConfidenceStatus = "PASS" | "MIXED" | "FAIL" | "UNAVAILABLE";

export interface TradeConfidenceFactor {
    key: string;
    label: string;
    weight: number;
    status: ConfidenceStatus;
    explanation: string;
}

export interface TradeConfidenceResult {
    score: number;
    recommendation: string;
    factors: TradeConfidenceFactor[];
    calculatedWeight: number;
    totalWeight: number;
}

const points = (weight: number, status: ConfidenceStatus) =>
    status === "PASS" ? weight : status === "MIXED" ? weight * .5 : 0;

export function buildTradeConfidence(
    result: ZoneResearchResult,
    analysis: StockZoneAnalysis | null,
    backend: StockDetailsBackendAnalysis | null,
): TradeConfidenceResult {
    const find = (label: string) => analysis?.checks.find((item) => item.label === label);
    const checkStatus = (label: string): ConfidenceStatus => find(label)?.status ?? "UNAVAILABLE";
    const checkReason = (label: string, fallback: string) => find(label)?.reason ?? fallback;
    const relative = backend?.nifty_comparison["3m"];
    const sector = backend?.sector.sector_vs_nifty?.["3m"];
    const ratio = backend?.trade_plan.risk_reward_ratio;
    const demand = result.zone_type === "DEMAND";
    const relativeStatus: ConfidenceStatus = relative?.difference === undefined
        ? "UNAVAILABLE"
        : demand ? relative.difference > 2 ? "PASS" : relative.difference < -2 ? "FAIL" : "MIXED"
            : relative.difference < -2 ? "PASS" : relative.difference > 2 ? "FAIL" : "MIXED";
    const sectorStatus: ConfidenceStatus = sector?.difference === undefined
        ? "UNAVAILABLE"
        : demand ? sector.difference > 2 ? "PASS" : sector.difference < -2 ? "FAIL" : "MIXED"
            : sector.difference < -2 ? "PASS" : sector.difference > 2 ? "FAIL" : "MIXED";
    const timeframeStatus: ConfidenceStatus = !backend ? "UNAVAILABLE"
        : backend.multi_timeframe.status === "CONFIRMED" ? "PASS"
            : backend.multi_timeframe.status === "MIXED" ? "MIXED" : "FAIL";
    const positionStatus: ConfidenceStatus = result.status === "IN ZONE"
        ? "PASS" : result.status === "APPROACHING" ? "MIXED" : "FAIL";
    const confirmationStatus: ConfidenceStatus = result.status === "IN ZONE"
        ? "MIXED" : result.distance_percent <= 3 ? "MIXED" : "FAIL";

    const factors: TradeConfidenceFactor[] = [
        { key: "zone", label: "Zone Quality", weight: 20, status: result.zone_score >= 75 ? "PASS" : result.zone_score >= 60 ? "MIXED" : "FAIL", explanation: `The zone itself scored ${result.zone_score.toFixed(0)} out of 100.` },
        { key: "ema", label: "EMA alignment", weight: 7, status: checkStatus("EMA alignment"), explanation: checkReason("EMA alignment", "Moving-average data is not ready.") },
        { key: "trend", label: "Trend", weight: 7, status: checkStatus("Trend confirmation"), explanation: checkReason("Trend confirmation", "Trend data is not ready.") },
        { key: "rsi", label: "RSI", weight: 5, status: checkStatus("RSI condition"), explanation: checkReason("RSI condition", "Momentum data is not ready.") },
        { key: "volume", label: "Volume", weight: 5, status: checkStatus("Volume confirmation"), explanation: checkReason("Volume confirmation", "Volume data is not ready.") },
        { key: "timeframes", label: "Higher timeframes", weight: 10, status: timeframeStatus, explanation: timeframeStatus === "PASS" ? "Daily, weekly and monthly conditions support this setup." : timeframeStatus === "UNAVAILABLE" ? "Higher-timeframe data is not ready." : "Larger timeframes do not fully support this setup." },
        { key: "sector", label: "Sector strength", weight: 7, status: sectorStatus, explanation: sectorStatus === "UNAVAILABLE" ? "The sector comparison is not available." : "The stock's sector was compared with Nifty." },
        { key: "relative", label: "Relative strength", weight: 7, status: relativeStatus, explanation: relativeStatus === "UNAVAILABLE" ? "The Nifty comparison is not available." : "The stock was compared with Nifty over three months." },
        { key: "breadth", label: "Market breadth", weight: 4, status: "UNAVAILABLE", explanation: "Live whole-market breadth is not connected yet." },
        { key: "institutions", label: "Big investor activity", weight: 4, status: "UNAVAILABLE", explanation: "Verified institutional activity data is not connected yet." },
        { key: "sentiment", label: "Market sentiment", weight: 4, status: "UNAVAILABLE", explanation: "A validated market sentiment feed is not connected yet." },
        { key: "risk", label: "Risk and reward", weight: 8, status: ratio === null || ratio === undefined ? "UNAVAILABLE" : ratio >= 2 ? "PASS" : ratio >= 1 ? "MIXED" : "FAIL", explanation: ratio === null || ratio === undefined ? "No validated opposing target is available." : `The current illustration offers 1:${ratio.toFixed(2)} risk and reward.` },
        { key: "confirmation", label: "Confirmation status", weight: 6, status: confirmationStatus, explanation: confirmationStatus === "MIXED" ? "Price is close, but a confirmation candle is still required." : "There is no confirmation candle yet." },
        { key: "position", label: "Current price position", weight: 6, status: positionStatus, explanation: result.status === "IN ZONE" ? "Price is currently inside the selected zone." : result.status === "REACTING" ? "Price has respected the zone and crossed back through its proximal boundary." : result.status === "APPROACHING" ? "Price is approaching the selected zone." : "Price is still far from the selected zone." },
    ];
    const score = Math.round(factors.reduce((sum, factor) => sum + points(factor.weight, factor.status), 0));
    const recommendation = score >= 75 ? "Ready to watch closely"
        : score >= 55 ? "Wait for confirmation"
            : "Current conditions are weak";
    return {
        score,
        recommendation,
        factors,
        calculatedWeight: factors.filter((factor) => factor.status !== "UNAVAILABLE").reduce((sum, factor) => sum + factor.weight, 0),
        totalWeight: factors.reduce((sum, factor) => sum + factor.weight, 0),
    };
}

export function explainScoreDifference(zoneQuality: number, tradeConfidence: number, zoneType: string) {
    const zoneName = zoneType === "DEMAND" ? "demand" : "supply";
    if (zoneQuality - tradeConfidence >= 20) {
        return `This is a well-formed ${zoneName} zone, but today's market conditions do not support trading it yet.`;
    }
    if (tradeConfidence - zoneQuality >= 15) {
        return `The ${zoneName} zone is not exceptional, but today's market conditions support watching this setup closely.`;
    }
    return `The ${zoneName} zone quality and today's market conditions are broadly in agreement.`;
}
