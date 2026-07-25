import { alpha, createTheme } from "@mui/material/styles";

const colors = {
    background: "#07101f",
    paper: "#0b1627",
    paperRaised: "#0f1c2f",
    border: "#1d2b40",
    primary: "#6366f1",
    text: "#f3f7fb",
    textMuted: "#8fa1b8",
};

const theme = createTheme({
    palette: {
        mode: "dark",
        primary: {
            main: colors.primary,
            contrastText: "#ffffff",
        },
        success: {
            main: "#35d07f",
        },
        error: {
            main: "#ff5c67",
        },
        warning: {
            main: "#f5b942",
        },
        background: {
            default: colors.background,
            paper: colors.paper,
        },
        divider: colors.border,
        text: {
            primary: colors.text,
            secondary: colors.textMuted,
        },
    },
    shape: {
        borderRadius: 10,
    },
    typography: {
        fontFamily:
            '"Inter", "Segoe UI", Roboto, Arial, sans-serif',
        fontSize: 12,
        h4: {
            fontWeight: 750,
            letterSpacing: "-0.03em",
            fontSize: "1.35rem",
        },
        h6: {
            fontWeight: 700,
            fontSize: "0.9rem",
        },
        h5: {
            fontSize: "1.12rem",
        },
        body1: {
            fontSize: "0.78rem",
        },
        body2: {
            fontSize: "0.72rem",
        },
        button: {
            fontWeight: 650,
            textTransform: "none",
        },
    },
    components: {
        MuiCssBaseline: {
            styleOverrides: {
                body: {
                    backgroundImage:
                        "radial-gradient(circle at 50% -20%, #13243c 0%, #07101f 42%)",
                },
            },
        },
        MuiCardContent: {
            styleOverrides: {
                root: {
                    padding: 14,
                    "&:last-child": {
                        paddingBottom: 14,
                    },
                },
            },
        },
        MuiCard: {
            styleOverrides: {
                root: {
                    backgroundImage:
                        "linear-gradient(145deg, rgba(12,27,48,.98), rgba(7,18,34,.99))",
                    border: `1px solid ${colors.border}`,
                    boxShadow: "0 12px 34px rgba(0, 0, 0, 0.16)",
                },
            },
        },
        MuiPaper: {
            styleOverrides: {
                root: {
                    backgroundImage: "none",
                },
            },
        },
        MuiAppBar: {
            styleOverrides: {
                root: {
                    backgroundImage: "none",
                    backgroundColor: alpha(colors.background, 0.96),
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
                    backgroundColor: "#081322",
                    borderRight: `1px solid ${colors.border}`,
                },
            },
        },
        MuiListItemButton: {
            styleOverrides: {
                root: {
                    borderRadius: 6,
                    color: colors.textMuted,
                    "& .MuiListItemIcon-root": {
                        color: "inherit",
                    },
                    "&:hover": {
                        color: colors.text,
                        backgroundColor: "rgba(59,130,246,.08)",
                    },
                    "&.Mui-selected": {
                        color: "#ffffff",
                        background:
                            "linear-gradient(100deg, #2447dc, #3d5ef4)",
                        boxShadow:
                            "inset 3px 0 0 #8b9cff, 0 8px 22px rgba(37,99,235,.2)",
                    },
                    "&.Mui-selected:hover": {
                        background:
                            "linear-gradient(90deg, rgba(37,99,235,.48), rgba(124,58,237,.36))",
                    },
                },
            },
        },
        MuiChip: {
            styleOverrides: {
                root: {
                    fontWeight: 700,
                },
            },
        },
        MuiLinearProgress: {
            styleOverrides: {
                root: {
                    backgroundColor: alpha(colors.textMuted, 0.12),
                },
            },
        },
    },
});

export default theme;
