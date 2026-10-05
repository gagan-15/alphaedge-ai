import assert from "node:assert/strict";
import test from "node:test";

import {
    rowsForSelectedTimeframe,
    scannerSelectionMatches,
    shouldRequestScannerBuild,
    timeframeStatusMessage,
} from "../src/components/scanner/scannerTimeframeState.ts";
import type { PersistedZonePage, ZoneResearchResult } from "../src/types/scanner.ts";

function row(timeframe: string): ZoneResearchResult {
    return { timeframe } as ZoneResearchResult;
}

function page(
    state: PersistedZonePage["state"],
    results: ZoneResearchResult[] = [],
): PersistedZonePage {
    return {
        state,
        total: results.length,
        page: 1,
        page_size: 14,
        results,
    };
}

test("a weekly selection cannot render daily rows", () => {
    const response = page("READY", [row("1D"), row("1W")]);

    assert.deepEqual(rowsForSelectedTimeframe(response, "WEEKLY"), [row("1W")]);
});

test("daily and weekly switches use separate selections in both directions", () => {
    assert.equal(
        scannerSelectionMatches(
            { timeframe: "DAILY", universe: "nse500" },
            { timeframe: "WEEKLY", universe: "nse500" },
        ),
        false,
    );
    assert.equal(
        scannerSelectionMatches(
            { timeframe: "WEEKLY", universe: "nse500" },
            { timeframe: "DAILY", universe: "nse500" },
        ),
        false,
    );
});

test("universe and timeframe jointly identify persisted results", () => {
    assert.equal(
        scannerSelectionMatches(
            { timeframe: "WEEKLY", universe: "nifty50" },
            { timeframe: "WEEKLY", universe: "nse500" },
        ),
        false,
    );
    assert.equal(
        scannerSelectionMatches(
            { timeframe: "1W", universe: "nse500" },
            { timeframe: "WEEKLY", universe: "nse500" },
        ),
        true,
    );
});

test("building and unavailable states never retain old rows", () => {
    const oldDailyRows = [row("1D")];

    assert.deepEqual(rowsForSelectedTimeframe(page("BUILDING", oldDailyRows), "WEEKLY"), []);
    assert.deepEqual(rowsForSelectedTimeframe(page("UNAVAILABLE", oldDailyRows), "WEEKLY"), []);
    assert.deepEqual(rowsForSelectedTimeframe(page("FAILED", oldDailyRows), "WEEKLY"), []);
});

test("same-timeframe stale rows remain visible during a refresh", () => {
    assert.deepEqual(rowsForSelectedTimeframe(page("STALE", [row("1W")]), "WEEKLY"), [row("1W")]);
});

test("timeframe status messages describe the selected snapshot", () => {
    assert.equal(
        timeframeStatusMessage(
            "BUILDING", "Weekly", 0, null, 1420, 2559, "NSE Main Equity",
        ),
        "Preparing Weekly for NSE Main Equity. 1,420 / 2,559 completed.",
    );
    assert.equal(timeframeStatusMessage("READY", "Weekly", 0), "No qualifying zones for this timeframe.");
    assert.equal(timeframeStatusMessage("UNAVAILABLE", "Weekly", 0), "This timeframe is not available.");
    assert.equal(
        timeframeStatusMessage("STALE", "Weekly", 3, "BUILDING"),
        "Weekly is refreshing. Showing its previous saved results.",
    );
});

test("the Dashboard never owns scanner materialization", () => {
    assert.equal(shouldRequestScannerBuild("READY"), false);
    assert.equal(shouldRequestScannerBuild("STALE"), false);
    assert.equal(shouldRequestScannerBuild("BUILDING"), false);
    assert.equal(shouldRequestScannerBuild("UNAVAILABLE"), false);
    assert.equal(shouldRequestScannerBuild("BUILDING", "WEEKLY"), false);
    assert.equal(shouldRequestScannerBuild("UNAVAILABLE", "MONTHLY"), false);
});
