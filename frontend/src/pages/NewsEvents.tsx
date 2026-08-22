import { useState } from "react";

import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Chip from "@mui/material/Chip";
import Grid from "@mui/material/Grid";
import LinearProgress from "@mui/material/LinearProgress";
import Stack from "@mui/material/Stack";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import Typography from "@mui/material/Typography";

const content = {
    Overview: ["Constructive demo conditions", "Broad participation remains positive in the current demo snapshot.", ["Advancers exceed decliners", "Volatility is lower", "Financials and IT show relative strength"]],
    Technical: ["Trend remains positive", "Selected indices remain above research moving averages.", ["Higher swing structure", "Positive momentum", "No verified breakout is claimed"]],
    Sentiment: ["Moderately positive sentiment", "Demo breadth suggests constructive participation, not a forecast.", ["Breadth above 55%", "India VIX lower in demo", "News sentiment feed unavailable"]],
    Scenarios: ["Conditional scenarios", "These are monitoring conditions, not predictions.", ["Bullish: breadth holds", "Neutral: leadership narrows", "Risk: volatility expands"]],
} as const;

function NewsEvents() {
    const [tab, setTab] = useState<keyof typeof content>("Overview");
    const selected = content[tab];
    return (
        <Stack spacing={1.5}>
            <Stack direction={{ xs: "column", md: "row" }} sx={{ justifyContent: "space-between", alignItems: { md: "center" } }}>
                <Box><Typography variant="h4">News & Events</Typography><Typography color="text.secondary">Explainable market context with source limitations.</Typography></Box>
                <Chip size="small" color="warning" label="NEWS PROVIDER NOT CONNECTED" />
            </Stack>
            <Stack direction="row" spacing={1}>
                {(Object.keys(content) as (keyof typeof content)[]).map((item) => (
                    <Button key={item} size="small" variant={tab === item ? "contained" : "outlined"} onClick={() => setTab(item)}>{item}</Button>
                ))}
            </Stack>
            <Grid container spacing={1.5}>
                <Grid size={{ xs: 12, lg: 8 }}>
                    <Card><CardContent>
                        <Typography color="success.main" variant="h5">{selected[0]}</Typography>
                        <Typography color="text.secondary" sx={{ my: 1.5 }}>{selected[1]}</Typography>
                        <Typography variant="h6" sx={{ mt: 2, mb: 1 }}>Observed factors</Typography>
                        {selected[2].map((factor) => <Typography key={factor} sx={{ py: .5 }}>• {factor}</Typography>)}
                    </CardContent></Card>
                </Grid>
                <Grid size={{ xs: 12, lg: 4 }}>
                    <Card><CardContent sx={{ textAlign: "center" }}>
                        <Typography variant="h6">Context quality</Typography>
                        <Typography variant="h2" color="primary.main" sx={{ my: 2 }}>62</Typography>
                        <LinearProgress variant="determinate" value={62} />
                        <Typography color="text.secondary" sx={{ mt: 1.5 }}>Limited because verified news sources are unavailable.</Typography>
                    </CardContent></Card>
                </Grid>
                <Grid size={12}>
                    <Card><CardContent>
                        <Typography variant="h6" sx={{ mb: 1 }}>Event Monitor</Typography>
                        <Table size="small">
                            <TableHead><TableRow>{["Time", "Event", "Possible relevance", "Status"].map((heading) => <TableCell key={heading}>{heading}</TableCell>)}</TableRow></TableHead>
                            <TableBody>
                                {[["09:15", "RBI policy commentary", "Banks and rates"], ["11:30", "Infrastructure output", "Industrials"], ["20:00", "US Federal Reserve decision", "Global risk sentiment"]].map((row) => (
                                    <TableRow key={row[1]}>{row.map((cell) => <TableCell key={cell}>{cell}</TableCell>)}<TableCell><Chip size="small" color="warning" label="Demo" /></TableCell></TableRow>
                                ))}
                            </TableBody>
                        </Table>
                    </CardContent></Card>
                </Grid>
            </Grid>
        </Stack>
    );
}

export default NewsEvents;
