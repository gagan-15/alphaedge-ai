import ExpandMoreRoundedIcon from "@mui/icons-material/ExpandMoreRounded";
import OpenInNewRoundedIcon from "@mui/icons-material/OpenInNewRounded";
import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Chip from "@mui/material/Chip";
import Collapse from "@mui/material/Collapse";
import Grid from "@mui/material/Grid";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { useEffect, useMemo, useState } from "react";
import { Link as RouterLink } from "react-router-dom";

import {
    getComparableHistoricalEvidence,
    historicalEvidenceErrorMessage,
} from "../../api/historicalEvidenceApi";
import type { ComparableHistoricalEvidence, EvidenceMetric } from "../../types/historicalEvidence";
import type { ZoneResearchResult } from "../../types/scanner";
import { zoneIdFor } from "../../services/zoneSelectionService";

function metricText(metric: EvidenceMetric) {
    const percent = metric.percent === null ? "Unavailable" : `${metric.percent.toFixed(1)}%`;
    return `${metric.numerator} / ${metric.denominator} · ${percent}`;
}

function matchTitle(level: number | null) {
    return level === 1 ? "Closest Match" : "Broadened Historical Match";
}

interface Props {
    result: ZoneResearchResult;
    zones: ZoneResearchResult[];
    methodologyVersion: string;
}

const comparablePattern: Record<string, string> = {
    DROP_BASE_RALLY: "DBR",
    RALLY_BASE_RALLY: "RBR",
    RALLY_BASE_DROP: "RBD",
    DROP_BASE_DROP: "DBD",
};

export default function ComparableHistoricalEvidenceSection({ result, zones, methodologyVersion }: Props) {
    const [open, setOpen] = useState(false);
    const [responseState, setResponseState] = useState<{ key: string; data: ComparableHistoricalEvidence | null; error: string }>({ key: "", data: null, error: "" });
    const qualityLabel = result.zone_quality_label;
    const confidenceLabel = result.trade_confidence?.label;
    const pattern = result.pattern_type ? comparablePattern[result.pattern_type] ?? result.pattern_type : null;
    const zoneId = zoneIdFor(zones, result);
    const requestKey = `${zoneId}:${result.timeframe}:${result.zone_type}:${pattern ?? ""}:${qualityLabel ?? ""}:${confidenceLabel ?? ""}:${methodologyVersion}`;
    const data = responseState.key === requestKey ? responseState.data : null;
    const error = responseState.key === requestKey ? responseState.error : "";

    useEffect(() => {
        let active = true;
        if (!qualityLabel || !confidenceLabel || !pattern || !methodologyVersion) return () => { active = false; };
        void getComparableHistoricalEvidence({
            zone_id: zoneId,
            timeframe: result.timeframe,
            zone_type: result.zone_type,
            pattern,
            zone_quality_label: qualityLabel,
            trade_confidence_label: confidenceLabel,
            current_methodology_version: methodologyVersion,
        }).then((response) => {
            if (active) setResponseState({ key: requestKey, data: response, error: "" });
        }).catch((reason) => {
            if (active) setResponseState({ key: requestKey, data: null, error: historicalEvidenceErrorMessage(reason) });
        });
        return () => { active = false; };
    }, [confidenceLabel, methodologyVersion, pattern, qualityLabel, requestKey, result.timeframe, result.zone_type, zoneId]);

    const fullEvidenceUrl = useMemo(() => {
        if (!data?.applied_cohort_definition) return "/historical-evidence";
        const definition = data.applied_cohort_definition;
        const query = new URLSearchParams();
        if (definition.timeframe) query.set("timeframe", definition.timeframe);
        if (definition.zone_type) query.set("zone_type", definition.zone_type);
        if (definition.pattern) query.set("pattern", definition.pattern);
        if (definition.zone_quality_label) query.set("zone_quality", definition.zone_quality_label);
        if (definition.trade_confidence_label) query.set("trade_confidence", definition.trade_confidence_label);
        return `/historical-evidence?${query.toString()}`;
    }, [data]);

    const summary = data?.summary_metrics;
    return (
        <Box sx={{ border: "1px solid", borderColor: "divider", borderRadius: 1.5, overflow: "hidden" }}>
            <Button
                fullWidth
                onClick={() => setOpen((value) => !value)}
                endIcon={<ExpandMoreRoundedIcon sx={{ transform: open ? "rotate(180deg)" : "none", transition: "transform 180ms" }} />}
                sx={{ px: 1.5, py: 1.1, justifyContent: "space-between", color: "text.primary" }}
            >
                <Box sx={{ textAlign: "left" }}>
                    <Typography variant="overline" color="text.secondary">Historical Evidence</Typography>
                    <Typography sx={{ fontWeight: 700 }}>Comparable Historical Setups</Typography>
                </Box>
            </Button>
            <Collapse in={open}>
                <Box sx={{ px: 1.5, pb: 1.5 }}>
                    {!data && !error && <Typography color="text.secondary">Loading frozen historical evidence…</Typography>}
                    {error && <Alert severity="warning">{error.includes("methodology") ? "Historical evidence is unavailable for the current methodology version." : error}</Alert>}
                    {data && data.status !== "AVAILABLE" && <Alert severity="info">{data.explanation}</Alert>}
                    {data && data.status === "AVAILABLE" && summary && (
                        <Stack spacing={1.25}>
                            <Typography variant="caption" color="text.secondary">
                                {data.current_zone.timeframe} · {data.current_zone.zone_type} · {data.current_zone.pattern} · {data.current_zone.zone_quality_label} ZQ · {data.current_zone.trade_confidence_label} TC
                            </Typography>
                            <Stack direction="row" spacing={1} sx={{ alignItems: "center", flexWrap: "wrap" }}>
                                <Chip size="small" label={data.reliability.replaceAll("_", " ")} />
                                <Typography sx={{ fontWeight: 700 }}>{matchTitle(data.selected_match_level)}</Typography>
                            </Stack>
                            <Typography variant="body2" color="text.secondary">{data.explanation}</Typography>
                            <Typography variant="caption">
                                Exact closest-match sample: {data.exact_level_1?.historical_zones ?? 0} historical zones / {data.exact_level_1?.interacted_zones ?? 0} interacted
                            </Typography>
                            <Grid container spacing={1}>
                                <Grid size={{ xs: 6 }}><Typography variant="caption" color="text.secondary">Historical Zones</Typography><Typography>{summary.historical_zones}</Typography></Grid>
                                <Grid size={{ xs: 6 }}><Typography variant="caption" color="text.secondary">Interacted Zones</Typography><Typography>{summary.interacted_zones}</Typography></Grid>
                                <Grid size={{ xs: 6 }}><Typography variant="caption" color="text.secondary">Interaction Rate</Typography><Typography>{metricText(summary.interaction_rate)}</Typography></Grid>
                                <Grid size={{ xs: 6 }}><Typography variant="caption" color="text.secondary">Structural Survival</Typography><Typography>{metricText(summary.structural_survival)}</Typography></Grid>
                                <Grid size={{ xs: 6 }}><Typography variant="caption" color="text.secondary">≥1 ZW</Typography><Typography>{metricText(summary.reaction_1_zone_width)}</Typography></Grid>
                                <Grid size={{ xs: 6 }}><Typography variant="caption" color="text.secondary">≥2 ZW</Typography><Typography>{metricText(summary.reaction_2_zone_width)}</Typography></Grid>
                                <Grid size={{ xs: 6 }}><Typography variant="caption" color="text.secondary">≥3 ZW</Typography><Typography>{metricText(summary.reaction_3_zone_width)}</Typography></Grid>
                                <Grid size={{ xs: 6 }}><Typography variant="caption" color="text.secondary">≥5 ZW</Typography><Typography>{metricText(summary.reaction_5_zone_width)}</Typography></Grid>
                                <Grid size={{ xs: 12 }}><Typography variant="caption" color="text.secondary">Structural Target Achievement</Typography><Typography>{metricText(summary.structural_target_achievement)}</Typography></Grid>
                                <Grid size={{ xs: 6 }}><Typography variant="caption" color="text.secondary">Median Favorable Excursion</Typography><Typography>{summary.median_mfe_zone_width === null ? "Unavailable" : `${summary.median_mfe_zone_width.toFixed(2)} zone widths`}</Typography></Grid>
                                <Grid size={{ xs: 6 }}><Typography variant="caption" color="text.secondary">Median Adverse Excursion</Typography><Typography>{summary.median_mae_zone_width === null ? "Unavailable" : `${summary.median_mae_zone_width.toFixed(2)} zone widths`}</Typography></Grid>
                            </Grid>
                            <Typography variant="caption" color="text.secondary">
                                These results describe how comparable historical zones behaved. Historical behavior does not guarantee a future result.
                            </Typography>
                            <Button component={RouterLink} to={fullEvidenceUrl} size="small" endIcon={<OpenInNewRoundedIcon />}>View Full Historical Evidence</Button>
                        </Stack>
                    )}
                </Box>
            </Collapse>
        </Box>
    );
}
