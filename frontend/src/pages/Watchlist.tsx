import { useEffect, useState } from "react";

import DeleteOutlineIcon from "@mui/icons-material/DeleteOutlined";
import RefreshOutlinedIcon from "@mui/icons-material/RefreshOutlined";
import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import CircularProgress from "@mui/material/CircularProgress";
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

interface WatchlistQuote {
    symbol: string;
    price: number | null;
    change: number | null;
}

const storageKey = "alphaedge.local.watchlist";

function loadSymbols() {
    try {
        const stored = JSON.parse(localStorage.getItem(storageKey) ?? "[]");
        return Array.isArray(stored) ? stored as string[] : [];
    } catch {
        return [];
    }
}

function Watchlist() {
    const [symbols, setSymbols] = useState<string[]>(loadSymbols);
    const [quotes, setQuotes] = useState<WatchlistQuote[]>([]);
    const [newSymbol, setNewSymbol] = useState("");
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    useEffect(() => {
        localStorage.setItem(storageKey, JSON.stringify(symbols));
        let active = true;
        void Promise.all(symbols.map(async (symbol) => {
            try {
                const result = await getMarketCandles(symbol, "1mo", "1d");
                const latest = result.candles.at(-1);
                const previous = result.candles.at(-2);
                return {
                    symbol,
                    price: latest?.close ?? null,
                    change: latest && previous
                        ? ((latest.close - previous.close) / previous.close) * 100
                        : null,
                };
            } catch {
                return { symbol, price: null, change: null };
            }
        })).then((results) => {
            if (active) {
                setQuotes(results);
                setError(results.every((quote) => quote.price === null)
                    ? "Delayed prices are unavailable. Check that the backend is running."
                    : "");
                setLoading(false);
            }
        });
        return () => {
            active = false;
        };
    }, [symbols]);

    function addSymbol() {
        const normalized = newSymbol.trim().toUpperCase();
        if (!/^[A-Z0-9.^_-]{1,24}$/.test(normalized)) {
            setError("Enter a valid market symbol.");
            return;
        }
        if (!symbols.includes(normalized)) {
            setLoading(true);
            setSymbols((current) => [...current, normalized]);
        }
        setNewSymbol("");
    }

    function removeSymbol(symbol: string) {
        setLoading(true);
        setSymbols((current) => current.filter((item) => item !== symbol));
    }

    function refresh() {
        setLoading(true);
        setSymbols((current) => [...current]);
    }

    return (
        <Stack spacing={2}>
            <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <Box>
                    <Typography variant="h4">Watchlist</Typography>
                    <Typography color="text.secondary">Your saved symbols with delayed research prices.</Typography>
                </Box>
                <Button startIcon={<RefreshOutlinedIcon />} onClick={refresh} disabled={loading}>Refresh</Button>
            </Box>
            <Card><CardContent>
                <Stack direction="row" spacing={1}>
                    <TextField
                        size="small"
                        label="NSE symbol"
                        value={newSymbol}
                        onChange={(event) => setNewSymbol(event.target.value)}
                        onKeyDown={(event) => event.key === "Enter" && addSymbol()}
                    />
                    <Button variant="contained" onClick={addSymbol}>Add symbol</Button>
                </Stack>
            </CardContent></Card>
            {error && <Alert severity="warning">{error}</Alert>}
            <Card><CardContent>
                {loading && <Box sx={{ display: "grid", placeItems: "center", minHeight: 180 }}><CircularProgress /></Box>}
                {!loading && symbols.length === 0 && <Alert severity="info">Your watchlist is empty.</Alert>}
                {!loading && symbols.length > 0 && (
                    <Table size="small">
                        <TableHead><TableRow>
                            <TableCell>Symbol</TableCell>
                            <TableCell>Delayed price</TableCell>
                            <TableCell>Daily change</TableCell>
                            <TableCell align="right">Action</TableCell>
                        </TableRow></TableHead>
                        <TableBody>
                            {quotes.map((quote) => (
                                <TableRow key={quote.symbol} hover>
                                    <TableCell sx={{ fontWeight: 800 }}>{quote.symbol}</TableCell>
                                    <TableCell>{quote.price === null ? "Unavailable" : `₹${quote.price.toLocaleString("en-IN", { maximumFractionDigits: 2 })}`}</TableCell>
                                    <TableCell sx={{ color: quote.change === null ? "text.secondary" : quote.change >= 0 ? "success.main" : "error.main" }}>
                                        {quote.change === null ? "—" : `${quote.change >= 0 ? "+" : ""}${quote.change.toFixed(2)}%`}
                                    </TableCell>
                                    <TableCell align="right">
                                        <IconButton aria-label={`Remove ${quote.symbol}`} onClick={() => removeSymbol(quote.symbol)}>
                                            <DeleteOutlineIcon fontSize="small" />
                                        </IconButton>
                                    </TableCell>
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>
                )}
            </CardContent></Card>
            <Typography variant="caption" color="text.secondary">
                Watchlists are stored only in this browser during local development.
            </Typography>
        </Stack>
    );
}

export default Watchlist;
