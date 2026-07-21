import Box from "@mui/material/Box";
import Toolbar from "@mui/material/Toolbar";

import { Outlet } from "react-router-dom";

import Header from "../components/header/Header";
import Sidebar from "../components/sidebar/Sidebar";

function AppLayout() {
    return (
        <Box sx={{ display: "flex" }}>
            <Header />

            <Sidebar />

            <Box
                component="main"
                sx={{
                    flexGrow: 1,
                    p: 3,
                }}
            >
                <Toolbar />

                <Outlet />
            </Box>
        </Box>
    );
}

export default AppLayout;