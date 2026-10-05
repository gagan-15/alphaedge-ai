import { useState } from "react";

import AutoAwesomeOutlinedIcon from "@mui/icons-material/AutoAwesomeOutlined";
import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Chip from "@mui/material/Chip";
import Stack from "@mui/material/Stack";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";

const prompts = ["Market outlook", "Explain zone quality", "Risk check", "Strategy checklist", "News impact"];

function researchAnswer(question: string) {
    const text = question.toLowerCase();
    if (text.includes("zone")) return {
        title: "How to judge zone quality",
        points: ["Check freshness and later retests", "Require decisive departure and follow-through", "Review base width and candle count", "Confirm structure and higher-timeframe alignment", "Define invalidation before considering a setup"],
    };
    if (text.includes("risk")) return {
        title: "Pre-trade risk check",
        points: ["Choose maximum account risk first", "Measure entry-to-invalidation distance", "Calculate position size from that distance", "Check liquidity, gaps and event risk", "Never treat a quality score as return probability"],
    };
    if (text.includes("strategy")) return {
        title: "Rule-based strategy checklist",
        points: ["State the market and timeframe", "Define setup rules without hindsight", "Specify entry, invalidation and exit", "Include fees and slippage in testing", "Validate on unseen historical periods"],
    };
    if (text.includes("news")) return {
        title: "News-impact framework",
        points: ["Separate confirmed facts from commentary", "Check whether the event was already expected", "Review sector and index sensitivity", "Avoid assuming a headline predicts direction", "Use an approved live-news provider for production"],
    };
    return {
        title: "Market research framework",
        points: ["Review index trend and breadth", "Compare sector participation", "Check volatility and scheduled events", "Study price structure across timeframes", "Use scenarios, not guaranteed forecasts"],
    };
}

export default function AIAssistant() {
    const [question, setQuestion] = useState("");
    const [submitted, setSubmitted] = useState("Market outlook");
    const answer = researchAnswer(submitted);

    function submit(value = question) {
        if (!value.trim()) return;
        setSubmitted(value.trim());
        setQuestion("");
    }

    return <Stack spacing={1.5}>
        <Stack direction="row" spacing={1} sx={{ alignItems: "center" }}>
            <AutoAwesomeOutlinedIcon color="secondary" />
            <Box><Typography variant="h4">Ask AlphaEdge AI</Typography><Typography color="text.secondary">Explainable research guidance with no broker execution.</Typography></Box>
        </Stack>
        <Alert severity="info">Local guidance mode is active. A generative AI provider is not connected, so answers use transparent rule-based research templates.</Alert>
        <Card><CardContent>
            <Stack direction={{ xs: "column", md: "row" }} spacing={1}>
                <TextField fullWidth label="Ask about markets, zones, risk or strategies" value={question} onChange={(e) => setQuestion(e.target.value)} onKeyDown={(e) => e.key === "Enter" && submit()} />
                <Button variant="contained" onClick={() => submit()}>Analyse</Button>
            </Stack>
            <Stack direction="row" spacing={1} useFlexGap sx={{ mt: 1.5, flexWrap: "wrap" }}>
                {prompts.map((prompt) => <Chip key={prompt} clickable label={prompt} onClick={() => submit(prompt)} color={submitted === prompt ? "primary" : "default"} />)}
            </Stack>
        </CardContent></Card>
        <Card><CardContent>
            <Typography variant="overline" color="secondary.main">RESEARCH RESPONSE</Typography>
            <Typography variant="h5" sx={{ mb: 2 }}>{answer.title}</Typography>
            <Stack spacing={1.2}>{answer.points.map((point, index) => <Box key={point} sx={{ display: "flex", gap: 1.25, p: 1.25, border: "1px solid", borderColor: "divider", borderRadius: 1.5 }}>
                <Chip size="small" label={index + 1} color="primary" /><Typography>{point}</Typography>
            </Box>)}</Stack>
            <Typography variant="caption" color="text.secondary" sx={{ display: "block", mt: 2 }}>Educational research only. Verify market data and consult a SEBI-registered professional when required.</Typography>
        </CardContent></Card>
    </Stack>;
}
