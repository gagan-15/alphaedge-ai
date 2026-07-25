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
                            minHeight: 92,
                            position: "relative",
                            overflow: "hidden",
                        }}
                    >
                        <CardContent sx={{ p: "13px !important", position: "relative", zIndex: 1 }}>
                            <Typography
                                variant="body2"
                                color="text.secondary"
                                sx={{ fontSize: ".67rem", fontWeight: 750, letterSpacing: ".04em" }}
                            >
                                {item.title}
                            </Typography>

                            <Typography
                                variant="h6"
                                sx={{
                                    mt: 0.5,
                                    fontWeight: 800,
                                    fontSize: "1.05rem",
                                }}
                            >
                                {item.value.toLocaleString()}
                            </Typography>

                            <Box
                                sx={{
                                    display: "flex",
                                    alignItems: "center",
                                    gap: 0.5,
                                    mt: 0.25,
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
                        </CardContent>
                        <Box
                            component="svg"
                            viewBox="0 0 100 36"
                            preserveAspectRatio="none"
                            aria-hidden="true"
                            sx={{
                                position: "absolute",
                                right: 8,
                                bottom: 7,
                                width: "45%",
                                height: 30,
                                opacity: .9,
                            }}
                        >
                            <polyline
                                fill="none"
                                stroke={item.change >= 0 ? "#35d07f" : "#ff5c67"}
                                strokeWidth="2"
                                points={item.change >= 0
                                    ? "0,31 10,27 18,29 29,20 38,23 48,14 58,18 70,9 80,13 91,4 100,7"
                                    : "0,7 12,11 22,9 33,17 43,15 55,24 67,20 79,28 90,25 100,33"}
                            />
                        </Box>
                    </Card>
                </Box>
            ))}
        </Box>
    );
}

export default MarketOverview;
