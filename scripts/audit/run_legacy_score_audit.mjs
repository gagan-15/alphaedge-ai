import { readFileSync, writeFileSync } from "node:fs";
import { analyzeStockZone, buildTradeConfidence, captureLegacyAiScore } from "../../tmp/trade7e/legacy-score-audit.mjs";

const input = JSON.parse(readFileSync("tmp/trade7e/legacy-score-inputs.json", "utf8"));
const records = input.records.map(({ zone, candles, backend }) => {
    const analysis = analyzeStockZone(zone, candles);
    const production = buildTradeConfidence(zone, analysis, backend);
    const audit = captureLegacyAiScore(zone, analysis, backend);
    if (production.score !== audit.score) throw new Error(`Audit mismatch for ${zone.symbol}`);
    return { zone_identity: audit.zoneIdentity, zone, analysis, backend, legacy_ai_score: audit.score, legacy_result: audit.result };
});
writeFileSync("tests/fixtures/legacy_ai_score_enriched_snapshot.json", JSON.stringify({ records, failures: input.failures }, null, 2));
console.log(JSON.stringify({ records: records.length, failures: input.failures.length, exact_matches: records.length }, null, 2));
