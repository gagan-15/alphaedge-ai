import Box from "@mui/material/Box";

import Header from "../components/header/Header";
import MarketTicker from "../components/shared/MarketTicker";
import ResearchDisclaimer from "../components/shared/ResearchDisclaimer";
import RiskConsentDialog from "../components/shared/RiskConsentDialog";

interface AppLayoutProps {
    children: React.ReactNode;
}

function AppLayout({ children }: AppLayoutProps) {
    return (
        <Box
            sx={{
                display: "flex",
                minHeight: "100vh",
                backgroundColor: "background.default",
            }}
        >
            <Header />
            <RiskConsentDialog />
            <MarketTicker />

            <Box
                component="main"
                sx={{
                    width: "100%",
                    pt: {
                        xs: "156px",
                        md: "156px",
                    },
                    px: {
                        xs: 1.25,
                        sm: 2,
                        xl: 3,
                    },
                    pb: 7,
                    minHeight: "100vh",
                    overflow: "hidden",
                }}
            >
                <Box
                    sx={{
                        width: "100%",
                        maxWidth: "none",
                    }}
                >
                    {children}

                    <ResearchDisclaimer />
                </Box>
            </Box>
        </Box>
    );
}

export default AppLayout;
