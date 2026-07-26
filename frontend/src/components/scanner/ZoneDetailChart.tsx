import {
    BaselineSeries,
    CandlestickSeries,
    ColorType,
    CrosshairMode,
    createChart,
    type UTCTimestamp,
} from "lightweight-charts";
import { useEffect, useRef, useState } from "react";

import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Chip from "@mui/material/Chip";
import CircularProgress from "@mui/material/CircularProgress";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";

import { getMarketCandles } from "../../api/marketApi";
import type { ZoneResearchResult } from "../../types/scanner";

const patternLabels: Record<string, string> = {
    DROP_BASE_RALLY: "DBR",
    RALLY_BASE_RALLY: "RBR",
    RALLY_BASE_DROP: "RBD",
    DROP_BASE_DROP: "DBD",
};

function ZoneDetailChart({ result, zones = [result], height = 360, showTools = false }: { result: ZoneResearchResult; zones?: ZoneResearchResult[]; height?: number; showTools?: boolean }) {
    const containerRef = useRef<HTMLDivElement>(null);
    const chartRef = useRef<ReturnType<typeof createChart> | null>(null);
    const measuringRef = useRef(false);
    const measureStartRef = useRef<number | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [measuring, setMeasuring] = useState(false);
    const [measurement, setMeasurement] = useState("Measurement tool is off.");

    useEffect(() => {
        const container = containerRef.current;
        if (!container) return;
        let cancelled = false;
        setLoading(true);
        setError("");

        let chart = createChart(container, {
            width: container.clientWidth,
            height,
            layout: {
                background: { type: ColorType.Solid, color: "#07111e" },
                textColor: "#8fa1b8",
                attributionLogo: false,
            },
            grid: {
                vertLines: { color: "#132236" },
                horzLines: { color: "#18273a" },
            },
            crosshair: { mode: CrosshairMode.Normal },
            rightPriceScale: { borderColor: "#24344a" },
            timeScale: { borderColor: "#24344a", timeVisible: true },
            handleScroll: true,
            handleScale: true,
        });
        chartRef.current = chart;

        const observer = new ResizeObserver(() => {
            chart.applyOptions({ width: container.clientWidth });
        });
        observer.observe(container);

        const intraday = ["5m", "15m", "75m", "125m", "1H", "2H", "4H", "6H"].includes(result.timeframe);
        const chartPeriod = intraday ? "1mo" : result.timeframe === "1D" ? "1y" : "10y";
        const chartInterval = intraday ? (result.timeframe.includes("H") ? "1h" : result.timeframe === "5m" || result.timeframe === "125m" ? "5m" : "15m") : "1d";
        void getMarketCandles(result.symbol, chartPeriod, chartInterval, result.timeframe)
            .then((response) => {
                if (cancelled) return;
                const data = response.candles.map((candle) => ({
                    time: Math.floor(new Date(candle.time).getTime() / 1000) as UTCTimestamp,
                    open: candle.open,
                    high: candle.high,
                    low: candle.low,
                    close: candle.close,
                }));
                if (!data.length) throw new Error("No candle history is available.");

                const candles = chart.addSeries(CandlestickSeries, {
                    upColor: "#16d784",
                    downColor: "#ff4d5e",
                    wickUpColor: "#16d784",
                    wickDownColor: "#ff4d5e",
                    borderVisible: false,
                });
                candles.setData(data);
                chart.subscribeClick((param) => {
                    if (!measuringRef.current || !param.point) return;
                    const price = candles.coordinateToPrice(param.point.y);
                    if (price === null) return;
                    if (measureStartRef.current === null) {
                        measureStartRef.current = price;
                        setMeasurement(`Start ₹${price.toFixed(2)} · select the second point.`);
                        return;
                    }
                    const startPrice = measureStartRef.current;
                    const change = price - startPrice;
                    const percent = startPrice === 0 ? 0 : change / startPrice * 100;
                    setMeasurement(`₹${startPrice.toFixed(2)} → ₹${price.toFixed(2)} · ${change >= 0 ? "+" : ""}${change.toFixed(2)} (${percent >= 0 ? "+" : ""}${percent.toFixed(2)}%)`);
                    measureStartRef.current = null;
                });

                zones.forEach((displayZone, zoneIndex) => {
                if (displayZone.proximal_price !== null && displayZone.distal_price !== null) {
                    const demand = displayZone.zone_type === "DEMAND";
                    const zoneColor = demand ? "#1d8cff" : "#ff2f68";
                    const zone = chart.addSeries(BaselineSeries, {
                        baseValue: { type: "price", price: displayZone.distal_price },
                        topLineColor: zoneColor,
                        topFillColor1: demand ? `rgba(29,140,255,${Math.max(.24, .52 - zoneIndex * .08)})` : `rgba(255,47,104,${Math.max(.24, .52 - zoneIndex * .08)})`,
                        topFillColor2: demand ? "rgba(29,140,255,.22)" : "rgba(255,47,104,.22)",
                        bottomLineColor: zoneColor,
                        bottomFillColor1: demand ? "rgba(29,140,255,.38)" : "rgba(255,47,104,.38)",
                        bottomFillColor2: demand ? "rgba(29,140,255,.22)" : "rgba(255,47,104,.22)",
                        lineWidth: 2,
                        priceLineVisible: false,
                        lastValueVisible: false,
                    });
                    const start = Math.max(0, Math.min(displayZone.base_index ?? data.length - 45, data.length - 1));
                    zone.setData(data.slice(start).map((candle) => ({
                        time: candle.time,
                        value: displayZone.proximal_price as number,
                    })));
                }
                });

                chart.timeScale().fitContent();
                setLoading(false);
            })
            .catch(() => {
                if (cancelled) return;
                setError("Chart data is unavailable. Start the backend market-data service and try again.");
                setLoading(false);
            });

        return () => {
            cancelled = true;
            observer.disconnect();
            chart.remove();
            chartRef.current = null;
            chart = null as never;
        };
    }, [height, result, zones]);

    function toggleMeasure() {
        const next = !measuring;
        setMeasuring(next);
        measuringRef.current = next;
        measureStartRef.current = null;
        setMeasurement(next ? "Select two chart points to measure price change." : "Measurement tool is off.");
    }

    return (
        <Box sx={{ bgcolor: "#07111e", border: "1px solid", borderColor: "divider", borderRadius: 1.5, overflow: "hidden" }}>
            <Stack direction="row" sx={{ px: 2, py: 1.2, alignItems: "center", gap: 1, borderBottom: "1px solid", borderColor: "divider" }}>
                <Typography sx={{ fontWeight: 850 }}>{result.symbol}</Typography>
                <Typography color={result.zone_type === "DEMAND" ? "#60a5fa" : "#ff6b8a"} sx={{ fontSize: ".68rem", fontWeight: 850 }}>
                    {result.zone_type} · {patternLabels[result.pattern_type ?? ""] ?? result.pattern_type ?? "Pattern pending"}
                </Typography>
                <Typography color="text.secondary" sx={{ ml: "auto", fontSize: ".68rem" }}>
                    Zone {result.distal_price?.toLocaleString("en-IN")}–{result.proximal_price?.toLocaleString("en-IN")} · {result.timeframe ?? "1D"}
                </Typography>
            </Stack>
            {showTools && <Stack direction="row" spacing={1} sx={{ px: 1.5, py: 1, alignItems: "center", borderBottom: "1px solid", borderColor: "divider" }}>
                <Button size="small" variant="outlined" onClick={() => chartRef.current?.timeScale().fitContent()}>Fit chart</Button>
                <Button size="small" variant={measuring ? "contained" : "outlined"} onClick={toggleMeasure}>Measure range</Button>
                <Chip size="small" label="Crosshair" />
                <Chip size="small" label="Drag to pan" />
                <Chip size="small" label="Wheel to zoom" />
                <Typography variant="caption" color={measuring ? "primary.main" : "text.secondary"} sx={{ ml: "auto" }}>{measurement}</Typography>
            </Stack>}
            {loading && <Box sx={{ height, display: "grid", placeItems: "center" }}><CircularProgress size={28} /></Box>}
            {error && <Alert severity="warning">{error}</Alert>}
            <Box ref={containerRef} sx={{ height: loading || error ? 0 : height }} />
            <Typography color="text.secondary" sx={{ px: 2, py: 1, fontSize: ".62rem" }}>
                Highlighted area is the detected research zone · drag to pan · wheel to zoom · delayed data may apply
            </Typography>
        </Box>
    );
}

export default ZoneDetailChart;
