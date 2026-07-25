import BarChartOutlinedIcon from "@mui/icons-material/BarChartOutlined";
import ShowChartOutlinedIcon from "@mui/icons-material/ShowChartOutlined";
import TimelineOutlinedIcon from "@mui/icons-material/TimelineOutlined";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Card from "@mui/material/Card";
import Divider from "@mui/material/Divider";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";

const candles = Array.from({ length: 58 }, (_, index) => {
    const trend = 2640 + index * 6.1;
    const wave = Math.sin(index * 0.55) * 42 + Math.sin(index * 0.17) * 28;
    const open = trend + wave;
    const close = open + Math.sin(index * 1.7) * 25;
    const high = Math.max(open, close) + 12 + (index % 4) * 3;
    const low = Math.min(open, close) - 10 - (index % 3) * 4;
    return { open, close, high, low };
});

function y(value: number) {
    return 330 - ((value - 2500) / 620) * 300;
}

function TradingChart() {
    return (
        <Card sx={{ height: 430, overflow: "hidden" }}>
            <Stack
                direction="row"
                sx={{
                    height: 42,
                    px: 1.5,
                    alignItems: "center",
                    justifyContent: "space-between",
                    bgcolor: "#091423",
                }}
            >
                <Box>
                    <Typography sx={{ fontWeight: 800, fontSize: "0.78rem" }}>
                        RELIANCE INDUSTRIES LTD · 1D · NSE
                    </Typography>
                    <Typography color="success.main" sx={{ fontSize: "0.68rem" }}>
                        O 2,966.00&nbsp; H 2,979.50&nbsp; L 2,964.00&nbsp; C 2,978.45&nbsp; +0.83%
                    </Typography>
                </Box>
                <Stack direction="row" spacing={0.5}>
                    {["1D", "5D", "1M", "6M", "1Y"].map((range) => (
                        <Button key={range} size="small" color={range === "1D" ? "primary" : "inherit"}>{range}</Button>
                    ))}
                </Stack>
            </Stack>
            <Divider />
            <Box sx={{ display: "flex", height: 346 }}>
                <Stack sx={{ width: 42, py: 1, alignItems: "center", gap: 1.5, borderRight: "1px solid", borderColor: "divider" }}>
                    <ShowChartOutlinedIcon fontSize="small" color="primary" />
                    <TimelineOutlinedIcon fontSize="small" />
                    <BarChartOutlinedIcon fontSize="small" />
                    <Typography sx={{ fontSize: "1.1rem" }}>T</Typography>
                    <Typography sx={{ fontSize: "1.1rem" }}>＋</Typography>
                </Stack>
                <Box sx={{ flex: 1, minWidth: 0, bgcolor: "#07111e" }}>
                    <svg
                        viewBox="0 0 900 350"
                        preserveAspectRatio="none"
                        width="100%"
                        height="100%"
                        role="img"
                        aria-label="Reliance daily candlestick research chart"
                    >
                        <defs>
                            <linearGradient id="chartGlow" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="0%" stopColor="#2563eb" stopOpacity="0.18" />
                                <stop offset="100%" stopColor="#2563eb" stopOpacity="0" />
                            </linearGradient>
                        </defs>
                        {[50, 110, 170, 230, 290].map((line) => (
                            <line key={line} x1="0" x2="900" y1={line} y2={line} stroke="#18273a" strokeWidth="1" />
                        ))}
                        {[120, 240, 360, 480, 600, 720, 840].map((line) => (
                            <line key={line} x1={line} x2={line} y1="0" y2="350" stroke="#132236" strokeWidth="1" />
                        ))}
                        <path
                            d="M0 260 C120 180, 190 235, 280 175 S430 140, 520 155 S680 95, 900 70 L900 350 L0 350 Z"
                            fill="url(#chartGlow)"
                        />
                        {candles.map((candle, index) => {
                            const x = 10 + index * 15.2;
                            const rising = candle.close >= candle.open;
                            const color = rising ? "#16d784" : "#ff4d5e";
                            return (
                                <g key={x}>
                                    <line x1={x} x2={x} y1={y(candle.high)} y2={y(candle.low)} stroke={color} strokeWidth="1.2" />
                                    <rect
                                        x={x - 3.5}
                                        y={Math.min(y(candle.open), y(candle.close))}
                                        width="7"
                                        height={Math.max(3, Math.abs(y(candle.open) - y(candle.close)))}
                                        fill={color}
                                        rx="1"
                                    />
                                </g>
                            );
                        })}
                        <line x1="0" x2="900" y1={y(2978.45)} y2={y(2978.45)} stroke="#35d07f" strokeDasharray="4 4" />
                        <rect x="835" y={y(2978.45) - 11} width="64" height="22" fill="#168451" rx="3" />
                        <text x="867" y={y(2978.45) + 4} textAnchor="middle" fill="white" fontSize="11">2,978.45</text>
                    </svg>
                </Box>
            </Box>
            <Stack direction="row" spacing={2} sx={{ height: 40, px: 2, alignItems: "center", bgcolor: "#091423" }}>
                <Typography color="primary.main" variant="caption">1D</Typography>
                <Typography color="text.secondary" variant="caption">5D</Typography>
                <Typography color="text.secondary" variant="caption">1M</Typography>
                <Typography color="text.secondary" variant="caption">YTD</Typography>
                <Typography color="text.secondary" variant="caption" sx={{ ml: "auto !important" }}>Research chart · local demo data</Typography>
            </Stack>
        </Card>
    );
}

export default TradingChart;
