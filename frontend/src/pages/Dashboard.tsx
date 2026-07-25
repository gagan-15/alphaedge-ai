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
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";

import { getDashboard } from "../api/dashboardApi";

import type { DashboardResult } from "../types/dashboard";

import AIInsightCard from "../components/dashboard/AIInsightCard";
import AlertCard from "../components/dashboard/AlertCard";
import BacktestCard from "../components/dashboard/BacktestCard";
import MarketOverview from "../components/dashboard/MarketOverview";
import TradingChart from "../components/dashboard/TradingChart";
import { getResearchLabel } from "../utils/researchLanguage";

function Dashboard() {
    const [dashboard, setDashboard] =
        useState<DashboardResult | null>(null);

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
                <Grid size={{ xs: 12, xl: 8 }}>
                    <TradingChart />
                </Grid>

                <Grid size={{ xs: 12, md: 6, xl: 2.25 }}>
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

                <Grid size={{ xs: 12, md: 6, xl: 1.75 }}>
                    <Stack spacing={1.5}>
                        <AIInsightCard
                            insight={dashboard.ai_explanation}
                        />
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
            </Grid>
        </Stack>
    );
}

export default Dashboard;
