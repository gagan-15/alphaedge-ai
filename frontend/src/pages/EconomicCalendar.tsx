import { useMemo, useState } from "react";

import CalendarMonthOutlinedIcon from "@mui/icons-material/CalendarMonthOutlined";
import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Chip from "@mui/material/Chip";
import MenuItem from "@mui/material/MenuItem";
import Stack from "@mui/material/Stack";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";

const events = [
    { date: "26 Jul", time: "10:00", country: "India", event: "RBI policy commentary", impact: "High", forecast: "—", previous: "—" },
    { date: "29 Jul", time: "17:30", country: "India", event: "Infrastructure output", impact: "Medium", forecast: "4.1%", previous: "4.8%" },
    { date: "31 Jul", time: "20:00", country: "United States", event: "Federal Reserve decision", impact: "High", forecast: "5.25%", previous: "5.25%" },
    { date: "01 Aug", time: "10:30", country: "India", event: "Manufacturing PMI", impact: "Medium", forecast: "58.2", previous: "58.5" },
    { date: "02 Aug", time: "18:00", country: "United States", event: "Non-farm payrolls", impact: "High", forecast: "190K", previous: "206K" },
    { date: "05 Aug", time: "14:30", country: "India", event: "Services PMI", impact: "Low", forecast: "60.8", previous: "60.5" },
];

export default function EconomicCalendar() {
    const [country, setCountry] = useState("All");
    const [impact, setImpact] = useState("All");
    const [window, setWindow] = useState("Upcoming");
    const visible = useMemo(() => events.filter((item, index) =>
        (country === "All" || item.country === country)
        && (impact === "All" || item.impact === impact)
        && (window === "Upcoming" || index === 0)
    ), [country, impact, window]);

    return <Stack spacing={1.5}>
        <Stack direction={{ xs: "column", md: "row" }} sx={{ justifyContent: "space-between", alignItems: { md: "center" } }}>
            <Box>
                <Typography variant="h4">Economic Calendar</Typography>
                <Typography color="text.secondary">Events that may affect Indian markets.</Typography>
            </Box>
            <Chip color="warning" label="DEMO EVENT FEED" />
        </Stack>
        <Card><CardContent>
            <Stack direction={{ xs: "column", md: "row" }} spacing={1.25}>
                <TextField select size="small" label="Country" value={country} onChange={(e) => setCountry(e.target.value)} sx={{ minWidth: 180 }}>
                    {["All", "India", "United States"].map((x) => <MenuItem key={x} value={x}>{x}</MenuItem>)}
                </TextField>
                <TextField select size="small" label="Impact" value={impact} onChange={(e) => setImpact(e.target.value)} sx={{ minWidth: 160 }}>
                    {["All", "High", "Medium", "Low"].map((x) => <MenuItem key={x} value={x}>{x}</MenuItem>)}
                </TextField>
                <Stack direction="row" spacing={0.5}>
                    {["Today", "Upcoming"].map((x) => <Button key={x} variant={window === x ? "contained" : "outlined"} onClick={() => setWindow(x)}>{x}</Button>)}
                </Stack>
            </Stack>
        </CardContent></Card>
        <Card><CardContent>
            <Stack direction="row" spacing={1} sx={{ mb: 1.5, alignItems: "center" }}>
                <CalendarMonthOutlinedIcon color="primary" /><Typography variant="h6">{window} events</Typography>
                <Chip size="small" label={`${visible.length} events`} />
            </Stack>
            <Box sx={{ overflowX: "auto" }}><Table size="small">
                <TableHead><TableRow>{["Date", "Time (IST)", "Country", "Event", "Impact", "Forecast", "Previous"].map((x) => <TableCell key={x}>{x}</TableCell>)}</TableRow></TableHead>
                <TableBody>{visible.map((row) => <TableRow key={`${row.date}-${row.event}`} hover>
                    <TableCell>{row.date}</TableCell><TableCell>{row.time}</TableCell><TableCell>{row.country}</TableCell>
                    <TableCell sx={{ fontWeight: 700 }}>{row.event}</TableCell>
                    <TableCell><Chip size="small" label={row.impact} color={row.impact === "High" ? "error" : row.impact === "Medium" ? "warning" : "default"} /></TableCell>
                    <TableCell>{row.forecast}</TableCell><TableCell>{row.previous}</TableCell>
                </TableRow>)}</TableBody>
            </Table></Box>
        </CardContent></Card>
        <Alert severity="info">Dates and figures are demonstration data. Connect an approved economic-data provider before production use.</Alert>
    </Stack>;
}
