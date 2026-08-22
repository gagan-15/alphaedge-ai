const researchLabels: Record<string, string> = {
    BUY: "Bullish Setup",
    SELL: "Bearish Setup",
    HOLD: "Watch",
    WAIT: "Watch",
    BULLISH_SETUP: "Bullish Setup",
    BEARISH_SETUP: "Bearish Setup",
    WATCH: "Watch",
};

export function getResearchLabel(
    value: string,
): string {
    return researchLabels[value.toUpperCase()] ?? value;
}

export function getResearchText(
    value: string,
): string {
    return value
        .replace(/\bBUY\b/gi, "Bullish Setup")
        .replace(/\bSELL\b/gi, "Bearish Setup")
        .replace(/\bHOLD\b/gi, "Watch")
        .replace(/\bSTOP LOSS\b/gi, "Invalidation Level");
}
