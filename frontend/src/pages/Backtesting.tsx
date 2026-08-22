import { useMemo, useState } from "react";

import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Chip from "@mui/material/Chip";
import Grid from "@mui/material/Grid";
import MenuItem from "@mui/material/MenuItem";
import Stack from "@mui/material/Stack";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";

function Backtesting() {
    const [strategy, setStrategy] = useState("Demand zone first retest");
    const [period, setPeriod] = useState("1 year");
    const [costs, setCosts] = useState(0.15);
    const [ran, setRan] = useState(false);
    const result = useMemo(() => {
        const multiplier = strategy.includes("Demand") ? 1 : .82;
        const years = period === "3 years" ? 3 : period === "5 years" ? 5 : 1;
        return {
            returnValue: (28.45 * multiplier * Math.sqrt(years) - costs * 12 * years).toFixed(2),
            drawdown: (-12.35 * (1 + (years - 1) * .08)).toFixed(2),
            winRate: (68.75 * multiplier).toFixed(2),
            trades: Math.round(156 * years * multiplier),
            profitFactor: (1.85 * multiplier).toFixed(2),
        };
    }, [costs, period, strategy]);

    return (
        <Stack spacing={1.5}>
            <Stack direction={{ xs: "column", md: "row" }} sx={{ justifyContent: "space-between", alignItems: { md: "center" } }}>
                <Box><Typography variant="h4">Backtesting Engine</Typography><Typography color="text.secondary">Historical rule testing with visible assumptions.</Typography></Box>
                <Chip size="small" color="warning" label="ILLUSTRATIVE ENGINE" />
            </Stack>
            <Grid container spacing={1.5}>
                <Grid size={{ xs: 12, lg: 3 }}>
                    <Card><CardContent>
                        <Typography variant="h6" sx={{ mb: 2 }}>Strategy Settings</Typography>
                        <Stack spacing={1.5}>
                            <TextField select label="Strategy" value={strategy} onChange={(event) => setStrategy(event.target.value)}>
                                <MenuItem value="Demand zone first retest">Demand zone first retest</MenuItem>
                                <MenuItem value="Trend following">Trend following</MenuItem>
                                <MenuItem value="Volume breakout">Volume breakout</MenuItem>
                            </TextField>
                            <TextField select label="Historical period" value={period} onChange={(event) => setPeriod(event.target.value)}>
                                <MenuItem value="1 year">1 year</MenuItem><MenuItem value="3 years">3 years</MenuItem><MenuItem value="5 years">5 years</MenuItem>
                            </TextField>
                            <TextField label="Estimated costs per trade (%)" type="number" value={costs} onChange={(event) => setCosts(Number(event.target.value))} />
                            <Button variant="contained" onClick={() => setRan(true)}>Run illustrative backtest</Button>
                        </Stack>
                    </CardContent></Card>
                </Grid>
                <Grid size={{ xs: 12, lg: 9 }}>
                    <Card sx={{ minHeight: 390 }}><CardContent>
                        <Typography variant="h6">Historical Results</Typography>
                        {!ran ? <Typography color="text.secondary" sx={{ mt: 8, textAlign: "center" }}>Choose assumptions and run the backtest.</Typography> : <>
                            <Grid container spacing={1.5} sx={{ mt: 1 }}>
                                {[["Total return", `${result.returnValue}%`], ["Max drawdown", `${result.drawdown}%`], ["Win rate", `${result.winRate}%`], ["Profit factor", result.profitFactor], ["Trades", String(result.trades)]].map(([label, value]) => (
                                    <Grid key={label} size={{ xs: 6, md: 2.4 }}><Typography variant="caption" color="text.secondary">{label}</Typography><Typography variant="h5">{value}</Typography></Grid>
                                ))}
                            </Grid>
                            <Box component="svg" viewBox="0 0 100 70" preserveAspectRatio="none" sx={{ width: "100%", height: 250, mt: 2 }}>
                                {[15, 35, 55].map((y) => <line key={y} x1="0" y1={y} x2="100" y2={y} stroke="#1d2b40" strokeWidth=".35" />)}
                                <polyline points="0,62 8,55 16,57 24,45 32,49 40,37 48,40 56,28 64,31 72,19 80,23 88,12 100,7" fill="none" stroke="#35d07f" strokeWidth="1.8" />
                            </Box>
                            <Typography variant="caption" color="text.secondary">Illustrative calculation only. A production result requires timestamped historical data, survivorship-bias controls, slippage and walk-forward validation.</Typography>
                        </>}
                    </CardContent></Card>
                </Grid>
            </Grid>
        </Stack>
    );
}

export default Backtesting;
