import {
    useEffect,
    useMemo,
    useState,
} from "react";

import {
    logoutAllSessions,
    logoutSession,
    refreshSession,
} from "../api/authApi";
import {
    AuthContext,
    type AuthContextValue,
    type AuthUser,
} from "./AuthState";

export function AuthProvider({ children }: { children: React.ReactNode }) {
    const [user, setUser] = useState<AuthUser | null>(null);
    const [accessToken, setAccessToken] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        void refreshSession()
            .then((result) => {
                setUser(result.user);
                setAccessToken(result.access_token);
            })
            .catch(() => {
                setUser(null);
                setAccessToken(null);
            })
            .finally(() => setIsLoading(false));
    }, []);

    const value = useMemo<AuthContextValue>(
        () => ({
            user,
            accessToken,
            isLoading,
            setAuthentication: (token, authenticatedUser) => {
                setAccessToken(token);
                setUser(authenticatedUser);
            },
            logout: async () => {
                try {
                    await logoutSession();
                } finally {
                    setAccessToken(null);
                    setUser(null);
                }
            },
            logoutAll: async () => {
                try {
                    await logoutAllSessions();
                } finally {
                    setAccessToken(null);
                    setUser(null);
                }
            },
        }),
        [user, accessToken, isLoading],
    );

    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
