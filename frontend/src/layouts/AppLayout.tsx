import Box from "@mui/material/Box";

import Header from "../components/header/Header";
import MarketTicker from "../components/shared/MarketTicker";
import ResearchDisclaimer from "../components/shared/ResearchDisclaimer";
import RiskConsentDialog from "../components/shared/RiskConsentDialog";
import Sidebar from "../components/sidebar/Sidebar";

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
            <Sidebar />
            <RiskConsentDialog />
            <MarketTicker />

            <Box
                component="main"
                sx={{
                    width: {
                        xs: "calc(100% - 64px)",
                        lg: "calc(100% - 224px)",
                    },
                    pt: {
                        xs: "72px",
                        md: "82px",
                    },
                    px: {
                        xs: 1.5,
                        sm: 2,
                        xl: 2,
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
