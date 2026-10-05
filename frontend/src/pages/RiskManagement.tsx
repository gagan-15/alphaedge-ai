import { useMemo, useState } from "react";

import Box from "@mui/material/Box";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Grid from "@mui/material/Grid";
import LinearProgress from "@mui/material/LinearProgress";
import Stack from "@mui/material/Stack";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";

function RiskManagement() {
    const [balance, setBalance] = useState(100000);
    const [riskPercent, setRiskPercent] = useState(1);
    const [entry, setEntry] = useState(100);
    const [stop, setStop] = useState(95);
    const [target, setTarget] = useState(115);
    const calculations = useMemo(() => {
        const riskCapital = balance * riskPercent / 100;
        const distance = Math.abs(entry - stop);
        const quantity = distance === 0 ? 0 : Math.floor(riskCapital / distance);
        const reward = Math.abs(target - entry);
        return { riskCapital, quantity, ratio: distance === 0 ? 0 : reward / distance, exposure: quantity * entry };
    }, [balance, entry, riskPercent, stop, target]);
    return (
        <Stack spacing={1.5}>
            <Box><Typography variant="h4">Risk Management</Typography><Typography color="text.secondary">Mathematical planning before considering a research setup.</Typography></Box>
            <Grid container spacing={1.5}>
                <Grid size={{ xs: 12, lg: 5 }}>
                    <Card><CardContent>
                        <Typography variant="h6" sx={{ mb: 2 }}>Position Size Calculator</Typography>
                        <Grid container spacing={1.5}>
                            <Grid size={6}><TextField fullWidth label="Account balance (₹)" type="number" value={balance} onChange={(e) => setBalance(Number(e.target.value))} /></Grid>
                            <Grid size={6}><TextField fullWidth label="Risk per idea (%)" type="number" value={riskPercent} onChange={(e) => setRiskPercent(Number(e.target.value))} /></Grid>
                            <Grid size={4}><TextField fullWidth label="Entry" type="number" value={entry} onChange={(e) => setEntry(Number(e.target.value))} /></Grid>
                            <Grid size={4}><TextField fullWidth label="Invalidation" type="number" value={stop} onChange={(e) => setStop(Number(e.target.value))} /></Grid>
                            <Grid size={4}><TextField fullWidth label="Scenario target" type="number" value={target} onChange={(e) => setTarget(Number(e.target.value))} /></Grid>
                        </Grid>
                    </CardContent></Card>
                </Grid>
                <Grid size={{ xs: 12, lg: 7 }}>
                    <Card><CardContent>
                        <Typography variant="h6">Calculated Plan</Typography>
                        <Grid container spacing={2} sx={{ mt: 1 }}>
                            {[["Capital at risk", `₹${calculations.riskCapital.toLocaleString("en-IN")}`], ["Illustrative quantity", String(calculations.quantity)], ["Position exposure", `₹${calculations.exposure.toLocaleString("en-IN")}`], ["Risk/reward", `1 : ${calculations.ratio.toFixed(2)}`]].map(([label, value]) => (
                                <Grid key={label} size={{ xs: 6, md: 3 }}><Typography variant="caption" color="text.secondary">{label}</Typography><Typography variant="h5">{value}</Typography></Grid>
                            ))}
                        </Grid>
                        <Typography variant="body2" sx={{ mt: 2 }}>Account risk usage</Typography>
                        <LinearProgress variant="determinate" value={Math.min(100, riskPercent / 2 * 100)} color={riskPercent <= 1.25 ? "success" : "warning"} sx={{ mt: .75, height: 8 }} />
                        <Typography variant="caption" color="text.secondary" sx={{ display: "block", mt: 1.5 }}>This calculator does not recommend a position. Liquidity, gaps, fees and market conditions can change actual risk.</Typography>
                    </CardContent></Card>
                </Grid>
            </Grid>
        </Stack>
    );
}

export default RiskManagement;
