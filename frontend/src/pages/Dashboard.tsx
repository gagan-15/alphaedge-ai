/**
 * Dashboard Page.
 *
 * Sprint:
 *     2.52 - Dashboard Page
 */

import { useEffect, useState } from "react";

import Grid from "@mui/material/Grid";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import CircularProgress from "@mui/material/CircularProgress";
import Box from "@mui/material/Box";

import { getDashboard } from "../api/dashboardApi";

import type { DashboardResult } from "../types/dashboard";

import AIInsightCard from "../components/dashboard/AIInsightCard";
import AlertCard from "../components/dashboard/AlertCard";
import BacktestCard from "../components/dashboard/BacktestCard";
import MarketOverview from "../components/dashboard/MarketOverview";
import PortfolioSummary from "../components/dashboard/PortfolioSummary";
import TradingChart from "../components/dashboard/TradingChart";

function Dashboard() {
    const [dashboard, setDashboard] =
        useState<DashboardResult | null>(null);

    useEffect(() => {
        async function loadDashboard() {
            try {
                const result = await getDashboard();
                setDashboard(result);
            } catch (error) {
                console.error("Failed to load dashboard.", error);
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
        <Stack spacing={3}>
            <MarketOverview market={dashboard.market} />

            <PortfolioSummary dashboard={dashboard} />

            <Grid
                container
                spacing={3}
            >
                <Grid size={{ xs: 12, xl: 9 }}>
                    <TradingChart />
                </Grid>

                <Grid size={{ xs: 12, xl: 3 }}>
                    <Stack spacing={3}>
                        <AIInsightCard
                            insight={dashboard.ai_explanation}
                        />

                        <AlertCard
                            alerts={dashboard.alerts}
                        />
                    </Stack>
                </Grid>

                <Grid size={{ xs: 12 }}>
                    <BacktestCard
                        backtest={dashboard.backtest}
                    />
                </Grid>
            </Grid>
        </Stack>
    );
}

export default Dashboard;