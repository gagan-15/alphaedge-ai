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

const timeframeKey = "alphaedge.market.timeframe";
const universeKey = "alphaedge.market.universe";
let sharedDashboardRequest: Promise<DashboardResult> | null = null;

function fetchDashboardOnce() {
    sharedDashboardRequest ??= getDashboard().finally(() => {
        sharedDashboardRequest = null;
    });
    return sharedDashboardRequest;
}

export function MarketIntelligenceProvider({ children }: { children: React.ReactNode }) {
    const [dashboard, setDashboard] = useState<DashboardResult | null>(null);
    const [timeframe, setTimeframeState] = useState<MarketTimeframe>(() => (localStorage.getItem(timeframeKey) as MarketTimeframe | null) ?? "1M");
    const [universe, setUniverseState] = useState(() => localStorage.getItem(universeKey) ?? "nifty500");
    const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState("");

    const refresh = useCallback(async () => {
        setIsLoading(true);
        setError("");
        try {
            const result = await fetchDashboardOnce();
            setDashboard(result);
            setLastUpdated(new Date());
        } catch {
            setError("Market data could not be loaded.");
        } finally {
            setIsLoading(false);
        }
    }, []);

    useEffect(() => {
        let active = true;
        void fetchDashboardOnce()
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
    }, []);

    const value = useMemo<MarketIntelligenceContextValue>(() => ({
        dashboard,
        snapshot: dashboard ? buildMarketIntelligence(dashboard) : emptyMarketIntelligence,
        timeframe,
        universe,
        lastUpdated,
        isLoading,
        error,
        setTimeframe: (next) => {
            localStorage.setItem(timeframeKey, next);
            setTimeframeState(next);
        },
        setUniverse: (next) => {
            localStorage.setItem(universeKey, next);
            setUniverseState(next);
        },
        refresh,
    }), [dashboard, error, isLoading, lastUpdated, refresh, timeframe, universe]);

    return <MarketIntelligenceContext.Provider value={value}>{children}</MarketIntelligenceContext.Provider>;
}
