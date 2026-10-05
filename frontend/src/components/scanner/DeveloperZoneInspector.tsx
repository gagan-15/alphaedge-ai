import ExpandMoreRoundedIcon from "@mui/icons-material/ExpandMoreRounded";
import Accordion from "@mui/material/Accordion";
import AccordionDetails from "@mui/material/AccordionDetails";
import AccordionSummary from "@mui/material/AccordionSummary";
import Box from "@mui/material/Box";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Chip from "@mui/material/Chip";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";

import type { DeveloperChartZone, DeveloperZoneStatus } from "./developerZones";
import type { ZoneCandidateDiagnostic } from "../../types/scanner";

interface DeveloperZoneInspectorProps {
    zones: DeveloperChartZone[];
    unformedCandidates?: ZoneCandidateDiagnostic[];
}

const groups: Array<{ status: DeveloperZoneStatus; title: string }> = [
    { status: "Accepted", title: "Accepted Zones" },
    { status: "Rejected", title: "Rejected Candidates" },
    { status: "Invalidated", title: "Invalidated Zones" },
];

function DeveloperZoneInspector({ zones, unformedCandidates = [] }: DeveloperZoneInspectorProps) {
    return (
        <Card sx={{ mb: 1.25, borderColor: "warning.main" }}>
            <CardContent>
                <Typography variant="h6">Developer Zone Inspector</Typography>
                <Typography variant="caption" color="text.secondary">
                    Internal rendering data. This does not change scanner results.
                </Typography>
                <Box sx={{ mt: 1 }}>
                    {groups.map((group) => {
                        const items = zones.filter((zone) => zone.zoneStatus === group.status);
                        const unformed = group.status === "Rejected" ? unformedCandidates : [];
                        return (
                            <Accordion key={group.status} disableGutters elevation={0} sx={{ bgcolor: "transparent" }}>
                                <AccordionSummary expandIcon={<ExpandMoreRoundedIcon />}>
                                    <Stack direction="row" sx={{ alignItems: "center", gap: 1 }}>
                                        <Typography sx={{ fontWeight: 700 }}>{group.title}</Typography>
                                        <Chip size="small" label={items.length + unformed.length} />
                                    </Stack>
                                </AccordionSummary>
                                <AccordionDetails>
                                    {items.length === 0 && unformed.length === 0 ? (
                                        <Typography variant="caption" color="text.secondary">
                                            No {group.title.toLowerCase()} were supplied.
                                        </Typography>
                                    ) : (
                                        <Stack spacing={1}>
                                            {items.map((zone) => (
                                                <Box key={`${group.status}-${zone.zoneId}`} sx={{ p: 1, border: "1px solid", borderColor: "divider", borderRadius: 1.5 }}>
                                                    <Typography sx={{ fontWeight: 750 }}>
                                                        {zone.zoneId} · {zone.zoneType} · {zone.pattern ?? "Pattern unavailable"}
                                                    </Typography>
                                                    <Typography variant="caption" color="text.secondary">
                                                        Score {zone.zoneScore ?? "Unavailable"} · {zone.zoneStatus}
                                                    </Typography>
                                                    <Typography variant="caption" color="text.secondary" sx={{ display: "block" }}>
                                                        Candles {zone.baseStartDate ?? "Unknown"} to {zone.baseEndDate ?? "Unknown"} · Zone ₹{Math.min(zone.proximalPrice, zone.distalPrice).toLocaleString("en-IN")}–₹{Math.max(zone.proximalPrice, zone.distalPrice).toLocaleString("en-IN")}
                                                    </Typography>
                                                    {zone.rejectionReasons?.length ? (
                                                        <Typography variant="caption" color="text.secondary" sx={{ display: "block" }}>
                                                            {zone.rejectionReasons.join("; ")}
                                                        </Typography>
                                                    ) : null}
                                                    {zone.ruleResults?.filter((rule) => !rule.passed).map((rule) => (
                                                        <Typography key={rule.key} variant="caption" color="error.light" sx={{ display: "block" }}>
                                                            Failed: {rule.label} · {String(rule.actual ?? "Unavailable")} (required {String(rule.required ?? "Unavailable")})
                                                        </Typography>
                                                    ))}
                                                </Box>
                                            ))}
                                            {unformed.map((candidate) => (
                                                <Box key={candidate.candidate_id} sx={{ p: 1, border: "1px dashed", borderColor: "warning.main", borderRadius: 1.5 }}>
                                                    <Typography sx={{ fontWeight: 750 }}>
                                                        Candidate not formed · {candidate.base_start_date}
                                                    </Typography>
                                                    <Typography variant="caption" color="text.secondary" sx={{ display: "block" }}>
                                                        Candle {candidate.base_start_index + 1} · Pattern unavailable because the initial base condition failed.
                                                    </Typography>
                                                    {candidate.rule_results.filter((rule) => !rule.passed).map((rule) => (
                                                        <Typography key={rule.key} variant="caption" color="error.light" sx={{ display: "block" }}>
                                                            Failed: {rule.label} · {String(rule.actual ?? "Unavailable")} (required {String(rule.required ?? "Unavailable")})
                                                        </Typography>
                                                    ))}
                                                </Box>
                                            ))}
                                        </Stack>
                                    )}
                                </AccordionDetails>
                            </Accordion>
                        );
                    })}
                </Box>
            </CardContent>
        </Card>
    );
}

export default DeveloperZoneInspector;
