import { useState } from "react";

import CachedOutlinedIcon from "@mui/icons-material/CachedOutlined";
import DashboardCustomizeOutlinedIcon from "@mui/icons-material/DashboardCustomizeOutlined";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Chip from "@mui/material/Chip";
import Grid from "@mui/material/Grid";
import MenuItem from "@mui/material/MenuItem";
import Select from "@mui/material/Select";
import Stack from "@mui/material/Stack";
import ToggleButton from "@mui/material/ToggleButton";
import ToggleButtonGroup from "@mui/material/ToggleButtonGroup";
import Typography from "@mui/material/Typography";

import {
    AIMarketSummaryWidget,
    IndiaVixWidget,
    InstitutionalFlowWidget,
    MarketBreadthWidget,
    MarketHealthWidget,
    MarketRegimeWidget,
    OpportunitiesWidget,
    ParticipationChartWidget,
    RiskMeterWidget,
    SectorRotationWidget,
    SentimentWidget,
    SmartAlertsWidget,
    TradingBiasWidget,
    VerdictWidget,
} from "../components/market-overview/MarketOverviewWidgets";
import OverviewPanel from "../components/market-overview/OverviewPanel";

export default function MarketOverview() {
    const [market, setMarket] = useState("NSE");
    const [timeframe, setTimeframe] = useState("1D");
    const [lastUpdated, setLastUpdated] = useState("Not refreshed");

    return (
        <Box sx={{ width: "100%", maxWidth: 1600, mx: "auto", px: { xs: 0, lg: 1 } }}>
            <Stack spacing={2.5}>
                <Stack
                    direction={{ xs: "column", xl: "row" }}
                    spacing={2}
                    sx={{ justifyContent: "space-between", alignItems: { xl: "center" } }}
                >
                    <Box>
                        <Stack direction="row" spacing={1} sx={{ alignItems: "center", flexWrap: "wrap" }}>
                            <Typography variant="h4">Market Overview</Typography>
                            <Chip size="small" color="success" variant="outlined" label="MARKET OPEN" />
                        </Stack>
                        <Typography color="text.secondary" sx={{ mt: .65 }}>
                            Institutional market context for faster research decisions.
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                            Last updated: {lastUpdated}
                        </Typography>
                    </Box>

                    <Stack
                        direction={{ xs: "column", sm: "row" }}
                        spacing={1}
                        useFlexGap
                        sx={{ alignItems: { sm: "center" }, flexWrap: "wrap" }}
                    >
                        <Select size="small" value={market} onChange={(event) => setMarket(event.target.value)} sx={{ minWidth: 108 }}>
                            <MenuItem value="NSE">NSE</MenuItem>
                            <MenuItem value="BSE">BSE</MenuItem>
                        </Select>
                        <ToggleButtonGroup
                            size="small"
                            exclusive
                            value={timeframe}
                            onChange={(_, value) => value && setTimeframe(value)}
                        >
                            {["1D", "1W", "1M", "3M"].map((value) => (
                                <ToggleButton key={value} value={value}>{value}</ToggleButton>
                            ))}
                        </ToggleButtonGroup>
                        <Button
                            variant="outlined"
                            startIcon={<CachedOutlinedIcon />}
                            onClick={() => setLastUpdated(new Date().toLocaleTimeString("en-IN"))}
                        >
                            Refresh
                        </Button>
                        <Button variant="outlined" startIcon={<DashboardCustomizeOutlinedIcon />}>
                            Customize
                        </Button>
                    </Stack>
                </Stack>

                <OverviewPanel
                    title="AI Market Summary"
                    subtitle="A concise interpretation of market health, leadership, risk and the preferred research approach will appear here."
                    eyebrow="Executive intelligence"
                    accent="#8b5cf6"
                    minHeight={190}
                    action={<Chip size="small" label="TRANSPARENT DEMO LOGIC" variant="outlined" />}
                >
                    <AIMarketSummaryWidget />
                </OverviewPanel>

                <Grid container spacing={2.5}>
                    <Grid size={{ xs: 12, md: 6, lg: 3 }}><OverviewPanel title="Market Health" subtitle="Participation, momentum and trend strength" accent="#32d583" minHeight={310}><MarketHealthWidget /></OverviewPanel></Grid>
                    <Grid size={{ xs: 12, md: 6, lg: 3 }}><OverviewPanel title="Market Regime" subtitle="Trending, ranging or transition environment" accent="#6172f3" minHeight={310}><MarketRegimeWidget /></OverviewPanel></Grid>
                    <Grid size={{ xs: 12, md: 6, lg: 3 }}><OverviewPanel title="Trading Bias" subtitle="Preferred directional research posture" accent="#22d3ee" minHeight={310}><TradingBiasWidget /></OverviewPanel></Grid>
                    <Grid size={{ xs: 12, md: 6, lg: 3 }}><OverviewPanel title="Risk Meter" subtitle="Volatility and participation risk context" accent="#fdb022" minHeight={310}><RiskMeterWidget /></OverviewPanel></Grid>
                </Grid>

                <OverviewPanel
                    title="Market Participation Trend"
                    subtitle={`${market} participation workspace · ${timeframe} view`}
                    eyebrow="Breadth through time"
                    minHeight={420}
                    action={<Chip size="small" label="INTERACTIVE DEMO" variant="outlined" />}
                >
                    <ParticipationChartWidget />
                </OverviewPanel>

                <Grid container spacing={2.5}>
                    <Grid size={{ xs: 12, lg: 6 }}>
                        <OverviewPanel title="Sector Rotation" subtitle="Leadership, improvement and deterioration by sector" minHeight={330}>
                            <SectorRotationWidget />
                        </OverviewPanel>
                    </Grid>
                    <Grid size={{ xs: 12, lg: 6 }}>
                        <OverviewPanel title="Market Breadth" subtitle="Advancing, declining and unchanged participation" minHeight={330}>
                            <MarketBreadthWidget />
                        </OverviewPanel>
                    </Grid>
                </Grid>

                <Grid container spacing={2.5}>
                    <Grid size={{ xs: 12, md: 6, lg: 4 }}>
                        <OverviewPanel title="Institutional Flow" subtitle="FII and DII activity context" minHeight={280}>
                            <InstitutionalFlowWidget />
                        </OverviewPanel>
                    </Grid>
                    <Grid size={{ xs: 12, md: 6, lg: 4 }}>
                        <OverviewPanel title="India VIX" subtitle="Volatility level, direction and risk state" minHeight={280}>
                            <IndiaVixWidget />
                        </OverviewPanel>
                    </Grid>
                    <Grid size={{ xs: 12, md: 12, lg: 4 }}>
                        <OverviewPanel title="Market Sentiment" subtitle="Combined participation and risk context" minHeight={280}>
                            <SentimentWidget />
                        </OverviewPanel>
                    </Grid>
                </Grid>

                <Grid container spacing={2.5}>
                    <Grid size={{ xs: 12, lg: 6 }}>
                        <OverviewPanel title="AI Opportunities" subtitle="Research candidates that deserve deeper validation" minHeight={300}>
                            <OpportunitiesWidget />
                        </OverviewPanel>
                    </Grid>
                    <Grid size={{ xs: 12, lg: 6 }}>
                        <OverviewPanel title="Smart Alerts" subtitle="Important market conditions requiring attention" minHeight={300}>
                            <SmartAlertsWidget />
                        </OverviewPanel>
                    </Grid>
                </Grid>

                <OverviewPanel
                    title="Today's Verdict"
                    subtitle="The final market posture, preferred strategy, risk level and next scan will be summarized here."
                    eyebrow="Decision brief"
                    accent="#32d583"
                    minHeight={220}
                    action={<Chip size="small" color="warning" variant="outlined" label="DEMO VERDICT" />}
                >
                    <VerdictWidget />
                </OverviewPanel>
            </Stack>
        </Box>
    );
}
