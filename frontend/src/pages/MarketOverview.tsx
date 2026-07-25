import { useMemo, useState } from "react";

import Box from "@mui/material/Box";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Chip from "@mui/material/Chip";
import Grid from "@mui/material/Grid";
import LinearProgress from "@mui/material/LinearProgress";
import Stack from "@mui/material/Stack";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import ToggleButton from "@mui/material/ToggleButton";
import ToggleButtonGroup from "@mui/material/ToggleButtonGroup";
import Typography from "@mui/material/Typography";

const indices = [
    { name: "NIFTY 50", value: "24,731.45", change: 0.85, color: "#32d583" },
    { name: "SENSEX", value: "81,214.85", change: 0.78, color: "#fdb022" },
    { name: "BANK NIFTY", value: "54,372.15", change: 1.15, color: "#6172f3" },
    { name: "FINNIFTY", value: "24,125.20", change: 1.02, color: "#22d3ee" },
    { name: "INDIA VIX", value: "12.45", change: -2.35, color: "#f04438" },
];

const series = [
    { name: "NIFTY 50", color: "#32d583", values: [42, 45, 49, 52, 51, 58, 56, 64, 61, 69, 65, 73] },
    { name: "SENSEX", color: "#fdb022", values: [38, 41, 40, 47, 45, 52, 50, 57, 59, 63, 60, 66] },
    { name: "BANK NIFTY", color: "#6172f3", values: [36, 40, 37, 44, 48, 46, 54, 52, 59, 56, 64, 60] },
    { name: "FINNIFTY", color: "#22d3ee", values: [33, 36, 39, 35, 43, 40, 48, 44, 51, 49, 57, 61] },
];

const movers = [
    ["RELIANCE", "2,978.45", "+0.83%", "12.45M"],
    ["TCS", "3,584.75", "-0.41%", "20.15M"],
    ["HDFCBANK", "1,654.20", "+1.12%", "18.22M"],
    ["INFY", "1,512.10", "+0.35%", "13.12M"],
    ["ICICIBANK", "1,234.55", "+0.70%", "11.84M"],
];

function MiniSpark({ color, down = false }: { color: string; down?: boolean }) {
    return <Box component="svg" viewBox="0 0 100 28" sx={{ width: "100%", height: 28 }}>
        <polyline points={down ? "0,6 12,9 24,8 36,15 48,13 60,20 72,17 84,23 100,25" : "0,24 12,21 24,22 36,15 48,17 60,10 72,13 84,7 100,3"} fill="none" stroke={color} strokeWidth="2" />
    </Box>;
}

export default function MarketOverview() {
    const [range, setRange] = useState("1M");
    const lines = useMemo(() => series.map((item) => {
        const points = item.values.map((value, index) => `${index * (100 / 11)},${100 - value}`).join(" ");
        return { ...item, points };
    }), []);

    return <Stack spacing={1.35}>
        <Stack direction={{ xs: "column", md: "row" }} sx={{ justifyContent: "space-between", alignItems: { md: "center" } }}>
            <Box><Typography variant="h4">Market Overview</Typography><Typography color="text.secondary">Index performance, participation and sector context.</Typography></Box>
            <Chip color="warning" label="DELAYED DEVELOPMENT DATA" />
        </Stack>
        <Grid container spacing={1.1}>{indices.map((item) => <Grid key={item.name} size={{ xs: 12, sm: 6, lg: 2.4 }}>
            <Card><CardContent sx={{ p: 1.6, "&:last-child": { pb: 1.4 } }}>
                <Typography variant="caption" color="text.secondary">{item.name}</Typography>
                <Stack direction="row" sx={{ justifyContent: "space-between", alignItems: "end", mt: .5 }}>
                    <Box><Typography variant="h5">{item.value}</Typography><Typography variant="body2" sx={{ color: item.change >= 0 ? "success.main" : "error.main", fontWeight: 800 }}>{item.change >= 0 ? "▲" : "▼"} {Math.abs(item.change).toFixed(2)}%</Typography></Box>
                    <Box sx={{ width: 74 }}><MiniSpark color={item.color} down={item.change < 0} /></Box>
                </Stack>
            </CardContent></Card>
        </Grid>)}</Grid>
        <Grid container spacing={1.35}>
            <Grid size={{ xs: 12, xl: 8.5 }}><Card sx={{ height: 390 }}><CardContent sx={{ height: "100%", p: 1.75 }}>
                <Stack direction="row" sx={{ justifyContent: "space-between", alignItems: "center" }}>
                    <Box><Typography variant="h6">Relative Market Performance</Typography><Typography variant="caption" color="text.secondary">Normalized index movement · illustrative series</Typography></Box>
                    <ToggleButtonGroup size="small" exclusive value={range} onChange={(_, value) => value && setRange(value)}>
                        {["1D", "1W", "1M", "3M", "1Y"].map((x) => <ToggleButton key={x} value={x}>{x}</ToggleButton>)}
                    </ToggleButtonGroup>
                </Stack>
                <Stack direction="row" spacing={2} sx={{ mt: 1.5 }}>{lines.map((item) => <Stack key={item.name} direction="row" spacing={.6} sx={{ alignItems: "center" }}>
                    <Box sx={{ width: 8, height: 8, borderRadius: "50%", bgcolor: item.color }} /><Typography variant="caption">{item.name}</Typography>
                </Stack>)}</Stack>
                <Box sx={{ position: "relative", height: 270, mt: 1 }}>
                    <Box sx={{ position: "absolute", left: 0, top: 8, bottom: 24, width: 34, display: "flex", flexDirection: "column", justifyContent: "space-between" }}>
                        {["+4%", "+2%", "0%", "-2%"].map((x) => <Typography key={x} variant="caption" color="text.secondary">{x}</Typography>)}
                    </Box>
                    <Box component="svg" viewBox="0 0 100 100" preserveAspectRatio="none" sx={{ position: "absolute", left: 38, right: 0, width: "calc(100% - 38px)", height: 235 }}>
                        <defs><linearGradient id="marketGlow" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#32d583" stopOpacity=".16" /><stop offset="1" stopColor="#32d583" stopOpacity="0" /></linearGradient></defs>
                        {[15, 40, 65, 90].map((y) => <line key={y} x1="0" y1={y} x2="100" y2={y} stroke="#20314a" strokeWidth=".45" />)}
                        <polygon points={`0,100 ${lines[0].points} 100,100`} fill="url(#marketGlow)" />
                        {lines.map((item) => <polyline key={item.name} points={item.points} fill="none" stroke={item.color} strokeWidth="1.25" vectorEffect="non-scaling-stroke" />)}
                    </Box>
                    <Stack direction="row" sx={{ position: "absolute", left: 38, right: 0, bottom: 0, justifyContent: "space-between" }}>
                        {["Jul 01", "Jul 08", "Jul 15", "Jul 22", "Today"].map((x) => <Typography key={x} variant="caption" color="text.secondary">{x}</Typography>)}
                    </Stack>
                </Box>
            </CardContent></Card></Grid>
            <Grid size={{ xs: 12, xl: 3.5 }}><Card sx={{ height: 390 }}><CardContent sx={{ p: 1.75 }}>
                <Typography variant="h6">Market Breadth</Typography><Typography variant="caption" color="text.secondary">Tracked-symbol participation</Typography>
                <Stack direction="row" spacing={2} sx={{ alignItems: "center", my: 2.5 }}>
                    <Box sx={{ width: 128, height: 128, borderRadius: "50%", background: "conic-gradient(#32d583 0 62%, #f04438 62% 95%, #667085 95%)", position: "relative", "&::after": { content: '""', position: "absolute", inset: 24, borderRadius: "50%", bgcolor: "background.paper" } }} />
                    <Stack spacing={1.2}>{[["Advancing", "1,682", "#32d583"], ["Declining", "802", "#f04438"], ["Unchanged", "126", "#98a2b3"]].map(([label, value, color]) => <Box key={label}><Typography variant="caption" sx={{ color }}>{label}</Typography><Typography sx={{ fontWeight: 850 }}>{value}</Typography></Box>)}</Stack>
                </Stack>
                <Box sx={{ p: 1.5, borderRadius: 2, bgcolor: "rgba(50,213,131,.07)", border: "1px solid rgba(50,213,131,.18)" }}><Typography variant="caption" color="text.secondary">Participation reading</Typography><Typography variant="h5" color="success.main">Broadly positive</Typography><Typography variant="caption">62% of tracked symbols advancing</Typography></Box>
            </CardContent></Card></Grid>
        </Grid>
        <Grid container spacing={1.35}>
            <Grid size={{ xs: 12, lg: 7 }}><Card><CardContent sx={{ p: 1.5 }}><Typography variant="h6" sx={{ mb: .75 }}>Top Market Movers</Typography>
                <Table size="small"><TableHead><TableRow>{["Symbol", "Price", "Change", "Volume"].map((x) => <TableCell key={x}>{x}</TableCell>)}</TableRow></TableHead><TableBody>{movers.map((row) => <TableRow key={row[0]} hover>{row.map((value, index) => <TableCell key={value} sx={{ fontWeight: index === 0 ? 800 : 500, color: index === 2 ? (value.startsWith("+") ? "success.main" : "error.main") : undefined }}>{value}</TableCell>)}</TableRow>)}</TableBody></Table>
            </CardContent></Card></Grid>
            <Grid size={{ xs: 12, lg: 5 }}><Card><CardContent sx={{ p: 1.5 }}><Typography variant="h6">Sector Performance</Typography>
                {[["Nifty IT", 82, "+1.62%"], ["Nifty Bank", 69, "+1.15%"], ["Nifty FMCG", 58, "+0.98%"], ["Nifty Auto", 34, "-0.32%"], ["Nifty Metal", 27, "-0.85%"]].map(([name, value, change]) => <Box key={name as string} sx={{ mt: 1.15 }}><Stack direction="row" sx={{ justifyContent: "space-between" }}><Typography variant="body2">{name}</Typography><Typography variant="body2" sx={{ color: (change as string).startsWith("+") ? "success.main" : "error.main" }}>{change}</Typography></Stack><LinearProgress variant="determinate" value={value as number} color={(change as string).startsWith("+") ? "success" : "error"} sx={{ mt: .45, height: 5 }} /></Box>)}
            </CardContent></Card></Grid>
        </Grid>
    </Stack>;
}
