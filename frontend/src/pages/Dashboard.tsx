import AutoAwesomeRoundedIcon from "@mui/icons-material/AutoAwesomeRounded";
import Box from "@mui/material/Box";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import CircularProgress from "@mui/material/CircularProgress";
import Grid from "@mui/material/Grid";
import FormControl from "@mui/material/FormControl";
import InputLabel from "@mui/material/InputLabel";
import MenuItem from "@mui/material/MenuItem";
import Select, { type SelectChangeEvent } from "@mui/material/Select";
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
import type { ZoneResearchResponse, ZoneResearchResult } from "../types/scanner";
import {
    marketUniverseOptions,
    type MarketUniverse,
    useMarketUniverse,
} from "../market-universe/MarketUniverseState";

function marketValue(label: string, value: string, change?: number) {
    return (
        <Box sx={{ minWidth: 0, flex: "1 1 118px" }}>
            <Typography color="text.secondary" sx={{ fontSize: "0.58rem", textTransform: "uppercase", letterSpacing: "0.06em" }}>{label}</Typography>
            <Stack direction="row" spacing={0.6} sx={{ mt: 0.25, alignItems: "baseline" }}>
                <Typography sx={{ fontSize: "0.94rem", fontWeight: 700 }}>{value}</Typography>
                {change !== undefined && (
                    <Typography sx={{ color: change >= 0 ? "success.main" : "error.main", fontSize: "0.61rem", fontWeight: 600 }}>
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
    const { marketUniverse, setMarketUniverse, customSymbols } = useMarketUniverse();
    const [zones, setZones] = useState<ZoneResearchResult[]>([]);
    const [zonesLoading, setZonesLoading] = useState(true);
    const [zonesError, setZonesError] = useState("");
    const [scanStatus, setScanStatus] = useState<ZoneResearchResponse | null>(null);

    useEffect(() => {
        let active = true;
        let pollTimer: ReturnType<typeof setTimeout> | undefined;
        queueMicrotask(() => {
            if (active) {
                setZonesLoading(true);
                setZonesError("");
            }
        });
        const watchlist = marketUniverse === "watchlist"
            ? JSON.parse(localStorage.getItem("alphaedge.local.watchlist") ?? "[]")
            : [];
        const suppliedSymbols = marketUniverse === "custom"
            ? customSymbols
            : watchlist;
        const loadZones = () => void getResearchZones("DAILY", marketUniverse, suppliedSymbols)
            .then((response) => {
                if (!active) return;
                setScanStatus(response);
                if (response.results.length) setZones(response.results);
                setZonesLoading(response.status !== "completed");
                if (response.status === "refreshing" || response.status === "queued") {
                    pollTimer = setTimeout(loadZones, 5000);
                }
            })
            .catch(() => {
                if (active) setZonesError("Zone opportunities could not be loaded. Open the Scanner to try again.");
            })
            .finally(() => {
                if (active && !pollTimer) setZonesLoading(false);
            });
        loadZones();
        return () => {
            active = false;
            if (pollTimer) clearTimeout(pollTimer);
        };
    }, [customSymbols, marketUniverse]);

    const demandOpportunities = useMemo(
        () => zones.filter((zone) => zone.zone_type === "DEMAND").map(toOpportunity),
        [zones],
    );
    const supplyOpportunities = useMemo(
        () => zones.filter((zone) => zone.zone_type === "SUPPLY").map(toOpportunity),
        [zones],
    );

    const bullish = snapshot.marketDirection === "Bullish";
    const bearish = snapshot.marketDirection === "Bearish";
    const verdictColor = bullish ? "#31c77a" : bearish ? "#ff5c67" : "#f5b942";
    const market = dashboard?.market;
    const marketMessage = isLoading
        ? "Loading market data..."
        : error || "Market data could not be loaded.";

    return (
        <Stack spacing={2}>
            <Box sx={{ display: "flex", justifyContent: "flex-end", alignItems: "center", gap: 1.5 }}>
                {scanStatus && (
                    <Typography color="text.secondary" sx={{ fontSize: "0.7rem" }}>
                        {scanStatus.processed_symbols}/{scanStatus.total_symbols} symbols
                        {" · "}{scanStatus.status === "completed" ? "Updated" : "Refreshing"}
                    </Typography>
                )}
                <FormControl size="small" sx={{ minWidth: 176 }}>
                    <InputLabel id="dashboard-market-universe-label">
                        Market Universe
                    </InputLabel>
                    <Select
                        labelId="dashboard-market-universe-label"
                        value={marketUniverse}
                        label="Market Universe"
                        onChange={(event: SelectChangeEvent) => {
                            setMarketUniverse(event.target.value as MarketUniverse);
                        }}
                    >
                        {marketUniverseOptions.map((option) => (
                            <MenuItem key={option.value} value={option.value}>
                                {option.label}
                            </MenuItem>
                        ))}
                    </Select>
                </FormControl>
            </Box>
            <Card sx={{ overflow: "hidden" }}>
                <CardContent sx={{ p: { xs: 2, lg: 2.1 }, "&:last-child": { pb: { xs: 2, lg: 2.1 } } }}>
                    <Grid container spacing={{ xs: 2, lg: 2.2 }} sx={{ alignItems: "stretch" }}>
                        <Grid size={{ xs: 12, md: 6, lg: 4 }}>
                            <Stack direction="row" spacing={1.25} sx={{ alignItems: "center" }}>
                                <Box sx={{ width: 40, height: 40, display: "grid", placeItems: "center", borderRadius: 2.5, color: verdictColor, bgcolor: alpha(verdictColor, 0.12) }}>
                                    <AutoAwesomeRoundedIcon />
                                </Box>
                                <Box>
                                    <Typography variant="overline" sx={{ color: verdictColor, fontWeight: 900, letterSpacing: "0.09em" }}>Market Verdict</Typography>
                                    <Typography variant="h4" sx={{ fontWeight: 600 }}>
                                        {dashboard ? `${snapshot.marketDirection} Market · ${snapshot.riskLevel}` : "Market verdict pending"}
                                    </Typography>
                                </Box>
                            </Stack>
                            <Typography color="text.secondary" sx={{ mt: 1.05, maxWidth: 560 }}>
                                {dashboard
                                    ? `${snapshot.marketHealth}. ${snapshot.todayStrategy}`
                                    : "Market data is unavailable right now. Zone research can still be reviewed below."}
                            </Typography>
                        </Grid>

                        <Grid size={{ xs: 12, md: 6, lg: 3 }}>
                            <Stack
                                direction="row"
                                spacing={1.4}
                                sx={{ height: "100%", alignItems: "center", p: 1.25, borderRadius: 2.5, border: "1px solid", borderColor: "divider" }}
                            >
                                <Box sx={{ position: "relative", width: 66, height: 66, flex: "0 0 auto" }}>
                                    <CircularProgress variant="determinate" value={100} size={66} thickness={4.2} sx={{ color: "action.hover", position: "absolute", inset: 0 }} />
                                    <CircularProgress variant="determinate" value={dashboard ? snapshot.aiConfidence : 0} size={66} thickness={4.2} sx={{ color: verdictColor, position: "absolute", inset: 0 }} />
                                    <Box sx={{ position: "absolute", inset: 0, display: "grid", placeItems: "center" }}>
                                        <Typography sx={{ fontSize: "0.9rem", fontWeight: 800 }}>{dashboard ? snapshot.aiConfidence : "—"}</Typography>
                                    </Box>
                                </Box>
                                <Box sx={{ minWidth: 0 }}>
                                    <Typography color="text.secondary" sx={{ fontSize: "0.58rem", textTransform: "uppercase", letterSpacing: "0.07em" }}>Confidence</Typography>
                                    <Typography sx={{ mt: 0.2, fontWeight: 600 }}>{dashboard ? "Current market view" : "Waiting for data"}</Typography>
                                    <Typography color="text.secondary" sx={{ mt: 0.7, fontSize: "0.58rem", textTransform: "uppercase", letterSpacing: "0.07em" }}>Today's Strategy</Typography>
                                    <Typography sx={{ mt: 0.15, color: verdictColor, fontSize: "0.65rem", fontWeight: 600 }}>
                                        {dashboard ? snapshot.todayStrategy : "Waiting for market data"}
                                    </Typography>
                                </Box>
                            </Stack>
                        </Grid>

                        <Grid size={{ xs: 12, lg: 5 }}>
                            <Typography color="text.secondary" sx={{ mb: 0.55, fontSize: "0.58rem", textTransform: "uppercase", letterSpacing: "0.07em" }}>Market Summary</Typography>
                            <Stack
                                direction="row"
                                useFlexGap
                                spacing={1.5}
                                sx={{
                                    p: 1.35,
                                    flexWrap: "wrap",
                                    borderRadius: 2.5,
                                    border: "1px solid",
                                    borderColor: "divider",
                                    bgcolor: "action.hover",
                                }}
                            >
                                {marketValue("Nifty", market ? market.nifty50.toLocaleString("en-IN") : "—", market?.nifty_change)}
                                {marketValue("Bank Nifty", market ? market.bank_nifty.toLocaleString("en-IN") : "—", market?.bank_nifty_change)}
                                {marketValue("India VIX", market ? market.india_vix.toFixed(2) : "—", market?.india_vix_change)}
                                {marketValue("Market Breadth", dashboard ? `${snapshot.marketBreadth}%` : "—")}
                            </Stack>
                            <Typography color="text.secondary" sx={{ mt: 0.55, textAlign: { lg: "right" }, fontSize: "0.58rem" }}>
                                {lastUpdated
                                    ? `Updated ${lastUpdated.toLocaleTimeString("en-IN")} · delayed research data`
                                    : marketMessage}
                            </Typography>
                        </Grid>
                    </Grid>
                    {!dashboard && !isLoading && (
                        <Typography color="warning.main" sx={{ mt: 1.05, fontSize: "0.65rem" }}>
                            {marketMessage} The Dashboard will update when the backend reconnects.
                        </Typography>
                    )}
                </CardContent>
            </Card>

            <Grid container spacing={2} sx={{ alignItems: "stretch" }}>
                <Grid size={{ xs: 12, lg: 6 }}>
                    <DashboardOpportunityTable
                        type="demand"
                        opportunities={demandOpportunities}
                        limit={5}
                        timeframe="DAILY"
                        loading={zonesLoading}
                        error={zonesError}
                    />
                </Grid>
                <Grid size={{ xs: 12, lg: 6 }}>
                    <DashboardOpportunityTable
                        type="supply"
                        opportunities={supplyOpportunities}
                        limit={5}
                        timeframe="DAILY"
                        loading={zonesLoading}
                        error={zonesError}
                    />
                </Grid>
            </Grid>
        </Stack>
    );
}
