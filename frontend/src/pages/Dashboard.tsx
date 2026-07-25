/**
 * Dashboard Page.
 *
 * Sprint:
 *     2.61 - Signals Panel
 */

import { useEffect, useState } from "react";

import Box from "@mui/material/Box";
import CircularProgress from "@mui/material/CircularProgress";
import Grid from "@mui/material/Grid";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Chip from "@mui/material/Chip";
import Divider from "@mui/material/Divider";
import Button from "@mui/material/Button";
import LinearProgress from "@mui/material/LinearProgress";
import TextField from "@mui/material/TextField";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";

import { getDashboard } from "../api/dashboardApi";

import type { DashboardResult } from "../types/dashboard";

import AIInsightCard from "../components/dashboard/AIInsightCard";
import AlertCard from "../components/dashboard/AlertCard";
import BacktestCard from "../components/dashboard/BacktestCard";
import MarketOverview from "../components/dashboard/MarketOverview";
import MarketPulseCard from "../components/dashboard/MarketPulseCard";
import TradingChart from "../components/dashboard/TradingChart";
import { getResearchLabel } from "../utils/researchLanguage";

function Dashboard() {
    const [dashboard, setDashboard] =
        useState<DashboardResult | null>(null);
    const [aiQuestion, setAiQuestion] = useState("");
    const [aiAnswer, setAiAnswer] = useState("");

    useEffect(() => {
        async function loadDashboard() {
            try {
                const result = await getDashboard();
                setDashboard(result);
            } catch (error) {
                console.error(
                    "Failed to load dashboard.",
                    error,
                );
            }
        }

        loadDashboard();
    }, []);

    function askAlphaEdge(prompt = aiQuestion) {
        const question = prompt.trim();
        if (!question) {
            setAiAnswer("Enter a market research question first.");
            return;
        }
        setAiQuestion(question);
        const normalized = question.toLowerCase();
        if (normalized.includes("risk")) {
            setAiAnswer(
                "Risk check: define invalidation before entry, limit account exposure, "
                + "and do not treat a quality score as a success probability.",
            );
        } else if (normalized.includes("news")) {
            setAiAnswer(
                "News impact is not connected to a verified provider yet. "
                + "Use the News & Events screen only as demo context until sources and timestamps are shown.",
            );
        } else if (normalized.includes("top stock")) {
            setAiAnswer(
                "AlphaEdge AI does not recommend a stock. Open Scanner to compare delayed "
                + "research zones by quality, freshness and distance.",
            );
        } else if (normalized.includes("strategy")) {
            setAiAnswer(
                "Strategy idea: combine a fresh zone with trend and market-structure confirmation, "
                + "then test the same rules historically before relying on them.",
            );
        } else {
            setAiAnswer(
                "Market outlook is research-only. Review breadth, trend, volatility and "
                + "fresh zones together; current demo panels are not a live market forecast.",
            );
        }
    }

    if (!dashboard) {
        return (
            <Box
                sx={{
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "center",
                    justifyContent: "center",
                    minHeight: "60vh",
                    gap: 2,
                }}
            >
                <CircularProgress />

                <Typography color="text.secondary">
                    Loading dashboard...
                </Typography>
            </Box>
        );
    }

    return (
        <Stack spacing={1.5}>
            <MarketOverview market={dashboard.market} />

            <Grid
                container
                spacing={1.5}
            >
                <Grid size={{ xs: 12, xl: 7 }}>
                    <TradingChart />
                </Grid>

                <Grid size={{ xs: 12, md: 6, xl: 2.5 }}>
                    <Card sx={{ height: "100%" }}>
                        <CardContent sx={{ p: 1.75 }}>
                            <Typography variant="h6" sx={{ mb: 1.25 }}>
                                AI Signals
                            </Typography>
                            {dashboard.signals.slice(0, 5).map((signal) => (
                                <Box key={signal.symbol}>
                                    <Box sx={{ display: "flex", justifyContent: "space-between", py: 1.1, gap: 1 }}>
                                        <Box>
                                            <Typography sx={{ fontWeight: 700, fontSize: "0.78rem" }}>
                                                {signal.symbol}
                                            </Typography>
                                            <Typography color="text.secondary" sx={{ fontSize: "0.68rem" }}>
                                                {signal.confidence}% conditions matched
                                            </Typography>
                                        </Box>
                                        <Chip
                                            size="small"
                                            color={signal.action === "BUY" ? "success" : signal.action === "SELL" ? "error" : "warning"}
                                            label={getResearchLabel(signal.action)}
                                            sx={{ fontSize: "0.62rem" }}
                                        />
                                    </Box>
                                    <Divider />
                                </Box>
                            ))}
                        </CardContent>
                    </Card>
                </Grid>

                <Grid size={{ xs: 12, md: 6, xl: 2.5 }}>
                    <Stack spacing={1.5}>
                        <AIInsightCard
                            insight={dashboard.ai_explanation}
                        />
                        <MarketPulseCard />
                    </Stack>
                </Grid>

                <Grid size={{ xs: 12, md: 6, xl: 3 }}>
                    <Card sx={{ height: "100%" }}><CardContent>
                        <Typography variant="h6" sx={{ mb: 1.5 }}>Top Movers</Typography>
                        {dashboard.signals.slice(0, 4).map((signal) => (
                            <Box key={signal.symbol} sx={{ display: "flex", justifyContent: "space-between", py: 0.75 }}>
                                <Typography>{signal.symbol}</Typography>
                                <Typography color={signal.action === "SELL" ? "error.main" : "success.main"}>
                                    {signal.confidence}%
                                </Typography>
                            </Box>
                        ))}
                    </CardContent></Card>
                </Grid>

                <Grid size={{ xs: 12, md: 6, xl: 3 }}>
                    <Card sx={{ height: "100%" }}><CardContent>
                        <Typography variant="h6" sx={{ mb: 1.5 }}>AI Strategy Builder</Typography>
                        {["Trend Following", "Demand Supply Swing", "RSI + MACD Combo"].map((strategy) => (
                            <Box key={strategy} sx={{ display: "flex", justifyContent: "space-between", py: 0.8 }}>
                                <Typography variant="body2">{strategy}</Typography>
                                <Typography variant="body2" color="success.main">Active</Typography>
                            </Box>
                        ))}
                    </CardContent></Card>
                </Grid>

                <Grid size={{ xs: 12, md: 6, xl: 3 }}>
                    <Card sx={{ height: "100%" }}><CardContent>
                        <Typography variant="h6">Portfolio Overview</Typography>
                        <Typography color="text.secondary" sx={{ mt: 2 }}>Total value</Typography>
                        <Typography variant="h5">₹{dashboard.portfolio.total_capital.toLocaleString("en-IN")}</Typography>
                        <Typography color="success.main" sx={{ mt: 1 }}>
                            ₹{dashboard.portfolio.invested_capital.toLocaleString("en-IN")} invested
                        </Typography>
                    </CardContent></Card>
                </Grid>

                <Grid size={{ xs: 12, md: 6, xl: 3 }}>
                    <AlertCard alerts={dashboard.alerts.slice(0, 2)} />
                </Grid>

                <Grid size={{ xs: 12, md: 6, xl: 3 }}>
                    <Card sx={{ height: "100%" }}><CardContent>
                        <Typography variant="h6" sx={{ mb: 1.25 }}>Sector Performance</Typography>
                        {[
                            ["Nifty IT", 78, "+1.62%"],
                            ["Nifty Bank", 66, "+1.15%"],
                            ["Nifty FMCG", 55, "+0.98%"],
                            ["Nifty Auto", 35, "-0.32%"],
                        ].map(([name, value, change]) => (
                            <Box key={name as string} sx={{ mb: 1 }}>
                                <Box sx={{ display: "flex", justifyContent: "space-between" }}>
                                    <Typography variant="caption">{name}</Typography>
                                    <Typography variant="caption" color={(change as string).startsWith("+") ? "success.main" : "error.main"}>{change}</Typography>
                                </Box>
                                <LinearProgress value={value as number} variant="determinate" color={(change as string).startsWith("+") ? "success" : "error"} />
                            </Box>
                        ))}
                    </CardContent></Card>
                </Grid>

                <Grid size={{ xs: 12, md: 6, xl: 3 }}>
                    <Card sx={{ height: "100%" }}><CardContent>
                        <Typography variant="h6">FII / DII Flow</Typography>
                        {[["FII", "+₹1,254.35 Cr"], ["DII", "+₹875.40 Cr"], ["Net", "+₹2,129.75 Cr"]].map(([name, value]) => (
                            <Box key={name} sx={{ display: "flex", justifyContent: "space-between", py: 1.25 }}>
                                <Typography color="text.secondary">{name}</Typography>
                                <Typography color="success.main">{value}</Typography>
                            </Box>
                        ))}
                    </CardContent></Card>
                </Grid>

                <Grid size={{ xs: 12, md: 6, xl: 3 }}>
                    <Card sx={{ height: "100%" }}><CardContent sx={{ textAlign: "center" }}>
                        <Typography variant="h6">Market Sentiment</Typography>
                        <Box sx={{ width: 110, height: 55, mx: "auto", mt: 2, border: "12px solid #26364d", borderBottom: 0, borderRadius: "110px 110px 0 0", borderTopColor: "success.main" }} />
                        <Typography variant="h4" sx={{ mt: 1 }}>72%</Typography>
                        <Typography color="success.main">Bullish conditions</Typography>
                    </CardContent></Card>
                </Grid>

                <Grid size={{ xs: 12, md: 6, xl: 3 }}>
                    <Card sx={{ height: "100%" }}><CardContent>
                        <Typography variant="h6" sx={{ mb: 1 }}>News & Events</Typography>
                        {[
                            ["09:15", "RBI keeps policy stance unchanged"],
                            ["08:45", "US market closes higher"],
                            ["08:30", "Crude oil prices ease"],
                            ["08:15", "FII buying in banking stocks"],
                        ].map(([time, news]) => (
                            <Box key={news} sx={{ display: "flex", gap: 1, py: 0.7 }}>
                                <Typography variant="caption" color="text.secondary">{time}</Typography>
                                <Typography variant="caption">{news}</Typography>
                            </Box>
                        ))}
                    </CardContent></Card>
                </Grid>

                <Grid size={{ xs: 12, lg: 8 }}>
                    <BacktestCard backtest={dashboard.backtest} />
                </Grid>
                <Grid size={{ xs: 12, lg: 4 }}>
                    <Card sx={{ height: "100%" }}><CardContent>
                        <Typography variant="h6">Risk Overview</Typography>
                        {[
                            ["Account risk", "1.25%"],
                            ["Daily loss limit", "2.00%"],
                            ["Risk–reward", "1 : 2.35"],
                        ].map(([label, value]) => (
                            <Box key={label} sx={{ display: "flex", justifyContent: "space-between", py: 1 }}>
                                <Typography color="text.secondary">{label}</Typography>
                                <Typography color="success.main">{value}</Typography>
                            </Box>
                        ))}
                    </CardContent></Card>
                </Grid>

                <Grid size={{ xs: 12 }}>
                    <Card><CardContent>
                        <Stack direction={{ xs: "column", lg: "row" }} spacing={1.25} sx={{ alignItems: { lg: "center" }, minWidth: 0 }}>
                            <Typography sx={{ fontWeight: 800, whiteSpace: "nowrap", flexShrink: 0 }}>Ask AlphaEdge AI</Typography>
                            <TextField
                                size="small"
                                value={aiQuestion}
                                onChange={(event) => setAiQuestion(event.target.value)}
                                onKeyDown={(event) => {
                                    if (event.key === "Enter") askAlphaEdge();
                                }}
                                placeholder="Ask about markets, stocks, risk or strategies..."
                                sx={{ flex: "1 1 260px", minWidth: 180 }}
                            />
                            <Button variant="contained" size="small" onClick={() => askAlphaEdge()}>Ask</Button>
                            <Stack direction="row" spacing={0.75} sx={{ flex: "0 1 auto", minWidth: 0, flexWrap: "wrap" }}>
                                {["Market Outlook", "Top Stocks", "Risk Check", "Strategy Idea", "News Impact"].map((label, index) => (
                                    <Button
                                        key={label}
                                        variant="outlined"
                                        size="small"
                                        onClick={() => askAlphaEdge(label)}
                                        sx={{
                                            whiteSpace: "nowrap",
                                            minWidth: 0,
                                            px: 1,
                                            display: {
                                                xs: "none",
                                                lg: index > 2 ? "none" : "inline-flex",
                                                xl: "inline-flex",
                                            },
                                        }}
                                    >
                                        {label}
                                    </Button>
                                ))}
                            </Stack>
                        </Stack>
                        {aiAnswer && (
                            <Box sx={{ mt: 1.5, p: 1.25, borderRadius: 1.5, bgcolor: "rgba(99,102,241,.08)" }}>
                                <Typography variant="body2">{aiAnswer}</Typography>
                            </Box>
                        )}
                    </CardContent></Card>
                </Grid>
            </Grid>

            <Card
                square
                sx={{
                    display: "none",
                    position: "fixed",
                    left: { xs: 64, lg: 196 },
                    right: 0,
                    bottom: 0,
                    zIndex: 1100,
                    borderLeft: 0,
                    borderRight: 0,
                    borderBottom: 0,
                }}
            >
                <CardContent sx={{ display: "flex", gap: 4, py: "8px !important", overflow: "hidden" }}>
                    <Chip label="LIVE" size="small" color="success" />
                    {[
                        ["RELIANCE", "2,978.45 ▲ 0.83%"],
                        ["TCS", "3,584.75 ▼ 0.41%"],
                        ["HDFC BANK", "1,654.20 ▲ 1.12%"],
                        ["INFY", "1,512.10 ▲ 0.35%"],
                    ].map(([symbol, quote]) => (
                        <Typography key={symbol} variant="caption" sx={{ whiteSpace: "nowrap" }}>
                            {symbol}&nbsp;&nbsp;<Box component="span" color={quote.includes("▼") ? "error.main" : "success.main"}>{quote}</Box>
                        </Typography>
                    ))}
                </CardContent>
            </Card>
        </Stack>
    );
}

export default Dashboard;
