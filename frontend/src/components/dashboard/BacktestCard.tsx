/**
 * Backtest Summary Card.
 *
 * Sprint:
 *     2.56 - Backtest Summary
 */

import AssessmentIcon from "@mui/icons-material/Assessment";
import Box from "@mui/material/Box";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Divider from "@mui/material/Divider";
import Typography from "@mui/material/Typography";

import type { BacktestResult } from "../../types/dashboard";

interface BacktestCardProps {
    backtest: BacktestResult;
}

function BacktestCard({
    backtest,
}: BacktestCardProps) {
    return (
        <Card
            elevation={2}
            sx={{
                height: "100%",
            }}
        >
            <CardContent>
                <Box
                    sx={{
                        display: "flex",
                        alignItems: "center",
                        gap: 1,
                        mb: 2,
                    }}
                >
                    <AssessmentIcon color="primary" />

                    <Typography
                        variant="h6"
                    >
                        Backtest Summary
                    </Typography>
                </Box>

                <Box
                    sx={{
                        display: "grid",
                        gridTemplateColumns: {
                            xs: "1fr",
                            sm: "1fr 1fr",
                        },
                        gap: 2,
                    }}
                >
                    <Box>
                        <Typography
                            variant="body2"
                            color="text.secondary"
                        >
                            Total Trades
                        </Typography>

                        <Typography
                            variant="h6"
                        >
                            {backtest.total_trades}
                        </Typography>
                    </Box>

                    <Box>
                        <Typography
                            variant="body2"
                            color="text.secondary"
                        >
                            Historical Win Rate
                        </Typography>

                        <Typography
                            variant="h6"
                        >
                            {backtest.win_rate}%
                        </Typography>
                    </Box>

                    <Divider sx={{ gridColumn: "1 / -1" }} />

                    <Box>
                        <Typography
                            variant="body2"
                            color="text.secondary"
                        >
                            Winning Trades
                        </Typography>

                        <Typography
                            variant="h6"
                            color="success.main"
                        >
                            {backtest.winning_trades}
                        </Typography>
                    </Box>

                    <Box>
                        <Typography
                            variant="body2"
                            color="text.secondary"
                        >
                            Losing Trades
                        </Typography>

                        <Typography
                            variant="h6"
                            color="error.main"
                        >
                            {backtest.losing_trades}
                        </Typography>
                    </Box>
                </Box>

                <Typography
                    variant="caption"
                    color="text.secondary"
                    sx={{
                        display: "block",
                        mt: 2,
                    }}
                >
                    Historical results do not guarantee future performance.
                </Typography>
            </CardContent>
        </Card>
    );
}

export default BacktestCard;
