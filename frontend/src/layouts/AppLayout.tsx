import Box from "@mui/material/Box";

import Header from "../components/header/Header";
import Sidebar from "../components/sidebar/Sidebar";

interface AppLayoutProps {
    children: React.ReactNode;
}

function AppLayout({ children }: AppLayoutProps) {
    return (
        <Box sx={{ display: "flex" }}>
            <Header />
            <Sidebar />

            <Box
                component="main"
                sx={{
                        flexGrow: 1,
                        p: 3,
                        pt: 10,
                        pl: "240px",
                        pr: 3,
                        pb: 3,
                        minHeight: "100vh",
                        backgroundColor: "background.default",
                    }}
            >
                {children}
            </Box>
        </Box>
    );
}

export default AppLayout;