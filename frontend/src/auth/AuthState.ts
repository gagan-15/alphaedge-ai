import {
    createContext,
    useContext,
} from "react";

export interface AuthUser {
    id: string;
    full_name: string;
    email: string;
}

export interface AuthContextValue {
    user: AuthUser | null;
    accessToken: string | null;
    isLoading: boolean;
    setAuthentication: (token: string, user: AuthUser) => void;
    logout: () => Promise<void>;
    logoutAll: () => Promise<void>;
}

export const LOCAL_DEMO_MODE =
    import.meta.env.DEV && import.meta.env.VITE_DEMO_MODE !== "false";

export const AuthContext = createContext<AuthContextValue | null>(null);

export function useAuth() {
    const context = useContext(AuthContext);

    if (!context) {
        throw new Error("useAuth must be used inside AuthProvider.");
    }

    return context;
}
