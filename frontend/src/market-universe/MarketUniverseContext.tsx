import {
    useMemo,
    useState,
    type ReactNode,
} from "react";
import {
    MarketUniverseContext,
    type MarketUniverse,
} from "./MarketUniverseState";

export function MarketUniverseProvider({ children }: { children: ReactNode }) {
    const [marketUniverse, setMarketUniverse] = useState<MarketUniverse>("nse500");
    const [customSymbols, setCustomSymbols] = useState<string[]>([]);
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
