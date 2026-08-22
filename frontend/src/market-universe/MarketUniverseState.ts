import { createContext, useContext } from "react";

export const marketUniverseOptions = [
    { value: "nifty50", label: "Nifty 50" },
    { value: "nifty100", label: "Nifty 100" },
    { value: "nifty200", label: "Nifty 200" },
    { value: "nse500", label: "NSE 500" },
    { value: "fno", label: "FnO" },
    { value: "allnse", label: "All NSE Stocks" },
    { value: "watchlist", label: "My Watchlist" },
    { value: "custom", label: "Custom Universe" },
] as const;

export type MarketUniverse = typeof marketUniverseOptions[number]["value"];

export const DEFAULT_MARKET_UNIVERSE: MarketUniverse = "nse500";
export const MARKET_UNIVERSE_STORAGE_KEY = "alphaedge.market.universe";

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
