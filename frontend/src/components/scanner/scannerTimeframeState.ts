import type { PersistedZonePage, ZoneResearchResult } from "../../types/scanner";

const timeframeLabels: Record<string, string> = {
    DAILY: "1D",
    WEEKLY: "1W",
    MONTHLY: "1M",
    QUARTERLY: "3M",
    HALFYEARLY: "6M",
    YEARLY: "1Y",
    MINUTE_5: "5M",
    MINUTE_15: "15M",
    MINUTE_75: "75M",
    MINUTE_125: "125M",
    HOUR_1: "1H",
    HOUR_2: "2H",
    HOUR_4: "4H",
    HOUR_6: "6H",
};

export function normalizedScannerTimeframe(value: string): string {
    return timeframeLabels[value.toUpperCase()] ?? value.toUpperCase();
}

export function rowsForSelectedTimeframe(
    response: PersistedZonePage,
    selectedTimeframe: string,
): ZoneResearchResult[] {
    if (response.state !== "READY" && response.state !== "STALE") return [];
    const expected = normalizedScannerTimeframe(selectedTimeframe);
    return response.results.filter(
        (row) => normalizedScannerTimeframe(row.timeframe) === expected,
    );
}

export function scannerSelectionMatches(
    stored: { timeframe: string; universe: string },
    selected: { timeframe: string; universe: string },
): boolean {
    return normalizedScannerTimeframe(stored.timeframe)
        === normalizedScannerTimeframe(selected.timeframe)
        && stored.universe === selected.universe;
}

export function shouldRequestScannerBuild(
    state: PersistedZonePage["state"],
    timeframe?: string,
): boolean {
    void state;
    void timeframe;
    // The browser is a read-only consumer of persisted scanner snapshots.
    // Missing materializations are owned by the backend scheduler, never by
    // a timeframe selection in the Dashboard.
    return false;
}

export function timeframeStatusMessage(
    state: PersistedZonePage["state"] | "LOADING",
    label: string,
    total: number,
    refreshState?: "BUILDING" | null,
    processed = 0,
    expected = 0,
    universeLabel = "the selected market",
): string | null {
    if (state === "LOADING") return `Loading ${label} results.`;
    if (state === "READY" && total === 0) {
        return "No qualifying zones for this timeframe.";
    }
    if (state === "BUILDING") {
        const progress = expected > 0 ? ` ${processed.toLocaleString()} / ${expected.toLocaleString()} completed.` : "";
        return `Preparing ${label} for ${universeLabel}.${progress}`;
    }
    if (state === "UNAVAILABLE") return "This timeframe is not available.";
    if (state === "FAILED") return "This timeframe could not be prepared.";
    if (state === "STALE" && refreshState === "BUILDING") {
        return `${label} is refreshing. Showing its previous saved results.`;
    }
    if (state === "STALE") return `Showing saved ${label} results.`;
    return null;
}
