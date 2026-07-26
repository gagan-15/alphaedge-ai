import { createContext, useContext } from "react";

import type { DashboardResult } from "../types/dashboard";
import type { MarketIntelligenceSnapshot } from "../services/marketIntelligenceService";

export type MarketTimeframe = "1D" | "1W" | "1M" | "3M" | "6M" | "1Y";

export interface MarketIntelligenceContextValue {
    dashboard: DashboardResult | null;
    snapshot: MarketIntelligenceSnapshot;
    timeframe: MarketTimeframe;
    universe: string;
    lastUpdated: Date | null;
    isLoading: boolean;
    error: string;
    setTimeframe: (value: MarketTimeframe) => void;
    setUniverse: (value: string) => void;
    refresh: () => Promise<void>;
}

export const MarketIntelligenceContext = createContext<MarketIntelligenceContextValue | null>(null);

export function useMarketIntelligence() {
    const context = useContext(MarketIntelligenceContext);
    if (!context) throw new Error("useMarketIntelligence must be used inside MarketIntelligenceProvider.");
    return context;
}
