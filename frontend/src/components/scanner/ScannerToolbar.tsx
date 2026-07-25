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
}: ScannerToolbarProps) {
    return (
        <Card>
            <CardContent>
                <Stack spacing={4}>
                    <Stack
                        sx={{
                            flexDirection: "row",
                            justifyContent: "space-between",
                            alignItems: "center",
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
                                gap: 2,
                            }}
                        >
                            <Button
                                variant="outlined"
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

                    <TextField
                        fullWidth
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
                        spacing={2}
                    >
                        <Grid size={{ xs: 12, md: 3 }}>
                            <Typography
                                variant="body2"
                                color="text.secondary"
                                sx={{ mb: 1 }}
                            >
                                Market
                            </Typography>

                            <Select
                                fullWidth
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

                        <Grid size={{ xs: 12, md: 3 }}>
                            <Typography
                                variant="body2"
                                color="text.secondary"
                                sx={{ mb: 1 }}
                            >
                                Timeframe
                            </Typography>

                            <Select
                                fullWidth
                                value={timeframe}
                                onChange={(event) => onTimeframeChange(event.target.value)}
                            >
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

                        <Grid size={{ xs: 12, md: 3 }}>
                            <Typography
                                variant="body2"
                                color="text.secondary"
                                sx={{ mb: 1 }}
                            >
                                Minimum quality
                            </Typography>

                            <Select
                                fullWidth
                                value={minimumScore}
                                onChange={(event) => onMinimumScoreChange(Number(event.target.value))}
                            >
                                <MenuItem value={0}>Any quality</MenuItem>
                                <MenuItem value={60}>60 and above</MenuItem>
                                <MenuItem value={75}>75 and above</MenuItem>
                                <MenuItem value={90}>90 and above</MenuItem>
                            </Select>
                        </Grid>

                        <Grid size={{ xs: 12, md: 3 }}>
                            <Typography
                                variant="body2"
                                color="text.secondary"
                                sx={{ mb: 1 }}
                            >
                                Zone type
                            </Typography>

                            <Select
                                fullWidth
                                value={approvalFilter}
                                onChange={(event) => onApprovalFilterChange(event.target.value)}
                            >
                                <MenuItem value="all">Demand and supply</MenuItem>
                                <MenuItem value="approved">Demand zones</MenuItem>
                                <MenuItem value="rejected">Supply zones</MenuItem>
                            </Select>
                        </Grid>
                    </Grid>
                </Stack>
            </CardContent>
        </Card>
    );
}

export default ScannerToolbar;
