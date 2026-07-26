import type { ReactNode } from "react";

import Box from "@mui/material/Box";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Stack from "@mui/material/Stack";
import Tooltip from "@mui/material/Tooltip";
import Typography from "@mui/material/Typography";

interface OverviewPanelProps {
    title: string;
    subtitle?: string;
    eyebrow?: string;
    action?: ReactNode;
    children: ReactNode;
    minHeight?: number | string;
    accent?: string;
    onExplore?: () => void;
}

export default function OverviewPanel({
    title,
    subtitle,
    eyebrow,
    action,
    children,
    minHeight,
    accent,
    onExplore,
}: OverviewPanelProps) {
    const card = (
        <Card
            role={onExplore ? "button" : undefined}
            tabIndex={onExplore ? 0 : undefined}
            aria-label={onExplore ? `Explore ${title}` : undefined}
            onClick={(event) => {
                if (!onExplore || (event.target as HTMLElement).closest("button,a,input,[role='button']")) return;
                onExplore();
            }}
            onKeyDown={(event) => {
                if (!onExplore || (event.target as HTMLElement).closest("button,a,input,[role='button']")) return;
                if (event.key === "Enter" || event.key === " ") {
                    event.preventDefault();
                    onExplore();
                }
            }}
            sx={{
                height: "100%",
                minHeight,
                borderRadius: "18px",
                borderColor: "rgba(118, 145, 184, .18)",
                bgcolor: "#0b1728",
                boxShadow: "0 14px 40px rgba(1, 7, 18, .16)",
                position: "relative",
                overflow: "hidden",
                cursor: onExplore ? "pointer" : "default",
                transition: "transform .18s ease, border-color .18s ease, box-shadow .18s ease",
                ...(onExplore ? {
                    "&:hover": {
                        transform: "translateY(-2px)",
                        borderColor: "rgba(97,114,243,.42)",
                        boxShadow: "0 18px 44px rgba(1,7,18,.24)",
                    },
                    "&:focus-visible": {
                        outline: "2px solid #6172f3",
                        outlineOffset: 2,
                    },
                } : {}),
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
    return onExplore ? <Tooltip title="Click to explore more" arrow>{card}</Tooltip> : card;
}
