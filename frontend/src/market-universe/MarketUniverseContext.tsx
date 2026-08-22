import {
    useMemo,
    useState,
    type ReactNode,
} from "react";
import {
    DEFAULT_MARKET_UNIVERSE,
    MARKET_UNIVERSE_STORAGE_KEY,
    MarketUniverseContext,
    normalizeMarketUniverse,
    type MarketUniverse,
} from "./MarketUniverseState";

export function MarketUniverseProvider({ children }: { children: ReactNode }) {
    const [marketUniverse, setMarketUniverseState] = useState<MarketUniverse>(() =>
        normalizeMarketUniverse(localStorage.getItem(MARKET_UNIVERSE_STORAGE_KEY) ?? DEFAULT_MARKET_UNIVERSE));
    const [customSymbols, setCustomSymbols] = useState<string[]>([]);
    const setMarketUniverse = (next: MarketUniverse) => {
        localStorage.setItem(MARKET_UNIVERSE_STORAGE_KEY, next);
        setMarketUniverseState(next);
    };
    const value = useMemo(
        () => ({
            marketUniverse,
            setMarketUniverse,
            customSymbols,
            setCustomSymbols,
        }),
        [customSymbols, marketUniverse],
    );
    return (
        <MarketUniverseContext.Provider value={value}>
            {children}
        </MarketUniverseContext.Provider>
    );
}
