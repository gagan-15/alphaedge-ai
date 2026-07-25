import { useEffect, useState } from "react";

import AddOutlinedIcon from "@mui/icons-material/AddOutlined";
import DeleteOutlinedIcon from "@mui/icons-material/DeleteOutlined";
import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Chip from "@mui/material/Chip";
import Grid from "@mui/material/Grid";
import IconButton from "@mui/material/IconButton";
import MenuItem from "@mui/material/MenuItem";
import Stack from "@mui/material/Stack";
import Switch from "@mui/material/Switch";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";

interface Strategy { id: string; name: string; setup: string; timeframe: string; enabled: boolean }
const storageKey = "alphaedge.local.strategies";
const defaults: Strategy[] = [
    { id: "zone", name: "Fresh Demand Retest", setup: "Fresh demand zone + bullish structure", timeframe: "1D", enabled: true },
    { id: "trend", name: "Trend Confluence", setup: "EMA alignment + structure confirmation", timeframe: "1W", enabled: true },
    { id: "breakout", name: "Breakout Follow-through", setup: "Range break + follow-through close", timeframe: "1D", enabled: false },
];

function loadStrategies() {
    try {
        const stored = JSON.parse(localStorage.getItem(storageKey) ?? "null");
        return Array.isArray(stored) ? stored as Strategy[] : defaults;
    } catch { return defaults; }
}

export default function Strategies() {
    const [strategies, setStrategies] = useState<Strategy[]>(loadStrategies);
    const [name, setName] = useState("");
    const [setup, setSetup] = useState("Demand zone + structure confirmation");
    const [timeframe, setTimeframe] = useState("1D");
    useEffect(() => localStorage.setItem(storageKey, JSON.stringify(strategies)), [strategies]);

    function create() {
        if (!name.trim()) return;
        setStrategies((current) => [...current, { id: crypto.randomUUID(), name: name.trim(), setup, timeframe, enabled: true }]);
        setName("");
    }

    return <Stack spacing={1.5}>
        <Box><Typography variant="h4">Strategy Builder</Typography><Typography color="text.secondary">Create transparent research rules. No automatic order execution.</Typography></Box>
        <Card><CardContent>
            <Typography variant="h6" sx={{ mb: 1.5 }}>Create strategy</Typography>
            <Grid container spacing={1.25}>
                <Grid size={{ xs: 12, md: 4 }}><TextField fullWidth size="small" label="Strategy name" value={name} onChange={(e) => setName(e.target.value)} /></Grid>
                <Grid size={{ xs: 12, md: 4 }}><TextField fullWidth select size="small" label="Rule template" value={setup} onChange={(e) => setSetup(e.target.value)}>
                    {["Demand zone + structure confirmation", "Supply zone + bearish structure", "Range breakout + follow-through", "Trend + momentum confluence"].map((x) => <MenuItem key={x} value={x}>{x}</MenuItem>)}
                </TextField></Grid>
                <Grid size={{ xs: 12, md: 2 }}><TextField fullWidth select size="small" label="Timeframe" value={timeframe} onChange={(e) => setTimeframe(e.target.value)}>
                    {["15m", "1H", "1D", "1W", "1M"].map((x) => <MenuItem key={x} value={x}>{x}</MenuItem>)}
                </TextField></Grid>
                <Grid size={{ xs: 12, md: 2 }}><Button fullWidth variant="contained" startIcon={<AddOutlinedIcon />} onClick={create}>Create</Button></Grid>
            </Grid>
        </CardContent></Card>
        <Grid container spacing={1.5}>{strategies.map((strategy) => <Grid key={strategy.id} size={{ xs: 12, md: 6, xl: 4 }}>
            <Card sx={{ height: "100%" }}><CardContent>
                <Stack direction="row" sx={{ justifyContent: "space-between", alignItems: "flex-start" }}>
                    <Box><Typography variant="h6">{strategy.name}</Typography><Chip size="small" label={strategy.timeframe} sx={{ mt: .75 }} /></Box>
                    <Stack direction="row"><Switch checked={strategy.enabled} onChange={() => setStrategies((current) => current.map((item) => item.id === strategy.id ? { ...item, enabled: !item.enabled } : item))} /><IconButton onClick={() => setStrategies((current) => current.filter((item) => item.id !== strategy.id))}><DeleteOutlinedIcon /></IconButton></Stack>
                </Stack>
                <Typography color="text.secondary" sx={{ my: 2 }}>{strategy.setup}</Typography>
                <Chip size="small" color={strategy.enabled ? "success" : "default"} label={strategy.enabled ? "Active for research" : "Paused"} />
            </CardContent></Card>
        </Grid>)}</Grid>
        <Alert severity="warning">Strategies must be backtested with costs and validated on unseen data. Active means enabled for research monitoring only.</Alert>
    </Stack>;
}
