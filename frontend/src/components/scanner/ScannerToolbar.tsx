/**
 * Scanner Toolbar.
 *
 * Sprint:
 *     2.65 - Professional Scanner UI
 */

import SearchIcon from "@mui/icons-material/Search";
import DownloadOutlinedIcon from "@mui/icons-material/DownloadOutlined";
import RefreshOutlinedIcon from "@mui/icons-material/RefreshOutlined";
import PlayArrowRoundedIcon from "@mui/icons-material/PlayArrowRounded";

import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Grid from "@mui/material/Grid";
import MenuItem from "@mui/material/MenuItem";
import Select from "@mui/material/Select";
import Stack from "@mui/material/Stack";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";
import { alpha } from "@mui/material/styles";

export type ScannerQuickPreset =
    | "fresh-demand"
    | "fresh-supply"
    | "near-entry"
    | "high-confidence"
    | "swing"
    | "intraday"
    | "todays-best"
    | "reset";

interface ScannerToolbarProps {
    isLoading: boolean;
    searchQuery: string;
    onRefresh: () => void;
    onRunScan: () => void;
    onSearchChange: (value: string) => void;
    minimumScore: number;
    approvalFilter: string;
    onMinimumScoreChange: (value: number) => void;
    onApprovalFilterChange: (value: string) => void;
    onExport: () => void;
    canExport: boolean;
    market: string;
    timeframe: string;
    onMarketChange: (value: string) => void;
    onTimeframeChange: (value: string) => void;
    patternFilter: string;
    statusFilter: string;
    proximityFilter: number;
    onPatternFilterChange: (value: string) => void;
    onStatusFilterChange: (value: string) => void;
    onProximityFilterChange: (value: number) => void;
    onQuickPreset: (preset: ScannerQuickPreset) => void;
}

function ScannerToolbar({
    isLoading,
    searchQuery,
    onRefresh,
    onRunScan,
    onSearchChange,
    minimumScore,
    approvalFilter,
    onMinimumScoreChange,
    onApprovalFilterChange,
    onExport,
    canExport,
    market,
    timeframe,
    onMarketChange,
    onTimeframeChange,
    patternFilter,
    statusFilter,
    proximityFilter,
    onPatternFilterChange,
    onStatusFilterChange,
    onProximityFilterChange,
    onQuickPreset,
}: ScannerToolbarProps) {
    const presets: Array<{ id: ScannerQuickPreset; label: string; color: string }> = [
        { id: "fresh-demand", label: "Fresh Demand", color: "#31c77a" },
        { id: "fresh-supply", label: "Fresh Supply", color: "#ff5c67" },
        { id: "near-entry", label: "Near Entry (<5%)", color: "#f5b942" },
        { id: "high-confidence", label: "High Confidence (≥90)", color: "#a78bfa" },
        { id: "swing", label: "Swing Setups", color: "#60a5fa" },
        { id: "intraday", label: "Intraday", color: "#22d3ee" },
        { id: "todays-best", label: "Today's Best", color: "#f59e0b" },
        { id: "reset", label: "Reset", color: "#94a3b8" },
    ];

    return (
        <Card>
            <CardContent sx={{ p: { xs: 1.5, md: 2 }, "&:last-child": { pb: { xs: 1.5, md: 2 } } }}>
                <Stack spacing={1.5}>
                    <Stack
                        sx={{
                            flexDirection: { xs: "column", sm: "row" },
                            justifyContent: "space-between",
                            alignItems: { xs: "stretch", sm: "center" },
                            gap: 1,
                        }}
                    >
                        <Box>
                            <Typography variant="h4">
                                Scanner
                            </Typography>

                            <Typography
                                variant="body2"
                                color="text.secondary"
                            >
                                Professional Market Scanner
                            </Typography>
                        </Box>

                        <Stack
                            sx={{
                                flexDirection: "row",
                                gap: 1,
                                flexWrap: "wrap",
                                justifyContent: "flex-end",
                            }}
                        >
                            <Button
                                variant="outlined"
                                size="small"
                                disabled={isLoading}
                                onClick={onRefresh}
                                startIcon={
                                    <RefreshOutlinedIcon />
                                }
                            >
                                Refresh
                            </Button>

                            <Button
                                variant="outlined"
                                size="small"
                                disabled={!canExport}
                                onClick={onExport}
                                startIcon={
                                    <DownloadOutlinedIcon />
                                }
                            >
                                Export
                            </Button>

                            <Button
                                variant="contained"
                                size="small"
                                disabled={isLoading}
                                onClick={onRunScan}
                                startIcon={
                                    <PlayArrowRoundedIcon />
                                }
                            >
                                {isLoading
                                    ? "Scanning..."
                                    : "Run Scan"}
                            </Button>
                        </Stack>
                    </Stack>

                    <Box>
                        <Typography color="text.secondary" sx={{ mb: 0.75, fontSize: "0.66rem", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.06em" }}>
                            Quick Presets
                        </Typography>
                        <Stack direction="row" useFlexGap sx={{ gap: 0.75, flexWrap: "wrap" }}>
                            {presets.map((preset) => (
                                <Button
                                    key={preset.id}
                                    size="small"
                                    variant="outlined"
                                    onClick={() => onQuickPreset(preset.id)}
                                    sx={{
                                        minHeight: 30,
                                        px: 1.2,
                                        color: preset.color,
                                        borderColor: alpha(preset.color, 0.48),
                                        bgcolor: alpha(preset.color, 0.035),
                                        fontSize: "0.66rem",
                                        "&:hover": {
                                            borderColor: preset.color,
                                            bgcolor: alpha(preset.color, 0.09),
                                        },
                                    }}
                                >
                                    {preset.label}
                                </Button>
                            ))}
                        </Stack>
                    </Box>

                    <TextField
                        fullWidth
                        size="small"
                        placeholder="Search symbol..."
                        value={searchQuery}
                        onChange={(event) => {
                            onSearchChange(
                                event.target.value,
                            );
                        }}
                        slotProps={{
                            input: {
                                startAdornment: (
                                    <SearchIcon
                                        fontSize="small"
                                    />
                                ),
                            },
                        }}
                    />

                    <Grid
                        container
                        spacing={1.25}
                    >
                        <Grid size={{ xs: 12, sm: 6, lg: 2 }}>
                            <Typography
                                variant="body2"
                                color="text.secondary"
                                sx={{ mb: 1 }}
                            >
                                Market
                            </Typography>

                            <Select
                                fullWidth
                                size="small"
                                value={market}
                                onChange={(event) => onMarketChange(event.target.value)}
                            >
                                <MenuItem value="NSE">
                                    NSE
                                </MenuItem>

                                <MenuItem value="BSE">
                                    BSE
                                </MenuItem>
                            </Select>
                        </Grid>

                        <Grid size={{ xs: 12, sm: 6, lg: 2 }}>
                            <Typography
                                variant="body2"
                                color="text.secondary"
                                sx={{ mb: 1 }}
                            >
                                Timeframe
                            </Typography>

                            <Select
                                fullWidth
                                size="small"
                                value={timeframe}
                                onChange={(event) => onTimeframeChange(event.target.value)}
                            >
                                <MenuItem value="MINUTE_5">5 minutes</MenuItem>
                                <MenuItem value="MINUTE_15">15 minutes</MenuItem>
                                <MenuItem value="MINUTE_75">75 minutes</MenuItem>
                                <MenuItem value="MINUTE_125">125 minutes</MenuItem>
                                <MenuItem value="HOUR_1">1 hour</MenuItem>
                                <MenuItem value="HOUR_2">2 hours</MenuItem>
                                <MenuItem value="HOUR_4">4 hours</MenuItem>
                                <MenuItem value="HOUR_6">6 hours</MenuItem>
                                <MenuItem value="DAILY">
                                    Daily
                                </MenuItem>

                                <MenuItem value="WEEKLY">
                                    Weekly
                                </MenuItem>

                                <MenuItem value="MONTHLY">
                                    Monthly
                                </MenuItem>

                                <MenuItem value="QUARTERLY">
                                    Quarterly
                                </MenuItem>

                                <MenuItem value="HALFYEARLY">
                                    Half-yearly
                                </MenuItem>

                                <MenuItem value="YEARLY">
                                    Yearly
                                </MenuItem>
                            </Select>
                        </Grid>

                        <Grid size={{ xs: 12, sm: 6, lg: 2 }}>
                            <Typography
                                variant="body2"
                                color="text.secondary"
                                sx={{ mb: 1 }}
                            >
                                Minimum quality
                            </Typography>

                            <Select
                                fullWidth
                                size="small"
                                value={minimumScore}
                                onChange={(event) => onMinimumScoreChange(Number(event.target.value))}
                            >
                                <MenuItem value={0}>Show rejected zones</MenuItem>
                                <MenuItem value={40}>Weak and above</MenuItem>
                                <MenuItem value={60}>60 and above</MenuItem>
                                <MenuItem value={75}>75 and above</MenuItem>
                                <MenuItem value={90}>90 and above</MenuItem>
                            </Select>
                        </Grid>

                        <Grid size={{ xs: 12, sm: 6, lg: 2 }}>
                            <Typography
                                variant="body2"
                                color="text.secondary"
                                sx={{ mb: 1 }}
                            >
                                Zone type
                            </Typography>

                            <Select
                                fullWidth
                                size="small"
                                value={approvalFilter}
                                onChange={(event) => onApprovalFilterChange(event.target.value)}
                            >
                                <MenuItem value="all">Demand and supply</MenuItem>
                                <MenuItem value="approved">Demand zones</MenuItem>
                                <MenuItem value="rejected">Supply zones</MenuItem>
                            </Select>
                        </Grid>
                        <Grid size={{ xs: 12, sm: 6, lg: 2 }}>
                            <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                                Pattern
                            </Typography>
                            <Select
                                fullWidth
                                size="small"
                                value={patternFilter}
                                onChange={(event) => onPatternFilterChange(event.target.value)}
                            >
                                <MenuItem value="all">All patterns</MenuItem>
                                <MenuItem value="DROP_BASE_RALLY">DBR</MenuItem>
                                <MenuItem value="RALLY_BASE_RALLY">RBR</MenuItem>
                                <MenuItem value="RALLY_BASE_DROP">RBD</MenuItem>
                                <MenuItem value="DROP_BASE_DROP">DBD</MenuItem>
                            </Select>
                        </Grid>
                        <Grid size={{ xs: 12, sm: 6, lg: 2 }}>
                            <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                                Status / proximity
                            </Typography>
                            <Stack direction="row" spacing={1}>
                                <Select
                                    fullWidth
                                    size="small"
                                    value={statusFilter}
                                    onChange={(event) => onStatusFilterChange(event.target.value)}
                                >
                                    <MenuItem value="all">All</MenuItem>
                                    <MenuItem value="IN ZONE">In zone</MenuItem>
                                    <MenuItem value="APPROACHING">Approaching</MenuItem>
                                    <MenuItem value="WATCH">Watch</MenuItem>
                                </Select>
                                <Select
                                    fullWidth
                                    size="small"
                                    value={proximityFilter}
                                    onChange={(event) => onProximityFilterChange(Number(event.target.value))}
                                >
                                    <MenuItem value={100}>Any distance</MenuItem>
                                    <MenuItem value={1}>Within 1%</MenuItem>
                                    <MenuItem value={3}>Within 3%</MenuItem>
                                    <MenuItem value={5}>Within 5%</MenuItem>
                                </Select>
                            </Stack>
                        </Grid>
                    </Grid>
                </Stack>
            </CardContent>
        </Card>
    );
}

export default ScannerToolbar;
