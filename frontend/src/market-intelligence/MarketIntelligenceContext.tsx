import { useCallback, useEffect, useMemo, useState } from "react";

import { getDashboard } from "../api/dashboardApi";
import type { DashboardResult } from "../types/dashboard";
import {
    buildMarketIntelligence,
    emptyMarketIntelligence,
} from "../services/marketIntelligenceService";
import {
    MarketIntelligenceContext,
    type MarketIntelligenceContextValue,
    type MarketTimeframe,
} from "./MarketIntelligenceState";
import { useMarketUniverse } from "../market-universe/MarketUniverseState";

const timeframeKey = "alphaedge.market.timeframe";
const sharedDashboardRequests = new Map<string, Promise<DashboardResult>>();

function fetchDashboardOnce(universe: string, symbols: string[]) {
    const key = `${universe}:${symbols.join(",")}`;
    const active = sharedDashboardRequests.get(key);
    if (active) return active;
    const request = getDashboard(universe, symbols).finally(() => {
        sharedDashboardRequests.delete(key);
    });
    sharedDashboardRequests.set(key, request);
    return request;
}

export function MarketIntelligenceProvider({ children }: { children: React.ReactNode }) {
    const { marketUniverse, customSymbols } = useMarketUniverse();
    const suppliedSymbols = useMemo(() => {
        if (marketUniverse === "custom") return customSymbols;
        if (marketUniverse !== "watchlist") return [];
        try {
            return JSON.parse(
                localStorage.getItem("alphaedge.local.watchlist") ?? "[]",
            ) as string[];
        } catch {
            return [];
        }
    }, [customSymbols, marketUniverse]);
    const [dashboard, setDashboard] = useState<DashboardResult | null>(null);
    const [timeframe, setTimeframeState] = useState<MarketTimeframe>(() => (localStorage.getItem(timeframeKey) as MarketTimeframe | null) ?? "1M");
    const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState("");

    const refresh = useCallback(async () => {
        setIsLoading(true);
        setError("");
        try {
            const result = await fetchDashboardOnce(marketUniverse, suppliedSymbols);
            setDashboard(result);
            setLastUpdated(new Date());
        } catch {
            setError("Market data could not be loaded.");
        } finally {
            setIsLoading(false);
        }
    }, [marketUniverse, suppliedSymbols]);

    useEffect(() => {
        let active = true;
        void fetchDashboardOnce(marketUniverse, suppliedSymbols)
            .then((result) => {
                if (!active) return;
                setDashboard(result);
                setLastUpdated(new Date());
            })
            .catch(() => {
                if (active) setError("Market data could not be loaded.");
            })
            .finally(() => {
                if (active) setIsLoading(false);
            });
        return () => { active = false; };
    }, [marketUniverse, suppliedSymbols]);

    const value = useMemo<MarketIntelligenceContextValue>(() => ({
        dashboard,
        snapshot: dashboard ? buildMarketIntelligence(dashboard) : emptyMarketIntelligence,
        timeframe,
        lastUpdated,
        isLoading,
        error,
        setTimeframe: (next) => {
            localStorage.setItem(timeframeKey, next);
            setTimeframeState(next);
        },
        refresh,
    }), [dashboard, error, isLoading, lastUpdated, refresh, timeframe]);

    return <MarketIntelligenceContext.Provider value={value}>{children}</MarketIntelligenceContext.Provider>;
}
