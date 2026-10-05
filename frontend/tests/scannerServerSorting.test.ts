import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

const page = readFileSync(new URL("../src/pages/Scanner.tsx", import.meta.url), "utf8");
const table = readFileSync(new URL("../src/components/scanner/ScannerResultsTable.tsx", import.meta.url), "utf8");
const api = readFileSync(new URL("../src/api/scannerApi.ts", import.meta.url), "utf8");

test("Dashboard sends sort state to the persisted server query", () => {
    assert.ok(page.includes("sort: resultSort"));
    assert.ok(page.includes('descending: resultSortDirection === "desc"'));
    assert.ok(api.includes("sort: params.sort"));
    assert.ok(api.includes("descending: params.descending"));
});

test("server sort changes reset pagination to page one", () => {
    assert.ok(page.includes("onServerSortChange="));
    assert.ok(page.includes("setResultPage(1)"));
});

test("server-paged rows are not locally resorted", () => {
    assert.ok(table.includes("externallySorted ? results : [...results].sort"));
    assert.ok(table.includes("if (externallySorted)"));
    assert.ok(table.includes("zones: [result]"));
    assert.ok(table.includes("onServerSortChange"));
});
