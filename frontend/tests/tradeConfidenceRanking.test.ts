import assert from "node:assert/strict";
import test from "node:test";

import {
    compareCanonicalTradeConfidence,
    tradeConfidenceBucket,
    tradeConfidenceExplanation,
} from "../src/components/scanner/tradeConfidenceRanking.ts";

const confidence = (label: string, sufficiency: string, score: number) => ({ label, data_sufficiency: sufficiency, score });
const zone = (id: string, tc: ReturnType<typeof confidence> | null, quality = 80, distance = 2) => ({
    zone_id: id,
    trade_confidence: tc,
    zone_score: quality,
    distance_percent: distance,
}) as never;

test("approved contextual buckets preserve conflict precedence", () => {
    assert.equal(tradeConfidenceBucket(confidence("VERY_HIGH", "AVAILABLE", 90) as never), 0);
    assert.equal(tradeConfidenceBucket(confidence("HIGH", "PARTIAL", 88) as never), 3);
    assert.equal(tradeConfidenceBucket(confidence("LOW", "AVAILABLE", 35) as never), 5);
    assert.equal(tradeConfidenceBucket(confidence("CONFLICTED", "AVAILABLE", 95) as never), 6);
    assert.equal(tradeConfidenceBucket(confidence("HIGH", "INSUFFICIENT", 99) as never), 7);
});

test("ranking uses bucket then score, quality, distance and stable identity", () => {
    const rows = [
        zone("conflict", confidence("CONFLICTED", "AVAILABLE", 99)),
        zone("b", confidence("HIGH", "AVAILABLE", 75), 82, 3),
        zone("a", confidence("HIGH", "AVAILABLE", 75), 82, 3),
        zone("quality", confidence("HIGH", "AVAILABLE", 75), 90, 8),
        zone("very-high", confidence("VERY_HIGH", "AVAILABLE", 70)),
    ].sort(compareCanonicalTradeConfidence);
    assert.deepEqual(rows.map((row: { zone_id: string }) => row.zone_id), ["very-high", "quality", "a", "b", "conflict"]);
});

test("primary-zone ordering and explanations never issue trade instructions", () => {
    const rows = [
        zone("partial", confidence("HIGH", "PARTIAL", 90)),
        zone("available", confidence("MODERATE", "AVAILABLE", 60)),
    ].sort(compareCanonicalTradeConfidence);
    assert.equal((rows[0] as { zone_id: string }).zone_id, "available");
    for (const item of rows) {
        const text = tradeConfidenceExplanation((item as { trade_confidence: never }).trade_confidence);
        assert.doesNotMatch(text, /buy|sell|enter now|avoid/i);
    }
});
