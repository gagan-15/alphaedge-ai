import KeyboardArrowRightRoundedIcon from "@mui/icons-material/KeyboardArrowRightRounded";
import CloseRoundedIcon from "@mui/icons-material/CloseRounded";
import FullscreenRoundedIcon from "@mui/icons-material/FullscreenRounded";
import BugReportOutlinedIcon from "@mui/icons-material/BugReportOutlined";
import Box from "@mui/material/Box";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Chip from "@mui/material/Chip";
import Dialog from "@mui/material/Dialog";
import DialogContent from "@mui/material/DialogContent";
import DialogTitle from "@mui/material/DialogTitle";
import Grid from "@mui/material/Grid";
import IconButton from "@mui/material/IconButton";
import Menu from "@mui/material/Menu";
import MenuItem from "@mui/material/MenuItem";
import Switch from "@mui/material/Switch";
import Stack from "@mui/material/Stack";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import TableSortLabel from "@mui/material/TableSortLabel";
import Typography from "@mui/material/Typography";
import { useCallback, useEffect, useMemo, useState } from "react";

import type { ConfluenceChartOverlay, ZoneResearchResult } from "../../types/scanner";
import ZoneDetailChart from "./ZoneDetailChart";
import ZoneExplanationPanel from "./ZoneExplanationPanel";
import { zoneSequenceLabel } from "./zoneLabels";
import { readOverlayTimeframes, saveOverlayTimeframes } from "../../services/overlayService";
import { selectZoneById, zoneIdFor } from "../../services/zoneSelectionService";
import { getMarketCandles } from "../../api/marketApi";
import { getStockDetailsAnalysis } from "../../api/scannerApi";
import { analyzeStockZone } from "./stockZoneAnalysis";
import { buildTradeConfidence } from "./tradeConfidence";
import DeveloperZoneInspector from "./DeveloperZoneInspector";
import { acceptedDeveloperZones } from "./developerZones";

interface ScannerResultsTableProps {
    results: ZoneResearchResult[];
    initialSelection?: {
        symbol: string;
        timeframe: string;
        selectedZone: "demand" | "supply";
    };
}

const patternLabels: Record<string, string> = {
    DROP_BASE_RALLY: "DBR",
    RALLY_BASE_RALLY: "RBR",
    RALLY_BASE_DROP: "RBD",
    DROP_BASE_DROP: "DBD",
};

function scorePresentation(score: number | undefined) {
    if (score === undefined) return { color: "#94a3b8", label: "Pending" };
    if (score >= 75) return { color: "#31c77a", label: "High" };
    if (score >= 50) return { color: "#f5b942", label: "Medium" };
    return { color: "#ff5c67", label: "Low" };
}

function recommendation(zoneType: string, score: number | undefined) {
    if (score === undefined || score < 60) return "WATCH";
    return zoneType === "DEMAND" ? "BUY" : "AVOID";
}

function normalizedTimeframe(value: string) {
    const aliases: Record<string, string> = {
        DAILY: "1D",
        WEEKLY: "1W",
        MONTHLY: "1M",
        QUARTERLY: "3M",
        HALFYEARLY: "6M",
        YEARLY: "1Y",
    };
    return aliases[value.toUpperCase()] ?? value.toUpperCase();
}

function resultKey(result: ZoneResearchResult) {
    return `${result.symbol}:${result.timeframe}:${result.zone_type}:${result.proximal_price}:${result.distal_price}:${result.base_index}`;
}

function ScannerResultsTable({ results, initialSelection }: ScannerResultsTableProps) {
    const initialZones = initialSelection
        ? results.filter((zone) =>
            zone.symbol === initialSelection.symbol
            && normalizedTimeframe(zone.timeframe) === normalizedTimeframe(initialSelection.timeframe)
        )
        : [];
    const initialZone = initialSelection
        ? initialZones.find((zone) => zone.zone_type === initialSelection.selectedZone.toUpperCase())
        : undefined;
    const [sortField, setSortField] = useState<"symbol" | "trade_confidence" | "zone_score" | "distance_percent">("trade_confidence");
    const [sortDirection, setSortDirection] = useState<"asc" | "desc">("desc");
    const [developerMode, setDeveloperMode] = useState(false);
    const [developerMenuAnchor, setDeveloperMenuAnchor] = useState<HTMLElement | null>(null);
    const [confidenceScores, setConfidenceScores] = useState<Record<string, number>>({});
    const [selectedZones, setSelectedZones] = useState<ZoneResearchResult[]>(initialZone ? initialZones : []);
    const [selectedZoneId, setSelectedZoneId] = useState(() =>
        initialZone ? zoneIdFor(initialZones, initialZone) : ""
    );
    const [confluenceOverlays, setConfluenceOverlays] = useState<ConfluenceChartOverlay[]>([]);
    const [availableConfluenceOverlays, setAvailableConfluenceOverlays] = useState<ConfluenceChartOverlay[]>([]);
    const [confluenceOverlaysHidden, setConfluenceOverlaysHidden] = useState(false);
    const [inspectedConfluenceTimeframe, setInspectedConfluenceTimeframe] = useState("");
    const [fullChartHeight, setFullChartHeight] = useState(() =>
        Math.max(420, Math.min(680, window.innerHeight - 300))
    );

    useEffect(() => {
        const updateHeight = () => setFullChartHeight(
            Math.max(420, Math.min(680, window.innerHeight - 300))
        );
        window.addEventListener("resize", updateHeight);
        return () => window.removeEventListener("resize", updateHeight);
    }, []);

    useEffect(() => {
        let active = true;
        void Promise.all(results.map(async (result) => {
            const intraday = ["5m", "15m", "75m", "125m", "1H", "2H", "4H", "6H"].includes(result.timeframe);
            const period = intraday ? "1mo" : result.timeframe === "1D" ? "1y" : "10y";
            const interval = intraday ? (result.timeframe.includes("H") ? "1h" : result.timeframe === "5m" || result.timeframe === "125m" ? "5m" : "15m") : "1d";
            try {
                const [candles, backend] = await Promise.all([
                    getMarketCandles(result.symbol, period, interval, result.timeframe),
                    getStockDetailsAnalysis(result),
                ]);
                return [resultKey(result), buildTradeConfidence(result, analyzeStockZone(result, candles.candles), backend).score] as const;
            } catch {
                return [resultKey(result), buildTradeConfidence(result, null, null).score] as const;
            }
        })).then((entries) => {
            if (active) setConfidenceScores(Object.fromEntries(entries));
        });
        return () => { active = false; };
    }, [results]);

    const sortedResults = useMemo(() => [...results].sort((left, right) => {
        const first = sortField === "trade_confidence" ? confidenceScores[resultKey(left)] ?? -1 : left[sortField];
        const second = sortField === "trade_confidence" ? confidenceScores[resultKey(right)] ?? -1 : right[sortField];
        const comparison = typeof first === "string"
            ? first.localeCompare(String(second))
            : Number(first) - Number(second);
        return sortDirection === "asc" ? comparison : -comparison;
    }), [confidenceScores, results, sortDirection, sortField]);
    const groupedResults = useMemo(() => {
        const groups = new Map<string, ZoneResearchResult[]>();
        sortedResults.forEach((result) => {
            groups.set(result.symbol, [...(groups.get(result.symbol) ?? []), result]);
        });
        return [...groups.entries()].map(([symbol, zones]) => ({
            symbol,
            zones,
            primary: [...zones].sort((left, right) =>
                (confidenceScores[resultKey(right)] ?? -1) - (confidenceScores[resultKey(left)] ?? -1)
                || left.distance_percent - right.distance_percent
                || right.zone_score - left.zone_score
            )[0],
        }));
    }, [confidenceScores, sortedResults]);

    function chooseSort(field: typeof sortField) {
        if (field === sortField) {
            setSortDirection((current) => current === "asc" ? "desc" : "asc");
        } else {
            setSortField(field);
            setSortDirection("desc");
        }
    }

    function openStock(zones: ZoneResearchResult[], selectedZone: ZoneResearchResult) {
        setConfluenceOverlays([]);
        setAvailableConfluenceOverlays([]);
        setConfluenceOverlaysHidden(false);
        setInspectedConfluenceTimeframe("");
        setSelectedZones(zones);
        setSelectedZoneId(zoneIdFor(zones, selectedZone));
    }

    function closeStock() {
        setSelectedZones([]);
        setSelectedZoneId("");
        setConfluenceOverlays([]);
        setAvailableConfluenceOverlays([]);
        setConfluenceOverlaysHidden(false);
        setInspectedConfluenceTimeframe("");
    }

    function toggleConfluenceOverlay(overlay: ConfluenceChartOverlay) {
        setConfluenceOverlaysHidden(false);
        setInspectedConfluenceTimeframe("");
        setConfluenceOverlays((current) => {
            const next = current.some((item) => item.timeframe === overlay.timeframe)
                ? current.filter((item) => item.timeframe !== overlay.timeframe)
                : [...current, overlay];
            saveOverlayTimeframes(next.map((item) => item.timeframe));
            return next;
        });
    }

    const handleAvailableConfluenceOverlays = useCallback((overlays: ConfluenceChartOverlay[]) => {
        setAvailableConfluenceOverlays(overlays);
        const saved = readOverlayTimeframes();
        setConfluenceOverlays(overlays.filter((overlay) => saved.includes(overlay.timeframe)));
    }, []);

    function chooseZone(zone: ZoneResearchResult) {
        setSelectedZoneId(zoneIdFor(selectedZones, zone));
        setConfluenceOverlays([]);
        setAvailableConfluenceOverlays([]);
        setConfluenceOverlaysHidden(false);
    }

    function sortableLabel(field: typeof sortField, label: string) {
        return (
            <TableSortLabel active={sortField === field} direction={sortField === field ? sortDirection : "asc"} onClick={() => chooseSort(field)}>
                {label}
            </TableSortLabel>
        );
    }

    return (
        <Card>
            <CardContent sx={{ p: 0, "&:last-child": { pb: 0 } }}>
                <Box sx={{ px: 2, py: 1.5, display: "flex", alignItems: "center", gap: 1 }}>
                    <Typography variant="h6">Zone Intelligence Results</Typography>
                    <Chip size="small" label={`${results.length} zones · ${groupedResults.length} stocks`} />
                    <Typography color="text.secondary" sx={{ ml: "auto", fontSize: ".66rem" }}>
                        Select a row to inspect the highlighted zone
                    </Typography>
                </Box>

                {results.length === 0 ? (
                    <Box sx={{ py: 8, textAlign: "center" }}>
                        <Typography variant="h6" color="text.secondary">No matching research zones</Typography>
                        <Typography color="text.secondary">Run the scanner or reduce the active filters.</Typography>
                    </Box>
                ) : (
                    <TableContainer>
                        <Table size="small" sx={{ minWidth: 1320 }}>
                            <TableHead>
                                <TableRow sx={{ "& th": { color: "text.secondary", py: 1, fontSize: ".66rem", fontWeight: 600, whiteSpace: "nowrap" } }}>
                                    <TableCell width={48}>Rank</TableCell>
                                    <TableCell>{sortableLabel("symbol", "Stock")}</TableCell>
                                    <TableCell align="center">Zones</TableCell>
                                    <TableCell align="center">{sortableLabel("trade_confidence", "AI Score")}</TableCell>
                                    <TableCell>Recommendation</TableCell>
                                    <TableCell>Type</TableCell>
                                    <TableCell>Pattern</TableCell>
                                    <TableCell>Status</TableCell>
                                    <TableCell align="right">Distance</TableCell>
                                    <TableCell align="right">LTP / Entry</TableCell>
                                    <TableCell>Base date</TableCell>
                                    <TableCell>Timeframe</TableCell>
                                    <TableCell align="center">Actions</TableCell>
                                </TableRow>
                            </TableHead>
                            <TableBody>
                                {groupedResults.map(({ symbol, zones, primary: result }, index) => {
                                    const zoneKey = `${result.symbol}-${result.zone_type}-${result.base_date}-${result.proximal_price}`;
                                    const status = result.status;
                                    const aiScore = confidenceScores[resultKey(result)];
                                    const scoreStyle = scorePresentation(aiScore);
                                    const recommendationLabel = recommendation(result.zone_type, aiScore);
                                    const recommendationColor = recommendationLabel === "BUY"
                                        ? "#31c77a"
                                        : recommendationLabel === "AVOID"
                                            ? "#ff5c67"
                                            : "#f5b942";
                                    return (
                                            <TableRow
                                                key={zoneKey}
                                                hover
                                                onClick={() => openStock(zones, result)}
                                                sx={{
                                                    cursor: "pointer",
                                                    transition: "background-color 150ms ease",
                                                    "& td": { py: 1.25, fontSize: ".72rem", fontWeight: 400 },
                                                    "&:hover": { bgcolor: "rgba(99,102,241,.065)" },
                                                    "&:active": { bgcolor: "rgba(99,102,241,.11)" },
                                                }}
                                            >
                                                <TableCell sx={{ color: "text.secondary" }}>
                                                    #{index + 1}
                                                </TableCell>
                                                <TableCell>
                                                    <Typography sx={{ color: "text.primary", fontSize: ".76rem", fontWeight: 650 }}>{symbol}</Typography>
                                                </TableCell>
                                                <TableCell align="center">
                                                    <Chip size="small" variant="outlined" label={zones.length} sx={{ minWidth: 30, fontWeight: 600 }} />
                                                </TableCell>
                                                <TableCell align="center">
                                                    <Box sx={{ display: "inline-flex", minWidth: 62, flexDirection: "column", alignItems: "stretch", gap: .35 }}>
                                                        <Stack direction="row" spacing={.5} sx={{ alignItems: "baseline", justifyContent: "center" }}>
                                                            <Typography sx={{ color: scoreStyle.color, fontSize: "1.02rem", lineHeight: 1, fontWeight: 900 }}>{aiScore ?? "…"}</Typography>
                                                            <Typography sx={{ color: "text.secondary", fontSize: ".54rem" }}>{scoreStyle.label}</Typography>
                                                        </Stack>
                                                        <Box sx={{ height: 3, overflow: "hidden", borderRadius: 5, bgcolor: "action.hover" }}>
                                                            <Box sx={{ width: `${Math.min(100, aiScore ?? 0)}%`, height: "100%", bgcolor: scoreStyle.color }} />
                                                        </Box>
                                                    </Box>
                                                </TableCell>
                                                <TableCell>
                                                    <Chip
                                                        size="small"
                                                        label={recommendationLabel}
                                                        sx={{
                                                            minWidth: 58,
                                                            color: recommendationColor,
                                                            bgcolor: `${recommendationColor}18`,
                                                            border: `1px solid ${recommendationColor}55`,
                                                            fontSize: ".61rem",
                                                            fontWeight: 800,
                                                        }}
                                                    />
                                                </TableCell>
                                                <TableCell>
                                                    <Stack direction="row" spacing={.5}>
                                                        {[...new Set(zones.map((zone) => zone.zone_type))].map((type) => <Chip key={type} size="small" label={type} sx={{ bgcolor: type === "DEMAND" ? "rgba(37,99,235,.28)" : "rgba(225,29,72,.28)", color: type === "DEMAND" ? "#93c5fd" : "#fda4af" }} />)}
                                                    </Stack>
                                                </TableCell>
                                                <TableCell>
                                                    <Box sx={{ display: "flex", gap: .5, alignItems: "center" }}>
                                                        {[...new Set(zones.map((zone) => patternLabels[zone.pattern_type ?? ""] ?? "Pending"))].slice(0, 2).map((pattern) => <Chip key={pattern} size="small" variant="outlined" label={pattern} />)}
                                                        {zones.some((zone) => zone.gap_type) && <Chip size="small" color="warning" label="GAP" />}
                                                    </Box>
                                                </TableCell>
                                                <TableCell>
                                                    <Chip size="small" color={status === "IN ZONE" ? "warning" : status === "APPROACHING" ? "success" : "default"} label={status} />
                                                </TableCell>
                                                <TableCell align="right" sx={{ color: (result.distance_percent ?? 99) <= 3 ? "success.main" : "text.secondary" }}>
                                                    {result.distance_percent === null ? "—" : `${result.distance_percent.toFixed(2)}%`}
                                                </TableCell>
                                                <TableCell align="right" sx={{ color: "text.primary", fontWeight: "600 !important" }}>
                                                    ₹{result.current_price.toLocaleString("en-IN", { maximumFractionDigits: 2 })}
                                                </TableCell>
                                                <TableCell>{result.base_date}</TableCell>
                                                <TableCell>{result.timeframe?.toUpperCase() ?? "1D"}</TableCell>
                                                <TableCell align="center">
                                                    <IconButton
                                                        size="small"
                                                        aria-label={`Open ${result.symbol} full-screen chart`}
                                                        onClick={(event) => {
                                                            event.stopPropagation();
                                                            openStock(zones, result);
                                                        }}
                                                    >
                                                        <KeyboardArrowRightRoundedIcon fontSize="small" />
                                                    </IconButton>
                                                </TableCell>
                                            </TableRow>
                                    );
                                })}
                            </TableBody>
                        </Table>
                    </TableContainer>
                )}
            </CardContent>
            <Dialog fullScreen open={selectedZones.length > 0} onClose={closeStock}>
                {selectedZones.length > 0 && (() => {
                    const selectedZone = selectZoneById(selectedZones, selectedZoneId);
                    if (!selectedZone) return null;
                    const selectedConfidence = confidenceScores[resultKey(selectedZone)];
                    const developerZones = developerMode ? acceptedDeveloperZones(selectedZones, selectedZoneId) : [];
                    return <>
                    <DialogTitle sx={{ py: 1.25, borderBottom: "1px solid", borderColor: "divider" }}>
                        <Box sx={{ display: "flex", alignItems: "center", gap: 1.25 }}>
                            <FullscreenRoundedIcon color="primary" />
                            <Box>
                                <Typography variant="h6">{selectedZone.symbol} · Selected Zone {selectedZoneId} · {selectedZone.zone_type} · {patternLabels[selectedZone.pattern_type ?? ""]}</Typography>
                                <Typography variant="caption" color="text.secondary">{selectedZone.timeframe} research chart · Trade Confidence {selectedConfidence ?? "calculating"} · Zone Quality {selectedZone.zone_score.toFixed(0)} · delayed data · no order execution</Typography>
                            </Box>
                            <Chip sx={{ ml: "auto" }} color={selectedZone.zone_type === "DEMAND" ? "primary" : "error"} label={`${selectedConfidence ?? "…"} · Trade Confidence`} />
                            {import.meta.env.DEV && (
                                <>
                                    <IconButton aria-label="Open developer settings" onClick={(event) => setDeveloperMenuAnchor(event.currentTarget)}>
                                        <BugReportOutlinedIcon />
                                    </IconButton>
                                    <Menu anchorEl={developerMenuAnchor} open={Boolean(developerMenuAnchor)} onClose={() => setDeveloperMenuAnchor(null)}>
                                        <MenuItem onClick={() => setDeveloperMode((enabled) => !enabled)}>
                                            <Switch size="small" checked={developerMode} />
                                            Developer Mode
                                        </MenuItem>
                                    </Menu>
                                </>
                            )}
                            <IconButton aria-label="Close full-screen chart" onClick={closeStock}><CloseRoundedIcon /></IconButton>
                        </Box>
                    </DialogTitle>
                    <DialogContent sx={{ p: 1.5, bgcolor: "#050d18", overflowY: { xs: "auto", lg: "hidden" } }}>
                        <Grid container spacing={1.5}>
                            <Grid size={{ xs: 12, lg: 8.5 }}>
                                <ZoneDetailChart
                                    result={selectedZone}
                                    zones={selectedZones}
                                    selectedZoneId={selectedZoneId}
                                    confluenceOverlays={confluenceOverlaysHidden ? [] : confluenceOverlays}
                                    availableConfluenceOverlays={availableConfluenceOverlays}
                                    onToggleConfluenceOverlay={toggleConfluenceOverlay}
                                    onInspectConfluenceOverlay={setInspectedConfluenceTimeframe}
                                    inspectedConfluenceTimeframe={inspectedConfluenceTimeframe}
                                    onResetChart={() => {
                                        setConfluenceOverlays([]);
                                        setConfluenceOverlaysHidden(false);
                                        setInspectedConfluenceTimeframe("");
                                        saveOverlayTimeframes([]);
                                    }}
                                    height={fullChartHeight}
                                    showTools
                                    developerMode={developerMode}
                                    developerZones={developerMode ? developerZones : undefined}
                                />
                            </Grid>
                            <Grid size={{ xs: 12, lg: 3.5 }}>
                                <Box sx={{ maxHeight: "calc(100vh - 100px)", overflowY: "auto" }}>
                                    {developerMode && <DeveloperZoneInspector zones={developerZones} />}
                                    <Card sx={{ mb: 1.25 }}><CardContent>
                                        <Typography variant="h6">All active zones</Typography>
                                        <Stack spacing={.75} sx={{ mt: 1 }}>
                                            {selectedZones.map((zone, zoneIndex) => {
                                                const zoneId = zoneSequenceLabel(selectedZones, zoneIndex);
                                                const selected = zoneId === selectedZoneId;
                                                return <Box
                                                    key={`${zone.base_date}-${zone.proximal_price}`}
                                                    component="button"
                                                    type="button"
                                                    onClick={() => chooseZone(zone)}
                                                    sx={{ width: "100%", p: 1, textAlign: "left", color: "inherit", font: "inherit", cursor: "pointer", bgcolor: selected ? "rgba(99,102,241,.14)" : "transparent", border: "1px solid", borderColor: selected ? "primary.main" : "divider", borderRadius: 1.5 }}
                                                >
                                                    <Stack direction="row" sx={{ justifyContent: "space-between", gap: 1 }}>
                                                        <Typography sx={{ fontWeight: 800 }}>{selected ? "✓ " : ""}{zoneId} · {zone.zone_type} · {patternLabels[zone.pattern_type ?? ""]}</Typography>
                                                        <Chip size="small" label={`Confidence ${confidenceScores[resultKey(zone)] ?? "…"} · Quality ${zone.zone_score.toFixed(0)}`} />
                                                    </Stack>
                                                    <Typography variant="caption" color="text.secondary">Status {zone.status} · Base {zone.base_date}{selected ? " · Selected" : " · Click to analyze"}</Typography>
                                                </Box>;
                                            })}
                                        </Stack>
                                    </CardContent></Card>
                                    <ZoneExplanationPanel
                                        result={selectedZone}
                                        confluenceOverlays={confluenceOverlays}
                                        confluenceOverlaysHidden={confluenceOverlaysHidden}
                                        onToggleConfluenceOverlay={toggleConfluenceOverlay}
                                        onToggleConfluenceVisibility={() => setConfluenceOverlaysHidden((hidden) => !hidden)}
                                        onClearConfluenceOverlays={() => {
                                            setConfluenceOverlays([]);
                                            setConfluenceOverlaysHidden(false);
                                            saveOverlayTimeframes([]);
                                        }}
                                        onAvailableConfluenceOverlays={handleAvailableConfluenceOverlays}
                                        inspectedConfluenceTimeframe={inspectedConfluenceTimeframe}
                                    />
                                </Box>
                            </Grid>
                        </Grid>
                    </DialogContent>
                </>; })()}
            </Dialog>
        </Card>
    );
}

export default ScannerResultsTable;
