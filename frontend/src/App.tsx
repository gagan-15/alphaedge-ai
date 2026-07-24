/**
 * Application Routes.
 *
 * Sprint:
 *     2.62 - Application Navigation & Routing
 */

import {
    Navigate,
    Route,
    Routes,
} from "react-router-dom";

import AppLayout from "./layouts/AppLayout";
import ProtectedRoute from "./auth/ProtectedRoute";

import AIAssistant from "./pages/AIAssistant";
import Dashboard from "./pages/Dashboard";
import Login from "./pages/Login";
import Reports from "./pages/Reports";
import Register from "./pages/Register";
import Scanner from "./pages/Scanner";
import Settings from "./pages/Settings";
import Watchlist from "./pages/Watchlist";
import VerifyEmail from "./pages/VerifyEmail";
import {
    AlertsPage,
    CalculatorsPage,
    EconomicCalendarPage,
    MarketBreadthPage,
    MarketOverviewPage,
    NewsInsightsPage,
    OptionChainPage,
    BacktestingPage,
    PortfolioPage,
    ResearchSignalsPage,
    RiskManagementPage,
} from "./pages/WorkspaceScreens";

function PrivatePage({ children }: { children: React.ReactNode }) {
    return (
        <ProtectedRoute>
            <AppLayout>{children}</AppLayout>
        </ProtectedRoute>
    );
}

function App() {
    return (
        <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/verify-email" element={<VerifyEmail />} />
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route
                path="/dashboard"
                element={<PrivatePage><Dashboard /></PrivatePage>}
            />
            <Route
                path="/scanner"
                element={<PrivatePage><Scanner /></PrivatePage>}
            />
            <Route
                path="/signals"
                element={<PrivatePage><ResearchSignalsPage /></PrivatePage>}
            />
            <Route
                path="/holdings"
                element={<PrivatePage><PortfolioPage /></PrivatePage>}
            />
            <Route
                path="/watchlist"
                element={<PrivatePage><Watchlist /></PrivatePage>}
            />
            <Route
                path="/backtest"
                element={<PrivatePage><BacktestingPage /></PrivatePage>}
            />
            <Route
                path="/ai-assistant"
                element={<PrivatePage><AIAssistant /></PrivatePage>}
            />
            <Route
                path="/reports"
                element={<PrivatePage><Reports /></PrivatePage>}
            />
            <Route
                path="/settings"
                element={<PrivatePage><Settings /></PrivatePage>}
            />
            <Route path="/market-overview" element={<PrivatePage><MarketOverviewPage /></PrivatePage>} />
            <Route path="/market-breadth" element={<PrivatePage><MarketBreadthPage /></PrivatePage>} />
            <Route path="/news" element={<PrivatePage><NewsInsightsPage /></PrivatePage>} />
            <Route path="/alerts" element={<PrivatePage><AlertsPage /></PrivatePage>} />
            <Route path="/economic-calendar" element={<PrivatePage><EconomicCalendarPage /></PrivatePage>} />
            <Route path="/option-chain" element={<PrivatePage><OptionChainPage /></PrivatePage>} />
            <Route path="/calculators" element={<PrivatePage><CalculatorsPage /></PrivatePage>} />
            <Route path="/risk-management" element={<PrivatePage><RiskManagementPage /></PrivatePage>} />
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
    );
}

export default App;
