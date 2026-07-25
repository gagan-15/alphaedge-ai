import { useState } from "react";

import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Chip from "@mui/material/Chip";
import Grid from "@mui/material/Grid";
import LinearProgress from "@mui/material/LinearProgress";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";

const sectors = [
    ["Nifty IT", 80, "8 / 10"],
    ["Nifty Bank", 70, "7 / 10"],
    ["Nifty FMCG", 62, "6 / 10"],
    ["Nifty Auto", 38, "4 / 10"],
    ["Nifty Metal", 31, "3 / 10"],
    ["Nifty Pharma", 57, "6 / 10"],
] as const;

function MarketBreadth() {
    const [range, setRange] = useState("1D");
    return (
        <Stack spacing={1.5}>
            <Stack direction={{ xs: "column", md: "row" }} sx={{ justifyContent: "space-between", alignItems: { md: "center" } }}>
                <Box>
                    <Typography variant="h4">Market Breadth</Typography>
                    <Typography color="text.secondary">Delayed participation across tracked Indian equities.</Typography>
                </Box>
                <Chip size="small" color="warning" label="DEMO BREADTH DATA" />
            </Stack>
            <Grid container spacing={1.25}>
                {[["Advancing", "1,682", "62%"], ["Declining", "802", "33%"], ["Unchanged", "126", "5%"]].map(([label, value, share]) => (
                    <Grid key={label} size={{ xs: 12, md: 4 }}>
                        <Card><CardContent>
                            <Typography color="text.secondary">{label}</Typography>
                            <Typography variant="h4" sx={{ mt: 1 }}>{value}</Typography>
                            <Typography color={label === "Advancing" ? "success.main" : label === "Declining" ? "error.main" : "text.secondary"}>{share} of tracked symbols</Typography>
                        </CardContent></Card>
                    </Grid>
                ))}
            </Grid>
            <Grid container spacing={1.5}>
                <Grid size={{ xs: 12, lg: 8 }}>
                    <Card sx={{ height: 370 }}><CardContent>
                        <Stack direction="row" sx={{ justifyContent: "space-between", alignItems: "center" }}>
                            <Box>
                                <Typography variant="h6">Advance–Decline Line</Typography>
                                <Typography variant="caption" color="text.secondary">Net market participation</Typography>
                            </Box>
                            <Stack direction="row" spacing={.5}>
                                {["1D", "1W", "1M", "3M"].map((item) => (
                                    <Button key={item} size="small" variant={range === item ? "contained" : "text"} onClick={() => setRange(item)}>{item}</Button>
                                ))}
                            </Stack>
                        </Stack>
                        <Box component="svg" viewBox="0 0 100 100" preserveAspectRatio="none" sx={{ width: "100%", height: 285, mt: 1 }}>
                            {[20, 40, 60, 80].map((y) => <line key={y} x1="0" y1={y} x2="100" y2={y} stroke="#1d2b40" strokeWidth=".35" />)}
                            <defs><linearGradient id="breadthArea" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#35d07f" stopOpacity=".38" /><stop offset="100%" stopColor="#35d07f" stopOpacity="0" /></linearGradient></defs>
                            <polygon points="0,88 8,79 16,83 24,67 32,71 40,55 48,61 56,46 64,52 72,34 80,39 88,25 100,16 100,100 0,100" fill="url(#breadthArea)" />
                            <polyline points="0,88 8,79 16,83 24,67 32,71 40,55 48,61 56,46 64,52 72,34 80,39 88,25 100,16" fill="none" stroke="#35d07f" strokeWidth="1.7" />
                        </Box>
                    </CardContent></Card>
                </Grid>
                <Grid size={{ xs: 12, lg: 4 }}>
                    <Card sx={{ height: 370 }}><CardContent>
                        <Typography variant="h6" sx={{ mb: 2 }}>Sector Breadth</Typography>
                        {sectors.map(([sector, value, ratio]) => (
                            <Box key={sector} sx={{ mb: 1.65 }}>
                                <Stack direction="row" sx={{ justifyContent: "space-between" }}>
                                    <Typography>{sector}</Typography>
                                    <Typography color={value >= 50 ? "success.main" : "error.main"}>{ratio}</Typography>
                                </Stack>
                                <LinearProgress variant="determinate" value={value} color={value >= 50 ? "success" : "error"} sx={{ mt: .5, height: 6 }} />
                            </Box>
                        ))}
                    </CardContent></Card>
                </Grid>
                <Grid size={{ xs: 12, md: 6 }}><Card><CardContent><Typography color="text.secondary">52-week highs</Typography><Typography variant="h4">156</Typography></CardContent></Card></Grid>
                <Grid size={{ xs: 12, md: 6 }}><Card><CardContent><Typography color="text.secondary">52-week lows</Typography><Typography variant="h4">23</Typography></CardContent></Card></Grid>
            </Grid>
        </Stack>
    );
}

export default MarketBreadth;
