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

const ranges: Record<string, number> = {
    "1M": 22,
    "3M": 66,
    "6M": 132,
    "1Y": 220,
    ALL: 260,
};

const candleData = Array.from({ length: 260 }, (_, index) => {
    const trend = 2480 + index * 1.9;
    const wave = Math.sin(index * 0.21) * 55 + Math.sin(index * 0.053) * 70;
    const open = trend + wave;
    const close = open + Math.sin(index * 1.41) * 24;
    const date = new Date(Date.UTC(2025, 6, 1 + index));
    return {
        time: Math.floor(date.getTime() / 1000) as UTCTimestamp,
        open,
        high: Math.max(open, close) + 11 + (index % 5) * 2,
        low: Math.min(open, close) - 10 - (index % 4) * 2,
        close,
    };
});

const movingAverage = candleData.map((candle, index) => {
    const start = Math.max(0, index - 19);
    const window = candleData.slice(start, index + 1);
    return {
        time: candle.time,
        value: window.reduce((total, item) => total + item.close, 0) / window.length,
    };
});

function TradingChart() {
    const containerRef = useRef<HTMLDivElement>(null);
    const chartRef = useRef<IChartApi | null>(null);
    const [activeRange, setActiveRange] = useState("6M");
    const [showIndicator, setShowIndicator] = useState(true);

    useEffect(() => {
        const container = containerRef.current;
        if (!container) return;

        const chart = createChart(container, {
            width: container.clientWidth,
            height: container.clientHeight,
            layout: {
                background: { type: ColorType.Solid, color: "#07111e" },
                textColor: "#91a3ba",
                attributionLogo: false,
            },
            grid: {
                vertLines: { color: "#132236" },
                horzLines: { color: "#18273a" },
            },
            crosshair: { mode: CrosshairMode.Normal },
            rightPriceScale: { borderColor: "#24344a" },
            timeScale: {
                borderColor: "#24344a",
                timeVisible: true,
                rightOffset: 4,
            },
            handleScroll: true,
            handleScale: true,
        });

        const candles = chart.addSeries(CandlestickSeries, {
            upColor: "#16d784",
            downColor: "#ff4d5e",
            wickUpColor: "#16d784",
            wickDownColor: "#ff4d5e",
            borderVisible: false,
            priceLineColor: "#35d07f",
        });
        candles.setData(candleData);

        if (showIndicator) {
            const average = chart.addSeries(LineSeries, {
                color: "#3478f6",
                lineWidth: 2,
                priceLineVisible: false,
                lastValueVisible: false,
            });
            average.setData(movingAverage);
        }

        chartRef.current = chart;
        const visible = ranges[activeRange];
        chart.timeScale().setVisibleLogicalRange({
            from: candleData.length - visible,
            to: candleData.length + 3,
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
    }, [activeRange, showIndicator]);

    function chooseRange(range: string) {
        setActiveRange(range);
    }

    return (
        <Card sx={{ height: 430, overflow: "hidden" }}>
            <Stack direction="row" sx={{ height: 42, px: 1.5, alignItems: "center", justifyContent: "space-between", bgcolor: "#091423" }}>
                <Box>
                    <Typography sx={{ fontWeight: 800, fontSize: "0.78rem" }}>RELIANCE INDUSTRIES LTD · 1D · NSE</Typography>
                    <Typography color="success.main" sx={{ fontSize: "0.68rem" }}>O 2,966.00&nbsp; H 2,979.50&nbsp; L 2,964.00&nbsp; C 2,978.45&nbsp; +0.83%</Typography>
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
            <Stack direction="row" sx={{ height: 40, px: 1.5, alignItems: "center", bgcolor: "#091423" }}>
                <Typography color="text.secondary" variant="caption">
                    Drag to pan · wheel to zoom · hover for crosshair
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
