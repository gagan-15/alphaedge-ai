import { useMemo, useState } from "react";

import CalculateOutlinedIcon from "@mui/icons-material/CalculateOutlined";
import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Grid from "@mui/material/Grid";
import Stack from "@mui/material/Stack";
import Tab from "@mui/material/Tab";
import Tabs from "@mui/material/Tabs";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";

const tools = ["Position size", "Risk / reward", "Profit", "Average price", "SIP", "Fibonacci"];

function Field({ label, value, onChange }: { label: string; value: number; onChange: (value: number) => void }) {
    return <TextField fullWidth type="number" label={label} value={value} onChange={(event) => onChange(Number(event.target.value))} />;
}

export default function Calculators() {
    const [active, setActive] = useState(0);
    const [values, setValues] = useState({
        capital: 100000, risk: 1, entry: 100, stop: 95, target: 115, quantity: 10,
        sell: 120, firstPrice: 100, firstQty: 10, secondPrice: 90, secondQty: 10,
        monthly: 5000, rate: 12, years: 10, high: 120, low: 80,
    });
    const set = (key: keyof typeof values) => (value: number) => setValues((current) => ({ ...current, [key]: value }));
    const result = useMemo(() => {
        const riskCapital = values.capital * values.risk / 100;
        const riskDistance = Math.abs(values.entry - values.stop);
        const rewardDistance = Math.abs(values.target - values.entry);
        const totalQty = values.firstQty + values.secondQty;
        const monthlyRate = values.rate / 1200;
        const months = Math.max(0, values.years * 12);
        return {
            position: riskDistance ? Math.floor(riskCapital / riskDistance) : 0,
            riskCapital,
            ratio: riskDistance ? rewardDistance / riskDistance : 0,
            profit: (values.sell - values.entry) * values.quantity,
            average: totalQty ? (values.firstPrice * values.firstQty + values.secondPrice * values.secondQty) / totalQty : 0,
            sip: monthlyRate ? values.monthly * (((1 + monthlyRate) ** months - 1) / monthlyRate) * (1 + monthlyRate) : values.monthly * months,
        };
    }, [values]);

    const panels = [
        <><Field label="Account capital (₹)" value={values.capital} onChange={set("capital")} /><Field label="Risk per idea (%)" value={values.risk} onChange={set("risk")} /><Field label="Entry price (₹)" value={values.entry} onChange={set("entry")} /><Field label="Invalidation price (₹)" value={values.stop} onChange={set("stop")} /></>,
        <><Field label="Entry price (₹)" value={values.entry} onChange={set("entry")} /><Field label="Invalidation price (₹)" value={values.stop} onChange={set("stop")} /><Field label="Target scenario (₹)" value={values.target} onChange={set("target")} /></>,
        <><Field label="Entry price (₹)" value={values.entry} onChange={set("entry")} /><Field label="Exit price (₹)" value={values.sell} onChange={set("sell")} /><Field label="Quantity" value={values.quantity} onChange={set("quantity")} /></>,
        <><Field label="First price (₹)" value={values.firstPrice} onChange={set("firstPrice")} /><Field label="First quantity" value={values.firstQty} onChange={set("firstQty")} /><Field label="Second price (₹)" value={values.secondPrice} onChange={set("secondPrice")} /><Field label="Second quantity" value={values.secondQty} onChange={set("secondQty")} /></>,
        <><Field label="Monthly contribution (₹)" value={values.monthly} onChange={set("monthly")} /><Field label="Illustrative annual rate (%)" value={values.rate} onChange={set("rate")} /><Field label="Years" value={values.years} onChange={set("years")} /></>,
        <><Field label="Range high" value={values.high} onChange={set("high")} /><Field label="Range low" value={values.low} onChange={set("low")} /></>,
    ];
    const resultViews = [
        [["Capital at risk", `₹${result.riskCapital.toLocaleString("en-IN")}`], ["Illustrative quantity", result.position.toLocaleString("en-IN")]],
        [["Risk / reward", `1 : ${result.ratio.toFixed(2)}`], ["Risk distance", `₹${Math.abs(values.entry - values.stop).toFixed(2)}`]],
        [["Gross result", `₹${result.profit.toLocaleString("en-IN")}`], ["Before costs", "Fees and taxes excluded"]],
        [["Weighted average", `₹${result.average.toFixed(2)}`], ["Total quantity", (values.firstQty + values.secondQty).toLocaleString("en-IN")]],
        [["Illustrative value", `₹${Math.round(result.sip).toLocaleString("en-IN")}`], ["Assumed return", `${values.rate}% yearly`]],
        [23.6, 38.2, 50, 61.8, 78.6].map((level) => [`${level}% retracement`, (values.high - (values.high - values.low) * level / 100).toFixed(2)]),
    ];

    return <Stack spacing={1.5}>
        <Box><Typography variant="h4">Trading Calculators</Typography><Typography color="text.secondary">Working mathematical tools for planning and risk awareness.</Typography></Box>
        <Card><Tabs value={active} onChange={(_, value) => setActive(value)} variant="scrollable" scrollButtons="auto">
            {tools.map((tool) => <Tab key={tool} icon={<CalculateOutlinedIcon />} iconPosition="start" label={tool} />)}
        </Tabs></Card>
        <Grid container spacing={1.5}>
            <Grid size={{ xs: 12, lg: 7 }}><Card><CardContent><Stack spacing={1.5}>{panels[active]}</Stack></CardContent></Card></Grid>
            <Grid size={{ xs: 12, lg: 5 }}><Card sx={{ height: "100%" }}><CardContent>
                <Typography variant="h6" sx={{ mb: 2 }}>{tools[active]} result</Typography>
                <Stack spacing={1.5}>{resultViews[active].map(([label, value]) => <Box key={label} sx={{ p: 1.5, border: "1px solid", borderColor: "divider", borderRadius: 1.5 }}>
                    <Typography variant="caption" color="text.secondary">{label}</Typography><Typography variant="h5">{value}</Typography>
                </Box>)}</Stack>
            </CardContent></Card></Grid>
        </Grid>
        <Alert severity="info">Mathematical illustration only. Results are not investment advice and exclude brokerage, taxes, liquidity and slippage unless stated.</Alert>
    </Stack>;
}
