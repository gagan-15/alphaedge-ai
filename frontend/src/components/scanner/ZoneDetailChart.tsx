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
import { useCallback, useEffect, useRef, useState } from "react";

import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import ButtonBase from "@mui/material/ButtonBase";
import Chip from "@mui/material/Chip";
import CircularProgress from "@mui/material/CircularProgress";
import Checkbox from "@mui/material/Checkbox";
import FormControl from "@mui/material/FormControl";
import InputLabel from "@mui/material/InputLabel";
import ListItemText from "@mui/material/ListItemText";
import MenuItem from "@mui/material/MenuItem";
import Select, { type SelectChangeEvent } from "@mui/material/Select";
import Stack from "@mui/material/Stack";
import Switch from "@mui/material/Switch";
import Typography from "@mui/material/Typography";
import Tooltip from "@mui/material/Tooltip";
import ViewSidebarOutlinedIcon from "@mui/icons-material/ViewSidebarOutlined";

import { getMarketCandles } from "../../api/marketApi";
import type { ConfluenceChartOverlay, ZoneResearchResult } from "../../types/scanner";
import { zoneSequenceLabel } from "./zoneLabels";
import { overlayStyles } from "../../services/overlayService";
import type { DeveloperChartZone } from "./developerZones";
import {
    createUserChartRectangle,
    clearUserChartRectangles,
    formatAnnotationPrice,
    removeUserChartRectangle,
    type RectangleDraftPoint,
    type UserChartRectangle,
} from "./chartAnnotations";

const noDeveloperZones: DeveloperChartZone[] = [];

const patternLabels: Record<string, string> = {
    DROP_BASE_RALLY: "DBR",
    RALLY_BASE_RALLY: "RBR",
    RALLY_BASE_DROP: "RBD",
    DROP_BASE_DROP: "DBD",
};
const confluenceTimeframes = [
    { timeframe: "1D", name: "Daily" },
    { timeframe: "1W", name: "Weekly" },
    { timeframe: "1M", name: "Monthly" },
    { timeframe: "3M", name: "Quarterly" },
    { timeframe: "6M", name: "Half-Yearly" },
    { timeframe: "1Y", name: "Yearly" },
];
const indicatorOptions = [
    { id: "EMA_9", label: "EMA 9", kind: "EMA", period: 9, color: "#f59e0b" },
    { id: "EMA_20", label: "EMA 20", kind: "EMA", period: 20, color: "#a855f7" },
    { id: "EMA_50", label: "EMA 50", kind: "EMA", period: 50, color: "#3b82f6" },
    { id: "EMA_100", label: "EMA 100", kind: "EMA", period: 100, color: "#22d3ee" },
    { id: "EMA_200", label: "EMA 200", kind: "EMA", period: 200, color: "#f43f5e" },
    { id: "SMA_20", label: "SMA 20", kind: "SMA", period: 20, color: "#84cc16" },
    { id: "SMA_50", label: "SMA 50", kind: "SMA", period: 50, color: "#eab308" },
    { id: "SMA_100", label: "SMA 100", kind: "SMA", period: 100, color: "#06b6d4" },
    { id: "SMA_200", label: "SMA 200", kind: "SMA", period: 200, color: "#ec4899" },
] as const;
const indicatorPreferenceKey = "alphaedge.chart.indicators";

const inactiveLifecycleStatuses = new Set([
    "TESTED",
    "TESTED_RESPECTED",
    "RETESTED",
    "MITIGATED",
    "INVALIDATED",
    "REMOVED",
]);

function isInactiveLifecycle(status?: string | null): boolean {
    return inactiveLifecycleStatuses.has((status ?? "").trim().toUpperCase());
}

function readIndicatorPreference(): string[] {
    try {
        const parsed = JSON.parse(localStorage.getItem(indicatorPreferenceKey) ?? "[]");
        return Array.isArray(parsed) ? parsed.map(String) : [];
    } catch {
        return [];
    }
}

interface ZoneDetailChartProps {
    result: ZoneResearchResult;
    zones?: ZoneResearchResult[];
    selectedZoneId?: string;
    confluenceOverlays?: ConfluenceChartOverlay[];
    availableConfluenceOverlays?: ConfluenceChartOverlay[];
    onToggleConfluenceOverlay?: (overlay: ConfluenceChartOverlay) => void;
    onInspectConfluenceOverlay?: (timeframe: string) => void;
    inspectedConfluenceTimeframe?: string;
    onResetChart?: () => void;
    height?: number;
    showTools?: boolean;
    developerMode?: boolean;
    developerZones?: DeveloperChartZone[];
    analysisPanelOpen?: boolean;
    onToggleAnalysisPanel?: () => void;
}

function ZoneDetailChart({
    result,
    zones = [result],
    selectedZoneId,
    confluenceOverlays = [],
    availableConfluenceOverlays = [],
    onToggleConfluenceOverlay,
    onInspectConfluenceOverlay,
    inspectedConfluenceTimeframe,
    onResetChart,
    height = 360,
    showTools = false,
    developerMode = false,
    developerZones = noDeveloperZones,
    analysisPanelOpen = false,
    onToggleAnalysisPanel,
}: ZoneDetailChartProps) {
    const containerRef = useRef<HTMLDivElement>(null);
    const chartRef = useRef<ReturnType<typeof createChart> | null>(null);
    const candleSeriesRef = useRef<ISeriesApi<"Candlestick"> | null>(null);
    const baseZoneAreaSeriesRef = useRef<ISeriesApi<"Baseline">[]>([]);
    const baseZoneBoundarySeriesRef = useRef<ISeriesApi<"Line">[]>([]);
    const zoneSeriesMapRef = useRef(new Map<string, {
        area: ISeriesApi<"Baseline">;
        proximal: ISeriesApi<"Line">;
        distal: ISeriesApi<"Line">;
        demand: boolean;
        status: DeveloperChartZone["zoneStatus"];
        inactiveLifecycle: boolean;
    }>());
    const zoneBorderDefinitionsRef = useRef<Array<{
        id: string;
        from: UTCTimestamp;
        to: UTCTimestamp;
        proximal: number;
        distal: number;
        color: string;
        status: DeveloperChartZone["zoneStatus"];
    }>>([]);
    const confluenceSeriesRef = useRef<ISeriesApi<"Baseline">[]>([]);
    const confluenceBoundarySeriesRef = useRef<ISeriesApi<"Line">[]>([]);
    const confluenceSeriesMapRef = useRef(new Map<ISeriesApi<"Baseline">, ConfluenceChartOverlay>());
    const measurementAreaSeriesRef = useRef<ISeriesApi<"Baseline"> | null>(null);
    const measurementBoundarySeriesRef = useRef<ISeriesApi<"Line">[]>([]);
    const indicatorSeriesRef = useRef<ISeriesApi<"Line">[]>([]);
    const measurementSelectionRef = useRef<{
        from: UTCTimestamp;
        to: UTCTimestamp;
        lower: number;
        upper: number;
        text: string;
    } | null>(null);
    const candleTimesRef = useRef<UTCTimestamp[]>([]);
    const candleDataRef = useRef<Array<{ time: UTCTimestamp; close: number }>>([]);
    const candleStepRef = useRef(86_400);
    const measuringRef = useRef(false);
    const crosshairVisibleRef = useRef(true);
    const measureStartRef = useRef<{
        price: number;
        time: UTCTimestamp;
        pointX: number;
        pointY: number;
    } | null>(null);
    const rectangleModeRef = useRef(false);
    const rectangleDraftStartRef = useRef<RectangleDraftPoint | null>(null);
    const rectanglesRef = useRef<UserChartRectangle[]>([]);
    const rectangleSequenceRef = useRef(0);
    const rectangleContextRef = useRef({ symbol: result.symbol, timeframe: result.timeframe });
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [measuring, setMeasuring] = useState(false);
    const [crosshairVisible, setCrosshairVisible] = useState(true);
    const [measurement, setMeasurement] = useState("Measurement tool is off.");
    const [chartReadyVersion, setChartReadyVersion] = useState(0);
    const [zonesVisible, setZonesVisible] = useState(true);
    const [htfLocationVisible, setHtfLocationVisible] = useState(true);
    const [gridVisible, setGridVisible] = useState(false);
    const [detailsVisible, setDetailsVisible] = useState(false);
    const [measurementLabel, setMeasurementLabel] = useState<{ left: number; top: number; text: string } | null>(null);
    const [rectangleMode, setRectangleMode] = useState(false);
    const [selectedRectangleId, setSelectedRectangleId] = useState<string | null>(null);
    const [rectangleDraft, setRectangleDraft] = useState<UserChartRectangle | null>(null);
    const [rectangleOverlays, setRectangleOverlays] = useState<Array<UserChartRectangle & {
        left: number;
        top: number;
        width: number;
        height: number;
    }>>([]);
    const [zoneBorders, setZoneBorders] = useState<Array<{
        id: string;
        left: number;
        top: number;
        width: number;
        height: number;
        color: string;
        status: DeveloperChartZone["zoneStatus"];
    }>>([]);
    const [selectedIndicators, setSelectedIndicators] = useState<string[]>(readIndicatorPreference);
    const [developerTooltip, setDeveloperTooltip] = useState<{ left: number; top: number; zone: DeveloperChartZone } | null>(null);
    const executionIndex = confluenceTimeframes.findIndex((item) => item.timeframe === result.timeframe);
    const higherTimeframeButtons = executionIndex < 0 ? [] : confluenceTimeframes.slice(executionIndex + 1);
    const inspectedOverlay = availableConfluenceOverlays.find((overlay) => overlay.timeframe === inspectedConfluenceTimeframe);
    const selectedLocation = confluenceOverlays[0];
    const updateMeasurementLabel = useCallback(() => {
        const chart = chartRef.current;
        const candles = candleSeriesRef.current;
        const selection = measurementSelectionRef.current;
        if (!chart || !candles || !selection) {
            setMeasurementLabel(null);
            return;
        }
        const fromX = chart.timeScale().timeToCoordinate(selection.from);
        const toX = chart.timeScale().timeToCoordinate(selection.to);
        const upperY = candles.priceToCoordinate(selection.upper);
        const lowerY = candles.priceToCoordinate(selection.lower);
        if (fromX === null || toX === null || upperY === null || lowerY === null) {
            setMeasurementLabel(null);
            return;
        }
        setMeasurementLabel({
            left: Math.min(fromX, toX) + Math.abs(toX - fromX) / 2,
            top: Math.min(upperY, lowerY) + Math.abs(lowerY - upperY) / 2,
            text: selection.text,
        });
    }, []);
    const updateZoneBorders = useCallback(() => {
        const chart = chartRef.current;
        const candles = candleSeriesRef.current;
        if (!chart || !candles) {
            setZoneBorders([]);
            return;
        }
        const next = zoneBorderDefinitionsRef.current.flatMap((zone) => {
            const fromX = chart.timeScale().timeToCoordinate(zone.from);
            const toX = chart.timeScale().timeToCoordinate(zone.to);
            const proximalY = candles.priceToCoordinate(zone.proximal);
            const distalY = candles.priceToCoordinate(zone.distal);
            if (fromX === null || toX === null || proximalY === null || distalY === null) return [];
            return [{
                id: zone.id,
                left: Math.min(fromX, toX),
                top: Math.min(proximalY, distalY),
                width: Math.max(1, Math.abs(toX - fromX)),
                height: Math.max(1, Math.abs(distalY - proximalY)),
                color: zone.color,
                status: zone.status,
            }];
        });
        setZoneBorders(next);
    }, []);
    const updateRectangleOverlays = useCallback((draft?: UserChartRectangle | null) => {
        const chart = chartRef.current;
        const candles = candleSeriesRef.current;
        if (!chart || !candles) {
            setRectangleOverlays([]);
            return;
        }
        const context = rectangleContextRef.current;
        const saved = rectanglesRef.current.filter(
            (rectangle) => rectangle.symbol === context.symbol && rectangle.timeframe === context.timeframe,
        );
        const source = draft ? [...saved, draft] : saved;
        setRectangleOverlays(source.flatMap((rectangle) => {
            const startX = chart.timeScale().timeToCoordinate(rectangle.startTime);
            const endX = chart.timeScale().timeToCoordinate(rectangle.endTime);
            const upperY = candles.priceToCoordinate(rectangle.upperPrice);
            const lowerY = candles.priceToCoordinate(rectangle.lowerPrice);
            if (startX === null || endX === null || upperY === null || lowerY === null) return [];
            return [{
                ...rectangle,
                left: Math.min(startX, endX),
                top: Math.min(upperY, lowerY),
                width: Math.max(2, Math.abs(endX - startX)),
                height: Math.max(2, Math.abs(lowerY - upperY)),
            }];
        }));
    }, []);

    useEffect(() => {
        const container = containerRef.current;
        if (!container) return;
        let cancelled = false;
        const confluenceSeriesMap = confluenceSeriesMapRef.current;
        const zoneSeriesMap = zoneSeriesMapRef.current;
        setLoading(true);
        setError("");

        let chart = createChart(container, {
            width: container.clientWidth,
            height,
            layout: {
                background: { type: ColorType.Solid, color: "#FFFFFF" },
                textColor: "#64748b",
                fontFamily: '"Inter", "Segoe UI", Arial, sans-serif',
                fontSize: 11,
                attributionLogo: false,
            },
            grid: {
                vertLines: { color: "rgba(148,163,184,0)", style: LineStyle.Solid },
                horzLines: { color: "rgba(148,163,184,0)", style: LineStyle.Solid },
            },
            crosshair: {
                mode: crosshairVisibleRef.current ? CrosshairMode.Normal : CrosshairMode.Hidden,
                vertLine: { color: "#94a3b8", width: 1, style: LineStyle.Dashed, labelBackgroundColor: "#475569" },
                horzLine: { color: "#94a3b8", width: 1, style: LineStyle.Dashed, labelBackgroundColor: "#475569" },
            },
            rightPriceScale: { borderColor: "#e2e8f0", scaleMargins: { top: 0.08, bottom: 0.08 } },
            timeScale: { borderColor: "#e2e8f0", timeVisible: true, rightOffset: 5, barSpacing: 7, minBarSpacing: 1, lockVisibleTimeRangeOnResize: true },
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
            updateMeasurementLabel();
            updateZoneBorders();
            updateRectangleOverlays(rectangleDraft);
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
                    upColor: "#089981",
                    downColor: "#f23645",
                    wickUpColor: "#089981",
                    wickDownColor: "#f23645",
                    borderVisible: false,
                    priceLineColor: "#64748b",
                    priceLineWidth: 1,
                });
                candleSeriesRef.current = candles;
                candles.setData(data);
                const recentSteps = data.slice(-12).reduce<number[]>((steps, candle, index, recent) => {
                    if (index > 0) steps.push(Number(candle.time) - Number(recent[index - 1].time));
                    return steps;
                }, []).filter((step) => step > 0).sort((left, right) => left - right);
                const candleStep = recentSteps[Math.floor(recentSteps.length / 2)] || 86_400;
                candleTimesRef.current = data.map((candle) => candle.time);
                candleDataRef.current = data.map((candle) => ({ time: candle.time, close: candle.close }));
                candleStepRef.current = candleStep;
                chart.subscribeClick((param) => {
                    if (!measuringRef.current && onInspectConfluenceOverlay) {
                        for (const [series, overlay] of confluenceSeriesMap) {
                            if (param.seriesData.has(series)) {
                                onInspectConfluenceOverlay(overlay.timeframe);
                                return;
                            }
                        }
                    }
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
                            pointX: param.point.x,
                            pointY: param.point.y,
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
                    const measurementText = `₹${startPrice.toFixed(2)} → ₹${price.toFixed(2)} · ${change >= 0 ? "+" : ""}${change.toFixed(2)} · ${percent >= 0 ? "+" : ""}${percent.toFixed(2)}%`;
                    measurementSelectionRef.current = {
                        from,
                        to,
                        lower,
                        upper,
                        text: measurementText,
                    };
                    setMeasurementLabel({
                        left: (measureStartRef.current.pointX + param.point.x) / 2,
                        top: (measureStartRef.current.pointY + param.point.y) / 2,
                        text: measurementText,
                    });
                    updateMeasurementLabel();
                    window.requestAnimationFrame(updateMeasurementLabel);
                    setMeasurement("Measured range is shown inside the chart.");
                    measureStartRef.current = null;
                });
                chart.timeScale().subscribeVisibleLogicalRangeChange(updateMeasurementLabel);
                chart.timeScale().subscribeVisibleLogicalRangeChange(updateZoneBorders);
                chart.timeScale().subscribeVisibleLogicalRangeChange(() => updateRectangleOverlays());

                const renderedZones: DeveloperChartZone[] = developerMode
                    ? developerZones
                    : zones.map((displayZone, zoneIndex) => ({
                        zoneId: zoneSequenceLabel(zones, zoneIndex),
                        zoneType: displayZone.zone_type === "DEMAND" ? "DEMAND" : "SUPPLY",
                        proximalPrice: displayZone.proximal_price,
                        distalPrice: displayZone.distal_price,
                        baseIndex: displayZone.base_index,
                        baseStartDate: displayZone.base_date,
                        pattern: displayZone.pattern_type ?? undefined,
                        zoneStatus: "Accepted",
                        zoneScore: displayZone.zone_score,
                        reacting: displayZone.status === "REACTING",
                        lifecycleStatus: displayZone.lifecycle_status ?? null,
                        selected: !selectedZoneId || zoneSequenceLabel(zones, zoneIndex) === selectedZoneId,
                    }));
                renderedZones.forEach((displayZone) => {
                if (displayZone.proximalPrice !== null && displayZone.distalPrice !== null) {
                    const demand = displayZone.zoneType === "DEMAND";
                    const inactiveLifecycle = isInactiveLifecycle(displayZone.lifecycleStatus);
                    const zoneColor = inactiveLifecycle ? "#94a3b8" : demand ? "#2f8f67" : "#c45f69";
                    const zoneLabel = displayZone.zoneId;
                    const lifecycleLabel = inactiveLifecycle
                        ? ` ${(displayZone.lifecycleStatus ?? "TESTED").replaceAll("_", " ")}`
                        : displayZone.reacting ? " REACTING" : "";
                    const selected = Boolean(displayZone.selected);
                    const rejected = displayZone.zoneStatus === "Rejected";
                    const invalidated = displayZone.zoneStatus === "Invalidated";
                    const opacity = invalidated ? .04 : rejected ? .08 : inactiveLifecycle ? (selected ? .10 : .06) : selected ? .18 : .12;
                    const borderStyle = invalidated ? LineStyle.Dotted : rejected ? LineStyle.Dashed : LineStyle.Solid;
                    const zone = chart.addSeries(BaselineSeries, {
                        baseValue: { type: "price", price: displayZone.distalPrice },
                        topLineColor: "rgba(0,0,0,0)",
                        topFillColor1: inactiveLifecycle ? `rgba(148,163,184,${opacity})` : demand ? `rgba(47,143,103,${opacity})` : `rgba(196,95,105,${opacity})`,
                        topFillColor2: inactiveLifecycle ? `rgba(148,163,184,${opacity})` : demand ? `rgba(47,143,103,${opacity})` : `rgba(196,95,105,${opacity})`,
                        bottomLineColor: "rgba(0,0,0,0)",
                        bottomFillColor1: inactiveLifecycle ? `rgba(148,163,184,${opacity})` : demand ? `rgba(47,143,103,${opacity})` : `rgba(196,95,105,${opacity})`,
                        bottomFillColor2: inactiveLifecycle ? `rgba(148,163,184,${opacity})` : demand ? `rgba(47,143,103,${opacity})` : `rgba(196,95,105,${opacity})`,
                        lineWidth: 1,
                        lineStyle: borderStyle,
                        priceLineVisible: false,
                        lastValueVisible: false,
                    });
                    const requestedBaseTime = displayZone.baseStartDate
                        ? new Date(displayZone.baseStartDate).getTime() / 1000
                        : Number.NaN;
                    const datedBaseIndex = Number.isFinite(requestedBaseTime)
                        ? data.reduce((closest, candle, index) =>
                            Math.abs(Number(candle.time) - requestedBaseTime)
                                < Math.abs(Number(data[closest].time) - requestedBaseTime)
                                ? index
                                : closest, 0)
                        : -1;
                    const baseIndex = Math.min(
                        datedBaseIndex >= 0 ? datedBaseIndex : displayZone.baseIndex ?? data.length - 45,
                        data.length - 1,
                    );
                    const start = Math.max(0, baseIndex - 3);
                    const zoneData = data.slice(start).map((candle) => ({
                        time: candle.time,
                        value: displayZone.proximalPrice,
                    }));
                    const latestTime = Number(data[data.length - 1].time);
                    for (let point = 1; point <= 3; point += 1) {
                        zoneData.push({
                            time: (latestTime + candleStep * point) as UTCTimestamp,
                            value: displayZone.proximalPrice,
                        });
                    }
                    zone.setData(zoneData);
                    baseZoneAreaSeriesRef.current.push(zone);
                    const proximalBoundary = chart.addSeries(LineSeries, {
                        color: zoneColor,
                        lineWidth: 1,
                        lineStyle: borderStyle,
                        lineVisible: false,
                        pointMarkersVisible: false,
                        crosshairMarkerVisible: false,
                        priceLineVisible: false,
                        lastValueVisible: true,
                        title: invalidated ? `${zoneLabel} Invalidated` : rejected ? `${zoneLabel} Rejected Candidate` : `${zoneLabel}${lifecycleLabel} PROXIMAL`,
                    });
                    const distalBoundary = chart.addSeries(LineSeries, {
                        color: zoneColor,
                        lineWidth: 1,
                        lineStyle: invalidated ? LineStyle.Dotted : LineStyle.Dashed,
                        lineVisible: false,
                        pointMarkersVisible: false,
                        crosshairMarkerVisible: false,
                        priceLineVisible: false,
                        lastValueVisible: true,
                        title: `${zoneLabel} DISTAL`,
                    });
                    const labelTime = zoneData[zoneData.length - 1].time;
                    zoneBorderDefinitionsRef.current.push({
                        id: zoneLabel,
                        from: zoneData[0].time,
                        to: labelTime,
                        proximal: displayZone.proximalPrice,
                        distal: displayZone.distalPrice,
                        color: zoneColor,
                        status: displayZone.zoneStatus,
                    });
                    // A single point keeps the price-axis label without drawing
                    // another horizontal guide line across the zone rectangle.
                    proximalBoundary.setData([{ time: labelTime, value: displayZone.proximalPrice }]);
                    distalBoundary.setData([{ time: labelTime, value: displayZone.distalPrice }]);
                    baseZoneBoundarySeriesRef.current.push(proximalBoundary, distalBoundary);
                    zoneSeriesMap.set(zoneLabel, { area: zone, proximal: proximalBoundary, distal: distalBoundary, demand, status: displayZone.zoneStatus, inactiveLifecycle });
                }
                });

                const activeIndex = Math.max(0, Math.min(result.base_index ?? data.length - 1, data.length - 1));
                chart.timeScale().setVisibleLogicalRange({
                    from: Math.max(0, activeIndex - 6),
                    to: data.length + 3,
                });
                updateZoneBorders();
                updateRectangleOverlays();
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
            zoneSeriesMap.clear();
            zoneBorderDefinitionsRef.current = [];
            setZoneBorders([]);
            confluenceSeriesRef.current = [];
            confluenceBoundarySeriesRef.current = [];
            confluenceSeriesMap.clear();
            measurementAreaSeriesRef.current = null;
            measurementBoundarySeriesRef.current = [];
            indicatorSeriesRef.current = [];
            measurementSelectionRef.current = null;
            candleTimesRef.current = [];
            candleDataRef.current = [];
            chart = null as never;
        };
        // Zone selection is handled separately so changing the active zone
        // never destroys the chart or resets user drawings and indicators.
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [developerMode, developerZones, height, onInspectConfluenceOverlay, result.symbol, result.timeframe, updateMeasurementLabel, updateRectangleOverlays, updateZoneBorders]);

    useEffect(() => {
        rectangleContextRef.current = { symbol: result.symbol, timeframe: result.timeframe };
        rectangleDraftStartRef.current = null;
        const frame = window.requestAnimationFrame(() => {
            setSelectedRectangleId(null);
            setRectangleDraft(null);
            updateRectangleOverlays();
        });
        return () => window.cancelAnimationFrame(frame);
    }, [result.symbol, result.timeframe, updateRectangleOverlays]);

    useEffect(() => {
        const onKeyDown = (event: KeyboardEvent) => {
            if (event.key === "Escape" && rectangleDraftStartRef.current) {
                rectangleDraftStartRef.current = null;
                setRectangleDraft(null);
                updateRectangleOverlays();
                return;
            }
            if ((event.key === "Delete" || event.key === "Backspace") && selectedRectangleId) {
                const target = event.target as HTMLElement | null;
                if (target?.matches("input, textarea, [contenteditable='true']")) return;
                rectanglesRef.current = removeUserChartRectangle(rectanglesRef.current, selectedRectangleId);
                setSelectedRectangleId(null);
                updateRectangleOverlays();
            }
        };
        window.addEventListener("keydown", onKeyDown);
        return () => window.removeEventListener("keydown", onKeyDown);
    }, [selectedRectangleId, updateRectangleOverlays]);

    useEffect(() => {
        if (!chartReadyVersion || !chartRef.current) return;
        const activeZone = zones.find((_, index) =>
            !selectedZoneId || zoneSequenceLabel(zones, index) === selectedZoneId
        ) ?? result;
        const activeIndex = Math.max(0, Math.min(activeZone.base_index ?? candleTimesRef.current.length - 1, candleTimesRef.current.length - 1));
        chartRef.current.timeScale().setVisibleLogicalRange({
            from: Math.max(0, activeIndex - 6),
            to: candleTimesRef.current.length + 3,
        });
        zoneSeriesMapRef.current.forEach((series, zoneId) => {
            const selected = !selectedZoneId || zoneId === selectedZoneId;
            const rejected = series.status === "Rejected";
            const invalidated = series.status === "Invalidated";
            const opacity = invalidated ? .04 : rejected ? .08 : series.inactiveLifecycle ? (selected ? .10 : .06) : selected ? .18 : .12;
            const fill = series.inactiveLifecycle
                ? `rgba(148,163,184,${opacity})`
                : series.demand ? `rgba(47,143,103,${opacity})` : `rgba(196,95,105,${opacity})`;
            series.area.applyOptions({
                topFillColor1: fill,
                topFillColor2: fill,
                bottomFillColor1: fill,
                bottomFillColor2: fill,
                lineWidth: 1,
            });
            series.proximal.applyOptions({ lineWidth: 1 });
            series.distal.applyOptions({ lineWidth: 1 });
        });
    }, [chartReadyVersion, result, selectedZoneId, zones]);

    useEffect(() => {
        const chart = chartRef.current;
        const candles = candleSeriesRef.current;
        const times = candleTimesRef.current;
        if (!chart || !candles || !times.length) return;

        confluenceBoundarySeriesRef.current.forEach((series) => chart.removeSeries(series));
        confluenceSeriesRef.current.forEach((series) => chart.removeSeries(series));
        confluenceBoundarySeriesRef.current = [];
        confluenceSeriesRef.current = [];
        confluenceSeriesMapRef.current.clear();

        const styles = [LineStyle.Dashed, LineStyle.Dotted, LineStyle.LargeDashed, LineStyle.SparseDotted];
        confluenceOverlays.forEach((overlay, index) => {
            const demand = overlay.zoneType === "DEMAND";
            const style = overlayStyles[overlay.timeframe] ?? { color: demand ? "#1d8cff" : "#ff2f68", width: 2 as const };
            const color = style.color;
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
                lineWidth: style.width,
                lineStyle: overlay.timeframe === "1M" ? LineStyle.Solid : styles[index % styles.length],
                priceLineVisible: false,
                lastValueVisible: false,
                autoscaleInfoProvider: () => null,
            });
            const startIndex = Math.max(0, times.length - Math.max(36, Math.floor(times.length * .3)));
            const overlayData = times.slice(startIndex).map((time) => ({
                time,
                value: upper,
            }));
            series.setData(overlayData);
            confluenceSeriesRef.current.push(series);
            confluenceSeriesMapRef.current.set(series, overlay);
            const upperBoundary = chart.addSeries(LineSeries, {
                color,
                lineWidth: style.width,
                lineStyle: overlay.timeframe === "1M" ? LineStyle.Solid : styles[index % styles.length],
                priceLineVisible: false,
                lastValueVisible: true,
                title: `${overlay.timeframe} HTF`,
                autoscaleInfoProvider: () => null,
            });
            const lowerBoundary = chart.addSeries(LineSeries, {
                color,
                lineWidth: style.width,
                lineStyle: overlay.timeframe === "1M" ? LineStyle.Solid : styles[index % styles.length],
                priceLineVisible: false,
                lastValueVisible: false,
                autoscaleInfoProvider: () => null,
            });
            upperBoundary.setData(overlayData);
            lowerBoundary.setData(overlayData.map((point) => ({ ...point, value: lower })));
            confluenceBoundarySeriesRef.current.push(upperBoundary, lowerBoundary);
        });
    }, [chartReadyVersion, confluenceOverlays, htfLocationVisible]);

    useEffect(() => {
        const chart = chartRef.current;
        if (!chart) return;
        const color = gridVisible ? "rgba(148,163,184,.16)" : "rgba(148,163,184,0)";
        chart.applyOptions({ grid: { vertLines: { color }, horzLines: { color } } });
    }, [chartReadyVersion, gridVisible]);

    useEffect(() => {
        confluenceSeriesRef.current.forEach((series) => series.applyOptions({ visible: htfLocationVisible }));
        confluenceBoundarySeriesRef.current.forEach((series) => series.applyOptions({ visible: htfLocationVisible }));
    }, [chartReadyVersion, confluenceOverlays, htfLocationVisible]);

    useEffect(() => {
        const chart = chartRef.current;
        const data = candleDataRef.current;
        if (!chart || !data.length) return;
        indicatorSeriesRef.current.forEach((series) => chart.removeSeries(series));
        indicatorSeriesRef.current = [];

        indicatorOptions
            .filter((option) => selectedIndicators.includes(option.id))
            .forEach((option) => {
                const series = chart.addSeries(LineSeries, {
                    color: option.color,
                    lineWidth: 2,
                    lineStyle: option.kind === "EMA" ? LineStyle.Solid : LineStyle.Dashed,
                    priceLineVisible: false,
                    lastValueVisible: true,
                    title: option.label,
                });
                if (option.kind === "EMA") {
                    const multiplier = 2 / (option.period + 1);
                    let average = data[0].close;
                    series.setData(data.map((point) => {
                        average = point.close * multiplier + average * (1 - multiplier);
                        return { time: point.time, value: average };
                    }));
                } else {
                    series.setData(data.slice(option.period - 1).map((point, index) => {
                        const sourceIndex = index + option.period - 1;
                        const window = data.slice(sourceIndex - option.period + 1, sourceIndex + 1);
                        return {
                            time: point.time,
                            value: window.reduce((sum, item) => sum + item.close, 0) / option.period,
                        };
                    }));
                }
                indicatorSeriesRef.current.push(series);
            });
    }, [chartReadyVersion, selectedIndicators]);

    function changeIndicators(event: SelectChangeEvent<string[]>) {
        const value = event.target.value;
        const next = typeof value === "string" ? value.split(",") : value;
        setSelectedIndicators(next);
        localStorage.setItem(indicatorPreferenceKey, JSON.stringify(next));
    }

    function toggleEmas() {
        const defaults = ["EMA_20", "EMA_50", "EMA_200"];
        const enabled = defaults.some((id) => selectedIndicators.includes(id));
        const next = enabled
            ? selectedIndicators.filter((id) => !id.startsWith("EMA_"))
            : [...selectedIndicators.filter((id) => !id.startsWith("EMA_")), ...defaults];
        setSelectedIndicators(next);
        localStorage.setItem(indicatorPreferenceKey, JSON.stringify(next));
    }

    function toggleZones() {
        const next = !zonesVisible;
        setZonesVisible(next);
        baseZoneAreaSeriesRef.current.forEach((series) => series.applyOptions({ visible: next }));
        baseZoneBoundarySeriesRef.current.forEach((series) => series.applyOptions({ visible: next }));
    }

    function toggleMeasure() {
        const next = !measuring;
        setMeasuring(next);
        measuringRef.current = next;
        measureStartRef.current = null;
        setMeasurement(next ? "Select two chart points to measure price change." : "Measurement tool is off.");
    }

    function toggleRectangleMode() {
        const next = !rectangleMode;
        setRectangleMode(next);
        rectangleModeRef.current = next;
        rectangleDraftStartRef.current = null;
        setRectangleDraft(null);
        setSelectedRectangleId(null);
        if (next && measuringRef.current) {
            setMeasuring(false);
            measuringRef.current = false;
            measureStartRef.current = null;
            setMeasurement("Measurement tool is off.");
        }
        chartRef.current?.applyOptions({ handleScroll: { pressedMouseMove: !next } });
    }

    function clearDrawings() {
        rectanglesRef.current = clearUserChartRectangles(rectanglesRef.current, result.symbol, result.timeframe);
        rectangleDraftStartRef.current = null;
        setRectangleDraft(null);
        setSelectedRectangleId(null);
        updateRectangleOverlays();
    }

    function chartPointFromPointer(event: React.PointerEvent<HTMLDivElement>): RectangleDraftPoint | null {
        const chart = chartRef.current;
        const candles = candleSeriesRef.current;
        const container = containerRef.current;
        if (!chart || !candles || !container) return null;
        const bounds = container.getBoundingClientRect();
        const x = event.clientX - bounds.left;
        const y = event.clientY - bounds.top;
        const time = chart.timeScale().coordinateToTime(x);
        const price = candles.coordinateToPrice(y);
        if (time === null || price === null || typeof time !== "number") return null;
        return { time: Number(time) as UTCTimestamp, price };
    }

    function startRectangle(event: React.PointerEvent<HTMLDivElement>) {
        if (!rectangleModeRef.current || event.button !== 0) return;
        const point = chartPointFromPointer(event);
        if (!point) return;
        event.currentTarget.setPointerCapture(event.pointerId);
        rectangleDraftStartRef.current = point;
        setSelectedRectangleId(null);
        event.preventDefault();
    }

    function moveRectangle(event: React.PointerEvent<HTMLDivElement>) {
        const start = rectangleDraftStartRef.current;
        if (!rectangleModeRef.current || !start) return;
        const point = chartPointFromPointer(event);
        if (!point) return;
        const draft = createUserChartRectangle("rectangle-draft", result.symbol, result.timeframe, start, point);
        setRectangleDraft(draft);
        updateRectangleOverlays(draft);
        event.preventDefault();
    }

    function finishRectangle(event: React.PointerEvent<HTMLDivElement>) {
        const start = rectangleDraftStartRef.current;
        if (!rectangleModeRef.current || !start) return;
        const point = chartPointFromPointer(event);
        rectangleDraftStartRef.current = null;
        if (point && (point.time !== start.time || point.price !== start.price)) {
            rectangleSequenceRef.current += 1;
            const rectangle = createUserChartRectangle(
                `rectangle-${rectangleSequenceRef.current}`,
                result.symbol,
                result.timeframe,
                start,
                point,
            );
            rectanglesRef.current = [...rectanglesRef.current, rectangle];
            setSelectedRectangleId(rectangle.id);
        }
        setRectangleDraft(null);
        setRectangleMode(false);
        rectangleModeRef.current = false;
        chartRef.current?.applyOptions({ handleScroll: { pressedMouseMove: true } });
        window.requestAnimationFrame(() => updateRectangleOverlays());
        event.preventDefault();
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
        measurementSelectionRef.current = null;
        setMeasurementLabel(null);
        measureStartRef.current = null;
        setMeasurement(measuring ? "Select two chart points to highlight a range." : "Measurement tool is off.");
    }

    function resetChart() {
        clearMeasurement();
        setMeasuring(false);
        measuringRef.current = false;
        setCrosshairVisible(true);
        crosshairVisibleRef.current = true;
        chartRef.current?.applyOptions({
            crosshair: { mode: CrosshairMode.Normal },
        });
        setZonesVisible(true);
        baseZoneAreaSeriesRef.current.forEach((series) => series.applyOptions({ visible: true }));
        baseZoneBoundarySeriesRef.current.forEach((series) => series.applyOptions({ visible: true }));
        setHtfLocationVisible(true);
        setGridVisible(false);
        setDetailsVisible(false);
        setSelectedIndicators([]);
        localStorage.removeItem(indicatorPreferenceKey);
        chartRef.current?.timeScale().fitContent();
        chartRef.current?.timeScale().applyOptions({ rightOffset: 3 });
        setMeasurement("Measurement tool is off.");
        onResetChart?.();
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
        <Box sx={{
            bgcolor: "#ffffff",
            color: "#172033",
            border: "1px solid #e2e8f0",
            borderRadius: 1.5,
            overflow: "hidden",
            "& .MuiTypography-colorTextSecondary": { color: "#64748b" },
            "& .MuiInputLabel-root": { color: "#64748b" },
            "& .MuiSelect-select": { color: "#172033" },
            "& .MuiOutlinedInput-notchedOutline": { borderColor: "#d8e0ea" },
            "& .MuiSvgIcon-root": { color: "inherit" },
        }}>
            <Stack direction="row" sx={{ px: 2, py: 1.2, alignItems: "center", gap: 1, borderBottom: "1px solid", borderColor: "divider" }}>
                <Typography sx={{ fontWeight: 850 }}>{result.symbol}</Typography>
                <Typography color={result.zone_type === "DEMAND" ? "#60a5fa" : "#ff6b8a"} sx={{ fontSize: ".68rem", fontWeight: 850 }}>
                    {result.zone_type} · {patternLabels[result.pattern_type ?? ""] ?? result.pattern_type ?? "Pattern pending"}
                </Typography>
                <Stack direction="row" sx={{ ml: "auto", alignItems: "center", gap: 1.25 }}>
                    {onToggleAnalysisPanel && (
                        <Tooltip title={analysisPanelOpen ? "Hide analysis panel" : "Show analysis panel"}>
                            <ButtonBase
                                aria-label={analysisPanelOpen ? "Hide analysis panel" : "Show analysis panel"}
                                aria-pressed={analysisPanelOpen}
                                onClick={onToggleAnalysisPanel}
                                sx={{
                                    minHeight: 40,
                                    px: 1.5,
                                    gap: 1,
                                    borderRadius: "999px",
                                    border: "1px solid",
                                    borderColor: analysisPanelOpen ? "#B8A6FF" : "#D8DCE8",
                                    bgcolor: analysisPanelOpen ? "#F4F1FF" : "#FFFFFF",
                                    color: analysisPanelOpen ? "#4F46E5" : "#344054",
                                    transition: "background-color 200ms ease, border-color 200ms ease, box-shadow 200ms ease",
                                    "&:hover": { boxShadow: "0 3px 10px rgba(15,23,42,.08)" },
                                    "&:focus-visible": { outline: "2px solid #5B5CEB", outlineOffset: 2 },
                                }}
                            >
                                <ViewSidebarOutlinedIcon sx={{ fontSize: 19, color: analysisPanelOpen ? "#4F46E5" : "#667085" }} />
                                <Typography sx={{ fontSize: ".78rem", fontWeight: 600, whiteSpace: "nowrap" }}>
                                    {analysisPanelOpen ? "Hide Analysis" : "Show Analysis"}
                                </Typography>
                                <Switch
                                    checked={analysisPanelOpen}
                                    size="small"
                                    tabIndex={-1}
                                    disableRipple
                                    sx={{
                                        pointerEvents: "none",
                                        ml: .25,
                                        "& .MuiSwitch-switchBase.Mui-checked": { color: "#5B5CEB" },
                                        "& .MuiSwitch-switchBase.Mui-checked + .MuiSwitch-track": { bgcolor: "#5B5CEB", opacity: 1 },
                                        "& .MuiSwitch-track": { bgcolor: "#D0D5DD", opacity: 1 },
                                    }}
                                />
                            </ButtonBase>
                        </Tooltip>
                    )}
                    <Typography color="text.secondary" sx={{ fontSize: ".68rem", whiteSpace: "nowrap" }}>
                    Zone {result.distal_price?.toLocaleString("en-IN")}–{result.proximal_price?.toLocaleString("en-IN")} · {result.timeframe ?? "1D"}
                    </Typography>
                </Stack>
            </Stack>
            {showTools && <Stack direction="row" spacing={1} sx={{ px: 1.5, py: 1, alignItems: "center", flexWrap: "wrap", rowGap: 1, borderBottom: "1px solid", borderColor: "divider" }}>
                <Button size="small" variant="outlined" onClick={() => chartRef.current?.timeScale().fitContent()}>Fit chart</Button>
                <Button size="small" variant="outlined" color="warning" onClick={resetChart}>Reset chart</Button>
                <Button size="small" variant={measuring ? "contained" : "outlined"} onClick={toggleMeasure}>Measure range</Button>
                <Button size="small" variant={rectangleMode ? "contained" : "outlined"} onClick={toggleRectangleMode}>Rectangle</Button>
                <Button size="small" variant="outlined" onClick={clearMeasurement}>Clear measurement</Button>
                <Button size="small" variant="outlined" onClick={clearDrawings} disabled={!rectangleOverlays.length}>Clear drawings</Button>
                <Button size="small" variant={crosshairVisible ? "contained" : "outlined"} onClick={toggleCrosshair}>Crosshair {crosshairVisible ? "On" : "Off"}</Button>
                <Button size="small" variant={zonesVisible ? "contained" : "outlined"} onClick={toggleZones}>Zones {zonesVisible ? "On" : "Off"}</Button>
                <Button size="small" variant={htfLocationVisible ? "contained" : "outlined"} disabled={!availableConfluenceOverlays.length} onClick={() => setHtfLocationVisible((value) => !value)}>HTF Location {htfLocationVisible ? "On" : "Off"}</Button>
                <Tooltip title="No validated target is available in this chart payload"><span><Button size="small" variant="outlined" disabled>Targets</Button></span></Tooltip>
                <Button size="small" variant={selectedIndicators.some((id) => id.startsWith("EMA_")) ? "contained" : "outlined"} onClick={toggleEmas}>EMAs</Button>
                <Button size="small" variant={gridVisible ? "contained" : "outlined"} onClick={() => setGridVisible((value) => !value)}>Grid</Button>
                <Button size="small" variant={detailsVisible ? "contained" : "outlined"} onClick={() => setDetailsVisible((value) => !value)}>Details</Button>
                <FormControl size="small" sx={{ minWidth: 150 }}>
                    <InputLabel id="chart-indicators-label">Indicators</InputLabel>
                    <Select<string[]>
                        labelId="chart-indicators-label"
                        multiple
                        value={selectedIndicators}
                        label="Indicators"
                        onChange={changeIndicators}
                        renderValue={(selected) => selected.length ? `${selected.length} selected` : "None"}
                    >
                        {indicatorOptions.map((option) => (
                            <MenuItem key={option.id} value={option.id}>
                                <Checkbox checked={selectedIndicators.includes(option.id)} />
                                <Box sx={{ width: 10, height: 10, borderRadius: "50%", bgcolor: option.color, mr: 1 }} />
                                <ListItemText primary={option.label} secondary={option.kind === "EMA" ? "Follows recent prices faster" : "Smooth average price"} />
                            </MenuItem>
                        ))}
                    </Select>
                </FormControl>
                <Chip size="small" label="Hold left mouse button and drag to pan" />
                <Chip size="small" label="Wheel to zoom" />
                <Typography variant="caption" color={measuring ? "primary.main" : "text.secondary"} sx={{ ml: "auto" }}>{measurement}</Typography>
            </Stack>}
            {higherTimeframeButtons.length > 0 && onToggleConfluenceOverlay && (
                <Stack direction="row" sx={{ px: 1.5, py: .75, alignItems: "center", gap: .75, borderBottom: "1px solid", borderColor: "divider", flexWrap: "wrap" }}>
                    <Typography variant="caption" sx={{ fontWeight: 700 }}>Higher timeframes:</Typography>
                    {higherTimeframeButtons.map((timeframe) => {
                        const overlay = availableConfluenceOverlays.find((item) => item.timeframe === timeframe.timeframe);
                        if (!overlay) {
                            return <Button key={timeframe.timeframe} size="small" variant="outlined" disabled>{timeframe.name}</Button>;
                        }
                        const selected = confluenceOverlays.some((active) => active.timeframe === overlay.timeframe);
                        return <Button
                            key={overlay.timeframe}
                            size="small"
                            variant={selected ? "contained" : "outlined"}
                            onClick={() => onToggleConfluenceOverlay(overlay)}
                            sx={{
                                color: selected ? "#ffffff" : overlayStyles[overlay.timeframe]?.color,
                                bgcolor: selected ? overlayStyles[overlay.timeframe]?.color : undefined,
                                borderColor: overlayStyles[overlay.timeframe]?.color,
                                "&:hover": { bgcolor: selected ? overlayStyles[overlay.timeframe]?.color : undefined },
                            }}
                        >
                            {timeframe.name}
                        </Button>;
                    })}
                    <Typography variant="caption" color="text.secondary">
                        Select a timeframe to show its validated zone.
                    </Typography>
                </Stack>
            )}
            <Box sx={{ px: 1.5, py: .8, bgcolor: "#f8fafc", borderBottom: "1px solid", borderColor: "divider" }}>
                <Stack direction="row" sx={{ gap: 2.5, flexWrap: "wrap", alignItems: "center" }}>
                    <Typography variant="caption"><strong>LOCATION</strong> {selectedLocation ? `${selectedLocation.timeframeName} ${selectedLocation.zoneType}` : "No HTF selected"}</Typography>
                    <Typography variant="caption"><strong>TREND</strong> Unavailable</Typography>
                    <Typography variant="caption"><strong>EXECUTION</strong> {result.timeframe} {result.zone_type} · {patternLabels[result.pattern_type ?? ""] ?? result.pattern_type ?? "Pattern unavailable"}</Typography>
                    <Typography variant="caption" sx={{ fontWeight: 700 }}>
                        <strong>ALIGNMENT</strong>{" "}
                        {!selectedLocation
                            ? "Select a higher timeframe to view its validated zone."
                            : selectedLocation.relationship === "NO_OVERLAP"
                                ? "No HTF zone overlap"
                                : selectedLocation.direction === "OPPOSING"
                                    ? `Opposing: ${result.timeframe} ${result.zone_type.toLowerCase()} lies in ${selectedLocation.timeframeName} ${selectedLocation.zoneType.toLowerCase()}`
                                    : selectedLocation.relationship === "FULL_OVERLAP"
                                        ? `Fully inside ${selectedLocation.timeframeName} ${selectedLocation.zoneType.toLowerCase()}`
                                        : `${selectedLocation.relationship === "PARTIAL_OVERLAP" ? "Partial overlap" : "Touching"} with ${selectedLocation.timeframeName} ${selectedLocation.zoneType.toLowerCase()}`}
                    </Typography>
                </Stack>
                {detailsVisible && (
                    <Typography variant="caption" color="text.secondary" sx={{ display: "block", mt: .35 }}>
                        {patternLabels[result.pattern_type ?? ""] ?? result.pattern_type ?? "Pattern unavailable"} · {result.zone_type} · proximal ₹{result.proximal_price.toLocaleString("en-IN")} · distal ₹{result.distal_price.toLocaleString("en-IN")} · {result.timeframe}
                    </Typography>
                )}
            </Box>
            {inspectedOverlay && (
                <Box sx={{ px: 1.5, py: 1, bgcolor: "#f8fafc", borderBottom: "1px solid", borderColor: overlayStyles[inspectedOverlay.timeframe]?.color ?? "divider" }}>
                    <Typography sx={{ fontWeight: 850 }}>
                        {inspectedOverlay.timeframeName} · {inspectedOverlay.zoneType === "DEMAND" ? "Demand" : "Supply"} · ₹{Math.min(inspectedOverlay.proximalPrice, inspectedOverlay.distalPrice).toLocaleString("en-IN")}–₹{Math.max(inspectedOverlay.proximalPrice, inspectedOverlay.distalPrice).toLocaleString("en-IN")}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                        Quality {inspectedOverlay.quality.toFixed(0)} · Overlap {inspectedOverlay.overlapPercent.toFixed(1)}% · Distance {inspectedOverlay.distancePercent.toFixed(2)}% · {inspectedOverlay.freshness} · {inspectedOverlay.retests} retests
                    </Typography>
                </Box>
            )}
            {loading && <Box sx={{ height, display: "grid", placeItems: "center" }}><CircularProgress size={28} /></Box>}
            {error && <Alert severity="warning">{error}</Alert>}
            <Box sx={{ position: "relative" }}>
                <Box
                    ref={containerRef}
                    onMouseLeave={() => developerMode && setDeveloperTooltip(null)}
                    onMouseMove={(event) => {
                        if (!developerMode || !candleSeriesRef.current || !containerRef.current) return;
                        const bounds = containerRef.current.getBoundingClientRect();
                        const price = candleSeriesRef.current.coordinateToPrice(event.clientY - bounds.top);
                        if (price === null) return;
                        const hovered = developerZones.find((zone) => {
                            const lower = Math.min(zone.proximalPrice, zone.distalPrice);
                            const upper = Math.max(zone.proximalPrice, zone.distalPrice);
                            return price >= lower && price <= upper;
                        });
                        setDeveloperTooltip(hovered ? {
                            left: event.clientX - bounds.left + 12,
                            top: event.clientY - bounds.top + 12,
                            zone: hovered,
                        } : null);
                    }}
                    sx={{ height: loading || error ? 0 : height }}
                />
                <Box
                    aria-label="Manual chart drawing layer"
                    onPointerDown={startRectangle}
                    onPointerMove={moveRectangle}
                    onPointerUp={finishRectangle}
                    sx={{
                        position: "absolute",
                        inset: 0,
                        zIndex: 24,
                        pointerEvents: rectangleMode ? "auto" : "none",
                        cursor: rectangleMode ? "crosshair" : "default",
                        touchAction: rectangleMode ? "none" : "auto",
                    }}
                />
                {rectangleOverlays.map((rectangle) => {
                    const selected = rectangle.id === selectedRectangleId;
                    return (
                        <Box
                            key={rectangle.id}
                            role="button"
                            tabIndex={rectangle.id === "rectangle-draft" ? -1 : 0}
                            aria-label={`Manual rectangle from ₹${formatAnnotationPrice(rectangle.lowerPrice)} to ₹${formatAnnotationPrice(rectangle.upperPrice)}`}
                            onClick={(event) => {
                                event.stopPropagation();
                                if (rectangle.id !== "rectangle-draft") setSelectedRectangleId(rectangle.id);
                            }}
                            onKeyDown={(event) => {
                                if ((event.key === "Delete" || event.key === "Backspace") && rectangle.id !== "rectangle-draft") {
                                    rectanglesRef.current = removeUserChartRectangle(rectanglesRef.current, rectangle.id);
                                    setSelectedRectangleId(null);
                                    updateRectangleOverlays();
                                }
                            }}
                            sx={{
                                position: "absolute",
                                left: rectangle.left,
                                top: rectangle.top,
                                width: rectangle.width,
                                height: rectangle.height,
                                zIndex: 23,
                                boxSizing: "border-box",
                                bgcolor: "rgba(79,70,229,.10)",
                                border: `${selected ? 2 : 1}px solid ${selected ? "#4f46e5" : "#7c83a8"}`,
                                pointerEvents: rectangleMode || rectangle.id === "rectangle-draft" ? "none" : "auto",
                                cursor: "pointer",
                                outline: "none",
                                "&:focus-visible": { borderColor: "#4f46e5", boxShadow: "0 0 0 2px rgba(79,70,229,.18)" },
                            }}
                        >
                            <Box sx={{ position: "absolute", right: -1, top: 0, transform: "translate(100%,-50%)", px: .65, py: .2, bgcolor: "#667085", color: "#fff", fontSize: ".68rem", fontWeight: 700, whiteSpace: "nowrap", borderRadius: "0 3px 3px 0" }}>
                                ₹{formatAnnotationPrice(rectangle.upperPrice)}
                            </Box>
                            <Box sx={{ position: "absolute", right: -1, bottom: 0, transform: "translate(100%,50%)", px: .65, py: .2, bgcolor: "#667085", color: "#fff", fontSize: ".68rem", fontWeight: 700, whiteSpace: "nowrap", borderRadius: "0 3px 3px 0" }}>
                                ₹{formatAnnotationPrice(rectangle.lowerPrice)}
                            </Box>
                        </Box>
                    );
                })}
                {zonesVisible && zoneBorders.map((zone) => (
                    <Box
                        key={zone.id}
                        aria-hidden="true"
                        sx={{
                            position: "absolute",
                            pointerEvents: "none",
                            boxSizing: "border-box",
                            left: zone.left,
                            top: zone.top,
                            width: zone.width,
                            height: zone.height,
                            borderWidth: "1px",
                            borderStyle: zone.status === "Invalidated" ? "dotted" : zone.status === "Rejected" ? "dashed" : "solid",
                            borderColor: zone.color,
                        }}
                    />
                ))}
                {developerMode && developerTooltip && (
                    <Box sx={{ position: "absolute", left: developerTooltip.left, top: developerTooltip.top, zIndex: 30, pointerEvents: "none", minWidth: 190, p: 1.25, bgcolor: "#ffffff", color: "#172033", border: "1px solid #d8e0ea", borderRadius: 1.5, boxShadow: "0 8px 24px rgba(15,23,42,.12)" }}>
                        <Typography sx={{ fontWeight: 800 }}>{developerTooltip.zone.zoneId}</Typography>
                        <Typography variant="caption" sx={{ display: "block" }}>Pattern: {developerTooltip.zone.pattern ?? "Unavailable"}</Typography>
                        <Typography variant="caption" sx={{ display: "block" }}>Status: {developerTooltip.zone.zoneStatus}</Typography>
                        <Typography variant="caption" sx={{ display: "block" }}>Score: {developerTooltip.zone.zoneScore ?? "Unavailable"}</Typography>
                        <Typography variant="caption" sx={{ display: "block" }}>Reason: {developerTooltip.zone.rejectionReasons?.join("; ") || "No reason supplied"}</Typography>
                        {developerTooltip.zone.ruleResults?.map((rule) => (
                            <Typography key={rule.key} variant="caption" color={rule.passed ? "#77e0a8" : "#ff899d"} sx={{ display: "block" }}>
                                {rule.passed ? "Pass" : "Fail"}: {rule.label} · {String(rule.actual ?? "Unavailable")} / {String(rule.required ?? "Unavailable")}
                            </Typography>
                        ))}
                    </Box>
                )}
                {measurementLabel && (
                    <Box
                        sx={{
                            position: "absolute",
                            left: measurementLabel.left,
                            top: measurementLabel.top,
                            transform: "translate(-50%, -50%)",
                            px: 1,
                            py: .5,
                            bgcolor: "rgba(255,255,255,.94)",
                            border: "1px solid #f5b942",
                            borderRadius: 1,
                            color: "#8a681d",
                            fontSize: ".72rem",
                            fontWeight: 850,
                            zIndex: 20,
                            pointerEvents: "none",
                            whiteSpace: "nowrap",
                        }}
                    >
                        {measurementLabel.text}
                    </Box>
                )}
            </Box>
            <Typography color="text.secondary" sx={{ px: 2, py: 1, fontSize: ".62rem" }}>
                Highlighted area is the detected research zone · drag to pan · wheel to zoom · delayed data may apply
            </Typography>
        </Box>
    );
}

export default ZoneDetailChart;
