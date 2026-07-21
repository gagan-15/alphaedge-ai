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

interface AlertCardProps {
    alerts: AlertResult[];
}

function AlertCard({
    alerts,
}: AlertCardProps) {
    return (
        <Card sx={{ mt: 3 }}>
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

                <List>
                    {alerts.map((alert) => (
                        <ListItem
                            key={alert.title}
                            divider
                        >
                            <div>
                                <Typography
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
                                    color="warning"
                                    label={alert.priority}
                                    sx={{ mt: 1 }}
                                />
                            </div>
                        </ListItem>
                    ))}
                </List>
            </CardContent>
        </Card>
    );
}

export default AlertCard;