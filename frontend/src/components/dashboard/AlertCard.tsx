/**
 * Alert Card.
 *
 * Sprint:
 *     2.55 - Alert Card
 */

import WarningAmberIcon from "@mui/icons-material/WarningAmber";

import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Chip from "@mui/material/Chip";
import List from "@mui/material/List";
import ListItem from "@mui/material/ListItem";
import Typography from "@mui/material/Typography";

import type { AlertResult } from "../../types/dashboard";
import Box from "@mui/material/Box";

interface AlertCardProps {
    alerts: AlertResult[];
}

function AlertCard({
    alerts,
}: AlertCardProps) {
    return (
        <Card elevation={2}>
            <CardContent>
                <Typography
                    variant="h6"
                    sx={{
                        display: "flex",
                        alignItems: "center",
                        gap: 1,
                        mb: 2,
                    }}
                >
                    <WarningAmberIcon color="warning" />
                    Alerts
                </Typography>

                <List disablePadding>
                    {alerts.map((alert) => (
                        <ListItem
                            key={alert.title}
                            divider
                            sx={{
                                py: 2,
                            }}
                        >
                            <Box>
                                <Typography
                                    variant="body1"
                                    sx={{
                                        fontWeight: 600,
                                    }}
                                >
                                    {alert.title}
                                </Typography>

                                <Typography
                                    variant="body2"
                                    color="text.secondary"
                                >
                                    {alert.message}
                                </Typography>

                                <Chip
                                    size="small"
                                    color={
                                        alert.priority === "HIGH"
                                            ? "error"
                                            : alert.priority === "MEDIUM"
                                                ? "warning"
                                                : "success"
                                    }
                                    label={alert.priority}
                                    sx={{ mt: 1 }}
                                />
                            </Box>
                        </ListItem>
                    ))}
                </List>
            </CardContent>
        </Card>
    );
}

export default AlertCard;