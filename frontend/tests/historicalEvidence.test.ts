import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

import {
    DEFAULT_EVIDENCE_FILTERS,
    metricText,
    readFilters,
    reliabilityLabel,
    TRADE_CONFIDENCE_LABELS,
    writeFilters,
} from "../src/historical-evidence/historicalEvidenceViewModel.ts";

test("default filter state is unfiltered and uses all interactions", () => {
    assert.deepEqual(DEFAULT_EVIDENCE_FILTERS, {
        timeframe: "", zoneType: "", pattern: "", zoneQuality: "",
        tradeConfidence: "", year: "", symbol: "", interactionStatus: "ALL",
    });
});

test("filter state round trips through the URL", () => {
    const filters = { ...DEFAULT_EVIDENCE_FILTERS, timeframe: "1W", zoneType: "DEMAND", symbol: "INFY", interactionStatus: "INTERACTED" };
    const params = writeFilters(filters);
    assert.deepEqual(readFilters(params), filters);
});

test("VERY HIGH remains a real selectable cohort", () => {
    assert.ok(TRADE_CONFIDENCE_LABELS.includes("VERY_HIGH"));
});

test("metrics preserve numerator and denominator semantics", () => {
    assert.equal(metricText({ numerator: 177, denominator: 189, percent: 93.65 }), "93.65%");
    assert.equal(metricText({ numerator: 0, denominator: 0, percent: null }), "Unavailable");
    assert.equal(reliabilityLabel("STRONGER_EVIDENCE"), "Stronger evidence");
});

test("page exposes required states and Daily Weekly wording", () => {
    const source = readFileSync(new URL("../src/pages/HistoricalEvidence.tsx", import.meta.url), "utf8");
    for (const text of ["No VERY HIGH observations", "Dataset version mismatch", "Daily and Weekly", "No historical zones match", "Server-filtered and deterministically paginated"]) {
        assert.ok(source.includes(text), `missing required UI state: ${text}`);
    }
});

test("page does not use forbidden promotional terminology", () => {
    const source = readFileSync(new URL("../src/pages/HistoricalEvidence.tsx", import.meta.url), "utf8").toLowerCase();
    const forbidden = ["win rate", "accuracy", "success probability", "probability of profit", "chance of winning", "expected profit", "expected return"];
    forbidden.forEach((term) => assert.equal(source.includes(term), false, `forbidden phrase: ${term}`));
});

test("page uses one metadata request and two cohort requests, never per row", () => {
    const source = readFileSync(new URL("../src/pages/HistoricalEvidence.tsx", import.meta.url), "utf8");
    assert.equal((source.match(/getHistoricalEvidenceMetadata\(/g) ?? []).length, 1);
    assert.equal((source.match(/getHistoricalEvidenceSummary\(/g) ?? []).length, 1);
    assert.equal((source.match(/getHistoricalEvidenceZones\(/g) ?? []).length, 1);
});
