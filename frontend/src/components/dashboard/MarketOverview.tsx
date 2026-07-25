/**
 * Market Overview.
 *
 * Sprint:
 *     2.58 - Market Overview
 */

import TrendingDownIcon from "@mui/icons-material/TrendingDown";
import TrendingUpIcon from "@mui/icons-material/TrendingUp";

import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Typography from "@mui/material/Typography";
import Box from "@mui/material/Box";

import type { MarketOverviewResult } from "../../types/dashboard";

interface MarketOverviewProps {
    market: MarketOverviewResult;
}

function MarketOverview({
    market,
}: MarketOverviewProps) {
    const items = [
        {
            title: "NIFTY 50",
            value: market.nifty50,
            change: market.nifty_change,
        },
        {
            title: "SENSEX",
            value: market.sensex,
            change: market.sensex_change,
        },
        {
            title: "BANK NIFTY",
            value: market.bank_nifty,
            change: market.bank_nifty_change,
        },
        {
            title: "INDIA VIX",
            value: market.india_vix,
            change: market.india_vix_change,
        },
        {
            title: "FINNIFTY",
            value: 24125.2,
            change: 1.02,
        },
        {
            title: "MARKET BREADTH",
            value: 1682,
            change: 62,
        },
    ];

    return (
        <Box
            sx={{
                display: "grid",
                gridTemplateColumns: {
                    xs: "1fr",
                    sm: "repeat(2, minmax(0, 1fr))",
                    lg: "repeat(3, minmax(0, 1fr))",
                    xl: "repeat(6, minmax(0, 1fr))",
                },
                gap: 1.25,
            }}
        >
            {items.map((item) => (
                <Box
                    key={item.title}
                >
                    <Card
                        elevation={2}
                        sx={{
                            height: "100%",
                        }}
                    >
                        <CardContent sx={{ p: "14px !important" }}>
                            <Typography
                                variant="body2"
                                color="text.secondary"
                            >
                                {item.title}
                            </Typography>

                            <Typography
                                variant="h6"
                                sx={{
                                    mt: 0.5,
                                    fontWeight: 600,
                                }}
                            >
                                {item.value.toLocaleString()}
                            </Typography>

                            <Box
                                sx={{
                                    display: "flex",
                                    alignItems: "center",
                                    gap: 0.5,
                                    mt: 0.5,
                                    color:
                                        item.change >= 0
                                            ? "success.main"
                                            : "error.main",
                                }}
                            >
                                {item.change >= 0 ? (
                                    <TrendingUpIcon fontSize="small" />
                                ) : (
                                    <TrendingDownIcon fontSize="small" />
                                )}

                                <Typography
                                    variant="body2"
                                    color="inherit"
                                    sx={{
                                        fontWeight: 600,
                                    }}
                                >
                                    {item.change}%
                                </Typography>
                            </Box>
                            <Box
                                aria-hidden="true"
                                sx={{
                                    height: 18,
                                    mt: 0.5,
                                    borderBottom: "2px solid",
                                    borderColor: item.change >= 0 ? "success.main" : "error.main",
                                    transform: item.change >= 0 ? "skewY(-5deg)" : "skewY(5deg)",
                                    opacity: 0.7,
                                }}
                            />
                        </CardContent>
                    </Card>
                </Box>
            ))}
        </Box>
    );
}

export default MarketOverview;
