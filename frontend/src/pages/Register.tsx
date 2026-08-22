import AutoGraphRoundedIcon from "@mui/icons-material/AutoGraphRounded";
import GridViewRoundedIcon from "@mui/icons-material/GridViewRounded";
import InsightsRoundedIcon from "@mui/icons-material/InsightsRounded";
import NotificationsActiveOutlinedIcon from "@mui/icons-material/NotificationsActiveOutlined";
import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Checkbox from "@mui/material/Checkbox";
import FormControlLabel from "@mui/material/FormControlLabel";
import Link from "@mui/material/Link";
import Stack from "@mui/material/Stack";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";
import { useEffect, useState } from "react";
import { Link as RouterLink, useNavigate } from "react-router-dom";

import { registerAccount } from "../api/authApi";
import { useAuth } from "../auth/AuthState";
import PublicHeader from "../components/public/PublicHeader";

const features = [
    [GridViewRoundedIcon, "Market Scanner", "Filter Indian equities with clear research conditions."],
    [AutoGraphRoundedIcon, "Supply & Demand Zones", "Review boundaries, quality, freshness and distance."],
    [InsightsRoundedIcon, "Explainable Insights", "Understand why a setup appears with plain-language reasons."],
    [NotificationsActiveOutlinedIcon, "Research Alerts", "Track conditions and key levels without broker execution."],
] as const;

function Register() {
    const navigate = useNavigate();
    const { user } = useAuth();
    const [confirmPassword, setConfirmPassword] = useState("");
    const [loading, setLoading] = useState(false);
    const [form, setForm] = useState({ full_name: "", email: "", password: "", country: "IN", accepts_terms: false, accepts_risk_disclosure: false, confirms_adult: false });
    const [message, setMessage] = useState("");
    const [error, setError] = useState("");

    useEffect(() => { if (user) navigate("/dashboard", { replace: true }); }, [navigate, user]);

    async function submit(event: React.FormEvent) {
        event.preventDefault();
        setMessage("");
        setError("");
        if (form.password !== confirmPassword) { setError("Passwords do not match."); return; }
        setLoading(true);
        try {
            const result = await registerAccount(form);
            setMessage(result.message || "Account created. Check your email to verify it before signing in.");
        } catch { setError("Registration failed. Check your details, password and required agreements."); }
        finally { setLoading(false); }
    }

    return (
        <Box sx={{ minHeight: "100vh", bgcolor: "#F8FAFF" }}>
            <PublicHeader />
            <Box className="auth-page" sx={{ minHeight: "calc(100vh - 68px)", py: 2 }}>
                <Card sx={{ width: "100%", maxWidth: 1160, overflow: "hidden", borderColor: "#E0E5EE", boxShadow: "0 24px 70px rgba(16,24,40,.09)", bgcolor: "white" }}>
                    <Box sx={{ display: "grid", gridTemplateColumns: { xs: "1fr", md: ".95fr 1.05fr" } }}>
                        <CardContent sx={{ p: { xs: 3, sm: 4.5 }, display: { xs: "none", md: "block" }, borderRight: "1px solid #E4E7EC", background: "radial-gradient(circle at 20% 10%,#F0EEFF,transparent 50%),linear-gradient(145deg,#FBFAFF,#F3F6FF)" }}>
                            <Typography sx={{ color: "#4338CA", fontSize: ".68rem", fontWeight: 800, letterSpacing: ".08em" }}>AI-POWERED MARKET RESEARCH</Typography>
                            <Typography variant="h4" sx={{ mt: 3, fontSize: "1.9rem", lineHeight: 1.2 }}>Indian market intelligence, <Box component="span" sx={{ color: "#5B5CEB" }}>explained clearly.</Box></Typography>
                            <Typography color="text.secondary" sx={{ mt: 1.5, mb: 3.5 }}>AI-assisted research, supply and demand zones, and disciplined risk tools — all in one workspace.</Typography>
                            <Stack spacing={1.6}>{features.map(([Icon, title, text]) => <Box key={title} sx={{ display: "flex", gap: 1.5, alignItems: "center" }}><Box sx={{ width: 36, height: 36, display: "grid", placeItems: "center", flexShrink: 0, borderRadius: 1.5, bgcolor: "#EFEDFF", color: "#5B5CEB", border: "1px solid #DDD8FF" }}><Icon sx={{ fontSize: 18 }} /></Box><Box><Typography sx={{ fontWeight: 750 }}>{title}</Typography><Typography variant="caption" color="text.secondary">{text}</Typography></Box></Box>)}</Stack>
                            <Box sx={{ mt: 4, p: 1.7, borderRadius: 1.5, border: "1px solid #BFE8DD", bgcolor: "#F0FBF8" }}><Typography sx={{ color: "#147D68", fontSize: ".72rem", fontWeight: 700 }}>Research-only platform · No auto trading · No broker access · Privacy first</Typography></Box>
                        </CardContent>
                        <CardContent sx={{ p: { xs: 3, sm: 4.5 } }}>
                            <Typography variant="h4" sx={{ fontSize: "1.7rem" }}>Create your AlphaEdge AI workspace</Typography>
                            <Typography color="text.secondary" sx={{ mt: 1, mb: 2.5 }}>Start researching the Indian market with AI-assisted insights.</Typography>
                            <Stack component="form" spacing={1.6} onSubmit={submit}>
                                {message && <Alert severity="success" action={<Button component={RouterLink} to="/login" size="small">Sign in</Button>}>{message}</Alert>}
                                {error && <Alert severity="error">{error}</Alert>}
                                <Box sx={{ display: "grid", gridTemplateColumns: { xs: "1fr", sm: "1fr 1fr" }, gap: 1.6 }}>
                                    <TextField label="Full name" value={form.full_name} onChange={(event) => setForm({ ...form, full_name: event.target.value })} required />
                                    <TextField label="Email address" type="email" value={form.email} onChange={(event) => setForm({ ...form, email: event.target.value })} required />
                                    <TextField label="Password" type="password" helperText="12+ characters with upper, lower, number and symbol." value={form.password} onChange={(event) => setForm({ ...form, password: event.target.value })} required />
                                    <TextField label="Confirm password" type="password" value={confirmPassword} onChange={(event) => setConfirmPassword(event.target.value)} required />
                                </Box>
                                <Stack spacing={0}>{[["accepts_terms", "I accept the Terms of Service and Privacy Policy."], ["accepts_risk_disclosure", "I understand AlphaEdge provides research, not investment advice."], ["confirms_adult", "I confirm that I am at least 18 years old."]].map(([field, label]) => <FormControlLabel key={field} control={<Checkbox size="small" checked={form[field as keyof typeof form] as boolean} onChange={(event) => setForm({ ...form, [field]: event.target.checked })} />} label={<Typography sx={{ fontSize: ".76rem" }}>{label}</Typography>} />)}</Stack>
                                <Button type="submit" variant="contained" size="large" disabled={loading}>{loading ? "Creating account..." : "Create Account"}</Button>
                            </Stack>
                            <Typography color="text.secondary" sx={{ mt: 2, textAlign: "center" }}>Already have an account? <Link component={RouterLink} to="/login">Sign in</Link></Typography>
                            <Typography variant="caption" color="text.secondary" sx={{ display: "block", mt: 2.5, p: 1.5, border: "1px solid #E4E7EC", borderRadius: 1.5, bgcolor: "#FAFBFF" }}>Research assistance only. AlphaEdge does not execute trades or provide investment advice.</Typography>
                        </CardContent>
                    </Box>
                </Card>
            </Box>
        </Box>
    );
}

export default Register;
