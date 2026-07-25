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
                        Explainable delayed scanner setups. No orders or guaranteed outcomes.
                    </Typography>
                </Box>
                <Button variant="outlined" onClick={loadSignals} disabled={loading}>Refresh</Button>
            </Box>

            <Stack direction="row" spacing={1}>
                {([
                    ["all", "All signals"],
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

            <Grid container spacing={1}>
                {visible.map((signal) => (
                    <Grid key={signal.symbol} size={12}>
                        <Card>
                            <CardContent>
                                <Grid container spacing={2} sx={{ alignItems: "center" }}>
                                    <Grid size={{ xs: 12, md: 2 }}>
                                        <Stack direction="row" spacing={1} sx={{ alignItems: "center" }}>
                                            <Typography variant="h6">{signal.symbol}</Typography>
                                            <Chip
                                                size="small"
                                                color={signal.approved ? "success" : "warning"}
                                                label={signal.approved ? "Qualified" : "Review"}
                                            />
                                        </Stack>
                                        <Typography
                                            variant="body2"
                                            color={signal.approved ? "success.main" : "warning.main"}
                                            sx={{ mt: .75, fontWeight: 750 }}
                                        >
                                            {signal.approved ? "Bullish research setup" : "Conditions incomplete"}
                                        </Typography>
                                        <Typography variant="caption" color="text.secondary">
                                            {signal.timeframe?.toUpperCase() ?? "1D"} · delayed research
                                        </Typography>
                                    </Grid>

                                    <Grid size={{ xs: 12, md: 3 }}>
                                        <Typography variant="caption" color="text.secondary">Why it was detected</Typography>
                                        {[
                                            ["Trend alignment", signal.trend_confirmed],
                                            ["Volume confirmation", signal.volume_confirmed],
                                            ["Momentum confirmation", signal.momentum_confirmed],
                                        ].map(([label, matched]) => (
                                            <Typography
                                                key={label as string}
                                                variant="body2"
                                                color={matched ? "success.main" : "text.secondary"}
                                                sx={{ py: .25 }}
                                            >
                                                {matched ? "✓" : "—"} {label}
                                            </Typography>
                                        ))}
                                    </Grid>

                                    <Grid size={{ xs: 12, md: 3 }}>
                                        <Stack direction="row" spacing={2}>
                                            <Box>
                                                <Typography color="text.secondary" variant="caption">Possible entry</Typography>
                                                <Typography>₹{signal.entry_price.toLocaleString("en-IN")}</Typography>
                                            </Box>
                                            <Box>
                                                <Typography color="text.secondary" variant="caption">Invalidation</Typography>
                                                <Typography color="error.main">₹{signal.stop_loss.toLocaleString("en-IN")}</Typography>
                                            </Box>
                                            <Box>
                                                <Typography color="text.secondary" variant="caption">Scenario</Typography>
                                                <Typography color="success.main">₹{signal.target_price.toLocaleString("en-IN")}</Typography>
                                            </Box>
                                        </Stack>
                                        <Chip
                                            size="small"
                                            variant="outlined"
                                            label={`Risk/reward 1:${signal.risk_reward_ratio.toFixed(2)}`}
                                            sx={{ mt: 1 }}
                                        />
                                    </Grid>

                                    <Grid size={{ xs: 12, md: 2 }}>
                                        <Box sx={{ display: "flex", justifyContent: "space-between", mb: .75 }}>
                                            <Typography variant="caption">Rule quality</Typography>
                                            <Typography variant="caption">{signal.confirmation_score.toFixed(0)}/100</Typography>
                                        </Box>
                                        <LinearProgress variant="determinate" value={signal.confirmation_score} />
                                        <Typography variant="caption" color="text.secondary" sx={{ display: "block", mt: .75 }}>
                                            Ranking score, not success probability.
                                        </Typography>
                                    </Grid>

                                    <Grid size={{ xs: 12, md: 2 }}>
                                        {signal.rejection_reason ? (
                                            <Typography color="warning.main" variant="caption">
                                                Review: {signal.rejection_reason}
                                            </Typography>
                                        ) : (
                                            <Alert severity="success" icon={false} sx={{ py: .25 }}>
                                                Risk checks passed
                                            </Alert>
                                        )}
                                    </Grid>
                                </Grid>
                            </CardContent>
                        </Card>
                    </Grid>
                ))}
            </Grid>
        </Stack>
    );
}

export default Signals;
