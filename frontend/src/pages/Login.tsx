import { useState } from "react";
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

function Login() {
    const navigate = useNavigate();
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);

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
            sessionStorage.setItem(
                "alphaedge_access_token",
                result.access_token,
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
            <Card sx={{ width: "100%", maxWidth: 440 }}>
                <CardContent sx={{ p: { xs: 3, sm: 5 } }}>
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
            </Card>
        </Box>
    );
}

export default Login;
