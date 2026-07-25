import Box from "@mui/material/Box";
import Chip from "@mui/material/Chip";
import Typography from "@mui/material/Typography";

const quotes = [
    { symbol: "RELIANCE", price: "2,978.45", change: "+0.83%" },
    { symbol: "TCS", price: "3,584.75", change: "-0.41%" },
    { symbol: "HDFC BANK", price: "1,654.20", change: "+1.12%" },
    { symbol: "INFY", price: "1,512.10", change: "+0.35%" },
];

function MarketTicker() {
    return (
        <Box
            aria-label="Delayed demo market ticker"
            sx={{
                position: "fixed",
                left: { xs: 64, lg: 224 },
                right: 0,
                bottom: 0,
                zIndex: 1200,
                height: 42,
                display: "flex",
                alignItems: "center",
                gap: { xs: 2, lg: 4 },
                px: 2,
                overflow: "hidden",
                borderTop: "1px solid",
                borderColor: "divider",
                bgcolor: "rgba(5, 14, 29, 0.97)",
                backdropFilter: "blur(14px)",
            }}
        >
            <Chip label="DELAYED DEMO" size="small" color="warning" />
            {quotes.map(({ symbol, price, change }) => {
                const positive = change.startsWith("+");
                return (
                    <Typography key={symbol} variant="caption" sx={{ whiteSpace: "nowrap" }}>
                        {symbol}&nbsp;&nbsp;{price}&nbsp;
                        <Box
                            component="span"
                            color={positive ? "success.main" : "error.main"}
                            sx={{ fontWeight: 800 }}
                        >
                            {positive ? "▲" : "▼"} {change.replace(/^[+-]/, "")}
                        </Box>
                    </Typography>
                );
            })}
        </Box>
    );
}

export default MarketTicker;
