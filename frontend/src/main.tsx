/**
 * Application Entry Point.
 *
 * Sprint:
 *     2.62 - Application Navigation & Routing
 */

import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";

import {
    CssBaseline,
    ThemeProvider,
} from "@mui/material";

import App from "./App";
import { AuthProvider } from "./auth/AuthContext";
import { MarketIntelligenceProvider } from "./market-intelligence/MarketIntelligenceContext";
import theme from "./theme/theme";
import "./index.css";

createRoot(
    document.getElementById("root")!,
).render(
    <StrictMode>
        <BrowserRouter>
            <ThemeProvider theme={theme}>
                <CssBaseline />

                <AuthProvider>
                    <MarketIntelligenceProvider>
                        <App />
                    </MarketIntelligenceProvider>
                </AuthProvider>
            </ThemeProvider>
        </BrowserRouter>
    </StrictMode>,
);
