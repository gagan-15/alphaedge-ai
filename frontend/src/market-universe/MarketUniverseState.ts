import { createContext, useContext } from "react";

export const marketUniverseOptions = [
    { value: "nifty50", label: "Nifty 50 (50)" },
    { value: "nifty100", label: "Nifty 100 (100)" },
    { value: "nifty200", label: "Nifty 200 (200)" },
    { value: "nse500", label: "NSE 500" },
    { value: "fno", label: "FnO" },
    { value: "nse_main", label: "NSE Main Equity" },
    { value: "nse_sme", label: "NSE SME" },
    { value: "allnse", label: "All NSE Equity" },
    { value: "bse_main", label: "BSE Main Equity" },
    { value: "bse_sme", label: "BSE SME" },
    { value: "allbse", label: "All BSE Equity" },
    { value: "allindia", label: "All Supported Indian Equity" },
    { value: "watchlist", label: "My Watchlist" },
    { value: "custom", label: "Custom Universe" },
] as const;

export type MarketUniverse = typeof marketUniverseOptions[number]["value"];

export const DEFAULT_MARKET_UNIVERSE: MarketUniverse = "allindia";
export const MARKET_UNIVERSE_STORAGE_KEY = "alphaedge.market.universe";
export const MARKET_UNIVERSE_DEFAULT_VERSION_KEY = "alphaedge.market.universe.default-version";
export const MARKET_UNIVERSE_DEFAULT_VERSION = "allindia-v2";

const legacyUniverseMap: Record<string, MarketUniverse> = {
    nifty500: "nse500",
    nseAll: "allnse",
    fo: "fno",
    holdings: "watchlist",
};

export function normalizeMarketUniverse(value: string | null | undefined): MarketUniverse {
    const normalized = value ? (legacyUniverseMap[value] ?? value) : DEFAULT_MARKET_UNIVERSE;
    return marketUniverseOptions.some((option) => option.value === normalized)
        ? normalized as MarketUniverse
        : DEFAULT_MARKET_UNIVERSE;
}

export interface MarketUniverseContextValue {
    marketUniverse: MarketUniverse;
    setMarketUniverse: (universe: MarketUniverse) => void;
    customSymbols: string[];
    setCustomSymbols: (symbols: string[]) => void;
}

export const MarketUniverseContext =
    createContext<MarketUniverseContextValue | null>(null);

export function useMarketUniverse() {
    const context = useContext(MarketUniverseContext);
    if (!context) {
        throw new Error(
            "useMarketUniverse must be used inside MarketUniverseProvider.",
        );
    }
    return context;
}
