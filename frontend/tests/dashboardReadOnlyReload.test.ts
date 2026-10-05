import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

const page = readFileSync(new URL("../src/pages/Scanner.tsx", import.meta.url), "utf8");
const api = readFileSync(new URL("../src/api/scannerApi.ts", import.meta.url), "utf8");

test("Dashboard Refresh invalidates only the persisted read query", () => {
    const refresh = page.slice(
        page.indexOf("function reloadScanner()"),
        page.indexOf("function updateDhanData()"),
    );
    assert.match(refresh, /setPersistedReloadNonce/);
    assert.doesNotMatch(refresh, /\n\s*loadScanner\(/);
    assert.doesNotMatch(refresh, /\n\s*startDhanIncrementalUpdate/);
});

test("only the explicit Update Data API request carries update intent", () => {
    const update = api.slice(
        api.indexOf("export async function startDhanIncrementalUpdate"),
        api.indexOf("export async function cancelDhanIncrementalUpdate"),
    );
    assert.match(update, /X-AlphaEdge-Update-Intent.*explicit-user/);
    assert.match(api, /cancelDhanIncrementalUpdate/);
});

test("Dashboard shows one stateful Update-or-Cancel control", () => {
    const toolbar = readFileSync(new URL("../src/components/scanner/ScannerToolbar.tsx", import.meta.url), "utf8");
    assert.match(toolbar, /Cancel Update/);
    assert.match(toolbar, /Cancelling update/);
    assert.match(toolbar, /props\.isUpdatingData \? props\.onCancelUpdate : props\.onUpdateData/);
});

test("Distance and Current Market Price are server-sortable table headers", () => {
    const table = readFileSync(new URL("../src/components/scanner/ScannerResultsTable.tsx", import.meta.url), "utf8");
    assert.match(table, /sortableLabel\("distance_percent", "Distance"\)/);
    assert.match(table, /sortableLabel\("current_price", "Current Market Price"\)/);
    assert.match(table, /Latest available Dhan market price/);
});

test("Far filter uses the response-time FAR status", () => {
    const toolbar = readFileSync(new URL("../src/components/scanner/ScannerToolbar.tsx", import.meta.url), "utf8");
    assert.match(toolbar, /MenuItem value="FAR">Far/);
});
