import Box from "@mui/material/Box";
import Chip from "@mui/material/Chip";
import Typography from "@mui/material/Typography";
import { alpha, keyframes } from "@mui/material/styles";
import { useMarketIntelligence } from "../../market-intelligence/MarketIntelligenceState";

interface TickerQuote {
    symbol: string;
    price: string;
    change: string;
}

const tickerScroll = keyframes`
    from { transform: translate3d(0, 0, 0); }
    to { transform: translate3d(-50%, 0, 0); }
`;

function QuoteGroup({ quotes, duplicate = false }: { quotes: TickerQuote[]; duplicate?: boolean }) {
    return (
        <Box
            aria-hidden={duplicate || undefined}
            sx={{
                display: "flex",
                flex: "0 0 auto",
                alignItems: "center",
                gap: { xs: 3, sm: 5, lg: 7 },
                pr: { xs: 3, sm: 5, lg: 7 },
            }}
        >
            {quotes.map(({ symbol, price, change }) => {
                const positive = change.startsWith("+");
                return (
                    <Box
                        key={symbol}
                        aria-disabled="true"
                        sx={{
                            display: "flex",
                            alignItems: "center",
                            gap: 0.85,
                            whiteSpace: "nowrap",
                            cursor: "pointer",
                            borderRadius: 1,
                            px: 0.5,
                            py: 0.35,
                            transition: "filter 160ms ease, background-color 160ms ease",
                            "&:hover": {
                                filter: "brightness(1.2)",
                                bgcolor: "action.hover",
                            },
                        }}
                    >
                        <Typography
                            component="span"
                            sx={{
                                color: positive ? "success.main" : "error.main",
                                fontSize: "0.7rem",
                                fontWeight: 800,
                            }}
                        >
                            {positive ? "▲" : "▼"}
                        </Typography>
                        <Typography component="span" sx={{ color: "text.primary", fontSize: "0.72rem", fontWeight: 700 }}>
                            {symbol}
                        </Typography>
                        <Typography component="span" sx={{ color: "text.primary", fontSize: "0.72rem" }}>
                            ₹{price}
                        </Typography>
                        <Typography
                            component="span"
                            sx={{
                                color: positive ? "success.main" : "error.main",
                                fontSize: "0.72rem",
                                fontWeight: 700,
                            }}
                        >
                            {change}
                        </Typography>
                    </Box>
                );
            })}
        </Box>
    );
}

function DashboardTicker() {
    const { dashboard } = useMarketIntelligence();
    const market = dashboard?.market;
    const quotes: TickerQuote[] = market ? [
        { symbol: "NIFTY 50", price: market.nifty50.toLocaleString("en-IN", { maximumFractionDigits: 2 }), change: `${market.nifty_change >= 0 ? "+" : ""}${market.nifty_change.toFixed(2)}%` },
        { symbol: "SENSEX", price: market.sensex.toLocaleString("en-IN", { maximumFractionDigits: 2 }), change: `${market.sensex_change >= 0 ? "+" : ""}${market.sensex_change.toFixed(2)}%` },
        { symbol: "BANK NIFTY", price: market.bank_nifty.toLocaleString("en-IN", { maximumFractionDigits: 2 }), change: `${market.bank_nifty_change >= 0 ? "+" : ""}${market.bank_nifty_change.toFixed(2)}%` },
        { symbol: "INDIA VIX", price: market.india_vix.toLocaleString("en-IN", { maximumFractionDigits: 2 }), change: `${market.india_vix_change >= 0 ? "+" : ""}${market.india_vix_change.toFixed(2)}%` },
    ].filter((quote) => quote.price !== "0") : [];
    const displayQuotes = quotes.length ? quotes : [
        { symbol: "MARKET DATA", price: "Refreshing", change: "0.00%" },
    ];
    const status = market?.data_status?.toUpperCase() ?? "REFRESHING";
    return (
        <Box
            aria-label="Delayed demo market ticker"
            sx={{
                position: "fixed",
                top: { xs: 64, md: 70 },
                left: { xs: 64, lg: 224 },
                right: 0,
                zIndex: 1199,
                height: 44,
                display: "flex",
                alignItems: "center",
                overflow: "hidden",
                borderTop: "1px solid",
                borderBottom: "1px solid",
                borderColor: "divider",
                bgcolor: (theme) => theme.palette.mode === "dark" ? "rgba(5,14,29,.98)" : "rgba(255,255,255,.98)",
                color: "text.primary",
                boxShadow: (theme) => theme.palette.mode === "light" ? "0 5px 18px rgba(28,45,72,.06)" : "none",
                "& + main": {
                    pt: { xs: "122px", md: "128px" },
                },
                "&:hover .dashboard-ticker-track": {
                    animationPlayState: "paused",
                },
            }}
        >
            <Box
                sx={{
                    alignSelf: "stretch",
                    display: "flex",
                    alignItems: "center",
                    px: { xs: 1, sm: 1.5 },
                    flex: "0 0 auto",
                    zIndex: 1,
                    bgcolor: "background.paper",
                    borderRight: "1px solid",
                    borderColor: "divider",
                }}
            >
                <Chip
                    label={status}
                    size="small"
                    sx={{
                        height: 25,
                        color: "#111827",
                        bgcolor: "warning.main",
                        border: (theme) => `1px solid ${alpha(theme.palette.warning.light, 0.8)}`,
                        boxShadow: (theme) => `0 0 0 3px ${alpha(theme.palette.warning.main, 0.1)}`,
                        fontSize: "0.62rem",
                        fontWeight: 900,
                        letterSpacing: "0.035em",
                    }}
                />
            </Box>

            <Box sx={{ minWidth: 0, flex: 1, overflow: "hidden" }}>
                <Box
                    className="dashboard-ticker-track"
                    sx={{
                        display: "flex",
                        width: "max-content",
                        alignItems: "center",
                        willChange: "transform",
                        animation: `${tickerScroll} 30s linear infinite`,
                        "@media (prefers-reduced-motion: reduce)": {
                            animation: "none",
                        },
                    }}
                >
                    <QuoteGroup quotes={displayQuotes} />
                    <QuoteGroup quotes={displayQuotes} duplicate />
                </Box>
            </Box>
        </Box>
    );
}

function MarketTicker() {
    return <DashboardTicker />;
}

export default MarketTicker;
