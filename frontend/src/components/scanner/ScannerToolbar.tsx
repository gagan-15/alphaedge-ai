import DownloadOutlinedIcon from "@mui/icons-material/DownloadOutlined";
import RefreshOutlinedIcon from "@mui/icons-material/RefreshOutlined";
import CloudSyncOutlinedIcon from "@mui/icons-material/CloudSyncOutlined";
import CancelOutlinedIcon from "@mui/icons-material/CancelOutlined";
import RestartAltRoundedIcon from "@mui/icons-material/RestartAltRounded";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import MenuItem from "@mui/material/MenuItem";
import Select from "@mui/material/Select";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import type { ReactNode } from "react";
import type { MarketUniverse } from "../../market-universe/MarketUniverseState";

export type ScannerQuickPreset = "fresh-demand" | "fresh-supply" | "near-entry" | "high-confidence" | "swing" | "intraday" | "todays-best" | "reset";
interface ScannerToolbarProps {
    isLoading: boolean; searchQuery: string; onRefresh: () => void; onUpdateData: () => void; onCancelUpdate: () => void; isUpdatingData: boolean; isCancellingUpdate: boolean; updateStage?: string; onSearchChange: (value: string) => void;
    minimumScore: number; approvalFilter: string; onMinimumScoreChange: (value: number) => void; onApprovalFilterChange: (value: string) => void;
    onExport: () => void; canExport: boolean; universe: MarketUniverse; universeOptions: Array<{ value: MarketUniverse; label: string }>;
    timeframe: string; onUniverseChange: (value: MarketUniverse) => void; onTimeframeChange: (value: string) => void;
    patternFilter: string; statusFilter: string; proximityFilter: number; onPatternFilterChange: (value: string) => void; onStatusFilterChange: (value: string) => void;
    onProximityFilterChange: (value: number) => void; onQuickPreset: (preset: ScannerQuickPreset) => void;
    actionableActive: boolean; actionableCount: number | null; onToggleActionable: () => void;
}
const selectSx = { width: "100%", height: 36, borderRadius: 1.25, bgcolor: "#ffffff", color: "#111827", fontSize: "0.72rem", "& .MuiSelect-select": { display: "flex", alignItems: "center", py: 0, pl: 1.5, pr: 4 }, "& .MuiSelect-icon": { right: 8, color: "#667085" }, "& .MuiOutlinedInput-notchedOutline": { borderColor: "#DFE5EE" }, "&:hover .MuiOutlinedInput-notchedOutline": { borderColor: "#c7d0dd" } };
function Filter({ label, children }: { label: string; children: ReactNode }) {
    return <Box sx={{ minWidth: 105, flex: "1 1 112px" }}><Typography sx={{ mb: 1, color: "text.secondary", fontSize: "0.64rem", lineHeight: 1, fontWeight: 500 }}>{label}</Typography>{children}</Box>;
}

export default function ScannerToolbar(props: ScannerToolbarProps) {
    return <Box sx={{ py: 1 }}>
        <Stack direction="row" useFlexGap sx={{ gap: 1, alignItems: "flex-end", flexWrap: "nowrap", overflowX: "auto", pb: .25 }}>
            <Filter label="Timeframe"><Select size="small" value={props.timeframe} onChange={(e) => props.onTimeframeChange(e.target.value)} sx={selectSx}><MenuItem value="MINUTE_15">15 minutes</MenuItem><MenuItem value="MINUTE_75">75 minutes</MenuItem><MenuItem value="MINUTE_125">125 minutes</MenuItem><MenuItem value="HOUR_1">1 hour</MenuItem><MenuItem value="DAILY">Daily</MenuItem><MenuItem value="WEEKLY">Weekly</MenuItem><MenuItem value="MONTHLY">Monthly</MenuItem><MenuItem value="QUARTERLY">Quarterly</MenuItem><MenuItem value="HALFYEARLY">Half-yearly</MenuItem><MenuItem value="YEARLY">Yearly</MenuItem></Select></Filter>
            <Filter label="Zone"><Select size="small" value={props.approvalFilter} onChange={(e) => props.onApprovalFilterChange(e.target.value)} sx={selectSx}><MenuItem value="all">All</MenuItem><MenuItem value="approved">Demand</MenuItem><MenuItem value="rejected">Supply</MenuItem></Select></Filter>
            <Filter label="Min Quality"><Select size="small" value={props.minimumScore} onChange={(e) => props.onMinimumScoreChange(Number(e.target.value))} sx={selectSx}><MenuItem value={0}>All</MenuItem><MenuItem value={40}>Weak & Above</MenuItem><MenuItem value={60}>60 & Above</MenuItem><MenuItem value={75}>75 & Above</MenuItem><MenuItem value={90}>90 & Above</MenuItem></Select></Filter>
            <Filter label="Status"><Select size="small" value={props.statusFilter} onChange={(e) => props.onStatusFilterChange(e.target.value)} sx={selectSx}><MenuItem value="all">All</MenuItem><MenuItem value="IN ZONE">In Zone</MenuItem><MenuItem value="REACTING">Reacting</MenuItem><MenuItem value="APPROACHING">Approaching</MenuItem><MenuItem value="FAR">Far</MenuItem></Select></Filter>
            <Filter label="Distance"><Select size="small" value={props.proximityFilter} onChange={(e) => props.onProximityFilterChange(Number(e.target.value))} sx={selectSx}><MenuItem value={100}>Any</MenuItem><MenuItem value={1}>Within 1%</MenuItem><MenuItem value={3}>Within 3%</MenuItem><MenuItem value={5}>Within 5%</MenuItem></Select></Filter>
            <Button size="small" variant={props.actionableActive ? "contained" : "outlined"} onClick={props.onToggleActionable} sx={{ height: 36, px: 1.5, borderRadius: 1.25, whiteSpace: "nowrap", fontWeight: 650, ...(props.actionableActive ? { bgcolor: "#4F46D8", "&:hover": { bgcolor: "#4338CA" } } : { borderColor: "#BFC7FF", color: "#4338CA" }) }}>{props.actionableActive ? `Actionable Zones (${props.actionableCount ?? "…"})` : "Actionable Zones"}</Button>
            <Filter label="Universe"><Select size="small" value={props.universe} onChange={(e) => props.onUniverseChange(e.target.value as MarketUniverse)} sx={selectSx}>{props.universeOptions.map((option) => <MenuItem key={option.value} value={option.value}>{option.label}</MenuItem>)}</Select></Filter>
            <Button size="small" onClick={() => props.onQuickPreset("reset")} startIcon={<RestartAltRoundedIcon sx={{ fontSize: 17 }} />} sx={{ height: 36, px: 1.5, gap: .25, borderRadius: 1.25, color: "text.primary", whiteSpace: "nowrap" }}>Reset</Button>
            <Button size="small" variant="outlined" disabled={props.isLoading} onClick={props.onRefresh} startIcon={<RefreshOutlinedIcon sx={{ fontSize: 17 }} />} sx={{ height: 36, px: 1.5, gap: .25, borderRadius: 1.25, whiteSpace: "nowrap", borderColor: "#DFE5EE" }}>Refresh</Button>
            <Button size="small" variant="outlined" disabled={!props.canExport} onClick={props.onExport} startIcon={<DownloadOutlinedIcon sx={{ fontSize: 17 }} />} sx={{ height: 36, px: 1.5, gap: .25, borderRadius: 1.25, whiteSpace: "nowrap", borderColor: "#DFE5EE" }}>Export</Button>
            <Button size="small" variant="contained" disableElevation disabled={props.isCancellingUpdate} onClick={props.isUpdatingData ? props.onCancelUpdate : props.onUpdateData} startIcon={props.isUpdatingData ? <CancelOutlinedIcon sx={{ fontSize: 17 }} /> : <CloudSyncOutlinedIcon sx={{ fontSize: 17 }} />} sx={{ height: 36, px: 1.5, gap: .25, borderRadius: 1.25, whiteSpace: "nowrap", bgcolor: props.isCancellingUpdate ? "#667085" : props.isUpdatingData ? "#B54708" : "#4F46D8", fontWeight: 600, boxShadow: "0 2px 6px rgba(79,70,216,.12)", "&:hover": { bgcolor: props.isUpdatingData ? "#93370D" : "#4338CA", boxShadow: "0 2px 7px rgba(67,56,202,.16)" } }}>{props.isCancellingUpdate ? "Cancelling update..." : props.isUpdatingData ? "Cancel Update" : "Update Data"}</Button>
        </Stack>
    </Box>;
}
