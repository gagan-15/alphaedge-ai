import { useMemo } from "react";

import DownloadOutlinedIcon from "@mui/icons-material/DownloadOutlined";
import Alert from "@mui/material/Alert";
import Button from "@mui/material/Button";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Grid from "@mui/material/Grid";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";

function readArray(key: string) {
    try {
        const value = JSON.parse(localStorage.getItem(key) ?? "[]");
        return Array.isArray(value) ? value : [];
    } catch { return []; }
}

export default function Reports() {
    const report = useMemo(() => ({
        generated_at: new Date().toISOString(),
        holdings: readArray("alphaedge.local.holdings"),
        watchlist: readArray("alphaedge.local.watchlist"),
        alerts: readArray("alphaedge.local.alerts"),
        strategies: readArray("alphaedge.local.strategies"),
        disclaimer: "Research and educational use only. No broker execution or guaranteed outcomes.",
    }), []);

    function download() {
        const url = URL.createObjectURL(new Blob([JSON.stringify(report, null, 2)], { type: "application/json" }));
        const link = document.createElement("a");
        link.href = url;
        link.download = `alphaedge-research-report-${new Date().toISOString().slice(0, 10)}.json`;
        link.click();
        URL.revokeObjectURL(url);
    }

    return <Stack spacing={1.5}>
        <Stack direction="row" sx={{ justifyContent: "space-between", alignItems: "center" }}>
            <div><Typography variant="h4">Research Reports</Typography><Typography color="text.secondary">Export a local snapshot of your research workspace.</Typography></div>
            <Button variant="contained" startIcon={<DownloadOutlinedIcon />} onClick={download}>Download JSON</Button>
        </Stack>
        <Grid container spacing={1.5}>{[
            ["Holdings", report.holdings.length],
            ["Watchlist symbols", report.watchlist.length],
            ["Alerts", report.alerts.length],
            ["Strategies", report.strategies.length],
        ].map(([label, value]) => <Grid key={label as string} size={{ xs: 12, sm: 6, lg: 3 }}><Card><CardContent><Typography color="text.secondary">{label}</Typography><Typography variant="h4">{value}</Typography></CardContent></Card></Grid>)}</Grid>
        <Card><CardContent><Typography variant="h6">Included data</Typography><Typography color="text.secondary" sx={{ mt: 1 }}>Browser-local holdings, watchlist, alerts and strategy templates. Passwords, tokens and direct personal details are never included.</Typography></CardContent></Card>
        <Alert severity="warning">This export is not a performance statement, tax report or investment recommendation.</Alert>
    </Stack>;
}
