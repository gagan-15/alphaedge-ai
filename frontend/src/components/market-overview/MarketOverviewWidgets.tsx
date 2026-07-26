import { useEffect, useState } from "react";

import ArrowDownwardRoundedIcon from "@mui/icons-material/ArrowDownwardRounded";
import ArrowForwardRoundedIcon from "@mui/icons-material/ArrowForwardRounded";
import ArrowUpwardRoundedIcon from "@mui/icons-material/ArrowUpwardRounded";
import AutoAwesomeOutlinedIcon from "@mui/icons-material/AutoAwesomeOutlined";
import CheckCircleOutlineRoundedIcon from "@mui/icons-material/CheckCircleOutlineRounded";
import ErrorOutlineRoundedIcon from "@mui/icons-material/ErrorOutlineRounded";
import OpenInNewRoundedIcon from "@mui/icons-material/OpenInNewRounded";
import ShowChartRoundedIcon from "@mui/icons-material/ShowChartRounded";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Chip from "@mui/material/Chip";
import Drawer from "@mui/material/Drawer";
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
import { Link as RouterLink } from "react-router-dom";

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

interface ExecutiveMetric {
    label: string;
    value: string;
    help: string;
    tone: "positive" | "neutral" | "caution";
}

interface ExecutiveSummaryData {
    updatedAt: string;
    marketStatus: string;
    confidence: number;
    participation: number;
    leaders: string[];
    laggards: string[];
    volatility: string;
    focus: string[];
    avoid: string;
    metrics: ExecutiveMetric[];
    reasons: string[];
}

const demoExecutiveSummary: ExecutiveSummaryData = {
    updatedAt: "09:18 AM",
    marketStatus: "Market Open",
    confidence: 91,
    participation: 72,
    leaders: ["Financials", "IT"],
    laggards: ["Metal", "Auto"],
    volatility: "below its recent average, so price swings are still controlled",
    focus: ["IT stocks after a small fall", "Banking stocks moving up strongly", "Stocks doing better than the market"],
    avoid: "Buying breakouts in weak sectors",
    metrics: [
        { label: "Today's Market", value: "Looking Healthy", help: "The main market indexes are rising and the wider market is supporting the move.", tone: "positive" },
        { label: "Most Stocks", value: "Going Up", help: "More than 65% of tracked stocks are rising today.", tone: "positive" },
        { label: "Market Strength", value: "Positive", help: "Recent price moves still show more buying than selling.", tone: "positive" },
        { label: "Strongest Sectors", value: "Technology + Banking", help: "Technology and banking stocks are doing better than most other sectors.", tone: "positive" },
        { label: "Price Movement", value: "Stable", help: "Expected market price swings remain controlled.", tone: "neutral" },
        { label: "Big Investors", value: "Mixed Buying", help: "Indian institutions are buying, while foreign institutions remain careful.", tone: "caution" },
        { label: "Current Trend", value: "Strong Rise", help: "The market is rising and more stocks are joining the move.", tone: "positive" },
    ],
    reasons: [
        "Around 72% of tracked stocks are rising today.",
        "Technology and Banking are the strongest sectors.",
        "Market fear remains low.",
        "More companies are making new highs than new lows.",
        "More stocks are joining the market rise.",
    ],
};

function ExecutiveStatusChip({ metric }: { metric: ExecutiveMetric }) {
    const toneColor = metric.tone === "positive" ? colors.green : metric.tone === "caution" ? colors.amber : colors.blue;
    return <Tooltip title={metric.help} arrow>
        <Stack
            direction="row"
            spacing={1}
            sx={{
                minWidth: 150,
                flex: "1 1 150px",
                p: 1.1,
                alignItems: "center",
                borderRadius: 2,
                border: "1px solid rgba(143,161,184,.16)",
                bgcolor: "rgba(4,12,25,.2)",
                transition: "transform .18s ease,border-color .18s ease",
                "&:hover": { transform: "translateY(-2px)", borderColor: `${toneColor}55` },
            }}
        >
            <Box sx={{ width: 27, height: 27, flex: "0 0 auto", display: "grid", placeItems: "center", borderRadius: 1.4, color: toneColor, bgcolor: `${toneColor}10` }}>
                <CheckCircleOutlineRoundedIcon sx={{ fontSize: 16 }} />
            </Box>
            <Box sx={{ minWidth: 0 }}>
                <Typography color="text.secondary" sx={{ fontSize: ".55rem", textTransform: "uppercase", letterSpacing: ".07em" }}>{metric.label}</Typography>
                <Typography noWrap sx={{ mt: .15, color: toneColor, fontSize: ".7rem", fontWeight: 850 }}>{metric.value}</Typography>
            </Box>
        </Stack>
    </Tooltip>;
}

export function AIMarketSummaryWidget({
    data = demoExecutiveSummary,
    loading = false,
}: {
    data?: ExecutiveSummaryData | null;
    loading?: boolean;
}) {
    const [whyOpen, setWhyOpen] = useState(false);
    const animatedScore = useCountUp(data?.confidence ?? 0);
    if (loading) return <WidgetLoading rows={5} />;
    if (!data) return <WidgetEmpty message="AI Summary unavailable. Waiting for validated market intelligence." />;
    const headline = data.participation >= 65
        ? "More stocks are joining the market rise. This is a healthy sign."
        : data.participation >= 50
            ? "The market is rising, but only some stocks are taking part."
            : "The main indexes are rising, but too few stocks are joining the move.";
    const explanation = [
        "Today's market is looking healthy.",
        `About ${data.participation}% of tracked stocks are rising, so the move is not limited to a few large companies.`,
        `${data.leaders.join(" and ")} are doing well, while price movement remains stable.`,
        "Look for quality buying opportunities, but avoid stocks that have already risen sharply.",
    ];
    return <Stack spacing={2.2}>
        <Grid container spacing={2.5} sx={{ alignItems: "stretch" }}>
            <Grid size={{ xs: 12, lg: 9 }}>
                <Stack spacing={2}>
                    <Stack direction="row" spacing={1.15} sx={{ alignItems: "center" }}>
                        <Box sx={{ width: 38, height: 38, display: "grid", placeItems: "center", borderRadius: 2, color: colors.violet, bgcolor: `${colors.violet}10` }}><AutoAwesomeOutlinedIcon /></Box>
                        <Box>
                            <Typography sx={{ fontSize: ".62rem", fontWeight: 850, letterSpacing: ".12em", color: "primary.light" }}>TODAY'S MARKET EXPLAINED</Typography>
                            <Stack direction="row" spacing={1} sx={{ mt: .35, alignItems: "center", flexWrap: "wrap" }}>
                                <Typography color="text.secondary" sx={{ fontSize: ".62rem" }}>Updated {data.updatedAt}</Typography>
                                <Box sx={{ width: 3, height: 3, borderRadius: "50%", bgcolor: "text.secondary" }} />
                                <Typography sx={{ color: colors.green, fontSize: ".62rem", fontWeight: 800 }}>{data.marketStatus}</Typography>
                            </Stack>
                        </Box>
                    </Stack>
                    <Box sx={{ animation: "executiveHeadline .45s ease both", "@keyframes executiveHeadline": { from: { opacity: 0, transform: "translateY(5px)" }, to: { opacity: 1, transform: "translateY(0)" } } }}>
                        <Typography sx={{ fontSize: { xs: "1.35rem", md: "1.8rem" }, lineHeight: 1.2, letterSpacing: "-.025em", fontWeight: 900 }}>{headline}</Typography>
                        <Stack spacing={.45} sx={{ mt: 1.1, maxWidth: 940 }}>
                            {explanation.map((sentence) => <Typography key={sentence} color="text.secondary" sx={{ fontSize: ".76rem", lineHeight: 1.55 }}>{sentence}</Typography>)}
                        </Stack>
                    </Box>
                    <Stack direction="row" useFlexGap spacing={1} sx={{ flexWrap: "wrap" }}>
                        {data.metrics.map((metric) => <ExecutiveStatusChip key={metric.label} metric={metric} />)}
                    </Stack>
                </Stack>
            </Grid>
            <Grid size={{ xs: 12, lg: 3 }}>
                <Stack sx={{ height: "100%", justifyContent: "center", alignItems: "center", borderLeft: { lg: "1px solid rgba(143,161,184,.14)" } }}>
                    <Box sx={{ width: 142, height: 142, borderRadius: "50%", p: "10px", background: `conic-gradient(${colors.violet} ${animatedScore * 3.6}deg,#17263a 0)` }}>
                        <Box sx={{ width: "100%", height: "100%", borderRadius: "50%", bgcolor: "#0b1728", display: "grid", placeItems: "center", textAlign: "center" }}>
                            <Box><Typography sx={{ fontSize: "1.75rem", lineHeight: 1, fontWeight: 900 }}>{animatedScore} <Box component="span" sx={{ fontSize: ".7rem", color: "text.secondary" }}>/ 100</Box></Typography><Typography sx={{ mt: .7, color: colors.green, fontSize: ".66rem", fontWeight: 800 }}>Market looks Healthy</Typography></Box>
                        </Box>
                    </Box>
                    <Typography color="text.secondary" sx={{ mt: 1, maxWidth: 190, textAlign: "center", fontSize: ".58rem" }}>This score shows the overall health of today's market.</Typography>
                    <Button size="small" sx={{ mt: .6 }} onClick={() => setWhyOpen(true)}>Why?</Button>
                </Stack>
            </Grid>
        </Grid>
        <Stack direction={{ xs: "column", lg: "row" }} spacing={1.5} sx={{ p: 1.25, alignItems: { lg: "center" }, borderRadius: 2, border: "1px solid rgba(143,161,184,.14)", bgcolor: "rgba(4,12,25,.22)" }}>
            <Box sx={{ minWidth: 190 }}><Typography color="text.secondary" sx={{ fontSize: ".56rem", textTransform: "uppercase", letterSpacing: ".08em" }}>Good Opportunities To Explore Today</Typography><Typography sx={{ mt: .2, fontSize: ".7rem", fontWeight: 850 }}>Look for careful buying opportunities</Typography></Box>
            <Stack direction="row" useFlexGap spacing={.7} sx={{ flex: 1, flexWrap: "wrap" }}>{data.focus.map((item) => <Chip key={item} size="small" label={item} variant="outlined" />)}<Chip size="small" label={`Avoid: ${data.avoid}`} sx={{ color: colors.red, borderColor: `${colors.red}55` }} variant="outlined" /></Stack>
            <Button component={RouterLink} to="/scanner" size="small" variant="contained" endIcon={<ArrowForwardRoundedIcon />}>Find Matching Stocks</Button>
        </Stack>
        <Box sx={{ p: 1.5, borderRadius: 2, border: "1px solid rgba(143,161,184,.14)", bgcolor: "rgba(4,12,25,.2)" }}>
            <Typography sx={{ fontWeight: 850, fontSize: ".78rem" }}>What should I do today?</Typography>
            <Grid container spacing={.7} sx={{ mt: .7 }}>
                {[
                    ["✓", "Look for buying opportunities.", colors.green],
                    ["✓", "Focus on Technology and Banking stocks.", colors.green],
                    ["✓", "Wait for a small price fall before buying.", colors.green],
                    ["✕", "Avoid buying stocks after large price jumps.", colors.red],
                    ["✕", "Avoid weaker sectors until they improve.", colors.red],
                ].map(([mark, text, color]) => <Grid key={text} size={{ xs: 12, md: 6 }}><Stack direction="row" spacing={.7}><Typography sx={{ color, fontWeight: 900 }}>{mark}</Typography><Typography color="text.secondary" sx={{ fontSize: ".68rem" }}>{text}</Typography></Stack></Grid>)}
            </Grid>
        </Box>
        <Drawer
            anchor="right"
            open={whyOpen}
            onClose={() => setWhyOpen(false)}
            slotProps={{ paper: { sx: { width: { xs: "92vw", sm: 420 }, p: 3, bgcolor: "#0b1728", backgroundImage: "none" } } }}
        >
            <Typography variant="h5">Why is AlphaEdge saying this?</Typography>
            <Typography color="text.secondary" sx={{ mt: .8, fontSize: ".72rem", lineHeight: 1.6 }}>These simple points support today's market view.</Typography>
            <Stack spacing={1.35} sx={{ mt: 3 }}>
                {data.reasons.map((reason) => <Stack key={reason} direction="row" spacing={1}><CheckCircleOutlineRoundedIcon sx={{ color: colors.green, fontSize: 18 }} /><Typography sx={{ fontSize: ".76rem", lineHeight: 1.5 }}>{reason}</Typography></Stack>)}
            </Stack>
            <Box sx={{ mt: "auto", pt: 3 }}>
                <Box sx={{ p: 2, borderRadius: 2, bgcolor: "rgba(155,138,251,.08)", border: "1px solid rgba(155,138,251,.22)" }}>
                    <Typography color="text.secondary" sx={{ fontSize: ".62rem" }}>Overall Market Score</Typography>
                    <Typography sx={{ mt: .4, fontSize: "2rem", fontWeight: 900 }}>{data.confidence} <Box component="span" sx={{ fontSize: ".8rem", color: "text.secondary" }}>/ 100</Box></Typography>
                    <Typography sx={{ color: colors.green, fontWeight: 800 }}>Market looks Healthy</Typography>
                </Box>
                <Button fullWidth variant="outlined" sx={{ mt: 2 }} onClick={() => setWhyOpen(false)}>Close</Button>
            </Box>
        </Drawer>
    </Stack>;
}

export function MarketHealthWidget() {
    const factors = [["Market direction", 5], ["Stocks joining", 4], ["Recent strength", 4], ["Expected swings", 4], ["Safety level", 3]] as const;
    return <Tooltip title="This example score looks at market direction, how many stocks are rising, recent price strength, expected price swings and risk. It does not predict returns.">
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
            <Typography sx={{ mt: 1.5, fontSize: "1.35rem", fontWeight: 900 }}>Strong Uptrend</Typography>
            <Typography color="text.secondary" sx={{ mt: .7, fontSize: ".72rem", lineHeight: 1.55 }}>The market is rising and more stocks are joining the rally.</Typography>
        </Box>
        <Box><Stack direction="row" sx={{ justifyContent: "space-between" }}><Typography color="text.secondary" sx={{ fontSize: ".68rem" }}>Confidence in this view</Typography><Typography sx={{ fontWeight: 850 }}>88%</Typography></Stack><LinearProgress value={88} variant="determinate" sx={{ mt: .7, height: 7 }} /></Box>
    </Stack>;
}

export function TradingBiasWidget() {
    return <Stack sx={{ height: "100%", justifyContent: "space-between" }}>
        <Box>
            <ArrowUpwardRoundedIcon sx={{ color: colors.green, fontSize: 56, transform: "rotate(35deg)" }} />
            <Typography sx={{ fontSize: "1.4rem", fontWeight: 900 }}>Look for Buying Opportunities</Typography>
        </Box>
        <Box>
            <Typography color="text.secondary" sx={{ fontSize: ".62rem", textTransform: "uppercase" }}>Ideas to research</Typography>
            <Typography sx={{ mt: .45, fontWeight: 800 }}>Strong stocks after a small fall · Stocks breaking above resistance</Typography>
            <Typography color="error.main" sx={{ mt: 1, fontSize: ".69rem" }}>Avoid selling strong stocks only because they have risen</Typography>
        </Box>
    </Stack>;
}

export function RiskMeterWidget() {
    const factors = [["Sudden opening move", "Low", colors.green], ["Ease of buying and selling", "Healthy", colors.green], ["Expected price swings", "Medium", colors.amber], ["Market direction stability", "High", colors.blue]];
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
            <Tooltip title="Example: 1,682 stocks rose, 802 fell, 156 reached a one-year high and 23 reached a one-year low." followCursor>
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
        <Box sx={{ mt: 1.5, p: 1.2, borderRadius: 2, bgcolor: "rgba(50,213,131,.06)", border: "1px solid rgba(50,213,131,.14)" }}><Typography sx={{ color: colors.green, fontSize: ".7rem", fontWeight: 800 }}>Simple explanation</Typography><Typography color="text.secondary" sx={{ mt: .35, fontSize: ".68rem" }}>More stocks are going up than before. This supports the wider market rise.</Typography></Box>
    </Stack>;
}

const sectorRows = [
    ["IT", "8/10", "↑↑", "Strong", "Doing well", colors.green],
    ["Bank", "7/10", "↑", "Positive", "Doing well", colors.green],
    ["FMCG", "6/10", "→", "Stable", "Getting stronger", colors.cyan],
    ["Auto", "4/10", "↓", "Soft", "Getting weaker", colors.amber],
    ["Metal", "2/10", "↓↓", "Negative", "Doing poorly", colors.red],
] as const;

export function SectorRotationWidget() {
    const [heatmap, setHeatmap] = useState(false);
    return <Stack sx={{ height: "100%" }}>
        {heatmap ? <Grid container spacing={1} sx={{ flex: 1 }}>{sectorRows.map(([sector, strength, , , status, color]) => <Grid key={sector} size={{ xs: 6, sm: 4 }}><Box sx={{ height: "100%", minHeight: 72, p: 1.2, borderRadius: 2, bgcolor: `${color}18`, border: `1px solid ${color}45` }}><Typography sx={{ fontWeight: 900 }}>{sector}</Typography><Typography sx={{ color, fontSize: "1.1rem", fontWeight: 900 }}>{strength}</Typography><Typography color="text.secondary" sx={{ fontSize: ".58rem" }}>{status}</Typography></Box></Grid>)}</Grid> :
            <Box sx={{ overflowX: "auto", flex: 1 }}><Table size="small"><TableHead><TableRow>{["Sector", "Strength", "Money Moving", "Direction", "Simple View"].map((heading) => <TableCell key={heading}>{heading}</TableCell>)}</TableRow></TableHead><TableBody>{sectorRows.map(([sector, strength, flow, trend, status, color]) => <TableRow key={sector} hover><TableCell sx={{ fontWeight: 850 }}>{sector}</TableCell><TableCell>{strength}</TableCell><TableCell sx={{ color, fontWeight: 900 }}>{flow}</TableCell><TableCell>{trend}</TableCell><TableCell><Chip size="small" label={status} sx={{ color, bgcolor: `${color}12`, border: `1px solid ${color}30` }} /></TableCell></TableRow>)}</TableBody></Table></Box>}
        <Button size="small" endIcon={<OpenInNewRoundedIcon />} onClick={() => setHeatmap((value) => !value)} sx={{ mt: 1.5, alignSelf: "flex-start" }}>{heatmap ? "View Table" : "View Heatmap"}</Button>
    </Stack>;
}

const breadthMetrics = [
    ["Stocks Up", 1682, "+62", "The number of tracked stocks that are rising today"], ["Stocks Down", 802, "-18", "The number of tracked stocks that are falling today"], ["No Change", 126, "+4", "Stocks with almost no price change"],
    ["One-Year Highs", 156, "+21", "Stocks trading at their highest price in one year"], ["One-Year Lows", 23, "-6", "Stocks trading at their lowest price in one year"], ["Above 20-Day Average", 1764, "+3.2%", "Stocks trading above their average price from the last 20 days"],
    ["Above 50-Day Average", 1521, "+2.1%", "Stocks trading above their average price from the last 50 days"], ["Above 200-Day Average", 1318, "+1.4%", "Stocks trading above their average price from the last 200 days"], ["Opened Higher", 84, "+12", "Stocks that opened clearly above yesterday's trading range"],
    ["Opened Lower", 31, "-5", "Stocks that opened clearly below yesterday's trading range"], ["Maximum Daily Rise", 42, "+7", "Stocks that reached their exchange-set daily rise limit"], ["Maximum Daily Fall", 11, "-2", "Stocks that reached their exchange-set daily fall limit"],
    ["High-Volume Stocks Up", 218, "+28", "Rising stocks with more trading activity than usual"], ["High-Volume Stocks Down", 94, "-9", "Falling stocks with more trading activity than usual"], ["Mid-Size Stocks Joining", 68, "+4%", "The percentage of mid-size companies joining the market move"], ["Small Stocks Joining", 61, "+2%", "The percentage of small companies joining the market move"],
] as const;

export function MarketBreadthWidget() {
    return <Grid container spacing={1}>{breadthMetrics.map(([label, value, trend, help]) => <Grid key={label} size={{ xs: 6, sm: 4, lg: 3 }}><Tooltip title={help}><Box sx={{ p: 1.05, borderRadius: 2, border: "1px solid rgba(143,161,184,.14)", bgcolor: "rgba(4,12,25,.24)", transition: "transform .18s ease,border-color .18s ease", "&:hover": { transform: "translateY(-2px)", borderColor: "rgba(97,114,243,.45)" } }}><Typography color="text.secondary" noWrap sx={{ fontSize: ".55rem" }}>{label}</Typography><Stack direction="row" spacing={.55} sx={{ mt: .35, alignItems: "baseline" }}><Typography sx={{ fontWeight: 900 }}>{value.toLocaleString("en-IN")}</Typography><Typography sx={{ color: String(trend).startsWith("-") ? colors.red : colors.green, fontSize: ".56rem" }}>{trend}</Typography></Stack></Box></Tooltip></Grid>)}</Grid>;
}

export function InstitutionalFlowWidget() {
    const rows = [["Foreign institutions", "-1,248 Cr", "Selling"], ["Indian institutions", "+2,129 Cr", "Buying"], ["Individual investors", "+684 Cr", "Buying"], ["Trading firms", "-214 Cr", "Selling"]];
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
    return <Grid container spacing={2} sx={{ alignItems: "center" }}><Grid size={{ xs: 12, sm: 6 }}><CircularGauge value={72} label="Mostly confident" color={colors.green} /></Grid><Grid size={{ xs: 12, sm: 6 }}><Stack spacing={1}>{[["Foreign institutions", "Careful", colors.amber], ["Individual investors", "Neutral", colors.blue], ["Options market", "Positive", colors.green]].map(([label, value, color]) => <Stack key={label} direction="row" sx={{ justifyContent: "space-between" }}><Typography color="text.secondary" sx={{ fontSize: ".68rem" }}>{label}</Typography><Typography sx={{ color, fontSize: ".68rem", fontWeight: 850 }}>{value}</Typography></Stack>)}</Stack></Grid></Grid>;
}

export function OpportunitiesWidget() {
    const items = [["Buying Areas", 18, colors.blue], ["Stocks Moving Strongly", 12, colors.green], ["Stocks Breaking Above Resistance", 7, colors.violet], ["Strong Stocks After a Small Fall", 14, colors.cyan], ["Stocks Continuing Up", 9, colors.amber]];
    const [selected, setSelected] = useState("");
    return <Stack spacing={1}><Grid container spacing={1.1}>{items.map(([label, count, color]) => <Grid key={label as string} size={{ xs: 12, sm: 6 }}><Box sx={{ p: 1.25, borderRadius: 2, border: "1px solid rgba(143,161,184,.15)", transition: "transform .18s ease", "&:hover": { transform: "translateY(-2px)" } }}><Stack direction="row" sx={{ justifyContent: "space-between", alignItems: "center" }}><Box><Typography sx={{ fontWeight: 800, fontSize: ".72rem" }}>{label}</Typography><Typography sx={{ color, fontSize: "1.35rem", fontWeight: 900 }}>{count}</Typography></Box><Button size="small" endIcon={<ArrowForwardRoundedIcon />} onClick={() => setSelected(String(label))}>Scan</Button></Stack></Box></Grid>)}</Grid>{selected && <Typography color="primary.light" sx={{ fontSize: ".65rem" }}>{selected} selected. Scanner hand-off will use the existing scanner route in the integration phase.</Typography>}</Stack>;
}

export function SmartAlertsWidget() {
    const alerts = [["More stocks are joining the rise", "Important", "2m", colors.green], ["Bank Nifty is stronger than the wider market", "Medium", "8m", colors.blue], ["Metal stocks are becoming weaker", "Medium", "14m", colors.amber], ["Small companies are doing better than large companies", "Information", "21m", colors.cyan]];
    return <Stack spacing={1}>{alerts.map(([message, severity, time, color]) => <Stack key={message} direction="row" spacing={1.1} sx={{ alignItems: "center", p: 1.1, borderRadius: 2, bgcolor: "rgba(4,12,25,.25)", border: "1px solid rgba(143,161,184,.12)" }}><Box sx={{ width: 8, height: 8, borderRadius: "50%", bgcolor: color, boxShadow: `0 0 10px ${color}` }} /><Box sx={{ flex: 1 }}><Typography sx={{ fontSize: ".72rem", fontWeight: 800 }}>{message}</Typography><Typography color="text.secondary" sx={{ fontSize: ".57rem" }}>{severity} severity</Typography></Box><Typography color="text.secondary" sx={{ fontSize: ".6rem" }}>{time}</Typography></Stack>)}</Stack>;
}

export function VerdictWidget() {
    const items = [["Market Direction", "Going up", colors.green], ["Stocks Joining", "Healthy", colors.green], ["Recent Price Strength", "Positive", colors.cyan], ["Risk", "Medium", colors.amber], ["What to Research", "Strong stocks after a small fall", colors.blue], ["Avoid", "Buying breakouts in weak sectors", colors.red]];
    return <Grid container spacing={2.5} sx={{ alignItems: "center" }}><Grid size={{ xs: 12, lg: 9 }}><Grid container spacing={1.1}>{items.map(([label, value, color]) => <Grid key={label} size={{ xs: 12, sm: 6, md: 4 }}><Box sx={{ p: 1.2, borderRadius: 2, bgcolor: `${color}09`, border: `1px solid ${color}25` }}><Typography color="text.secondary" sx={{ fontSize: ".58rem", textTransform: "uppercase" }}>{label}</Typography><Typography sx={{ mt: .3, color, fontWeight: 850 }}>{value}</Typography></Box></Grid>)}</Grid></Grid><Grid size={{ xs: 12, lg: 3 }}><CircularGauge value={89} label="Overall confidence" color={colors.violet} /></Grid></Grid>;
}
