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
import { useNavigate } from "react-router-dom";

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
import MarketOverviewDetailDrawer, { type MarketDetailContent } from "../components/market-overview/MarketOverviewDetailDrawer";
import OverviewPanel from "../components/market-overview/OverviewPanel";
import {
    loadMarketOverviewPreferences,
    saveMarketOverviewPreferences,
} from "../components/market-overview/marketOverviewPreferences";
import { useAuth } from "../auth/AuthState";

export default function MarketOverview() {
    const navigate = useNavigate();
    const { user } = useAuth();
    const userKey = user?.id ?? "local-demo";
    const [savedPreferences, setSavedPreferences] = useState(() => loadMarketOverviewPreferences(userKey));
    const [previewPreferences, setPreviewPreferences] = useState(savedPreferences);
    const [customizeOpen, setCustomizeOpen] = useState(false);
    const [customizeSession, setCustomizeSession] = useState(0);
    const [detail, setDetail] = useState<MarketDetailContent | null>(null);
    const [market, setMarket] = useState("NSE");
    const [timeframe, setTimeframe] = useState(savedPreferences.defaultTimeframe);
    const [lastUpdated, setLastUpdated] = useState("Not refreshed");
    const visible = previewPreferences.visibleWidgets;
    const professional = previewPreferences.language === "professional";
    const scanner = (filter: string, value: string) => navigate(`/scanner?${new URLSearchParams({ [filter]: value }).toString()}`);
    const comingSoon = (title: string) => setDetail({
        title: "Coming Soon",
        description: "This detailed analysis page will be available in a future AlphaEdge AI update.",
        comingSoon: true,
        sections: [{ title, points: ["The current dashboard summary remains available.", "Detailed history and deeper filters will be added here."] }],
    });
    const openReport = (title: string) => setDetail({
        title,
        description: "A larger explanation of what the market is doing, what looks strong and what needs caution.",
        sections: [
            { title: "Market strengths", points: ["Most tracked stocks are rising.", "Technology and Banking remain the strongest sectors.", "Expected price movement remains controlled."] },
            { title: "Market weaknesses", points: ["Metal and Auto are becoming weaker.", "Foreign investors remain careful."] },
            { title: "Key opportunities", points: ["Strong stocks after a small price fall.", "Technology and Banking stocks with healthy price strength."] },
            { title: "Risks", points: ["Unexpected news can still create large opening moves.", "Avoid buying stocks after a sharp rise."] },
            { title: "Suggested approach", points: ["Look for careful buying opportunities.", "Wait for clear risk levels before acting."] },
        ],
        action: { label: "Find Matching Stocks", onClick: () => scanner("setup", "recommended") },
    });

    function saveCustomization(next: typeof savedPreferences) {
        saveMarketOverviewPreferences(userKey, next);
        setSavedPreferences(next);
        setPreviewPreferences(next);
        setCustomizeOpen(false);
    }

    return (
        <Box sx={{ width: "100%", maxWidth: 1600, mx: "auto", px: { xs: 0, lg: 1 } }}>
            <Stack spacing={2.5} sx={previewPreferences.density === "compact" ? { "& .MuiCardContent-root": { p: "16px !important" } } : undefined}>
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
                            {professional ? "Market trend, breadth, risk and sector context for active research." : "A simple view of what the market is doing and what you may want to check next."}
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
                            {["1D", "1W", "1M", "3M", "6M", "1Y"].map((value) => (
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
                    subtitle={professional ? "A concise interpretation of market trend, breadth, leadership and risk." : "A clear explanation of today's market, the main risks and what to research next."}
                    eyebrow={professional ? "Market intelligence" : "Today's market explained"}
                    accent="#8b5cf6"
                    minHeight={190}
                    action={<Chip size="small" label="TRANSPARENT DEMO LOGIC" variant="outlined" />}
                    onExplore={() => openReport("Full AI Market Report")}
                >
                    <AIMarketSummaryWidget timeframe={timeframe} universe={previewPreferences.marketUniverse} language={previewPreferences.language} showTooltips={previewPreferences.chart.showTooltips} />
                </OverviewPanel>}

                {(visible.marketHealth || visible.marketTrend || visible.researchFocus || visible.marketRisk) && <Grid container spacing={2.5}>
                    {visible.marketHealth && <Grid size={{ xs: 12, md: 6, lg: 3 }}><OverviewPanel title="Market Health" subtitle={professional ? "Composite trend, breadth, momentum, volatility and risk reading." : "Are most stocks supporting today's market move?"} accent="#32d583" minHeight={310} onExplore={() => setDetail({ title: "Market Health Details", description: "See how the market health score has changed over different time periods.", sections: [{ title: "Health history", points: ["Daily trend: Improving", "Weekly trend: Healthy", "Monthly trend: Strong"] }, { title: "Score breakdown", points: ["Market direction: Strong", "Stocks joining the move: Healthy", "Expected price movement: Controlled", "Overall risk: Medium"] }] })}><MarketHealthWidget timeframe={timeframe} universe={previewPreferences.marketUniverse} showTooltips={previewPreferences.chart.showTooltips} /></OverviewPanel></Grid>}
                    {visible.marketTrend && <Grid size={{ xs: 12, md: 6, lg: 3 }}><OverviewPanel title={professional ? "Market Regime" : "Market Direction"} subtitle={professional ? "Identifies whether conditions are trending, ranging or changing." : "Is the market rising, falling or moving sideways?"} accent="#6172f3" minHeight={310} onExplore={() => setDetail({ title: "Market Trend Timeline", description: "See how the wider market has changed between rising, falling, recovery and sideways periods.", sections: [{ title: "Recent changes", points: ["March: Recovery", "April: Sideways market", "May: Strong rise", "June to today: Healthy rise"] }, { title: "Possible market states", points: ["Bull: the market is rising", "Bear: the market is falling", "Recovery: prices are improving after a fall", "Sideways: prices have no clear direction", "Distribution: large investors may be selling into strength"] }] })}><MarketRegimeWidget timeframe={timeframe} language={previewPreferences.language} /></OverviewPanel></Grid>}
                    {visible.researchFocus && <Grid size={{ xs: 12, md: 6, lg: 3 }}><OverviewPanel title="Today's Research Focus" subtitle="Should you mainly look for buying or selling opportunities?" accent="#22d3ee" minHeight={310} onExplore={() => scanner("setup", "today-recommended")}><TradingBiasWidget /></OverviewPanel></Grid>}
                    {visible.marketRisk && <Grid size={{ xs: 12, md: 6, lg: 3 }}><OverviewPanel title="Market Risk" subtitle="How careful should you be today?" accent="#fdb022" minHeight={310} onExplore={() => setDetail({ title: "Market Risk Analysis", description: "A simple view of the main risks that may affect today's market.", sections: [{ title: "Risk checks", points: ["Large opening move risk: Low", "Ease of buying and selling: Healthy", "Expected price movement: Medium", "Market stability: High", "News impact: Moderate"] }], action: { label: "Open Risk Tools", onClick: () => navigate("/risk-management") } })}><RiskMeterWidget /></OverviewPanel></Grid>}
                </Grid>}

                {visible.participationTrend && <OverviewPanel
                    title="Market Participation Trend"
                    subtitle={`See whether more stocks are rising or falling in the ${market} market · ${timeframe} view`}
                    eyebrow="How many stocks support the move?"
                    minHeight={420}
                    action={<Chip size="small" label="INTERACTIVE DEMO" variant="outlined" />}
                    onExplore={() => setDetail({
                        title: "Full Screen Market Participation",
                        description: "Compare the wider market with Nifty and Bank Nifty. Use the chart controls to change the time period, compare lines and export data.",
                        content: <ParticipationChartWidget defaultRange={timeframe} universe={previewPreferences.marketUniverse} initialNifty={previewPreferences.chart.showNifty} initialBankNifty={previewPreferences.chart.showBankNifty} showEvents={previewPreferences.chart.showEvents} showInsights={previewPreferences.chart.showAiExplanations} showTooltips={previewPreferences.chart.showTooltips} />,
                        action: { label: "View Detailed Market Data", onClick: () => navigate("/market-breadth") },
                    })}
                >
                    <ParticipationChartWidget
                        key={`${timeframe}-${previewPreferences.marketUniverse}-${previewPreferences.chart.showNifty}-${previewPreferences.chart.showBankNifty}`}
                        defaultRange={timeframe}
                        universe={previewPreferences.marketUniverse}
                        initialNifty={previewPreferences.chart.showNifty}
                        initialBankNifty={previewPreferences.chart.showBankNifty}
                        showEvents={previewPreferences.chart.showEvents}
                        showInsights={previewPreferences.chart.showAiExplanations}
                        showTooltips={previewPreferences.chart.showTooltips}
                    />
                </OverviewPanel>}

                {(visible.sectorRotation || visible.marketBreadth) && <Grid container spacing={2.5}>
                    {visible.sectorRotation && <Grid size={{ xs: 12, lg: 6 }}>
                        <OverviewPanel title="Strong and Weak Sectors" subtitle="See where money is moving and which sectors are losing strength." minHeight={330}>
                            <SectorRotationWidget onSectorExplore={(sector) => setDetail({ title: "Coming Soon", description: "This detailed analysis page will be available in a future AlphaEdge AI update.", comingSoon: true, sections: [{ title: `${sector} sector scanner`, points: [`The scanner will show only ${sector} stocks.`, "Sector information is not connected to the current zone feed yet."] }], action: { label: "Open General Scanner", onClick: () => navigate("/scanner") } })} />
                        </OverviewPanel>
                    </Grid>}
                    {visible.marketBreadth && <Grid size={{ xs: 12, lg: 6 }}>
                        <OverviewPanel title="Stocks Going Up and Down" subtitle="A wider look at how many stocks are supporting the market." minHeight={330}>
                            <MarketBreadthWidget shortNumbers={previewPreferences.numberFormat === "short"} showTooltips={previewPreferences.chart.showTooltips} onMetricExplore={(metric) => setDetail({ title: "Coming Soon", description: "This detailed analysis page will be available in a future AlphaEdge AI update.", comingSoon: true, sections: [{ title: metric, points: [`A future stock list will show every company matching “${metric}”.`, "The required full-market stock feed is not connected yet."] }], action: { label: "Open General Scanner", onClick: () => navigate("/scanner") } })} />
                        </OverviewPanel>
                    </Grid>}
                </Grid>}

                {(visible.bigInvestorActivity || visible.marketVolatility || visible.marketSentiment) && <Grid container spacing={2.5}>
                    {visible.bigInvestorActivity && <Grid size={{ xs: 12, md: 6, lg: 4 }}>
                        <OverviewPanel title="Large Investor Activity" subtitle="See whether foreign and Indian institutions are buying or selling." minHeight={280} onExplore={() => setDetail({ title: "FII / DII Analysis", description: "Foreign and Indian institution buying and selling over different periods.", sections: [{ title: "Daily", points: ["Foreign institutions: Net selling", "Indian institutions: Net buying"] }, { title: "Weekly", points: ["Foreign activity remains careful", "Indian buying remains supportive"] }, { title: "Monthly history", points: ["Domestic buying has offset most foreign selling"] }] })}>
                            <InstitutionalFlowWidget />
                        </OverviewPanel>
                    </Grid>}
                    {visible.marketVolatility && <Grid size={{ xs: 12, md: 6, lg: 4 }}>
                        <OverviewPanel title="India VIX" subtitle="India VIX measures expected market swings. A higher value means more uncertainty." minHeight={280} onExplore={() => comingSoon("Detailed India VIX analysis")}>
                            <IndiaVixWidget />
                        </OverviewPanel>
                    </Grid>}
                    {visible.marketSentiment && <Grid size={{ xs: 12, md: 12, lg: 4 }}>
                        <OverviewPanel title="Market Mood" subtitle="A simple view of whether traders feel fearful or confident." minHeight={280} onExplore={() => setDetail({ title: "Market Mood Analysis", description: "Understand whether traders are fearful, neutral, confident or overly excited.", sections: [{ title: "Mood levels", points: ["Fear: traders expect prices to fall", "Neutral: buyers and sellers are balanced", "Optimistic: more traders expect prices to rise", "Euphoric: confidence may be too high, so be careful"] }] })}>
                            <SentimentWidget />
                        </OverviewPanel>
                    </Grid>}
                </Grid>}

                {(visible.aiOpportunities || visible.smartAlerts) && <Grid container spacing={2.5}>
                    {visible.aiOpportunities && <Grid size={{ xs: 12, lg: 6 }}>
                        <OverviewPanel title="Ideas to Research" subtitle="Groups of stocks that may be worth checking in the scanner." minHeight={300}>
                            <OpportunitiesWidget onScan={(scanName) => scanner("setup", scanName)} />
                        </OverviewPanel>
                    </Grid>}
                    {visible.smartAlerts && <Grid size={{ xs: 12, lg: 6 }}>
                        <OverviewPanel title="Important Market Changes" subtitle="Recent changes that may need your attention." minHeight={300}>
                            <SmartAlertsWidget onAlert={(alert) => setDetail({ title: "Alert Details", description: alert, sections: [{ title: "Why this alert appeared", points: ["A tracked market condition changed enough to need attention.", "Time: A few minutes ago", "Affected sectors: Based on the selected alert", "Suggested action: Review the related stocks before making a decision"] }], action: { label: "Open Alerts", onClick: () => navigate("/alerts") } })} />
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
                    onExplore={() => openReport("Complete AI Market Report")}
                >
                    <VerdictWidget timeframe={timeframe} universe={previewPreferences.marketUniverse} language={previewPreferences.language} />
                </OverviewPanel>}
            </Stack>
            <MarketOverviewCustomizeDrawer
                key={customizeSession}
                open={customizeOpen}
                value={savedPreferences}
                onClose={() => setCustomizeOpen(false)}
                onPreview={(next) => {
                    setPreviewPreferences(next);
                    setTimeframe(next.defaultTimeframe);
                }}
                onSave={saveCustomization}
            />
            <MarketOverviewDetailDrawer detail={detail} onClose={() => setDetail(null)} />
        </Box>
    );
}
