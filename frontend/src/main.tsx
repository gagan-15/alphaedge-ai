/**
 * Application Entry Point.
 *
 * Sprint:
 *     2.62 - Application Navigation & Routing
 */

import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";

import App from "./App";
import { AuthProvider } from "./auth/AuthContext";
import { MarketIntelligenceProvider } from "./market-intelligence/MarketIntelligenceContext";
import { AppThemeProvider } from "./theme/AppThemeProvider";
import "./index.css";

createRoot(
    document.getElementById("root")!,
).render(
    <StrictMode>
        <BrowserRouter>
            <AppThemeProvider>
                <AuthProvider>
                    <MarketIntelligenceProvider>
                        <App />
                    </MarketIntelligenceProvider>
                </AuthProvider>
            </AppThemeProvider>
        </BrowserRouter>
    </StrictMode>,
);
