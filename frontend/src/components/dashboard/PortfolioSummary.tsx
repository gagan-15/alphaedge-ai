/**
 * Portfolio Summary Component.
 *
 * Sprint:
 *     2.53 - Portfolio Summary
 */

import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Grid from "@mui/material/Grid";
import Typography from "@mui/material/Typography";

import type { DashboardResult } from "../../types/dashboard";

interface PortfolioSummaryProps {
    dashboard: DashboardResult;
}

function PortfolioSummary({
    dashboard,
}: PortfolioSummaryProps) {
    return (
        <Grid container spacing={3}>
            <Grid size={{ xs: 12, md: 3 }}>
                <Card>
                    <CardContent>
                        <Typography variant="subtitle2">
                            Total Capital
                        </Typography>

                        <Typography variant="h5">
                            ₹{dashboard.portfolio.total_capital.toLocaleString()}
                        </Typography>
                    </CardContent>
                </Card>
            </Grid>

            <Grid size={{ xs: 12, md: 3 }}>
                <Card>
                    <CardContent>
                        <Typography variant="subtitle2">
                            Invested Capital
                        </Typography>

                        <Typography variant="h5">
                            ₹{dashboard.portfolio.invested_capital.toLocaleString()}
                        </Typography>
                    </CardContent>
                </Card>
            </Grid>

            <Grid size={{ xs: 12, md: 3 }}>
                <Card>
                    <CardContent>
                        <Typography variant="subtitle2">
                            Available Capital
                        </Typography>

                        <Typography variant="h5">
                            ₹{dashboard.portfolio.available_capital.toLocaleString()}
                        </Typography>
                    </CardContent>
                </Card>
            </Grid>

            <Grid size={{ xs: 12, md: 3 }}>
                <Card>
                    <CardContent>
                        <Typography variant="subtitle2">
                            Win Rate
                        </Typography>

                        <Typography variant="h5">
                            {dashboard.backtest.win_rate}%
                        </Typography>
                    </CardContent>
                </Card>
            </Grid>
        </Grid>
    );
}

export default PortfolioSummary;