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
import { useMemo, useState } from "react";

import type { ZoneExplanationFactor, ZoneResearchResult } from "../../types/scanner";

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

function recommendation(result: ZoneResearchResult) {
    if (result.status === "IN ZONE" && result.zone_score >= 75) return "Wait for confirmation";
    if (result.distance_percent <= 3 && result.zone_score >= 75) return "Watch closely";
    if (result.zone_score >= 75) return "Add to watchlist";
    if (result.zone_score >= 60) return "Wait for stronger evidence";
    return "Avoid for now";
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
    const explanation = result.explanation;
    const positiveKeys = useMemo(() => new Set(explanation.positive_factors.map((factor) => factor.key.toLowerCase())), [explanation.positive_factors]);
    const qualityConfidence = result.zone_score >= 75 ? "High rule confidence" : result.zone_score >= 60 ? "Medium rule confidence" : "Low rule confidence";
    const currentZone = `${result.distal_price.toLocaleString("en-IN")} – ${result.proximal_price.toLocaleString("en-IN")}`;
    const checks = [
        ["Fresh zone", result.is_fresh],
        ["Strong departure", result.strength_score >= 70],
        ["Few retests", result.touch_count <= 1],
        ["Extra zone support", result.merge_score >= 50],
        ["Moving-average alignment", positiveKeys.has("ema_alignment")],
        ["Volume confirmation", positiveKeys.has("volume_confirmation")],
        ["Trend confirmation", positiveKeys.has("trend_confirmation")],
        ["Sector strength", positiveKeys.has("sector_strength")],
        ["Relative strength", positiveKeys.has("relative_strength")],
        ["Risk and reward", positiveKeys.has("risk_reward")],
        ["Multiple timeframes", positiveKeys.has("multi_timeframe")],
    ] as const;

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
                            <Grid size={{ xs: 5 }}>
                                <Typography color="text.secondary" variant="overline">Zone quality</Typography>
                                <Stack direction="row" spacing={1} sx={{ alignItems: "baseline" }}>
                                    <Typography variant="h2">{explanation.overall_score.toFixed(0)}</Typography>
                                    <Typography color="text.secondary">/ 100</Typography>
                                </Stack>
                            </Grid>
                            <Grid size={{ xs: 7 }}>
                                <Chip label={recommendation(result)} color={result.zone_score >= 75 ? "success" : "warning"} />
                                <Typography sx={{ mt: 1, fontWeight: 800 }}>{qualityConfidence}</Typography>
                                <Typography variant="caption" color="text.secondary">Confidence in the rule checks, not the chance of profit.</Typography>
                            </Grid>
                        </Grid>
                        <Typography color="text.secondary" sx={{ mt: 1 }}>{explanation.summary}</Typography>
                    </Section>

                    <Section title="Trading Plan">
                        <Grid container spacing={1}>
                            <Grid size={{ xs: 6 }}><Field label="Current zone" value={currentZone} /></Grid>
                            <Grid size={{ xs: 6 }}><Field label="Expected holding period" value="Not available" /></Grid>
                            {["Entry trigger", "Stop loss", "Target 1", "Target 2", "Target 3", "Risk : Reward"].map((label) => (
                                <Grid key={label} size={{ xs: 6 }}><Field label={label} value="Needs trade-plan data" /></Grid>
                            ))}
                        </Grid>
                        <Typography variant="caption" color="text.secondary">AlphaEdge will not invent entry, stop or target prices. These require a validated trade-plan service.</Typography>
                    </Section>

                    <FactorList title="Why AlphaEdge selected this zone" factors={explanation.positive_factors} positive />
                    <FactorList title="What could weaken this setup" factors={explanation.negative_factors} positive={false} />

                    <Section title="AI Checklist">
                        <Stack spacing={.8}>
                            {checks.map(([label, passed]) => (
                                <Stack key={label} direction="row" sx={{ justifyContent: "space-between", alignItems: "center" }}>
                                    <Typography variant="body2">{label}</Typography>
                                    <Chip size="small" color={passed ? "success" : "default"} label={passed ? "PASS" : "NOT CONFIRMED"} />
                                </Stack>
                            ))}
                        </Stack>
                    </Section>

                    <Section title="Demand / Supply Analysis">
                        <Grid container spacing={1}>
                            <Grid size={{ xs: 6 }}><Field label="Current zone" value={currentZone} /></Grid>
                            <Grid size={{ xs: 6 }}><Field label="Zone type" value={result.zone_type} /></Grid>
                            <Grid size={{ xs: 6 }}><Field label="Freshness" value={result.is_fresh ? "Fresh" : "Previously tested"} /></Grid>
                            <Grid size={{ xs: 6 }}><Field label="Later retests" value={String(result.touch_count)} /></Grid>
                            <Grid size={{ xs: 6 }}><Field label="Zone quality" value={`${result.zone_score.toFixed(0)} / 100`} /></Grid>
                            <Grid size={{ xs: 6 }}><Field label="Departure" value={result.strength_score >= 70 ? "Strong" : "Needs caution"} /></Grid>
                            <Grid size={{ xs: 6 }}><Field label="Nearest demand" value={result.zone_type === "DEMAND" ? currentZone : "Not available"} /></Grid>
                            <Grid size={{ xs: 6 }}><Field label="Nearest supply" value={result.zone_type === "SUPPLY" ? currentZone : "Not available"} /></Grid>
                        </Grid>
                    </Section>

                    <Section title="Trend and Momentum">
                        <Grid container spacing={1}>
                            {["Short-term trend", "Medium-term trend", "Long-term trend", "RSI", "Volume", "Buying strength", "Selling pressure"].map((label) => (
                                <Grid key={label} size={{ xs: 6 }}><Field label={label} value="Data not available" /></Grid>
                            ))}
                        </Grid>
                    </Section>

                    <Section title="Sector and Relative Performance">
                        <Grid container spacing={1}>
                            {["Current sector", "Sector strength", "Sector rank", "Money flow", "Stock vs Nifty", "Stock vs sector"].map((label) => (
                                <Grid key={label} size={{ xs: 6 }}><Field label={label} value="Data not available" /></Grid>
                            ))}
                        </Grid>
                    </Section>

                    <Section title="History and Risk">
                        <Grid container spacing={1}>
                            {["Similar past zones", "Average gain", "Average loss", "Historical success rate", "Probability", "Volatility", "Gap risk", "Liquidity"].map((label) => (
                                <Grid key={label} size={{ xs: 6 }}><Field label={label} value="Data not available" /></Grid>
                            ))}
                        </Grid>
                        <Typography variant="caption" color="text.secondary">Historical testing and probability must come from a validated, time-safe backtest. They are never guessed.</Typography>
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
