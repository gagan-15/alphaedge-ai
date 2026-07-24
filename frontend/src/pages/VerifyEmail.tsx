import { useEffect, useState } from "react";
import { Link as RouterLink, useSearchParams } from "react-router-dom";

import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import CircularProgress from "@mui/material/CircularProgress";
import Typography from "@mui/material/Typography";

import { verifyEmail } from "../api/authApi";

function VerifyEmail() {
    const [params] = useSearchParams();
    const token = params.get("token");
    const [state, setState] = useState<"loading" | "success" | "error">(
        token ? "loading" : "error",
    );

    useEffect(() => {
        if (!token) {
            return;
        }

        void verifyEmail(token)
            .then(() => setState("success"))
            .catch(() => setState("error"));
    }, [token]);

    return (
        <Box className="auth-page">
            <Card sx={{ width: "100%", maxWidth: 440 }}>
                <CardContent sx={{ p: 5, textAlign: "center" }}>
                    <Typography variant="h4">Email verification</Typography>
                    {state === "loading" && <CircularProgress sx={{ mt: 4 }} />}
                    {state === "success" && (
                        <Alert severity="success" sx={{ mt: 3 }}>
                            Email verified. You can now log in.
                        </Alert>
                    )}
                    {state === "error" && (
                        <Alert severity="error" sx={{ mt: 3 }}>
                            This verification link is invalid or expired.
                        </Alert>
                    )}
                    <Button
                        component={RouterLink}
                        to="/login"
                        variant="contained"
                        sx={{ mt: 3 }}
                    >
                        Go to Login
                    </Button>
                </CardContent>
            </Card>
        </Box>
    );
}

export default VerifyEmail;
