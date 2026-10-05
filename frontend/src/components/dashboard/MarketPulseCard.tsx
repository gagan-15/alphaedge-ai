import Box from "@mui/material/Box";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";

function MarketPulseCard() {
    return (
        <Card sx={{ flex: 1 }}>
            <CardContent>
                <Typography variant="h6">Market Breadth</Typography>
                <Stack direction="row" spacing={2} sx={{ mt: 1.5, alignItems: "center" }}>
                    <Box
                        aria-label="62 percent advancing, 33 percent declining, 5 percent unchanged"
                        sx={{
                            width: 76,
                            height: 76,
                            flexShrink: 0,
                            borderRadius: "50%",
                            background: "conic-gradient(#35d07f 0 62%, #ff5c67 62% 95%, #64748b 95% 100%)",
                            position: "relative",
                            "&::after": {
                                content: '""',
                                position: "absolute",
                                inset: 14,
                                borderRadius: "50%",
                                bgcolor: "background.paper",
                            },
                        }}
                    />
                    <Stack spacing={0.75} sx={{ flex: 1 }}>
                        {[
                            ["Advancing", "1,682 (62%)", "#35d07f"],
                            ["Declining", "802 (33%)", "#ff5c67"],
                            ["Unchanged", "126 (5%)", "#94a3b8"],
                        ].map(([label, value, color]) => (
                            <Stack key={label} direction="row" sx={{ justifyContent: "space-between", gap: 1 }}>
                                <Typography variant="caption" sx={{ color }}>{label}</Typography>
                                <Typography variant="caption">{value}</Typography>
                            </Stack>
                        ))}
                    </Stack>
                </Stack>
                <Box sx={{ mt: 1.5, pt: 1.25, borderTop: "1px solid", borderColor: "divider" }}>
                    <Stack direction="row" sx={{ justifyContent: "space-between" }}>
                        <Typography variant="caption" color="text.secondary">Market sentiment</Typography>
                        <Typography variant="caption" color="success.main" sx={{ fontWeight: 800 }}>72% Bullish</Typography>
                    </Stack>
                </Box>
            </CardContent>
        </Card>
    );
}

export default MarketPulseCard;
