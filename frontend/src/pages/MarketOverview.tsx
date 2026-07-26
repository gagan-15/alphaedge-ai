import { useState } from "react";

import AutoAwesomeOutlinedIcon from "@mui/icons-material/AutoAwesomeOutlined";
import AutoGraphOutlinedIcon from "@mui/icons-material/AutoGraphOutlined";
import BoltOutlinedIcon from "@mui/icons-material/BoltOutlined";
import CachedOutlinedIcon from "@mui/icons-material/CachedOutlined";
import DashboardCustomizeOutlinedIcon from "@mui/icons-material/DashboardCustomizeOutlined";
import InsightsOutlinedIcon from "@mui/icons-material/InsightsOutlined";
import NotificationsActiveOutlinedIcon from "@mui/icons-material/NotificationsActiveOutlined";
import RadarOutlinedIcon from "@mui/icons-material/RadarOutlined";
import SecurityOutlinedIcon from "@mui/icons-material/SecurityOutlined";
import ShowChartOutlinedIcon from "@mui/icons-material/ShowChartOutlined";
import TimelineOutlinedIcon from "@mui/icons-material/TimelineOutlined";
import TrendingUpOutlinedIcon from "@mui/icons-material/TrendingUpOutlined";
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

import OverviewPanel from "../components/market-overview/OverviewPanel";

const kpis = [
    {
        title: "Market Health",
        subtitle: "Participation, momentum and trend strength",
        icon: InsightsOutlinedIcon,
        accent: "#32d583",
    },
    {
        title: "Market Regime",
        subtitle: "Trending, ranging or transition environment",
        icon: TimelineOutlinedIcon,
        accent: "#6172f3",
    },
    {
        title: "Trading Bias",
        subtitle: "Preferred directional research posture",
        icon: TrendingUpOutlinedIcon,
        accent: "#22d3ee",
    },
    {
        title: "Risk Meter",
        subtitle: "Volatility and participation risk context",
        icon: SecurityOutlinedIcon,
        accent: "#fdb022",
    },
] as const;

function WidgetPlaceholder({ icon: Icon, text }: { icon: typeof AutoGraphOutlinedIcon; text: string }) {
    return (
        <Box
            sx={{
                height: "100%",
                minHeight: 104,
                display: "grid",
                placeItems: "center",
                border: "1px dashed rgba(143, 161, 184, .22)",
                borderRadius: 2,
                bgcolor: "rgba(4, 12, 25, .28)",
                textAlign: "center",
                px: 2,
            }}
        >
            <Box>
                <Icon sx={{ color: "text.secondary", fontSize: 28 }} />
                <Typography color="text.secondary" sx={{ mt: 1, fontSize: ".74rem" }}>{text}</Typography>
            </Box>
        </Box>
    );
}

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
                    action={<Chip size="small" label="AI PLACEHOLDER" variant="outlined" />}
                >
                    <WidgetPlaceholder icon={AutoAwesomeOutlinedIcon} text="AI interpretation is intentionally not connected in this layout phase." />
                </OverviewPanel>

                <Grid container spacing={2.5}>
                    {kpis.map(({ title, subtitle, icon: Icon, accent }) => (
                        <Grid key={title} size={{ xs: 12, md: 6, lg: 3 }}>
                            <OverviewPanel title={title} subtitle={subtitle} accent={accent} minHeight={210}>
                                <WidgetPlaceholder icon={Icon} text="Metric widget ready for a validated data source." />
                            </OverviewPanel>
                        </Grid>
                    ))}
                </Grid>

                <OverviewPanel
                    title="Market Participation Trend"
                    subtitle={`${market} participation workspace · ${timeframe} view`}
                    eyebrow="Breadth through time"
                    minHeight={420}
                    action={<Chip size="small" label="CHART CONTAINER" variant="outlined" />}
                >
                    <WidgetPlaceholder icon={ShowChartOutlinedIcon} text="Interactive participation chart will be added without changing this layout." />
                </OverviewPanel>

                <Grid container spacing={2.5}>
                    <Grid size={{ xs: 12, lg: 6 }}>
                        <OverviewPanel title="Sector Rotation" subtitle="Leadership, improvement and deterioration by sector" minHeight={330}>
                            <WidgetPlaceholder icon={RadarOutlinedIcon} text="Sector rotation widget slot" />
                        </OverviewPanel>
                    </Grid>
                    <Grid size={{ xs: 12, lg: 6 }}>
                        <OverviewPanel title="Market Breadth" subtitle="Advancing, declining and unchanged participation" minHeight={330}>
                            <WidgetPlaceholder icon={AutoGraphOutlinedIcon} text="Market breadth widget slot" />
                        </OverviewPanel>
                    </Grid>
                </Grid>

                <Grid container spacing={2.5}>
                    <Grid size={{ xs: 12, md: 6, lg: 4 }}>
                        <OverviewPanel title="Institutional Flow" subtitle="FII and DII activity context" minHeight={280}>
                            <WidgetPlaceholder icon={TimelineOutlinedIcon} text="Institutional flow widget slot" />
                        </OverviewPanel>
                    </Grid>
                    <Grid size={{ xs: 12, md: 6, lg: 4 }}>
                        <OverviewPanel title="India VIX" subtitle="Volatility level, direction and risk state" minHeight={280}>
                            <WidgetPlaceholder icon={BoltOutlinedIcon} text="Volatility widget slot" />
                        </OverviewPanel>
                    </Grid>
                    <Grid size={{ xs: 12, md: 12, lg: 4 }}>
                        <OverviewPanel title="Market Sentiment" subtitle="Combined participation and risk context" minHeight={280}>
                            <WidgetPlaceholder icon={InsightsOutlinedIcon} text="Sentiment widget slot" />
                        </OverviewPanel>
                    </Grid>
                </Grid>

                <Grid container spacing={2.5}>
                    <Grid size={{ xs: 12, lg: 6 }}>
                        <OverviewPanel title="AI Opportunities" subtitle="Research candidates that deserve deeper validation" minHeight={300}>
                            <WidgetPlaceholder icon={AutoAwesomeOutlinedIcon} text="Opportunity widget slot" />
                        </OverviewPanel>
                    </Grid>
                    <Grid size={{ xs: 12, lg: 6 }}>
                        <OverviewPanel title="Smart Alerts" subtitle="Important market conditions requiring attention" minHeight={300}>
                            <WidgetPlaceholder icon={NotificationsActiveOutlinedIcon} text="Alert widget slot" />
                        </OverviewPanel>
                    </Grid>
                </Grid>

                <OverviewPanel
                    title="Today's Verdict"
                    subtitle="The final market posture, preferred strategy, risk level and next scan will be summarized here."
                    eyebrow="Decision brief"
                    accent="#32d583"
                    minHeight={220}
                    action={<Chip size="small" color="warning" variant="outlined" label="SUMMARY PLACEHOLDER" />}
                >
                    <WidgetPlaceholder icon={InsightsOutlinedIcon} text="Premium verdict container ready for validated market intelligence." />
                </OverviewPanel>
            </Stack>
        </Box>
    );
}
