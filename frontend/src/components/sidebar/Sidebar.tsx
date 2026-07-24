import AccountBalanceWalletOutlinedIcon from "@mui/icons-material/AccountBalanceWalletOutlined";
import AssessmentOutlinedIcon from "@mui/icons-material/AssessmentOutlined";
import CandlestickChartOutlinedIcon from "@mui/icons-material/CandlestickChartOutlined";
import DashboardOutlinedIcon from "@mui/icons-material/DashboardOutlined";
import QueryStatsOutlinedIcon from "@mui/icons-material/QueryStatsOutlined";
import SettingsOutlinedIcon from "@mui/icons-material/SettingsOutlined";
import ShowChartOutlinedIcon from "@mui/icons-material/ShowChartOutlined";
import SmartToyOutlinedIcon from "@mui/icons-material/SmartToyOutlined";
import VisibilityOutlinedIcon from "@mui/icons-material/VisibilityOutlined";
import Box from "@mui/material/Box";
import Drawer from "@mui/material/Drawer";
import List from "@mui/material/List";
import ListItemButton from "@mui/material/ListItemButton";
import ListItemIcon from "@mui/material/ListItemIcon";
import ListItemText from "@mui/material/ListItemText";
import Typography from "@mui/material/Typography";
import { useLocation, useNavigate } from "react-router-dom";

const menuItems = [
    {
        text: "Dashboard",
        icon: <DashboardOutlinedIcon />,
        path: "/dashboard",
    },
    {
        text: "Scanner",
        icon: <ShowChartOutlinedIcon />,
        path: "/scanner",
    },
    {
        text: "Signals",
        icon: <CandlestickChartOutlinedIcon />,
        path: "/signals",
    },
    {
        text: "My Holdings",
        icon: <AccountBalanceWalletOutlinedIcon />,
        path: "/holdings",
    },
    {
        text: "Watchlist",
        icon: <VisibilityOutlinedIcon />,
        path: "/watchlist",
    },
    {
        text: "Backtest",
        icon: <QueryStatsOutlinedIcon />,
        path: "/backtest",
    },
    {
        text: "AI Assistant",
        icon: <SmartToyOutlinedIcon />,
        path: "/ai-assistant",
    },
    {
        text: "Reports",
        icon: <AssessmentOutlinedIcon />,
        path: "/reports",
    },
    {
        text: "Settings",
        icon: <SettingsOutlinedIcon />,
        path: "/settings",
    },
];

function Sidebar() {
    const navigate = useNavigate();
    const location = useLocation();

    return (
        <Drawer
            variant="permanent"
            sx={{
                width: {
                    xs: 76,
                    lg: 240,
                },
                flexShrink: 0,
                "& .MuiDrawer-paper": {
                    width: {
                        xs: 76,
                        lg: 240,
                    },
                    boxSizing: "border-box",
                    overflowX: "hidden",
                },
            }}
        >
            <Box
                sx={{
                    minHeight: {
                        xs: 64,
                        md: 76,
                    },
                    display: "flex",
                    alignItems: "center",
                    justifyContent: {
                        xs: "center",
                        lg: "flex-start",
                    },
                    px: {
                        xs: 1,
                        lg: 2,
                    },
                    borderBottom: "1px solid",
                    borderColor: "divider",
                }}
            >
                <Box
                    sx={{
                        width: 30,
                        height: 30,
                        borderRadius: 1.5,
                        display: "grid",
                        placeItems: "center",
                        color: "primary.main",
                        border: "1px solid",
                        borderColor: "primary.main",
                        fontWeight: 900,
                    }}
                >
                    A
                </Box>

                <Typography
                    sx={{
                        display: {
                            xs: "none",
                            lg: "block",
                        },
                        ml: 1,
                        fontWeight: 800,
                        letterSpacing: "-0.02em",
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

            <List
                component="nav"
                aria-label="Main navigation"
                sx={{
                    px: {
                        xs: 1,
                        lg: 1.25,
                    },
                    py: 1.5,
                }}
            >
                {menuItems.map((item) => (
                    <ListItemButton
                        key={item.text}
                        selected={location.pathname === item.path}
                        onClick={() => navigate(item.path)}
                        aria-label={item.text}
                        sx={{
                            minHeight: 42,
                            mb: 0.5,
                            px: {
                                xs: 1.25,
                                lg: 1.5,
                            },
                            justifyContent: {
                                xs: "center",
                                lg: "flex-start",
                            },
                        }}
                    >
                        <ListItemIcon
                            sx={{
                                minWidth: {
                                    xs: 0,
                                    lg: 36,
                                },
                                justifyContent: "center",
                                "& .MuiSvgIcon-root": {
                                    fontSize: "1.15rem",
                                },
                            }}
                        >
                            {item.icon}
                        </ListItemIcon>

                        <ListItemText
                            primary={item.text}
                            sx={{
                                display: {
                                    xs: "none",
                                    lg: "block",
                                },
                            }}
                            slotProps={{
                                primary: {
                                    sx: {
                                        fontSize: "0.82rem",
                                        fontWeight: 600,
                                    },
                                },
                            }}
                        />
                    </ListItemButton>
                ))}
            </List>
        </Drawer>
    );
}

export default Sidebar;
