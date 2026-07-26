import ArrowForwardRoundedIcon from "@mui/icons-material/ArrowForwardRounded";
import BookmarkRoundedIcon from "@mui/icons-material/BookmarkRounded";
import NotificationsActiveRoundedIcon from "@mui/icons-material/NotificationsActiveRounded";
import PlayArrowRoundedIcon from "@mui/icons-material/PlayArrowRounded";
import SearchRoundedIcon from "@mui/icons-material/SearchRounded";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Chip from "@mui/material/Chip";
import CircularProgress from "@mui/material/CircularProgress";
import Divider from "@mui/material/Divider";
import Grid from "@mui/material/Grid";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { Link as RouterLink } from "react-router-dom";

import AlertCard from "../components/dashboard/AlertCard";
import { useMarketIntelligence } from "../market-intelligence/MarketIntelligenceState";
import { getResearchLabel } from "../utils/researchLanguage";

function readStringList(key: string): string[] {
    try {
        const value = JSON.parse(localStorage.getItem(key) ?? "[]");
        return Array.isArray(value) ? value.map(String) : [];
    } catch {
        return [];
    }
}

function readRecentResearch() {
    try {
        const value = JSON.parse(localStorage.getItem("alphaedge.local.watchlist.zones") ?? "[]");
        return Array.isArray(value) ? value.slice(-3).reverse() as Array<Record<string, string>> : [];
    } catch {
        return [];
    }
}

export default function Dashboard() {
    const { dashboard, snapshot, lastUpdated, isLoading, error } = useMarketIntelligence();
    const watchlist = readStringList("alphaedge.local.watchlist").slice(0, 5);
    const recentResearch = readRecentResearch();

    if (isLoading && !dashboard) {
        return <Box sx={{ minHeight: "60vh", display: "grid", placeItems: "center" }}><Stack spacing={2} sx={{ alignItems: "center" }}><CircularProgress /><Typography color="text.secondary">Loading your workspace...</Typography></Stack></Box>;
    }
    if (!dashboard) {
        return <Card><CardContent><Typography variant="h6">Your workspace is unavailable</Typography><Typography color="text.secondary">{error || "Market data could not be loaded."}</Typography></CardContent></Card>;
    }

    return (
        <Stack spacing={2}>
            <Stack direction={{ xs: "column", md: "row" }} sx={{ justifyContent: "space-between", alignItems: { md: "center" } }}>
                <Box>
                    <Typography variant="h4">My Trading Workspace</Typography>
                    <Typography color="text.secondary">Your signals, saved stocks, alerts and next research steps.</Typography>
                </Box>
                <Typography variant="caption" color="text.secondary">Market updated {lastUpdated?.toLocaleTimeString("en-IN") ?? "recently"}</Typography>
            </Stack>

            <Card><CardContent>
                <Stack direction={{ xs: "column", md: "row" }} spacing={2} sx={{ alignItems: { md: "center" } }}>
                    <Box sx={{ flex: 1 }}>
                        <Typography variant="overline" color="text.secondary">Quick Market Snapshot</Typography>
                        <Typography variant="h5">{snapshot.marketDirection} · {snapshot.riskLevel}</Typography>
                        <Typography color="text.secondary" sx={{ mt: .5 }}>{snapshot.todayStrategy}</Typography>
                    </Box>
                    <Stack direction="row" spacing={1} sx={{ flexWrap: "wrap" }}>
                        <Chip label={`Nifty ${dashboard.market.nifty_change >= 0 ? "+" : ""}${dashboard.market.nifty_change}%`} color={dashboard.market.nifty_change >= 0 ? "success" : "error"} variant="outlined" />
                        <Chip label={`India VIX ${dashboard.market.india_vix}`} variant="outlined" />
                        <Button component={RouterLink} to="/market-overview" endIcon={<ArrowForwardRoundedIcon />}>Why is the market doing this?</Button>
                    </Stack>
                </Stack>
            </CardContent></Card>

            <Grid container spacing={2}>
                <Grid size={{ xs: 12, lg: 8 }}>
                    <Card sx={{ height: "100%" }}><CardContent>
                        <Stack direction="row" sx={{ justifyContent: "space-between", alignItems: "center" }}>
                            <Box><Typography variant="h5">Today's AI Signals</Typography><Typography color="text.secondary">Start with the setups that match the most rules.</Typography></Box>
                            <Button component={RouterLink} to="/signals">View all</Button>
                        </Stack>
                        <Grid container spacing={1.5} sx={{ mt: .5 }}>
                            {dashboard.signals.slice(0, 6).map((signal) => <Grid key={signal.symbol} size={{ xs: 12, sm: 6, lg: 4 }}>
                                <Box sx={{ p: 1.5, border: "1px solid", borderColor: "divider", borderRadius: 2 }}>
                                    <Stack direction="row" sx={{ justifyContent: "space-between" }}><Typography sx={{ fontWeight: 900 }}>{signal.symbol}</Typography><Chip size="small" label={getResearchLabel(signal.action)} color={signal.action === "BUY" ? "success" : signal.action === "SELL" ? "error" : "warning"} /></Stack>
                                    <Typography variant="h6" sx={{ mt: 1 }}>₹{signal.price.toLocaleString("en-IN")}</Typography>
                                    <Typography variant="caption" color="text.secondary">{signal.confidence}% of current rules matched</Typography>
                                </Box>
                            </Grid>)}
                        </Grid>
                    </CardContent></Card>
                </Grid>
                <Grid size={{ xs: 12, lg: 4 }}><AlertCard alerts={dashboard.alerts.slice(0, 4)} /></Grid>

                <Grid size={{ xs: 12, md: 6, lg: 4 }}>
                    <Card sx={{ height: "100%" }}><CardContent>
                        <Stack direction="row" spacing={1} sx={{ alignItems: "center" }}><BookmarkRoundedIcon color="primary" /><Typography variant="h6">My Watchlist</Typography></Stack>
                        <Stack spacing={1} divider={<Divider flexItem />} sx={{ mt: 1.5 }}>
                            {(watchlist.length ? watchlist : ["No stocks saved yet"]).map((symbol) => <Typography key={symbol} color={watchlist.length ? "text.primary" : "text.secondary"}>{symbol}</Typography>)}
                        </Stack>
                        <Button component={RouterLink} to="/watchlist" sx={{ mt: 1.5 }}>Open watchlist</Button>
                    </CardContent></Card>
                </Grid>

                <Grid size={{ xs: 12, md: 6, lg: 4 }}>
                    <Card sx={{ height: "100%" }}><CardContent>
                        <Stack direction="row" spacing={1} sx={{ alignItems: "center" }}><PlayArrowRoundedIcon color="primary" /><Typography variant="h6">Continue Last Research</Typography></Stack>
                        <Stack spacing={1} sx={{ mt: 1.5 }}>
                            {(recentResearch.length ? recentResearch : [{ symbol: "No recent stock research" }]).map((item, index) => <Box key={`${item.symbol}-${index}`}>
                                <Typography sx={{ fontWeight: 800 }}>{item.symbol}</Typography>
                                {item.zoneType && <Typography variant="caption" color="text.secondary">{item.timeframe} · {item.zoneType} zone</Typography>}
                            </Box>)}
                        </Stack>
                        <Button component={RouterLink} to="/scanner" sx={{ mt: 1.5 }}>Continue research</Button>
                    </CardContent></Card>
                </Grid>

                <Grid size={{ xs: 12, md: 6, lg: 4 }}>
                    <Card sx={{ height: "100%" }}><CardContent>
                        <Typography variant="h6">My Holdings Summary</Typography>
                        <Typography color="text.secondary" sx={{ mt: 1.5 }}>Invested capital</Typography>
                        <Typography variant="h5">₹{dashboard.portfolio.invested_capital.toLocaleString("en-IN")}</Typography>
                        <Typography color="text.secondary" sx={{ mt: .75 }}>{dashboard.portfolio.total_positions} saved positions</Typography>
                        <Button component={RouterLink} to="/holdings" sx={{ mt: 1.5 }}>View holdings</Button>
                    </CardContent></Card>
                </Grid>

                <Grid size={{ xs: 12, md: 6, lg: 4 }}>
                    <Card sx={{ height: "100%" }}><CardContent>
                        <Stack direction="row" spacing={1} sx={{ alignItems: "center" }}><SearchRoundedIcon color="primary" /><Typography variant="h6">Scanner Shortcut</Typography></Stack>
                        <Typography color="text.secondary" sx={{ mt: 1 }}>Find stocks near fresh demand or supply zones.</Typography>
                        <Button component={RouterLink} to="/scanner" variant="contained" sx={{ mt: 2 }}>Run scanner</Button>
                    </CardContent></Card>
                </Grid>

                <Grid size={{ xs: 12, md: 6, lg: 4 }}>
                    <Card sx={{ height: "100%" }}><CardContent>
                        <Stack direction="row" spacing={1} sx={{ alignItems: "center" }}><NotificationsActiveRoundedIcon color="primary" /><Typography variant="h6">AI Notifications</Typography></Stack>
                        <Typography color="text.secondary" sx={{ mt: 1 }}>{dashboard.alerts.filter((alert) => alert.requires_action).length} items may need your attention.</Typography>
                        <Button component={RouterLink} to="/alerts" sx={{ mt: 1.5 }}>Review alerts</Button>
                    </CardContent></Card>
                </Grid>
            </Grid>
        </Stack>
    );
}
