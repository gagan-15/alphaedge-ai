import ArrowForwardRoundedIcon from "@mui/icons-material/ArrowForwardRounded";
import TrendingDownRoundedIcon from "@mui/icons-material/TrendingDownRounded";
import TrendingUpRoundedIcon from "@mui/icons-material/TrendingUpRounded";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Chip from "@mui/material/Chip";
import LinearProgress from "@mui/material/LinearProgress";
import Stack from "@mui/material/Stack";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import Typography from "@mui/material/Typography";
import { alpha } from "@mui/material/styles";
import { Link as RouterLink } from "react-router-dom";

import type { ZoneResearchResult } from "../../types/scanner";

export type DashboardOpportunityType = "demand" | "supply";

export interface DashboardOpportunity {
    zone: ZoneResearchResult;
    tradeConfidence: number;
}

interface DashboardOpportunityTableProps {
    type: DashboardOpportunityType;
    opportunities: DashboardOpportunity[];
    limit: number;
    loading?: boolean;
    error?: string;
}

function formatPrice(value: number) {
    return value.toLocaleString("en-IN", { maximumFractionDigits: 2 });
}

export default function DashboardOpportunityTable({
    type,
    opportunities,
    limit,
    loading = false,
    error = "",
}: DashboardOpportunityTableProps) {
    const demand = type === "demand";
    const title = demand ? "Top Demand Zone Opportunities" : "Top Supply Zone Opportunities";
    const subtitle = demand
        ? "Stocks near stronger buying areas that may deserve attention."
        : "Stocks near selling areas that may need caution or monitoring.";
    const Icon = demand ? TrendingUpRoundedIcon : TrendingDownRoundedIcon;
    const accent = demand ? "#31c77a" : "#ff5c67";
    const visible = opportunities.slice(0, Math.max(0, limit));

    return (
        <Card sx={{ height: "100%", minHeight: { lg: 430 }, overflow: "hidden" }}>
            <CardContent sx={{ height: "100%", display: "flex", flexDirection: "column", p: 0, "&:last-child": { pb: 0 } }}>
                <Stack
                    direction="row"
                    spacing={1.25}
                    sx={{
                        px: 2,
                        py: 1.75,
                        alignItems: "center",
                        borderBottom: "1px solid",
                        borderColor: "divider",
                        bgcolor: (theme) => alpha(accent, theme.palette.mode === "dark" ? 0.07 : 0.05),
                    }}
                >
                    <Box sx={{ width: 36, height: 36, display: "grid", placeItems: "center", borderRadius: 2, color: accent, bgcolor: alpha(accent, 0.12) }}>
                        <Icon />
                    </Box>
                    <Box sx={{ flex: 1, minWidth: 0 }}>
                        <Typography variant="h6">{title}</Typography>
                        <Typography color="text.secondary" sx={{ mt: 0.2, fontSize: "0.67rem" }}>{subtitle}</Typography>
                    </Box>
                    <Button component={RouterLink} to="/scanner" size="small" endIcon={<ArrowForwardRoundedIcon />}>
                        View All
                    </Button>
                </Stack>

                <TableContainer sx={{ flex: 1 }}>
                    <Table size="small" aria-label={title}>
                        <TableHead>
                            <TableRow>
                                <TableCell width={48}>Rank</TableCell>
                                <TableCell>Stock</TableCell>
                                <TableCell align="right">AI Score</TableCell>
                                <TableCell>Zone</TableCell>
                                <TableCell align="right">Distance</TableCell>
                                <TableCell align="right">Trade Confidence</TableCell>
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            {!loading && visible.map(({ zone, tradeConfidence }, index) => (
                                <TableRow key={`${zone.symbol}-${zone.timeframe}-${zone.base_index}-${zone.proximal_price}`} hover>
                                    <TableCell>
                                        <Chip size="small" label={`#${index + 1}`} sx={{ minWidth: 34, color: accent, bgcolor: alpha(accent, 0.1), fontWeight: 900 }} />
                                    </TableCell>
                                    <TableCell>
                                        <Typography sx={{ fontWeight: 900 }}>{zone.symbol}</Typography>
                                        <Typography color="text.secondary" sx={{ fontSize: "0.61rem" }}>{zone.timeframe} · {zone.status}</Typography>
                                    </TableCell>
                                    <TableCell align="right">
                                        <Typography sx={{ color: accent, fontWeight: 900 }}>{zone.zone_score.toFixed(0)}</Typography>
                                    </TableCell>
                                    <TableCell>
                                        <Typography sx={{ fontWeight: 750, whiteSpace: "nowrap" }}>
                                            ₹{formatPrice(Math.min(zone.proximal_price, zone.distal_price))}
                                            {" – "}
                                            ₹{formatPrice(Math.max(zone.proximal_price, zone.distal_price))}
                                        </Typography>
                                    </TableCell>
                                    <TableCell align="right">
                                        <Typography sx={{ fontWeight: 800 }}>{zone.distance_percent.toFixed(2)}%</Typography>
                                    </TableCell>
                                    <TableCell align="right">
                                        <Stack spacing={0.45} sx={{ minWidth: 82, alignItems: "flex-end" }}>
                                            <Typography sx={{ fontWeight: 900 }}>{tradeConfidence}%</Typography>
                                            <LinearProgress
                                                variant="determinate"
                                                value={tradeConfidence}
                                                sx={{
                                                    width: 72,
                                                    height: 5,
                                                    bgcolor: "action.hover",
                                                    "& .MuiLinearProgress-bar": { bgcolor: accent },
                                                }}
                                            />
                                        </Stack>
                                    </TableCell>
                                </TableRow>
                            ))}
                            {!loading && !error && visible.length === 0 && (
                                <TableRow>
                                    <TableCell colSpan={6} sx={{ py: 7, textAlign: "center" }}>
                                        <Typography sx={{ fontWeight: 800 }}>No {type} zones are ready to show.</Typography>
                                        <Typography color="text.secondary" sx={{ mt: 0.5 }}>Open the Scanner to check other timeframes or filters.</Typography>
                                    </TableCell>
                                </TableRow>
                            )}
                            {!loading && error && (
                                <TableRow>
                                    <TableCell colSpan={6} sx={{ py: 7, textAlign: "center" }}>
                                        <Typography color="warning.main" sx={{ fontWeight: 800 }}>Zone data is unavailable right now.</Typography>
                                        <Typography color="text.secondary" sx={{ mt: 0.5 }}>{error}</Typography>
                                    </TableCell>
                                </TableRow>
                            )}
                            {loading && (
                                <TableRow>
                                    <TableCell colSpan={6} sx={{ py: 7, textAlign: "center" }}>
                                        <Typography color="text.secondary">Loading zone opportunities...</Typography>
                                    </TableCell>
                                </TableRow>
                            )}
                        </TableBody>
                    </Table>
                </TableContainer>

                <Stack direction="row" sx={{ px: 2, py: 1.1, alignItems: "center", justifyContent: "space-between", borderTop: "1px solid", borderColor: "divider" }}>
                    <Typography color="text.secondary" sx={{ fontSize: "0.61rem" }}>
                        Ranked by the existing Scanner service · delayed research data
                    </Typography>
                    <Typography sx={{ color: accent, fontSize: "0.61rem", fontWeight: 800 }}>
                        {visible.length} shown
                    </Typography>
                </Stack>
            </CardContent>
        </Card>
    );
}
