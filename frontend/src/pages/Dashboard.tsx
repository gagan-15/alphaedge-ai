/**
 * Dashboard Page.
 *
 * Sprint:
 *     2.52 - Dashboard Page
 */

import { useEffect, useState } from "react";

import Typography from "@mui/material/Typography";

import { getDashboard } from "../api/dashboardApi";

import type { DashboardResult } from "../types/dashboard";

import PortfolioSummary from "../components/dashboard/PortfolioSummary";

import AIInsightCard from "../components/dashboard/AIInsightCard";

import AlertCard from "../components/dashboard/AlertCard";

import Grid from "@mui/material/Grid";

import BacktestCard from "../components/dashboard/BacktestCard";

import MarketOverview from "../components/dashboard/MarketOverview";

import TradingChart from "../components/dashboard/TradingChart";

import Stack from "@mui/material/Stack";

function Dashboard() {
    const [dashboard, setDashboard] =
        useState<DashboardResult | null>(null);

    useEffect(() => {
        async function loadDashboard() {
            try {
                const result = await getDashboard();

                setDashboard(result);
            } catch (error) {
                console.error(error);
            }
        }

        loadDashboard();
    }, []);

    if (!dashboard) {
        return (
            <Typography variant="h5">
                Loading Dashboard...
            </Typography>
        );
    }

    console.log("Dashboard object:", dashboard);
    console.log("Market object:", dashboard.market);

   return (
    <>


        <MarketOverview market={dashboard.market} />

        <PortfolioSummary dashboard={dashboard} />

        <Grid
            container
            spacing={3}
            sx={{ mt: 1 }}
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
    </>
    );
}

export default Dashboard;