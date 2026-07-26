import { useEffect, useMemo, useRef, useState } from "react";

import ArrowDownwardRoundedIcon from "@mui/icons-material/ArrowDownwardRounded";
import ArrowForwardRoundedIcon from "@mui/icons-material/ArrowForwardRounded";
import ArrowUpwardRoundedIcon from "@mui/icons-material/ArrowUpwardRounded";
import AutoAwesomeOutlinedIcon from "@mui/icons-material/AutoAwesomeOutlined";
import CheckCircleOutlineRoundedIcon from "@mui/icons-material/CheckCircleOutlineRounded";
import DownloadRoundedIcon from "@mui/icons-material/DownloadRounded";
import ErrorOutlineRoundedIcon from "@mui/icons-material/ErrorOutlineRounded";
import FullscreenRoundedIcon from "@mui/icons-material/FullscreenRounded";
import MoreVertRoundedIcon from "@mui/icons-material/MoreVertRounded";
import OpenInNewRoundedIcon from "@mui/icons-material/OpenInNewRounded";
import ShowChartRoundedIcon from "@mui/icons-material/ShowChartRounded";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Chip from "@mui/material/Chip";
import Drawer from "@mui/material/Drawer";
import Grid from "@mui/material/Grid";
import IconButton from "@mui/material/IconButton";
import LinearProgress from "@mui/material/LinearProgress";
import Menu from "@mui/material/Menu";
import MenuItem from "@mui/material/MenuItem";
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
        <Box sx={{ width: "100%", height: "100%", borderRadius: "50%", bgcolor: "background.paper", display: "grid", placeItems: "center", textAlign: "center" }}>
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

function ExecutiveStatusChip({ metric, showTooltip = true }: { metric: ExecutiveMetric; showTooltip?: boolean }) {
    const toneColor = metric.tone === "positive" ? colors.green : metric.tone === "caution" ? colors.amber : colors.blue;
    const chip = <Stack
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
        </Stack>;
    return showTooltip ? <Tooltip title={metric.help} arrow>{chip}</Tooltip> : chip;
}

export function AIMarketSummaryWidget({
    data = demoExecutiveSummary,
    loading = false,
    timeframe = "1M",
    universe = "nifty500",
    language = "simple",
    showTooltips = true,
}: {
    data?: ExecutiveSummaryData | null;
    loading?: boolean;
    timeframe?: string;
    universe?: string;
    language?: "simple" | "professional";
    showTooltips?: boolean;
}) {
    const [whyOpen, setWhyOpen] = useState(false);
    const timeframeScore: Record<string, number> = { "1D": -3, "1W": -1, "1M": 0, "3M": 1, "6M": 2, "1Y": 3 };
    const universeScore: Record<string, number> = { nseAll: 1, nifty500: 0, nifty200: -1, nifty100: -2, fo: 1, watchlist: -3, holdings: -4 };
    const marketScore = Math.max(0, Math.min(100, (data?.confidence ?? 0) + (timeframeScore[timeframe] ?? 0) + (universeScore[universe] ?? 0)));
    const animatedScore = useCountUp(marketScore);
    if (loading) return <WidgetLoading rows={5} />;
    if (!data) return <WidgetEmpty message="AI Summary unavailable. Waiting for validated market intelligence." />;
    const headline = data.participation >= 65
        ? "More stocks are joining the market rise. This is a healthy sign."
        : data.participation >= 50
            ? "The market is rising, but only some stocks are taking part."
            : "The main indexes are rising, but too few stocks are joining the move.";
    const explanation = language === "professional" ? [
        `The ${timeframe} market structure remains constructive.`,
        `About ${data.participation}% of the selected ${universe} universe is advancing, confirming broad participation.`,
        `${data.leaders.join(" and ")} continue to lead while volatility remains controlled.`,
        "The preferred approach is to buy quality pullbacks and avoid extended breakouts.",
    ] : [
        `The market looks healthy in the selected ${timeframe} view.`,
        `About ${data.participation}% of the selected stocks are rising, so the move is not limited to a few large companies.`,
        `${data.leaders.join(" and ")} are doing well, while price movement remains stable.`,
        "Look for quality buying opportunities, but avoid stocks that have already risen sharply.",
    ];
    const displayMetrics = language === "professional" ? data.metrics.map((metric) => ({
        ...metric,
        label: ({ "Today's Market": "Market Direction", "Most Stocks": "Market Breadth", "Market Strength": "Momentum", "Strongest Sectors": "Sector Leadership", "Price Movement": "Volatility", "Big Investors": "Institutional Flow", "Current Trend": "Market Regime" } as Record<string, string>)[metric.label] ?? metric.label,
    })) : data.metrics;
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
                        {displayMetrics.map((metric) => <ExecutiveStatusChip key={metric.label} metric={metric} showTooltip={showTooltips} />)}
                    </Stack>
                </Stack>
            </Grid>
            <Grid size={{ xs: 12, lg: 3 }}>
                <Stack sx={{ height: "100%", justifyContent: "center", alignItems: "center", borderLeft: { lg: "1px solid rgba(143,161,184,.14)" } }}>
                    <Box sx={{ width: 142, height: 142, borderRadius: "50%", p: "10px", background: `conic-gradient(${colors.violet} ${animatedScore * 3.6}deg,#17263a 0)` }}>
                        <Box sx={{ width: "100%", height: "100%", borderRadius: "50%", bgcolor: "background.paper", display: "grid", placeItems: "center", textAlign: "center" }}>
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
            slotProps={{ paper: { sx: { width: { xs: "92vw", sm: 420 }, p: 3, bgcolor: "background.paper", backgroundImage: "none" } } }}
        >
            <Typography variant="h5">Why is AlphaEdge saying this?</Typography>
            <Typography color="text.secondary" sx={{ mt: .8, fontSize: ".72rem", lineHeight: 1.6 }}>These simple points support today's market view.</Typography>
            <Stack spacing={1.35} sx={{ mt: 3 }}>
                {data.reasons.map((reason) => <Stack key={reason} direction="row" spacing={1}><CheckCircleOutlineRoundedIcon sx={{ color: colors.green, fontSize: 18 }} /><Typography sx={{ fontSize: ".76rem", lineHeight: 1.5 }}>{reason}</Typography></Stack>)}
            </Stack>
            <Box sx={{ mt: "auto", pt: 3 }}>
                <Box sx={{ p: 2, borderRadius: 2, bgcolor: "rgba(155,138,251,.08)", border: "1px solid rgba(155,138,251,.22)" }}>
                    <Typography color="text.secondary" sx={{ fontSize: ".62rem" }}>Overall Market Score</Typography>
                    <Typography sx={{ mt: .4, fontSize: "2rem", fontWeight: 900 }}>{marketScore} <Box component="span" sx={{ fontSize: ".8rem", color: "text.secondary" }}>/ 100</Box></Typography>
                    <Typography sx={{ color: colors.green, fontWeight: 800 }}>Market looks Healthy</Typography>
                </Box>
                <Button fullWidth variant="outlined" sx={{ mt: 2 }} onClick={() => setWhyOpen(false)}>Close</Button>
            </Box>
        </Drawer>
    </Stack>;
}

export function MarketHealthWidget({ score = 87, health = "Looking Healthy", showTooltips = true }: { timeframe?: string; universe?: string; score?: number; health?: string; showTooltips?: boolean }) {
    const factors = [["Market direction", 5], ["Stocks joining", 4], ["Recent strength", 4], ["Expected swings", 4], ["Safety level", 3]] as const;
    const content = <Box>
            <CircularGauge value={score} label={health} />
            <Stack spacing={.55} sx={{ mt: 1.5 }}>{factors.map(([label, value]) => <Stack key={label} direction="row" sx={{ justifyContent: "space-between" }}><Typography color="text.secondary" sx={{ fontSize: ".67rem" }}>{label}</Typography><Stars value={value} /></Stack>)}</Stack>
            <Typography color="text.secondary" sx={{ mt: 1.3, fontSize: ".58rem" }}>Updated 10:42 IST</Typography>
        </Box>;
    return showTooltips ? <Tooltip title="This example score looks at market direction, how many stocks are rising, recent price strength, expected price swings and risk. It does not predict returns.">{content}</Tooltip> : content;
}

export function MarketRegimeWidget({ timeframe = "1M", language = "simple", regime = "Strong Rise", confidence = 88 }: { timeframe?: string; language?: "simple" | "professional"; regime?: string; confidence?: number }) {
    const longTerm = timeframe === "6M" || timeframe === "1Y";
    return <Stack sx={{ height: "100%", justifyContent: "space-between" }}>
        <Box>
            <Box sx={{ width: 54, height: 54, display: "grid", placeItems: "center", borderRadius: 3, bgcolor: `${colors.blue}12`, color: colors.blue }}><ShowChartRoundedIcon fontSize="large" /></Box>
            <Typography sx={{ mt: 1.5, fontSize: "1.35rem", fontWeight: 900 }}>{language === "professional" ? regime : longTerm && regime === "Strong Rise" ? "Healthy Long-Term Rise" : regime}</Typography>
            <Typography color="text.secondary" sx={{ mt: .7, fontSize: ".72rem", lineHeight: 1.55 }}>{language === "professional" ? "Price structure and market breadth remain positive." : longTerm ? "The wider market has continued to rise over a longer period." : "The market is rising and more stocks are joining the rally."}</Typography>
        </Box>
        <Box><Stack direction="row" sx={{ justifyContent: "space-between" }}><Typography color="text.secondary" sx={{ fontSize: ".68rem" }}>Confidence in this view</Typography><Typography sx={{ fontWeight: 850 }}>{confidence}%</Typography></Stack><LinearProgress value={confidence} variant="determinate" sx={{ mt: .7, height: 7 }} /></Box>
    </Stack>;
}

export function TradingBiasWidget({ strategy = "Look for buying opportunities after a small price fall.", direction = "Bullish" }: { strategy?: string; direction?: string }) {
    return <Stack sx={{ height: "100%", justifyContent: "space-between" }}>
        <Box>
            <ArrowUpwardRoundedIcon sx={{ color: direction === "Bearish" ? colors.red : colors.green, fontSize: 56, transform: direction === "Bearish" ? "rotate(145deg)" : "rotate(35deg)" }} />
            <Typography sx={{ fontSize: "1.4rem", fontWeight: 900 }}>{strategy}</Typography>
        </Box>
        <Box>
            <Typography color="text.secondary" sx={{ fontSize: ".62rem", textTransform: "uppercase" }}>Ideas to research</Typography>
            <Typography sx={{ mt: .45, fontWeight: 800 }}>Strong stocks after a small fall · Stocks breaking above resistance</Typography>
            <Typography color="error.main" sx={{ mt: 1, fontSize: ".69rem" }}>Avoid selling strong stocks only because they have risen</Typography>
        </Box>
    </Stack>;
}

export function RiskMeterWidget({ riskLevel = "Moderate Risk", volatility = "Moderate" }: { riskLevel?: string; volatility?: string }) {
    const factors = [["Sudden opening move", riskLevel === "High Risk" ? "High" : "Low", riskLevel === "High Risk" ? colors.red : colors.green], ["Ease of buying and selling", "Healthy", colors.green], ["Expected price swings", volatility, volatility === "High" ? colors.red : colors.amber], ["Market direction stability", riskLevel === "Low Risk" ? "High" : "Medium", colors.blue]];
    return <Stack>
        <Box sx={{ width: 170, height: 86, mx: "auto", overflow: "hidden", position: "relative" }}>
            <Box sx={{ width: 170, height: 170, borderRadius: "50%", background: `conic-gradient(from 270deg,${colors.green} 0 25%,${colors.amber} 25% 38%,${colors.red} 38% 50%,transparent 50%)`, p: "15px" }}>
                <Box sx={{ width: "100%", height: "100%", borderRadius: "50%", bgcolor: "background.paper" }} />
            </Box>
            <Typography sx={{ position: "absolute", bottom: 0, width: "100%", textAlign: "center", fontWeight: 900, color: riskLevel === "High Risk" ? colors.red : riskLevel === "Low Risk" ? colors.green : colors.amber }}>{riskLevel.toUpperCase()}</Typography>
        </Box>
        <Stack spacing={.8} sx={{ mt: 1.5 }}>{factors.map(([label, value, color]) => <Stack key={label} direction="row" sx={{ justifyContent: "space-between" }}><Typography color="text.secondary" sx={{ fontSize: ".67rem" }}>{label}</Typography><Typography sx={{ color, fontSize: ".67rem", fontWeight: 800 }}>{value}</Typography></Stack>)}</Stack>
    </Stack>;
}

interface ParticipationPoint {
    label: string;
    date: string;
    net: number;
    nifty: number;
    bank: number;
    advancing: number;
    declining: number;
    highs: number;
    lows: number;
    event?: string;
}

const participationNets = {
    "1D": [4, 8, 5, 12, 10, 18, 15, 24, 21, 29, 27, 34, 31, 39, 36, 43, 40, 48, 45, 52, 49, 57, 54, 61],
    "1W": [18, 27, 22, 38, 46],
    "1M": [-8, -3, 4, 1, 9, 14, 11, 20, 17, 24, 21, 29, 27, 34, 31, 39, 36, 43, 47, 45, 52, 57],
    "3M": [-18, -9, -3, 6, 2, 14, 11, 23, 20, 32, 28, 41, 48],
    "6M": [-28, -23, -17, -21, -12, -6, 2, -3, 8, 14, 11, 21, 18, 29, 25, 34, 31, 40, 37, 46, 43, 51, 48, 56, 53, 62],
    "1Y": [-35, -28, -31, -20, -12, -4, 7, 3, 16, 27, 39, 52],
} as const;

const axisLabels = {
    "1D": ["09:15", "10:00", "11:00", "12:00", "13:00", "14:00", "15:30"],
    "1W": ["Mon", "Tue", "Wed", "Thu", "Fri"],
    "1M": ["Week 1", "Week 2", "Week 3", "Week 4"],
    "3M": ["May", "June", "July"],
    "6M": ["February", "March", "April", "May", "June", "July"],
    "1Y": ["Aug", "Oct", "Dec", "Feb", "Apr", "Jun", "Jul"],
} as const;

function buildParticipationData(range: keyof typeof participationNets, universe = "nifty500"): ParticipationPoint[] {
    const universeAdjustment: Record<string, number> = { nseAll: 6, nifty500: 0, nifty200: -3, nifty100: -5, fo: 4, watchlist: -8, holdings: -10 };
    return participationNets[range].map((sourceNet, index, values) => {
        const net = sourceNet + (universeAdjustment[universe] ?? 0);
        return {
        label: axisLabels[range][Math.min(axisLabels[range].length - 1, Math.floor(index * axisLabels[range].length / values.length))],
        date: `${axisLabels[range][Math.min(axisLabels[range].length - 1, Math.floor(index * axisLabels[range].length / values.length))]} · ${range}`,
        net,
        nifty: Math.round(index * 2.5 + Math.sin(index * .8) * 4 + 10),
        bank: Math.round(index * 2.2 + Math.cos(index * .7) * 5 + 8),
        advancing: 1280 + net * 8 + index * 4,
        declining: 1180 - net * 5,
        highs: Math.max(18, 62 + net * 2),
        lows: Math.max(8, 45 - net),
        event: index === Math.floor(values.length * .42) ? "RBI policy update" : index === Math.floor(values.length * .72) ? "Major earnings day" : undefined,
        };
    });
}

export function ParticipationChartWidget({
    loading = false,
    available = true,
    defaultRange = "1M",
    universe = "nifty500",
    initialNifty = true,
    initialBankNifty = true,
    showEvents = true,
    showInsights = true,
    showTooltips = true,
}: {
    loading?: boolean;
    available?: boolean;
    defaultRange?: keyof typeof participationNets;
    universe?: string;
    initialNifty?: boolean;
    initialBankNifty?: boolean;
    showEvents?: boolean;
    showInsights?: boolean;
    showTooltips?: boolean;
}) {
    const [range, setRange] = useState<keyof typeof participationNets>(defaultRange);
    const [marketLine, setMarketLine] = useState(true);
    const [nifty, setNifty] = useState(initialNifty);
    const [bank, setBank] = useState(initialBankNifty);
    const [hoverIndex, setHoverIndex] = useState<number | null>(null);
    const [menuAnchor, setMenuAnchor] = useState<null | HTMLElement>(null);
    const chartAreaRef = useRef<HTMLDivElement>(null);
    const data = useMemo(() => buildParticipationData(range, universe), [range, universe]);
    const values = data.map((point) => point.net);
    const maxValue = Math.max(...values);
    const minValue = Math.min(...values);
    const scaleY = (value: number) => 50 - value * .68;
    const scaleX = (index: number) => index * 100 / Math.max(1, data.length - 1);
    const participationPoints = data.map((point, index) => `${scaleX(index)},${scaleY(point.net)}`).join(" ");
    const niftyPoints = data.map((point, index) => `${scaleX(index)},${scaleY(point.nifty)}`).join(" ");
    const bankPoints = data.map((point, index) => `${scaleX(index)},${scaleY(point.bank)}`).join(" ");
    const current = data[data.length - 1];
    const highestIndex = values.indexOf(maxValue);
    const lowestIndex = values.indexOf(minValue);
    const activeIndex = hoverIndex ?? data.length - 1;
    const active = data[activeIndex];
    const participationChange = current.net - data[Math.max(0, data.length - 4)].net;
    const indexChange = current.nifty - data[Math.max(0, data.length - 4)].nifty;
    const divergence = indexChange > 0 && participationChange < 0;
    const insight = divergence
        ? "The index is rising while fewer stocks are rising. Be careful because the market move may be getting weaker."
        : participationChange > indexChange
            ? "More companies are joining the rally. The wider market is getting stronger."
            : "Today's index move is supported by many stocks rising together.";
    const interpretation = divergence ? "Weakening" : participationChange > 8 ? "Improving" : current.net > 30 ? "Healthy" : "Mixed";
    const health = current.net > 40 ? "Healthy" : current.net > 15 ? "Fair" : "Weak";
    const exportData = () => {
        const csv = ["Date,Advancing,Declining,Net Participation,New Highs,New Lows", ...data.map((point) => `${point.date},${point.advancing},${point.declining},${point.net},${point.highs},${point.lows}`)].join("\n");
        const url = URL.createObjectURL(new Blob([csv], { type: "text/csv" }));
        const link = document.createElement("a");
        link.href = url;
        link.download = `alphaedge-market-participation-${range}.csv`;
        link.click();
        URL.revokeObjectURL(url);
        setMenuAnchor(null);
    };
    if (loading) return <Stack spacing={1.2}><Skeleton height={64} variant="rounded" /><Skeleton height={400} variant="rounded" /><Skeleton height={58} variant="rounded" /></Stack>;
    if (!available) return <WidgetEmpty message="Market participation data is currently unavailable." />;
    return <Stack sx={{ height: "100%" }}>
        <Stack direction={{ xs: "column", lg: "row" }} spacing={1} sx={{ justifyContent: "space-between", alignItems: { lg: "center" } }}>
            <ToggleButtonGroup exclusive size="small" value={range} onChange={(_, value) => value && setRange(value)}>
                {Object.keys(participationNets).map((value) => <ToggleButton key={value} value={value}>{value}</ToggleButton>)}
            </ToggleButtonGroup>
            <Stack direction="row" spacing={1} sx={{ alignItems: "center", flexWrap: "wrap" }}>
                <Chip size="small" color={divergence ? "warning" : "success"} label={interpretation} />
                {([["Market Participation", marketLine, setMarketLine], ["Nifty", nifty, setNifty], ["Bank Nifty", bank, setBank]] as const).map(([label, checked, setter]) => <Stack key={label} direction="row" spacing={.2} sx={{ alignItems: "center" }}><Switch size="small" checked={checked} onChange={(event) => setter(event.target.checked)} slotProps={{ input: { "aria-label": `Show ${label}` } }} /><Typography sx={{ fontSize: ".62rem" }}>{label}</Typography></Stack>)}
                <IconButton aria-label="Chart actions" size="small" onClick={(event) => setMenuAnchor(event.currentTarget)}><MoreVertRoundedIcon /></IconButton>
                <Menu anchorEl={menuAnchor} open={Boolean(menuAnchor)} onClose={() => setMenuAnchor(null)}>
                    <MenuItem onClick={() => { void chartAreaRef.current?.requestFullscreen(); setMenuAnchor(null); }}><FullscreenRoundedIcon fontSize="small" sx={{ mr: 1 }} />Expand Chart</MenuItem>
                    <MenuItem onClick={() => { setNifty(true); setBank(true); setMenuAnchor(null); }}>Compare Indexes</MenuItem>
                    <MenuItem onClick={exportData}><DownloadRoundedIcon fontSize="small" sx={{ mr: 1 }} />Export CSV</MenuItem>
                    <MenuItem component={RouterLink} to="/market-breadth">View Detailed Market Data</MenuItem>
                </Menu>
            </Stack>
        </Stack>
        <Grid container spacing={1} sx={{ mt: 1.2 }}>
            {[
                ["Current", current.net], ["Highest", maxValue], ["Lowest", minValue],
                ["5-Day Average", Math.round(values.slice(-5).reduce((sum, value) => sum + value, 0) / Math.min(5, values.length))],
                ["20-Day Average", Math.round(values.slice(-20).reduce((sum, value) => sum + value, 0) / Math.min(20, values.length))],
            ].map(([label, value]) => <Grid key={label} size={{ xs: 6, sm: 4, lg: 2.4 }}><Box sx={{ p: .9, borderRadius: 2, bgcolor: "rgba(4,12,25,.22)", border: "1px solid rgba(143,161,184,.12)" }}><Typography color="text.secondary" sx={{ fontSize: ".55rem" }}>{label}</Typography><Typography sx={{ mt: .2, fontWeight: 900, color: Number(value) >= 0 ? colors.green : colors.red }}>{Number(value) > 0 ? "+" : ""}{value}</Typography></Box></Grid>)}
        </Grid>
        <Box ref={chartAreaRef} sx={{ position: "relative", height: 400, mt: 1.25, bgcolor: "#081322", color: "#f3f7fb", borderRadius: 2, border: "1px solid rgba(143,161,184,.14)", overflow: "hidden" }}>
            <Typography color="text.secondary" sx={{ position: "absolute", left: 8, top: "44%", fontSize: ".55rem", transform: "rotate(-90deg)", transformOrigin: "left top" }}>Net Market Participation — stocks up minus stocks down</Typography>
            <Box sx={{ position: "absolute", left: 50, top: 16, bottom: 28, width: 54, display: "flex", flexDirection: "column", justifyContent: "space-between" }}>{[["Positive", "+50"], ["Zero", "0"], ["Negative", "-25"]].map(([label, value]) => <Box key={label}><Typography sx={{ fontSize: ".53rem", color: label === "Positive" ? colors.green : label === "Negative" ? colors.red : "text.secondary" }}>{label}</Typography><Typography color="text.secondary" sx={{ fontSize: ".5rem" }}>{value}</Typography></Box>)}</Box>
            <Box
                component="svg"
                tabIndex={0}
                role="img"
                aria-label={`Market participation chart. Current value ${current.net}. Highest ${maxValue}. Lowest ${minValue}.`}
                viewBox="0 0 100 100"
                preserveAspectRatio="none"
                onMouseMove={(event) => {
                    const bounds = event.currentTarget.getBoundingClientRect();
                    setHoverIndex(Math.max(0, Math.min(data.length - 1, Math.round((event.clientX - bounds.left) / bounds.width * (data.length - 1)))));
                }}
                onMouseLeave={() => setHoverIndex(null)}
                onKeyDown={(event) => {
                    if (event.key === "ArrowLeft") setHoverIndex(Math.max(0, activeIndex - 1));
                    if (event.key === "ArrowRight") setHoverIndex(Math.min(data.length - 1, activeIndex + 1));
                }}
                sx={{ position: "absolute", left: 108, top: 16, width: "calc(100% - 124px)", height: "calc(100% - 48px)", outline: "none", "&:focus": { filter: "drop-shadow(0 0 3px #6172f3)" }, "& .participation-line": { strokeDasharray: 500, strokeDashoffset: 500, animation: "drawParticipation .7s ease forwards" }, "@keyframes drawParticipation": { to: { strokeDashoffset: 0 } } }}
            >
                {[16, 50, 84].map((y) => <line key={y} x1="0" y1={y} x2="100" y2={y} stroke={y === 50 ? "#61758f" : "#213149"} strokeDasharray={y === 50 ? "2 2" : undefined} strokeWidth=".5" />)}
                <defs><linearGradient id="participationFillDetailed" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor={colors.green} stopOpacity=".24" /><stop offset="100%" stopColor={colors.green} stopOpacity="0" /></linearGradient></defs>
                {marketLine && <><polygon points={`0,100 ${participationPoints} 100,100`} fill="url(#participationFillDetailed)" /><polyline className="participation-line" points={participationPoints} fill="none" stroke={colors.green} strokeWidth="1.8" vectorEffect="non-scaling-stroke" /></>}
                {nifty && <polyline points={niftyPoints} fill="none" stroke={colors.blue} strokeWidth="1.15" vectorEffect="non-scaling-stroke" />}
                {bank && <polyline points={bankPoints} fill="none" stroke={colors.amber} strokeWidth="1.15" vectorEffect="non-scaling-stroke" />}
                {showEvents && data.map((point, index) => point.event && (showTooltips ? <Tooltip key={point.event} title={point.event} arrow><circle cx={scaleX(index)} cy="8" r="1.4" fill={colors.violet} /></Tooltip> : <circle key={point.event} cx={scaleX(index)} cy="8" r="1.4" fill={colors.violet} />))}
                <circle cx={scaleX(highestIndex)} cy={scaleY(maxValue)} r="1.5" fill={colors.green} stroke="#fff" strokeWidth=".45" />
                <circle cx={scaleX(lowestIndex)} cy={scaleY(minValue)} r="1.5" fill={colors.red} stroke="#fff" strokeWidth=".45" />
                <circle cx={scaleX(data.length - 1)} cy={scaleY(current.net)} r="1.7" fill={colors.cyan} stroke="#fff" strokeWidth=".45" />
                <line x1={scaleX(activeIndex)} x2={scaleX(activeIndex)} y1="0" y2="100" stroke="#cbd5e1" strokeDasharray="2 2" strokeWidth=".45" />
                <circle cx={scaleX(activeIndex)} cy={scaleY(active.net)} r="1.8" fill="#fff" stroke={colors.green} strokeWidth=".7" />
            </Box>
            <Stack direction="row" sx={{ position: "absolute", left: 108, right: 16, bottom: 7, justifyContent: "space-between" }}>{axisLabels[range].map((label) => <Typography key={label} color="text.secondary" sx={{ fontSize: ".54rem" }}>{label}</Typography>)}</Stack>
            {showTooltips && <Box sx={{ position: "absolute", right: 18, top: 18, width: 220, p: 1.2, borderRadius: 2, bgcolor: "rgba(7,17,30,.94)", border: "1px solid rgba(143,161,184,.28)", pointerEvents: "none" }}>
                <Typography sx={{ fontSize: ".66rem", fontWeight: 850 }}>{active.date}</Typography>
                <Grid container spacing={.4} sx={{ mt: .5 }}>{[["Stocks Up", active.advancing], ["Stocks Down", active.declining], ["Net", active.net], ["Market Health", health], ["New Highs", active.highs], ["New Lows", active.lows]].map(([label, value]) => <Grid key={label} size={6}><Typography color="text.secondary" sx={{ fontSize: ".51rem" }}>{label}</Typography><Typography sx={{ fontSize: ".62rem", fontWeight: 800 }}>{value}</Typography></Grid>)}</Grid>
                <Typography sx={{ mt: .7, color: active.net > 20 ? colors.green : colors.amber, fontSize: ".57rem" }}>{active.net > 20 ? "Most stocks joined this market rise." : "Only some stocks joined this move."}</Typography>
            </Box>}
        </Box>
        {showInsights && <Box sx={{ mt: 1.2, p: 1.2, borderRadius: 2, bgcolor: divergence ? "rgba(253,176,34,.07)" : "rgba(50,213,131,.06)", border: `1px solid ${divergence ? "rgba(253,176,34,.2)" : "rgba(50,213,131,.14)"}` }}>
            <Typography sx={{ color: divergence ? colors.amber : colors.green, fontSize: ".7rem", fontWeight: 850 }}>{divergence ? "Warning" : "What this means"}</Typography>
            <Typography color="text.secondary" sx={{ mt: .35, fontSize: ".68rem" }}>{insight}</Typography>
        </Box>}
    </Stack>;
}

const sectorRows = [
    ["IT", "8/10", "↑↑", "Strong", "Doing well", colors.green],
    ["Bank", "7/10", "↑", "Positive", "Doing well", colors.green],
    ["FMCG", "6/10", "→", "Stable", "Getting stronger", colors.cyan],
    ["Auto", "4/10", "↓", "Soft", "Getting weaker", colors.amber],
    ["Metal", "2/10", "↓↓", "Negative", "Doing poorly", colors.red],
] as const;

export function SectorRotationWidget({ leaders = [] }: { leaders?: string[] }) {
    const [heatmap, setHeatmap] = useState(false);
    return <Stack sx={{ height: "100%" }}>
        {leaders.length > 0 && <Typography variant="caption" color="text.secondary" sx={{ mb: 1 }}>Shared leaders: {leaders.join(" and ")}</Typography>}
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

export function MarketBreadthWidget({ participation = 62, shortNumbers = false, showTooltips = true }: { participation?: number; shortNumbers?: boolean; showTooltips?: boolean }) {
    const format = (value: number) => shortNumbers && value >= 1000 ? `${(value / 1000).toFixed(2)}K` : value.toLocaleString("en-IN");
    const total = 2610;
    const sharedMetrics = breadthMetrics.map((metric) => metric[0] === "Stocks Up"
        ? [metric[0], Math.round(total * participation / 100), metric[2], metric[3]] as const
        : metric[0] === "Stocks Down"
            ? [metric[0], Math.round(total * (100 - participation) / 100), metric[2], metric[3]] as const
            : metric);
    return <Grid container spacing={1}>{sharedMetrics.map(([label, value, trend, help]) => {
        const metric = <Box sx={{ p: 1.05, borderRadius: 2, border: "1px solid rgba(143,161,184,.14)", bgcolor: "rgba(4,12,25,.24)", transition: "transform .18s ease,border-color .18s ease", "&:hover": { transform: "translateY(-2px)", borderColor: "rgba(97,114,243,.45)" } }}><Typography color="text.secondary" noWrap sx={{ fontSize: ".55rem" }}>{label}</Typography><Stack direction="row" spacing={.55} sx={{ mt: .35, alignItems: "baseline" }}><Typography sx={{ fontWeight: 900 }}>{format(value)}</Typography><Typography sx={{ color: String(trend).startsWith("-") ? colors.red : colors.green, fontSize: ".56rem" }}>{trend}</Typography></Stack></Box>;
        return <Grid key={label} size={{ xs: 6, sm: 4, lg: 3 }}>{showTooltips ? <Tooltip title={help}>{metric}</Tooltip> : metric}</Grid>;
    })}</Grid>;
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

export function VerdictWidget({ timeframe = "1M", universe = "nifty500", language = "simple" }: { timeframe?: string; universe?: string; language?: "simple" | "professional" }) {
    const professional = language === "professional";
    const items = professional
        ? [["Market Trend", "Bullish", colors.green], ["Breadth", "Healthy", colors.green], ["Momentum", "Positive", colors.cyan], ["Risk", "Moderate", colors.amber], ["Preferred Setup", "Buy pullbacks", colors.blue], ["Avoid", "Weak-sector breakouts", colors.red]]
        : [["Market Direction", "Going up", colors.green], ["Stocks Joining", "Healthy", colors.green], ["Recent Price Strength", "Positive", colors.cyan], ["Risk", "Medium", colors.amber], ["What to Research", timeframe === "1D" ? "Strong stocks after a small fall today" : "Strong stocks after a small fall", colors.blue], ["Avoid", "Buying breakouts in weak sectors", colors.red]];
    const score = 89 + (timeframe === "1Y" ? 2 : timeframe === "1D" ? -2 : 0) + (universe === "holdings" ? -2 : 0);
    return <Grid container spacing={2.5} sx={{ alignItems: "center" }}><Grid size={{ xs: 12, lg: 9 }}><Grid container spacing={1.1}>{items.map(([label, value, color]) => <Grid key={label} size={{ xs: 12, sm: 6, md: 4 }}><Box sx={{ p: 1.2, borderRadius: 2, bgcolor: `${color}09`, border: `1px solid ${color}25` }}><Typography color="text.secondary" sx={{ fontSize: ".58rem", textTransform: "uppercase" }}>{label}</Typography><Typography sx={{ mt: .3, color, fontWeight: 850 }}>{value}</Typography></Box></Grid>)}</Grid></Grid><Grid size={{ xs: 12, lg: 3 }}><CircularGauge value={score} label="Overall confidence" color={colors.violet} /></Grid></Grid>;
}
