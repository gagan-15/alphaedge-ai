import CheckCircleRoundedIcon from "@mui/icons-material/CheckCircleRounded";
import ErrorOutlineRoundedIcon from "@mui/icons-material/ErrorOutlineRounded";
import LightbulbOutlinedIcon from "@mui/icons-material/LightbulbOutlined";
import Box from "@mui/material/Box";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Chip from "@mui/material/Chip";
import Grid from "@mui/material/Grid";
import LinearProgress from "@mui/material/LinearProgress";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";

import type { ZoneExplanationFactor, ZoneResearchResult } from "../../types/scanner";

function FactorList({
    title,
    factors,
    positive,
}: {
    title: string;
    factors: ZoneExplanationFactor[];
    positive: boolean;
}) {
    if (factors.length === 0) return null;
    return (
        <Box>
            <Typography variant="h6" sx={{ mb: 1.25 }}>{title}</Typography>
            <Stack spacing={1}>
                {factors.map((factor) => (
                    <Box
                        key={factor.key}
                        sx={{
                            p: 1.25,
                            border: "1px solid",
                            borderColor: "divider",
                            borderRadius: 1.5,
                            bgcolor: positive ? "rgba(16,185,129,.06)" : "rgba(245,158,11,.06)",
                        }}
                    >
                        <Stack direction="row" spacing={1} sx={{ alignItems: "center" }}>
                            {positive
                                ? <CheckCircleRoundedIcon color="success" fontSize="small" />
                                : <ErrorOutlineRoundedIcon color="warning" fontSize="small" />}
                            <Typography sx={{ fontWeight: 800 }}>{factor.title}</Typography>
                        </Stack>
                        <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
                            {factor.summary}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                            Next check: {factor.recommendation}
                        </Typography>
                    </Box>
                ))}
            </Stack>
        </Box>
    );
}

function ZoneExplanationPanel({ result }: { result: ZoneResearchResult }) {
    const explanation = result.explanation;
    return (
        <Card variant="outlined" sx={{ mb: 1.5, overflow: "hidden" }}>
            <CardContent>
                <Grid container spacing={2.5}>
                    <Grid size={{ xs: 12, md: 4 }}>
                        <Typography color="text.secondary" variant="overline">Zone Quality</Typography>
                        <Stack direction="row" spacing={1.5} sx={{ alignItems: "baseline" }}>
                            <Typography variant="h2">{explanation.overall_score.toFixed(0)}</Typography>
                            <Typography color="text.secondary">/ 100</Typography>
                        </Stack>
                        <Typography color="warning.main" sx={{ letterSpacing: 2 }}>
                            {"★".repeat(explanation.rating)}{"☆".repeat(5 - explanation.rating)}
                        </Typography>
                        <Chip label={explanation.label} color={explanation.overall_score >= 70 ? "success" : "warning"} sx={{ mt: 1 }} />
                        <Typography variant="caption" color="text.secondary" sx={{ display: "block", mt: 1 }}>
                            Research quality, not probability of success.
                        </Typography>
                    </Grid>
                    <Grid size={{ xs: 12, md: 8 }}>
                        <Typography variant="h6">Overall Summary</Typography>
                        <Typography color="text.secondary" sx={{ mt: 1 }}>
                            {explanation.summary}
                        </Typography>
                    </Grid>
                    <Grid size={{ xs: 12, lg: 6 }}>
                        <FactorList title="Why AlphaEdge AI likes this zone" factors={explanation.positive_factors} positive />
                    </Grid>
                    <Grid size={{ xs: 12, lg: 6 }}>
                        <FactorList title="Things reducing the quality" factors={explanation.negative_factors} positive={false} />
                    </Grid>
                    <Grid size={{ xs: 12 }}>
                        <Typography variant="h6" sx={{ mb: 1 }}>Quality Breakdown</Typography>
                        <Grid container spacing={1.5}>
                            {[...explanation.positive_factors, ...explanation.negative_factors].map((factor) => (
                                <Grid key={factor.key} size={{ xs: 12, sm: 6, lg: 3 }}>
                                    <Stack direction="row" sx={{ justifyContent: "space-between" }}>
                                        <Typography variant="body2">{factor.title}</Typography>
                                        <Typography variant="body2" sx={{ fontWeight: 800 }}>{factor.score.toFixed(0)}</Typography>
                                    </Stack>
                                    <LinearProgress variant="determinate" value={factor.score} sx={{ mt: 0.75 }} />
                                </Grid>
                            ))}
                        </Grid>
                    </Grid>
                    <Grid size={{ xs: 12 }}>
                        <Box sx={{ display: "flex", gap: 1, p: 1.25, bgcolor: "rgba(99,102,241,.08)", borderRadius: 1.5 }}>
                            <LightbulbOutlinedIcon color="primary" />
                            <Box>
                                <Typography sx={{ fontWeight: 800 }}>Educational Insight</Typography>
                                <Typography variant="body2" color="text.secondary">
                                    {explanation.educational_insight}
                                </Typography>
                            </Box>
                        </Box>
                    </Grid>
                </Grid>
            </CardContent>
        </Card>
    );
}

export default ZoneExplanationPanel;
