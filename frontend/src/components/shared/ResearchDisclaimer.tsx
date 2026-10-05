import InfoOutlinedIcon from "@mui/icons-material/InfoOutlined";
import Alert from "@mui/material/Alert";
import AlertTitle from "@mui/material/AlertTitle";

function ResearchDisclaimer() {
    return (
        <Alert
            severity="info"
            icon={<InfoOutlinedIcon fontSize="small" />}
            sx={{
                mt: 3,
                color: "text.secondary",
                backgroundColor: "rgba(59, 130, 246, 0.06)",
                border: "1px solid rgba(96, 165, 250, 0.18)",
                "& .MuiAlert-icon": {
                    color: "#60a5fa",
                },
            }}
        >
            <AlertTitle
                sx={{
                    color: "text.primary",
                    fontSize: "0.8rem",
                    fontWeight: 700,
                }}
            >
                Research and education only
            </AlertTitle>
            AlphaEdge AI provides market analytics, not personalized
            investment advice. It does not execute trades or guarantee
            returns. Market investments can cause loss of capital. Make
            your own decisions and consult a SEBI-registered professional
            when required.
        </Alert>
    );
}

export default ResearchDisclaimer;
