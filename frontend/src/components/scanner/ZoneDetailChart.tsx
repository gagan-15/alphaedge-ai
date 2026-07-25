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

function ZoneDetailChart({ result }: { result: ZoneResearchResult }) {
    const containerRef = useRef<HTMLDivElement>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    useEffect(() => {
        const container = containerRef.current;
        if (!container) return;
        let cancelled = false;
        setLoading(true);
        setError("");

        let chart = createChart(container, {
            width: container.clientWidth,
            height: 360,
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

        const observer = new ResizeObserver(() => {
            chart.applyOptions({ width: container.clientWidth });
        });
        observer.observe(container);

        void getMarketCandles(result.symbol)
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

                if (result.proximal_price !== null && result.distal_price !== null) {
                    const demand = result.zone_type === "DEMAND";
                    const zone = chart.addSeries(BaselineSeries, {
                        baseValue: { type: "price", price: result.distal_price },
                        topLineColor: demand ? "#3478f6" : "#ff476f",
                        topFillColor1: demand ? "rgba(52,120,246,.24)" : "rgba(255,71,111,.24)",
                        topFillColor2: demand ? "rgba(52,120,246,.16)" : "rgba(255,71,111,.16)",
                        bottomLineColor: "transparent",
                        bottomFillColor1: "transparent",
                        bottomFillColor2: "transparent",
                        lineWidth: 1,
                        priceLineVisible: false,
                        lastValueVisible: false,
                    });
                    const start = Math.max(0, Math.min(result.base_index ?? data.length - 45, data.length - 1));
                    zone.setData(data.slice(start).map((candle) => ({
                        time: candle.time,
                        value: result.proximal_price as number,
                    })));
                }

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
            chart = null as never;
        };
    }, [result]);

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
            {loading && <Box sx={{ height: 360, display: "grid", placeItems: "center" }}><CircularProgress size={28} /></Box>}
            {error && <Alert severity="warning">{error}</Alert>}
            <Box ref={containerRef} sx={{ height: loading || error ? 0 : 360 }} />
            <Typography color="text.secondary" sx={{ px: 2, py: 1, fontSize: ".62rem" }}>
                Highlighted area is the detected research zone · drag to pan · wheel to zoom · delayed data may apply
            </Typography>
        </Box>
    );
}

export default ZoneDetailChart;
