import { alpha, createTheme } from "@mui/material/styles";

export type AppThemeMode = "dark" | "light";

export function createAppTheme(mode: AppThemeMode) {
    const dark = mode === "dark";
    const colors = dark ? {
        background: "#07101f", paper: "#0b1627", border: "#1d2b40",
        primary: "#6366f1", text: "#f3f7fb", textMuted: "#8fa1b8",
    } : {
        background: "#f4f7fb", paper: "#ffffff", border: "#d8e1ec",
        primary: "#4f46e5", text: "#142033", textMuted: "#607089",
    };

    return createTheme({
        palette: {
            mode,
            primary: { main: colors.primary, contrastText: "#ffffff" },
            success: { main: "#35a96f" },
            error: { main: "#e54855" },
            warning: { main: "#d99a22" },
            background: { default: colors.background, paper: colors.paper },
            divider: colors.border,
            text: { primary: colors.text, secondary: colors.textMuted },
        },
        shape: { borderRadius: 10 },
        typography: {
            fontFamily: '"Inter", "Segoe UI", Roboto, Arial, sans-serif',
            fontSize: 12,
            h4: { fontWeight: 750, letterSpacing: "-0.03em", fontSize: "1.35rem" },
            h6: { fontWeight: 700, fontSize: "0.9rem" },
            h5: { fontSize: "1.12rem" },
            body1: { fontSize: "0.78rem" },
            body2: { fontSize: "0.72rem" },
            button: { fontWeight: 650, textTransform: "none" },
        },
        components: {
            MuiCssBaseline: {
                styleOverrides: {
                    body: {
                        backgroundColor: colors.background,
                        backgroundImage: dark
                            ? "radial-gradient(circle at 50% -20%, #13243c 0%, #07101f 42%)"
                            : "radial-gradient(circle at 50% -20%, #ffffff 0%, #f4f7fb 52%)",
                    },
                },
            },
            MuiCardContent: {
                styleOverrides: { root: { padding: 14, "&:last-child": { paddingBottom: 14 } } },
            },
            MuiCard: {
                styleOverrides: {
                    root: {
                        backgroundImage: dark ? "linear-gradient(145deg, rgba(12,27,48,.98), rgba(7,18,34,.99))" : "none",
                        backgroundColor: colors.paper,
                        border: `1px solid ${colors.border}`,
                        boxShadow: dark ? "0 12px 34px rgba(0,0,0,.16)" : "0 10px 28px rgba(28,45,72,.08)",
                    },
                },
            },
            MuiPaper: { styleOverrides: { root: { backgroundImage: "none" } } },
            MuiAppBar: {
                styleOverrides: {
                    root: {
                        backgroundImage: "none",
                        backgroundColor: alpha(colors.background, .96),
                        borderBottom: `1px solid ${colors.border}`,
                        boxShadow: "none",
                        backdropFilter: "blur(14px)",
                    },
                },
            },
            MuiDrawer: {
                styleOverrides: {
                    paper: {
                        backgroundImage: "none",
                        backgroundColor: dark ? "#081322" : "#ffffff",
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
                        "&:hover": { color: colors.text, backgroundColor: alpha(colors.primary, .08) },
                        "&.Mui-selected": {
                            color: "#ffffff",
                            background: "linear-gradient(100deg, #2447dc, #3d5ef4)",
                            boxShadow: "inset 3px 0 0 #8b9cff, 0 8px 22px rgba(37,99,235,.2)",
                        },
                        "&.Mui-selected:hover": { background: "linear-gradient(90deg, rgba(37,99,235,.82), rgba(124,58,237,.72))" },
                    },
                },
            },
            MuiChip: { styleOverrides: { root: { fontWeight: 700 } } },
            MuiLinearProgress: { styleOverrides: { root: { backgroundColor: alpha(colors.textMuted, .12) } } },
        },
    });
}

export default createAppTheme("dark");
