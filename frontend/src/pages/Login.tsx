import { useEffect, useState } from "react";
import { Link as RouterLink, useNavigate } from "react-router-dom";

import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Link from "@mui/material/Link";
import Stack from "@mui/material/Stack";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";

import { loginAccount } from "../api/authApi";
import { LOCAL_DEMO_MODE, useAuth } from "../auth/AuthState";

function Login() {
    const navigate = useNavigate();
    const { setAuthentication } = useAuth();
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        if (LOCAL_DEMO_MODE) {
            navigate("/dashboard", { replace: true });
        }
    }, [navigate]);

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
            setAuthentication(
                result.access_token,
                result.user,
            );
            navigate("/dashboard");
        } catch {
            setError("Login failed. Check your details and email verification.");
        } finally {
            setLoading(false);
        }
    }

    return (
        <Box className="auth-page">
            <Card sx={{ width: "100%", maxWidth: 900, overflow: "hidden" }}>
                <Box sx={{ display: "grid", gridTemplateColumns: { xs: "1fr", md: "1.2fr 0.8fr" } }}>
                    <CardContent sx={{ p: { xs: 3, sm: 5 }, bgcolor: "rgba(78,45,150,.12)", display: { xs: "none", md: "block" } }}>
                        <Typography variant="h5">AlphaEdge <Box component="span" color="primary.main">AI</Box></Typography>
                        <Typography variant="h4" sx={{ mt: 5, maxWidth: 380 }}>
                            Market intelligence with explainable research.
                        </Typography>
                        <Typography color="text.secondary" sx={{ mt: 1.5, mb: 4, maxWidth: 430 }}>
                            Scan Indian equities, review delayed market data, test rule-based strategies and manage risk from one workspace.
                        </Typography>
                        <Stack spacing={2}>
                            {[
                                ["AI-Assisted Scanner", "Find setups using transparent technical conditions."],
                                ["Interactive Charts", "Review delayed candles, time ranges and indicators."],
                                ["Risk Controls", "Plan invalidation, exposure and position size."],
                                ["Backtesting", "Evaluate rules on historical data without guarantees."],
                            ].map(([title, description]) => (
                                <Box key={title} sx={{ display: "flex", gap: 1.5 }}>
                                    <Box sx={{ width: 28, height: 28, borderRadius: 1, display: "grid", placeItems: "center", bgcolor: "rgba(74,222,128,.1)", color: "primary.main" }}>✓</Box>
                                    <Box><Typography sx={{ fontWeight: 800 }}>{title}</Typography><Typography variant="caption" color="text.secondary">{description}</Typography></Box>
                                </Box>
                            ))}
                        </Stack>
                        <Typography variant="caption" color="success.main" sx={{ display: "block", mt: 5 }}>
                            Secure · Research-only · No broker execution
                        </Typography>
                    </CardContent>
                    <CardContent sx={{ p: { xs: 3, sm: 5 }, alignSelf: "center" }}>
                    <Typography variant="h5" sx={{ mb: 0.5 }}>AlphaEdge AI</Typography>
                    <Typography variant="h4">
                        Welcome back
                    </Typography>
                    <Typography color="text.secondary" sx={{ mt: 1, mb: 4 }}>
                        Log in to your AlphaEdge AI research workspace.
                    </Typography>

                    <Stack component="form" spacing={2.5} onSubmit={submit}>
                        {error && <Alert severity="error">{error}</Alert>}
                        <TextField
                            label="Email"
                            type="email"
                            value={email}
                            onChange={(event) => setEmail(event.target.value)}
                            required
                        />
                        <TextField
                            label="Password"
                            type="password"
                            value={password}
                            onChange={(event) => setPassword(event.target.value)}
                            required
                        />
                        <Button
                            type="submit"
                            variant="contained"
                            size="large"
                            disabled={loading}
                        >
                            {loading ? "Logging in..." : "Log In"}
                        </Button>
                    </Stack>

                    <Typography color="text.secondary" sx={{ mt: 3 }}>
                        New to AlphaEdge AI?{" "}
                        <Link component={RouterLink} to="/register">
                            Create an account
                        </Link>
                    </Typography>
                    </CardContent>
                </Box>
            </Card>
        </Box>
    );
}

export default Login;
