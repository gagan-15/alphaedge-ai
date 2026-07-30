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

