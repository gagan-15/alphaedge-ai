/**
 * AlphaEdge AI
 *
 * Sprint:
 *     2.60 - Professional Application Shell
 */

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
import SmartToyOutlinedIcon from "@mui/icons-material/SmartToyOutlined";
import SettingsOutlinedIcon from "@mui/icons-material/SettingsOutlined";

const drawerWidth = 240;

function Sidebar() {
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
                <ListItemButton selected>
                    <ListItemIcon>
                        <DashboardOutlinedIcon />
                    </ListItemIcon>
                    <ListItemText primary="Dashboard" />
                </ListItemButton>

                <ListItemButton>
                    <ListItemIcon>
                        <ShowChartOutlinedIcon />
                    </ListItemIcon>
                    <ListItemText primary="Scanner" />
                </ListItemButton>

                <ListItemButton>
                    <ListItemIcon>
                        <CandlestickChartOutlinedIcon />
                    </ListItemIcon>
                    <ListItemText primary="Signals" />
                </ListItemButton>

                <ListItemButton>
                    <ListItemIcon>
                        <AccountBalanceWalletOutlinedIcon />
                    </ListItemIcon>
                    <ListItemText primary="Portfolio" />
                </ListItemButton>

                <ListItemButton>
                    <ListItemIcon>
                        <SmartToyOutlinedIcon />
                    </ListItemIcon>
                    <ListItemText primary="AI Assistant" />
                </ListItemButton>

                <ListItemButton>
                    <ListItemIcon>
                        <SettingsOutlinedIcon />
                    </ListItemIcon>
                    <ListItemText primary="Settings" />
                </ListItemButton>
            </List>
        </Drawer>
    );
}

export default Sidebar;