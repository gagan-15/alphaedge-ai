import StarBorderRoundedIcon from "@mui/icons-material/StarBorderRounded";
import VisibilityOutlinedIcon from "@mui/icons-material/VisibilityOutlined";
import FilterAltOutlinedIcon from "@mui/icons-material/FilterAltOutlined";
import ChevronRightRoundedIcon from "@mui/icons-material/ChevronRightRounded";
import CloseRoundedIcon from "@mui/icons-material/CloseRounded";
import FullscreenRoundedIcon from "@mui/icons-material/FullscreenRounded";
import BugReportOutlinedIcon from "@mui/icons-material/BugReportOutlined";
import QueryStatsRoundedIcon from "@mui/icons-material/QueryStatsRounded";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Chip from "@mui/material/Chip";
import Dialog from "@mui/material/Dialog";
import DialogContent from "@mui/material/DialogContent";
import DialogTitle from "@mui/material/DialogTitle";
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
import Tooltip from "@mui/material/Tooltip";
import Typography from "@mui/material/Typography";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";

import type { ConfluenceChartOverlay, ZoneDiagnosticsResponse, ZoneResearchResult } from "../../types/scanner";
import ZoneDetailChart from "./ZoneDetailChart";
import ZoneExplanationPanel from "./ZoneExplanationPanel";
import { zoneSequenceLabel } from "./zoneLabels";
import { readOverlayTimeframes, saveOverlayTimeframes } from "../../services/overlayService";
import { selectZoneById, zoneIdFor } from "../../services/zoneSelectionService";
import { getZoneDiagnostics } from "../../api/scannerApi";
import { formatZoneQuality, formatZoneQualityLabel } from "./zoneQualityPresentation";
import { compareCanonicalTradeConfidence, tradeConfidenceDisplay } from "./tradeConfidenceRanking";
import DeveloperZoneInspector from "./DeveloperZoneInspector";
import { acceptedDeveloperZones, diagnosticDeveloperZones } from "./developerZones";

interface ScannerResultsTableProps {
    results: ZoneResearchResult[];
    methodologyVersion?: string;
    initialSelection?: {
        symbol: string;
        timeframe: string;
        selectedZone: "demand" | "supply";
        proximalPrice?: number;
        distalPrice?: number;
        baseIndex?: number;
    };
    onDetailsClose?: () => void;
}

const patternLabels: Record<string, string> = {
    DROP_BASE_RALLY: "DBR",
    RALLY_BASE_RALLY: "RBR",
    RALLY_BASE_DROP: "RBD",
    DROP_BASE_DROP: "DBD",
};
const analysisPanelPreferenceKey = "alphaedge.stock-details.analysis-panel";

function scorePresentation(score: number | undefined) {
    if (score === undefined) return { color: "#64748b", background: "#f1f5f9", border: "#cbd5e1" };
    if (score >= 80) return { color: "#28785a", background: "#edf7f2", border: "#9bcbb5" };
    if (score >= 60) return { color: "#8a681d", background: "#fbf6e8", border: "#ddc98d" };
    if (score >= 40) return { color: "#9a642f", background: "#fcf1e7", border: "#e3bd98" };
    return { color: "#8f5660", background: "#faf0f1", border: "#e4c2c7" };
}

function qualityPresentation(score: number) {
    if (score >= 90) return { label: "Excellent", color: "#166534", background: "#E8F5EC", border: "#B7DEC2" };
    if (score >= 80) return { label: "Strong", color: "#28785A", background: "#EDF7F2", border: "#B9DCCA" };
    if (score >= 70) return { label: "Good", color: "#2563EB", background: "#EEF4FF", border: "#C9DAFF" };
    if (score >= 60) return { label: "Average", color: "#A16207", background: "#FFF4DE", border: "#F7D99B" };
    return { label: "Weak", color: "#667085", background: "#F2F4F7", border: "#D0D5DD" };
}

function statusPresentation(status: string) {
    if (status === "REACTING") return { color: "#4338CA", background: "#EEF2FF", border: "#A5B4FC", hover: "#E4E8FF" };
    if (status === "IN ZONE") return { color: "#166534", background: "#DCFCE7", border: "#4ADE80", hover: "#D2F8DF" };
    if (status === "APPROACHING") return { color: "#92400E", background: "#FEF3C7", border: "#FBBF24", hover: "#FCEBB4" };
    if (status === "TESTED") return { color: "#7C3AED", background: "#F3ECFF", border: "#D9C6FF", hover: "#ECE2FD" };
    if (status === "INVALID") return { color: "#DC2626", background: "#FDECEC", border: "#F7CACA", hover: "#F9E2E2" };
    return { color: "#475569", background: "#F1F5F9", border: "#CBD5E1", hover: "#E8EEF5" };
}

function distancePresentation(distance: number | null) {
    if (distance === null || distance > 5) return "#667085";
    if (distance <= 1) return "#166534";
    if (distance <= 2) return "#22834F";
    if (distance <= 3) return "#3D9365";
    return "#66947A";
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

function ScannerResultsTable({ results, methodologyVersion = "", initialSelection, onDetailsClose }: ScannerResultsTableProps) {
    const navigate = useNavigate();
    const [page, setPage] = useState(0);
    const initialZones = initialSelection
        ? results.filter((zone) =>
            zone.symbol === initialSelection.symbol
            && normalizedTimeframe(zone.timeframe) === normalizedTimeframe(initialSelection.timeframe)
        )
        : [];
    const initialZone = initialSelection
        ? initialZones.find((zone) =>
            zone.zone_type === initialSelection.selectedZone.toUpperCase()
            && (initialSelection.baseIndex === undefined || zone.base_index === initialSelection.baseIndex)
            && (initialSelection.proximalPrice === undefined || zone.proximal_price === initialSelection.proximalPrice)
            && (initialSelection.distalPrice === undefined || zone.distal_price === initialSelection.distalPrice)
        ) ?? initialZones.find((zone) => zone.zone_type === initialSelection.selectedZone.toUpperCase())
        : undefined;
    const [sortField, setSortField] = useState<"symbol" | "trade_confidence" | "zone_score" | "distance_percent">("trade_confidence");
    const [sortDirection, setSortDirection] = useState<"asc" | "desc">("desc");
    const [developerMode, setDeveloperMode] = useState(false);
    const [analysisPanelOpen, setAnalysisPanelOpen] = useState(() =>
        localStorage.getItem(analysisPanelPreferenceKey) === "open"
    );
    const [developerMenuAnchor, setDeveloperMenuAnchor] = useState<HTMLElement | null>(null);
    const [developerDiagnostics, setDeveloperDiagnostics] = useState<ZoneDiagnosticsResponse | null>(null);
    const [developerDiagnosticsError, setDeveloperDiagnosticsError] = useState("");
    const [selectedZones, setSelectedZones] = useState<ZoneResearchResult[]>(initialZone ? initialZones : []);
    const [selectedZoneId, setSelectedZoneId] = useState(() =>
        initialZone ? zoneIdFor(initialZones, initialZone) : ""
    );
    const initialSelectionHandled = useRef(Boolean(initialZone));

    useEffect(() => {
        if (!initialSelection || initialSelectionHandled.current || results.length === 0) {
            return;
        }
        const matchingZones = results.filter((zone) =>
            zone.symbol === initialSelection.symbol
            && normalizedTimeframe(zone.timeframe) === normalizedTimeframe(initialSelection.timeframe)
        );
        const matchingZone = matchingZones.find((zone) =>
            zone.zone_type === initialSelection.selectedZone.toUpperCase()
            && (initialSelection.baseIndex === undefined || zone.base_index === initialSelection.baseIndex)
            && (initialSelection.proximalPrice === undefined || zone.proximal_price === initialSelection.proximalPrice)
            && (initialSelection.distalPrice === undefined || zone.distal_price === initialSelection.distalPrice)
        ) ?? matchingZones.find((zone) =>
            zone.zone_type === initialSelection.selectedZone.toUpperCase()
        );
        if (!matchingZone) return;
        initialSelectionHandled.current = true;
        queueMicrotask(() => {
            setSelectedZones(matchingZones);
            setSelectedZoneId(zoneIdFor(matchingZones, matchingZone));
        });
    }, [initialSelection, results]);
    const developerChartZones = useMemo(
        () => {
            if (!developerMode) return [];
            const selected = selectZoneById(selectedZones, selectedZoneId);
            const diagnosticsMatch = Boolean(
                selected
                && developerDiagnostics
                && developerDiagnostics.symbol === selected.symbol
                && normalizedTimeframe(developerDiagnostics.timeframe)
                    === normalizedTimeframe(selected.timeframe)
            );
            return diagnosticsMatch && developerDiagnostics
                ? diagnosticDeveloperZones(developerDiagnostics.candidates, selected)
                : acceptedDeveloperZones(selectedZones, selectedZoneId);
        },
        [developerDiagnostics, developerMode, selectedZoneId, selectedZones],
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
        if (!developerMode || selectedZones.length === 0) {
            return;
        }
        const selected = selectZoneById(selectedZones, selectedZoneId);
        if (!selected) return;
        let active = true;
        void getZoneDiagnostics(selected.symbol, selected.timeframe)
            .then((payload) => {
                if (active) {
                    setDeveloperDiagnostics(payload);
                    setDeveloperDiagnosticsError("");
                }
            })
            .catch(() => {
                if (active) setDeveloperDiagnosticsError("Candidate diagnostics could not be loaded.");
            });
        return () => {
            active = false;
        };
    }, [developerMode, selectedZoneId, selectedZones]);

    const sortedResults = useMemo(() => [...results].sort((left, right) => {
        if (sortField === "trade_confidence") {
            const comparison = compareCanonicalTradeConfidence(left, right);
            return sortDirection === "desc" ? comparison : -comparison;
        }
        const first = left[sortField];
        const second = right[sortField];
        const comparison = typeof first === "string"
            ? first.localeCompare(String(second))
            : Number(first) - Number(second);
        return sortDirection === "asc" ? comparison : -comparison;
    }), [results, sortDirection, sortField]);
    const groupedResults = useMemo(() => {
        const groups = new Map<string, ZoneResearchResult[]>();
        sortedResults.forEach((result) => {
            groups.set(result.symbol, [...(groups.get(result.symbol) ?? []), result]);
        });
        return [...groups.entries()].map(([symbol, zones]) => ({
            symbol,
            zones,
            primary: [...zones].sort(compareCanonicalTradeConfidence)[0],
        }));
    }, [sortedResults]);
    const safePage = Math.min(page, Math.max(0, Math.ceil(groupedResults.length / 14) - 1));
    const visibleGroups = groupedResults.slice(safePage * 14, safePage * 14 + 14);

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
        onDetailsClose?.();
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

    const toggleAnalysisPanel = useCallback(() => {
        setAnalysisPanelOpen((open) => {
            const next = !open;
            localStorage.setItem(analysisPanelPreferenceKey, next ? "open" : "hidden");
            return next;
        });
    }, []);

    useEffect(() => {
        const handleShortcut = (event: KeyboardEvent) => {
            if (event.shiftKey && event.key.toLowerCase() === "p") {
                event.preventDefault();
                toggleAnalysisPanel();
            }
        };
        window.addEventListener("keydown", handleShortcut);
        return () => window.removeEventListener("keydown", handleShortcut);
    }, [toggleAnalysisPanel]);

    function sortableLabel(field: typeof sortField, label: string) {
        return (
            <TableSortLabel active={sortField === field} direction={sortField === field ? sortDirection : "asc"} onClick={() => chooseSort(field)}>
                {label}
            </TableSortLabel>
        );
    }

    return (
        <Card sx={{ borderRadius: "16px", boxShadow: "0 4px 16px rgba(28,45,72,.04)", overflow: "hidden" }}>
            <CardContent sx={{ p: 0, "&:last-child": { pb: 0 } }}>
                <Box sx={{ display: "none" }}>
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
                        <Table stickyHeader size="small" sx={{ width: "100%", minWidth: 1440, tableLayout: "fixed" }}>
                            <colgroup>
                                <col style={{ width: 40 }} />
                                <col style={{ width: 50 }} />
                                <col style={{ width: 220 }} />
                                <col style={{ width: 100 }} />
                                <col style={{ width: 140 }} />
                                <col style={{ width: 260 }} />
                                <col style={{ width: 80 }} />
                                <col style={{ width: 155 }} />
                                <col style={{ width: 105 }} />
                                <col style={{ width: 125 }} />
                                <col style={{ width: 90 }} />
                                <col style={{ width: 75 }} />
                            </colgroup>
                            <TableHead>
                                <TableRow sx={{ "& th": { color: "#475467", px: 2, py: 1.05, fontSize: ".66rem", lineHeight: 1.3, fontWeight: 600, whiteSpace: "nowrap", bgcolor: "#F5F7FA", borderBottom: "1px solid #DFE5EE", verticalAlign: "middle" } }}>
                                    <TableCell align="center"><FilterAltOutlinedIcon sx={{ fontSize: 15, verticalAlign: "middle" }} /></TableCell>
                                    <TableCell align="center">#</TableCell>
                                    <TableCell>{sortableLabel("symbol", "Stock")}</TableCell>
                                    <TableCell align="center">{sortableLabel("trade_confidence", "Trade Confidence")}</TableCell>
                                    <TableCell align="center">
                                        <Tooltip title="Zone Quality measures how well the zone itself was formed. Trade Confidence adds higher-timeframe location and trend context.">
                                            <Box component="span">{sortableLabel("zone_score", "Zone Quality")}</Box>
                                        </Tooltip>
                                    </TableCell>
                                    <TableCell>Zone (Price Range)</TableCell>
                                    <TableCell align="center">Pattern</TableCell>
                                    <TableCell align="center">Status</TableCell>
                                    <TableCell align="right">Distance</TableCell>
                                    <TableCell align="right">LTP</TableCell>
                                    <TableCell align="center">Timeframe</TableCell>
                                    <TableCell align="center">Action</TableCell>
                                </TableRow>
                            </TableHead>
                            <TableBody>
                                {visibleGroups.map(({ symbol, zones, primary: result }, index) => {
                                    const zoneKey = `${result.symbol}-${result.zone_type}-${result.base_date}-${result.proximal_price}`;
                                    const status = result.status;
                                    const canonical = result.trade_confidence;
                                    const confidence = tradeConfidenceDisplay(canonical);
                                    const scoreStyle = scorePresentation(canonical?.score);
                                    const qualityStyle = qualityPresentation(result.zone_score);
                                    const statusStyle = statusPresentation(status);
                                    return (
                                            <TableRow
                                                key={zoneKey}
                                                hover
                                                onClick={() => openStock(zones, result)}
                                                sx={{
                                                    cursor: "pointer",
                                                    transition: "background-color 150ms ease",
                                                    "& td": { height: 45, px: 2, py: 0.55, fontSize: ".72rem", lineHeight: 1.4, fontWeight: 500, borderColor: "#DFE5EE", verticalAlign: "middle" },
                                                    "& td:first-of-type": { borderLeft: "2px solid transparent" },
                                                    "&:hover": { bgcolor: "#F8FAFC" },
                                                    "&:hover td:first-of-type": { borderLeftColor: "#b9c8f1" },
                                                    "&:active": { bgcolor: "#eef5ff" },
                                                }}
                                            >
                                                <TableCell align="center"><StarBorderRoundedIcon sx={{ color: "text.secondary", fontSize: 17, verticalAlign: "middle" }} /></TableCell>
                                                <TableCell align="center" sx={{ color: "text.secondary" }}>
                                                    {safePage * 14 + index + 1}
                                                </TableCell>
                                                <TableCell>
                                                    <Typography sx={{ color: "#172033", fontSize: ".74rem", lineHeight: 1.35, fontWeight: 600 }}>{symbol}</Typography>
                                                </TableCell>
                                                <TableCell align="center">
                                                    <Box>
                                                        <Box sx={{ display: "inline-grid", width: 29, height: 29, placeItems: "center", borderRadius: "50%", border: "1px solid", borderColor: `${scoreStyle.border}B8`, bgcolor: scoreStyle.background }}>
                                                            <Typography sx={{ color: scoreStyle.color, fontSize: ".64rem", fontWeight: 750 }}>{confidence.score}</Typography>
                                                        </Box>
                                                        <Typography color="text.secondary" sx={{ fontSize: ".52rem", mt: .2 }}>{confidence.label}</Typography>
                                                    </Box>
                                                </TableCell>
                                                <TableCell align="center">
                                                    <Box sx={{ display: "inline-flex", height: 24, minWidth: 68, justifyContent: "center", alignItems: "center", gap: .6, px: 1, borderRadius: 1.25, border: "1px solid", borderColor: `${qualityStyle.border}CC`, bgcolor: qualityStyle.background }}>
                                                        <Typography sx={{ color: qualityStyle.color, fontSize: ".7rem", lineHeight: 1, fontWeight: 800 }}>{formatZoneQuality(result.zone_score)}</Typography>
                                                        <Typography sx={{ color: qualityStyle.color, fontSize: ".56rem", lineHeight: 1, fontWeight: 700 }}>{formatZoneQualityLabel(result.zone_quality_label ?? qualityStyle.label)}</Typography>
                                                    </Box>
                                                </TableCell>
                                                <TableCell sx={{ whiteSpace: "nowrap", color: result.zone_type === "DEMAND" ? "#2f7d5b" : "#b45863", fontWeight: "500 !important" }}>
                                                    {"\u20B9"}{Math.min(result.proximal_price, result.distal_price).toLocaleString("en-IN", { maximumFractionDigits: 2 })}{" \u2013 \u20B9"}{Math.max(result.proximal_price, result.distal_price).toLocaleString("en-IN", { maximumFractionDigits: 2 })}
                                                </TableCell>
                                                <TableCell align="center">
                                                    <Typography sx={{ fontSize: ".7rem", fontWeight: 500 }}>{patternLabels[result.pattern_type ?? ""] ?? "—"}</Typography>
                                                </TableCell>
                                                <TableCell align="center">
                                                    <Chip
                                                        size="small"
                                                        label={status === "WATCH" ? "NEARBY" : status}
                                                        sx={{
                                                            height: 27,
                                                            borderRadius: "999px",
                                                            color: statusStyle.color,
                                                            bgcolor: statusStyle.background,
                                                            border: "1px solid",
                                                            borderColor: statusStyle.border,
                                                            fontSize: ".56rem",
                                                            lineHeight: 1,
                                                            fontWeight: 600,
                                                            letterSpacing: ".035em",
                                                            transition: "background-color 160ms ease",
                                                            "& .MuiChip-label": { px: 1.4, py: 0, lineHeight: "25px" },
                                                            "&:hover": { bgcolor: statusStyle.hover },
                                                        }}
                                                    />
                                                </TableCell>
                                                <TableCell align="right" sx={{ color: distancePresentation(result.distance_percent) }}>
                                                    {result.distance_percent === null ? "—" : `${result.distance_percent.toFixed(2)}%`}
                                                </TableCell>
                                                <TableCell align="right" sx={{ color: "text.primary", fontWeight: "600 !important" }}>
                                                    ₹{result.current_price.toLocaleString("en-IN", { maximumFractionDigits: 2 })}
                                                </TableCell>
                                                <TableCell align="center">{result.timeframe?.toUpperCase() ?? "1D"}</TableCell>
                                                <TableCell align="center" sx={{ verticalAlign: "middle" }}>
                                                    <Stack direction="row" spacing={.25} sx={{ justifyContent: "center" }}>
                                                        {(normalizedTimeframe(result.timeframe) === "1D" || normalizedTimeframe(result.timeframe) === "1W") && (
                                                            <Tooltip title="Historical Evidence">
                                                                <IconButton
                                                                    size="small"
                                                                    aria-label={`View ${result.symbol} historical evidence`}
                                                                    onClick={(event) => {
                                                                        event.stopPropagation();
                                                                        const query = new URLSearchParams({
                                                                            timeframe: normalizedTimeframe(result.timeframe),
                                                                            zone_type: result.zone_type,
                                                                            pattern: patternLabels[result.pattern_type ?? ""] ?? result.pattern_type ?? "",
                                                                            zone_quality: result.zone_quality_label ?? "",
                                                                            trade_confidence: result.trade_confidence?.label ?? "",
                                                                        });
                                                                        navigate(`/historical-evidence?${query.toString()}`);
                                                                    }}
                                                                    sx={{ width: 30, height: 30, color: "#66758b", "&:hover": { bgcolor: "#EEF4FF", color: "#344054" } }}
                                                                >
                                                                    <QueryStatsRoundedIcon sx={{ fontSize: 17 }} />
                                                                </IconButton>
                                                            </Tooltip>
                                                        )}
                                                        <IconButton
                                                            size="small"
                                                            aria-label={`Open ${result.symbol} full-screen chart`}
                                                            onClick={(event) => {
                                                                event.stopPropagation();
                                                                openStock(zones, result);
                                                            }}
                                                            sx={{ width: 30, height: 30, color: "#66758b", transition: "background-color 150ms ease, color 150ms ease", "&:hover": { bgcolor: "#EEF4FF", color: "#344054" } }}
                                                        >
                                                            <VisibilityOutlinedIcon sx={{ fontSize: 17 }} />
                                                        </IconButton>
                                                    </Stack>
                                                </TableCell>
                                            </TableRow>
                                    );
                                })}
                            </TableBody>
                        </Table>
                    </TableContainer>
                )}
                {groupedResults.length > 0 && (() => {
                    const pageCount = Math.ceil(groupedResults.length / 14);
                    const pageButton = (value: number) => <Button key={value} size="small" variant={safePage === value - 1 ? "contained" : "outlined"} onClick={() => setPage(value - 1)} sx={{ minWidth: 34, width: 34, height: 34, p: 0, borderColor: safePage === value - 1 ? "primary.main" : "#dbe1e9", color: safePage === value - 1 ? "#fff" : "text.secondary" }}>{value}</Button>;
                    return <Stack direction="row" sx={{ px: 1.25, py: 1.5, alignItems: "center", borderTop: "1px solid", borderColor: "divider" }}>
                        <Typography color="text.secondary" sx={{ fontSize: ".66rem" }}>Showing {safePage * 14 + 1} to {Math.min((safePage + 1) * 14, groupedResults.length)} of {groupedResults.length} results</Typography>
                        <Stack direction="row" spacing={0.75} sx={{ ml: "auto", alignItems: "center" }}>
                            {pageButton(1)}{pageCount > 1 && pageButton(2)}{pageCount > 2 && pageButton(3)}{pageCount > 4 && <Typography color="text.secondary">…</Typography>}{pageCount > 3 && pageButton(pageCount)}
                            <Button size="small" variant="outlined" disabled={safePage >= pageCount - 1} onClick={() => setPage((current) => current + 1)} sx={{ minWidth: 34, width: 34, height: 34, p: 0 }}><ChevronRightRoundedIcon fontSize="small" /></Button>
                        </Stack>
                    </Stack>;
                })()}
            </CardContent>
            <Dialog fullScreen open={selectedZones.length > 0} onClose={closeStock}>
                {selectedZones.length > 0 && (() => {
                    const selectedZone = selectZoneById(selectedZones, selectedZoneId);
                    if (!selectedZone) return null;
                    const selectedCanonical = selectedZone.trade_confidence;
                    const selectedConfidence = tradeConfidenceDisplay(selectedCanonical);
                    const selectedQuality = qualityPresentation(selectedZone.zone_score);
                    const selectedStatus = statusPresentation(selectedZone.status);
                    return <>
                    <DialogTitle sx={{ py: 1.25, borderBottom: "1px solid", borderColor: "divider" }}>
                        <Box sx={{ display: "flex", alignItems: "center", gap: 1.25 }}>
                            <FullscreenRoundedIcon color="primary" />
                            <Box>
                                <Typography variant="h6">{selectedZone.symbol} · Selected Zone {selectedZoneId} · {selectedZone.zone_type} · {patternLabels[selectedZone.pattern_type ?? ""]}</Typography>
                                <Typography variant="caption" color="text.secondary">{selectedZone.timeframe} research chart · Trade Confidence {selectedConfidence.score} · Zone Quality {formatZoneQuality(selectedZone.zone_score)} · delayed data · no order execution</Typography>
                            </Box>
                            <Stack direction="row" spacing={.75} sx={{ ml: "auto", alignItems: "center" }}>
                                <Chip size="small" variant="outlined" label={`TC ${selectedConfidence.score} · ${selectedConfidence.label}`} />
                                <Chip size="small" label={`Zone Quality ${formatZoneQuality(selectedZone.zone_score)} · ${formatZoneQualityLabel(selectedZone.zone_quality_label ?? selectedQuality.label)}`} sx={{ color: selectedQuality.color, bgcolor: selectedQuality.background, border: "1px solid", borderColor: selectedQuality.border, fontWeight: 700 }} />
                                <Chip size="small" label={selectedZone.status === "WATCH" ? "NEARBY" : selectedZone.status} sx={{ color: selectedStatus.color, bgcolor: selectedStatus.background, border: "1px solid", borderColor: selectedStatus.border, fontWeight: 700 }} />
                            </Stack>
                            {import.meta.env.DEV && (
                                <>
                                    <IconButton aria-label="Open developer settings" onClick={(event) => setDeveloperMenuAnchor(event.currentTarget)}>
                                        <BugReportOutlinedIcon />
                                    </IconButton>
                                    <Menu anchorEl={developerMenuAnchor} open={Boolean(developerMenuAnchor)} onClose={() => setDeveloperMenuAnchor(null)}>
                                        <MenuItem onClick={() => {
                                            const next = !developerMode;
                                            setDeveloperMode(next);
                                            if (!next) {
                                                setDeveloperDiagnostics(null);
                                                setDeveloperDiagnosticsError("");
                                            }
                                        }}>
                                            <Switch size="small" checked={developerMode} />
                                            Developer Mode
                                        </MenuItem>
                                    </Menu>
                                </>
                            )}
                            <IconButton aria-label="Close full-screen chart" onClick={closeStock}><CloseRoundedIcon /></IconButton>
                        </Box>
                    </DialogTitle>
                    <DialogContent sx={{ position: "relative", p: 1.5, bgcolor: "#f4f6f9", overflow: "hidden" }}>
                        <Box sx={{ display: "flex", width: "100%", height: "100%", gap: { xs: 0, lg: analysisPanelOpen ? 1.5 : 0 } }}>
                            <Box sx={{ flex: "1 1 auto", minWidth: 0, transition: "width 200ms ease" }}>
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
                                    developerZones={developerMode ? developerChartZones : undefined}
                                    analysisPanelOpen={analysisPanelOpen}
                                    onToggleAnalysisPanel={toggleAnalysisPanel}
                                />
                            </Box>
                            <Box
                                aria-hidden={!analysisPanelOpen}
                                sx={{
                                    position: { xs: "absolute", lg: "relative" },
                                    top: { xs: 12, lg: "auto" },
                                    right: { xs: 12, lg: "auto" },
                                    bottom: { xs: 12, lg: "auto" },
                                    zIndex: { xs: 20, lg: "auto" },
                                    width: { xs: "min(88vw, 360px)", lg: analysisPanelOpen ? 350 : 0 },
                                    maxWidth: "100%",
                                    overflow: "hidden",
                                    opacity: analysisPanelOpen ? 1 : 0,
                                    pointerEvents: analysisPanelOpen ? "auto" : "none",
                                    transform: { xs: analysisPanelOpen ? "translateX(0)" : "translateX(calc(100% + 24px))", lg: "none" },
                                    transition: "width 200ms ease, opacity 200ms ease, transform 200ms ease",
                                    bgcolor: "#f4f6f9",
                                    boxShadow: { xs: analysisPanelOpen ? "-8px 0 24px rgba(15,23,42,.12)" : "none", lg: "none" },
                                }}
                            >
                                <Box sx={{ width: { xs: "min(88vw, 360px)", lg: 350 }, maxWidth: "100%", maxHeight: "calc(100vh - 100px)", overflowY: "auto" }}>
                                    {developerMode && (
                                        <>
                                            {developerDiagnosticsError && (
                                                <Typography color="error.light" sx={{ mb: 1 }}>
                                                    {developerDiagnosticsError}
                                                </Typography>
                                            )}
                                            <DeveloperZoneInspector
                                                zones={developerChartZones}
                                                unformedCandidates={developerDiagnostics?.candidates.filter((candidate) => candidate.zone_type === null)}
                                            />
                                        </>
                                    )}
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
                                                        <Chip size="small" label={`TC ${tradeConfidenceDisplay(zone.trade_confidence).score} · ZQ ${formatZoneQuality(zone.zone_score)}`} />
                                                    </Stack>
                                                    <Typography variant="caption" color="text.secondary">Status {zone.status} · Base {zone.base_date}{selected ? " · Selected" : " · Click to analyze"}</Typography>
                                                    {zone.status === "REACTING" && (
                                                        <Stack direction="row" spacing={1.5} sx={{ mt: .6 }}>
                                                            <Typography variant="caption" sx={{ color: "#4338CA", fontWeight: 700 }}>REACTING</Typography>
                                                            <Typography variant="caption">Reaction {zone.reaction_percent !== null && zone.reaction_percent !== undefined ? `${zone.reaction_percent >= 0 ? "+" : ""}${zone.reaction_percent.toFixed(2)}%` : "Calculating"}</Typography>
                                                            <Typography variant="caption">Started {zone.reaction_duration_candles ? `${zone.reaction_duration_candles} candles ago` : zone.reaction_started ?? "recently"}</Typography>
                                                        </Stack>
                                                    )}
                                                </Box>;
                                            })}
                                        </Stack>
                                    </CardContent></Card>
                                    <ZoneExplanationPanel
                                        result={selectedZone}
                                        zones={selectedZones}
                                        methodologyVersion={methodologyVersion}
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
                            </Box>
                        </Box>
                    </DialogContent>
                </>; })()}
            </Dialog>
        </Card>
    );
}

export default ScannerResultsTable;
