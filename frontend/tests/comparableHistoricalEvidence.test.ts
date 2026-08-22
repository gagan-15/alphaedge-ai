import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

const component = readFileSync(new URL("../src/components/scanner/ComparableHistoricalEvidence.tsx", import.meta.url), "utf8");
const api = readFileSync(new URL("../src/api/historicalEvidenceApi.ts", import.meta.url), "utf8");
const table = readFileSync(new URL("../src/components/scanner/ScannerResultsTable.tsx", import.meta.url), "utf8");

test("Stock Details exposes the compact comparable historical evidence section", () => {
    for (const wording of [
        "Historical Evidence", "Comparable Historical Setups", "Closest Match",
        "Broadened Historical Match", "Exact closest-match sample", "Structural Target Achievement",
        "Median Favorable Excursion", "Median Adverse Excursion",
    ]) assert.ok(component.includes(wording), `missing wording: ${wording}`);
});

test("backend reliability and exact denominator metrics are rendered", () => {
    assert.ok(component.includes("data.reliability"));
    assert.ok(component.includes("metric.numerator"));
    assert.ok(component.includes("metric.denominator"));
    assert.equal(component.includes("interacted_zones >="), false);
});

test("unsupported, VERY HIGH and version mismatch states use backend explanations", () => {
    assert.ok(component.includes('data.status !== "AVAILABLE"'));
    assert.ok(component.includes("data.explanation"));
    assert.ok(component.includes("Historical evidence is unavailable for the current methodology version."));
});

test("full evidence navigation uses only the selected backend cohort definition", () => {
    assert.ok(component.includes("data.applied_cohort_definition"));
    assert.ok(component.includes("View Full Historical Evidence"));
    assert.ok(component.includes("zone_quality"));
    assert.ok(component.includes("trade_confidence"));
});

test("one comparable request is cached per version and current-zone cohort", () => {
    assert.equal((component.match(/getComparableHistoricalEvidence\(/g) ?? []).length, 1);
    assert.ok(api.includes("comparableRequests"));
    assert.ok(api.includes("HISTORICAL_EVIDENCE_VERSION"));
    assert.ok(api.includes("trade_confidence_label"));
    assert.ok(api.includes("zone_type"));
});

test("Dashboard row action navigates without calling historical APIs", () => {
    assert.ok(table.includes("Historical Evidence"));
    assert.ok(table.includes("/historical-evidence?"));
    assert.equal(table.includes("getComparableHistoricalEvidence"), false);
});

test("new UI avoids promotional outcome wording", () => {
    const source = component.toLowerCase();
    for (const phrase of ["win rate", "success probability", "chance of winning", "accuracy", "expected return", "buy probability", "sell probability"])
        assert.equal(source.includes(phrase), false, `forbidden phrase: ${phrase}`);
    assert.ok(source.includes("historical behavior does not guarantee a future result"));
});

test("historical evidence does not import ranking or scoring code", () => {
    for (const forbidden of ["tradeConfidenceRanking", "compareCanonicalTradeConfidence", "zoneQualityPresentation"])
        assert.equal(component.includes(forbidden), false, `unexpected ranking dependency: ${forbidden}`);
});
