import { useEffect, useMemo, useState } from "react";

import DeleteOutlinedIcon from "@mui/icons-material/DeleteOutlined";
import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Grid from "@mui/material/Grid";
import IconButton from "@mui/material/IconButton";
import Stack from "@mui/material/Stack";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";

import { getMarketCandles } from "../api/marketApi";

interface Holding {
    id: string;
    symbol: string;
    quantity: number;
    averagePrice: number;
}

const storageKey = "alphaedge.local.holdings";

function loadHoldings(): Holding[] {
    try {
        const parsed = JSON.parse(localStorage.getItem(storageKey) ?? "[]");
        return Array.isArray(parsed) ? parsed : [];
    } catch {
        return [];
    }
}

function MyHoldings() {
    const [holdings, setHoldings] = useState<Holding[]>(loadHoldings);
    const [prices, setPrices] = useState<Record<string, number>>({});
    const [symbol, setSymbol] = useState("");
    const [quantity, setQuantity] = useState("");
    const [averagePrice, setAveragePrice] = useState("");
    const [message, setMessage] = useState("");

    useEffect(() => {
        localStorage.setItem(storageKey, JSON.stringify(holdings));
        let active = true;
        const symbols = [...new Set(holdings.map((holding) => holding.symbol))];
        void Promise.all(symbols.map(async (item) => {
            try {
                const result = await getMarketCandles(item, "1mo", "1d");
                return [item, result.candles.at(-1)?.close] as const;
            } catch {
                return [item, undefined] as const;
            }
        })).then((entries) => {
            if (active) {
                setPrices(Object.fromEntries(entries.filter((entry) => entry[1] !== undefined)));
            }
        });
        return () => {
            active = false;
        };
    }, [holdings]);

    const summary = useMemo(() => holdings.reduce((result, holding) => {
        const invested = holding.quantity * holding.averagePrice;
        const current = holding.quantity * (prices[holding.symbol] ?? holding.averagePrice);
        return {
            invested: result.invested + invested,
            current: result.current + current,
        };
    }, { invested: 0, current: 0 }), [holdings, prices]);

    function addHolding() {
        const normalized = symbol.trim().toUpperCase();
        const parsedQuantity = Number(quantity);
        const parsedPrice = Number(averagePrice);
        if (!/^[A-Z0-9.^_-]{1,24}$/.test(normalized) || parsedQuantity <= 0 || parsedPrice <= 0) {
            setMessage("Enter a valid symbol, quantity and average price.");
            return;
        }
        setHoldings((current) => [...current, {
            id: crypto.randomUUID(),
            symbol: normalized,
            quantity: parsedQuantity,
            averagePrice: parsedPrice,
        }]);
        setSymbol("");
        setQuantity("");
        setAveragePrice("");
        setMessage("");
    }

    const profit = summary.current - summary.invested;

    return (
        <Stack spacing={2}>
            <Box>
                <Typography variant="h4">Portfolio</Typography>
                <Typography color="text.secondary">Manual holdings with delayed research prices. No broker connection.</Typography>
            </Box>
            <Grid container spacing={1.5}>
                {[
                    ["Invested value", summary.invested],
                    ["Current value", summary.current],
                    ["Overall P&L", profit],
                ].map(([label, value]) => (
                    <Grid key={label as string} size={{ xs: 12, md: 4 }}>
                        <Card><CardContent>
                            <Typography color="text.secondary">{label}</Typography>
                            <Typography variant="h5" color={label === "Overall P&L" ? (profit >= 0 ? "success.main" : "error.main") : "text.primary"}>
                                ₹{(value as number).toLocaleString("en-IN", { maximumFractionDigits: 2 })}
                            </Typography>
                        </CardContent></Card>
                    </Grid>
                ))}
            </Grid>
            <Card><CardContent>
                <Stack direction={{ xs: "column", md: "row" }} spacing={1}>
                    <TextField size="small" label="NSE symbol" value={symbol} onChange={(event) => setSymbol(event.target.value)} />
                    <TextField size="small" type="number" label="Quantity" value={quantity} onChange={(event) => setQuantity(event.target.value)} />
                    <TextField size="small" type="number" label="Average price (₹)" value={averagePrice} onChange={(event) => setAveragePrice(event.target.value)} />
                    <Button variant="contained" onClick={addHolding}>Add holding</Button>
                </Stack>
                {message && <Alert severity="warning" sx={{ mt: 1.5 }}>{message}</Alert>}
            </CardContent></Card>
            <Card><CardContent>
                {holdings.length === 0 ? <Alert severity="info">No holdings added yet.</Alert> : (
                    <Table size="small">
                        <TableHead><TableRow>
                            {["Symbol", "Quantity", "Average", "Delayed LTP", "Value", "P&L", ""].map((label) => <TableCell key={label}>{label}</TableCell>)}
                        </TableRow></TableHead>
                        <TableBody>{holdings.map((holding) => {
                            const ltp = prices[holding.symbol];
                            const current = holding.quantity * (ltp ?? holding.averagePrice);
                            const rowProfit = current - holding.quantity * holding.averagePrice;
                            return <TableRow key={holding.id}>
                                <TableCell sx={{ fontWeight: 800 }}>{holding.symbol}</TableCell>
                                <TableCell>{holding.quantity}</TableCell>
                                <TableCell>₹{holding.averagePrice.toLocaleString("en-IN")}</TableCell>
                                <TableCell>{ltp ? `₹${ltp.toLocaleString("en-IN", { maximumFractionDigits: 2 })}` : "Unavailable"}</TableCell>
                                <TableCell>₹{current.toLocaleString("en-IN", { maximumFractionDigits: 2 })}</TableCell>
                                <TableCell sx={{ color: rowProfit >= 0 ? "success.main" : "error.main" }}>₹{rowProfit.toLocaleString("en-IN", { maximumFractionDigits: 2 })}</TableCell>
                                <TableCell><IconButton onClick={() => setHoldings((currentHoldings) => currentHoldings.filter((item) => item.id !== holding.id))}><DeleteOutlinedIcon fontSize="small" /></IconButton></TableCell>
                            </TableRow>;
                        })}</TableBody>
                    </Table>
                )}
            </CardContent></Card>
            <Typography variant="caption" color="text.secondary">Local portfolio data stays in this browser and is not sent to a broker.</Typography>
        </Stack>
    );
}

export default MyHoldings;
