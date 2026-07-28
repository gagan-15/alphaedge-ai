import AutoAwesomeRoundedIcon from "@mui/icons-material/AutoAwesomeRounded";
import Box from "@mui/material/Box";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Chip from "@mui/material/Chip";
import CircularProgress from "@mui/material/CircularProgress";
import Grid from "@mui/material/Grid";
import LinearProgress from "@mui/material/LinearProgress";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { alpha } from "@mui/material/styles";
import { useEffect, useMemo, useState } from "react";

import { getResearchZones } from "../api/scannerApi";
import DashboardOpportunityTable, {
    type DashboardOpportunity,
} from "../components/dashboard/DashboardOpportunityTable";
import { buildTradeConfidence } from "../components/scanner/tradeConfidence";
import { useMarketIntelligence } from "../market-intelligence/MarketIntelligenceState";
import type { ZoneResearchResult } from "../types/scanner";

function marketValue(label: string, value: string, change?: number) {
    return (
        <Box sx={{ minWidth: 0, flex: "1 1 140px" }}>
            <Typography color="text.secondary" sx={{ fontSize: "0.61rem", textTransform: "uppercase", letterSpacing: "0.06em" }}>{label}</Typography>
            <Stack direction="row" spacing={0.7} sx={{ mt: 0.3, alignItems: "baseline" }}>
                <Typography sx={{ fontSize: "1rem", fontWeight: 900 }}>{value}</Typography>
                {change !== undefined && (
                    <Typography sx={{ color: change >= 0 ? "success.main" : "error.main", fontSize: "0.65rem", fontWeight: 850 }}>
                        {change >= 0 ? "+" : ""}{change.toFixed(2)}%
                    </Typography>
                )}
            </Stack>
        </Box>
    );
}

function toOpportunity(zone: ZoneResearchResult): DashboardOpportunity {
    return {
        zone,
        tradeConfidence: buildTradeConfidence(zone, null, null).score,
    };
}

export default function Dashboard() {
    const { dashboard, snapshot, lastUpdated, isLoading, error } = useMarketIntelligence();
    const [zones, setZones] = useState<ZoneResearchResult[]>([]);
    const [zonesLoading, setZonesLoading] = useState(true);
    const [zonesError, setZonesError] = useState("");

    useEffect(() => {
        let active = true;
        void getResearchZones("DAILY")
            .then((response) => {
                if (active) setZones(response.results);
            })
            .catch(() => {
                if (active) setZonesError("Zone opportunities could not be loaded. Open the Scanner to try again.");
            })
            .finally(() => {
                if (active) setZonesLoading(false);
            });
        return () => { active = false; };
    }, []);

    const demandOpportunities = useMemo(
        () => zones.filter((zone) => zone.zone_type === "DEMAND").map(toOpportunity),
        [zones],
    );
    const supplyOpportunities = useMemo(
        () => zones.filter((zone) => zone.zone_type === "SUPPLY").map(toOpportunity),
        [zones],
    );

    if (isLoading && !dashboard) {
        return (
            <Box sx={{ minHeight: "60vh", display: "grid", placeItems: "center" }}>
                <Stack spacing={2} sx={{ alignItems: "center" }}>
                    <CircularProgress />
                    <Typography color="text.secondary">Loading market intelligence...</Typography>
                </Stack>
            </Box>
        );
    }

    if (!dashboard) {
        return (
            <Card>
                <CardContent>
                    <Typography variant="h6">Dashboard is unavailable</Typography>
                    <Typography color="text.secondary">{error || "Market data could not be loaded."}</Typography>
                </CardContent>
            </Card>
        );
    }

    const bullish = snapshot.marketDirection === "Bullish";
    const bearish = snapshot.marketDirection === "Bearish";
    const verdictColor = bullish ? "#31c77a" : bearish ? "#ff5c67" : "#f5b942";

    return (
        <Stack spacing={2}>
            <Card sx={{ overflow: "hidden" }}>
                <CardContent sx={{ p: { xs: 2, lg: 2.25 }, "&:last-child": { pb: { xs: 2, lg: 2.25 } } }}>
                    <Grid container spacing={{ xs: 2, lg: 2.5 }} sx={{ alignItems: "center" }}>
                        <Grid size={{ xs: 12, lg: 5 }}>
                            <Stack direction="row" spacing={1.25} sx={{ alignItems: "center" }}>
                                <Box sx={{ width: 40, height: 40, display: "grid", placeItems: "center", borderRadius: 2.5, color: verdictColor, bgcolor: alpha(verdictColor, 0.12) }}>
                                    <AutoAwesomeRoundedIcon />
                                </Box>
                                <Box>
                                    <Typography variant="overline" sx={{ color: verdictColor, fontWeight: 900 }}>AI Market Verdict</Typography>
                                    <Typography variant="h4">{snapshot.marketDirection} Market · {snapshot.riskLevel}</Typography>
                                </Box>
                            </Stack>
                            <Typography color="text.secondary" sx={{ mt: 1.15, maxWidth: 600 }}>
                                {snapshot.marketHealth}. {snapshot.todayStrategy}
                            </Typography>
                            <Stack direction={{ xs: "column", sm: "row" }} spacing={1.5} sx={{ mt: 1.4, alignItems: { sm: "center" } }}>
                                <Box sx={{ minWidth: 210 }}>
                                    <Stack direction="row" sx={{ justifyContent: "space-between" }}>
                                        <Typography color="text.secondary" sx={{ fontSize: "0.65rem" }}>Confidence Score</Typography>
                                        <Typography sx={{ fontWeight: 900 }}>{snapshot.aiConfidence}%</Typography>
                                    </Stack>
                                    <LinearProgress
                                        variant="determinate"
                                        value={snapshot.aiConfidence}
                                        sx={{ mt: 0.65, height: 7, "& .MuiLinearProgress-bar": { bgcolor: verdictColor } }}
                                    />
                                </Box>
                                <Chip label={`Today's Strategy: ${snapshot.todayStrategy}`} variant="outlined" sx={{ color: verdictColor, borderColor: alpha(verdictColor, 0.45), fontWeight: 800 }} />
                            </Stack>
                        </Grid>

                        <Grid size={{ xs: 12, lg: 7 }}>
                            <Stack
                                direction="row"
                                useFlexGap
                                spacing={2}
                                sx={{
                                    p: 1.6,
                                    flexWrap: "wrap",
                                    borderRadius: 2.5,
                                    border: "1px solid",
                                    borderColor: "divider",
                                    bgcolor: "action.hover",
                                }}
                            >
                                {marketValue("Nifty", dashboard.market.nifty50.toLocaleString("en-IN"), dashboard.market.nifty_change)}
                                {marketValue("Bank Nifty", dashboard.market.bank_nifty.toLocaleString("en-IN"), dashboard.market.bank_nifty_change)}
                                {marketValue("India VIX", dashboard.market.india_vix.toFixed(2), dashboard.market.india_vix_change)}
                                {marketValue("Market Breadth", `${snapshot.marketBreadth}%`)}
                            </Stack>
                            <Typography color="text.secondary" sx={{ mt: 0.8, textAlign: { lg: "right" }, fontSize: "0.61rem" }}>
                                Market updated {lastUpdated?.toLocaleTimeString("en-IN") ?? "recently"} · research data may be delayed
                            </Typography>
                        </Grid>
                    </Grid>
                </CardContent>
            </Card>

            {zonesError && (
                <Typography color="warning.main" sx={{ px: 0.5, fontSize: "0.68rem" }}>{zonesError}</Typography>
            )}

            <Grid container spacing={2} sx={{ alignItems: "stretch" }}>
                <Grid size={{ xs: 12, lg: 6 }}>
                    <DashboardOpportunityTable
                        type="demand"
                        opportunities={demandOpportunities}
                        limit={5}
                        loading={zonesLoading}
                    />
                </Grid>
                <Grid size={{ xs: 12, lg: 6 }}>
                    <DashboardOpportunityTable
                        type="supply"
                        opportunities={supplyOpportunities}
                        limit={5}
                        loading={zonesLoading}
                    />
                </Grid>
            </Grid>
        </Stack>
    );
}
