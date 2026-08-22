import BarChartOutlinedIcon from "@mui/icons-material/BarChartOutlined";
import InfoOutlinedIcon from "@mui/icons-material/InfoOutlined";
import RestartAltRoundedIcon from "@mui/icons-material/RestartAltRounded";
import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Chip from "@mui/material/Chip";
import FormControl from "@mui/material/FormControl";
import Grid from "@mui/material/Grid";
import InputLabel from "@mui/material/InputLabel";
import MenuItem from "@mui/material/MenuItem";
import Pagination from "@mui/material/Pagination";
import Select from "@mui/material/Select";
import Skeleton from "@mui/material/Skeleton";
import Stack from "@mui/material/Stack";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import TextField from "@mui/material/TextField";
import Tooltip from "@mui/material/Tooltip";
import Typography from "@mui/material/Typography";
import { useCallback, useEffect, useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";

import {
    getHistoricalEvidenceMetadata,
    getHistoricalEvidenceSummary,
    getHistoricalEvidenceZones,
    historicalEvidenceErrorMessage,
} from "../api/historicalEvidenceApi";
import {
    DEFAULT_EVIDENCE_FILTERS,
    metricText,
    readFilters,
    reliabilityLabel,
    TRADE_CONFIDENCE_LABELS,
    writeFilters,
    ZONE_QUALITY_LABELS,
} from "../historical-evidence/historicalEvidenceViewModel";
import type {
    HistoricalEvidenceFilters,
    HistoricalEvidenceMetadata,
    HistoricalEvidenceSummary,
    HistoricalEvidenceZonesPage,
} from "../types/historicalEvidence";
import { HISTORICAL_EVIDENCE_VERSION } from "../types/historicalEvidence";

const PAGE_SIZE = 25;
const SORT_OPTIONS = [
    ["formation_timestamp", "Newest formation"], ["symbol", "Symbol"],
    ["zone_quality", "Zone Quality"], ["trade_confidence", "Trade Confidence"],
    ["mfe_zone_width", "Reaction depth"],
] as const;

function FilterSelect({ label, value, options, onChange }: { label: string; value: string; options: Array<[string, string]>; onChange: (value: string) => void }) {
    return <FormControl size="small" sx={{ minWidth: 138, flex: "1 1 138px" }}>
        <InputLabel>{label}</InputLabel>
        <Select label={label} value={value} onChange={(event) => onChange(event.target.value)}>
            {options.map(([optionValue, optionLabel]) => <MenuItem key={optionValue || "all"} value={optionValue}>{optionLabel}</MenuItem>)}
        </Select>
    </FormControl>;
}

function MetricCard({ label, metric, note }: { label: string; metric: { numerator: number; denominator: number; percent: number | null }; note: string }) {
    return <Card><CardContent>
        <Stack direction="row" spacing={0.6} sx={{ alignItems: "center" }}><Typography color="text.secondary" sx={{ fontWeight: 600 }}>{label}</Typography><Tooltip title={note}><InfoOutlinedIcon sx={{ fontSize: 15, color: "text.secondary" }} /></Tooltip></Stack>
        <Typography sx={{ mt: 0.5, fontSize: "1.35rem", fontWeight: 750 }}>{metricText(metric)}</Typography>
        <Typography color="text.secondary" sx={{ mt: 0.2, fontSize: ".66rem" }}>{metric.numerator.toLocaleString()} of {metric.denominator.toLocaleString()}</Typography>
    </CardContent></Card>;
}

function ReactionDepthChart({ summary }: { summary: HistoricalEvidenceSummary }) {
    const values = [
        ["1 zone width", summary.reaction_1_zone_width], ["2 zone widths", summary.reaction_2_zone_width],
        ["3 zone widths", summary.reaction_3_zone_width], ["5 zone widths", summary.reaction_5_zone_width],
    ] as const;
    return <Card><CardContent>
        <Stack direction="row" spacing={0.8} sx={{ alignItems: "center" }}><BarChartOutlinedIcon color="primary" /><Typography variant="h6">Favorable reaction depth</Typography></Stack>
        <Typography color="text.secondary" sx={{ mt: 0.35 }}>How far price moved in the expected direction after interacting with a zone, measured in zone widths.</Typography>
        <Stack spacing={1.15} sx={{ mt: 2 }}>{values.map(([label, metric]) => <Box key={label}>
            <Stack direction="row" sx={{ justifyContent: "space-between" }}><Typography sx={{ fontWeight: 600 }}>{label}</Typography><Typography>{metricText(metric)} <Box component="span" sx={{ color: "text.secondary", fontSize: ".65rem" }}>({metric.numerator.toLocaleString()} / {metric.denominator.toLocaleString()})</Box></Typography></Stack>
            <Box sx={{ mt: .5, height: 8, borderRadius: 99, bgcolor: "#EEF1F6", overflow: "hidden" }}><Box sx={{ width: `${metric.percent ?? 0}%`, height: "100%", bgcolor: "primary.main", borderRadius: 99 }} /></Box>
        </Box>)}</Stack>
    </CardContent></Card>;
}

export default function HistoricalEvidence() {
    const [searchParams, setSearchParams] = useSearchParams();
    const [filters, setFilters] = useState(() => readFilters(searchParams));
    const [metadata, setMetadata] = useState<HistoricalEvidenceMetadata | null>(null);
    const [summary, setSummary] = useState<HistoricalEvidenceSummary | null>(null);
    const [zones, setZones] = useState<HistoricalEvidenceZonesPage | null>(null);
    const [page, setPage] = useState(Number(searchParams.get("page")) || 1);
    const [sortBy, setSortBy] = useState(searchParams.get("sort_by") ?? "formation_timestamp");
    const [sortDirection, setSortDirection] = useState<"asc" | "desc">(searchParams.get("sort_direction") === "asc" ? "asc" : "desc");
    const [loading, setLoading] = useState(true);
    const [metadataLoading, setMetadataLoading] = useState(true);
    const [error, setError] = useState("");

    const updateFilter = useCallback((key: keyof HistoricalEvidenceFilters, value: string) => {
        setFilters((current) => ({ ...current, [key]: value }));
        setPage(1);
        setLoading(true);
        setError("");
    }, []);

    useEffect(() => {
        let active = true;
        getHistoricalEvidenceMetadata().then((value) => { if (active) setMetadata(value); }).catch((reason) => { if (active) setError(historicalEvidenceErrorMessage(reason)); }).finally(() => { if (active) setMetadataLoading(false); });
        return () => { active = false; };
    }, []);

    useEffect(() => {
        const nextParams = writeFilters(filters);
        if (page > 1) nextParams.set("page", String(page));
        if (sortBy !== "formation_timestamp") nextParams.set("sort_by", sortBy);
        if (sortDirection !== "desc") nextParams.set("sort_direction", sortDirection);
        setSearchParams(nextParams, { replace: true });
        let active = true;
        Promise.all([
            getHistoricalEvidenceSummary(filters),
            getHistoricalEvidenceZones(filters, page, PAGE_SIZE, sortBy, sortDirection),
        ]).then(([summaryValue, zonesValue]) => {
            if (!active) return;
            setSummary(summaryValue);
            setZones(zonesValue);
        }).catch((reason) => { if (active) setError(historicalEvidenceErrorMessage(reason)); }).finally(() => { if (active) setLoading(false); });
        return () => { active = false; };
    }, [filters, page, setSearchParams, sortBy, sortDirection]);

    const versionMismatch = useMemo(() => [metadata?.historical_evidence_version, summary?.historical_evidence_version, zones?.historical_evidence_version].filter(Boolean).some((version) => version !== HISTORICAL_EVIDENCE_VERSION), [metadata, summary, zones]);
    const veryHighEmpty = filters.tradeConfidence === "VERY_HIGH" && !loading && summary?.historical_zones === 0;

    return <Stack spacing={1.5} sx={{ maxWidth: 1680, mx: "auto" }}>
        <Stack direction={{ xs: "column", md: "row" }} sx={{ justifyContent: "space-between", gap: 1 }}>
            <Box><Typography variant="h4">Historical Evidence</Typography><Typography color="text.secondary">Explore the frozen Milestone 9C research baseline without changing current scanner results.</Typography></Box>
            <Stack direction="row" spacing={1} sx={{ alignItems: "center" }}><Chip label="Research baseline" variant="outlined" color="primary" /><Chip label={HISTORICAL_EVIDENCE_VERSION} /></Stack>
        </Stack>

        <Card><CardContent><Grid container spacing={1.5} sx={{ alignItems: "center" }}>
            {[['Dataset', 'Milestone 9C Research Baseline'], ['Period', metadata ? `${metadata.dataset_period.start} to ${metadata.dataset_period.end}` : 'Loading...'], ['Coverage', 'Current NSE 500 constituent historical replay'], ['Zones', metadata ? metadata.record_count.toLocaleString() : '...'], ['Timeframes', 'Daily and Weekly']].map(([label, value]) => <Grid key={label} size={{ xs: 12, sm: 6, lg: 2.4 }}><Typography color="text.secondary" sx={{ fontSize: ".64rem", textTransform: "uppercase", letterSpacing: ".06em" }}>{label}</Typography><Typography sx={{ mt: .25, fontWeight: 650 }}>{value}</Typography></Grid>)}
        </Grid></CardContent></Card>

        {versionMismatch && <Alert severity="error">Dataset version mismatch. This page requires {HISTORICAL_EVIDENCE_VERSION}; displayed results have been stopped.</Alert>}
        {error && <Alert severity="error">{error}</Alert>}

        <Card><CardContent><Stack direction="row" useFlexGap sx={{ flexWrap: "wrap", gap: 1, alignItems: "center" }}>
            <FilterSelect label="Timeframe" value={filters.timeframe} options={[["", "All"], ["1D", "Daily"], ["1W", "Weekly"]]} onChange={(value) => updateFilter("timeframe", value)} />
            <FilterSelect label="Zone type" value={filters.zoneType} options={[["", "All"], ["DEMAND", "Demand"], ["SUPPLY", "Supply"]]} onChange={(value) => updateFilter("zoneType", value)} />
            <FilterSelect label="Pattern" value={filters.pattern} options={[["", "All"], ...["DBR", "RBR", "RBD", "DBD"].map((value) => [value, value] as [string, string])]} onChange={(value) => updateFilter("pattern", value)} />
            <FilterSelect label="Zone Quality" value={filters.zoneQuality} options={[["", "All"], ...ZONE_QUALITY_LABELS.map((value) => [value, value] as [string, string])]} onChange={(value) => updateFilter("zoneQuality", value)} />
            <FilterSelect label="Trade Confidence" value={filters.tradeConfidence} options={[["", "All"], ...TRADE_CONFIDENCE_LABELS.map((value) => [value, value.replaceAll("_", " ")] as [string, string])]} onChange={(value) => updateFilter("tradeConfidence", value)} />
            <FilterSelect label="Year" value={filters.year} options={[["", "All"], ...[2021, 2022, 2023, 2024, 2025, 2026].map((value) => [String(value), String(value)] as [string, string])]} onChange={(value) => updateFilter("year", value)} />
            <FilterSelect label="Interaction" value={filters.interactionStatus} options={[["ALL", "All"], ["INTERACTED", "Interacted"], ["NOT_INTERACTED", "Not interacted"]]} onChange={(value) => updateFilter("interactionStatus", value)} />
            <TextField size="small" label="Symbol" value={filters.symbol} onChange={(event) => updateFilter("symbol", event.target.value.toUpperCase())} sx={{ minWidth: 140, flex: "1 1 140px" }} />
            <Button startIcon={<RestartAltRoundedIcon />} onClick={() => { setLoading(true); setError(""); setFilters(DEFAULT_EVIDENCE_FILTERS); setPage(1); }}>Reset</Button>
        </Stack></CardContent></Card>

        {(metadataLoading || (loading && !summary)) ? <Grid container spacing={1.2}>{Array.from({ length: 4 }).map((_, index) => <Grid key={index} size={{ xs: 12, sm: 6, lg: 3 }}><Skeleton variant="rounded" height={104} /></Grid>)}</Grid> : summary && !versionMismatch && <>
            <Grid container spacing={1.2}>
                <Grid size={{ xs: 12, sm: 6, lg: 3 }}><Card><CardContent><Typography color="text.secondary">Historical zones</Typography><Typography sx={{ mt: .5, fontSize: "1.35rem", fontWeight: 750 }}>{summary.historical_zones.toLocaleString()}</Typography><Typography color="text.secondary" sx={{ fontSize: ".66rem" }}>Matching the selected cohort</Typography></CardContent></Card></Grid>
                <Grid size={{ xs: 12, sm: 6, lg: 3 }}><MetricCard label="Zones with interaction" metric={summary.interaction_rate} note="The denominator is every historical zone in the selected cohort." /></Grid>
                <Grid size={{ xs: 12, sm: 6, lg: 3 }}><MetricCard label="Structural survival" metric={summary.structural_survival} note="The denominator is interacted zones only." /></Grid>
                <Grid size={{ xs: 12, sm: 6, lg: 3 }}><MetricCard label="Structural target available" metric={summary.structural_target_availability} note="The denominator is interacted zones only." /></Grid>
                <Grid size={{ xs: 12, sm: 6, lg: 3 }}><MetricCard label="Structural target reached" metric={summary.structural_target_achievement} note="The denominator is interacted zones with an available structural target." /></Grid>
                <Grid size={{ xs: 12, sm: 6, lg: 3 }}><Card><CardContent><Typography color="text.secondary">Median favorable movement</Typography><Typography sx={{ mt: .5, fontSize: "1.35rem", fontWeight: 750 }}>{summary.median_mfe_zone_width === null ? "Unavailable" : `${summary.median_mfe_zone_width.toFixed(2)} ZW`}</Typography><Typography color="text.secondary" sx={{ fontSize: ".66rem" }}>Interacted zones with recorded movement</Typography></CardContent></Card></Grid>
                <Grid size={{ xs: 12, sm: 6, lg: 3 }}><Card><CardContent><Typography color="text.secondary">Median adverse movement</Typography><Typography sx={{ mt: .5, fontSize: "1.35rem", fontWeight: 750 }}>{summary.median_mae_zone_width === null ? "Unavailable" : `${summary.median_mae_zone_width.toFixed(2)} ZW`}</Typography><Typography color="text.secondary" sx={{ fontSize: ".66rem" }}>Interacted zones with recorded movement</Typography></CardContent></Card></Grid>
            </Grid>
            <Grid container spacing={1.2}><Grid size={{ xs: 12, lg: 8 }}><ReactionDepthChart summary={summary} /></Grid><Grid size={{ xs: 12, lg: 4 }}><Card sx={{ height: "100%" }}><CardContent><Typography variant="h6">Evidence reliability</Typography><Chip sx={{ mt: 1 }} label={reliabilityLabel(summary.reliability)} color={summary.interacted_zones >= 300 ? "success" : "warning"} variant="outlined" /><Typography sx={{ mt: 1.2, fontWeight: 650 }}>{summary.interacted_zones.toLocaleString()} interacted zones</Typography><Typography color="text.secondary" sx={{ mt: .5 }}>Reliability reflects the amount of evidence in this filtered cohort. It does not describe a future outcome.</Typography><Typography color="text.secondary" sx={{ mt: 1 }}>Historical reactions are research observations, not a trading probability, promise, or guarantee.</Typography></CardContent></Card></Grid></Grid>
        </>}

        {veryHighEmpty && <Alert severity="info">No VERY HIGH observations exist in the frozen Milestone 9C baseline. AlphaEdge does not substitute another Trade Confidence group.</Alert>}

        <Card><CardContent sx={{ p: 0, "&:last-child": { pb: 0 } }}>
            <Stack direction={{ xs: "column", sm: "row" }} sx={{ justifyContent: "space-between", gap: 1, px: 2, py: 1.5, borderBottom: "1px solid", borderColor: "divider" }}><Box><Typography variant="h6">Historical zones</Typography><Typography color="text.secondary">Server-filtered and deterministically paginated.</Typography></Box><Stack direction="row" spacing={1}><FilterSelect label="Sort" value={sortBy} options={SORT_OPTIONS.map(([value, label]) => [value, label])} onChange={(value) => { setLoading(true); setSortBy(value); setPage(1); }} /><FilterSelect label="Direction" value={sortDirection} options={[["desc", "Descending"], ["asc", "Ascending"]]} onChange={(value) => { setLoading(true); setSortDirection(value as "asc" | "desc"); setPage(1); }} /></Stack></Stack>
            <TableContainer sx={{ minHeight: 430 }}><Table size="small" sx={{ minWidth: 1120 }}><TableHead><TableRow>{["Symbol", "Formed", "Type", "Pattern", "Timeframe", "Zone range", "Zone Quality", "Trade Confidence", "Interaction", "Reaction depth"].map((heading) => <TableCell key={heading} sx={{ bgcolor: "#F8FAFC", color: "text.secondary", fontWeight: 600 }}>{heading}</TableCell>)}</TableRow></TableHead><TableBody>
                {loading ? Array.from({ length: 8 }).map((_, index) => <TableRow key={index}>{Array.from({ length: 10 }).map((__, cell) => <TableCell key={cell}><Skeleton width={cell === 0 ? 70 : "80%"} /></TableCell>)}</TableRow>) : zones?.items.map((zone) => <TableRow key={zone.zone_id} hover>
                    <TableCell sx={{ fontWeight: 700 }}>{zone.symbol}</TableCell><TableCell>{new Date(zone.planning_timestamp).toLocaleDateString("en-IN")}</TableCell><TableCell><Chip size="small" label={zone.zone_type} color={zone.zone_type === "DEMAND" ? "success" : "error"} variant="outlined" /></TableCell><TableCell>{zone.pattern}</TableCell><TableCell>{zone.timeframe === "1D" ? "Daily" : "Weekly"}</TableCell><TableCell>{"\u20B9"}{zone.zone_low.toLocaleString("en-IN")} - {"\u20B9"}{zone.zone_high.toLocaleString("en-IN")}</TableCell><TableCell>{zone.zone_quality_score?.toFixed(1) ?? "-"}<Typography component="span" color="text.secondary" sx={{ ml: .5, fontSize: ".62rem" }}>{zone.zone_quality_label ?? ""}</Typography></TableCell><TableCell>{zone.trade_confidence_score?.toFixed(1) ?? "-"}<Typography component="span" color="text.secondary" sx={{ ml: .5, fontSize: ".62rem" }}>{zone.trade_confidence_label?.replaceAll("_", " ") ?? ""}</Typography></TableCell><TableCell>{zone.interacted ? "Interacted" : "Not interacted"}</TableCell><TableCell>{zone.mfe_zone_width === null ? "Unavailable" : `${zone.mfe_zone_width.toFixed(2)} ZW`}</TableCell>
                </TableRow>)}
                {!loading && zones?.items.length === 0 && <TableRow><TableCell colSpan={10} align="center" sx={{ py: 8 }}><Typography sx={{ fontWeight: 650 }}>No historical zones match these filters.</Typography><Typography color="text.secondary" sx={{ mt: .5 }}>Try a broader cohort. The frozen evidence is never estimated or replaced.</Typography></TableCell></TableRow>}
            </TableBody></Table></TableContainer>
            <Stack direction={{ xs: "column", sm: "row" }} sx={{ justifyContent: "space-between", alignItems: "center", gap: 1, px: 2, py: 1.4, borderTop: "1px solid", borderColor: "divider" }}><Typography color="text.secondary">{zones ? `${zones.total.toLocaleString()} zones - Page ${zones.page} of ${zones.total_pages || 1}` : "Loading zones..."}</Typography><Pagination page={page} count={Math.max(zones?.total_pages ?? 1, 1)} onChange={(_, value) => { setLoading(true); setPage(value); }} color="primary" size="small" disabled={loading} /></Stack>
        </CardContent></Card>

        <Alert severity="info" icon={<InfoOutlinedIcon />}>This page presents frozen historical research evidence. It does not use current market data, alter scanner ranking, or predict what will happen next. Daily and Weekly evidence is available; 15-minute, 75-minute, and 125-minute evidence is not part of this baseline.</Alert>
    </Stack>;
}
