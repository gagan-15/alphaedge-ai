import { useState } from "react";

import WarningAmberRoundedIcon from "@mui/icons-material/WarningAmberRounded";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Dialog from "@mui/material/Dialog";
import DialogContent from "@mui/material/DialogContent";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";

const consentKey = "alphaedge.risk-consent.v1";

function RiskConsentDialog() {
    const [open, setOpen] = useState(
        () => localStorage.getItem(consentKey) !== "accepted",
    );

    function accept() {
        localStorage.setItem(consentKey, "accepted");
        setOpen(false);
    }

    return (
        <Dialog
            open={open}
            maxWidth="xs"
            fullWidth
            slotProps={{ backdrop: { sx: { bgcolor: "rgba(1, 6, 16, 0.88)", backdropFilter: "blur(3px)" } } }}
        >
            <DialogContent sx={{ p: 3 }}>
                <Stack spacing={2} sx={{ alignItems: "center", textAlign: "center" }}>
                    <Box sx={{ width: 64, height: 64, borderRadius: "50%", display: "grid", placeItems: "center", bgcolor: "rgba(245,185,66,.1)", border: "1px solid rgba(245,185,66,.25)" }}>
                        <WarningAmberRoundedIcon color="warning" sx={{ fontSize: 34 }} />
                    </Box>
                    <Typography variant="h6" color="warning.main">Important Risk Disclaimer</Typography>
                    <Typography color="text.secondary">Please read before entering AlphaEdge AI.</Typography>
                    {[
                        "Research and educational analytics only. This is not personalized investment advice or SEBI-registered research.",
                        "Market conditions are unpredictable. Historical patterns and model estimates do not guarantee future results.",
                        "AlphaEdge does not execute trades. Use your own judgment, risk limits and professional advice when needed.",
                    ].map((message) => (
                        <Box key={message} sx={{ width: "100%", p: 1.5, textAlign: "left", border: "1px solid", borderColor: "divider", borderRadius: 1, bgcolor: "rgba(255,255,255,.02)" }}>
                            <Typography color="text.secondary">• {message}</Typography>
                        </Box>
                    ))}
                    <Button fullWidth size="large" variant="contained" onClick={accept}>
                        I Understand and Accept the Risk
                    </Button>
                </Stack>
            </DialogContent>
        </Dialog>
    );
}

export default RiskConsentDialog;
