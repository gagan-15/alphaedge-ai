import { useState } from "react";
import { Link as RouterLink } from "react-router-dom";

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

import { registerAccount } from "../api/authApi";

function Register() {
    const [form, setForm] = useState({
        full_name: "",
        email: "",
        password: "",
        country: "IN",
        accepts_terms: false,
        accepts_risk_disclosure: false,
        confirms_adult: false,
    });
    const [message, setMessage] = useState("");
    const [error, setError] = useState("");

    async function submit(event: React.FormEvent) {
        event.preventDefault();
        setMessage("");
        setError("");

        try {
            const result = await registerAccount(form);
            setMessage(result.message);
        } catch {
            setError("Registration failed. Check your details and password.");
        }
    }

    return (
        <Box className="auth-page">
            <Card sx={{ width: "100%", maxWidth: 520 }}>
                <CardContent sx={{ p: { xs: 3, sm: 5 } }}>
                    <Typography variant="h4">Create account</Typography>
                    <Typography color="text.secondary" sx={{ mt: 1, mb: 3 }}>
                        Free local access to the research platform.
                    </Typography>

                    <Stack component="form" spacing={2} onSubmit={submit}>
                        {message && <Alert severity="success">{message}</Alert>}
                        {error && <Alert severity="error">{error}</Alert>}
                        <TextField
                            label="Full name"
                            value={form.full_name}
                            onChange={(event) =>
                                setForm({ ...form, full_name: event.target.value })
                            }
                            required
                        />
                        <TextField
                            label="Email"
                            type="email"
                            value={form.email}
                            onChange={(event) =>
                                setForm({ ...form, email: event.target.value })
                            }
                            required
                        />
                        <TextField
                            label="Password"
                            type="password"
                            helperText="12+ characters with upper, lower, number and symbol."
                            value={form.password}
                            onChange={(event) =>
                                setForm({ ...form, password: event.target.value })
                            }
                            required
                        />
                        {[
                            ["accepts_terms", "I accept the Terms."],
                            [
                                "accepts_risk_disclosure",
                                "I understand market investments can cause loss.",
                            ],
                            ["confirms_adult", "I confirm I am at least 18."],
                        ].map(([field, label]) => (
                            <FormControlLabel
                                key={field}
                                control={
                                    <Checkbox
                                        checked={
                                            form[
                                                field as keyof typeof form
                                            ] as boolean
                                        }
                                        onChange={(event) =>
                                            setForm({
                                                ...form,
                                                [field]: event.target.checked,
                                            })
                                        }
                                    />
                                }
                                label={label}
                            />
                        ))}
                        <Button type="submit" variant="contained" size="large">
                            Create Account
                        </Button>
                    </Stack>
                    <Typography color="text.secondary" sx={{ mt: 3 }}>
                        Already registered?{" "}
                        <Link component={RouterLink} to="/login">
                            Log in
                        </Link>
                    </Typography>
                </CardContent>
            </Card>
        </Box>
    );
}

export default Register;
