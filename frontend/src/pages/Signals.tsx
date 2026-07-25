import { useEffect, useState } from "react";

import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Chip from "@mui/material/Chip";
import CircularProgress from "@mui/material/CircularProgress";
import Grid from "@mui/material/Grid";
import LinearProgress from "@mui/material/LinearProgress";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";

import { getScanner } from "../api/scannerApi";
import type { ScannerResult } from "../types/scanner";

type SignalFilter = "all" | "approved" | "review";

function Signals() {
    const [results, setResults] = useState<ScannerResult[]>([]);
    const [filter, setFilter] = useState<SignalFilter>("all");
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    function loadSignals() {
        setLoading(true);
        setError("");
        void getScanner()
            .then((response) => setResults(response.results))
            .catch(() => setError("Signals could not be loaded. Check that the backend is running."))
            .finally(() => setLoading(false));
    }

    useEffect(() => {
        void getScanner()
            .then((response) => setResults(response.results))
            .catch(() => setError("Signals could not be loaded. Check that the backend is running."))
            .finally(() => setLoading(false));
    }, []);

    const visible = results.filter((result) =>
        filter === "all"
        || (filter === "approved" && result.approved)
        || (filter === "review" && !result.approved),
    );

    return (
        <Stack spacing={2}>
            <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 2 }}>
                <Box>
                    <Typography variant="h4">AI Research Signals</Typography>
                    <Typography color="text.secondary">
                        Explainable scanner setups. Not investment advice or guaranteed outcomes.
                    </Typography>
                </Box>
                <Button variant="outlined" onClick={loadSignals} disabled={loading}>Refresh</Button>
            </Box>

            <Stack direction="row" spacing={1}>
                {([
                    ["all", "All"],
                    ["approved", "Risk checks passed"],
                    ["review", "Needs review"],
                ] as const).map(([value, label]) => (
                    <Button
                        key={value}
                        size="small"
                        variant={filter === value ? "contained" : "outlined"}
                        onClick={() => setFilter(value)}
                    >
                        {label}
                    </Button>
                ))}
            </Stack>

            {error && <Alert severity="error">{error}</Alert>}
            {loading && <Box sx={{ display: "grid", placeItems: "center", minHeight: 240 }}><CircularProgress /></Box>}
            {!loading && !error && visible.length === 0 && (
                <Alert severity="info">No research setups match this filter.</Alert>
            )}

            <Grid container spacing={1.5}>
                {visible.map((signal) => (
                    <Grid key={signal.symbol} size={{ xs: 12, md: 6, xl: 4 }}>
                        <Card sx={{ height: "100%" }}>
                            <CardContent>
                                <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                                    <Typography variant="h6">{signal.symbol}</Typography>
                                    <Chip
                                        size="small"
                                        color={signal.approved ? "success" : "warning"}
                                        label={signal.approved ? "Bullish setup" : "Needs review"}
                                    />
                                </Box>
                                <Grid container spacing={1.5} sx={{ my: 2 }}>
                                    <Grid size={4}>
                                        <Typography color="text.secondary" variant="caption">Possible entry</Typography>
                                        <Typography>₹{signal.entry_price.toLocaleString("en-IN")}</Typography>
                                    </Grid>
                                    <Grid size={4}>
                                        <Typography color="text.secondary" variant="caption">Invalidation</Typography>
                                        <Typography color="error.main">₹{signal.stop_loss.toLocaleString("en-IN")}</Typography>
                                    </Grid>
                                    <Grid size={4}>
                                        <Typography color="text.secondary" variant="caption">Scenario target</Typography>
                                        <Typography color="success.main">₹{signal.target_price.toLocaleString("en-IN")}</Typography>
                                    </Grid>
                                </Grid>
                                <Box sx={{ display: "flex", justifyContent: "space-between", mb: 0.75 }}>
                                    <Typography variant="caption">Conditions matched</Typography>
                                    <Typography variant="caption">{signal.confirmation_score.toFixed(0)}%</Typography>
                                </Box>
                                <LinearProgress variant="determinate" value={signal.confirmation_score} />
                                <Stack direction="row" spacing={0.75} sx={{ mt: 1.5, flexWrap: "wrap" }}>
                                    <Chip size="small" variant="outlined" label={`Risk/reward 1:${signal.risk_reward_ratio.toFixed(2)}`} />
                                    <Chip size="small" variant="outlined" label={`Trend ${signal.trend_confirmed ? "✓" : "—"}`} />
                                    <Chip size="small" variant="outlined" label={`Volume ${signal.volume_confirmed ? "✓" : "—"}`} />
                                </Stack>
                                {signal.rejection_reason && (
                                    <Typography color="warning.main" variant="caption" sx={{ display: "block", mt: 1.25 }}>
                                        Review: {signal.rejection_reason}
                                    </Typography>
                                )}
                            </CardContent>
                        </Card>
                    </Grid>
                ))}
            </Grid>
        </Stack>
    );
}

export default Signals;
