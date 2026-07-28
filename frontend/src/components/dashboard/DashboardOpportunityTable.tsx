import ArrowForwardRoundedIcon from "@mui/icons-material/ArrowForwardRounded";
import TrendingDownRoundedIcon from "@mui/icons-material/TrendingDownRounded";
import TrendingUpRoundedIcon from "@mui/icons-material/TrendingUpRounded";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import LinearProgress from "@mui/material/LinearProgress";
import Skeleton from "@mui/material/Skeleton";
import Stack from "@mui/material/Stack";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import Typography from "@mui/material/Typography";
import { alpha } from "@mui/material/styles";
import { Link as RouterLink, useNavigate } from "react-router-dom";

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
    const navigate = useNavigate();
    const demand = type === "demand";
    const title = demand ? "Top Demand Zone Opportunities" : "Top Supply Zone Opportunities";
    const subtitle = demand
        ? "Stocks near stronger buying areas that may deserve attention."
        : "Stocks near selling areas that may need caution or monitoring.";
    const Icon = demand ? TrendingUpRoundedIcon : TrendingDownRoundedIcon;
    const accent = demand ? "#31c77a" : "#ff5c67";
    const visible = opportunities.slice(0, Math.max(0, limit));
    const skeletonRows = Array.from({ length: Math.max(1, limit) });

    return (
        <Card sx={{ height: "100%", minHeight: { lg: 430 }, overflow: "hidden", borderTop: `2px solid ${alpha(accent, 0.75)}` }}>
            <CardContent sx={{ height: "100%", display: "flex", flexDirection: "column", p: 0, "&:last-child": { pb: 0 } }}>
                <Stack
                    direction="row"
                    spacing={1.25}
                    sx={{
                        px: 2,
                        py: 1.55,
                        alignItems: "center",
                        borderBottom: "1px solid",
                        borderColor: "divider",
                        bgcolor: (theme) => alpha(accent, theme.palette.mode === "dark" ? 0.085 : 0.055),
                    }}
                >
                    <Box sx={{ width: 36, height: 36, display: "grid", placeItems: "center", borderRadius: 2, color: accent, bgcolor: alpha(accent, 0.14) }}>
                        <Icon />
                    </Box>
                    <Box sx={{ flex: 1, minWidth: 0 }}>
                        <Typography variant="h6" sx={{ color: accent }}>{title}</Typography>
                        <Typography color="text.secondary" sx={{ mt: 0.15, fontSize: "0.64rem" }}>{subtitle}</Typography>
                    </Box>
                    <Button
                        component={RouterLink}
                        to="/scanner"
                        size="small"
                        variant="outlined"
                        endIcon={<ArrowForwardRoundedIcon />}
                        sx={{ color: accent, borderColor: alpha(accent, 0.42), "&:hover": { borderColor: accent, bgcolor: alpha(accent, 0.07) } }}
                    >
                        View All
                    </Button>
                </Stack>

                <TableContainer sx={{ flex: 1, height: 340, minHeight: 340 }}>
                    <Table size="small" aria-label={title} sx={{ minWidth: 650 }}>
                        <TableHead>
                            <TableRow
                                sx={{
                                    "& th": {
                                        color: "text.secondary",
                                        fontSize: "0.68rem",
                                        fontWeight: 500,
                                    },
                                }}
                            >
                                <TableCell width={46}>Rank</TableCell>
                                <TableCell>Stock</TableCell>
                                <TableCell align="center">AI Score</TableCell>
                                <TableCell>Zone</TableCell>
                                <TableCell align="right">Distance</TableCell>
                                <TableCell align="right">Trade Confidence</TableCell>
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            {!loading && visible.map(({ zone, tradeConfidence }, index) => (
                                <TableRow
                                    key={`${zone.symbol}-${zone.timeframe}-${zone.base_index}-${zone.proximal_price}`}
                                    hover
                                    tabIndex={0}
                                    role="link"
                                    onClick={() => navigate("/scanner")}
                                    onKeyDown={(event) => {
                                        if (event.key === "Enter" || event.key === " ") navigate("/scanner");
                                    }}
                                    sx={{
                                        cursor: "pointer",
                                        transition: "background-color 160ms ease",
                                        "& td": { py: 1.3 },
                                        "& td:first-of-type": { borderLeft: `3px solid ${alpha(accent, 0.72)}` },
                                        "&:hover, &:focus-visible": { bgcolor: alpha(accent, 0.065), outline: "none" },
                                    }}
                                >
                                    <TableCell>
                                        <Typography sx={{ color: "text.secondary", fontSize: "0.68rem", fontWeight: 500 }}>#{index + 1}</Typography>
                                    </TableCell>
                                    <TableCell>
                                        <Typography sx={{ color: "text.primary", fontSize: "0.86rem", fontWeight: 600 }}>{zone.symbol}</Typography>
                                        <Typography color="text.secondary" sx={{ fontSize: "0.75rem", fontWeight: 400 }}>{zone.timeframe} · {zone.status}</Typography>
                                    </TableCell>
                                    <TableCell align="center">
                                        <Box sx={{ display: "inline-grid", minWidth: 48, height: 38, px: 0.85, placeItems: "center", borderRadius: 1.8, color: accent, bgcolor: alpha(accent, 0.13), border: `1px solid ${alpha(accent, 0.3)}` }}>
                                            <Typography sx={{ fontSize: "1.12rem", lineHeight: 1, fontWeight: 900 }}>{zone.zone_score.toFixed(0)}</Typography>
                                        </Box>
                                    </TableCell>
                                    <TableCell>
                                        <Typography sx={{ fontSize: "0.7rem", fontWeight: 500, whiteSpace: "nowrap" }}>
                                            ₹{formatPrice(Math.min(zone.proximal_price, zone.distal_price))}
                                            {" – "}
                                            ₹{formatPrice(Math.max(zone.proximal_price, zone.distal_price))}
                                        </Typography>
                                    </TableCell>
                                    <TableCell align="right">
                                        <Typography sx={{ fontSize: "0.7rem", fontWeight: 500 }}>{zone.distance_percent.toFixed(2)}%</Typography>
                                    </TableCell>
                                    <TableCell align="right">
                                        <Stack spacing={0.4} sx={{ minWidth: 78, alignItems: "flex-end" }}>
                                            <Typography sx={{ fontSize: "0.72rem", fontWeight: 500 }}>{tradeConfidence}%</Typography>
                                            <LinearProgress
                                                variant="determinate"
                                                value={tradeConfidence}
                                                sx={{
                                                    width: 66,
                                                    height: 4,
                                                    bgcolor: "action.hover",
                                                    "& .MuiLinearProgress-bar": { bgcolor: accent },
                                                }}
                                            />
                                        </Stack>
                                    </TableCell>
                                </TableRow>
                            ))}
                            {loading && skeletonRows.map((_, index) => (
                                <TableRow key={`skeleton-${index}`} sx={{ height: 58, "& td": { py: 1.35 } }}>
                                    <TableCell><Skeleton width={24} /></TableCell>
                                    <TableCell><Skeleton width={72} /><Skeleton width={48} height={14} /></TableCell>
                                    <TableCell align="center"><Skeleton variant="rounded" width={42} height={34} sx={{ mx: "auto" }} /></TableCell>
                                    <TableCell><Skeleton width={116} /></TableCell>
                                    <TableCell><Skeleton width={48} sx={{ ml: "auto" }} /></TableCell>
                                    <TableCell><Skeleton width={66} sx={{ ml: "auto" }} /></TableCell>
                                </TableRow>
                            ))}
                            {!loading && !error && visible.length < limit && (
                                <TableRow>
                                    <TableCell
                                        colSpan={6}
                                        sx={{
                                            height: Math.max(72, (limit - visible.length) * 58),
                                            px: 3,
                                            textAlign: "center",
                                            verticalAlign: "middle",
                                        }}
                                    >
                                        <Typography color="text.secondary" sx={{ maxWidth: 430, mx: "auto", lineHeight: 1.6 }}>
                                            Only the highest-quality opportunities matched today's filters. Click View All to explore additional scanner results.
                                        </Typography>
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
                        </TableBody>
                    </Table>
                </TableContainer>

                <Stack direction="row" sx={{ px: 2, py: 0.45, alignItems: "center", justifyContent: "flex-end", borderTop: "1px solid", borderColor: "divider" }}>
                    <Typography color="text.secondary" sx={{ fontSize: "0.52rem", opacity: 0.52 }}>
                        Delayed research data · {visible.length} shown
                    </Typography>
                </Stack>
            </CardContent>
        </Card>
    );
}
