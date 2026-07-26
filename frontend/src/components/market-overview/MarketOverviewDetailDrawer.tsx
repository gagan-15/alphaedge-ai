import CloseRoundedIcon from "@mui/icons-material/CloseRounded";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Chip from "@mui/material/Chip";
import Drawer from "@mui/material/Drawer";
import IconButton from "@mui/material/IconButton";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import type { ReactNode } from "react";

export interface MarketDetailContent {
    title: string;
    description: string;
    sections?: Array<{ title: string; points: string[] }>;
    comingSoon?: boolean;
    content?: ReactNode;
    action?: { label: string; onClick: () => void };
}

export default function MarketOverviewDetailDrawer({ detail, onClose }: { detail: MarketDetailContent | null; onClose: () => void }) {
    return <Drawer anchor="right" open={Boolean(detail)} onClose={onClose} slotProps={{ paper: { sx: { width: { xs: "96vw", md: detail?.content ? "min(1100px, 96vw)" : 520 }, bgcolor: "#0b1728", backgroundImage: "none" } } }}>
        {detail && <Stack sx={{ height: "100%" }}>
            <Stack direction="row" sx={{ p: 2.5, alignItems: "flex-start", borderBottom: "1px solid", borderColor: "divider" }}>
                <Box sx={{ flex: 1 }}>
                    {detail.comingSoon && <Chip size="small" color="warning" label="COMING SOON" sx={{ mb: 1 }} />}
                    <Typography variant="h4">{detail.title}</Typography>
                    <Typography color="text.secondary" sx={{ mt: .7, lineHeight: 1.6 }}>{detail.description}</Typography>
                </Box>
                <IconButton aria-label="Close details" onClick={onClose}><CloseRoundedIcon /></IconButton>
            </Stack>
            <Stack spacing={2} sx={{ p: 2.5, overflowY: "auto", flex: 1 }}>
                {detail.content}
                {detail.sections?.map((section) => <Box key={section.title} sx={{ p: 2, borderRadius: 2, border: "1px solid", borderColor: "divider", bgcolor: "rgba(4,12,25,.22)" }}>
                    <Typography sx={{ fontWeight: 900 }}>{section.title}</Typography>
                    <Stack spacing={.8} sx={{ mt: 1.2 }}>{section.points.map((point) => <Typography key={point} color="text.secondary" sx={{ fontSize: ".75rem" }}>• {point}</Typography>)}</Stack>
                </Box>)}
            </Stack>
            <Stack direction="row" spacing={1} sx={{ p: 2, borderTop: "1px solid", borderColor: "divider", justifyContent: "flex-end" }}>
                <Button onClick={onClose}>Close</Button>
                {detail.action && <Button variant="contained" onClick={detail.action.onClick}>{detail.action.label}</Button>}
            </Stack>
        </Stack>}
    </Drawer>;
}
