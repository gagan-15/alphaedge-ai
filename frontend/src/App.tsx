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
import Alerts from "./pages/Alerts";
import Backtesting from "./pages/Backtesting";
import Calculators from "./pages/Calculators";
import Dashboard from "./pages/Dashboard";
import EconomicCalendar from "./pages/EconomicCalendar";
import Login from "./pages/Login";
import Landing from "./pages/Landing";
import MyHoldings from "./pages/MyHoldings";
import MarketBreadth from "./pages/MarketBreadth";
import MarketOverview from "./pages/MarketOverview";
import NewsEvents from "./pages/NewsEvents";
import OptionChain from "./pages/OptionChain";
import Reports from "./pages/Reports";
import RiskManagement from "./pages/RiskManagement";
import Register from "./pages/Register";
import Scanner from "./pages/Scanner";
import Signals from "./pages/Signals";
import Settings from "./pages/Settings";
import Strategies from "./pages/Strategies";
import Watchlist from "./pages/Watchlist";
import VerifyEmail from "./pages/VerifyEmail";

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
            <Route path="/" element={<Landing />} />
            <Route
                path="/dashboard"
                element={<PrivatePage><Dashboard /></PrivatePage>}
            />
            <Route
                path="/stock-details/:symbol"
                element={<PrivatePage><Scanner /></PrivatePage>}
            />
            <Route
                path="/signals"
                element={<PrivatePage><Signals /></PrivatePage>}
            />
            <Route
                path="/holdings"
                element={<PrivatePage><MyHoldings /></PrivatePage>}
            />
            <Route
                path="/watchlist"
                element={<PrivatePage><Watchlist /></PrivatePage>}
            />
            <Route
                path="/backtest"
                element={<PrivatePage><Backtesting /></PrivatePage>}
            />
            <Route
                path="/ai-assistant"
                element={<PrivatePage><AIAssistant /></PrivatePage>}
            />
            <Route path="/strategies" element={<PrivatePage><Strategies /></PrivatePage>} />
            <Route
                path="/reports"
                element={<PrivatePage><Reports /></PrivatePage>}
            />
            <Route
                path="/settings"
                element={<PrivatePage><Settings /></PrivatePage>}
            />
            <Route path="/market-overview" element={<PrivatePage><MarketOverview /></PrivatePage>} />
            <Route path="/market-breadth" element={<PrivatePage><MarketBreadth /></PrivatePage>} />
            <Route path="/news" element={<PrivatePage><NewsEvents /></PrivatePage>} />
            <Route path="/alerts" element={<PrivatePage><Alerts /></PrivatePage>} />
            <Route path="/economic-calendar" element={<PrivatePage><EconomicCalendar /></PrivatePage>} />
            <Route path="/option-chain" element={<PrivatePage><OptionChain /></PrivatePage>} />
            <Route path="/calculators" element={<PrivatePage><Calculators /></PrivatePage>} />
            <Route path="/risk-management" element={<PrivatePage><RiskManagement /></PrivatePage>} />
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
    );
}

export default App;
