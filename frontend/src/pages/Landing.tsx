import AutoGraphRoundedIcon from "@mui/icons-material/AutoGraphRounded";
import ArrowForwardRoundedIcon from "@mui/icons-material/ArrowForwardRounded";
import GridViewRoundedIcon from "@mui/icons-material/GridViewRounded";
import InsightsRoundedIcon from "@mui/icons-material/InsightsRounded";
import NotificationsActiveRoundedIcon from "@mui/icons-material/NotificationsActiveRounded";
import SecurityRoundedIcon from "@mui/icons-material/SecurityRounded";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Card from "@mui/material/Card";
import Chip from "@mui/material/Chip";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { Link as RouterLink } from "react-router-dom";

import { useAuth } from "../auth/AuthState";
import BrandLogo from "../components/brand/BrandLogo";
import PublicHeader from "../components/public/PublicHeader";

const features = [
    [GridViewRoundedIcon, "Market Scanner", "Find clear setups with transparent filters and risk conditions."],
    [AutoGraphRoundedIcon, "Supply & Demand Zones", "Review zone boundaries, quality, freshness and distance."],
    [InsightsRoundedIcon, "Insights & Signals", "Understand why a setup appears and what it means for your research."],
    [NotificationsActiveRoundedIcon, "Research Alerts", "Track conditions and price levels without broker execution."],
] as const;

const workflow = [
    ["1", "Scan", "Apply intelligent filters to discover strong setups."],
    ["2", "Validate", "Compare trend, momentum, volume and zone quality."],
    ["3", "Plan", "Define risk, position size and invalidation."],
    ["4", "Monitor", "Track performance and important price levels."],
] as const;

const market = [
    ["NIFTY 50", "24,774.3", "+1.60%"],
    ["SENSEX", "78,639.03", "+0.70%"],
    ["BANK NIFTY", "58,247.95", "+1.72%"],
    ["INDIA VIX", "11.93", "+1.40%"],
] as const;

function Landing() {
    const { user } = useAuth();
    const workspacePath = user ? "/dashboard" : "/login";

    return (
        <Box sx={{ minHeight: "100vh", bgcolor: "#FBFCFF", color: "#101828" }}>
            <PublicHeader />
            <Box component="main">
                <Box
                    component="section"
                    sx={{
                        position: "relative",
                        overflow: "hidden",
                        pt: { xs: 7, md: 9 },
                        pb: 9,
                        textAlign: "center",
                        background: "radial-gradient(circle at 50% 8%, #EEF0FF 0, rgba(248,250,255,.7) 42%, #FBFCFF 76%)",
                    }}
                >
                    <Box sx={{ width: "min(1120px, calc(100% - 32px))", mx: "auto", position: "relative", zIndex: 1 }}>
                        <Chip label="AI-POWERED STOCK RESEARCH · BUILT FOR INDIAN MARKETS" variant="outlined" size="small" sx={{ color: "#4338CA", borderColor: "#C7D2FE", bgcolor: "#F5F6FF", fontWeight: 700, letterSpacing: ".08em" }} />
                        <Typography component="h1" sx={{ maxWidth: 760, mx: "auto", mt: 2.5, fontSize: { xs: "2.45rem", md: "3.45rem" }, lineHeight: 1.05, fontWeight: 850, letterSpacing: "-.045em" }}>
                            Indian market intelligence,<br />
                            <Box component="span" sx={{ color: "#5B5CEB" }}>explained clearly.</Box>
                        </Typography>
                        <Typography sx={{ maxWidth: 700, mx: "auto", mt: 2, color: "#475467", lineHeight: 1.65 }}>
                            Find research opportunities with AI-assisted analysis, supply and demand zones,
                            and disciplined risk tools — all in one place.
                        </Typography>
                        <Stack direction={{ xs: "column", sm: "row" }} spacing={1.5} sx={{ mt: 3.5, justifyContent: "center" }}>
                            <Button component={RouterLink} to={workspacePath} variant="contained" size="large" endIcon={<ArrowForwardRoundedIcon />}>Explore the platform</Button>
                            <Button component="a" href="#how-it-works" variant="outlined" size="large">See how it works</Button>
                        </Stack>
                    </Box>
                </Box>

                <Card sx={{ width: "min(910px, calc(100% - 32px))", mx: "auto", mt: -4.2, position: "relative", zIndex: 2, p: 1.5, borderColor: "#E3E8F0", boxShadow: "0 16px 45px rgba(16,24,40,.09)" }}>
                    <Box sx={{ display: "grid", gridTemplateColumns: { xs: "1fr 1fr", md: "1.2fr repeat(4,1fr)" }, alignItems: "center" }}>
                        <Box sx={{ p: 1.5 }}><Typography sx={{ fontWeight: 700 }}>Market snapshot</Typography><Typography color="text.secondary" sx={{ fontSize: ".72rem" }}>Delayed data</Typography></Box>
                        {market.map(([name, value, change]) => <Box key={name} sx={{ p: 1.5, borderLeft: "1px solid #E7EAF0" }}><Typography color="text.secondary" sx={{ fontSize: ".62rem", fontWeight: 650 }}>{name}</Typography><Typography sx={{ fontWeight: 750 }}>{value} <Box component="span" sx={{ ml: .5, color: "#15803D", fontSize: ".65rem" }}>▲ {change}</Box></Typography></Box>)}
                    </Box>
                </Card>

                <Box id="platform" component="section" sx={{ width: "min(1160px, calc(100% - 32px))", mx: "auto", pt: 9, pb: 8 }}>
                    <Box id="features" sx={{ scrollMarginTop: 80, textAlign: "center" }}>
                        <Typography sx={{ color: "#5B5CEB", fontSize: ".68rem", fontWeight: 800, letterSpacing: ".18em" }}>WHY ALPHAEDGE AI</Typography>
                        <Typography sx={{ mt: 1, fontSize: { xs: "1.75rem", md: "2.2rem" }, fontWeight: 800, letterSpacing: "-.035em" }}>Everything important, in one place.</Typography>
                        <Typography color="text.secondary">Powerful research tools to help you study the market with clarity and confidence.</Typography>
                    </Box>
                    <Box sx={{ display: "grid", gridTemplateColumns: { xs: "1fr", sm: "repeat(2,1fr)", lg: "repeat(4,1fr)" }, gap: 2, mt: 4 }}>
                        {features.map(([Icon, title, text]) => <Card key={title} sx={{ p: 2.5, minHeight: 180, borderColor: "#DDE3EE", boxShadow: "0 10px 28px rgba(16,24,40,.04)" }}><Box sx={{ width: 43, height: 43, display: "grid", placeItems: "center", borderRadius: "50%", bgcolor: "#F0EEFF", color: "#5B5CEB" }}><Icon /></Box><Typography sx={{ mt: 2, fontWeight: 750 }}>{title}</Typography><Typography color="text.secondary" sx={{ mt: .7, fontSize: ".76rem", lineHeight: 1.6 }}>{text}</Typography></Card>)}
                    </Box>
                </Box>

                <Box id="how-it-works" component="section" sx={{ scrollMarginTop: 80, width: "min(1040px, calc(100% - 32px))", mx: "auto", py: 8, textAlign: "center" }}>
                    <Typography sx={{ color: "#5B5CEB", fontSize: ".68rem", fontWeight: 800, letterSpacing: ".18em" }}>4 SIMPLE STEPS</Typography>
                    <Typography sx={{ mt: 1, fontSize: { xs: "1.75rem", md: "2.2rem" }, fontWeight: 800 }}>From scan to a monitored idea.</Typography>
                    <Typography color="text.secondary">A clear workflow that helps you make more disciplined research decisions.</Typography>
                    <Box sx={{ display: "grid", gridTemplateColumns: { xs: "1fr", sm: "repeat(2,1fr)", md: "repeat(4,1fr)" }, gap: 3, mt: 4 }}>
                        {workflow.map(([number, title, text]) => <Box key={number}><Box sx={{ width: 48, height: 48, mx: "auto", display: "grid", placeItems: "center", borderRadius: "50%", bgcolor: "#EEECFF", color: "#5B5CEB", fontWeight: 800, fontSize: "1.2rem" }}>{number}</Box><Typography sx={{ mt: 1.5, fontWeight: 750 }}>{title}</Typography><Typography color="text.secondary" sx={{ mt: .5, fontSize: ".74rem", lineHeight: 1.6 }}>{text}</Typography></Box>)}
                    </Box>
                </Box>

                <Box id="safety" component="section" sx={{ scrollMarginTop: 80, width: "min(900px, calc(100% - 32px))", mx: "auto", py: 7 }}>
                    <Card sx={{ p: 3, display: "grid", gridTemplateColumns: { xs: "1fr", sm: "auto 1fr auto" }, alignItems: "center", gap: 2.5, bgcolor: "#F0FBF8", borderColor: "#BFE8DD" }}><Box sx={{ width: 52, height: 52, display: "grid", placeItems: "center", borderRadius: "50%", bgcolor: "#DDF6EE", color: "#14866D" }}><SecurityRoundedIcon /></Box><Box><Typography sx={{ fontWeight: 750 }}>Research assistance, not guaranteed advice.</Typography><Typography color="text.secondary" sx={{ mt: .4, fontSize: ".78rem" }}>AlphaEdge supports self-study and research. It does not execute trades or promise returns.</Typography></Box><Button component={RouterLink} to="/register" variant="outlined">Learn more</Button></Card>
                </Box>

                <Box sx={{ width: "min(900px, calc(100% - 32px))", mx: "auto", pb: 8, textAlign: "center" }}><Card sx={{ p: 4, bgcolor: "#F4F3FF", borderColor: "#DCD8FF" }}><Typography sx={{ fontSize: "1.7rem", fontWeight: 800 }}>Ready to explore AlphaEdge AI?</Typography><Typography color="text.secondary" sx={{ mt: .5 }}>Open the research workspace and explore the platform safely.</Typography><Button component={RouterLink} to={workspacePath} variant="contained" endIcon={<ArrowForwardRoundedIcon />} sx={{ mt: 2.5 }}>Open the workspace</Button></Card></Box>
            </Box>
            <Box component="footer" sx={{ borderTop: "1px solid #E7EAF0", py: 2.5, bgcolor: "white" }}><Box sx={{ width: "min(1160px, calc(100% - 32px))", mx: "auto", display: "flex", flexWrap: "wrap", gap: 2, alignItems: "center", justifyContent: "space-between" }}><BrandLogo /><Typography color="text.secondary" sx={{ fontSize: ".68rem" }}>Educational and analytical purposes only · Market risk applies · © 2026 AlphaEdge AI</Typography></Box></Box>
        </Box>
    );
}

export default Landing;
