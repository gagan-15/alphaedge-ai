/**
 * AlphaEdge AI
 *
 * Sprint:
 *     2.62 - Application Navigation & Routing
 */

import { useLocation, useNavigate } from "react-router-dom";

import Drawer from "@mui/material/Drawer";
import Toolbar from "@mui/material/Toolbar";
import List from "@mui/material/List";
import ListItemButton from "@mui/material/ListItemButton";
import ListItemIcon from "@mui/material/ListItemIcon";
import ListItemText from "@mui/material/ListItemText";

import DashboardOutlinedIcon from "@mui/icons-material/DashboardOutlined";
import ShowChartOutlinedIcon from "@mui/icons-material/ShowChartOutlined";
import CandlestickChartOutlinedIcon from "@mui/icons-material/CandlestickChartOutlined";
import AccountBalanceWalletOutlinedIcon from "@mui/icons-material/AccountBalanceWalletOutlined";
import VisibilityOutlinedIcon from "@mui/icons-material/VisibilityOutlined";
import QueryStatsOutlinedIcon from "@mui/icons-material/QueryStatsOutlined";
import SmartToyOutlinedIcon from "@mui/icons-material/SmartToyOutlined";
import AssessmentOutlinedIcon from "@mui/icons-material/AssessmentOutlined";
import SettingsOutlinedIcon from "@mui/icons-material/SettingsOutlined";

const drawerWidth = 240;

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
                width: drawerWidth,
                flexShrink: 0,
                "& .MuiDrawer-paper": {
                    width: drawerWidth,
                    boxSizing: "border-box",
                    position: "fixed",
                    top: 64,
                    height: "calc(100% - 64px)",
                },
            }}
        >
            <Toolbar />

            <List sx={{ mt: 1 }}>
                {menuItems.map((item) => (
                    <ListItemButton
                        key={item.text}
                        selected={location.pathname === item.path}
                        onClick={() => navigate(item.path)}
                    >
                        <ListItemIcon>
                            {item.icon}
                        </ListItemIcon>

                        <ListItemText
                            primary={item.text}
                        />
                    </ListItemButton>
                ))}
            </List>
        </Drawer>
    );
}

export default Sidebar;