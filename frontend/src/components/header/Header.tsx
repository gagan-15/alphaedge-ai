import NotificationsNoneOutlinedIcon from "@mui/icons-material/NotificationsNoneOutlined";
import SearchRoundedIcon from "@mui/icons-material/SearchRounded";
import SettingsOutlinedIcon from "@mui/icons-material/SettingsOutlined";
import LogoutOutlinedIcon from "@mui/icons-material/LogoutOutlined";
import HelpOutlineRoundedIcon from "@mui/icons-material/HelpOutlineRounded";
import DarkModeOutlinedIcon from "@mui/icons-material/DarkModeOutlined";
import LightModeOutlinedIcon from "@mui/icons-material/LightModeOutlined";
import AppBar from "@mui/material/AppBar";
import Avatar from "@mui/material/Avatar";
import Box from "@mui/material/Box";
import IconButton from "@mui/material/IconButton";
import InputAdornment from "@mui/material/InputAdornment";
import TextField from "@mui/material/TextField";
import Toolbar from "@mui/material/Toolbar";
import Typography from "@mui/material/Typography";
import Chip from "@mui/material/Chip";
import Tooltip from "@mui/material/Tooltip";
import { useNavigate } from "react-router-dom";

import { LOCAL_DEMO_MODE, useAuth } from "../../auth/AuthState";
import { useThemeMode } from "../../theme/ThemeModeState";

function Header() {
    const navigate = useNavigate();
    const { user, logout } = useAuth();
    const { mode, toggleMode } = useThemeMode();

    async function handleLogout() {
        await logout();
        navigate("/", { replace: true });
    }

    return (
        <AppBar
            position="fixed"
            sx={{
                left: {
                    xs: 64,
                    lg: 224,
                },
                width: {
                    xs: "calc(100% - 64px)",
                    lg: "calc(100% - 224px)",
                },
                zIndex: (theme) => theme.zIndex.drawer - 1,
            }}
        >
            <Toolbar
                sx={{
                    minHeight: {
                        xs: "64px !important",
                        md: "70px !important",
                    },
                    px: {
                        xs: 1.5,
                        sm: 2.5,
                    },
                    gap: 1,
                }}
            >
                <Box
                    sx={{
                        flex: 1,
                        minWidth: 0,
                        textAlign: "left",
                    }}
                >
                    <Typography
                        component="div"
                        sx={{
                            display: { xs: "block", md: "none" },
                            fontSize: {
                                xs: "1.15rem",
                                md: "1.55rem",
                            },
                            fontWeight: 800,
                            letterSpacing: "-0.04em",
                            lineHeight: 1.05,
                        }}
                    >
                        AlphaEdge{" "}
                        <Box
                            component="span"
                            sx={{ color: "primary.main" }}
                        >
                            AI
                        </Box>
                    </Typography>

                </Box>

                <TextField
                    size="small"
                    placeholder="Search (Ctrl + K)"
                    aria-label="Search AlphaEdge AI"
                    sx={{
                        display: {
                            xs: "none",
                            xl: "block",
                        },
                        width: 344,
                        "& .MuiOutlinedInput-root": {
                            backgroundColor: (theme) => theme.palette.mode === "dark" ? "rgba(5, 12, 24, 0.7)" : "rgba(255,255,255,.84)",
                            fontSize: "0.78rem",
                        },
                    }}
                    slotProps={{
                        input: {
                            startAdornment: (
                                <InputAdornment position="start">
                                    <SearchRoundedIcon fontSize="small" />
                                </InputAdornment>
                            ),
                        },
                    }}
                />

                <Box
                    sx={{
                        display: "flex",
                        alignItems: "center",
                        gap: 0.25,
                    }}
                >
                    {LOCAL_DEMO_MODE && (
                        <Chip
                            label="LOCAL DEMO"
                            color="warning"
                            size="small"
                            sx={{ display: { xs: "none", sm: "flex" } }}
                        />
                    )}
                    <IconButton
                        aria-label="Notifications"
                        color="inherit"
                        size="small"
                    >
                        <NotificationsNoneOutlinedIcon fontSize="small" />
                    </IconButton>

                    <IconButton
                        aria-label="Settings"
                        color="inherit"
                        size="small"
                        sx={{
                            display: {
                                xs: "none",
                                sm: "inline-flex",
                            },
                        }}
                    >
                        <SettingsOutlinedIcon fontSize="small" />
                    </IconButton>

                    <IconButton
                        aria-label="Help"
                        color="inherit"
                        size="small"
                        sx={{ display: { xs: "none", md: "inline-flex" } }}
                    >
                        <HelpOutlineRoundedIcon fontSize="small" />
                    </IconButton>

                    <Box
                        sx={{
                            display: { xs: "none", xl: "block" },
                            textAlign: "right",
                            ml: 0.75,
                            maxWidth: 130,
                        }}
                    >
                        <Typography sx={{ fontSize: "0.72rem", fontWeight: 750, lineHeight: 1.15 }} noWrap>
                            {user?.full_name ?? "AlphaEdge User"}
                        </Typography>
                        <Typography color="text.secondary" sx={{ fontSize: "0.6rem", lineHeight: 1.2 }} noWrap>
                            Research workspace
                        </Typography>
                    </Box>
                    <Avatar
                        aria-label={user?.full_name ?? "User account"}
                        sx={{
                            ml: 0.5,
                            width: 30,
                            height: 30,
                            background: "linear-gradient(145deg,#2563eb,#8b5cf6)",
                            color: "#fff",
                            border: "1px solid rgba(255,255,255,.18)",
                            boxShadow: "0 0 16px rgba(99,102,241,.24)",
                            fontSize: "0.75rem",
                            fontWeight: 800,
                        }}
                    >
                        {user?.full_name
                            ?.split(" ")
                            .map((part) => part[0])
                            .join("")
                            .slice(0, 2)
                            .toUpperCase() ?? "AE"}
                    </Avatar>
                    <Tooltip title={`Switch to ${mode === "dark" ? "light" : "dark"} theme`}>
                        <IconButton
                            aria-label={`Switch to ${mode === "dark" ? "light" : "dark"} theme`}
                            color="inherit"
                            size="small"
                            onClick={toggleMode}
                        >
                            {mode === "dark" ? <LightModeOutlinedIcon fontSize="small" /> : <DarkModeOutlinedIcon fontSize="small" />}
                        </IconButton>
                    </Tooltip>
                    <Tooltip title="Log out">
                        <IconButton
                            aria-label="Log out"
                            color="inherit"
                            size="small"
                            onClick={() => void handleLogout()}
                        >
                            <LogoutOutlinedIcon fontSize="small" />
                        </IconButton>
                    </Tooltip>
                </Box>
            </Toolbar>
        </AppBar>
    );
}

export default Header;
