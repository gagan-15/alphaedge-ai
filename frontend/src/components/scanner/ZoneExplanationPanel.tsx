import AddAlertRoundedIcon from "@mui/icons-material/AddAlertRounded";
import BookmarkAddRoundedIcon from "@mui/icons-material/BookmarkAddRounded";
import CheckCircleRoundedIcon from "@mui/icons-material/CheckCircleRounded";
import ErrorOutlineRoundedIcon from "@mui/icons-material/ErrorOutlineRounded";
import OpenInFullRoundedIcon from "@mui/icons-material/OpenInFullRounded";
import ShareRoundedIcon from "@mui/icons-material/ShareRounded";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Chip from "@mui/material/Chip";
import Divider from "@mui/material/Divider";
import Grid from "@mui/material/Grid";
import Snackbar from "@mui/material/Snackbar";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { useEffect, useState } from "react";

import { getMarketCandles } from "../../api/marketApi";
import { getStockDetailsAnalysis, type StockDetailsBackendAnalysis } from "../../api/scannerApi";
import type { ZoneExplanationFactor, ZoneResearchResult } from "../../types/scanner";
import { analyzeStockZone, type StockZoneAnalysis } from "./stockZoneAnalysis";

const watchlistKey = "alphaedge.local.watchlist";
const alertsKey = "alphaedge.local.alerts";

function readList(key: string): string[] {
    try {
        const value = JSON.parse(localStorage.getItem(key) ?? "[]");
        return Array.isArray(value) ? value.map(String) : [];
    } catch {
        return [];
    }
}

function saveUnique(key: string, value: string) {
    localStorage.setItem(key, JSON.stringify([...new Set([...readList(key), value])]));
}

function recommendation(analysis: StockZoneAnalysis | null, tradeConfidence: number) {
    if (analysis?.broken) return "Invalidated";
    if (!analysis) return "Calculating";
    if (analysis.zoneQualityScore >= 75 && tradeConfidence >= 70) return "Strong setup — wait for confirmation";
    if (analysis.zoneQualityScore >= 60 && tradeConfidence >= 50) return "Watch";
    if (analysis.zoneQualityScore >= 60) return "Wait for confirmation";
    return "Weak setup";
}

function Field({ label, value, note }: { label: string; value: string; note?: string }) {
    return (
        <Box sx={{ py: .6 }}>
            <Typography variant="caption" color="text.secondary">{label}</Typography>
            <Typography sx={{ fontWeight: 800 }}>{value}</Typography>
            {note && <Typography variant="caption" color="text.secondary">{note}</Typography>}
        </Box>
    );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
    return (
        <Box>
            <Typography variant="h6" sx={{ mb: 1 }}>{title}</Typography>
            {children}
        </Box>
    );
}

function FactorList({ title, factors, positive }: { title: string; factors: ZoneExplanationFactor[]; positive: boolean }) {
    if (!factors.length) return null;
    return (
        <Section title={title}>
            <Stack spacing={1}>
                {factors.map((factor) => (
                    <Box key={factor.key} sx={{ p: 1.25, border: "1px solid", borderColor: "divider", borderRadius: 1.5, bgcolor: positive ? "rgba(16,185,129,.06)" : "rgba(245,158,11,.06)" }}>
                        <Stack direction="row" spacing={1} sx={{ alignItems: "center" }}>
                            {positive ? <CheckCircleRoundedIcon color="success" fontSize="small" /> : <ErrorOutlineRoundedIcon color="warning" fontSize="small" />}
                            <Typography sx={{ fontWeight: 800 }}>{factor.title}</Typography>
                        </Stack>
                        <Typography variant="body2" color="text.secondary" sx={{ mt: .5 }}>{factor.summary}</Typography>
                        <Typography variant="caption" color="text.secondary">Next check: {factor.recommendation}</Typography>
                    </Box>
                ))}
            </Stack>
        </Section>
    );
}

function ZoneExplanationPanel({ result }: { result: ZoneResearchResult }) {
    const [message, setMessage] = useState("");
    const [analysis, setAnalysis] = useState<StockZoneAnalysis | null>(null);
    const [backendAnalysis, setBackendAnalysis] = useState<StockDetailsBackendAnalysis | null>(null);
    const [analysisError, setAnalysisError] = useState("");
    const [scoreDetailsOpen, setScoreDetailsOpen] = useState(false);
    const explanation = result.explanation;
    const rawZoneScore = result.raw_zone_score ?? (
        result.freshness_score
        + result.strength_score
        + result.touch_score
        + result.merge_score
    );
    const qualityCap = result.quality_cap ?? result.zone_score;
    const currentZone = `${result.distal_price.toLocaleString("en-IN")} – ${result.proximal_price.toLocaleString("en-IN")}`;
    const unavailable = "Unavailable with the current data source";
    const number = (value: number | null, suffix = "") => value === null ? "Insufficient candle history" : `${value.toFixed(2)}${suffix}`;
    const displayChecks = analysis?.checks.map((item) => {
        if (item.label === "Relative strength" && backendAnalysis) {
            const comparison = backendAnalysis.nifty_comparison["3m"];
            const status = comparison?.status === "OUTPERFORMING" ? "PASS" : comparison?.status === "UNDERPERFORMING" ? "FAIL" : "MIXED";
            return { ...item, status, value: comparison?.difference === undefined ? comparison?.status ?? "Insufficient history" : `${comparison.difference.toFixed(2)}% versus Nifty`, threshold: "More than 2% outperformance", reason: "Calculated from aligned three-month closing prices", scoreEffect: "Context only" } as const;
        }
        if (item.label === "Multiple timeframes" && backendAnalysis) {
            const status = backendAnalysis.multi_timeframe.status === "CONFIRMED" ? "PASS" : backendAnalysis.multi_timeframe.status === "MIXED" ? "MIXED" : "FAIL";
            return { ...item, status, value: backendAnalysis.multi_timeframe.status.replaceAll("_", " "), threshold: "Daily, weekly and monthly must agree", reason: "Calculated from each timeframe's trend and EMA alignment", scoreEffect: "Context only" } as const;
        }
        if (item.label === "Risk and reward" && backendAnalysis) {
            const ratio = backendAnalysis.trade_plan.risk_reward_ratio;
            return { ...item, status: ratio === null ? "UNAVAILABLE" : ratio >= 2 ? "PASS" : "FAIL", value: ratio === null ? "No validated opposing target" : `1 : ${ratio}`, threshold: "At least 1 : 2", reason: backendAnalysis.trade_plan.target_basis, scoreEffect: "Context only" } as const;
        }
        return item;
    });
    const availableChecks = displayChecks?.filter((item) => item.status !== "UNAVAILABLE").length ?? 0;
    const dataConfidence = displayChecks ? `${availableChecks} of ${displayChecks.length} checks calculated` : "Calculating data confidence";
    const tradeFactors = [
        ["EMA alignment", 12, displayChecks?.find((item) => item.label === "EMA alignment")],
        ["Trend", 12, displayChecks?.find((item) => item.label === "Trend confirmation")],
        ["RSI", 8, displayChecks?.find((item) => item.label === "RSI condition")],
        ["Volume", 8, displayChecks?.find((item) => item.label === "Volume confirmation")],
        ["Relative strength", 12, displayChecks?.find((item) => item.label === "Relative strength")],
        ["Sector strength", 8, backendAnalysis?.sector.comparison?.["3m"] ? { status: backendAnalysis.sector.comparison["3m"].status === "OUTPERFORMING" ? "PASS" : backendAnalysis.sector.comparison["3m"].status === "UNDERPERFORMING" ? "FAIL" : "MIXED", reason: "Three-month stock return compared with its sector benchmark." } : undefined],
        ["Multiple timeframes", 15, displayChecks?.find((item) => item.label === "Multiple timeframes")],
        ["Risk and reward", 15, displayChecks?.find((item) => item.label === "Risk and reward")],
        ["Market context", 5, backendAnalysis?.nifty_comparison?.["3m"] ? { status: (backendAnalysis.nifty_comparison["3m"].benchmark_return ?? 0) > 2 ? "PASS" : (backendAnalysis.nifty_comparison["3m"].benchmark_return ?? 0) < -2 ? "FAIL" : "MIXED", reason: "Three-month Nifty direction." } : undefined],
        ["Confluence", 5, { status: result.merge_score >= 7.5 ? "PASS" : result.merge_score > 0 ? "MIXED" : "FAIL", reason: "Overlap with another detected zone." }],
    ] as const;
    const awarded = (weight: number, status?: string) => status === "PASS" ? weight : status === "MIXED" ? weight * .5 : 0;
    const tradeConfidence = Math.round(tradeFactors.reduce((sum, [, weight, factor]) => sum + awarded(weight, factor?.status), 0));

    useEffect(() => {
        let active = true;
        const intraday = ["5m", "15m", "75m", "125m", "1H", "2H", "4H", "6H"].includes(result.timeframe);
        const period = intraday ? "1mo" : result.timeframe === "1D" ? "1y" : "10y";
        const interval = intraday ? (result.timeframe.includes("H") ? "1h" : result.timeframe === "5m" || result.timeframe === "125m" ? "5m" : "15m") : "1d";
        void getMarketCandles(result.symbol, period, interval, result.timeframe)
            .then((response) => { if (active) setAnalysis(analyzeStockZone(result, response.candles)); })
            .catch(() => { if (active) setAnalysisError("Calculation failed because candle history could not be loaded."); });
        void getStockDetailsAnalysis(result.symbol, result.zone_type, result.base_index)
            .then((response) => { if (active) setBackendAnalysis(response); })
            .catch(() => { if (active) setBackendAnalysis(null); });
        return () => { active = false; };
    }, [result]);

    function addToWatchlist() {
        saveUnique(watchlistKey, result.symbol);
        setMessage(`${result.symbol} was added to your watchlist.`);
    }

    function createAlert() {
        const existing: unknown[] = (() => {
            try {
                const stored = JSON.parse(localStorage.getItem(alertsKey) ?? "[]");
                return Array.isArray(stored) ? stored.filter((item) => typeof item === "object" && item !== null) : [];
            } catch {
                return [];
            }
        })();
        const condition = result.zone_type === "DEMAND" ? "below" : "above";
        const target = result.zone_type === "DEMAND" ? result.distal_price : result.proximal_price;
        localStorage.setItem(alertsKey, JSON.stringify([...existing, {
            id: crypto.randomUUID(),
            symbol: result.symbol,
            condition,
            target,
            current: null,
            enabled: true,
        }]));
        setMessage("A local zone alert was created.");
    }

    async function share() {
        const text = `${result.symbol} ${result.zone_type} zone ${currentZone}. Quality ${result.zone_score.toFixed(0)}/100. Research only.`;
        if (navigator.share) await navigator.share({ title: "AlphaEdge AI zone research", text });
        else await navigator.clipboard.writeText(text);
        setMessage(navigator.share ? "Share window opened." : "Analysis copied.");
    }

    return (
        <Card variant="outlined" sx={{ mb: 1.5, overflow: "hidden" }}>
            <CardContent>
                <Stack spacing={2.25} divider={<Divider flexItem />}>
                    <Section title="AI Decision">
                        <Grid container spacing={1.5}>
                            <Grid size={{ xs: 6 }}>
                                <Typography color="text.secondary" variant="overline">Zone Quality</Typography>
                                <Stack direction="row" spacing={1} sx={{ alignItems: "baseline" }}>
                                    <Typography variant="h2">{analysis?.zoneQualityScore.toFixed(0) ?? "—"}</Typography>
                                    <Typography color="text.secondary">/ 100</Typography>
                                </Stack>
                                <Typography variant="caption" color="text.secondary">How well the zone itself was formed.</Typography>
                            </Grid>
                            <Grid size={{ xs: 6 }}>
                                <Typography color="text.secondary" variant="overline">Trade Confidence</Typography>
                                <Stack direction="row" spacing={1} sx={{ alignItems: "baseline" }}>
                                    <Typography variant="h2">{analysis ? tradeConfidence : "—"}</Typography>
                                    <Typography color="text.secondary">/ 100</Typography>
                                </Stack>
                                <Typography variant="caption" color="text.secondary">How supportive current conditions are.</Typography>
                            </Grid>
                            <Grid size={{ xs: 12 }}>
                                <Chip label={recommendation(analysis, tradeConfidence)} color={analysis?.broken ? "error" : analysis && analysis.zoneQualityScore >= 75 && tradeConfidence >= 70 ? "success" : "warning"} />
                                <Typography sx={{ mt: 1, fontWeight: 800 }}>{dataConfidence}</Typography>
                                <Typography variant="caption" color="text.secondary">This shows data coverage, not the chance of profit.</Typography>
                            </Grid>
                        </Grid>
                        <Typography color="text.secondary" sx={{ mt: 1 }}>{explanation.summary}</Typography>
                        <Button size="small" sx={{ mt: 1 }} onClick={() => setScoreDetailsOpen((open) => !open)}>{scoreDetailsOpen ? "Hide Details" : "Expand Details"}</Button>
                        {scoreDetailsOpen && <Stack spacing={1} sx={{ mt: 1 }}>
                            <Typography sx={{ fontWeight: 800 }}>Zone Quality Details</Typography>
                            {analysis?.zoneQualityFactors.map((factor) => <Box key={factor.factor} sx={{ p: 1, border: "1px solid", borderColor: "divider", borderRadius: 1.25 }}>
                                <Stack direction="row" sx={{ justifyContent: "space-between" }}><Typography variant="body2" sx={{ fontWeight: 800 }}>{factor.factor}</Typography><Typography variant="body2">{factor.points.toFixed(1)} / {factor.weight}</Typography></Stack>
                                <Typography variant="caption" color="text.secondary">{factor.reason}</Typography>
                            </Box>)}
                            <Typography sx={{ fontWeight: 800, mt: 1 }}>Trade Confidence Details</Typography>
                            {tradeFactors.map(([factor, weight, status]) => <Box key={factor} sx={{ p: 1, border: "1px solid", borderColor: "divider", borderRadius: 1.25 }}>
                                <Stack direction="row" sx={{ justifyContent: "space-between" }}><Typography variant="body2" sx={{ fontWeight: 800 }}>{factor}</Typography><Typography variant="body2">{awarded(weight, status?.status).toFixed(1)} / {weight}</Typography></Stack>
                                <Typography variant="caption" color="text.secondary">{status?.reason ?? "Unavailable with the current data source."}</Typography>
                            </Box>)}
                            <Typography variant="caption" color="text.secondary">Previous backend zone score: {rawZoneScore.toFixed(1)} raw, capped at {qualityCap.toFixed(1)}. It is kept only for API compatibility.</Typography>
                        </Stack>}
                    </Section>

                    <Section title="Trading Plan">
                        <Grid container spacing={1}>
                            <Grid size={{ xs: 6 }}><Field label="Entry range" value={backendAnalysis ? `₹${backendAnalysis.trade_plan.entry_range[0].toLocaleString("en-IN")} – ₹${backendAnalysis.trade_plan.entry_range[1].toLocaleString("en-IN")}` : "Calculating from active zones…"} /></Grid>
                            <Grid size={{ xs: 6 }}><Field label="Expected holding period" value="Requires a validated outcome backtest" /></Grid>
                            <Grid size={{ xs: 12 }}><Field label="Suggested trigger" value={result.zone_type === "DEMAND" ? "Wait for a bullish confirmation candle inside the demand zone before considering the setup." : "Wait for a bearish rejection candle inside the supply zone before considering the setup."} note="Do not use the zone as an immediate entry." /></Grid>
                            <Grid size={{ xs: 6 }}><Field label="Illustrative entry" value={backendAnalysis ? `₹${backendAnalysis.trade_plan.illustrative_entry.toLocaleString("en-IN")}` : "Calculating…"} /></Grid>
                            <Grid size={{ xs: 6 }}><Field label="Invalidation stop" value={backendAnalysis ? `₹${backendAnalysis.trade_plan.invalidation_stop.toLocaleString("en-IN")}` : "Calculating…"} note={backendAnalysis?.trade_plan.stop_buffer_rule} /></Grid>
                            <Grid size={{ xs: 6 }}><Field label="Target" value={backendAnalysis?.trade_plan.target ? `₹${backendAnalysis.trade_plan.target.toLocaleString("en-IN")}` : backendAnalysis?.trade_plan.target_basis ?? "Calculating…"} /></Grid>
                            <Grid size={{ xs: 6 }}><Field label="Risk : Reward" value={backendAnalysis?.trade_plan.risk_reward_ratio ? `1 : ${backendAnalysis.trade_plan.risk_reward_ratio}` : "No validated opposing target"} /></Grid>
                            <Grid size={{ xs: 6 }}><Field label="Risk per share" value={backendAnalysis ? `₹${backendAnalysis.trade_plan.risk_per_share.toLocaleString("en-IN")}` : "Calculating…"} /></Grid>
                            <Grid size={{ xs: 6 }}><Field label="Reward per share" value={backendAnalysis?.trade_plan.reward_per_share ? `₹${backendAnalysis.trade_plan.reward_per_share.toLocaleString("en-IN")}` : "No validated opposing target"} /></Grid>
                        </Grid>
                        <Typography variant="caption" color="text.secondary">Research illustration only. The target uses the nearest detected opposing zone; no order is placed.</Typography>
                    </Section>

                    <FactorList title="Why AlphaEdge selected this zone" factors={explanation.positive_factors} positive />
                    <FactorList title="What could weaken this setup" factors={explanation.negative_factors} positive={false} />

                    <Section title="AI Checklist">
                        {!analysis && !analysisError && <Typography color="text.secondary">Calculating from delayed OHLCV candles…</Typography>}
                        {analysisError && <Button size="small" color="warning" onClick={() => window.location.reload()}>{analysisError} Retry</Button>}
                        {displayChecks && <Stack spacing={1}>{displayChecks.map((item) => (
                            <Box key={item.label} sx={{ p: 1, border: "1px solid", borderColor: "divider", borderRadius: 1.25 }}>
                                <Stack direction="row" sx={{ justifyContent: "space-between", alignItems: "center" }}>
                                    <Typography variant="body2" sx={{ fontWeight: 800 }}>{item.label}</Typography>
                                    <Chip size="small" color={item.status === "PASS" ? "success" : item.status === "FAIL" ? "error" : item.status === "MIXED" ? "warning" : "default"} label={item.status} />
                                </Stack>
                                <Typography variant="caption" color="text.secondary" sx={{ display: "block" }}>Value: {item.value} · Rule: {item.threshold}</Typography>
                                <Typography variant="caption" color="text.secondary" sx={{ display: "block" }}>{item.reason} · {item.scoreEffect}</Typography>
                            </Box>
                        ))}</Stack>}
                    </Section>

                    <Section title="Demand / Supply Analysis">
                        <Grid container spacing={1}>
                            <Grid size={{ xs: 6 }}><Field label="Current zone" value={currentZone} /></Grid>
                            <Grid size={{ xs: 6 }}><Field label="Zone type" value={result.zone_type} /></Grid>
                            <Grid size={{ xs: 6 }}><Field label="Freshness" value={analysis ? analysis.retests === 0 ? "Fresh" : "Previously tested" : "Calculating…"} note="A wick intersection counts as a retest." /></Grid>
                            <Grid size={{ xs: 6 }}><Field label="Later retests" value={analysis ? String(analysis.retests) : "Calculating…"} /></Grid>
                            <Grid size={{ xs: 6 }}><Field label="First retest" value={analysis?.firstRetest ?? (analysis ? "No later retest" : "Calculating…")} /></Grid>
                            <Grid size={{ xs: 6 }}><Field label="Latest retest" value={analysis?.latestRetest ?? (analysis ? "No later retest" : "Calculating…")} /></Grid>
                            <Grid size={{ xs: 6 }}><Field label="Maximum penetration" value={analysis ? `${analysis.maximumPenetration.toFixed(1)}%` : "Calculating…"} /></Grid>
                            <Grid size={{ xs: 6 }}><Field label="Current status" value={analysis?.positionExplanation ?? "Calculating…"} /></Grid>
                            <Grid size={{ xs: 6 }}><Field label="Distance from zone" value={analysis ? `${analysis.distanceFromZone.toFixed(2)}%` : "Calculating…"} /></Grid>
                            <Grid size={{ xs: 6 }}><Field label="Zone quality" value={`${result.zone_score.toFixed(0)} / 100`} /></Grid>
                            <Grid size={{ xs: 6 }}><Field label="Departure" value={result.strength_score >= 70 ? "Strong" : "Needs caution"} /></Grid>
                            <Grid size={{ xs: 6 }}><Field label="Nearest demand" value={result.zone_type === "DEMAND" ? currentZone : "Not available"} /></Grid>
                            <Grid size={{ xs: 6 }}><Field label="Nearest supply" value={result.zone_type === "SUPPLY" ? currentZone : "Not available"} /></Grid>
                        </Grid>
                    </Section>

                    <Section title="Trend and Momentum">
                        <Grid container spacing={1}>
                            <Grid size={{ xs: 6 }}><Field label="Short-term trend" value={analysis?.shortTrend ?? "Calculating…"} note="Change over the latest 10 candles." /></Grid>
                            <Grid size={{ xs: 6 }}><Field label="Medium-term trend" value={analysis?.mediumTrend ?? "Calculating…"} note="Change over the latest 30 candles." /></Grid>
                            <Grid size={{ xs: 6 }}><Field label="Long-term trend" value={analysis?.longTrend ?? "Calculating…"} note="Change over the latest 100 candles." /></Grid>
                            <Grid size={{ xs: 6 }}><Field label="Overall trend" value={analysis?.overallTrend ?? "Calculating…"} /></Grid>
                            <Grid size={{ xs: 6 }}><Field label="EMA 20" value={analysis ? number(analysis.ema20) : "Calculating…"} /></Grid>
                            <Grid size={{ xs: 6 }}><Field label="EMA 50" value={analysis ? number(analysis.ema50) : "Calculating…"} /></Grid>
                            <Grid size={{ xs: 6 }}><Field label="EMA 200" value={analysis ? number(analysis.ema200) : "Calculating…"} /></Grid>
                            <Grid size={{ xs: 6 }}><Field label="EMA alignment" value={analysis?.emaAlignment ?? "Calculating…"} note={analysis?.emaAlignment === "Mixed" ? `EMA 20 is ${analysis.ema20 !== null && analysis.ema50 !== null && analysis.ema20 > analysis.ema50 ? "above" : "below"} EMA 50, but the full direction does not agree${analysis.ema200 === null ? " because EMA 200 needs more history" : " with EMA 200"}.` : undefined} /></Grid>
                            <Grid size={{ xs: 6 }}><Field label="RSI (14)" value={analysis ? number(analysis.rsi14) : "Calculating…"} note={analysis ? `RSI is ${analysis.rsiDirection.toLowerCase()}.` : undefined} /></Grid>
                            <Grid size={{ xs: 6 }}><Field label="ATR (14)" value={analysis ? number(analysis.atr14) : "Calculating…"} note="ATR estimates normal price movement." /></Grid>
                            <Grid size={{ xs: 6 }}><Field label="Current volume" value={analysis ? analysis.currentVolume?.toLocaleString("en-IN") ?? "Volume unavailable from source" : "Calculating…"} /></Grid>
                            <Grid size={{ xs: 6 }}><Field label="Relative volume" value={analysis ? number(analysis.relativeVolume, "×") : "Calculating…"} note="Compared with the latest 20 periods." /></Grid>
                            <Grid size={{ xs: 12 }}><Field label="Buying and selling pressure" value={analysis?.pressure ?? "Calculating…"} note={analysis ? `${analysis.pressureConfidence} confidence. This is an OHLCV estimate, not true bid/ask order flow.` : undefined} /></Grid>
                        </Grid>
                    </Section>

                    <Section title="Sector and Relative Performance">
                        <Grid container spacing={1}>
                            <Grid size={{ xs: 6 }}><Field label="Current sector" value={backendAnalysis?.sector.name ?? "Loading maintained mapping…"} /></Grid>
                            <Grid size={{ xs: 6 }}><Field label="Sector benchmark" value={backendAnalysis?.sector.benchmark ?? "Sector benchmark mapping required"} /></Grid>
                            {(["1m", "3m", "6m"] as const).map((period) => {
                                const comparison = backendAnalysis?.nifty_comparison[period];
                                return <Grid key={period} size={{ xs: 6 }}><Field label={`${period.toUpperCase()} stock vs Nifty`} value={comparison?.difference === undefined ? comparison?.status ?? "Calculating…" : `${comparison.difference >= 0 ? "+" : ""}${comparison.difference.toFixed(2)}% · ${comparison.status.toLowerCase()}`} /></Grid>;
                            })}
                            <Grid size={{ xs: 6 }}><Field label="Overall relative strength" value={(() => {
                                if (!backendAnalysis) return "Calculating…";
                                const values = Object.values(backendAnalysis.nifty_comparison).filter((item) => typeof item.difference === "number");
                                if (!values.length) return "Insufficient aligned history";
                                const average = values.reduce((sum, item) => sum + (item.difference ?? 0), 0) / values.length;
                                return average > 2 ? "Outperforming" : average < -2 ? "Underperforming" : "Matching Market";
                            })()} /></Grid>
                            <Grid size={{ xs: 6 }}><Field label="Stock vs sector (3M)" value={backendAnalysis?.sector.comparison?.["3m"]?.difference === undefined ? backendAnalysis?.sector.status ?? "Calculating…" : `${backendAnalysis.sector.comparison["3m"].difference! >= 0 ? "+" : ""}${backendAnalysis.sector.comparison["3m"].difference!.toFixed(2)}%`} /></Grid>
                            <Grid size={{ xs: 6 }}><Field label="True institutional money flow" value="Requires institutional-flow data" /></Grid>
                        </Grid>
                    </Section>

                    <Section title="Multiple Timeframes">
                        <Stack spacing={.8}>
                            {backendAnalysis?.multi_timeframe.frames.map((frame) => <Box key={frame.timeframe} sx={{ p: 1, border: "1px solid", borderColor: "divider", borderRadius: 1.25 }}>
                                <Stack direction="row" sx={{ justifyContent: "space-between" }}><Typography sx={{ fontWeight: 800 }}>{frame.timeframe}</Typography><Chip size="small" label={frame.confirmation === "CONFIRMED" ? "Aligned" : frame.confirmation === "NOT_CONFIRMED" ? "Not Aligned" : frame.confirmation === "MIXED" ? "Partially Aligned" : "Insufficient History"} color={frame.confirmation === "CONFIRMED" ? "success" : "default"} /></Stack>
                                <Typography variant="caption" color="text.secondary">Trend: {frame.trend.toLowerCase()} · EMA alignment: {frame.ema_alignment.toLowerCase()}</Typography>
                            </Box>) ?? <Typography color="text.secondary">Calculating daily, weekly and monthly confirmation…</Typography>}
                            {backendAnalysis && <Typography variant="caption" color="text.secondary">Combined result: {backendAnalysis.multi_timeframe.status === "CONFIRMED" ? "Aligned" : backendAnalysis.multi_timeframe.status === "MIXED" ? "Partially Aligned" : "Not Aligned"}</Typography>}
                        </Stack>
                    </Section>

                    <Section title="History and Risk">
                        <Grid container spacing={1}>
                            {["Similar past zones", "Average gain", "Average loss", "Historical success rate", "Probability", "Volatility", "Gap risk", "Liquidity"].map((label) => (
                                <Grid key={label} size={{ xs: 6 }}><Field label={label} value={label === "Volatility" && analysis ? number(analysis.atr14) : label === "Liquidity" ? "Requires average traded-value rules" : label === "Gap risk" ? "Requires next-session gap history" : "Requires historical-zone backtest"} /></Grid>
                            ))}
                        </Grid>
                        <Typography variant="caption" color="text.secondary">{unavailable}: historical testing and probability need a validated, time-safe zone backtest. They are never guessed.</Typography>
                    </Section>

                    <Section title="Actions">
                        <Grid container spacing={1}>
                            <Grid size={{ xs: 6 }}><Button fullWidth variant="outlined" startIcon={<BookmarkAddRoundedIcon />} onClick={addToWatchlist}>Add to Watchlist</Button></Grid>
                            <Grid size={{ xs: 6 }}><Button fullWidth variant="outlined" startIcon={<AddAlertRoundedIcon />} onClick={createAlert}>Create Alert</Button></Grid>
                            <Grid size={{ xs: 6 }}><Button fullWidth variant="outlined" startIcon={<OpenInFullRoundedIcon />} onClick={() => setMessage("You are already viewing the full chart.")}>Open Full Chart</Button></Grid>
                            <Grid size={{ xs: 6 }}><Button fullWidth variant="outlined" startIcon={<ShareRoundedIcon />} onClick={() => void share()}>Share Analysis</Button></Grid>
                        </Grid>
                    </Section>
                </Stack>
            </CardContent>
            <Snackbar open={Boolean(message)} autoHideDuration={2500} onClose={() => setMessage("")} message={message} />
        </Card>
    );
}

export default ZoneExplanationPanel;
