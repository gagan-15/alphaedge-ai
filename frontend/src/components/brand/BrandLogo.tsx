import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";

function BrandLogo({ compact = false }: { compact?: boolean }) {
    return (
        <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
            <Box
                aria-hidden="true"
                sx={{
                    position: "relative",
                    width: 32,
                    height: 30,
                    flexShrink: 0,
                    "&::before": {
                        content: '""',
                        position: "absolute",
                        inset: "1px 12px 1px 2px",
                        borderRadius: "5px 5px 3px 3px",
                        bgcolor: "#3b82f6",
                        transform: "skew(-25deg)",
                        boxShadow: "0 0 18px rgba(59,130,246,.45)",
                    },
                    "&::after": {
                        content: '""',
                        position: "absolute",
                        inset: "7px 2px 1px 14px",
                        borderRadius: "4px",
                        background: "linear-gradient(145deg,#8b5cf6,#d946ef)",
                        transform: "skew(25deg)",
                        boxShadow: "0 0 18px rgba(168,85,247,.4)",
                    },
                }}
            />
            {!compact && (
                <Typography sx={{ fontSize: "0.95rem", fontWeight: 900, letterSpacing: "-0.035em", whiteSpace: "nowrap" }}>
                    AlphaEdge <Box component="span" sx={{ background: "linear-gradient(90deg,#60a5fa,#a855f7)", backgroundClip: "text", color: "transparent" }}>AI</Box>
                </Typography>
            )}
        </Box>
    );
}

export default BrandLogo;
