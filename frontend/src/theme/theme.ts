import { alpha, createTheme } from "@mui/material/styles";

// The production Dashboard uses one fixed light visual language.
export type AppThemeMode = "light";

const colors = {
    background: "#ffffff", paper: "#ffffff", border: "#e3e8ef",
    primary: "#4f5bd5", text: "#172033", textMuted: "#69758a",
};

export function createAppTheme() {

    return createTheme({
        palette: {
            mode: "light",
            primary: { main: colors.primary, contrastText: "#ffffff" },
            success: { main: "#3b8d69" },
            error: { main: "#c9606c" },
            warning: { main: "#b98a38" },
            background: { default: colors.background, paper: colors.paper },
            divider: colors.border,
            text: { primary: colors.text, secondary: colors.textMuted },
        },
        shape: { borderRadius: 12 },
        typography: {
            fontFamily: '"Inter", "Segoe UI", Roboto, Arial, sans-serif',
            fontSize: 12,
            h4: { fontWeight: 750, letterSpacing: "-0.03em", fontSize: "1.35rem" },
            h6: { fontWeight: 700, fontSize: "0.9rem" },
            h5: { fontSize: "1.12rem" },
            body1: { fontSize: "0.78rem", lineHeight: 1.5 },
            body2: { fontSize: "0.72rem", lineHeight: 1.5 },
            button: { fontWeight: 600, textTransform: "none", letterSpacing: 0 },
        },
        components: {
            MuiCssBaseline: {
                styleOverrides: {
                    body: {
                        backgroundColor: colors.background,
                        backgroundImage: "none",
                    },
                },
            },
            MuiCardContent: {
                styleOverrides: { root: { padding: 14, "&:last-child": { paddingBottom: 14 } } },
            },
            MuiCard: {
                styleOverrides: {
                    root: {
                        borderRadius: 16,
                        backgroundImage: "none",
                        backgroundColor: colors.paper,
                        border: `1px solid ${colors.border}`,
                        boxShadow: "0 6px 20px rgba(28,45,72,.045)",
                    },
                },
            },
            MuiPaper: { styleOverrides: { root: { backgroundImage: "none" } } },
            MuiAppBar: {
                styleOverrides: {
                    root: {
                        backgroundImage: "none",
                        backgroundColor: alpha(colors.background, .96),
                        color: colors.text,
                        borderBottom: `1px solid ${colors.border}`,
                        boxShadow: "none",
                    },
                },
            },
            MuiDrawer: {
                styleOverrides: {
                    paper: {
                        backgroundImage: "none",
                        backgroundColor: "#ffffff",
                        color: colors.text,
                        borderRight: `1px solid ${colors.border}`,
                    },
                },
            },
            MuiListItemButton: {
                styleOverrides: {
                    root: {
                        borderRadius: 6,
                        color: colors.textMuted,
                        "& .MuiListItemIcon-root": { color: "inherit" },
                        transition: "color 160ms ease, background-color 160ms ease",
                        "&:hover": { color: colors.text, backgroundColor: alpha(colors.primary, .055) },
                        "&.Mui-selected": {
                            color: colors.primary,
                            backgroundColor: alpha(colors.primary, .08),
                            boxShadow: `inset 2px 0 0 ${colors.primary}`,
                        },
                        "&.Mui-selected:hover": { backgroundColor: alpha(colors.primary, .11) },
                    },
                },
            },
            MuiButton: {
                styleOverrides: {
                    root: {
                        borderRadius: 12,
                        boxShadow: "none",
                        transition: "background-color 160ms ease, border-color 160ms ease, color 160ms ease",
                        "&:hover": { boxShadow: "none", backgroundColor: alpha(colors.primary, .045) },
                        "&.Mui-focusVisible": { outline: `2px solid ${alpha(colors.primary, .28)}`, outlineOffset: 2 },
                    },
                },
            },
            MuiIconButton: {
                styleOverrides: {
                    root: {
                        transition: "background-color 160ms ease, color 160ms ease",
                        "&:hover": { backgroundColor: alpha(colors.primary, .06) },
                        "&.Mui-focusVisible": { outline: `2px solid ${alpha(colors.primary, .28)}`, outlineOffset: 2 },
                    },
                },
            },
            MuiOutlinedInput: {
                styleOverrides: {
                    root: {
                        borderRadius: 12,
                        transition: "background-color 160ms ease, box-shadow 160ms ease",
                        "& .MuiOutlinedInput-notchedOutline": { transition: "border-color 160ms ease" },
                        "&:hover .MuiOutlinedInput-notchedOutline": { borderColor: "#c8d0dc" },
                        "&.Mui-focused": { boxShadow: `0 0 0 3px ${alpha(colors.primary, .09)}` },
                        "&.Mui-focused .MuiOutlinedInput-notchedOutline": { borderColor: colors.primary, borderWidth: 1 },
                    },
                },
            },
            MuiChip: { styleOverrides: { root: { borderRadius: 999, fontWeight: 600, letterSpacing: 0 } } },
            MuiLinearProgress: { styleOverrides: { root: { backgroundColor: alpha(colors.textMuted, .12) } } },
        },
    });
}

export default createAppTheme();
