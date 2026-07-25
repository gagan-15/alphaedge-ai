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

    useEffect(() => {
        if (user) {
            navigate("/dashboard", { replace: true });
        }
    }, [navigate, user]);

    function enterLocalDemo() {
        setAuthentication("local-demo-token", {
            id: "local-demo",
            full_name: "Local Demo",
            email: "demo@localhost",
        });
        navigate("/dashboard", { replace: true });
    }

    async function submit(event: React.FormEvent) {
        event.preventDefault();
        setLoading(true);
        setError("");

        try {
            const result = await loginAccount({
                email,
                password,
                device_name: "Web browser",
            });
            setAuthentication(result.access_token, result.user);
            navigate("/dashboard", { replace: true });
        } catch {
            setError("Login failed. Check your details and email verification.");
        } finally {
            setLoading(false);
        }
    }

    return (
        <Box className="auth-page">
            <Card
                sx={{
                    width: "100%",
                    maxWidth: 980,
                    overflow: "hidden",
                    borderColor: "rgba(99,102,241,.28)",
                    boxShadow: "0 32px 90px rgba(0,0,0,.48), 0 0 80px rgba(79,70,229,.08)",
                }}
            >
                <Box sx={{ display: "grid", gridTemplateColumns: { xs: "1fr", md: "1.15fr .85fr" }, minHeight: 610 }}>
                    <CardContent
                        sx={{
                            p: { xs: 3, sm: 5 },
                            display: { xs: "none", md: "block" },
                            borderRight: "1px solid rgba(99,102,241,.18)",
                            background:
                                "radial-gradient(circle at 15% 0%,rgba(124,58,237,.22),transparent 42%), linear-gradient(145deg,rgba(30,20,67,.82),rgba(9,18,34,.96))",
                        }}
                    >
                        <BrandLogo />
                        <Typography variant="h4" sx={{ mt: 5, maxWidth: 430, fontSize: "1.75rem", lineHeight: 1.18 }}>
                            Research the market with{" "}
                            <Box component="span" sx={{ color: "#9b7cff" }}>
                                clarity and discipline.
                            </Box>
                        </Typography>
                        <Typography color="text.secondary" sx={{ mt: 1.5, mb: 4, maxWidth: 440 }}>
                            Scan Indian equities, study supply and demand zones,
                            validate rules and manage risk from one workspace.
                        </Typography>

                        <Stack spacing={2}>
                            {features.map(([Icon, title, description]) => (
                                <Box key={title} sx={{ display: "flex", gap: 1.5, alignItems: "center" }}>
                                    <Box
                                        sx={{
                                            width: 36,
                                            height: 36,
                                            flexShrink: 0,
                                            borderRadius: 1.5,
                                            display: "grid",
                                            placeItems: "center",
                                            bgcolor: "rgba(99,102,241,.12)",
                                            color: "#9b8cff",
                                            border: "1px solid rgba(129,140,248,.16)",
                                        }}
                                    >
                                        <Icon sx={{ fontSize: 18 }} />
                                    </Box>
                                    <Box>
                                        <Typography sx={{ fontWeight: 800 }}>{title}</Typography>
                                        <Typography variant="caption" color="text.secondary">{description}</Typography>
                                    </Box>
                                </Box>
                            ))}
                        </Stack>

                        <Box sx={{ mt: 5, px: 2, py: 1.4, borderRadius: 1.5, border: "1px solid rgba(74,222,128,.14)", bgcolor: "rgba(74,222,128,.035)" }}>
                            <Typography variant="caption" color="success.main" sx={{ fontWeight: 750 }}>
                                Secure · Research-only · No broker execution
                            </Typography>
                        </Box>
                    </CardContent>

                    <CardContent sx={{ p: { xs: 3, sm: 5 }, alignSelf: "center", width: "100%" }}>
                        <Box sx={{ display: { xs: "block", md: "none" }, mb: 4 }}><BrandLogo /></Box>
                        <Typography variant="h4">Welcome back</Typography>
                        <Typography color="text.secondary" sx={{ mt: 1, mb: 4 }}>
                            Log in to your AlphaEdge AI research workspace.
                        </Typography>

                        <Stack component="form" spacing={2.25} onSubmit={submit}>
                            {error && <Alert severity="error">{error}</Alert>}
                            {LOCAL_DEMO_MODE && (
                                <Alert severity="info">
                                    Account service is optional in local demo mode.
                                </Alert>
                            )}
                            <TextField label="Email" type="email" value={email} onChange={(event) => setEmail(event.target.value)} required />
                            <TextField label="Password" type="password" value={password} onChange={(event) => setPassword(event.target.value)} required />
                            <Button type="submit" variant="contained" size="large" disabled={loading}>
                                {loading ? "Logging in..." : "Log In"}
                            </Button>
                            {LOCAL_DEMO_MODE && (
                                <Button type="button" variant="outlined" size="large" onClick={enterLocalDemo}>
                                    Enter Local Demo
                                </Button>
                            )}
                        </Stack>

                        <Typography color="text.secondary" sx={{ mt: 3 }}>
                            New to AlphaEdge AI?{" "}
                            <Link component={RouterLink} to="/register">Create an account</Link>
                        </Typography>
                        <Link
                            component={RouterLink}
                            to="/"
                            sx={{ display: "inline-block", mt: 2, fontSize: ".74rem" }}
                        >
                            ← Back to complete product overview
                        </Link>
                        <Typography variant="caption" color="text.secondary" sx={{ display: "block", mt: 4, lineHeight: 1.55 }}>
                            Educational and analytical use only. Market outcomes are uncertain,
                            and historical results do not guarantee future performance.
                        </Typography>
                    </CardContent>
                </Box>
            </Card>
        </Box>
    );
}

export default Login;
