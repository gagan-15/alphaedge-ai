import { alpha, createTheme } from "@mui/material/styles";

const colors = {
    background: "#07101f",
    paper: "#0b1627",
    paperRaised: "#0f1c2f",
    border: "#1d2b40",
    primary: "#4ade80",
    text: "#f3f7fb",
    textMuted: "#8fa1b8",
};

const theme = createTheme({
    palette: {
        mode: "dark",
        primary: {
            main: colors.primary,
            contrastText: "#04110a",
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
        borderRadius: 8,
    },
    typography: {
        fontFamily:
            '"Inter", "Segoe UI", Roboto, Arial, sans-serif',
        h4: {
            fontWeight: 750,
            letterSpacing: "-0.03em",
        },
        h6: {
            fontWeight: 700,
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
        MuiCard: {
            styleOverrides: {
                root: {
                    backgroundImage: "none",
                    backgroundColor: colors.paper,
                    border: `1px solid ${colors.border}`,
                    boxShadow: "0 14px 40px rgba(0, 0, 0, 0.18)",
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
                        backgroundColor: alpha(colors.primary, 0.06),
                    },
                    "&.Mui-selected": {
                        color: "#dfffea",
                        backgroundColor: alpha(colors.primary, 0.13),
                        boxShadow: `inset 3px 0 0 ${colors.primary}`,
                    },
                    "&.Mui-selected:hover": {
                        backgroundColor: alpha(colors.primary, 0.17),
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
