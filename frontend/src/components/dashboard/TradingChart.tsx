import { useEffect, useRef, useState } from "react";
import {
    CandlestickSeries,
    ColorType,
    CrosshairMode,
    LineSeries,
    createChart,
    type IChartApi,
    type UTCTimestamp,
} from "lightweight-charts";

import BarChartOutlinedIcon from "@mui/icons-material/BarChartOutlined";
import ShowChartOutlinedIcon from "@mui/icons-material/ShowChartOutlined";
import TimelineOutlinedIcon from "@mui/icons-material/TimelineOutlined";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Card from "@mui/material/Card";
import Divider from "@mui/material/Divider";
import Link from "@mui/material/Link";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";

import { getMarketCandles } from "../../api/marketApi";

const ranges: Record<string, number> = {
    "1M": 22,
    "3M": 66,
    "6M": 132,
    "1Y": 220,
    ALL: 260,
};

type ChartCandle = {
    time: UTCTimestamp;
    open: number;
    high: number;
    low: number;
    close: number;
};

function calculateMovingAverage(data: ChartCandle[]) {
    return data.map((candle, index) => {
    const start = Math.max(0, index - 19);
    const window = data.slice(start, index + 1);
    return {
        time: candle.time,
        value: window.reduce((total, item) => total + item.close, 0) / window.length,
    };
    });
}

interface TradingChartProps {
    symbol: string;
    displayName?: string;
}

function TradingChart({ symbol, displayName }: TradingChartProps) {
    const containerRef = useRef<HTMLDivElement>(null);
    const chartRef = useRef<IChartApi | null>(null);
    const [activeRange, setActiveRange] = useState("6M");
    const [showIndicator, setShowIndicator] = useState(true);
    const [chartData, setChartData] = useState<ChartCandle[]>([]);
    const [dataLabel, setDataLabel] = useState("Loading delayed market data...");

    useEffect(() => {
        void getMarketCandles(symbol)
            .then((result) => {
                if (result.candles.length === 0) {
                    throw new Error("No candles returned.");
                }
                setChartData(
                    result.candles.map((candle) => ({
                        time: Math.floor(new Date(candle.time).getTime() / 1000) as UTCTimestamp,
                        open: candle.open,
                        high: candle.high,
                        low: candle.low,
                        close: candle.close,
                    })),
                );
                setDataLabel(`${result.source}${result.delayed ? " · delayed" : ""}`);
            })
            .catch(() => {
                setChartData([]);
                setDataLabel("Market candles unavailable · no generated data shown");
            });
    }, [symbol]);

    useEffect(() => {
        const container = containerRef.current;
        if (!container) return;

        const chart = createChart(container, {
            width: container.clientWidth,
            height: container.clientHeight,
            layout: {
                background: { type: ColorType.Solid, color: "#FFFFFF" },
                textColor: "#64748b",
                fontFamily: '"Inter", "Segoe UI", Arial, sans-serif',
                fontSize: 11,
                attributionLogo: false,
            },
            grid: {
                vertLines: { color: "rgba(148,163,184,.16)" },
                horzLines: { color: "rgba(148,163,184,.16)" },
            },
            crosshair: {
                mode: CrosshairMode.Normal,
                vertLine: { color: "#94a3b8", width: 1, style: 2, labelBackgroundColor: "#475569" },
                horzLine: { color: "#94a3b8", width: 1, style: 2, labelBackgroundColor: "#475569" },
            },
            rightPriceScale: { borderColor: "#e2e8f0", scaleMargins: { top: 0.08, bottom: 0.08 } },
            timeScale: {
                borderColor: "#e2e8f0",
                timeVisible: true,
                rightOffset: 5,
                barSpacing: 7,
                minBarSpacing: 1,
                lockVisibleTimeRangeOnResize: true,
            },
            handleScroll: true,
            handleScale: true,
        });

        const candles = chart.addSeries(CandlestickSeries, {
            upColor: "#089981",
            downColor: "#f23645",
            wickUpColor: "#089981",
            wickDownColor: "#f23645",
            borderVisible: false,
            priceLineColor: "#64748b",
            priceLineWidth: 1,
        });
        candles.setData(chartData);

        if (showIndicator) {
            const average = chart.addSeries(LineSeries, {
                color: "#3478f6",
                lineWidth: 2,
                priceLineVisible: false,
                lastValueVisible: false,
            });
            average.setData(calculateMovingAverage(chartData));
        }

        chartRef.current = chart;
        const visible = Math.min(ranges[activeRange], chartData.length);
        chart.timeScale().setVisibleLogicalRange({
            from: chartData.length - visible,
            to: chartData.length + 3,
        });

        const observer = new ResizeObserver(() => {
            chart.applyOptions({
                width: container.clientWidth,
                height: container.clientHeight,
            });
        });
        observer.observe(container);

        return () => {
            observer.disconnect();
            chart.remove();
            chartRef.current = null;
        };
    }, [activeRange, chartData, showIndicator]);

    function chooseRange(range: string) {
        setActiveRange(range);
    }

    return (
        <Card sx={{ height: 430, overflow: "hidden", bgcolor: "#ffffff", color: "#172033", boxShadow: "none" }}>
            <Stack direction="row" sx={{ height: 42, px: 1.5, alignItems: "center", justifyContent: "space-between", bgcolor: "#ffffff" }}>
                <Box>
                    <Typography sx={{ fontWeight: 800, fontSize: "0.78rem" }}>
                        {displayName ?? symbol} · 1D · NSE
                    </Typography>
                    <Typography color="text.secondary" sx={{ fontSize: "0.68rem" }}>
                        Historical research chart
                    </Typography>
                </Box>
                <Stack direction="row" spacing={0.25}>
                    {Object.keys(ranges).map((range) => (
                        <Button
                            key={range}
                            size="small"
                            variant={activeRange === range ? "contained" : "text"}
                            onClick={() => chooseRange(range)}
                        >
                            {range}
                        </Button>
                    ))}
                </Stack>
            </Stack>
            <Divider />
            <Box sx={{ display: "flex", height: 346 }}>
                <Stack sx={{ width: 42, py: 1, alignItems: "center", gap: 1.5, borderRight: "1px solid", borderColor: "divider" }}>
                    <ShowChartOutlinedIcon fontSize="small" color="primary" />
                    <TimelineOutlinedIcon fontSize="small" />
                    <BarChartOutlinedIcon
                        fontSize="small"
                        color={showIndicator ? "primary" : "inherit"}
                        onClick={() => setShowIndicator((value) => !value)}
                        sx={{ cursor: "pointer" }}
                    />
                    <Typography sx={{ fontSize: "1.1rem" }}>T</Typography>
                    <Typography sx={{ fontSize: "1.1rem" }}>＋</Typography>
                </Stack>
                <Box ref={containerRef} sx={{ flex: 1, minWidth: 0, height: "100%" }} />
            </Box>
            <Stack direction="row" sx={{ height: 40, px: 1.5, alignItems: "center", bgcolor: "#ffffff" }}>
                <Typography sx={{ color: "#64748b" }} variant="caption">
                    Drag to pan · wheel to zoom · {dataLabel}
                </Typography>
                <Link
                    href="https://www.tradingview.com/"
                    target="_blank"
                    rel="noreferrer"
                    variant="caption"
                    sx={{ ml: "auto" }}
                >
                    Charts by TradingView
                </Link>
            </Stack>
        </Card>
    );
}

export default TradingChart;
