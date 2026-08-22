const preferenceKey = "alphaedge.stock-details.higher-timeframe-overlays";

export const overlayStyles: Record<string, { color: string; width: 1 | 2 | 3 | 4; label: string }> = {
    "1W": { color: "#f59e0b", width: 2, label: "Weekly" },
    "1M": { color: "#a855f7", width: 2, label: "Monthly" },
    "3M": { color: "#3b82f6", width: 2, label: "Quarterly" },
    "6M": { color: "#22d3ee", width: 2, label: "Half-Yearly" },
    "1Y": { color: "#facc15", width: 4, label: "Yearly" },
};

export function readOverlayTimeframes(): string[] {
    try {
        const parsed = JSON.parse(localStorage.getItem(preferenceKey) ?? "[]");
        return Array.isArray(parsed) ? parsed.map(String) : [];
    } catch {
        return [];
    }
}

export function saveOverlayTimeframes(timeframes: string[]) {
    localStorage.setItem(preferenceKey, JSON.stringify([...new Set(timeframes)]));
}
