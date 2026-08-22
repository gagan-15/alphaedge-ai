export const stockDetailsSectionOptions = [
    { id: "decision", label: "AI Decision", note: "Zone quality and current trade confidence." },
    { id: "plan", label: "Trading Plan", note: "Illustrative entry, stop, target and risk." },
    { id: "strengths", label: "Why this zone was selected", note: "The strongest points supporting the zone." },
    { id: "weaknesses", label: "What could weaken this setup", note: "Warnings and missing confirmation." },
    { id: "checklist", label: "AI Checklist", note: "The rule-by-rule validation list." },
    { id: "zoneAnalysis", label: "Demand / Supply Analysis", note: "Zone freshness, retests and current status." },
    { id: "trend", label: "Trend and Momentum", note: "Trend, moving averages, RSI and volume." },
    { id: "sector", label: "Sector and Relative Performance", note: "Stock, sector and Nifty comparison." },
    { id: "timeframes", label: "Multiple Timeframes", note: "Checks whether different timeframes agree." },
    { id: "confluence", label: "Higher Timeframe Zones", note: "Optional zones from larger timeframes." },
    { id: "history", label: "History and Risk", note: "Available historical and risk information." },
    { id: "actions", label: "Actions", note: "Watchlist, alert and sharing buttons." },
] as const;

export type StockDetailsSectionId = typeof stockDetailsSectionOptions[number]["id"];
export type StockDetailsVisibility = Record<StockDetailsSectionId, boolean>;

export const defaultStockDetailsVisibility = Object.fromEntries(
    stockDetailsSectionOptions.map(({ id }) => [id, true]),
) as StockDetailsVisibility;
