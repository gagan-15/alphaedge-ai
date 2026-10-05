import AccessTimeRoundedIcon from "@mui/icons-material/AccessTimeRounded";
import CloudDoneOutlinedIcon from "@mui/icons-material/CloudDoneOutlined";
import ErrorOutlineRoundedIcon from "@mui/icons-material/ErrorOutlineRounded";
import SyncRoundedIcon from "@mui/icons-material/SyncRounded";
import Box from "@mui/material/Box";
import Chip from "@mui/material/Chip";
import Stack from "@mui/material/Stack";
import Tooltip from "@mui/material/Tooltip";
import Typography from "@mui/material/Typography";

import type { DhanRuntimeStatus } from "../../api/scannerApi";
import type { ZoneResearchResult } from "../../types/scanner";

interface DhanDataStatusProps {
    status: DhanRuntimeStatus | null;
    currentResult?: ZoneResearchResult;
}

function displayTime(value?: string | null) {
    if (!value) return "—";
    const parsed = new Date(value);
    return Number.isNaN(parsed.getTime()) ? value.slice(0, 10) : parsed.toLocaleString();
}

export default function DhanDataStatus({ status, currentResult }: DhanDataStatusProps) {
    const state = status?.data_status ?? "READY";
    const wasCancelled = status?.last_update.status === "CANCELLED";
    const failedUpdate = status?.last_update.status === "FAILED";
    const activeRun = state === "UPDATING" || state === "CANCELLING";
    const update = status?.last_update;
    const progressTotal = update?.progress_total ?? 0;
    const progressCompleted = update?.progress_completed ?? 0;
    const tone = state === "FAILED" ? { color: "#B42318", bg: "#FEF3F2", border: "#FECDCA", icon: <ErrorOutlineRoundedIcon fontSize="small" /> }
        : state === "CANCELLING" ? { color: "#B54708", bg: "#FFFAEB", border: "#FEDF89", icon: <SyncRoundedIcon fontSize="small" /> }
            : state === "UPDATING" ? { color: "#175CD3", bg: "#EFF8FF", border: "#B2DDFF", icon: <SyncRoundedIcon fontSize="small" /> }
            : { color: "#027A48", bg: "#ECFDF3", border: "#ABEFC6", icon: <CloudDoneOutlinedIcon fontSize="small" /> };
    const source = currentResult?.price_source ?? "PERSISTED_DHAN_CLOSE";
    const priceAsOf = currentResult?.price_as_of;
    return (
        <Box sx={{ px: 3.25, pt: 1.35, pb: 0.25 }}>
            <Stack direction="row" spacing={1} sx={{ alignItems: "center", flexWrap: "wrap", rowGap: 0.7 }}>
                <Chip
                    icon={tone.icon}
                    label={`Data Status: ${state}`}
                    size="small"
                    sx={{ height: 25, color: tone.color, bgcolor: tone.bg, border: "1px solid", borderColor: tone.border, fontWeight: 700 }}
                />
                {status?.auth_status && (
                    <Typography variant="caption" color={status.auth_status === "AUTH_REQUIRED" ? "error" : "text.secondary"}>
                        Dhan auth: {status.auth_status}
                    </Typography>
                )}
                <Typography variant="caption" color="text.secondary">Last successful update: {displayTime(status?.last_successful_update)}</Typography>
                {wasCancelled && <Typography variant="caption" color="text.secondary">Last update cancelled</Typography>}
                {failedUpdate && (
                    <Typography variant="caption" color="error">
                        Update failed: {update?.stage || "Update failed"}{update?.error ? ` (${update.error})` : ""}
                    </Typography>
                )}
                <Typography variant="caption" color="text.secondary">Latest trading date: {displayTime(status?.latest_trading_date)}</Typography>
                <Tooltip title={source === "LIVE_QUOTE" ? "Live Dhan Market Quote" : "Latest validated persisted Dhan Daily close"}>
                    <Stack direction="row" spacing={0.35} sx={{ alignItems: "center", color: "text.secondary" }}>
                        <AccessTimeRoundedIcon sx={{ fontSize: 14 }} />
                        <Typography variant="caption">Price: {source}{priceAsOf ? ` · ${displayTime(priceAsOf)}` : ""}</Typography>
                    </Stack>
                </Tooltip>
            </Stack>
            {activeRun && update && (
                <Stack direction="row" spacing={1.1} sx={{ mt: .7, ml: .15, alignItems: "center", flexWrap: "wrap", rowGap: .35 }}>
                    <Typography variant="caption" sx={{ color: tone.color, fontWeight: 700 }}>
                        Run #{update.run_id ?? "—"} · {update.stage || "Checking Dhan..."}
                    </Typography>
                    {progressTotal > 0 && (
                        <Typography variant="caption" color="text.secondary">
                            {progressCompleted.toLocaleString()} / {progressTotal.toLocaleString()} instruments
                        </Typography>
                    )}
                    {update.affected_timeframes && (
                        <Typography variant="caption" color="text.secondary">
                            Affected timeframes: {update.affected_timeframes}
                        </Typography>
                    )}
                    <Typography variant="caption" color="text.secondary">
                        Started: {displayTime(update.started_at)}
                    </Typography>
                </Stack>
            )}
        </Box>
    );
}
