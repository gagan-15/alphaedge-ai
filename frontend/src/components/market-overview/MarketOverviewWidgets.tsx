import { useEffect, useState } from "react";

import ArrowDownwardRoundedIcon from "@mui/icons-material/ArrowDownwardRounded";
import ArrowForwardRoundedIcon from "@mui/icons-material/ArrowForwardRounded";
import ArrowUpwardRoundedIcon from "@mui/icons-material/ArrowUpwardRounded";
import AutoAwesomeOutlinedIcon from "@mui/icons-material/AutoAwesomeOutlined";
import ErrorOutlineRoundedIcon from "@mui/icons-material/ErrorOutlineRounded";
import OpenInNewRoundedIcon from "@mui/icons-material/OpenInNewRounded";
import ShowChartRoundedIcon from "@mui/icons-material/ShowChartRounded";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Chip from "@mui/material/Chip";
import Collapse from "@mui/material/Collapse";
import Grid from "@mui/material/Grid";
import LinearProgress from "@mui/material/LinearProgress";
import Skeleton from "@mui/material/Skeleton";
import Stack from "@mui/material/Stack";
import Switch from "@mui/material/Switch";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import ToggleButton from "@mui/material/ToggleButton";
import ToggleButtonGroup from "@mui/material/ToggleButtonGroup";
import Tooltip from "@mui/material/Tooltip";
import Typography from "@mui/material/Typography";

const colors = {
    green: "#32d583",
    red: "#f97066",
    amber: "#fdb022",
    blue: "#6172f3",
    cyan: "#22d3ee",
    violet: "#9b8afb",
};

function useCountUp(target: number, duration = 700) {
    const [value, setValue] = useState(0);
    useEffect(() => {
        let frame = 0;
        const started = performance.now();
        const tick = (now: number) => {
            const progress = Math.min(1, (now - started) / duration);
            setValue(Math.round(target * (1 - (1 - progress) ** 3)));
            if (progress < 1) frame = requestAnimationFrame(tick);
        };
        frame = requestAnimationFrame(tick);
        return () => cancelAnimationFrame(frame);
    }, [duration, target]);
    return value;
}

export function WidgetLoading({ rows = 3 }: { rows?: number }) {
    return <Stack spacing={1.2}>{Array.from({ length: rows }, (_, index) => <Skeleton key={index} height={42} variant="rounded" />)}</Stack>;
}

export function WidgetEmpty({ message }: { message: string }) {
    return <Box sx={{ minHeight: 110, display: "grid", placeItems: "center", textAlign: "center", color: "text.secondary" }}>
        <Box><ErrorOutlineRoundedIcon /><Typography sx={{ mt: 1, fontSize: ".75rem" }}>{message}</Typography></Box>
    </Box>;
}

function StatusPill({ label, value, color }: { label: string; value: string; color: string }) {
    return <Box sx={{ px: 1.15, py: .75, borderRadius: 2, border: `1px solid ${color}35`, bgcolor: `${color}10` }}>
        <Typography color="text.secondary" sx={{ fontSize: ".58rem", textTransform: "uppercase", letterSpacing: ".08em" }}>{label}</Typography>
        <Typography sx={{ mt: .2, color, fontSize: ".72rem", fontWeight: 850 }}>{value}</Typography>
    </Box>;
}

function Stars({ value }: { value: number }) {
    return <Typography aria-label={`${value} out of 5`} sx={{ color: colors.amber, letterSpacing: ".08em", fontSize: ".78rem" }}>
        {"★".repeat(value)}<Box component="span" sx={{ color: "#334155" }}>{"★".repeat(5 - value)}</Box>
    </Typography>;
}

function CircularGauge({ value, label, color = colors.green }: { value: number; label: string; color?: string }) {
    const animated = useCountUp(value);
    return <Box sx={{ width: 132, height: 132, mx: "auto", borderRadius: "50%", p: "10px", background: `conic-gradient(${color} ${animated * 3.6}deg,#17263a 0)`, transition: "background .25s ease" }}>
        <Box sx={{ width: "100%", height: "100%", borderRadius: "50%", bgcolor: "#0b1728", display: "grid", placeItems: "center", textAlign: "center" }}>
            <Box><Typography sx={{ fontSize: "2rem", lineHeight: 1, fontWeight: 900 }}>{animated}</Typography><Typography color="text.secondary" sx={{ mt: .5, fontSize: ".66rem" }}>{label}</Typography></Box>
        </Box>
    </Box>;
}

export function AIMarketSummaryWidget() {
    const [expanded, setExpanded] = useState(false);
    return <Grid container spacing={2.5} sx={{ height: "100%", alignItems: "stretch" }}>
        <Grid size={{ xs: 12, lg: 9 }}>
            <Stack spacing={2}>
                <Stack direction="row" spacing={1.2} sx={{ alignItems: "center" }}>
                    <Box sx={{ width: 38, height: 38, display: "grid", placeItems: "center", borderRadius: 2, color: colors.violet, bgcolor: `${colors.violet}14` }}><AutoAwesomeOutlinedIcon /></Box>
                    <Box><Typography sx={{ fontSize: "1.05rem", fontWeight: 850 }}>Healthy participation supports the current uptrend</Typography><Typography color="text.secondary" sx={{ mt: .35, lineHeight: 1.6 }}>Financials and IT are leading while volatility remains controlled. Breadth is constructive, but selective weakness in metals argues against chasing every breakout.</Typography></Box>
                </Stack>
                <Stack direction="row" useFlexGap spacing={1} sx={{ flexWrap: "wrap" }}>
                    <StatusPill label="Trend" value="Bullish" color={colors.green} />
                    <StatusPill label="Breadth" value="Healthy" color={colors.green} />
                    <StatusPill label="Momentum" value="Positive" color={colors.cyan} />
                    <StatusPill label="Volatility" value="Controlled" color={colors.blue} />
                    <StatusPill label="Leadership" value="IT + Banks" color={colors.violet} />
                </Stack>
                <Collapse in={expanded}>
                    <Box sx={{ p: 1.5, borderRadius: 2, bgcolor: "rgba(155,138,251,.07)", border: "1px solid rgba(155,138,251,.18)" }}>
                        <Typography sx={{ fontWeight: 800, fontSize: ".72rem" }}>Why this interpretation?</Typography>
                        <Typography color="text.secondary" sx={{ mt: .6, fontSize: ".7rem", lineHeight: 1.6 }}>Advancers exceed decliners, most tracked stocks remain above medium-term averages, Bank Nifty leadership is positive, and India VIX remains below its recent stress range. This is transparent demo logic, not generated AI.</Typography>
                    </Box>
                </Collapse>
            </Stack>
        </Grid>
        <Grid size={{ xs: 12, lg: 3 }}>
            <Stack sx={{ height: "100%", justifyContent: "center", alignItems: "center" }}>
                <CircularGauge value={91} label="Confidence" color={colors.violet} />
                <Button size="small" sx={{ mt: 1 }} onClick={() => setExpanded((value) => !value)}>{expanded ? "Hide reasons" : "Why?"}</Button>
            </Stack>
        </Grid>
    </Grid>;
}

export function MarketHealthWidget() {
    const factors = [["Trend", 5], ["Participation", 4], ["Momentum", 4], ["Volatility", 4], ["Risk", 3]] as const;
    return <Tooltip title="Demo score combines trend, breadth, momentum, volatility and risk factors. It is not a prediction.">
        <Box>
            <CircularGauge value={87} label="Strong bullish" />
            <Stack spacing={.55} sx={{ mt: 1.5 }}>{factors.map(([label, value]) => <Stack key={label} direction="row" sx={{ justifyContent: "space-between" }}><Typography color="text.secondary" sx={{ fontSize: ".67rem" }}>{label}</Typography><Stars value={value} /></Stack>)}</Stack>
            <Typography color="text.secondary" sx={{ mt: 1.3, fontSize: ".58rem" }}>Updated 10:42 IST</Typography>
        </Box>
    </Tooltip>;
}

export function MarketRegimeWidget() {
    return <Stack sx={{ height: "100%", justifyContent: "space-between" }}>
        <Box>
            <Box sx={{ width: 54, height: 54, display: "grid", placeItems: "center", borderRadius: 3, bgcolor: `${colors.blue}12`, color: colors.blue }}><ShowChartRoundedIcon fontSize="large" /></Box>
            <Typography sx={{ mt: 1.5, fontSize: "1.35rem", fontWeight: 900 }}>Bull Expansion</Typography>
            <Typography color="text.secondary" sx={{ mt: .7, fontSize: ".72rem", lineHeight: 1.55 }}>Price trend and participation are expanding together.</Typography>
        </Box>
        <Box><Stack direction="row" sx={{ justifyContent: "space-between" }}><Typography color="text.secondary" sx={{ fontSize: ".68rem" }}>Regime probability</Typography><Typography sx={{ fontWeight: 850 }}>88%</Typography></Stack><LinearProgress value={88} variant="determinate" sx={{ mt: .7, height: 7 }} /></Box>
    </Stack>;
}

export function TradingBiasWidget() {
    return <Stack sx={{ height: "100%", justifyContent: "space-between" }}>
        <Box>
            <ArrowUpwardRoundedIcon sx={{ color: colors.green, fontSize: 56, transform: "rotate(35deg)" }} />
            <Typography sx={{ fontSize: "1.4rem", fontWeight: 900 }}>Long Bias</Typography>
        </Box>
        <Box>
            <Typography color="text.secondary" sx={{ fontSize: ".62rem", textTransform: "uppercase" }}>Preferred strategy</Typography>
            <Typography sx={{ mt: .45, fontWeight: 800 }}>Buy pullbacks · Momentum breakouts</Typography>
            <Typography color="error.main" sx={{ mt: 1, fontSize: ".69rem" }}>Avoid counter-trend shorts</Typography>
        </Box>
    </Stack>;
}

export function RiskMeterWidget() {
    const factors = [["Gap risk", "Low", colors.green], ["Liquidity", "Healthy", colors.green], ["Volatility", "Moderate", colors.amber], ["Trend stability", "High", colors.blue]];
    return <Stack>
        <Box sx={{ width: 170, height: 86, mx: "auto", overflow: "hidden", position: "relative" }}>
            <Box sx={{ width: 170, height: 170, borderRadius: "50%", background: `conic-gradient(from 270deg,${colors.green} 0 25%,${colors.amber} 25% 38%,${colors.red} 38% 50%,transparent 50%)`, p: "15px" }}>
                <Box sx={{ width: "100%", height: "100%", borderRadius: "50%", bgcolor: "#0b1728" }} />
            </Box>
            <Typography sx={{ position: "absolute", bottom: 0, width: "100%", textAlign: "center", fontWeight: 900, color: colors.amber }}>MEDIUM</Typography>
        </Box>
        <Stack spacing={.8} sx={{ mt: 1.5 }}>{factors.map(([label, value, color]) => <Stack key={label} direction="row" sx={{ justifyContent: "space-between" }}><Typography color="text.secondary" sx={{ fontSize: ".67rem" }}>{label}</Typography><Typography sx={{ color, fontSize: ".67rem", fontWeight: 800 }}>{value}</Typography></Stack>)}</Stack>
    </Stack>;
}

const chartProfiles = {
    "1D": { labels: ["09:15", "10:45", "12:15", "13:45", "15:30"], values: [2, 8, 5, 16, 13, 22, 18, 27, 31, 28, 36, 42] },
    "1W": { labels: ["Mon", "Tue", "Wed", "Thu", "Fri"], values: [-8, -2, 7, 4, 11, 17, 13, 20, 25, 22, 29, 34] },
    "1M": { labels: ["W1", "W2", "W3", "W4", "Today"], values: [-14, -8, -3, 6, 4, 12, 18, 15, 24, 28, 35, 39] },
    "3M": { labels: ["May", "Jun", "Jul", "Today"], values: [-25, -17, -9, 2, -4, 8, 14, 21, 18, 30, 38, 44] },
    "6M": { labels: ["Feb", "Mar", "Apr", "May", "Jun", "Jul"], values: [-32, -20, -24, -8, 3, 12, 7, 19, 28, 35, 31, 46] },
    "1Y": { labels: ["Jul '25", "Oct", "Jan '26", "Apr", "Jul"], values: [-40, -28, -35, -18, -6, 10, 3, 22, 17, 34, 42, 51] },
} as const;

export function ParticipationChartWidget() {
    const [range, setRange] = useState<keyof typeof chartProfiles>("1M");
    const [nifty, setNifty] = useState(true);
    const [bank, setBank] = useState(true);
    const [events, setEvents] = useState(false);
    const profile = chartProfiles[range];
    const points = profile.values.map((value, index) => `${index * 100 / (profile.values.length - 1)},${55 - value * .75}`).join(" ");
    const niftyPoints = profile.values.map((value, index) => `${index * 100 / (profile.values.length - 1)},${61 - value * .42 + Math.sin(index) * 2}`).join(" ");
    const bankPoints = profile.values.map((value, index) => `${index * 100 / (profile.values.length - 1)},${65 - value * .34 + Math.cos(index) * 3}`).join(" ");
    return <Stack sx={{ height: "100%" }}>
        <Stack direction={{ xs: "column", md: "row" }} spacing={1} sx={{ justifyContent: "space-between", alignItems: { md: "center" } }}>
            <ToggleButtonGroup exclusive size="small" value={range} onChange={(_, value) => value && setRange(value)}>
                {Object.keys(chartProfiles).map((value) => <ToggleButton key={value} value={value}>{value}</ToggleButton>)}
            </ToggleButtonGroup>
            <Stack direction="row" spacing={1.2} sx={{ alignItems: "center" }}>
                {([["Nifty", nifty, setNifty], ["BankNifty", bank, setBank], ["Events", events, setEvents]] as const).map(([label, checked, setter]) => <Stack key={label} direction="row" spacing={.3} sx={{ alignItems: "center" }}><Switch size="small" checked={checked} onChange={(event) => setter(event.target.checked)} /><Typography sx={{ fontSize: ".65rem" }}>{label}</Typography></Stack>)}
            </Stack>
        </Stack>
        <Box sx={{ position: "relative", flex: 1, minHeight: 260, mt: 1.5 }}>
            <Box sx={{ position: "absolute", left: 0, top: 0, bottom: 24, width: 42, display: "flex", flexDirection: "column", justifyContent: "space-between" }}>{["+50", "+25", "0", "-25"].map((label) => <Typography key={label} color="text.secondary" sx={{ fontSize: ".58rem" }}>{label}</Typography>)}</Box>
            <Tooltip title="Demo point: Advances 1,682 · Declines 802 · Net breadth +880 · Health 87 · Highs 156 · Lows 23" followCursor>
                <Box component="svg" viewBox="0 0 100 100" preserveAspectRatio="none" sx={{ position: "absolute", left: 44, width: "calc(100% - 44px)", height: "calc(100% - 24px)" }}>
                    {[15, 40, 65, 90].map((y) => <line key={y} x1="0" y1={y} x2="100" y2={y} stroke="#213149" strokeWidth=".45" />)}
                    <defs><linearGradient id="participationFill" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor={colors.green} stopOpacity=".25" /><stop offset="100%" stopColor={colors.green} stopOpacity="0" /></linearGradient></defs>
                    <polygon points={`0,100 ${points} 100,100`} fill="url(#participationFill)" />
                    <polyline points={points} fill="none" stroke={colors.green} strokeWidth="1.8" vectorEffect="non-scaling-stroke" />
                    {nifty && <polyline points={niftyPoints} fill="none" stroke={colors.blue} strokeWidth="1.15" vectorEffect="non-scaling-stroke" />}
                    {bank && <polyline points={bankPoints} fill="none" stroke={colors.amber} strokeWidth="1.15" vectorEffect="non-scaling-stroke" />}
                    {events && <line x1="72" x2="72" y1="5" y2="95" stroke={colors.violet} strokeDasharray="2 2" />}
                </Box>
            </Tooltip>
            <Stack direction="row" sx={{ position: "absolute", left: 44, right: 0, bottom: 0, justifyContent: "space-between" }}>{profile.labels.map((label) => <Typography key={label} color="text.secondary" sx={{ fontSize: ".58rem" }}>{label}</Typography>)}</Stack>
        </Box>
        <Box sx={{ mt: 1.5, p: 1.2, borderRadius: 2, bgcolor: "rgba(50,213,131,.06)", border: "1px solid rgba(50,213,131,.14)" }}><Typography sx={{ color: colors.green, fontSize: ".7rem", fontWeight: 800 }}>AI insight</Typography><Typography color="text.secondary" sx={{ mt: .35, fontSize: ".68rem" }}>Participation has improved over the selected period and currently supports the broader market trend.</Typography></Box>
    </Stack>;
}

const sectorRows = [
    ["IT", "8/10", "↑↑", "Strong", "Leading", colors.green],
    ["Bank", "7/10", "↑", "Positive", "Leading", colors.green],
    ["FMCG", "6/10", "→", "Stable", "Improving", colors.cyan],
    ["Auto", "4/10", "↓", "Soft", "Weakening", colors.amber],
    ["Metal", "2/10", "↓↓", "Negative", "Lagging", colors.red],
] as const;

export function SectorRotationWidget() {
    const [heatmap, setHeatmap] = useState(false);
    return <Stack sx={{ height: "100%" }}>
        {heatmap ? <Grid container spacing={1} sx={{ flex: 1 }}>{sectorRows.map(([sector, strength, , , status, color]) => <Grid key={sector} size={{ xs: 6, sm: 4 }}><Box sx={{ height: "100%", minHeight: 72, p: 1.2, borderRadius: 2, bgcolor: `${color}18`, border: `1px solid ${color}45` }}><Typography sx={{ fontWeight: 900 }}>{sector}</Typography><Typography sx={{ color, fontSize: "1.1rem", fontWeight: 900 }}>{strength}</Typography><Typography color="text.secondary" sx={{ fontSize: ".58rem" }}>{status}</Typography></Box></Grid>)}</Grid> :
            <Box sx={{ overflowX: "auto", flex: 1 }}><Table size="small"><TableHead><TableRow>{["Sector", "Strength", "Money Flow", "Trend", "Status"].map((heading) => <TableCell key={heading}>{heading}</TableCell>)}</TableRow></TableHead><TableBody>{sectorRows.map(([sector, strength, flow, trend, status, color]) => <TableRow key={sector} hover><TableCell sx={{ fontWeight: 850 }}>{sector}</TableCell><TableCell>{strength}</TableCell><TableCell sx={{ color, fontWeight: 900 }}>{flow}</TableCell><TableCell>{trend}</TableCell><TableCell><Chip size="small" label={status} sx={{ color, bgcolor: `${color}12`, border: `1px solid ${color}30` }} /></TableCell></TableRow>)}</TableBody></Table></Box>}
        <Button size="small" endIcon={<OpenInNewRoundedIcon />} onClick={() => setHeatmap((value) => !value)} sx={{ mt: 1.5, alignSelf: "flex-start" }}>{heatmap ? "View Table" : "View Heatmap"}</Button>
    </Stack>;
}

const breadthMetrics = [
    ["Advancing", 1682, "+62", "Advancers in tracked universe"], ["Declining", 802, "-18", "Decliners in tracked universe"], ["Unchanged", 126, "+4", "Unchanged symbols"],
    ["52W Highs", 156, "+21", "New 52-week highs"], ["52W Lows", 23, "-6", "New 52-week lows"], ["Above 20 EMA", 1764, "+3.2%", "Stocks above 20-day EMA"],
    ["Above 50 EMA", 1521, "+2.1%", "Stocks above 50-day EMA"], ["Above 200 EMA", 1318, "+1.4%", "Stocks above 200-day EMA"], ["Gap Ups", 84, "+12", "Opening above prior high"],
    ["Gap Downs", 31, "-5", "Opening below prior low"], ["Upper Circuit", 42, "+7", "Symbols at upper circuit"], ["Lower Circuit", 11, "-2", "Symbols at lower circuit"],
    ["High Vol. Advances", 218, "+28", "Advancers with elevated volume"], ["High Vol. Declines", 94, "-9", "Decliners with elevated volume"], ["Midcap Participation", 68, "+4%", "Midcap participation percentage"], ["Smallcap Participation", 61, "+2%", "Smallcap participation percentage"],
] as const;

export function MarketBreadthWidget() {
    return <Grid container spacing={1}>{breadthMetrics.map(([label, value, trend, help]) => <Grid key={label} size={{ xs: 6, sm: 4, lg: 3 }}><Tooltip title={help}><Box sx={{ p: 1.05, borderRadius: 2, border: "1px solid rgba(143,161,184,.14)", bgcolor: "rgba(4,12,25,.24)", transition: "transform .18s ease,border-color .18s ease", "&:hover": { transform: "translateY(-2px)", borderColor: "rgba(97,114,243,.45)" } }}><Typography color="text.secondary" noWrap sx={{ fontSize: ".55rem" }}>{label}</Typography><Stack direction="row" spacing={.55} sx={{ mt: .35, alignItems: "baseline" }}><Typography sx={{ fontWeight: 900 }}>{value.toLocaleString("en-IN")}</Typography><Typography sx={{ color: String(trend).startsWith("-") ? colors.red : colors.green, fontSize: ".56rem" }}>{trend}</Typography></Stack></Box></Tooltip></Grid>)}</Grid>;
}

export function InstitutionalFlowWidget() {
    const rows = [["FII", "-1,248 Cr", "Selling"], ["DII", "+2,129 Cr", "Buying"], ["Retail", "+684 Cr", "Buying"], ["Proprietary", "-214 Cr", "Selling"]];
    return <Stack spacing={1.1}>{rows.map(([label, value, state]) => <Stack key={label} direction="row" sx={{ justifyContent: "space-between", alignItems: "center", p: 1, borderBottom: "1px solid rgba(143,161,184,.12)" }}><Box><Typography sx={{ fontWeight: 800 }}>{label}</Typography><Typography color="text.secondary" sx={{ fontSize: ".6rem" }}>Net {state}</Typography></Box><Stack direction="row" spacing={.5} sx={{ alignItems: "center", color: value.startsWith("+") ? colors.green : colors.red }}>{value.startsWith("+") ? <ArrowUpwardRoundedIcon fontSize="small" /> : <ArrowDownwardRoundedIcon fontSize="small" />}<Typography sx={{ fontWeight: 850 }}>{value}</Typography></Stack></Stack>)}<Typography color="text.secondary" sx={{ fontSize: ".58rem" }}>Demo values · Updated after previous session</Typography></Stack>;
}

export function IndiaVixWidget() {
    return <Stack sx={{ height: "100%", justifyContent: "space-between" }}>
        <Box><Stack direction="row" sx={{ alignItems: "baseline", gap: 1 }}><Typography sx={{ fontSize: "2.5rem", fontWeight: 900 }}>12.45</Typography><Typography color="error.main" sx={{ fontWeight: 850 }}>-2.35%</Typography></Stack><Chip size="small" label="LOW VOLATILITY" sx={{ mt: .6, color: colors.green, bgcolor: `${colors.green}12` }} /></Box>
        <Box component="svg" viewBox="0 0 100 35" preserveAspectRatio="none" sx={{ width: "100%", height: 70 }}><polyline points="0,9 10,13 20,11 30,18 40,15 50,22 60,19 70,25 80,21 90,27 100,24" fill="none" stroke={colors.cyan} strokeWidth="2" vectorEffect="non-scaling-stroke" /></Box>
        <Typography color="text.secondary" sx={{ fontSize: ".68rem", lineHeight: 1.5 }}>Volatility is controlled. Sudden event risk can still create gaps.</Typography>
    </Stack>;
}

export function SentimentWidget() {
    return <Grid container spacing={2} sx={{ alignItems: "center" }}><Grid size={{ xs: 12, sm: 6 }}><CircularGauge value={72} label="Optimistic" color={colors.green} /></Grid><Grid size={{ xs: 12, sm: 6 }}><Stack spacing={1}>{[["FII", "Cautious", colors.amber], ["Retail", "Neutral", colors.blue], ["Options", "Bullish", colors.green]].map(([label, value, color]) => <Stack key={label} direction="row" sx={{ justifyContent: "space-between" }}><Typography color="text.secondary" sx={{ fontSize: ".68rem" }}>{label}</Typography><Typography sx={{ color, fontSize: ".68rem", fontWeight: 850 }}>{value}</Typography></Stack>)}</Stack></Grid></Grid>;
}

export function OpportunitiesWidget() {
    const items = [["Demand Zones", 18, colors.blue], ["Momentum", 12, colors.green], ["Breakouts", 7, colors.violet], ["Pullbacks", 14, colors.cyan], ["Trend Continuation", 9, colors.amber]];
    const [selected, setSelected] = useState("");
    return <Stack spacing={1}><Grid container spacing={1.1}>{items.map(([label, count, color]) => <Grid key={label as string} size={{ xs: 12, sm: 6 }}><Box sx={{ p: 1.25, borderRadius: 2, border: "1px solid rgba(143,161,184,.15)", transition: "transform .18s ease", "&:hover": { transform: "translateY(-2px)" } }}><Stack direction="row" sx={{ justifyContent: "space-between", alignItems: "center" }}><Box><Typography sx={{ fontWeight: 800, fontSize: ".72rem" }}>{label}</Typography><Typography sx={{ color, fontSize: "1.35rem", fontWeight: 900 }}>{count}</Typography></Box><Button size="small" endIcon={<ArrowForwardRoundedIcon />} onClick={() => setSelected(String(label))}>Scan</Button></Stack></Box></Grid>)}</Grid>{selected && <Typography color="primary.light" sx={{ fontSize: ".65rem" }}>{selected} selected. Scanner hand-off will use the existing scanner route in the integration phase.</Typography>}</Stack>;
}

export function SmartAlertsWidget() {
    const alerts = [["Breadth improving", "High", "2m", colors.green], ["Bank Nifty leading", "Medium", "8m", colors.blue], ["Metal sector weakening", "Medium", "14m", colors.amber], ["Smallcaps outperforming", "Info", "21m", colors.cyan]];
    return <Stack spacing={1}>{alerts.map(([message, severity, time, color]) => <Stack key={message} direction="row" spacing={1.1} sx={{ alignItems: "center", p: 1.1, borderRadius: 2, bgcolor: "rgba(4,12,25,.25)", border: "1px solid rgba(143,161,184,.12)" }}><Box sx={{ width: 8, height: 8, borderRadius: "50%", bgcolor: color, boxShadow: `0 0 10px ${color}` }} /><Box sx={{ flex: 1 }}><Typography sx={{ fontSize: ".72rem", fontWeight: 800 }}>{message}</Typography><Typography color="text.secondary" sx={{ fontSize: ".57rem" }}>{severity} severity</Typography></Box><Typography color="text.secondary" sx={{ fontSize: ".6rem" }}>{time}</Typography></Stack>)}</Stack>;
}

export function VerdictWidget() {
    const items = [["Market", "Bullish", colors.green], ["Participation", "Healthy", colors.green], ["Momentum", "Positive", colors.cyan], ["Risk", "Moderate", colors.amber], ["Strategy", "Buy pullbacks", colors.blue], ["Avoid", "Weak-sector breakouts", colors.red]];
    return <Grid container spacing={2.5} sx={{ alignItems: "center" }}><Grid size={{ xs: 12, lg: 9 }}><Grid container spacing={1.1}>{items.map(([label, value, color]) => <Grid key={label} size={{ xs: 12, sm: 6, md: 4 }}><Box sx={{ p: 1.2, borderRadius: 2, bgcolor: `${color}09`, border: `1px solid ${color}25` }}><Typography color="text.secondary" sx={{ fontSize: ".58rem", textTransform: "uppercase" }}>{label}</Typography><Typography sx={{ mt: .3, color, fontWeight: 850 }}>{value}</Typography></Box></Grid>)}</Grid></Grid><Grid size={{ xs: 12, lg: 3 }}><CircularGauge value={89} label="Overall confidence" color={colors.violet} /></Grid></Grid>;
}
