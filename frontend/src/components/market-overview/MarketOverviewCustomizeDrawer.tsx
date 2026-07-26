import { useMemo, useState } from "react";

import CloseRoundedIcon from "@mui/icons-material/CloseRounded";
import RestartAltRoundedIcon from "@mui/icons-material/RestartAltRounded";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Dialog from "@mui/material/Dialog";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";
import DialogTitle from "@mui/material/DialogTitle";
import Divider from "@mui/material/Divider";
import Drawer from "@mui/material/Drawer";
import FormControlLabel from "@mui/material/FormControlLabel";
import IconButton from "@mui/material/IconButton";
import Radio from "@mui/material/Radio";
import RadioGroup from "@mui/material/RadioGroup";
import Stack from "@mui/material/Stack";
import Switch from "@mui/material/Switch";
import Typography from "@mui/material/Typography";

import {
    defaultMarketOverviewPreferences,
    marketOverviewWidgetKeys,
    preferencesForPreset,
    type DashboardPreset,
    type MarketOverviewPreferences,
    type MarketOverviewWidgetKey,
} from "./marketOverviewPreferences";

const widgetLabels: Record<MarketOverviewWidgetKey, [string, string]> = {
    aiSummary: ["AI Market Summary", "A short explanation of today's market."],
    marketHealth: ["Market Health", "Shows whether the wider market supports today's move."],
    marketTrend: ["Market Trend", "Shows whether the market is rising, falling or moving sideways."],
    researchFocus: ["Today's Research Focus", "Suggests what type of ideas may be worth checking."],
    marketRisk: ["Market Risk", "Shows how careful you may need to be."],
    sectorRotation: ["Strong and Weak Sectors", "Shows which business sectors are improving or weakening."],
    marketBreadth: ["Stocks Going Up and Down", "Shows how many tracked stocks are rising or falling."],
    bigInvestorActivity: ["Big Investor Activity", "Shows buying and selling by large investor groups."],
    marketVolatility: ["Market Volatility", "Shows expected market price swings."],
    marketSentiment: ["Market Mood", "Shows whether traders feel fearful or confident."],
    aiOpportunities: ["Ideas to Research", "Shows groups of stocks that may deserve a closer look."],
    smartAlerts: ["Important Market Changes", "Shows recent changes that may need attention."],
    todayVerdict: ["Today's Verdict", "Shows the final simple market summary."],
};

const presets: Array<[DashboardPreset, string, string]> = [
    ["beginner", "Beginner", "Shows the complete dashboard with simple explanations."],
    ["swing", "Swing Trader", "Focuses on ideas that may last several days or weeks."],
    ["intraday", "Intraday Trader", "Focuses on today's market movement and risk."],
    ["longTerm", "Long-term Investor", "Focuses on wider trends and large investor activity."],
    ["custom", "Custom", "Uses the choices you make below."],
];

function Section({ title, text, children }: { title: string; text: string; children: React.ReactNode }) {
    return <Box><Typography sx={{ fontWeight: 900 }}>{title}</Typography><Typography color="text.secondary" sx={{ mt: .35, fontSize: ".68rem", lineHeight: 1.5 }}>{text}</Typography><Box sx={{ mt: 1.25 }}>{children}</Box></Box>;
}

function RadioLabel({ title, text }: { title: string; text: string }) {
    return <Box><Typography sx={{ fontSize: ".74rem", fontWeight: 800 }}>{title}</Typography><Typography color="text.secondary" sx={{ fontSize: ".6rem" }}>{text}</Typography></Box>;
}

interface Props {
    open: boolean;
    value: MarketOverviewPreferences;
    onClose: () => void;
    onPreview: (value: MarketOverviewPreferences) => void;
    onSave: (value: MarketOverviewPreferences) => void;
}

export default function MarketOverviewCustomizeDrawer({ open, value, onClose, onPreview, onSave }: Props) {
    const [draft, setDraft] = useState(value);
    const [warning, setWarning] = useState("");
    const [resetOpen, setResetOpen] = useState(false);
    const visibleCount = useMemo(() => Object.values(draft.visibleWidgets).filter(Boolean).length, [draft.visibleWidgets]);
    const dirty = useMemo(() => JSON.stringify(draft) !== JSON.stringify(value), [draft, value]);
    const analysisKeys: MarketOverviewWidgetKey[] = ["marketHealth", "marketTrend", "researchFocus", "marketRisk", "sectorRotation", "marketBreadth", "bigInvestorActivity", "marketVolatility", "marketSentiment", "aiOpportunities"];
    const preview = (next: MarketOverviewPreferences) => {
        setDraft(next);
        onPreview(next);
    };
    const update = (next: MarketOverviewPreferences) => preview({ ...next, preset: "custom" });
    const choosePreset = (preset: DashboardPreset) => {
        if (preset === "custom") update({ ...draft, preset: "custom" });
        else preview(preferencesForPreset(preset));
    };
    const toggleWidget = (key: MarketOverviewWidgetKey, checked: boolean) => {
        if (key === "aiSummary" && !checked) {
            setWarning("AI Market Summary must remain visible.");
            return;
        }
        if (!checked && visibleCount === 1 && draft.visibleWidgets[key]) {
            setWarning("Keep at least one widget visible.");
            return;
        }
        const nextVisibility = { ...draft.visibleWidgets, [key]: checked };
        if (!analysisKeys.some((analysisKey) => nextVisibility[analysisKey])) {
            setWarning("Keep at least one market analysis widget visible.");
            return;
        }
        setWarning("");
        update({ ...draft, visibleWidgets: nextVisibility });
    };
    const cancel = () => {
        onPreview(value);
        onClose();
    };
    return <Drawer anchor="right" open={open} onClose={cancel} slotProps={{ paper: { sx: { width: { xs: "94vw", sm: 440 }, bgcolor: "background.paper", backgroundImage: "none" } } }}>
        <Stack sx={{ height: "100%" }}>
            <Stack direction="row" sx={{ p: 2.5, alignItems: "center", justifyContent: "space-between", borderBottom: "1px solid", borderColor: "divider" }}>
                <Box><Typography variant="h5">Customize Market Overview</Typography><Typography color="text.secondary" sx={{ mt: .35, fontSize: ".68rem" }}>Choose what you want to see. Market data and calculations will not change.</Typography></Box>
                <IconButton aria-label="Close customization" onClick={cancel}><CloseRoundedIcon /></IconButton>
            </Stack>
            <Stack spacing={2.5} divider={<Divider flexItem />} sx={{ p: 2.5, overflowY: "auto", flex: 1 }}>
                <Section title="Dashboard Presets" text="Choose a ready-made view. You can change individual widgets afterwards.">
                    <Stack spacing={.7}>{presets.map(([key, label, text]) => <PresetButton key={key} label={label} text={text} selected={draft.preset === key} onClick={() => choosePreset(key)} />)}</Stack>
                </Section>
                <Section title="Visible Widgets" text={`${visibleCount} of ${marketOverviewWidgetKeys.length} widgets are visible.`}>
                    <Stack spacing={.3}>{marketOverviewWidgetKeys.map((key) => <FormControlLabel key={key} sx={{ m: 0, py: .4, alignItems: "flex-start" }} control={<Switch size="small" disabled={key === "aiSummary"} checked={draft.visibleWidgets[key]} onChange={(event) => toggleWidget(key, event.target.checked)} />} label={<RadioLabel title={widgetLabels[key][0]} text={key === "aiSummary" ? "This explanation always remains visible." : widgetLabels[key][1]} />} />)}</Stack>
                    {warning && <Typography color="warning.main" sx={{ mt: .7, fontSize: ".65rem" }}>{warning}</Typography>}
                </Section>
                <Section title="Default Timeframe" text="Choose the time period you want to see first when you return.">
                    <RadioGroup value={draft.defaultTimeframe} onChange={(event) => update({ ...draft, defaultTimeframe: event.target.value as MarketOverviewPreferences["defaultTimeframe"] })}>{[["1D", "One trading day"], ["1W", "The last trading week"], ["1M", "The last month"], ["3M", "The last three months"], ["6M", "The last six months"], ["1Y", "The last year"]].map(([item, text]) => <FormControlLabel key={item} value={item} control={<Radio size="small" />} label={<RadioLabel title={item} text={text} />} />)}</RadioGroup>
                </Section>
                <Section title="Market Universe" text="This decides which stocks are included in market calculations.">
                    <RadioGroup value={draft.marketUniverse} onChange={(event) => update({ ...draft, marketUniverse: event.target.value as MarketOverviewPreferences["marketUniverse"] })}>
                        {[["nseAll", "NSE All Stocks", "All supported stocks listed on NSE."], ["nifty500", "Nifty 500", "A broad group of large and mid-size Indian companies."], ["nifty200", "Nifty 200", "The 200 larger companies in the Nifty universe."], ["nifty100", "Nifty 100", "The 100 largest companies in the Nifty universe."], ["fo", "F&O Stocks", "Stocks available in the futures and options market."], ["watchlist", "My Watchlist", "Only stocks saved in your watchlist."], ["holdings", "My Holdings", "Only stocks saved in your local holdings."]].map(([key, title, text]) => <FormControlLabel key={key} value={key} control={<Radio size="small" />} label={<RadioLabel title={title} text={text} />} />)}
                    </RadioGroup>
                </Section>
                <Section title="Chart Preferences" text="Choose the extra information shown with market charts.">
                    <Stack>{[["showNifty", "Show Nifty comparison", "Compare the wider market with Nifty."], ["showBankNifty", "Show Bank Nifty comparison", "Compare the wider market with banking stocks."], ["showEvents", "Show important market events", "Mark important news dates on charts."], ["showAiExplanations", "Show AI explanations", "Show simple explanations below charts."], ["showTooltips", "Show tooltips", "Show more information when you point at a chart."]].map(([key, title, text]) => <FormControlLabel key={key} sx={{ m: 0, py: .3 }} control={<Switch size="small" checked={draft.chart[key as keyof typeof draft.chart]} onChange={(event) => update({ ...draft, chart: { ...draft.chart, [key]: event.target.checked } })} />} label={<RadioLabel title={title} text={text} />} />)}</Stack>
                </Section>
                <Section title="Language Mode" text="Choose how AlphaEdge explains the market.">
                    <RadioGroup value={draft.language} onChange={(event) => update({ ...draft, language: event.target.value as MarketOverviewPreferences["language"] })}>
                        <FormControlLabel value="simple" control={<Radio size="small" />} label={<RadioLabel title="Simple English (Recommended)" text="Explain the market in everyday language." />} />
                        <FormControlLabel value="professional" control={<Radio size="small" />} label={<RadioLabel title="Professional" text="Use common technical market terms." />} />
                    </RadioGroup>
                </Section>
                <Section title="Display Preferences" text="Choose how much space and number detail you prefer.">
                    <Typography sx={{ fontSize: ".68rem", fontWeight: 850 }}>Density</Typography>
                    <RadioGroup value={draft.density} onChange={(event) => update({ ...draft, density: event.target.value as MarketOverviewPreferences["density"] })}><FormControlLabel value="comfortable" control={<Radio size="small" />} label={<RadioLabel title="Comfortable" text="Use more space so cards are easier to read." />} /><FormControlLabel value="compact" control={<Radio size="small" />} label={<RadioLabel title="Compact" text="Fit more information on the screen." />} /></RadioGroup>
                    <Typography sx={{ mt: 1, fontSize: ".68rem", fontWeight: 850 }}>Number Format</Typography>
                    <RadioGroup value={draft.numberFormat} onChange={(event) => update({ ...draft, numberFormat: event.target.value as MarketOverviewPreferences["numberFormat"] })}><FormControlLabel value="full" control={<Radio size="small" />} label={<RadioLabel title="Full Numbers" text="Show complete values such as 1,250." />} /><FormControlLabel value="short" control={<Radio size="small" />} label={<RadioLabel title="Short Numbers (1.2K)" text="Shorten large values so they take less space." />} /></RadioGroup>
                </Section>
            </Stack>
            {dirty && <Typography color="warning.main" sx={{ px: 2.5, pt: 1, fontSize: ".66rem", fontWeight: 850 }}>Unsaved Changes</Typography>}
            <Stack direction="row" spacing={1} sx={{ p: 2, borderTop: "1px solid", borderColor: "divider" }}>
                <Button startIcon={<RestartAltRoundedIcon />} onClick={() => setResetOpen(true)}>Reset to Default</Button>
                <Button sx={{ ml: "auto" }} onClick={cancel}>Cancel</Button>
                <Button variant="contained" disabled={!dirty} onClick={() => onSave(draft)}>Save Dashboard</Button>
            </Stack>
        </Stack>
        <Dialog open={resetOpen} onClose={() => setResetOpen(false)}>
            <DialogTitle>Reset Market Overview?</DialogTitle>
            <DialogContent><Typography color="text.secondary">This will restore the AlphaEdge default choices in the preview. Click Save Dashboard if you want to keep them.</Typography></DialogContent>
            <DialogActions><Button onClick={() => setResetOpen(false)}>Keep My Choices</Button><Button color="warning" variant="contained" onClick={() => { preview(defaultMarketOverviewPreferences); setResetOpen(false); }}>Reset Preview</Button></DialogActions>
        </Dialog>
    </Drawer>;
}

function PresetButton({ label, text, selected, onClick }: { label: string; text: string; selected: boolean; onClick: () => void }) {
    return <Button onClick={onClick} variant={selected ? "contained" : "outlined"} sx={{ justifyContent: "flex-start", textAlign: "left", py: 1 }}>
        <Box><Typography sx={{ color: "inherit", fontSize: ".74rem", fontWeight: 850 }}>{label}</Typography><Typography sx={{ mt: .2, color: selected ? "rgba(255,255,255,.74)" : "text.secondary", fontSize: ".59rem", textTransform: "none" }}>{text}</Typography></Box>
    </Button>;
}
