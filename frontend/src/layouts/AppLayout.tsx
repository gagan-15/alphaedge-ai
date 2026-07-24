import Box from "@mui/material/Box";

import Header from "../components/header/Header";
import ResearchDisclaimer from "../components/shared/ResearchDisclaimer";
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

            <Box
                component="main"
                sx={{
                    width: {
                        xs: "calc(100% - 76px)",
                        lg: "calc(100% - 240px)",
                    },
                    ml: {
                        xs: "76px",
                        lg: "240px",
                    },
                    pt: {
                        xs: "76px",
                        md: "88px",
                    },
                    px: {
                        xs: 1.5,
                        sm: 2,
                        xl: 2.5,
                    },
                    pb: 3,
                    minHeight: "100vh",
                    overflow: "hidden",
                }}
            >
                <Box
                    sx={{
                        width: "100%",
                        maxWidth: 1600,
                        mx: "auto",
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
