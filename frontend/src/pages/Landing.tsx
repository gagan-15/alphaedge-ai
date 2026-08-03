import AutoGraphRoundedIcon from "@mui/icons-material/AutoGraphRounded";
import BoltRoundedIcon from "@mui/icons-material/BoltRounded";
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

import BrandLogo from "../components/brand/BrandLogo";

const featureCards = [
    [GridViewRoundedIcon, "Market Scanner", "Filter Indian equities with transparent technical and risk conditions."],
    [AutoGraphRoundedIcon, "Supply & Demand Zones", "Review zone boundaries, quality, freshness, distance and timeframe."],
    [InsightsRoundedIcon, "Explainable Insights", "Understand why a setup appears instead of receiving a black-box promise."],
    [NotificationsActiveRoundedIcon, "Research Alerts", "Track conditions and price levels without placing broker orders."],
] as const;

// Marketing-page examples only. Production dashboards never consume this data.
const previewRows = [
    ["RELIANCE", "Demand", "Fresh", "2,940–2,967", "89", "+0.83%"],
    ["HDFCBANK", "Demand", "Tested", "1,628–1,654", "84", "+1.12%"],
    ["TCS", "Supply", "Watch", "3,560–3,585", "78", "-0.41%"],
    ["INFY", "Demand", "Fresh", "1,490–1,512", "87", "+0.35%"],
];

const workflow = [
    ["1", "Scan", "Apply clear filters across the research universe."],
    ["2", "Validate", "Compare trend, momentum, volume and zone quality."],
    ["3", "Plan risk", "Define invalidation and exposure before acting."],
    ["4", "Monitor", "Save the idea and receive research alerts."],
];

function SectionTitle({ eyebrow, title, text }: { eyebrow: string; title: string; text: string }) {
    return (
        <Box sx={{ textAlign: "center", maxWidth: 680, mx: "auto", mb: 5 }}>
            <Typography sx={{ color: "#8b8cff", fontSize: ".68rem", fontWeight: 850, letterSpacing: ".16em" }}>
                {eyebrow}
            </Typography>
            <Typography sx={{ mt: 1, fontSize: { xs: "1.7rem", md: "2.25rem" }, fontWeight: 850, letterSpacing: "-.045em" }}>
                {title}
            </Typography>
            <Typography color="text.secondary" sx={{ mt: 1.25, lineHeight: 1.75 }}>
                {text}
            </Typography>
        </Box>
    );
}

function Landing() {
    return (
        <Box sx={{ minHeight: "100vh", bgcolor: "#07071a", color: "text.primary", overflow: "hidden" }}>
            <Box
                component="header"
                sx={{
                    position: "sticky",
                    top: 0,
                    zIndex: 10,
                    borderBottom: "1px solid rgba(129,140,248,.12)",
                    bgcolor: "rgba(7,7,26,.82)",
                    backdropFilter: "blur(18px)",
                }}
            >
                <Box sx={{ width: "min(1180px, calc(100% - 32px))", mx: "auto", height: 68, display: "flex", alignItems: "center" }}>
                    <BrandLogo />
                    <Stack direction="row" spacing={3} sx={{ ml: "auto", mr: 3, display: { xs: "none", md: "flex" } }}>
                        {["Platform", "Features", "How it works", "Safety"].map((label) => (
                            <Typography
                                key={label}
                                component="a"
                                href={`#${label.toLowerCase().replaceAll(" ", "-")}`}
                                color="text.secondary"
                                sx={{ textDecoration: "none", fontSize: ".76rem", "&:hover": { color: "white" } }}
                            >
                                {label}
                            </Typography>
                        ))}
                    </Stack>
                    <Button component={RouterLink} to="/login" variant="outlined" size="small">Log in</Button>
                </Box>
            </Box>

            <Box
                component="main"
                sx={{
                    background:
                        "radial-gradient(circle at 50% 4%,rgba(91,55,210,.26),transparent 27%), radial-gradient(circle at 85% 32%,rgba(37,99,235,.11),transparent 25%)",
                }}
            >
                <Box component="section" sx={{ width: "min(1040px, calc(100% - 32px))", mx: "auto", pt: { xs: 9, md: 13 }, pb: 10, textAlign: "center" }}>
                    <Chip label="FREE LOCAL RESEARCH MODE · NO PAYMENT REQUIRED" size="small" color="success" variant="outlined" />
                    <Typography
                        component="h1"
                        sx={{
                            maxWidth: 850,
                            mx: "auto",
                            mt: 3,
                            fontSize: { xs: "2.4rem", sm: "3.4rem", md: "4.25rem" },
                            fontWeight: 900,
                            lineHeight: 1.02,
                            letterSpacing: "-.06em",
                        }}
                    >
                        Indian market intelligence,{" "}
                        <Box component="span" sx={{ background: "linear-gradient(90deg,#60a5fa,#a855f7)", backgroundClip: "text", color: "transparent" }}>
                            explained clearly.
                        </Box>
                    </Typography>
                    <Typography color="text.secondary" sx={{ maxWidth: 700, mx: "auto", mt: 2.5, fontSize: { xs: ".9rem", md: "1.05rem" }, lineHeight: 1.75 }}>
                        Scan equities, study supply and demand zones, validate strategies and manage risk.
                        AlphaEdge supports research decisions—it does not promise returns or execute trades.
                    </Typography>
                    <Stack direction={{ xs: "column", sm: "row" }} spacing={1.5} sx={{ mt: 4, justifyContent: "center" }}>
                        <Button component={RouterLink} to="/login" variant="contained" size="large" endIcon={<BoltRoundedIcon />}>
                            Open Free Local Demo
                        </Button>
                        <Button component="a" href="#platform" variant="outlined" size="large">Explore the platform</Button>
                    </Stack>
                    <Typography color="success.main" sx={{ mt: 2, fontSize: ".68rem" }}>
                        No card · No broker connection · Delayed data is labelled
                    </Typography>
                </Box>

                <Box id="platform" component="section" sx={{ width: "min(1120px, calc(100% - 32px))", mx: "auto", pb: 13 }}>
                    <SectionTitle eyebrow="THE RESEARCH WORKSPACE" title="Every setup. Every reason. One view." text="A dense but readable workspace for reviewing market context, zone quality and risk." />
                    <Card sx={{ p: { xs: 1.5, md: 2.5 }, borderColor: "rgba(99,102,241,.32)", boxShadow: "0 30px 90px rgba(0,0,0,.38)" }}>
                        <Box sx={{ display: "flex", gap: 1, mb: 2 }}>
                            {["#ff5c67", "#f5b942", "#35d07f"].map((color) => <Box key={color} sx={{ width: 8, height: 8, borderRadius: "50%", bgcolor: color }} />)}
                            <Typography color="text.secondary" sx={{ ml: 1, fontSize: ".66rem" }}>AlphaEdge zone intelligence preview</Typography>
                        </Box>
                        <Box sx={{ overflowX: "auto" }}>
                            <Box sx={{ minWidth: 720 }}>
                                <Box sx={{ display: "grid", gridTemplateColumns: "1.3fr repeat(5, 1fr)", p: 1.3, color: "text.secondary", fontSize: ".65rem", borderBottom: "1px solid", borderColor: "divider" }}>
                                    {["SYMBOL", "ZONE", "STATUS", "BOUNDARIES", "SCORE", "CHANGE"].map((cell) => <Box key={cell}>{cell}</Box>)}
                                </Box>
                                {previewRows.map((row) => (
                                    <Box key={row[0]} sx={{ display: "grid", gridTemplateColumns: "1.3fr repeat(5, 1fr)", p: 1.45, borderBottom: "1px solid rgba(29,43,64,.65)", fontSize: ".72rem", alignItems: "center" }}>
                                        {row.map((cell, index) => (
                                            <Box key={cell} sx={{ fontWeight: index === 0 ? 800 : 500, color: index === 5 ? (cell.startsWith("+") ? "success.main" : "error.main") : "inherit" }}>{cell}</Box>
                                        ))}
                                    </Box>
                                ))}
                            </Box>
                        </Box>
                    </Card>
                </Box>

                <Box id="features" component="section" sx={{ width: "min(1120px, calc(100% - 32px))", mx: "auto", pb: 13 }}>
                    <SectionTitle eyebrow="BUILT FOR DISCIPLINED RESEARCH" title="Everything important, in one place." text="The platform connects discovery, explanation, validation and monitoring." />
                    <Box sx={{ display: "grid", gridTemplateColumns: { xs: "1fr", sm: "repeat(2,1fr)", lg: "repeat(4,1fr)" }, gap: 2 }}>
                        {featureCards.map(([Icon, title, description]) => (
                            <Card key={title} sx={{ p: 2.5, minHeight: 190 }}>
                                <Box sx={{ width: 40, height: 40, display: "grid", placeItems: "center", borderRadius: 1.5, bgcolor: "rgba(99,102,241,.13)", color: "#9b8cff" }}><Icon /></Box>
                                <Typography sx={{ mt: 2.5, fontWeight: 850 }}>{title}</Typography>
                                <Typography color="text.secondary" sx={{ mt: 1, fontSize: ".74rem", lineHeight: 1.7 }}>{description}</Typography>
                            </Card>
                        ))}
                    </Box>
                </Box>

                <Box id="how-it-works" component="section" sx={{ width: "min(1040px, calc(100% - 32px))", mx: "auto", pb: 13 }}>
                    <SectionTitle eyebrow="A CLEAR PROCESS" title="From scan to monitored idea." text="A repeatable workflow helps reduce impulsive decisions and hidden assumptions." />
                    <Box sx={{ display: "grid", gridTemplateColumns: { xs: "1fr", md: "repeat(4,1fr)" }, gap: 2 }}>
                        {workflow.map(([number, title, text]) => (
                            <Box key={number} sx={{ textAlign: "center", px: 2 }}>
                                <Box sx={{ width: 36, height: 36, mx: "auto", display: "grid", placeItems: "center", borderRadius: "50%", background: "linear-gradient(145deg,#2563eb,#8b5cf6)", fontWeight: 850 }}>{number}</Box>
                                <Typography sx={{ mt: 2, fontWeight: 850 }}>{title}</Typography>
                                <Typography color="text.secondary" sx={{ mt: .8, fontSize: ".7rem", lineHeight: 1.65 }}>{text}</Typography>
                            </Box>
                        ))}
                    </Box>
                </Box>

                <Box id="safety" component="section" sx={{ width: "min(940px, calc(100% - 32px))", mx: "auto", pb: 13 }}>
                    <Card sx={{ p: { xs: 3, md: 5 }, display: "grid", gridTemplateColumns: { xs: "1fr", md: "auto 1fr auto" }, alignItems: "center", gap: 3, borderColor: "rgba(74,222,128,.2)" }}>
                        <Box sx={{ width: 54, height: 54, display: "grid", placeItems: "center", borderRadius: 2, bgcolor: "rgba(74,222,128,.09)", color: "success.main" }}><SecurityRoundedIcon fontSize="large" /></Box>
                        <Box>
                            <Typography sx={{ fontSize: "1.2rem", fontWeight: 850 }}>Research assistance, not guaranteed advice.</Typography>
                            <Typography color="text.secondary" sx={{ mt: 1, lineHeight: 1.7 }}>
                                No broker execution, no guaranteed returns and no hidden “sure-shot” claims.
                                Users keep control of every decision.
                            </Typography>
                        </Box>
                        <Button component={RouterLink} to="/register" variant="outlined">Create account</Button>
                    </Card>
                </Box>

                <Box component="section" sx={{ textAlign: "center", width: "min(800px, calc(100% - 32px))", mx: "auto", pb: 12 }}>
                    <Typography sx={{ fontSize: { xs: "1.8rem", md: "2.5rem" }, fontWeight: 900, letterSpacing: "-.045em" }}>Ready to explore AlphaEdge AI?</Typography>
                    <Typography color="text.secondary" sx={{ mt: 1.5 }}>Start with free local demo data. Add licensed providers only when the product is ready.</Typography>
                    <Button component={RouterLink} to="/login" variant="contained" size="large" sx={{ mt: 3 }}>Open the workspace</Button>
                </Box>
            </Box>

            <Box component="footer" sx={{ borderTop: "1px solid rgba(129,140,248,.12)", py: 3 }}>
                <Box sx={{ width: "min(1180px, calc(100% - 32px))", mx: "auto", display: "flex", flexWrap: "wrap", gap: 2, justifyContent: "space-between" }}>
                    <BrandLogo />
                    <Typography color="text.secondary" sx={{ fontSize: ".67rem" }}>
                        Educational and analytical purposes only · Market risk applies · © 2026 AlphaEdge AI
                    </Typography>
                </Box>
            </Box>
        </Box>
    );
}

export default Landing;
