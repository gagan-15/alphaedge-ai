import type { DashboardResult, MarketOverviewResult } from "../types/dashboard";

export type MarketDirection = "Bullish" | "Bearish" | "Neutral";
export type MarketRisk = "Low Risk" | "Moderate Risk" | "High Risk";

export interface MarketIntelligenceSnapshot {
    market: MarketOverviewResult | null;
    marketHealth: "Looking Healthy" | "Mixed" | "Weak Momentum";
    marketRegime: "Strong Rise" | "Sideways" | "Strong Fall";
    marketBreadth: number;
    sectorLeadership: string[];
    riskLevel: MarketRisk;
    aiConfidence: number;
    volatility: "Low" | "Moderate" | "High";
    participation: number;
    marketDirection: MarketDirection;
    todayStrategy: string;
    marketStatus: "Open" | "Closed" | "Pre Open";
}

export const emptyMarketIntelligence: MarketIntelligenceSnapshot = {
    market: null,
    marketHealth: "Mixed",
    marketRegime: "Sideways",
    marketBreadth: 0,
    sectorLeadership: [],
    riskLevel: "Moderate Risk",
    aiConfidence: 0,
    volatility: "Moderate",
    participation: 0,
    marketDirection: "Neutral",
    todayStrategy: "Wait for clearer market conditions.",
    marketStatus: "Closed",
};

export function buildMarketIntelligence(data: DashboardResult): MarketIntelligenceSnapshot {
    const indexChanges = [
        data.market.nifty_change,
        data.market.sensex_change,
        data.market.bank_nifty_change,
    ];
    const averageChange = indexChanges.reduce((sum, value) => sum + value, 0) / indexChanges.length;
    const participation = Math.round(indexChanges.filter((value) => value > 0).length / indexChanges.length * 100);
    const direction: MarketDirection = averageChange > .25 ? "Bullish" : averageChange < -.25 ? "Bearish" : "Neutral";
    const volatility = data.market.india_vix >= 20 ? "High" : data.market.india_vix >= 14 ? "Moderate" : "Low";
    const riskLevel: MarketRisk = volatility === "High" ? "High Risk" : volatility === "Moderate" ? "Moderate Risk" : "Low Risk";
    const marketHealth = direction === "Bullish" && participation >= 60
        ? "Looking Healthy" : direction === "Neutral" ? "Mixed" : "Weak Momentum";
    const confidence = Math.round(Math.min(95, Math.max(35, 50 + Math.abs(averageChange) * 20 + participation * .25 - (volatility === "High" ? 15 : 0))));
    return {
        market: data.market,
        marketHealth,
        marketRegime: direction === "Bullish" ? "Strong Rise" : direction === "Bearish" ? "Strong Fall" : "Sideways",
        marketBreadth: participation,
        sectorLeadership: data.market.bank_nifty_change >= data.market.nifty_change ? ["Banking", "Large Companies"] : ["Large Companies", "Banking"],
        riskLevel,
        aiConfidence: confidence,
        volatility,
        participation,
        marketDirection: direction,
        todayStrategy: direction === "Bullish"
            ? "Look for buying opportunities after a small price fall."
            : direction === "Bearish"
                ? "Protect capital and wait for strong confirmation."
                : "Focus only on the clearest setups and keep risk small.",
        marketStatus: "Open",
    };
}
