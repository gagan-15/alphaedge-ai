import type { ReactNode } from "react";

import Box from "@mui/material/Box";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";

interface OverviewPanelProps {
    title: string;
    subtitle?: string;
    eyebrow?: string;
    action?: ReactNode;
    children: ReactNode;
    minHeight?: number | string;
    accent?: string;
}

export default function OverviewPanel({
    title,
    subtitle,
    eyebrow,
    action,
    children,
    minHeight,
    accent,
}: OverviewPanelProps) {
    return (
        <Card
            sx={{
                height: "100%",
                minHeight,
                borderRadius: "18px",
                borderColor: "divider",
                bgcolor: "background.paper",
                boxShadow: (theme) => theme.palette.mode === "dark" ? "0 14px 40px rgba(1, 7, 18, .16)" : "0 12px 32px rgba(28,45,72,.08)",
                position: "relative",
                overflow: "hidden",
                ...(accent ? {
                    "&::before": {
                        content: '""',
                        position: "absolute",
                        inset: "0 auto 0 0",
                        width: 3,
                        bgcolor: accent,
                    },
                } : {}),
            }}
        >
            <CardContent
                sx={{
                    p: 3,
                    height: "100%",
                    display: "flex",
                    flexDirection: "column",
                    "&:last-child": { pb: 3 },
                }}
            >
                <Stack direction="row" spacing={2} sx={{ justifyContent: "space-between", alignItems: "flex-start" }}>
                    <Box sx={{ minWidth: 0 }}>
                        {eyebrow && (
                            <Typography
                                sx={{
                                    color: "primary.light",
                                    fontSize: ".65rem",
                                    fontWeight: 850,
                                    letterSpacing: ".12em",
                                    textTransform: "uppercase",
                                }}
                            >
                                {eyebrow}
                            </Typography>
                        )}
                        <Typography variant="h6" sx={{ mt: eyebrow ? .55 : 0, fontWeight: 850 }}>
                            {title}
                        </Typography>
                        {subtitle && (
                            <Typography color="text.secondary" sx={{ mt: .55, fontSize: ".76rem", lineHeight: 1.55 }}>
                                {subtitle}
                            </Typography>
                        )}
                    </Box>
                    {action}
                </Stack>
                <Box sx={{ mt: 2.5, flex: 1, minHeight: 0 }}>{children}</Box>
            </CardContent>
        </Card>
    );
}
