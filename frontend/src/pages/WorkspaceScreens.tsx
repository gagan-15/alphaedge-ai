import { useMemo, useState } from "react";

import AddAlertOutlinedIcon from "@mui/icons-material/AddAlertOutlined";
import CalculateOutlinedIcon from "@mui/icons-material/CalculateOutlined";
import CalendarMonthOutlinedIcon from "@mui/icons-material/CalendarMonthOutlined";
import InsightsOutlinedIcon from "@mui/icons-material/InsightsOutlined";
import Button from "@mui/material/Button";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Chip from "@mui/material/Chip";
import Grid from "@mui/material/Grid";
import LinearProgress from "@mui/material/LinearProgress";
import MenuItem from "@mui/material/MenuItem";
import Stack from "@mui/material/Stack";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";

const stocks = [
    ["RELIANCE", "2,978.45", "+0.83%", "Bullish Setup"],
    ["TCS", "3,584.75", "-0.41%", "Watch"],
    ["HDFCBANK", "1,654.20", "+1.12%", "Bullish Setup"],
    ["INFY", "1,512.10", "+0.35%", "Watch"],
    ["ICICIBANK", "1,234.55", "+0.78%", "Bullish Setup"],
];

function PageTitle({ title, subtitle }: { title: string; subtitle: string }) {
    return (
        <Stack spacing={0.5}>
            <Typography variant="h4">{title}</Typography>
            <Typography color="text.secondary">{subtitle}</Typography>
        </Stack>
    );
}

function MetricCard({ label, value, note }: {
    label: string;
    value: string;
    note: string;
}) {
    return (
        <Card>
            <CardContent>
                <Typography color="text.secondary" variant="body2">{label}</Typography>
                <Typography variant="h5" sx={{ mt: 1 }}>{value}</Typography>
                <Typography color="success.main" variant="body2">{note}</Typography>
            </CardContent>
        </Card>
    );
}

function StockTable() {
    return (
        <Table size="small">
            <TableHead>
                <TableRow>
                    {["Symbol", "Price", "Change", "Research view"].map((item) => (
                        <TableCell key={item}>{item}</TableCell>
                    ))}
                </TableRow>
            </TableHead>
            <TableBody>
                {stocks.map((row) => (
                    <TableRow key={row[0]} hover>
                        {row.map((cell, index) => (
                            <TableCell
                                key={cell}
                                sx={index === 2 ? {
                                    color: cell.startsWith("+")
                                        ? "success.main"
                                        : "error.main",
                                } : undefined}
                            >
                                {index === 3 ? (
                                    <Chip
                                        size="small"
                                        label={cell}
                                        color={cell === "Bullish Setup" ? "success" : "default"}
                                    />
                                ) : cell}
                            </TableCell>
                        ))}
                    </TableRow>
                ))}
            </TableBody>
        </Table>
    );
}

export function MarketOverviewPage() {
    return (
        <Stack spacing={2.5}>
            <PageTitle title="Market Overview" subtitle="Indian market health and movement at a glance." />
            <Grid container spacing={2}>
                {[
                    ["NIFTY 50", "24,731.45", "+0.85%"],
                    ["SENSEX", "81,214.85", "+0.78%"],
                    ["BANK NIFTY", "54,372.15", "+1.15%"],
                    ["INDIA VIX", "12.45", "-2.35%"],
                ].map(([label, value, note]) => (
                    <Grid key={label} size={{ xs: 12, sm: 6, xl: 3 }}>
                        <MetricCard label={label} value={value} note={note} />
                    </Grid>
                ))}
            </Grid>
            <Grid container spacing={2}>
                <Grid size={{ xs: 12, lg: 8 }}>
                    <Card><CardContent>
                        <Typography variant="h6" sx={{ mb: 2 }}>Top market movers</Typography>
                        <StockTable />
                    </CardContent></Card>
                </Grid>
                <Grid size={{ xs: 12, lg: 4 }}>
                    <Card><CardContent>
                        <Typography variant="h6">Sector performance</Typography>
                        {["Nifty IT", "Nifty Bank", "Nifty FMCG", "Nifty Auto"].map((sector, i) => (
                            <Stack key={sector} spacing={0.75} sx={{ mt: 2 }}>
                                <Typography variant="body2">{sector}</Typography>
                                <LinearProgress variant="determinate" value={[78, 67, 55, 42][i]} />
                            </Stack>
                        ))}
                    </CardContent></Card>
                </Grid>
            </Grid>
        </Stack>
    );
}

export function MarketBreadthPage() {
    return (
        <Stack spacing={2.5}>
            <PageTitle title="Market Breadth" subtitle="Participation across advancing, declining and unchanged stocks." />
            <Grid container spacing={2}>
                <Grid size={{ xs: 12, md: 4 }}><MetricCard label="Advancing" value="1,682" note="62% of tracked stocks" /></Grid>
                <Grid size={{ xs: 12, md: 4 }}><MetricCard label="Declining" value="802" note="33% of tracked stocks" /></Grid>
                <Grid size={{ xs: 12, md: 4 }}><MetricCard label="Unchanged" value="126" note="5% of tracked stocks" /></Grid>
            </Grid>
            <Card><CardContent>
                <Typography variant="h6" sx={{ mb: 2 }}>Sector breadth</Typography>
                {["Nifty IT", "Nifty Bank", "Nifty FMCG", "Nifty Auto", "Nifty Metal", "Nifty Pharma"].map((sector, i) => (
                    <Stack key={sector} direction="row" spacing={2} sx={{ mb: 2, alignItems: "center" }}>
                        <Typography sx={{ width: 110 }}>{sector}</Typography>
                        <LinearProgress variant="determinate" value={[80, 70, 62, 38, 31, 57][i]} sx={{ flex: 1 }} />
                        <Typography color="text.secondary">{[8, 7, 6, 4, 3, 6][i]} / 10</Typography>
                    </Stack>
                ))}
            </CardContent></Card>
        </Stack>
    );
}

export function NewsInsightsPage() {
    return (
        <Stack spacing={2.5}>
            <PageTitle title="News & AI Insight" subtitle="Explainable market context. Not investment advice." />
            <Grid container spacing={2}>
                <Grid size={{ xs: 12, lg: 8 }}>
                    <Card><CardContent>
                        <Stack direction="row" spacing={1} sx={{ alignItems: "center" }}>
                            <InsightsOutlinedIcon color="primary" />
                            <Typography variant="h6">Market outlook</Typography>
                        </Stack>
                        <Typography color="success.main" variant="h5" sx={{ my: 2 }}>Strong bullish momentum</Typography>
                        <Typography color="text.secondary">
                            Major indices remain above key moving averages with broad participation.
                            Conditions can change quickly; review risk before acting.
                        </Typography>
                        <Typography variant="h6" sx={{ mt: 3, mb: 1 }}>Factors observed</Typography>
                        {["Price above major moving averages", "Positive advance-decline breadth", "Volume above recent average", "Momentum remains positive"].map((item) => (
                            <Typography key={item} sx={{ py: 0.5 }}>• {item}</Typography>
                        ))}
                    </CardContent></Card>
                </Grid>
                <Grid size={{ xs: 12, lg: 4 }}>
                    <Card><CardContent sx={{ textAlign: "center" }}>
                        <Typography variant="h6">AI confidence</Typography>
                        <Typography variant="h2" color="primary.main" sx={{ my: 3 }}>82%</Typography>
                        <LinearProgress variant="determinate" value={82} />
                        <Typography color="text.secondary" sx={{ mt: 2 }}>Model estimate, not a guarantee.</Typography>
                    </CardContent></Card>
                </Grid>
            </Grid>
        </Stack>
    );
}

export function EconomicCalendarPage() {
    const events = [
        ["26 Jul", "10:00", "RBI policy commentary", "High"],
        ["29 Jul", "17:30", "India infrastructure output", "Medium"],
        ["31 Jul", "20:00", "US Federal Reserve decision", "High"],
        ["01 Aug", "10:30", "India manufacturing PMI", "Medium"],
    ];
    return (
        <Stack spacing={2.5}>
            <PageTitle title="Economic Calendar" subtitle="Events that may affect Indian markets." />
            <Card><CardContent>
                <Stack direction="row" spacing={1} sx={{ mb: 2, alignItems: "center" }}>
                    <CalendarMonthOutlinedIcon color="primary" /><Typography variant="h6">Upcoming events</Typography>
                </Stack>
                <Table><TableHead><TableRow>
                    {["Date", "Time (IST)", "Event", "Impact"].map((x) => <TableCell key={x}>{x}</TableCell>)}
                </TableRow></TableHead><TableBody>
                    {events.map((row) => <TableRow key={row[2]}>{row.map((x, i) => (
                        <TableCell key={x}>{i === 3 ? <Chip size="small" label={x} color={x === "High" ? "error" : "warning"} /> : x}</TableCell>
                    ))}</TableRow>)}
                </TableBody></Table>
            </CardContent></Card>
        </Stack>
    );
}

export function OptionChainPage() {
    const strikes = [2850, 2900, 2950, 3000, 3050];
    return (
        <Stack spacing={2.5}>
            <PageTitle title="Option Chain" subtitle="Research view of calls and puts. No order placement." />
            <Stack direction={{ xs: "column", sm: "row" }} spacing={2}>
                <TextField select label="Underlying" defaultValue="RELIANCE" sx={{ minWidth: 180 }}>
                    <MenuItem value="RELIANCE">RELIANCE</MenuItem><MenuItem value="NIFTY">NIFTY</MenuItem>
                </TextField>
                <TextField select label="Expiry" defaultValue="30 Jul 2026" sx={{ minWidth: 180 }}>
                    <MenuItem value="30 Jul 2026">30 Jul 2026</MenuItem>
                </TextField>
            </Stack>
            <Card><CardContent>
                <Table><TableHead><TableRow>
                    {["Call OI", "Call change", "Call LTP", "Strike", "Put LTP", "Put change", "Put OI"].map((x) => <TableCell key={x}>{x}</TableCell>)}
                </TableRow></TableHead><TableBody>
                    {strikes.map((strike, i) => <TableRow key={strike}>
                        <TableCell>{(12496 + i * 1300).toLocaleString()}</TableCell>
                        <TableCell sx={{ color: "success.main" }}>+{1.2 + i * 0.3}%</TableCell>
                        <TableCell>{(129 - i * 18).toFixed(2)}</TableCell>
                        <TableCell sx={{ fontWeight: 800 }}>{strike}</TableCell>
                        <TableCell>{(28 + i * 20).toFixed(2)}</TableCell>
                        <TableCell sx={{ color: "error.main" }}>-{(0.8 + i * 0.2).toFixed(1)}%</TableCell>
                        <TableCell>{(8905 + i * 700).toLocaleString()}</TableCell>
                    </TableRow>)}
                </TableBody></Table>
            </CardContent></Card>
        </Stack>
    );
}

export function AlertsPage() {
    const [created, setCreated] = useState(false);
    return (
        <Stack spacing={2.5}>
            <PageTitle title="Alerts" subtitle="Research notifications for user-defined market conditions." />
            <Button startIcon={<AddAlertOutlinedIcon />} variant="contained" onClick={() => setCreated(true)} sx={{ alignSelf: "flex-start" }}>
                Create alert
            </Button>
            {created && <Chip color="success" label="Demo alert created locally" sx={{ alignSelf: "flex-start" }} />}
            <Card><CardContent><StockTable /></CardContent></Card>
        </Stack>
    );
}

export function CalculatorsPage() {
    const [capital, setCapital] = useState(100000);
    const [risk, setRisk] = useState(1);
    const [stop, setStop] = useState(2);
    const [activeCalculator, setActiveCalculator] = useState(0);
    const [calculatorValues, setCalculatorValues] = useState<Record<string, number>>({
        entry: 100,
        invalidation: 95,
        target: 115,
        monthly: 5000,
        rate: 12,
        years: 10,
        buy: 100,
        sell: 120,
        tradeQuantity: 10,
        firstPrice: 100,
        firstQuantity: 10,
        secondPrice: 90,
        secondQuantity: 10,
        high: 120,
        low: 80,
    });
    const quantity = useMemo(() => Math.floor((capital * risk / 100) / (stop || 1)), [capital, risk, stop]);
    function calculatorField(key: string, label: string) {
        return (
            <TextField
                key={key}
                label={label}
                type="number"
                value={calculatorValues[key]}
                onChange={(event) => setCalculatorValues((current) => ({
                    ...current,
                    [key]: Number(event.target.value),
                }))}
            />
        );
    }
    const riskDistance = Math.abs(calculatorValues.entry - calculatorValues.invalidation);
    const rewardDistance = Math.abs(calculatorValues.target - calculatorValues.entry);
    const monthlyRate = calculatorValues.rate / 1200;
    const months = Math.max(0, calculatorValues.years * 12);
    const sipValue = monthlyRate === 0
        ? calculatorValues.monthly * months
        : calculatorValues.monthly
            * (((1 + monthlyRate) ** months - 1) / monthlyRate)
            * (1 + monthlyRate);
    const totalAverageQuantity = calculatorValues.firstQuantity + calculatorValues.secondQuantity;
    const weightedAverage = totalAverageQuantity === 0
        ? 0
        : (
            calculatorValues.firstPrice * calculatorValues.firstQuantity
            + calculatorValues.secondPrice * calculatorValues.secondQuantity
        ) / totalAverageQuantity;
    const fibonacciRange = calculatorValues.high - calculatorValues.low;
    return (
        <Stack spacing={2.5}>
            <PageTitle title="Trading Calculators" subtitle="Planning tools for research and risk awareness." />
            <Grid container spacing={2}>
                <Grid size={{ xs: 12, lg: 6 }}>
                    <Card><CardContent>
                        <Stack direction="row" spacing={1} sx={{ mb: 3, alignItems: "center" }}>
                            <CalculateOutlinedIcon color="primary" /><Typography variant="h6">Position size calculator</Typography>
                        </Stack>
                        <Stack spacing={2}>
                            <TextField label="Capital (₹)" type="number" value={capital} onChange={(e) => setCapital(Number(e.target.value))} />
                            <TextField label="Risk per idea (%)" type="number" value={risk} onChange={(e) => setRisk(Number(e.target.value))} />
                            <TextField label="Stop distance (₹)" type="number" value={stop} onChange={(e) => setStop(Number(e.target.value))} />
                            <Typography variant="h5">Illustrative quantity: {quantity}</Typography>
                            <Typography color="text.secondary">This is a mathematical estimate, not a recommendation.</Typography>
                        </Stack>
                    </CardContent></Card>
                </Grid>
                <Grid size={{ xs: 12, lg: 6 }}>
                    <Card><CardContent>
                        <Typography variant="h6" sx={{ mb: 2 }}>Available tools</Typography>
                        {["Risk–reward calculator", "SIP calculator", "Profit calculator", "Average price calculator", "Fibonacci levels"].map((x, index) => (
                            <Button
                                key={x}
                                fullWidth
                                variant={activeCalculator === index ? "contained" : "outlined"}
                                onClick={() => setActiveCalculator(index)}
                                sx={{ mb: 1, justifyContent: "flex-start" }}
                            >
                                {x}
                            </Button>
                        ))}
                        <Stack spacing={1.5} sx={{ mt: 2, pt: 2, borderTop: "1px solid", borderColor: "divider" }}>
                            {activeCalculator === 0 && <>
                                {calculatorField("entry", "Entry price")}
                                {calculatorField("invalidation", "Invalidation price")}
                                {calculatorField("target", "Target scenario")}
                                <Typography variant="h5">
                                    Risk/reward: 1 : {riskDistance === 0 ? "—" : (rewardDistance / riskDistance).toFixed(2)}
                                </Typography>
                            </>}
                            {activeCalculator === 1 && <>
                                {calculatorField("monthly", "Monthly contribution (₹)")}
                                {calculatorField("rate", "Illustrative annual rate (%)")}
                                {calculatorField("years", "Years")}
                                <Typography variant="h5">
                                    Illustrative value: ₹{Math.round(sipValue).toLocaleString("en-IN")}
                                </Typography>
                            </>}
                            {activeCalculator === 2 && <>
                                {calculatorField("buy", "Buy price")}
                                {calculatorField("sell", "Sell price")}
                                {calculatorField("tradeQuantity", "Quantity")}
                                <Typography variant="h5">
                                    Gross result: ₹{((calculatorValues.sell - calculatorValues.buy) * calculatorValues.tradeQuantity).toLocaleString("en-IN")}
                                </Typography>
                            </>}
                            {activeCalculator === 3 && <>
                                {calculatorField("firstPrice", "First price")}
                                {calculatorField("firstQuantity", "First quantity")}
                                {calculatorField("secondPrice", "Second price")}
                                {calculatorField("secondQuantity", "Second quantity")}
                                <Typography variant="h5">Weighted average: ₹{weightedAverage.toFixed(2)}</Typography>
                            </>}
                            {activeCalculator === 4 && <>
                                {calculatorField("high", "Range high")}
                                {calculatorField("low", "Range low")}
                                {[23.6, 38.2, 50, 61.8, 78.6].map((level) => (
                                    <Typography key={level}>
                                        {level}%: {(calculatorValues.high - fibonacciRange * level / 100).toFixed(2)}
                                    </Typography>
                                ))}
                            </>}
                            <Typography variant="caption" color="text.secondary">
                                Mathematical illustration only. Fees, taxes and slippage may change results.
                            </Typography>
                        </Stack>
                    </CardContent></Card>
                </Grid>
            </Grid>
        </Stack>
    );
}

export function ResearchSignalsPage() {
    return (
        <Stack spacing={2.5}>
            <PageTitle title="AI Trading Signals" subtitle="Explainable research setups. No broker orders or guaranteed outcomes." />
            <Grid container spacing={2}>
                {stocks.slice(0, 4).map(([symbol, price, , view], index) => (
                    <Grid key={symbol} size={{ xs: 12, lg: 6 }}>
                        <Card><CardContent>
                            <Stack direction="row" sx={{ justifyContent: "space-between" }}>
                                <Typography variant="h6">{symbol}</Typography>
                                <Chip label={view} color={view === "Bullish Setup" ? "success" : "default"} />
                            </Stack>
                            <Typography variant="h5" sx={{ my: 1 }}>₹{price}</Typography>
                            <Typography color="text.secondary">Conditions matched: price trend, momentum and volume.</Typography>
                            <Grid container spacing={1.5} sx={{ mt: 1 }}>
                                <Grid size={4}><Typography variant="body2">Possible entry<br />₹{[2965, 3570, 1645, 1500][index]}</Typography></Grid>
                                <Grid size={4}><Typography variant="body2">Invalidation<br />₹{[2890, 3480, 1590, 1450][index]}</Typography></Grid>
                                <Grid size={4}><Typography variant="body2">Confidence<br />{[82, 62, 79, 65][index]}%</Typography></Grid>
                            </Grid>
                        </CardContent></Card>
                    </Grid>
                ))}
            </Grid>
        </Stack>
    );
}

export function PortfolioPage() {
    return (
        <Stack spacing={2.5}>
            <PageTitle title="My Portfolio" subtitle="Track manually entered holdings and research performance." />
            <Grid container spacing={2}>
                <Grid size={{ xs: 12, md: 4 }}><MetricCard label="Illustrative value" value="₹12,45,300" note="+1.53% today" /></Grid>
                <Grid size={{ xs: 12, md: 4 }}><MetricCard label="Overall P&L" value="+₹1,25,320" note="+11.22%" /></Grid>
                <Grid size={{ xs: 12, md: 4 }}><MetricCard label="Holdings" value="18" note="Diversification review available" /></Grid>
            </Grid>
            <Card><CardContent><StockTable /></CardContent></Card>
        </Stack>
    );
}

export function BacktestingPage() {
    const [ran, setRan] = useState(false);
    return (
        <Stack spacing={2.5}>
            <PageTitle title="Backtesting Engine" subtitle="Test rule-based strategies on historical data. Past results do not predict future performance." />
            <Grid container spacing={2}>
                <Grid size={{ xs: 12, lg: 4 }}>
                    <Card><CardContent><Stack spacing={2}>
                        <TextField select label="Strategy" defaultValue="Trend following"><MenuItem value="Trend following">Trend following</MenuItem><MenuItem value="Breakout">Breakout with volume</MenuItem></TextField>
                        <TextField select label="Period" defaultValue="1 year"><MenuItem value="1 year">1 year</MenuItem><MenuItem value="3 years">3 years</MenuItem></TextField>
                        <Button variant="contained" onClick={() => setRan(true)}>Run backtest</Button>
                    </Stack></CardContent></Card>
                </Grid>
                <Grid size={{ xs: 12, lg: 8 }}>
                    <Card><CardContent>
                        <Typography variant="h6">Backtest results</Typography>
                        {ran ? (
                            <Grid container spacing={2} sx={{ mt: 1 }}>
                                <Grid size={3}><MetricCard label="Return" value="+28.45%" note="Historical" /></Grid>
                                <Grid size={3}><MetricCard label="Max drawdown" value="-12.35%" note="Historical" /></Grid>
                                <Grid size={3}><MetricCard label="Win rate" value="68.75%" note="156 trades" /></Grid>
                                <Grid size={3}><MetricCard label="Profit factor" value="1.85" note="Before costs" /></Grid>
                            </Grid>
                        ) : <Typography color="text.secondary" sx={{ mt: 3 }}>Choose settings and run the test.</Typography>}
                    </CardContent></Card>
                </Grid>
            </Grid>
        </Stack>
    );
}

export function RiskManagementPage() {
    return (
        <Stack spacing={2.5}>
            <PageTitle title="Risk Management" subtitle="Monitor limits before considering any market idea." />
            <Grid container spacing={2}>
                {[
                    ["Account risk", "1.25%", "Within 2% limit"],
                    ["Maximum drawdown", "8.50%", "Monitor closely"],
                    ["Risk–reward", "1 : 2.35", "Illustrative"],
                    ["Total exposure", "68.25%", "Within set limit"],
                ].map(([label, value, note]) => (
                    <Grid key={label} size={{ xs: 12, sm: 6 }}>
                        <MetricCard label={label} value={value} note={note} />
                    </Grid>
                ))}
            </Grid>
            <Card><CardContent>
                <Typography variant="h6" sx={{ mb: 2 }}>Safety checks</Typography>
                {["Position stays within chosen account risk", "Invalidation level is defined", "No guaranteed-return assumption", "Liquidity and market conditions reviewed"].map((x) => (
                    <Typography key={x} sx={{ py: 0.75 }}>✓ {x}</Typography>
                ))}
            </CardContent></Card>
        </Stack>
    );
}
