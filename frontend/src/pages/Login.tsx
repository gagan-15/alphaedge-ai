import AutoGraphRoundedIcon from "@mui/icons-material/AutoGraphRounded";
import GridViewRoundedIcon from "@mui/icons-material/GridViewRounded";
import NotificationsActiveOutlinedIcon from "@mui/icons-material/NotificationsActiveOutlined";
import SecurityOutlinedIcon from "@mui/icons-material/SecurityOutlined";
import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Link from "@mui/material/Link";
import Stack from "@mui/material/Stack";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";
import { useEffect, useState } from "react";
import { Link as RouterLink, useNavigate } from "react-router-dom";

import { loginAccount } from "../api/authApi";
import { LOCAL_DEMO_MODE, useAuth } from "../auth/AuthState";
import BrandLogo from "../components/brand/BrandLogo";
import PublicHeader from "../components/public/PublicHeader";

const features = [
    [GridViewRoundedIcon, "Market Scanner", "Transparent filters and ranked research setups."],
    [AutoGraphRoundedIcon, "Zone Intelligence", "Supply, demand and multi-timeframe context."],
    [SecurityOutlinedIcon, "Risk Controls", "Plan exposure, invalidation and position size."],
    [NotificationsActiveOutlinedIcon, "Smart Alerts", "Watch conditions without broker execution."],
] as const;

function Login() {
    const navigate = useNavigate();
    const { user, setAuthentication } = useAuth();
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);

    useEffect(() => { if (user) navigate("/dashboard", { replace: true }); }, [navigate, user]);

    function enterLocalDemo() {
        setAuthentication("local-demo-token", { id: "local-demo", full_name: "Local Demo", email: "demo@localhost" });
        navigate("/dashboard", { replace: true });
    }

    async function submit(event: React.FormEvent) {
        event.preventDefault();
        setLoading(true);
        setError("");
        try {
            const result = await loginAccount({ email, password, device_name: "Web browser" });
            setAuthentication(result.access_token, result.user);
            navigate("/dashboard", { replace: true });
        } catch {
            setError("Login failed. Check your details and email verification.");
        } finally { setLoading(false); }
    }

    return (
        <Box sx={{ minHeight: "100vh", bgcolor: "#F8FAFF" }}>
            <PublicHeader />
            <Box className="auth-page" sx={{ minHeight: "calc(100vh - 68px)", py: 2 }}>
                <Card sx={{ width: "100%", maxWidth: 1160, overflow: "hidden", borderColor: "#E0E5EE", boxShadow: "0 24px 70px rgba(16,24,40,.09)", bgcolor: "white" }}>
                    <Box sx={{ display: "grid", gridTemplateColumns: { xs: "1fr", md: "1.05fr .95fr" }, minHeight: 530 }}>
                        <CardContent sx={{ p: { xs: 3, sm: 4.5 }, display: { xs: "none", md: "block" }, borderRight: "1px solid #E4E7EC", background: "radial-gradient(circle at 20% 10%,#F0EEFF,transparent 50%),linear-gradient(145deg,#FBFAFF,#F3F6FF)" }}>
                            <Typography sx={{ color: "#4338CA", fontSize: ".68rem", fontWeight: 800, letterSpacing: ".08em" }}>AI-POWERED MARKET RESEARCH</Typography>
                            <Typography variant="h4" sx={{ mt: 3, maxWidth: 430, fontSize: "2rem", lineHeight: 1.18 }}>Indian market research, <Box component="span" sx={{ color: "#5B5CEB" }}>explained clearly.</Box></Typography>
                            <Typography color="text.secondary" sx={{ mt: 1.5, mb: 3.5, maxWidth: 440 }}>Scan Indian equities, study supply and demand zones, validate rules and manage risk from one workspace.</Typography>
                            <Stack spacing={1.6}>{features.map(([Icon, title, description]) => <Box key={title} sx={{ display: "flex", gap: 1.5, alignItems: "center" }}><Box sx={{ width: 36, height: 36, flexShrink: 0, borderRadius: 1.5, display: "grid", placeItems: "center", bgcolor: "#EFEDFF", color: "#5B5CEB", border: "1px solid #DDD8FF" }}><Icon sx={{ fontSize: 18 }} /></Box><Box><Typography sx={{ fontWeight: 750 }}>{title}</Typography><Typography variant="caption" color="text.secondary">{description}</Typography></Box></Box>)}</Stack>
                            <Box sx={{ mt: 4, px: 2, py: 1.4, borderRadius: 1.5, border: "1px solid #BFE8DD", bgcolor: "#F0FBF8" }}><Typography variant="caption" sx={{ color: "#147D68", fontWeight: 750 }}>Secure · Research-only · No broker execution</Typography></Box>
                        </CardContent>
                        <CardContent sx={{ p: { xs: 3, sm: 4.5 }, alignSelf: "center", width: "100%" }}>
                            <Box sx={{ display: { xs: "block", md: "none" }, mb: 3 }}><BrandLogo /></Box>
                            <Typography variant="h4">Welcome back</Typography>
                            <Typography color="text.secondary" sx={{ mt: 1, mb: 3 }}>Sign in to your AlphaEdge AI workspace.</Typography>
                            <Stack component="form" spacing={2} onSubmit={submit}>
                                {error && <Alert severity="error">{error}</Alert>}
                                {LOCAL_DEMO_MODE && <Alert severity="info">Account service is optional in local demo mode.</Alert>}
                                <TextField label="Email address" type="email" value={email} onChange={(event) => setEmail(event.target.value)} required />
                                <TextField label="Password" type="password" value={password} onChange={(event) => setPassword(event.target.value)} required />
                                <Button type="submit" variant="contained" size="large" disabled={loading}>{loading ? "Signing in..." : "Sign In"}</Button>
                                {LOCAL_DEMO_MODE && <Button type="button" variant="outlined" size="large" onClick={enterLocalDemo}>Enter Local Demo</Button>}
                            </Stack>
                            <Typography color="text.secondary" sx={{ mt: 2.5 }}>New to AlphaEdge AI? <Link component={RouterLink} to="/register">Create your free workspace</Link></Typography>
                            <Link component={RouterLink} to="/" sx={{ display: "inline-block", mt: 1.5, fontSize: ".74rem" }}>Back to product overview</Link>
                            <Typography variant="caption" color="text.secondary" sx={{ display: "block", mt: 3, lineHeight: 1.55 }}>Research and educational use only. Market outcomes are uncertain, and historical results do not guarantee future performance.</Typography>
                        </CardContent>
                    </Box>
                </Card>
            </Box>
        </Box>
    );
}

export default Login;
