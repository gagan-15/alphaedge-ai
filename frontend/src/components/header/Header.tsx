import NotificationsNoneOutlinedIcon from "@mui/icons-material/NotificationsNoneOutlined";
import SearchRoundedIcon from "@mui/icons-material/SearchRounded";
import SettingsOutlinedIcon from "@mui/icons-material/SettingsOutlined";
import AppBar from "@mui/material/AppBar";
import Avatar from "@mui/material/Avatar";
import Box from "@mui/material/Box";
import IconButton from "@mui/material/IconButton";
import InputAdornment from "@mui/material/InputAdornment";
import TextField from "@mui/material/TextField";
import Toolbar from "@mui/material/Toolbar";
import Typography from "@mui/material/Typography";

function Header() {
    return (
        <AppBar
            position="fixed"
            sx={{
                left: {
                    xs: 76,
                    lg: 240,
                },
                width: {
                    xs: "calc(100% - 76px)",
                    lg: "calc(100% - 240px)",
                },
                zIndex: (theme) => theme.zIndex.drawer - 1,
            }}
        >
            <Toolbar
                sx={{
                    minHeight: {
                        xs: "64px !important",
                        md: "76px !important",
                    },
                    px: {
                        xs: 1.5,
                        sm: 2.5,
                    },
                    gap: 1.5,
                }}
            >
                <Box
                    sx={{
                        flex: 1,
                        minWidth: 0,
                        textAlign: {
                            xs: "left",
                            md: "center",
                        },
                    }}
                >
                    <Typography
                        component="div"
                        sx={{
                            fontSize: {
                                xs: "1.15rem",
                                md: "1.9rem",
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

                    <Typography
                        color="text.secondary"
                        sx={{
                            display: {
                                xs: "none",
                                md: "block",
                            },
                            mt: 0.5,
                            fontSize: "0.7rem",
                            letterSpacing: "0.12em",
                            textTransform: "uppercase",
                        }}
                    >
                        AI-Assisted Trading Intelligence Platform
                    </Typography>
                </Box>

                <TextField
                    size="small"
                    placeholder="Search"
                    aria-label="Search AlphaEdge AI"
                    sx={{
                        display: {
                            xs: "none",
                            xl: "block",
                        },
                        width: 210,
                        "& .MuiOutlinedInput-root": {
                            backgroundColor: "rgba(5, 12, 24, 0.7)",
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

                    <Avatar
                        aria-label="User account"
                        sx={{
                            ml: 0.5,
                            width: 30,
                            height: 30,
                            bgcolor: "primary.main",
                            color: "primary.contrastText",
                            fontSize: "0.75rem",
                            fontWeight: 800,
                        }}
                    >
                        GD
                    </Avatar>
                </Box>
            </Toolbar>
        </AppBar>
    );
}

export default Header;
