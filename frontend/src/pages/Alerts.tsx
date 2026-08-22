import { useEffect, useState } from "react";

import DeleteOutlinedIcon from "@mui/icons-material/DeleteOutlined";
import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Chip from "@mui/material/Chip";
import IconButton from "@mui/material/IconButton";
import MenuItem from "@mui/material/MenuItem";
import Stack from "@mui/material/Stack";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";

import { getMarketCandles } from "../api/marketApi";

interface PriceAlert {
    id: string;
    symbol: string;
    condition: "above" | "below";
    target: number;
    current: number | null;
    enabled: boolean;
}

const storageKey = "alphaedge.local.alerts";

function loadAlerts(): PriceAlert[] {
    try {
        const parsed = JSON.parse(localStorage.getItem(storageKey) ?? "[]");
        return Array.isArray(parsed)
            ? parsed.map((item) => ({ ...item, enabled: item.enabled ?? true }))
            : [];
    } catch {
        return [];
    }
}

function Alerts() {
    const [alerts, setAlerts] = useState<PriceAlert[]>(loadAlerts);
    const [symbol, setSymbol] = useState("");
    const [condition, setCondition] = useState<"above" | "below">("above");
    const [target, setTarget] = useState("");
    const [message, setMessage] = useState("");
    const [view, setView] = useState<"active" | "paused">("active");

    useEffect(() => {
        localStorage.setItem(storageKey, JSON.stringify(alerts.map((item) => ({ ...item, current: null }))));
    }, [alerts]);

    async function createAlert() {
        const normalized = symbol.trim().toUpperCase();
        const parsedTarget = Number(target);
        if (!/^[A-Z0-9.^_-]{1,24}$/.test(normalized) || parsedTarget <= 0) {
            setMessage("Enter a valid symbol and target price.");
            return;
        }
        setAlerts((current) => [...current, {
            id: crypto.randomUUID(),
            symbol: normalized,
            condition,
            target: parsedTarget,
            current: null,
            enabled: true,
        }]);
        setSymbol("");
        setTarget("");
        setMessage("");
    }

    async function checkAlerts() {
        setMessage("Checking delayed prices...");
        const checked = await Promise.all(alerts.map(async (item) => {
            if (!item.enabled) return item;
            try {
                const data = await getMarketCandles(item.symbol, "1mo", "1d");
                return { ...item, current: data.candles.at(-1)?.close ?? null };
            } catch {
                return { ...item, current: null };
            }
        }));
        setAlerts(checked);
        setMessage(checked.some((item) => item.current !== null)
            ? "Alert conditions updated using delayed prices."
            : "Prices are unavailable. Check that the backend is running.");
    }

    return (
        <Stack spacing={2}>
            <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <Box>
                    <Typography variant="h4">Alerts</Typography>
                    <Typography color="text.secondary">Local research alerts. No broker action is performed.</Typography>
                </Box>
                <Button variant="outlined" onClick={() => void checkAlerts()} disabled={alerts.length === 0}>Check now</Button>
            </Box>
            <Card><CardContent>
                <Stack direction={{ xs: "column", md: "row" }} spacing={1}>
                    <TextField size="small" label="NSE symbol" value={symbol} onChange={(event) => setSymbol(event.target.value)} />
                    <TextField select size="small" label="Condition" value={condition} onChange={(event) => setCondition(event.target.value as "above" | "below")}>
                        <MenuItem value="above">Price moves above</MenuItem>
                        <MenuItem value="below">Price moves below</MenuItem>
                    </TextField>
                    <TextField size="small" type="number" label="Target price (₹)" value={target} onChange={(event) => setTarget(event.target.value)} />
                    <Button variant="contained" onClick={() => void createAlert()}>Create alert</Button>
                </Stack>
                {message && <Alert severity="info" sx={{ mt: 1.5 }}>{message}</Alert>}
            </CardContent></Card>
            <Card><CardContent>
                <Stack direction="row" spacing={1} sx={{ mb: 1.5 }}>
                    <Button size="small" variant={view === "active" ? "contained" : "outlined"} onClick={() => setView("active")}>Active alerts</Button>
                    <Button size="small" variant={view === "paused" ? "contained" : "outlined"} onClick={() => setView("paused")}>Paused alerts</Button>
                </Stack>
                {alerts.filter((item) => view === "active" ? item.enabled : !item.enabled).length === 0 ? <Alert severity="info">No {view} alerts.</Alert> : (
                    <Table size="small">
                        <TableHead><TableRow>
                            {["Symbol", "Condition", "Target", "Delayed price", "Status", ""].map((label) => <TableCell key={label}>{label}</TableCell>)}
                        </TableRow></TableHead>
                        <TableBody>{alerts.filter((item) => view === "active" ? item.enabled : !item.enabled).map((item) => {
                            const triggered = item.current !== null
                                && (item.condition === "above" ? item.current >= item.target : item.current <= item.target);
                            return <TableRow key={item.id}>
                                <TableCell sx={{ fontWeight: 800 }}>{item.symbol}</TableCell>
                                <TableCell>{item.condition === "above" ? "Moves above" : "Moves below"}</TableCell>
                                <TableCell>₹{item.target.toLocaleString("en-IN")}</TableCell>
                                <TableCell>{item.current === null ? "Not checked" : `₹${item.current.toLocaleString("en-IN", { maximumFractionDigits: 2 })}`}</TableCell>
                                <TableCell><Chip size="small" color={triggered ? "warning" : "default"} label={triggered ? "Condition met" : "Watching"} /></TableCell>
                                <TableCell>
                                    <Button
                                        size="small"
                                        onClick={() => setAlerts((current) => current.map((alertItem) => alertItem.id === item.id ? { ...alertItem, enabled: !alertItem.enabled } : alertItem))}
                                    >
                                        {item.enabled ? "Pause" : "Resume"}
                                    </Button>
                                    <IconButton onClick={() => setAlerts((current) => current.filter((alertItem) => alertItem.id !== item.id))}><DeleteOutlinedIcon fontSize="small" /></IconButton>
                                </TableCell>
                            </TableRow>;
                        })}</TableBody>
                    </Table>
                )}
            </CardContent></Card>
            <Typography variant="caption" color="text.secondary">Automatic background and Telegram delivery are not enabled yet.</Typography>
        </Stack>
    );
}

export default Alerts;
