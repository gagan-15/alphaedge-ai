import {
    BaselineSeries,
    CandlestickSeries,
    ColorType,
    CrosshairMode,
    LineSeries,
    LineStyle,
    createChart,
    type ISeriesApi,
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
import type { ConfluenceChartOverlay, ZoneResearchResult } from "../../types/scanner";
import { zoneSequenceLabel } from "./zoneLabels";

const patternLabels: Record<string, string> = {
    DROP_BASE_RALLY: "DBR",
    RALLY_BASE_RALLY: "RBR",
    RALLY_BASE_DROP: "RBD",
    DROP_BASE_DROP: "DBD",
};

interface ZoneDetailChartProps {
    result: ZoneResearchResult;
    zones?: ZoneResearchResult[];
    confluenceOverlays?: ConfluenceChartOverlay[];
    height?: number;
    showTools?: boolean;
}

function ZoneDetailChart({
    result,
    zones = [result],
    confluenceOverlays = [],
    height = 360,
    showTools = false,
}: ZoneDetailChartProps) {
    const containerRef = useRef<HTMLDivElement>(null);
    const chartRef = useRef<ReturnType<typeof createChart> | null>(null);
    const candleSeriesRef = useRef<ISeriesApi<"Candlestick"> | null>(null);
    const baseZoneAreaSeriesRef = useRef<ISeriesApi<"Baseline">[]>([]);
    const baseZoneBoundarySeriesRef = useRef<ISeriesApi<"Line">[]>([]);
    const confluenceSeriesRef = useRef<ISeriesApi<"Baseline">[]>([]);
    const confluenceBoundarySeriesRef = useRef<ISeriesApi<"Line">[]>([]);
    const measurementAreaSeriesRef = useRef<ISeriesApi<"Baseline"> | null>(null);
    const measurementBoundarySeriesRef = useRef<ISeriesApi<"Line">[]>([]);
    const candleTimesRef = useRef<UTCTimestamp[]>([]);
    const candleStepRef = useRef(86_400);
    const measuringRef = useRef(false);
    const crosshairVisibleRef = useRef(true);
    const measureStartRef = useRef<{ price: number; time: UTCTimestamp } | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [measuring, setMeasuring] = useState(false);
    const [crosshairVisible, setCrosshairVisible] = useState(true);
    const [measurement, setMeasurement] = useState("Measurement tool is off.");
    const [chartReadyVersion, setChartReadyVersion] = useState(0);
    const [zonesVisible, setZonesVisible] = useState(true);

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
            crosshair: { mode: crosshairVisibleRef.current ? CrosshairMode.Normal : CrosshairMode.Hidden },
            rightPriceScale: { borderColor: "#24344a" },
            timeScale: { borderColor: "#24344a", timeVisible: true },
            handleScroll: {
                mouseWheel: true,
                pressedMouseMove: true,
                horzTouchDrag: true,
                vertTouchDrag: true,
            },
            handleScale: {
                axisPressedMouseMove: true,
                mouseWheel: true,
                pinch: true,
            },
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
                candleSeriesRef.current = candles;
                candles.setData(data);
                const recentSteps = data.slice(-12).reduce<number[]>((steps, candle, index, recent) => {
                    if (index > 0) steps.push(Number(candle.time) - Number(recent[index - 1].time));
                    return steps;
                }, []).filter((step) => step > 0).sort((left, right) => left - right);
                const candleStep = recentSteps[Math.floor(recentSteps.length / 2)] || 86_400;
                candleTimesRef.current = data.map((candle) => candle.time);
                candleStepRef.current = candleStep;
                const futureZonePoints = 12;
                chart.subscribeClick((param) => {
                    if (!measuringRef.current || !param.point || !param.time) return;
                    const price = candles.coordinateToPrice(param.point.y);
                    if (price === null) return;
                    if (measureStartRef.current === null) {
                        if (measurementAreaSeriesRef.current) {
                            chart.removeSeries(measurementAreaSeriesRef.current);
                            measurementAreaSeriesRef.current = null;
                        }
                        measurementBoundarySeriesRef.current.forEach((series) => chart.removeSeries(series));
                        measurementBoundarySeriesRef.current = [];
                        measureStartRef.current = {
                            price,
                            time: Number(param.time) as UTCTimestamp,
                        };
                        setMeasurement(`Start ₹${price.toFixed(2)} · select the second point.`);
                        return;
                    }
                    const startPrice = measureStartRef.current.price;
                    const startTime = measureStartRef.current.time;
                    const change = price - startPrice;
                    const percent = startPrice === 0 ? 0 : change / startPrice * 100;
                    const lower = Math.min(startPrice, price);
                    const upper = Math.max(startPrice, price);
                    const secondTime = Number(param.time) as UTCTimestamp;
                    const from = Math.min(Number(startTime), Number(secondTime)) as UTCTimestamp;
                    const to = Math.max(Number(startTime), Number(secondTime)) as UTCTimestamp;
                    const area = chart.addSeries(BaselineSeries, {
                        baseValue: { type: "price", price: lower },
                        topLineColor: "#f5b942",
                        topFillColor1: "rgba(245,185,66,.28)",
                        topFillColor2: "rgba(245,185,66,.14)",
                        bottomLineColor: "#f5b942",
                        bottomFillColor1: "rgba(245,185,66,.12)",
                        bottomFillColor2: "rgba(245,185,66,.05)",
                        lineWidth: 2,
                        priceLineVisible: false,
                        lastValueVisible: false,
                    });
                    const upperLine = chart.addSeries(LineSeries, {
                        color: "#f5b942",
                        lineWidth: 2,
                        priceLineVisible: false,
                        lastValueVisible: false,
                    });
                    const lowerLine = chart.addSeries(LineSeries, {
                        color: "#f5b942",
                        lineWidth: 2,
                        priceLineVisible: false,
                        lastValueVisible: false,
                    });
                    const rangeData = [{ time: from, value: upper }, { time: to, value: upper }];
                    area.setData(rangeData);
                    upperLine.setData(rangeData);
                    lowerLine.setData([{ time: from, value: lower }, { time: to, value: lower }]);
                    measurementAreaSeriesRef.current = area;
                    measurementBoundarySeriesRef.current = [upperLine, lowerLine];
                    setMeasurement(`₹${startPrice.toFixed(2)} → ₹${price.toFixed(2)} · ${change >= 0 ? "+" : ""}${change.toFixed(2)} (${percent >= 0 ? "+" : ""}${percent.toFixed(2)}%)`);
                    measureStartRef.current = null;
                });

                zones.forEach((displayZone, zoneIndex) => {
                if (displayZone.proximal_price !== null && displayZone.distal_price !== null) {
                    const demand = displayZone.zone_type === "DEMAND";
                    const zoneColor = demand ? "#1d8cff" : "#ff2f68";
                    const zoneLabel = zoneSequenceLabel(zones, zoneIndex);
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
                    const zoneData = data.slice(start).map((candle) => ({
                        time: candle.time,
                        value: displayZone.proximal_price as number,
                    }));
                    const latestTime = Number(data[data.length - 1].time);
                    for (let point = 1; point <= futureZonePoints; point += 1) {
                        zoneData.push({
                            time: (latestTime + candleStep * point) as UTCTimestamp,
                            value: displayZone.proximal_price as number,
                        });
                    }
                    zone.setData(zoneData);
                    baseZoneAreaSeriesRef.current.push(zone);
                    const proximalBoundary = chart.addSeries(LineSeries, {
                        color: zoneColor,
                        lineWidth: 2,
                        lineStyle: LineStyle.Solid,
                        priceLineVisible: false,
                        lastValueVisible: true,
                        title: `${zoneLabel} PROXIMAL`,
                    });
                    const distalBoundary = chart.addSeries(LineSeries, {
                        color: zoneColor,
                        lineWidth: 1,
                        lineStyle: LineStyle.Dashed,
                        priceLineVisible: false,
                        lastValueVisible: true,
                        title: `${zoneLabel} DISTAL`,
                    });
                    proximalBoundary.setData(zoneData);
                    distalBoundary.setData(zoneData.map((point) => ({
                        time: point.time,
                        value: displayZone.distal_price as number,
                    })));
                    baseZoneBoundarySeriesRef.current.push(proximalBoundary, distalBoundary);
                }
                });

                chart.timeScale().fitContent();
                chart.timeScale().applyOptions({ rightOffset: 3 });
                setChartReadyVersion((version) => version + 1);
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
            candleSeriesRef.current = null;
            baseZoneAreaSeriesRef.current = [];
            baseZoneBoundarySeriesRef.current = [];
            confluenceSeriesRef.current = [];
            confluenceBoundarySeriesRef.current = [];
            measurementAreaSeriesRef.current = null;
            measurementBoundarySeriesRef.current = [];
            candleTimesRef.current = [];
            chart = null as never;
        };
    }, [height, result, zones]);

    useEffect(() => {
        const chart = chartRef.current;
        const candles = candleSeriesRef.current;
        const times = candleTimesRef.current;
        if (!chart || !candles || !times.length) return;

        confluenceBoundarySeriesRef.current.forEach((series) => chart.removeSeries(series));
        confluenceSeriesRef.current.forEach((series) => chart.removeSeries(series));
        confluenceBoundarySeriesRef.current = [];
        confluenceSeriesRef.current = [];

        const styles = [LineStyle.Dashed, LineStyle.Dotted, LineStyle.LargeDashed, LineStyle.SparseDotted];
        confluenceOverlays.forEach((overlay, index) => {
            const demand = overlay.zoneType === "DEMAND";
            const color = demand ? "#1d8cff" : "#ff2f68";
            const lower = Math.min(overlay.proximalPrice, overlay.distalPrice);
            const upper = Math.max(overlay.proximalPrice, overlay.distalPrice);
            const series = chart.addSeries(BaselineSeries, {
                baseValue: { type: "price", price: lower },
                topLineColor: color,
                topFillColor1: demand ? "rgba(29,140,255,.18)" : "rgba(255,47,104,.18)",
                topFillColor2: demand ? "rgba(29,140,255,.08)" : "rgba(255,47,104,.08)",
                bottomLineColor: color,
                bottomFillColor1: demand ? "rgba(29,140,255,.12)" : "rgba(255,47,104,.12)",
                bottomFillColor2: "rgba(0,0,0,0)",
                lineWidth: 2,
                lineStyle: styles[index % styles.length],
                priceLineVisible: false,
                lastValueVisible: false,
            });
            const startIndex = Math.max(0, times.length - Math.max(36, Math.floor(times.length * .3)));
            const overlayData = times.slice(startIndex).map((time) => ({
                time,
                value: upper,
            }));
            const latestTime = Number(times[times.length - 1]);
            for (let point = 1; point <= 12; point += 1) {
                overlayData.push({
                    time: (latestTime + candleStepRef.current * point) as UTCTimestamp,
                    value: upper,
                });
            }
            series.setData(overlayData);
            confluenceSeriesRef.current.push(series);
            const upperBoundary = chart.addSeries(LineSeries, {
                color,
                lineWidth: 1,
                lineStyle: styles[index % styles.length],
                priceLineVisible: false,
                lastValueVisible: true,
                title: `${overlay.timeframe} HTF`,
            });
            const lowerBoundary = chart.addSeries(LineSeries, {
                color,
                lineWidth: 1,
                lineStyle: styles[index % styles.length],
                priceLineVisible: false,
                lastValueVisible: false,
            });
            upperBoundary.setData(overlayData);
            lowerBoundary.setData(overlayData.map((point) => ({ ...point, value: lower })));
            confluenceBoundarySeriesRef.current.push(upperBoundary, lowerBoundary);
        });
    }, [chartReadyVersion, confluenceOverlays]);

    function toggleZones() {
        const next = !zonesVisible;
        setZonesVisible(next);
        baseZoneAreaSeriesRef.current.forEach((series) => series.applyOptions({ visible: next }));
        baseZoneBoundarySeriesRef.current.forEach((series) => series.applyOptions({ visible: next }));
        confluenceSeriesRef.current.forEach((series) => series.applyOptions({ visible: next }));
        confluenceBoundarySeriesRef.current.forEach((series) => series.applyOptions({ visible: next }));
    }

    function toggleMeasure() {
        const next = !measuring;
        setMeasuring(next);
        measuringRef.current = next;
        measureStartRef.current = null;
        setMeasurement(next ? "Select two chart points to measure price change." : "Measurement tool is off.");
    }

    function clearMeasurement() {
        const chart = chartRef.current;
        if (!chart) return;
        if (measurementAreaSeriesRef.current) {
            chart.removeSeries(measurementAreaSeriesRef.current);
            measurementAreaSeriesRef.current = null;
        }
        measurementBoundarySeriesRef.current.forEach((series) => chart.removeSeries(series));
        measurementBoundarySeriesRef.current = [];
        measureStartRef.current = null;
        setMeasurement(measuring ? "Select two chart points to highlight a range." : "Measurement tool is off.");
    }

    function toggleCrosshair() {
        const next = !crosshairVisible;
        setCrosshairVisible(next);
        crosshairVisibleRef.current = next;
        chartRef.current?.applyOptions({
            crosshair: { mode: next ? CrosshairMode.Normal : CrosshairMode.Hidden },
        });
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
                <Button size="small" variant="outlined" onClick={clearMeasurement}>Clear measurement</Button>
                <Button size="small" variant={crosshairVisible ? "contained" : "outlined"} onClick={toggleCrosshair}>Crosshair {crosshairVisible ? "On" : "Off"}</Button>
                <Button size="small" variant={zonesVisible ? "outlined" : "contained"} onClick={toggleZones}>{zonesVisible ? "Hide all zones" : "Show zones"}</Button>
                <Chip size="small" label="Hold left mouse button and drag to pan" />
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
