/**
 * AI Insight Card.
 *
 * Sprint:
 *     2.54 - AI Insight Card
 */

import PsychologyIcon from "@mui/icons-material/Psychology";
import Box from "@mui/material/Box";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Chip from "@mui/material/Chip";
import LinearProgress from "@mui/material/LinearProgress";
import Typography from "@mui/material/Typography";

import type { AIExplanationResult } from "../../types/dashboard";

interface AIInsightCardProps {
    insight: AIExplanationResult;
}

function AIInsightCard({
    insight,
}: AIInsightCardProps) {
    const chipColor =
        insight.decision === "BUY"
            ? "success"
            : insight.decision === "SELL"
              ? "error"
              : "warning";

    return (
        <Card sx={{ mt: 3 }}>
            <CardContent>
                <Box
                    sx={{
                        display: "flex",
                        justifyContent: "space-between",
                        alignItems: "center",
                        mb: 2,
                    }}
                >
                    <Box
                        sx={{
                            display: "flex",
                            alignItems: "center",
                            gap: 1,
                        }}
                    >
                        <PsychologyIcon color="primary" />

                        <Typography variant="h6">
                            AI Insight
                        </Typography>
                    </Box>

                    <Chip
                        label={insight.decision}
                        color={chipColor}
                    />
                </Box>

                <Typography
                    variant="body1"
                    sx={{
                        fontWeight: 600,
                        mb: 1,
                    }}
                >
                    {insight.summary}
                </Typography>

                {insight.reasons.map((reason) => (
                    <Typography
                        key={reason}
                        variant="body2"
                        color="text.secondary"
                    >
                        • {reason}
                    </Typography>
                ))}

                <Box sx={{ mt: 2 }}>
                    <Typography
                        variant="caption"
                    >
                        Confidence {insight.confidence_score}%
                    </Typography>

                    <LinearProgress
                        variant="determinate"
                        value={insight.confidence_score}
                        sx={{ mt: 1 }}
                    />
                </Box>
            </CardContent>
        </Card>
    );
}

export default AIInsightCard;