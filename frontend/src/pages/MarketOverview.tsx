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
import MarketOverviewCustomizeDrawer from "../components/market-overview/MarketOverviewCustomizeDrawer";
import OverviewPanel from "../components/market-overview/OverviewPanel";
import {
    loadMarketOverviewPreferences,
    saveMarketOverviewPreferences,
} from "../components/market-overview/marketOverviewPreferences";
import { useAuth } from "../auth/AuthState";

export default function MarketOverview() {
    const { user } = useAuth();
    const userKey = user?.id ?? "local-demo";
    const [savedPreferences, setSavedPreferences] = useState(() => loadMarketOverviewPreferences(userKey));
    const [previewPreferences, setPreviewPreferences] = useState(savedPreferences);
    const [customizeOpen, setCustomizeOpen] = useState(false);
    const [customizeSession, setCustomizeSession] = useState(0);
    const [market, setMarket] = useState("NSE");
    const [timeframe, setTimeframe] = useState("1D");
    const [lastUpdated, setLastUpdated] = useState("Not refreshed");
    const visible = previewPreferences.visibleWidgets;

    function saveCustomization(next: typeof savedPreferences) {
        saveMarketOverviewPreferences(userKey, next);
        setSavedPreferences(next);
        setPreviewPreferences(next);
        setCustomizeOpen(false);
    }

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
                            A simple view of what the market is doing and what you may want to check next.
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
                        <Button variant="outlined" startIcon={<DashboardCustomizeOutlinedIcon />} onClick={() => { setPreviewPreferences(savedPreferences); setCustomizeSession((value) => value + 1); setCustomizeOpen(true); }}>
                            Customize
                        </Button>
                    </Stack>
                </Stack>

                {visible.aiSummary && <OverviewPanel
                    title="AI Market Summary"
                    subtitle="A clear explanation of today's market, the main risks and what to research next."
                    eyebrow="Today's market explained"
                    accent="#8b5cf6"
                    minHeight={190}
                    action={<Chip size="small" label="TRANSPARENT DEMO LOGIC" variant="outlined" />}
                >
                    <AIMarketSummaryWidget />
                </OverviewPanel>}

                {(visible.marketHealth || visible.marketTrend || visible.researchFocus || visible.marketRisk) && <Grid container spacing={2.5}>
                    {visible.marketHealth && <Grid size={{ xs: 12, md: 6, lg: 3 }}><OverviewPanel title="Market Health" subtitle="Are most stocks supporting today's market move?" accent="#32d583" minHeight={310}><MarketHealthWidget /></OverviewPanel></Grid>}
                    {visible.marketTrend && <Grid size={{ xs: 12, md: 6, lg: 3 }}><OverviewPanel title="Market Direction" subtitle="Is the market rising, falling or moving sideways?" accent="#6172f3" minHeight={310}><MarketRegimeWidget /></OverviewPanel></Grid>}
                    {visible.researchFocus && <Grid size={{ xs: 12, md: 6, lg: 3 }}><OverviewPanel title="Today's Research Focus" subtitle="Should you mainly look for buying or selling opportunities?" accent="#22d3ee" minHeight={310}><TradingBiasWidget /></OverviewPanel></Grid>}
                    {visible.marketRisk && <Grid size={{ xs: 12, md: 6, lg: 3 }}><OverviewPanel title="Market Risk" subtitle="How careful should you be today?" accent="#fdb022" minHeight={310}><RiskMeterWidget /></OverviewPanel></Grid>}
                </Grid>}

                {visible.participationTrend && <OverviewPanel
                    title="Market Participation Trend"
                    subtitle={`See whether more stocks are rising or falling in the ${market} market · ${timeframe} view`}
                    eyebrow="How many stocks support the move?"
                    minHeight={420}
                    action={<Chip size="small" label="INTERACTIVE DEMO" variant="outlined" />}
                >
                    <ParticipationChartWidget />
                </OverviewPanel>}

                {(visible.sectorRotation || visible.marketBreadth) && <Grid container spacing={2.5}>
                    {visible.sectorRotation && <Grid size={{ xs: 12, lg: 6 }}>
                        <OverviewPanel title="Strong and Weak Sectors" subtitle="See where money is moving and which sectors are losing strength." minHeight={330}>
                            <SectorRotationWidget />
                        </OverviewPanel>
                    </Grid>}
                    {visible.marketBreadth && <Grid size={{ xs: 12, lg: 6 }}>
                        <OverviewPanel title="Stocks Going Up and Down" subtitle="A wider look at how many stocks are supporting the market." minHeight={330}>
                            <MarketBreadthWidget />
                        </OverviewPanel>
                    </Grid>}
                </Grid>}

                {(visible.bigInvestorActivity || visible.marketVolatility || visible.marketSentiment) && <Grid container spacing={2.5}>
                    {visible.bigInvestorActivity && <Grid size={{ xs: 12, md: 6, lg: 4 }}>
                        <OverviewPanel title="Large Investor Activity" subtitle="See whether foreign and Indian institutions are buying or selling." minHeight={280}>
                            <InstitutionalFlowWidget />
                        </OverviewPanel>
                    </Grid>}
                    {visible.marketVolatility && <Grid size={{ xs: 12, md: 6, lg: 4 }}>
                        <OverviewPanel title="India VIX" subtitle="India VIX measures expected market swings. A higher value means more uncertainty." minHeight={280}>
                            <IndiaVixWidget />
                        </OverviewPanel>
                    </Grid>}
                    {visible.marketSentiment && <Grid size={{ xs: 12, md: 12, lg: 4 }}>
                        <OverviewPanel title="Market Mood" subtitle="A simple view of whether traders feel fearful or confident." minHeight={280}>
                            <SentimentWidget />
                        </OverviewPanel>
                    </Grid>}
                </Grid>}

                {(visible.aiOpportunities || visible.smartAlerts) && <Grid container spacing={2.5}>
                    {visible.aiOpportunities && <Grid size={{ xs: 12, lg: 6 }}>
                        <OverviewPanel title="Ideas to Research" subtitle="Groups of stocks that may be worth checking in the scanner." minHeight={300}>
                            <OpportunitiesWidget />
                        </OverviewPanel>
                    </Grid>}
                    {visible.smartAlerts && <Grid size={{ xs: 12, lg: 6 }}>
                        <OverviewPanel title="Important Market Changes" subtitle="Recent changes that may need your attention." minHeight={300}>
                            <SmartAlertsWidget />
                        </OverviewPanel>
                    </Grid>}
                </Grid>}

                {visible.todayVerdict && <OverviewPanel
                    title="Today's Verdict"
                    subtitle="A short summary of the market, the risk and what you may want to research."
                    eyebrow="Simple daily summary"
                    accent="#32d583"
                    minHeight={220}
                    action={<Chip size="small" color="warning" variant="outlined" label="DEMO VERDICT" />}
                >
                    <VerdictWidget />
                </OverviewPanel>}
            </Stack>
            <MarketOverviewCustomizeDrawer
                key={customizeSession}
                open={customizeOpen}
                value={savedPreferences}
                onClose={() => setCustomizeOpen(false)}
                onPreview={(next) => {
                    setPreviewPreferences(next);
                }}
                onSave={saveCustomization}
            />
        </Box>
    );
}
