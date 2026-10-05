import InfoOutlinedIcon from "@mui/icons-material/InfoOutlined";
import Box from "@mui/material/Box";
import Stack from "@mui/material/Stack";
import Tooltip from "@mui/material/Tooltip";
import Typography from "@mui/material/Typography";

import type { ZoneResearchResult } from "../../types/scanner";
import {
    canonicalQualityComponents,
    formatZoneQuality,
    formatZoneQualityLabel,
    qualityReasonDescriptions,
    zoneQualityComponentHelp,
    zoneQualityComponentNames,
} from "./zoneQualityPresentation";

export default function ZoneQualityBreakdown({ result }: { result: ZoneResearchResult }) {
    const components = canonicalQualityComponents(result);
    const reasons = qualityReasonDescriptions(result);
    const authenticityUnavailable = (result.zone_quality_reason_codes ?? []).includes("AUTHENTICITY_UNAVAILABLE");

    return <Box sx={{ mt: 1.25 }}>
        <Typography variant="overline" color="text.secondary">AlphaEdge Canonical Zone Quality</Typography>
        <Stack direction="row" sx={{ alignItems: "baseline", justifyContent: "space-between", mb: 1 }}>
            <Typography sx={{ fontWeight: 700 }}>Zone Quality</Typography>
            <Typography sx={{ fontWeight: 800 }}>{formatZoneQuality(result.zone_score)} · {formatZoneQualityLabel(result.zone_quality_label)}</Typography>
        </Stack>
        {components.length > 0 ? <Stack spacing={0.7}>
            {components.map((component) => <Stack key={component.key} direction="row" sx={{ alignItems: "center", justifyContent: "space-between", gap: 1 }}>
                <Stack direction="row" spacing={0.5} sx={{ alignItems: "center", minWidth: 0 }}>
                    <Typography variant="body2">{zoneQualityComponentNames[component.key] ?? component.key}</Typography>
                    <Tooltip title={zoneQualityComponentHelp[component.key] ?? "Canonical formation evidence component."}>
                        <InfoOutlinedIcon sx={{ color: "text.secondary", fontSize: 14 }} />
                    </Tooltip>
                </Stack>
                <Typography variant="body2" sx={{ fontWeight: 700, whiteSpace: "nowrap" }}>
                    {component.score.toFixed(1)} / {component.maximum_score.toFixed(0)}
                </Typography>
            </Stack>)}
            <Stack direction="row" sx={{ justifyContent: "space-between", pt: 0.75, borderTop: "1px solid", borderColor: "divider" }}>
                <Typography sx={{ fontWeight: 800 }}>Total</Typography>
                <Typography sx={{ fontWeight: 800 }}>{formatZoneQuality(result.zone_score)} / 100</Typography>
            </Stack>
        </Stack> : <Typography variant="caption" color="text.secondary">Component evidence is unavailable for this legacy zone.</Typography>}
        {authenticityUnavailable && <Typography variant="caption" color="text.secondary" sx={{ display: "block", mt: 0.75 }}>
            Authenticity status: Evidence unavailable. The neutral component score is shown.
        </Typography>}
        {reasons.length > 0 && <Box sx={{ mt: 1.25 }}>
            <Typography sx={{ fontWeight: 700, mb: 0.5 }}>Why this score?</Typography>
            {reasons.map((reason) => <Typography key={reason} variant="caption" color="text.secondary" sx={{ display: "block" }}>✓ {reason}</Typography>)}
        </Box>}
        <Typography variant="caption" color="text.secondary" sx={{ display: "block", mt: 1 }}>
            Formation quality only. This is not a prediction of profit.
        </Typography>
    </Box>;
}
