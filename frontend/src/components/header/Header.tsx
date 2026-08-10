import NotificationsNoneOutlinedIcon from "@mui/icons-material/NotificationsNoneOutlined";
import SearchRoundedIcon from "@mui/icons-material/SearchRounded";
import AppBar from "@mui/material/AppBar";
import Avatar from "@mui/material/Avatar";
import Box from "@mui/material/Box";
import IconButton from "@mui/material/IconButton";
import InputAdornment from "@mui/material/InputAdornment";
import Menu from "@mui/material/Menu";
import MenuItem from "@mui/material/MenuItem";
import Stack from "@mui/material/Stack";
import TextField from "@mui/material/TextField";
import Toolbar from "@mui/material/Toolbar";
import Typography from "@mui/material/Typography";
import { useState } from "react";
import { Link as RouterLink, useLocation, useNavigate } from "react-router-dom";

import { useAuth } from "../../auth/AuthState";
import BrandLogo from "../brand/BrandLogo";

const navigation = [
    ["Dashboard", "/dashboard"],
    ["Markets", "/market-overview"],
    ["Signals", "/signals"],
    ["Watchlist", "/watchlist"],
    ["Portfolio", "/holdings"],
    ["Alerts", "/alerts"],
    ["Reports", "/reports"],
] as const;

export default function Header() {
    const { pathname } = useLocation();
    const navigate = useNavigate();
    const { user, logout } = useAuth();
    const [profileAnchor, setProfileAnchor] = useState<HTMLElement | null>(null);

    async function signOut() {
        setProfileAnchor(null);
        await logout();
        navigate("/", { replace: true });
    }

    return (
        <AppBar position="fixed" elevation={0} sx={{ left: 0, width: "100%", height: 72, zIndex: (theme) => theme.zIndex.drawer + 2, bgcolor: "#ffffff", color: "#111827", borderBottom: "1px solid #E5E7EB", boxShadow: "none" }}>
            <Toolbar sx={{ minHeight: "72px !important", height: 72, px: { xs: 1.5, md: 3 }, gap: { xs: 1, md: 3 }, alignItems: "center" }}>
                <Box component={RouterLink} to="/dashboard" sx={{ display: "flex", alignItems: "center", color: "inherit", textDecoration: "none", flex: "0 0 auto" }}>
                    <BrandLogo compact={false} />
                </Box>
                <Stack component="nav" direction="row" sx={{ display: { xs: "none", lg: "flex" }, alignSelf: "stretch", alignItems: "stretch", gap: 1 }}>
                    {navigation.map(([label, path]) => {
                        const active = pathname === path || (path === "/dashboard" && pathname.startsWith("/stock-details/"));
                        return <Box key={path} component={RouterLink} to={path} sx={{ position: "relative", display: "flex", px: 1, alignItems: "center", color: active ? "primary.main" : "#667085", textDecoration: "none", fontSize: "0.76rem", fontWeight: active ? 600 : 500, transition: "color 160ms ease", "&:hover": { color: "#1D2939" }, "&::after": { content: '""', position: "absolute", height: 2, left: 8, right: 8, bottom: 0, borderRadius: 2, bgcolor: "primary.main", transform: active ? "scaleX(1)" : "scaleX(0)", transformOrigin: "center", transition: "transform 160ms ease" } }}>{label}</Box>;
                    })}
                </Stack>
                <Box sx={{ flex: 1 }} />
                <TextField size="small" placeholder="Search stocks, indices..." aria-label="Search AlphaEdge AI" onChange={(event) => window.dispatchEvent(new CustomEvent("alphaedge:global-search", { detail: event.target.value }))} sx={{ display: { xs: "none", md: "block" }, width: { md: 340, lg: 370, xl: 400 }, minWidth: { md: 320, lg: 340, xl: 370 }, maxWidth: 400, flex: "0 0 auto", "& .MuiInputBase-root": { width: "100%" }, "& .MuiOutlinedInput-root": { height: 40, bgcolor: "#ffffff", fontSize: "0.74rem", borderRadius: "12px", "&:hover .MuiOutlinedInput-notchedOutline": { borderColor: "#C9D0DB" }, "&.Mui-focused .MuiOutlinedInput-notchedOutline": { borderColor: "primary.main", borderWidth: 1 } }, "& .MuiOutlinedInput-notchedOutline": { borderColor: "#DFE5EE" }, "& input": { py: 0, height: 40, boxSizing: "border-box" }, "& input::placeholder": { color: "#667085", opacity: 1 }, "& .MuiInputAdornment-root": { color: "#748197", alignItems: "center" } }} slotProps={{ input: { startAdornment: <InputAdornment position="start"><SearchRoundedIcon sx={{ fontSize: 18 }} /></InputAdornment> } }} />
                <IconButton size="small" aria-label="Notifications" sx={{ color: "#667085", transition: "color 160ms ease", "&:hover": { color: "primary.main", bgcolor: "#F4F1FF" } }}><NotificationsNoneOutlinedIcon fontSize="small" /></IconButton>
                <Stack
                    component="button"
                    type="button"
                    direction="row"
                    spacing={0.8}
                    onClick={(event) => setProfileAnchor(event.currentTarget)}
                    aria-label="Open profile menu"
                    sx={{ alignItems: "center", border: 0, bgcolor: "transparent", p: .5, borderRadius: 1.5, cursor: "pointer", color: "inherit", "&:hover": { bgcolor: "#F7F8FC" } }}
                >
                    <Avatar sx={{ width: 30, height: 30, bgcolor: "primary.main", fontSize: "0.7rem", fontWeight: 700 }}>{user?.full_name?.split(" ").map((part) => part[0]).join("").slice(0, 2).toUpperCase() ?? "AE"}</Avatar>
                    <Box sx={{ display: { xs: "none", xl: "block" } }}><Typography sx={{ fontSize: "0.7rem", fontWeight: 700, lineHeight: 1.15 }}>{user?.full_name ?? "AlphaEdge User"}</Typography><Typography color="text.secondary" sx={{ fontSize: "0.58rem" }}>Research workspace</Typography></Box>
                </Stack>
                <Menu anchorEl={profileAnchor} open={Boolean(profileAnchor)} onClose={() => setProfileAnchor(null)} anchorOrigin={{ vertical: "bottom", horizontal: "right" }} transformOrigin={{ vertical: "top", horizontal: "right" }}>
                    <MenuItem component={RouterLink} to="/settings" onClick={() => setProfileAnchor(null)}>Settings</MenuItem>
                    <MenuItem onClick={signOut}>Log Out</MenuItem>
                </Menu>
            </Toolbar>
        </AppBar>
    );
}
