import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Chip from "@mui/material/Chip";
import CircularProgress from "@mui/material/CircularProgress";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { useEffect, useMemo, useState } from "react";

import { getTimeframeConfluence } from "../../api/scannerApi";
import type {
    ConfluenceChartOverlay,
    ConfluenceTimeframe,
    TimeframeConfluenceResponse,
    ZoneResearchResult,
} from "../../types/scanner";

interface Props {
    result: ZoneResearchResult;
    activeTimeframes: string[];
    overlaysHidden: boolean;
    onToggleOverlay: (overlay: ConfluenceChartOverlay) => void;
    onToggleVisibility: () => void;
    onClearOverlays: () => void;
}

function overlayFrom(frame: ConfluenceTimeframe): ConfluenceChartOverlay | null {
    if (!frame.zone) return null;
    return {
        timeframe: frame.timeframe,
        timeframeName: frame.timeframe_name,
        zoneType: frame.zone.zone_type,
        proximalPrice: frame.zone.proximal_price,
        distalPrice: frame.zone.distal_price,
    };
}

function TimeframeConfluenceExplorer({
    result,
    activeTimeframes,
    overlaysHidden,
    onToggleOverlay,
    onToggleVisibility,
    onClearOverlays,
}: Props) {
    const [received, setReceived] = useState<{ key: string; data: TimeframeConfluenceResponse } | null>(null);
    const [failedKey, setFailedKey] = useState("");
    const [confirmedOnly, setConfirmedOnly] = useState(false);
    const requestKey = `${result.symbol}:${result.timeframe}:${result.zone_type}:${result.proximal_price}:${result.distal_price}:${result.base_date}`;
    const response = received?.key === requestKey ? received.data : null;
    const error = failedKey === requestKey ? "Higher-timeframe analysis is unavailable right now." : "";
    const loading = !response && !error;

    useEffect(() => {
        let active = true;
        void getTimeframeConfluence(result)
            .then((data) => {
                if (!active) return;
                const sameSelection = data.symbol === result.symbol
                    && data.execution_timeframe === result.timeframe
                    && data.execution_zone.zone_type === result.zone_type
                    && data.execution_zone.proximal_price === result.proximal_price
                    && data.execution_zone.distal_price === result.distal_price;
                if (sameSelection) setReceived({ key: requestKey, data });
            })
            .catch(() => {
                if (active) setFailedKey(requestKey);
            });
        return () => {
            active = false;
        };
    }, [requestKey, result]);

    const frames = useMemo(
        () => response?.higher_timeframes.filter(
            (frame) => !confirmedOnly || frame.status === "CONFIRMED",
        ) ?? [],
        [confirmedOnly, response],
    );
    const availableOverlays = useMemo(
        () => response?.higher_timeframes
            .map(overlayFrom)
            .filter((overlay): overlay is ConfluenceChartOverlay => overlay !== null) ?? [],
        [response],
    );

    function showAllTimeframesOnChart() {
        availableOverlays.forEach((overlay) => {
            if (!activeTimeframes.includes(overlay.timeframe)) {
                onToggleOverlay(overlay);
            }
        });
        if (overlaysHidden) onToggleVisibility();
    }

    if (loading) {
        return <Box sx={{ py: 2, display: "flex", justifyContent: "center" }}><CircularProgress size={22} /></Box>;
    }
    if (error) return <Typography color="warning.main">{error}</Typography>;
    if (!response) return null;

    return (
        <Stack spacing={1.25}>
            <Stack direction="row" sx={{ flexWrap: "wrap", gap: .75 }}>
                <Button
                    size="small"
                    variant="contained"
                    disabled={!availableOverlays.length}
                    onClick={showAllTimeframesOnChart}
                >
                    Show all timeframe zones on chart
                </Button>
                <Button size="small" variant={confirmedOnly ? "contained" : "outlined"} onClick={() => setConfirmedOnly(true)}>
                    Show only confirmed
                </Button>
                <Button size="small" variant={!confirmedOnly ? "contained" : "outlined"} onClick={() => setConfirmedOnly(false)}>
                    Show all cards
                </Button>
                <Button size="small" variant="outlined" onClick={onToggleVisibility}>
                    {overlaysHidden ? "Show overlays" : "Hide overlays"}
                </Button>
                <Button size="small" variant="outlined" disabled={!activeTimeframes.length} onClick={onClearOverlays}>
                    Clear overlays
                </Button>
            </Stack>

            <Box sx={{ p: 1.25, border: "1px solid", borderColor: "divider", borderRadius: 1.5 }}>
                <Stack direction="row" sx={{ alignItems: "center", justifyContent: "space-between", gap: 1 }}>
                    <Typography sx={{ fontWeight: 850 }}>Confluence score: {response.confluence_score.toFixed(0)} / 100</Typography>
                    <Chip size="small" label={response.strength} color={response.strength === "Strong" ? "success" : response.strength === "Moderate" ? "warning" : "default"} />
                </Stack>
                <Typography variant="body2" color="text.secondary" sx={{ mt: .5 }}>{response.summary}</Typography>
            </Box>

            {frames.map((frame) => {
                const overlay = overlayFrom(frame);
                const selected = activeTimeframes.includes(frame.timeframe) && !overlaysHidden;
                return (
                    <Box
                        key={frame.timeframe}
                        component={overlay ? "button" : "div"}
                        type={overlay ? "button" : undefined}
                        onClick={overlay ? () => {
                            onToggleOverlay(overlay);
                        } : undefined}
                        sx={{
                            width: "100%",
                            p: 1.25,
                            color: "inherit",
                            textAlign: "left",
                            font: "inherit",
                            cursor: overlay ? "pointer" : "default",
                            bgcolor: selected ? "rgba(99,102,241,.12)" : "transparent",
                            border: "1px solid",
                            borderColor: selected ? "primary.main" : "divider",
                            borderRadius: 1.5,
                        }}
                    >
                        <Stack direction="row" sx={{ alignItems: "center", justifyContent: "space-between", gap: 1 }}>
                            <Typography sx={{ fontWeight: 850 }}>{frame.timeframe_name}</Typography>
                            <Chip
                                size="small"
                                label={frame.status === "CONFIRMED" ? "Confirmed" : frame.status === "PARTIAL" ? "Partly confirmed" : "Not confirmed"}
                                color={frame.status === "CONFIRMED" ? "success" : frame.status === "PARTIAL" ? "warning" : "default"}
                            />
                        </Stack>
                        {frame.zone && (
                            <Stack direction="row" sx={{ mt: .75, flexWrap: "wrap", gap: 1 }}>
                                <Typography variant="caption">{frame.zone.zone_type === "DEMAND" ? "Demand" : "Supply"}</Typography>
                                <Typography variant="caption">Quality {frame.zone.quality.toFixed(0)}</Typography>
                                <Typography variant="caption">₹{frame.zone.lower_price.toLocaleString("en-IN")}–₹{frame.zone.upper_price.toLocaleString("en-IN")}</Typography>
                                <Typography variant="caption">Overlap {frame.zone.overlap_percent.toFixed(1)}%</Typography>
                                <Typography variant="caption">Distance {frame.zone.distance_percent.toFixed(2)}%</Typography>
                            </Stack>
                        )}
                        <Typography variant="body2" color="text.secondary" sx={{ mt: .5 }}>{frame.explanation}</Typography>
                        {overlay && <Typography variant="caption" color="primary.main">{selected ? "Shown on chart. Click to remove." : "Click to show this zone on the chart."}</Typography>}
                    </Box>
                );
            })}
            {!frames.length && <Typography color="text.secondary">No confirmed higher-timeframe zones were found.</Typography>}
            <Typography variant="caption" color="text.secondary">Uses delayed market data. This measures chart alignment, not the chance of profit.</Typography>
        </Stack>
    );
}

export default TimeframeConfluenceExplorer;
