import { useMemo, useState } from "react";

import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Chip from "@mui/material/Chip";
import MenuItem from "@mui/material/MenuItem";
import Stack from "@mui/material/Stack";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";

const underlyingConfig: Record<string, { spot: number; step: number }> = {
    NIFTY: { spot: 24731, step: 50 },
    BANKNIFTY: { spot: 54372, step: 100 },
    RELIANCE: { spot: 2978, step: 50 },
};

export default function OptionChain() {
    const [symbol, setSymbol] = useState("NIFTY");
    const [expiry, setExpiry] = useState("30 Jul 2026");
    const [rows, setRows] = useState(9);
    const config = underlyingConfig[symbol];
    const chain = useMemo(() => {
        const atm = Math.round(config.spot / config.step) * config.step;
        const expiryIndex = ["30 Jul 2026", "06 Aug 2026", "27 Aug 2026"].indexOf(expiry);
        const timeValue = 1 + Math.max(0, expiryIndex) * .18;
        return Array.from({ length: rows }, (_, index) => {
            const strike = atm + (index - Math.floor(rows / 2)) * config.step;
            const distance = (strike - config.spot) / config.step;
            return {
                strike,
                callOi: Math.round((12500 + Math.abs(distance) * 1900 + index * 320) * timeValue),
                callChange: 0.8 + index * 0.22,
                callLtp: Math.max(8, (110 - distance * config.step * 0.48) * timeValue),
                putLtp: Math.max(8, (90 + distance * config.step * 0.48) * timeValue),
                putChange: -0.6 - index * 0.18,
                putOi: Math.round((10500 + Math.abs(distance) * 1700 + (rows - index) * 290) * timeValue),
                atm: strike === atm,
            };
        });
    }, [config, expiry, rows]);

    return <Stack spacing={1.5}>
        <Stack direction={{ xs: "column", md: "row" }} sx={{ justifyContent: "space-between", alignItems: { md: "center" } }}>
            <Box><Typography variant="h4">Option Chain</Typography><Typography color="text.secondary">Open-interest research view with no order placement.</Typography></Box>
            <Chip color="warning" label="DELAYED DEMO CHAIN" />
        </Stack>
        <Card><CardContent>
            <Stack direction={{ xs: "column", sm: "row" }} spacing={1.25}>
                <TextField select size="small" label="Underlying" value={symbol} onChange={(e) => setSymbol(e.target.value)} sx={{ minWidth: 180 }}>
                    {Object.keys(underlyingConfig).map((x) => <MenuItem key={x} value={x}>{x}</MenuItem>)}
                </TextField>
                <TextField select size="small" label="Expiry" value={expiry} onChange={(e) => setExpiry(e.target.value)} sx={{ minWidth: 180 }}>
                    {["30 Jul 2026", "06 Aug 2026", "27 Aug 2026"].map((x) => <MenuItem key={x} value={x}>{x}</MenuItem>)}
                </TextField>
                <TextField select size="small" label="Strikes" value={rows} onChange={(e) => setRows(Number(e.target.value))} sx={{ minWidth: 130 }}>
                    {[5, 9, 13].map((x) => <MenuItem key={x} value={x}>{x}</MenuItem>)}
                </TextField>
            </Stack>
        </CardContent></Card>
        <Card><CardContent>
            <Stack direction="row" sx={{ mb: 1, justifyContent: "space-between" }}>
                <Typography variant="h6">{symbol} · {expiry}</Typography>
                <Typography color="success.main">Illustrative spot {config.spot.toLocaleString("en-IN")}</Typography>
            </Stack>
            <Box sx={{ overflowX: "auto" }}><Table size="small">
                <TableHead><TableRow>{["Call OI", "Call Δ", "Call LTP", "Strike", "Put LTP", "Put Δ", "Put OI"].map((x) => <TableCell key={x} align="right">{x}</TableCell>)}</TableRow></TableHead>
                <TableBody>{chain.map((row) => <TableRow key={row.strike} sx={{ bgcolor: row.atm ? "rgba(99,102,241,.12)" : undefined }}>
                    <TableCell align="right">{row.callOi.toLocaleString("en-IN")}</TableCell>
                    <TableCell align="right" sx={{ color: "success.main" }}>+{row.callChange.toFixed(2)}%</TableCell>
                    <TableCell align="right">{row.callLtp.toFixed(2)}</TableCell>
                    <TableCell align="right" sx={{ fontWeight: 900 }}>{row.strike.toLocaleString("en-IN")}{row.atm && <Chip size="small" label="ATM" sx={{ ml: 1 }} />}</TableCell>
                    <TableCell align="right">{row.putLtp.toFixed(2)}</TableCell>
                    <TableCell align="right" sx={{ color: "error.main" }}>{row.putChange.toFixed(2)}%</TableCell>
                    <TableCell align="right">{row.putOi.toLocaleString("en-IN")}</TableCell>
                </TableRow>)}</TableBody>
            </Table></Box>
        </CardContent></Card>
        <Alert severity="warning">This is not an exchange option feed and must not be used for trading decisions. Live NSE derivatives data requires an authorized provider.</Alert>
    </Stack>;
}
