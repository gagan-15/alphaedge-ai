import { createContext, useContext } from "react";
import type { AppThemeMode } from "./theme";

export interface ThemeModeContextValue {
    mode: AppThemeMode;
    toggleMode: () => void;
}

export const ThemeModeContext = createContext<ThemeModeContextValue | null>(null);

export function useThemeMode() {
    const value = useContext(ThemeModeContext);
    if (!value) throw new Error("useThemeMode must be used inside AppThemeProvider.");
    return value;
}
