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
}

function ScannerToolbar({
    isLoading,
    searchQuery,
    onRefresh,
    onRunScan,
    onSearchChange,
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
                                disabled
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
                                defaultValue="NSE"
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
                                defaultValue="Daily"
                            >
                                <MenuItem value="Daily">
                                    Daily
                                </MenuItem>

                                <MenuItem value="Weekly">
                                    Weekly
                                </MenuItem>

                                <MenuItem value="75 Min">
                                    75 Min
                                </MenuItem>

                                <MenuItem value="125 Min">
                                    125 Min
                                </MenuItem>
                            </Select>
                        </Grid>

                        <Grid size={{ xs: 12, md: 3 }}>
                            <Typography
                                variant="body2"
                                color="text.secondary"
                                sx={{ mb: 1 }}
                            >
                                Strategy
                            </Typography>

                            <Select
                                fullWidth
                                defaultValue="Demand Zone"
                            >
                                <MenuItem value="Demand Zone">
                                    Demand Zone
                                </MenuItem>
                            </Select>
                        </Grid>

                        <Grid size={{ xs: 12, md: 3 }}>
                            <Typography
                                variant="body2"
                                color="text.secondary"
                                sx={{ mb: 1 }}
                            >
                                Universe
                            </Typography>

                            <Select
                                fullWidth
                                defaultValue="FnO"
                            >
                                <MenuItem value="FnO">
                                    FnO
                                </MenuItem>

                                <MenuItem value="NIFTY 200">
                                    NIFTY 200
                                </MenuItem>

                                <MenuItem value="All Stocks">
                                    All Stocks
                                </MenuItem>
                            </Select>
                        </Grid>
                    </Grid>
                </Stack>
            </CardContent>
        </Card>
    );
}

export default ScannerToolbar;
