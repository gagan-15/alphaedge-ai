import AccountBalanceWalletOutlinedIcon from "@mui/icons-material/AccountBalanceWalletOutlined";
import AssessmentOutlinedIcon from "@mui/icons-material/AssessmentOutlined";
import CandlestickChartOutlinedIcon from "@mui/icons-material/CandlestickChartOutlined";
import DashboardOutlinedIcon from "@mui/icons-material/DashboardOutlined";
import QueryStatsOutlinedIcon from "@mui/icons-material/QueryStatsOutlined";
import SettingsOutlinedIcon from "@mui/icons-material/SettingsOutlined";
import ShowChartOutlinedIcon from "@mui/icons-material/ShowChartOutlined";
import SmartToyOutlinedIcon from "@mui/icons-material/SmartToyOutlined";
import VisibilityOutlinedIcon from "@mui/icons-material/VisibilityOutlined";
import AddAlertOutlinedIcon from "@mui/icons-material/AddAlertOutlined";
import CalculateOutlinedIcon from "@mui/icons-material/CalculateOutlined";
import CalendarMonthOutlinedIcon from "@mui/icons-material/CalendarMonthOutlined";
import NewspaperOutlinedIcon from "@mui/icons-material/NewspaperOutlined";
import PieChartOutlineOutlinedIcon from "@mui/icons-material/PieChartOutlineOutlined";
import TableChartOutlinedIcon from "@mui/icons-material/TableChartOutlined";
import SecurityOutlinedIcon from "@mui/icons-material/SecurityOutlined";
import AccountTreeOutlinedIcon from "@mui/icons-material/AccountTreeOutlined";
import Box from "@mui/material/Box";
import Drawer from "@mui/material/Drawer";
import List from "@mui/material/List";
import ListItemButton from "@mui/material/ListItemButton";
import ListItemIcon from "@mui/material/ListItemIcon";
import ListItemText from "@mui/material/ListItemText";
import Typography from "@mui/material/Typography";
import { useLocation, useNavigate } from "react-router-dom";
import BrandLogo from "../brand/BrandLogo";

const menuItems = [
    {
        section: "OVERVIEW",
        text: "Dashboard",
        icon: <DashboardOutlinedIcon />,
        path: "/dashboard",
    },
    {
        section: "MARKET",
        text: "Scanner",
        icon: <ShowChartOutlinedIcon />,
        path: "/scanner",
    },
    {
        section: "MARKET",
        text: "Market Overview",
        icon: <QueryStatsOutlinedIcon />,
        path: "/market-overview",
    },
    {
        section: "MARKET",
        text: "Signals",
        icon: <CandlestickChartOutlinedIcon />,
        path: "/signals",
    },
    {
        section: "MARKET",
        text: "My Holdings",
        icon: <AccountBalanceWalletOutlinedIcon />,
        path: "/holdings",
    },
    {
        section: "MARKET",
        text: "Watchlist",
        icon: <VisibilityOutlinedIcon />,
        path: "/watchlist",
    },
    {
        section: "MARKET",
        text: "Market Breadth",
        icon: <PieChartOutlineOutlinedIcon />,
        path: "/market-breadth",
    },
    {
        section: "MARKET",
        text: "News & Insights",
        icon: <NewspaperOutlinedIcon />,
        path: "/news",
    },
    {
        section: "ANALYSIS",
        text: "Backtest",
        icon: <QueryStatsOutlinedIcon />,
        path: "/backtest",
    },
    {
        section: "ANALYSIS",
        text: "Strategies",
        icon: <AccountTreeOutlinedIcon />,
        path: "/strategies",
    },
    {
        section: "ANALYSIS",
        text: "AI Assistant",
        icon: <SmartToyOutlinedIcon />,
        path: "/ai-assistant",
    },
    {
        section: "ANALYSIS",
        text: "Reports",
        icon: <AssessmentOutlinedIcon />,
        path: "/reports",
    },
    {
        section: "TOOLS",
        text: "Alerts",
        icon: <AddAlertOutlinedIcon />,
        path: "/alerts",
    },
    {
        section: "TOOLS",
        text: "Economic Calendar",
        icon: <CalendarMonthOutlinedIcon />,
        path: "/economic-calendar",
    },
    {
        section: "TOOLS",
        text: "Option Chain",
        icon: <TableChartOutlinedIcon />,
        path: "/option-chain",
    },
    {
        section: "TOOLS",
        text: "Calculators",
        icon: <CalculateOutlinedIcon />,
        path: "/calculators",
    },
    {
        section: "TOOLS",
        text: "Risk Management",
        icon: <SecurityOutlinedIcon />,
        path: "/risk-management",
    },
    {
        section: "ACCOUNT",
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
                    xs: 64,
                    lg: 224,
                },
                flexShrink: 0,
                "& .MuiDrawer-paper": {
                    width: {
                        xs: 64,
                        lg: 224,
                    },
                    boxSizing: "border-box",
                    overflowX: "hidden",
                    scrollbarWidth: "thin",
                    scrollbarColor: "#263a56 transparent",
                },
            }}
        >
            <Box
                sx={{
                    minHeight: {
                        xs: 56,
                        md: 70,
                    },
                    display: "flex",
                    alignItems: "center",
                    justifyContent: {
                        xs: "center",
                        lg: "flex-start",
                    },
                    px: {
                        xs: 1,
                        lg: 2.25,
                    },
                    borderBottom: "1px solid",
                    borderColor: "divider",
                }}
            >
                <Box sx={{ display: { xs: "none", lg: "block" } }}><BrandLogo /></Box>
                <Box sx={{ display: { xs: "block", lg: "none" } }}><BrandLogo compact /></Box>
            </Box>

            <List
                component="nav"
                aria-label="Main navigation"
                sx={{
                    px: {
                        xs: 1,
                        lg: 1.25,
                    },
                    pt: 1.25,
                    pb: 2,
                }}
            >
                {menuItems.map((item, index) => (
                    <Box key={item.text}>
                    {(index === 0 || menuItems[index - 1].section !== item.section) && (
                        <Typography
                            variant="caption"
                            color="text.secondary"
                            sx={{
                                display: { xs: "none", lg: "block" },
                                px: 1.5,
                                pt: index === 0 ? 0 : 1,
                                pb: 0.5,
                                fontSize: "0.58rem",
                                letterSpacing: "0.12em",
                                fontWeight: 800,
                            }}
                        >
                            {item.section}
                        </Typography>
                    )}
                    <ListItemButton
                        selected={location.pathname === item.path}
                        onClick={() => navigate(item.path)}
                        aria-label={item.text}
                        sx={{
                            minHeight: 38,
                            mb: 0.35,
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
                                    fontSize: "1.2rem",
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
                                        fontSize: "0.84rem",
                                        fontWeight: 600,
                                    },
                                },
                            }}
                        />
                    </ListItemButton>
                    </Box>
                ))}
            </List>
        </Drawer>
    );
}

export default Sidebar;
