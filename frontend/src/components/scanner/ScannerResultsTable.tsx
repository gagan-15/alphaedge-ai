import KeyboardArrowRightRoundedIcon from "@mui/icons-material/KeyboardArrowRightRounded";
import CloseRoundedIcon from "@mui/icons-material/CloseRounded";
import FullscreenRoundedIcon from "@mui/icons-material/FullscreenRounded";
import Box from "@mui/material/Box";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Chip from "@mui/material/Chip";
import Dialog from "@mui/material/Dialog";
import DialogContent from "@mui/material/DialogContent";
import DialogTitle from "@mui/material/DialogTitle";
import Grid from "@mui/material/Grid";
import IconButton from "@mui/material/IconButton";
import Stack from "@mui/material/Stack";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import TableSortLabel from "@mui/material/TableSortLabel";
import Typography from "@mui/material/Typography";
import { useMemo, useState } from "react";

import type { ZoneResearchResult } from "../../types/scanner";
import ZoneDetailChart from "./ZoneDetailChart";
import ZoneExplanationPanel from "./ZoneExplanationPanel";

interface ScannerResultsTableProps {
    results: ZoneResearchResult[];
}

const patternLabels: Record<string, string> = {
    DROP_BASE_RALLY: "DBR",
    RALLY_BASE_RALLY: "RBR",
    RALLY_BASE_DROP: "RBD",
    DROP_BASE_DROP: "DBD",
};

function valueOrDash(value: number | null, digits = 2) {
    return value === null ? "—" : value.toLocaleString("en-IN", { maximumFractionDigits: digits });
}

function qualityLabel(score: number) {
    if (score >= 90) return "Elite";
    if (score >= 75) return "Strong";
    if (score >= 60) return "Moderate";
    if (score >= 40) return "Weak";
    return "Rejected";
}

function ScannerResultsTable({ results }: ScannerResultsTableProps) {
    const [sortField, setSortField] = useState<"symbol" | "zone_score" | "distance_percent">("zone_score");
    const [sortDirection, setSortDirection] = useState<"asc" | "desc">("desc");
    const [selectedZones, setSelectedZones] = useState<ZoneResearchResult[]>([]);

    const sortedResults = useMemo(() => [...results].sort((left, right) => {
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
            primary: [...zones].sort((left, right) =>
                left.distance_percent - right.distance_percent
                || right.zone_score - left.zone_score
            )[0],
        }));
    }, [sortedResults]);

    function chooseSort(field: typeof sortField) {
        if (field === sortField) {
            setSortDirection((current) => current === "asc" ? "desc" : "asc");
        } else {
            setSortField(field);
            setSortDirection("desc");
        }
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
                        <Table size="small" sx={{ minWidth: 1080 }}>
                            <TableHead>
                                <TableRow>
                                    <TableCell width={34} />
                                    <TableCell>{sortableLabel("symbol", "Symbol")}</TableCell>
                                    <TableCell>Type</TableCell>
                                    <TableCell>Pattern</TableCell>
                                    <TableCell>Status</TableCell>
                                    <TableCell align="right">Proximal</TableCell>
                                    <TableCell align="right">Distal</TableCell>
                                    <TableCell align="right">Distance</TableCell>
                                    <TableCell align="right">{sortableLabel("zone_score", "Quality")}</TableCell>
                                    <TableCell align="right">LTP / Entry</TableCell>
                                    <TableCell>Base date</TableCell>
                                    <TableCell>Timeframe</TableCell>
                                </TableRow>
                            </TableHead>
                            <TableBody>
                                {groupedResults.map(({ symbol, zones, primary: result }) => {
                                    const zoneKey = `${result.symbol}-${result.zone_type}-${result.base_date}-${result.proximal_price}`;
                                    const status = result.status;
                                    return (
                                            <TableRow key={zoneKey} hover onClick={() => setSelectedZones(zones)} sx={{ cursor: "pointer" }}>
                                                <TableCell>
                                                    <IconButton size="small" aria-label={`Open ${result.symbol} full-screen chart`}>
                                                        <KeyboardArrowRightRoundedIcon />
                                                    </IconButton>
                                                </TableCell>
                                                <TableCell sx={{ fontWeight: 850 }}>
                                                    <Stack direction="row" spacing={.75} sx={{ alignItems: "center" }}>
                                                        <span>{symbol}</span><Chip size="small" label={`${zones.length} zone${zones.length === 1 ? "" : "s"}`} />
                                                    </Stack>
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
                                                <TableCell align="right">{valueOrDash(result.proximal_price)}</TableCell>
                                                <TableCell align="right">{valueOrDash(result.distal_price)}</TableCell>
                                                <TableCell align="right" sx={{ color: (result.distance_percent ?? 99) <= 3 ? "success.main" : "text.secondary" }}>
                                                    {result.distance_percent === null ? "—" : `${result.distance_percent.toFixed(2)}%`}
                                                </TableCell>
                                                <TableCell align="right">
                                                    <Box sx={{ display: "inline-flex", gap: .7, alignItems: "center" }}>
                                                        <Box>
                                                            <Typography sx={{ fontWeight: 850 }}>{result.zone_score.toFixed(0)}</Typography>
                                                            <Typography variant="caption" color="text.secondary">
                                                                {qualityLabel(result.zone_score)}
                                                            </Typography>
                                                        </Box>
                                                        <Box sx={{ width: 36, height: 5, bgcolor: "rgba(143,161,184,.14)", borderRadius: 9, overflow: "hidden" }}>
                                                            <Box sx={{ width: `${Math.min(100, result.zone_score)}%`, height: "100%", bgcolor: result.zone_score >= 75 ? "success.main" : "warning.main" }} />
                                                        </Box>
                                                    </Box>
                                                </TableCell>
                                                <TableCell align="right" sx={{ fontWeight: 800 }}>{result.current_price.toLocaleString("en-IN", { maximumFractionDigits: 2 })}</TableCell>
                                                <TableCell>{result.base_date}</TableCell>
                                                <TableCell>{result.timeframe?.toUpperCase() ?? "1D"}</TableCell>
                                            </TableRow>
                                    );
                                })}
                            </TableBody>
                        </Table>
                    </TableContainer>
                )}
            </CardContent>
            <Dialog fullScreen open={selectedZones.length > 0} onClose={() => setSelectedZones([])}>
                {selectedZones.length > 0 && (() => {
                    const selectedZone = selectedZones[0];
                    return <>
                    <DialogTitle sx={{ py: 1.25, borderBottom: "1px solid", borderColor: "divider" }}>
                        <Box sx={{ display: "flex", alignItems: "center", gap: 1.25 }}>
                            <FullscreenRoundedIcon color="primary" />
                            <Box>
                                <Typography variant="h6">{selectedZone.symbol} · {selectedZone.zone_type} · {patternLabels[selectedZone.pattern_type ?? ""]}</Typography>
                                <Typography variant="caption" color="text.secondary">{selectedZone.timeframe} research chart · delayed data · no order execution</Typography>
                            </Box>
                            <Chip sx={{ ml: "auto" }} color={selectedZone.zone_type === "DEMAND" ? "primary" : "error"} label={`${selectedZone.zone_score.toFixed(0)} · ${qualityLabel(selectedZone.zone_score)}`} />
                            <IconButton aria-label="Close full-screen chart" onClick={() => setSelectedZones([])}><CloseRoundedIcon /></IconButton>
                        </Box>
                    </DialogTitle>
                    <DialogContent sx={{ p: 1.5, bgcolor: "#050d18" }}>
                        <Grid container spacing={1.5}>
                            <Grid size={{ xs: 12, xl: 8.5 }}>
                                <ZoneDetailChart result={selectedZone} zones={selectedZones} height={680} showTools />
                            </Grid>
                            <Grid size={{ xs: 12, xl: 3.5 }}>
                                <Box sx={{ maxHeight: "calc(100vh - 100px)", overflowY: "auto" }}>
                                    <Card sx={{ mb: 1.25 }}><CardContent>
                                        <Typography variant="h6">All active zones</Typography>
                                        <Stack spacing={.75} sx={{ mt: 1 }}>
                                            {selectedZones.map((zone) => <Box key={`${zone.base_date}-${zone.proximal_price}`} sx={{ p: 1, border: "1px solid", borderColor: "divider", borderRadius: 1.5 }}>
                                                <Stack direction="row" sx={{ justifyContent: "space-between" }}><Typography sx={{ fontWeight: 800 }}>{zone.zone_type} · {patternLabels[zone.pattern_type ?? ""]}</Typography><Chip size="small" label={zone.zone_score.toFixed(0)} /></Stack>
                                                <Typography variant="caption" color="text.secondary">{zone.distal_price.toLocaleString("en-IN")} – {zone.proximal_price.toLocaleString("en-IN")} · {zone.status} · {zone.base_date}</Typography>
                                            </Box>)}
                                        </Stack>
                                    </CardContent></Card>
                                    <ZoneExplanationPanel result={selectedZone} />
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
