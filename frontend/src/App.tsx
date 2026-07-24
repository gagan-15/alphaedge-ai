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

import AIAssistant from "./pages/AIAssistant";
import Backtest from "./pages/Backtest";
import Dashboard from "./pages/Dashboard";
import Login from "./pages/Login";
import MyHoldings from "./pages/MyHoldings";
import Reports from "./pages/Reports";
import Register from "./pages/Register";
import Scanner from "./pages/Scanner";
import Settings from "./pages/Settings";
import Signals from "./pages/Signals";
import Watchlist from "./pages/Watchlist";

function App() {
    return (
        <Routes>
                <Route path="/login" element={<Login />} />
                <Route path="/register" element={<Register />} />
                <Route
                    path="/"
                    element={
                        <Navigate
                            to="/dashboard"
                            replace
                        />
                    }
                />

                <Route
                    path="/dashboard"
                    element={<AppLayout><Dashboard /></AppLayout>}
                />

                <Route
                    path="/scanner"
                    element={<AppLayout><Scanner /></AppLayout>}
                />

                <Route
                    path="/signals"
                    element={<AppLayout><Signals /></AppLayout>}
                />

                <Route
                    path="/holdings"
                    element={<AppLayout><MyHoldings /></AppLayout>}
                />

                <Route
                    path="/watchlist"
                    element={<AppLayout><Watchlist /></AppLayout>}
                />

                <Route
                    path="/backtest"
                    element={<AppLayout><Backtest /></AppLayout>}
                />

                <Route
                    path="/ai-assistant"
                    element={<AppLayout><AIAssistant /></AppLayout>}
                />

                <Route
                    path="/reports"
                    element={<AppLayout><Reports /></AppLayout>}
                />

                <Route
                    path="/settings"
                    element={<AppLayout><Settings /></AppLayout>}
                />

                <Route
                    path="*"
                    element={
                        <Navigate
                            to="/dashboard"
                            replace
                        />
                    }
                />
            </Routes>
    );
}

export default App;
