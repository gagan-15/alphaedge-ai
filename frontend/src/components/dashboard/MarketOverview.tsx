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
import Grid from "@mui/material/Grid";
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
    ];

    return (
        <Grid
            container
            spacing={3}
        >
            {items.map((item) => (
                <Grid
                    key={item.title}
                    size={{ xs: 12, sm: 6, lg: 3 }}
                >
                    <Card
                        elevation={2}
                        sx={{
                            height: "100%",
                        }}
                    >
                        <CardContent>
                            <Typography
                                variant="body2"
                                color="text.secondary"
                            >
                                {item.title}
                            </Typography>

                            <Typography
                                variant="h6"
                                sx={{
                                    mt: 1,
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
                                    mt: 1,
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
                    </Card>
                </Grid>
            ))}
        </Grid>
    );
}

export default MarketOverview;