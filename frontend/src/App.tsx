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
import MyHoldings from "./pages/MyHoldings";
import Reports from "./pages/Reports";
import Scanner from "./pages/Scanner";
import Settings from "./pages/Settings";
import Signals from "./pages/Signals";
import Watchlist from "./pages/Watchlist";

function App() {
    return (
        <AppLayout>
            <Routes>
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
                    element={<Dashboard />}
                />

                <Route
                    path="/scanner"
                    element={<Scanner />}
                />

                <Route
                    path="/signals"
                    element={<Signals />}
                />

                <Route
                    path="/holdings"
                    element={<MyHoldings />}
                />

                <Route
                    path="/watchlist"
                    element={<Watchlist />}
                />

                <Route
                    path="/backtest"
                    element={<Backtest />}
                />

                <Route
                    path="/ai-assistant"
                    element={<AIAssistant />}
                />

                <Route
                    path="/reports"
                    element={<Reports />}
                />

                <Route
                    path="/settings"
                    element={<Settings />}
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
        </AppLayout>
    );
}

export default App;