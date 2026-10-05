import AddAlertRoundedIcon from "@mui/icons-material/AddAlertRounded";
import BookmarkAddRoundedIcon from "@mui/icons-material/BookmarkAddRounded";
import CheckCircleRoundedIcon from "@mui/icons-material/CheckCircleRounded";
import ErrorOutlineRoundedIcon from "@mui/icons-material/ErrorOutlineRounded";
import ShareRoundedIcon from "@mui/icons-material/ShareRounded";
import TuneRoundedIcon from "@mui/icons-material/TuneRounded";
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
import TimeframeConfluenceExplorer from "./TimeframeConfluenceExplorer";
import type { ConfluenceChartOverlay } from "../../types/scanner";
import StockDetailsCustomizeDrawer from "./StockDetailsCustomizeDrawer";
import {
    defaultStockDetailsVisibility,
    type StockDetailsVisibility,
} from "./stockDetailsPreferences";
import { tradeConfidenceDisplay, tradeConfidenceExplanation } from "./tradeConfidenceRanking";
import ZoneQualityBreakdown from "./ZoneQualityBreakdown";
import { formatZoneQuality } from "./zoneQualityPresentation";
import ComparableHistoricalEvidenceSection from "./ComparableHistoricalEvidence";

const watchlistKey = "alphaedge.local.watchlist";
const watchlistZonesKey = "alphaedge.local.watchlist.zones";
const alertsKey = "alphaedge.local.alerts";
const stockDetailsVisibilityKey = "alphaedge.stock-details.visible-sections";

function readVisibility(): StockDetailsVisibility {
    try {
        const stored = JSON.parse(localStorage.getItem(stockDetailsVisibilityKey) ?? "{}") as Partial<StockDetailsVisibility>;
        return { ...defaultStockDetailsVisibility, ...stored };
    } catch {
        return defaultStockDetailsVisibility;
    }
}

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

function readObjects(key: string): Record<string, unknown>[] {
    try {
        const value = JSON.parse(localStorage.getItem(key) ?? "[]");
        return Array.isArray(value)
            ? value.filter((item): item is Record<string, unknown> => typeof item === "object" && item !== null)
            : [];
    } catch {
        return [];
    }
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

interface ZoneExplanationPanelProps {
    result: ZoneResearchResult;
    zones: ZoneResearchResult[];
    methodologyVersion: string;
    confluenceOverlays?: ConfluenceChartOverlay[];
    confluenceOverlaysHidden?: boolean;
    onToggleConfluenceOverlay?: (overlay: ConfluenceChartOverlay) => void;
    onToggleConfluenceVisibility?: () => void;
    onClearConfluenceOverlays?: () => void;
    onAvailableConfluenceOverlays?: (overlays: ConfluenceChartOverlay[]) => void;
    inspectedConfluenceTimeframe?: string;
}

function ZoneExplanationPanel({
    result,
    zones,
    methodologyVersion,
    confluenceOverlays = [],
    confluenceOverlaysHidden = false,
    onToggleConfluenceOverlay,
    onToggleConfluenceVisibility,
    onClearConfluenceOverlays,
    onAvailableConfluenceOverlays,
    inspectedConfluenceTimeframe,
}: ZoneExplanationPanelProps) {
    const [message, setMessage] = useState("");
    const selectedAnalysisKey = `${result.symbol}:${result.timeframe}:${result.zone_type}:${result.proximal_price}:${result.distal_price}:${result.base_index}`;
    const [calculatedAnalysis, setAnalysis] = useState<{ key: string; data: StockZoneAnalysis } | null>(null);
    const analysis = calculatedAnalysis?.key === selectedAnalysisKey ? calculatedAnalysis.data : null;
    const [receivedBackendAnalysis, setBackendAnalysis] = useState<StockDetailsBackendAnalysis | null>(null);
    const [analysisError, setAnalysisError] = useState("");
    const [scoreDetailsOpen, setScoreDetailsOpen] = useState(false);
    const [watchlistSavedKey, setWatchlistSavedKey] = useState("");
    const [alertSavedKey, setAlertSavedKey] = useState("");
    const [actionBusy, setActionBusy] = useState<"" | "watchlist" | "alert" | "share">("");
    const [customizeOpen, setCustomizeOpen] = useState(false);
    const [visibleSections, setVisibleSections] = useState<StockDetailsVisibility>(readVisibility);
    const explanation = result.explanation;
    const sameNumber = (left: number, right: number) => Math.abs(left - right) <= Math.max(0.01, Math.abs(right) * 0.000001);
    const backendAnalysis = receivedBackendAnalysis
        && receivedBackendAnalysis.symbol === result.symbol
        && receivedBackendAnalysis.selected_zone.symbol === result.symbol
        && receivedBackendAnalysis.selected_zone.zone_type === result.zone_type
        && receivedBackendAnalysis.selected_zone.timeframe === result.timeframe
        && sameNumber(receivedBackendAnalysis.selected_zone.proximal_price, result.proximal_price)
        && sameNumber(receivedBackendAnalysis.selected_zone.distal_price, result.distal_price)
        ? receivedBackendAnalysis
        : null;
    const currentZone = `${result.distal_price.toLocaleString("en-IN")} – ${result.proximal_price.toLocaleString("en-IN")}`;
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
            return { ...item, status: "UNAVAILABLE", value: "Execution stop policy is not defined", threshold: "Requires an approved protective-stop policy", reason: "Structural invalidation is not presented as a protective stop.", scoreEffect: "Not scored" } as const;
        }
        if (item.label === "Sector strength" && backendAnalysis) {
            const comparison = backendAnalysis.sector.sector_vs_nifty?.["3m"];
            if (comparison?.difference === undefined) {
                return { ...item, status: "UNAVAILABLE", value: backendAnalysis.sector.status ?? "Insufficient aligned sector history", threshold: "Requires a mapped sector index and aligned history", reason: "The sector comparison could not be calculated.", scoreEffect: "Context only" } as const;
            }
            const supportsDirection = result.zone_type === "DEMAND"
                ? comparison.difference > 2
                : comparison.difference < -2;
            const opposesDirection = result.zone_type === "DEMAND"
                ? comparison.difference < -2
                : comparison.difference > 2;
            return {
                ...item,
                status: supportsDirection ? "PASS" : opposesDirection ? "FAIL" : "MIXED",
                value: `${backendAnalysis.sector.name} is ${comparison.difference >= 0 ? "+" : ""}${comparison.difference.toFixed(2)}% versus Nifty over 3 months`,
                threshold: result.zone_type === "DEMAND" ? "Sector should beat Nifty by more than 2%" : "Sector should trail Nifty by more than 2%",
                reason: supportsDirection ? "The sector direction supports this zone." : opposesDirection ? "The sector direction works against this zone." : "The sector is moving close to the wider market.",
                scoreEffect: "Included in Trade Confidence only",
            } as const;
        }
        return item;
    });
    const canonicalConfidence = result.trade_confidence;
    const confidence = tradeConfidenceDisplay(canonicalConfidence);
    const zoneLower = Math.min(result.proximal_price, result.distal_price);
    const zoneUpper = Math.max(result.proximal_price, result.distal_price);
    const plan = backendAnalysis?.trade_plan;
    const planIsSynchronized = Boolean(plan
        && plan.symbol === result.symbol
        && plan.timeframe === result.timeframe
        && plan.zone_type === result.zone_type
        && plan.interaction_range
        && plan.planned_entry_reference !== null
        && plan.structural_invalidation !== null
        && sameNumber(plan.interaction_range[0], zoneLower)
        && sameNumber(plan.interaction_range[1], zoneUpper)
        && sameNumber(plan.planned_entry_reference, result.proximal_price)
        && sameNumber(plan.structural_invalidation, result.distal_price)
        && (plan.target === null || (result.zone_type === "DEMAND" ? plan.target > plan.planned_entry_reference : plan.target < plan.planned_entry_reference)));
    const watchlistAdded = watchlistSavedKey === selectedAnalysisKey
        || readObjects(watchlistZonesKey).some((item) => item.id === selectedAnalysisKey);
    const alertAdded = alertSavedKey === selectedAnalysisKey
        || readObjects(alertsKey).some((item) => item.zoneId === selectedAnalysisKey);

    function updateVisibleSections(next: StockDetailsVisibility) {
        if (!Object.values(next).some(Boolean)) return;
        setVisibleSections(next);
        localStorage.setItem(stockDetailsVisibilityKey, JSON.stringify(next));
    }

    useEffect(() => {
        let active = true;
        const intraday = ["5m", "15m", "75m", "125m", "1H", "2H", "4H", "6H"].includes(result.timeframe);
        const period = intraday ? "1mo" : result.timeframe === "1D" ? "1y" : "10y";
        const interval = intraday ? (result.timeframe.includes("H") ? "1h" : result.timeframe === "5m" || result.timeframe === "125m" ? "5m" : "15m") : "1d";
        void getMarketCandles(result.symbol, period, interval, result.timeframe)
            .then((response) => { if (active) setAnalysis({ key: selectedAnalysisKey, data: analyzeStockZone(result, response.candles) }); })
            .catch(() => { if (active) setAnalysisError("Calculation failed because candle history could not be loaded."); });
        void getStockDetailsAnalysis(result)
            .then((response) => { if (active) setBackendAnalysis(response); })
            .catch(() => { if (active) setBackendAnalysis(null); });
        return () => { active = false; };
    }, [result, selectedAnalysisKey]);

    function addToWatchlist() {
        if (watchlistAdded) return;
        setActionBusy("watchlist");
        try {
            saveUnique(watchlistKey, result.symbol);
            localStorage.setItem(watchlistZonesKey, JSON.stringify([...readObjects(watchlistZonesKey), {
                id: selectedAnalysisKey,
                symbol: result.symbol,
                zoneType: result.zone_type,
                proximalPrice: result.proximal_price,
                distalPrice: result.distal_price,
                timeframe: result.timeframe,
                baseDate: result.base_date,
            }]));
            setWatchlistSavedKey(selectedAnalysisKey);
            setMessage(`${result.symbol} and this zone were added to your watchlist.`);
        } catch {
            setMessage("The watchlist could not be updated. Please try again.");
        } finally {
            setActionBusy("");
        }
    }

    function createAlert() {
        if (alertAdded) return;
        setActionBusy("alert");
        const existing = readObjects(alertsKey);
        const condition = result.zone_type === "DEMAND" ? "below" : "above";
        const target = result.proximal_price;
        try {
            localStorage.setItem(alertsKey, JSON.stringify([...existing, {
                id: crypto.randomUUID(),
                zoneId: selectedAnalysisKey,
                symbol: result.symbol,
                condition,
                target,
                current: null,
                enabled: true,
                alertType: "PRICE_TOUCHES_PROXIMAL",
                zoneType: result.zone_type,
                timeframe: result.timeframe,
            }]));
            setAlertSavedKey(selectedAnalysisKey);
            setMessage(`Alert created for price touching ₹${target.toLocaleString("en-IN")}.`);
        } catch {
            setMessage("The alert could not be created. Please try again.");
        } finally {
            setActionBusy("");
        }
    }

    async function share() {
        setActionBusy("share");
        const text = `${result.symbol} ${result.zone_type} zone ${currentZone}. Quality ${formatZoneQuality(result.zone_score)}/100. Research only.`;
        try {
            if (navigator.share) await navigator.share({ title: "AlphaEdge AI zone research", text });
            else await navigator.clipboard.writeText(text);
            setMessage(navigator.share ? "Share window opened." : "Analysis copied.");
        } catch (error) {
            setMessage(error instanceof DOMException && error.name === "AbortError"
                ? "Sharing was cancelled."
                : "The analysis could not be shared. Please try again.");
        } finally {
            setActionBusy("");
        }
    }

    return (
        <Card variant="outlined" sx={{ mb: 1.5, overflow: "hidden" }}>
            <CardContent>
                <Stack direction="row" sx={{ justifyContent: "flex-end", mb: 1 }}>
                    <Button size="small" variant="outlined" startIcon={<TuneRoundedIcon />} onClick={() => setCustomizeOpen(true)}>
                        Customize
                    </Button>
                </Stack>
                <Stack spacing={2.25} divider={<Divider flexItem />}>
                    {visibleSections.decision && <Section title="AI Decision">
                        <Grid container spacing={1.5}>
                            <Grid size={{ xs: 12 }}>
                                <Typography color="text.secondary" variant="overline">Trade Confidence</Typography>
                                <Stack direction="row" spacing={1} sx={{ alignItems: "baseline" }}>
                                    <Typography variant="h1">{confidence.score}</Typography>
                                    <Typography color="text.secondary">/ 100</Typography>
                                </Stack>
                                <Chip sx={{ mt: .5 }} label={analysis?.broken ? "Invalidated" : confidence.label} color={analysis?.broken ? "error" : (canonicalConfidence?.score ?? 0) >= 75 ? "success" : "warning"} />
                                <Typography sx={{ mt: 1, fontWeight: 700 }}>This score summarizes zone quality, higher-timeframe location and trend context. It is not a trade instruction.</Typography>
                            </Grid>
                            <Grid size={{ xs: 12 }}>
                                <ZoneQualityBreakdown result={result} />
                            </Grid>
                            <Grid size={{ xs: 12 }}>
                                <Typography sx={{ mt: 1, fontWeight: 800 }}>Context data: {canonicalConfidence?.data_sufficiency.replaceAll("_", " ") ?? "Unavailable"}</Typography>
                                <Typography variant="caption" color="text.secondary">This shows data coverage, not the chance of profit.</Typography>
                            </Grid>
                        </Grid>
                        <Typography sx={{ mt: 1.5 }}>{tradeConfidenceExplanation(canonicalConfidence)}</Typography>
                        <Typography color="text.secondary" sx={{ mt: 1 }}>{explanation.summary}</Typography>
                        <Button size="small" sx={{ mt: 1 }} onClick={() => setScoreDetailsOpen((open) => !open)}>{scoreDetailsOpen ? "Hide score explanation" : "Why is Trade Confidence this score?"}</Button>
                        {scoreDetailsOpen && <Stack spacing={1} sx={{ mt: 1 }}>
                            <Typography sx={{ fontWeight: 800 }}>Trade Confidence breakdown</Typography>
                            {canonicalConfidence ? <>
                                <Field label="Zone Quality contribution" value={`${canonicalConfidence.zone_quality_contribution.toFixed(2)} / 40`} />
                                <Field label="Higher-timeframe location contribution" value={`${canonicalConfidence.location_contribution.toFixed(2)} / 35`} note={canonicalConfidence.location_alignment.replaceAll("_", " ")} />
                                <Field label="Canonical Trend contribution" value={`${canonicalConfidence.trend_contribution.toFixed(2)} / 25`} note={canonicalConfidence.trend_alignment.replaceAll("_", " ")} />
                                <Field label="Combined context" value={canonicalConfidence.combined_context.replaceAll("_", " ")} />
                                {canonicalConfidence.evidence.map((item) => <Typography key={item} variant="caption" color="text.secondary">{item}</Typography>)}
                            </> : <Typography color="text.secondary">Canonical context is unavailable for this zone.</Typography>}
                            <Typography variant="caption" color="text.secondary">Trade Confidence uses the frozen 40% Zone Quality, 35% higher-timeframe location and 25% Canonical Trend formula.</Typography>
                        </Stack>}
                    </Section>}

                    {visibleSections.plan && <Section title="Trading Plan">
                        {receivedBackendAnalysis && !planIsSynchronized
                            ? <Typography color="warning.main">Trading plan unavailable because the selected analysis is out of sync.</Typography>
                            : <Grid container spacing={1}>
                            <Grid size={{ xs: 6 }}><Field label="Interaction range" value={plan?.interaction_range ? `₹${plan.interaction_range[0].toLocaleString("en-IN")} – ₹${plan.interaction_range[1].toLocaleString("en-IN")}` : "Calculating from the selected zone…"} note="The exact price area defined by the selected canonical zone." /></Grid>
                            <Grid size={{ xs: 6 }}><Field label="Expected holding period" value="Requires a validated outcome backtest" /></Grid>
                            <Grid size={{ xs: 6 }}><Field label="Proximal entry reference" value={plan?.planned_entry_reference != null ? `₹${plan.planned_entry_reference.toLocaleString("en-IN")}` : "Unavailable"} note="A structural planning coordinate, not a confirmed entry." /></Grid>
                            <Grid size={{ xs: 6 }}><Field label="Structural invalidation" value={plan?.structural_invalidation != null ? `₹${plan.structural_invalidation.toLocaleString("en-IN")}` : "Unavailable"} note="The distal boundary where the zone structure is no longer valid. This is not a protective stop." /></Grid>
                            <Grid size={{ xs: 6 }}><Field label="Nearest structural target" value={plan?.target != null ? `₹${plan.target.toLocaleString("en-IN")}` : "No valid opposing zone"} note="The nearest eligible opposite zone on the same timeframe." /></Grid>
                            <Grid size={{ xs: 6 }}><Field label="Available room" value={plan?.available_room != null ? `₹${plan.available_room.toLocaleString("en-IN")}` : "Unavailable without a target"} /></Grid>
                            <Grid size={{ xs: 6 }}><Field label="Protective stop" value="Not defined by structural plan" note="A future execution and risk policy must define it." /></Grid>
                            <Grid size={{ xs: 6 }}><Field label="Risk : Reward" value="Unavailable" note="Risk cannot be calculated until an execution stop policy is defined." /></Grid>
                            <Grid size={{ xs: 6 }}><Field label="Plan status" value={plan?.status.replaceAll("_", " ") ?? "Calculating…"} /></Grid>
                            <Grid size={{ xs: 6 }}><Field label="Structural reward per share" value={plan?.structural_reward_per_share != null ? `₹${plan.structural_reward_per_share.toLocaleString("en-IN")}` : "Unavailable without a target"} /></Grid>
                        </Grid>}
                        {planIsSynchronized && <Typography variant="caption" color="text.secondary">Research only. This structural plan does not place orders or define an execution-ready stop.</Typography>}
                    </Section>}

                    {visibleSections.strengths && <FactorList title="Why AlphaEdge selected this zone" factors={explanation.positive_factors} positive />}
                    {visibleSections.weaknesses && <FactorList title="What could weaken this setup" factors={explanation.negative_factors} positive={false} />}

                    {visibleSections.checklist && <Section title="AI Checklist">
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
                    </Section>}

                    {visibleSections.zoneAnalysis && <Section title="Demand / Supply Analysis">
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
                            <Grid size={{ xs: 6 }}><Field label="Zone quality" value={`${formatZoneQuality(result.zone_score)} / 100`} /></Grid>
                            <Grid size={{ xs: 6 }}><Field label="Departure" value={result.strength_score >= 70 ? "Strong" : "Needs caution"} /></Grid>
                            <Grid size={{ xs: 6 }}><Field label="Nearest demand" value={result.zone_type === "DEMAND" ? currentZone : "Not available"} /></Grid>
                            <Grid size={{ xs: 6 }}><Field label="Nearest supply" value={result.zone_type === "SUPPLY" ? currentZone : "Not available"} /></Grid>
                        </Grid>
                    </Section>}

                    {visibleSections.trend && <Section title="Trend and Momentum">
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
                    </Section>}

                    {visibleSections.sector && <Section title="Sector and Relative Performance">
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
                    </Section>}

                    {visibleSections.timeframes && <Section title="Multiple Timeframes">
                        <Stack spacing={.8}>
                            {backendAnalysis?.multi_timeframe.frames.map((frame) => <Box key={frame.timeframe} sx={{ p: 1, border: "1px solid", borderColor: "divider", borderRadius: 1.25 }}>
                                <Stack direction="row" sx={{ justifyContent: "space-between" }}><Typography sx={{ fontWeight: 800 }}>{frame.timeframe}</Typography><Chip size="small" label={frame.confirmation === "CONFIRMED" ? "Aligned" : frame.confirmation === "NOT_CONFIRMED" ? "Not Aligned" : frame.confirmation === "MIXED" ? "Partially Aligned" : "Insufficient History"} color={frame.confirmation === "CONFIRMED" ? "success" : "default"} /></Stack>
                                <Typography variant="caption" color="text.secondary">Trend: {frame.trend.toLowerCase()} · EMA alignment: {frame.ema_alignment.toLowerCase()}</Typography>
                            </Box>) ?? <Typography color="text.secondary">Calculating daily, weekly and monthly confirmation…</Typography>}
                            {backendAnalysis && <Typography variant="caption" color="text.secondary">Combined result: {backendAnalysis.multi_timeframe.status === "CONFIRMED" ? "Aligned" : backendAnalysis.multi_timeframe.status === "MIXED" ? "Partially Aligned" : "Not Aligned"}</Typography>}
                        </Stack>
                    </Section>}

                    {visibleSections.confluence && onToggleConfluenceOverlay && onToggleConfluenceVisibility && onClearConfluenceOverlays && onAvailableConfluenceOverlays && (
                        <Section title="Higher Timeframe Confluence">
                            <TimeframeConfluenceExplorer
                                result={result}
                                activeTimeframes={confluenceOverlays.map((overlay) => overlay.timeframe)}
                                overlaysHidden={confluenceOverlaysHidden}
                                onToggleOverlay={onToggleConfluenceOverlay}
                                onToggleVisibility={onToggleConfluenceVisibility}
                                onClearOverlays={onClearConfluenceOverlays}
                                onAvailableOverlays={onAvailableConfluenceOverlays}
                                inspectedTimeframe={inspectedConfluenceTimeframe}
                            />
                        </Section>
                    )}

                    {visibleSections.history && (
                        <ComparableHistoricalEvidenceSection
                            result={result}
                            zones={zones}
                            methodologyVersion={methodologyVersion}
                        />
                    )}

                    {visibleSections.actions && <Section title="Actions">
                        <Grid container spacing={1}>
                            <Grid size={{ xs: 6 }}><Button fullWidth variant="outlined" disabled={watchlistAdded || actionBusy === "watchlist"} startIcon={<BookmarkAddRoundedIcon />} onClick={addToWatchlist}>{watchlistAdded ? "Added" : "Add to Watchlist"}</Button></Grid>
                            <Grid size={{ xs: 6 }}><Button fullWidth variant="outlined" disabled={alertAdded || actionBusy === "alert"} startIcon={<AddAlertRoundedIcon />} onClick={createAlert}>{alertAdded ? "Alert Created" : "Create Alert"}</Button></Grid>
                            <Grid size={{ xs: 12 }}><Button fullWidth variant="outlined" disabled={actionBusy === "share"} startIcon={<ShareRoundedIcon />} onClick={() => void share()}>{actionBusy === "share" ? "Sharing…" : "Share Analysis"}</Button></Grid>
                        </Grid>
                    </Section>}
                </Stack>
            </CardContent>
            <StockDetailsCustomizeDrawer
                open={customizeOpen}
                value={visibleSections}
                onClose={() => setCustomizeOpen(false)}
                onChange={updateVisibleSections}
            />
            <Snackbar open={Boolean(message)} autoHideDuration={2500} onClose={() => setMessage("")} message={message} />
        </Card>
    );
}

export default ZoneExplanationPanel;
