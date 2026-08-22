import CircularProgress from "@mui/material/CircularProgress";
import Box from "@mui/material/Box";
import { Navigate } from "react-router-dom";

import { useAuth } from "./AuthState";

function ProtectedRoute({ children }: { children: React.ReactNode }) {
    const { user, isLoading } = useAuth();

    if (isLoading) {
        return (
            <Box className="auth-page">
                <CircularProgress />
            </Box>
        );
    }

    if (!user) {
        return <Navigate to="/login" replace />;
    }

    return children;
}

export default ProtectedRoute;
