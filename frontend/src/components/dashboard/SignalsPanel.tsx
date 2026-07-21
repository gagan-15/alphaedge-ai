/**
 * Signals Panel.
 *
 * Sprint:
 *     2.61 - Signals Panel
 */

import ShowChartIcon from "@mui/icons-material/ShowChart";

import Box from "@mui/material/Box";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Chip from "@mui/material/Chip";
import Grid from "@mui/material/Grid";
import LinearProgress from "@mui/material/LinearProgress";
import Typography from "@mui/material/Typography";

import type { SignalResult } from "../../types/dashboard";

interface SignalsPanelProps {
    signals: SignalResult[];
}

function getSignalColor(
    action: string,
): "success" | "error" | "warning" | "primary" {
    if (action === "BUY") {
        return "success";
    }

    if (action === "SELL") {
        return "error";
    }

    if (action === "WAIT") {
        return "warning";
    }

    return "primary";
}

function SignalsPanel({
    signals,
}: SignalsPanelProps) {
    return (
        <Card elevation={2}>
            <CardContent
                sx={{
                    p: 2.5,
                }}
            >
                <Box
                    sx={{
                        display: "flex",
                        alignItems: "center",
                        gap: 1,
                        mb: 2,
                    }}
                >
                    <ShowChartIcon color="primary" />

                    <Typography
                        variant="h6"
                        sx={{
                            fontWeight: 700,
                        }}
                    >
                        Trading Signals
                    </Typography>
                </Box>

                {signals.length === 0 ? (
                    <Typography color="text.secondary">
                        No trading signals available.
                    </Typography>
                ) : (
                    <Grid
                        container
                        spacing={2}
                    >
                        {signals.map((signal) => (
                            <Grid
                                key={`${signal.symbol}-${signal.action}`}
                                size={{ xs: 12, sm: 6, lg: 3 }}
                            >
                                <Card
                                    variant="outlined"
                                    sx={{
                                        height: "100%",
                                        minHeight: 170,
                                        transition: "0.2s ease-in-out",
                                        "&:hover": {
                                            boxShadow: 4,
                                            transform: "translateY(-2px)",
                                        },
                                    }}
                                >
                                    <CardContent>
                                        <Box
                                            sx={{
                                                display: "flex",
                                                alignItems: "center",
                                                justifyContent: "space-between",
                                                gap: 1,
                                                mb: 2,
                                            }}
                                        >
                                            <Typography
                                                variant="h6"
                                                sx={{
                                                    fontWeight: 700,
                                                }}
                                            >
                                                {signal.symbol}
                                            </Typography>

                                            <Chip
                                                label={signal.action}
                                                color={getSignalColor(
                                                    signal.action,
                                                )}
                                                size="small"
                                            />
                                        </Box>

                                        <Typography
                                            variant="body2"
                                            color="text.secondary"
                                        >
                                            Current Price
                                        </Typography>

                                        <Typography
                                            variant="h6"
                                            sx={{
                                                mt: 0.5,
                                                mb: 2,
                                                fontWeight: 600,
                                            }}
                                        >
                                            ₹
                                            {signal.price.toLocaleString(
                                                "en-IN",
                                                {
                                                    minimumFractionDigits: 2,
                                                    maximumFractionDigits: 2,
                                                },
                                            )}
                                        </Typography>

                                        <Box>
                                            <Box
                                                sx={{
                                                    display: "flex",
                                                    justifyContent:
                                                        "space-between",
                                                    alignItems: "center",
                                                    mb: 1,
                                                }}
                                            >
                                                <Typography
                                                    variant="body2"
                                                    color="text.secondary"
                                                >
                                                    Confidence
                                                </Typography>

                                                <Typography
                                                    variant="subtitle2"
                                                    sx={{
                                                        fontWeight: 700,
                                                    }}
                                                >
                                                    {signal.confidence}%
                                                </Typography>
                                            </Box>

                                            <LinearProgress
                                                variant="determinate"
                                                value={signal.confidence}
                                                color={getSignalColor(
                                                    signal.action,
                                                )}
                                                sx={{
                                                    height: 10,
                                                    borderRadius: 5,
                                                }}
                                            />
                                        </Box>
                                    </CardContent>
                                </Card>
                            </Grid>
                        ))}
                    </Grid>
                )}
            </CardContent>
        </Card>
    );
}

export default SignalsPanel;