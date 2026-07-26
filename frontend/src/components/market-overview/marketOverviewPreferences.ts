export const marketOverviewWidgetKeys = [
    "aiSummary",
    "marketHealth",
    "marketTrend",
    "researchFocus",
    "marketRisk",
    "participationTrend",
    "sectorRotation",
    "marketBreadth",
    "bigInvestorActivity",
    "marketVolatility",
    "marketSentiment",
    "aiOpportunities",
    "smartAlerts",
    "todayVerdict",
] as const;

export type MarketOverviewWidgetKey = typeof marketOverviewWidgetKeys[number];
export type DashboardPreset = "beginner" | "swing" | "intraday" | "longTerm" | "custom";
export type DashboardTimeframe = "1D" | "1W" | "1M" | "3M" | "6M" | "1Y";
export type MarketUniverse = "nseAll" | "nifty500" | "nifty200" | "nifty100" | "fo" | "watchlist" | "holdings";

export interface MarketOverviewPreferences {
    version: 1;
    preset: DashboardPreset;
    visibleWidgets: Record<MarketOverviewWidgetKey, boolean>;
    defaultTimeframe: DashboardTimeframe;
    marketUniverse: MarketUniverse;
    chart: {
        showNifty: boolean;
        showBankNifty: boolean;
        showEvents: boolean;
        showAiExplanations: boolean;
        showTooltips: boolean;
    };
    language: "simple" | "professional";
    density: "comfortable" | "compact";
    numberFormat: "full" | "short";
}

const allVisible = Object.fromEntries(marketOverviewWidgetKeys.map((key) => [key, true])) as Record<MarketOverviewWidgetKey, boolean>;

export const defaultMarketOverviewPreferences: MarketOverviewPreferences = {
    version: 1,
    preset: "beginner",
    visibleWidgets: allVisible,
    defaultTimeframe: "1D",
    marketUniverse: "nifty500",
    chart: {
        showNifty: true,
        showBankNifty: true,
        showEvents: true,
        showAiExplanations: true,
        showTooltips: true,
    },
    language: "simple",
    density: "comfortable",
    numberFormat: "full",
};

const presetVisibility: Record<Exclude<DashboardPreset, "custom">, MarketOverviewWidgetKey[]> = {
    beginner: marketOverviewWidgetKeys.slice(),
    swing: ["aiSummary", "marketHealth", "marketTrend", "researchFocus", "marketRisk", "participationTrend", "sectorRotation", "marketBreadth", "marketVolatility", "aiOpportunities", "smartAlerts", "todayVerdict"],
    intraday: ["aiSummary", "marketHealth", "marketTrend", "researchFocus", "marketRisk", "participationTrend", "sectorRotation", "marketBreadth", "bigInvestorActivity", "marketVolatility", "marketSentiment", "smartAlerts", "todayVerdict"],
    longTerm: ["aiSummary", "marketHealth", "marketTrend", "marketRisk", "participationTrend", "sectorRotation", "marketBreadth", "bigInvestorActivity", "marketVolatility", "marketSentiment", "todayVerdict"],
};

export function preferencesForPreset(preset: Exclude<DashboardPreset, "custom">): MarketOverviewPreferences {
    const visible = new Set(presetVisibility[preset]);
    return {
        ...defaultMarketOverviewPreferences,
        preset,
        defaultTimeframe: preset === "intraday" ? "1D" : preset === "longTerm" ? "1Y" : preset === "swing" ? "1M" : "1D",
        visibleWidgets: Object.fromEntries(marketOverviewWidgetKeys.map((key) => [key, visible.has(key)])) as Record<MarketOverviewWidgetKey, boolean>,
    };
}

function storageKey(userId: string) {
    return `alphaedge.market-overview.preferences.${userId || "local-demo"}`;
}

export function loadMarketOverviewPreferences(userId: string): MarketOverviewPreferences {
    try {
        const saved = JSON.parse(localStorage.getItem(storageKey(userId)) ?? "{}") as Partial<MarketOverviewPreferences>;
        return {
            ...defaultMarketOverviewPreferences,
            ...saved,
            visibleWidgets: { ...defaultMarketOverviewPreferences.visibleWidgets, ...saved.visibleWidgets },
            chart: { ...defaultMarketOverviewPreferences.chart, ...saved.chart },
        };
    } catch {
        return defaultMarketOverviewPreferences;
    }
}

export function saveMarketOverviewPreferences(userId: string, preferences: MarketOverviewPreferences) {
    localStorage.setItem(storageKey(userId), JSON.stringify(preferences));
}
