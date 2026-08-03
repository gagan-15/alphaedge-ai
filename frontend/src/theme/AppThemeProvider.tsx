import CssBaseline from "@mui/material/CssBaseline";
import { ThemeProvider } from "@mui/material/styles";

import appTheme from "./theme";

export function AppThemeProvider({ children }: { children: React.ReactNode }) {
    return <ThemeProvider theme={appTheme}>
        <CssBaseline />
        {children}
    </ThemeProvider>;
}
