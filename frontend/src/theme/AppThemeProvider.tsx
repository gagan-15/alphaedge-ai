import { useEffect, useMemo, useState } from "react";
import CssBaseline from "@mui/material/CssBaseline";
import { ThemeProvider } from "@mui/material/styles";

import { createAppTheme, type AppThemeMode } from "./theme";
import { ThemeModeContext } from "./ThemeModeState";

const storageKey = "alphaedge.theme.mode";

export function AppThemeProvider({ children }: { children: React.ReactNode }) {
    const [mode, setMode] = useState<AppThemeMode>(() =>
        localStorage.getItem(storageKey) === "light" ? "light" : "dark"
    );
    const theme = useMemo(() => createAppTheme(mode), [mode]);
    useEffect(() => {
        document.documentElement.dataset.theme = mode;
    }, [mode]);
    const context = useMemo(() => ({
        mode,
        toggleMode: () => setMode((current) => {
            const next = current === "dark" ? "light" : "dark";
            localStorage.setItem(storageKey, next);
            return next;
        }),
    }), [mode]);

    return <ThemeModeContext.Provider value={context}>
        <ThemeProvider theme={theme}>
            <CssBaseline />
            {children}
        </ThemeProvider>
    </ThemeModeContext.Provider>;
}
