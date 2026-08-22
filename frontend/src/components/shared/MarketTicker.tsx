import RefreshRoundedIcon from "@mui/icons-material/RefreshRounded";
import Box from "@mui/material/Box";
import IconButton from "@mui/material/IconButton";
import Stack from "@mui/material/Stack";
import Tooltip from "@mui/material/Tooltip";
import Typography from "@mui/material/Typography";

import { useMarketIntelligence } from "../../market-intelligence/MarketIntelligenceState";

export default function MarketTicker() {
    const { dashboard, lastUpdated, isLoading, refresh } = useMarketIntelligence();
    const market = dashboard?.market;
    const items = [
        ["NIFTY 50", market?.nifty50, market?.nifty_change],
        ["SENSEX", market?.sensex, market?.sensex_change],
        ["BANK NIFTY", market?.bank_nifty, market?.bank_nifty_change],
        ["INDIA VIX", market?.india_vix, market?.india_vix_change],
    ] as const;

    return (
        <Box
            aria-label="Market summary"
            sx={{
                position: "fixed",
                top: 80,
                left: { xs: 12, md: 24 },
                right: { xs: 12, md: 24 },
                zIndex: 1199,
                height: 56,
                px: { xs: 1.5, md: 1.5 },
                display: "flex",
                alignItems: "center",
                overflowX: "auto",
                border: "1px solid",
                borderColor: "divider",
                borderRadius: 1,
                bgcolor: "#ffffff",
                boxShadow: "0 3px 12px rgba(28,45,72,.035)",
                "& + main": { pt: "156px" },
            }}
        >
            <Stack direction="row" sx={{ width: "100%", minWidth: 760, alignItems: "center" }}>
                {items.map(([label, value, change], index) => {
                    const positive = (change ?? 0) >= 0;
                    return (
                        <Box
                            key={label}
                            sx={{
                                minWidth: 160,
                                px: 3,
                                py: .75,
                                position: "relative",
                                borderRadius: 1,
                                cursor: "pointer",
                                transition: "background-color 150ms ease",
                                "&:hover": { bgcolor: "#F8FAFC" },
                                "&::before": index === 0 ? undefined : {
                                    content: '""',
                                    position: "absolute",
                                    left: 0,
                                    top: "50%",
                                    width: "1px",
                                    height: 20,
                                    bgcolor: "#E5E7EB",
                                    transform: "translateY(-50%)",
                                },
                            }}
                        >
                            <Stack direction="row" spacing={0.8} sx={{ alignItems: "baseline", whiteSpace: "nowrap" }}>
                                <Typography sx={{ color: "#7a8699", fontSize: "0.62rem", lineHeight: 1.25, fontWeight: 500, letterSpacing: ".02em" }}>{label}</Typography>
                                <Typography sx={{ fontSize: "0.75rem", lineHeight: 1.25, fontWeight: 650, fontVariantNumeric: "tabular-nums" }}>{value ? value.toLocaleString("en-IN", { maximumFractionDigits: 2 }) : "—"}</Typography>
                                {change !== undefined && <Typography sx={{ color: positive ? "success.main" : "error.main", fontSize: "0.62rem", lineHeight: 1.25, fontWeight: 600, fontVariantNumeric: "tabular-nums" }}>{positive ? "▲ +" : "▼ "}{change.toFixed(2)}%</Typography>}
                            </Stack>
                        </Box>
                    );
                })}
                <Box sx={{ ml: "auto", pl: 2.25, flex: "0 0 auto" }}>
                    <Stack direction="row" spacing={0.75} sx={{ alignItems: "center" }}>
                        <Box sx={{ textAlign: "right" }}>
                            <Typography color="text.secondary" sx={{ fontSize: "0.54rem" }}>Delayed data · Last updated</Typography>
                            <Typography sx={{ fontSize: "0.64rem", fontWeight: 600 }}>{lastUpdated ? lastUpdated.toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit" }) : "Waiting"}</Typography>
                        </Box>
                        <Tooltip title="Refresh market data"><span><IconButton size="small" disabled={isLoading} onClick={() => void refresh()}><RefreshRoundedIcon sx={{ fontSize: 17 }} /></IconButton></span></Tooltip>
                    </Stack>
                </Box>
            </Stack>
        </Box>
    );
}
